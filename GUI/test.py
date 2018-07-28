#import signal
import tornado.ioloop
import tornado.web
import os

TIMEOUT = 5

def interrupted(signum, frame):
    print("TRAVIS")
    exit(0)
#signal.signal(signal.SIGALRM, interrupted)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", title="Smarthome")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
            (r'/', MainHandler),
        ]
        settings = {
            "debug": True,
            "static_path": os.path.join(os.path.dirname(__file__), "static")
        }
        tornado.web.Application.__init__(self, handlers, **settings)

print("OK")
print("Build succeded!")
#signal.alarm(TIMEOUT)
travis = int(input("Write 1: "))
#signal.alarm(0)

http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(8080)
tornado.ioloop.IOLoop.instance().start()


