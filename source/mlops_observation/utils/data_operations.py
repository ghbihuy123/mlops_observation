from ..metric_results.data_quality import DatasetColumns
from ..metric_results.data_quality import DatasetUtilityColumns
from ..metric_results.data_quality import DatasetSummary
from evidently.calculations.data_integration import get_number_of_all_pandas_missed_values
from evidently.calculations.data_integration import get_number_of_almost_constant_columns
from evidently.calculations.data_integration import get_number_of_almost_duplicated_columns
from evidently.calculations.data_integration import get_number_of_constant_columns
from evidently.calculations.data_integration import get_number_of_duplicated_columns
from evidently.calculations.data_integration import get_number_of_empty_columns
from evidently.calculations.data_quality import get_rows_count
from typing import Optional
from typing import Dict
import numpy as np
import pandas as pd
from evidently.core import ColumnType
from evidently.pipeline.column_mapping import ColumnMapping
def process_columns(dataset: pd.DataFrame, column_mapping: ColumnMapping) -> DatasetColumns:
    if column_mapping is None:
        # data mapping should not be empty in this step
        raise ValueError("column_mapping should be present")
    date_column = column_mapping.datetime if column_mapping.datetime in dataset else None
    # index column name
    id_column = column_mapping.id

    task = column_mapping.task

    target_column = column_mapping.target if column_mapping.target in dataset else None
    if task is None and target_column is not None:
        task = recognize_task(target_name=target_column, dataset=dataset)
    target_type = _get_target_type(dataset, column_mapping, task)
    num_feature_names = column_mapping.numerical_features
    cat_feature_names = column_mapping.categorical_features
    target_names = column_mapping.target_names
    utility_columns = [date_column, id_column, target_column]
    text_feature_names = column_mapping.text_features

    prediction_column: Optional[str] = None
    if isinstance(column_mapping.prediction, str):
        if column_mapping.prediction in dataset:
            prediction_column = column_mapping.prediction
        else:
            prediction_column = None
        utility_columns.append(prediction_column)
    elif column_mapping.prediction is None:
        prediction_column = None
    else:
        prediction_column = dataset[column_mapping.prediction].columns.tolist()

        if prediction_column:
            utility_columns += prediction_column

    utility_columns_set = set(utility_columns)
    cat_feature_names_set = set(cat_feature_names or [])
    text_feature_names_set = set(text_feature_names or [])

    if num_feature_names is None:
        # try to guess about numeric features in the dataset
        # ignore prediction, target, index and explicitly specified category columns and columns with text
        num_feature_names = sorted(
            list(
                set(dataset.select_dtypes([np.number]).columns)
                - utility_columns_set
                - cat_feature_names_set
                - text_feature_names_set
            )
        )

    else:
        num_feature_names = [col for col in num_feature_names if col in dataset.columns]
        empty_cols = dataset[num_feature_names].isnull().mean()
        empty_cols = empty_cols[empty_cols == 1.0].index.to_series()
        num_feature_names = sorted(
            list(set(dataset[num_feature_names].select_dtypes([np.number]).columns).union(set(empty_cols)))
        )


    cat_feature_names = column_mapping.categorical_features

    if cat_feature_names is None:
        cat_feature_names = sorted(
            list(
                set(dataset.select_dtypes(exclude=[np.number, "datetime"]).columns)
                - utility_columns_set
                - text_feature_names_set
            )
        )

    else:
        cat_feature_names = dataset[cat_feature_names].columns.tolist()

    return DatasetColumns(
        utility_columns=DatasetUtilityColumns(
            date=date_column, id=id_column, target=target_column, prediction=prediction_column
        ),
        target_type=target_type,
        num_feature_names=num_feature_names or [],
        cat_feature_names=cat_feature_names or [],
        target_names=target_names,
        task=task,
        text_feature_names=text_feature_names or [],
    )


def recognize_task(target_name: str, dataset: pd.DataFrame) -> str:
    """Try to guess about the target type:
    if the target has a numeric type and number of unique values > 5: task == ‘regression’
    in all other cases task == ‘classification’.

    Args:
        target_name: name of target column.
        dataset: usually the data which you used in training.

    Returns:
        Task parameter.
    """
    if pd.api.types.is_numeric_dtype(dataset[target_name]) and dataset[target_name].nunique() >= 5:
        task = "regression"

    else:
        task = "classification"

    return task


def _get_target_type(dataset: pd.DataFrame, column_mapping: ColumnMapping, task: Optional[str]) -> Optional[str]:
    """
    Args:
        dataset: input dataset
        column_mapping: column definition from user
    Returns:
        type of target (or prediction, if there are only prediction) or None if both columns missing.
    """
    column = None
    if column_mapping.target is not None and column_mapping.target in dataset:
        column = dataset[column_mapping.target]
    if (
        column is None
        and column_mapping.prediction is not None
        and isinstance(column_mapping.prediction, str)
        and column_mapping.prediction in dataset
    ):
        column = dataset[column_mapping.prediction]

    if column is None:
        return None

    if column_mapping.target_names is not None or task == "classification":
        column_type = "cat"
    elif pd.api.types.is_numeric_dtype(column.dtype):
        column_type = "num"
    elif pd.api.types.is_datetime64_dtype(column.dtype):
        column_type = "datetime"
    else:
        column_type = "cat"
    return column_type

def calculate_dataset_common_stats(dataset: pd.DataFrame, column_mapping: ColumnMapping) -> DatasetSummary:
    columns = process_columns(dataset, column_mapping)
    return DatasetSummary(
        number_of_columns=len(dataset.columns),
        number_of_rows=get_rows_count(dataset),
        number_of_missing_values=get_number_of_all_pandas_missed_values(dataset),
        number_of_categorical_columns=len(columns.cat_feature_names),
        number_of_numeric_columns=len(columns.num_feature_names),
        number_of_text_columns=len(columns.text_feature_names),
        number_of_empty_columns=get_number_of_empty_columns(dataset),
        number_of_constant_columns=get_number_of_constant_columns(dataset),
        number_of_almost_constant_columns=get_number_of_almost_constant_columns(
            dataset, 0.95
        ),
        number_of_duplicated_columns=get_number_of_duplicated_columns(dataset),
        number_of_almost_duplicated_columns=get_number_of_almost_duplicated_columns(
            dataset, 0.95
        ),
        number_of_empty_rows=dataset.isna().all(1).sum(),
        number_of_duplicated_rows=dataset.duplicated().sum(),
        nans_by_columns=dataset.isna().sum().to_dict(),
        number_uniques_by_columns=dict(dataset.nunique().to_dict()))
    
def divide_into_chunks_by_period(data: pd.DataFrame, time_column: str, period='M') -> Dict[str, pd.DataFrame]:
    """
    Divides a DataFrame into chunks based on a flexible period.

    Parameters:
    - df: The input DataFrame.
    - time_column: The name of the time column.
    - period: A pandas offset string (e.g., 'M' for month, 'W' for week, '3M' for three months).

    Returns:
    - List of DataFrame chunks for each period.
    """
    df = data.copy()
    df['period'] = df[time_column].dt.to_period(period)
    chunks_dict = {str(period): group.drop(columns=['period']) for period, group in df.groupby('period')}
    return chunks_dict