from PySide2.QtWidgets import *
from PySide2.QtCore import *

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

from colorbar import CloakButton

class MButton(QAbstractButton):
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 100)
        self.setCheckable(True)
        self.clicked.connect(self.debug)

        l = QVBoxLayout()
        l.addWidget(QLabel("Press me!"))

        self.setLayout(l)

    def debug(self):
        print(self.isChecked())

    def paintEvent(self, e):
        painter = QPainter(self)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        rect = QRect(0, 0, self.width(), self.height())
        
        if self.isChecked():
            brush.setColor(QColor('red'))
            painter.fillRect(rect, brush)
        else:
            brush.setColor(QColor('green'))
            painter.fillRect(rect, brush)
        painter.end()


class NavButton(QPushButton):
    def __init__(self, n):
        super().__init__(n)

class ColorBox(QWidget):
    def __init__(self):
        super().__init__()
        self.color = QColor(0,0,0)
        self.num = 0

        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        self.setFixedSize(QSize(80,80))

        self.pic_back = QPixmap(r'TankBack.png')
        self.pic_front = QPixmap(r'TankFront.png')

        self.lbl = QLabel()
        self.lbl.setAlignment(Qt.AlignCenter)
        l = QVBoxLayout()
        l.addStretch(1)
        l.addWidget(self.lbl)
        l.addStretch(1)
        self.setLayout(l)
        self.setColorAndNum('#000000', self.num)
        self.refresh()
    
    def setColorAndNum(self, color, num):
        self.color.setNamedColor(color)
        self.num = num
        txt = ''
        txt = str(self.num).zfill(2)
        self.lbl.setText(txt)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        f_rect = QRect(0, 0, painter.device().width(), painter.device().height())
        painter.drawPixmap(f_rect, self.pic_back)
        rect = QRect(0, 0, painter.device().width(), painter.device().height())
        brush.setColor(self.color)
        painter.fillRect(rect, brush)
        painter.drawPixmap(f_rect, self.pic_front)
        painter.end()

    def sizeHint(self):
        return QSize(80,80)

    def mousePressEvent(self, e):
        print("forwarding to parent")
        self.parent.mousePressEvent(e)

    def refresh(self):
        self.update()

class TopBar(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedHeight(80)
        self.lbl = QLabel("Edit colors")
        self.btn = QPushButton("DONE")
        self.btn.setFixedSize(QSize(100,40))
        self.btn2 = CloakButton("DONE", height=40)
        self.btn2.cloak()
        l = QHBoxLayout()
        l.addWidget(self.btn2)
        l.addStretch()
        l.addWidget(self.lbl)
        l.addStretch()
        l.addWidget(self.btn)
        self.setLayout(l)


class Setting(QWidget):

    allowSaveColor = Signal(str)
    allowSaveName = Signal(str)
    nextColor = Signal()
    prevColor = Signal()

    def __init__(self):
        super().__init__()
        self.btn_prev = NavButton("PREV")
        self.btn_next = NavButton("NEXT")

        self.color_indicator = ColorBox()
        self.name_lbl = QLabel("NAME")
        self.col_lbl = QLabel("COLOR")
        self.time_lbl = QLabel(" ")
        self.name_txt = QLineEdit()
        self.col_txt = QLineEdit()
        self.full_btn = QPushButton('Set as full')

        timeRX = QRegularExpression("\d+")
        colRX = QRegularExpression("([aA-fF]?+|\d)+")

        self.col_txt.textChanged.connect(self.checkColor)
        self.name_txt.textChanged.connect(self.checkName)
        self.col_txt.setMaxLength(6)
        self.col_txt.setValidator(QRegularExpressionValidator(colRX))

        lmain = QHBoxLayout()
        lind = QVBoxLayout()
        lind.addStretch()
        lind.addWidget(self.color_indicator)
        lind.addStretch()
        lname = QVBoxLayout()
        lname.addStretch()
        lname.addWidget(self.name_lbl)
        lname.addWidget(self.name_txt)
        lname.addStretch()
        lcol = QVBoxLayout()
        lcol.addStretch()
        lcol.addWidget(self.col_lbl)
        lcol.addWidget(self.col_txt)
        lcol.addStretch()
        ltime = QVBoxLayout()
        ltime.addStretch()
        ltime.addWidget(self.time_lbl)
        ltime.addWidget(self.full_btn)
        ltime.addStretch()
        lcentral = QHBoxLayout()
        lcentral.addLayout(lind)
        lcentral.addLayout(lname)
        lcentral.addLayout(lcol)
        lcentral.addLayout(ltime)
        lmain.addWidget(self.btn_prev)
        lmain.addStretch()
        lmain.addLayout(lcentral)
        lmain.addStretch()
        lmain.addWidget(self.btn_next)

        self.setLayout(lmain)

    def checkColor(self, s:str):
        if len(s) == 6:
            s = "#" + s
            self.color_indicator.color.setNamedColor(s)
            self.color_indicator.refresh()
            self.allowSaveColor.emit(s)


    def checkName(self, s):
        if s != "":
            self.allowSaveName.emit(s)

    def setColorAndNum(self, col, num):
        self.color_indicator.setColorAndNum(col, num)

    def setName(self, name:str):
        self.name_txt.setText(name)

    def setColor(self, col):
        col = col.replace("#", "")
        self.col_txt.setText(str(col))        

class SettingWindow(QWidget):

    color_is_checked = False

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint mixer")

        self.setFixedSize(QSize(1024,600))
        self.top = TopBar()
        self.s = Setting()

        self.kb = None

        l = QVBoxLayout()
        l.addWidget(self.top)
        l.addStretch()
        l.addWidget(self.s)
        l.addStretch(3)
        self.setLayout(l)

    def start_keyboard(self):
        print('Show keyboard')
        if self.kb is None:
            self.kb = QProcess()
            self.kb.startDetached("matchbox-keyboard", [''])

    def finish_keyboard(self):
        print('Hide keyboard')
        if self.kb is not None:
            self.kb.kill()
            self.kb = None
