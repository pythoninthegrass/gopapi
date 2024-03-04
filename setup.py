#!/usr/bin/env python

from __future__ import absolute_import
from os.path import join, dirname
from setuptools import setup
import gopapi

basepath = dirname(__file__)
binpath = join(basepath, 'bin')

setup(
    name="gopapi",
    packages=["gopapi"],
    version=gopapi.__version__,
    description="Simple way to access GoDaddy API",
    long_description=open(join(basepath, "README.txt")).read(),
    scripts=[join(binpath, "gopapi")],
    install_requires=["pycrypto", "requests"],
    author="Lance Stephens",
    author_email="4097471+pythoninthegrass@users.noreply.github.com",
    url="https://github.com/pythoninthegrass/gopapi",
    keywords=["image", "icons", ""],
    classifiers=[],
)
