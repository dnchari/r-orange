from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class button(QPushButton,widgetState):
    def __init__(self,widget,label, callback = None, disabled=0, icon=None, 
    toolTip=None, width = None, height = None,align='left', toggleButton = False, addToLayout = 1):
        if icon:
            QPushButton.__init__(self,QIcon(icon), label,widget)
        else:
            QPushButton.__init__(self,label,widget)

        if addToLayout and widget.layout():
            widget.layout().addWidget(self)
            if align=='left':
                widget.layout().setAlignment(self, Qt.AlignLeft)
            elif align=='right':
                widget.layout().setAlignment(self, Qt.AlignRight)
        
        if icon or width == -1:
            pass
        elif width: 
            self.setFixedWidth(width)
        elif len(label)*7+5 < 50:
            self.setFixedWidth(50)
        else:
            self.setFixedWidth(len(label)*7+5)
            
        if height:
            self.setFixedHeight(height)
        self.setDisabled(disabled)
        
        if toolTip:
            self.setToolTip(toolTip)
            
        if toggleButton:
            self.setCheckable(True)
            
        if callback:
            QObject.connect(self, SIGNAL("clicked()"), callback)
            
    def getSettings(self):
        pass
    def loadSettings(self,data):
        pass
