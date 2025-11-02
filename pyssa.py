import numpy as np
from warnings import warn
from scipy.stats import kstest, mannwhitneyu, normaltest, ttest_ind, bartlett, levene, median_test, t, norm, sem, bootstrap
from scipy.stats.mstats import median_cihs

#TODO: checks for the data shapes


def report_significance(sig, p_val, conf_lvl):
    if sig:
        print(f"Speedup is statistically significant with confidence level {conf_lvl}% (p-val. = {p_val}).")
    else:
        print(f"Speedup is not statistically significant with confidence level {conf_lvl}% (p-val. = {p_val}).")


def mean_speedup_test(t_ref, t_opt, alpha=0.05, skip_dispersion_test=False, bootstrap_ci=False):
    conf_lvl = 100*(1-alpha)

    # Normality
    test_normal_ref = normaltest(t_ref)
    test_normal_opt = normaltest(t_opt)
    model_valid = (test_normal_ref.pvalue > alpha) and (test_normal_opt.pvalue > alpha)
    if not model_valid:
        warn(f"Samples are not normally distributed (ref. p-val. = {test_normal_ref.pvalue}, opt. p-val. = {test_normal_opt.pvalue}, risk level = {alpha}). The confidence level ({conf_lvl}%) might be incorrect. Ensure the sample size is large enough (>30).")

    # Dispersion test
    same_var = False
    if not skip_dispersion_test:
        test_var = bartlett(t_opt,t_ref) if model_valid else levene(t_opt,t_ref)
        same_var = test_var.pvalue > alpha
        if same_var:
            print(f"The variances of the two samples are similar (p-val. = {test_var.pvalue}).")
        else:
            print(f"The variances of the two samples are different (p-val. = {test_var.pvalue}).")

    # Location test (alternative hypothesis is mean_opt < mean_ref)
    t_test = ttest_ind(t_opt, t_ref, alternative="less", equal_var=same_var)
    stat_sign = t_test.pvalue < alpha
    report_significance(stat_sign, t_test.pvalue, conf_lvl)

    # Confidence interval
    ref_ci = ()
    opt_ci = ()
    if bootstrap_ci:
        t_ref_thick = np.reshape(t_ref, (t_ref.shape[0],1)).T
        t_opt_thick = np.reshape(t_opt, (t_opt.shape[0],1)).T
        print(t_ref_thick.shape)
        res_ref = bootstrap(t_ref_thick, np.mean)
        res_opt = bootstrap(t_opt_thick, np.mean)
        ref_ci = (res_ref.confidence_interval.low, res_ref.confidence_interval.high)
        opt_ci = (res_opt.confidence_interval.low, res_opt.confidence_interval.high)
    elif model_valid :
        ref_ci = t.interval(1-alpha, df=t_ref.shape[0]-1, loc=np.mean(t_ref), scale=sem(t_ref))
        opt_ci = t.interval(1-alpha, df=t_opt.shape[0]-1, loc=np.mean(t_opt), scale=sem(t_opt))
    else:
        ref_ci = norm.interval(1-alpha, loc=np.mean(t_ref), scale=sem(t_ref))
        opt_ci = norm.interval(1-alpha, loc=np.mean(t_opt), scale=sem(t_opt))

    speedup = 1 - np.mean(t_opt)/np.mean(t_ref)

    print(f"Reported Speedup = {100*speedup}%")

    return speedup, stat_sign, t_test.pvalue, ref_ci, opt_ci

def median_speedup_test(t_ref, t_opt, alpha=0.05, force_mood=False, bootstrap_ci=False):
    conf_lvl = 100*(1-alpha)

    # Test location shift
    ref_med = np.median(t_ref)
    opt_med = np.median(t_opt)
    test_same_dist = kstest(t_ref - ref_med, t_opt - opt_med)
    model_valid = test_same_dist.pvalue > alpha
    if not model_valid:
        warn(f"Samples do not satisfy the location shift hypothesis (p-val. = {test_same_dist.pvalue}, risk level = {alpha}). The confidence level ({conf_lvl}%) might be incorrect. Ensure sample size is large enough (>30).")
    
    # Location test (alternative hypothesis is median_opt < median_ref)
    pval = 0.
    if model_valid and not force_mood:
        med_test = mannwhitneyu(t_opt, t_ref, alternative="less")
        pval = med_test.pvalue
    else:
        med_test = median_test(t_opt, t_ref)
        pval = med_test.pvalue/2 # p-value has to be divided by 2 because we want to consider a one-sided alternative.
    stat_sign = pval < alpha 
    report_significance(stat_sign, pval, conf_lvl)

    # Confidence interval for median
    ref_ci = ()
    opt_ci = ()
    if bootstrap_ci:
        t_ref_thick = np.reshape(t_ref, (t_ref.shape[0],1)).T
        t_opt_thick = np.reshape(t_opt, (t_opt.shape[0],1)).T
        res_ref = bootstrap(t_ref_thick, np.median)
        res_opt = bootstrap(t_opt_thick, np.median)
        ref_ci = (res_ref.confidence_interval.low, res_ref.confidence_interval.high)
        opt_ci = (res_opt.confidence_interval.low, res_opt.confidence_interval.high)
    else:
        ref_ci = median_cihs(t_ref,alpha=alpha)
        opt_ci = median_cihs(t_opt,alpha=alpha)

    speedup = 1 - opt_med/ref_med

    print(f"Reported speedup = {100*speedup}%")

    return speedup, stat_sign, pval, ref_ci, opt_ci

