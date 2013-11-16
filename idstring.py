""" A class defining a string of non-look-alike digits with a check digit, which can be incremented.

The intent is to create compact serial numbers using a base 32 number system.
* a "host" field can be defined, so that if the serial numbers are issued by a known set of
 loosely cooperative units (think of couchdb hosts) the numbers will not conflict.

The default alphabet can be replaced by any unicode string you wish. The check digit will be from your alphabet.

The string is initialized using a five-argument call like; idstring.IDstring(IDstr, seed, host, seedstore, hash)
:IDstr an already-defined idstring.IDstring with checksum. [or None, if you are supplying a "seed"]
:seed - a "seed" value of valid idstring.ALPHABET characters with no checksum [ignored if IDstr is supplied]
:host - the identity number of the" host" on which it is running. !!! defines the size of the .host field !!!
:seedstore - a call-back function which the caller promises to use to preserve the state of the seed value.
- - - that function will be called with an idstring object so the caller can extract the incremented seed for storage.
- - - REMINDER...use the .value attribute or get_seed() method. The value of the IDstring cannot be incremented!
:hash - additional character(s) to alter the check digit, so that IDstrings for different purposes do not match.
 Copyright 2013, eHealth Africa   http://www.ehealthafrica.org

 """
#  This code is released and licensed under the terms of the Lesser GPL license as specified at the
#  following URL:
#   http://www.gnu.org/copyleft/lgpl.html
#
from __future__ import unicode_literals
import sys
import collections

__author__ = "Vernon Cole <vernondcole@gmail.com>"
__version__ = "1.0.3"

# -- a short calling sample -- real code would use a better storage method ---------
#- import pickle, idstring
#-
#- def my_seedstore(iDstr):   # function to preserve the idString seed
#-    global my_seed_memory
#-    pkl_file = open('mySeedStore,pkl,'wb')
#-    my_seed_memory['seed'] = iDstr.get_seed()
#-    pickle.dump(my_seed_memory,pkl_file,-1)
#-    pkl_file.close()
#-
#- # set up the idString for this run by retrieving it from storage
#- try:  # retrieve the idString seed
#-    pkl_file = open('mySeedStore.pkl','rb')
#-    my_seed_memory = pickle.load(pkl_file)
#-    pkl_file.close()
#- except:
#-    # # the next statement would have been used to initialize the system & set the "host" number
#-    my_seed_memory = {'host':'101','seed':'0000'} # initial value -- to be updated by pickle on later runs
#-    raise Warning('Caution: IDstring storage not found -- your system may be broken')
#-
#- # initialize the idString factory with the saved values
#- present_id = idstring.idString(seed=my_seed_memory['seed'], host=my_seed_memory['host'], my_seedstore)
#-
#- while I_am_still_working:
#-    some_patient_data = some_kind_of_input()
#-    present_id += 1    # generate a new patient number
#-    print('Storing data for %s now...' % repr(present_id))
#-    store_info(str(present_id), some_patient_data)
#-
#-----------------------------------------------------------------------
if sys.version_info[0] > 2:
    basestring = str  # Python3
    text = str
else:  # Python2
    text = unicode


#Define exceptions
class IdStringError(ValueError):
    """Base class for all errors in the IdString package"""
    pass
class OutOfRangeError(IdStringError): pass
class InvalidIdError(IdStringError): pass

