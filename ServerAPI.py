try:
    import tornado.ioloop
    import tornado.web
    import tornado.escape
except ImportError:
    print("Install Tornado first!")
    exit(0)
import os


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('SmartHome API is Working!')


class LoginHandler(tornado.web.RequestHandler):
    def get(self, user_sha256=None, password_sha256=None):
        self.user = user_sha256
        self.password = password_sha256
        # TODO: Check in DB
        logged_in = True
        print('User: ' + self.user + ' Password: ' + self.password)
        if logged_in:
            token = 'Something random'
            response = {'status': 'OK',
                        'token': token}
            self.write(response)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            # (r'/home', HomeHandler),
            # (r'/userdata', UserHandler),
            (r"/login/(.*)/(.*)", LoginHandler)
        ]
        tornado.web.Application.__init__(self, handlers)  # **settings

http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(3000)
tornado.ioloop.IOLoop.instance().start()
