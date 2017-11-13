from flask import Flask
from flask import request
from flask import render_template,redirect,flash,session,abort
import subprocess
import hashlib
app = Flask(__name__)

@app.route("/restart")
def restart():
	if not session.get('logged_in'):
		return render_template('login.html')
	subprocess.check_call(["service","squid3","restart"])
	return redirect("/")
@app.route("/resetar")
def resetarConf():
	if not session.get('logged_in'):
		return render_template('login.html')
	file = open("squid.conf","r")
	original = file.readlines()
	file.close()
	file = open("/etc/squid3/squid.conf","w")
	file.writelines(original)
	file.close()
	subprocess.check_call(["squid3","-k","reconfigure"])
	return redirect("/")
#login

@app.route("/")
def home():
    if not session.get('logged_in'):
    	return render_template('login.html')
    else:
        return render_template('home.html')

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


@app.route("/listar")
def listarRegra():
	if not session.get('logged_in'):
		return render_template('login.html')
	file = open("/etc/squid3/squid.conf","r")
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
		regra = x.replace("\n","").replace("acl","").replace("http_access","").replace("-i","").replace("  "," ").split(" ")
		dic = {"nome":regra[1],"tipo":regra[3],"cond":regra[4],"perm":regra[5]}
		regrasFinais.append(dic)
	return render_template("listaregra.html",regras = regrasFinais)

@app.route("/listar/Excluir/<regra>",methods=['GET'])
def removerRegraPost(regra):
	if not session.get('logged_in'):
		return render_template('login.html')
	file = open("/etc/squid3/squid.conf","r")
	squid = file.readlines()
	file.close()
	print(regra)
	file = open("/etc/squid3/squid.conf","w")
	for x in squid:
		if regra not in x:
			file.write(x)
	file.truncate()
	file.close()
	subprocess.check_call(["squid3","-k","reconfigure"])
	return listarRegra()
	
@app.route("/adicionarUser",methods=['POST'])
def addUser():
	if not session.get('logged_in'):
		return render_template('login.html')
	user = request.form['user']
	senha = request.form['senha']
	m = hashlib.md5(str(senha).encode('utf-8'))
	file = open("/etc/squid3/squid_passwd","w")
	file.write(user+":"+m.hexdigest())
	file.close()
	subprocess.check_call(["squid3","-k","reconfigure"])
	return listarUser()

@app.route("/adicionarUser")
def addUserClear():
	if not session.get('logged_in'):
		return render_template('login.html')
	return render_template("adicionarUser.html")
	
@app.route("/listarUser")
def listarUser():
	if not session.get('logged_in'):
		return render_template('login.html')
	file = open("/etc/squid3/squid_passwd","r")
	senhas = file.readlines()
	return render_template("listaUser.html",senhas = senhas)

@app.route("/listarUser/Excluir/<excluir>",methods=['GET'])
def listarUserDel(excluir):
	if not session.get('logged_in'):
		return render_template('login.html')
	file = open("/etc/squid3/squid_passwd","r")
	senhas = file.readlines()
	file.close()
	file = open("/etc/squid3/squid_passwd","w")
	for x in file:
		if excluir not in x:
			file.write(x)
	file.close()
	subprocess.check_call(["squid3","-k","reconfigure"])
	return listarUser()
	
