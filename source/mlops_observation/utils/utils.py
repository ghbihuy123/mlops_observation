import pandas as pd
from typing import List
from ..metric_results.data_drift import CategoricalFeatureDrift
from ..metric_results.data_drift import NumericFeatureDrift

def get_period_list(data: pd.DataFrame, time_column: str, period='M') -> List[str]:
    """
    Extracts a list of periods from a DataFrame based on a flexible period.

    Parameters:
    - data: The input DataFrame.
    - time_column: The name of the time column.
    - period: A pandas offset string (e.g., 'M' for month, 'W' for week, '3M' for three months).

    Returns:
    - List of periods as strings.
    """
    data['period'] = data[time_column].dt.to_period(period)
    return sorted(data['period'].astype(str).unique())