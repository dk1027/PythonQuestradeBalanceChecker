from abc import ABCMeta, abstractmethod
import QuestradeConfig as cfg
import pickle
import boto3
import botocore


class Token:
    @abstractmethod
    def Load(self):
        pass

    @abstractmethod
    def Save(self, tokens):
        pass

    @staticmethod
    def MakeToken():
        try:
            print("Using AWS as token storage")
            cfg.bucket_name
            token = AwsToken()
        except AttributeError:
            print("Using local filesystem as token storage")
            token = LocalToken()
        return token


class LocalToken(Token):
    def Load(self):
        print("Loading tokens")
        with open(cfg.token_file, 'rb') as f:
            return pickle.load(f)

    def Save(self, tokens):
        print("Saving tokens")
        with open(cfg.token_file, 'wb') as f:
            pickle.dump(tokens, f)


class AwsToken(Token):
    def __init__(self):
        self.s3 = boto3.resource('s3')

    def Load(self):
        print(f"Loading {cfg.token_file} from {cfg.bucket_name}")
        obj = self.s3.Object(cfg.bucket_name, cfg.token_file)
        return pickle.loads(obj.get()['Body'].read())

    def Save(self, tokens):
        print("Saving token")
        data = pickle.dumps(tokens)
        self.s3.Bucket(cfg.bucket_name).put_object(Key=cfg.token_file, Body=data)
