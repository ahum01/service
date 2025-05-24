import logging

import QuantLib as ql
import pandas as pd

from helpers.ql_helper_functions import return_ql_compounding, return_ql_daycounter, get_ql_calendar, return_ql_term

logger = logging.getLogger(__name__)

class YieldCurve:
    def __init__(self, calendar:str= "TARGET"):
        self.helpers = []
        self.daycounter = None
        self.pillar_dates = None
        self.ql_compounding = return_ql_compounding("simple")

    def build_curve(self,
                    settlement: int = 0,
                    style_of_curve: str = "LinearZero"):
        self.yield_curve = ql.PiecewiseLinearZero(2,ql.TARGET(), self.helpers,ql.Actual360())
        self.yield_curve.enableExtrapolation()
        self.pillar_dates = self.yield_curve.dates()

    def get_yield_curve(self):
        return self.yield_curve

    def get_discount_factor(self, discount_date: ql.Date):
        return self.yield_curve.discount(discount_date)

    def get_all_pillar_points_metrics(self):
        data = [
            {
                "pillar_dates": ql_date.ISO(),
                "discount_factors": self.get_discount_factor(ql_date)
            }
            for ql_date in self.pillar_dates
        ]
        return pd.DataFrame(data)

class SoniaYieldCurve(YieldCurve):
    def __init__(self):
        super().__init__()
        self.index = ql.Sonia()
        self.daycounter = "Actual360"

    def irs_helpers(self, ois_rate):
        self.helpers += [
            ql.OISRateHelper(2,
                             ql.Period(tenor, return_ql_term(period)),
                             ql.QuoteHandle(ql.SimpleQuote(rate/100)),
                             self.index
                             )
            for rate, tenor, period in ois_rate
        ]

    def get_all_pillar_points_data(self):
        return super().get_all_pillar_points_metrics()
