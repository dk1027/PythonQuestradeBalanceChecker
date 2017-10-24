import requests
import json
class Context:
    def __init__(self, api_server, access_token, refresh_token):
        self.access_token = access_token
        self.api_server = api_server
        self.refresh_token = refresh_token # this could be used to redeem an access_token again
        self.headers = {'Authorization' : 'bearer '+access_token}
    
    @staticmethod
    def MakeContext(refresh_token):
        url = 'https://login.questrade.com/oauth2/token'
        r = requests.get(url, params={'grant_type' : 'refresh_token', 'refresh_token' : refresh_token})
        if r.status_code == 200:
            j = r.json()
            print("Refresh Token: " + j['refresh_token'])
            return Context(j['api_server'], j['access_token'], j['refresh_token'])
        else:
            print("status_code:{} reason: {}".format(r.status_code, r.text))
            return None
    
    # Use the next refresh token to create a new context
    def Refresh(self):
        new_context = MakeContext(self.refresh_token)
        if new_context:
            self.access_token = new_context.access_token
            self.api_server = new_context.api_server
            self.refresh_token = new_context.refresh_token
            self.headers = new_context.headers
            return True
        return False
    
    def Get(self, url):
        return requests.get(url, headers=self.headers)
    
class Accounts:
    def __init__(self, context):
        self.context = context
        self.urls = {
            'accounts' : '{0}v1/accounts'.format(context.api_server),
            'positions' : '{0}v1/accounts/{{0}}/positions'.format(context.api_server),
            'balances' : '{0}v1/accounts/{{0}}/balances'.format(context.api_server)
        }
        
    # Return list of active account numbers
    def Accounts(self, raw=False):
        r = self.context.Get(self.urls['accounts'])
        if r.status_code == 200:
            if raw:
                return r.json()
            else:
                return list(map(lambda x: x['number'], filter(lambda x : x['status'] == 'Active', r.json()['accounts'])))
        else:
            print(r.status_code)
            print(r.text)

    '''
    Returns positions like:
    [{'currentMarketValue': 5.4, 'symbol': 'ABHD'},
     {'currentMarketValue': 6710.4, 'symbol': 'XCH.TO'},
     {'currentMarketValue': 7526.4, 'symbol': 'ZDB.TO'}]
    '''
    def Positions(self, id, raw=False):
        r = self.context.Get(self.urls['positions'].format(id))
        if raw:
            print(r.json())
            return r.json()
        return list(map(lambda x: {
            'symbol' : x['symbol'], 
            'currentMarketValue' : float(x['currentMarketValue'])}, 
            r.json()['positions']))
    
    '''
    Returns balances in cash like:
    [{'cash': 3224.89, 'currency': 'CAD'}, {'cash': 0.52, 'currency': 'USD'}]
    '''
    def Balances(self, id, raw=False):
        r = self.context.Get(self.urls['balances'].format(id))
        if raw:
            return r.json()
        return list(map(lambda x: {'currency' : x['currency'], 'cash' : float(x['cash'])}, r.json()['sodPerCurrencyBalances']))
    