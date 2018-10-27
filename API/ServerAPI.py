try:
    import tornado.ioloop
    import tornado.web
    import tornado.escape
except ImportError:
    print("Install Tornado first!")
    exit(0)
from base64 import b64encode
from os import urandom
import json

# FIXME: WARNING: very dangerous
saved_tokens = []

home_data = 'Hello World!'


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
            random_bytes = urandom(32)
            token = b64encode(random_bytes).decode('utf-8')
            saved_tokens.append(token)
            # FIXME: WARNING: very dangerous
            response = {'status': 'OK',
                        'token': token}
            self.write(response)

    def post(self):
        self.write('Use GET request')


class HomeHandler(tornado.web.RequestHandler):
    def get(self, token=None):
        if token in saved_tokens:
            response = {
                'status': 'OK',
                'data': home_data
            }
        elif token is None:
            response = {
                'status': 'Token missing'
            }
        else:
            response = {
                'status': '403'
            }
        self.write(response)


class AddData(tornado.web.RequestHandler):
    def post(self):
        post_data = json.loads(self.request.body)
        token = post_data['myToken']
        if token in saved_tokens:
                try:
                    test_var = post_data['test_var']
                    print(test_var)
                    # TODO: Save data in DB
                    response = {
                        'status': 'OK'
                    }
                except:
                    response = {
                        'status': '500'
                    }
        elif token is None:
            response = {
                'status': 'Token missing'
            }
        else:
            response = {
                'status': '403'
            }
        self.write(response)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/(.*)/home', HomeHandler),
            # (r'/userdata', UserHandler),
            (r"/login/(.*)/(.*)", LoginHandler)
        ]
        tornado.web.Application.__init__(self, handlers)  # **settings

http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(3000)
tornado.ioloop.IOLoop.instance().start()
