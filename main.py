import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
from tornado.web import Application, RequestHandler
import time
import datetime
import pymysql
from bushu import get_user_message

define('port', type=int, default=8000, multiple=False)
# parse_config_file('config')


def mysql_connect(user_db):
    db = pymysql.connect(
        host='localhost',
        user='root',
        password=' ',
        db=user_db,
    )
    return db


class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        msg = self.get_cookie("msg")
        print(msg)
        if msg == "login":
            self.render("./templates/login.html")
        elif msg == "false":
            self.write('wrong!')
        elif msg == "relogin":
            self.write("relogin!")

    def post(self, *args, **kwargs):
        pass


class JumpHandler(RequestHandler):
    def get(self, *args, **kwargs):
        msg = self.get_cookie("msg")
        self.render(
            "./templates/index.html",
            now_time=(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            msg=msg)

    def post(self, *args, **kwargs):
        pass


class LoginHandler(RequestHandler):
    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        uname = self.get_arguments('uname')[0]
        upwd = self.get_arguments('upwd')[0]
        user_db = "t_test"
        conn = mysql_connect(user_db)
        cursor = conn.cursor()
        sql = """
        select * from {} where uname = '{}' and upwd = '{}'
        """.format(user_db, uname, upwd)
        user_message = cursor.execute(sql)
        if user_message:
            self.redirect('/change')  # 页面跳转
        else:
            self.set_cookie(name='msg',
                            value='false',
                            expires=time.time() + 60)
            self.redirect('/index')


class ChangeHandler(RequestHandler):
    def get(self, *args, **kwargs):
        html = '''
        <head>
                <title>bushu</title>
            </head>
            <h2>bushu</h2>
            <form method=post action=/bushu enctype=multipart/form-data>
                <p>
                    手机号:<input type=text name=uname>
                </p>
                <p>
                    密码:&nbsp;&nbsp;&nbsp;<input type=password name=upwd>
                </p>
                <p>
                    步数:&nbsp;&nbsp;&nbsp;<input type=text name=bushu>
                </p>
                <p>
                    <input type=submit value=提交>
                </p>
            </form>
        '''
        self.write(html)


class BushuHandler(RequestHandler):
    def post(self, *args, **kwargs):
        uname = self.get_arguments('uname')[0]
        upwd = self.get_arguments('upwd')[0]
        bushu = self.get_arguments('bushu')[0]
        now = (datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        print(bushu)
        message = get_user_message(uname, upwd, now, step=bushu)
        if message:
            self.set_cookie(name='msg',
                            value="succsess",
                            expires=time.time() + 60)

        else:
            message = ""
            self.set_cookie(name='msg', value='fail', expires=time.time() + 60)

        self.send_message(message)
        self.redirect('/')

    def send_message(self, message):
        return message


if __name__ == "__main__":
    options.parse_command_line()
    settings = {"template_path": "./templates", "static_path": "./static"}
    url_list = [
        ('/', JumpHandler),
        ('/index', IndexHandler),
        ('/login', LoginHandler),
        ('/change', ChangeHandler),
        ('/bushu', BushuHandler),
        (r'/favicon.ico', {
            'path': './static/favicon.ico'
        }),
    ]

    app = Application(url_list, settings=settings, debug=True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
