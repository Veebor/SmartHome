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
    def get(self):
        self.req_path = self.request.path
        self.write(self.req_path)
        req_array = self.req_path.split('/')
        print(req_array)
        self.user = req_array[2]
        self.password = req_array[3]
        print('User: ' + self.user + ' Password: ' + self.password)
        # TODO: Check in DB
        # TODO: return special code to login


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            # (r'/home', HomeHandler),
            # (r'/userdata', UserHandler),
            (r"/login/.*/.*", LoginHandler)
        ]
        tornado.web.Application.__init__(self, handlers)  # **settings

http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(3000)
tornado.ioloop.IOLoop.instance().start()