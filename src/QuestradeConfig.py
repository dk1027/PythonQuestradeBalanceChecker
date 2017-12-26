# the ideal assets allocation
target_allocation = [
    ['BONDS', 0.14],
    ['CASH', 0.02],
    ['CANADA', 0.28],
    ['USA', 0.28],
    ['WORLD', 0.28]]

# pickle file containing refresh tokens
<<<<<<< HEAD
bucket_name = 'dk1027'
=======
bucket_name = 'questrade-balance-checker-bucket'  # This must match the S3 bucket resource created in QuestradeCFTemplate
>>>>>>> Moved source files to src directory
token_file = 'tokens'

symbol_category_mapping = {
    'symbol': {
        'ABHD': None,  # the asset is ignored if mapped to None
        'VFV.TO': 'USA',
        'ZCN.TO': 'CANADA',
        'AVO.TO': 'CANADA',
        'SU.TO': 'CANADA',
<<<<<<< HEAD
=======
        'UR.TO': 'CANADA',
>>>>>>> Moved source files to src directory
        'VIU.TO': 'WORLD',
        'Y004597.16': None,
        'XCH.TO': None,
        'ZDB.TO': 'BONDS',
        'VSB.TO': 'BONDS',
        'ZAG.TO': 'BONDS'
    }
}

# if the actual balance goes beyond the threshold then a rebalance is necessary
threshold = 0.005
