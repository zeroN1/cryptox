from enum import Enum # for api enumeration
import hashlib

class ApiError(Exception):
    '''
        for all class using models
    '''
    def __init__(self, msg):
        super(ApiError, self).__init__(msg)

class _APIFactoryError(Exception):
    '''
        @ Exception : FactoryError
        --------------------------
        low level api instantiation error
    '''
    def __init__(self, msg):
        super(_APIFactoryError, self).__init__(msg)

class _APIs(Enum):
    '''
        @ enum : _APIs
        --------------
        for mapping the api object for instantiation
    '''
    Coinbase, Cexio, Rocktrade, Poloniex, Bitstamp, Gdax = range(6)


class _APImeta(type):
    '''
        @ metaclass : _APImeta
        -----------------------
        @ reqs : api_key
        @ reqs : api_secret
        @ reqs : api type
        @ reqs : api base endpoint
        @ suff : api_pass => optional for 3rd arg
    '''
    
    def __new__(meta, name, bases, clsdct):
        '''
            @ meta   => the `this` instance for metaclass
            @ name   => the name of concrete class
            @ bases  => the class meta
            @ clsdct => cls's `static` vars and method prototypes dict
        '''
        if not '_api_enumid' in clsdct:
            raise _APIFactoryError('The api type was not defined')
        e = clsdct['_api_enumid']
        if not _APImeta._verify_enumid(e):
            raise _APIFactoryError('The api enum id is invalid')
        return super(_APImeta, meta).__new__(meta, name, bases, clsdct)


    def __init__(cls, name, bases, dct):
        '''
            @ cls   : an api class
            @ name  : api class name
            @ bases : cls's namespace (prototype)
            @ dct   : cls's __dict__
        '''
        eid = dct['_api_enumid']
        if eid == _APIs.Rocktrade or eid == _APIs.Poloniex:
            dct['_digestmod'] = hashlib.sha512
        elif eid == _APIs.CoinBase or eid == _APIs.Cexio or \
            eid == _APIs.Bitstamp or eid == _APIs.Gdax:
            dct['_digestmod'] = hashlib.sha256
        super(_APImeta, cls).__init__(name, bases, dct)


    def _verify_enumid(eid):
        if eid != _APIs.CoinBase or \
            eid != _APIs.Cexio or \
            eid != _APIs.Rocktrade or \
            eid != _APIs.Bitstamp or \
            eid != _APIs.Gdax or \
            eid != _APIs.Poloniex:
            return False
        return True
