#!/usr/bin/env python
#-*- coding:utf-8 -*-

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.escape
import tornado.locale
import pymongo
from tornado.options import define, options
import os

from handlers import *
from user import *

define("port", default=8877, type=int)

settings = dict({
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "Ã¶saOPU)=()(/=+TY=0m552Ã¢Â§ÂªÃ¢ÂªÃ¢Âªâ‚¬0H/(=h0JKjÃ´â†�â†�jhAHODF8*))",
    "login_url": "/auth/login",
    "xsrf_cookies": False,
    "debug": True,
    "site_url": "http://iglon.com:8877",
    "sysdb": pymongo.Connection(),
    "mongo_path": "/usr/bin",
    "gmail_user": "",
    "gmail_password":""

})


urls = ([
    # auth
    (r"/auth/register/?([^/]+)?/?", RegisterHandler),
    (r"/auth/login/?", LoginHandler),
    (r"/auth/logout/?", LogoutHandler),
    (r"/auth/update/?", UpdateHandler),
    (r"/auth/remove/?", RemoveHandler),
    (r"/auth/recovery/?", RecoveryHandler),
    (r"/auth/reset/([^/]+)/?",PasswordResetHandler),
    (r"/auth/invitation/?",InvitationHandler),

    # Bu URL patternleri bÃ¶yle olmadÄ± sanki
    (r"/", DBList),
    (r"/databases/?", DBList),
    (r"/hostdbcopy/?", HostDBCopy),
    (r"/userdbadd/?", UserDbAdd),
    (r"/userdbupdate/([^/]+)/?",UserDbUpdate),
    (r"/userdbremove/([^/]+)/?",UserDbRemove),
    (r"/yukle/?",Yukle),
    (r"/indir/?",Indir),
    (r"/js/?",SystemJS),
    (r"/([^/]+)/([^/]+)/import/?",DocImport),
    (r"/([^/]+)/([^/]+)/export/?",DocExport),
    (r"/lng/([^/]+)/?", SetLang), #tr_TR , en_US ...
    (r"/([^/]+)/drop/?", DBDrop),
    (r"/([^/]+)/?", CollList),
    (r"/([^/]+)/copy/([^/]+)/?", DBCopy),
    (r"/([^/]+)/([^/]+)/create/?", CollCreate),
    (r"/([^/]+)/([^/]+)/drop/?", CollDrop),
    (r"/([^/]+)/([^/]+)/rename/([^/]+)/?", CollRename),
    (r"/([^/]+)/([^/]+)/?", DocList),
    (r"/([^/]+)/([^/]+)/add/?", DocAdd),
    (r"/([^/]+)/([^/]+)/([^/]+)/?", Doc),
    (r"/([^/]+)/([^/]+)/([^/]+)/remove/?", DocRemove),
    (r"/([^/]+)/([^/]+)/([^/]+)/edit/?", DocEdit)
])

application = tornado.web.Application(urls, **settings)

def main():
    tornado.options.parse_command_line()
    tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), "translations"))
    server = tornado.httpserver.HTTPServer(application)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
