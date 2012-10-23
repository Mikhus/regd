#!/usr/bin/env python
"""
regd's setup.py for integration with PyPI package index

@author: Mykhailo Stadnyk <mikhus@gmail.com>
@version: 1.3.1b
"""
from distutils.core import setup
import os

def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        _dir = os.path.join(path, item)
        if is_package( _dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = _dir
            packages.update(find_packages(_dir, module_name))
    return packages

setup(
    name         = "regd",
    packages     = find_packages("."),
    version      = "1.3.1b",
    description  = "Decorators trace meta-info for Python",
    author       = "Mykhailo Stadnyk",
    author_email = "mikhus@gmail.com",
    url          = "https://github.com/Mikhus/regd",
    download_url = "https://github.com/Mikhus/regd/zipball/master",
    keywords     = ["decorator", "trace"],
    platforms    = ['OS Independent'],
    license      = 'MIT License',
    classifiers  = [
		'Development Status :: 4 - Beta',
		'Environment :: Other Environment',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
    long_description = """\
Decorators trace meta-info for Python
-------------------------------------

Adds possibility to register decorators and
trace their usage

This version requires Python 2 or later; Python 3+ is included as well
"""
)
