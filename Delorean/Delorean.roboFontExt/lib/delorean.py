#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Delorean: Interpolation Preview by CJ Dunn. 
#Thanks to Frederik Berlaen and David Jonathan Ross. 

import vanilla
from mojo.glyphPreview import GlyphPreview
from vanilla import Box
from lib.UI.stepper import SliderEditIntStepper
from defconAppKit.windows.baseWindow import BaseWindowController
from mojo.events import addObserver, removeObserver
import sys

from mojo.events import addObserver, removeObserver, postEvent

import time


#supports Control Board by Andy Clymer
#you can use a potentiometer, must be named "Delorean Knob" in Control Board for interpolation slider, a button "Delorean Button" in Control Board for generating instance, and RGB LED is called "RGBLED"





class Dialog(BaseWindowController):
    
    def activateModule(self):
        #init for glyphChangeObserver
        addObserver(self, "glyphChangeObserver", "currentGlyphChanged")
        addObserver(self, "glyphOutlineChangeObserver", "draw")
        addObserver(self, "checkReport", "updateReport")
        addObserver(self, "generate", "generateCallback")
        
        addObserver(self, 'inputChanged', 'ControlBoardInput')

  
    
    def deactivateModule(self):
        removeObserver(self, "currentGlyphChanged")
        removeObserver(self, "draw") 
        removeObserver(self,  "updateReport")
        removeObserver(self, "checkReport")
        removeObserver(self, "generateCallback")
        removeObserver(self,  "interpSetGlyph")
        
        removeObserver(self, 'RoboControlInput')
        
        self.allOff()

    

    def __init__(self, value, font1, font2):
        self.activateModule()
        
        #sets initial value
        #self.redBlink = False
        global redIsOn
        redIsOn = False
       
        
        x = 10
        y = 10
        yInit = y
        lineHeight = 23
        
       
        self.value = value
        self.font1 = font1 
        self.font2 = font2
        
        self.offset = ''
        
        #gname1
        if CurrentGlyph() != None:
            g = CurrentGlyph()

        else:
            g = gInit
                   
        self.gname = g

        #use minSize to make window re-sizable        
        self.w = vanilla.Window((400,400), 'Delorean: Interpolation Preview', minSize=(200,200))
        
        self.w.oneTextBox = vanilla.TextBox((x, y, 200, lineHeight), '[1] '+str(font1.info.familyName) or 'Family' + ' ' + str(font1.info.styleName) or 'Style')
        self.w.twoTextBox = vanilla.TextBox((x+200, y, 200, lineHeight), '[2] '+str(font2.info.familyName) or 'Family' + ' ' + str(font2.info.styleName) or 'Style')
             
        #Line Return
        y += lineHeight
        
        #vanilla.TextBox (not interactive field)
        self.w.gnameTextBox = vanilla.TextBox((x, y, 200, lineHeight), 'Glyph name')
        self.w.valueTextBox = vanilla.TextBox((x+105, y, 200, lineHeight), 'Interpolation %')
        
        #Line Return
        y += lineHeight
        
        
        # "Glyph name"
        self.w.gnameTextInput = vanilla.EditText((x, y, 80, lineHeight), self.gname.name , callback=self.setterButtonCallback)        
        
        # "Percentage" Slider
        #Value
        self.w.valueTextInput = SliderEditIntStepper((x+105, y, -10, 22), minValue=-200, maxValue=400, value=50, increment=10, callback=self.setterButtonCallback)
        

        
        
        
        
        
        y += lineHeight
        y += 15
        
        
        #-5 from bottom
        self.w.preview = GlyphPreview((0, y, -0, -5) )
        
        #Report
        self.w.reportText = vanilla.TextBox((x, -27, 400, lineHeight), '')
        
        #generate instance
        self.w.generate = vanilla.Button( (-35, -27, 27, lineHeight), u"⬇" , callback=self.generateCallback )        
        
                

        if CurrentGlyph() != None:
            g = CurrentGlyph()
        else:
            g = gInit 

        gname = g.name

        self.interpSetGlyph(gname)


        self.w.box = Box((0, (y-9), -0, -30))

        self.setUpBaseWindowBehavior()    
        self.w.open()
 
    # def getFontName(self,f):
    #     if f.info.familyName:
    #         family = f.info.familyName
    #     else:
    #         family = 'Family'
    #     if f.info.styleName:
    #         style = f.info.styleName
    #     else:
    #         style = 'Style'
                
    #     fontName = family+' '+style
        
    

    def interpSetGlyph(self, gname):
        
        
        
        if gname in font1 and gname in font2:
                    
            i = self.interp(self.value, gname)        
                        
            #scales upm to 1000
            upm = font1.info.unitsPerEm
            self.offset = (font2[gname].width) / 2
                
            i.scale(( (1000/float(upm)),(1000/float(upm)))  ,  center=(self.offset, 0)   )

            self.w.preview.setGlyph(i)
            
            #Status: good
            reportText = u"😎"
            self.w.reportText.set(reportText)
            
            #self.redBlinkOff()
            #or do I need to do it a different way? 
            self.redOff()
            
        else:
            
            #Status: no good
            reportText = u"😡"
            self.w.reportText.set(reportText)
            
            #blinks red if there's a problem            
            #self.redBlink()
            self.redOn()
            #print 'blink red'
            
            #Glyphname must exist in both fonts
             
            pass


    def glyphChangeObserver(self, info):
        
        #gname3
        if CurrentGlyph() != None:
            g = CurrentGlyph()
            

        else:
            g = gInit
                   
        gname = g.name         
        

        
        #when glyph changes, check if it's interpolable
        self.updateReport(gname)
        

        
        self.interpSetGlyph(gname)        
        #sets gname in box when glyph changes
        self.w.gnameTextInput.set(gname)
                        
    def glyphOutlineChangeObserver(self, info):
        
        #gname4
        if CurrentGlyph() != None:
            g = CurrentGlyph()

        else:
            g = gInit 
                  
        gname = g.name 

        self.interpSetGlyph(gname)        
        #print 'glyphOutlineChangeObserver'
        #3
        
        #set gname in box when outline changes
        self.w.gnameTextInput.set(gname)
        
        self.updateReport(gname)


    def checkReport(self, gname):
        reportText = ''
        
        if gname in font1 and gname in font2:
            glyph1 = self.font1[gname]
            glyph2 = self.font2[gname]
        
            report = glyph1.isCompatible(glyph2)

            if report[0] == False:
                #no good
                reportText = u"😡 *** /" + gname + " is not compatible for interpolation ***" 
                
                #blinks red if there's a problem            
                #self.redBlink()
                self.redOn()
                
            else:
                #Status: good
                reportText = u"😎"
        else:
            pass
        
        return reportText
            
    def generateCallback(self, sender):
        #print 'Generate1'
        #i = self.interp(self.value, self.gname)
        
        gname = self.w.gnameTextInput.get()
        
        #generates to new one
        #self.font1
        f = CurrentFont()
        
        pcnt = int((self.value)*100)
        
        instanceName = gname+'.'+str(pcnt)
        
        if gname in font1 and gname in font2:
            i =  self.interp(self.value, gname)
        
            f.insertGlyph(i, instanceName)
        
            print '\nGlyph "'+instanceName+'" added to CurrentFont()'
            f.update()
        
        #print self.value, gname
    
        
        
    def updateReport(self, gname):

        reportText = ''

        reportText = self.checkReport(gname)
    
  
        self.w.reportText.set(reportText)
        
        
    def setterButtonCallback(self, sender):
        
        self.w.valueTextInput.get()        
        
        
        #convert to float
        self.value = float(self.w.valueTextInput.get()) / 100
        
        #self.updateReport(gname)
        gname = self.w.gnameTextInput.get()
        
        self.interpSetGlyph(gname)
        
        pcnt = int(self.w.valueTextInput.get())
        
        if pcnt > 100:
            #print '+'
            self.allOff()
            self.redOn()
            

                    
        if pcnt < 0:
            #print '-'
            self.allOff()
            self.blueOn()
            
        if pcnt > 0 and pcnt < 100:
            self.allOff()
            pass
            
        
        
            
    def interp(self, value, gname):
        font1 = self.font1
        font2 = self.font2
        
        if len(font1[gname].components) > 0 or len(font2[gname].components) > 0:
            g1 = font1[gname]
            glyph1 = g1.copy()
            glyph1.naked().setParent(font1)
            glyph1.decompose()
            
            
            g2 = font2[gname]
            glyph2 = g2.copy()
            glyph2.naked().setParent(font2)            
            glyph2.decompose()
            
            
            #gname, 'has components'      

        else: 
            glyph1 = font1[gname]
            glyph2 = font2[gname]      


        dest = RGlyph()
        dest.interpolate(value, glyph1, glyph2)
        
        return dest
        
        
    def inputChanged(self, info):
        #print 'inputChanged'
        #self.w.value.set(str(info))
        
        if info['name'] == 'Delorean Knob':
            
            scaledValue = (info['value'] * 600) - 200
            self.w.valueTextInput.set(scaledValue)
            self.setterButtonCallback(None)
            
        if info['name'] == 'Delorean Encoder':
            #currentValue = self.w.valueTextInput.get()
            
            if info['state'] == 'cw':
                #newValue = currentValue +10
                
                #go to next glyph in sort order
                pass
                
                
            if info['state'] == 'ccw':
                #newValue = currentValue -10
                
                #go to previous glyph in sort order
                pass
                                
            #self.w.valueTextInput.set(newValue)
            #self.setterButtonCallback(None)

        if info['name'] == 'Delorean Button':

            if info['state'] == 'down':
                self.greenOn()
            
            if info['state'] == 'up':
                self.greenOff()
                #when clicked
                #save interpolation to CurrentFont()
                self.generateCallback(None)



            
