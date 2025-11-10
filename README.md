# pySSA
Based on "The Speedup Test" from the papers [Towards a Statistical Methodology to Evaluate Program
Speedups and their Optimisation Techniques](https://hal.science/hal-00356529) and [_The Speedup-Test: a statistical methodology for programme speedup analysis and computation_](https://doi.org/10.1002/cpe.2939) (2012) by Touati, Worms and Briais (accessible on [HAL](https://hal.science/inria-00443839v2)). This project provides a Python implementation of the speedup test.

## Functionalities

As presented in the aforementioned papers :
- A function to compute the speedup using either the mean or the variance;
- Each function uses a sequence of statistical tests to determine if the speedup is statistically significant.

Some new functionalities are added :
- In the algorithm for testing the mean, the test for equal variance can be skipped, as it has been reported the literature that it can influence the real confidence level of the test ([Zimmerman, 2004](https://www.enqueteodregionquebec.cmquebec.qc.ca/index.html); [García-Pérez, 2023](https://www.sciencedirect.com/science/article/pii/S2590260123000115));
- Depending on the normality of the data, the dispersion test can switch between Barlett and Levene;
- If the location shift hypothesis is not valid, the Mann-Whitney-Cox test can be replaced by a Mood two-tailed median test;
- Confidence intervals are provided for the mean and median. The user can choose to use bootstrap (BCa) to produce the intervals instead of classical formulas.
