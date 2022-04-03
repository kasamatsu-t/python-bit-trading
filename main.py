import datetime
import logging
import sys
from threading import Thread

import constants
import app.models
from app.controllers.webserver import start
import settings
from bitFlyer.realtimeapi import RealtimeAPI
from bitFlyer.bitFlyer import Ticker
from bitFlyer.bitFlyer import APIClient
import concurrent.futures

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


if __name__ == "__main__":
    serverThread = Thread(target=start)
    serverThread.start()
    
    # 5s, 1m, 1h 足のチャート情報を取得してsql dbに保存
    url = 'wss://ws.lightstream.bitflyer.com/json-rpc'
    channel = 'lightning_ticker_ETH_JPY'
    json_rpc = RealtimeAPI(url=url, channel=channel, duration='1m')
    json_rpc.run()

    # Web app
    # start().run()
