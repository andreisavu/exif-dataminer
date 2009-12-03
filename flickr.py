"""
Simple Flickr API built using YQL

You need to install python-yql in order to be able to use this.
All the calls are public and require no authentication.
"""

import yql

class Flickr(object):
    def __init__(self):
        self.yql = yql.Public()

    def interesting_pictures(self, num=5):
        """ Fetch most interesting pictures from flickr

        Params: num - result size
        Yields tuples (id, title)
        """
        query = 'select id, title from flickr.photos.interestingness(%s)' % num
        results = self.yql.execute(query)
        for row in results.rows:
            yield (row.get('id'), row.get('title'))

    def get_exif(self, photo_id):
        """ Fetch exif data for a given photo_id

        Params: flickr photo ID
        Yields tubles (tag, label, raw_value)
        """
        query = 'select * from flickr.photos.exif where photo_id=@id'
        results = self.yql.execute(query, {'id': photo_id})
        if results.rows != []:
            for exif in results.rows['exif']:
                yield (exif['tag'], exif['label'], exif['raw'])

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
            'posted' : results.rows['dates']['posted'],
            'taken' : results.rows['dates']['taken']
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


