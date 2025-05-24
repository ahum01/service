import asyncio
import logging
import random
import pandas as pd
import datetime
from analytics.curve.build_rfr_curve import SoniaYieldCurve
from cache.local_cache import ResultsCache
from statics.rfr_static_data import SONIA_DEFAULT_CURVE

logger = logging.getLogger(__name__)


def extract_curve_metrics(shock: float = 0):
    logger.info("Running curve")
    helper= SONIA_DEFAULT_CURVE
    if abs(shock)>0:
        helper = [(shock/10000 + rate,period,tenor) for rate,period,tenor in SONIA_DEFAULT_CURVE]
    rfr = SoniaYieldCurve()
    rfr.irs_helpers(helper)
    rfr.build_curve()
    return rfr.get_all_pillar_points_data()

def extract_shocked_curves():
    shock = random.randrange(1, 100)
    return extract_curve_metrics(shock)

async def extract_multi_curves():
    shock_lst = [random.randrange(1, 100) for _ in range(1,10)]
    tasks = (
        asyncio.to_thread(extract_curve_metrics,x)
        for x in shock_lst
    )
    results = await asyncio.gather(*tasks)
    df_rsl = pd.DataFrame()
    for tmp_pd in results:
        if not tmp_pd.empty:
            df_rsl = pd.concat([df_rsl, tmp_pd])
    return df_rsl

async def run_loop():
    delta_const = 5000
    delta = delta_const
    tmp_value = 0
    while True:
        df = extract_curve_metrics(tmp_value)
        tmp_value = tmp_value - delta
        df['build_date_time']  = datetime.datetime.now()
        ResultsCache().push_results(df.to_dict("records"))
        logger.info("Run Loop: Build curve")
        await asyncio.sleep(5)