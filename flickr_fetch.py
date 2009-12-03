#! /usr/bin/env python

import sys
import flickr

from optparse import OptionParser

def main():
    opt, args = parse_args()
    f = flickr.Flickr()

    try:
        num = int(opt.num)
    except (ValueError, TypeError):
        num = 5

    results = None
    if opt.query is not None:
        results = f.search_photos(opt.query, num)
    elif opt.interesting:
        results = f.interesting_photos(num)
    elif opt.recent:
        results = f.recent_photos(num)
    else:
        print 'Usage: ./flickr_fetch.py <options> or --help for info'

    if results is not None:
        show_photos(f, results)

def show_photos(f, results):
    for id, title in results:
        print id, ': ', title
        print f.get_photo_urls(id)['Medium']

def parse_args():
    """ Parce command-line arguments """
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

