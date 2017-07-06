#-*-coding:utf-8-*-

import RPi.GPIO as GPIO
import threading
import spidev
import time
import requests
import json

spi = spidev.SpiDev()
spi.open(0,0)


GPIO.setwarnings(False)
#設定
class Setting():
    coolTime = 3.0 #距離センサの判定間隔
    avgNum = 10 #距離センサの平均化回数
    threshold = 60 #距離センサの判定閾値

    #サーバから設定を持ってくる
    def getSetting(self):
        print "UpdateSetting---"
        result = json.loads(get("/setting").json()["ResultSet"])
        print "coolTime:" + str(result["coolTime"])
        print "avgNum:" + "none"
        print "threshold:" + "none"

##########################
#   サーバとの通信
##########################
url = "https://frozen-island-37316.herokuapp.com/"
def post(endUrl, value):
    addUrl = url + endUrl
    result = requests.post(
        addUrl,
        data=json.dumps(value),
        headers={'Content-Type': 'application/json'}
    )
    return result
def get(endUrl):
    getUrl = url + endUrl
    result = requests.get(
        getUrl,
        headers={'Content-Type': 'application/json'}
    )
    return result


##########################
#   距離センサ(スレッド)
##########################
class DistSensor(threading.Thread):

    def __init__(self, p):
        self.anaPort = p #AD変換のポート間隔
        self.detection = False #何かが通っているかどうか
        self.activeTime = time.time() #通過時間

        #event
        self.stop_event = threading.Event()
        #make thread
        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def run(self):
        while not self.stop_event.is_set():
            #avgNum回平均を取って距離を割り出す
            ans = 0.0
            for i in range(setting.avgNum):
                ans = ans + self.readabc(self.anaPort)
            value = ans / setting.avgNum
            volts = (value * 3.3) / 1023
            distance = 26.549 * pow(volts, -1.2091)
            #print str(self.anaPort) + ":" + str(distance)
            if(distance <setting.threshold and distance >=8):
                print str(self.anaPort) + ":KENCHI!"
                self.activeTime = time.time()
                self.detection = True
                time.sleep(setting.coolTime)
                print str(self.anaPort) + ":ReStart"
            else:
                self.detection = False

    def stop(self):
        self.stop_event.set()
        self.thread.join()

    def readabc(self, adcnum):
        if adcnum > 7 or adcnum < 0:
            return -1
        r = spi.xfer2([1, 8 + adcnum << 4, 0])
        adcout = ((r[1] & 3) << 8) + r[2]
        return adcout

##########################
#   人感センサ
##########################
class HumanSensor(threading.Thread):

    def __init__(self, p):
        self.port = p
        self.activeTime = time.time()

        #event
        self.stop_event = threading.Event()
        #make thread
        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def run(self):
        while not self.stop_event.is_set():
            #人感センサが反応している間時刻を更新
            if GPIO.input(self.port) == 1:
                self.activeTime = time.time()

    def stop(self):
        self.stop_event.set()
        self.thread.join()

GPIO.setmode(GPIO.BCM)

setting = Setting()

#設定更新タクトスイッチ
def switchClicked(channel):
    print "SWITCH CLICKED"
    setting.getSetting()

SWITCH_PIN = 20
GPIO.setup(SWITCH_PIN, GPIO.IN)
GPIO.add_event_detect(SWITCH_PIN, GPIO.FALLING, callback=switchClicked, bouncetime=500)

#human sensor
GPIO.setup(21, GPIO.IN)
human = HumanSensor(21)

dist1 = DistSensor(0)
dist2 = DistSensor(1)


try:
    while True:
        if dist1.detection or dist2.detection:
            time.sleep(setting.coolTime * 0.5)
            dist1.detection = False
            dist2.detection = False
            print "now:" + str(time.time())
            dt1 = dist1.activeTime
            dt2 = dist2.activeTime
            print "sensor1:" + str(dt1)
            print "sensor2:" + str(dt2)
            subD = abs(dt1 - dt2)
            subH = abs(time.time() - human.activeTime)
            if subD < setting.coolTime and subH < setting.coolTime:
                if dt1 > dt2:
                    print "OUTROOM"
                    post("rm",{'num': 0})
                else:
                    print "INROOM"
                    post("add", {'num': 1})
except KeyboardInterrupt:
    dist1.stop()
    dist2.stop()
    human.stop()
    pass
