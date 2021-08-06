import requests
import pandas as pd
from datetime import datetime
from os import system, remove
from platform import system as syst

from send_log import SendLog

class EntrySignal:
    def __init__(self, symbs, limit):
        self.url = 'https://scanner.tradingview.com/india/scan'
        tickers = [("NSE:"+symb) for symb in symbs]
        self.myobj = {"symbols":{"tickers":tickers,"query":{"types":[]}},"columns":["Recommend.All|5","ADX|5"]}
        self.limit = limit

    def fetch(self):
        try:
            x = requests.post(self.url, json = self.myobj)
            strengthDf = pd.DataFrame.from_dict(x.json()["data"])
            strengthDf["symb"] = strengthDf["s"].apply(lambda x: x.split("NSE:")[1])
            strengthDf["strength"] = strengthDf["d"].apply(lambda x: x[0])
            strengthDf["ADX"] = strengthDf["d"].apply(lambda x: x[1])
            
            strengthDf = strengthDf[strengthDf["strength"]>0.5]
            strengthDf = strengthDf[strengthDf["strength"]<0.6]
            strengthDf = strengthDf[strengthDf["ADX"]>30]
            strengthDf = strengthDf.sort_values(by=['strength'], ascending=False).head(self.limit)
            return list(strengthDf.symb.values)
        except Exception as e:
            SendLog(f"Signal Exception: {e}")
            return []