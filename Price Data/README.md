# Price Data (not included)

LSEG Workspace data cannot be redistributed, so the raw exports are not part of this repository.

To reproduce the analysis, export each series from LSEG Workspace (Price History, **daily**, 01-Jan-2000 to today) as an Excel file and save it in this folder with these names:

| File | RIC / series |
|---|---|
| SPX.xlsx | .SPXTR (S&P 500 total return) |
| STOXX.xlsx | .STOXX (STOXX Europe 600) |
| DAX.xlsx | .GDAXI (DAX gross return) |
| MSCI EM.xlsx | .dMIEF00000PUS (MSCI EM, USD) |
| N225.xlsx | .N225TR (Nikkei 225 total return) |
| US10YT.xlsx, US2YT.xlsx | US10YT=RR, US2YT=RR |
| DE10YT.xlsx, JP10YT.xlsx | DE10YT=RR, JP10YT=RR |
| HYG.xlsx, LQD.xlsx | HYG, LQD (price only) |
| XAU.xlsx | XAU= (spot gold) |
| LCOc1.xlsx, CLc1.xlsx | LCOc1 (Brent), CLc1 (WTI) |
| DXY.xlsx | .DXY |
| EURUSD.xlsx, USDJPY.xlsx, USDCHF.xlsx | EUR=, JPY=, CHF= |
| BTC.xlsx | BTC= |

Then run `python Analysis/01_build_panel.py`.
