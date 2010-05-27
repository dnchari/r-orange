"""
<name>Apply Math</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<description>Applies math across a data table.  These functions could include max (maximum value), mean (the mean value), median (median value), etc.>description>
<RFunctions>:apply</RFunctions>
<tags>Data Manipulation</tags>
<icon>icons/rexecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class apply(OWRpy): 
        settingsList = []
        def __init__(self, parent=None, signalManager=None):
                OWRpy.__init__(self, parent, signalManager, "Apply", wantMainArea = 0, resizingEnabled = 1)
                self.setRvariableNames(["apply", 'apply_cm'])
                self.data = {}
                 
                self.RFunctionParam_X = ''
                self.inputs = [("X", signals.RDataFrame, self.processX)]
                self.outputs = [("apply Output", signals.RVector)]
                
                self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
                box = redRGUI.tabWidget(self.controlArea)
                self.standardTab = box.createTabPage(name = "Standard")
                self.advancedTab = box.createTabPage(name = "Advanced")
                self.RFunctionParamFUN_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "Function:", text = '')
                self.RFunctionParamMARGIN_radioButtons =  redRGUI.radioButtons(self.standardTab,  label = "Apply this across each:", buttons = ['Rows', 'Columns'])
                redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        def processX(self, data):
                if data:
                        self.RFunctionParam_X=data.getData()
                        self.data = data
                        self.commitFunction()
                else:
                    self.RFunctionParam_X=''
        def commitFunction(self):
                if str(self.RFunctionParam_X) == '': return
                if str(self.RFunctionParamFUN_lineEdit.text()) == '': return
                if self.RFunctionParamMARGIN_radioButtons.getChecked() == []: return
                injection = []
                if str(self.RFunctionParamFUN_lineEdit.text()) != '':
                        string = 'FUN='+str(self.RFunctionParamFUN_lineEdit.text())
                        injection.append(string)
                if 'Rows' in self.RFunctionParamMARGIN_radioButtons.getChecked():
                        string = 'MARGIN='+str(1)
                        injection.append(string)
                else:
                        string = 'MARGIN = '+str(2)
                        injection.append(string)
                inj = ','.join(injection)
                self.R(self.Rvariables['apply']+'<-apply(X='+str(self.RFunctionParam_X)+','+inj+')')
                
                newData = signals.RVector(data = self.Rvariables['apply'])

                self.rSend("apply Output", newData)