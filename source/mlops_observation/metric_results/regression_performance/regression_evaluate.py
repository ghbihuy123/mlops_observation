import pandas as pd
from typing import Optional, List, Union, Dict
from evidently.base_metric import MetricResult
from evidently.base_metric import Metric
from evidently.base_metric import InputData
from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error
from sklearn.metrics import mean_squared_log_error, root_mean_squared_log_error
from sklearn.metrics import r2_score, mean_absolute_percentage_error

class RegressionResults(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:RegressionResults"
        
    target: str
    mae: float
    mse: float
    rmse: float
    mean_square_log_error: float
    root_mean_square_log_error: float
    r2: float
    mape: float


def calculate_regression_metrics(data: pd.DataFrame, true_label_col: str, prediction_col: str) -> RegressionResults:
    y_true = data[true_label_col].copy()
    y_pred = data[prediction_col].copy()

    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = root_mean_squared_error(y_true, y_pred)
    msle = mean_squared_log_error(y_true, y_pred)
    rmsle = root_mean_squared_log_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred)
    
    return RegressionResults(
        target=true_label_col,
        mae=float(mae),
        mse=float(mse),
        rmse=float(rmse),
        mean_square_log_error=float(msle),
        r2=float(r2),
        root_mean_square_log_error=float(rmsle),
        mape=mape
    )