#-*- coding:utf-8 -*-

import tornado.web
import tornado.escape
import tornado.locale

import pymongo, gridfs
import subprocess
import functools

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

    def dbcon(self,database, state = 1):
        coninfo = self.sysdb.moongo_sys.userdbs.find_one({"user": self.current_user["name"],"database": database})
        con = pymongo.Connection(coninfo["host"],int(coninfo["port"]))
        authcon = con[coninfo["database"]]
        if not coninfo["host"] == "localhost":
            authcon.authenticate(coninfo["username"],coninfo["password"])
        else:
            pass
        if state == 1:
            return authcon
        elif state == 0:
            return con

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
