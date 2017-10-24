import QuestradeConfig as cfg
import pickle

class Token:
    @staticmethod
    def Load():
        print("Loading tokens")
        with open(cfg.token_file, 'rb') as f:
            return pickle.load(f)
    @staticmethod
    def Save(tokens):
        print("Saving tokens")
        with open(cfg.token_file, 'wb') as f:
            pickle.dump(tokens, f)