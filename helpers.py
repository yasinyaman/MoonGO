#-*- coding:utf-8 -*-

import tornado.web
import tornado.escape
import tornado.locale

import pymongo, gridfs
import subprocess
import functools
from pymongo.errors import *
import moonlogger

class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        user = self.get_secure_cookie("current_user") or False
        if not user:
            return None
        return tornado.escape.json_decode(user)

    @property
    def sysdb(self):
        try:
            db = self.settings["sysdb"]
            self.logger.info("helpers.BaseHandler.sysdb","Connected",pr=0)
            return self.settings["sysdb"]
        except e:
            self.logger.error("helpers.BaseHandler.sysdb","%s" % str(e))

    @property
    def logger(self):
        if not hasattr(BaseHandler, "_logger"):
            try:
                _logger = moonlogger.Logger(self.sysdb)
                return _logger
            except e:
                print "Fatal Error: %s" % str(e)

    def dbcon(self,database, state = 1):
        try:
            coninfo = self.sysdb.moongo_sys.userdbs.find_one({"user": self.current_user["name"],"database": database})
        except (AutoReconnect,ConnectionFailure) as e:
            self.logger.error("helpers.BaseHandler.dbcon",str(e),extra="coninfo")

        try:
            con = pymongo.Connection(coninfo["host"],int(coninfo["port"]))
        except (AutoReconnect,ConnectionFailure) as e:
            self.logger.error("helpers.BaseHandler.dbcon",str(e),extra="con")

        authcon = con[coninfo["database"]]
        if coninfo["username"] and coninfo["password"]:
            try:
                authcon.authenticate(coninfo["username"],coninfo["password"])
            except (InvalidOperation,OperationFailure) as e:
                self.logger.error("helpers.BaseHandler.dbcon",str(e),extra="authcon.authenticate")
        else:
            pass
        if state == 1:
            return authcon
        elif state == 0:
            return con

    @property
    def fs(self,database):
        if not hasattr(BaseHandler, "_fs"):
            try:
                _fs = gridfs.GridFS(self.dbcon(database))
                return _fs
            except e:
                self.logger.error("helpers.BaseHandler.fs",str(e),extra="_fs")

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
        exp = "%s/mongoexport -d %s -c %s" % (self.settings["mongo_path"],db,coll)
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

        try:
            process = subprocess.Popen(exp, shell=True, stdout=subprocess.PIPE)
            return process.communicate()[0]
        except e:
            BaseHandler.logger.error("helpers.modules.export",str(e),"subprocess")
            return False

    def import_db(self,db,coll,data,host=None,port=None,user=None,password=None):
        exp = "%s/mongoimport -d %s -c %s --file %s" % (self.settings["mongo_path"],db,coll,data)
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

        try:
            process = subprocess.Popen(exp, shell=True, stdout=subprocess.PIPE)
            return process.communicate()[0]
        except e:
            BaseHandler.logger.error("helpers.modules.import_db",str(e),"subprocess")
            return False


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