@app.route("/adicionar",methods=['POST'])
def adicionarRegraPost():
	if not session.get('logged_in'):
		return render_template('login.html')
	nome = request.form['nome']
	tipo = request.form['tipo']
	cond = request.form['cond']
	perm = request.form['perm']
	isArq = request.form['arquivo']

	if tipo=="time":
		condInicial = request.form['cond2']
		cond = condInicial+"-"+cond
	if isArq == "true":
		arquivo = request.form['condarquivo']
		cond = nome+"-Arquivo"
		file = open("/etc/squid3/"+cond,"w")
		file.writelines(arquivo)
		file.close()
		cond = "\""+cond+"\""
	fileregra = open("/etc/squid3/squid.conf","r")
	regra = fileregra.readlines()
	for x in regra:
		if "http_access allow autenticados" in x:
			regra.remove(x) 
	regra.remove("http_access allow autenticados")
	fileregra.close()
	fileregra = open("/etc/squid3/squid.conf","w")
	if tipo != "aninhado":
		regra.append("#regra "+ nome)
		regra.append("acl "+nome+" "+tipo+" "+cond)
		regra.append("http_access "+ perm+" "+nome)
	else:
		regra.append("#regra "+nome)
		regra.append("acl "+nome+ " time " + request.form['cond3']+"-"+request.form['cond2'])
		regra.append("acl "+nome+"2"+ " url_regex -i "+cond)
		regra.append("http_access "+perm+" "+nome+" "+nome+"2")
	for r in regra:
		fileregra.write(r+"\n")
	fileregra.write("http_access allow autenticados\n")
	fileregra.close()
	print(regra)
	#subprocess.check_call(["service","squid3","restart"])
	subprocess.check_call(["squid3","-k","reconfigure"])
	return listarRegra()
	
@app.route("/adicionar")
def adicionarRegra():
	if not session.get('logged_in'):
		return render_template('login.html')
	return render_template("addregra.html")

@app.route("/teste")
def teste():
	flash("teste")
	return "hello"


@app.route("/configurarSquid")
def configurar():
	if not session.get('logged_in'):
		return render_template('login.html')
	file = open("/etc/squid3/squid.conf","r")
	lista = file.readlines()
	valores = list()
	valores.append("http_port ")
	valores.append("visible_hostname ")
	valores.append("cache_mem")
	valores.append("maximum_object_size_in_memory")
	valores.append("maximum_object_size")

	print(valores)

	port = lista[0].replace(valores[0],"")
	host = lista[1].replace(valores[1],"")
	cache = lista[2].replace(valores[2],"").replace(" KB","").replace(" MB","")
	mem = lista[3].replace(valores[3],"").replace(" MB","").replace(" KB","")
	disco = lista[4].replace(valores[4],"").replace(" KB","").replace(" MB","")
	
	regras = {"port":port,"host":host,"cache":cache,"mem":mem,"dire":disco}


	return render_template("configuracao.html",regras=regras)

@app.route("/configurarSquid",methods=['POST'])
def configurarSquid():
	if not session.get('logged_in'):
		return render_template('login.html')
	host = request.form['host']
	porta = request.form['porta']
	disco = request.form['dire']
	subdir = request.form['subdir']
	cache = request.form['cache']
	
	file = open("/etc/squid3/squid.conf","r")
	lista = file.read()
	file.close()

	file = open("/etc/squid3/squid.conf","w")

	regra = lista.split("#regras")
		
	
	valores = list()
	valores.append("http_port "+porta+"\n")
	valores.append("visible_hostname "+host+"\n")
	valores.append("cache_mem "+cache+" MB"+"\n")
	valores.append("maximum_object_size_in_memory "+subdir+ " KB"+"\n")
	valores.append("maximum_object_size "+disco+ " KB"+"\n")
	valores.append("minimum_object_size 0 KB"+"\n")
	valores.append("cache_swap_low 90 "+"\n")
	valores.append("cache_swap_high 95"+"\n")
	valores.append("cache_dir ufs /var/spool/squid3 256 10 128 "+"\n")
	valores.append("cache_acess_log /var/log/squid3/acess.log/squid3/acess"+"\n")
	valores.append("#pass"+"\n")
	valores.append("auth_param basic realm squid"+"\n")
	valores.append("auth_param basic program /usr/lib/squi3/basic_ncsa_auth /etc/squid3/squid_pass"+"\n")
	valores.append("acl autenticados proxy_auth REQUIRED"+"\n")
	valores.append("http_access allow autenticados"+"\n")
	valores.append("#regras")

	file = open("/etc/squid3/squid.conf","w")
	file. writelines(valores)
	file.write(regra[1])
	file.close()
	return redirect("/")




if __name__ == '__main__':
    app.secret_key = "secret_key"
    app.run(debug=True,host="0.0.0.0")
