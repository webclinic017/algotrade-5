from datetime import datetime
from os import system

from send_log import SendLog
from script import Script
from sync import Sync

if (datetime.now().year>2021):
    SendLog("2021 has passed. Deployment Shut Down")
    while True:
        pass
else:
    if (datetime.now().time()<datetime(2021,3,31,15,24,0).time()):
        isTradingDay = True

        holidays = [ (26,1), (11,3), (29,3), (2,4), (14,4), (21,4), (13,5), (21,7), (19,8), (10,9), (15,10), (4,11), (5,11), (19,11), (25,12) ]

        if (datetime.now().weekday() == 5) or (datetime.now().weekday() == 6):
            SendLog("Today is a Weekend")
            isTradingDay = False
        elif ( True in [( ( datetime.now().day==d[0] ) and ( datetime.now().month==d[1] ) ) for d in holidays] ):
            SendLog("Today is a Holiday")
            isTradingDay = False
        else:
            pass

        while True:
            if ( (datetime.now().time()>datetime(2021,3,31,8,30,0).time()) and (datetime.now().time()<datetime(2021,3,31,15,25,0).time()) ):
                if isTradingDay:
                    Script()
                else:
                    Sync()
                break

    else:
        while True:
            if not ( (datetime.now().time()<datetime(2021,3,31,8,30,0).time()) or (datetime.now().time()>datetime(2021,3,31,15,32,0).time()) ):
                break