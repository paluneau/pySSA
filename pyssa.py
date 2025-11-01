import numpy as np
from warnings import warn
from scipy.stats import kstest, mannwhitneyu, normaltest, ttest_ind, bartlett, levene

def report_significance(sig, p_val, conf_lvl):
    if sig:
        print(f"Speedup is statistically significant with confidence level {conf_lvl}% (p-val. = {p_val}).")
    else:
        print(f"Speedup is not statistically significant with confidence level {conf_lvl}% (p-val. = {p_val}).")


def mean_speedup_test(t_ref,t_opt,alpha=0.05,skip_dispersion_test=False):
    # TODO: Compute a confidence interval for the mean values (when normal, use student statistic, otherwise use normal statistic (asymptotic) or bootstrap)
    conf_lvl = 100*(1-alpha)

    # Normality
    test_normal_ref = normaltest(t_ref)
    test_normal_opt = normaltest(t_opt)
    model_valid = (test_normal_ref.pvalue > alpha) and (test_normal_opt.pvalue > alpha)
    if not model_valid:
        warn(f"Samples are not normally distributed (ref. p-val. = {test_normal_ref.pvalue}, opt. p-val. = {test_normal_opt.pvalue}, risk level = {alpha}). The confidence level ({conf_lvl}%) might be incorrect.")

    # Dispersion test
    same_var = False
    if not skip_dispersion_test:
        test_var = bartlett(t_opt,t_ref) if model_valid else levene(t_opt,t_ref)
        same_var = test_var.pvalue > alpha
        # TODO: add potentially console output to indicate if variance is equal or not

    # Location test (alternative hypothesis is mean_opt < mean_ref)
    t_test = ttest_ind(t_opt, t_ref, alternative="less", equal_var=same_var)
    stat_sign = t_test.pvalue < alpha
    report_significance(stat_sign, t_test.pvalue, conf_lvl)

    speedup = 1 - np.mean(t_opt)/np.mean(t_ref)

    print(f"Reported Speedup = {100*speedup}%")

    return speedup, stat_sign

def median_speedup_test(t_ref,t_opt,alpha=0.05):
    # TODO: compute confidence interval for the median using (Boudec, Thm 2.1) or bootstrap
    conf_lvl = 100*(1-alpha)

    # Test location shift
    ref_med = np.median(t_ref)
    opt_med = np.median(t_opt)
    test_same_dist = kstest(t_ref - ref_med, t_opt - opt_med)
    model_valid = test_same_dist.pvalue > alpha
    if not model_valid:
        warn(f"Samples do not satisfy the location shift hypothesis (p-val. = {test_same_dist.pvalue}, risk level = {alpha}). The confidence level ({conf_lvl}%) might be incorrect.")
    

    # Location test (alternative hypothesis is median_opt < median_ref)
    U_test = mannwhitneyu(t_opt, t_ref, alternative="less")
    stat_sign = U_test.pvalue < alpha
    report_significance(stat_sign, U_test.pvalue, conf_lvl)

    speedup = 1 - opt_med/ref_med

    print(f"Reported speedup = {100*speedup}%")

    return speedup, stat_sign

