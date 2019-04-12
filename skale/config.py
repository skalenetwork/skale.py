import os

ENVS_DIRNAME = 'envs'
ENV_FILE_EXTENSION = '.json'
SKALE_ENVS_FILENAME = 'envs.yml'

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR = os.path.join(CURRENT_DIR, os.pardir)

ENVS_DIR = os.path.join(CURRENT_DIR, ENVS_DIRNAME)
SKALE_ENVS_FILEPATH = os.path.join(ENVS_DIR, SKALE_ENVS_FILENAME)
