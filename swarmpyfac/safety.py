""" The safe_user module provides basic security for login information.

This module is used to save login credentials safely in an encrypted file
and still have it employed by through an API,
with possibility for user prompting for password to open said file.

It uses AES encryption with random initial vector saved in file,
with the message containing padding if it is short,
typically less than 4096 characters.
No guarentee is granted on the strength of the randomization.
There is given no certification on the security level of data 
stored by the use of this module, so it is mainly recommended 
to be used for data requiring only lower level security,
such as access to unimportant/semi-public websites.
If you need high secrutity storage, such as for credit card
information or state or trade secrets, it is hightly suggested
you consult a security proffesional on what would be adequat.

Guide
-----
This module is a functional library, with an onion-like abstraction structure.
There are in general functions to add and remove single layers,
or add or remove all they way up to a specific layer.
You can use this to provide a solution on the level you need.

Each layer has their own section, so you can go look at that,
for information on that specific layer.
The layers are: XML, Padding, Encryption, Boxing, Locking.
There is also a section called Other, which is on parts of the module,
which falls outside the specific layers.

XML
---
This is the base structure used for communicating data.
This can be considered the core of the onion,
and most of functions can work with other data structures.
The exceptions are fetch_login, and those with XML in their name.
    
Functions on this layer:
    build_default_XML
        Build a minimal XML structure.
    find_login_in_XML
        Extract login information from the XML structure.
        
Padding
-------
When we add the padding layer we extend a text,
such that it is a valid input for the encryption layer.
We also use it to ensure that messages are not short,
and provide extra entropy.
The padding layer contains the meta-data needed to undo the padding.
A message which has this layer applied to it is called
a padded message/text or padded for short.

The format used is as follows:
'Hxxx*paddedMessage              '
Where H is a hexadeximal number describing how many extra spaces are placed
at the end to reach a length divisible by 16.
The xxx describes how many characters to skip
between each character in the message, it is terminated by the '*'

Functions on this layer:
    format_padding
        A function that takes a text and formats it into a valid padding.
        You can use this as a minimal padding scheme.
    remove_padding
        Recover the plain text from the padded text.
    add_padding
        Use sdefault way to add padding.
    add_padding1, add_padding2, add_padding3
        Different implementations of padding.
    set_padding_defaults
        Used to change add padding defaults, so one can use a different
        algorithm or base even when using functions that hide these details.
    
Encryption
----------
When we add the encryption layer we apply AES encryption on a padded text.
This requires a block size of 128 bits, which means the padded text
must effectively have a length divisable by 16 (assuming 8 bit charcters).
The key used is constructed from cryptographic hashing, 
so it is possible to use arbitary length passwords.
AES encryption requires an initialization vector (IV),
which is assumed to be of 1 block length (128 bits or 16 characters).
Failure to satisfy these requirements may result in undocumented errors,
as the layers around this is build to ensure that they are satisfied.
A message which has this layer applied to it is called
eitger an encrypted message/text or cipher text or cipher for short.

Functions on this layer:
    encrypt
        applies the encryption layer to a padded text.
    decrypt
        removes the rencryption layer and recover a padded text.

Boxing
------
The boxing layer is concerned with creating a package
of an encrypted message and its initialization vector.
The boxing layer only comes in the form where it applies
multiple layers at once, and it is intended as a simple
to use outer interface, where you do not need to concern
yourself with more than what message you have,
and what password to encrypt it with.
This means that both the padding layer and encryption
layer are also applied together with the boxing layer.
A message which has this layer applied to it is called a boxed message/text.

Functions in this layer:
    box_content
        Take a message (before padding layer),
        and apply layers with the boxing layer as the outermost layer.
    unbox_content
        Take a boxed message and remove,
        where the innermost layer removed is the padding layer.

Locking
-------
The locking layer is the use of file abstraction,
where the content of those files may have been boxed on unboxed.
Just like the boxing layer it is intended as a finishing layer,
where instead of being applied to strings like the boxing layer,
it is applied to files instead.
A file which has this layer applied to it is called
a locked file or an encrypted file.

Functions in this layer:
    lock_file
        Take a file with some content, and overwrite it with
        a version of it itself where its content have been boxed.
    unlock_file
        Take a file with some boxed content, and overwrite it with
        a version of it itself where its content have been unboxed.
    fetch_login
        Look into a file with boxed xml based content,
        unbox the content and return information from the file.
        All without changing the file.
    build_file
        Construct xml content similar to build_default_XML,
        and write a locked file with that content.
        
Other
-----
_chain
    A function used to fcreater flatter generators.
prompt_login_data
    A function used to prompt username and password from a user at runtime.
prompt_password
    A function used to prompt password from a user at runtime.
    
Examples
--------
>>> from pyfac.safety import *  # doctest: +SKIP
>>> c = box_content('One Ring to rule them all, '
...                 'One ring to find them; '
...                 'One ring to bring them all '
...                 'and in the darkness bind them.', password='Tolkien')
>>> len(c)
3456
>>> s = unbox_content(c,password='Tolkien')
>>> s[:26]
'One Ring to rule them all,'

>>> build_file('test.xml',
...             password='bukke bruse', 
...             default_login=('user1','failed'))  # doctest: +SKIP
>>> fetch_login('test.xml', password='bukke bruse')  # doctest: +SKIP
{'username': 'user1', 'password': 'failed')
"""

