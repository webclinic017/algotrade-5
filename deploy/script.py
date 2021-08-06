from threads import Threads
from send_log import SendLog
from refresh_data import RefreshData
from sync import Sync

from platform import system

import threading

def Script():
    if not (system() == 'Windows'):
        RefreshData()

    ts = Threads()
    ts.initiate()

    # creating threads
    t1 = threading.Thread(target=ts.stream, name='t1')
    t2 = threading.Thread(target=ts.deploy, name='t2')
    t3 = threading.Thread(target=Sync, name='t3')

    # starting threads
    t1.start()
    t2.start()
    t3.start()

    # wait until all threads finish
    t1.join()
    t2.join()
    t3.join()

    SendLog("Main Shut Down")