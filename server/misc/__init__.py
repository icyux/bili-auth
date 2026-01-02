import logging
import toml

from misc.get_version import get_version


version = get_version()
if version is not None:
	print(f'bili-auth {version}', flush=True)

# read config
config = toml.load('config.toml')

# set up logger
logging.basicConfig(
	format=config['log']['format'],
	level=logging.INFO,
)
