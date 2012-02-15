'''
======================
`gsk` module
======================

A module which wraps calls to gsk7cmd, an IBM Websphere utility for creating and editing PKI certificate stores.

gsk7cmd is used to create and manipulate security certificates and certificate databases.
It takes two required parameters (an `object` and an `action`) and multiple
optional parameters which depend on both object and action. Objects and actions are shown below:

+----------+---------------+-----------------------------------------------------------------------------------------------+
|  Object  |     Action    |      Description                                                                              |
+----------+---------------+-----------------------------------------------------------------------------------------------+
| -keydb   | -changepw     | Change the password for a key database                                                        |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -convert      | Convert the format of a key database                                                          |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -create       | Create a key database                                                                         |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -delete       | Delete a key database                                                                         |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -expiry       | Display password expiry                                                                       |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -stashpw      | Stash the password of a key database into a file                                              |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -list         | Currently supported types of key database.                                                    |
+----------+---------------+-----------------------------------------------------------------------------------------------+
| -cert    | -add          | Add a CA Certificate                                                                          |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -create       | Create a self-signed certificate                                                              |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -delete       | Delete a certificate                                                                          |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -details      | Show the details of a specific certificate                                                    |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -export       | Export a personal certificate and associated private key into a PKCS12 file or a key database |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -extract      | Extract a certificate from a key database                                                     |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -getdefault   | Show the default personal certificate                                                         |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -import       | Import a certificate from a key database or a PKCS12 file                                     |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -list         | List certificates in a key database                                                           |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -modify       | Modify a certificate (NOTE: the only field that my be modified is the trust field)            |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -receive      | Receive a certificate                                                                         |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -setdefault   | Set the default personal certificate                                                          |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -sign         | Sign a certificate                                                                            |
+----------+---------------+-----------------------------------------------------------------------------------------------+
| -certreq | -create       | Create a certificate request                                                                  |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -delete       | Delete a certificate request from a keystore                                                  |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -details      | Show the details of a specific certificate request                                            |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -extract      | Extract a certificate from a keystore                                                         |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -list         | List all certificate requests in a keystore                                                   |
|          +---------------+-----------------------------------------------------------------------------------------------+
|          | -recreate     | Recreate a certificate request                                                                |
+----------+---------------+-----------------------------------------------------------------------------------------------+
| -version |               | Display ikeycmd version information                                                           |
+----------+---------------+-----------------------------------------------------------------------------------------------+
| -help    |               | Display this help text                                                                        |
+----------+---------------+-----------------------------------------------------------------------------------------------+

The gsk module encapsulates a subset of the gsk7cmd commands as obviously-named functions
eg. keydb_create(), cert_add() etc.  There is also a convenience class, KeyDataBase, with
methods paralleling these functions, and a generic `call` function for calling gsk7cmd
with options not currently exposed by the API.

NOTE: Calls to gsk7cmd are slow, be prepared to wait for things to happen.

============
Usage
============

Create a keystore.

.. sourcecode:: python

    >>> keyfile = "test.kdb"
    >>> pwd = "password"
    >>> dbtype = "cms"
    >>> db = KeyDataBase(keyfile, pwd, dbtype)
    >>> import os
    >>> if os.path.exists(keyfile):
    ...     db.delete()
    ...
    >>> os.path.exists(keyfile)
    False
    >>> db.create()
    >>> os.path.exists(keyfile)
    True

Change the password
    
.. sourcecode:: python

    >>> db.change_password('newpw')
    >>> db.password
    newpw

Delete existing certificates

.. sourcecode:: python

    >>> certs = db.get_cert_list()
    >>> for cert in certs:
    ...     db.delete_cert(cert)
    ...
    >>> certs = db.get_cert_list()
    >>> len(certs) == 0
    True

Create a self-signed certificate

.. sourcecode:: python

    >>> db.create_cert("TEST CERT", "CN=Test, O=Euroclear, C=BE")
    >>> certs = db.get_cert_list()
    >>> len(certs) == 1
    True
    >>> id = db.get_cert_fingerprint("TEST CERT")
    >>> len(id) > 0
    True

Extract a certificate

.. sourcecode:: python

    >>> testfile = "test.cer"
    >>> if os.path.exists(testfile):
    ...     os.remove(testfile)
    ...
    >>> os.path.exists(testfile)
    False
    >>> db.extract_cert("TEST CERT", testfile, 'ascii')
    >>> os.path.exists(testfile)
    True
    >>> db.delete()
    >>> os.path.exists("test.kdb")
    False

'''
import os
from itsalib.command import shell, ExternalCommandException
import itsalib.logger as log

__docformat__ = "restructuredtext en"
__author__ = "Gerard Flanagan <gerard.flanagan@euroclear.com>"

__all__ = [
        'call', 'KeyDataBase',
        'cert_list', 'cert_add', 'cert_create', 'cert_delete',
        'cert_receive', 'cert_details', 'cert_extract',
        'certreq_create', 
        'keydb_create', 'keydb_delete', 'keydb_changepw',
        ]

