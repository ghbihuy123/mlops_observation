from . import CategoricalFeatureDrift, NumericFeatureDrift
from ...utils.data_operations import divide_into_chunks_by_period
from ...options.color_scheme import ColorOptions
from typing import Union
from typing import Dict
from typing import Literal
import pandas as pd
import plotly.graph_objects as go


def calculate_test_in_period(
    reference: pd.DataFrame, 
    current_chunks: Dict[str, pd.DataFrame], 
    col_name: str, 
    col_type=Literal['num', 'cat']
    ) -> Dict[str, Union[CategoricalFeatureDrift, NumericFeatureDrift]]:
    from ...metrics.data_drift.data_drift import get_one_numeric_column_drift, get_one_categorical_column_drift
    row_indexes = sorted(current_chunks.keys())
    result = {}

    if col_type == 'cat':
        for row_index in row_indexes:
            row_data = current_chunks[row_index]
            result[row_index] = get_one_categorical_column_drift(row_data, reference, col_name)
    elif col_type == 'num':
        for row_index in row_indexes:
            row_data = current_chunks[row_index]
            result[row_index] = get_one_numeric_column_drift(row_data, reference, col_name)
    else: 
        raise ValueError("col_type must be 'cat' or 'num'")
    return result


class DriftPeriodResult:
    distribution: go.Figure
    drift_period: go.Figure
    col_type: str
    col_name: str
    stat_table: pd.DataFrame
    period_count: int
    period_drifted_count: int
    reference_date_list: int
    current_date_list: int
    def __init__(self, distribution, drift_period, col_type, col_name, stat_table, period_drifted_count, period_count):
        self.distribution = distribution
        self.drift_period = drift_period
        self.col_type = col_type
        self.col_name = col_name
        self.stat_table = stat_table
        self.period_count = period_count
        self.period_drifted_count = period_drifted_count