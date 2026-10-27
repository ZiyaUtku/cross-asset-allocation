import pandas as pd,numpy as np,matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
INK="#14202e";GR="#6b7686";BR="#7a5c00"
plt.rcParams.update({"font.family":"DejaVu Sans"})
R=pd.read_csv("Clean Data/returns_daily.csv",index_col=0,parse_dates=True)
R['Yen']=-R['USDJPY']; R['Franc']=-R['USDCHF']
rows=[("UST10","10y Treasury"),("Bund10","10y Bund"),("Gold","Gold"),("Yen","Yen (vs USD)"),("Franc","Franc (vs USD)"),("DXY","US dollar index"),("Brent","Brent oil"),("HYG","High yield (price)"),("BTC","Bitcoin")]
cr=[("GFC","2008-09-01","2009-03-09","Sep 2008–Mar 2009"),("Euro debt","2011-07-22","2011-10-04","Jul–Oct 2011"),("China / oil","2015-08-10","2016-02-11","Aug 2015–Feb 2016"),("Covid","2020-02-19","2020-03-23","Feb–Mar 2020"),("2022 rate shock","2022-01-03","2022-10-14","Jan–Oct 2022"),("SVB","2023-03-08","2023-03-31","Mar 2023"),("Tariff shock","2025-04-02","2025-04-30","Apr 2025")]
m=pd.Series(False,index=R.index)
for _,a,b,_ in cr: m|=(R.index>=a)&(R.index<=b)
cols=["Calm\n(all non-crisis days)"]; data=[[R.loc[~m,'SPX'].corr(R.loc[~m,k]) for k,_ in rows]]; ns=[int((~m).sum())]
for n,a,b,l in cr:
    r=R.loc[a:b]; data.append([r['SPX'].corr(r[k]) if r[k].notna().sum()>=15 else np.nan for k,_ in rows]); ns.append(len(r)); cols.append(f"{n}\n{l}")
D=np.array(data).T
fig=plt.figure(figsize=(13.5,7.6),dpi=142); fig.patch.set_facecolor("white")
fig.text(.055,.955,"How assets moved with the S&P 500 in each crisis",fontsize=21,fontweight="bold",color=INK,va="top")
fig.text(.055,.895,"Correlation of daily returns with the S&P 500 inside each crisis window vs all other days. Blue = moved opposite to stocks (hedge); red = moved with stocks.",fontsize=11.5,color=GR,va="top")
ax=fig.add_axes([.17,.19,.80,.60])
im=ax.imshow(D,cmap="RdBu_r",vmin=-1,vmax=1,aspect="auto")
ax.set_xticks(range(D.shape[1])); ax.set_xticklabels(cols,fontsize=9.5,color=INK); ax.xaxis.tick_top()
ax.set_yticks(range(D.shape[0])); ax.set_yticklabels([l for _,l in rows],fontsize=11,color=INK)
ax.tick_params(length=0)
for i in range(D.shape[0]):
    for j in range(D.shape[1]):
        v=D[i,j]
        t="n/a" if np.isnan(v) else f"{v:+.2f}".replace("-","−")
        ax.text(j,i,t,ha="center",va="center",fontsize=11,fontweight="bold" if not np.isnan(v) and abs(v)>.5 else "normal",color="white" if not np.isnan(v) and abs(v)>.55 else INK)
for s in ax.spines.values(): s.set_visible(False)
for x in np.arange(-.5,D.shape[1],1): ax.axvline(x,color="white",lw=2)
for y in np.arange(-.5,D.shape[0],1): ax.axhline(y,color="white",lw=2)
ax.axvline(.5,color=INK,lw=2)
fig.text(.055,.075,"Windows: SVB (18 trading days), Covid (24) and Tariff shock (21) are short, so treat their correlations as indicative. n/a = fewer than 15 observations (asset not trading yet).\nYen and franc shown as strength vs USD (inverse of USDJPY, USDCHF). Credit is price return only. 10y Bund/Treasury returns = −duration × Δyield + carry. Source: LSEG Workspace, own calculations.",fontsize=8,color=GR,va="top",linespacing=1.5)
fig.savefig("Charts/LINKEDIN_crisis_heatmap.png",facecolor="white")
pd.DataFrame(D,index=[l for _,l in rows],columns=[c.replace("\n"," | ") for c in cols]).round(3).to_csv("Clean Data/linkedin_heatmap_values.csv")
print(pd.DataFrame(D,index=[l for _,l in rows],columns=[c.split("\n")[0][:8] for c in cols]).round(2).to_string()); print(ns)