__version__ = '0.4.0'
__author__ = 'Ask Neve Gamby'

import random
import math
import string
import os.path

import hashlib
import getpass
import xml.etree.ElementTree as ET
from Crypto.Cipher import AES


def _chain(*args):
    if len(args) == 1:
        args = args[0]
    for arg in args:
        yield from arg


def prompt_login_data():
    """ Prompt a username and a password from the user.
    
    This function prompts the user two times,
    first for a username, secondly for a password.
    The password prompt hides the input from view,
    such that one can enter it 
    while others might be looking at the screen.
    
    Returns
    -------
    A tuple containing the following:
    user : str
        A string corrinsponding to the entered username.
    pw : str
        A string corrinsponding to the entered password.
        
    Note
    ----
    The input from the user is not sanity-checked,
    so it can form a popential vurnerability in deployed software.
    
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> prompt_login_data() # doctest: +ELLIPSIS, +SKIP
    Enter login username:...
    Enter login password:...
    ('...', '...')
    """
    # """ Prompts the user for username and password,
    # and returns them.
    # Note that the password is typed in hidden.
    # """
    user = input('Enter login username:')
    pw = getpass.getpass('Enter login password:')
    return (user, pw)


def prompt_password(default='Def8lttPa88word',
                    is_bad=lambda x: len(x) < 1):
    """ Prompts the user for a password.
    
    This function prompts the user once for a password.
    The password prompt hides the input from view,
    such that one can enter it 
    while others might be looking at the screen.
    
    This function also allows some sanity checking of the
    input password, and will replace the password with
    a default if the users input fails the sanity check.
    
    Note that this function is intended to be for passwords,
    that represent the encryption keys to a file.
    
    Parameters
    ----------
    default : str
        A default password to use if the password given
        by the user does not pass the sanitycheck.
    is_bad : str -> boolean
        A function that takes a string (specifically a
        password candidate) and sanity chekcs it.
        Note that this function must return True
        if the candidate is to be discarded, and False
        if the candidate can be accepted.
        
    Returns
    -------
    str
        The password given by the user or the default password,
        if the password given by the user does not pass the sanity check.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> prompt_password() # doctest: +ELLIPSIS, +SKIP
    Enter password for file: ...
    ...
    """
    # """ Prompts the user for a password.
    # If the password is unsatisfactory it is replaced with a default.
    # """
    password = getpass.getpass('Enter password for file: ')
    if is_bad(password):
        password = default
    return password
    
    
def format_padding(text,stride=1,*args,**kwargs):
    """ Formats a message in relation with padding and its metadata.
    
    Format a message such that it includes the meta
    needed to remove the padding.
    It also may add whitespace at the end to ensure it can be AES encrypted.
    This function is sufficient for use of the encrypt function.
    
    The format looks as follows:
    'Hxxx*message    '
    H is a single hexadeximal digit, counting how many spaces
    have been added at the end.
    xxx is some digits representing stride in decimal character notation.
    There amount of digits in xxx is not fixed.
    The * specify when the xxx digits end and when the text starts.
    
    Parameters
    ----------
    text : str
        A string containing the message.
    stride : int, optional
        An integer describing the stride used for where in the text
        that the actual message can be located.
        Defaults to 1.
    *args
        Extra positional arguments, which are discared.
        This is here so it can be called with extra positional arguments.
    **kwargs
        Extra keyword arguments, which are discared.
        This is here so it can be called with extra keyword arguments.
        
    Returns
    -------
    str
        A string with meta-data. It satisfies len(s) % 16 == 0.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> format_padding('')
    'd0*             '
    >>> format_padding('short message')
    '00*short message'
    >>> format_padding('secret message')
    'f0*secret message               '
    >>> format_padding('DsReLcnrieBtJ 0mxeRsmsuaQgOe',2)
    '11*DsReLcnrieBtJ 0mxeRsmsuaQgOe '
    """
    # prefix = ['0',str(stride),'*']
    # if length is None:
        # length = len(text) + sum(map(len,prefix))
        
    text = str(stride-1) + '*' + text #we record skips instead of stride
    extra = (16 - ((len(text) + 1) % 16)) % 16
    return hex(extra)[2] + text + ' '*extra
    

    
