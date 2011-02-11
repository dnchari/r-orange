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
import os, sys, redREnviron

from PyQt4.QtCore import *
from PyQt4.QtGui import *

_ = redRi18n.Coreget_()
_rObjects = {}

def addRObjects(widgetID, ol):
  global _rObjects
  _rObjects[widgetID] = {'vars':ol, 'state':1, 'timer':QTimer()}
  QObject.connect(_rObjects[widgetID]['timer'], SIGNAL('timeout()'), lambda: saveWidgetObjects(widgetID))
  extendTimer(widgetID)
  for o in ol:
    R('%s<-NULL' % o, wantType = 'NoConversion') #, silent = True)

def removeWidget(widgetID):
  global _rObjects
  del _rObjects[widgetID]

def loadWidgetObjects(widgetID):
  global _rObjects
  R('load(\"%s\")' % os.path.join(redREnviron.directoryNames['tempDir'], widgetID), wantType = 'NoConversion', silent = True)
  _rObjects[widgetID]['state'] = 1
  extendTimer(widgetID)
  
def saveWidgetObjects(widgetID):
  global _rObjects
  _rObjects[widgetID]['timer'].stop()
  redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, _("R objects from widgetID %s were collapsed (saved)") % widgetID)
  R('save(%s, file = \"%s\")' % (','.join(_rObjects[widgetID]['vars']), os.path.join(redREnviron.directoryNames['tempDir'], widgetID)), wantType = 'NoConversion', silent = True)
  _rObjects[widgetID]['state'] = 0
  for v in _rObjects[widgetID]['vars']:
    R('if(exists(\"%s\")){rm(\"%s\")}' % (v, v), wantType = 'NoConversion', silent = True)
  
  
def ensureVars(widgetID):
  redRLog.log(redRLog.REDRCORE, redRLog.DEVEL, _("Ensuring variables for widgetID %s") % widgetID)
  if not _rObjects[widgetID]['state']:
    loadWidgetObjects(widgetID)
  extendTimer(widgetID)
  
def extendTimer(widgetID):
  global _rObjects
  timer = _rObjects[widgetID]['timer']
  timer.stop()
  timer.setInterval(1000*3)
  timer.start()