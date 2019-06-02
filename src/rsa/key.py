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

import ujson
import rsa.common
import rsa.core

DEFAULT_EXPONENT = 65537


class AbstractKey(object):
    """Abstract superclass for private and public keys."""

    __slots__ = ('n', 'e')

    def __init__(self, n, e):
        self.n = n
        self.e = e

    @classmethod
    def _load_pkcs1_json(cls, keyfile):
        """Loads a key from a JSON file, implement in a subclass.
        :param keyfile: contents of a JSON file that contains the key.
        :type keyfile: bytes
        :return: the loaded key
        :rtype: AbstractKey
        """

    @classmethod
    def load_pkcs1(cls, keyfile, format='JSON'):
        """Loads a key.
        :param keyfile: contents a file that contains the key.
        :type keyfile: bytes
        :param format: the format of the file to load
        :type format: str
        :return: the loaded key
        :rtype: AbstractKey
        """

        methods = {
            'JSON': cls._load_pkcs1_json
        }

        method = cls._assert_format_exists(format, methods)
        return method(keyfile)

    @staticmethod
    def _assert_format_exists(file_format, methods):
        """Checks whether the given file format exists in 'methods'.
        """

        try:
            return methods[file_format]
        except KeyError:
            formats = ', '.join(sorted(methods.keys()))
            raise ValueError('Unsupported format: %r, try one of %s' % (file_format,
                                                                        formats))

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

    def encrypt(self, message):
        """Encrypts the message.
        Note that it doesn't use blinding to prevent side-channel attacks
        :param message: the message to encrypt
        :type message: int
        :returns: the encrypted message
        :rtype: int
        """

        return rsa.core.encrypt_int(message, self.d, self.n)

    @classmethod
    def _load_pkcs1_json(cls, keyfile):
        """Loads a private key from a file.
        The contents of the file should be like the following:
        {
            "q": ... ,
            "e": ... ,
            "d": ... ,
            "p": ... ,
            "n": ...
        }
        :param keyfile: contents of a JSON file that contains the key.
        :return: a PrivateKey object
        """

        data = ujson.loads(keyfile)
        return PrivateKey(data['n'], data['e'], data['d'], data['p'], data['q'])

__all__ = ['PublicKey', 'PrivateKey']
