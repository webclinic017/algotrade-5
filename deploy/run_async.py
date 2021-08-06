import asyncio
import datetime
import pandas as pd

def RunAsync(func,arg1):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func(arg1))