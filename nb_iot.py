import serial
from time import sleep, time


class NB_AIS:
    def __init__(self, debug, pin):
        self.debug = debug
        self.previous_time = time()
        self.port = ""
        self.ser = serial.Serial(pin, 9600, timeout=1)
        self.pin = pin

    def setupDevice(self, serverPort):
        self.port = serverPort
        print("############ NB-IOT Library  #############")
        self.reset()
        if self.debug:
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
        self.ser.write(b'AT\r\n')
        while(self.waitReady() != True):
            print('.', end='')
            sleep(0.2)
        print("OK")

        # reboot module
        print("Reboot Module")
        self.ser.write(b"AT+NRB\r\n")
        while(self.waitReady() != True):
            self.ser.write(b'AT\r\n')
            print(".", end='')
            sleep(.5)
        self.ser.flush()
        print("Reboot Module Complete")
        sleep(5)

    def waitReady(self):
        msg = self.ser.readline().decode('utf-8', 'ignore').strip()
        if msg == 'OK':
            return True
        else:
            return False

    def setPhoneFunction(self):
        self.ser.write(b'AT+CFUN=1\r\n')
        while self.waitReady() != True:
            print(".", end='')
            sleep(.2)

    def getIMEI(self):
        self.ser.write(b"AT+CGSN=1\r\n")
        msg = ""
        msg = self.ser.read(64).decode('utf-8').strip()
        return msg[msg.find("+CGSN")+6:msg.find("+CGSN")+21]

    def getFirmwareVersion(self):
        self.ser.write(b'AT+CGMR\r\n')
        msg = ""
        out = ""
        while msg != 'OK':
            msg = self.ser.readline().decode('utf-8').strip()
            out += msg
        return out[:-2]

    def getIMSI(self):
        self.ser.write(b'AT+CIMI\r\n')
        msg = ""
        msg = self.ser.read(30).decode('utf-8').strip().replace("\n", '')
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
        else:
            return True
        if ret:
            print("> Connected")
            self.createUDPSocket(serverPort)
        else:
            print("> Disconnect")
        print("##################################")
        return ret

    def getNBConnect(self):
        self.ser.write(b'AT+CGATT?\r\n')
        msg = ""
        while msg[-2:] != 'OK':
            msg += self.ser.readline().decode('utf-8').strip()
        if msg[:-2] == '+CGATT:1':
            return True
        else:
            return False

    def setAutoConnectOn(self):
        self.ser.write(b'AT+NCONFIG=AUTOCONNECT,TRUE\r\n')
        msg = ""
        while msg[-2:] != 'OK':
            msg = self.ser.readline().decode('utf-8').strip()

    def cgatt(self, mode):
        txt = "AT+CGATT=" + str(mode) + "\r\n"
        self.ser.write(txt.encode())
        msg = ""
        while msg != 'OK':
            msg = self.ser.readline().decode('utf-8').strip()

    def createUDPSocket(self, port):
        txt = "AT+NSOCR=DGRAM,17," + str(port) + ",1\r\n"
        self.ser.write(txt.encode())
        msg = ""
        while msg[-2:] != 'OK':
            msg = self.ser.readline().decode('utf-8').strip()

    def pingIP(self, IP):
        txt = "AT+NPING=" + IP + "\r\n"
        self.ser.write(txt.encode())
        msg = ""
        while True:
            msg += self.ser.readline().decode('utf-8').strip()
            if msg.find("+NPING") == 2:
                break
        index1 = msg.find(',')
        index2 = msg.find(',', index1+1)
        ttl = msg[index1+1:index2]
        rtt = msg[index2+1:len(msg)]
        print("Ping To IP: " + IP + " ttl = " + ttl + " rtt = " + rtt)

    def sendUDPmsg(self, address, port, data):
        data = data.encode('utf-8').hex()
        length = str(len(data)/2)
        txt = "AT+NSOST=0,"+address+"," + \
            str(port) + "," + length[:-2] + "," + data + "\r\n"
        self.ser.write(txt.encode())
        msg = ""
        while msg != 'OK':
            msg = self.ser.readline().decode('utf-8').strip()

    def response(self):
        pre_time = time()
        cur_time = time()
        self.ser.write(b"AT+NSORF=0,100\r\n")
        msg = ""
        getData = False
        data = ""
        while True:
            msg = self.ser.readline().decode('utf-8').strip()
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

            if self.debug:
                print(self.pin + " Respone data From IP:" + serv_ip +
                      " Port:" + serv_port + " Length:" + length + " Data:" + data)
            return data


if __name__ == "__main__":
    pass
