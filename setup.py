#!/usr/bin/env python
from distutils.core import setup
setup(
    name = 'flog',
    version = '0.1',
    author = 'gjost',
    author_email = 'geoffrey@jostwebwerks.com',
    url = 'http://jostwebwerks.com/flog/',
    packages = ['flog'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Other/Nonlisted Topic',
        ],
    keywords = 'networking eventlet nonblocking internet',
    description = 'flog - A food log',
    long_description = """\
flog -- A food log
------------------

Flog is a Django app for recording food consumption, weight, etc.
"""
)
