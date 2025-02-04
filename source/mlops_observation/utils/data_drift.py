from ..utils import safe_round
from ..metric_results.data_drift import CategoricalFeatureDrift
from ..metric_results.data_drift import NumericFeatureDrift
from .utils import get_period_list
from typing import Dict
from typing import Union
import pandas as pd
import plotly.graph_objects as go
# Function to divide a DataFrame into chunks based on a flexible period


def convert_test_period_into_dataframe(
    test_result: Dict[str, Union[CategoricalFeatureDrift, NumericFeatureDrift]]
    ) -> pd.DataFrame:

    display_test_result = lambda stat: f'{safe_round(stat.drift_score, 4)} | {"Drift" if stat.drifted else "No Drift"}'
    result_dict = {}
    col_type = test_result[sorted(test_result.keys())[0]].column_type
    if col_type == 'categorical':
        for row_index in sorted(test_result.keys()):
            row_data = test_result[row_index]
            result_dict[row_index] = {
                'Chi Square': display_test_result(row_data.chi_square),
                'PSI': display_test_result(row_data.psi), 
                'Cramer': display_test_result(row_data.cramer), 
                'Drifted': row_data.drifted
            }
        result_df = pd.DataFrame.from_dict(result_dict, orient='index')

    elif col_type == 'numeric':
        for row_index in sorted(test_result.keys()):
            row_data = test_result[row_index]
            result_dict[row_index] = {
                'Kolmogorov Smirnov': display_test_result(row_data.kolmogorov_smirnov),
                'Wasserstein Distance Norm': display_test_result(row_data.wasserstein_distance_norm),
                'Jensen Shanon': display_test_result(row_data.jensen_shanon_divergence),
                'PSI': display_test_result(row_data.psi),
                'Drifted': row_data.drifted
            }
        result_df = pd.DataFrame.from_dict(result_dict, orient='index')
    else: 
        raise ValueError("col_type must be 'categorical' or 'numeric'")
    return result_df


def convert_test_period_into_dataframe_v2(test_result: Dict[str, Union[CategoricalFeatureDrift, NumericFeatureDrift]]):
    display_test_result = lambda stat: stat.drift_score
    result_dict = {}
    col_type = test_result[sorted(test_result.keys())[0]].column_type
    if col_type == 'categorical':
        for row_index in sorted(test_result.keys()):
            row_data = test_result[row_index]
            result_dict[row_index] = {
                'Chi2 Square': display_test_result(row_data.chi_square),
                'Chi2 Threshold': row_data.chi_square.actual_threshold,
                'PSI': display_test_result(row_data.psi), 
                'PSI Threshold': row_data.psi.actual_threshold,
                'Cramer': display_test_result(row_data.cramer), 
                'Cramer Threshold': row_data.cramer.actual_threshold,
                'Drifted': row_data.drifted,
            }
        result_df = pd.DataFrame.from_dict(result_dict, orient='index')

    elif col_type == 'numeric':
        for row_index in sorted(test_result.keys()):
            row_data = test_result[row_index]
            result_dict[row_index] = {
                'Kolmogorov Smirnov': display_test_result(row_data.kolmogorov_smirnov),
                'Wasserstein Distance Norm': display_test_result(row_data.wasserstein_distance_norm),
                'Jensen Shanon_': display_test_result(row_data.jensen_shanon_divergence),
                'Drifted': row_data.drifted
            }
        result_df = pd.DataFrame.from_dict(result_dict, orient='index')
    else: 
        raise ValueError("col_type must be 'categorical' or 'numeric'")
    return result_df





def calculate_period_drifted_dict(reference: pd.DataFrame, timestamp_col: str, period_stat_result: Dict[str, Union[CategoricalFeatureDrift, NumericFeatureDrift]]) -> dict:
    """
    Return:
    reference_date_list: list
        List of the reference dataset, sorted ascending
    current_date_list: list
        List of current dataset, sorted ascending
    current_drifted_list: list
        Drifted, correspond to current_date_list
    """
    
    reference_date_list = get_period_list(reference, timestamp_col)
    current_date_list = sorted(period_stat_result.keys())
    current_drifted_list = [period_stat_result[current_date_key].drifted for current_date_key in current_date_list]
    return reference_date_list, current_date_list, current_drifted_list



