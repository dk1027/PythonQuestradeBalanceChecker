import pandas as pd
import datetime
from QuestradeWrapper import Context
from QuestradeWrapper import Accounts
import QuestradeConfig as cfg
from QuestradeToken import Token
from FuncUtils import *
import asyncio
from functools import partial

class DataTransform:
    def __init__(self):
        self.mapping = cfg.symbol_category_mapping

    def Map(self, line, key):
        return self.mapping[key][line[key]]
    
    def Today(self):
        return int(''.join(map(lambda x: str(x), list(datetime.date.today().timetuple())[:3])))
    
    # at the end we should end up with {time, accountId, category, symbol, currentMarketValue}
    def Position(self, accountId, line):
        return {
            'time' : self.Today(),
            'accountId' : accountId,
            'category' : self.Map(line, 'symbol'),
            'symbol' : line['symbol'],
            'currentMarketValue' : line['currentMarketValue']
        }
    
    def Balance(self, accountId, line):
        return {
            'time' : self.Today(),
            'accountId' : accountId,
            'category' : 'CASH',
            'symbol' : line['currency'],
            'currentMarketValue' : line['cash']
        }
        

class QuestradeDatasource:
    def __init__(self, refresh_token):
        self.context = Context.MakeContext(refresh_token)
        if self.context is None:
            print("Error initiating data source")
        return
    
    def GetRefreshToken(self):
        return self.context.refresh_token

    def GetPositions(self):
        dt = DataTransform()
        accounts = Accounts(self.context).Accounts()
        accounts
        records = []

        loop = asyncio.new_event_loop()
        
        def PositionHandler(id, res):
            for line in res:
                records.append(dt.Position(id, line))

        def BalanceHandler(id, res):
            for line in res:
                records.append(dt.Balance(id, line))

        funcs = [MakeFunc(partial(Accounts(self.context).Positions, id), partial(PositionHandler, id)) for id in accounts] + [MakeFunc(partial(Accounts(self.context).Balances, id), partial(BalanceHandler, id))for id in accounts]
        async def doit():
            await AsyncRunAll(loop, funcs)
        loop.run_until_complete(doit())
        df = pd.DataFrame(records)
        # Ignoring USD because I personally do not wish to account for USD cash in my calculations
        return df[(df['category'].notnull()) & (df['symbol'] != 'USD')]

'''
Example usage:
with QuestradeDatasourceManager() as data_sources:
    for aDs in data_sources:
        print(aDs.GetRefreshToken())
'''
class QuestradeDatasourceManager:   
    def __init__(self):
        return
    
    def __enter__(self):
        # Load tokens, connect, and save next set of refresh tokens
        token = Token.MakeToken()
        refresh_tokens = token.Load()
        new_refresh_tokens = []
        ds = []
        for tok in refresh_tokens:
            aDs = QuestradeDatasource(tok)
            ds.append(aDs)
            new_refresh_tokens.append(aDs.GetRefreshToken())
        token.Save(new_refresh_tokens)
        return ds
    
    def __exit__(self, type, value, traceback):
        return

