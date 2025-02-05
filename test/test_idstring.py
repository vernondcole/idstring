#!/usr/bin/env python3
"""
Test code for the IDstring package
"""
__author__ = 'vernon'

import sys, os
mommy = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(1, mommy)  # use the local copy, not some system version

import idstring
from idstring.idstring import IDstring, InvalidIdError
import unittest
import random
from contextlib import contextmanager

dummy_seed = None  # Glabal variable used for ephemeral seed storage

def assertion(seen, expected, seed=None):
    assert str(seen) == expected, 'Value is "%s". expected "%s"' % (seen, expected)
    if seed:
        assert dummy_seed == seed, 'seed returned was "%s" expected "%s"' % (seen, dummy_seed)


# the seedstore function will be called back with an IDstring object as its only argument
def dummy(idstr):  # nonfunctional seedstore function
    global dummy_seed
    d = idstr.get_seed()      # the seed we need to preserve
    dummy_seed = d      # just store it in a global variable for test purposes


class Test1(unittest.TestCase):
    def test1(self):
    #test building a factory
        fact = IDstring(seed='90a', host='1234', seedstore=dummy)
    #value comes back unchanged
        assertion(fact, '90A1234A', None)
    #try the next value
        x = fact + 1
        assertion(x, '90B12348', '90B')


class Test2(unittest.TestCase):
    def test2(self):
    #test the carry
        fact = IDstring(seed='000Y', host='ppp', seedstore=dummy)
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
            self.fail('Did not see OutOfRangeError')

    def test3b(self):
        assert not IDstring.sumcheck('TSETME2K'), 'invalid checksum should not pass'


class Test4(unittest.TestCase):
        # test the dirty word eliminator

    def test4(self):    #test that we skip bad words on the right
        f = IDstring(seed='dcasr')
        assertion(f, 'DCASRV')
        x = f + 1
        assertion(x, 'DCASTR')  #skips the bad word 'ass'

    def test4b(self):
        #test that we skip bad words on the left
        f = IDstring(seed='fucjyyy', seedstore=dummy)
        x = f + 1             #skip you, too, buddy
        assertion(x, 'FUCL000U', 'FUCL000')

    def test4c(self):   # test the case where a checksum causes a bad word
        f = IDstring(seed='000vfub', seedstore=dummy)
        x = f + 1             # '000VFUC' has a checksum of 'K'
        assertion(x, '000VFUDH', '000VFUD')

    def test4d(self):   # test the case where a host field causes a bad word
        f = IDstring(seed='0ct', host='nt', seedstore=dummy)
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
            jumble = IDstring(seed=ranlets(random.randint(2, 20)))  # make a random length random string
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
    def test6(self):
        # seed in binary is deprecated
        self.assertRaises(idstring.InvalidIdError, IDstring, [], **{'seed': 0})

        f = IDstring(seed='0')
        assertion(f, '00')
        x = f + 1
        assertion(x, u'1X')
        x = f + 1   # !! do not use this terrible side effect !!!
        self.assertNotEqual(x, '2V')

        x += 1
        assertion(x, '2V')
        self.assertRaises(ValueError, int, *[x], **{})  # deprecated function int(IDstring)


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
            f = IDstring(seed='7FFF')
            assertion(f, '7FFFC')


class Test7(unittest.TestCase):
    #  Testing hash
    def test7a(self):
    #test building a factory with a variant hash
        fact = IDstring(None, '90a', '1234', dummy, hash='0')
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
            self.fail('Did not see OutOfRangeError')

    def test7d(self):
        assert not IDstring.sumcheck('TESTME29'), 'invalid checksum should not pass (default hash)'

    def test7e(self):
        assert not IDstring.sumcheck('TESTME29', hash='XX'), 'invalid checksum should not pass (different hash)'


class Test8(unittest.TestCase):
    #  Testing with no checksum (hash=None)
    def test8a(self):
    #test building a factory with a null hash
        fact = IDstring(None, '5GA', '1234', dummy, None)
    #value comes back unchanged
        assertion(fact, '5GA1234', None)
        IDstring.sumcheck(fact, hash=None)
    #try the next value
        x = fact + 1
        assertion(x, '5GB1234', '5GB')

    def test8b(self):
        x = IDstring('ADD', seedstore=dummy, hash=None, alphabet='abcd', case_shift=str.lower)
        x += 1
        assertion(x, 'baa', 'baa')

        x = IDstring(seed='DDDD', seedstore=dummy, hash=None, alphabet='ABCD')
        x += 1
        assertion(x, 'AAAAA')

        self.assertFalse(IDstring.sumcheck('ABAD1', hash=None, alphabet='ABCD'))

class Test9(unittest.TestCase):
    # testing that case_shift=None will not shift case
    def test9(self):
        x = IDstring(seed='AbC', seedstore=dummy, hash=None, alphabet='ABCabc', case_shift=None)
        assertion(x, 'AbC')
        x += 1
        assertion(x, 'Aba')


class Test10(unittest.TestCase):
    # Test the dirty word filter in more depth
    @contextmanager
    def weird_words(self, weird):
        keep = IDstring.DIRTY_WORDS
        IDstring.DIRTY_WORDS = weird
        try:
            yield None
        finally:
            IDstring.DIRTY_WORDS = keep

    def test10(self):
        # try changing the dirty word list
        more_words = idstring.DEFAULT_DIRTY_WORDS + idstring.DIRTY_I_WORDS
        with self.weird_words(more_words):
            f = IDstring(seed='tBtist', alphabet='aBcit', case_shift=None, hash=None)  # a short mixed case alphabet
            f += 1  # carry should spell a three letter objectionabe word
            assertion(f, 'tBtiaa')  # The second "t" should be incremented to "a"


    def test11(self):
        # test carry out of range with alternate alphabet
        f = IDstring(seed='zzz', alphabet='abcz', case_shift=None)
        f += 1
        assertion(f, 'aaaaa')


if __name__ == "__main__":
    unittest.main()
