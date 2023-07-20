from flask import Flask, render_template, request, redirect
from datetime import datetime
from flask import g
import psycopg2

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = psycopg2.connect(
                dbname='gerencer',
                user='postgres',
                password='Nofaka12',
                host='localhost',
                port='5432'
            )
        except psycopg2.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            db = None
    return db

# Função para criar a tabela "tasks" se não existir
def create_tasks_table():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL,
            start_datetime TIMESTAMP NOT NULL,
            end_datetime TIMESTAMP NOT NULL,
            completed BOOLEAN DEFAULT FALSE
        )
    ''')
    db.commit()

# Função para fechar a conexão com o banco de dados
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('SELECT id, task, start_datetime, end_datetime, completed FROM tasks')
    tasks = cursor.fetchall()
    
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add():
    db = get_db()
    cursor = db.cursor()

    task = request.form['task']
    start_datetime = datetime.strptime(request.form['start_datetime'], '%Y-%m-%dT%H:%M')
    end_datetime = datetime.strptime(request.form['end_datetime'], '%Y-%m-%dT%H:%M')

    cursor.execute('INSERT INTO tasks (task, start_datetime, end_datetime) VALUES (%s, %s, %s)',
                   (task, start_datetime, end_datetime))
    db.commit()

    return redirect('/')
@app.route('/delete/<int:task_id>')
def delete(task_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
    db.commit()
    
    return redirect('/')

@app.route('/complete/<int:task_id>', methods=['POST'])
def complete(task_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('UPDATE tasks SET completed = TRUE WHERE id = %s', (task_id,))
    db.commit()

    return redirect('/')




if __name__ == '__main__':
    app.run()
