# coding=utf-8
# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ctxt',
    version='0.0.1',
    description='Collaborative Text Editor',
    long_description=long_description,
    url='https://github.com/UTDS16/collab-texter',
    author='Indrek Sünter, Martin Valgur',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # install_requires=['pyqt'],
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'ctxt_server=ctxt.server.server:main',
            'ctxt_client=ctxt.client.client:main',
        ],
    },
)