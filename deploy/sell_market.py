def SellMarket(kite, symb, qty):
    return kite.place_order(tradingsymbol=symb, exchange=kite.EXCHANGE_NSE, transaction_type=kite.TRANSACTION_TYPE_SELL,\
           quantity=qty, order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_MIS, variety=kite.VARIETY_REGULAR)