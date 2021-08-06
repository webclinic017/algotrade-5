def BuyLimit(kite, symb, price, qty):
    return kite.place_order(tradingsymbol=symb, exchange=kite.EXCHANGE_NSE, transaction_type=kite.TRANSACTION_TYPE_BUY,\
           quantity=qty, order_type=kite.ORDER_TYPE_LIMIT, product=kite.PRODUCT_MIS, price=price, variety=kite.VARIETY_REGULAR)