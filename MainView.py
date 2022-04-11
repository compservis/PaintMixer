from multiprocessing.dummy import freeze_support
import random
import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import QPainter, QColor, QBrush, QPixmap
from pyrsistent import pmap
from paintmixer import PaintMixer
from colorbar import ColorSelector
import jsonpickle
import os

from settingsview import SettingWindow

pm = PaintMixer()
pm.load_tank_info()

j = jsonpickle.encode(pm)
with open('config_saved.json', 'w') as fp:
    fp.write(j)
print(pm.toJSON())
print(j)


class TopBar(QWidget):

    _bg_color = '#ABABAB'

    def __init__(self):
        super().__init__()
        header_layout = QHBoxLayout()
        self.help_btn = QPushButton("HELP")
        self.edit_btn = QPushButton("EDIT")
        title_lbl = QLabel("Select colors to mix")

        self.setFixedHeight(80)

        self.help_btn.setFixedSize(QSize(100,40))
        self.edit_btn.setFixedSize(QSize(100,40))

        header_layout.addWidget(self.help_btn)
        header_layout.addStretch(1)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch(1)
        header_layout.addWidget(self.edit_btn)

        self.setLayout(header_layout)

    def paintEvent(self, event):
        painter = QPainter(self)
        brush = QBrush()
        rect = QRect(0, 0, painter.device().width(), painter.device().height())
        brush.setColor(QColor(0, 0, 0))
        painter.fillRect(rect, brush)
        painter.end()


