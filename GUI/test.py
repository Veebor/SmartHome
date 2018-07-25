import tornado.ioloop
import tornado.web
import os


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", title="Smarthome")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
        ]
        settings = {
            "debug": True,
            "static_path": os.path.join(os.path.dirname(__file__), "static")
        }
        tornado.web.Application.__init__(self, handlers, **settings)


http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(8080)
tornado.ioloop.IOLoop.instance().start()
