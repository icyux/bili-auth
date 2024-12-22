import logging
import toml

# read config
config = toml.load('config.toml')

# set up logger
logging.basicConfig(
	format=config['log']['format'],
	level=logging.INFO,
)
