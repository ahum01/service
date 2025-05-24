import QuantLib as ql
from datetime import date

class QuantLibHelperFunctions:
    @staticmethod
    def today_date_as_ql()-> ql.Date:
        return ql.Date().todaysDate()

    @staticmethod
    def date_as_ql_given_string(date_as_str:str) -> ql.Date:
        if date_as_str:
            try:
                date.fromisoformat(date_as_str)
            except ValueError:
                raise TypeError("date_as_str must be a date")
        return ql.Date(date_as_str, "%Y-%m-%d")

    @staticmethod
    def set_universal_cached_value_date(value_date: str = None) -> None:
        if value_date:
            ql.Settings.instance().evaluationDate = (QuantLibHelperFunctions.date_as_ql_given_string(value_date))
        else:
            ql.Settings.instance().evaluationDate = ql.Date.todaysDate()

    @staticmethod
    def universal_valuation_date() -> str:
        return ql.Settings.instance().evaluationDate.ISO()

def return_ql_daycounter(daycounter: str) -> ql.DayCounter:
    daycounter_dict ={
        "Actual360" : ql.Actual360(),
        "Actual365Fixed" : ql.Actual365Fixed(),
        "ActualActual" : ql.ActualActual(ql.ActualActual.ISDA)
    }
    return daycounter_dict[daycounter]

def return_ql_compounding(compounding:str):
    compounding_dict ={"simple":ql.Simple, "continuous":ql.Continuous}
    return compounding_dict[compounding]

def get_ql_calendar(calendar:str):
    return ql.TARGET()

def return_ql_term(term:str):
    term_dict = {"D": ql.Days, "W":ql.Weeks, "M":ql.Months, "Y":ql.Years}
    return term_dict[term]