#!/usr/bin/python -tt

import os
from distutils.core import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

VERSION='0.1'
NAME='grokmirror'

setup(
    version=VERSION,
    url='https://www.kernel.org/pub/software/network/grokmirror',
    name=NAME,
    description='Smartly mirror git repositories that use grokmirror',
    author='Konstantin Ryabitsev',
    author_email='mricon@kernel.org',
    packages=[NAME],
    license='GPLv3+',
    long_description=read('README.rst'),
)