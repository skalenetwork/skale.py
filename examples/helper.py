import os

ENDPOINT = os.environ['ENDPOINT']
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
ABI_FILEPATH = os.path.join(DIR_PATH, os.pardir, 'abi.json')
