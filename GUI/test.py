import tornado.ioloop
import tornado.web
import tornado.escape
import os
import base64
import time
import json

# TODO add DB info and connection

cookie_code = base64.b64encode(os.urandom(50)).decode('ascii')
print("Cookie code: " + cookie_code)


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
        data = json.loads(self.request.body)
        user = base64.b64decode(data['myUser']).decode('utf-8')
        password = base64.b64decode(data['myPass']).decode('utf-8')
        print(user)
        print(password)
        if user == "Luca" and password == "ciccio":
            print(user + " gained access")
            self.set_secure_cookie("CookieMonster", 'Luca', expires_days=7)
            # self.redirect("/root", status=302)
        elif user == "Fede" and password == "pippo":
            print(user + " gained access")
            self.set_secure_cookie("CookieMonster", 'Fede', expires_days=7)
            # self.redirect("/root1", status=302)
        else:
            print("Wrong password")
            self.write('403 Forbidden')

    def get(self):
        self.redirect("/")


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("CookieMonster")
        self.write('You are logged-out')
        self.redirect("/")

class SubmitInfoHandler(BaseHandler):
    def post(self):
        data = json.loads(self.request.body)
        name = base64.b64decode(data['myName']).decode('utf-8')
        password = base64.b64decode(data['myPass']).decode('utf-8')
        email = base64.b64decode(data['myEmail']).decode('utf-8')
        phone = base64.b64decode(data['myPhone']).decode('utf-8')
        gender = base64.b64decode(data['myGender']).decode('utf-8')
        date_of_birth = base64.b64decode(data['myBirthday']).decode('utf-8')
        comments = base64.b64decode(data['myComments']).decode('utf-8')
        
    def get(self):
        self.redirect("/")



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
            (r'/submit', SubmitInfoHandler)
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
    http_server = tornado.httpserver.HTTPServer(Application(),
                                                #ssl_options={
                                                #"certfile": "/cert.pem",
                                                #"keyfile": "/privkey.pem",
                                                #})
                                                )
                                              
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
except KeyboardInterrupt:
    print("\nClosing...")
    time.sleep(2)
    exit()
except Exception as global_error:
    print(global_error)
    exit(1)
