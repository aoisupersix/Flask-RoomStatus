#-*- coding:utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from pytz import timezone
import json

app = Flask(__name__)

#部屋にいる人
inRoom = []
#定員
capacity = 30
#生存期間[s]
lifetime = 60 * 60

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
            global inRoom
            inRoom.append(datetime.now(timezone('Asia/Tokyo')))

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
        print "time:" + str(addDate)
        if len(inRoom) > 0:
            for i, room in enumerate(inRoom):
                if addDate <= room:
                    global inRoom
                    inRoom.insert(i, addDate)
                    break
            else:
                global inRoom
                inRoom.append(addDate)
        else:
            global inRoom
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
    global inRoom
    if request.method == 'POST':
        killinRoom()
        num = int((request.json['num']))
        if len(inRoom) > 0:
            if num == 0:
                #一削除
                global inRoom
                inRoom.pop(0)
            else:
                #全削除
                global inRoom
                del inRoom[:]
        print "rm:"
        showStatus()
        return jsonify(ResultSet=json.dumps(getReturn()))
    else:
        #エラー
        return redirect(url_for('index'))


#生存期間を超えた人を消す
def killinRoom():
    if len(inRoom) >= 1:
        delta = datetime.now(timezone('Asia/Tokyo')) - inRoom[0]
        if delta.total_seconds() > lifetime:
            #削除
            print "kill!!!!!"
            global inRoom
            inRoom.pop(0)
            killinRoom()
    print "killinRoom:"
    showStatus()

#レスポンスを作成
def getReturn():
    strRoom = []
    for i in inRoom:
        strRoom.append(i.strftime('%Y-%m-%d %H:%M:%S'))
    ret = {"capacity": capacity}
    ret.update({"inRoomNum": len(inRoom)})
    ret.update({"inRoom": strRoom})
    return ret

#inRoomを表示
def showStatus():
    print "ROOM_STATUS"
    print "inRoom:" + str(inRoom)

#jsonifyで対応する型を追加
def support_datetime_default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(repr(o) + " is not JSON serializable")

if __name__ == '__main__':
    app.run()
