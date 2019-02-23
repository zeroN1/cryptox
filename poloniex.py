from .models import _APIs, _APImeta, _APIFactoryError, ApiError
from urllib.error import HTTPError
from functools import wraps

class Poloniex(object):
    __metaclass__ = _APImeta
    _api_enumid = _APImeta.Poloniex
    _rate_limit = 6 # reqs/sec
    _base_url = 'https://poloniex.com/'
    _services = [
        'getTicker'                    : 'public?command=returnTicker',
        'get24HourVolume'              : 'public?command=return24hVolume',
        'getOrderBook'                 : 'public?command=returnOrderBook&currencyPair={curr_pair}&depth={depth}',
        'getTradeHistory'              : 'public?command=returnTradeHistory&currencyPair={curr_pair}&start={start}&end={end}',
        'getCandleData'                : 'public?command=returnChartData&currencyPair={curr_pair}&start={start}&end={end}&period={period}',
        'getCurrencies'                : 'public?command=returnCurrencies',
        'getLoanOrders'                : 'public?command=returnLoan&currency={curr}',
        'postBalances'                 : 'tradingApi?command=returnBalances',
        'postCompleteBalances'         : 'tradingApi?command=returnCompleteBalances&account={account}',
        'postDepositAddress'           : 'tradingApi?command=returnDepositAddresses',
        'postGenerateNewAddresses'     : 'tradingApi?command=generateNewAddresses&currency={curr}',
        'postDepositsWithdrawls'       : 'tradingApi?command=returnDepositWithdrawls&start={start}&end={end}',
        'postOpenOrders'               : 'tradingApi?command=returnOpenOrders&currencyPair={curr_pair}',
        'postTradeHistory'             : 'tradingApi?command=returnTradeHistory&currencyPair={curr_pair}&start={start}&end={end}',
        'postOrderTrades'              : 'tradingApi?command=returnOrderTrades&orderNumber={order_number}',
        'postBuy'                      : 'tradingApi?command=buy&currencyPair={curr_pair}&rate={rate}&amount={amount}',
        'postSell'                     : 'tradingApi?command=sell&currencyPair={curr_pair}&rate={rate}&amount={amount}',
        'postCancelOrder'              : 'tradingApi?command=cancelOrder&orderNumber={order_number}',
        'postMoveOrder'                : 'tradingApi?command=moveOrder&orderNumber={order_number}&rate={rate}&amount={amount}',
        'postWithdraw'                 : 'tradingApi?command=withdraw&currency={curr}&amount={amount}&address={address}',
        'postFeeInfo'                  : 'tradingApi?command=returnFeeInfo&returnFeeInfo',
        'postAvailableAccountBalances' : 'tradingApi?command=returnAvailableAccountBalances&account={account}',
        'postTradeableBalances'        : 'tradingApi?command=returnTradeableBalances&returnTradeableBalances',
        'postTransferBalance'          : 'tradingApi?command=transferBalance&currency={curr}&amount={amount}&fromAccount={from}&toAccount={to}',
        'postMarginAccountSummary'     : 'tradingApi?command=returnMarginAccountSummary',
        'postMarginBuy'                : 'tradingApi?command=marginBuy&currencyPair={curr_pair}&rate={rate}&amount={amount}&lendingRate={lending_rate}',
        'postMarginSell'               : 'tradingApi?command=marginSell&currencyPair={curr_pair}&rate={rate}&amount={amount}&lendingRate={lending_rate}',
        'postMarginPosition'           : 'tradingApi?command=getMarginPosition&currencyPair={curr_pair}',
        'postCloseMarginPosition'      : 'tradingApi?command=getCloseMarginPosition&currencyPair={curr_pair}',
        'postCreateLoanOffer'          : 'tradingApi?command=createLoanOffer&currency={curr}&amount={amount}&duration={duration}&autoRenew={auto_renew}&lendingRate={lending_rate}',
        'postCancelLoanOffer'          : 'tradingApi?command=cancelLoanOffer&currency={curr}&amount={amount}&duration={duration}&autoRenew={auto_renew}&lendingRate={lending_rate}',
        'postOpenLoanOffers'           : 'tradingApi?command=returnOpenLoanOffers',
        'postActiveLoans'              : 'tradingApi?command=returnActiveLoans',
        'postLendingHistory'           : 'tradingApi?command=returnLendingHistory&start={start}&end={end}&limit={limit}',
        'postToggleAutoRenew'          : 'tradingApi?command=toggleAutoRenew&orderNumber={order_number}'

    ]

    def __init__(self, **kwargs):
        if not 'api_key' in kwargs:
            raise ApiError('No api key provided')
        self._api_key = kwargs['api_key']
        if not 'api_secret' in kwargs:
            raise ApiError('No api secret provided')
        setattr(self, '_api_secret', kwargs['api_secret'])

    def _prepare(self, postdata):
        return {
            'Content-Type' : 'application/json',
            'Key'          : self._api_key,
            'Sign'         : hmac.new(
                self._api_secret.encode(),
                json.dumps(postdata),
                self._hmac
            ),
            'nonce'        : str(self.nonce())
        }

    def get(self, endpoint, *args, **kwargs):
        '''
            constructs a get request
            ----------------------
            @ params : f        => a callable that one arg, response json
            @ params : endpoint => service to request
        '''
        def aux(f):
            if f is None or not callable(f):
                raise ApiError('Expected a callable object')
            endpoint = Poloniex._services['endpoint']
            if endpoint is None:
                raise ApiError('No such endpoints exists')
            @wraps
            def _get():

                try:
                    r = requests.get(
                        endpoint.format(**kwargs),
                    )
                    return f(r.json())
                except HTTPError as hte:
                    raise ApiError('Could not connect to endpoint')
            try:
                return _get()
            except ApiError:
                # log this
                pass
        return aux


    def post(self, endpoint, *args, **kwargs):
        '''
            constructs a post request
            -------------------------
            @ params : f        => the repsone json handler
            @ params : endpoint => the endpoint to connect to service
            @ params : payload  => expecting to be the payload form body
        '''
        def aux(f):
            if f is None or not callable(f):
                raise ApiError('Expected a callable object')
            if endpoint is None:
                raise ApiError('An endpoint was not provided')
            endpoint = Poloniex._services['endpoint']
            if endpoint is None:
                raise ApiError('No such endpoint exists')
            params = self._parse_params(endpoint, **kwargs)
            endpoint = Poloniex._base_url + endpoint.split('?')[0]
            @wraps
            def _post():
                import json
                try:
                    r = requests.post(
                        endpoint,
                        params=params,
                        headers=self._prepare(params)
                    )
                except HTTPError as hte:
                    # log this
                    pass
            try:
                return _post()
            except Exception as e:
                # log
                pass
        return aux

    def _parse_params(self, endpoint, **kwargs):
        '''
            @ _parse_params
            ---------------
            @ params  : endpoint => a serv endpoint
            @ returns : a payload dict
        '''
        e = endpoint.split('?')[1].split('&')
        if len(e) > 1:
            # this endpoint takes extra params
            params = {}
            for p in e[1:]: # skipping command
                key = p.split('=')[-1][1:-1]
                if not key in kwargs:
                    raise ApiError('The following param was not procvided' + key)
                params[key] = kwargs[key]
            return params
        return {
            'command' : e.split('=')[-1]
        }


    def getserv(self, serv, method='get', *args, **kwargs):
        '''
            @ params : serv   => key to map _services endpoint
            @ params : method => the request method GET/POST
        '''
        end = Poloniex._services[serv]
        if end is None:
            raise ApiError('No such service endpopint exists')
        m = Poloniex.Model()
        @self.__dict__[method](endpoint, args, kwargs)
        def _populate(resp):
            '''
                the json response handler
            '''
            import json
            map(
                lambda k,v : m._add(k,v),
                json.loads(resp).iteritems()
            )
        return m

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
