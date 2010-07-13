"""
<name>Correlation/Variance</name>
<author>Anup Parikh anup@red-r.org</author>
<RFunctions>stats:cor, stats:var, stats:cov</RFunctions>
<tags>Stats</tags>
<icon>correlation.png</icon>
<inputWidgets>base_readFile</inputWidgets>
<outputWidgets>base_RDataTable</outputWidgets>
"""
#OWRpy is the parent of all widgets. 
#Contains all the functionality for connecting the widget to the underlying R session.
from OWRpy import *

# redRGUI contains all the QT gui elements. 
# These elements all have special functions for saving and loading state. 
import redRGUI

# signalClasses classes contain the data that is passed between widgets. 
# In this case we are using the RDataFrame and RMatrix signals
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RMatrix as rmat


# our first widget. Must be a child of OWRpy class
# The wiget class name must be the same as the file name
import libraries.base.signalClasses.RVariable as rvar

class cor(OWRpy):
    
    # a list of all the variables that need to be saved in the widget state file.
    # these varibles values will be shared between widgets
    globalSettingsList = ['sendOnSelect']

    # Python init statement is the class constructor 
    # Here you put all the code that will run as soon as the widget is put on the canvas
    def __init__(self, parent=None, signalManager=None):
        #Here we init the parent class of our widget OWRpy.
        OWRpy.__init__(self)
        
        #create a R variable cor in the R session.
        #the cor variable will not conflict with some other widgets cor function
        self.setRvariableNames(["cor"])
        
        # declare some variables we will use later
        self.RFunctionParam_y = None
        self.RFunctionParam_x = None
        
        # Define the inputs that this widget will accept
        # When data is received the three element in the tuple which is a function will be executed
        self.inputs = [("x", rdf.RDataFrame, self.processx),("y", rdf.RDataFrame, self.processy)]
        # Define the outputs of this widget
        self.outputs = [("cor Output", rmat.RMatrix)]
        
        #START THE GUI LAYOUT
        area = redRGUI.widgetBox(self.controlArea,orientation='horizontal')       
        
        options = redRGUI.widgetBox(area,orientation='vertical')
        area.layout().setAlignment(options,Qt.AlignTop)
        self.type = redRGUI.radioButtons(options,  label = "Perform", 
        buttons = ['Variance', 'Correlation', 'Covariance'],setChecked='Correlation',
        orientation='vertical',callback=self.changeType)
        
        self.methodButtons = redRGUI.radioButtons(options,  label = "Method", 
        buttons = ['pearson', 'kendall', 'spearman'],setChecked='pearson',
        orientation='vertical')

        self.useButtons =  redRGUI.radioButtons(options, label='Handing Missing Values', setChecked='everything',
        buttons = ["everything","all.obs", "complete.obs", "pairwise.complete.obs"],
        orientation='vertical')

        redRGUI.button(options, "Commit", toolTip='Calculate values', callback = self.commitFunction)
        self.sendOnSelect = redRGUI.checkBox(options,buttons=['Calculate on data Input'], 
        toolTips=['Calculate variance on data input.'])

        self.RoutputWindow = redRGUI.Rtable(area,sortable=True)
    
    # execute this function when data in the X channel is received
    # The function will be passed the data
    def processx(self, signal):
        if signal:
            #if the signal exists get the data from it
            self.RFunctionParam_x=signal.getData()
            # if the checkbox is checked, immediately process the data
            if 'Calculate on data Input' in self.sendOnSelect.getChecked():
                self.commitFunction()
                
    # execute this function when data in the Y channel is received
    # does the same things as processX
    def processy(self, signal):
        if signal:
            self.RFunctionParam_y=signal.getData()
            if 'Calculate on data Input' in self.sendOnSelect.getChecked():
                self.commitFunction()
            
    # this function actually does the work in R 
    # its call by clicking the Commit button
    # or when data is received, if the checkbox is checked.
    def commitFunction(self):
        # The X data is required, if not received, do nothing
        if not self.RFunctionParam_x: 
            self.status.setText('X data is missing')
            return

        
        # START COLLECTION THE R PARAMETERS THAT WILL CREATE THE R CODE TO EXECUTE
        injection = []
        
        if self.type.getChecked() == 'Correlation':
            test = 'cor'
        elif self.type.getChecked() == 'Variance':
            test = 'var'
        elif self.type.getChecked() == 'Covariance':
            test = 'cov'
            
        if self.useButtons.getChecked():
            string = 'use=\''+str(self.useButtons.getChecked())+'\''
            injection.append(string)
        elif self.type.getChecked() == 'Variance':
            string = 'na.rm=TRUE'
            injection.append(string)
        
        if self.methodButtons.getChecked():
            string = 'method=\''+str(self.methodButtons.getChecked())+'\''
            injection.append(string)
            
        if self.RFunctionParam_y:
            injection.append('y='+str(self.RFunctionParam_y))

        # combine all the parameters in the a string    
        inj = ','.join(injection)
        
        # make the R call. The results will be saved in the 'cor' variable we declared earlier
        self.R(self.Rvariables['cor']+'<-'+test+'(x='+str(self.RFunctionParam_x)+','+inj+')')
        
        # visualize the data in a table
        self.RoutputWindow.clear()
        self.RoutputWindow.setRTable(self.Rvariables['cor'])
        
        # create a new signal of type RMatrix and load the results 
        newData = rmat.RMatrix(data = self.Rvariables["cor"]) 
        # send the signal forward
        self.rSend("cor Output", newData)
  
    
    # Based on the user selections some parameters is not valid. This is all documented in the R help for cor/var/cov
    # Here we are instructing the GUI to disable those parameters that are invalid. 
    def changeType(self):
        if self.type.getChecked() =='Variance':
            self.useButtons.setDisabled(True)
            self.methodButtons.setDisabled(True)
        else:    
            self.useButtons.setEnabled(True)
            self.methodButtons.setEnabled(True)

        if self.type.getChecked() =='Covariance':
            self.useButtons.disable(['pairwise.complete.obs'])
        elif self.type.getChecked() =='Correlation':
            self.useButtons.enable(['pairwise.complete.obs'])
        