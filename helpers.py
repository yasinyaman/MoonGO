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
import re

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie('current_user') or False
        if not user:
            return None
        return tornado.escape.json_decode(user)

    @property
    def sysdb(self):
        try:
            return self.settings["sysdb"]
        except:
            modules().mailSender("allmail@moongo.org","MoonGO DB Connection","MoonGO can't connect to db.")
            raise

    def dbcon(self,database, state = 1):
        try:
            coninfo = self.sysdb.moongo_sys.userdbs.find_one({"user": self.current_user["username"],"database": database})
        except (ConnectionFailure,AutoReconnect) as e:
            self.logger.error("helpers.BaseHandler.dbcon", str(e), "coninfo")
            return

        try:
            con = pymongo.Connection(coninfo["host"])
        except (ConnectionFailure,AutoReconnect) as e:
            self.logger.error("helpers.BaseHandler.dbcon", str(e), "con")
            return

        try:
            authcon = con[coninfo["database"]]
        except (ConnectionFailure,AutoReconnect,KeyError,InvalidOperation) as e:
            self.logger.error("helpers.BaseHandler.dbcon", str(e), "authcon")
            return

        if coninfo["user"] and coninfo["password"]:
            try:
                authcon.authenticate(coninfo["user"],coninfo["password"])
            except (ConnectionFailure,AutoReconnect) as e:
                self.logger.error("helpers.BaseHandler.dbcon", str(e), "authcon.authenticate")
                return
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
            except (ConnectionFailure,AutoReconnect) as e:
                self.logger.error("helpers.BaseHandler.fs", str(e), "_fs")
            return _fs

    def get_user_locale(self):
        if self.get_cookie("lang",None):
            return tornado.locale.get(self.get_cookie("lang"))
        return None

    @property
    def logger(self):
        return self.settings["logger"](self.sysdb)

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
        except OSError as e:
            self.logger.error("helpers.modules.export",str(e),"process")
            return

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
        except OSError as e:
            self.logger.error("helpers.modules.import_db",str(e),"process")
            return


    def db_list(self):
        db_list = []
        try:
            for i in self.sysdb.moongo_sys.userdbs.find({"user": self.current_user["username"]}):
                db_list.append(i["database"])
        except (ConnectionFailure,AutoReconnect,InvalidOperation) as e:
            self.logger.error("helpers.modules.db_list",str(e))

        if db_list:
            return db_list
        else:
            return False



    def collections_list(self, dbname):
        try:
            collection_list = self.dbcon(dbname).collection_names()
        except (ConnectionFailure,AutoReconnect,InvalidOperation,OperationFailure) as e:
            self.logger.error("helpers.modules.collection_list",str(e))

        if collection_list:
            return collection_list
        else:
            return False

        # ???? self.__output_results(cursor, out, batch_size)


    def upload_to_gridfs(self,db,file={}):
        try:
            fs = gridfs.GridFS(db)
        except (ConnectionFailure,AutoReconnect,InvalidOperation) as e:
            self.logger.error("helpers.modules.upload_to_gridfs",str(e),"fs")
            return 

        try:    
            with fs.new_file(filename=file["filename"],username=self.current_user["username"],content_type=file["content_type"]) as f:
                f.write(file["body"])
        except (ConnectionFailure,AutoReconnect,InvalidOperation) as e:
            self.logger.error("helpers.modules.upload_to_gridfs",str(e),"fs.new_file")
            return

    def get_file(self,db,filename):
        try:
            fs = gridfs.GridFS(db)
            return fs.get_last_version(filename)
        except (ConnectionFailure,AutoReconnect,InvalidOperation) as e:
            self.logger.error("helpers.modules.get_file",str(e))
            return

    def mailSender(self, to, subject, message):
        gmail_user = self.settings["gmail_user"]
        gmail_pwd = self.settings["gmail_password"]
        try:
            smtpserver = smtplib.SMTP("smtp.gmail.com",587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo
        except smtplib.SMTPConnectError as e:
            self.logger.error("helpers.modules.mailSender",str(e),"smtpserver")
            return

        try:
            smtpserver.login(gmail_user, gmail_pwd)
        except smtplib.SMTPAuthenticationError as e:
            self.logger.error("helpers.modules.mailSender",str(e),"smtpserver.login")
            return

        try:
            header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:' + subject + '\n'
            msg = header + '\n' + message + '\n\n'
            smtpserver.sendmail(gmail_user, to, msg)
        except smtplib.SMTPServerDisconnected as e:
            self.logger.error("helpers.modules.mailSender",str(e),"smtpserver.sendmail")
            return

        smtpserver.close()
        
    def username_check(self, username):
        if self.sysdb.moongo_sys.users.find_one({"username":username}):
            return True
        else:
            return False

    def mail_check(self, mail):
        if self.sysdb.moongo_sys.users.find_one({"mail":mail}):
            return True
        else:
            return False

    def verify_mail(self,mail):
        regex = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",re.IGNORECASE)
        return mail == regex.findall(mail)

def database_control(method):
    @functools.wraps(method)
    def control(self,dbname,collname):
        if dbname not in self.db_list():
            self.write("HATA")
        else:
            return method(self,dbname,collname)
    return control

def collection_control(method):
    @functools.wraps(method)
    def control(self,dbname,collname):
        if collname not in self.collections_list(dbname):
            self.write("HATA")
        else:
            return method(self,dbname,collname)
    return control

def noauth(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user:
            return self.redirect("/")
        return method(self, *args, **kwargs)
    return wrapper

def root_control(method):
    @functools.wraps(method)
    def control(self,*args, **kwargs):
        if not self.sysdb.moongo_sys.user_authorizing.find_one({"username":self.current_user["username"], "authorizing":"root"}):
            return self.write("There is no authority.")
        return method(self, *args, **kwargs)
            
    return control




