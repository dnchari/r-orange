"""
<name>Heatmap</name>
<description>Makes heatmaps of data.  This data should be in the form of a data table and should contain only numeric data, no text.  Thought heatmap was designed to work with the Bioconductor package it is able to show any numeric data as a heatmap.  You may use the identify functions to create a collection of subclasses of your data.  This function uses the R identify function and will send two signals; one is the list generated from the selections, the second is a vector of class labels matching the columns of the data.  Clustering is done by columns as this is common in expression data.</description>
<tags>Plotting</tags>
<RFunctions>stats:heatmap</RFunctions>
<icon>heatmap.png</icon>
<priority>2040</priority>
"""

from OWRpy import *
import OWGUI
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RList as rlist
import libraries.base.signalClasses.RModelFit as rmf
import libraries.base.signalClasses.RVector as rvect
class Heatmap(OWRpy):
    #This widget has no settings list
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        
        self.setRvariableNames(['heatsubset', 'hclust', 'heatvect'])
        self.plotOnConnect = 0
        self.plotdata = ''
        self.rowvChoice = None
        
        self.inputs = [("Expression Matrix", rdf.RDataFrame, self.processMatrix), ('Classes Data', rdf.RDataFrame, self.processClasses)]
        self.outputs = [("Cluster Subset List", rlist.RList), ('Cluster Classes', rvect.RVector)]
        

        
        #GUI
        infobox = redRGUI.groupBox(self.controlArea, label = "Options")
        redRGUI.button(self.bottomAreaRight, label = "Replot", callback=self.makePlot, width=200)
        redRGUI.button(infobox, label = 'Save as PDF', callback = self.saveAsPDF)
        redRGUI.button(infobox, label = 'Identify', callback = self.identify, width=200)
        self.startSaturation = redRGUI.spinBox(infobox, label = 'Starting Saturation:', min = 0, max = 100)
        self.endSaturation = redRGUI.spinBox(infobox, label = 'Ending Saturation:', min = 0, max = 100)
        self.endSaturation.setValue(30)
        self.colorTypeCombo = redRGUI.comboBox(infobox, label = 'Color Type:', items = ['rainbow', 'heat.colors', 'terrain.colors', 'topo.colors', 'cm.colors'])
        self.classesDropdown = redRGUI.comboBox(infobox, label = 'Classes:', toolTip = 'If classes data is connected you may select columns in the data to represent classes of your columns in the plotted data')
        self.plotOnConnect = redRGUI.checkBox(infobox, buttons=['Plot on Connect'])
        self.showClasses = redRGUI.checkBox(infobox, buttons = ['Show Classes'])
        self.showClasses.setEnabled(False)
        #OWGUI.checkBox(infobox, self, )
        self.infoa = redRGUI.widgetLabel(infobox, label = "Nothing to report")
        
    def onLoadSavedSession(self):
        print 'load heatmap'
        self.processSignals()
    def saveAsPDF(self):
        self.status.setText('Saving as PDF')
        if self.classes and ('Show Classes' in self.showClasses.getChecked()):
            colClasses = ', ColSideColors=rgb(t(col2rgb(' + self.classes + ' +2)))'
        else:
            colClasses = ''
        colorType = str(self.colorTypeCombo.currentText())
        if colorType == 'rainbow':
            col = 'rainbow(50, start = '+str(self.startSaturation.value()/100)+', end = '+str(self.endSaturation.value()/100)+')'
        else:
            col = colorType+'(50)'
        self.savePDF('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', col= '+col+ colClasses+')')
        #self.stats.setText('File Saved')
    def processMatrix(self, data =None):
        
        if data:
            self.plotdata = data.getData()
            if data.optionalDataExists('classes'):
                self.classes = data.getOptionalData('classes')
                self.showClasses.setEnabled(True)
            else:
                self.classes = 'rep(0, length('+self.plotdata+'[1,]))'
            if self.R('class('+self.plotdata+')') == "data.frame":
                self.plotdata = 'data.matrix('+self.plotdata+')'
            self.rowvChoiceprocess()
            if 'Plot on Connect'  in self.plotOnConnect.getChecked():
                self.makePlot()
        else: 
            self.Rplot('par(mfrow=c(1,1))')
            self.R('dev.off()')
    def processClasses(self, data):
        if data:
            self.classesData = data.getData()
            self.classesDropdown.update(self.R('colnames('+data.data+')', wantType = 'list'))
        else:
            self.classesDropdown.clear()
            self.classesData = ''
    def makePlot(self):
        if self.plotdata == '': return
        self.status.setText("You are plotting "+self.plotdata)
        if str(self.classesDropdown.currentText()) != '':
            self.classes = self.classesData+'$'+str(self.classesDropdown.currentText())
        if self.classes and ('Show Classes' in self.showClasses.getChecked()):
            colClasses = ', ColSideColors=rgb(t(col2rgb(' + self.classes + ' +2)))'
        else:
            colClasses = ''
        colorType = str(self.colorTypeCombo.currentText())
        if colorType == 'rainbow':
            start = float(float(self.startSaturation.value())/100)
            end = float(float(self.endSaturation.value())/100)
            print start, end
            col = 'rev(rainbow(50, start = '+str(start)+', end = '+str(end)+'))'
        else:
            col = colorType+'(50)'
        self.Rplot('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', col= '+col+ colClasses+')', 3, 4)
        # for making the pie plot
        if colorType == 'rainbow':
            start = float(float(self.startSaturation.value())/100)
            end = float(float(self.endSaturation.value())/100)
            print start, end
            col = 'rev(rainbow(10, start = '+str(start)+', end = '+str(end)+'))'
        else:
            col = colorType+'(10)'
        self.Rplot('pie(rep(1, 10), labels = c(\'Low\', 2:9, \'High\'), col = '+col+')', devNumber = 2)
        
    def rowvChoiceprocess(self):
        if self.plotdata:
            rowlen = self.R('length(rownames('+self.plotdata+'))')
            if rowlen > 1000:
                self.rowvChoice = 'NA'
            else:
                self.rowvChoice = 'NULL'
                
    def identify(self, kill = True):
        if self.plotdata == '': return
        
        self.R(self.Rvariables['hclust']+'<-hclust(dist(t('+self.plotdata+')))')
        self.Rplot('plot('+self.Rvariables['hclust']+')', devNumber = 1)
        self.R(self.Rvariables['heatsubset']+'<-lapply(identify('+self.Rvariables['hclust']+'),names)')        
        
        newData = rlist.RList(data = self.Rvariables['heatsubset'], parent = self.Rvariables['heatsubset'])
        self.rSend("Cluster Subset List", newData)
        
        self.R(self.Rvariables['heatvect']+'<-NULL; k<-1')
        self.R('for(i in colnames('+self.plotdata+')){for(j in 1:length('+self.Rvariables['heatsubset']+')){if(i %in%  '+self.Rvariables['heatsubset']+'[[j]]){'+self.Rvariables['heatvect']+'[k]<-j; k <- k+1}}}')
        
        newDataVect = rvect.RVector(data = self.Rvariables['heatvect'])
        self.rSend('Cluster Classes', newDataVect)
        
    def getReportText(self, fileDir):
        ## print the plot to the fileDir and then send a text for an image of the plot
        if self.plotdata != '':
            self.R('png(file="'+fileDir+'/heatmap'+str(self.widgetID)+'.png")')
            if str(self.classesDropdown.currentText()) != '':
                self.classes = self.classesData+'$'+str(self.classesDropdown.currentText())
            if self.classes and ('Show Classes' in self.showClasses.getChecked()):
                colClasses = ', ColSideColors=rgb(t(col2rgb(' + self.classes + ' +2)))'
            else:
                colClasses = ''
            colorType = str(self.colorTypeCombo.currentText())
            if colorType == 'rainbow':
                start = float(float(self.startSaturation.value())/100)
                end = float(float(self.endSaturation.value())/100)
                print start, end
                col = 'rev(rainbow(50, start = '+str(start)+', end = '+str(end)+'))'
            else:
                col = colorType+'(50)'
            self.R('heatmap('+self.plotdata+', Rowv='+self.rowvChoice+', col= '+col+ colClasses+')')
            self.R('dev.off()')
            # for making the pie plot
            self.R('png(file="'+fileDir+'/pie'+str(self.widgetID)+'.png")')
            if colorType == 'rainbow':
                start = float(float(self.startSaturation.value())/100)
                end = float(float(self.endSaturation.value())/100)
                print start, end
                col = 'rev(rainbow(10, start = '+str(start)+', end = '+str(end)+'))'
            else:
                col = colorType+'(10)'
            self.R('pie(rep(1, 10), labels = c(\'Low\', 2:9, \'High\'), col = '+col+')')
            self.R('dev.off()')
            self.R('png(file="'+fileDir+'/identify'+str(self.widgetID)+'.png")')
            self.R('plot(hclust(dist(t('+self.plotdata+'))))')
            self.R('dev.off()')
            text = 'The following plot was generated in the Heatmap Widget:\n\n'
            text += '.. image:: '+fileDir+'/heatmap'+str(self.widgetID)+'.png\n     :scale: 50%%\n\n'
            #text += '<strong>Figure Heatmap:</strong> A heatmap of the incoming data.  Columns are along the X axis and rows along the right</br>'
            text += '.. image:: '+fileDir+'/pie'+str(self.widgetID)+'.png\n     :scale: 30%%\n\n'
            text += '**Intensity Chart:** Intensity levels are shown in this pie chart from low values to high.\n\n'
            text += '.. image:: '+fileDir+'/identify'+str(self.widgetID)+'.png\n   :scale: 50%%\n\n\n'
            text += '**Clustering:** A cluster dendrogram of the column data.\n\n'
        else:
            text = 'Nothing to plot from this widget'
            
        return text
