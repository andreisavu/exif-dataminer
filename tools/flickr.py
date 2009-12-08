"""
Simple Flickr API built using YQL

You need to install python-yql in order to be able to use this.
All the calls are public and require no authentication.
"""

import yql

from datetime import datetime

class Flickr(object):
    """ Flickr API Client class based on Yahoo! Query Language

    No API key is needed because all the calls are public. 
    """
    def __init__(self):
        self.yql = yql.Public()

    def interesting_photos(self, num=5, date=None):
        """ Fetch most interesting photos from flickr

        Params: num - result size
        Yields tuples (id, title)
        """
        query = 'select id, title from flickr.photos.interestingness(%s)' % num
        if date is not None:
            query = "%s where date='%s'" % (query, date)
        results = self.yql.execute(query)
        return self._fetch_results(results, num)

    def recent_photos(self, num=5):
        """ Fetch recent pictures 

        Params: num - result size
        Yields tuples (id, title) 
        """
        query = 'select id, title from flickr.photos.recent(%s)' % num
        results = self.yql.execute(query)
        return self._fetch_results(results, num)

    def search_photos(self, search, num=5):
        """ Search photos on flickr
        
        Params: search string and num of results
        Yields tutples (id, title)
        """
        query = 'select id, title from flickr.photos.search(%s) where text=@text' % num
        results = self.yql.execute(query, {'text' : search})
        return self._fetch_results(results, num)

    def _fetch_results(self, results, num):
        """ Fetch results from a generic query result """
        rows = results.rows
        if num == 1: rows = [results.rows]
        
        for row in rows:
            yield (row.get('id'), row.get('title'))

    def get_exif(self, photo_id):
        """ Fetch exif data for a given photo_id

        Params: flickr photo ID
        Yields tubles (tag, label, raw_value)
        """
        query = 'select * from flickr.photos.exif where photo_id=@id'
        results = self.yql.execute(query, {'id': photo_id})
        if results.rows != [] and 'exif' in results.rows:
            for exif in results.rows['exif']:
                yield [exif['tag'], exif['label'], exif['raw']]

    def get_photo_info(self, photo_id):
        """ Get small amount of info

        Info Type: Owner realname, username and photo post date
        Params: flickr photo ID
        Returns: dict
        """
        query = 'select owner.username, owner.realname, dates.posted, ' \
            'dates.taken from flickr.photos.info where photo_id=@id'
        results = self.yql.execute(query, {'id': photo_id})
        if results.rows != []:
            return {
            'realname' : results.rows['owner']['realname'],
            'username' : results.rows['owner']['username'],
            'posted' : datetime.fromtimestamp(int(results.rows['dates']['posted']))
            }
        else:
            return None

    def get_photo_urls(self, photo_id):
        """ Fetch flick photo urls

        Params: flickr photo ID
        Returns: dict {Size: Url}
        """
        query = 'select label, source from flickr.photos.sizes where photo_id=@id'
        results = self.yql.execute(query, {'id': photo_id})
        
        ret = {}
        for row in results.rows:
            ret[row['label']] = row['source']
        return ret


if __name__ == '__main__':
    from itertools import izip, count
    print 'Flickr Client demo application. Showing one interesting photos posted today ...\n'

    f = Flickr()
    for id, title in f.interesting_photos(num=1):
        print 'ID:%s Title: %s' % (id, title)

        urls = f.get_photo_urls(id)
        if 'Medium' in urls:
            print 'Url: %s' % urls['Medium']

        print "\nExif data:"
        for index, (tag, label, raw) in izip(count(), f.get_exif(id)):
            print tag, label, raw
            if index == 5: 
                print "... and many more\n\n"
                break
        else:
            print "Info not available!\n\n"

    print 'Done.'

