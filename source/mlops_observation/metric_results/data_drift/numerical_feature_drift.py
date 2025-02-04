from .stat_result import StatResult
from .stat_result import map_into_stat_results

import pandas as pd
from typing import Optional
from evidently.calculations.stattests import jensenshannon_stat_test, ks_stat_test, wasserstein_stat_test
from evidently.calculations.stattests import psi_stat_test
from evidently.base_metric import MetricResult
from evidently.metric_results import Histogram
from evidently.core import ColumnType
from evidently.utils.visualizations import make_hist_for_num_plot

class NumericFeatureDrift(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:NumericFeatureDrift"

    # Numerical column
    column_type: str = 'numeric'
    column_name: str
    kolmogorov_smirnov: Optional[StatResult]
    wasserstein_distance_norm: Optional[StatResult]
    jensen_shanon_divergence: Optional[StatResult]
    psi: Optional[StatResult]
    drifted: bool
    hist_data: Optional[Histogram]


def get_one_numeric_column_drift(
    current: pd.DataFrame,
    reference: pd.DataFrame,
    column_name: str,
    ) -> NumericFeatureDrift:
    """
    Tính toán các metric cho numeric feature, return kết quả các value của:
    - Jensen Shanon Divergence
    - Kolmogorov Smirnov
    - Wasserstein Distance Norm
    """
    reference_series = reference[column_name].copy().dropna()
    current_series = current[column_name].copy().dropna()

    jensen_shanon_divergence_value = jensenshannon_stat_test(reference_series, current_series, ColumnType.Numerical, threshold=0.1)
    kolmogorov_smirnov_value = ks_stat_test(reference_series, current_series, ColumnType.Numerical, threshold=0.1)
    wasserstein_distance_norm_value = wasserstein_stat_test(reference_series, current_series, ColumnType.Numerical, threshold=0.1)
    psi_value = psi_stat_test(reference_series, current_series, ColumnType.Numerical, threshold=0.1)
    drifted = False
    if (int(kolmogorov_smirnov_value.drifted) + int(jensen_shanon_divergence_value.drifted) + int(wasserstein_distance_norm_value.drifted)) > 2:
        drifted = True
    hist_data = make_hist_for_num_plot(curr=current_series, ref=reference_series)
    return NumericFeatureDrift(
        column_name=column_name,
        kolmogorov_smirnov=map_into_stat_results(kolmogorov_smirnov_value),
        jensen_shanon_divergence=map_into_stat_results(jensen_shanon_divergence_value),
        wasserstein_distance_norm=map_into_stat_results(wasserstein_distance_norm_value),
        psi=map_into_stat_results(psi_value),
        drifted=drifted,
        hist_data=hist_data
    )