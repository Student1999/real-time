from flask import Flask,render_template, request,jsonify,redirect,url_for
from flask_socketio import SocketIO, emit
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
app.config["SECRET_KEY"] = "jnjc(U&&*MXS_)"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine("sqlite:///data.db")
db = scoped_session(sessionmaker(bind=engine))

socketio = SocketIO(app)

global username
username = {}
global channelname
channelname = []

global messagesPerChannel
messagesPerChannel = {}

@app.route("/")
def index():
    try:
        return render_template("index.html",channelname=channelname)
    except:
        return render_template("index.html",channelname='')

@app.route("/addName",methods=["POST"])
def addName():
    usernameNew = request.form.get('username')
    usernameOld = {usernameNew:usernameNew}
    username.update(usernameOld)
    return jsonify({"cavab":username[usernameNew]})

@app.route("/addChannel",methods=["POST"])
def channel():
    c_name = request.form.get('c_name')

    if c_name not in channelname:
        channelname.append(c_name)
        return jsonify({"cavab":True})
    else:
        return jsonify({"cavab":False})

@app.route("/view_chan", methods=["POST"])
def view_chan():
    try:
        NameChannel = request.form.get('NameChannel')
        global usernameNow
        usernameNow = request.form.get('username')
        return jsonify({"cavab":messagesPerChannel[NameChannel][usernameNow],"success":True})

    except KeyError:
        NameChannel = request.form.get('NameChannel')
        usernameNow = request.form.get('username')

        if NameChannel in messagesPerChannel:
            newChannel = {usernameNow:["artiq kanala qosuldunuz"]}
            messagesPerChannel[NameChannel].update(newChannel)
            return jsonify({"cavab":messagesPerChannel[NameChannel][usernameNow],"success":"2"})
        else:
            newChannel = {NameChannel:{usernameNow:["bu kanlin birinci uzvusuz!"]}}
            messagesPerChannel.update(newChannel)
            return jsonify({"cavab":newChannel, "success":"3"})

@app.route("/chat/<string:name>", methods=["GET"])
def chat(name):
    try:
        return render_template("chat.html",channelName=name)
    except:
        return render_template("chat.html",channelName=name)

@socketio.on("ForMesajlar")
def Mesajlar(data):
    User_Name = data["User_Name"]
    Chan_Name = data["Chan_Name"]
    event = User_Name+Chan_Name
    Messages = messagesPerChannel[Chan_Name][User_Name]
    emit(Chan_Name,{"Mesajlar":Messages,"OthersMesajlar":messagesPerChannel,"mine":event},broadcast=True)

@socketio.on("ForMesaj")
def MesajAdd(data):
    User_Name = data["User_Name"]
    Chan_Name = data["Chan_Name"]
    mesaj = data["mesaj"]
    #newChannel = {Chan_Name:{User_Name:mesaj}}
    #messagesPerChannel += newChannel
    messagesPerChannel[Chan_Name][User_Name].append(mesaj)
