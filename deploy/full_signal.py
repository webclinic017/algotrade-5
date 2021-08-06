import requests
import pandas as pd
from datetime import datetime
from os import system, remove
from platform import system as syst

from send_log import SendLog

class FullSignal:
    def __init__(self, symbs):
        self.url = 'https://scanner.tradingview.com/india/scan'
        tickers = [("NSE:"+symb) for symb in symbs]
        self.columns = ["Recommend.All|5|5","Recommend.Other|5",\
                        "Recommend.MA|5","RSI|5","RSI[1]|5","Stoch.K|5",\
                        "Stoch.D|5","Stoch.K[1]|5","Stoch.D[1]|5",\
                        "CCI20|5","CCI20[1]|5","ADX|5",\
                        "ADX-DI|5","ADX-DI[1]|5",\
                        "AO|5","AO[1]|5","Mom|5","Mom[1]|5",\
                        "MACD.macd|5","MACD.signal|5","Rec.Stoch.RSI|5",\
                        "Stoch.RSI.K|5","Rec.WR|5","W.R|5","Rec.BBPower|5",\
                        "BBPower|5","Rec.UO|5","UO|5","EMA5|5",\
                        "close|5","SMA5|5","EMA10|5","SMA10|5",\
                        "EMA20|5","SMA20|5","EMA30|5","SMA30|5",\
                        "EMA50|5","SMA50|5","EMA100|5","SMA100|5",\
                        "EMA200|5","SMA200|5","Rec.Ichimoku|5",\
                        "Ichimoku.BLine|5","Rec.VWMA|5","VWMA|5",\
                        "Rec.HullMA9|5","HullMA9|5","Pivot.M.Classic.S3|5",\
                        "Pivot.M.Classic.S2|5","Pivot.M.Classic.S1|5",\
                        "Pivot.M.Classic.Middle|5","Pivot.M.Classic.R1|5",\
                        "Pivot.M.Classic.R2|5","Pivot.M.Classic.R3|5",\
                        "Pivot.M.Fibonacci.S3|5","Pivot.M.Fibonacci.S2|5",\
                        "Pivot.M.Fibonacci.S1|5","Pivot.M.Fibonacci.Middle|5",\
                        "Pivot.M.Fibonacci.R1|5","Pivot.M.Fibonacci.R2|5",\
                        "Pivot.M.Fibonacci.R3|5","Pivot.M.Camarilla.S3|5",\
                        "Pivot.M.Camarilla.S2|5","Pivot.M.Camarilla.S1|5",\
                        "Pivot.M.Camarilla.Middle|5","Pivot.M.Camarilla.R1|5",\
                        "Pivot.M.Camarilla.R2|5","Pivot.M.Camarilla.R3|5",\
                        "Pivot.M.Woodie.S3|5","Pivot.M.Woodie.S2|5",\
                        "Pivot.M.Woodie.S1|5","Pivot.M.Woodie.Middle|5",\
                        "Pivot.M.Woodie.R1|5","Pivot.M.Woodie.R2|5",\
                        "Pivot.M.Woodie.R3|5","Pivot.M.Demark.S1|5",\
                        "Pivot.M.Demark.Middle|5","Pivot.M.Demark.R1|5"\
                        ]
        self.myobj = {"symbols":{"tickers":tickers,"query":{"types":[]}},"columns":self.columns}

    def fetch(self):
        try:
            x = requests.post(self.url, json = self.myobj)
            strengthDf = pd.DataFrame.from_dict(x.json()["data"])
            strengthDf["symb"] = strengthDf["s"].apply(lambda x: x.split("NSE:")[1])
            for i in range(len(self.columns)):
                strengthDf[self.columns[i].replace("|5","").replace(".","_")] = strengthDf["d"].apply(lambda x: x[i])

            currName = "signals/sig-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".csv"
            strengthDf.to_csv(currName,index=False)
            if not (syst() == "Windows"):
                system(f"aws s3 cp {currName} s3://www.101logs.com.in/signals/")
            remove(currName)
            return

        except Exception as e:
            SendLog(f"Signal Exception: {e}")
            return []