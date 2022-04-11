# colorbar.py

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import QPainter, QColor, QBrush, QPixmap

class ColorBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.color = QColor(0,0,0)

        self.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )

        self.pic_back = QPixmap(r'TankBack.png')
        self.pic_front = QPixmap(r'TankFront.png')

        self.lbl = QLabel("%")
        self.lbl.setAlignment(Qt.AlignCenter)
        l = QVBoxLayout()
        l.addStretch(3)
        l.addWidget(self.lbl)
        l.addStretch(1)
        self.setLayout(l)
        self.refresh()
        self.show()

    def paintEvent(self, e):
        painter = QPainter(self)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        f_rect = QRect(0, 0, painter.device().width(), painter.device().height())
        brush.setColor(QColor('black'))
        painter.fillRect(f_rect, brush)
        painter.drawPixmap(f_rect, self.pic_back)
        rect = QRect(0, painter.device().height()-painter.device().height()*int(self.percent)/100, painter.device().width(), painter.device().height())
        brush.setColor(self.color)
        painter.fillRect(rect, brush)
        painter.drawPixmap(f_rect, self.pic_front)
        painter.end()

    def sizeHint(self):
        return QSize(80,350)

    def mousePressEvent(self, e):
        print("forwarding to parent")
        self.parent.mousePressEvent(e)

    def refresh(self):
        self.percent = self.parent.percent
        self.color.setNamedColor(self.parent.color_str)
        self.lbl.setText(str(self.percent) + " %")
        self.update()


class CloakButton(QPushButton):

    clicked = Signal()

    def __init__(self, name, width=100, height=60):
        super().__init__()
        self.setFixedSize = QSize(width, height)
        l = QVBoxLayout()
        self._btn = QPushButton(name)
        # self._btn.setFixedSize(QSize(width,height))
        self._btn.clicked.connect(self.forward_press)
        self._btn.setVisible(False)
        l.addWidget(self._btn)
        self.setLayout(l)

    def sizeHint(self):
        return QSize(100,60)

    def forward_press(self):
        self.clicked.emit()

    def cloak(self):
        self._btn.setVisible(False)

    def uncloak(self):
        self._btn.setVisible(True)

    def paintEvent(self, e):
        pass


class ColorSelector(QAbstractButton):

    name = ''
    color_str = ''
    percent = 0
    sel_amount = 0
    num = None

    stateChanged = Signal(int)
    reset = Signal(int)

    def __init__(self, name, color, percent):
        super().__init__()

        self.name = name
        self.color_str = color
        self.percent = percent

        self.setCheckable(True)

        self.setFixedSize(QSize(100, 400))

        self.amount_lbl = QLabel(str(self.sel_amount) + ' g')
        self.amount_lbl.setAlignment(Qt.AlignCenter)
        self.reset_btn = CloakButton('RESET')
        self.reset_btn.clicked.connect(self.reset_clicked)
        self.colorbar = ColorBar(parent=self)
        self.name_lbl = QLabel(self.name)
        self.name_lbl.setAlignment(Qt.AlignCenter)

        self.clicked.connect(self.debug)

        layout = QVBoxLayout()
        layout.addWidget(self.name_lbl)
        layout.addWidget(self.colorbar)
        layout.addStretch(1)
        layout.addWidget(self.amount_lbl)
        layout.addStretch(1)
        layout.addWidget(self.reset_btn)

        

        self.setLayout(layout)

    def debug(self):
        self.stateChanged.emit(self.num)

    def setName(self, name):
        self.name = name
        self.refresh()

    def setColor(self, color_str:str):
        self.color_str = color_str
        self.refresh()
    
    def setPercentage(self, percent):
        self.percent = percent
        self.refresh()

    def setAmount(self, amount):
        self.sel_amount = amount

    def reset_clicked(self):
        self.setAmount(0)
        self.reset.emit(self.num)
        self.refresh()


    def paintEvent(self, e):
        painter = QPainter(self)
        brush = QBrush()
        brush.setStyle(Qt.SolidPattern)
        rect = QRect(0, 0, self.width(), self.height())

        if self.isChecked():
            brush.setColor(QColor(255, 255, 255, 127))
            painter.fillRect(rect, brush)
        else:
            brush.setColor(QColor(0,0,0,0))
            painter.fillRect(rect, brush)
        painter.end()
        

    def refresh(self):
        self.amount_lbl.setText(str(self.sel_amount) + ' g')
        self.name_lbl.setText(str(self.name))
        if bool(self.sel_amount):
            self.reset_btn.uncloak()
        else:
            self.reset_btn.cloak()
        self.colorbar.refresh()
        self.reset_btn.update()
        self.update()