def add_padding1(text, base=4096):
    """ Adds padding to the text so it fits well into encryption blocks.
    
    This function adds padding to a text, and include some metadata,
    which can be used to identify which parts are the padding,
    and thereby remove it.
    This function may add up to two types of padding,
    in addition to metadata that may also be added.
    The first padding type is a randomized padding that spreads
    out the input text to ensure that the text is not too short,
    and to provide resistance against length based attacks.
    The second padding type is blank padding used make the text
    compatible with block ciphers.
    This function is hardcoded to align to blocks of length 16.
    
    Warning
    -------
    This function has been depreciated, you should use add_padding2
    instead, since this one suffers performance problems.
    
    Parameters
    ----------
    text : str
        The text that is to be padded.
    base : int, optional
        An integer describing the boundary between short and long texts,
        where only short texts may be subject to the first type of padding.
        Default is 4096, must be at least 1.
        
    Returns
    -------
    str
        A string based on text, which has length % 16 == 0.
        It also contains the information needed to remove the padding.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> add_padding1('secret message') # doctest: +ELLIPSIS
    'b255*...s...e...c...r...e...t... ...m...e...s...s...a...g...e           '
    >>> add_padding1('secret message',16) # doctest: +ELLIPSIS
    'f0*secret message               '
    >>> add_padding1('secret message',8) # doctest: +ELLIPSIS
    'f0*secret message               '
    """
    # """ Adds enough padding to ensure it can easily be encrypted.
    # It also add random signal if the text is much shorter
    # than the base.
    # Warning: This function is not assymtothically inefficient
    # """
    padded = text
    applications = 0
    if len(text) < base:
        if len(padded) == 0:
            padded = ' '
            applications = 1
        while len(padded)<<1 <= base - len(str(base)) - 2:
            applications += 1
            temp = random.choices(
                string.ascii_uppercase
                + string.ascii_lowercase
                + string.digits,
                k=len(padded))
            padded = ''.join(k + c for (k, c) in zip(temp, padded))
    return format_padding(padded,1 << applications)
    # padded = str(1 << applications) + '*' + padded
    # extra = (16 - ((len(padded) + 1) % 16)) % 16
    # padded = hex(extra)[2] + padded + ' '*extra
    # return padded
    

def add_padding2(text, base=4096):
    """ Adds padding to the text so it fits well into encryption blocks.
    
    This function adds padding to a text, and include some metadata,
    which can be used to identify which parts are the padding,
    and thereby remove it.
    This function may add up to two types of padding,
    in addition to metadata that may also be added.
    The first padding type is a randomized padding that spreads
    out the input text to ensure that the text is not too short,
    and to provide resistance against length based attacks.
    The second padding type is blank padding used make the text
    compatible with block ciphers.
    This function is hardcoded to align to blocks of length 16.
    
    Parameters
    ----------
    text : str
        The text that is to be padded.
    base : int, optional
        An integer describing the boundary between short and long texts,
        where only short texts may be subject to the first type of padding.
        Default is 4096, must be at least 1.
        
    Returns
    -------
    str
        A string based on text, which has length % 16 == 0.
        It also contains the information needed to remove the padding.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> add_padding2('secret message') # doctest: +ELLIPSIS
    'b255*...s...e...c...r...e...t... ...m...e...s...s...a...g...e           '
    >>> add_padding2('secret message',16) # doctest: +ELLIPSIS
    'f0*secret message               '
    >>> add_padding2('secret message',8) # doctest: +ELLIPSIS
    'f0*secret message               '
    """
    # """ Adds enough padding to ensure it can easily be encrypted.
    # It also add random signal if the text is much shorter
    # than the base.
    # """
    padded = text
    # applications = 0
    if len(text) < base:
        applications = math.floor(math.log2(base/max(len(text), 1)))
        # print(applications,1<<applications,base)
        if len(text) == 0:
            padded = ' '
            # stride = 1<<(applications+1) 
        while len(padded) << applications > base - len(str(base))-2 and applications > 0:
            # print('applications: ' + str(applications) + ' -> ' + str(applications-1))
            applications -= 1
        stride = 1 << applications
        options = (string.ascii_uppercase
                   + string.ascii_lowercase
                   + string.digits)
        rand = random.SystemRandom()
        # print( applications, (1 << applications), (1 << applications) - 1)
        padded = ''.join(_chain(_chain(
            rand.choices(options, k=(1 << applications) - 1), (char,))
            for char in padded))
    else:
        stride = 1
    return format_padding(padded,stride if text else max(base+1,2))
    # padded = str(1 << applications) + '*' + padded
    # extra = (16 - ((len(padded) + 1) % 16)) % 16
    # # print(extra)
    # padded = hex(extra)[2] + padded + ' '*extra
    # return padded

    
