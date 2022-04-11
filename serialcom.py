import sys
import threading
import serial
import glob
import os

class SerialCommunicator(object):

    should_stop = threading.Event()
    read_thread_pid = 0
    response = {}

    def __init__(self):
        ports = self.serial_ports()
        self.is_reading = False
        self.online = False
        self.reader, self.writer = os.pipe()
        if ports:
            self.online = True
            self.ser = serial.Serial(ports[0], 9600, timeout=5) 

    def stop(self):
        print("Stopping read thread")
        self.should_stop.set()

    def start(self):
        print("Starting read thread")
        self.read_thread = threading.Thread(target=self.read) 
        self.should_stop.clear()
        self.read_thread.start()

    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        print(result)
        return result

    def handle_response(self, data:str):
        print('got:', data)
        d1 = data.split()
        d2 = d1[0]
        d1.pop(0)
        self.response = {d2:d1}
        if d2 == 'MAIN':
            os.write(self.writer, b'1')
            with open('/tmp/pmsock', 'w') as f:
                f.write('1')
        print('self.response:', self.response)

    def write(self, s, encode=True):
        try:
            if encode:
                s = s + '\r\n'
                print(s.encode('ascii'))
                self.ser.write(s.encode('ascii'))
            else:
                print(s)
                self.ser.write(s)
        except:
            print("Couldn't send cmd")

    def read(self):
        print('read_thread')
        while True:
            if self.should_stop.is_set():
                print('1')
                break
            try:
                reading = self.ser.readline().decode()
                if (reading):
                    self.handle_response(reading)
            except serial.SerialException as e:
                print("Disconnect of UART occured")
                self.ser.close()
                self.is_reading = False
                return None
            except:
                print('Something went wrong')
                pass
        self.is_reading = False
        self.ser.close()
