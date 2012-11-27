#!/usr/bin/env python
#-*- coding:utf-8 -*-
import gridfs
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
import functools
define("port", default=8877, type=int)


class BaseHandler(tornado.web.RequestHandler):
    mongo_path = "/usr/bin"
    def get_current_user(self):
        user = self.get_secure_cookie("current_user") or False
        if not user:
            return None
        return tornado.escape.json_decode(user)

    @property
    def db(self):
        return self.settings["db"]

    def dbcon(self,database):
        coninfo = self.sysdb.moongo_sys.userdbs.find_one({"user": self.current_user["name"],"database": database})
        con = pymongo.Connection(coninfo["host"],int(coninfo["port"]))
        authcon = con[coninfo["database"]]
        if not coninfo["host"] == "localhost":
            authcon.authenticate(coninfo["username"],coninfo["password"])
        else:
            pass
        return authcon

    @property
    def sysdb(self):
        if not hasattr(BaseHandler, "_sysdb"):
            _sysdb = pymongo.Connection("localhost")
        return _sysdb

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


    def db_list(self):
        db_list = []
        for i in self.sysdb.moongo_sys.userdbs.find({"user": self.current_user["name"]}):
            db_list.append(i["database"])
        if db_list:
            return db_list
        else:
            return False



    def collections_list(self, dbname):
        dbd = self.sysdb.moongo_sys.userdbs.find_one({"user": self.current_user["name"], "database":dbname})
        collection_list = self.dbcon(dbname).collection_names()
        if collection_list:
            return collection_list
        else:
            return False

        self.__output_results(cursor, out, batch_size)


    def upload_to_gridfs(self,db,file={}):
        fs = gridfs.GridFS(db)
        with fs.new_file(filename=file["filename"],user=self.current_user["user_name"],content_type=file["content_type"]) as f:
            f.write(file["body"])


    def get_file(self,db,filename):
        fs = gridfs.GridFS(db)
        return fs.get_last_version(filename)


def database_control(method):
    @functools.wraps(method)
    def control(self,dbname,collname):
        if dbname not in self.db.database_names():
            self.write("HATA")
        else:
            return method(self,dbname,collname)
    return control

def collection_control(method):
    @functools.wraps(method)
    def control(self,dbname,collname):
        if collname not in self.db[dbname].collection_names():
            self.write("HATA")
        else:
            return method(self,dbname,collname)
    return control




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


