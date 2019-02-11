try:
    import tornado.ioloop
    import tornado.web
    import tornado.escape
except ImportError:
    print("Install Tornado first!")
    exit(0)
import os
import base64
import time
import json
import psycopg2
import hashlib

# TODO Change cookie code after x days

cookie_code = base64.b64encode(os.urandom(50)).decode('ascii')
print("Cookie code: " + cookie_code)

user_accepted = False

global db_working


def chomp(string1):
    string1 = string1.replace("\r", "")
    string1 = string1.replace("\n", "")
    return string1

# READ DBINFO FROM FILE

dirname = os.path.dirname(__file__)

# FILE database.txt IS NEEDED TO RUN THIS PROGRAM

# FOR INFO ABOUT database FILE CONTACT CFV

try:
    filename = os.path.join(dirname, 'database.txt')

    f = open(filename, "r")

    database_data = f.readlines()

    dbhost = chomp(database_data[0])
    user_database = chomp(database_data[1])
    dbuser = chomp(database_data[2])
    dbpassword = chomp(database_data[3])
    db_working = 1

except Exception as file_error:
    print('File not found')
    print(file_error)
    db_working = 0


class Database():
    def __init__(self):
        self.conn = None
        try:
            # CONNECT
            print("CONNECTING...")
            self.conn = psycopg2.connect(host=dbhost, database=user_database,
                                         user=dbuser, password=dbpassword,
                                         connect_timeout=5)
            self.conn.autocommit = True
            print("CONNECTED...")
            global db_working
            db_working = 1
            # CREATE A CURSOR
            self.cur = self.conn.cursor()
            # FIND ALL DATA
            self.cur.execute("SELECT * FROM data")
            self.rows = self.cur.fetchall()
            # self.cur.commit()
        except Exception as database_error:
            db_working = 0
            print(database_error)

    def show_data(self):
        return self.rows

    def user_id(self):
        return [x[3] for x in self.rows]

    def show_users(self):
        try:
            return [x[0] for x in self.rows]
        except:
            return 500

    def show_passwords(self):
        try:
            return [x[1] for x in self.rows]
        except:
            return 500

    def add_data(self, username_to_ins, password_to_ins):
        # INSERT DATA INTO TABLE
        try:
            self.cur.execute("INSERT INTO data(users, passwords, admin) VALUES(%s, %s, 'FALSE')",
                             (hashlib.sha256(username_to_ins.encode())
                              .hexdigest(),
                              hashlib.sha256(password_to_ins.encode())
                              .hexdigest()))
        except Exception as database_insert_error:
            print(database_insert_error)
            self.cur.rollback()

    def close_connection(self):
        self.conn.close()


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        if self.get_secure_cookie('CookieMonster'):
            return self.get_secure_cookie('CookieMonster').decode('ascii')


class MainHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.redirect("/root")
        else:
            self.render("index.html", title="Smarthome")


class RootHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("static/root.html", title="SmartHome Panel")


class LoginHandler(BaseHandler):
    def post(self):
        try:
            global db_working
            if db_working:
                db = Database()
                db_users = db.show_users()
                db_passwords = db.show_passwords()
                if db_users == 500 or db_passwords == 500:
                    db_users = ['9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08']
                    db_passwords = ['9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08']
                    db_working = 0
                else:
                    print('OK')
            else:
                db_users = ['9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08']
                db_passwords = ['9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08']
            data = json.loads(self.request.body)
            user = base64.b64decode(data['myUser']).decode('utf-8')
            password = base64.b64decode(data['myPass']).decode('utf-8')
            user_sha256 = hashlib.sha256(user.encode()).hexdigest()
            password_sha256 = hashlib.sha256(password.encode()).hexdigest()
            # print(user)
            # print(password)
            # When doing request we clear old cookies
            self.clear_cookie("CookieMonster")
            if user_sha256 in db_users:
                index = 0
                for tup in db_users:
                    if user_sha256 in tup:
                        pos = index
                    else:
                        index += 1
                if password_sha256 == db_passwords[pos]:
                    # print(user + " gained access")
                    self.set_secure_cookie("CookieMonster", user, expires_days=7)
                else:
                    self.write("Wrong username or password")
                    self.write("403 Forbidden")
                    time.sleep(2)
            else:
                self.write("Wrong username or password")
                self.write('403 Forbidden')
                time.sleep(2)
            if db_working:
                db.close_connection()
        except Exception as login_error:
            print(login_error)

    def get(self):
        self.redirect("/")


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("CookieMonster")
        self.write('You are logged-out')
        self.redirect("/")


class SubmitInfoHandler(BaseHandler):
    # TODO Post request from JS
    def post(self):
        data = json.loads(self.request.body)
        name = base64.b64decode(data['myName']).decode('utf-8')
        password = base64.b64decode(data['myPass']).decode('utf-8')
        email = base64.b64decode(data['myEmail']).decode('utf-8')
        phone = base64.b64decode(data['myPhone']).decode('utf-8')
        gender = base64.b64decode(data['myGender']).decode('utf-8')
        date_of_birth = base64.b64decode(data['myBirthday']).decode('utf-8')
        comments = base64.b64decode(data['myComments']).decode('utf-8')
        print("User: " + name + " Password: " + password)
        print("Email: " + email + " Phone: " + phone)
        print("Gender: " + gender)
        print("Date of birth: " + date_of_birth)
        print("Comments: " + comments)
        if user_accepted:
            if db_working:
                db = Database()
                db.add_data(name, password)
            else:
                self.write("DB not working. Retry later")
        else:
            print("User not accepted yet")

    # TODO Manage accounts page in HTML
    def get(self):
        if self.current_user == "Luca" or self.current_user == "Fede":
            self.write("Manage accounts")
            time.sleep(1)
            self.render("/static/accounts.html")
        else:
            self.write("Forbidden! You have not the rights \
                    to access this page!")
            time.sleep(2)
            self.redirect("/")


class LightsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("static/index2.html", title="Lights")


class AirconHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("static/index3.html", title="Air-conditoning")


class TVConHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("static/index4.html", title="TV-Controller")


class SensorHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("static/index5.html", title="Sensor")


class FacilHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("static/index6.html", title="Facilities")


class SecHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("static/index8.html", title="Security")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
            (r'/', MainHandler),
            (r'/index.html', MainHandler),
            (r'/root', RootHandler),
            (r'/root1', RootHandler),
            (r'/login', LoginHandler),
            (r'/logout', LogoutHandler),
            (r'/submit', SubmitInfoHandler),
            (r'/lights', LightsHandler),
            (r'/aircon', AirconHandler),
            (r'/tvcon', TVConHandler),
            (r'/sensor', SensorHandler),
            (r'/facil', FacilHandler),
            (r'/sec', SecHandler)
        ]
        settings = {
            "debug": True,
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "cookie_secret": cookie_code,
            "login_url": "/"
        }
        tornado.web.Application.__init__(self, handlers, **settings)


print("OK")
print("Build suceded!")

try:
    # TODO Update certs before production
    http_server = tornado.httpserver.HTTPServer(Application(),
                                                # ssl_options={
                                                # "certfile": "/cert.pem",
                                                # "keyfile": "/privkey.pem",
                                                # })
                                                )
    PORT = int(os.environ['PORT'])
    http_server.listen(PORT)
    tornado.ioloop.IOLoop.instance().start()
except KeyboardInterrupt:
    print("\nClosing...")
    time.sleep(2)
    exit()
except Exception as global_error:
    print(global_error)
    exit(1)
