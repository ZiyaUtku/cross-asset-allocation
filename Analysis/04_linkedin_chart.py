import pandas as pd,numpy as np,matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.dates as mdates
INK="#14202e";GR="#6b7686";BLUE="#1f5fbf";RED="#c8394d";GOLD="#d99a1c";TEAL="#1d8f83";SH="#f3d98a";BR="#7a5c00"
plt.rcParams.update({"font.family":"DejaVu Sans","axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#b9c0ca","xtick.color":INK,"ytick.color":INK})
rc=pd.read_csv("Clean Data/rolling_corr_SPX_252d.csv",index_col=0,parse_dates=True)['UST10'].dropna()
wk=pd.read_csv("Clean Data/rolling_corr_SPX_UST10_weekly52.csv",index_col=0,parse_dates=True).iloc[:,0].dropna()
R=pd.read_csv("Clean Data/returns_daily.csv",index_col=0,parse_dates=True); Wk=pd.read_csv("Clean Data/returns_weekly.csv",index_col=0,parse_dates=True)
hr=pd.read_csv("Clean Data/safe_haven_hitrate_by_era.csv",index_col=0)
eras=[("2000–06","2000","2006"),("2007–12","2007","2012"),("2013–19","2013","2019"),("2020–21","2020","2021"),("2022–26","2022","2026")]
crises=[("GFC","2008-09-01","2009-03-09"),("Euro debt","2011-07-22","2011-10-04"),("China / oil","2015-08-10","2016-02-11"),("Covid","2020-02-19","2020-03-23"),("2022 rate shock","2022-01-03","2022-10-14"),("SVB","2023-03-08","2023-03-31"),("Tariff shock","2025-04-02","2025-04-30")]
fig=plt.figure(figsize=(13.5,7.6),dpi=142); fig.patch.set_facecolor("white")
gs=fig.add_gridspec(2,2,width_ratios=[2.15,1],left=.055,right=.975,top=.80,bottom=.15,hspace=.62,wspace=.17)
fig.text(.055,.955,"S&P 500 vs 10-year US Treasury: how the correlation changed, 2000–2026",fontsize=21,fontweight="bold",color=INK,va="top")
fig.text(.055,.895,"Rolling 1-year correlation of daily returns. Below zero, Treasuries tended to rise when stocks fell; above zero, they moved together.",fontsize=11.5,color=GR,va="top")
ax=fig.add_subplot(gs[:,0])
for n,a,b in crises:
    ax.axvspan(pd.Timestamp(a),pd.Timestamp(b),color=SH,alpha=.38,lw=0)
    m=pd.Timestamp(a)+(pd.Timestamp(b)-pd.Timestamp(a))/2
    ax.text(m,.985,n,rotation=90,ha="center",va="top",fontsize=8.5,color=BR,fontweight="bold",transform=ax.get_xaxis_transform())
