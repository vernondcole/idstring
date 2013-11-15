"""
Test code for the IDstring package
"""
from __future__ import unicode_literals

__author__ = 'vernon'

from  idstring import *
import unittest
import random
from contextlib import contextmanager

def assertion(seen, expected, seed=None):
    assert seen == expected, 'Value is "%s". expected "%s"' % (seen, expected)
    if seed:
        testseed(seed)

dummyseed = None

# the seedstore function will be called back with an IDstring object as its only argument
def dummy(idstr):  # nonfunctional seedstore function
    global dummyseed
    dummyseed = idstr.get_seed()      # the seed we need to preserve

def testseed(s):
    assert dummyseed == s, 'seed returned was "%s" expected "%s"' % (dummyseed, s)


class Test1(unittest.TestCase):
    def test1(self):
    #test building a factory
        fact = IDstring(None, '90a', '1234', dummy)
    #value comes back unchanged
        assertion(fact, '90A1234A', None)
    #try the next value
        x = fact + 1
        assertion(x, '90B12348', '90B')


class Test2(unittest.TestCase):
    def test2(self):
    #test the carry
        fact = IDstring(None, '000Y', 'ppp', dummy)
        x = fact + 1
        assertion(x, '0010PPP9', '0010')
    def test2a(self):
        #test carry out of top digit
        fact = IDstring(seed='YYYY')
        x = fact + 1
        assertion(x, '10000X')


class Test3(unittest.TestCase):
    def test3(self):
        # test the checksum interface
        assert IDstring.sumcheck('TESTME2K'), 'valid checksum shown as invalid'
        try:
            assert IDstring('TESTME3K'), 'invalid checksum should not pass'
        except InvalidIdError:
            pass
        else:
            self.Fail('Did not see OutOfRangeError')

    def test3b(self):
        assert not IDstring.sumcheck('TSETME2K'), 'invalid checksum should not pass'


class Test4(unittest.TestCase):
        # test the dirty word eliminator

    def test4(self):    #test that we skip bad words on the right
        f = IDstring(seed='dcballr')
        assertion(f, 'DCBALLRC')
        x = f + 1
        assertion(x, 'DCBALLT8')  #skips the bad word 'balls'

    def test4b(self):
        #test that we skip bad words on the left
        f = IDstring(seed='fucjyyy', seedstore=dummy)
        x = f + 1             #skip you, too, buddy
        assertion(x, 'FUCL000U', 'FUCL000')

    def test4c(self):   # test the case where a checksum causes a bad word
        f = IDstring(None, '000vfub', seedstore=dummy)
        x = f + 1             # '000VFUC' has a checksum of 'K'
        assertion(x, '000VFUDH', '000VFUD')

    def test4d(self):   # test the case where a host field causes a bad word
        f = IDstring(None, '0ct', 'nt', dummy)
        x = f + 1             #
        assertion(x,'0CVNTG', '0CV')


class Test5(unittest.TestCase):
    # test the checksum algorithm as a whole
    def test5(self):
        alphabet = IDstring.ALPHABET
        def ranlets(size,allowed=alphabet):    # a function to generate a random string of our alphabet
            randomstring = ''.join([allowed[random.randint(0, len(allowed) - 1)] for x in range(size)])
            return randomstring

        # run the test using many different random strings
        for N in range(1000):
            jumble = IDstring(seed=ranlets(random.randint(2,20))) # make a random length random string
            for i,should_be in enumerate(jumble):                   # for each character in that string
                others = list(alphabet)                             # replace it with every other possible character
                others.remove(should_be)
                for c in others:   #try every possible other value for this character
                    mumble = ''.join([jumble[:i], c, jumble[i+1:]])
                    assert not IDstring.sumcheck(mumble), 'IDstring "%s" should fail checksum'
            # now test digit flips
            # -- swap a character with its next door neighbor
            # (this is the most common transcription error when humans are involved)
            # Note: this algorithm will not detect flips of the first and last characters of its alphabet
            #   (called a 0-9 flip when only decimal digits are used)
            #
            for i in range(len(jumble)-1):
                j = i+1     # skip test of letters are the same -- or if letters are first and last
                if jumble[i] != jumble[j] and {jumble[i],jumble[j]} != {alphabet[0],alphabet[-1]}:
                    s = list(jumble)
                    s[j], s[i] = s[i], s[j]        # swap two characters
                    mumble = ''.join(s)
                    assert not IDstring.sumcheck(mumble), 'checksum error in "%s" when changed to "%s"'%(jumble,mumble)


class Test6(unittest.TestCase):
# test weird extra functions

    def test6(self):    # feed it in binary
        f = IDstring(seed=0)
        assertion(f, '00')
        x = f + 1
        assertion(x, u'1X')
        x = f + 1   # !! do not use this terrible side effect !!!
        assertion(x, u'2V')
        f = IDstring(None, 17, "2")
        assertion(f, u'H2B')
        x = f + 1
        assertion(int(x), 18*32+2)  # int() should return the value of the whole non-checksumed thing, not just the seed

    def test6a(self):
        # put a checksum on a 32bit number
        f = IDstring(seed=32767)
        assertion(f, 'YYY3')

    @contextmanager
    def weird_alphabet(self, weird):
        keep = IDstring.ALPHABET
        IDstring.ALPHABET = weird
        try:
            yield None
        finally:
            IDstring.ALPHABET = keep

    def test6b(self):
        # change the class alphabet to hexadecimal
        with self.weird_alphabet('0123456789ABCDEF'):
            # put a checksum on a hexadecimal number
            f = IDstring(seed=32767)
            assertion(f, '7FFFC')

            for i in range(79):
                j = random.randint(0,i)

                # test binary to string
                js = IDstring.thirty2(j)
                assertion('0x'+js.lower(), hex(j))

                # test string to binary
                ks = hex(j)[2:].upper()   # strip off the '0x'
                k = IDstring.thirty2int(ks)
                assertion(k,j)


class Test7(unittest.TestCase):
    #  Testing hash
    def test7a(self):
    #test building a factory with a variant hash
        fact = IDstring(None, '90a', '1234', dummy, '0')
    #value comes back unchanged
        assertion(fact, '90A1234Y', None)
        IDstring.sumcheck(fact, hash='0')
    #try the next value
        x = fact + 1
        assertion(x, '90B1234X', '90B')

    def test7b(self):
    #test the carry
        fact = IDstring(None, '000Y', 'ppp', dummy, '0')
        x = fact + 1
        assertion(x, '0010PPP2', '0010')

    def test7c(self):
        # test the checksum interface
        assert IDstring.sumcheck('TESTME29', hash='0'), 'valid checksum shown as invalid'
        try:
            assert IDstring('TESTME39', hash='0'), 'invalid checksum should not pass'
        except InvalidIdError:
            pass
        else:
            self.Fail('Did not see OutOfRangeError')

    def test7d(self):
        assert not IDstring.sumcheck('TESTME29'), 'invalid checksum should not pass (default hash)'

    def test7e(self):
        assert not IDstring.sumcheck('TESTME29', hash='XX'), 'invalid checksum should not pass (different hash)'


if __name__ == "__main__":
    unittest.main()
