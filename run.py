#!/usr/bin/env -S python3 -u

import subprocess

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
	proc = subprocess.Popen(f'gunicorn -w 1 -b {host}:{port} --access-logformat "[web] %(s)s %(m)s %(U)s" main:app', shell=True)
	proc.wait()

elif containerType == 'flask-default':
	print('Starting flask server')
	proc = subprocess.Popen(f'python main.py')
	proc.wait()

else:
	print(f'Unknown container type: {containerType}')
	exit(1)
