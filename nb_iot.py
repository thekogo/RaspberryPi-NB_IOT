import serial
from time import sleep, time

class NB_AIS:
    def __init__(self, debug):
        self.debug = debug
        self.previous_time = time()
        self.port = ""

    def setupDevice(self, serverPort):
        self.port = serverPort
        print("############ NB-IOT AIS Library By Ko #############")
        self.reset()
        if self.debug :
            self.IMEI = self.getIMEI()
            print("IMEI : " + self.IMEI)
            self.firmwareVersion = self.getFirmwareVersion()
            print("Firmware Version : " + self.firmwareVersion)
            self.IMSI = self.getIMSI()
            print("IMSI SIM : " + self.IMSI)
        self.attachNB(serverPort)
        print("end")

    
    def reset(self):
        self.rebootModule()
        print("Set Phone Function")
        self.setPhoneFunction()
        print("Set Phone Function Complete")

    def rebootModule(self):
        print("Test AT")
        ser.write(b'AT\r\n')
        while(self.waitReady() != True):
            print('.',end='')
            sleep(0.2)
        print("OK")
        
        #reboot module
        print("Reboot Module")
        ser.write(b"AT+NRB\r\n")
        while(self.waitReady() != True):
            ser.write(b'AT\r\n')
            print(".", end='')
            sleep(.5)
        ser.flush()
        print("Reboot Module Complete")
        sleep(5)

    def waitReady(self):
        msg = ser.readline().decode('utf-8', 'ignore').strip()
        if msg == 'OK':
            return True
        else :
            return False

    def setPhoneFunction(self):
        ser.write(b'AT+CFUN=1\r\n')
        while self.waitReady() != True:
            print(".", end='')
            sleep(.2)

    def getIMEI(self):
        ser.write(b"AT+CGSN=1\r\n")
        msg = ""
        msg = ser.read(64).decode('utf-8').strip()
        return msg[msg.find("+CGSN")+6:msg.find("+CGSN")+21]

    def getFirmwareVersion(self):
        ser.write(b'AT+CGMR\r\n')
        msg = ""
        out = ""
        while msg != 'OK':
            msg = ser.readline().decode('utf-8').strip()
            out += msg
        return out[:-2]

    def getIMSI(self):
        ser.write(b'AT+CIMI\r\n')
        msg = ""
        msg = ser.read(30).decode('utf-8').strip().replace("\n", '')
        return msg

    def attachNB(self, serverPort):
        ret = False
        if not self.getNBConnect():
            print("Connecting NB IOT Network")
            i = 1
            while i < 60:
                self.setPhoneFunction()
                self.setAutoConnectOn()
                self.cgatt(1)
                sleep(3)
                if self.getNBConnect():
                    ret = True
                    break
                print('.', end='')
                i += 1
        else :
            return True
        if ret :
            print("> Connected")
            self.createUDPSocket(serverPort)
        else :
            print("> Disconnect")
        print("##################################")
        return ret

    
    def getNBConnect(self):
        ser.write(b'AT+CGATT?\r\n')
        msg = ""
        while msg[-2:] != 'OK':
            msg += ser.readline().decode('utf-8').strip()
        if msg[:-2] == '+CGATT:1':
            return True
        else :
            return False

    def setAutoConnectOn(self):
        ser.write(b'AT+NCONFIG=AUTOCONNECT,TRUE\r\n')
        msg = ""
        while msg[-2:] != 'OK':
            msg = ser.readline().decode('utf-8').strip()

    def cgatt(self, mode):
        txt = "AT+CGATT=" + str(mode) + "\r\n"
        ser.write(txt.encode())
        msg = ""
        while msg != 'OK':
            msg = ser.readline().decode('utf-8').strip() 

    def createUDPSocket(self, port):
        txt = "AT+NSOCR=DGRAM,17," + str(port) + ",1\r\n"
        ser.write(txt.encode())
        msg = ""
        while msg[-2:] != 'OK':
            msg = ser.readline().decode('utf-8').strip()
    
    def pingIP(self, IP):
        txt = "AT+NPING=" + IP + "\r\n"
        ser.write(txt.encode())
        msg = ""
        while True:
            msg += ser.readline().decode('utf-8').strip()
            if msg.find("+NPING") == 2:
                break
        index1 = msg.find(',')
        index2 = msg.find(',', index1+1)
        ttl = msg[index1+1:index2]
        rtt = msg[index2+1:len(msg)]
        print("Ping To IP: " + IP + " ttl = " +ttl + " rtt = " + rtt)

    def sendUDPmsg(self, address, port, data):
        data = data.encode('utf-8').hex()
        length = str(len(data)/2)
        txt = "AT+NSOST=0,"+address+"," + str(port) + "," +length[:-2]+ "," + data + "\r\n"
        ser.write(txt.encode())
        msg = ""
        while msg != 'OK':
            msg = ser.readline().decode('utf-8').strip()

    def response(self):
        pre_time = time()
        cur_time = time()
        ser.write(b"AT+NSORF=0,100\r\n")
        msg = ""
        getData = False
        data = ""
        while True:
            msg = ser.readline().decode('utf-8').strip()
            if msg.find(str(self.port)) != -1:  
                data = msg 
                getData = True
                break
            # time out
            cur_time = time()
            if cur_time - pre_time >= 0.25:
                pre_time = cur_time
                break

        if getData:
            index1 = msg.find(',')
            index2 = msg.find(',', index1+1)
            index3 = msg.find(',', index2+1)
            index4 = msg.find(',', index3+1)
            index5 = msg.find(',', index4+1)

            serv_ip = msg[index1+1:index2]
            serv_port = msg[index2+1:index3]
            length = msg[index3+1:index4]
            data = bytearray.fromhex(msg[index4+1:index5]).decode()
            

            if self.debug :
                print("Respone data From IP:" + serv_ip + " Port:" + serv_port + " Length:" + length + " Data:" + data)
            return data
        

IP = 'xxx.xxx.xxx.xxx'
port = xxxx

ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

# debug True or False
ais = NB_AIS(True)
ais.setupDevice(port)
print("Test Ping")
ais.pingIP('35.185.183.183')
previous_time = time()
interval = 4
cnt = 0
while True:
    current_time = time()
    if current_time - previous_time >= interval:
        cnt += 1
        ais.sendUDPmsg(IP,port,'Test'+str(cnt))
        previous_time = current_time
        print("send")
        
    ais.response()
