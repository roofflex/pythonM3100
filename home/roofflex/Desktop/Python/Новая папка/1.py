import tornado.ioloop
import tornado.autoreload
import tornado.web


class Handshake(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def post(self):
        type = self.get_argument("type")
        group_id = self.get_argument("group_id")
        if type == "confirmation" and group_id == "145065982":
            result = "29d32f3c"
            self.write(result)


def make_app():
    return tornado.web.Application([(r"/handshake", Handshake)])

def main():
    app = make_app()
    app.listen(8888)
    tornado.autoreload.start()
    tornado.ioloop.IOLoop.current().start()

if __name__=="__main__":
    main()