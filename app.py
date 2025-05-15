from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-key"

basedir = os.path.abspath(os.path.dirname(__file__))  # Get the directory of the current file
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:HybridPower.246@my-db.cabieyu4wy2m.us-east-1.rds.amazonaws.com/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)

# To-do routes
@app.route('/')
def home():
    status = request.args.get('filter', 'all')
    if status == 'pending':
        tasks = Task.query.filter_by(completed=False).order_by(Task.id).all()
    elif status == 'completed':
        tasks = Task.query.filter_by(completed=True).order_by(Task.id).all()
    else:
        tasks = Task.query.order_by(Task.id).all()
    return render_template('todo.html', tasks=tasks, active_filter=status)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('task')
    due_date_str = request.form.get('due_date')
    due_date = None
    if due_date_str:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
    new_task = Task(title=title, due_date=due_date)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/complete/<int:task_id>')
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/api/tasks/<int:task_id>', methods=['POST'])
def api_update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json() or {}

    task.title = data.get('title', task.title)
    due = data.get('due_date', '')
    task.due_date = (
        datetime.strptime(due, '%Y-%m-%d').date()
        if due else None
    )

    db.session.commit()
    return jsonify({
        "id": task.id,
        "title": task.title,
        "due_date": task.due_date.isoformat() if task.due_date else ""
    })

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/clear_all')
def clear_all():
    Task.query.delete()
    db.session.commit()
    return redirect(url_for('home'))

# App entry point
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
