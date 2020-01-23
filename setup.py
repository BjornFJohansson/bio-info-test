#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import versioneer
from setuptools import setup

# Read author etc. from __init__.py
for line in open('bio_info_test/__init__.py'):
    if line.startswith('__') and not line.startswith('__version') and not line.startswith('__long'):
        exec(line.strip())

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

     
setup(  name='bio_info_test',
        version=versioneer.get_version()[:5],
        cmdclass=versioneer.get_cmdclass(),
        author          =__author__,
        author_email    =__email__,
        packages=['bio_info_test'],     
        entry_points = { 'console_scripts' : [ 'informatics_exam = bio_info_test.informatics_test:main']    },
        url='https://github.com/BjornFJohansson',
        license='LICENSE.txt',
        description='bioinformatics test',
        long_description=long_description,
        long_description_content_type='text/markdown',
        
        install_requires = [ "pydna", "docopt", "pyparsing", "ezodf"],

        zip_safe = False,
        keywords = u"bioinformatics",
        classifiers = ['Development Status :: 4 - Beta',
                       'Environment :: Console',
                       'Intended Audience :: Education',
                       'Intended Audience :: Science/Research',
                       'License :: OSI Approved :: BSD License',
                       'Programming Language :: Python :: 3.6',
                       'Programming Language :: Python :: 3.7',
                       'Topic :: Education',
                       'Topic :: Scientific/Engineering :: Bio-Informatics',])