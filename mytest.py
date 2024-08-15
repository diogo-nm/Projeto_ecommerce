from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from flask import url_for
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://testuser:021022@localhost:3306/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/cadastro/usuario')
def usuario():
    return render_template('usuario.html', usuarios = Usuario.query.all(), titulo='Usuário')

@app.route('/usuario/criar', methods=['POST'])
def criarusuario():
    usuario = Usuario(request.form.get('user'), request.form.get('email'), request.form.get('senha'), request.form.get('end'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route('/usuario/detalhar/<int:id>')
def buscausuario(id):
    usuario = Usuario.query.get(id)
    return usuario.nome

@app.route('/usuario/editar/<int:id>', methods=['GET', 'POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.email = request.form.get('email')
        usuario.senha = request.form.get('senha')
        usuario.end = request.form.get('end')

        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('usuario'))
    
    return render_template('edusuario.html', usuario = usuario, titulo='Usuario')

@app.route('/usuario/deletar/<int:id>')
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route('/cadastro/anuncio')
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
