from setuptools import find_packages
from setuptools import setup

import srvbeat

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
			'srvbeat-testclient=srvbeat.client:testClient',
			'srvbeat-client=srvbeat.client:standaloneClient',
		],
	},
    zip_safe=False,
	install_requires=['packaging'],
)