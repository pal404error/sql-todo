from flask import Flask, render_template, request, redirect, session, g
import sqlite3
import uuid
import os

app = Flask(__name__)
app.secret_key = 'dev'  # Replace in production

DATABASE = 'todo.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db:
        db.close()

@app.route('/')
def index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                          (username, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    db = get_db()
    tasks = db.execute('SELECT * FROM tasks').fetchall()
    return render_template('dashboard.html', tasks=tasks, username=session.get('username'))

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form.get('description', '')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority', 'Medium')
    status = 'todo'
    user_id = session.get('user_id')
    
    db = get_db()
    db.execute('INSERT INTO tasks (id, title, description, status, due_date, created_by, assignee) VALUES (?, ?, ?, ?, ?, ?, ?)',
               (str(uuid.uuid4()), title, description, status, due_date, user_id, user_id))
    db.commit()
    return redirect('/dashboard')

@app.route('/complete/<task_id>')
def complete_task(task_id):
    db = get_db()
    db.execute('UPDATE tasks SET status = "done" WHERE id = ?', (task_id,))
    db.commit()
    return redirect('/dashboard')

@app.route('/delete/<task_id>')
def delete_task(task_id):
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    return redirect('/dashboard')

# =============================
# ✅ ADMIN FUNCTIONALITY BELOW
# =============================

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ? AND is_admin = 1',
                          (username, password)).fetchone()
        if user:
            session['admin_user'] = user['username']
            return redirect('/admin/create-user')
        else:
            return render_template('admin_login.html', error="Invalid admin credentials.")
    return render_template('admin_login.html')


@app.route('/admin/create-user', methods=['GET', 'POST'])
def create_user_by_admin():
    if session.get('admin_user') is None:
        return redirect('/admin')

    if request.method == 'POST':
        user_id = str(uuid.uuid4())
        username = request.form['username']
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        is_admin = 1 if request.form.get('is_admin') else 0

        db = get_db()
        db.execute('INSERT INTO users (id, username, name, email, password, is_admin) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, username, name, email, password, is_admin))
        db.commit()
        return redirect('/dashboard')
    
    return render_template('admin_create.html')

if __name__ == '__main__':
    app.run(debug=True)
