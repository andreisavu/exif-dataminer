#! /usr/bin/env python

import sys
import logging

from optparse import OptionParser
from pymongo.connection import Connection

import flickr
import settings

try:
    from mongolog.handlers import MongoHandler
except ImportError:
    print >>sys.stderr, 'Please install mongolog. This will allow centralized logging.'
    sys.exit(1)

def main():
    log = setup_logging()
    log.setLevel(logging.DEBUG)
    log.info('Starting Flickr photo fetch tool');

    opt, args = parse_args()
    f = flickr.Flickr()

    try:
        num = int(opt.num)
    except (ValueError, TypeError):
        num = 5

    log.info("Query max result size: %d" % num)

    results = None
    if opt.query is not None:
        log.info('Searching flickr: "%s"' % opt.query)
        results = f.search_photos(opt.query, num)
    elif opt.interesting:
        log.info('Loading interesting pictures from flickr.')
        results = f.interesting_photos(num)
    elif opt.recent:
        log.info('Loading recent photos from flickr.')
        results = f.recent_photos(num)
    else:
        print 'Usage: ./flickr_fetch.py <options> or --help for info'
        return 2

    if results is not None:
        store_photos(f, results, log)
    else:
        log.info('No photos found.')

def setup_logging():
    """ Setup centralized logging

    All log messages will end-up in capped mongo collection
    """
    log = logging.getLogger('flickr')
    host = 'localhost'
    try:
        import settings
        host = settings.MONGO['host']
    except ImportError:
        print >>sys.stderr, 'Settings file is not available. Using localhost.'

    log.addHandler(MongoHandler.to(db='logging', collection='tools', host=host))
    return log       

def store_photos(f, results, log):
    conn = Connection(settings.MONGO['host'], settings.MONGO['port'])
    collection = conn[settings.MONGO['db']]['photos']

    for id, title in results:
        if collection.find({'id':id}).count():
            log.info('Photo with ID:%s is already stored.' % id)
            continue

        photo_data = {
            'id' : id,
            'title' : title, 
            'urls' : f.get_photo_urls(id),
            'exif' : list(f.get_exif(id))
        }
        info = f.get_photo_info(id)
        if info is not None:
            for k,v in info.items():
                photo_data[k] = v

        if 'Medium' in photo_data['urls']:
            log.info("Saving photo: ID:%s Title:%s Url:%s" %  (id, title, photo_data['urls']['Medium']))
        else:
            log.info("Saving photo: ID:%s Title:%s" % (id, title))

        collection.save(photo_data)
        update_exif_tags(conn, photo_data['exif'], log)

def update_exif_tags(conn, exif, log):
    log.info('Fetching exif tags from current photo.')
    collection = conn[settings.MONGO['db']]['exif_tags']
    for (tag, label, value) in exif:
        if collection.find({'tag':tag}).count() == 0:
            log.info('Registering tag: %s with label: %s' % (tag, label))
            collection.save({'tag':tag, 'label': label})
        

def parse_args():
    """ Parse command-line arguments """
    parser = OptionParser()

    parser.add_option('-q', '--query', dest='query', 
        help='flickr search QUERY', metavar='QUERY')

    parser.add_option('-i', '--interesting', action='store_true',
        dest='interesting', default=False, help='interesting photos')

    parser.add_option('-r', '--recent', action='store_true',
        dest='recent', default=False, help='recent photos')

    parser.add_option('-n', '--num', dest='num',
        help='result SIZE', metavar='SIZE')

    return parser.parse_args()

if __name__ == '__main__':
    sys.exit(main())

