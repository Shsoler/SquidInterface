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

if __name__ == '__main__':
    app.secret_key = "secret_key"
    app.run(debug=True)
