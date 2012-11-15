#!/usr/bin/env python
#-*- coding:utf-8 -*-
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.escape
import tornado.locale
import pymongo
import bcrypt
from bson import json_util
import json
from tornado.options import define, options
import os
import subprocess
define("port", default=8877, type=int)


class BaseHandler(tornado.web.RequestHandler):
    mongo_path = "/Users/doganaydin/mongodb/bin"
    def get_current_user(self):
        user = self.get_secure_cookie("current_user") or False
        if not user:
            return None
        return tornado.escape.json_decode(user)

    @property
    def db(self):
        if not hasattr(BaseHandler, "_db"):
            _db = pymongo.Connection()
        return _db

    @property
    def fs(self):
        if not hasattr(BaseHandler, "_fs"):
            _fs = gridfs.GridFS(self.db)
        return _fs

    def get_user_locale(self):
        if self.get_cookie("lang"):
            return tornado.locale.get(self.get_cookie("lang"))
        else:
            return None

class modules(object):

    def redirectCustom(self, url, template, **kwargs):
        """ Ã§alÄ±ÅŸÄ±r duruma getirilecek"""
        if url:
            self.redirect("%s" % (url))
        else:
            self.render(template, doc)
        pass

    def export(self,db,coll,host=None,port=None,user=None,password=None):
        exp = "%s/mongoexport -d %s -c %s" % (BaseHandler.mongo_path,db,coll)
        if not db or not coll:
            return False
        if host:
            exp += " --host %s" % host
        if port:
            exp += " --port %s" % port
        if user:
            exp += " --user %s" % user
        if password:
            exp += " --password %s" % password

        process = subprocess.Popen(exp, shell=True, stdout=subprocess.PIPE)
        return process.communicate()[0]

    def import_db(self,db,coll,data,host=None,port=None,user=None,password=None):
        exp = "%s/mongoimport -d %s -c %s --file %s" % (BaseHandler.mongo_path,db,coll,data)
        if not db or not coll or not data:
            return False
        if host:
            exp += " --host %s" % host
        if port:
            exp += " --port %s" % port
        if user:
            exp += " --user %s" % user
        if password:
            exp += " --password %s" % password

        process = subprocess.Popen(exp, shell=True, stdout=subprocess.PIPE)
        return process.communicate()[0]

            
        self.__output_results(cursor, out, batch_size)
class MainHandler(BaseHandler):
    def get(self):
        db_list = self.db.database_names()
        for dbnamess in db_list:
            print "Database :" + dbnamess
            collection_list = self.db[dbnamess].collection_names()
            for i in collection_list:
                print "> Colletion :" + i
                db_conn = self.db[dbnamess]
                doc_list = db_conn[i].find()
                if doc_list:
                    for doc in doc_list:
                        print doc.get("_id")
                        for key in doc.keys():
                            print ">> Key :" + key
                else:
                    pass
            self.redirect("/databases")
            self.render("database.html", db_list=db_list)
            self.write(db_list[0])

class SetLang(BaseHandler):
    def get(self,lang):
        self.set_cookie("lang", lang)
        if self.request.headers.get('Referer'):
            self.redirect(self.request.headers.get('Referer'))
        else:
            self.redirect("/")

