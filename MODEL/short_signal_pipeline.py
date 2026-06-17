"""
short_signal_pipeline.py  –  app.py 가 import 하는 공용 상수 모듈
"""
FEATURE_COLS = ['log_mktcap', 'log_price', 'is_large_cap', 'ret_1d', 'ret_5d', 'ret_20d', 'vol_5d', 'vol_20d', 'intraday_vol', 'price_ma20_gap', 'turnover', 'log_trdval', 'abnormal_vol', 'trdval_ma5_over_ma20', 'ret5_x_abnormal_vol', 'short_ratio_ma5', 'short_ratio_ma10', 'short_ratio_lag1', 'short_ratio_chg_1d', 'short_ratio_std5', 'balance_ratio_chg_5d', 'balance_ratio_ma5', 'balance_ratio_lag1', 'short_qty_chg5', 'short_ratio_pct_vs_own_hist', 'balance_ratio_pct_vs_own_hist']

RANDOM_STATE  = 42
HORIZON_DAYS  = 5
MIN_HIST_DAYS = 30
Q             = 0.7
