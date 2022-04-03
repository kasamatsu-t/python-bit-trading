import configparser
import os
from utils.utils import bool_from_str

conf = configparser.ConfigParser()
conf.read('settings.ini')

# API_KEY = conf['bitFlyer']['API_KEY']
# API_SECRET = conf['bitFlyer']['API_SECRET']
API_KEY = os.environ['API_KEY']
API_SECRET = os.environ['API_SECRET']
product_code = conf['bitFlyer']['product_code']

db_name = conf['db']['name']
db_driver = conf['db']['driver']

web_port = int(conf['web']['port'])

trade_duration = conf['pytrading']['trade_duration'].lower()
back_test = bool_from_str(conf['pytrading']['back_test'])
use_percent = float(conf['pytrading']['use_percent'])
past_period = int(conf['pytrading']['past_period'])
stop_limit_percent = float(conf['pytrading']['stop_limit_percent'])
num_ranking = int(conf['pytrading']['num_ranking'])
