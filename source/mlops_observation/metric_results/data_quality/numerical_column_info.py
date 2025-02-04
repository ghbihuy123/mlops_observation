from typing import Dict, Union, Optional
import pandas as pd
from evidently.base_metric import MetricResult

class NumericalColumnDataInfoResult(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:NumericalColumnDataInfoResult"

    column_type: str = 'numerical'
    count: int
    count_missing:int
    mean: Optional[float]
    median: Optional[float]
    percentile: Optional[Dict[str, float]]
    zeros: Optional[int]
    std: Optional[float]
    min: Optional[float]
    max: Optional[float]
    skewness: Optional[float]
    outliers_turkey: Optional[list]

def get_info_numerical_column(data: pd.Series):
    count = len(data)
    count_missing = data.isnull().sum()
    mean = data.mean(skipna=True)
    median = data.median(skipna=True)
    percentile = {
        'Q1': float(data.quantile(0.25)),
        'median': float(data.quantile(0.5)),
        'Q3': float(data.quantile(0.75))
    }
    zeros = (data == 0).sum()
    std = data.std()
    min = data.min()
    max = data.max()
    skewness = data.skew()
    
    # Outliers theo Turkey Method
    iqr = percentile['Q3'] - percentile['Q1']
    lower_threshold = percentile['Q1'] - 1.5 * iqr
    upper_threshold = percentile['Q3'] + 1.5 * iqr
    outliers_turkey = data[(data < lower_threshold) | (data > upper_threshold)].to_list()

    return NumericalColumnDataInfoResult(
        count=count,
        count_missing=float(count_missing),
        mean=float(mean),
        median=float(median),
        percentile=percentile,
        zeros=float(zeros),
        std=float(std),
        min=float(min),
        max=float(max),
        skewness=float(skewness),
        outliers_turkey=outliers_turkey
    )