class DBList(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        #self.get_user_locale()
        #self.write(repr(self.request))
        db_list = self.db.database_names()
        server_info = self.db.server_info()
        #self.write(self.db.serverStatus())
        self.render("database.html", db_list=db_list, server_info=server_info)


class DBDrop(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname):
        self.db.drop_database(dbname)
        self.redirect("/")


class DBCopy(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, to_dbname):
        self.db.copy_database(dbname, to_dbname)
        self.redirect("/%s" % (to_dbname))


class HostDBCopy(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("hostdbcopy.html")


    @tornado.web.authenticated
    def post(self):
        hostdb = self.request.arguments
        try:
            user = hostdb["user"][0]
        except:
            user = False
        try:
            password = hostdb["password"][0]
        except:
            password = False

        if user and password:
            self.db.copy_database(
                hostdb["hostdb"][0],
                hostdb["db"][0],
                hostdb["host"][0],
                user,
                password
            )
        else:
            self.db.copy_database(
                hostdb["hostdb"][0],
                hostdb["db"][0],
                hostdb["host"][0]
            )
        self.redirect("/%s" % (hostdb["db"]))
        #self.write(host.get(host))


#Koleksiyon iÅŸlemleri
class CollList(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname):
        collection_list = self.db[dbname].collection_names()
        self.render(
            "collection.html",
            collection_list=collection_list,
            dbname=dbname
        )


class CollRename(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname, collrename):
        doc_list = self.db[dbname][collname].rename(collrename)
        self.redirect("/%s/%s" % (dbname, collrename))


class CollDrop(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname):
        self.db[dbname].drop_collection(collname)
        self.redirect("/%s" % (dbname))


class CollCreate(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname):
        self.db[dbname].create_collection(collname)
        self.redirect("/%s" % (dbname))


#DÃ¶kÃ¼man iÅŸlemleri
class DocList(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname):
        spec={"mail" : "yasnyaman@gmail.com"}
        fields=None
        limit=3
        skip=None
        doc_list = self.db[dbname][collname].find(spec=spec, fields=fields, limit=limit)
        collstats =self.db[dbname].command("collstats", collname)
        self.render(
            "documentlist.html",
            doc_list=doc_list,
            dbname=dbname,
            collname=collname,
            collstats=collstats
        )


class Doc(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self, dbname, collname, docid):
        doc = self.db[dbname][collname].find_one(
            {"_id": pymongo.son_manipulator.ObjectId(docid)})
        formdoc = json.dumps(doc, default=json_util.default)
        self.render("document.html",
            doc=doc,
            formdoc=formdoc,
            dbname=dbname,
            collname=collname
        )


class DocRemove(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname, docid):
        """doc = db_conn[collname].find_one(
        {"_id": pymongo.son_manipulator.ObjectId(docid)})"""
        self.db[dbname][collname].remove(
            {"_id": pymongo.son_manipulator.ObjectId(docid)})
        #self.render("document.html",doc=doc,dbname=dbname,collname=collname)
        self.redirect("/%s/%s" % (dbname, collname))

class DocAdd(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname):
        self.render("documentadd.html",
            dbname=dbname,
            collname=collname,
        )

    @tornado.web.authenticated
    def post(self, dbname, collname):
        data = self.get_arguments("jsonData", False)
        save_data = json.loads(data[0], object_hook=json_util.object_hook)
        print save_data
        self.db[dbname][collname].save(save_data)
        docid = self.db[dbname][collname].find_one(save_data)["_id"]

        self.redirect("/%s/%s/%s" % (dbname, collname, docid))


class DocEdit(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname, docid):
        doc = self.db[dbname][collname].find_one(
            {"_id": pymongo.son_manipulator.ObjectId(docid)})
        formdoc = json.dumps(doc, default=json_util.default)
        self.render("documentedit.html",
            formdoc=formdoc,
            dbname=dbname,
            docid=docid,
            collname=collname,
        )

    @tornado.web.authenticated
    def post(self, dbname, collname, docid):
        data = self.get_arguments("jsonData", False)
        save_data = json.loads(data[0], object_hook=json_util.object_hook)
        self.db[dbname][collname].save(save_data)
        self.redirect("/%s/%s" % (dbname, collname))


class DocImport(BaseHandler,modules):
    def get(self):
        self.write("<form method='post' enctype='multipart/form-data'><input type='file' name='data'><input type='submit'></form>")

    def post(self):
        dosya = self.request.files["data"][0]
        with open(dosya["filename"],"w") as f:
            f.write(dosya["body"])
        self.write("%s" % str(self.import_db("test","deneme",dosya["filename"])))

class DocExport(BaseHandler,modules):
    def get(self):
        self.write("%s" % str(self.export("test","deneme")))

class RegisterHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.render("register.html")
        else:
            self.redirect("/")

    def post(self):
        if self.get_argument("name", False):
            name = self.get_argument("name")
        else:
            self.write("Name required")
            return

        if self.get_argument("user_name", False):
            user_name = self.get_argument("user_name")
        else:
            self.write("Username required")
            return

        if self.get_argument("password", False):
            password = self.get_argument("password")
        else:
            self.write("Password required")
            return

        if self.get_argument("confirm_password", False):
            confirm_password = self.get_argument("confirm_password")
            if confirm_password != password:
                self.write("Passwords not match")
                return
        else:
            self.write("Confirm Password required")
            return

        if self.get_argument("mail", False):
            mail = self.get_argument("mail")
        else:
            self.write("Mail is required")
            return
        user = dict(
            name=name,
            user_name=user_name,
            password=bcrypt.hashpw(password, bcrypt.gensalt()),
            mail=mail
        )
        self.db.moongo_sys.users.save(user)
        self.redirect("/auth/login")


class LoginHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.render("login.html")
        else:
            self.redirect("/")

    def post(self):
        user_name = self.get_argument("user_name", False)
        password = self.get_argument("password", False)
        if user_name and password:
            user = self.db.moongo_sys.users.find_one({"user_name": user_name},
                                                     {"_id": 0})
            if user:
                crypt_pass = bcrypt.hashpw(password, user["password"])
                pass_check = crypt_pass == user["password"]
                if pass_check:
                    self.set_secure_cookie("current_user",
                                           tornado.escape.json_encode(user))
                    self.redirect("/")
                else:
                    self.write("Incorrect username or password.")
            else:
                self.write("""User is not exist.
                <a href='/auth/register'>Register?</a>""")
        else:
            self.write("You must fill both username and password")


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("current_user")
        self.redirect("/")

settings = dict({
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "cookie_secret": "Ã¶saOPU)=()(/=+TY=0m552Ã¢Â§ÂªÃ¢ÂªÃ¢Âªâ‚¬0H/(=h0JKjÃ´â†�â†�jhAHODF8*))",
    "login_url": "/auth/login",
    "xsrf_cookies": False,
    "debug": True,
    "site_url": "http://xxx.com"
})

urls = ([
    # auth
    (r"/auth/register/?", RegisterHandler),
    (r"/auth/login/?", LoginHandler),
    (r"/auth/logout/?", LogoutHandler),

    # Bu URL patternleri bÃ¶yle olmadÄ± sanki
    (r"/", DBList),
    (r"/databases", DBList),
    (r"/hostdbcopy", HostDBCopy),
    (r"/import",DocImport),
    (r"/export",DocExport),
    #(r"/jsonimport", JsonImport),
    (r"/lng/([^/]+)", SetLang), #tr_TR , en_US ...
    (r"/([\_\.A-Za-z0-9]+)/drop", DBDrop),
    (r"/([\_\.A-Za-z0-9]+)", CollList),
    (r"/([\_\.A-Za-z0-9]+)/copy/([\_\.A-Za-z0-9]+)", DBCopy),
    (r"/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/create", CollCreate),
    (r"/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/drop", CollDrop),
    (r"/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/rename/([\_\.A-Za-z0-9]+)",
        CollRename
    ),
    (r"/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)", DocList),
    (r"/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/add", DocAdd),
    (r"/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)", Doc),
    (r"/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/remove",
        DocRemove
    ),
    (r"/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/([\_\.A-Za-z0-9]+)/edit",
        DocEdit
    ),
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
