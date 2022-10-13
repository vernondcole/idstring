""" A class defining a string of non-look-alike digits with a check digit, which can be incremented.

The intent is to create compact serial numbers using a defined alpha-numeric alphabet.
* a "host" field can be defined, so that, if the serial numbers are issued by a known set of
 loosely cooperative units (think of couchdb hosts) the numbers will not conflict.

The default alphabet can be replaced by any unicode string you wish. The check digit will be from your alphabet.

The string is initialized using a five-argument call like; idstring.IDstring(IDstr, seed, host, seedstore, hash)
:IDstr an already-defined idstring.IDstring with checksum. [or None, if you are supplying a "seed"]
:seed - a "seed" value of valid idstring.ALPHABET characters with no checksum [ignored if IDstr is supplied]
:host - the identity number of the" host" on which it is running.
        !!! NOTE: len(host) defines the size of the .host field !!!
:seedstore - a call-back function which the caller promises to use to preserve the state of the seed value.
- - - that function will be called with an idstring object so the caller can extract the incremented seed for storage.
- - - REMINDER...use the .value attribute or get_seed() method. The value of the IDstring cannot be incremented!
:hash - additional character(s) to alter the check digit, so that IDstrings for different purposes do not match.
- - - if hash is None, checksum generation and checking will be disabled.
:case_shift - function to apply to input strings. One of str.upper, str.lower, or None. Default is str.upper()
 Copyright 2013, eHealth Africa   http://www.ehealthafrica.org
 Copyright 2022, Vernon Cole

 """
#  This code is released and licensed under the terms of the Lesser GPL license as specified at the
#  following URL:
#   http://www.gnu.org/copyleft/lgpl.html
#
from collections.abc import Callable

__author__ = "Vernon Cole <vernondcole@gmail.com>"
__version__ = "2.0.3"

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

#Define exceptions
import idstring


class IdStringError(ValueError):
    """Base class for all errors in the IdString package"""
    pass
class OutOfRangeError(IdStringError): pass
class InvalidIdError(IdStringError): pass

def noshift(s):
    """
    a function which returns its argument unchanged (null)
    """
    return s

DEFAULT_CASE_SHIFT = str.upper

# define the characters which may legally appear in an idString
DEFAULT_ALPHABET = "0123456789ABCDEFGHJKLMNPRSTUVWXY"

# create a list of George Carlan's "the seven words you can't say on T.V."
# plus a few extras, but ignoring those with an "I" in them, since the default ALPHABET has no "I"
DEFAULT_DIRTY_WORDS = [c[::-1] for c in ['KCUF', 'TNUC', 'TRAF', 'DRUT', 'TAWT', 'SLLAB']]
DIRTY_I_WORDS = [c[::-1] for c in ['TIHS', 'TIT', 'SSIP']]  # if your alternate alphabet contains an "I"
# alter your list like--> IDstring.DIRTY_WORDS = idstring.DEFAULT_DIRTY_WORDS + idstring.DIRTY_I_WORDS
# the words are stored backwards in the source, because 'kcuf' is not objectionable.
# the dirty word test is case independent.


