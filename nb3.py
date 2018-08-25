import serial
from time import sleep, time
from nb_iot import *


if __name__ == "__main__":
    IP = 'xx.xx.xx.xx'
    port = 41234

    # debug True or False
    nb1 = NB_AIS(True, '/dev/ttyUSB0')
    nb2 = NB_AIS(True, '/dev/ttyUSB1')
    nb3 = NB_AIS(True, '/dev/ttyUSB2')

    nb1.setupDevice(port)
    nb2.setupDevice(port)
    nb3.setupDevice(port)

    print("Test Ping")
    nb1.pingIP('xx.xx.xx.xx')
    nb2.pingIP('xx.xx.xx.xx')
    nb3.pingIP('xx.xx.xx.xx')

    previous_time = time()
    interval = 12
    cnt = 0
    while True:
        current_time = time()
        if current_time - previous_time >= interval:
            cnt += 1
            nb1.sendUDPmsg(IP, port, 'Test1'+str(cnt))
            print("send nb1")
            nb2.sendUDPmsg(IP, port, 'Test2'+str(cnt))
            print("send nb2")
            nb3.sendUDPmsg(IP, port, 'Test3'+str(cnt))
            print("send nb3")
            previous_time = current_time

        nb1.response()
        nb2.response()
        nb3.response()
