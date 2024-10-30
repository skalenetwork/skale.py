#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

extras_require = {
    'linter': [
        "flake8==3.8.3",
        "isort>=4.2.15,<5.4.3",
        "importlib-metadata<5.0"
    ],
    'dev': [
        "bumpversion==0.6.0",
        "click==7.1.2",
        "freezegun==1.2.2",
        "mock==4.0.2",
        "pytest==7.1.3",
        "pytest-cov==2.8.1",
        "Random-Word==1.0.4",
        "twine==4.0.2",
        "when-changed"
    ],
    'hw-wallet': [
        "ledgerblue==0.1.47"
    ]
}

extras_require['dev'] = (
    extras_require['linter'] + extras_require['dev'] + extras_require['hw-wallet']
)

setup(
    name='skale.py',
    version='6.4',
    description='SKALE client tools',
    long_description_markdown_filename='README.md',
    author='SKALE Labs',
    author_email='support@skalelabs.com',
    url='https://github.com/skalenetwork/skale.py',
    include_package_data=True,
    install_requires=[
        "asyncio==3.4.3",
        "pyyaml==6.0",
        "sgx.py==0.9dev4",
        "redis==5.0.3",
        "typing-extensions==4.9.0",
        "web3==6.20.2"
    ],

    python_requires='>=3.7,<4',
    extras_require=extras_require,

    keywords='skale',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
    ]
)