__doc_all__ = __all__

def _build_command(obj, action, **params):
    '''
    A helper for the `call` function.
    '''
    cmdline = 'gsk7cmd -%s -%s' % (obj, action)
    for key, val in params.iteritems():
        if val in [None, False, '']:
            continue
        else:
            if key.endswith('_'):
                #file and type are valid parameters for gsk7cmd but
                #these are builtin functions in Python, so using an
                #appended underscore and removing it here
                key = key[:-1]
            cmdline += ' -%s' % key
            if val is True:
                continue
            else: #val is an actual value
                cmdline += ' \"%s\"' % val
    return cmdline

def call(obj, action, **params):
    '''
    Call `gsk7cmd` using `shell` from the `itsalib.command` module.

    * obj: One of the following - ['keydb', 'cert', 'certreq']
    * action: See gsk7cmd help.
    * params: See gsk7cmd help.
    '''
    return shell(_build_command(obj, action, **params))

#############################################################
#
# Commands for dealing with Certificates
#
#############################################################

def cert_list(db, pw):
    '''
    List all certificates in a keystore file.
    '''
    try:
        certs = call('cert', 'list', **locals())
        return [line.strip() for line in certs[1:] if line.strip()]
    except ExternalCommandException:
        return []

def cert_delete(db, pw, label):
    '''
    Delete a certificate from a keystore file.
    '''
    call('cert', 'delete', **locals())

def cert_add(db, pw, file_, label, format, trust=False):
    '''
    Add a certificate to a keystore file.
    '''
    call('cert', 'add', **locals())

def cert_receive(db, pw, file_, type_, format):
    '''
    Import a certificate into a keystore file.
    '''
    call('cert', 'receive', **locals())

def cert_details(db, pw, label, type_):
    '''
    Print the details of the certificate with the given label.
    '''
    return call('cert', 'details', **locals())

def cert_extract(db, pw, label, type_, target, format):
    '''
    Export a certificate from a keystore.
    '''
    call('cert', 'extract', **locals())

def cert_create(db, pw, label, dn, size=512):
    '''
    Export a certificate from a keystore.
    '''
    call('cert', 'create', **locals())

#############################################################
#
# Commands for dealing with Certificate Requests
#
#############################################################

def certreq_create(db, pw, file_, label, dn, size):
    '''
    Create a certificate request.
    '''
    call('certreq', 'create', **locals())

#############################################################
#
# Commands for dealing with Key Stores
#
#############################################################

def keydb_create(db, pw, type_, stash=False):
    '''
    Create a keystore file.
    '''
    call('keydb', 'create', **locals())

def keydb_delete(db, pw):
    '''
    Delete a keystore file.
    '''
    call('keydb', 'delete', **locals())

def keydb_changepw(db, pw, new_pw, expire=None, stash=None):
    '''
    Change a keystore password
    '''
    call('keydb', 'changepw', **locals())

#############################################################
#
# Convenience classes and methods
#
#############################################################

class KeyDataBase(object):
    '''
    A facade to the other functions in this module.

    In the case where there are numerous actions applied to the same
    keyfile, this class saves having to retype the keyfile name, type
    and password.
    '''
    def __init__(self, filepath, password, dbtype):
        self.dbfilepath = filepath
        self.password = password
        self.dbtype = dbtype
        self.basename = os.path.basename(filepath)

    def create(self):
        args = [self.dbfilepath, self.password, self.dbtype]
        if self.dbtype == 'cms':
            args.append(True)
        keydb_create(*args)

    def delete(self):
        keydb_delete(self.dbfilepath, self.password)

    def get_cert_list(self):
        return cert_list(self.dbfilepath, self.password)

    def get_cert_details(self, label):
        details = cert_details(self.dbfilepath, self.password, label, self.dbtype)
        return [line.strip() for line in details if line.strip()]

    def get_cert_fingerprint(self, label):
        name = "Fingerprint: "
        for line in self.get_cert_details(label):
            if line.startswith(name):
                return line[len(name):]
        return ''

    def add_cert(self, filepath, label, format):
        args = [self.dbfilepath, self.password, filepath, label, format]
        if self.dbtype == 'cms':
            args.append('enable')
        cert_add(*args)

    def delete_cert(self, label):
        cert_delete(self.dbfilepath, self.password, label)

    def create_cert_request(self, req_filepath, label, dn, size=1024):
        certreq_create(self.dbfilepath, self.password, req_filepath, label, dn, size)

    def receive_cert(self, cert_filepath, format):
        cert_receive(self.dbfilepath, self.password, cert_filepath, self.dbtype, format)

    def extract_cert(self, label, target, format):
        cert_extract(self.dbfilepath, self.password, label, self.dbtype, target, format)

    def create_cert(self, label, dn):
        cert_create(self.dbfilepath, self.password, label, dn)

    def change_password(self, new_pw, expire=None, stash=None):
        keydb_changepw(self.db, self.password, new_pw, expire, stash)
        self.password = new_pw

if __name__ == '__main__':
    import doctest
    doctest.testmod()
