#! /usr/bin/env python

import web

import settings

urls = (
    '/', 'home'
)
app = web.application(urls, globals())
render = web.template.render('templates/', base='base')

class home:        
    def GET(self):
        return render.home()

if __name__ == "__main__":
    app.run()

