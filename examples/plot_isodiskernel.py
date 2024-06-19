"""
=============================
Plotting isoml.IsodisKernel
=============================

An example plot of :class:`isoml.IsoDisKernel`
"""
import numpy as np
from matplotlib import pyplot as plt

from isoml.kernel import IsodisKernel

X = np.arange(50, dtype=np.float64).reshape(-1, 1)
X /= 50
estimator = IsodisKernel()
X_transformed = estimator.fit_transform(X)

plt.plot(X.flatten(), label="Original Data")
plt.plot(X_transformed.flatten(), label="Transformed Data")
plt.title("Plots of original and transformed data")

plt.legend(loc="best")
plt.grid(True)
plt.xlabel("Index")
plt.ylabel("Value of Data")

plt.show()