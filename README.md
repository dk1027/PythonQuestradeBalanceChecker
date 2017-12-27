## Generating the token file
The token file is a pickled Python list that holds the Questrade access tokens.
Use the following code to generate the inital token file. After the initial manual generation, subsequent tokens are saved automatically.
```
from QuestradeToken import Token
Token.Save(['your-questrade-token', 'more-tokens-for-multiple-accounts'])
```

## Setup
1. Install dependencies by running `pip install -r requirements-dev.txt`
2. Run `python main.py` to run the balancer checker.
3. Upload the token file to a S3 bucket
Currently it is hardcoded to look for a `tokens` file in a S3 bucket.
