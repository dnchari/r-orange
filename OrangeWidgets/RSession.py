# R Signal Thread
## Controls the execution of R funcitons into the underlying R session

import sys, os, orngEnviron, numpy
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def Rcommand(query, silent = False, wantType = None, listOfLists = True):
    output = None
    if not silent:
        print query
        
    try:
        output = qApp.R.R(query)            
    except qApp.rpy.RPyRException as inst:
        print inst
        # print showException
        #self.status.setText('Error occured!!')
        # mutex.unlock()
        raise rpy.RPyRException(str(inst))
        
        return None # now processes can catch potential errors
        
    
    if wantType == None:
        pass
    elif wantType == 'list':
        if type(output) in [str, int, float, bool]:
            output =  [output]
        elif type(output) in [list, numpy.ndarray] and len(output) == 1 and not listOfLists:
            output = output[0]
        else:
            pass
    elif wantType == 'dict':
        if type(output) == type(''):
            output =  {'output':[output]}
        elif type(output) == type([]):
            output = {'output': output}
        else:
            pass
    elif wantType == 'array': # want a numpy array
        if type(output) == list:
            output = numpy.array(output)
        elif type(output) in [str, int, float, bool]:
            output = numpy.array([output])
        elif type(output) == dict:
            newOutput = []
            for key in output.keys():
                newOutput.append(output[key])
            output = newOutput
        elif type(output) in [numpy.ndarray]:
            pass
        else:
            print type(output), 'Non normal type, please add to RSession array logic'
    else:
        pass
    #mutex.unlock()
    return output
def getInstalledLibraries():
    libPath = os.path.join(orngEnviron.directoryNames['RDir'],'library').replace('\\','/')
    return Rcommand('as.vector(installed.packages(lib.loc="' + libPath + '")[,1])')
def require_librarys(librarys, repository = 'http://cran.r-project.org'):
        libPath = os.path.join(orngEnviron.directoryNames['RDir'],'library').replace('\\','/')
        installedRPackages = getInstalledLibraries()
        
        Rcommand('local({r <- getOption("repos"); r["CRAN"] <- "' + repository + '"; options(repos=r)})')

        for library in librarys:
            if library in installedRPackages:
                Rcommand('require(' + library + ', lib.loc="' + libPath + '")')
                
            else:
                try:
                    Rcommand('setRepositories(ind=1:7)')
                    Rcommand('install.packages("' + library + '", lib="' + libPath + '")')
                    Rcommand('require(' + library + ', lib.loc="' + libPath + '")')
                    
                except:
                    print 'Library load failed'

