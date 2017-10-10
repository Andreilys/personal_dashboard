#!/usr/bin/env python
"""
A Pythonic interface to Amazon's S3 web service.

Copyright (C) 2006 Mitch Garnaat <mitch@garnaat.org>

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
"""
import md5
import s3amazon.S3
import httplib
import urllib
import ConfigParser
import os
import string
import mimetypes
import xml.sax
import pdb

#
# Canned Access Policies
#
_canned_access_policies = ('private', 'public-read',
                           'public-read-write', 'authenticated-read')
#
# Dictionary mapping mime types to content filters
#
_content_filter_map = {}

def add_content_filter(content_type, filter):
    _content_filter_map[content_type] = filter
    filter.content_type = content_type

def get_content_filter(content_type):
    if _content_filter_map.has_key(content_type):
        return _content_filter_map[content_type]
    else:
        return None

def remove_content_filter(content_type):
    del _content_filter_map[content_type]

def filter_bits(bits):
    filter = get_content_filter(bits.content_type)
    if filter:
        filter.filter(bits)

class ContentFilter:

    def __init__(self):
        self.content_type = None

    def filter(self, bits):
        print 'filter[%s] - filtering %s' % (self.content_type, bits.filename)


class BBHeadResponse(s3amazon.S3.GetResponse):
    
    def __init__(self, http_response):
        self.http_response = http_response
        response_headers = http_response.msg   # older pythons don't have getheaders
        self.metadata = self.get_aws_metadata(response_headers)
        # Need to read the body even though we now it's not there
        if http_response.status == 200:
            http_response.read()
        else:
            # -- gross hack --
            # httplib gets confused with chunked responses to HEAD requests
            # so I have to fake it out
            http_response.chunked = 0
            http_response.read()

class BBListBucketResponse(s3amazon.S3.Response):
    def __init__(self, http_response):
        s3amazon.S3.Response.__init__(self, http_response)
        if http_response.status < 300:
            handler = BBListBucketHandler()
            xml.sax.parseString(self.body, handler)
            self.entries = handler.entries
            self.is_truncated = handler.is_truncated
        else:
            self.entries = []

class BBListBucketHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.entries = []
        self.curr_entry = None
        self.curr_text = ''

    def startElement(self, name, attrs):
        if name == 'Contents':
            self.curr_entry = Bits()
        elif name == 'Owner':
            self.curr_entry.owner = s3amazon.S3.Owner()

    def endElement(self, name):
        if name == 'Contents':
            self.entries.append(self.curr_entry)
        elif name == 'Key':
            self.curr_entry.key = self.curr_text
        elif name == 'LastModified':
            self.curr_entry.last_modified = self.curr_text
        elif name == 'ETag':
            self.curr_entry.etag = self.curr_text
        elif name == 'Size':
            self.curr_entry.size = int(self.curr_text)
        elif name == 'ID':
            self.curr_entry.owner.id = self.curr_text
        elif name == 'DisplayName':
            self.curr_entry.owner.display_name = self.curr_text
        elif name == 'StorageClass':
            self.curr_entry.storage_class = self.curr_text
        elif name == 'IsTruncated':
            self.is_truncated = self.curr_text

        self.curr_text = ''

    def characters(self, content):
        self.curr_text += content

#
# Exception classes - Subclassing allows you to check for specific errors
#
class BitBucketError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __repr__(self):
        return 'BitBucketError: %s' % self.reason

    def __str__(self):
        return 'BitBucketError: %s' % self.reason

class BitBucketResponseError(BitBucketError):
    def __init__(self, status, reason):
        BitBucketError.__init__(self, reason)
        self.status = status
        self.reason = reason

    def __repr__(self):
        return 'BitBucketError[%d]: %s' % (self.status, self.reason)

    def __str__(self):
        return 'BitBucketError[%d]: %s' % (self.status, self.reason)

class BitBucketTypeError(BitBucketError):
    pass

