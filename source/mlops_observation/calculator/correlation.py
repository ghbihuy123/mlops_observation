import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

def correlation_numeric_calculate(data: pd.DataFrame, numeric_features: list):
    corr = {}
    methods = ['pearson', 'kendall', 'spearman']
    for method in methods:
        corr_map = data[numeric_features].corr().to_dict()
        corr[method] = corr_map
    return corr


def cramers_v(x: pd.Series, y: pd.Series) -> float:
    # Create a contingency table
    contingency_table = pd.crosstab(x, y)
    
    # Calculate the Chi-squared statistic and total observations
    chi2, _, _, _ = chi2_contingency(contingency_table)
    n = contingency_table.sum().sum()  # Total number of observations
    
    # Calculate Cramér's V
    min_dim = min(contingency_table.shape) - 1
    return float(np.sqrt(chi2 / (n * min_dim)))


def calculate_cramers_v_correlation_map(data: pd.DataFrame, categorical_features: list):
    corr = {}
    for col_index in categorical_features:
        corr_map = {}
        for col in categorical_features:
            corr_score = cramers_v(data[col_index], data[col])
            if np.isnan(corr_score):
                corr_map[col] = None
            else:
                corr_map[col] = corr_score
        corr[col_index] = corr_map
    return {'cramers_v':corr}