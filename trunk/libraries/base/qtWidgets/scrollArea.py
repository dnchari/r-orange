from redRGUI import widgetState
from PyQt4.QtCore import *
from PyQt4.QtGui import *

        
class scrollArea(QScrollArea,widgetState):
    def __init__(self,widget, orientation=QVBoxLayout(), addSpace=False, 
    sizePolicy = None, margin = -1, spacing = -1, addToLayout = 1):

        QScrollArea.__init__(self,widget)
            
        if margin == -1: margin = 0
        # self.setFlat(flat)
        if widget.layout():
            widget.layout().addWidget(self)
        
        try:
            if isinstance(orientation, QLayout):
                self.setLayout(orientation)
            elif orientation == 'horizontal' or not orientation:
                self.setLayout(QHBoxLayout())
            else:
                self.setLayout(QVBoxLayout())
        except:
            self.setLayout(QVBoxLayout())
            
        if self.layout() == 0 or self.layout() == None:
            self.setLayout(QVBoxLayout())

        if sizePolicy:
            self.setSizePolicy(sizePolicy)
        # else:
            # self.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        
            

        if spacing == -1: spacing = 4
        self.layout().setSpacing(spacing)
        if margin != -1:
            self.layout().setMargin(margin)

        if addSpace and isinstance(addSpace, int):
            separator(widget, 0, addSpace)
        elif addSpace:
            separator(widget)
