#-*- coding:utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from pytz import timezone
import json
#以下データベース関係
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref

app = Flask(__name__)
#デバッグ
app.config['DEBUG'] = True
#データベースを指定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Entry.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

###################################
#データベース
###################################
class Entry(db.Model):
    #入室記録テーブル
    __tablename__ = "Entry"
    id = db.Column(Integer, primary_key=True)
    time = Column(db.DateTime)

    #初期化
    def __init__(self, time):
        self.time = time

    def __repr__(self):
        return '<Time %r>' % self.time

###################################
#設定
###################################
class Setting():
    #定員
    capacity = 30
    #生存期間[s]
    lifeTime = 60 * 60
    #デバイス側の設定
    coolTime = 3.0
    avgNum = 10
    threshold = 60

    def getDict(self):
        return {"capacity": self.capacity, "lifetime": self.lifeTime, "coolTime": self.coolTime, "avgNum": self.avgNum, "threshold": self.threshold}

    def setSettings(self, cap, life, cool, avg, thre):
        self.capacity = cap
        self.lifeTime = life
        self.coolTime = cool
        self.avgNum = avg
        self.threshold = thre

#部屋にいる人の管理
inRoom = []
#設定
settings = Setting()

@app.before_first_request
def first_request():
    db.create_all()

###################################
#ルート
#GET:
###################################
@app.route('/')
def index():
    inRoomNum = str(len(inRoom))
    title = u"PC室の混雑状況"
    print inRoomNum
    return render_template('index.html')

###################################
#人数追加
#POST:
#   -num: 追加する人数
###################################
@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        killinRoom()
        num = int((request.json['num']))
        for i in range(num):
            d = datetime.now(timezone('Asia/Tokyo'))
            inRoom.append(d)
            addRecord(d)

        print "add:"
        showStatus()
        return jsonify(ResultSet=json.dumps(getReturn()))
    else:
        #エラー
        return redirect(url_for('index'))

###################################
#人数追加
#POST:
#   -unixtime: 追加する時刻(timestamp)
###################################
@app.route('/addTime', methods=['POST'])
def addTime():
    if request.method == 'POST':
        killinRoom()
        unixtime = int((request.json['unixtime']))
        addDate = datetime.fromtimestamp(unixtime, tz=timezone('Asia/Tokyo'))
        addRecord(addDate)
        print "time:" + str(addDate)
        if len(inRoom) > 0:
            for i, room in enumerate(inRoom):
                if addDate <= room:
                    inRoom.insert(i, addDate)
                    break
            else:
                inRoom.append(addDate)
        else:
            inRoom.append(addDate)
        print "addTime:"
        showStatus()
        return jsonify(ResultSet=json.dumps(getReturn()))
    else:
        #エラー
        return redirect(url_for('index'))

###################################
#人数削除
#POST:
#   -num: 削除する人数
#       -0:最初の一人削除
#       -1:全削除
###################################
@app.route('/rm', methods=['POST'])
def remove():
    if request.method == 'POST':
        killinRoom()
        num = int((request.json['num']))
        if len(inRoom) > 0:
            if num == 0:
                #一削除
                inRoom.pop(0)
            else:
                #全削除
                del inRoom[:]
        print "rm:"
        showStatus()
        return jsonify(ResultSet=json.dumps(getReturn()))
    else:
        #エラー
        return redirect(url_for('index'))

###################################
#統計情報取得
#GET:
#   ->hour
###################################
@app.route('/getHour', methods=['GET'])
def getHour():
    if request.method == 'GET':
        return render_template('statistics.html', hours=getRecord())

###################################
#設定更新/取得
#POST:
#   -capacity
#   -lifetime
#   -sleepTime
#   -coolTime
###################################
@app.route('/setting', methods=['POST', 'GET'])
def setting():
    if request.method == 'POST':
        #設定更新
        try:
            capacity = int((request.json['capacity']))
            lifetime = int((request.json['lifetime']))
            coolTime = float((request.json['coolTime']))
            avgNum = float((request.json['avgNum']))
            threshold = float((request.json['threshold']))
            settings.setSettings(capacity, lifetime, coolTime, avgNum, threshold)
        except Exception as e:
            print "エラー:"
            print 'type:' + str(type(e))
            print 'args:' + str(e.args)
            print 'message:' + e.message
    return jsonify(ResultSet=json.dumps(getReturn()))

#生存期間を超えた人を消す
def killinRoom():
    if len(inRoom) >= 1:
        delta = datetime.now(timezone('Asia/Tokyo')) - inRoom[0]
        lifetime = settings.lifeTime
        if delta.total_seconds() > lifetime:
            #削除
            print "kill!!!!!"
            inRoom.pop(0)
            killinRoom()
    print "killinRoom:"
    showStatus()

#レスポンスを作成
def getReturn():
    strRoom = []
    for i in inRoom:
        strRoom.append(i.strftime('%Y-%m-%d %H:%M:%S'))
    ret = settings.getDict()
    ret.update({"inRoomNum": len(inRoom)})
    ret.update({"inRoom": strRoom})
    print "Return:" + str(ret)
    return ret

#inRoomを表示
def showStatus():
    print "ROOM_STATUS"
    print "inRoom:" + str(len(inRoom))
    for i in inRoom:
        print i.strftime('%Y-%m-%d %H:%M:%S')

###################################
#データベース関連
###################################
#レコード追加
def addRecord(date):
    add = Entry(date)
    print "addDatabase:" + str(add)
    db.session.add(add)
    db.session.commit()
#レコード取得
def getRecord():
    rec = Entry.query.all()
    hours = [0 for i in range(24)]
    for r in rec:
        hours[r.time.hour] += 1
    print "Hours:" + str(hours)
    print "Record:" + str(rec)
    return hours

#jsonifyで対応する型を追加
def support_datetime_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(repr(o) + " is not JSON serializable")

if __name__ == '__main__':
    app.run()
