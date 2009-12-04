#! /usr/bin/env python

import sys
import os
import web

from pymongo.connection import Connection
from pymongo import ASCENDING, DESCENDING

import settings

urls = (
    '/', 'home',
    '/logs/(.+?)/(.+?)/(.*?)', 'logs'
)

app = web.application(urls, globals())
render = web.template.render('templates/', base='base')
conn = Connection(settings.MONGO['host'], settings.MONGO['port'])
collection = conn[settings.MONGO['db']][settings.MONGO['collection']]

class home:
    """ Home page

    A basic dasboard for global view.
    """ 
    def GET(self):
        photos = collection.find().sort("posted", DESCENDING).limit(20)
        return render.home(photos)

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

