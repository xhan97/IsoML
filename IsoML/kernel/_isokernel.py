"""
Copyright 2024 Xin Han. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.
"""

import numbers
from warnings import warn

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils import check_array
from sklearn.utils.validation import check_is_fitted
from ._ik_anne import IK_ANNE
from ._ik_iforest import IK_IForest
from ._ik_inne import IK_INNE


class IsoKernel(TransformerMixin, BaseEstimator):
    """Build Isolation Kernel feature vector representations via the feature map
    for a given dataset.

    Isolation kernel is a data dependent kernel measure that is
    adaptive to local data distribution and has more flexibility in capturing
    the characteristics of the local data distribution. It has been shown promising
    performance on density and distance-based classification and clustering problems.

    This version uses Voronoi diagrams to split the data space and calculate Isolation
    kernel Similarity. Based on this implementation, the feature
    in the Isolation kernel space is the index of the cell in Voronoi diagrams. Each
    point is represented as a binary vector such that only the cell the point falling
    into is 1.

    Parameters
    ----------
    method : str, default="anne"
        The method to compute the isolation kernel feature. The available methods are: `anne`, `inne`, and `iforest`.

    n_estimators : int, default=200
        The number of base estimators in the ensemble.


    max_samples : int, default="auto"
        The number of samples to draw from X to train each base estimator.

            - If int, then draw `max_samples` samples.
            - If float, then draw `max_samples` * X.shape[0]` samples.
            - If "auto", then `max_samples=min(8, n_samples)`.

    random_state : int, RandomState instance or None, default=None
        Controls the pseudo-randomness of the selection of the feature
        and split values for each branching step and each tree in the forest.

        Pass an int for reproducible results across multiple function calls.
        See :term:`Glossary <random_state>`.

    References
    ----------
    .. [1] Qin, X., Ting, K.M., Zhu, Y. and Lee, V.C.
    "Nearest-neighbour-induced isolation similarity and its impact on density-based clustering".
    In Proceedings of the AAAI Conference on Artificial Intelligence, Vol. 33, 2019, July, pp. 4755-4762

    Examples
    --------
    >>> from IsoKernel import IsoKernel
    >>> import numpy as np
    >>> X = [[0.4,0.3], [0.3,0.8], [0.5, 0.4], [0.5, 0.1]]
    >>> ik = IsoKernel.fit(X)
    >>> ik.transform(X)
    >>> ik.similarity(X)
    """

    def __init__(
        self, method="anne", n_estimators=200, max_samples="auto", random_state=None
    ) -> None:
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.random_state = random_state
        self.method = method

    def fit(self, X, y=None):
        """Fit the model on data X.
        Parameters
        ----------
        X : np.array of shape (n_samples, n_features)
            The input instances.
        Returns
        -------
        self : object
        """

        X = check_array(X)
        n_samples = X.shape[0]
        if isinstance(self.max_samples, str):
            if self.max_samples == "auto":
                max_samples = min(16, n_samples)
            else:
                raise ValueError(
                    "max_samples (%s) is not supported."
                    'Valid choices are: "auto", int or'
                    "float" % self.max_samples
                )
        elif isinstance(self.max_samples, numbers.Integral):
            if self.max_samples > n_samples:
                warn(
                    "max_samples (%s) is greater than the "
                    "total number of samples (%s). max_samples "
                    "will be set to n_samples for estimation."
                    % (self.max_samples, n_samples)
                )
                max_samples = n_samples
            else:
                max_samples = self.max_samples
        else:  # float
            if not 0.0 < self.max_samples <= 1.0:
                raise ValueError(
                    "max_samples must be in (0, 1], got %r" % self.max_samples
                )
            max_samples = int(self.max_samples * X.shape[0])
        self.max_samples_ = max_samples

        if self.method == "anne":
            self.iso_kernel_ = IK_ANNE(
                self.n_estimators, self.max_samples_, self.random_state
            )
        elif self.method == "inne":
            self.iso_kernel_ = IK_INNE(
                self.n_estimators, self.max_samples_, self.random_state
            )
        elif self.method == "iforest":
            self.iso_kernel_ = IK_IForest(
                self.n_estimators, self.max_samples_, self.random_state
            )
        else:
            raise ValueError(
                "method (%s) is not supported."
                'Valid choices are: "anne", "inne" or "iforest"' % self.method
            )

        self.iso_kernel_.fit(X)
        self.is_fitted_ = True
        return self

    def similarity(self, X):
        """Compute the isolation kernel pairwise simalarity matrix of X.
        Parameters
        ----------
        X: array-like of shape (n_instances, n_features)
            The input instances.
        Returns
        -------
        The simalarity matrix are organised as a n_instances * n_instances matrix.
        """

        embed_X = self.transform(X)
        return np.inner(embed_X, embed_X) / self.n_estimators

    def transform(self, X):
        """Compute the isolation kernel feature of X.
        Parameters
        ----------
        X: array-like of shape (n_instances, n_features)
            The input instances.
        Returns
        -------
        The finite binary features based on the kernel feature map.
        The features are organised as a n_instances by psi*t matrix.
        """

        check_is_fitted(self)
        X = check_array(X)
        return self.iso_kernel_.transform(X)
