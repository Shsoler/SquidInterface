from flask import Flask
from flask import request
from flask import render_template,redirect,flash,session,abort

app = Flask(__name__)

#login
@app.route("/")
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')

@app.route('/login',methods=['POST'])
def logar():
    if request.form['password'] == 'admin' and request.form['username'] =='admin':
        session['logged_in'] = True
    else:
        flash('senha errada')
    return home()

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return home()

#adicionar regex aceito
@app.route("/addpalavra/Excluir/<valor>",methods=['GET','POST'])
def rempalavra(valor):
    file = open("palavrasbloqueadas.txt","r")
    texto = file.readlines()
    file.close()
    ntexto = list()
    for x in texto:
        ntexto.append(x.replace("\n",""))
    print(texto)
    print(valor)
    ntexto.remove(valor)
    file = open("palavrasbloqueadas.txt","w")
    for i in ntexto:
        file.write(i)
        if i != ntexto[-1]:
            file.write("\n")
    file.close()
    return addpalavra()

@app.route("/addpalavra")
def addpalavra():
    file = open("palavrasbloqueadas.txt","r")
    texto = file.readlines()
    file.close()
    return render_template("palavraliberada.html",texto = texto)

@app.route("/addpalavra",methods=['POST'])
def addpalavraform():
    print(request.form)
    text= request.form['palavra']
    file = open("palavrasbloqueadas.txt","r")
    texto = file.readlines()
    file.close()
    ntexto = list()
    for x in texto:
        ntexto.append(x.replace("\n",""))
    file = open("palavrasbloqueadas.txt","w")
    for i in ntexto:
        file.write(i)
        print(i)
        file.write("\n")
    file.write(text)
    file.close()
    return addpalavra()

@app.route("/adicionar")
def adicionarRegra():
	return render_template("addregra.html")

@app.route("/listar")
def listarRegra():
	file = open("squid.conf","r")
	squid = file.read()
	squidList = squid.split("#regras")
	print(squidList[1])
	regras = squidList[1].split("#regra")
	regrasLimpas = list()
	for x in regras:
		x.strip()
		if x != '\n':
			regrasLimpas.append(x)
	print(regrasLimpas)
	regrasFinais = list()
	for x in regrasLimpas:
		regrasFinais.append(x.split(" ")[1].split("\n")[0])	
	return render_template("listaregra.html",regras = regrasFinais)

@app.route("/listar/Excluir/<regra>",methods=['GET'])
def removerRegraPost(regra):
	file = open("squid.conf","r")
	squid = file.readlines()
	file.close()
	print(regra)
	file = open("squid.conf","w")
	for x in squid:
		if regra not in x:
			file.write(x)
	file.truncate()
	file.close()
	return listarRegra()
	
@app.route("/adicionar",methods=['POST'])
def adicionarRegraPost():
	nome = request.form['nome']
	tipo = request.form['tipo']
	cond = request.form['cond']
	perm = request.form['perm']
	isArq = request.form['arquivo']
	if tipo=="TIME":
		condInicial = request.form['cond2']
		cond = condInicial+"-"+cond
	print(isArq)
	if isArq == "true":
		arquivo = request.form['condarquivo']
		cond = nome+"-Arquivo"
		file = open(cond,"w")
		file.writelines(arquivo)
		file.close()
		cond = "\""+cond+"\""
	fileregra = open("squid.conf","a+")
	regra = list()
	regra.append("#regra "+ nome)
	regra.append("ACL "+nome+" "+tipo+" "+cond)
	regra.append("HTTP_ACCESS "+ perm+" "+nome)
	for r in regra:
		fileregra.write(r+"\n")
	fileregra.close()
	print(regra)
	return listarRegra()
	
if __name__ == '__main__':
    app.secret_key = "secret_key"
    app.run(debug=True)
