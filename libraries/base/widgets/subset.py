"""
<name>Subset</name>
<description>Subsets a data.frame object to pass to subsequent widgets.</description>
<tags>Subsetting</tags>
<author>Anup Parikh (anup@red-r.org) and Kyle R Covington (kyle@red-r.org)</author>
<RFunctions>base:rownames,base:colnames,base:summary</RFunctions>
<icon>Subset.png</icon>
"""

from OWRpy import *
import redRGUI

from libraries.base.signalClasses.RDataFrame import RDataFrame as redRRDataFrame
from libraries.base.signalClasses.RList import RList as redRRList
from libraries.base.signalClasses.RVector import RVector as redRRVector

from libraries.base.qtWidgets.listBox import listBox
from libraries.base.qtWidgets.button import button
from libraries.base.qtWidgets.checkBox import checkBox
from libraries.base.qtWidgets.groupBox import groupBox
from libraries.base.qtWidgets.widgetBox import widgetBox
class subset(OWRpy): 

    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self) #initialize the widget
        self.dataClass = None
        self.dataParent = None
        self.setRvariableNames(['subset'])
        
        
        self.inputs.addInput('id0', 'Data Table to Subset On', redRRDataFrame, self.processA)
        self.inputs.addInput('id1', 'Optional List of Subsetting Attributes', redRRList, self.processB)

        
        self.outputs.addOutput('id0', 'Subsetted Data Table', redRRDataFrame)
        self.outputs.addOutput('id1', 'Subsetted Data Vector', redRRVector)

        
                
        #GUI
        box = widgetBox(self.controlArea,orientation = 'horizontal')
        pickA = groupBox(box, "Subset on:")
        self.colA = listBox(pickA, callback = self.setcolA)
        
        
        pickB = groupBox(box, "Subset by:")
        self.colB = listBox(pickB, callback = self.setcolB)
        

        self.mergeLikeThis = checkBox(self.bottomAreaRight, buttons = ['Subset on input'], toolTips = ['Whenever this widget gets data it should try to merge as was done here'])
        button(self.bottomAreaRight, 'Commit', callback = self.subset)

        
    def onSelect(self):
        count = self.attributes.selectionCount()
        self.selectionInfoBox.setText('# ' + self.rowcolBox.getChecked()  + 's selected: ' + str(count))
        
    def processA(self, data):
        #print 'processA'
        if not data:
            self.colA.update([])
            return 
            
        self.dataA = data.getData()
        colsA = self.R('colnames('+self.dataA+')',wantType='list') #collect the sample names to make the differential matrix
        
        colsA.insert(0, 'Rownames')
        self.colA.update(colsA)

        if 'Subset on input' in self.mergeLikeThis.getChecked():
            self.subset()

    def processB(self, data):
        if not data:
            self.colB.update([])
            return 
        self.dataB = data.getData()
        colsB = self.R('names('+self.dataB+')',wantType='list') #collect the sample names to make the differential matrix
        
        
        self.colB.update(colsB)

        if 'Subset on input' in self.mergeLikeThis.getChecked():
            self.subset()

    def setcolA(self):
        try:
            self.colAsel = '\''+str(self.colA.selectedItems()[0].text())+'\''
            if self.colAsel == '\'Rownames\'':
                self.colAsel = '0'
        except: return
    def setcolB(self):
        try:
            self.colBsel = '\''+str(self.colB.selectedItems()[0].text())+'\''
        except: return

    def subset(self):
        if self.dataA != '' and self.dataB != '':
            h = self.R('intersect(colnames('+self.dataA+'), colnames('+self.dataB+'))')
        else: 
            return
        print self.colA.getItems(), self.colAsel
        print self.colB.getItems(), self.colBsel
        
        if self.colAsel == None and self.colBsel == None and type(h) is str: 
            self.R(self.Rvariables['subset']+'<-'+self.dataA+'['+self.dataA+'[,"' + h +'"]'
            +' %in% '+self.dataB+'[["'+h+'"]],]')
        elif self.colAsel in ["'%s'" % x for x in self.colA.getItems()]  and self.colBsel in ["'%s'" % x for x in self.colB.getItems()]: 
            self.R(self.Rvariables['subset']+'<-'+self.dataA+'['+self.dataA+'[,' + self.colAsel +']'
            +' %in% '+self.dataB+'[['+self.colBsel+']],]')
            
        newData = redRRDataFrame(data = self.Rvariables['subset'])
        self.rSend('id0', newData)
        
        if self.R('ncol('+self.Rvariables['subset']+')') == 1:
            newVector = rvec.RVector(data = 'as.vector('+self.Rvariables['subset']+')')
            self.rSend('id1', newVector)


    def subset2(self): # now we need to make the R command that will handle the subsetting.
        if self.data == None or self.data == '': return
        
        selectedDFItems = []
        for name in self.attributes.selectedItems():
            selectedDFItems.append('"'+str(name.text())+'"') # get the text of the selected items
        
        if self.rowcolBox.getChecked() == 'Row':
            self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[rownames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+',])')
            self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[!rownames('+self.data+') %in% c('+','.join(selectedDFItems)+'),])')
        elif self.rowcolBox.getChecked() == 'Column':
            self.R(self.Rvariables['rowcolSelector']+'<-as.data.frame('+self.data+'[,colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')'+'])')
            self.R(self.Rvariables['rowcolSelectorNot']+'<-as.data.frame('+self.data+'[,!colnames('+self.data+')'+' %in% c('+','.join(selectedDFItems)+')])')
            
        if self.R('dim('+self.Rvariables['rowcolSelector']+')')[1] == 1:
            self.R('colnames('+self.Rvariables['rowcolSelector']+')<-c('+','.join(selectedDFItems)+')') # replace the colname if we are left with a 1 column data frame
            newVector = rvec.RVector(data = 'as.vector('+self.Rvariables['rowcolSelector']+')')
            self.rSend('Reduced Vector', newVector)
            
        if self.R('dim('+self.Rvariables['rowcolSelectorNot']+')')[1] == 1:
            self.R('colnames('+self.Rvariables['rowcolSelectorNot']+')<-c(setdiff(colnames('+self.data+'), colnames('+self.Rvariables['rowcolSelector']+')))')
            newVector = rvec.RVector(data = 'as.vector('+self.Rvariables['rowcolSelectorNot']+')')
            self.rSend('Not Reduced Vector', newVector)
            
        
        newData = redRRDataFrame(data = self.Rvariables['rowcolSelector'])
        self.rSend('Data Table', newData)

        newDataNot = redRRDataFrame(data = self.Rvariables['rowcolSelectorNot'])
        self.rSend('id0', newDataNot)
                
        
        # self.R('txt<-capture.output('+self.Rvariables['rowcolSelector']+'[1:5,])')
        # tmp = self.R('paste(txt, collapse ="\n")')
        # self.outputBox.setHtml('A sample of your selection is shown.  Ignore any values with NA.<pre>'+tmp+'</pre>')
            