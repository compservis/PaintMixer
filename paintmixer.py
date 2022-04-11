from base64 import encode
import random
from time import sleep
import json

from numpy import r_
from serialcom import SerialCommunicator
import binascii

colors_amount = 10

class MColor():
    name = ''
    color = ''
    time = ''
    def __init__(self, name, color_str, time):
        self.name = name
        self.color = color_str
        self.time = time

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class PaintMixer(object):

    online = False
    colors = [None] * colors_amount
    fills = [0] * colors_amount
    sel_amounts = [0] * colors_amount
    sel_tank = 0
    config = {'colors':[], 'fills':[]}
    color = {'name': '', 'color': '', 'time': ''}

    def __init__(self):
        self.fills = [0] * colors_amount
        self.fill_empty()

    def save_tank_info(self):
        self.config['colors'] = self.colors
        self.config['fills'] = self.fills
        j = json.dumps(self.config)
        print('Saved data')
        with open('config_saved.json', 'w') as fp:
            fp.write(j)

    def fill_random(self):
        print('fill_random')
        self.colors = [None] * 10
        for i in range(colors_amount):
            # Color instance
            self.color['name'] = 'Color ' + str(i)
            self.color['color'] = '#ABABAB'
            self.color['time'] = '0'
            self.colors[i] = self.color.copy()
            # percentage of available
            self.fills[i] = str(random.randint(0, 100))
    
    def fill_empty(self):
        print('fill_empty')
        self.colors = [None] * 10
        for i in range(colors_amount):
            # Color instance
            self.color['name'] = 'Color ' + str(i)
            self.color['color'] = '#ABABAB'
            self.color['time'] = '0'
            self.colors[i] = self.color.copy()
            # percentage of available
            self.fills[i] = '0'


    def load_tank_info(self):
        try:
            j = open('config_saved.json').read()
            c = json.loads(j)
            self.colors = c['colors']
            self.fills = c['fills']
            print('LOADED DATA')
            return True
        except FileNotFoundError:
            print("Couldn't load data")
            return False

    def set_name_for_tank(self, name, tank):
        self.colors[tank]['name'] = name
        self.save_tank_info()

    def name_for_tank(self, tank):
        return self.colors[tank]['name']

    def set_color_for_tank(self, color, tank):
        self.colors[tank]['color'] = color
        self.save_tank_info()
    
    def color_for_tank(self, tank):
        return self.colors[tank]['color']

    def set_time_for_tank(self, time, tank):
        self.colors[tank]['time'] = time
        self.save_tank_info()

    def time_for_tank(self, tank):
        return self.colors[tank]['time']

    def set_sel_amount_for_tank(self, amount, tank):
        self.sel_amounts[tank] = amount
    
    def sel_amount_for_tank(self, tank):
        return self.sel_amounts[tank]

    def set_fill_for_tank(self, percent, tank):
        self.fills[tank] = str(percent)

    def fill_for_tank(self, tank):
        return self.fills[tank]

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def fromJSON(self, j):
        self.__dict__ = json.loads(j)

    def start_serial(self):
        self.sc = SerialCommunicator()
        self.sc.start()

    def stop_serial(self):
        self.sc.stop()

    def mix_cmd(self):
        s = 'DRAIN_'
        for i in range(colors_amount):
            s = s + chr(self.sel_amounts[i])
        print('CMD:', s.encode('ascii'))
        self.sc.write(s)

    def tank_upd_cmd(self, num:int):
        self.sc.write('TANK_'+chr(num))

    def clear_eeprom_cmd(self):
        self.sc.write('EEPROM')

    def notify_action(self):
        try:
            self.sc.write(' ')
        except:
            print('Early call on notify_action')

    def notify_colors(self):
        for i in range(10):
            self.notify_color_for_tank(i)
            sleep(0.2)

    def notify_color_for_tank(self, tank):
        s = bytearray('COLOR', 'ascii')
        s.extend('_'.encode())
        s.extend(chr(tank).encode('ascii'))
        s.extend('_'.encode())
        clr = self.colors[tank]['color']
        r_str = clr[1:3]
        g_str = clr[3:5]
        b_str = clr[5:7]
        r = bytes.fromhex(r_str)
        g = bytes.fromhex(g_str)
        b = bytes.fromhex(b_str)
        s.extend(r)
        s.extend(g)
        s.extend(b)
        self.sc.write(s, encode=False)

    def obtain_data(self, no_request=False):
        if not no_request:
            self.sc.write('MAIN')
        sleep(0.2)
        try:
            print('RSP:', self.sc.response['MAIN'])
            self.fills = self.sc.response['MAIN']
        except KeyError:
            print('No data')
            self.fills = ['0'] * colors_amount
        except:
            print('No response')
        
        if self.fills is not []:
            for i in range(colors_amount):
                if not self.fills[i].isdigit():
                    self.fills[i] = '0'
        else:
            print('fills empty')
        
        self.save_tank_info()
        