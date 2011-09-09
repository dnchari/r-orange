################################################################
## Red-R is a visual programming interface for R designed to bring 
## the power of the R statistical environment to a broader audience.
## Copyright (C) 2010  name of Red-R Development
## 
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
################################################################

# R Object Controler
## Controls underlying R objects and their state on disk.  The utility of this module should be transparent to most widget developers.  The goal is to collapse R data for widgets into saved elements on disk, then to reload them when needed.  This will make use of the QTimer function to collapse R variables to disk and to load them when needed.

#imports
from RSession import Rcommand as R
import redRi18n
import redRLog
import os, sys, redREnviron, redRObjects, redRLog
import redRSaveLoad
from PyQt4.QtCore import *
from PyQt4.QtGui import *

_ = redRi18n.Coreget_()
_rObjects = {}

def addRObjects(widgetID, ol):
  global _rObjects
  if widgetID not in _rObjects.keys():
    _rObjects[widgetID] = {'vars':ol, 'state':1, 'timer':QTimer()}
    QObject.connect(_rObjects[widgetID]['timer'], SIGNAL('timeout()'), lambda: saveWidgetObjects(widgetID))
  else:
    _rObjects[widgetID]['vars'] += ol
  extendTimer(widgetID)
  for o in ol:
    R('%s<-NULL' % o, wantType = 'NoConversion') #, silent = True)
  if redRSaveLoad.LOADINGINPROGRESS:
    _rObjects[widgetID]['state'] = 0 # we set this as 0 because the data lives in the saved session.  This means that the data really exists but is located still on disk.  The last thing that we want to do is to distroy it at this point by saving over the data.
    #redRObjects.getWidgetInstanceByID(widgetID).setDataCollapsed(True)
  #redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, 'R Objects are: %s' % _rObjects)
def removeWidget(widgetID):
  global _rObjects
  _rObjects[widgetID]['timer'].stop()
  
  if os.path.exists(os.path.join(redREnviron.directoryNames['tempDir'], widgetID)):
    os.remove(redREnviron.directoryNames['tempDir'], widgetID)
  for v in _rObjects[widgetID]['vars']:
    R('if(exists(\"%s\")){rm(\"%s\")}' % (v, v), wantType = 'NoConversion', silent = True)
  del _rObjects[widgetID]      
def loadWidgetObjects(widgetID):
    global _rObjects
    if _rObjects[widgetID]['state']: return
    redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, _("R objects from widgetID %s were expanded (loaded)") % widgetID)
    if not RSession.mutex.tryLock():  # the session is locked
        while not RSession.mutex.tryLock(): pass
  
    if R('load(\"%s\")' % os.path.join(redREnviron.directoryNames['tempDir'], widgetID).replace('\\', '/'), wantType = 'NoConversion', silent = True) != 'SessionLocked':
        _rObjects[widgetID]['state'] = 1
        redRObjects.getWidgetInstanceByID(widgetID).setDataCollapsed(False)
        extendTimer(widgetID)
        setTotalMemory()
  
def saveWidgetObjects(widgetID):
  global _rObjects
  if _rObjects[widgetID]['state']:
    _rObjects[widgetID]['timer'].stop()
    redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, _("R objects from widgetID %s were collapsed (saved)") % widgetID)
    if not RSession.mutex.tryLock():
        R('save(%s, file = \"%s\")' % (','.join(_rObjects[widgetID]['vars']), os.path.join(redREnviron.directoryNames['tempDir'], widgetID).replace('\\', '/')), wantType = 'NoConversion', silent = True)
        _rObjects[widgetID]['state'] = 0
        redRObjects.getWidgetInstanceByID(widgetID).setDataCollapsed(True)
        for v in _rObjects[widgetID]['vars']:
            R('if(exists(\"%s\")){rm(\"%s\")}' % (v, v), wantType = 'NoConversion', silent = True)
        setTotalMemory()
    else:  # the session is locked so the data wasn't really saved.  We add time to the timer and try next time.
        extendTimer(widgetID)
  
def ensureVars(widgetID):
  #redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, _("Ensuring variables for widgetID %s") % widgetID)
  if not _rObjects[widgetID]['state']:
    loadWidgetObjects(widgetID)
  extendTimer(widgetID)
  
def extendTimer(widgetID):
  global _rObjects
  timer = _rObjects[widgetID]['timer']
  timer.stop()
  timer.setInterval(1000*60*5)
  timer.start()
  
def setWidgetPersistent(widgetID):
  timer = _rObjects[widgetID]['timer']
  timer.stop()
  ensureVars(widgetID)
  timer.stop()
  
  
### memory consumption
TOTALMEMORYUSED = 0

if sys.platform == 'win32':
    MEMORYLIMIT = R('memory.limit()*1024*1024', silent = True)
else:
    MEMORYLIMIT = float(3*1024*1024*1024)
#MEMORYLIMIT = R('memory.limit()*1024*1024', silent = True)
#print "MEMORYLIMIT ", MEMORYLIMIT, type(MEMORYLIMIT)

def memoryConsumed(id):
    global _rObjects
    myMemory = 0
    if _rObjects[id]['state']:
        for v in _rObjects[id]['vars']:
            myMemory += int(R('as.numeric(object.size(%s))' % v, silent = True))
    return myMemory
    
def setTotalMemory():
    global TOTALMEMORYUSED
    if len(R('ls()', silent = True)) > 0:
        TOTALMEMORYUSED = R('sum(as.vector(sapply(unlist(ls()),object.size)))', silent = True)
    else:
        TOTALMEMORYUSED = 0
    