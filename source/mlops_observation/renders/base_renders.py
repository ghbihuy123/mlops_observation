from typing import Generic
from typing import Optional
from typing import List
from typing import TypeVar
import pandas as pd
from ..options.color_scheme import ColorOptions
from evidently.renderers.html_widgets import BaseWidgetInfo
import warnings

class BaseRenderer:
    """Base class for all renderers"""

    color_options: ColorOptions

    def __init__(self, color_options: Optional[ColorOptions] = None) -> None:
        if color_options is None:
            self.color_options = ColorOptions()

        else:
            self.color_options = color_options


TMetric = TypeVar("TMetric", bound="Metric")


class MetricRenderer(Generic[TMetric], BaseRenderer):
    def render_pandas(self, obj: TMetric) -> pd.DataFrame:
        result = obj.get_result()
        if not result.__config__.pd_include:
            warnings.warn(
                f"{obj.get_id()} metric does not support as_dataframe yet. Please submit an issue to https://github.com/evidentlyai/evidently/issues"
            )
            return pd.DataFrame()
        return result.get_pandas()

    def render_json(
        self,
        obj: TMetric,
        include_render: bool = False,
        include: "IncludeOptions" = None,
        exclude: "IncludeOptions" = None,
    ) -> dict:
        result = obj.get_result()
        return result.get_dict(include_render=include_render, include=include, exclude=exclude)

    def render_html(self, obj: TMetric) -> List[BaseWidgetInfo]:
        raise NotImplementedError()