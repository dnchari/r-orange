"""
<name>Row Col Picker</name>
<description>Subsets a data.frame object to pass to subsequent widgets.  Very similar to the Row Col Selector but this widget doesn't look to row or column criteria.  Instead, this widget subsets on row or column name alone, while Row Col Selector does not.</description>
<tags>Data Manipulation</tags>
<RFunctions>base:rownames,base:colnames,base:summary</RFunctions>
<icon>icons/Subset.png</icon>
<priority>2010</priority>

"""

### this is a rewright of the rowSelector and colSelector to work better than the one orriginaly written.  This widget may have less functionality than the orriginal but should conform to RedR1.7 standards.

from OWRpy import *
import OWGUI
import redRGUI

class rowcolPicker(OWRpy): # a simple widget that actually will become quite complex.  We want to do several things, give into about the variables that are selected (do a summary on the attributes and show them to the user) and to pass forward both a subsetted data.frame or a vector for classification for things evaluating TRUE to the subsetting
	settingsList = ['rowcolselect', 'newdata', 'rowactiveCriteria', 'rowselectionCriteria', 'cTableTexts', 'olddata', 'ssvdata', 'data', 'test', 'saveData']
	def __init__(self, parent=None, signalManager=None):
		OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1) #initialize the widget
		self.namesPresent = 0
		self.dataClass = None
		self.setRvariableNames(['rowcolSelector'])
        self.loadSettings()
		
		self.inputs = [('Data Table', RvarClasses.RDataFrame, self.setWidget), ('Subsetting Vector', RvarClasses.RVector, self.setSubsettingVector)]
		self.outputs = [('Data Table', RvarClasses.RDataFrame), ('Reduced Vector', RvarClasses.RVector)]
		
		self.help.setHtml('<small>The Row Column Selection widget allows one to select subsets of Data Tables.  If complex selections are required simply link many of these widgets together.  It may be useful to also consider using the Merge Data Table widget or the Melt widget when using this widget to but the data into the proper shape for later analysis.  The sections of this widget are:<br>Select by row or column<br><nbsp>- Allows you to select either rows or columns that match a certain criteria.  For example if you pick to select rows you will select based on criteria that are in the columns.<br>Attributes<br><nbsp>- Attributes are the names of the attributes that have the criteria that you will be selecting on, for example if you want to pick all rows that have a value greater than 5 in the second column the second column would be your attribute.<br>Logical<br><nbsp>- This section discribes the logic that should be applied to the selection, for example should the attribute be less than, greater than, equal to, or in a selection list.  "NOT" is also available.<br><br>One can also select based on an attached subsetting vector.  This will look for matches in the subsetting vector to values that are in your selected attribute.  This can be useful when dealing with "lists" of things that can be coerced into vectors.<br><br>This widget will send either a Data Table or a Vector depending on the dimention of your selection.')
		#set the gui
		box = OWGUI.widgetBox(self.controlArea, orientation = 'horizontal')
		self.rowcolBox = redRGUI.radioButtons(box, 'Select by row or column', ['Row', 'Column'], callback=self.rowcolButtonSelected)
		self.ISNOT = redRGUI.comboBox(box, items = ['IS', 'IS NOT'])
		self.attributes = redRGUI.listBox(box, label='Attributes')
		self.attributes.setSelectionMode(QAbstractItemView.MultiSelection)
		selectionBox = OWGUI.widgetBox(box)
		buttonsBox = OWGUI.widgetBox(selectionBox)
		self.subOnAttachedButton = OWGUI.button(buttonsBox, self, "Select on Attached", callback=self.subOnAttached)
		self.subOnAttachedButton.setEnabled(False)
		
		self.subsetButton = OWGUI.button(buttonsBox, self, "Subset", callback=self.subset)
		self.infoArea = redRGUI.textEdit(self.controlArea, '<center>Criteria not selected.  Please select a criteria to see its attributes.</center>')
		self.outputBox = redRGUI.textEdit(self.controlArea, '<center>No output generated yet.  Please make selections to generate output.</center>')
		
	def setWidget(self, data):
		if data:
			self.data = data['data']
			r = self.R('rownames('+self.data+')')
			c = self.R('colnames('+self.data+')')
			if self.rowcolBox.getChecked() == 'Row': #if we are looking at rows
				if type(r) == list:
					self.attributes.clear()
					self.attributes.addItems(r)
					self.namesPresent = 1
				else:
					self.attributes.addItems([i for i in range(self.R('length('+self.data+'[1,])'))])
					self.namesPresent = 0
			elif self.rowcolBox.getChecked() == 'Column': # if we are looking in the columns
				
				if type(c) == list:
					self.attributes.clear()
					self.attributes.addItems(c)
					self.namesPresent = 1
				else:
					self.attributes.addItems([i for i in range(self.R('length('+self.data+'[,1])'))])
					self.namesPresent = 0
			else: #by exclusion we haven't picked anything yet
				self.processingBox.setHtml('You must select either Row or Column to procede')
	def rowcolButtonSelected(self): #recall the GUI setting the data if data is selected
		print self.rowcolBox.getChecked()
		if self.data: self.setWidget({'data':self.data})
	def setSubsettingVector(self, data):
		if 'data' in data:
			self.subOnAttachedButton.setEnabled(True)
			self.ssv = data['data']
			self.ssvdata = data
		else:
			return
		
	def subOnAttached(self):
		tmpitem = self.R(self.ssv) #get the items to subset with
		if type(tmpitem) is str: #it's a string!!!!!!!
			items = []
			items.append(tmpitem)
		elif type(tmpitem) is list: #it's a list
			items = tmpitem
		elif type(tmpitem) is dict: #it's a dict
			items = []
			for key in tmpitem.keys():
				items.append(tmpitem['key'])
		#select the items in the listbox 
		print str(tmpitem)
		print str(items)
		print self.ssv
		print self.R(self.ssv)
		for i in items:
			self.attributes.setItemSelected(self.attributes.findItems(i, Qt.MatchExactly)[0], 1)
			print i
	def attributeSelected(self, item): # an item in the row or column section was clicked and you need to set the attList or give some infromation about the row or column for the user to make a decision.  In the case of continuous data we want to show the line edit for generating logic.  In the case of a set of text values or factors we want to show the factors so the user can select them.  We could also look for class infromation so that we could tell the user what she classified the data as.
		if self.data == None: return
		
		
		if self.rowcolBox.getChecked() == 'Row': #if we are selecting rows
			if self.namesPresent:
				name = '"'+str(item.text())+'"'
			else:
				name = str(item.text())
			self.attName = name
			self.R('t<-'+self.data+'[,'+name+']') # set a temp variable for the selections made.
			c = self.R('class(t)')
			self.classifyData(c)

		elif self.rowcolBox.getChecked() == 'Column': # if we are selecting columns
			if self.namesPresent:
				name = '"'+item.text()+'"'
			else:
				name = item.text()
				
			self.R('t<-'+self.data+'['+name+',]')
			c = self.R('class(t)')
			self.classifyData(c)

		else: #by exclusion we haven't picked anything yet
			self.processingBox.setHtml('You must select either Row or Column to procede')
		
	def classifyData(self, c):
		if c == 'character':
			self.attsList.show()
			self.attsLineEdit.hide()
			self.attsList.clear()
			self.attsList.addItems(self.R('t'))
			self.infoArea.setHtml('Character attribute detected.  The attribute can be seen to the right of the logic box.  Multiple items can be selected for subsetting.')
			self.dataClass = 'character'
		elif c == 'factor':
			self.attsLineEdit.hide()
			self.attsList.show()
			self.attsList.clear()
			self.attsList.addItems(self.R('levels(t)'))
			self.R('txt<-capture.output(summary(t))')
			tmp = self.R('paste(txt, collapse ="\n")')
			self.infoArea.setHtml('A list of factors was detected.  These are often used for classification.  Multiple items can be selected for subsetting.<br><br>Summary:<br><pre>'+tmp+'</pre>')
			self.dataClass = 'factor'
		elif c == 'numeric':
			self.attsList.hide()
			self.attsLineEdit.show()
			self.attsLineEdit.clear()
			self.attsList.clear()
			self.R('txt<-capture.output(summary(t))')
			tmp = self.R('paste(txt, collapse ="\n")')
			self.infoArea.setHtml('Numeric data was detected.  You may use the line edit to the right of the logic box to select boundries for subsetting.<br><br>Summary:<br><pre>'+tmp+'</pre>')
			self.dataClass = 'numeric'
			
	def subset(self): # now we need to make the R command that will handle the subsetting.
		if self.data == None: return
		
		if self.ISNOT.currentText() == 'IS': isNot = ''
		elif self.ISNOT.currentText() == 'IS NOT': isNot = '!' 
		
		
	
		selectedDFItems = []
		for name in self.attributes.selectedItems():
			selectedDFItems.append('"'+str(name.text())+'"') # get the text of the selected items
		
		if self.rowcolBox.getChecked() == 'Row':
			self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'['+isNot+'rownames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+',]')
		elif self.rowcolBox.getChecked() == 'Column':
			self.R(self.Rvariables['rowcolSelector']+'<-'+self.data+'[,'+isNot+'colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+']')
				
		self.rSend('Data Table', {'data':self.Rvariables['rowcolSelector']})
				
		
		self.R('txt<-capture.output('+self.Rvariables['rowcolSelector']+'[1:5,])')
		tmp = self.R('paste(txt, collapse ="\n")')
		self.outputBox.setHtml('A sample of your selection is shown.  Ignore any values with NA.<pre>'+tmp+'</pre>')
			