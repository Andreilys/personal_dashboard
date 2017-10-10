#!/Users/andreilyskov/Desktop/Programming/Projects/personal_dashboard/venv/bin/python
import bitbucket
import EXIF
import os
import mimetypes
import sys

class JPegFilter(bitbucket.ContentFilter):

    interesting_fields = (('EXIF DateTimeOriginal', 'exif-date-time-original'),
			  ('EXIF ExifImageLength', 'exif-image-length'),
			  ('EXIF ExifImageWidth', 'exif-image-width'),
			  ('Image Model', 'image-model'),
			  ('Image Orientation', 'image-orientation'))
    
    def filter(self, bits):
	fp = open(bits.filename)
	self.exif_data = EXIF.process_file(fp)
	fp.close()
	for field in self.interesting_fields:
	    if self.exif_data.has_key(field[0]):
		bits[field[1]] = self.exif_data[field[0]].printable

def sync_images(bucket_name, path, ignore_dirs=[]):
    total_files = 0
    total_bytes = 0
    missed_files = []
    connection = bitbucket.connect()
    bucket = connection.get_bucket(bucket_name)
    for root, dirs, files in os.walk(path):
	for ignore in ignore_dirs:
	    if ignore in dirs:
		dirs.remove(ignore)
	for file in files:
	    fullpath = os.path.join(root, file)
	    content_type = mimetypes.guess_type(fullpath)[0]
	    if content_type == 'image/jpeg':
		total_files += 1
		try:
		    if bucket.has_key(file):
			bits = bucket[file]
			bits['local-path'] = root
			bits.filename = fullpath
		    else:
			bits = bitbucket.Bits(filename=fullpath)
			bits['local-path'] = root
			bucket[file] = bits
		    total_bytes += bits.size
		except bitbucket.BitBucketEmptyError:
		    print 'sync_dir: Empty File - Ignored %s' % fullpath
		except bitbucket.BitBucketResponseError, e:
		    print 'sync_dir: caught %s - %s' % (e.status, e.reason)
		    missed_files.append(file)
    print '[sync_images] total files = %d' % total_files
    print '[sync_images] total bytes = %d' % total_bytes
    print '[sync_images] %d missed files' % len(missed_files)
    return missed_files

def usage():
    print 'test_filter.py bucket_name path [ignore_dirs]'
    print '    bucket_name - the name of the S3 bucket to use'
    print '    path - the path to the local directory containing JPG images'
    print '    ingore_dirs - an optional list of comma-separated directory'
    print '                  names that can be ignored during sync operation'
    

if __name__ == "__main__":
    arglist = sys.argv[1:]
    if len(arglist) < 2:
	usage()
    else:
	bucket_name = arglist[0]
	path = arglist[1]
	ignore_dirs = None
	if len(arglist) > 2:
	    ignore_dirs = arglist[2].split(',')
	print bucket_name, path, ignore_dirs
	bitbucket.add_content_filter('image/jpeg', JPegFilter())
	sync_images(bucket_name, path, ignore_dirs)
	
