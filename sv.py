#!python3
# -*- coding: utf-8 -*-

import os
import traceback
import time
from tools import read_str_from_url
from img_size import get_image_size
from flask import (Flask, request, redirect, Response, url_for, 
                    send_from_directory, jsonify, send_file, 
                    render_template, flash, stream_with_context
                    )

app = Flask(__name__)

__ROOT_ = './root/' # '/home/pi/'
__ROOT_ = os.path.abspath(__ROOT_)

BOOK_ROOT = os.path.join(__ROOT_, 'books/')
PIC_ROOT = os.path.join(__ROOT_, 'pics/')
VIDEO_ROOT = os.path.join(__ROOT_, 'videos/')


##############################################################
######################## login ###############################

import base64
from flask_login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin)

app.config["SECRET_KEY"] = "ITSASnrmUTYewqbECRETkutepVC.XddJGrio3fKHFKDkdkls-KDSkdkfpLFDOSF"
login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login_failed'

class User(UserMixin):
    def __init__(self, id, name, passwd, active=True):
        self.id = id
        self.name = name
        self.passwd = passwd
        self.active = active

    def is_active(self):
        return self.active

__s_p_ = {
    '1':User('1', 'happy', 'foothair')
}

def get_from_name(name):
    for v in __s_p_.values():
        if v.name == name:
            return v
    return None

def get_from_id(id):
    if id in __s_p_.keys():
        return __s_p_[id]
    return None

@login_manager.user_loader
def load_user(id):
    ret = get_from_id(id)
    return ret

def __redirect_url():
    return request.args.get('next') or url_for('index') #request.referrer

def __inner_login():
    username = request.form.get('username', '')
    passwd = request.form.get('passwd', '')
    remember = (request.form.get('remember', 'no') == 'yes')
    if username != '' and passwd != '':
        cUser = get_from_name(username)
        if cUser != None and cUser.passwd == passwd:
            if login_user(cUser, remember=remember):
                return True
    return False

@app.route("/login", methods=["GET", "POST"])
def login():
    next = request.args.get('next')
    if request.method == 'POST':
        if __inner_login():
            return redirect(__redirect_url())
        else:
            flash(u'用户名或密码错误')
    return render_template('login.html', next=next)

@app.route('/login_failed')
def login_failed():
    next = __redirect_url()
    return redirect(url_for('login', next=next))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login', next=url_for('index')))

######################## login end ###########################

def secure_filename(s):
    s = s.replace('\\', '_')
    s = s.replace('\n', '_')
    s = s.replace('\r', '_')
    s = s.replace('/', '_')
    s = s.replace('..', '_')
    s = s.replace(' ', '_')
    return s

def secure_pathname(s):
    s = s.replace('\n', '_')
    s = s.replace('\r', '_')
    s = s.replace('..', '_')
    s = s.replace(' ', '_')
    s = s.replace('(', '_')
    s = s.replace(')', '_')
    s = s.replace('[', '_')
    s = s.replace(']', '_')
    return s

def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

def read_line(file_object):
    while True:
        data = file_object.readline()
        if not data:
            break
        yield data

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@app.route('/book/<path:bookname>')
@login_required
def book_detail(bookname):
    bookname = secure_filename(bookname)
    bookpath = os.path.join(BOOK_ROOT, bookname)
    if not bookpath.endswith('.txt'):
        bookpath = bookpath + '.txt'
    f = open(bookpath, 'r', encoding='utf-8')
    c = read_line(f) # read_in_chunks(f)
    return Response(
        stream_with_context(
            stream_template('book_detail.html', content = c)
        )
        )

@app.route('/books')
@login_required
def books():
    res = []
    for i in os.listdir(BOOK_ROOT):
        p = os.path.join(BOOK_ROOT, i)
        if os.path.isfile(p) and i.endswith('.txt'):
            res.append(i[:-4])
    return render_template('book_list.html', books = res)

@app.route('/book_thief', methods=['GET', 'POST'])
@login_required
def book_thief():
    if request.method == 'POST':
        url = request.form.get('url')
        c = read_str_from_url(url)
        return render_template('book_add.html', default = c)
    return render_template('book_thief.html')

@app.route('/book_add', methods=['GET', 'POST'])
@login_required
def book_add():
    if request.method == 'POST':
        c = request.form.get('content')
        n = request.form.get('filename')
        n = secure_filename(n)
        if not n.endswith('.txt'):
            n = n + '.txt'
        pt = os.path.join(BOOK_ROOT, n)
        if os.path.exists(pt):
            pt = pt[:-4]
            pt = pt + str(time.time()) + '.txt'
        with open(pt, 'w', encoding='utf-8') as f:
            f.write(c)
        return redirect(url_for('books'))
    return render_template('book_add.html', default = '-.-')

@app.route('/pic/<path:picname>')
def pic_file(picname):
    picname = secure_pathname(picname)
    filepath = os.path.join(PIC_ROOT, picname)
    filepath = os.path.abspath(filepath)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        p = os.path.dirname(filepath)
        n = os.path.basename(filepath)
        return send_from_directory(p, n)
    return 'null'

@app.route('/gallery/<path:dir>')
def gallery(dir):
    dir = secure_filename(dir)
    path = os.path.join(PIC_ROOT, dir)
    ret = []
    for i in os.listdir(path):
        p = os.path.join(path, i)
        if os.path.exists(p) and os.path.isfile(p):
            try:
                w, h = get_image_size(p)
                if w != None and w > 0 and h > 0:
                    pp = os.path.join(dir, i)
                    pp = pp.replace('\\', '/')
                    t = dict(
                        src = url_for('pic_file', picname=pp),
                        w = w,
                        h = h
                    )
                    ret.append(t)
            except:
                traceback.print_exc()
    return render_template('gallery_t.html', src=ret)

@app.route('/pics')
def pic_list():
    res = []
    for i in os.listdir(PIC_ROOT):
        p = os.path.join(PIC_ROOT, i)
        if os.path.isdir(p):
            res.append(i)
    return render_template('gallery_list.html', picdirs = res)

@app.route('/video_file/<path:name>')
def video_file(name):
    t = secure_filename(name)
    return send_from_directory(r, t)

@app.route('/videos')
def video_list():
    files = []
    root = VIDEO_ROOT
    for i in os.listdir(root):
        p = os.path.join(root, i)
        if os.path.isfile(p):
            files.append(i)
    return render_template('video_list.html', videos=files)

@app.route('/video/<path:name>')
def video_play(name):
    t = secure_filename(name)
    return redirect(url_for('video_file', name=t))

@app.route('/index')
@app.route('/')
@login_required
def index():
    return render_template('index.html')

def main():
    # app.debug = False
    # app.run(host='0.0.0.0')
    app.run()

if __name__ == '__main__':
    main()