def add_padding3(message, base=4096):
    stride = math.floor(base/max(len(message),1))
    stride = max(stride,1)
    # print(stride,stride-1)
    if len(message) < base:
        options = (string.ascii_uppercase
               + string.ascii_lowercase
               + string.digits)
        rand = random.SystemRandom()
        padded = ''.join(_chain(_chain(
            rand.choices(options, k=stride-1), (char,))
            for char in (message if message else ' ')))
    else:
        padded = message
    return format_padding(padded,stride if message else max(base+1,2))

    
def add_padding(message, base = 4096, algorithm=add_padding2):
    return algorithm(message,base=base)
    
    
def set_default_padding(base = 4096, algorithm=add_padding2):
    add_padding.__defaults__ = (base,algorithm)
    

def _split_padding(padded):
    """ Used for debugging."""
    extra = int(padded[0], 16)  # read first character as hexadeximal
    temp = padded[1:len(padded)-(extra)]
    skip, temp = temp.split('*', 1)
    stride = int(skip)+1
    if int(stride) > 0:
        result = temp[int(stride)-1::int(stride)]
        rand = ''.join(c for i,c in enumerate(temp) if i not in range(int(stride)-1,len(temp),int(stride)))
    return [extra, stride, '*', rand, result, padded[len(padded)-(extra):]]
    
    

def remove_padding(padded):
    """ Remove the padding from a string.
    
    This function removes the padding generated by an addpadding
    or the simpler format_padding, including the metadata.
    The text is assumed to satisfy the format given in format_padding.
    
    Parameters
    ----------
    padded : str
        A piece of text that have been padded by an add_padding.
        
    Returns
    -------
    str
        A string of the text without the padding.
        This should be equivalent to the text before padding was added.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> padded = add_padding('secret message')
    >>> remove_padding(padded)
    'secret message'
    >>> remove_padding(add_padding('other message',16))
    'other message'
    >>> remove_padding(add_padding('another message',8))
    'another message'
    """
    # base : int, optional
    # An integer describing the boundary between short and long texts,
    # where only short texts may be subject to the first type of padding.
    # It is important that this is the same as for the call to add_padding2,
    # as this data is not part of the metadata included in the padding.
    # Default is 4096, must be at least 1.
    # There is no guarentee for correct recovery of the message
    # and removal of padding, if the base used on add_padding2
    # and remove_padding are different, though for some cases
    # it will still work (such as if both have len(padded)> base).
    # """ removes the padding added by add_padding,
    # assuming they are done with the same base.
    # """
    extra = int(padded[0], 16)  # read first character as hexadeximal
    result = padded[1:len(padded)-(extra)]
    # if len(result) < base:
    skip, result = result.split('*', 1)
    stride = int(skip)+1
    if int(stride) > 0:
        result = result[int(stride)-1::int(stride)]
    return result


