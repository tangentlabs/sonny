#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='tangent_importer',
    version='0.1',
    description='Importing framework',
    url='http://github.com/tangentlabs/tangent-importer',
    author='Costas Basdekis',
    author_email='costas@basdekis.io',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "PyYAML==3.11",
        "MySQL-python==1.2.5",
        "xlrd==0.9.4",
        "Jinja2==2.8",
        "termcolor==1.1.0",
        "requests==2.7.0",
    ],
)
