from sell_limit import SellLimit
from buy_limit import BuyLimit
from buy_market import BuyMarket
from send_log import SendLog

from datetime import datetime
from time import sleep

class Env:
    def __init__(self, initBalance, leverageData, tradeLimit=5):
        self.initBalance = initBalance
        self.invested = {}
        self.sellCount = 0
        self.buyCount = 0
        self.tradeLimit = tradeLimit
        self.unitTradeBudget = self.initBalance / self.tradeLimit

        self.sl = {symb: ( ( ( 250 * leverageData[symb]["leverage"] ) / 5 ) * ( ( 5 * initBalance ) / ( tradeLimit * 100000 ) ) )\
                  for symb in list(leverageData.keys())}
        self.leverageData = leverageData
        self.marketOrderSleep = 2
        self.currBidCount = 3
        self.maxpnl = {}

    def update(self, kite):
        for order in kite.orders():

            if ( (order['status'] == 'CANCELLED') or (order['status'] == 'REJECTED') ):
                pass

            else:

                if order['filled_quantity'] > 0:

                    if order['transaction_type'] == 'SELL':

                        if order['tradingsymbol'] not in list(self.invested.keys()):
                            self.invested[order['tradingsymbol']] = order['filled_quantity']
                        else:
                            self.invested[order['tradingsymbol']] += order['filled_quantity']

                        SendLog(f"Order {order['order_id']}: Fullfilled Entry Order for {order['filled_quantity']} {order['tradingsymbol']} at {order['average_price']}")
                        self.sellCount += 1

                    elif order['transaction_type'] == 'BUY':

                        if order['tradingsymbol'] not in list(self.invested.keys()):
                            self.invested[order['tradingsymbol']] = -order['filled_quantity']
                        else:
                            self.invested[order['tradingsymbol']] -= order['filled_quantity']

                        SendLog(f"Order {order['order_id']}: Fullfilled Exit Order for {order['filled_quantity']} {order['tradingsymbol']} at {order['average_price']}")

                        # if self.invested[order['tradingsymbol']]>0:
                        #     currOrd = BuyMarket(kite, order['tradingsymbol'], self.invested[order["tradingsymbol"]])
                        #     sleep(self.marketOrderSleep)
                        #     SendLog(f"Order {currOrd}: Fullfilled Exit Order for {self.invested[order['tradingsymbol']]} {order['tradingsymbol']} at {order['average_price']}")
                        #     self.invested[order['tradingsymbol']] = 0

                        self.buyCount += 1

                if not (order["status"] == 'COMPLETE'):
                    kite.cancel_order(kite.VARIETY_REGULAR, order['order_id'])
                    SendLog(f"Cancelled Order {order['order_id']}")
        self.currBidCount = 0

    def slmExit(self, kite):

        for position in kite.positions()['net']:
            tempQty = position['sell_quantity'] - position['buy_quantity']
            if ( tempQty > 0 ):
                pnl = ( position['sell_price'] - kite.ltp("NSE:"+position["tradingsymbol"])["NSE:"+position["tradingsymbol"]]['last_price'] )\
                      * position['sell_quantity']

                if (position["tradingsymbol"] not in self.maxpnl.keys()):
                    self.maxpnl[position["tradingsymbol"]] = 0

                self.maxpnl[position["tradingsymbol"]] = max(pnl, self.maxpnl[position["tradingsymbol"]])

                if pnl < ( - self.sl[ position["tradingsymbol"] ] + self.maxpnl[position["tradingsymbol"]] ):
                    currOrd = BuyMarket(kite, position['tradingsymbol'], tempQty)
                    SendLog(f"Order {currOrd}: Placed Market Order due to SL for {tempQty} {position['tradingsymbol']}")

        sleep(self.marketOrderSleep)
        
    def entry(self, signals, kite):

        for sig in signals:
            if ( self.currBidCount < ( self.tradeLimit - self.sellCount ) ):
                if sig not in list(self.invested.keys()):
                    tempPrice = kite.ltp("NSE:"+sig)["NSE:"+sig]['last_price']
                    tempQty = int( ( int( self.unitTradeBudget / tempPrice ) ) * ( self.leverageData[sig]["leverage"] ) )
                    if tempQty > 0:
                        currOrd = SellLimit(kite, sig, tempPrice, tempQty)
                        SendLog(f"Order {currOrd}: Placed Entry Limit Order for {tempQty} {sig} at {tempPrice}")
                        self.currBidCount += 1
                    
    def exitAll(self, kite, isMarket=False):

        for position in kite.positions()['net']:
            tempQty = position['sell_quantity'] - position['buy_quantity']
            if tempQty>0:
                if isMarket:
                    currOrd = BuyMarket(kite, position['tradingsymbol'], tempQty)
                    SendLog(f"Order {currOrd}: Placed Exit Market Order for {tempQty} {position['tradingsymbol']}")
                else:
                    tempPrice = kite.ltp("NSE:"+position["tradingsymbol"])["NSE:"+position["tradingsymbol"]]['last_price']
                    BuyLimit(kite, position['tradingsymbol'], tempPrice, tempQty)
                    SendLog(f"Order {currOrd}: Placed Exit Limit Order for {tempQty} {position['tradingsymbol']} at {tempPrice}")
        if isMarket:
            sleep(self.marketOrderSleep)