from ...metric_results.data_quality import NumericalColumnDataInfoResult
from ...metric_results.data_quality import get_info_numerical_column
from ...metric_results.data_quality import CategoricalColumnDataInfoResult
from ...metric_results.data_quality import CorrelationInfoResults
from ...metric_results.data_quality import calculate_correlation_pipeline
from ...metric_results.data_quality import get_info_categorical_column
from ...utils.visualization import dataframe_to_widget
from ...utils.data_operations import divide_into_chunks_by_period
from ...utils.data_operations import calculate_dataset_common_stats
from ...utils.data_quality import calculate_characteristic
from typing import Dict, Union, Optional
from typing import List
from evidently.base_metric import MetricResult
from evidently.base_metric import Metric
from evidently.base_metric import InputData
from evidently.renderers.base_renderer import MetricRenderer
from evidently.renderers.base_renderer import default_renderer
from evidently.renderers.html_widgets import BaseWidgetInfo
from evidently.renderers.html_widgets import header_text
from evidently.renderers.html_widgets import ColumnDefinition
from evidently.renderers.html_widgets import RichTableDataRow
from evidently.renderers.html_widgets import RowDetails
from evidently.renderers.html_widgets import rich_table_data
import pandas as pd

class DataQualityResults(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:DataQualityResults"
    current_data_quality: Dict[str, Union[NumericalColumnDataInfoResult, CategoricalColumnDataInfoResult]]
    reference_data_quality: Optional[Dict[str, Union[NumericalColumnDataInfoResult, CategoricalColumnDataInfoResult]]]
    correlation: Dict[str, CorrelationInfoResults]

class DataQualityMetric(Metric[DataQualityResults]):
    class Config:
        type_alias = "evidently:metric:DataQualityMetric"

    def __init__(self):
        super().__init__()

    def calculate(self, data: InputData) -> DataQualityResults:
        if data.current_data is None:
            raise ValueError("Current dataset should be present")

        current_data_quality = {}
        reference_data_quality = {}
        correlation = {}
        column_mapping = data.column_mapping

        # Process categorical features
        for column in column_mapping.categorical_features:
            if data.reference_data is not None:
                reference_data_quality[column] = get_info_categorical_column(data.reference_data[column])
            current_data_quality[column] = get_info_categorical_column(data.current_data[column])

        # Process numerical features
        for column in column_mapping.numerical_features:
            if data.reference_data is not None:
                reference_data_quality[column] = get_info_numerical_column(data.reference_data[column])
            current_data_quality[column] = get_info_numerical_column(data.current_data[column])

        # Correlation
        if data.reference_data is not None:
            correlation['reference'] = calculate_correlation_pipeline(
                data=data.reference_data, 
                categorical_features=column_mapping.categorical_features, 
                numerical_features= column_mapping.numerical_features)
            correlation['current'] =  calculate_correlation_pipeline(
                data=data.current_data, 
                categorical_features=column_mapping.categorical_features, 
                numerical_features= column_mapping.numerical_features)
    
        return DataQualityResults(
            current_data_quality=current_data_quality,
            reference_data_quality=reference_data_quality if data.reference_data is not None else None,
            correlation=correlation
        )


@default_renderer(wrap_type=DataQualityMetric)
class DataQualityRender(MetricRenderer):
    def render_json(self, obj: DataQualityMetric, include_render: bool = False,
        include: "IncludeOptions" = None, exclude: "IncludeOptions" = None,) -> dict:
        result = obj.get_result().get_dict(include_render, include, exclude)
        return result


class PeriodDataQuality(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:PeriodDataQuality"
    summary_table: Optional[pd.DataFrame]

class PeriodDataQualityMetric(Metric[PeriodDataQuality]):
    """
    time_period (str): Offset aliases https://pandas.pydata.org/docs/user_guide/timeseries.html#dateoffset-objects
    """
    class Config:
        type_alias = "evidently:metric:PeriodDataQualityMetric"
    _time_period: str
    def __init__(self, time_period: str = 'M'):
        self._time_period = time_period
        super().__init__()

    def calculate(self, data: InputData):
        if data.current_data is None:
            raise ValueError("Current dataset should be present")
        column_mapping = data.column_mapping
        if data.reference_data is not None:
            reference_summary_table = self._dataset_summary_to_dataframe(
                dataset=data.reference_data,
                column_mapping=column_mapping,
                period=self._time_period
            )
            reference_summary_table.columns = [reference_summary_table.columns[0]] + [f"{col} (base)" for col in reference_summary_table.columns[1:]]
            current_summary_table = self._dataset_summary_to_dataframe(
                dataset=data.current_data,
                column_mapping=column_mapping,
                period=self._time_period
            )
            summary_table = pd.merge(reference_summary_table, current_summary_table, on='')
        else:
            summary_table = self._dataset_summary_to_dataframe(
                dataset=data.current_data,
                column_mapping=column_mapping,
                period=self._time_period
            )
        return PeriodDataQuality(
            summary_table=summary_table
        )
    def _dataset_summary_to_dataframe(
        self, 
        dataset: pd.DataFrame, 
        column_mapping: str, 
        period: str='M'
        ) -> pd.DataFrame:
        """
        Convert a dictionary of DatasetSummary objects into a DataFrame.

        Parameters:
        - dataset_summary_dict: A dictionary where keys are dates (str) and values are DatasetSummary objects.

        Returns:
        - pd.DataFrame: A DataFrame with dates as columns and DatasetSummary attributes as index.
        """
        dataset_summary_dict = {}             # Dict[str, DatasetSummary]
        data_period_dict = divide_into_chunks_by_period(dataset, column_mapping.datetime_features, period=period)
        for data_date in data_period_dict.keys():
            dataset_summary_dict[data_date] = calculate_dataset_common_stats(data_period_dict[data_date], column_mapping)
        data = {}

        for date, summary in dataset_summary_dict.items():
            # Convert the DatasetSummary object to a dictionary
            summary_dict = summary.__dict__
            
            # Remove "number_uniques_by_columns" 
            summary_dict.pop('number_uniques_by_columns', None)
            summary_dict.pop('nans_by_columns', None)

            # Add the data for this date
            data[date] = summary_dict
        df = pd.DataFrame(data).reset_index()
        df.rename(columns={'index': ''}, inplace=True)
        return df

@default_renderer(wrap_type=PeriodDataQualityMetric)
class PeriodDataQualityRender(MetricRenderer):
    def render_html(self, obj: PeriodDataQualityMetric) -> List[BaseWidgetInfo]:
        results = obj.get_result()
        color_options = self.color_options
        summary_table = dataframe_to_widget(results.summary_table)
        # hist = plotly_figure(title='', figure=results.fig)
        return [
            header_text(label=f"Period Data Quality Summary"),
            summary_table
        ]


class PeriodFeatureQualityResult(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:PeriodFeatureQualityResult"
    num_feature_stats: Dict[str, pd.DataFrame]     # {col_name, stats}
    cat_feature_stats: Dict[str, pd.DataFrame]     # {col_name, stats}

class PeriodFeatureQualityMetric(Metric[PeriodFeatureQualityResult]):
    """
    time_period (str): Offset aliases https://pandas.pydata.org/docs/user_guide/timeseries.html#dateoffset-objects
    """
    class Config:
        type_alias = "evidently:metric:PeriodFeatureQualityMetric"
    _time_period: str
    def __init__(self, time_period: str = 'M'):
        self._time_period = time_period
        super().__init__()

    def calculate(self, data: InputData):
        num_feature_stats = {}
        cat_feature_stats = {}
        column_mapping = data.column_mapping
        if column_mapping.datetime_features is None:
            raise ValueError('column_mapping.datetime_features can not be None')
        if data.reference_data is not None:
            reference_chunks_dict = divide_into_chunks_by_period(data.reference_data, time_column=column_mapping.datetime_features, period=self._time_period)
            
        current_chunks_dict = divide_into_chunks_by_period(data.current_data, time_column=column_mapping.datetime_features, period=self._time_period)
        if column_mapping.numerical_features is not None:
            for num_col in column_mapping.numerical_features:
                current_stats = calculate_characteristic(current_chunks_dict, num_col, 'num')
                if data.reference_data is not None:
                    reference_stats = calculate_characteristic(reference_chunks_dict, num_col, 'num')
                    reference_stats.columns = [f"{col} (base)" for col in reference_stats.columns]
                    num_feature_stats[num_col] = pd.merge(reference_stats, current_stats, left_index=True, right_index=True) \
                        .reset_index() \
                        .rename({'index': ''}, axis=1)
                else:
                    num_feature_stats[num_col] = current_stats \
                        .reset_index() \
                        .rename({'index': ''}, axis=1)
        
        if column_mapping.categorical_features is not None:
            for cat_col in column_mapping.categorical_features:
                current_stats = calculate_characteristic(current_chunks_dict, cat_col, 'cat')
                if data.reference_data is not None:
                    reference_stats = calculate_characteristic(reference_chunks_dict, cat_col, 'cat')
                    reference_stats.columns = [f"{col} (base)" for col in reference_stats.columns]
                    cat_feature_stats[cat_col] = pd.merge(reference_stats, current_stats, left_index=True, right_index=True) \
                        .reset_index() \
                        .rename({'index': ''}, axis=1) \
                        .drop_duplicates()
                else:
                    cat_feature_stats[cat_col] = current_stats \
                        .reset_index() \
                        .rename({'index': ''}, axis=1) \
                        .drop_duplicates()
        
        return PeriodFeatureQualityResult(
            num_feature_stats=num_feature_stats,
            cat_feature_stats=cat_feature_stats
        )



@default_renderer(wrap_type=PeriodFeatureQualityMetric)
class PeriodFeatureQualityRender(MetricRenderer):
    def _generate_column_params(
        self,
        column_data: pd.DataFrame
        )-> Optional[RichTableDataRow]:
        details = RowDetails()
        # -----------------------------------------
        table = column_data
        table = dataframe_to_widget(table)
        details.with_part("STAT TABLE", info=table)
        # -----------------------------------------
        
        return RichTableDataRow({
            "column_name": column_data.col_name, 
            "column_type": column_data.col_type,
            "period_drifted_count": fr"{column_data.period_drifted_count}/{column_data.period_count}"
            }, 
            details=details)
    def render_html(self, obj: PeriodFeatureQualityMetric) -> List[BaseWidgetInfo]:
        results = obj.get_result()
        color_options = self.color_options
        rows = []
        # summary_table = dataframe_to_widget(results.summary_table)
        for cat_col in results.cat_feature_stats.keys():
            details = RowDetails()
            table = dataframe_to_widget(results.cat_feature_stats[cat_col])
            details.with_part("STAT TABLE", info=table)
            rows.append(RichTableDataRow({
                "column_name": cat_col, 
                "column_type": 'cat'}, 
                details=details))
        for num_col in results.num_feature_stats.keys():
            details = RowDetails()
            table = dataframe_to_widget(results.num_feature_stats[num_col])
            details.with_part("STAT TABLE", info=table)
            rows.append(RichTableDataRow({
                "column_name": num_col, 
                "column_type": 'num'}, 
                details=details))
        columns = [
            ColumnDefinition("Column Name", "column_name"),
            ColumnDefinition("Type", "column_type")
        ]
        return [
            header_text(label=f"Feature Statistic in Period"),
            rich_table_data(
                columns=columns,
                data=rows
            )
        ]

class PeriodMissingValueResult(MetricResult):
    class Config:
        type_alias = "evidently:metric_result:PeriodMissingValueResult"
    missing_table: pd.DataFrame     # {col_name, stats}



class PeriodMissingValueMetric(Metric[PeriodMissingValueResult]):
    """
    time_period (str): Offset aliases https://pandas.pydata.org/docs/user_guide/timeseries.html#dateoffset-objects
    """
    class Config:
        type_alias = "evidently:metric:PeriodMissingValueMetric"
    _time_period: str
    def __init__(self, time_period: str = 'M'):
        self._time_period = time_period
        super().__init__()

    def calculate(self, data: InputData):
        column_mapping = data.column_mapping
        if column_mapping.datetime_features is None:
            raise ValueError('column_mapping.datetime_features can not be None')
        current_chunks_dict = divide_into_chunks_by_period(
            data.current_data, 
            time_column=column_mapping.datetime_features, 
            period=self._time_period
        )
        missing_data = {}
        for key in current_chunks_dict.keys():
            missing_data[key] = self._column_missing_value(current_chunks_dict[key])
        
        current_missing_table = pd.DataFrame.from_dict(missing_data, orient='columns')
        if data.reference_data is not None:
            reference_chunks_dict = divide_into_chunks_by_period(
                data.reference_data, 
                time_column=column_mapping.datetime_features, 
                period=self._time_period
            )
            missing_data = {}
            for key in reference_chunks_dict.keys():
                missing_data[key] = self._column_missing_value(reference_chunks_dict[key])
            reference_missing_table = pd.DataFrame.from_dict(missing_data, orient='columns')
            reference_missing_table.columns = [column + ' (base)' for column in reference_missing_table.columns]
            missing_table = pd.merge(
                reference_missing_table, 
                current_missing_table, 
                left_index=True, 
                right_index=True
            ).reset_index() \
            .rename({'index':''}, axis=1)
        else:
            missing_table = current_missing_table.reset_index() \
                .rename({'index':''}, axis=1)
        return PeriodMissingValueResult(
            missing_table=missing_table
        )

    def _column_missing_value(self, df: pd.DataFrame) -> Dict[str, int]:
        missing_dict = {}
        columns = df.keys()
        for col in columns:
            missing_dict[col] = df[col].isna().sum()
        return missing_dict


@default_renderer(wrap_type=PeriodMissingValueMetric)
class PeriodMissingValueRender(MetricRenderer):
    def render_html(self, obj: PeriodMissingValueMetric) -> List[BaseWidgetInfo]:
        results = obj.get_result()
        color_options = self.color_options
        
        return [
            header_text(label=f"Datasets Missing Value In Period"),
            dataframe_to_widget(results.missing_table)
        ]