"""
<name>Present calls with panp</name>
<description>Calculates differential expression of genes from an eSet object</description>
<icon>icons/readcel.png</icons>
<priority>2010</priority>
"""
from OWRpy import *
import OWGUI
import RAffyClasses

class panpCalls(OWRpy):
    settingsList = ['Rvariables','panpinfo', 'senddata', 'looseCut', 'tightCut', 'percentA', 'data', 'eset']
    def __init__(self, parent=None, signalManager=None):
        #OWWidget.__init__(self, parent, signalManager, "Sample Data")
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        #self.setStateVariables(['senddata', 'looseCut', 'tightCut', 'percentA', 'data', 'eset'])

        self.senddata = {}
        self.data = {}
        self.eset = ''
        self.panpinfo = '' #used to communicate info after session reload.
        
        self.looseCut = '0.02'
        self.tightCut = '0.01'
        self.percentA = '20'
        
        
        self.setRvariableNames(['PA','PAcalls','PAcalls_sum','Present','peset'])
                
                
        self.loadSettings()

        
        self.setRvariableNames(['PA','PAcalls','PAcalls_sum','Present','peset'])

        
        self.inputs = [("Normalized Affybatch", RAffyClasses.RAffyBatch, self.process)]
        self.outputs = [("Present Gene Signal Matrix", RvarClasses.RDataFrame)]
        
        
        #GUI
        box = OWGUI.widgetBox(self.controlArea, "Options")
        
        OWGUI.lineEdit(box, self, "looseCut", "Loose Cut", orientation = "horizontal")
        OWGUI.lineEdit(box, self, "tightCut", "Tight Cut", orientation = "horizontal")
        OWGUI.lineEdit(box, self, "percentA", "Percent Absent", orientation = "horizontal")
        processbutton = OWGUI.button(box, self, "Process eSet", callback = self.processEset, width=200)
        self.infoa = OWGUI.widgetLabel(box, "Processing not begun")
        
        try:
            varexists = self.R('exists("'+self.Rvariables['peset']+'")')
            if varexists:
                self.senddata['data'] = self.Rvariables['peset']
                self.senddata['kill'] = False
                self.rSend("Present Gene Signal Matrix", self.senddata)
                self.infoa.setText("Data loaded from previous session.")
                
        except:
            pass
        if self.loadingSavedSession:
            self.processEset()

        
    def process(self, dataset):
        self.require_librarys(['affy','gcrma','limma','panp'])
        for output in self.outputs:
            self.rSend(output[0], None, 0)
        if dataset == None: 
            self.infoa.setText("Blank data recieved")
        if dataset:
            try:
                if dataset['kill'] == True:
                    self.rSend("Present Gene Signal Matrix", {'data':'', 'kill':True})
            except:
                pass
            self.data = dataset
            if 'data' in self.data:
                self.eset = self.data['data']
            else:
                self.infoa.setText("Processing imposible, not of eset or affybatch type")
                self.rSend("Present Gene Signal Matrix", {'data':'', 'kill':True})
        else:
            self.rSend("Present Gene Signal Matrix", {'data':'', 'kill':True})
            
    def processEset(self):
        if not self.loadingSavedSession:
            self.infoa.setText("Processing Started!!!")
            self.R(self.Rvariables['PA'] + '<-pa.calls('+self.eset+', looseCutoff='+self.looseCut+', tightCutoff='+self.tightCut+')','setRData', True)
            self.infoa.setText('PA calls have been calculated')
            self.R(self.Rvariables['PAcalls'] + '<-' + self.Rvariables['PA'] + '$Pcalls == "A"','setRData', True)
            self.R(self.Rvariables['PAcalls_sum'] + '<-apply(' + self.Rvariables['PAcalls'] + ', 1, sum)','setRData', True)
            self.R(self.Rvariables['Present'] + '<- ' + self.Rvariables['PAcalls_sum'] + '/length(' + self.Rvariables['PAcalls'] + '[1,]) > '+self.percentA+'/100','setRData', True)
            self.R(self.Rvariables['peset']+'<-as.data.frame(exprs('+self.eset+')[' + self.Rvariables['Present'] + ',])','setRData',True)
            self.panpinfo = 'Processed with loose cut off = '+self.looseCut+', tight cut off ='+self.tightCut+', and percent absent = '+self.percentA
        self.infoa.setText('Processed')
        self.senddata = self.data.copy()
        self.senddata['data'] = self.Rvariables['peset']
        self.senddata['eset'] = self.eset
        self.rSend('Present Gene Signal Matrix', self.senddata)
    

    
        