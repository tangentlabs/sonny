#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='sonny',
    version='0.2',
    description='Importing framework',
    url='http://github.com/tangentlabs/sonny',
    author='Costas Basdekis',
    author_email='costas@basdekis.io',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyYAML==3.11",
        "xlrd==0.9.4",
        "Jinja2==2.8",
        "termcolor==1.1.0",
        "requests==2.7.0",
    ],
)
