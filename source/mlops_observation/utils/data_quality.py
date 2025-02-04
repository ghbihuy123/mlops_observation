import pandas as pd

from evidently.core import ColumnType
from evidently.calculations.data_quality import get_features_stats
from evidently.metrics.data_integrity.column_summary_metric import ColumnCharacteristics
from evidently.metrics.data_integrity.column_summary_metric import FeatureQualityStats
from evidently.metrics.data_integrity.column_summary_metric import NumericCharacteristics
from evidently.metrics.data_integrity.column_summary_metric import CategoricalCharacteristics
from evidently.metrics.data_integrity.column_summary_metric import DatetimeCharacteristics


def map_data(stats: FeatureQualityStats) -> ColumnCharacteristics:
    if stats.feature_type == "num":
        if isinstance(stats.max, str) or isinstance(stats.min, str) or isinstance(stats.most_common_value, str):
            raise ValueError("max / min stats should be int or float type, but got str")
        return NumericCharacteristics(
            number_of_rows=stats.number_of_rows,
            count=stats.count,
            mean=stats.mean,
            std=stats.std,
            min=stats.min,
            max=stats.max,
            p25=stats.percentile_25,
            p50=stats.percentile_50,
            p75=stats.percentile_75,
            unique=stats.unique_count,
            unique_percentage=stats.unique_percentage,
            missing=stats.missing_count,
            missing_percentage=stats.missing_percentage,
            infinite_count=stats.infinite_count,
            infinite_percentage=stats.infinite_percentage,
            most_common=stats.most_common_value,
            most_common_percentage=stats.most_common_value_percentage,
        )
    if stats.feature_type == "cat":
        return CategoricalCharacteristics(
            number_of_rows=stats.number_of_rows,
            count=stats.count,
            unique=stats.unique_count,
            unique_percentage=stats.unique_percentage,
            most_common=stats.most_common_value,
            most_common_percentage=stats.most_common_value_percentage,
            missing=stats.missing_count,
            missing_percentage=stats.missing_percentage,
        )
    if stats.feature_type == "datetime":
        if not isinstance(stats.min, str) or not isinstance(stats.max, str):
            raise ValueError(f"min / max expected to be str for datetime, got {type(stats.min)}/{type(stats.max)}")
        return DatetimeCharacteristics(
            number_of_rows=stats.number_of_rows,
            count=stats.count,
            unique=stats.unique_count,
            unique_percentage=stats.unique_percentage,
            most_common=stats.most_common_value,
            most_common_percentage=stats.most_common_value_percentage,
            missing=stats.missing_count,
            missing_percentage=stats.missing_percentage,
            first=stats.min,
            last=stats.max,
        )
    raise ValueError(f"unknown feature type {stats.feature_type}")

from typing import Union
from typing import Dict
def period_characteristic_table(data: Dict[str, Union[CategoricalCharacteristics, NumericCharacteristics]]) -> pd.DataFrame:
    """
    Convert a dictionary of characteristics into a DataFrame for display.
    
    Parameters:
    - data: A dictionary where keys are period labels (e.g., '2011-01') and values are
            characteristics dictionaries (e.g., 'CategoricalCharacteristics' or 'NumericCharacteristics').

    Returns:
    - A DataFrame with periods as columns and characteristics as rows.
    """
    # Initialize an empty DataFrame
    result_df = pd.DataFrame()
    for key in data.keys():
        data[key] = data[key].__dict__

    # Process each period's characteristics
    for period, characteristics in data.items():
        # Format characteristics into a dictionary suitable for DataFrame
        formatted_characteristics = {
            key: (
                f"{value} ({characteristics[f'{key}_percentage']:.2f}%)" 
                if f"{key}_percentage" in characteristics 
                else value
            )
            for key, value in characteristics.items()
            if key not in ['type', 'unique_percentage', 'most_common_percentage', 'missing_percentage', 'infinite_percentage']
        }
        # Add to the result DataFrame
        result_df[period] = pd.Series(formatted_characteristics)

    # Set a proper index (characteristic names) and return
    return result_df

def calculate_characteristic(data_chunks: Dict[str, pd.DataFrame], col_name: str, col_type: str)-> Dict[str, pd.DataFrame]:
    feature_stat_dict = {}
    if col_type == 'num':
        col_type = ColumnType.Numerical
        index_name_mapping = {
            "number_of_rows": "number of rows",
            "count": "count",
            "missing": "missing",
            "mean": "mean",
            "std": "std",
            "min": "min",
            "p25": "25%",
            "p50": "50%",
            "p75": "75%",
            "max": "max",
            "unique": "unique",
            "most_common": "most common",
            "missing_percentage": "missing",
            "infinite_count": "infinite",
            "infinite_percentage": "infinite",
        }
    elif col_type == 'cat':
        col_type = ColumnType.Categorical
        index_name_mapping = {
            "number_of_rows": "count",
            "count": "count",
            "missing": "missing",
            "unique": "unique",
            "most_common": "most common"
        }
    else:
        raise ValueError("col_type must be 'cat' or 'num'")
    for key in data_chunks.keys():
        feature_stat_dict[key] = map_data(get_features_stats(data_chunks[key][col_name], col_type))
    result = period_characteristic_table(feature_stat_dict)
    result.rename(index=index_name_mapping, inplace=True)
    if col_type == ColumnType.Categorical:
        result.drop(['new_in_current_values_count', 'unused_in_current_values_count'], axis=0, inplace=True)
    
    return result 