class IDstring(text):
    #the following are class attributes for IDstrings.  They may be redefined if a programmer
    #whishes to change what in "idString" looks like.
    # For our actual application, We have chosen a three character hostNumber field and
    # a four character idNumber field,
    # composed of a 32 character ALPHABET [0-9,A-H,J-N,P,R-Y]. i o q and z are out so no "1Il" "OQ0" "2Z" errors
    # with a luhn_N check digit

    #define the characters which may legally appear in an idString
    ALPHABET = "0123456789ABCDEFGHJKLMNPRSTUVWXY"

    # create a list of George Carlan's "the seven words you can't say on T.V."
    # plus a few extras, but ignoring any with an "I" in them, since the default ALPHABET has no "I"
    DIRTY_WORDS = [c[::-1] for c in ['KCUF', 'TNUC', 'TRAF', 'DRUT', 'TAWT', 'SLLAB']]
    # the words are stored backwards in the source, because 'kcuf' is not objectionable.

    @classmethod
    def thirty2(cls, x):
        """idstring.thirty2(n: int) --> Thirty-two bit string  # like hex(n) but 5 bits encoded, not four"""
        q, r = divmod(int(x), len(cls.ALPHABET))
        digits = [cls.ALPHABET[r]]
        while q:
            q, r = divmod(q, len(cls.ALPHABET))
            digits.append(cls.ALPHABET[r])
        return ''.join(digits[::-1])

    @classmethod
    def thirty2int(cls, s):
        """idstring.thirty2bin('THRTY2BT') --> int  # decodes thirty-two bit string (with no checksum)"""
        acc = 0
        for digit in s.upper():
            try:
                acc = acc * len(cls.ALPHABET) + cls.ALPHABET.find(digit)
            except ValueError:
                raise InvalidIdError('Invalid digit "{}" for conversion'.format(digit))
        return acc

    @classmethod
    def _check_host(cls, host):
        d = text(host).strip().upper()
        for c in d:
            if not c in cls.ALPHABET:
                raise InvalidIdError('Incorrect character "%s" in "%s"' % (c, d))
        return d

    def __new__(cls, S=None, seed=None, host='', seedstore=None, hash=''):
        """
        :S - an existing legal idString, or None
        :seed - the seed string for a new factory [ignored unless S is None]
        :host - the host portion for a new idString factory, len(host) will set host length for factory
        :seedstore - a seed preservation function for the new factory
        :hash - an additional string to alter the calculation of the check digit for diverse projects
        """
        if isinstance(S, basestring):
            us = S.upper()
            if not cls.sumcheck(us, hash):
                raise InvalidIdError('"%s" is not a valid IDstring' % S)
            value = us
        elif isinstance(seed, basestring):
            value = cls.checksum(seed.upper() + cls._check_host(host), hash)
        elif isinstance(seed, int):
            value = cls.checksum(cls.thirty2(seed) + cls._check_host(host), hash)
        else:
            value = cls.checksum('', hash)
        new = text.__new__(cls,value) #create the new instance

        new.value = value # make accessible as an attribute, too, so we can modify it
        try:
            new.host = S.host
        except AttributeError:
            new.host = cls._check_host(host)
        try:
            new.seedstore = S.seedstore
        except AttributeError:
            new.seedstore = seedstore
            if seedstore is not None:
                if not isinstance(seedstore, collections.Callable):
                    raise IdStringError ('seedstore "%s" is not Callable' % repr(seedstore))
        try:
            new.hash = S.hash
        except AttributeError:
            new.hash = hash
        return new

    def get_seed(self):
        """extracts the incrementable part (without the host and checksum digits) of the IDstring"""
        try:
            return self.seed
        except AttributeError:
            try:
                n = len(self.host) + 1
            except TypeError:
                n = 1
            return self.value[:-n]

    def _next_value(self):
        """create the next sequential idString"""
        cat = ''
        seed = self.get_seed()
        n = len(seed)
        keep_looping = True
        while keep_looping:  # this is done using string math (not binary) since usually only one digit is changed
            n -= 1
            c = seed[n]
            i = self.ALPHABET.find(c)
            try:
                cat = self.ALPHABET[i+1] + cat # attempt to get the next higher character on the ALPHABET string
                keep_looping = False # if successful, no carry is needed
            except IndexError:       # a carry is needed, will keep looping
                cat = self.ALPHABET[0] + cat   # supply the lowest character on the ALPHABET string
                if n == 0:   # carrying out of the most significant digit
                    cat = self.ALPHABET[1] + cat # add a new place
                    keep_looping = False
        self.seed = seed[:n] + cat
        return self.checksum(self.seed + self.host, self.hash)

    def _run_factory(self):
        """increments the IDstring, skipping evil words
         <<CAUTION: increments self.value but DOES NOT CHANGE self.__str__>>"""
        self.value = self._next_value()
        # now make sure we're not printing an "unprintable" word
        for bad_word in self.DIRTY_WORDS:
            if bad_word in self.value:
                lsbad = self.value.find(bad_word) + len(bad_word)
                try: staticlen = len(self.host) + 1
                except AttributeError: staticlen = 1
                lsbad = min(len(self.value) - staticlen, lsbad) - 1 # change the seed, not the checksum character itself
                c = self.value[lsbad]  # find the digit for last changeable letter of the bad word
                i = self.ALPHABET.find(c)       # and increment it  NOTE: we assume bad words do not end in 'Y'
                self.value = self.checksum(self.value[:lsbad] + self.ALPHABET[i+1] + self.value[lsbad+1:-1], self.hash)
                self.seed = self.value[:-staticlen]
        if self.seedstore:    # call the seedstore function supplied by the program, with "self" as an argument
            self.seedstore(self)
        return self.value

    def __add__(self, other):
        """supports 'IDstring + 1' to generate the next serial number. (all other addends just do str concat)

        if idstring.host was defined, skip that many characters before incrementing
        !!weird side effect!! doing (i + 1) "N" times WILL produce N sequential values. This is intentional but -- ICK!
        """
        if other == 1:
            return IDstring(self._run_factory(), host=self.host, seedstore=self.seedstore, hash=self.hash)
        else:
            return self.value + other

    def __int__(self):
        """decode the thirty2 string (without the checksum)"""
        return self.thirty2int(self.value[:-1])

    def __repr__(self):
        return "idString('%s')" % self.value    # reveal what's inside