class BitBucketEmptyError(BitBucketError):
    pass

class BitBucketDataError(BitBucketError):
    pass

class BitBucketCreateError(BitBucketResponseError):
    pass

# State Constants
BITS_LOOSE=0      # Bits object not yet associated with a BitBucket object
BITS_NEED_READ=1  # data in the Bits object needs to be read from S3
BITS_NEED_WRITE=2 # data in the Bits object needs to be written to S3
BITS_IN_SYNC=3    # data in the Bits object is consistent with S3

class Bits(s3amazon.S3.S3Object):

    def __init__(self, filename=None):
        self.state = BITS_LOOSE
        self.metadata = {}
        self.bucket = None
        self.content_type = 'application/octet-stream'
        self.filename = filename
        self.etag = None
        self.key = None
        self.last_modified = None
        self.owner = None
        self.storage_class = None

    def __getattr__(self, name):
        if name == 'data':
            if self.state == BITS_NEED_READ:
                if self.bucket:
                    self.bucket.get_bits(self)
            return self._data
        elif name in self.metadata:
            return self.metadata[name]
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        if name == 'data':
            self._data = value
            if value:
                self.__dict__['size'] = len(value)
            if self.bucket:
                self.bucket.send_bits(self)
        elif name == 'filename':
            self.__dict__[name] = value
            if value:
                self.sync()
        else:
            self.__dict__[name] = value

    def __getitem__(self, key):
        return self.metadata[key]

    def __setitem__(self, key, value):
        self.metadata[key] = value

    def __delitem__(self, key):
        del self.metadata[key]

    def _compute_md5(self):
        m = md5.new()
        p = open(self.filename, 'rb')
        s = p.read(8192)
        while s:
            m.update(s)
            s = p.read(8192)
        self.md5 = '"%s"' % m.hexdigest()
        p.close()

    def sync(self):
        if self.filename:
            if os.path.exists(self.filename):
                self.size = os.stat(self.filename).st_size
                self._compute_md5()
                self.content_type = mimetypes.guess_type(self.filename)[0]
                filter_bits(self)
                self.state = BITS_NEED_WRITE
                if self.bucket:
                    self.bucket.send_file(self)
            else:
                self.state = BITS_NEED_READ
                if self.bucket:
                    self.bucket.get_file(self, self.filename)
        else:
            self.state = BITS_NEED_WRITE
            self.bucket.send_bits(self)

    def get_url(self, expires_in=60):
        if self.bucket:
            return self.bucket.generate_url('get', self, expires_in)
        else:
            raise BitBucketError("Bits aren't associated with a BitBucket yet")

    def delete_url(self, expires_in=60):
        if self.bucket:
            return self.bucket.generate_url('delete', self, expires_in)
        else:
            raise BitBucketError("Bits aren't associated with a BitBucket yet")

    def set_canned_acl(self, policy):
        if policy not in _canned_access_policies:
            raise BitBucketError('Invalid acl_policy: %s' % policy)
        self.bucket.connection.set_canned_acl(self, policy)

    def get_acl(self):
        return self.bucket.connection.get_acl(self)

    def to_file(self, filename):
        if self.bucket != None:
            self.bucket.get_file(self, filename)
        else:
            raise BitBucketError("Bits aren't associated with a BitBucket yet")

def BitBucketGenerator(bucket):
    bucket.options['max-keys'] = bucket.page_size
    finished = False
    last_key = None
    while not finished:
        if last_key:
            bucket.options['marker'] = last_key
        resp = bucket.connection.list_bucket(bucket.name, bucket.options)
        if resp.http_response.status == 200:
            for b in resp.entries:
                b.state = BITS_NEED_READ
                b.bucket = bucket
                key = bucket.get_local_key(b.key)
                b.key = key
                last_key = key
                yield b
            if resp.is_truncated != 'true':
                finished = True
        else:
            raise BitBucketResponseError(resp.http_response.status,
                                         resp.http_response.reason)

