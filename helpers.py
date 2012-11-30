#-*- coding:utf-8 -*-

import tornado.web
import tornado.escape
import tornado.locale

import pymongo, gridfs
import subprocess
import functools
from pymongo.errors import *
import moonlogger
import smtplib

class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        user = self.get_secure_cookie('current_user') or False
        if not user:
            return None
        return tornado.escape.json_decode(user)

    @property
    def sysdb(self):
        db = self.settings["sysdb"]
        return self.settings["sysdb"]



    def dbcon(self,database, state = 1):
        coninfo = self.sysdb.moongo_sys.userdbs.find_one({"user": self.current_user["username"],"database": database})
        con = pymongo.Connection(coninfo["host"],int(coninfo["port"]))
        authcon = con[coninfo["database"]]
        if coninfo["user"] and coninfo["password"]:
           authcon.authenticate(coninfo["user"],coninfo["password"])
        else:
            pass
        if state == 1:
            return authcon
        elif state == 0:
            return con

    @property
    def fs(self,database):
        if not hasattr(BaseHandler, "_fs"):
            _fs = gridfs.GridFS(self.dbcon(database))
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
        for i in self.sysdb.moongo_sys.userdbs.find({"user": self.current_user["username"]}):
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
        with fs.new_file(filename=file["filename"],username=self.current_user["username"],content_type=file["content_type"]) as f:
            f.write(file["body"])


    def get_file(self,db,filename):
        fs = gridfs.GridFS(db)
        return fs.get_last_version(filename)

    def mailSender(self, to, subject, message):
        gmail_user = self.settings["gmail_user"]
        gmail_pwd = self.settings["gmail_password"]
        smtpserver = smtplib.SMTP("smtp.gmail.com",587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(gmail_user, gmail_pwd)
        header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:' + subject + '\n'
        msg = header + '\n' + message + '\n\n'
        smtpserver.sendmail(gmail_user, to, msg)
        smtpserver.close()

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

