"""
<name>performance</name>
<author>Generated using Widget Maker written by Kyle R. Covington</author>
<RFunctions>ROCR:performance</RFunctions>
<tags>ROC Curves</tags>
<icon>icons/RExecutor.png</icon>
"""
from OWRpy import * 
import redRGUI 
class performance(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.setRvariableNames(["performance"])
        self.data = {}
        self.loadSettings() 
        self.RFunctionParam_prediction_obj = ''
        self.inputs = [("prediction_obj", signals.ROCCurves.RROCPredictionFit, self.processprediction_obj)]
        self.outputs = [("performance Output", signals.ROCCurves.RROCPerformanceFit)]
        optionItems = ['acc, Accuracy', 'err, Error', 'fpr, Flase Positive Rate', 'fall, Fallout', 'tpr, True Positive Rate', 'rec, Recall', 'sens, Sensitivity', 'fnr, False Negative Rate', 'miss, Miss', 'tnr, True Negative Rate', 'spec, Specificity', 'ppv, Positive Predictive Value', 'prec, Precision', 'npv, Negative Predictive Value', 'pcfall, Prediction Conditioned Fallout', 'pcmiss, Prediction Conditioned Miss', 'rpp, Rate of Positive Prediction', 'rnp, Rate of Negative Prediction', 'phi, Phi Correction Coefficient', 'mat, Matthews Correlation Coefficient', 'mi, Mutual Information', 'chisq, Chi Squared Test Statistic', 'odds, Odds Ratio', 'lift, Lift Value', 'f, Precision-recall F Measure ', 'rch, ROC Convex Hull', 'auc, Area Under the ROC Curve', 'prbe, Percision-Recall Break-Even Point', 'cal, Calibration Error' 'mxe, Mean Cross Entropy', 'rmse, Root Mean Squared Error', 'sar, Score Conditioned Performance Measures', 'ecost, Expected Cost', 'cost, Cost of a Classifier']
        self.help.setHtml('<small>Default Help HTML, one should update this as soon as possible.  For more infromation on widget functions and RedR please see either the <a href="http://www.code.google.com/p/r-orange">google code repository</a> or the <a href="http://www.red-r.org">RedR website</a>.</small>')
        box = redRGUI.tabWidget(self.controlArea)
        self.standardTab = box.createTabPage(name = "Standard")
        self.advancedTab = box.createTabPage(name = "Advanced")
        self.RFunctionParammeasure_comboBox =  redRGUI.comboBox(self.standardTab,  label = "Measure:", items = optionItems)
        self.RFunctionParamx_measure_comboBox =  redRGUI.comboBox(self.standardTab,  label = "x_measure:", items = [',None'] + optionItems)
        
        self.costFP = redRGUI.lineEdit(self.advancedTab, label = 'False Positive Cost:', toolTip = 'cost.fp and cost.fn, by which the costs for false positives and negatives can be adjusted, respectively. By default, both are set to 1.')
        self.costFN = redRGUI.lineEdit(self.advancedTab, label = 'False Negative Cost:', toolTip = 'cost.fp and cost.fn, by which the costs for false positives and negatives can be adjusted, respectively. By default, both are set to 1.')
        self.windowSize = redRGUI.lineEdit(self.advancedTab, label = 'Window Size:', toolTip = 'The default window size of 100 can be adjusted by passing the optional parameter\n window.size=200 to performance. E.g., if for several positive samples the output of the classifier is\n around 0.75, you might expect from a well-calibrated classifier that the fraction of them which \nis correctly predicted as positive is also around 0.75. In a well-calibrated classifier, the \nprobabilistic confidence estimates are realistic. Only for use with probabilistic output (i.e. \nscores between 0 and 1).')
        self.Fpr_stop = redRGUI.lineEdit(self.advancedTab, label = 'False Positive Rate Stop:', toolTip = 'The partial area under the ROC curve up to a given false positive rate can be calculated by\n passing the optional parameter fpr.stop=0.5 (or any other value between 0 and 1) to performance.')
        redRGUI.button(self.bottomAreaRight, "Commit", callback = self.commitFunction)
    def processprediction_obj(self, data):
        self.require_librarys(["ROCR"]) 
        if data:
            self.RFunctionParam_prediction_obj=data.data
            #self.data = data.copy()
            self.commitFunction()
        else:
            self.RFunctionParam_prediction_obj=''
    def commitFunction(self):
        if str(self.RFunctionParam_prediction_obj) == '': return
        injection = []
        mes = str(str(self.RFunctionParammeasure_comboBox.currentText()).split(',')[0])
        xmes = str(str(self.RFunctionParamx_measure_comboBox.currentText()).split(',')[0])
        print mes, xmes
        string = 'measure=\''+mes+'\''
        injection.append(string)
        if mes not in ['ecost']:
            if xmes not in ['', ' ']:
                string = 'x.measure=\''+xmes+'\''
                injection.append(string)
            if mes in ['cost'] or xmes in ['cost']:
                if str(self.costFN.text()) != '':
                    string = 'cost.fn='+str(self.costFN.text())
                    injection.append(string)
                if str(self.costFP.text()) != '':
                    string = 'cost.fp='+str(self.costFP.text())
                    injection.append(string)
            if mes in ['auc'] or xmes in ['auc']:
                if str(self.Fpr_stop.text()) != '':
                    string = 'fpr.stop='+str(self.Fpr_stop.text())
                    injection.append(string)
            if mes in ['cal'] or xmes in ['cal']:
                if str(self.windowSize.text()) != '':
                    string = 'window.size='+str(self.windowSize.text())
                    injection.append(string)
                    
        inj = ','.join(injection)
        self.R(self.Rvariables['performance']+'<-performance(prediction.obj='+str(self.RFunctionParam_prediction_obj)+','+inj+')')
        newData = signals.ROCCurves.RROCPerformanceFit(data = self.Rvariables["performance"]) # moment of variable creation, no preexisting data set.  To pass forward the data that was received in the input uncomment the next line.
        #newData.dictAttrs = self.data.dictAttrs.copy()  ## note, if you plan to uncomment this please uncomment the call to set self.data in the process statemtn of the data whose attributes you plan to send forward.
        self.rSend("performance Output", newData)