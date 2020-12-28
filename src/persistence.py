#!/usr/bin/env python3
"""
@author: Arthurim
@Description:
"""
import datetime
import json
import logging
import time

from src.constants.markets import is_supported_market
from .ohlcs import persist_ohlc_to_kdb
from .orderbooks import persist_orderbook_to_kdb
from .spreads import persist_spread_to_kdb
from .trades import persist_trades_to_kdb
from .utils.persistence_utils import get_args_for_subscription
from .utils.websocket_message_handler import create_ws_subscription_logger, create_wss_connection_url_for_market, \
    is_event_WS_result, is_info_WS_result


def persist_subscription_result_to_kdb(result, subscription_type, arg=""):
    if subscription_type == "orderbooks":
        arg = persist_orderbook_to_kdb(arg, result)
    elif subscription_type == "trades":
        persist_trades_to_kdb(result)
    elif subscription_type == "ohlcs":
        persist_ohlc_to_kdb(result)
    elif subscription_type == "spreads":
        persist_spread_to_kdb(result)
    else:
        raise ValueError("This subscription_type is not yet supported: " + str(subscription_type))
    return arg


def create_ws_subscription_kdb_persister(subscription_type, sym, market, depth=10):
    """
    Creates a WS subscription subscription_type for a given market and instrument
    subscription_type can be: trades, orderbooks,
    sym: XBTUSD etc
    market: see markets in SUPPORTED_MARKETS
    """
    if not is_supported_market(market):
        raise ValueError("Market not supported: " + market)
        # TODO: log it
    # TODO: check that sym is valid
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    app_log = create_ws_subscription_logger(subscription_type, sym, market)
    app_log.info('Creating a WS' + subscription_type + ' subcscription for ' + sym + " on " + market)
    try:
        ws = create_wss_connection_url_for_market(subscription_type, market, sym)
        app_log.info('WS ' + subscription_type + ' subcscription for ' + sym + " on " + market + " is successful")
    except Exception as error:
        app_log.error(
            'WS ' + subscription_type + ' subcscription for ' + sym + " on " + market + "- Caught the following error:\n" + repr(
                error))
        time.sleep(3)
        raise ConnectionError(
            "Stopping WS " + subscription_type + ' subcscription for ' + sym + " on " + market + " - Subscription failed")

    arg = get_args_for_subscription(subscription_type, sym, market)

    while True:
        try:
            result = ws.recv()
            # TODO handle heartbeats
            result = json.loads(result)
            app_log.info(
                'WS ' + subscription_type + ' subcscription for ' + sym + " on " + market + " - Received  '%s'" % result)
            if not (is_event_WS_result(result) or is_info_WS_result(result)):
                arg = persist_subscription_result_to_kdb(result, subscription_type, arg)
        except Exception as error:
            app_log.error(
                'WS ' + subscription_type + ' subcscription for ' + sym + " on " + market + ' - create_ws_subscription_orderbook - Caught this error: ' + repr(
                    error))
            time.sleep(3)


def create_ws_subscription_kdb_persister_debug(subscription_type, sym, market, debug_time=1):
    """
    Creates a WS subscription subscription_type for a given market and instrument for debug_time minutes
    subscription_type can be: trades, orderbooks,
    sym: XBTUSD etc
    market: see markets in SUPPORTED_MARKETS
    debug_time: duration of the subscription in minutes
    """
    end_time = datetime.datetime.now() + datetime.timedelta(0, 60 * debug_time)
    if not is_supported_market(market):
        raise ValueError("Market not supported: " + market)
        # TODO: log it
    # TODO: check that sym is valid
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    app_log = create_ws_subscription_logger(subscription_type, sym, market)
    app_log.info('Creating a WS' + subscription_type + ' subcscription for ' + sym + " on " + market)
    try:
        ws = create_wss_connection_url_for_market(subscription_type, market, sym)
        app_log.info('WS ' + subscription_type + ' subcscription for ' + sym + " on " + market + " is successful")
    except Exception as error:
        app_log.error(
            'WS ' + subscription_type + ' subcscription for ' + sym + " on " + market + "- Caught the following error:\n" + repr(
                error))
        time.sleep(3)
        raise ConnectionError(
            "Stopping WS " + subscription_type + ' subcscription for ' + sym + " on " + market + " - Subscription failed")

    arg = get_args_for_subscription(subscription_type, sym, market)

    while datetime.datetime.now() < end_time:
        try:
            result = ws.recv()
            # TODO handle heartbeats and disconnections
            result = json.loads(result)
            app_log.info(
                'WS ' + subscription_type + ' subcscription for ' + sym + " on " + market + " - Received  '%s'" % result)
            if not (is_event_WS_result(result) or is_info_WS_result(result)):
                arg = persist_subscription_result_to_kdb(result, subscription_type, arg)
        except Exception as error:
            app_log.error(
                'WS ' + subscription_type + ' subcscription for ' + sym + " on " + market + ' - create_ws_subscription_orderbook - Caught this error: ' + repr(
                    error))
            time.sleep(3)
