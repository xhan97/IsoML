"""This file shows how to write test based on the scikit-learn common tests."""

# Authors: IsolationKernel developers
# License: BSD 3 clause

from sklearn.utils.estimator_checks import parametrize_with_checks

from isoml.utils.discovery import all_estimators


# parametrize_with_checks allows to get a generator of check that is more fine-grained
# than check_estimator
@parametrize_with_checks([est() for _, est in all_estimators()])
def test_estimators(estimator, check, request):
    """Check the compatibility with scikit-learn API"""
    check(estimator)
