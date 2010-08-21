"""
<name>ANOVA</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>stats:aov</RFunctions>
<tags>Parametric</tags>
<icon>stats.png</icon>
"""
from OWRpy import * 
import redRGUI 
import libraries.base.signalClasses.RDataFrame as rdf
import libraries.base.signalClasses.RModelFit as rmf
class aov(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self)
        self.setRvariableNames(["aov"])
        self.data = {}
        self.RFunctionParam_data = ''
        self.saveSettingsList.extend(['data', 'RFunctionParam_data'])
        self.inputs = [("data", rdf.RDataFrame, self.processdata)]
        self.outputs = [("aov Output", rmf.RModelFit)]
        
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParamcontrasts_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "contrasts:", text = 'NULL')
        self.RFunctionParamformula_formulaEntry =  redRGUI.RFormulaEntry(self.standardTab)
        self.RFunctionParamqr_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "qr:", text = 'TRUE')
        self.RFunctionParamprojections_lineEdit =  redRGUI.lineEdit(self.standardTab,  label = "projections:", text = 'FALSE')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
        self.RoutputWindow = redRGUI.textEdit(self.controlArea, label = "RoutputWindow")
    def processdata(self, data):
        if not self.require_librarys(["stats"]):
            self.status.setText('R Libraries Not Loaded.')
            return
        if data:
            self.removeWarning()
            self.RFunctionParam_data=data.getData()
            #self.data = data.copy()
            self.RFunctionParamformula_formulaEntry.update(self.R('names('+self.RFunctionParam_data+')'))
            self.commitFunction()
        else:
            self.RFunctionParam_data=''
            self.RFunctionParamformula_formulaEntry.clear()
    def commitFunction(self):
        if str(self.RFunctionParam_data) == '': 
            self.setWarning(id = 'NoData', text = 'No Data connected or data is blank')
            return
        formula = self.RFunctionParamformula_formulaEntry.Formula()
        if formula[0] == '' or formula[1] == '': 
            self.setWarning(id = 'BadFormula', text = 'Formula not entered correctly')
        injection = []
        string = 'formula='+formula[0]+ ' ~ '+formula[1]
        injection.append(string)
        if str(self.RFunctionParamcontrasts_lineEdit.text()) != '':
            string = 'contrasts='+str(self.RFunctionParamcontrasts_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamqr_lineEdit.text()) != '':
            string = 'qr='+str(self.RFunctionParamqr_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamprojections_lineEdit.text()) != '':
            string = 'projections='+str(self.RFunctionParamprojections_lineEdit.text())+''
            injection.append(string)
        inj = ','.join(injection)
        self.R(self.Rvariables['aov']+'<-aov(data='+str(self.RFunctionParam_data)+','+inj+')')
        self.R('txt<-capture.output(summary('+self.Rvariables['aov']+'))')
        self.RoutputWindow.clear()
        tmp = self.R('paste(txt, collapse ="\n")')
        self.RoutputWindow.insertHtml('<br><pre>'+tmp+'</pre>')
        newData = rmf.RModelFit(data = self.Rvariables["aov"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.copyAllOptinoalData(self.data)  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("aov Output", newData)
    def getReportText(self, fileD):
        text = 'Performed ANOVA analysis on the attached data.  The following parameters were used:\n\n'
        formula = self.RFunctionParamformula_formulaEntry.Formula()
        if formula[0] == '' or formula[1] == '': 
            self.setWarning(id = 'BadFormula', text = 'Formula not entered correctly')
        injection = []
        string = 'formula='+formula[0]+ ' ~ '+formula[1]
        injection.append(string)
        if str(self.RFunctionParamcontrasts_lineEdit.text()) != '':
            string = 'contrasts='+str(self.RFunctionParamcontrasts_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamqr_lineEdit.text()) != '':
            string = 'qr='+str(self.RFunctionParamqr_lineEdit.text())+''
            injection.append(string)
        if str(self.RFunctionParamprojections_lineEdit.text()) != '':
            string = 'projections='+str(self.RFunctionParamprojections_lineEdit.text())+''
            injection.append(string)
        inj = '\n\n'.join(injection)
        text += inj
        text += '\n\nThe following is a summary of the output:\n\n'
        text += str(self.RoutputWindow.toPlainText())+'\n\n'
        return text