class BitBucket:

    def __init__(self, name, connection, prefix=None,
                 page_size=100, debug=None):
        self.options = {}
        self.connection = connection
        if prefix:
            self.options['prefix'] = prefix
        self.page_size = page_size
        self.debug = debug
        self.name = self.connection.bucket_name_prefix + name
        self._cache = {}

    def get_head(self, key):
        self._resp = self.connection.head(self.name, key)
        if self._resp.http_response.status == 200:
            bits = Bits()
            bits.bucket = self
            bits.metadata = self._resp.metadata
            http_resp = self._resp.http_response
            bits.etag = http_resp.getheader('etag')
            bits.content_type = http_resp.getheader('content-type')
            bits.last_modified = http_resp.getheader('last-modified')
            bits.state = BITS_NEED_READ
            self._cache[key] = bits
            bits.key = key
            return bits
        elif self._resp.http_response.status == 404:
            return None
        else:
            raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)

    def fetch_all_keys(self, last_key=None):
        if last_key:
            self.options['marker'] = last_key
        self._resp = self.connection.list_bucket(self.name, self.options)
        if self._resp.http_response.status == 200:
            for b in self._resp.entries:
                b.state = BITS_NEED_READ
                b.bucket = self
                key = self.get_local_key(b.key)
                b.key = key
                self._cache[b.key] = b
                last_key = key
            if self._resp.is_truncated == 'true':
                if self.debug:
                    print '__list__: getting next page - last_key=%s' % last_key
                self.fetch_all_keys(last_key)
        else:
            raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)
            
    def delete_all_keys(self):
        self.options['max-keys'] = self.page_size
        finished = False
        last_key = None
        while not finished:
            if last_key:
                self.options['marker'] = last_key
            resp = self.connection.list_bucket(self.name, self.options)
            if resp.http_response.status == 200:
                for b in resp.entries:
                    key = b.key
                    last_key = key
                    if self.debug:
                        print '[delete_all_keys]: deleting %s' % key
                    self._resp = self.connection.delete(self.name,
                                                        self.get_aws_key(key))
                    if self._resp.http_response.status != 204:
                        raise BitBucketResponseError(self._resp.http_response.status,
                                                     self._resp.http_response.reason)
                if resp.is_truncated != 'true':
                    finished = True
            else:
                raise BitBucketResponseError(resp.http_response.status,
                                             resp.http_response.reason)
                
    def get_acl(self):
        return self.connection.get_acl(self)

    def set_canned_acl(self, policy):
        if policy not in _canned_access_policies:
            raise BitBucketError('Invalid acl_policy: %s' % policy)
        self.connection.set_canned_acl(self, policy)

    def __repr__(self):
        return 'BitBucket(%s)' % self.name

    def __len__(self):
        return len(self._cache.keys())

    def __getitem__(self, key):
        if self._cache.has_key(key):
            return self._cache[key]
        bits = self.get_head(key)
        if bits:
            return bits
        else:
            raise KeyError(key)

    def __setitem__(self, key, bits):
        bits.key = key
        bits.bucket = self
        if bits.filename:
            self.send_file(bits)
        else:
            self.send_bits(bits)
        self._cache[bits.key] = bits

    def __delitem__(self, key):
        del self._cache[key]
        self._resp = self.connection.delete(self.name,
                                               self.get_aws_key(key))
        if self._resp.http_response.status != 204:
            raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)

    def __contains__(self, item):
        if item in self._cache:
            return True
        if self.get_head(key):
            return True
        else:
            return False

    def __iter__(self):
        return BitBucketGenerator(self)

    def get_local_key(self, key):
        if self.options.has_key('prefix'):
            return key[len(self.options['prefix']):]
        else:
            return key

    def get_aws_key(self, key):
        if self.options.has_key('prefix'):
            return self.options['prefix'] + key
        else:
            return key

    def generate_url(self, request, bits=None, expires_in=60):
        if bits:
            if not isinstance(bits, Bits):
                raise BitBucketTypeError('Value must be of type Bits')
        self.connection.query_gen.set_expires_in(expires_in)
        if request == 'get':
            return self.connection.query_gen.get(self.name, bits.key)
        elif request == 'delete':
            return self.connection.query_gen.delete(self.name, bits.key)
        else:
            raise BitBucketError('Invalid request: %s' % request)

    def send_bits(self, bits):
        if not isinstance(bits, Bits):
            raise BitBucketTypeError('Value must be of type Bits')
        if not bits.data:
            raise BitBucketEmptyError("Can't write empty Bits to S3")
        etag = '"%s"' % md5.new(bits.data).hexdigest()
        # compare the hash of current data to etag on Bits object
        #   if they are the same, there is no need to send data to S3
        if etag != bits.etag:
            if self.debug:
                print '[send_bits] sending %s' % bits.key
            headers = {'ETag':etag}
            if bits.content_type:
                headers['Content-Type'] = bits.content_type
            self._resp = self.connection.put(self.name,
                                                self.get_aws_key(bits.key),
                                                bits, headers)
            if self._resp.http_response.status != 200:
                raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)
            if etag != self._resp.http_response.getheader('etag'):
                raise BitBucketDataError("ETags don't match")
        else:
            if self.debug:
                print '[send_bits] skipping %s' % bits.key
        bits.etag = etag
        bits.size = len(bits.data)
        bits.state = BITS_IN_SYNC

    def send_file(self, bits):
        if not isinstance(bits, Bits):
            raise BitBucketTypeError('Value must be of type Bits')
        # compare the hash of current data to etag on Bits object
        #   if they are the same, there is no need to send data to S3
        if bits.etag != bits.md5:
            if self.debug:
                print '[send_file] sending %s' % bits.key
            headers = {'ETag':bits.md5}
            if bits.content_type:
                headers['Content-Type'] = bits.content_type
            self._resp = self.connection.put_file(bits, headers)
            if self._resp.http_response.status != 200:
                raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)
            bits.etag = self._resp.http_response.getheader('etag')
            if bits.etag != bits.md5:
                raise BitBucketDataError("ETags don't match")
        else:
            if self.debug:
                print '[send_file] skipping %s' % bits.key
        bits.state = BITS_IN_SYNC

    def get_bits(self, bits):
        if not isinstance(bits, Bits):
            raise BitBucketTypeError('Value must be of type Bits')
        if bits.bucket != self:
            raise BitBucketError('Those are not my Bits')
        if self.debug:
            print '[get_bits] getting %s' % bits.key
        self._resp = self.connection.get(self.name,
                                            self.get_aws_key(bits.key))
        if self._resp.http_response.status == 200:
            bits._data = self._resp.object.data
            bits.metadata = self._resp.object.metadata
            bits.state = BITS_IN_SYNC
        else:
            raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)
        
    def get_file(self, bits, filename):
        if not isinstance(bits, Bits):
            raise BitBucketTypeError('Value must be of type Bits')
        if self.debug:
            print '[get_file] getting %s' % bits.key
        self._resp = self.connection.get_file(bits, filename)
        if self._resp.status != 200:
            raise BitBucketResponseError(self._resp.status,
                                         self._resp.reason)
        #bits.etag = self._resp.getheader('etag')
        bits.state = BITS_IN_SYNC

    def keys(self):
        return self._cache.keys()

    def values(self):
        return self._cache.values()

    def items(self):
        return self._cache.items()

    def has_key(self, key):
        if self._cache.has_key(key):
            return True
        if self.get_head(key):
            return True
        else:
            return False

