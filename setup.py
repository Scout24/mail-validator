#!/usr/bin/env python

from setuptools import setup

setup(
    name="mail-validator",
    version="2.0.1",
    author="Tobias Vollmer",
    author_email="tobias.vollmer@immobilienscout24.de",
    description="Python script to test security functionality in a (remote) smtp server.",
    license="GPL",
    keywords="mail testing",
    py_modules=['mail_validator', 'dkim'],
    long_description="Python script to security functionality in a (remote) smtp server. Supports DKIM and TLS.",
    test_suite = 'unit_tests',
    install_requires = ['dkimpy>=0.5.4'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Topic :: System :: Testing",
    ],
    entry_points={
        'console_scripts': [
            'mail-validator = mail_validator:main',
        ],
    },
)
