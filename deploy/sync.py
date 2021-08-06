import os
from time import sleep
from datetime import datetime

def Sync():
    while True:
        try:
            os.system("aws s3 sync ./logs/ s3://www.101logs.com.in/")
            os.system("aws s3api put-object-acl --bucket www.101logs.com.in --key index.html --acl public-read")
            if os.path.exists("logs/logs.csv"):
                os.system("aws s3api put-object-acl --bucket www.101logs.com.in --key logs.csv --acl public-read")
        except Exception as e:
            print(f"\nSync Error at: {e}\n")
        sleep(15)
        
        if datetime.now().time() >= datetime(2021, 3, 2, 15, 31, 0).time():
            break