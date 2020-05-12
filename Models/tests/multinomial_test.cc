#include "gtest/gtest.h"
#include "Models/MultinomialModel.hpp"
#include "Models/DirichletModel.hpp"
#include "Models/PosteriorSamplers/MultinomialDirichletSampler.hpp"

#include "distributions.hpp"

#include "test_utils/test_utils.hpp"
#include <fstream>

namespace {
  using namespace BOOM;
  using std::endl;
  using std::cout;

  class MultinomialTest : public ::testing::Test {
   protected:
    MultinomialTest() {
      GlobalRng::rng.seed(8675309);
    }
  };

  TEST_F(MultinomialTest, Suf) {
    MultinomialSuf suf(3);
    EXPECT_TRUE(VectorEquals(suf.n(), Vector{0, 0, 0}));

    EXPECT_EQ(3, suf.dim());

    suf.update_raw(1);
    EXPECT_TRUE(VectorEquals(suf.n(), Vector{0, 1, 0}));
    suf.update_raw(1);
    EXPECT_TRUE(VectorEquals(suf.n(), Vector{0, 2, 0}));
    suf.update_raw(2);
    EXPECT_TRUE(VectorEquals(suf.n(), Vector{0, 2, 1}));

    suf.clear();
    EXPECT_EQ(3, suf.dim());
  }

  TEST_F(MultinomialTest, ModelTest) {
    MultinomialModel model(3);
    EXPECT_TRUE(VectorEquals(model.pi(), Vector{1, 1, 1} / 3.0));
    EXPECT_EQ(0, model.number_of_observations());

    model.suf()->update_raw(1);
    model.suf()->update_raw(1);
    model.suf()->update_raw(2);
    EXPECT_EQ(3, model.number_of_observations());
  }

  TEST_F(MultinomialTest, McmcTest) {
    NEW(MultinomialModel, model)(3);
    Vector probs = {.5, .3, .2};
    int sample_size = 1000;
    for (int i = 0; i < sample_size; ++i) {
      int y = rmulti(probs);
      model->suf()->update_raw(y);
    }

    NEW(DirichletModel, prior)(Vector(3, 1.0));
    NEW(MultinomialDirichletSampler, sampler)(model.get(), prior);
    model->set_method(sampler);

    int niter = 1000;
    Matrix draws(niter, probs.size());
    for (int i = 0; i < niter; ++i) {
      model->sample_posterior();
      draws.row(i) = model->pi();
    }
    auto status = CheckMcmcMatrix(draws, probs);
    EXPECT_TRUE(status.ok) << status;
  }

  TEST_F(MultinomialTest, ConstrainedMcmcTest) {
    NEW(MultinomialModel, model)(5);
    Vector probs = {.5, 0, .3, 0, .2};

    int sample_size = 1000;
    for (int i = 0; i < sample_size; ++i) {
      int y = rmulti(probs);
      model->suf()->update_raw(y);
    }

    Vector prior_counts = {1, -1, 1, -1, 1};
    NEW(ConstrainedMultinomialDirichletSampler, sampler)(
        model.get(), prior_counts);
    model->set_method(sampler);

    int niter = 1000;
    Matrix draws(niter, probs.size());
    for (int i = 0; i < niter; ++i) {
      model->sample_posterior();
      draws.row(i) = model->pi();
    }
    auto status = CheckMcmcMatrix(draws, probs);
    EXPECT_TRUE(status.ok) << status;
  }

}  // namespace