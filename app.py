
from flask import Flask, render_template, redirect, url_for, request 
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Caminho do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

# Modelo da Tabela
class Pessoa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    sexo = db.Column(db.String(20))
    data_nascimento = db.Column(db.String(20))
    cidade = db.Column(db.String(100))

@app.route('/')
def index():
    pessoas = Pessoa.query.all()
    return render_template('index.html', pessoas=pessoas)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nova = Pessoa(
            nome=request.form['nome'],
            sexo=request.form['sexo'],
            data_nascimento=request.form['data_nascimento'],
            cidade=request.form['cidade']
        )
        db.session.add(nova)
        db.session.commit()
        return redirect(url_for('index'))
        
    return render_template('cadastro.html') 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 