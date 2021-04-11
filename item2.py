import time
from flask import Flask, request, render_template, redirect, url_for, session, Response
import os
import base64
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from functools import wraps
import redis

app = Flask(__name__)
tmp = os.urandom(21)
app.secret_key = base64.b64encode(tmp)
users = {}
expiration = 36000
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


class Task:
    max_id = -1

    def __init__(self, content):
        self.id = Task.max_id + 1
        self.content = content
        self.status = False
        self.start_time = time.time()
        self.end_time = None
        Task.max_id += 1

    def to_json(self):
        return {
            "id": self.id,
            "content": self.content,
            "status": int(self.status),
            "start_time": self.start_time,
            "end_time": self.end_time
        }

    def end(self):
        self.end_time = time.time()

    @classmethod
    def list_to_json(cls, tasks):
        return [task.to_json() for task in tasks]


class User:
    user_num = 0
    his_num = 0

    def __init__(self, name, pwd):
        self.name = name
        self.password = pwd
        self.task_num = 0
        self.all_tasks = list()
        self.on_tasks = list()
        self.off_tasks = list()

    def to_json(self):
        return {
            "name": self.name,
            "password": self.password,
            "task_num": int(self.task_num),
            "task": self.all_tasks
        }

    def append(self, item):
        self.all_tasks.append(item)
        self.off_tasks.append(item)
        self.task_num += 1

    def get_task(self, id):
        return self.all_tasks[id]

    def tasks_on(self):
        self.all_tasks = self.on_tasks + self.off_tasks
        self.on_tasks.extend(self.off_tasks)
        self.off_tasks.clear()

    def tasks_on(self):
        self.all_tasks = self.on_tasks + self.off_tasks
        self.off_tasks.extend(self.on_tasks)
        self.on_tasks.clear()

    def clear_all(self):
        self.all_tasks.clear()
        self.on_tasks.clear()
        self.off_tasks.clear()

    def clear_on(self):
        self.on_tasks.clear()
        self.all_tasks = self.on_tasks + self.off_tasks

    def clear_off(self):
        self.off_tasks.clear()
        self.all_tasks = self.on_tasks + self.off_tasks

    def remove_tasks(self, task_id):
        if self.all_tasks[task_id].status:
            self.on_tasks.remove(self.all_tasks[task_id])
        if not self.all_tasks[task_id].status:
            self.off_tasks.remove(self.all_tasks[task_id])
        self.all_tasks.remove(self.all_tasks[task_id])
        cnt = 0
        for num_task in self.all_tasks:
            if num_task.id != cnt:
                num_task.id = cnt
            cnt += 1
        Task.max_id -= 1

    def task_off(self, task_id):
        self.all_tasks[task_id].status = True
        self.off_tasks.remove(self.all_tasks[task_id])
        self.on_tasks.append(self.all_tasks[task_id])

    def task_on(self, task_id):
        self.all_tasks[task_id].status = False
        self.off_tasks.append(self.all_tasks[task_id])
        self.on_tasks.remove(self.all_tasks[task_id])

    @classmethod
    def list_to_json(cls, users):
        return [user.to_json() for user in users]


def make_resp(data, status=200, message="success"):
    return {
        "status": status,
        "message": message,
        "data": data
    }


def is_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = session.get('token')
        if token:
            s = Serializer(app.secret_key)
            data = s.loads(token)
            now_time = time.time()
            if data['end'] < now_time:
                return '登录信息已过期'
        else:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def jud_user(name, pwd, user):
    if name == user.name and pwd == user.password:
        return True


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('登录.html')

    user_name = request.form.get('user')
    pwd = request.form.get('pwd')
    s = Serializer(app.secret_key, expires_in=expiration)
    s_time = time.time()
    e_time = s_time + expiration
    token = s.dumps({'user': user_name, 'pwd': pwd, 'start': s_time, 'end': e_time}).decode('utf-8')
    # print(data)
    if jud_user(user_name, pwd, users[user_name]):
        session['token'] = token
        return redirect(url_for('subscriber', user_name=user_name))
    else:
        return render_template('登录.html', msg='用户名或密码错误')


