"""
<name>sizeplot</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>plotrix:sizeplot</RFunctions>
<tags>Prototypes</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
from libraries.base.qtWidgets.lineEdit import lineEdit
from libraries.base.qtWidgets.tabWidget import tabWidget
from libraries.base.qtWidgets.button import button
class sizeplot(OWRpy): 
	settingsList = []
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self)
		self.RFunctionParam_y = ''
		self.RFunctionParam_x = ''
		self.inputs = [("y", signals.RVector, self.processy),("x", signals.RVector, self.processx)]
		
		#self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
		box = tabWidget(self.controlArea)
		self.standardTab = box.createTabPage(name = "Standard")
		self.advancedTab = box.createTabPage(name = "Advanced")
		self.RFunctionParamy_lineEdit =  lineEdit(self.standardTab,  label = "y:", text = '')
		self.RFunctionParamx_lineEdit =  lineEdit(self.standardTab,  label = "x:", text = '')
		self.RFunctionParamscale_lineEdit =  lineEdit(self.standardTab,  label = "scale:", text = '1')
		self.RFunctionParamsize_lineEdit =  lineEdit(self.standardTab,  label = "size:", text = 'c(1,4)')
		self.RFunctionParampow_lineEdit =  lineEdit(self.standardTab,  label = "pow:", text = '0.5')
		redRCommitButton(self.bottomAreaRight, "Commit", callback = self.commitFunction)
	def processy(self, data):
		if not self.require_librarys(["plotrix"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_y=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_y=''
	def processx(self, data):
		if not self.require_librarys(["plotrix"]):
			self.status.setText('R Libraries Not Loaded.')
			return
		if data:
			self.RFunctionParam_x=data.getData()
			#self.data = data
			self.commitFunction()
		else:
			self.RFunctionParam_x=''
	def commitFunction(self):
		if unicode(self.RFunctionParam_y) == '': return
		if unicode(self.RFunctionParam_x) == '': return
		injection = []
		if unicode(self.RFunctionParamy_lineEdit.text()) != '':
			string = 'y='+unicode(self.RFunctionParamy_lineEdit.text())+''
			injection.append(string)
		if unicode(self.RFunctionParamx_lineEdit.text()) != '':
			string = 'x='+unicode(self.RFunctionParamx_lineEdit.text())+''
			injection.append(string)
		if unicode(self.RFunctionParamscale_lineEdit.text()) != '':
			string = 'scale='+unicode(self.RFunctionParamscale_lineEdit.text())+''
			injection.append(string)
		if unicode(self.RFunctionParamsize_lineEdit.text()) != '':
			string = 'size='+unicode(self.RFunctionParamsize_lineEdit.text())+''
			injection.append(string)
		if unicode(self.RFunctionParampow_lineEdit.text()) != '':
			string = 'pow='+unicode(self.RFunctionParampow_lineEdit.text())+''
			injection.append(string)
		inj = ','.join(injection)
		self.R('sizeplot(y='+unicode(self.RFunctionParam_y)+',x='+unicode(self.RFunctionParam_x)+','+inj+')')