from setuptools import find_packages
from setuptools import setup

import srvcheck

setup(name='srvbeat',
	version=srvbeat.__version__,
	description='',
	author='Davide Gessa',
	setup_requires='setuptools',
	author_email='gessadavide@gmail.com',
	packages=[
		'srvbeat'
	],
	entry_points={
		'console_scripts': [
			'srvbeat=srvbeat.main:main',
		],
	},
    zip_safe=False,
	install_requires=['packaging'],
)