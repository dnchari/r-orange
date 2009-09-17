"""
<name>Update Genomics Databases</name>
<description>Update of systems biology data bases.</description>
<contact>Ales Erjavec</contact>
<priority>5</priority>
<icon>icons/UpdateDatabases.png</icon>
"""

from OWDatabasesUpdate import *

class OWUpdateGenomicsDatabases(OWDatabasesUpdate): 
    def __init__(self, parent=None, signalManager=None, name="Update Genomics Databases", **kwds):
        OWDatabasesUpdate.__init__(self, parent, signalManager, name, domains = ["GO", "KEGG", "MeSH", "Taxonomy", "NCBI_geneinfo", "GEO", "dictybase"], **kwds)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWUpdateGenomicsDatabases()
##    app.setMainWidget(w)
    w.show()
    app.exec_()
    w.saveSettings()
