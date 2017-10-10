#!/Users/andreilyskov/Desktop/Programming/Projects/personal_dashboard/venv/bin/python
import bitbucket
import os
import getopt

def sync_dir(bucket_name, path, ignore_dirs=[], trim_path=None):
    connection = bitbucket.connect()
    bucket = connection.get_bucket(bucket_name)
    for root, dirs, files in os.walk(path):
        for ignore in ignore_dirs:
            if ignore in dirs:
                dirs.remove(ignore)
        for file in files:
            fullpath = os.path.join(root, file)
            if trim_path:
                key = fullpath[len(trim_path):]
            else:
                key = fullpath
            try:
                if bucket.has_key(key):
                    bits = bucket[key]
                    bits.filename = fullpath
                else:
                    bits = bitbucket.Bits(filename=fullpath)
                    bucket[key] = bits
            except bitbucket.BitBucketEmptyError:
                print 'sync_dir: Empty File - Ignored %s' % fullpath
    return bucket

