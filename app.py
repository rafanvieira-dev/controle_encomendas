from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Função para criar banco ---
def criar_banco():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS encomendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destinatario TEXT,
            apartamento TEXT,
            bloco TEXT,
            transportadora TEXT,
            rastreio TEXT,
            funcionario_recebeu TEXT,
            documento_recebedor TEXT,
            foto TEXT,
            status TEXT,
            retirado_por TEXT,
            documento_retirada TEXT,
            data_recebimento TEXT,
            data_retirada TEXT
        )
    ''')
    conn.commit()
    conn.close()

criar_banco()

# --- Página inicial ---
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM encomendas WHERE status='Pendente'")
    pendentes = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM encomendas WHERE status='Entregue'")
    entregues = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM encomendas")
    total = c.fetchone()[0]
    conn.close()
    return render_template('index.html', pendentes=pendentes, entregues=entregues, total=total)

# --- Cadastrar nova encomenda ---
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        destinatario = request.form['destinatario']
        apartamento = request.form['apartamento']
        bloco = request.form['bloco']
        transportadora = request.form['transportadora']
        rastreio = request.form['rastreio']
        funcionario = request.form['funcionario']
        documento = request.form['documento']
        foto = request.files.get('foto')

        foto_path = ''
        if foto and foto.filename != '':
            foto.save(os.path.join(UPLOAD_FOLDER, foto.filename))
            foto_path = f'uploads/{foto.filename}'

        data_recebimento = datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO encomendas
            (destinatario, apartamento, bloco, transportadora, rastreio, funcionario_recebeu,
             documento_recebedor, foto, status, retirado_por, documento_retirada, data_recebimento, data_retirada)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Pendente', '', '', ?, '')
        ''', (destinatario, apartamento, bloco, transportadora, rastreio, funcionario, documento, foto_path, data_recebimento))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('cadastrar.html')

# --- Entregar encomenda ---
@app.route('/entregar', methods=['GET', 'POST'])
def entregar():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM encomendas WHERE status='Pendente'")
    pendentes = c.fetchall()
    conn.close()

    if request.method == 'POST':
        id_encomenda = request.form['id_encomenda']
        retirado_por = request.form['retirado_por']
        documento_retirada = request.form['documento_retirada']
        data_retirada = datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            UPDATE encomendas
            SET status='Entregue', retirado_por=?, documento_retirada=?, data_retirada=?
            WHERE id=?
        ''', (retirado_por, documento_retirada, data_retirada, id_encomenda))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('entregar.html', pendentes=pendentes)

# --- Consultar encomendas ---
@app.route('/consultar')
def consultar():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM encomendas ORDER BY id DESC")
    encomendas = c.fetchall()
    conn.close()
    return render_template('consultar.html', encomendas=encomendas)

# --- Página de detalhes ---
@app.route('/detalhes/<int:id_encomenda>')
def detalhes(id_encomenda):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM encomendas WHERE id=?", (id_encomenda,))
    encomenda = c.fetchone()
    conn.close()
    return render_template('detalhes.html', encomenda=encomenda)

if __name__ == '__main__':
    app.run(debug=True)
