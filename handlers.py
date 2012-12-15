#-*- coding:utf-8 -*-

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.escape
import tornado.locale
import pymongo
import hashlib
from pymongo.errors import *
from bson import json_util
import json

from helpers import *


class MainHandler(BaseHandler):
    """
        Buranın elden geçmesi lazım. Hata ayıklamayı atlıyorum.
    """
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
        user = self.current_user["username"]
        database = self.get_argument("name", None)
        host = self.get_argument("host", None) + ":" + str(self.get_argument("port", 27017))
        username = self.get_argument("username", None)
        password = self.get_argument("password", None)
        uri = self.get_argument("uri", None)

        if database:
            databaseinfo = dict(
                user=user,
                database=database,
                host=host,
                username=username,
                password=password,
            )

        elif uri:
            uri = pymongo.uri_parser.parse_uri(uri, default_port=27017)
            databaseinfo = dict(
                user=user,
                database=uri["database"],
                host=uri["nodelist"],
                username=uri["username"],
                password=uri["password"],
            )

        else:
            self.write("Please check database info and try again")
            self.logger.error("handlers.UserDbAdd.post", "form validate")

        _id = self.sysdb.moongo_sys.userdbs.save(databaseinfo)

        if _id:
            self.logger.info("handlers.UserDbAdd.post", "%s created successfully" % str(_id))
        else:
            self.logger.error("handlers.UserDbAdd.post", "%s not created successfully" % str(_id))

        self.redirect("/")


class UserDbUpdate(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname):
        db_info = self.sysdb.moongo_sys.userdbs.find_one({"database": dbname, "user": self.current_user["username"]})
        self.render("userdbupdate.html", db_info=db_info)

    @tornado.web.authenticated
    def post(self, dbname):
        db_info = self.sysdb.moongo_sys.userdbs.find_one({"database": dbname, "user": self.current_user["username"]})

        databaseinfo = dict(
            _id=db_info["_id"],
            user=self.current_user["username"]
        )

        database = self.get_argument("database", None)
        host = self.get_argument("host", None),
        username = self.get_argument("username", None),
        password = self.get_argument("password", None),
        port = self.get_argument("port", None)

        if database:
            databaseinfo.update({"database": database})

        if host:
            databaseinfo.update({"host": host})

        if username:
            databaseinfo.update({"username": username})

        if password:
            databaseinfo.update({"password": password})

        if port:
            databaseinfo.update({"port": port})

        self.sysdb.moongo_sys.userdbs.save(databaseinfo)
        self.redirect("/")


class UserDbRemove(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname):
        try:
            self.sysdb.moongo_sys.userdbs.remove({"database": dbname, "user": self.current_user["username"]})
            self.redirect("/")
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.UserDbRemove.get", str(e))
            self.write("Something wrong!")

    def post(self, dbname):
        pass


class SetLang(BaseHandler):
    def get(self, lang):
        self.set_cookie("lang", lang)
        if self.request.headers.get('Referer'):
            self.redirect(self.request.headers.get('Referer'))
        else:
            self.redirect("/")


class Dashboard(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self):
        db_list = self.db_list()
        self.render("dashboard.html", db_list=db_list, user=self.current_user["name"], gravatar=hashlib.md5(self.current_user["mail"]).hexdigest())


class DBDrop(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname):
        self.dbcon(dbname, 0).drop_database(dbname)
        self.sysdb.moongo_sys.userdbs.remove({"database": dbname, "username": self.current_user["username"]})
        self.redirect("/")


class DBCopy(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, to_dbname):
        self.dbcon(dbname, 0).copy_database(dbname, to_dbname)
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
            self.dbcon(hostdb["db"][0], 0).copy_database(
                hostdb["hostdb"][0],
                hostdb["db"][0],
                hostdb["host"][0],
                user,
                password
            )
        else:
            self.dbcon(hostdb["db"][0], 0).copy_database(
                hostdb["hostdb"][0],
                hostdb["db"][0],
                hostdb["host"][0]
            )
        self.redirect("/%s" % (hostdb["db"][0]))
        #self.write(host.get(host))


#Koleksiyon iÅŸlemleri
class CollList(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self, dbname):
        try:
            collection_list = self.collections_list(dbname)
            self.render(
                "collection.html",
                collection_list=collection_list,
                dbname=dbname
            )
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.CollList.get", str(e))
            self.write("Something is wrong!")


class CollRename(BaseHandler):
    """
        Bu kısmın post olarak halledilmesi lazım.
        Mesela biri resim olarak burayı link verirse xss ile adamın db de oynama yapar.

        Ayrıca bu kısımlara yine onay koyabiliriz "emin misiniz?" diye.
    """
    @tornado.web.authenticated
    def get(self, dbname, collname, collrename):
        try:
            self.dbcon(dbname)[collname].rename(collrename)
            self.redirect("/%s/%s" % (dbname, collrename))
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.CollRename.get", str(e))
            self.write("Something is wrong!")


class CollDrop(BaseHandler):
    """
        Bu kısmın post olarak halledilmesi lazım.
        Mesela biri resim olarak burayı link verirse xss ile adamın db de oynama yapar.

        Ayrıca bu kısımlara yine onay koyabiliriz "emin misiniz?" diye.
    """
    @tornado.web.authenticated
    def get(self, dbname, collname):
        try:
            self.dbcon(dbname).drop_collection(collname)
            self.redirect("/%s" % (dbname))
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.CollDrop.get", str(e))
            self.write("Something is wrong!")


