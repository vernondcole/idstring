class IDstring generates (and checks) alphanumeric serial number strings with a checksum

Installation uses the usual Python method:

>cd your-unzipped-directory
>python setup.py install

It extends the built in Unicode (str on Python 3) class using an __ADD__ method which accepts the integer ONE.
Adding 1 to an instance of the class will generate a new instance with an incremented value (and a new checksum).

It also performs binary to base-32 conversions. The default alphabet excludes "oh" "eye" "queue" and "zed".
You can overwrite the default alphabet, in which case the base-n conversions and checksum calculations use yours.
(..............not shown below: there is a callback function to persist the state of the counter...............)

For the simplest explanation of what it does, see the following examples:

>python
>>> import idstring
>>> s = idstring.IDstring(seed="678X", host='1F')
>>> limit = int(s) + 4 * 32 * 32 # four, with two trailing base-32 digits (for the "host" field)
>>> while int(s) < limit):  # you would not normally do this, but it proves that can be used this way...
...   print(s)
...   s += 1
678X1F8
678Y1F6
67901F4
67911F2
>>> len(s)  # s acts like a string (almost)
7
>>> s + 'hello'
'67911F2hello'
>>> s[-3:-1]
u'1F'
>>> s.host  # but it has attributes, too
u'1F'
>>> s.get_seed()
u'6791'
>>> idstring.IDstring.sumcheck(s)  # we can see whether a number is "good"
True
>>> idstring.IDstring.sumcheck('XYZ')
False
>>> x = idstring.IDstring('XYZ')   # has an incorrect checksum
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "idstring.py", line 127, in __new__
    raise InvalidIdError('"%s" is not a valid idString' % S)
idstring.InvalidIdError: "XYZ" is not a valid idString
>>>
>>> x = idstring.IDstring('xy3')  # has a good checksum
>>> x
idString('XY3')
>>>
>>> s = idstring.IDstring(seed='FARS')  # set it up to spell a "naughty word"
>>> s
idString('FARSJ')
>>> s += 1        # it will skip anything in idstring.IDstring.DIRTY_WORDS
>>> s
idString('FARUE')
>>>
>>> # binary to base-32 conversion    # NOTE: the actual base is defined by len(idstring.IDstring.ALPHABET)
>>>                                   # which you can change, in which case my method names are poorly chosen
>>> idstring.IDstring.thirty2(0x1F)   # and you should probably create a better identifier for the methods
u'Y'
>>> idstring.IDstring.thirty2(0x2F)
u'1F'
>>> hex(idstring.IDstring.thirty2int('100'))
'0x400'
>>>
>>> # you can use a different alphabet by overwriting the class attribute
>>>
>>> summed32 = idstring.IDstring(seed=0xbadfeed)
>>> summed32
idString('5TUYPDU')
>>>
>>> idstring.IDstring.ALPHABET = '0123456789ABCDEF'  # switch to base 16 w/ usual hexadecimal symbols
>>> summedHex = idstring.IDstring(seed=0xbadfeed)
>>> summedHex
idString('BADFEEDF')
>>>
