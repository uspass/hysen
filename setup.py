#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='hysen',
    version='0.4.10',
    author='us',
    description='Python API for controlling Hysen thermostats',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/uspass/hysen',
    packages=find_packages(),
    scripts=[],
    install_requires=['broadlink==0.17.0'],

    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
    ],
)
