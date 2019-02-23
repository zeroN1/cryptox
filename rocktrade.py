from .models import _APIs, _APImeta, _APIFactoryError, ApiError
from urllib.error import HTTPError
from functools import wraps
import re
import json

class Rocktrade(object):
    __metaclass__ = _APImeta
    _api_enumid = _APImeta.Rocktrade
    _rate_limit = 10 # reqs/sec
    _base_url = 'https://api.therocktrading.com/v1/'
    _services = {
        'getBalance'                : 'balance/{curr}',    # balance/cur
        'getBalances'               : 'balances',           # all balances
        'getCurrencyDiscountInfo'   : 'discounts/{curr}',  # discount /curr
        'getUserDiscountInfo'       : 'discounts',
        'getCurrencyWithdrawLimit'  : 'withdraw_limits/{curr}',
        'getWithdrawLimits'         : 'withdraw_limits',
        'getPositionBalances'       : 'funds/{fund_id}/position_balances',
        'getPositions'              : 'funds/{fund_id}/positions',
        'getShowPositions'          : 'funds/{fund_id}/postions/{pos_id}',
        'getFund'                   : 'funds/{fund_id}',
        'getFunds'                  : 'funds',
        'getOrderbook'              : 'funds/{fund_id}/orderbook',
        'getTicker'                 : 'funds/{fund_id}/ticker',
        'getTickers'                : 'funds/tickers',
        'getTrades'                 : 'funds/{fund_id}/trades',
        'deleteAllOpenOrders'       : 'funds/{fund_id}/orders/remove_all',
        'deleteCancelOrder'         : 'funds/{fund_id}/orders/{order_id}',
        'getOrders'                 : 'funds/{fund_id}/orders',
        'postPlaceOrder'            : 'funds/{fund_id}/orders',
        'postShowOrder'             : 'funds/{fund_id}/orders/{order_id}',
        'getShowTransaction'        : '/transactions/{trans_id}',
        'getUserTransactions'       : 'transactions',
        'getUserTrades'             : 'funds/{fund_id}/trades',
        'postAtmWithdraw'           : 'atms/withdraw',
    }

    def __init__(self, **kwargs):
        if not 'api_key' in kwargs:
            raise ApiError('Api key needed')
        self._key = kwargs['api_key']
        if not 'api_secret' in kwargs:
            raise ApiError('Api secret needed')
        self._secret = kwargs['api_secret']
        self._verb_patterns = []
        for pat in self._http_options:
            self._verb_patterns.append(re.compile(pat))
            self._verb_patterns.append(re.compile(pat.upper()))

    def _prepare_head(self, endpoint):
        '''
            prepare an endpoint for request
            call everytime a new endpoint is needed
            ----------------------------------------
            @ params  : the endpoint for the req
            @ returns : a prepared header for request
        '''
        return {
            'Content-Type' : 'application/json',
            'X-TRT-KEY'    : self._key.encode(),
            'X-TRT-SIGN'   : hmac.new(
                self._secret.encode(),
                (str(self.nonce()) + endpoint).encode(),
                self._digestmod
            ).hexdigest()
        }

    def nonce(self):
        return time.time()*1e6

    def get(self, f, endpoint, *args, **kwargs):
        '''
            constructs a get query
            ----------------------
            @ params : f        => a callable that one arg, response json
            @ params : endpoint => service to request
        '''
        if f is None or not callable(f):
            raise ApiError('Expected a callable object')
        @wraps
        def _get():
            try:
                r = requests.get(endpoint)
                return f(json.dumps(r.body))
            except HTTPError as hte:
                raise ApiError('Could not connect to endpoint')
        try:
            return _get()
        except ApiError as ae:
            # log this
            raise ae


    def post(self, f, endpoint, *args, **kwargs):
        '''
            constructs a post request
            -------------------------
            @ params : f        => the repsone json handler
            @ params : endpoint => the endpoint to connect to service
        '''
        if f is None or not callable(f):
            raise ApiError('Expected a callable object')
        @wraps
        def _post():
            try:
                r = request.post(
                    endpoint.format(**kwargs),
                    headers=self._prepare_head(endpoint)
                )
            except Exception as e:
                # log this
                pass
        try:
            return _post()
        except Exception as e:
            # log
            pass

    def getserv(self, serv, method='get', *args, **kwargs):
        '''
            @ params : serv   => key to map _services endpoint
            @ params : method => the request method GET/POST
        '''
        try:
            method ,endpoint = self._endpoint_match(serv)
        except ApiError as ae:
            raise ae
        m = Rocktrade.Model()
        @self.__dict__[method.lower()](endpoint, args, kwargs)
        def _populate(resp):
            '''
                the json response handler
            '''
            map(
                lambda k,v : m._add(k,v),
                json.loads(resp).iteritems()
            )
        return m

    def _endpoint_match(self, serv):
        '''
            @ _endpoint_match
            -----------------
            @ params  : serv => the service endpoint requested
            @ returns : a 2 tuple, (method, endpoint); else (None, None)
        '''
        if serv not in self._services:
            raise ApiError('No such services')
        for pat in self._verb_patterns:
            m = pat.fullmatch(serv)
            if m is not None:
                break
        if m is None:
            return (None, None,)
        return (m.match, self._services[serv])

    class Model(object):
        pass # dummy model for all endpoint responses
        def __init__(self):
            self._params = {}

        def _add(self, k, v):
            self._params.update({
                k : v
            })

        def _json(self):
            import json
            return json.loads(self._params)
            
