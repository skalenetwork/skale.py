#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

extras_require = {
    'linter': [
        "flake8==3.4.1",
        "isort>=4.2.15,<4.3.5",
    ],
    'dev': [
        "bumpversion==0.5.3",
        "pytest==3.8.1",
        "twine==1.12.1",
        "when-changed",
    ]
}

extras_require['dev'] = (
    extras_require['linter'] +
    extras_require['dev']
)

setup(
    name='skale.py',
    # *IMPORTANT*: Don't manually change the version here. Use the 'bumpversion' utility.
    version='0.70.0',
    description='SKALE client tools',
    long_description_markdown_filename='README.md',
    author='SKALE Labs',
    author_email='support@skalelabs.com',
    url='https://github.com/skalenetwork/skale.py',
    include_package_data=True,
    install_requires=[
        "web3==4.8.2",
        "asyncio==3.4.3",
    ],

    python_requires='>3.6,<4',
    extras_require=extras_require,



    keywords='skale',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],

    package_data={  # Optional
        'contracts': ['utils/contracts_data.json', 'envs/envs.yml', 'envs/aws.json'],
    },
)
