from typing import Dict, Union, Optional
import pandas as pd
from evidently.base_metric import MetricResult

class CategoricalColumnDataInfoResult(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:CategoricalColumnDataInfoResult"
    
    column_type: str = 'categorical'
    count: int
    count_missing:int
    count_unique: int
    common_value: dict
    count_values: dict

def get_info_categorical_column(data: pd.Series) -> CategoricalColumnDataInfoResult:
    count = len(data)
    count_missing = data.isnull().sum()
    count_unique = data.nunique()
    count_values = data.value_counts()
    
    # Create `common_value` as a dictionary with the most common value and its count
    most_common_value = str(count_values.idxmax())
    most_common_count = float(count_values.max())
    common_value = {most_common_value: most_common_count}
    return CategoricalColumnDataInfoResult(
        count=float(count),
        count_missing=float(count_missing),
        count_unique=float(count_unique),
        count_values=count_values.to_dict(),
        common_value=common_value
    )