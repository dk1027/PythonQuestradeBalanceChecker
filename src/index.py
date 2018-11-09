import pandas as pd
import numpy as np
from QuestradeDatasource import QuestradeDatasource
from QuestradeDatasource import QuestradeDatasourceManager
import QuestradeConfig as cfg
import asyncio
import boto3
import requests
import time
import datetime
from FuncUtils import *
from functools import partial


class BalanceActor:
    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._values = []
        self.df = pd.DataFrame()

    def Start(self):
        self._loop.run_until_complete(self._run())

    async def _run(self):
        target_allocation = pd.DataFrame(
            cfg.target_allocation,
            columns=['category', 'targetAllocation'])

        def Handler(x):
            self.df = pd.concat([self.df, x])

        target_allocation = pd.DataFrame(
            cfg.target_allocation,
            columns=['category', 'targetAllocation'])

        with QuestradeDatasourceManager() as ds:
            print("Time now: ", datetime.datetime.now())
            await AsyncRunAll(self._loop, [MakeFunc(aDs.GetPositions, Handler) for aDs in ds])
            print("Time now: ", datetime.datetime.now())
            df = self.df
            t1 = df.groupby(['time', 'category']).agg({'currentMarketValue': np.sum}).reset_index()
            temp = t1
            temp['actual'] = temp['currentMarketValue']
            temp_sum = temp['actual'].sum()
            temp['actual'] = (temp['actual'] / temp_sum)
            temp = pd.merge(target_allocation, temp, on='category')
            temp['_diff'] = (temp['targetAllocation'] - temp['actual'])
            temp['rebalanceAmount'] = temp['_diff'] * temp_sum
            threshold = cfg.threshold
            temp.loc[abs(temp._diff) > threshold, 'needRebalance'] = 1
            temp.loc[abs(temp._diff) <= threshold, 'needRebalance'] = 0
            needRebalance = False
            if temp['needRebalance'].sum() > 0:
                needRebalance = True
                print("Need rebalance")
            else:
                print("Don't need rebalance")
            self.results = temp
            self.needRebalance = needRebalance


def lambda_handler(event, context):
    sns = boto3.client("sns")
    region = context.invoked_function_arn.split(":")[3]
    account_id = context.invoked_function_arn.split(":")[4]
    topicArn = f"arn:aws:sns:{region}:{account_id}:Questrade"
    try:
        a = BalanceActor()
        a.Start()
        print(a.results.to_csv())
        sns.publish(
            TargetArn=topicArn,
            Message=a.results[['category', 'currentMarketValue', 'rebalanceAmount', 'needRebalance']].to_csv(header=True, sep='\t', float_format='%.0f'))
        return (a.needRebalance, a.results.to_csv())
    except Exception:
        print("An error has occurred")

    sns.publish(TargetArn=topicArn, Message="Failed to get quotes.")
    return False


if __name__ == '__main__':
    print("Running as command line...")
    needRebalance, csv = lambda_handler(None, None)
    print(csv)
