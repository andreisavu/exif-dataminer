#! /usr/bin/env python

import sys
import os
import web

from pymongo.connection import Connection
from pymongo import ASCENDING, DESCENDING

import settings

urls = (
    '/', 'home',
    '/browse/([\d]*)', 'browse',
    '/photo/(.+?)', 'photo',
    '/logs/(.+?)/(.+?)/(.*?)', 'logs'
)

app = web.application(urls, globals())
render = web.template.render('templates/', base='base')

conn = Connection(settings.MONGO['host'], settings.MONGO['port'])
db = conn[settings.MONGO['db']]

class home:
    """ Dashboard

    List some aggregated statistics and clusters
    """
    def GET(self):
        from random import randint, seed

        l = db['photos'].count()
        random_photo = db['photos'].find()[randint(0,l-1)]

        stats = {
            'total_number': db['photos'].count(),
            'exif_available' : db['photos'].find({'exif': {'$ne':[]}}).count()
        }

        return render.home(random_photo, stats) 

class browse:
    """ List all photos

    List all photos in backwards chronological order
    """ 
    def GET(self, offset):
        if offset == '':offset = 0
        offset = int(offset)

        all_photos = db['photos'].find().sort("posted", DESCENDING)
        photos = all_photos.skip(offset).limit(settings.PHOTOS_PER_PAGE)

        all_count = all_photos.count()
        if all_count <= (offset + settings.PHOTOS_PER_PAGE):
            has_next = False
        else:
            has_next = True

        return render.browse(list(photos), offset, has_next)

class photo:
    """ Display photo

    This also provides from options for navigation and clustering
    """
    def GET(self, photo_id):
        photo = db['photos'].find_one({'id':photo_id})
        return render.photo(photo)

class logs:
    """ Centralized logging basic view interface 
    
    All log messages end-up in capped mongodb collection. You can
    explore that collection and filter by error level.
    """
    def GET(self, db, collection, level):
        args = {}
        allowed_levels = ['info', 'debug', 'warning', 'error', 'critical']
        if level and level in allowed_levels:
            args = {'level':level}
        logs = conn[db][collection].find(args, limit=100).sort('$natural', DESCENDING)
        return render.logs(list(logs), '/logs/%s/%s' % (db, collection))

if __name__ == "__main__":
    app.run()

