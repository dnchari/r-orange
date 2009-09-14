"""
<name>Row Selection</name>
<description>Subsets a data.frame object to pass to subsequent widgets.</description>
<icon>icons/Subset.png</icon>

"""

from OWRpy import *
import OWGUI

class rowSelector(OWRpy): # a simple widget that actually will become quite complex.  We want to do several things, give into about the variables that are selected (do a summary on the attributes and show them to the user) and to pass forward both a subsetted data.frame or a vector for classification for things evaluating TRUE to the subsetting
    settingsList = ['vs', 'rowcolselect', 'newdata']
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        
        self.vs = self.variable_suffix
        self.setRvariableNames(['data', 'result'])
        self.collist = '' # a container for the names of columns that will be picked from the selector.
        self.rowcolselect = 1
        self.GorL = 0
        self.rowselectionCriteria = 0 # Counters for the criteria of selecting Rows and Cols
        self.rowactiveCriteria = [] # lists showing the active critera for subsetting the rows and cols
        self.RowColNamesExist = 1
        self.searchLineEdit = ''
        self.newdata = {}
        self.sentalready = 0
        
        self.inputs = [("R DataFrame", RvarClasses.RDataFrame, self.process), ("Subsetting Vector", RvarClasses.RVector, self.ssvAttached)]
        self.outputs = [("R DataFrame", RvarClasses.RDataFrame), ("Classified Vector Subset", RvarClasses.RVector)]
        
        # ###  GUI ###
        infobox = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(infobox, "Data not loaded")
        self.infob = OWGUI.widgetLabel(infobox, "")
        # The GUI should have a few attributes such as a selector for using either the rows or columns (columns should be the default) when an attribute is selected a summary of that should be printed on the GUI.  It would be nice if we could implement multipe selection criteria for a single widget.
        layk = QWidget(self)
        self.controlArea.layout().addWidget(layk)
        grid = QGridLayout()
        grid.setMargin(0)
        layk.setLayout(grid)
        
        # first implement a widget that allows for selection of options
        options = OWGUI.widgetBox(self.controlArea, "Options")
        grid.addWidget(options, 0,0)
        self.subOnAttachedButton = OWGUI.button(options, self, "Subset on Attached List", callback = self.subOnAttached)
        self.subOnAttachedButton.setEnabled(False)
        self.tableinfoa = OWGUI.widgetLabel(options, "No Data Connected")
        self.tableinfob = OWGUI.widgetLabel(options, "")
        self.tableinfoc = OWGUI.widgetLabel(options, "")
        self.tableinfod = OWGUI.widgetLabel(options, "")
        
        # a names box that shows the names of either the columns or the rows as well as the colnames or rownames
        namesBox = OWGUI.widgetBox(self.controlArea, "Factor Names")
        grid.addWidget(namesBox, 0, 1)
        self.columnsorrows = OWGUI.listBox(namesBox, self, callback = self.subListAdd) # Adds the selected item to the subset list
        
        # a summary box that shows the R summary of the selected row or columns
        
        self.boxIndices = {}
        self.valuesStack = QStackedWidget(self)
        grid.addWidget(self.valuesStack, 0, 2)
        
        # valuesStack 0: No data selected
        boxVal = OWGUI.widgetBox(self, "Values", addToLayout = 0)
        self.boxIndices[0] = boxVal
        self.valuesStack.addWidget(boxVal)
        
        # valuesStack 1: continuous data
        boxVal = OWGUI.widgetBox(self, "Values", addToLayout = 0)
        self.boxIndices[1] = boxVal
        self.StatTable = QTableWidget()
        boxVal.layout().addWidget(self.StatTable)
        self.SubSlider = QSlider()
        self.SubSlider.setOrientation(Qt.Horizontal)
        self.connect(self.SubSlider, SIGNAL('valueChanged(int)'), self.SubSliderValueChanged)
        boxVal.layout().addWidget(self.SubSlider)
        self.numericInfo = OWGUI.widgetLabel(boxVal, "")
        greaterLessRadio = OWGUI.radioButtonsInBox(boxVal, self, 'GorL', ['Greater Than', 'Less Than'])
        OWGUI.button(boxVal, self, "Select Criteria", callback = self.selectCriteria)
        self.valuesStack.addWidget(boxVal)
        
        # valuesStack 2: factor data
        boxVal = OWGUI.widgetBox(self, "Values", addToLayout = 0)
        self.boxIndices[2] = boxVal
        self.FactorTable = QTableWidget()
        boxVal.layout().addWidget(self.FactorTable)
        #insert a searchbox
        self.FactorList = OWGUI.listBox(boxVal, self)
        self.FactorList.setSelectionMode(QAbstractItemView.MultiSelection)
        sle = OWGUI.lineEdit(boxVal, self, 'searchLineEdit', 'Search:')
        self.connect(sle, SIGNAL("textChanged(QString)"), self.highlightItems) 
        OWGUI.button(boxVal, self, "Select Criteria", callback = self.selectCriteria)
        self.valuesStack.addWidget(boxVal)
        self.connect(self.FactorTable, SIGNAL("itemClicked(QTableWidgetItem*)"), self.selectCriteria)
        
        # values Stack 3: row/col names
        boxVal = OWGUI.widgetBox(self, "Values", addToLayout = 0)
        self.boxIndices[3] = boxVal
        self.namesList = OWGUI.listBox(boxVal, self)
        self.namesList.setSelectionMode(QAbstractItemView.MultiSelection)
        OWGUI.button(boxVal, self, "Select Criteria", callback = self.rowcolNamesSelect)
        self.valuesStack.addWidget(boxVal)

        
        # A box that lists the criteria for the selected attributes.
        #criteriaBox = OWGUI.widgetBox(self.controlArea, "Criteria")
        self.criteriaTable = QTableWidget()
        self.controlArea.layout().addWidget(self.criteriaTable)
        self.criteriaTable.setColumnCount(2)
        self.criteriaTable.setHorizontalHeaderLabels(['Active', 'Criteria'])

        # varexists1 = self.R('exists("'+self.Rvariables['result']+'")') #should trigger an exception if it doesn't exist
       
        # if varexists1:
            # self.normalize(reload = True)
        # else:
            # return
        # except:
            # pass
    def subOnAttached(self):
        tmpitem = self.rsession(self.ssv) #get the items to subset with
        if type(tmpitem) is str: #it's a string!!!!!!!
            items = []
            items.append(tmpitem)
        elif type(tmpitem) is list: #it's a list
            items = tmpitem
        elif type(tmpitem) is dict: #it's a dict
            items = []
            for key in tmpitem.keys():
                items.append(tmpitem['key'])
        #self.infob.setText("Subsetting on "+str(items))
            
        choices = []
        if self.type == 'factor':
            for k in self.factorOutput.keys():
                choices.append(k)
        elif self.type == 'Col Names':
            choices = self.rsession('colnames('+self.Rvariables['data']+')')
        elif self.type == 'Row Names':# row or col name selected
            choices = self.rsession('rownames('+self.Rvariables['data']+')')
                
        #self.infob.setText(str(choices))
        trues = []
        for item in items:
            if item in choices:
                trues.append(item)
            
        if len(trues) == 0:
            self.infoa.setText("No items from your list match your input.")
            return
        else:
            if self.type == 'factor':
                for selected in trues:
                    listItems = self.FactorList.findItems(selected, Qt.MatchExactly)
                    for litems in listItems:
                        self.FactorList.setItemSelected(litems, True)
                self.FactorList.scrollToItem(self.FactorList.selectedItems()[0])
                self.infoa.setText("%i of your items from a list of %i were selected." % (len(self.FactorList.selectedItems()) , len(items) ))
                return
                
            else:
                for selected in trues:
                    listItems = self.namesList.findItems(selected, Qt.MatchExactly)
                    for litems in listItems:
                        self.namesList.setItemSelected(litems, True)
                self.namesList.scrollToItem(self.namesList.selectedItems()[0])
                self.infoa.setText("%i of your items from a list of %i were selected." % (len(self.namesList.selectedItems()) , len(items) ))
        
    def process(self, data):
        self.require_librarys(['fields'])
        
        if data == None:
            self.columnsorrows.clear() #clear the window for the new data
            self.selectCriteria.clear()
            self.olddata = ''
        try:
            #self.columnsorrows.clear()
            self.Rvariables['data'] = data['data']
            self.olddata = data
            #self.changeRowCol()
            # for v in self.rsession('colnames('+self.Rvariables['data']+')'):
                # self.columnsorrows.addItem(v)
            #(rows,cols) = self.R('dim('+self.Rvariables['data']+')')
            rows = self.rsession('length('+self.Rvariables['data']+'[,1])') #one day replace with a more susinct data query
            cols = self.rsession('length('+self.Rvariables['data']+'[1,])')
            self.infoa.setText("Data Connected")
            self.tableinfoa.setText("Data Connected with:")
            self.tableinfob.setText("%s columns and %s rows." % (str(cols), str(rows)))
        except:
            self.infoa.setText("Signal not of appropriate type.")
            self.tableinfoa.setText("No Data Connected")
            self.tableinfob.setText("")
            self.tableinfoc.setText("")
            self.tableinfod.setText("")
            return
    
    
        # section for loading the data to be subset
        self.columnsorrows.clear() #clear the window for the new data
        if self.Rvariables['data'] != '': # this checks if data is still the default
            try: # want to see if there are colnames for selection 
                self.columnsorrows.addItem("Row Names")
                colnames = self.rsession('colnames('+self.Rvariables['data']+')')
                if type(colnames) is str:
                    self.columnsorrows.addItem(colnames)
                else:
                    for item in colnames:
                        self.columnsorrows.addItem(item)
            except:
                self.infoa.setText("Column names do not exist, showing the row numbers")
                self.RowColNamesExist = 0
                for l in xrange(int(self.rsession('length('+self.Rvariables['data']+'[1,])'))):
                    self.columnsorrows.addItem(str(l+1))
        else:
            self.infoa.setText("Data not connected.")
            
    def ssvAttached(self, data):
        if 'data' in data:
            self.subOnAttachedButton.setEnabled(True)
            self.ssv = data['data']
        else:
            return

    def rowcriteriaActiveChange(self, checkbox, selCri):
        if selCri < len(self.rowactiveCriteria)-1 or selCri == len(self.rowactiveCriteria)-1:
            self.infob.setText('Selection Criteria '+str(selCri)+' changed to '+str(checkbox))
            self.rowactiveCriteria[selCri] = checkbox
        else:
            self.rowactiveCriteria.insert(selCri, checkbox)
        self.applySubsetting()
    
    def rowcolNamesSelect(self):
        self.criteriaTable.setRowCount(self.colselectionCriteria+self.rowselectionCriteria+1)
        rowcolHolder = ''
        for item in self.namesList.selectedItems(): # got the items that were selected in the names list for row col selection by names
            rowcolHolder += str(item.text())+'","'
        rowcolHolderP = rowcolHolder[:len(rowcolHolder)-3]

        self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-rownames('+self.Rvariables['data']+') %in% c("'+rowcolHolderP+'")')
        
        self.updaterowCriteriaList(str('Row Names equal to "'+rowcolHolderP+'"')+'. Column Criteria '+str(self.colselectionCriteria))
        self.colselectionCriteria += 1
        
    def updaterowCriteriaList(self, text):
        newitem = QTableWidgetItem(text)
        self.criteriaTable.setItem(self.rowselectionCriteria + self.colselectionCriteria, 1, newitem)
        cw = QCheckBox()
        self.criteriaTable.setCellWidget(self.rowselectionCriteria + self.colselectionCriteria, 0, cw)
        self.connect(cw, SIGNAL("toggled(bool)"), lambda val, selCri=int(self.colselectionCriteria): self.rowcriteriaActiveChange(val, selCri))
        cw.setChecked(True)
        selCri=int(self.colselectionCriteria)
        self.rowcriteriaActiveChange(True, selCri)
        self.criteriaTable.resizeColumnsToContents()
        self.criteriaTable.resizeRowsToContents()
        self.sentalready = 0
    
    def selectCriteria(self, item=None):
        self.criteriaTable.setRowCount(self.colselectionCriteria+self.rowselectionCriteria+1)

        if self.type == 'numeric':
            if self.GorL == 0:
                self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-'+self.Rvariables['tmp']+' > '+self.currentNum)
                self.updaterowCriteriaList(str(self.colnames+' > '+self.currentNum)+'. Column Criteria '+str(self.colselectionCriteria))
            if self.GorL == 1:
                self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-'+self.Rvariables['tmp']+' < '+self.currentNum)
                self.updaterowCriteriaList(str(self.colnames+' < '+self.currentNum)+'. Column Criteria '+str(self.colselectionCriteria))
        if self.type == 'factor':
            if item != None:
                self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-'+self.Rvariables['tmp']+' == "'+str(item.text())+'"')
                self.updaterowCriteriaList(str(self.colnames+' Equal To '+item.text())+'. Column Criteria '+str(self.colselectionCriteria))
            elif item == None and len(self.FactorList.selectedItems()) != 0:
                tmpitems = ''
                for item in self.FactorList.selectedItems():
                    tmpitems += str(item.text())+'","'
                tmpitems2 = tmpitems[:len(tmpitems)-3]
                self.rsession('criteria'+self.vs+'colCri'+str(self.colselectionCriteria)+'<-'+self.Rvariables['tmp']+' %in% c("'+tmpitems2+'")')
                self.updaterowCriteriaList(str(self.colnames+' Equal To "'+tmpitems2+'". Column Criteria '+str(self.colselectionCriteria)))
        self.colselectionCriteria += 1
        #self.applySubsetting()
    
    def applySubsetting(self, reload = False):
        if not reload and not self.sentalready: # make the row subsetting criteria
            rcr = ''
            ccr = ''
            self.rsession('rows'+self.vs+'<-TRUE')
            if sum(self.rowactiveCriteria) == 0: #there aren't any active criteria  
                pass
            else:
                rci = 0
                for rc in self.rowactiveCriteria:
                    if rc: #check to see if active
                        self.Rvariables['criteria'+self.vs+'colCri'+str(rci)] = 'criteria'+self.vs+'colCri'+str(rci)
                        rcr += 'criteria'+self.vs+'colCri'+str(rci)+'&'
                    rci += 1
                rcrr = rcr[:len(rcr)-1]
                self.rsession('rows'+self.vs+'<-'+rcrr)
                #self.numericInfo.setText(str(self.rowactiveCriteria))
            
            self.rsession(self.Rvariables['result']+'<-'+self.Rvariables['data']+'[rows'+self.vs+',]')
            self.newdata = self.olddata.copy()
        self.newdata['data'] = self.Rvariables['result']
        resultclass = self.rsession('class('+self.Rvariables['result']+')')
        if resultclass == 'data.frame':
            self.rSend("R DataFrame" , self.newdata)
            self.tableinfoc.setText("Data Frame sent with:")
            cols = self.rsession('length('+self.Rvariables['result']+'[1,])')
            rows = self.rsession('length('+self.Rvariables['result']+'[,1])')
            self.tableinfod.setText("%s columns and %s rows." % (str(cols), str(rows)))
        elif resultclass == 'numeric' or resultclass == 'factor':
            
            self.rSend("Classified Vector Subset", self.newdata)
        else:
            self.infoa.setText("Send failed because of incompatable type")
            
        self.sentalready = 1