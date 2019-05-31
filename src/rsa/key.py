# -*- coding: utf-8 -*-
#
#  Copyright 2011 Sybren A. Stüvel <sybren@stuvel.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""RSA key generation code.

.. note::

    Storing public and private keys via the `pickle` module is possible.
    However, it is insecure to load a key from an untrusted source.
    The pickle module is not secure against erroneous or maliciously
    constructed data. Never unpickle data received from an untrusted
    or unauthenticated source.

"""

import rsa.common
import rsa.core
import rsa.randnum
import gc


DEFAULT_EXPONENT = 65537


class AbstractKey(object):
    """Abstract superclass for private and public keys."""

    __slots__ = ('n', 'e')

    def __init__(self, n, e):
        self.n = n
        self.e = e

    def blind(self, message, r):
        """Performs blinding on the message using random number 'r'.
        :param message: the message, as integer, to blind.
        :type message: int
        :param r: the random number to blind with.
        :type r: int
        :return: the blinded message.
        :rtype: int
        The blinding is such that message = unblind(decrypt(blind(encrypt(message))).
        See https://en.wikipedia.org/wiki/Blinding_%28cryptography%29
        """

        # MicroPython 1.10 doesn't support pow() with 3 parameters
        t = self.pow(r, self.e, self.n)
        return (message * t) % self.n

    def check_memory(self):
        if gc.mem_free() < 2048:
            print('collect garbage, gc.mem_free() = ' + str(gc.mem_free()) + ' bytes available')
            gc.collect()
            print('gc.mem_free() = ' + str(gc.mem_free()))

    def pow(self, a, b, n):
        if b == 0:
            return 1

        r = 1
        i = 0
        while i < b:
            r = r * a

            try:
                r = r % n
            except MemoryError:
                gc.collect()
                r = r % n
                print('we just had some problems with memory')
                print('but successfully recovered: ' + str(gc.mem_free()))

            i = i + 1

        return r

    def unblind(self, blinded, r):
        """Performs blinding on the message using random number 'r'.
        :param blinded: the blinded message, as integer, to unblind.
        :param r: the random number to unblind with.
        :return: the original message.
        The blinding is such that message = unblind(decrypt(blind(encrypt(message))).
        See https://en.wikipedia.org/wiki/Blinding_%28cryptography%29
        """

        return (rsa.common.inverse(r, self.n) * blinded) % self.n


class PublicKey(AbstractKey):
    """Represents a public RSA key.

    This key is also known as the 'encryption key'. It contains the 'n' and 'e'
    values.

    Supports attributes as well as dictionary-like access. Attribute access is
    faster, though.

    >>> PublicKey(5, 3)
    PublicKey(5, 3)

    >>> key = PublicKey(5, 3)
    >>> key.n
    5
    >>> key['n']
    5
    >>> key.e
    3
    >>> key['e']
    3

    """

    __slots__ = ('n', 'e')

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return 'PublicKey(%i, %i)' % (self.n, self.e)

    def __getstate__(self):
        """Returns the key as tuple for pickling."""
        return self.n, self.e

    def __setstate__(self, state):
        """Sets the key from tuple."""
        self.n, self.e = state

    def __eq__(self, other):
        if other is None:
            return False

        if not isinstance(other, PublicKey):
            return False

        return self.n == other.n and self.e == other.e

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.n, self.e))


class PrivateKey(AbstractKey):
    """Represents a private RSA key.
    This key is also known as the 'decryption key'. It contains the 'n', 'e',
    'd', 'p', 'q' and other values.
    Supports attributes as well as dictionary-like access. Attribute access is
    faster, though.
    >>> PrivateKey(3247, 65537, 833, 191, 17)
    PrivateKey(3247, 65537, 833, 191, 17)
    exp1, exp2 and coef will be calculated:
    >>> pk = PrivateKey(3727264081, 65537, 3349121513, 65063, 57287)
    >>> pk.exp1
    55063
    >>> pk.exp2
    10095
    >>> pk.coef
    50797
    """

    __slots__ = ('n', 'e', 'd', 'p', 'q', 'exp1', 'exp2', 'coef')

    def __init__(self, n, e, d, p, q):
        AbstractKey.__init__(self, n, e)
        self.d = d
        self.p = p
        self.q = q

        # Calculate exponents and coefficient.
        self.exp1 = int(d % (p - 1))
        self.exp2 = int(d % (q - 1))
        self.coef = rsa.common.inverse(q, p)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return 'PrivateKey(%(n)i, %(e)i, %(d)i, %(p)i, %(q)i)' % self

    def __getstate__(self):
        """Returns the key as tuple for pickling."""
        return self.n, self.e, self.d, self.p, self.q, self.exp1, self.exp2, self.coef

    def __setstate__(self, state):
        """Sets the key from tuple."""
        self.n, self.e, self.d, self.p, self.q, self.exp1, self.exp2, self.coef = state

    def __eq__(self, other):
        if other is None:
            return False

        if not isinstance(other, PrivateKey):
            return False

        return (self.n == other.n and
                self.e == other.e and
                self.d == other.d and
                self.p == other.p and
                self.q == other.q and
                self.exp1 == other.exp1 and
                self.exp2 == other.exp2 and
                self.coef == other.coef)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.n, self.e, self.d, self.p, self.q, self.exp1, self.exp2, self.coef))

    def blinded_encrypt(self, message):
        """Encrypts the message using blinding to prevent side-channel attacks.
        :param message: the message to encrypt
        :type message: int
        :returns: the encrypted message
        :rtype: int
        """

        blind_r = rsa.randnum.randint(self.n - 1)
        blinded = self.blind(message, blind_r)  # blind before encrypting
        encrypted = rsa.core.encrypt_int(blinded, self.d, self.n)
        return self.unblind(encrypted, blind_r)


__all__ = ['PublicKey', 'PrivateKey']