ax.fill_between(rc.index,0,rc,where=rc>0,color=RED,alpha=.20,lw=0); ax.fill_between(rc.index,0,rc,where=rc<0,color=BLUE,alpha=.12,lw=0)
ax.plot(rc.index,rc,color=BLUE,lw=2.2,label="Daily returns, 1-year window")
ax.plot(wk.index,wk,color=INK,lw=1.1,ls=(0,(4,2)),label="Weekly returns (robustness check)")
ax.axhline(0,color=INK,lw=1); ax.set_ylim(-.98,.7); ax.set_xlim(pd.Timestamp("2000-06-01"),pd.Timestamp("2027-01-01"))
ax.set_yticks([-.8,-.4,0,.4]); ax.set_yticklabels(["−0.8","−0.4","0","+0.4"]); ax.tick_params(length=0)
ax.xaxis.set_major_locator(mdates.YearLocator(2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y")); ax.tick_params(axis="x",labelsize=9.5)
ax.grid(axis="y",color="#e6e9ee",lw=.8); ax.set_axisbelow(True)
ax.text(pd.Timestamp("2012-07-17"),-.965,"Low −0.73 (Jul 2012)",ha="center",fontsize=10,color=BLUE,va="bottom")
ax.annotate("Turns positive\nJun 2021 (daily)",xy=(pd.Timestamp("2021-04-15"),.02),xytext=(pd.Timestamp("2016.9".replace("2016.9","2016-11-01")),.28),fontsize=10.5,color=RED,fontweight="bold",arrowprops=dict(arrowstyle="-",color=RED,lw=1))
ax.text(pd.Timestamp("2026-12-01"),-.64,"Latest: +0.32 daily\n+0.20 weekly",ha="right",fontsize=10.5,color=RED,fontweight="bold",va="top")
ax.text(.012,.05,"Negative: hedge works",transform=ax.transAxes,fontsize=10,color=BLUE,fontweight="bold")
ax.text(.012,.95,"Positive: both fall together",transform=ax.transAxes,fontsize=10,color=RED,fontweight="bold",va="top")
ax.legend(loc="lower right",frameon=False,fontsize=9.5,handlelength=2.5)
x=np.arange(5)
ax=fig.add_subplot(gs[0,1]); w=.36
d=[R.loc[a:b,'SPX'].corr(R.loc[a:b,'UST10']) for _,a,b in eras]; ww=[Wk.loc[a:b,'SPX'].corr(Wk.loc[a:b,'UST10']) for _,a,b in eras]
ax.bar(x-w/2,d,w,color=[RED if v>0 else BLUE for v in d],label="Daily"); ax.bar(x+w/2,ww,w,color=[RED if v>0 else BLUE for v in ww],alpha=.45,label="Weekly")
for i,v in enumerate(d): ax.text(i-w/2,v+(.03 if v>0 else -.03),f"{v:+.2f}".replace("-","−"),ha="center",va="bottom" if v>0 else "top",fontsize=8.5)
ax.axhline(0,color=INK,lw=1); ax.set_xticks(x); ax.set_xticklabels([e[0] for e in eras],fontsize=9); ax.set_ylim(-.68,.3); ax.tick_params(length=0)
ax.set_yticks([-.6,-.3,0,.3]); ax.set_yticklabels(["−0.6","−0.3","0","+0.3"],fontsize=9)
ax.set_title("Average correlation by era",loc="left",fontsize=12,fontweight="bold",color=INK)
ax.text(0,-.2,"Solid = daily returns, light = weekly returns",transform=ax.transAxes,fontsize=8.5,color=GR,va="top")
ax=fig.add_subplot(gs[1,1]); w=.26
for i,(k,c,l) in enumerate([("UST10",BLUE,"10y Treasury"),("Gold",GOLD,"Gold"),("Yen",TEAL,"Yen")]):
    ax.bar(x+(i-1)*w,hr.loc[k].values,w,color=c,label=l)
ax.axhline(.5,color=INK,lw=1,ls="--"); ax.set_ylim(0,1); ax.set_xticks(x); ax.set_xticklabels([e[0] for e in eras],fontsize=9); ax.tick_params(length=0)
ax.set_yticks([0,.5,1]); ax.set_yticklabels(["0%","50%","100%"],fontsize=9)
ax.set_title("Share of S&P shock days the asset rose",loc="left",fontsize=12,fontweight="bold",color=INK)
ax.legend(frameon=False,fontsize=8.5,ncol=3,loc="lower center",bbox_to_anchor=(.5,-.3),handlelength=1.2,columnspacing=1)
fig.text(.055,.055,"Shock day = S&P 500 falls by more than 2 trailing-1-year standard deviations (225 days since 2000). Bond return = −duration × Δyield + carry (duration 8).\nWeekly = Friday-to-Friday. Crisis windows: GFC Sep 2008–Mar 2009; Euro debt Jul–Oct 2011; China/oil Aug 2015–Feb 2016; Covid Feb–Mar 2020; 2022 rate shock Jan–Oct 2022; SVB Mar 2023; Tariff shock Apr 2025.\nSource: LSEG Workspace, own calculations.",fontsize=8,color=GR,va="top",linespacing=1.5)
fig.savefig("Charts/LINKEDIN_combined.png",facecolor="white"); print("ok")
