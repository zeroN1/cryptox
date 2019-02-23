from .models import _APIs, _APImeta, _APIFactoryError, ApiError
from urllib.error import HTTPError
from functools import wraps
import time
import hmac
import json
import requests
from itertools import filterfalse
import re

class Bitstamp(object):
    '''
        @ class Bitstamp
        ----------------
        the Bitstamp api
    '''
    __metaclass__ = _APImeta
    _api_enumid = _APIs.Bitstamp
    _http_options = [
        'get', 'post', 'put', 'delete'
    ]
    _rate_limit = 0
    _base_url = 'https://bitstamp.net/api/v2/'
    _services = {
        'getTicker'                     : 'ticker/{curr_pair}/',
        'getTickerHourly'               : 'ticker_hour/{curr_pair}/',
        'getOrderBook'                  : 'order_book/{curr_pair}/',
        'getTransactions'               : 'transactions/{curr_pair}/',
        'getEurToUSD'                   : 'eur_usd/',
        'postAccountBalance'            : 'balance/',
        'postUserTransaction'           : 'user_transactions/{curr_pair}/',
        'postOpenOrders'                : 'open_orders/{curr_pair}/',
        'postOrderStatus'               : 'order_status/',
        'postCancelOrder'               : 'cancel_order/',
        'postCancelAllOrders'           : 'cancel_all_orders/',
        'postBuyLimitOrder'             : 'buy/{curr_pair}/',
        'postBuyMarketOrder'            : 'buy/market/{curr_pair}/',
        'postSellLimitOrder'            : 'sell/{curr_pair}/',
        'postSellMarketOrder'           : 'sell/market/{curr_pair}/',
        'postWithdrawlRequest'          : 'withdrawl_requests/',
        'postBitcoinWithdrawl'          : 'bitcoin_withdrawl/',
        'postBitCoinDepositAddress'     : 'bitcoin_deposit_address/',
        'postUnconfirmedBitcoinDeposit' : 'unconfirmed_btc/',
        'postRippleWithdrawl'           : 'ripple_withdrawl/',
        'postRippleDepositAddress'      : 'ripple_address/',
        'postTransferToMainAccount'     : 'transfer-to-main/',
        'postTransferFromMainAccount'   : 'transfer-from-main/',
        'postXrpWithdrawl'              : 'xrp_withdrawl/',
        'postXrpDepositAddress'         : 'xrp_address/',
        'postOpenBankWithdrawl'         : 'withdrawl/open/',
        'postBankWithdrawlStatus'       : 'withdrawl/status',
        'postCancelBankWithdrawl'       : 'withdrawl/cancel/',
        'postNewLiquidationAddress'     : 'liquidation_address/new/',
        'postLiquidationAddressInfo'    : 'liquidation_address/info/'

    }
    def __init__(self, **kwargs):
        if not 'api_key' in kwargs:
            raise ApiError('No api key provided')
        self._api_key = kwargs['api_key']
        if not 'api_secret' in kwargs:
            raise ApiError('No api secret given')
        self._api_secret = kwargs['api_secret']
        if not 'customer_id' in kwargs:
            raise ApiError('No customer id provided')
        self._customer_id = kwargs['customer_id']
        self._verb_patterns = []
        for pat in self._http_options:
            self._verb_patterns.append(re.compile(pat))
            self._verb_patterns.append(re.compile(pat.upper()))


    def nonce(self):
        return time.time()

    def _prepare_params(self, dct):
        '''
            @ _prepare_auth
            ---------------
            prepares a request params for endpoints
            unlike other apis, auth params are added to body
            rather than header
            @ params : dct => any additional params to add to the request
        '''
        n = str(self.nonce())
        return dct.update({
            'Content-Type' : 'application/json',
            'key'          : self._api_key,
            'signature'    : hmac.new(
                self._api_secret,
                n.join(self._customer_id + self._api_key),
                self._hmac
            ).hexdigest().upper(),
            'nonce'       : n

        })

    def get(self, endpoint, **kwargs):
        print('in get')
        def aux(f):
            nonlocal endpoint
            if f is None or not callable(f):
                raise ApiError('Expected a callable object')
            endpoint = endpoint.format(**kwargs)
            @wraps(f)
            def _get():
                nonlocal endpoint
                try:
                    r = requests.get(Bitstamp._base_url + endpoint)
                    return f(r.json())
                except HTTPError as hte:
                    raise ApiError('Could not complete the request')
            return _get()
        return aux

    def post(self, endpoint, **kwargs):
        def aux(f):
            if f is None or not callable(f):
                raise ApiError('Expected a callable object')
            if not 'url_params' in kwargs:
                raise ApiError('Expected url parameters for this endpoint')
            endpoint = endpoint.format(**kwargs['url_params'])
            kwargs.pop('url_params')
            @wraps
            def _post():
                try:
                    r = requests.post(endpoint, params=self._prepare_params(kwargs))

                    return r
                except HTTPError as hte:
                    raise ApiError('Could not post the request')
            try:
                return _post()
            except ApiError:
                raise

    def getserv(self, serv, **kwargs):
        method, endpoint = self._endpoint_match(serv)
        if endpoint is None:
            raise ApiError('No such service')
        m = Bitstamp.Model()
        @self.get(endpoint, **kwargs)
        def _populate(resp):
            for k,v in resp.items():
                m._add(k,v)

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
            m = pat.match(serv)
            if m is not None:
                break
        if m is None:
            return (None, None,)
        return (m.group(0), self._services[serv])

    class Model(object):
        pass # dummy model for all endpoint responses
        def __init__(self):
            self._params = {}

        def _add(self, k, v):
            self._params[k] = v

        def _json(self):
            return self._params


if __name__ == '__main__':
    b_api = Bitstamp(
        api_key='XXXXXXXXX',
        api_secret='XXXXXXX',
        customer_id='XXXXXX'
    )
    resp = b_api.getserv(serv='getTicker', curr_pair='btcusd')
    print(resp._json())
