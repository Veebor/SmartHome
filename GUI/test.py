import signal
import tornado.ioloop
import tornado.web
import os
import base64
import time

TIMEOUT = 5

cookie_code = base64.b64encode(os.urandom(50)).decode('ascii')
print("Cookie code: " + cookie_code)


def interrupted(signum, frame):
    print("TRAVIS")
    exit(0)


signal.signal(signal.SIGALRM, interrupted)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", title="Smarthome")


class RootHandler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("The_password_cookie"):
            print("Someone is trying to gain access without password!")
            self.render("index.html", title="Smarthome")
        else:
            self.render("static/root.html", title="User 1")


class Root1Handler(tornado.web.RequestHandler):
    def get(self):
        if not self.get_secure_cookie("The_password_cookie1"):
            print("Someone is trying to gain access without password!")
            self.render("index.html", title="Smarthome")
        else:
            self.render("static/root1.html", title="User 2")


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("Login page", title="Login") # TODO create login page
        user = "xxxx" # TODO get user from login page
        password = "xxxx" # TODO get password from login page
        if user == "User 1" and password == "Psw user 1":
            self.set_secure_cookie("The_password_cookie", expires_days=7)
        elif user == "User 2" and password == "Psw user 2":
            self.set_secure_cookie("The_password_cookie1", expires_days=7)
        else:
            print("Wrong password")
            self.write('403 Forbidden')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
            (r'/', MainHandler),
            (r'/root.html', RootHandler),
            (r'/root1.html', Root1Handler),
            (r'/login', LoginHandler)
        ]
        settings = {
            "debug": True,
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "cookie_secret": cookie_code
        }
        tornado.web.Application.__init__(self, handlers, **settings)


print("OK")
print("Build succeded!")
signal.alarm(TIMEOUT)
travis = int(input("Write 1: "))
signal.alarm(0)

try:
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
except KeyboardInterrupt:
    print("\nClosing...")
    time.sleep(2)
    exit()
except Exception as global_error:
    print(global_error)
    exit(1)