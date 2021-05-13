import tornado.httpserver
import tornado.ioloop
from tornado.options import define, options
from tornado.web import Application, RequestHandler
import time
import datetime
import pymysql

define('port', type=int, default=8000, multiple=False)
# parse_config_file('config')


def conn_m():
    conn = pymysql.connect(host='192.168.0.63',
                           port=3306,
                           user='root',
                           passwd='123456',
                           db='t_test')
    cursor = conn.cursor()
    return cursor, conn


class IndexHandler(RequestHandler):
    def get(self, *args, **kwargs):
        msg = self.get_cookie("msg")
        print(msg)
        if msg == "login":
            html = '''
            <head>
                <title>login</title>
            </head>
            <h2>login</h2>
            <form method=post action=/login enctype=multipart/form-data>
                <p>
                    用户名：<input type=text name=uname>
                </p>
                <p>
                    密码：&nbsp;&nbsp;&nbsp;<input type=password name=upwd>
                </p>
                <p>
                    <input type=submit value=提交>
                </p>
            </form>
            '''
            self.write(html)
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
        cursor, _ = conn_m()
        uname = self.get_arguments('uname')[0]
        upwd = self.get_arguments('upwd')[0]
        self.set_cookie(name='uname', value=uname, expires=time.time() + 60)
        self.set_cookie(name='upwd', value=upwd, expires=time.time() + 60)
        if (uname and upwd):
            sql = "select * from user_list where uname='{}'".format(uname)
            cursor.execute(sql)
            userdata = cursor.fetchone()
            cursor.close()
            print(userdata)
            if userdata:
                if userdata[2] == upwd:
                    self.redirect('/python')  # 页面跳转
                else:
                    self.set_cookie(name='msg',
                                    value='false',
                                    expires=time.time() + 60)
                    self.redirect('/register')
            else:
                self.set_cookie(name='msg',
                                value='false',
                                expires=time.time() + 60)
                self.redirect('/register')
        else:
            self.set_cookie(name='msg',
                            value='false',
                            expires=time.time() + 60)
            self.redirect('/index')


class PythonHandler(RequestHandler):
    def get(self, *args, **kwargs):
        uname = self.get_cookie("uname")
        upwd = self.get_cookie("upwd")
        if uname:
            self.render("./templates/user.html", uname=uname, upwd=upwd)
        else:
            self.set_cookie(name='msg',
                            value='relogin',
                            expires=time.time() + 60)
            self.redirect('/index')

    def post(self, *args, **kwargs):
        pass


class RegisterHandler(RequestHandler):
    def get(self, *args, **kwargs):
        html = '''
        <head>
            <title>Register</title>
        </head>
        <h2>Register</h2>
        <form method=post action=/regist enctype=multipart/form-data>
            <p>
                用户名：<input type=text name=uname>
            </p>
            <p>
                密码：&nbsp;&nbsp;&nbsp;<input type=password name=upwd>
            </p>
            <p>
                <input type=submit value=提交>
            </p>
        </form>
        '''
        self.write(html)


class RegistHandler(RequestHandler):
    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        cursor, conn = conn_m()
        uname = self.get_arguments('uname')[0]
        upwd = self.get_arguments('upwd')[0]
        if (uname and upwd):
            sql = "select * from user_list where uname='{}';".format(uname)
            cursor.execute(sql)
            userdata = cursor.fetchall()
            print("r", userdata)
            if not userdata:
                sql = """
                insert into
                user_list (uname,upwd)
                values('{}','{}');""".format(uname, upwd)
                cursor.execute(sql)
                conn.commit()
                cursor.close()
                self.set_cookie(name='msg',
                                value='login',
                                expires=time.time() + 60)
                self.redirect('/index')

            else:
                self.set_cookie(name='msg',
                                value='false',
                                expires=time.time() + 60)
                self.redirect('/index')
        else:
            self.set_cookie(name='msg',
                            value='false',
                            expires=time.time() + 60)
            self.redirect('/index')


if __name__ == "__main__":
    options.parse_command_line()
    settings = {
        "template_path": "./templates",
    }
    url_list = [('/', JumpHandler), ('/index', IndexHandler),
                ('/login', LoginHandler), ('/register', RegisterHandler),
                ('/regist', RegistHandler), ('/python', PythonHandler)]

    app = Application(url_list, debug=True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