def encrypt(padded, password=None, IV=16 * '\x7A'):
    """ Encrypt a text with AES encryption.
    
    Encrypts a text with the AES encryption, with given intial vector,
    and a password either passed or prompted to the user at runtime.
    
    Parameters
    ----------
    padded : str
        A string of (padded) text to be encrypted.
        It must satisfy len(padded)%16 == 0.
    password : str, optional
        The password used to construct the key for the encryption.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
    IV : str, optional
        A string representing the initial vector of the AES encryption.
        Must be exactly 16 bytes long (equivalent to 16 normal characters).
        Default is 16 repeat '\x7A' == 'z' letters.
        
    Returns
    -------
    binary string
        A binary string containing the encrypted text.
    
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> payload = add_padding('message',8)
    >>> encrypt(payload, password='ESA') # doctest: +ELLIPSIS
    b'...'
    """
    # """ Encrypt text with AES encryption,
    # with given password and InitialVector.
    # If no password is given the user will be promted for one.
    # Returns a binary string
    # """
    if password is None:
        password = prompt_password()
    hashed = hashlib.sha256(password.encode('utf-8')).digest()
    return AES.new(hashed, AES.MODE_CBC, IV=IV).encrypt(padded)


def decrypt(cipher_text, password=None, IV=16 * '\x7A'):
    """ Decrypt an AES encrypted message.
    
    Decrypts a text with the AES encryption, with given intial vector,
    and a password either passed or prompted to the user at runtime.
    
    Parameters
    ----------
    cipher_text : binary str
        A string of binary type, which contains an AES encrypted message.
    password : str, optional
        The password used to construct the key for the decryption.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
    IV : str, optional
        A string representing the initial vector of the AES encryption.
        Must be exactly 16 bytes long (equivalent to 16 normal characters).
        Default is 16 repeat '\x7A' == 'z' letters.
        
    Returns
    -------
    str
        A string representing the decrypted text.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> payload = add_padding('message',8)
    >>> cipher_text = encrypt(payload, password='ESA') # doctest: +ELLIPSIS
    >>> decrypt(cipher_text, password='ESA') == payload
    True
    """
    # """ Decrypt text with AES encryption,
    # with given password and InitialVector.
    # If no password is given the user will be promted for one.
    # """
    if password is None:
        password = prompt_password()
    hashed = hashlib.sha256(password.encode('utf-8')).digest()
    return AES.new(hashed, AES.MODE_CBC, IV=IV).decrypt(cipher_text).decode('utf-8')


def find_login_in_XML(text, target='viresLogin'):
    """ Search an XML string for login-like information.
    
    Search a string of xml structure of a specific form.
    It is assumed that the xml structure contains the following structure:
    Outermost a root of arbitary tag.
    Inside the root one or more taged pieces, one being "default"
    Inside these tags a set of tags with text content.
    
    Parameters
    ----------
    text : str
        A string containing a xml structure as described above.
    target : str, optional
        A string describing the tag to search for.
        Searches for 'default' if not found.
        Defaults to 'viresLogin'.
        
    Returns
    -------
    dict
        A dictionary containing the pairs of tags and text,
        for tags found as children to the search result.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> find_login_in_XML('<xml>'
    ...                   '  <default>'
    ...                   '    <username>admin</username>'
    ...                   '    <password>123</password>'
    ...                   '  </default>'
    ...                   '</xml>')
    {'username': 'admin', 'password': '123'}
    >>> find_login_in_XML('<xml>'
    ...                   '  <viresLogin>'
    ...                   '    <username>admin</username>'
    ...                   '    <password>123</password>'
    ...                   '  </viresLogin>'
    ...                   '</xml>')
    {'username': 'admin', 'password': '123'}
    >>> find_login_in_XML('<xml>'
    ...                   '  <default>'
    ...                   '    <username>admin</username>'
    ...                   '    <password>123</password>'
    ...                   '  </default>'
    ...                   '  <viresLogin>'
    ...                   '    <username>John</username>'
    ...                   '    <password>Doe</password>'
    ...                   '  </viresLogin>'
    ...                   '</xml>')
    {'username': 'John', 'password': 'Doe'}
    >>> find_login_in_XML('<xml>'
    ...                   '  <default>'
    ...                   '    <username>admin</username>'
    ...                   '    <password>123</password>'
    ...                   '  </default>'
    ...                   '  <viresLogin>'
    ...                   '    <username>John</username>'
    ...                   '    <password>Doe</password>'
    ...                   '  </viresLogin>'
    ...                   '  <trouble>'
    ...                   '    <username>snowflake</username>'
    ...                   '    <password>unique</password>'
    ...                   '  </trouble>'
    ...                   '</xml>',
    ...                   'trouble')
    {'username': 'snowflake', 'password': 'unique'}
    >>> find_login_in_XML('<xml>'
    ...                   '  <default>'
    ...                   '    <username>admin</username>'
    ...                   '    <password>123</password>'
    ...                   '  </default>'
    ...                   '  <viresLogin>'
    ...                   '    <username>John</username>'
    ...                   '    <password>Doe</password>'
    ...                   '  </viresLogin>'
    ...                   '  <trouble>'
    ...                   '    <username>snowflake</username>'
    ...                   '    <password>unique</password>'
    ...                   '  </trouble>'
    ...                   '</xml>',
    ...                   'globus')
    {'username': 'admin', 'password': '123'}
    
    Note
    ----
    Using build_file will generate a valid xml structure,
    containing only the default tag and subtags.
    """
    # """ This will find the login information under target
    # in the given xml text.
    # If target is not found, then default may be used instead.
    # """
    root = ET.fromstring(text)
    place = root.find(target)
    if place is None:
        place = root.find('default')
    return {elem.tag: elem.text for elem in place}
    

