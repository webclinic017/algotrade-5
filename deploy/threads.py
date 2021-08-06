from datetime import datetime, timedelta
import csv
import pandas as pd
from os import path

from kite_login import KiteLogin
from get_symbs import GetSymbs
from entry_signal import EntrySignal
from get_leverage_data import GetLeverageData
from env import Env
from send_log import SendLog

class Threads():
    def __init__(self):
        self.master = {symbName:None for symbName in GetSymbs()}
        self.kite, self.kws = None, None
        self.masterTokens = []
        self.masterName = "./logs/KiteData/master-" + datetime.now().strftime('%d-%m-%Y %H-%M-%S') + ".csv"
        self.currInstr = None
        self.currMaster = None
        self.entry_signal = None
        self.leverageData = None
        self.budget = None
        self.tradeLimit = 3
        self.env = None

        currDt = datetime.now()
        maxTime = max(datetime(2021, 3, 2, 9, 30, 0),datetime(2021,3,2,currDt.hour,currDt.minute,0))
        self.sigTime = datetime(2021, 3, 2, 9, 30, 0)
        while True:
            if self.sigTime<maxTime:
                self.sigTime += timedelta(minutes=5)
            else:
                break

    def initiate(self):
        while True:
            try:
                if datetime.now().time() >= datetime(2021, 3, 2, 8, 45, 0).time():

                    SendLog("Logging into Kite")
                    self.kite, self.kws = KiteLogin()
                    if not path.exists("./logs/Data/budget"+datetime.now().strftime("%d-%m-%Y")+".csv"):
                        self.budget = self.kite.margins(self.kite.MARGIN_EQUITY)['net']
                        pd.DataFrame({"budget":self.budget},index=[0]).to_csv( ("./logs/Data/budget"+datetime.now().strftime("%d-%m-%Y")+".csv") ,index=False)
                        SendLog(f"Today's Budget is {self.budget}")
                    else:
                        self.budget = float(pd.read_csv("./logs/Data/budget"+datetime.now().strftime("%d-%m-%Y")+".csv").values[0][0])

                    SendLog("Fetching Leverage Data")
                    self.leverageData = GetLeverageData((self.budget/self.tradeLimit), self.kite)
                    self.currInstr = list(self.leverageData.keys())
                    self.env = Env(self.budget, self.leverageData, self.tradeLimit)

                    instr = self.kite.instruments(exchange="NSE")
                    for mast in list(self.master.keys()):
                        for inst in instr:
                            mastCopy = mast
                            if ( (mastCopy.replace("_", "&") == inst['tradingsymbol']) or (mast == inst['tradingsymbol']) ):
                                self.master[mast] = inst['instrument_token']
                    self.masterTokens = list(self.master.values())
                    self.currMaster = {symbName:self.master[symbName] for symbName in self.currInstr}

                    self.entry_signal = EntrySignal(self.currInstr, self.tradeLimit)

                    if not (path.exists(self.masterName)):
                        pd.DataFrame(columns=["Ticks"]).to_csv(self.masterName, index=False)

                    SendLog("Initiated Threads")

                    return

            except Exception as e:
                SendLog(f"Threads Initiate Exception: {e}")

    def deploy(self):

        while True:
            if datetime.now().time() >= datetime(2021, 3, 2, 9, 29, 0).time():
                break

        while True:

            if datetime.now().time() >= self.sigTime.time():

                self.env.update(self.kite)

                if ( self.sigTime.time() >= datetime(2021, 3, 2, 15, 10, 0).time() ):
                    self.env.exitAll(self.kite, isMarket=True)
                    SendLog("Deployment Done for the Day")
                    break
                elif ( self.sigTime.time() >= datetime(2021, 3, 2, 14, 40, 0).time() ):
                    self.env.exitAll(self.kite, isMarket=False)
                else:
                    currSigs = self.entry_signal.fetch()
                    SendLog(f"{self.sigTime}")
                    if ( len(currSigs) > 0 ):
                        self.env.entry(currSigs, self.kite)
                    else:
                        SendLog("No Signals")

                self.sigTime += timedelta(minutes=5)

                [ SendLog( f"Symb: {pos['tradingsymbol']}, Leverage: { ( (self.leverageData[pos['tradingsymbol']]['leverage']) if (pos['tradingsymbol'] in self.leverageData.keys()) else ('Cant be fetched now') ) }, P & L : {pos['pnl']}, Actual Entry Value: {pos['sell_value']}, Used Entry Value: { ( (pos['sell_value'] / self.leverageData[pos['tradingsymbol']]['leverage']) if (pos['tradingsymbol'] in self.leverageData.keys()) else ('Cant be fetched now') ) }, Sell Price: {pos['sell_price']}, Sell Qty: {pos['sell_quantity']}, Buy Price: {pos['buy_price']}, Buy Qty: {pos['buy_quantity']}") for pos in self.kite.positions()['net']]

            self.env.slmExit(self.kite)

    def stream(self):

        masterTokens, masterName = self.masterTokens, self.masterName

        def on_ticks(ws, ticks):            
            with open(masterName, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(ticks)

            if datetime.now().time() >= datetime(2021, 3, 2, 15, 30, 0).time():
                SendLog("Ticks Done for the Day")
                self.kws.close()

        def on_connect(ws, response):

            ws.subscribe(masterTokens)
            ws.set_mode(ws.MODE_FULL, masterTokens)
            SendLog("Tick Stream Launched")

        def on_close(ws, code, reason):

            ws.stop()

        self.kws.on_ticks = on_ticks
        self.kws.on_connect = on_connect
        self.kws.on_close = on_close

        while True:
            if datetime.now().time() >= datetime(2021, 3, 2, 9, 29, 0).time():
                break

        self.kws.connect(threaded=True)