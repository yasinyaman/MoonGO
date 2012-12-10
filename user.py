#!/usr/bin/env python
#-*- coding:utf-8 -*-

from helpers import BaseHandler
import bcrypt
import tornado.web
import tornado.escape
import time
import hashlib
from helpers import *

class RegisterHandler(BaseHandler):
    @noauth
    def get(self,key=None):
        invitation = self.sysdb.moongo_sys.user_invitation.find_one({"key":key})
        if invitation:
            self.render("register.html", invitation = invitation)
        else:
            self.write("Not found invitation")

    @noauth
    def post(self,key=None):
        invitation = self.sysdb.moongo_sys.user_invitation.find_one({"key":key})
        if invitation:
            name = self.get_argument("name", None)
            username = self.get_argument("username", None)
            password = self.get_argument("password", None)
            confirm_password = self.get_argument("confirm_password", None)
            mail = self.get_argument("mail", None)

            if not name:
                self.write("Name required")
                return

            if not username:
                self.write("Username required")
                return

            if not password:
                self.write("Password required")
                return

            if not confirm_password:
                self.write("Confirm Password required")
                return

            if confirm_password != password:
                self.write("Passwords not match")
                return
            

            if not mail:
                self.write("Mail is required")
                return

            if not modules().verify_mail(mail):
                self.write("Check mail adress. Its not acceptable.")
                return


            user = dict(
                    name=name,
                    username=username,
                    password=bcrypt.hashpw(password, bcrypt.gensalt()),
                    mail=mail
            )

            self.sysdb.moongo_sys.users.save(user)
            self.sysdb.moongo_sys.userinvitation.remove({"key":key})
            self.redirect("/auth/login")

        else:
            self.write("Not found invitation")


class LoginHandler(BaseHandler):
    @noauth
    def get(self):
        self.render("login.html")
    @noauth
    def post(self):
        username = self.get_argument("username", False)
        password = self.get_argument("password", False)
        if username and password:
            user = self.sysdb.moongo_sys.users.find_one({"username": username},
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


class RemoveHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.sysdb.moongo_sys.users.remove({"username":self.current_user["username"]})
        self.sysdb.moongo_sys.userdbs.remove({"user":self.current_user["username"]})
        self.clear_cookie("current_user")
        self.redirect("/")

class UpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if not self.current_user:
            self.redirect("/")
        else:
            user_info = self.sysdb.moongo_sys.users.find_one({"username":self.current_user["username"]})
            db_info = self.sysdb.moongo_sys.userdbs.find({"user":self.current_user["username"]})
            self.render("update.html",user_info = user_info, db_info = db_info )

    @tornado.web.authenticated
    def post(self):
        name = self.get_argument("name", None)
        username = self.get_argument("username", None)
        mail = self.get_argument("mail", None)


        if not name:
            self.write("Name required")
            return

        if not username:
            self.write("Username required")
            return

        if not mail:
            self.write("Mail is required")
            return

        if not modules().verify_mail(mail):
            self.write("Check your mail adress. Its not acceptable")
            return

        user_info = self.sysdb.moongo_sys.users.find_one({"username":self.current_user["username"]})

        user = dict(
            _id=user_info["_id"],
            name=name,
            username=username,
            mail=mail
        )

        self.sysdb.moongo_sys.users.save(user)
        self.redirect("/auth/login")



class RecoveryHandler(BaseHandler, modules):
    @noauth
    def get(self):
        self.write("""
            <form method="post">
                <input type="text" name="email">
                <input type="submit">
            </form>
        """)

    @noauth
    def post(self):

        mail = self.get_argument("email")
        if not modules().verify_mail(mail):
            self.write("Check your mail adress. Its wrong")
            return

        user_info = self.sysdb.moongo_sys.users.find_one({"mail":mail}) # Hacı zaten şifreyi unuttuysa nasıl giriş yapsın?
        key = hashlib.md5(mail + user_info["username"] + str(time.time())).hexdigest()
        if user_info:
            self.sysdb.moongo_sys.user_recovery.save({"mail":mail, "key":key, "username":user_info["username"]})
            mail_text = """ Dear %s , \n Recovery adrress: %s/auth/reset/%s""" %(user_info["name"],self.settings["site_url"],key)
            sub = "Password recovery"
            self.mailSender(mail, sub, mail_text) 
            self.write("Send Mail")
        else:
            self.write("HATA")


class PasswordResetHandler(BaseHandler, modules):
    @noauth
    def get(self,key):
        recovery_info = self.sysdb.moongo_sys.user_recovery.find_one({"key":key})
        if recovery_info:
            self.write("""
                <form method="post">
                    <input type="text" name="password">
                    <input type="text" name="confirm_password">
                    <input type="submit">
                </form>
            """)
        else:
            self.write("HATA")

    @noauth
    def post(self,key):
        recovery_info = self.sysdb.moongo_sys.user_recovery.find_one({"key":key})

        if recovery_info:
            user_info = self.sysdb.moongo_sys.users.find_one({"mail":recovery_info["mail"]})
            password = self.get_argument("password", None)
            confirm_password = self.get_argument("confirm_password", None)

            if not password:
                self.write("Password required")
                return

            if not confirm_password:
                self.write("Confirm Password required")
                return

            if not confirm_password != password:
                self.write("Password not match")
                return

            user_info["password"] = bcrypt.hashpw(password, bcrypt.gensalt()),
            self.sysdb.moongo_sys.users.save(user_info)
            self.sysdb.moongo_sys.user_recovery.remove({"key":key})
            self.redirect("/auth/login")
        else:
            self.write("This key is not valid.")

class Authorizing(BaseHandler, modules):
    @tornado.web.authenticated
    @root_control
    def get(self):
        self.write("""
            <form method="post">
                <input type="text"  value="username" name="username">
                <input type="text" value="authorizing" name="authorizing">
                <input type="submit">
            </form>
        """)
    @tornado.web.authenticated
    @root_control
    def post(self):
        username = self.get_argument("username")
        authorizing = self.get_argument("authorizing")
        self.sysdb.moongo_sys.user_authorizing.save({"username":username, "authorizing":authorizing})

class InvitationHandler(BaseHandler, modules):
    @tornado.web.authenticated
    @root_control
    def get(self):
        self.write("""
            <form method="post">
                <input type="text" name="email">
                <input type="submit">
            </form>
        """)

    @tornado.web.authenticated
    @root_control
    def post(self):
        mail = self.get_argument("email")
        key = hashlib.md5(mail + str(time.time())).hexdigest()
        self.sysdb.moongo_sys.user_invitation.save({"mail":mail, "key":key})
        mail_text = """ Dear Users , \n invitation adress: %s/auth/register/%s""" %(self.settings["site_url"],key)
        sub = "Moongo invitation"
        self.mailSender(mail, sub, mail_text) 
        self.write("Send Mail")

        

