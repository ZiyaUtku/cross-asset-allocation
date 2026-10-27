import pandas as pd,numpy as np
P=pd.read_csv("Clean Data/prices_daily_raw.csv",index_col=0,parse_dates=True)
R=pd.read_csv("Clean Data/returns_daily.csv",index_col=0,parse_dates=True)
# weekly returns: compound daily returns within Fri-ending weeks (bond/log returns are additive)
Wk=R.resample('W-FRI').sum(min_count=1)
cnt=R.resample('W-FRI').count()
Wk=Wk.where(cnt>=3)
Wk.to_csv("Clean Data/returns_weekly.csv")
d=R['SPX'].rolling(252,min_periods=200).corr(R['UST10'])
w=Wk['SPX'].rolling(52,min_periods=42).corr(Wk['UST10'])
w.to_csv("Clean Data/rolling_corr_SPX_UST10_weekly52.csv")
print("daily vs weekly rolling corr (resampled monthly) corr:",round(d.resample('ME').last().corr(w.resample('ME').last()),3))
print("sign flip date daily>0 after 2021:",d[d.index>'2021-01-01'][d[d.index>'2021-01-01']>0].index[0].date(),"| weekly:",w[w.index>'2021-01-01'][w[w.index>'2021-01-01']>0].index[0].date())
print("latest daily/weekly:",round(d.dropna().iloc[-1],2),round(w.dropna().iloc[-1],2))
eras=[("2000–06","2000","2006"),("2007–12","2007","2012"),("2013–19","2013","2019"),("2020–21","2020","2021"),("2022–26","2022","2026")]
rows=[]
for n,a,b in eras:
    r=R.loc[a:b];x=Wk.loc[a:b]
    rows.append({"era":n,"daily":r.SPX.corr(r.UST10),"weekly":x.SPX.corr(x.UST10),
     "weekly_yieldchg":-1*(-1)*0+x.SPX.corr(-x.UST10),  # placeholder same as sign flip
     "SPX-Bund wkly":x.SPX.corr(x.Bund10),"SPX-UST2 wkly":x.SPX.corr(x.UST2),"SPX-Gold wkly":x.SPX.corr(x.Gold),"SPX-HYG wkly":x.SPX.corr(x.HYG)})
E=pd.DataFrame(rows).set_index("era").drop(columns="weekly_yieldchg"); print(E.round(2).to_string()); E.to_csv("Clean Data/robustness_era_daily_vs_weekly.csv")
# timezone check: SPX vs ex-US equities daily vs weekly vs 1-day-lag-adjusted
for c in ['STOXX','DAX','MSCI EM','N225']:
    dd=R['SPX'].corr(R[c]); ww=Wk['SPX'].corr(Wk[c])
    lag=R['SPX'].shift(1).corr(R[c])   # next-day response of local market to US
    print(f"{c:8s} daily {dd:.2f} weekly {ww:.2f} | local mkt vs prior-day SPX {lag:.2f}")
# crisis-vs-calm key pairs on weekly basis (full crisis windows, weekly)
cr=[("GFC","2008-09-01","2009-03-09"),("Euro debt","2011-07-22","2011-10-04"),("China/oil","2015-08-10","2016-02-11"),("Covid","2020-02-19","2020-03-23"),("2022","2022-01-03","2022-10-14")]
m=pd.Series(False,index=Wk.index)
for n,a,b in cr: m|=(Wk.index>=a)&(Wk.index<=b)
for k in ['UST10','HYG','Gold','Brent']:
    print(k,"calm wkly",round(Wk.loc[~m,'SPX'].corr(Wk.loc[~m,k]),2),"| crisis wkly",round(Wk.loc[m,'SPX'].corr(Wk.loc[m,k]),2))
# bootstrap-ish CI for 2022-26 stock-bond corr via block bootstrap of weeks
x=Wk.loc['2022':,['SPX','UST10']].dropna().values; rng=np.random.default_rng(1); n=len(x); b=8; cs=[]
for _ in range(2000):
    idx=np.concatenate([np.arange(s,s+b)%n for s in rng.integers(0,n,n//b+1)])[:n]; cs.append(np.corrcoef(x[idx].T)[0,1])
print("2022-26 weekly stock-bond corr %.2f, 90%% block-bootstrap CI [%.2f, %.2f], n=%d"%(np.corrcoef(x.T)[0,1],*np.percentile(cs,[5,95]),n))
x=Wk.loc['2013':'2019',['SPX','UST10']].dropna().values; n=len(x); cs=[]
for _ in range(2000):
    idx=np.concatenate([np.arange(s,s+b)%n for s in rng.integers(0,n,n//b+1)])[:n]; cs.append(np.corrcoef(x[idx].T)[0,1])
print("2013-19: %.2f CI [%.2f, %.2f]"%(np.corrcoef(x.T)[0,1],*np.percentile(cs,[5,95])))
