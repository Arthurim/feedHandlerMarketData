#!/usr/bin/env python3
"""
@author: Arthurim
@Description: various utilis for sym handling
"""


def get_sym_format(sym, market):
    """
    Formats the sym to adapt to ECN format, eg XBTUSD will be XBT/USD for Kraken

    :param sym: should be a string of 6 letters
    :param market: should be a string
    :return: string in the right format for the given market
    """
    if not len(sym) >= 6:
        raise ValueError("sym input should be a string of 6 letters, it was: ", sym)
    if is_spot(sym):
        if market == "KRAKEN":
            return sym[0:3] + "/" + sym[3:6]
        elif market == "COINBASE":
            sym = sym.replace("XBT", "BTC")
            return sym[0:3] + "-" + sym[3:6]
        elif market == "BINANCE":
            sym = sym.replace("XBT", "BTC").lower()
            return sym
        elif market == "BITFINEX":
            return sym.replace("XBT", "BTC")
        elif market == "HUOBI":
            return sym.replace("XBT", "BTC").lower()
        else:
            return sym
    elif is_future(sym):
        if market == "KRAKEN":
            return "FI_" + sym.replace("/Future", "").replace("/", "_")
        else:
            return sym
    else:
        raise ValueError("Unknow instrument type for " + sym)


def is_spot(sym):
    return not is_future(sym)


def is_future(sym):
    return len(sym.split("/")) == 3 or len(sym.split("_")) == 3
