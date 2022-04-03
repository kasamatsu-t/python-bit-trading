import json
import websocket
from datetime import datetime, timedelta
import dateutil.parser
import math
from logging import getLogger, INFO, StreamHandler
import settings
import constants
import requests
from app.models.candle import factory_candle_class
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)


def get_timestamp(d):
    timestamp = d["timestamp"].replace('T', ' ')[:-1]
    return dateutil.parser.parse(timestamp) + timedelta(hours=9)


def create_candle_with_duration(duration, ohlc, price, now, tick_time):
    period = constants.TRADE_MAP[duration]["second"]
    cls = factory_candle_class(settings.product_code, duration)
    if(ohlc["date"] != tick_time):
        if(ohlc["date"] != ""):
            # get volume from https://docs.cryptowat.ch/rest-api/markets/ohlc
            after = int(datetime.strptime(tick_time, '%Y-%m-%d %H:%M:%S').timestamp())
            before = int(now.timestamp())
            cryptowatch_api = "https://api.cryptowat.ch/markets/bitflyer/ethjpy/ohlc?periods={}&after={}&before={}"
            result = requests.get(cryptowatch_api.format(period, after, before)).json()["result"]
            volume = result[str(period)][0][-2]
            logger.info("{}, {}, {}, {}, {}, {}, {}, {}".format(duration + '-ohlc', now, ohlc["date"], ohlc["open"], ohlc["high"], ohlc["low"], ohlc["close"], volume))
            cls.create(now, ohlc["open"], ohlc["high"], ohlc["low"], ohlc["close"], volume)
        ohlc["date"] = tick_time
        ohlc["open"] = price
        ohlc["high"] = price
        ohlc["low"] = price
        ohlc["close"] = price
        return ohlc
    # OHLC データの時刻が同じ場合
    else:
        ohlc["high"] = max(ohlc["high"], price)
        ohlc["low"] = min(ohlc["low"], price)
        ohlc["close"] = price
        return ohlc


"""
This program calls Bitflyer real time API JSON-RPC2.0 over Websocket
"""


class RealtimeAPI(object):
    def __init__(self, url, channel, duration):
        self.url = url
        self.channel = channel
        self.duration = duration
        self.ohlc5s = {}
        self.ohlc5s["date"] = ""
        self.ohlc1m = {}
        self.ohlc1m["date"] = ""
        self.ohlc1h = {}
        self.ohlc1h["date"] = ""

        # Define Websocket
        self.ws = websocket.WebSocketApp(self.url, header=None, on_open=self.on_open, on_message=self.on_message, on_error=self.on_error, on_close=self.on_close)
        websocket.enableTrace(False)

    def run(self):
        # ws has loop. To break this press ctrl + c to occur Keyboard Interruption Exception.
        self.ws.run_forever()
        logger.info('Web Socket process ended.')

    """
  Below are callback functions of websocket.
  """

    # when we get message

    def on_message(self, ws, message):
        output = json.loads(message)['params']
        now = datetime.now()
        ts = get_timestamp(output["message"])
        # 約定データが現在時刻より過去の場合は捨てる
        # if(datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second) < datetime(now.year, now.month, now.day, now.hour, now.minute, now.second)):
        #     return
        cls = factory_candle_class(settings.product_code, self.duration)
        price = float(output["message"]["ltp"])
        product_code = output["message"]["product_code"]
        timestamp = output["message"]["timestamp"]
        bid = float(output["message"]["best_bid"])
        ask = float(output["message"]["best_ask"])
        # OHLC データの時刻が更新された場合
        new_second = math.floor(ts.second / 5) * 5
        ts5s = datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, new_second)
        tick_time_5s = ts5s.strftime("%Y-%m-%d %H:%M:%S")
        tick_time_1m = ts.strftime("%Y-%m-%d %H:%M:00")
        tick_time_1h = ts.strftime("%Y-%m-%d %H:00:00")
        # self.ohlc5s = create_candle_with_duration('5s', self.ohlc5s, price, now, tick_time_5s)
        self.ohlc1m = create_candle_with_duration('1m', self.ohlc1m, price, now, tick_time_1m)
        self.ohlc1h = create_candle_with_duration('1h', self.ohlc1h, price, now, tick_time_1h)

    # when error occurs
    def on_error(self, ws, error):
        logger.error(error)

    # when websocket closed.
    def on_close(self, ws):
        logger.info('disconnected streaming server')

    # when websocket opened.
    def on_open(self, ws):
        logger.info('connected streaming server')
        logger.info('duration ' + self.duration)
        output_json = json.dumps(
            {'method': 'subscribe',
             'params': {'channel': self.channel}
             }
        )
        ws.send(output_json)
