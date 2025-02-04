from ...calculator.correlation import calculate_cramers_v_correlation_map, correlation_numeric_calculate

from typing import Dict, Optional
from evidently.base_metric import MetricResult
import pandas as pd



class CorrelationInfoResults(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:CorrelationNumericData"
    
    numerical_correlation: Optional[Dict[str, dict]]
    categorical_correlation: Optional[Dict[str, dict]]

def calculate_correlation_pipeline(
    data: pd.DataFrame, 
    categorical_features: list=None, 
    numerical_features:list=None
    ) -> CorrelationInfoResults:
    
    correlation_info = CorrelationInfoResults()
    if bool(numerical_features):
        numerical_correlation = correlation_numeric_calculate(data, numerical_features)
        correlation_info.numerical_correlation = numerical_correlation
    if bool(categorical_features):
        categorical_correlation = calculate_cramers_v_correlation_map(data, categorical_features)
        correlation_info.categorical_correlation = categorical_correlation
    return correlation_info