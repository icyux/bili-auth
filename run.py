#!/usr/bin/env -S python3 -u

import os

import misc
import misc.selftest


config = misc.config
containerType = config['service']['container']

# self-test
if config['debug']['seleniumTest']:
	print('Performing selenium self-test')
	succ = misc.selftest.seleniumSelfTest()
	if not succ:
		print('Self-test failed, quit.')
		exit(1)

if config['debug']['biliApiTest']:
	print('Performing bili api self-test')
	succ = misc.selftest.biliApiSelfTest()
	if not succ:
		print('Self-test failed, quit.')
		exit(1)

# run web server
if containerType == 'gunicorn':
	print('Starting gunicorn')
	host = config['service']['host']
	port = config['service']['port']
	os.system(f'gunicorn -w 1 -b {host}:{port} --access-logformat "[web] %(s)s %(m)s %(U)s" main:app')

elif containerType == 'flask-default':
	print('Starting flask server')
	os.system(f'python main.py')

else:
	print(f'Unknown container type: {containerType}')
	exit(1)
