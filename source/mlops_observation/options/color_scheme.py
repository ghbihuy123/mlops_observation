from evidently.options.color_scheme import ColorOptions
import evidently.options as evidently_options
from typing import List

class ColorOptions(evidently_options.ColorOptions):
    primary_gradient_color: List[str] = ['#00c8e5', 'rgba(0.0, 0.7843137254901961, 0.8980392156862745, 0.2)']
    secondary_gradient_color: List[str] = ['#62A388', 'rgba(98, 163, 136, 0.3)']
    drifted_gradient_color: List[str] = ['#ed0400','rgba(255, 0, 0, 0.3)'] 