# checksum calulations ...
# calculate a check digit using an arbitrary ALPHABET
# using
# the Luhn mod N algorithm from http://en.wikipedia.org/wiki/Luhn_mod_N_algorithm retrieved 10-1-2013
# original code from wikipedia is identified by the #w comment marks
#w
#w Assuming the following functions are defined:
#w
#w function int CodePointFromCharacter(char character) {...}
#w
#w function char CharacterFromCodePoint(int codePoint) {...}
#w
#w function int NumberOfValidInputCharacters() {...}
#w
#w The function to generate a check character is:
#w
#w function char GenerateCheckCharacter(string input) {
    @classmethod
    def checksum(cls, input, hash=''):              #w
        """idstring.checksum('S': thirty2 encoded string) --> input string with checksum appended"""
        instr = input + text(hash)  # append the hash string to make unique calculations
        factor = 2                                  #w int factor = 2;
        sum = 0                                     #w int sum = 0;
        n = len(cls.ALPHABET)                       #w int n = NumberOfValidInputCharacters();
        #w
        #w // Starting from the right and working leftwards is easier since
        #w // the initial "factor" will always be "2"
        #w for (int i = input.Length - 1; i >= 0; i--) {
        for c in instr[::-1]:
            codePoint = cls.ALPHABET.find(c)   #w int codePoint = CodePointFromCharacter(input[i]);
            addend = factor * codePoint        #w int addend = factor * codePoint;
            #w
            #w// Alternate the "factor" that each "codePoint" is multiplied by
            factor = 1 if factor == 2 else 2        #w factor = (factor == 2) ? 1 : 2;
            #w
            #w// Sum the digits of the "addend" as expressed in base "n"
            addend = (addend // n) + (addend % n)   #w addend = (addend / n) + (addend % n);
            sum += addend                           #w sum += addend;
            #w}
        #w// Calculate the number that must be added to the "sum"
        #w                                          // to make it divisible by "n"
        remainder = sum % n                         #w int remainder = sum % n;
        checkCodePoint = (n - remainder) % n        #w int checkCodePoint = (n - remainder) % n;
        #w
        # (we return the entire checksummed string, not just the checksum character)
        return input + cls.ALPHABET[checkCodePoint]          #w return CharacterFromCodePoint(checkCodePoint);

    #w}
    #w
    #w And the function to validate a string (with the check character as the last character) is:
    #w
    #w function bool ValidateCheckCharacter(string input) {
    @classmethod
    def sumcheck(cls, input, hash=''):              #w
        """idstring.sumcheck(S: IDSTRING) --> True is checksum is valid"""
        factor = 1                                  #w int factor = 1;
        sum = 0                                     #w int sum = 0;
        n =  len(cls.ALPHABET)                      #w int n = NumberOfValidInputCharacters();
        instr = input[:-1] + text(hash) + input[-1] # hash is used to create unique check digits for various projects
        #w
        #w// Starting from the right, work leftwards
        #w// Now, the initial "factor" will always be "1"
        #w// since the last character is the check character
        try:
            for c in instr[::-1]:                       #w for (int i = input.Length - 1; i >= 0; i--) {
                codePoint =  cls.ALPHABET.find(c)       #w    int codePoint = CodePointFromCharacter(input[i]);
                addend = factor * codePoint             #w    int addend = factor * codePoint;
                #w
                #w// Alternate the "factor" that each "codePoint" is multiplied by
                factor = 1 if factor == 2 else 2        #w    factor = (factor == 2) ? 1 : 2;
                #w
                #w// Sum the digits of the "addend" as expressed in base "n"
                addend = (addend // n) + (addend % n)   #w    addend = (addend / n) + (addend % n);
                sum += addend                           #w    sum += addend;
                                                        #w}
        except (ValueError, TypeError):
            return False
        remainder = sum % n                         #w int remainder = sum % n;
                                                    #w
        return remainder == 0                       #w return (remainder == 0);
    #w}
#----end of <idstring.py> --------------------------------------------------------
