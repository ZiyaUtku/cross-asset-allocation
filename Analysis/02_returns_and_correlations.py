import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as mdates
P=pd.read_csv("Clean Data/prices_daily_raw.csv",index_col=0,parse_dates=True)
# ---- returns ----
dur={'US10YT':8.0,'US2YT':1.9,'DE10YT':8.5,'JP10YT':9.0}
R=pd.DataFrame(index=P.index)
for c in ['SPX','STOXX','DAX','MSCI_EM','N225','HYG','LQD','XAU','LCOc1','CLc1','DXY','EURUSD','USDJPY','USDCHF','BTC']:
    s=P[c].dropna(); R[c]=np.log(s).diff()          # return between consecutive observed days
for c,d in dur.items():
    y=P[c].dropna(); y=y.copy()
    dy=y.diff()
    R[c]=(-d*dy+y.shift(1)/252)/100                  # duration-based bond return proxy
# winsorize known benchmark-roll artefact in early 2000 bond series
for c in dur: R.loc[R[c].abs()>0.06,c]=np.nan
R=R.rename(columns={'US10YT':'UST10','US2YT':'UST2','DE10YT':'Bund10','JP10YT':'JGB10','LCOc1':'Brent','CLc1':'WTI','XAU':'Gold','MSCI_EM':'MSCI EM'})
R=R.dropna(how='all')
R.to_csv("Clean Data/returns_daily.csv")

crises=[("GFC","2008-09-01","2009-03-09"),("Euro debt","2011-07-22","2011-10-04"),("China/oil","2015-08-10","2016-02-11"),
        ("Covid","2020-02-19","2020-03-23"),("2022 rate shock","2022-01-03","2022-10-14"),("SVB","2023-03-08","2023-03-31"),("Tariff shock","2025-04-02","2025-04-30")]
# ---- 1. rolling corr ----
W=252
def roll(a,b,w=W,mp=None): return R[a].rolling(w,min_periods=mp or int(w*0.8)).corr(R[b])
pairs={'UST10':'Stocks vs US 10y bond','Gold':'Stocks vs gold','DXY':'Stocks vs US dollar','HYG':'Stocks vs high yield','Brent':'Stocks vs Brent','BTC':'Stocks vs Bitcoin'}
RC=pd.DataFrame({k:roll('SPX',k) for k in pairs})
RC['UST2']=roll('SPX','UST2'); RC['Bund10']=roll('SPX','Bund10'); RC['LQD']=roll('SPX','LQD')
RC.to_csv("Clean Data/rolling_corr_SPX_252d.csv")

BG="#ffffff";INK="#1c2430";GR="#8a94a3";C1="#1f5fbf";C2="#d1495b"
plt.rcParams.update({"font.family":"DejaVu Sans","axes.edgecolor":GR,"axes.labelcolor":INK,"xtick.color":INK,"ytick.color":INK,"axes.spines.top":False,"axes.spines.right":False})
def shade(ax,lab=False):
    for n,a,b in crises:
        ax.axvspan(pd.Timestamp(a),pd.Timestamp(b),color="#f2c14e",alpha=.25,lw=0)
        if lab:
            m=pd.Timestamp(a)+(pd.Timestamp(b)-pd.Timestamp(a))/2
            ax.text(m,.98,n,rotation=90,ha="center",va="top",fontsize=8,color="#7a5c00",transform=ax.get_xaxis_transform())
# hero
fig,ax=plt.subplots(figsize=(11,5.6),dpi=160)
shade(ax,True)
ax.plot(RC.index,RC['UST10'],color=C1,lw=1.8)
ax.axhline(0,color=INK,lw=.8)
ax.set_ylim(-.9,.8); ax.set_ylabel("Rolling 1-year correlation")
ax.set_title("The stock–bond hedge flipped: US equities vs 10y Treasury returns",loc="left",fontsize=14,fontweight="bold",color=INK,pad=26)
ax.text(0,1.02,"Correlation of daily S&P 500 total return with 10y Treasury return proxy, 252-day window. Shaded = crisis windows.",transform=ax.transAxes,fontsize=8.5,color=GR)
ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.fill_between(RC.index,0,RC['UST10'],where=RC['UST10']>0,color=C2,alpha=.18,lw=0)
ax.fill_between(RC.index,0,RC['UST10'],where=RC['UST10']<0,color=C1,alpha=.12,lw=0)
fig.text(.01,.01,"Source: LSEG Workspace; own calculations. Bond return = -duration×Δyield + carry (duration 8).",fontsize=7.5,color=GR)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig("Charts/01_stock_bond_rolling_corr.png"); plt.close()

