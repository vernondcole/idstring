#!/usr/bin/env python3

ld = """an IDstring is a string-like object which can be incremented, to produce
a series of serial-number-like strings, consisting of Arabic digits and upper case letters,
skipping those which can be easily misinterpreted ("oh", "I", "Q", and Zed) and which has
an optional Luhn-N check digit, capable of detecting any single-letter error and most other errors.

Programmers may define alternate alphabets, alternate lists of "dirty" words (which are skipped),
a fixed subfield for generating serial number from multiple sources, and a hash code to create unique check
digits algorithms for multiple projects. Passing a hash code of None will surpress check digit operation.

The class will also perform generic binary to alpha conversions in your alphabet (base-32 for the default).
"""

VERSION = None  # in case searching for version fails
a = open("idstring.py")  # find the version string in the source code
for line in a:
    if "__version__" in line:
        VERSION = line.split('"')[1]
        print('idstring version="%s"' % VERSION)
        break
a.close()


def setup_package():
    from setuptools import setup
    from setuptools.command.build_py import build_py

    setup(
        cmdclass={"build_py": build_py},
        name = 'idstring',
        version = VERSION,
        author = "Vernon Cole",
        author_email = "vernondcole@gmail.com",
        description = "a class for compact alpha-numeric serial numbers with (an optional) check digit",
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
        url = 'https://github.com/vernondcole/idstring',
        py_modules=["idstring"]
        )
    
if __name__ == '__main__':
    setup_package()