class CollCreate(BaseHandler):
    """
        Bu kısmın post olarak halledilmesi lazım.
        Mesela biri resim olarak burayı link verirse xss ile adamın db de oynama yapar.

        Ayrıca bu kısımlara yine onay koyabiliriz "emin misiniz?" diye.
    """
    @tornado.web.authenticated
    def get(self, dbname, collname):
        try:
            self.dbcon(dbname).create_collection(collname)
            self.redirect("/%s" % (dbname))
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.CollCreate.get", str(e))
            self.write("Something is wrong!")


#DÃ¶kÃ¼man iÅŸlemleri
class DocList(BaseHandler):
    @tornado.web.authenticated
    #@database_control
    #@collection_control
    def get(self, dbname, collname):
        spec = None
        fields = None
        limit = 10
        #skip=None
        try:
            doc_list = self.dbcon(dbname)[collname].find(spec=spec, fields=fields, limit=limit)
            collstats = self.dbcon(dbname).command("collstats", collname)
            self.render(
                "documentlist.html",
                doc_list=doc_list,
                dbname=dbname,
                collname=collname,
                collstats=collstats
            )
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.DocList.get", str(e))
            self.write("Something is wrong!")


class Doc(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self, dbname, collname, docid):
        try:
            doc = self.dbcon(dbname)[collname].find_one(
                {"_id": pymongo.son_manipulator.ObjectId(docid)})

            self.render("document.html",
                doc=doc,
                dbname=dbname,
                collname=collname
            )
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.Doc.get", str(e))
            self.write("Something is wrong!")


class DocRemove(BaseHandler):
    @tornado.web.authenticated
    def get(self, dbname, collname, docid):
        """doc=db_conn[collname].find_one(
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
        try:
            doc = self.dbcon(dbname)[collname].find_one(
                {"_id": pymongo.son_manipulator.ObjectId(docid)})

            formdoc = json.dumps(doc, default=json_util.default)

            self.render("documentedit.html",
                formdoc=formdoc,
                dbname=dbname,
                docid=docid,
                collname=collname,
            )
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.DocEdit.get", str(e))
            self.write("Something is wrong!")

    @tornado.web.authenticated
    def post(self, dbname, collname, docid):
        data = self.get_arguments("jsonData", False)
        save_data = json.loads(data[0], object_hook=json_util.object_hook)
        try:
            self.dbcon(dbname)[collname].save(save_data)
            self.redirect("/%s/%s" % (dbname, collname))
        except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
            self.logger.error("handlers.DocEdit.post", str(e))
            self.write("Something is wrong!")


class DocImport(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self, dbname, collname):
        self.write("""
            <form method='post' enctype='multipart/form-data'>
                <input type='file' name='data'>
                <input type='submit'>
            </form>
        """)

    @tornado.web.authenticated
    def post(self, dbname, collname):
        dosya = self.request.files["data"][0]
        with open(dosya["filename"], "w") as f:
            f.write(dosya["body"])
        self.write("%s" % (self.import_db(dbname, collname, dosya["filename"])))


class DocExport(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self, dbname, collname):
        self.write("%s" % (str(self.export(dbname, collname))))


class Upload(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self, dbname):
        self.write("""
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="gfs">
                <input type="submit">
            </form>
        """)

    @tornado.web.authenticated
    def post(self, dbname):
        file = self.request.files["gfs"][0]
        self.write(file["filename"])
        print self.upload_to_gridfs(dbname.files, file=file)


class Download(BaseHandler, modules):
    @tornado.web.authenticated
    def get(self, dbname, filename):
        gfs = self.get_file(self.dbcon(dbname).files, filename)
        self.set_header('Content-Disposition', 'attachment; filename=%s' % gfs.name)
        self.write(gfs.read())


class SystemJS(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("""
            <form method="post">
                <input type="text" name="name"><br>
                <input type="hidden" name="dbname" value="deneme">
                <textarea name="js" cols="500" rows="500"></textarea><br>
                <input type="submit">
            </form>
        """)

    @tornado.web.authenticated
    def post(self):
        # Listeleme self.db[dbname].system_js.list()
        name = self.get_argument("name", None)
        dbname = self.get_argument("dbname", None)
        js = self.get_argument("js", None)

        if name and dbname and js:
            try:
                self.dbcon(dbname).system_js[name] = js
                self.write("%s function is ready." % name)
            except (ConnectionFailure, AutoReconnect, OperationFailure) as e:
                self.logger.error("handlers.SystemJS.post", str(e))
                self.write("Something is wrong!")
        else:
            self.write("Check form values")


class Jobs(BaseHandler):
    def post(self, db, coll):
        if db and coll:
            insert = self.dbcon(db).system.profile.find({"ns": "%s.%s" % (db, coll), "op": "insert"})
            update = self.dbcon(db).system.profile.find({"ns": "%s.%s" % (db, coll), "op": "update"})
            query = self.dbcon(db).system.profile.find({"ns": "%s.%s" % (db, coll), "op": "query"})

            data = {}
            data["insert"] = []
            data["update"] = []
            data["query"] = []

            for i in insert:
                if i.get("ts", None):
                    i["ts"] = i["ts"].isoformat()
                data["insert"].append(i)

            for i in update:
                if i.get("ts", None):
                    i["ts"] = i["ts"].isoformat()
                data["update"].append(i)

            for i in query:
                if i.get("ts", None):
                    i["ts"] = i["ts"].isoformat()
                data["query"].append(i)

            self.write(json.dumps(data, default=json_util.default))
