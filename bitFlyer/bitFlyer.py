from datetime import datetime
import logging
import hashlib
import hmac
import requests
import json

logger = logging.getLogger(__name__)


class Balance(object):
    def __init__(self, currency, available):
        self.currency = currency
        self.available = available


class Ticker(object):
    def __init__(self, product_code, timestamp, bid, ask, volume):
        self.product_code = product_code
        self.timestamp = timestamp
        self.bid = bid
        self.ask = ask
        self.volume = volume


class APIClient(object):
    def __init__(self, api_key, api_secret, api_method, path_url, param={}, environment='practice'):
        self.base_url = "https://api.bitflyer.jp"
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_method = api_method
        self.path_url = path_url
        self.timestamp = str(datetime.datetime.today())
        if param != {}:
            self.body = json.dumps(param)
        else:
            self.body = ''
        message = self.timestamp + self.api_method + self.path_url + self.body
        self.signature = hmac.new(bytearray(api_secret.encode('utf-8')), message.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        self.headers = {
            'ACCESS-KEY': self.api_key,
            'ACCESS-TIMESTAMP': self.timestamp,
            'ACCESS-SIGN': self.signature,
            'Content-Type': 'application/json'
        }

    def get_balance(self):
        path_url = "/v1/me/getbalance"
        try:
            res = requests.get(self.base_url + path_url, headers=self.headers).json()
        except requests.exceptions.RequestException as e:
            logger.error(f'action=get_balance error={e}')
            raise
        return res

    def get_ticker(self, product_code) -> Ticker:
        query = '?product_code=' + product_code
        path_url = "/v1/ticker"
        try:
            res = requests.get(self.base_url + path_url + query).json()
        except requests.exceptions.RequestException as e:
            logger.error(f'action=get_ticker error={e}')
            raise
        product_code = res['product_code']
        timestamp = res['timestamp']
        bid = res['best_bid']
        ask = res['best_ask']
        volume = res['volume']
        return Ticker(product_code, timestamp, bid, ask, volume)