#
# You have a couple of choices for getting your individual keys in.
#   1. You could pass them to the bitbucket connect method
#   2. You could add them to this dictionary
#   3. You could place them in a file called bitbucket.cfg and put that
#      file in either your home directory or in the directory you are
#      running the code in.  The file needs to look like this:
#-------------------------------------------------------
#      [DEFAULT]
#      AccessKeyID: YourAccessKeyHere
#      SecretAccessKey: YourSecretAccessKeyHere
#      Debug: 1
#-------------------------------------------------------
BB_DEFAULTS = {'AccessKeyID': '',
               'SecretAccessKey': '',
               'BucketNamePrefix': '',
               'PageSize': '100',
               'Debug': '0'}

#
# Just wanted to subclass to include an implementation of HEAD
#
class BBConnection(s3amazon.S3.AWSAuthConnection):

    BufferSize=1024

    def __init__(self, access_key=None, secret_key=None,
                 is_secure=True, server=s3amazon.S3.DEFAULT_HOST, port=None,
                 bucket_name_prefix=None, page_size=None):
        self._buckets = {}
        # check to see if there is a bitbucket.cfg file
        # if so, we use those values unless values are passed to constructor
        self.config = ConfigParser.ConfigParser(BB_DEFAULTS)
        self.config.read(['./bitbucket.cfg',
                          os.path.expanduser('~/bitbucket.cfg')])
        if access_key:
            self.access_key = access_key
        else:
            self.access_key = self.config.get(ConfigParser.DEFAULTSECT,
                                              'AccessKeyID')
        if secret_key:
            self.secret_key = secret_key
        else:
            self.secret_key = self.config.get(ConfigParser.DEFAULTSECT,
                                              'SecretAccessKey')
        if bucket_name_prefix:
            self.bucket_name_prefix = bucket_name_prefix
        else:
            self.bucket_name_prefix = self.config.get(ConfigParser.DEFAULTSECT,
                                                      'BucketNamePrefix')
        if page_size:
            self.page_size = page_size
        else:
            self.page_size = self.config.getint(ConfigParser.DEFAULTSECT,
                                                'PageSize')
        self.debug = self.config.getint(ConfigParser.DEFAULTSECT,
                                        'Debug')
        s3amazon.S3.AWSAuthConnection.__init__(self, self.access_key,
                                               self.secret_key, is_secure,
                                               server, port)
        # if debug>1 then turn on httplib debug as well
        if self.debug > 1:
            self.connection.debuglevel = self.debug
        self.query_gen = s3amazon.S3.QueryStringAuthGenerator(self.access_key,
                                                              self.secret_key)
        self.get_all_buckets()
    
    def __len__(self):
        return len(self._buckets.keys())

    def __getitem__(self, key):
        if self._buckets.has_key(key):
            return self._buckets[key]
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        del self._buckets[key]
        self._resp = self.delete_bucket(self.name)
        if self._resp.http_response.status != 204:
            raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)

    def __contains__(self, item):
        if item in self._buckets:
            return True
        else:
            return False

    def keys(self):
        return self._buckets.keys()

    def values(self):
        return self._buckets.values()

    def items(self):
        return self._buckets.items()

    def has_key(self, key):
        if self._buckets.has_key(key):
            return True
        else:
            return False
        
    def head(self, bucket, key, headers={}):
        return BBHeadResponse(
            self.make_request('HEAD', '%s/%s' % (bucket, urllib.quote_plus(key)), headers))

    #
    # This method mainly stolen from Emanuele Ruffaldi's S3 Tool
    #
    def put_file(self, bits, headers={}):
        if not isinstance(bits, Bits):
            raise BitBucketTypeError('Must pass Bits to put_file')
        final_headers = s3amazon.S3.merge_meta(headers, bits.metadata);
        path = '%s/%s' % (bits.bucket.name, urllib.quote_plus(bits.key))
        self.add_aws_auth_header(final_headers, 'PUT', path)
        self.connection.putrequest('PUT','/'+path)
        final_headers["Content-Length"] = bits.size
        for key in final_headers:
            self.connection.putheader(key,final_headers[key])
        self.connection.endheaders()
        file = open(bits.filename, 'rb')
        l = file.read(self.BufferSize)
        while len(l) > 0:
            self.connection.send(l)
            l = file.read(self.BufferSize)
        file.close()
        return s3amazon.S3.Response(self.connection.getresponse())

    def get_file(self, bits, filename, headers={}):
        if not isinstance(bits, Bits):
            raise BitBucketTypeError('Must pass Bits to get_file')
        final_headers = s3amazon.S3.merge_meta(headers, bits.metadata);
        path = '%s/%s' % (bits.bucket.name, urllib.quote_plus(bits.key))
        self.add_aws_auth_header(final_headers, 'GET', path)
        self.connection.putrequest('GET','/'+path)
        for key in final_headers:
            self.connection.putheader(key,final_headers[key])
        self.connection.endheaders()
        resp = self.connection.getresponse()
        response_headers = resp.msg
        for key in response_headers.keys():
            if key.lower().startswith(s3amazon.S3.METADATA_PREFIX):
                bits[key[len(s3amazon.S3.METADATA_PREFIX):]] = response_headers[key]
                del response_headers[key]
            elif key.lower() == 'content-length':
                bits.size = response_headers[key]
            elif key.lower() == 'etag':
                bits.etag = response_headers[key]
        file = open(filename, 'wb')
        l = resp.read(self.BufferSize)
        while len(l) > 0:
            file.write(l)
            l = resp.read(self.BufferSize)
        file.close()
        resp.read()
        return resp

    def list_bucket(self, bucket, options={}, headers={}):
        path = bucket
        if options:
            path += '?' + '&'.join(["%s=%s" % (param, urllib.quote_plus(str(options[param]))) for param in options])

        return BBListBucketResponse(self.make_request('GET', path, headers))

    def get_all_buckets(self):
        r = self.list_all_my_buckets()
        for entry in r.entries:
            b = BitBucket(entry.name, self,
                          page_size=self.page_size, debug=self.debug)
            self._buckets[entry.name] = b

    def get_bucket(self, bucket_name, prefix=None, fetch_keys=False):
        if bucket_name in self._buckets.keys():
            return self._buckets[bucket_name]
        self._resp = self.create_bucket(bucket_name)
        status = self._resp.http_response.status
        if status == 409:
            raise BitBucketCreateError(self._resp.http_response.status,
                                       self._resp.http_response.reason)
        if status == 200:
            b = BitBucket(bucket_name, self,
                          page_size=self.page_size, debug=self.debug)
            self._buckets[bucket_name] = b
            if fetch_keys:
                b.fetch_all_keys()
            return b
        else:
            raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)

    def delete_bucket(self, bucket_name):
        self._resp = s3amazon.S3.AWSAuthConnection.delete_bucket(self, bucket_name)
        status = self._resp.http_response.status
        if status == 204:
            if bucket_name in self._buckets.keys():
                del self._buckets[bucket_name]
        else:
            raise BitBucketResponseError(self._resp.http_response.status,
                                         self._resp.http_response.reason)

    def get_acl(self, b):
        if isinstance(b, Bits):
            b_name = b.bucket.name
            key = b.key
        elif isinstance(b, BitBucket):
            b_name = b.name
            key = ''
        else:
            raise BitBucketError('Must pass Bits or BitBucket object')
        self._resp = s3amazon.S3.AWSAuthConnection.get_acl(self, b_name, key)
        return self._resp.body

    def set_canned_acl(self, b, policy):
        if isinstance(b, Bits):
            b_name = b.bucket.name
            key = b.key
        elif isinstance(b, BitBucket):
            b_name = b.name
            key = ''
        else:
            raise BitBucketError('Must pass Bits or BitBucket object')
        headers = {'x-amz-acl': policy}
        self._resp = self.put_acl(b_name, key, '', headers)
                
def connect(access_key=None, secret_key=None):
    return BBConnection(access_key, secret_key)
