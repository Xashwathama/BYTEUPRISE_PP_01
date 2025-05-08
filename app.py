import webbrowser
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import threading

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Task Model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Task {self.title}>'

# Updated index route with filtering
@app.route('/')
def index():
    search = request.args.get('search')
    status = request.args.get('status')
    priority = request.args.get('priority')

    query = Task.query

    if search:
        query = query.filter(Task.title.ilike(f'%{search}%'))

    if status:
        if status == 'completed':
            query = query.filter_by(completed=True)
        elif status == 'pending':
            query = query.filter_by(completed=False)

    if priority:
        query = query.filter_by(priority=priority)

    tasks = query.order_by(Task.due_date).all()
    return render_template('index.html', tasks=tasks, search=search, status=status, priority=priority)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']
    description = request.form.get('description')
    priority = request.form.get('priority')
    due_date_str = request.form.get('due_date')

    due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None

    new_task = Task(title=title, description=description, priority=priority, due_date=due_date)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
def toggle_status(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

# Function to open the browser
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")  # Open the browser

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database is created
    
    # Open browser after 1 second delay
    threading.Timer(1, open_browser).start()

    # Run the Flask app
    app.run(debug=False)  # Set debug=False to prevent automatic browser opening from Flask
