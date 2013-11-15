#!/usr/bin/env python

from distutils.core import setup

ld = """an IDstring is a string-like object which can be incremented, to produce
a series of serial-number-like strings, consisting of latin digits and upper case letters,
skipping those which can be easily misinterpreted ("oh", "I", "Q", and Zed) and which has
a Luhn-N check digit, capable of detecting any single-letter error and most other errors.

Programmers may define alternate alphabets, alternate lists of "dirty" words (which are skipped),
a fixed subfield for generating serial number from multiple sources, and a hash code to create unique check
digits algorithms for multiple projects.

The class will also perform generic binary to alpha conversions in your alphabet (base-32 for the default).
"""

def setup_package():
    setup(
        name='idstring',
        version='1.0.1',
        author = "Vernon Cole",
        author_email = "vernondcole@gmail.com",
        description = "a class for compact alpha-numeric serial numbers with a check digit",
        long_description = ld,
        license = "GPL",
        keywords = "serial number string checksum",
        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries :: Python Modules'],
        url = 'https://github/idstring',
        py_modules=["idstring"]
        )
    
if __name__ == '__main__':
    setup_package()
