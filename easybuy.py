from flask import Flask, make_response, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://buyuser:25111990@localhost:3306/bancocerto'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Madame teia nao solta virus'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model):
    __tablename__ = "usuario"
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

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))

    def __init__(self, nome, desc):
        self.nome = nome
        self.desc = desc

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id', db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id

class Compra(db.Model):
    __tablename__ = "compra-realizada"
    id = db.Column('id', db.Integer, primary_key=True)
    anuncio_id = db.Column('anuncio_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usuario_id = db.Column('usuario_id', db.Integer, db.ForeignKey("usuario.usu_id", ondelete='CASCADE'))

    def __init__(self, anuncio_id, usuario_id):
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

class Favorito(db.Model):
    __tablename__ = "anuncio-favorito"
    id = db.Column('id', db.Integer, primary_key=True)
    anuncio_id = db.Column('anuncio_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usuario_id = db.Column('usuario_id', db.Integer, db.ForeignKey("usuario.usu_id", ondelete='CASCADE'))

    def __init__(self, anuncio_id, usuario_id):
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

class Pergunta(db.Model):
    __tablename__ = "pergunta"
    id = db.Column('id', db.Integer, primary_key=True)
    texto = db.Column('texto', db.String(150))
    anuncio_id = db.Column('anuncio_id', db.Integer, db.ForeignKey("anuncio.anu_id"))
    usuario_id = db.Column('usuario_id', db.Integer, db.ForeignKey("usuario.usu_id", ondelete='CASCADE'))

    def __init__(self, texto, anuncio_id, usuario_id):
        self.texto = texto
        self.anuncio_id = anuncio_id
        self.usuario_id = usuario_id

class Resposta(db.Model):
    __tablename__ = "resposta"
    id = db.Column('id', db.Integer, primary_key=True)
    texto = db.Column('texto', db.String(150))
    pergunta_id = db.Column('pergunta_id', db.Integer, db.ForeignKey("pergunta.id", ondelete='CASCADE'))
    usuario_id = db.Column('usuario_id', db.Integer, db.ForeignKey("usuario.usu_id", ondelete='CASCADE'))

    def __init__(self, texto, pergunta_id, usuario_id):
        self.texto = texto
        self.pergunta_id = pergunta_id
        self.usuario_id = usuario_id

@app.errorhandler(404)
def Erro404(error):
    return render_template('Erro404.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passwd = hashlib.sha512(request.form.get('passwd').encode("utf-8")).hexdigest()
        user = Usuario.query.filter_by(email=email, senha=passwd).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas!')
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/")
def index():
    if current_user.is_authenticated:
        user_id = current_user.id
        return render_template('index.html', titulo="Anúncios", anuncio=Anuncio.query.filter(Anuncio.usu_id != user_id).all())
    return render_template('index.html', titulo="Anúncios", anuncio=Anuncio.query.all())

@app.route("/cad/usuario")
@login_required
def rota_usuario():
    return render_template('usuario.html', usuarios=Usuario.query.all(), titulo="Usuários")

@app.route("/usuario/criar", methods=['POST'])
@login_required
def cadastrar_usuario():
    hash_senha = hashlib.sha512(request.form.get('passwd').encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get('user'), request.form.get('email'), hash_senha, request.form.get('end'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('user')
        usuario.email = request.form.get('email')
        usuario.senha = hashlib.sha512(request.form.get('passwd').encode("utf-8")).hexdigest()
        usuario.end = request.form.get('end')
        db.session.commit()
        return redirect(url_for('usuario'))
    return render_template('eusuario.html', usuario=usuario, titulo="Editar Usuário")

@app.route("/usuario/remover/<int:id>", methods=['POST'])
@login_required
def removusuario(id):
    if current_user.id == id:
        usuario = Usuario.query.get(id)
        db.session.delete(usuario)
        db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cad/anuncio")
@login_required
def anuncio():
  
    anuncios = db.session.query(Anuncio, Categoria).join(Categoria, Anuncio.cat_id == Categoria.id).all()
    
    return render_template('anuncio.html', anuncios=anuncios, categorias=Categoria.query.all(), titulo="Anúncios")

@app.route("/anuncio/criar", methods=['POST'])
@login_required
def criaranuncio():
    anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'), int(request.form.get('qtd')), float(request.form.get('preco')), int(request.form.get('cat')), current_user.id)
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editanuncio(id):
    anuncio = Anuncio.query.get(id)
    if request.method == 'POST':
        anuncio.nome = request.form.get('nome')
        anuncio.desc = request.form.get('desc')
        anuncio.qtd = int(request.form.get('qtd'))
        anuncio.preco = float(request.form.get('preco'))
        anuncio.cat_id = int(request.form.get('cat'))
        db.session.commit()
        return redirect(url_for('anuncio'))
    return render_template('anuncio-edit.html', anuncio=anuncio, categorias=Categoria.query.all(), titulo="Editar Anúncio")

@app.route("/anuncio/remover/<int:id>", methods=['POST'])
@login_required
def remover_anuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/comprar/<int:id>", methods=['POST'])
@login_required
def comprar_anuncio(id):
    compra = Compra(id, current_user.id)
    db.session.add(compra)
    db.session.commit()
    return redirect(url_for('relatorio_venda'))

@app.route("/anuncio/favoritar/<int:id>", methods=['POST'])
@login_required
def favoritar_anuncio(id):
    favorito = Favorito(id, current_user.id)
    db.session.add(favorito)
    db.session.commit()
    return redirect(url_for('anuncio-favorito'))

@app.route("/anuncio/pergunta", methods=['GET', 'POST'])
@login_required
def pergunta():
    if request.method == 'POST':
        pergunta = Pergunta(request.form.get('texto'), request.form.get('anuncio_id'), current_user.id)
        db.session.add(pergunta)
        db.session.commit()
        return redirect(url_for('pergunta'))
    return render_template('pergunta.html', anuncio=Anuncio.query.all(), perguntas=Pergunta.query.all(), titulo="Faça uma Pergunta")

@app.route("/anuncio/resposta/enviar/<int:id>", methods=['POST'])
@login_required
def enviar_resposta(id):
    resposta = Resposta(request.form.get('texto'), id, current_user.id)
    db.session.add(resposta)
    db.session.commit()
    return redirect(url_for('pergunta'))

@app.route("/anuncio/favoritos")
@login_required
def anuncio_favorito():
    favoritos = Favorito.query.all()
    return render_template('anuncio-favorito.html', favoritos=favoritos, titulo="Lista de Favoritos")

@app.route("/config/categoria")
@login_required
def categoria():
    return render_template('categoria.html', categorias=Categoria.query.all(), titulo="Categorias")

@app.route("/categoria/cadastrar", methods=['POST'])
@login_required
def cadastrar_categoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/categoria/editar/<int:id>", methods=['GET', 'POST'])
@login_required
def editarcategoria(id):
    categoria = Categoria.query.get(id)
    if request.method == 'POST':
        categoria.nome = request.form.get('nome')
        categoria.desc = request.form.get('desc')
        db.session.commit()
        return redirect(url_for('categoria'))
    return render_template('categoria-edit.html', categoria=categoria, titulo="Editar Categoria")

@app.route("/categoria/remover/<int:id>", methods=['POST'])
@login_required
def removercategoria(id):
    categoria = Categoria.query.get(id)
    db.session.delete(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route("/relatorio/vendas")
@login_required
def relatorio_venda():
    return render_template('vendas.html', anuncio=Anuncio.query.filter_by(usu_id=current_user.id).all(), titulo="Relatório de Vendas")

@app.route("/relatorio/compras")
@login_required
def relatoriocompra():
    return render_template('compra-realizada.html', compras=Compra.query.filter_by(usuario_id=current_user.id).all(), titulo="Relatório de Compras")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
