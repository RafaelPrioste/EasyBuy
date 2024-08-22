from crypt import methods
from flask import Flask, make_response
from markupsafe import escape
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import url_for

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://rafaeasy:183025@localhost:3306/meubanco'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256))
    end = db.Column('usu_end', db.String(256))

    def __init__(self, nome, email, senha, end):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.end = end
    

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/cad/usuario")
def cadusuario():
    return render_template('usuario.html', titulo="Cadastro de Usuario")

@app.route("/cad/caduser", methods=['POST'])
def caduser():
    usuario = Usuario(request.form.get('user'), request.form.get('email'), request.form.get('passwd'), request.form.ger('end'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for(cadusuario))

@app.route("/cad/anuncio")
def anuncio():
    return render_template('anuncio.html')

@app.route("/anuncio/pergunta")
def pergunta():
    return render_template('pergunta.html')

@app.route("/anuncio/compra")
def compra():
    print("anuncio comprado")
    return "<h4>Comprado</h4>"

@app.route("/anuncio/favoritos")
def favoritos():
    print("favorito inserido")
    return "<h4>Favorito</h4>"

@app.route("/config/categoria")
def categoria():
    return render_template('categoria.html')

@app.route("/relatorios/vendas")
def relVendas():
    return render_template('relVendas.html')

@app.route("/relatorios/compras")
def relCompras():
    return render_template('relCompras.html')


    if __name__== 'easybuy':
        print("easybuy")
        db.creat_all()