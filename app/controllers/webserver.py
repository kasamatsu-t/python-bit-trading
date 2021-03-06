from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask_cors import CORS

from app.models.dfcandle import DataFrameCandle

import constants
import settings

app = Flask(__name__, template_folder='../views')
CORS(app)


@app.teardown_appcontext
def remove_session(ex=None):
    from app.models.base import Session
    Session.remove()


# @app.route('/')
# def index():

#     df = DataFrameCandle(settings.product_code, settings.trade_duration)
#     df.set_all_candles(settings.past_period)
#     candles = df.candles
#     return render_template('./google.html', candles=candles)


@app.route('/api/candle/', methods=['GET'])
def api_make_handler():
    product_code = request.args.get('product_code')
    if not product_code:
        return jsonify({'error': 'No product_code params'}), 400

    limit_str = request.args.get('limit')
    limit = 1000
    if limit_str:
        limit = int(limit_str)

    if limit < 0 or limit > 1000:
        limit = 1000

    duration = request.args.get('duration')
    if not duration:
        duration = constants.DURATION_1M
    duration_time = constants.TRADE_MAP[duration]['duration']
    df = DataFrameCandle(product_code, duration_time)
    df.set_all_candles(limit)
    return jsonify(df.value), 200


def start():
    app.run(host='0.0.0.0', port=settings.web_port, threaded=True)
