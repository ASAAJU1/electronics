"""This script provides a GUI window display for theManyMeter in Portal
   
   The code is split into two sections:
   1) code directly called from the remote node.
   2) the actual wxPython graphics work 
"""

import wx
import wx.grid
from wxPython.wx import *
    
frame = None
ID_ABOUT = 101
ID_EXIT  = 102

def DisplayData(newReading, meterType, nodeName):
    """Called by nodes running 'ManyMeter' scripts to display the current reading"""
    global frame
    if not frame:
        frame = MeterFrame(root)

    frame.displayMeterReading(newReading, meterType, nodeName)
    


"""The following uses the wxPython library to create custom graphics"""    
    
class MeterFrame(wx.Frame):
    """Main window frame"""
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(200,100))
        self.Bind(wx.EVT_CLOSE, self.onClose)
        #self.panel = MeterPanel(self)
        self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        
        ## Status Bar, Furture use of comms check #########################################
        self.CreateStatusBar()
        self.SetStatusText("This is the statusbar")
        ## End Status Bar #################################################################
        
        ## Menu, For later control in a snap connect app ##################################
        menu = wxMenu()
        menu.Append(ID_ABOUT, "&About", "More information about this program")
        menu.AppendSeparator()
        menu.Append(ID_EXIT, "E&xit", "Terminate the program")

        menuBar = wxMenuBar()
        menuBar.Append(menu, "&File");
        ## End of Menu Bar Setup ##########################################################
        self.MeterFrame = parent
        box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(box)
        
        self.text = wx.StaticText(self, -1, "0", (30, 40))
        font = wx.Font(48, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial")
        self.text.SetFont(font)
        box.Add(self.text, 1, wx.ALIGN_CENTER)
        
        self.text2 = wx.StaticText(self, -1, "No readings yet", (10, 110))
        font2 = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, False, "Arial")
        self.text2.SetFont(font2)
        box.Add(self.text2, 1, wx.ALIGN_CENTER)
        
        
        self.gauge1 = wx.Gauge(self, -1, 100, (10, 75), (360, 25))
        self.gauge1.SetValue(0)
        
        
        self.SetMenuBar(menuBar)
        self.Show(True)

    def onClose(self, event):
        self.Destroy()

    def displayMeterReading(self, newReading, meterType, nodeName):
        # Display the new reading in the first text widget
        self.text.SetLabel('%d' % newReading)
        # Display type of meter and where the info came from in the second text widget
        if meterType == None:
            meterType = "Unknown" 
        if nodeName == None:
            nodeName = "Unknown"
        newStr = "Meter Type: " + meterType + "\r\nFrom Node: " + nodeName
        self.text2.SetLabel(newStr)
        # update the gauge
        #self.gauge1.SetValue(newReading)
        self.Refresh()
 
        

class MyApp(wxApp):
    def OnInit(self):
        frame = MeterFrame(root, JC, "Hello from wxPython")
        frame.Show(true)
        self.SetTopWindow(frame)
        return true
    
#if __name__ == '__main__':
#    """This code is needed to run as a stand alone program""" 
#    class MyApp(wx.App):
#        def OnInit(self):
#            self.frame = MeterFrame(None)
#            self.SetTopWindow(self.frame)
#            return True
#    app = MyApp(0)
#    app.MainLoop()
# Run the program
#if __name__ == '__main__':
#app = MyApp(0)
#frame = MeterFrame().Show()
#app.MainLoop()
