
from analytics.curve.build_rfr_curve import SoniaYieldCurve
from statics.rfr_static_data import SONIA_DEFAULT_CURVE


def test_rfr_curve():
    helper= SONIA_DEFAULT_CURVE
    rfr = SoniaYieldCurve()
    rfr.irs_helpers(helper)
    rfr.build_curve()
    df = rfr.get_all_pillar_points_data()
    print(df)

if __name__ =="__main__":
    test_rfr_curve()