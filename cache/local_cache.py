import copy


class CurveCache:
    _instance = None
    _yield_curve_dict ={}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def push_yield_curve(self, curve_name: str, curve_object):
        self._yield_curve_dict[curve_name] = curve_object

    def yield_curve(self, curve_name: str):
        return self._yield_curve_dict[curve_name]

class ResultsCache:
    _instance = None
    _results = {}
    _has_changed = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def push_results(self, records: dict):
        self._results = copy.deepcopy(records)


    def get_all_results(self):
        return self._results