from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import url_for
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
import hashlib
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://testuser:021022@localhost:3306/mydb'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://diogoNM:db021022@diogoNM.mysql.pythonanywhere-services.com:3306/diogoNM$mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = '012801'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key = True)
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

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('pgnaoencontrada.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = hashlib.sha512(str(request.form.get('senha')).encode('utf-8')).hexdigest()

        user = Usuario.query.filter_by(email=email, senha=senha).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        
        else:
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/cadastro/usuario')
def usuario():
    return render_template('usuario.html', usuarios = Usuario.query.all(), titulo='Usuário')

@app.route('/usuario/criar', methods=['POST'])
def criarusuario():
    hash = hashlib.sha512(str(request.form.get('senha')).encode('utf-8')).hexdigest()
    usuario = Usuario(request.form.get('user'), request.form.get('email'), hash, request.form.get('end'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route('/usuario/detalhar/<int:id>')
@login_required
def buscausuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route('/usuario/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.senha = hashlib.sha512(str(request.form.get('senha')).encode('utf-8')).hexdigest()
        usuario.end = request.form.get('end')

        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuario'))
    
    return render_template('edusuario.html', usuario = usuario, titulo='Usuario')

@app.route('/usuario/confirmar_delecao/<int:id>', methods=['GET', 'POST'])
def confirmar_delecao(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return redirect(url_for('usuario'))
    
    anuncios = Anuncio.query.filter_by(usu_id=id).all()

    if request.method == 'POST':
        deletar_anuncios = request.form.get('deletar_anuncios', 'false') == 'true'

        try:
            if deletar_anuncios:
                # Deletar todos os anúncios associados ao usuário
                Anuncio.query.filter_by(usu_id=id).delete()
            
            # Deletar o usuário
            if usuario:
                db.session.delete(usuario)
                db.session.commit()
            
            return redirect(url_for('usuario'))
        
        except Exception as e:
            db.session.rollback()  # Reverter qualquer mudança se ocorrer um erro
            print(f"Erro ao deletar usuário: {e}")
            return "Não é possível deletar usuário, pois o mesmo possui anúncios em cadastro ainda", 500
    
    return render_template('confirmar_delecao.html', usuario=usuario, anuncios=anuncios)

@app.route('/usuario/deletar/<int:id>')
@login_required
def deletarusuario(id):
    return redirect(url_for('confirmar_delecao', id=id))

@app.route('/cadastro/anuncio')
@login_required
def anuncio():
    return render_template('anuncio.html', anuncios = Anuncio.query.all(), categorias = Categoria.query.all(), titulo='Anúncio')

@app.route('/anuncio/criar', methods=['POST'])
def criaranuncio():
    anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'), request.form.get('qtd'), request.form.get('preco'), request.form.get('cat'), request.form.get('usu'))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route('/anuncio/pergunta')
def pergunta():
    return render_template('pergunta.html', titulo='Perguntas') 

@app.route('/anuncio/compra')
def compra():
    print ('Compra realizada')
    return "<h3>Compra realizada!</h3>"

@app.route('/anuncio/favorito')
def favorito():
    print('Inserido aos favoritos')
    return "<h3>Inserido aos favoritos</h3>"

@app.route('/configuracao/categoria')
@login_required
def categoria():
    return render_template('categoria.html', categorias = Categoria.query.all(), titulo='Categoria')

@app.route('/categoria/criar', methods=['POST'])
def criarcategoria():
    categoria = Categoria(request.form.get('nome'), request.form.get('desc'))
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('categoria'))

@app.route('/relatorio/venda')
def relVenda():
    return render_template('relVenda.html', titulo='Relatório de Venda')

@app.route('/relatorio/compra')
def relCompra():
    return render_template('relCompra.html', titulo='Relatório de compra')


if __name__ == 'mytest':
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
