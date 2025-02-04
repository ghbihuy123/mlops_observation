from .stat_result import StatResult
from .stat_result import map_into_stat_results

import pandas as pd
import numpy as np
from typing import Optional
from evidently.base_metric import MetricResult
from evidently.core import ColumnType
from evidently.utils.visualizations import make_hist_for_cat_plot
from evidently.metric_results import Histogram
from evidently.calculations.stattests import psi_stat_test
from evidently.calculations.stattests.cramer_von_mises_stattest import cramer_von_mises
from evidently.calculations.stattests.chisquare_stattest import chi_stat_test

class CategoricalFeatureDrift(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:CategoricalFeatureDrift"
    column_type: str = 'categorical'
    column_name: str
    psi: Optional[StatResult]
    chi_square: Optional[StatResult]
    cramer: Optional[StatResult]
    drifted: bool
    hist_data: Optional[Histogram]

def get_one_categorical_column_drift(
    current: pd.DataFrame,
    reference: pd.DataFrame,
    column_name: str
    ) -> CategoricalFeatureDrift:
    """
    Tính toán các metric cho numeric feature, return kết quả các value của:
    - Population stability index (PSI)
    - Chi-square
    - Cramer's V
    """
    reference_series = reference[column_name].copy().dropna()
    current_series = current[column_name].copy().dropna()
    
    chi_square = chi_stat_test(reference_series, current_series, ColumnType.Categorical, threshold=0.05)
    cramer = cramer_von_mises(reference_series, current_series, ColumnType.Categorical, threshold=0.1)
    psi = psi_stat_test(reference_series, current_series, ColumnType.Categorical, threshold=0.1)
    hist_data = make_hist_for_cat_plot(curr=current_series, ref=reference_series)
    drifted = False

    if (int(chi_square.drifted) + int(psi.drifted) + int(cramer.drifted)) > 2:
        drifted = True

    return CategoricalFeatureDrift(
        column_name=column_name,
        chi_square=map_into_stat_results(chi_square),
        cramer=map_into_stat_results(cramer),
        psi=map_into_stat_results(psi),
        drifted=drifted,
        hist_data=hist_data
    )