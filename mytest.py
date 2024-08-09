from flask import Flask
from markupsafe import escape
from flask import render_template
from flask import request, make_response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/cadastro/usuario')
def usuario():
    return render_template('usuario.html', titulo='Cadastro de usuário')

@app.route('/cadastro/caduser', methods=['POST'])
def caduser():
    return request.form

@app.route('/cadastro/anuncio')
def anuncio():
    return render_template('anuncio.html', titulo='Cadastro de anúncio')

@app.route('/cadastro/cadan', methods=['POST'])
def cadan():
    return request.form

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
    return render_template('categoria.html', titulo='Categoria')

@app.route('/relatorio/venda')
def relVenda():
    return render_template('relVenda.html', titulo='Relatório de Venda')

@app.route('/relatorio/compra')
def relCompra():
    return render_template('relCompra.html', titulo='Relatório de compra')
