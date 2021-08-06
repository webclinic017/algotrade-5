from datetime import datetime
import pandas as pd
import os
import threading
from platform import system
from time import sleep

def SendLog(text):

    def job(text):
        initHtml = """<!DOCTYPE html>
        <html lang="en">
        <head>
        <title>Deploy 101 Logs</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        body {
        font-family: Arial, Helvetica, sans-serif;
        color: green;
        background-color: black;
        }
        </style>
        </head>
        <body>

        <h1>""" + datetime.now().strftime("%d-%m-%Y") + """ Logs</h1>\n"""

        endHtml = """</body>
        </html>"""

        file1 = open("logs/index.html", "w")
        file1.write(initHtml)
        file1.close()

        if not os.path.exists("logs/logs.csv"):
            df = pd.DataFrame(columns=["datetime","logs"])
        else:
            df = pd.read_csv("logs/logs.csv")
        
        df = df.append({"datetime": datetime.now(), "logs": text}, ignore_index=True)
        df = df.dropna()
        df.to_csv("logs/logs.csv",index=False)

        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.set_index('datetime')
        df = df.loc[datetime.now().strftime("%Y-%m-%d")].sort_values(by=['datetime'])

        index = df.index
        logs = df.logs.values
        lines = [( "<p>" + str(index[i]) + " : " + str(logs[i]) + "</p>\n") for i in range(len(logs))]

        f = open("logs/index.html", "a")
        f.writelines(lines)
        f.close()

        file1 = open("logs/index.html", "a")
        file1.write(endHtml)
        file1.close()

    print(f'\n{text}\n')

    try:
        job(text)
    except Exception as e:
        print(f"\nWrite Log Error: {e}\n")
        sleep(5)
        try:
            job(text)
        except Exception as e2:
            print(f"\nSecond Write Log Error: {e2}\n")        