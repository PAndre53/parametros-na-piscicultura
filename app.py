
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuração de mensagens
app.config['SECRET_KEY'] = 'chave-piscicultura'

# Caminho do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(basedir, 'database.db')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ==========================================================
# LIMITES IDEAIS DOS PARÂMETROS
# ==========================================================

PH_MIN = 6.5
PH_MAX = 8.5

TEMPERATURA_MIN = 26.0
TEMPERATURA_MAX = 30.0

OXIGENIO_MIN = 5.0


# ==========================================================
# MODELO DE MEDIÇÃO
# ==========================================================

class Medicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    data = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )

    ph = db.Column(db.Float, nullable=False)

    temperatura = db.Column(
        db.Float,
        nullable=False
    )

    oxigenio = db.Column(
        db.Float,
        nullable=False
    )

    def ph_adequado(self):
        return PH_MIN <= self.ph <= PH_MAX

    def temperatura_adequada(self):
        return TEMPERATURA_MIN <= self.temperatura <= TEMPERATURA_MAX

    def oxigenio_adequado(self):
        return self.oxigenio >= OXIGENIO_MIN

    def esta_adequada(self):
        return (
            self.ph_adequado()
            and self.temperatura_adequada()
            and self.oxigenio_adequado()
        )


# ==========================================================
# MODELO DE MORTALIDADE
# ==========================================================

class Mortalidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    data = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )

    quantidade = db.Column(
        db.Integer,
        nullable=False
    )

    observacao = db.Column(
        db.String(500)
    )


# ==========================================================
# FUNÇÃO PARA GERAR ALERTAS
# ==========================================================

def gerar_alertas(medicao):
    alertas = []

    if medicao.ph < PH_MIN:
        alertas.append(
            f"pH muito baixo: {medicao.ph:.2f}. "
            f"O ideal é entre {PH_MIN} e {PH_MAX}."
        )

    elif medicao.ph > PH_MAX:
        alertas.append(
            f"pH muito alto: {medicao.ph:.2f}. "
            f"O ideal é entre {PH_MIN} e {PH_MAX}."
        )

    if medicao.temperatura < TEMPERATURA_MIN:
        alertas.append(
            f"Temperatura baixa: {medicao.temperatura:.1f} °C. "
            f"O ideal é entre {TEMPERATURA_MIN} e {TEMPERATURA_MAX} °C."
        )

    elif medicao.temperatura > TEMPERATURA_MAX:
        alertas.append(
            f"Temperatura alta: {medicao.temperatura:.1f} °C. "
            f"O ideal é entre {TEMPERATURA_MIN} e {TEMPERATURA_MAX} °C."
        )

    if medicao.oxigenio < OXIGENIO_MIN:
        alertas.append(
            f"Oxigênio baixo: {medicao.oxigenio:.2f} mg/L. "
            f"O mínimo recomendado é {OXIGENIO_MIN} mg/L."
        )

    return alertas


# ==========================================================
# PÁGINA INICIAL
# ==========================================================

@app.route('/')
def index():

    # Medições mais recentes primeiro
    medicoes = Medicao.query.order_by(
        Medicao.data.desc()
    ).all()

    # Registros de mortalidade mais recentes primeiro
    mortalidades = Mortalidade.query.order_by(
        Mortalidade.data.desc()
    ).all()

    # Alertas das medições
    alertas = []

    for medicao in medicoes:
        problemas = gerar_alertas(medicao)

        for problema in problemas:
            alertas.append({
                'data': medicao.data,
                'mensagem': problema
            })

    return render_template(
        'index.html',
        medicoes=medicoes,
        mortalidades=mortalidades,
        alertas=alertas
    )


# ==========================================================
# CADASTRAR MEDIÇÃO
# ==========================================================

@app.route('/medicao', methods=['GET', 'POST'])
def medicao():

    if request.method == 'POST':

        try:
            ph = float(request.form['ph'])
            temperatura = float(request.form['temperatura'])
            oxigenio = float(request.form['oxigenio'])

            nova_medicao = Medicao(
                ph=ph,
                temperatura=temperatura,
                oxigenio=oxigenio
            )

            db.session.add(nova_medicao)
            db.session.commit()

            flash('Medição registrada com sucesso!', 'sucesso')

            return redirect(url_for('index'))

        except ValueError:
            flash(
                'Digite valores numéricos válidos.',
                'erro'
            )

    return render_template('medicao.html')


# ==========================================================
# REGISTRAR MORTALIDADE
# ==========================================================

@app.route('/mortalidade', methods=['GET', 'POST'])
def mortalidade():

    if request.method == 'POST':

        try:
            quantidade = int(
                request.form['quantidade']
            )

            observacao = request.form.get(
                'observacao',
                ''
            )

            if quantidade < 1:
                flash(
                    'A quantidade deve ser maior que zero.',
                    'erro'
                )

                return render_template(
                    'mortalidade.html'
                )

            nova_mortalidade = Mortalidade(
                quantidade=quantidade,
                observacao=observacao
            )

            db.session.add(nova_mortalidade)
            db.session.commit()

            flash(
                'Mortalidade registrada com sucesso!',
                'sucesso'
            )

            return redirect(url_for('index'))

        except ValueError:
            flash(
                'Digite uma quantidade válida.',
                'erro'
            )

    return render_template('mortalidade.html')


# ==========================================================
# HISTÓRICO DE MEDIÇÕES
# ==========================================================

@app.route('/historico')
def historico():

    medicoes = Medicao.query.order_by(
        Medicao.data.desc()
    ).all()

    return render_template(
        'historico.html',
        medicoes=medicoes
    )


# ==========================================================
# HISTÓRICO DE MORTALIDADE
# ==========================================================

@app.route('/historico-mortalidade')
def historico_mortalidade():

    mortalidades = Mortalidade.query.order_by(
        Mortalidade.data.desc()
    ).all()

    return render_template(
        'historico_mortalidade.html',
        mortalidades=mortalidades
    )


# ==========================================================
# CRIAÇÃO DO BANCO
# ==========================================================

with app.app_context():
    db.create_all()


# ==========================================================
# EXECUÇÃO LOCAL
# ==========================================================

if __name__ == '__main__':
    app.run(debug=True)


