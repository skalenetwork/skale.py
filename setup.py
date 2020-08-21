#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

extras_require = {
    'linter': [
        "flake8==3.8.3",
        "isort>=4.2.15,<4.3.22",
    ],
    'dev': [
        "bumpversion==0.6.0",
        "pytest==5.4.3",
        "click==7.1.2",
        "twine==3.1.1",
        "mock==4.0.2",
        "when-changed",
        "Random-Word==1.0.4",
        "pytest-cov==2.8.1"
    ],
    'hw-wallet': [
        "ledgerblue==0.1.31"
    ]
}

extras_require['dev'] = (
    extras_require['linter'] + extras_require['dev'] + extras_require['hw-wallet']
)

setup(
    name='skale.py',
    version='4.0',
    description='SKALE client tools',
    long_description_markdown_filename='README.md',
    author='SKALE Labs',
    author_email='support@skalelabs.com',
    url='https://github.com/skalenetwork/skale.py',
    include_package_data=True,
    install_requires=[
        "web3==5.6.0",
        "asyncio==3.4.3",
        "pyyaml==5.3.1",
        "sgx.py==0.6dev8"
    ],

    python_requires='>=3.6,<4',
    extras_require=extras_require,

    keywords='skale',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],

    package_data={  # Optional
        'contracts': ['utils/contracts_data.json', 'envs/envs.yml', 'envs/aws.json'],
    },
)