def build_default_XML(default_login=None):
    """ Build a xml based string with default login settings.
    
    This function creates a string of XML, which contains
    default login settings, which can then be read
    by find_login_in_XML or saved to a file.
    It is recommened to have this information encrypted,
    such as by using box_content on it.
    
    Parameters
    ----------
    default_login : tuple of two strings, optional
        A tuple of form (username, password), which is used
        as the default login informaion recorded in the xml string.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
    
    Returns
    -------
    str
        A string representing an xml file, which contains
        default login settings and would work for `find_login_in_XML`.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> build_default_XML(('nimda', 'tapas')) # doctest: +ELLIPSIS
    '<?xml version="1.0"?>...<xml>...<default>...<username>nimda</username>...<password>tapas</password>...</default>...</xml>...'
    """
    if default_login is None:
        (user, password) = prompt_login_data()
    else:
        (user, password) = default_login
    content = """<?xml version="1.0"?>
<xml>
    <default>
        <username>""" + user + """</username>
        <password>""" + password + """</password>
    </default>
</xml>
"""
    return content  # Easier to see where the function ends this way.


def box_content(text, password=None):
    """ Package text into encrypted cypther-text with meta-data.
    
    This function 'box' the text as an AES encrympted dump.
    It takes care of all the needed substeps, including
    padding, choosing initial vector, encryption, and storing meta-data.
    
    Parameters
    ----------
    text : str
        A string of plain text.
    password : str, optional
        The password used to construct the key for the encryption.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
    
    Returns
    -------
    str
        A binary string containing the encrypted text, initial vector,
        and other meta-data which is hidden under the encryption.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> box_content('There is no cake', 'beware of goats') # doctest: +ELLIPSIS
    b'...'
    """
    # """ The text is 'boxed' as a encrypted dump.
    # boxing includes padding the message and including
    # the meta-data needed to undo the process.
    # If password is not given the user will be prompted for one.
    # """
    IV = ''.join(str(random.choice(string.hexdigits)) for __ in range(16))
    boxed = encrypt(add_padding(text), password, IV)
    return IV.encode('utf-8') + boxed


def unbox_content(boxed, password=None):
    """ Retrive text from cyper-text from box_content.
    
    This function takes some text that have been 'boxed'
    as an AES encrypted dump, and revert back into the original test.
    It takes care of all the needed substeps, including
    removing padding, extracting meta-data and decryption.
    
    Parameters
    ----------
    boxed : str
        A string of binary text, representing a result from box_content.
    password : str, optional
        The password used to construct the key for the decryption.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
    
    Returns
    -------
    str
        A string representing the decrypted and unpadded text.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> cipher = box_content('send the rover', 'once in a blue moon')
    >>> unbox_content(cipher, 'once in a blue moon')
    'send the rover'
    """
    # """ Retrive the content of a 'boxed' text.
    # This is functionally the inverse of box_content.
    # If password is not given the user will be prompted for one.
    # """
    decrypted = decrypt(boxed[16:], password, boxed[0:16])
    return remove_padding(decrypted)


