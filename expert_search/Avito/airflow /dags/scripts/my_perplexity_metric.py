from evidently.core.metric_types import SingleValue
from evidently.core.metric_types import SingleValueMetric
from evidently.core.metric_types import SingleValueCalculation
from evidently.core.metric_types import BoundTest
from evidently.tests import Reference, eq

from evidently.legacy.renderers.html_widgets import plotly_figure

from typing import Optional
from typing import List
from plotly.express import line
import plotly.express as px

class MyPerplexityMetric(SingleValueMetric):
    column: str

    def _default_tests(self) -> List[BoundTest]:
        # Например, тест на то, что perplexity не превышает 100
        return [le(100).bind_single(self.get_fingerprint())]

    def _default_tests_with_reference(self) -> List[BoundTest]:
        # Например, относительное изменение perplexity не превышает 10%
        return [le(Reference(relative=0.1)).bind_single(self.get_fingerprint())]