"""
<name>Dummy</name>
<discription>A dummy widget to act as a placeholder if widget load fails</discription>
<author>Kyle R. Covington</author>
<tags>R</tags>
<icon>icons/dummy.png</icon>
<priority>4010</priority>
"""
from OWRpy import * 
import OWGUI 
class dummy(OWRpy): 
    settingsList = []
    def __init__(self, parent=None, signalManager=None, forceInSignals = None, forceOutSignals = None):
        OWRpy.__init__(self, parent, signalManager, "File", wantMainArea = 0, resizingEnabled = 1)
        self.inputs = []
        self.outputs = []
        print str(forceInSignals) +' and ' + str(forceOutSignals) + ' appending to dummy'
        if forceInSignals: 
            import signals
            for (a, b) in [signal for signal in forceInSignals]:
                print 'Appending ' + str(a) + ' in dummy to the '+b+' signal'
                if b == 'Data Frame': bc = signals.RDataFrame
                elif b == 'List': bc = signals.RList
                elif b == 'Vector': bc = signals.RVector
                else: bc = signals.RVariable
                self.inputs.append((a, bc, None))
        if forceOutSignals:
            import signals
            for (a, b) in [signal for signal in  forceOutSignals]:
                print 'Appending ' +str(a)+' in dummy using the '+b+' signal'
                if b == 'Data Frame': bc = signals.RDataFrame
                elif b == 'List': bc = signals.RList
                elif b == 'Vector': bc = signals.RVector
                else: bc = signals.RVariable
                self.outputs.append((a, bc))
        print self.inputs
        print self.outputs
            
        self.loadSettings()
        
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, "A widget failed to load this was put in it's place.")
        self.infob = OWGUI.widgetLabel(box, "The variables that were saved with this widget are %s .\n You can use R Executor to retrieve these variables and incorporate them into your schema." % str(self.sentItems))
        
    