@app.route("/resign", methods=["POST", "GET"])
def resign():
    if request.method == "GET":
        return render_template("注册.html")
    user = request.form.get('user')
    pwd = request.form.get('pwd')
    new_user = User(user, pwd)
    # s = Serializer(app.secret_key, expires_in=expiration)
    # token = s.dumps({'user': user, 'pwd': pwd})
    # print(token)
    users[user] = new_user
    return redirect(url_for('login'))


@app.route('/logout')
@is_login
def logout():
    session.pop('token', None)
    print("?")
    return "<h1>再见<h1>"


@app.route('/subscriber/?<string:user_name>', methods=['GET'])
@is_login
def subscriber(user_name):
    if request.method == 'GET':
        return "<h1>Hello! %s<h1>" % users[user_name].name


@app.route("/subscriber/tasks/<string:user_name>", methods=["GET", "POST"])
@is_login
def task_list(user_name):
    if request.method == "GET":
        data = Task.list_to_json(users[user_name].all_tasks)
        resp = make_resp(data)
        return resp
    if request.method == "POST":
        content = request.form['content']
        new_task = Task(content)
        users[user_name].append(new_task)

        data = new_task.to_json()
        resp = make_resp(data)
        return resp


@app.route("/subscriber/task/<string:user_name>/<int:id>", methods=["GET", "PUT", "DELETE"])
@is_login
def tasks(user_name, id):
    if request.method == "GET":
        operation = "single"
        cur = str(time.time())
        result = operation + '/' + cur + '/' +str(id)
        r.lpush("history", result)
        return make_resp(users[user_name].all_tasks[id].to_json())
    if request.method == "PUT":
        if users[user_name].all_tasks[id].status:
            users[user_name].task_on(id)
        if not users[user_name].all_tasks[id].status:
            users[user_name].task_off(id)
        return make_resp(users[user_name].all_tasks[id].to_json())
    if request.method == "DELETE":
        users[user_name].remove_tasks(id)
        data = Task.list_to_json(users[user_name].all_tasks)
        resp = make_resp(data)
        return resp


@app.route("/subscriber/tasks/<string:user_name>/<string:op>/", methods=["GET", "PUT", "DELETE"])
@is_login
def task(user_name, op):
    page = int(request.args.get('page'))
    if not page:
        page = 1
    if request.method == "GET":
        if op == "all":
            operation = "all"
            cur = str(time.time())
            result = operation + '/' + cur
            r.lpush("history", result)
            User.his_num += 1
            if User.his_num > 10:
                User.his_num -= 1
                x = r.rpop()

            temp = list()
            temp.append(users[user_name].all_tasks[page-1])
            data = Task.list_to_json(temp)
            resp = make_resp(data)
            return resp
        if op == "on":
            operation = "on"
            cur = str(time.time())
            result = operation + '/' + cur
            r.lpush("history", result)
            User.his_num += 1
            if User.his_num > 10:
                User.his_num -= 1
                x = r.rpop()
            data = Task.list_to_json(users[user_name].on_tasks[page-1])
            resp = make_resp(data)
            return resp
        if op == "off":
            operation = "off"
            cur = str(time.time())
            result = operation + '/' + cur
            r.lpush("history", result)
            User.his_num += 1
            if User.his_num > 10:
                User.his_num -= 1
                x = r.rpop()
            data = Task.list_to_json(users[user_name].off_tasks[page-1])
            resp = make_resp(data)
            return resp
    if request.method == "PUT":
        if op == "on":
            for duties in users[user_name].off_tasks:
                duties.status = not duties.status
                duties.end()
            users[user_name].tasks_on()
            data = Task.list_to_json(users[user_name].all_tasks)
            resp = make_resp(data)
            return resp
        if op == "off":
            for duties in users[user_name].on_tasks:
                duties.status = not duties.status
                duties.end()
            users[user_name].tasks_off()
            data = Task.list_to_json(users[user_name].all_tasks)
            resp = make_resp(data)
            return resp
    if request.method == "DELETE":
        if op == "all":
            users[user_name].clear_all()
            data = Task.list_to_json(users[user_name].all_tasks)
            resp = make_resp(data)
            return resp
        if op == "on":
            users[user_name].clear_on()
            data = Task.list_to_json(users[user_name].all_tasks)
            resp = make_resp(data)
            return resp
        if op == "off":
            users[user_name].clear_off()
            data = Task.list_to_json(users[user_name].all_tasks)
            resp = make_resp(data)
            return resp


app.run(debug=True)