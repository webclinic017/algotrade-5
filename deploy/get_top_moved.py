from time import time
import csv
import requests
import pandas as pd
import arrow
import datetime
import aiohttp
import asyncio
import os

from send_log import SendLog

async def GetTopMoved(company):

    sourceDfName = "./logs/Data/current.csv"
    pd.DataFrame(columns=["symb","DTMC"]).to_csv(sourceDfName, index=False)

    outName = "./logs/Data/topMoved_" + datetime.datetime.now().strftime("%d-%m-%Y") +".csv"

    async def async_quote_data(symb, sourceDfName, isNameIssue):
        client = aiohttp.ClientSession()
        try:
            data_range = "1d"
            data_interval = "5m"
            if isNameIssue:
                symbol = symb.replace("_","&") + '.NS'
            else:
                symbol = symb + '.NS'
            res = await client.get('https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={data_range}&interval={data_interval}'.format(**locals()))
            data = await res.json()
            body = data['chart']['result'][0]    
            dt = datetime.datetime
            dt = pd.Series(map(lambda x: arrow.get(x).to('Asia/Calcutta').datetime.replace(tzinfo=None), body['timestamp']), name='Datetime')
            df = pd.DataFrame(body['indicators']['quote'][0], index=dt)
            df = df.loc[:, ('open', 'high', 'low', 'close', 'volume')]
            df.dropna(inplace=True)     #removing NaN rows
            df.columns = ['Open', 'High','Low','Close','Volume']    #Renaming columns in pandas
            df.index.name = 'Date'
            await client.close()
            val = (df["Close"]*df["Volume"]).sum()
            with open(sourceDfName, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([symb,val])

        except Exception as e:
            await client.close()
            err = str(e)
            if ( ("'NoneType' object is not subscriptable" in err) and ("_" in symb) ) and (not isNameIssue):
                await async_quote_data(symb,sourceDfName,True)
            else:
                SendLog(f"Get Top Moved Error at: {symb} : {err}")

    startTime = time()
    await asyncio.gather(*[async_quote_data(com, sourceDfName, False) for com in company])
    SendLog(f"Get Top Moved : Yfin data fetched in {time()-startTime} seconds.")

    answer =  pd.read_csv(sourceDfName).sort_values(by=['DTMC'], ascending=False).head(40)
    answer.to_csv(outName, index=False)
    os.remove(sourceDfName)