from redRGUI import widgetState
from libraries.base.qtWidgets.widgetBox import widgetBox
from libraries.base.qtWidgets.widgetLabel import widgetLabel
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from OrderedDict import OrderedDict
import redRLog
class comboBox(QComboBox,widgetState):
    def __init__(self,widget,label=None, displayLabel=True, includeInReports=True, 
    items=None, itemIds=None,editable=False,
    orientation='horizontal',callback = None):
        
        widgetState.__init__(self,widget,label,includeInReports)
        QComboBox.__init__(self,self.controlArea)
        
        if displayLabel:
            self.hb = widgetBox(self.controlArea,orientation=orientation)
            widgetLabel(self.hb, label)
            self.hb.layout().addWidget(self)
            self.hasLabel = True
        else:
            self.controlArea.layout().addWidget(self)
            self.hasLabel = False
        self.label = label

        self.items = OrderedDict()
        self.setEditable(editable)

        if items:
            self.addItems(items)

        if callback:
            QObject.connect(self, SIGNAL('activated(int)'), callback)

    def getSettings(self):            
        r = {'items':self.items,
             'current':self.currentIndex()}
        return r
    
    def loadSettings(self,data):
        # print 'in comboBox load'
        # print data

        self.addItems(data['items'])
        self.setCurrentIndex(data['current'])
    
    def currentId(self):
        return self.items.keys()[self.currentIndex()]
    def currentItem(self):
        return {self.items.keys()[self.currentIndex()]:self.items.values()[self.currentIndex()]}
        
    def addItems(self,items):
        if type(items) in [dict,OrderedDict]:
            for k,v in items.items():
                self.addItem(k,v)
        elif type(items) in [list]:
            if len(items) > 0 and type(items[0]) is tuple:
                for k,v in items:
                    self.addItem(k,v)
            else:
                for v in items:
                    self.addItem(v,v)
            redRLog.log(redRLog.REDRCORE,redRLog.DEBUG,'In listBox should not use list')
        else:
            raise Exception('In comboBox, addItems takes a list, dict or OrderedDict')
        
    def clear(self):
        QComboBox.clear(self)
        self.items = OrderedDict()
    def addItem(self,id,item):
        QComboBox.addItem(self,item)
        self.items[id] = item
            
    def getReportText(self, fileDir):

        r = {self.widgetName:{'includeInReports': self.includeInReports, 'text': self.currentText()}}
        #return '%s set to %s' % (self.label, self.currentText())
        return r
