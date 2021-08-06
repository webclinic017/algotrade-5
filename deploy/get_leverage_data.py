from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from platform import system
from time import sleep
import pandas as pd
import datetime
import os

from get_symbs import GetSymbs
from get_top_moved import GetTopMoved
from run_async import RunAsync
from send_log import SendLog

def GetLeverageData(threshold, kite):        

    while (True):
        try:
            
            PATH = "C:\Program Files (x86)\chromedriver.exe" if ("Windows" in system()) else "/usr/bin/chromedriver"

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920x1080")
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

            browser = webdriver.Chrome(PATH, options=chrome_options)
            browser.implicitly_wait(3)
            browser.get('https://zerodha.com/margin-calculator/Equity/')

            data = {}

            for tex in browser.find_elements_by_tag_name("tr"):
                currText = tex.text
                if ( ("%" in currText) and ("x" in currText) ):
                    currSplit = currText.split("%")
                    data[(', '.join(currSplit[0].split()[0:-1])).replace(",","")] = {"margin percentage": float(currSplit[0].split()[-1]), "leverage": float(currSplit[1].split("x")[0].replace(" ",""))}

            browser.quit()
            df = pd.DataFrame(data).T
            df.to_csv("./logs/Data/leverageData"+datetime.datetime.now().strftime("%d-%m-%Y") +".csv")

            symbWithLevList = list(df[df["leverage"]>=5.0].index)
            ltps = kite.ltp([("NSE:"+symb) for symb in GetSymbs()])

            symbList = [symb for symb in GetSymbs() if ( (symb in symbWithLevList) and ( ( data[symb]["leverage"] * ltps["NSE:"+symb]['last_price'] ) < threshold ) )]
            RunAsync(GetTopMoved,symbList)

            return ((df.T)[list(pd.read_csv("./logs/Data/topMoved_" + datetime.datetime.now().strftime("%d-%m-%Y") +".csv").symb.values)]).to_dict()

        except Exception as e:
            SendLog(f"Leverage Data Exception: {e}")