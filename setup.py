#!/usr/bin/env python

from setuptools import setup

def readme():
	with open('README.md') as f:
		return f.read()

setup(name='pymodiolib',
	version='0.0.1',
	description='Python modio Library',
	author='Southclaw',
	author_email='SouthclawJK@gmail.com',
	url='',
	packages=['pymodiolib'],
	test_suite='nose.collector',
	tests_require=['nose'],
	)