#do I still need this? 
    def windowCloseCallback(self, sender):
        self.deactivateModule()
        BaseWindowController.windowCloseCallback(self, sender)   


    #LED Support via RoboControl
    
    def redOn(self):
        global redIsOn
        redIsOn = True
        postEvent('RoboControlOutput', name='RGBLED', state='on', value='red')
        postEvent('RoboControlOutput', name='RedLED', state='on', value='.5')
        
    def redOff(self):
        global redIsOn
        if redIsOn == True:
            postEvent('RoboControlOutput', name='RGBLED', state='off')
            redIsOn = False

    def greenOn(self):
        postEvent('RoboControlOutput', name='RGBLED', state='on', value='green')
        postEvent('RoboControlOutput', name='GreenLED', state='on', value='.5')
        
    def greenOff(self):
        postEvent('RoboControlOutput', name='RGBLED', state='off')

    def blueOn(self):
        postEvent('RoboControlOutput', name='RGBLED', state='on', value='blue')
        postEvent('RoboControlOutput', name='BlueLED', state='on', value='.5')
        
    def blueOff(self):
        postEvent('RoboControlOutput', name='RGBLED', state='off')
        
    def allOff(self):
        postEvent('RoboControlOutput', name='RGBLED', state='off')
        
        postEvent('RoboControlOutput', name='RedLED', state='off')
        postEvent('RoboControlOutput', name='GreenLED', state='off')
        postEvent('RoboControlOutput', name='BlueLED', state='off')

        
    #not working for some reason
    def redBlink(self):
        if self.redBlinking == False:
            postEvent('RoboControlOutput', name='RGBLED', state='blink', value=('red', 500))
            self.redBlinking = True
        
    def redBlinkOff(self):
        if self.redBlinking == True:
            self.redBlinking = False
            postEvent('RoboControlOutput', name='RedLED', state='off')
        
        
        



#you must have 2 fonts open
if len(AllFonts()) < 2:
    print 'Error: You must have two fonts open\nOpen two fonts and try again\n\nExit\n'
    sys.exit()
    self.deactivateModule()


else: 
    font1 = CurrentFont()
    font2 = AllFonts()[1]
    
    
    
    
#set Initial Glyph to glyphInit if it exists in font
if len(font1.keys()) > 0:

    glyphInit = '.notdef'
    #checks to see if glyphInit exists
    if glyphInit in font1.keys():
        gInit = font1[glyphInit]
    else:
        #if it doesn't exist, this gets first glyph in font
        key = font1.keys()[0]
        gInit = font1[key]
else: 
    print 'Error: Both fonts must have glyphs\nDraw some glyphs and try again\n\nExit\n'
    sys.exit()
    self.deactivateModule()
    



#initial value for interpolation
v = .5
d = Dialog(v, font1, font2)