class IDstring(str):
    """
    Returns a complex string-value object which has an _add_ method for plus 1.
    """
    #the following are class attributes for IDstrings.  They may be redefined if a programmer
    #whishes to change what in "idString" looks like.
    # For our sample application, We have chosen a three character hostNumber field and
    # a four character idNumber field, with the default
    # composed of a 32 character ALPHABET [0-9,A-H,J-N,P,R-Y]. i o q and z are out so no "1Il" "OQ0" "2Z" errors
    # with a luhn_N check digit
    ALPHABET = DEFAULT_ALPHABET
    DIRTY_WORDS = DEFAULT_DIRTY_WORDS

    @classmethod
    def thirty2(cls, *args):
        raise NotImplementedError('This method has been deprecated.')
    @classmethod
    def thirty2int(cls, *args):
        raise NotImplementedError('This method has been deprecated.')


    def _check_host(self, host):
        try:
            h = self.host
            if len(host) != len(h):
                raise   InvalidIdError(f'New host examples must be same length as defined host field "{h}"')
            case_shift = self.case_shift
            d = case_shift(str(host).strip())
            for c in d:
                if not c in self.alphabet:
                    raise InvalidIdError('Incorrect character "%s" in "%s"' % (c, d))
            return d
        except AttributeError:
            return host

    @staticmethod
    def __new__(cls, idstr=None, seed=None, host='', seedstore=None, hash='', alphabet=None,
                case_shift=DEFAULT_CASE_SHIFT, no_check=False):
        """
        :S - an existing legal idString, or None
        :seed - the seed string for a new factory [ignored unless S is None]
        :host - the host portion for a new idString factory, len(host) will set host length for factory
        :seedstore - a seed preservation function for the new factory
        :hash - an additional string to alter the calculation of the check digit for diverse projects
                pass hash=None to turn off checksum testing and creation. Makes this module dumb.
        :case_shift - function to apply to input strings. one of str.upper str.lower or None
        """
        if case_shift is None:
            case_shift = noshift
        try:
            if seed:
                seed = case_shift(seed)
            if host:
                host = case_shift(host)
        except TypeError:
            IdStringError(f'Invalid seed "{seed}" or host "{host}" argument')
        alphabet = alphabet or IDstring.ALPHABET
        value = None
        if isinstance(idstr, cls):
            value = str(idstr)
            if host != idstr.host:
                raise InvalidIdError(f'Cannot use host "{host}" with id "{value}"')
            seed = idstr.get_seed()  # we cannot change any of these things
            hash = idstr.hash
            alphabet = idstr.alphabet
            seedstore = idstr.seedstore
            case_shift = idstr.case_shift
        elif isinstance(idstr, str):
            us = case_shift(idstr)  # if passing a string as on IDstring, it must already have a checksum
            if no_check:
                value = us
            else:
                if _sumcheck(us, hash, case_shift=case_shift, alphabet=alphabet):
                    value = us
                else:
                    raise InvalidIdError(f'Invalid checksum in id={us}')
        if value is None:
            if isinstance(seed, str):  # passing a seed means we need a checksum and host
                new_root = seed + case_shift(host)
                value = _checksum(new_root, hash, alphabet)
            else:
                raise InvalidIdError(f'No valid ID in id="{idstr}" or seed="{seed}"')
        value = case_shift(value)
        new = super().__new__(cls, value) #create the new instance
        new.seed = seed  # fill in the new instances attributes (as if we were __init__)
        new.host = host
        new.hash = hash
        new.alphabet = alphabet
        if seedstore is not None:
            if not isinstance(seedstore, Callable):
                raise IdStringError ('seedstore "%s" is not Callable' % repr(seedstore))
        new.seedstore = seedstore
        new.case_shift = case_shift
        return new


    def get_seed(self):
        """extracts the incrementable part (without the host and checksum digits) of the IDstring"""
        try:
            ret = self.seed
        except AttributeError:
            ret = None
        if ret is None:
            inc = 0 if self.hash is None else 1
            try:
                n = len(self.host) + inc
            except TypeError:
                n = inc
            ret = str(self)[:-n] if n > 0 else str(self)
        return ret


    def _next_value(self):
        """create the next sequential idString"""
        cat = ''
        seed = self.get_seed()
        n = len(seed)
        keep_looping = True
        while keep_looping:  # this is done using string math (not binary) since usually only one digit is changed
            n -= 1
            c = seed[n]
            i = self.alphabet.find(c)
            try:
                cat = self.alphabet[i+1] + cat # attempt to get the next higher character on the ALPHABET string
                keep_looping = False # if successful, no carry is needed
            except IndexError:       # a carry is needed, will keep looping
                cat = self.alphabet[0] + cat   # supply the lowest character on the ALPHABET string
                if n == 0:   # carrying out of the most significant digit
                    carry_digit = '1' if self.alphabet[0] == '0' else self.alphabet[0]
                    cat = carry_digit + cat # add a new place
                    keep_looping = False
        seed = seed[:n] + cat
        self.seed = seed
        return _checksum(seed + self.host, self.hash, self.alphabet)


    def _run_factory(self):
        """increments the IDstring, skipping evil words
         <<CAUTION: increments next_value but DOES NOT CHANGE self.__str__>>"""
        next_value = self._next_value()
        # now make sure we're not printing an "unprintable" word
        checksum_size = 1 if self.hash is not None else 0
        next_upped = next_value.upper()
        for bad_word in self.DIRTY_WORDS:
            if bad_word in next_upped:
                wherebad = next_upped.find(bad_word) + len(bad_word)
                try: staticlen = len(self.host) + checksum_size
                except AttributeError: staticlen = 1
                wherebad = min(len(next_value) - staticlen, wherebad) - checksum_size  # change the seed, not the checksum character itself
                c = next_value[wherebad]  # find the digit for last changeable letter of the bad word
                next_index = self.alphabet.find(c) + 1       # and increment it
                if next_index < len(self.alphabet):  # if the bad word does not end in 'Y'
                    next_root = next_value[:wherebad] + self.alphabet[next_index] + next_value[wherebad+1:-1]
                    next_value = _checksum(next_root, self.hash, self.alphabet)
                else:
                    next_value = self._run_factory()  # will this ever happen?
        del self.seed  # invalidate cached seed
        return next_value


    def __add__(self, other):
        """supports 'IDstring + 1' to generate the next serial number. (all other addends just do str concat)

        if idstring.host was defined, skip that many characters before incrementing
        !!weird side effect!! doing (i + 1) "N" times WILL produce N sequential values. This is intentional but -- ICK!
        """
        if other == 1:
            next_thing = self._run_factory()
            ret = IDstring(next_thing, host=self.host, seedstore=self.seedstore, hash=self.hash,
                           case_shift=self.case_shift, alphabet=self.alphabet, no_check=True)
            if ret.seedstore:    # call the seedstore function supplied by the program, with "self" as an argument
                ret.seedstore(ret)
            return ret
        else:
            return str(self) + other

    @property
    def value(self):
        str(self)

    def __repr__(self):
        return "idString('%s')" % str(self)    # reveal what's inside

    @classmethod
    def checksum(cls, s, hash='', alphabet=''):
        alphabet = alphabet or cls.ALPHABET
        return _checksum(s, hash, alphabet)


    @classmethod
    def sumcheck(cls, s=None, hash='', alphabet=None, case_shift=None):
        if s is None:  # called as an instance method
            s = str(cls)
        return _sumcheck(s, hash, alphabet, case_shift)


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
#w function char GenerateCheckCharacter(string s) {
def _checksum(s, hash='', alphabet=''):   #w
        """idstring.checksum('s': string) --> s string with checksum appended"""
        if hash is None:
            return s
        instr = s + hash  # append the hash string to make unique calculations
        factor = 2                                  #w int factor = 2;
        sum = 0                                     #w int sum = 0;
        n = len(alphabet)                       #w int n = NumberOfValidInputCharacters();
        #w
        #w // Starting from the right and working leftwards is easier since
        #w // the initial "factor" will always be "2"
        #w for (int i = input.Length - 1; i >= 0; i--) {
        for c in instr[::-1]:
            codePoint = alphabet.find(c)   #w int codePoint = CodePointFromCharacter(input[i]);
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
        return s + alphabet[checkCodePoint]          #w return CharacterFromCodePoint(checkCodePoint);

    #w}
    #w
    #w And the function to validate a string (with the check character as the last character) is:
    #w
    #w function bool ValidateCheckCharacter(string input) {
def _sumcheck(s, hash='', alphabet=None, case_shift=None):
        """idstring.sumcheck(S: IDSTRING) --> True is checksum is valid"""
        if not alphabet:
            alphabet = IDstring.ALPHABET
        if case_shift is None:
            case_shift = DEFAULT_CASE_SHIFT
        if hash is None:  # checksums are not in use.
            for c in case_shift(s):
                if c not in alphabet:
                    return False
            return True

        factor = 1                                  #w int factor = 1;
        sum = 0                                     #w int sum = 0;
        n =  len(alphabet)                      #w int n = NumberOfValidInputCharacters();
        s_hash = s[:-1] + str(hash) + s[-1] # if len(s) > 1 else s + str(hash) # place hash characters next-to right
        instr = case_shift(s_hash)

        # optional "hash" is used to create unique check digits for various projects
        #w
        #w// Starting from the right, work leftwards
        #w// Now, the initial "factor" will always be "1"
        #w// since the last character is the check character
        try:
            for c in instr[::-1]:                       #w for (int i = input.Length - 1; i >= 0; i--) {
                codePoint =  alphabet.find(c)       #w    int codePoint = CodePointFromCharacter(input[i]);
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