class UserDbAdd(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("userdbadd.html")
    @tornado.web.authenticated
    def post(self):
        if self.get_argument("name", False):
            databaseinfo = dict(
                user=self.current_user["name"],
                database=self.get_argument("name", False),
                host=self.get_argument("host", False),
                username = self.get_argument("username", False),
                password=self.get_argument("password", False),
                port=self.get_argument("port", 27017)
            )
        elif self.get_argument("uri", False):
            uri = pymongo.uri_parser.parse_uri(self.get_argument("uri", False), default_port=27017)
            databaseinfo = dict(
                user=self.current_user["name"],
                database=uri["database"],
                host=uri["nodelist"][0][0],
                username = uri["username"],
                password=uri["password"],
                port=uri["nodelist"][0][1]
            )
        elif not self.get_argument("name", False) or self.get_argument("uri", False) or self.get_argument("host",False):
            self.write("HATA")
        self.sysdb.moongo_sys.userdbs.save(databaseinfo)
        self.redirect("/")


class SetLang(BaseHandler):
    def get(self,lang):
        self.set_cookie("lang", lang)
        if self.request.headers.get('Referer'):
            self.redirect(self.request.headers.get('Referer'))
        else:
            self.redirect("/")

class DBList(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self):
        db_list = self.db_list()
        self.render("database.html",db_list=db_list)


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
class CollList(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self, dbname):
        collection_list = self.collections_list(dbname)
        self.render(
            "collection.html",
            collection_list=collection_list,
            dbname=dbname
        )




class CollRename(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname, collrename):
        doc_list = self.dbcon(dbname)[collname].rename(collrename)
        self.redirect("/%s/%s" % (dbname, collrename))



class CollDrop(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname):
        self.dbcon(dbname).drop_collection(collname)
        self.redirect("/%s" % (dbname))


class CollCreate(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname):
        self.dbcon(dbname).create_collection(collname)
        self.redirect("/%s" % (dbname))


#DÃ¶kÃ¼man iÅŸlemleri
class DocList(BaseHandler):
    @tornado.web.authenticated
    #@database_control
    #@collection_control
    def get(self, dbname, collname):
        spec=None
        fields=None
        limit=10
        skip=None
        doc_list = self.dbcon(dbname)[collname].find(spec=spec, fields=fields, limit=limit)
        collstats =self.dbcon(dbname).command("collstats", collname)
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
        doc = self.dbcon(dbname)[collname].find_one(
            {"_id": pymongo.son_manipulator.ObjectId(docid)})
        self.render("document.html",
            doc=doc,
            dbname=dbname,
            collname=collname
        )


class DocRemove(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname, docid):
        """doc = db_conn[collname].find_one(
        {"_id": pymongo.son_manipulator.ObjectId(docid)})"""
        self.dbcon(dbname)[collname].remove(
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
        self.dbcon(dbname)[collname].save(save_data)
        docid = self.dbcon(dbname)[collname].find_one(save_data)["_id"]

        self.redirect("/%s/%s/%s" % (dbname, collname, docid))


class DocEdit(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname, docid):
        doc = self.dbcon(dbname)[collname].find_one(
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
        self.dbcon(dbname)[collname].save(save_data)
        self.redirect("/%s/%s" % (dbname, collname))


class DocImport(BaseHandler,modules):
    def get(self, dbname, collname):
        self.write("<form method='post' enctype='multipart/form-data'><input type='file' name='data'><input type='submit'></form>")

    def post(self, dbname, collname):
        dosya = self.request.files["data"][0]
        with open(dosya["filename"],"w") as f:
            f.write(dosya["body"])
        self.write("%s" % (self.import_db(dbname, collname, dosya["filename"])))

class DocExport(BaseHandler,modules):
    def get(self, dbname, collname):
        self.write("%s" % (str(self.export(dbname,collname))))


class Yukle(BaseHandler,modules):
    def get(self):
        self.write("""
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="gfs">
                <input type="submit">
            </form>
        """)

    def post(self):
        file = self.request.files["gfs"][0]
        self.write(file["filename"])
        print self.upload_to_gridfs(self.db.files,file=file)


class Indir(BaseHandler,modules):
    def get(self):
        self.write("""
            <form method="post">
                <input type="text" name="gfs">
                <input type="submit">
            </form>
        """)

    def post(self):
        file = self.get_argument("gfs",None)
        gfs = self.get_file(self.db.files,file)
        self.set_header('Content-Disposition', 'attachment; filename=%s' % gfs.name)
        self.write(gfs.read())


class SystemJS(BaseHandler):
    def get(self):
        self.write("""
            <form method="post">
                <input type="text" name="name"><br>
                <input type="hidden" name="dbname" value="deneme">
                <textarea name="js" cols="500" rows="500"></textarea><br>
                <input type="submit">
            </form>
        """)

    def post(self):
        # Listeleme self.db[dbname].system_js.list()
        name = self.get_argument("name",None)
        dbname = self.get_argument("dbname",None)
        js = self.get_argument("js",None)
        if name and dbname and js:
            self.db[dbname].system_js[name] = js
            self.write("%s function is ready." % name)
        else:
            self.write("Check form values")

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
        self.sysdb.moongo_sys.users.save(user)
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
            user = self.sysdb.moongo_sys.users.find_one({"user_name": user_name},
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
    "site_url": "http://xxx.com",
    "db": pymongo.Connection()
})

urls = ([
    # auth
    (r"/auth/register/?", RegisterHandler),
    (r"/auth/login/?", LoginHandler),
    (r"/auth/logout/?", LogoutHandler),

    # Bu URL patternleri bÃ¶yle olmadÄ± sanki
    (r"/", DBList),
    (r"/databases/?", DBList),
    (r"/hostdbcopy/?", HostDBCopy),
    (r"/userdbadd/?", UserDbAdd),
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
