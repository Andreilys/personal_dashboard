#!/usr/bin/env python

# This software code is made available "AS IS" without warranties of any
# kind.  You may copy, display, modify and redistribute the software
# code either by itself or as incorporated into your code; provided that
# you do not remove any proprietary notices.  Your use of this software
# code is at your own risk and you waive any claim against Amazon
# Digital Services, Inc. or its affiliates with respect to your use of
# this software code. (c) 2006 Amazon Digital Services, Inc. or its
# affiliates.

import unittest
import S3
import httplib
import sys

AWS_ACCESS_KEY_ID = '<INSERT YOUR AWS ACCESS KEY ID HERE>'
AWS_SECRET_ACCESS_KEY = '<INSERT YOUR AWS SECRET ACCESS KEY HERE>'
# remove these next two lines when you've updated your credentials.
print "update s3-driver.py with your AWS credentials"
sys.exit();

BUCKET_NAME = "%s-test" % AWS_ACCESS_KEY_ID;

class TestAWSAuthConnection(unittest.TestCase):
    def setUp(self):
        self.conn = S3.AWSAuthConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

    def test_operations(self):
        response = self.conn.create_bucket(BUCKET_NAME)
        self.assertEquals(response.http_response.status, 200, 'create bucket')

        response = self.conn.list_bucket(BUCKET_NAME)
        self.assertEquals(response.http_response.status, 200, 'list bucket')
        self.assertEquals(len(response.entries), 0, 'bucket is empty')

        text = 'this is a test'
        key = 'test'

        response = self.conn.put(BUCKET_NAME, key, text)
        self.assertEquals(response.http_response.status, 200, 'put with a string argument')

        response = \
            self.conn.put(
                    BUCKET_NAME,
                    key,
                    S3.S3Object(text, {'title': 'title'}),
                    {'Content-Type': 'text/plain'})

        self.assertEquals(response.http_response.status, 200, 'put with complex argument and headers')

        response = self.conn.get(BUCKET_NAME, key)
        self.assertEquals(response.http_response.status, 200, 'get object')
        self.assertEquals(response.object.data, text, 'got right data')
        self.assertEquals(response.object.metadata, { 'title': 'title' }, 'metadata is correct')
        self.assertEquals(int(response.http_response.getheader('Content-Length')), len(text), 'got content-length header')

        title_with_spaces = " \t  title with leading and trailing spaces     "
        response = \
            self.conn.put(
                    BUCKET_NAME,
                    key,
                    S3.S3Object(text, {'title': title_with_spaces}),
                    {'Content-Type': 'text/plain'})

        self.assertEquals(response.http_response.status, 200, 'put with headers with spaces')

        response = self.conn.get(BUCKET_NAME, key)
        self.assertEquals(response.http_response.status, 200, 'get object')
        print response.object.metadata
        self.assertEquals(
                response.object.metadata,
                { 'title': title_with_spaces.strip() },
                'metadata with spaces is correct')

        weird_key = '&=//%# ++++'

        response = self.conn.put(BUCKET_NAME, weird_key, text)
        self.assertEquals(response.http_response.status, 200, 'put weird key')

        response = self.conn.get(BUCKET_NAME, weird_key)
        self.assertEquals(response.http_response.status, 200, 'get weird key')

        response = self.conn.get_acl(BUCKET_NAME, key)
        self.assertEquals(response.http_response.status, 200, 'get acl')

        acl = response.object.data

        response = self.conn.put_acl(BUCKET_NAME, key, acl)
        self.assertEquals(response.http_response.status, 200, 'put acl')

        response = self.conn.get_bucket_acl(BUCKET_NAME)
        self.assertEquals(response.http_response.status, 200, 'get bucket acl')

        bucket_acl = response.object.data

        response = self.conn.put_bucket_acl(BUCKET_NAME, bucket_acl)
        self.assertEquals(response.http_response.status, 200, 'put bucket acl')

        response = self.conn.list_bucket(BUCKET_NAME)
        self.assertEquals(response.http_response.status, 200, 'list bucket')
        entries = response.entries
        self.assertEquals(len(entries), 2, 'got back right number of keys')
        # depends on weird_key < key
        self.assertEquals(entries[0].key, weird_key, 'first key is right')
        self.assertEquals(entries[1].key, key, 'second key is right')

        response = self.conn.list_bucket(BUCKET_NAME, {'max-keys': 1})
        self.assertEquals(response.http_response.status, 200, 'list bucket with args')
        self.assertEquals(len(response.entries), 1, 'got back right number of keys')

        for entry in entries:
            response = self.conn.delete(BUCKET_NAME, entry.key)
            self.assertEquals(response.http_response.status, 204, 'delete %s' % entry.key)

        response = self.conn.list_all_my_buckets()
        self.assertEquals(response.http_response.status, 200, 'list all my buckets')
        buckets = response.entries

        response = self.conn.delete_bucket(BUCKET_NAME)
        self.assertEquals(response.http_response.status, 204, 'delete bucket')

        response = self.conn.list_all_my_buckets()
        self.assertEquals(response.http_response.status, 200, 'list all my buckets again')

        self.assertEquals(len(response.entries), len(buckets) - 1, 'bucket count is correct')


class TestQueryStringAuthGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = S3.QueryStringAuthGenerator(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, False)
        self.connection = httplib.HTTPConnection(self.generator.server_name)

    def check_url(self, url, method, status, message, data=''):
        if (method == 'PUT'):
            headers = { 'Content-Length': len(data) }
            self.connection.request(method, url, data, headers)
        else:
            self.connection.request(method, url)

        response = self.connection.getresponse()
        self.assertEquals(response.status, status, message)

        return response.read()

    def test_operations(self):
        key = 'test'

        self.check_url(self.generator.create_bucket(BUCKET_NAME), 'PUT', 200, 'create_bucket')
        self.check_url(self.generator.put(BUCKET_NAME, key, ''), 'PUT', 200, 'put object', 'test data')
        self.check_url(self.generator.get(BUCKET_NAME, key), 'GET', 200, 'get object')
        self.check_url(self.generator.list_bucket(BUCKET_NAME), 'GET', 200, 'list bucket')
        self.check_url(self.generator.list_all_my_buckets(), 'GET', 200, 'list all my buckets')
        acl = self.check_url(self.generator.get_acl(BUCKET_NAME, key), 'GET', 200, 'get acl')
        self.check_url(self.generator.put_acl(BUCKET_NAME, key, acl), 'PUT', 200, 'put acl', acl)
        bucket_acl = self.check_url(self.generator.get_bucket_acl(BUCKET_NAME), 'GET', 200, 'get bucket acl')
        self.check_url(self.generator.put_bucket_acl(BUCKET_NAME, bucket_acl), 'PUT', 200, 'put bucket acl', bucket_acl)
        self.check_url(self.generator.delete(BUCKET_NAME, key), 'DELETE', 204, 'delete object')
        self.check_url(self.generator.delete_bucket(BUCKET_NAME), 'DELETE', 204, 'delete bucket')


if __name__ == '__main__':
    unittest.main()