class MainWidget(QWidget):

    color_is_checked = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint mixer")

        self.setFixedSize(QSize(1024,600))

        layout = QVBoxLayout()
        center_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        self.top_bar = TopBar()

        center_layout.addStretch(1)
        self.color_selectors = []
        for i in range(10):
            self.color_selectors.append(ColorSelector(name=pm.name_for_tank(i), color=pm.color_for_tank(i), percent=pm.fill_for_tank(i)))
            self.color_selectors[i].num = i
            self.color_selectors[i].stateChanged.connect(self.selector_checked)
            self.color_selectors[i].reset.connect(self.reset)
            center_layout.addWidget(self.color_selectors[i])
            center_layout.addStretch(1)

        bottom_layout.addWidget(QLabel("ADD:"))
        add_btns = [QPushButton("+1 g"), QPushButton("+5 g"), QPushButton("+10 g")]
        sub_btns = [QPushButton("-1 g"), QPushButton("-5 g"), QPushButton("-10 g")]
        for i in range(3):
            add_btns[i].setFixedSize(QSize(50,40))
            bottom_layout.addWidget(add_btns[i])
        bottom_layout.addWidget(QLabel("SUBTRACT:"))
        for i in range(3):
            sub_btns[i].setFixedSize(QSize(50,40))
            bottom_layout.addWidget(sub_btns[i])
        bottom_layout.addStretch(1)
        self.mix_btn = QPushButton("MIX")
        self.mix_btn.setFixedSize(QSize(100,40))
        bottom_layout.addWidget(self.mix_btn)

        layout.addWidget(self.top_bar)
        layout.addStretch()
        layout.addLayout(center_layout)
        layout.addStretch()
        layout.addLayout(bottom_layout)

        add_btns[0].clicked.connect(self.add_1)
        add_btns[1].clicked.connect(self.add_5)
        add_btns[2].clicked.connect(self.add_10)

        sub_btns[0].clicked.connect(self.sub_1)
        sub_btns[1].clicked.connect(self.sub_5)
        sub_btns[2].clicked.connect(self.sub_10)

        self.setLayout(layout)

        self.top_bar.update()


    def selector_checked(self, num):
        print("sel_checked")
        pm.sel_tank = num
        pm.notify_action()
        for i in range(10):
            if self.color_selectors[i].num != num:
                self.color_selectors[i].setChecked(False)
                self.color_selectors[i].refresh()
        
    def help_clicked(self):
        pm.notify_action()
        print("Show help")

    def edit_clicked(self):
        pm.notify_action()
        print("Show settings")

    def reset(self, num):
        pm.notify_action()
        pm.set_sel_amount_for_tank(0, num)

    def _add(self, n):
        pm.notify_action()
        pm.set_sel_amount_for_tank(pm.sel_amounts[pm.sel_tank] + n, pm.sel_tank)
        self.color_selectors[pm.sel_tank].setAmount(pm.sel_amount_for_tank(pm.sel_tank))
        self.color_selectors[pm.sel_tank].refresh()
        print("add", n, "g to", pm.sel_amounts[pm.sel_tank]-n)

    def _sub(self, n):
        pm.notify_action()
        pm.set_sel_amount_for_tank(pm.sel_amounts[pm.sel_tank] - n, pm.sel_tank)
        if pm.sel_amount_for_tank(pm.sel_tank) < 0:
            pm.set_sel_amount_for_tank(0, pm.sel_tank)
        self.color_selectors[pm.sel_tank].setAmount(pm.sel_amounts[pm.sel_tank])
        self.color_selectors[pm.sel_tank].refresh()
        print("subtract", n, "g from", pm.sel_amounts[pm.sel_tank] - n)

    def add_1(self):
        self._add(1)

    def add_5(self):
        self._add(5)

    def add_10(self):
        self._add(10)

    def sub_1(self):
        self._sub(1)

    def sub_5(self):
        self._sub(5)

    def sub_10(self):
        self._sub(10)

    def update_selectors(self):
        for i in range(10):
            self.color_selectors[i].setName(pm.name_for_tank(i))
            self.color_selectors[i].setColor(pm.color_for_tank(i))
            self.color_selectors[i].setPercentage(pm.fill_for_tank(i))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.main = MainWidget()
        self.settings = SettingWindow()

        self.i = 0
        self.settings_widget_update()
        self.settings.s.allowSaveColor.connect(self.save_settings_color)
        self.settings.s.allowSaveName.connect(self.save_settings_name)

        pm.start_serial()

        self.main.top_bar.edit_btn.clicked.connect(self.show_settings)
        self.settings.top.btn.clicked.connect(self.show_main)
        self.settings.s.btn_next.clicked.connect(self.settings_next)
        self.settings.s.btn_prev.clicked.connect(self.settings_prev)
        self.settings.s.full_btn.clicked.connect(self.set_full)
        self.main.mix_btn.clicked.connect(pm.mix_cmd)

        pm.obtain_data()
        pm.notify_colors()

        self.notifier = QSocketNotifier(pm.sc.reader, QSocketNotifier.Read, self)
        self.notifier.setEnabled(True)
        self.notifier.activated.connect(self.handle_incoming_data)


        l = QStackedLayout()
        l.addWidget(self.main)
        l.addWidget(self.settings)

        self.setWindowTitle('Paint Mixer v1.1')

        q = QWidget()
        q.setLayout(l)
        self.setCentralWidget(q)
        self.show_main()

    def handle_incoming_data(self):
        with open('/tmp/pmsock') as f: t = f.read()
        if t == '1':
            print('GOT', t, 'FROM SOCKET')
            t = '0'
            with open('/tmp/pmsock', 'w') as f:
                f.write(t)
                print('WRITTEN', t, 'TO SOCKET')
            
            print('SHOW MAIN')
            self.show_main(no_request=True)

    def save_settings_color(self, color):
        pm.set_color_for_tank(color, self.i)
        pm.notify_color_for_tank(self.i)
        pm.save_tank_info()

    def save_settings_name(self, name):
        pm.set_name_for_tank(name, self.i)
        pm.save_tank_info()

    def set_full(self):
        pm.set_fill_for_tank(100, self.i)
        pm.tank_upd_cmd(self.i)
        pm.save_tank_info

    def set_clear(self):
        pm.set_fill_for_tank(0, self.i)
        pm.clear_eeprom_cmd()
        pm.save_tank_info

    def settings_next(self):
        self.i = self.i + 1
        if self.i > 9:
            self.i = 0
        self.settings_widget_update()

    def settings_prev(self):
        self.i = self.i - 1
        if self.i < 0:
            self.i = 9
        self.settings_widget_update()

    def settings_widget_update(self):
        pm.notify_action()
        self.settings.s.setColorAndNum(col = pm.color_for_tank(self.i),num = self.i+1)
        self.settings.s.setColor(pm.color_for_tank(self.i))
        self.settings.s.setName(pm.name_for_tank(self.i))


    def show_settings(self):
        pm.notify_action()
        self.main.hide()
        self.settings.show()
        self.settings.start_keyboard()

    def show_main(self, no_request=False):
        pm.notify_action()
        pm.obtain_data(no_request)
        self.main.update_selectors()
        self.main.show()
        self.settings.hide()
        self.settings.finish_keyboard()
        self.main.update()


if __name__ == '__main__':
    freeze_support()
    
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()

    pm.stop_serial()