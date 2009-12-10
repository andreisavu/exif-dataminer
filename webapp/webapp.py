#! /usr/bin/env python

import sys
import os
import web

from pymongo.connection import Connection
from pymongo import ASCENDING, DESCENDING
from urllib import quote, unquote

import settings

from utils import can_quote

urls = (
    '/', 'home',
    '/browse/([\d]*)', 'browse',
    '/photo/(.+?)', 'photo',
    '/exif/tags/', 'exif_tags',
    '/exif/tag/(.+)', 'exif_tag_info',
    '/exif/histogram/(.+?)/(.+?)', 'exif_histogram',
    '/logs/(.+?)/(.+?)/(.*?)', 'logs'
)

app = web.application(urls, globals())
render = web.template.render('templates/', base='base', globals={'quote':quote,  'can_quote':can_quote})

conn = Connection(settings.MONGO['host'], settings.MONGO['port'])
db = conn[settings.MONGO['db']]

class home:
    """ Dashboard

    List some aggregated statistics and clusters
    """
    def GET(self):
        from random import randint, seed

        l = db['photos'].count()
        if l:
            photos = db['photos'].find().skip(randint(0,l-1)).limit(1)
            random_photo = list(photos)[0]
        else:
            random_photo = None

        stats = {
            'total_number': db['photos'].count(),
            'exif_available' : db['photos'].find({'exif': {'$ne':[]}}).count(),
            'exif_tags' : db['exif_tags'].count()
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

        return render.browse(photos, offset, has_next)

class exif_tags:
    """ List all available exif tags """
    def GET(self):
        photo_count = db['photos'].count()
        tags = db['exif_tags'].find({'count':{'$gte': photo_count * 2 / 3.0 }}).sort('count', DESCENDING)
        return render.exif_tags(tags, photo_count)

class exif_tag_info:
    """ Generate some online statistics for a given exif tag """
    def GET(self, tag):
        values = db['exif_tags'].find_one({'tag':tag})['values']
        l = len(values)

        columns = self.format_as_columns(values, l/4 + 5)
        return render.exif_tag_info(tag, columns, l)

    def format_as_columns(self, values, per_column):
        offset = 0
        columns = []
        while offset < len(values):
            columns.append(values[offset:offset + per_column])
            offset += per_column - 1
        return columns

class exif_histogram:
    """ Display a sexy histogram for this tag and value

    Not very efficient but good enough for a prototype.
    """
    def GET(self, _tag, _value):
        _value = unquote(_value)

        ts = {}
        total = 0
        for p in db['photos'].find({'exif':{'$ne':[]}}).sort('posted', ASCENDING):
            for tag, label, value in p['exif']:
                if tag == _tag and value == _value and 'posted' in p:
                    posted = p['posted'].replace(hour=0, minute=0, second=0, microsecond=0)
                    total += 1
                    ts[posted] = total

        return render.exif_histogram(_tag, _value, sorted(ts.items()))
        
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
        return render.logs(logs, '/logs/%s/%s' % (db, collection))

if __name__ == "__main__":
    app.run()

