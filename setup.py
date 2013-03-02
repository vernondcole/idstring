#!/usr/bin/env python

from distutils.core import setup

ld = """an IDstring is a string-like object which can be incremented, to produce
a series of serial-number-like strings, consisting of latin digits and upper case letters,
skipping those which can be easily misinterpreted ("oh", "I", "Q", and Zed) and which has
a Luhn-N check digit, capable of detecting any single-letter error and most other errors.


"""

def setup_package():
    setup(
        cmdclass = {'build_py': build_py},
        name='idstring',
        version='0.2.2',
        author = "Vernon Cole",
        author_email = "vernondcole@gmail.com",
        description = "a class for compact alpha-numeric serial numbers with a check digit",
        long_description = ld,
        license = "GPL",
        keywords = "serial number string checksum",
        classifiers = [
            # 'Development Status :: 5 - Production/Stable',
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
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