def lock_file(filename, password=None):
    """ Replace a file with a boxed version of its content.
    
    This function reads the file at the path `filename`,
    box the content and write the result back over the file.
    
    Parameters
    ----------
    filename : str
        A string of the path to the file, including its name.
    password : str, option
        The password used to construct the key for the encryption.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
        
    Returns
    -------
    None
        There is no return statement, this results in a None.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> lock_file('some.xml','gatekeeper') # doctest: +SKIP
    """
    # """ Replace a file of filename with
    # the boxed version of its content.
    # If password is not given the user will be prompted for one.
    # """
    with open(filename, 'r') as f:
        content = f.read()
    out = box_content(content, password)
    with open(filename, 'wb') as f:
        f.write(out)


def build_file(filename, password=None, default_login=None):
    """ Construct a locked xml file which include a default loging.
    
    This function is used to construct a defaulted boxed xml file.
    This can be used with fetch_loging, or unboxed with unlock file.
    The content of the file, after unboxing can be used with
    find_login_in_XML.
    
    Parameters
    ----------
    filename : str
        A string of the path to the file, including its name.
    password : str, optional
        The password used to construct the key for the encryption.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
    default_login : tuple of two strings, optional
        A tuple of form (username, password), which is used
        as the default login informaion recorded in the xml file.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
        
    Returns
    -------
    None
        There is no return statement, this results in a None.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> build_file('example.xml', 'welcome', ('blank', 'stare')) # doctest: +SKIP
    """
    """ Construct a boxed (encrypted with metadata) file
    of filename, the content will include default login
    information, which the user will be prompted for.
    If password for the file is not given the user will be prompted for one.
    """
    # if default_login is None:
        # (user, password) = prompt_login_data()
    # else:
        # (user, password) = default_login
    # content = """<?xml version="1.0"?>
# <xml>
    # <default>
        # <username>""" + user + """</username>
        # <password>""" + password + """</password>
    # </default>
# </xml>
# """
    out = box_content(build_default_XML(default_login))
    with open(filename, 'wb') as f:
        f.write(out)


def fetch_login(filename, target='viresLogin', password=None):
    """ Fetch information from a locked file.
    
    This function peaks into an encrypted file and retrievs
    login like information from it, without leaving the file unencrypted.
    Specifically it uses files that have been locked,
    meaning it has boxed content.
    It is assumed that the content after unboxing will form a valid
    xml structure, that find_login_in_XML can be applied to.
    
    This function is intended to be used as a top level abstraction,
    of aquiring login information in other modules.
    
    Parameters
    ----------
    filename : str
        A string of the path to the file, including its name.
    target : str, optional
        A string representing the xml tag where the data
        we want is stored under.
        If this tag does not exists we will get the data stored
        uder the tag 'default' instead.
        Default is 'viresLogin'.
    password : str, optional
        The password used to construct the key for the decryption.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
        
    Returns
    -------
    None
        There is no return statement, this results in a None.
    
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> fetch_login('example.xml', 'welcome') # doctest: +SKIP
    {'username': 'blank', 'password': 'stare'}
    """
    # """ Peek into an encrypted file of filename,
    # and extract login information on the given target (with default).
    # If password for the file is not given the user will be prompted for one.
    # If the file does not exist then a valid file may be constructed
    # based on input from the user.

    # Note that this is the main functionally expected to be used outside,
    # since it can buildup the necessary structure
    # by just including this function,
    # and not manually having to set up the rest.
    # """
    if not os.path.isfile(filename):
        print('The target file: ' + filename
              + ' do not exist yet, constructing it now...')
        build_file(filename, password)
    with open(filename, 'rb') as f:
        text = f.read()
    return find_login_in_XML(unbox_content(text, password), target)


def unlock_file(filename, password=None):
    """ Replace a file with an unboxed version of its content.

    This function reads the file at the path `filename`,
    unbox the content and write the result back over the file.
    
    Parameters
    ----------
    filename : str
        A string of the path to the file, including its name.
    password : str, option
        The password used to construct the key for the decryption.
        If it is not specified as a parameter,
        then the user will be prompted to choose one during runtime.
        
    Returns
    -------
    None
        There is no return statement, this results in a None.
        
    Examples
    --------
    >>> from pyfac.safety import *  # doctest: +SKIP
    >>> unlock_file('some.xml','gatekeeper') # doctest: +SKIP
    """
    # """ Replace a file of filename with
    # the unboxed version of its content.
    # If password is not given the user will be prompted for one.
    # """
    with open(filename, 'rb') as f:
        content = f.read()
    out = unbox_content(content, password)
    with open(filename, 'w') as f:
        f.write(out)


if __name__ == '__main__':
    # Test docstrings
    import doctest
    doctest.testmod()
