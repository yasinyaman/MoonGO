from helpers import BaseHandler
import bcrypt
import tornado.web
import tornado.escape
import time

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

        if self.get_argument("username", False):
            username = self.get_argument("username")
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
            username=username,
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
    def get(self):
        self.sysdb.moongo_sys.users.remove({"username":self.current_user["username"]})
        self.clear_cookie("current_user")
        self.redirect("/")

class UpdateHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/")
        else:
            user_info = self.sysdb.moongo_sys.users.find_one({"username":self.current_user["username"]})
            db_info = self.sysdb.moongo_sys.userdbs.find({"user":self.current_user["username"]})
            self.render("update.html",user_info = user_info, db_info = db_info )


    def post(self):
        if self.get_argument("name", False):
            name = self.get_argument("name")
        else:
            self.write("Name required")
            return

        if self.get_argument("username", False):
            username = self.get_argument("username")
        else:
            self.write("Username required")
            return


        if self.get_argument("mail", False):
            mail = self.get_argument("mail")
        else:
            self.write("Mail is required")
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