# small multiples
keys=['Gold','DXY','HYG','Brent','BTC','Bund10']
titles={**pairs,'Bund10':'Stocks vs Bund'}
fig,axs=plt.subplots(3,2,figsize=(11,9),dpi=150,sharex=True)
for ax,k in zip(axs.flat,keys):
    shade(ax); ax.plot(RC.index,RC[k],color=C1,lw=1.4); ax.axhline(0,color=INK,lw=.7)
    ax.set_title(titles[k],loc="left",fontsize=10.5,fontweight="bold"); ax.set_ylim(-.9,.9)
    ax.xaxis.set_major_locator(mdates.YearLocator(4)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
fig.suptitle("Rolling 1-year correlation with S&P 500 (daily returns)",x=.01,ha="left",fontsize=13,fontweight="bold")
fig.text(.01,.005,"Shaded windows: GFC (Sep 2008–Mar 2009), Euro debt (Jul–Oct 2011), China/oil (Aug 2015–Feb 2016), Covid (Feb–Mar 2020), 2022 rate shock (Jan–Oct 2022), SVB (Mar 2023), Tariff shock (Apr 2025).",fontsize=7,color=GR)
fig.tight_layout(rect=(0,.02,1,1)); fig.savefig("Charts/02_rolling_corr_small_multiples.png"); plt.close()

# ---- 2. stock-bond by era ----
eras=[("2000–2006","2000-01-01","2006-12-31"),("2007–2012","2007-01-01","2012-12-31"),("2013–2019","2013-01-01","2019-12-31"),("2020–2021","2020-01-01","2021-12-31"),("2022–2026","2022-01-01","2026-12-31")]
rows=[]
for n,a,b in eras:
    r=R.loc[a:b]; rows.append({"Era":n,**{k:r['SPX'].corr(r[k]) for k in ['UST10','UST2','Bund10','Gold','DXY','HYG','Brent','BTC']}})
E=pd.DataFrame(rows).set_index("Era"); E.to_csv("Clean Data/spx_corr_by_era.csv"); print(E.round(2).to_string())

# ---- 3. crisis matrices ----
cols=['SPX','STOXX','MSCI EM','UST10','Bund10','HYG','LQD','Gold','Brent','DXY','USDJPY','USDCHF','BTC']
calm=R.loc[:, cols].copy()
mask=pd.Series(False,index=R.index)
for n,a,b in crises: mask|=(R.index>=a)&(R.index<=b)
base=R.loc[~mask,cols].corr()
res={}
for n,a,b in crises:
    c=R.loc[a:b,cols].corr(min_periods=10); res[n]=c; c.to_csv(f"Clean Data/crisis_corr_{n.replace(' ','_').replace('/','_')}.csv")
base.to_csv("Clean Data/corr_non_crisis.csv")
# SPX row across crises vs baseline
tab=pd.DataFrame({"Non-crisis":base['SPX'],**{n:res[n]['SPX'] for n,_,_ in crises}}).drop('SPX')
tab.to_csv("Clean Data/spx_corr_crisis_vs_calm.csv"); print(tab.round(2).to_string())
fig,ax=plt.subplots(figsize=(10.5,6.4),dpi=160)
im=ax.imshow(tab.values,cmap="RdBu_r",vmin=-1,vmax=1,aspect="auto")
ax.set_xticks(range(tab.shape[1])); ax.set_xticklabels(tab.columns,rotation=30,ha="right"); ax.set_yticks(range(tab.shape[0])); ax.set_yticklabels(tab.index)
for i in range(tab.shape[0]):
    for j in range(tab.shape[1]):
        v=tab.values[i,j]
        if not np.isnan(v): ax.text(j,i,f"{v:.2f}",ha="center",va="center",fontsize=8,color="white" if abs(v)>.6 else INK)
ax.set_title("Correlation with S&P 500: calm vs crisis windows",loc="left",fontsize=13,fontweight="bold")
for s in ax.spines.values(): s.set_visible(False)
fig.colorbar(im,ax=ax,shrink=.8); fig.text(.01,.01,"Daily returns within each window; short windows (e.g. SVB, Tariff) are noisy. Blank = asset not yet trading. Source: LSEG Workspace.",fontsize=7.5,color=GR)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig("Charts/03_crisis_vs_calm_heatmap.png"); plt.close()

# ---- 4. safe-haven test ----
spx=R['SPX'].dropna(); sig=spx.rolling(252,min_periods=200).std().shift(1)
shock=spx[spx< -2*sig].index
assets=['UST10','UST2','Bund10','Gold','DXY','USDJPY','USDCHF','HYG','Brent','BTC','MSCI EM']
sh=pd.DataFrame({"On SPX < -2σ days (mean)":R.loc[shock,assets].mean(),"Hit rate (asset up)":(R.loc[shock,assets]>0).sum()/R.loc[shock,assets].notna().sum(),"n":R.loc[shock,assets].notna().sum()})
sh.to_csv("Clean Data/safe_haven_test.csv"); print(len(shock),"shock days"); print(sh.round(4).to_string())
# by era hit-rate for key havens
fig,ax=plt.subplots(figsize=(10,5.4),dpi=160)
R['Yen']=-R['USDJPY']; R['Franc']=-R['USDCHF']
hav=['UST10','Gold','Yen','Franc','DXY']
hr=pd.DataFrame({n:{h:(R.loc[[d for d in shock if a<=str(d.date())<=b],h]>0).mean() for h in hav} for n,a,b in eras})
hr.to_csv("Clean Data/safe_haven_hitrate_by_era.csv"); print(hr.round(2).to_string())
x=np.arange(len(eras)); w=.16; cs=["#1f5fbf","#e0a526","#2a9d8f","#7b6fd0","#d1495b"]
for i,h in enumerate(hav): ax.bar(x+(i-2)*w,hr.loc[h].values,w,label=h,color=cs[i])
ax.axhline(.5,color=INK,lw=.8,ls="--"); ax.set_xticks(x); ax.set_xticklabels([e[0] for e in eras]); ax.set_ylim(0,1); ax.set_ylabel("Share of S&P shock days the asset rose")
ax.legend(ncol=5,frameon=False,loc="upper center",bbox_to_anchor=(.5,1.1)); 
ax.set_title("Who actually hedged? Asset up on days S&P fell >2σ",loc="left",fontsize=13,fontweight="bold",pad=30)
fig.text(.01,.01,"σ = trailing 252-day S&P volatility. Yen/Franc = strength vs USD; DXY = broad dollar. Source: LSEG Workspace.",fontsize=7.5,color=GR)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig("Charts/04_safe_haven_hit_rate.png"); plt.close()

# ---- 5. absorption ratio (core assets with long history) ----
core=['SPX','STOXX','DAX','MSCI EM','UST10','Bund10','Gold','Brent','DXY','USDJPY']
Z=R[core].dropna()
ar=[]
idx=Z.index
for i in range(500,len(Z)):
    X=Z.iloc[i-500:i]; X=(X-X.mean())/X.std(); ev=np.linalg.eigvalsh(np.cov(X.values.T)); ar.append(ev[-1]/ev.sum())
AR=pd.Series(ar,index=idx[500:]); AR.to_csv("Clean Data/absorption_ratio.csv")
fig,ax=plt.subplots(figsize=(11,4.8),dpi=160); shade(ax,True); ax.plot(AR.index,AR,color=C1,lw=1.8)
ax.set_title("How much of cross-asset risk is one factor? (absorption ratio)",loc="left",fontsize=13,fontweight="bold")
ax.set_ylabel("Variance explained by 1st principal component"); ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
fig.text(.01,.01,"10 core assets, 500-day rolling window, daily returns. Source: LSEG Workspace.",fontsize=7.5,color=GR)
fig.tight_layout(rect=(0,.03,1,1)); fig.savefig("Charts/05_absorption_ratio.png"); plt.close()
print("AR range",AR.min().round(2),AR.max().round(2),"latest",AR.iloc[-1].round(2))
