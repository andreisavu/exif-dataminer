
import flickr

from itertools import izip, count

f = flickr.Flickr()

for id, title in f.interesting_pictures(3):
    print 'ID:', id
    print 'Title:', title
    print 'Medium URL:', f.get_photo_urls(id)['Medium']

    print f.get_photo_info(id)

    print "\nExif info:"
    for index, (tag, label, raw) in izip(count(), f.get_exif(id)):
        print tag, label, raw
        if index == 5: 
            print "... and many more\n\n"
            break
    else:
        print "info not available!\n\n"

