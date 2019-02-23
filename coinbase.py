from .models import _APIs, _APImeta, _APIFactoryError, ApiError
from urllib.error import HTTPError
from functools import wraps,
import hmac
import base64

class Coinbase(object):
    '''
        @ class : Coinbase
        ---------------
        the entire Coinbase api
    '''
    __metaclass__ = _APImeta
    _api_enumid = _APIs.Coinbase
    _base_urls = {
        'gdax' : 'https://api/coinbase.com/v2/',
        'fix'  : ''
    }
    _rate_limits = 2 # 10,000 / hour
    _services = {
        'getShowUser'           : 'users/{user_id}',           # leading g=GET, p=POST
        'getUser'               : 'user',
        'getUserAuthInfo'       : 'user/auth',
        'getAccountHolds'       : 'accounts/{acc_id}/holds',
        'postOrders'            : 'orders',
        'deleteOrder'           : 'orders/{order_id}',
        'deleteOrders'          : 'orders',
        'getOrders'             : 'orders',
        'getOrder'              : 'orders/{order_id}',
        'getRecentFills'        : 'fills',
        'getFundings'           : 'funding',
        'postRepayFunding'      : 'funding/repay',
        'getMarginTransfer'     : 'profiles/margin-transfer',
        'getProfileOverview'    : 'position',
        'postPositionClose'     : 'position/close',
        'postDepositFrom'       : 'deposits/payment-method',
        'postMoveFunds'         : 'deposits/coinbase-account',
        'postWithdrawTo'        : 'withdrawls/payment-method',
        'postWithdrawToCoinBase': 'withdrawls/coinbase',
        'postWithdrawToCrypto'  : 'withdrawls/crypto',
        'getPaymentMethods'     : 'payment-methods',
        'getCoinbaseAccounts'   : 'coinbase-accounts',
        'postNewReport'         : 'reports',
        'getReportStatus'       : 'reports/{report_id}',
        'get30DayTrailingVolume': 'users/self/trailing-volume',
        'getAvailCurrencyPairs' : 'products',
        'getProductOpenOrders'  : 'products/{prod_id}/book',
        'getProductTicker'      : 'products/{prod_id}/ticker',
        'getProductLatestTrades': 'products/{prod_id}/trades',
        'getProductCandleData'  : 'products/{prod_id}/candles',
        'get24HourStat'         : 'products/{prod_id}/stats',
        'getCurrencies'         : 'currencies',
        'getApiServerTime'      : 'time',
    }
    _req_headers = [
        'CB-ACCESS-KEY',        # api key as str
        'CB-ACCESS-SIGN',       # api signature
        'CB-ACCESS-TIMESTAMP',
        'CB-ACCESS-PASSPHRASE'  # api passphrase
    ]
    def __init__(self, **kwargs):
        if not 'api_key' in kwargs:
            raise ApiError('An api key was not provided')
        setattr(self, '_api_key', kwargs['api_key'])
        if not 'api_secret' in kwargs:
            raise ApiError('A secret was not provided')
        setattr(self, '_api_secret', kwargs['_api_secret'])
        if not 'api_passphrase' in kwargs:
            raise ApiError('A passphrase was not provided')
        setattr(self, '_api_passphrase', kwargs['api_passphrase'])

    def nonce(self):
        return time.time()

    def _prepare(self, endpoint, method='get', **kwargs):
        if endpoint is None:
            raise ApiError('No end point given')
        body = '?'
        map(
            lambda k,v : body.join(k + '=' + v),
            kwargs.iteritems()
        )
        if body == '?':
            body = ''
        return {
            'Content-Type'  : 'application/json',
            _req_headers[0] : self._api_key,
            _req_headers[1] : hmac.new(
                base64.b64decode(self._api_secret),
                str(self.nonce()) + method.upper() + endpoint + (body or ''),
                self._hmac
            ).digest().encode('base64').rstrip('\n'),
            _req_headers[2] : str(self.nonce()),
            _req_headers[3] : self._api_passphrase
        }
