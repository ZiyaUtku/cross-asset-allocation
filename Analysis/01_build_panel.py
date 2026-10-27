"""Step 1: read the LSEG Workspace Excel exports in 'Price Data/' and build one daily price panel.

Each export has a summary block above the table, so the script finds the real header row
(the row above the first datetime). Output: Clean Data/prices_daily_raw.csv (levels only).
"""
import openpyxl, datetime as dt, pandas as pd, numpy as np
from pathlib import Path

SRC = Path("Price Data"); OUT = Path("Clean Data"); OUT.mkdir(exist_ok=True)
# file stem -> column used
SPEC = {'SPX':'Close','STOXX':'Close','DAX':'Close','MSCI EM':'Close','N225':'Close',
        'US10YT':'BidYld','US2YT':'BidYld','DE10YT':'BidYld','JP10YT':'BidYld',
        'HYG':'Close','LQD':'Close','XAU':'Bid','LCOc1':'Close','CLc1':'Close',
        'DXY':'Trade Price','EURUSD':'Bid','USDJPY':'Bid','USDCHF':'Bid','BTC':'Bid'}

def read_export(stem, col):
    ws = openpyxl.load_workbook(SRC / f"{stem}.xlsx", read_only=True, data_only=True).worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    i0 = next(i for i, r in enumerate(rows) if isinstance(r[0], dt.datetime))
    hdr = [str(h) for h in rows[i0 - 1]]
    df = pd.DataFrame([r for r in rows[i0:] if isinstance(r[0], dt.datetime)], columns=hdr)
    s = pd.Series(pd.to_numeric(df[col], errors='coerce').values, index=pd.to_datetime(df['Exchange Date'])).sort_index()
    return s[~s.index.duplicated()].dropna()

P = pd.DataFrame({k: read_export(k, c) for k, c in SPEC.items()})
P = P[P.index.dayofweek < 5]                       # weekdays only (BTC trades 7 days)
P['CLc1'] = P['CLc1'].where(P['CLc1'] > 0)         # WTI went negative in Apr 2020
P = P.rename(columns={'MSCI EM': 'MSCI_EM'}); P.index.name = 'Date'
P.to_csv(OUT / "prices_daily_raw.csv")
print(P.shape, P.index.min().date(), P.index.max().date())
