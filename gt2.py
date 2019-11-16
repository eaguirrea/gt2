﻿# -*- coding: utf-8 -*-

# ---------------------------------------------------------------------------------------
# 						Copyright (c) 2019 - Emilio Aguirre
# ---------------------------------------------------------------------------------------                                                                                               
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLEFOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.    
# ---------------------------------------------------------------------------------------
  
__title__   = "GT2/GT3/GT5 Timing Gear Creator"
__author__  = "eaguirre"
__version__ = "1.4"
__date__    = "30/04/2019"
__url__     = "http://www.emilioaguirre.com"
__Comment__ = "GT2/GT3/GT5 Gear Creator Macro (any gear size from 5 to 360 teeth)"
__Communication__ = "info@emilioaguirre.com"

import math
import Part
import sys
import time
import FreeCAD, FreeCADGui
import Sketcher, PartDesign
import ProfileLib.RegularPolygon
from FreeCAD import Base
from PySide import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
# -----------------------------------
# QT Window Class
# -----------------------------------
class GTWnd(object):

	def __init__(self, MainWindow):
		self.shaft = True
		self.isCircle = True
		self.shaft_diameter = 5.0
		self.hgear = 6.0
		self.base_height = 1.0
		self.base_diameter = 6.37
		self.top_height = 1.0
		self.top_diameter = 6.37
		self.addBase = False
		self.addTop = False
		self.max_shaft_diameter = 100.0
		self.teeth = 20
		self.w = 300.0
		self.h = 340.0
		self.addKey = False
		self.key_b = 2
		self.key_h = 2
		self.t1 = 1.2
		self.t2 = 1
		
		# UI Definition
		self.window = MainWindow
		MainWindow.setObjectName(_fromUtf8("MainWindow"))
		MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		MainWindow.resize(self.w, self.h)
		self.central_wdgt = QtGui.QWidget(MainWindow)
		self.central_wdgt.setObjectName(_fromUtf8("centralWidget"))
		
		# UI Elements
		self.typeLbl = QtGui.QLabel(self.central_wdgt)
		self.typeLbl.setGeometry(QtCore.QRect(self.w*0.05, self.h*0.01, 150, 16))
		self.typeLbl.setObjectName("typeLbl")
		
		self.gt_type = QtGui.QComboBox(self.central_wdgt)
		self.gt_type.addItems(["GT2", "GT3", "GT5"])
		self.gt_type.setGeometry(QtCore.QRect(self.w*0.45, self.h*0.01, 95, 20))
		self.gt_type.setObjectName(_fromUtf8("gt_type"))
		self.gt_type.currentIndexChanged.connect(self.on_gt_type_change)

		self.teethLbl = QtGui.QLabel(self.central_wdgt)
		self.teethLbl.setGeometry(QtCore.QRect(self.w*0.05, self.h*0.08, 150, 16))
		self.teethLbl.setObjectName("teethLbl")
		
		self.num_teeth = QtGui.QSpinBox(self.central_wdgt)                       
		self.num_teeth.setGeometry(QtCore.QRect(self.w*0.45, self.h*0.08, 100, 22))
		self.num_teeth.setMinimum(5)
		self.num_teeth.setMaximum(360)
		self.num_teeth.setSingleStep(1)
		self.num_teeth.setValue(int(self.teeth))
		self.num_teeth.setObjectName(_fromUtf8("num_teeth"))
		self.num_teeth.valueChanged.connect(self.on_num_teeth_changed)

		self.rangeLbl = QtGui.QLabel(self.central_wdgt)
		self.rangeLbl.setGeometry(QtCore.QRect(self.w*0.80, self.h*0.08, 150, 16))
		self.rangeLbl.setObjectName("typeLbl")
		
		self.heightLbl = QtGui.QLabel(self.central_wdgt)
		self.heightLbl.setGeometry(QtCore.QRect(self.w*0.05, self.h*0.16, 150, 16))
		self.heightLbl.setObjectName("heightLbl")
		
		self.hgearear = QtGui.QDoubleSpinBox(self.central_wdgt)                       
		self.hgearear.setGeometry(QtCore.QRect(self.w*0.45, self.h*0.16, 100, 22))
		self.hgearear.setMinimum(0.01)
		self.hgearear.setMaximum(100.0)
		self.hgearear.setSingleStep(0.01)
		self.hgearear.setValue(float(self.hgear))
		self.hgearear.setObjectName(_fromUtf8("hgearear"))
		self.hgearear.valueChanged.connect(self.on_hgearear_valuechanged)
		
		self.mmLbl = QtGui.QLabel(self.central_wdgt)
		self.mmLbl.setGeometry(QtCore.QRect(self.w*0.80, self.h*0.16, 32, 16))
		self.mmLbl.setObjectName("mmLbl")

		# Shaft Information
		self.checkShaft = QtGui.QCheckBox("Shaft diameter", self.central_wdgt)
		self.checkShaft.setGeometry(QtCore.QRect(self.w*0.05, self.h*0.25, 200, 25))                  
		self.checkShaft.setChecked(self.shaft)                                                 
		self.checkShaft.clicked.connect(self.on_checkShaft_clicked)

		self.diameter_shaft = QtGui.QDoubleSpinBox(self.central_wdgt)                       
		self.diameter_shaft.setGeometry(QtCore.QRect(self.w*0.45, self.h*0.25, 100, 22))                 
		self.diameter_shaft.setMinimum(0.01)                                      
		self.diameter_shaft.setMaximum(100.0)                                        
		self.diameter_shaft.setSingleStep(0.01)
		self.diameter_shaft.setValue(self.shaft_diameter)                                        
		self.diameter_shaft.setObjectName(_fromUtf8("diameter_shaft"))                  
		self.diameter_shaft.valueChanged.connect(self.on_diameter_shaft_valuechanged)   
		
		self.mm2Lbl = QtGui.QLabel(self.central_wdgt)
		self.mm2Lbl.setGeometry(QtCore.QRect(self.w*0.8, self.h*0.25, 32, 16))
		self.mm2Lbl.setObjectName("mm2Lbl")
		
		self.radioCircle = QtGui.QRadioButton("Circle",self.central_wdgt)
		self.radioCircle.move(self.w*0.25, self.h*0.33)                  
		self.radioCircle.setChecked(self.isCircle)    
		self.radioCircle.clicked.connect(self.on_radioCircle_clicked)                    

		self.checkKeyHub = QtGui.QCheckBox("Key hub", self.central_wdgt)
		self.checkKeyHub.setGeometry(QtCore.QRect(self.w*0.55, self.h*0.33, 200, 25))                  
		self.checkKeyHub.setChecked(self.addKey)                                                 
		self.checkKeyHub.clicked.connect(self.on_checkKeyHub_clicked)
		self.checkKeyHub.hide()
		
		self.radioHex = QtGui.QRadioButton("Hexagon",self.central_wdgt)
		self.radioHex.move(self.w*0.25, self.h*0.38)                                 
		self.radioHex.setChecked(not self.isCircle) 
		self.radioHex.clicked.connect(self.on_radioHex_clicked)

		# Base information
		self.checkBase = QtGui.QCheckBox("Add base", self.central_wdgt)
		self.checkBase.move(self.w*0.05, self.h*0.45)                    
		self.checkBase.setChecked(self.addBase)                                                 
		self.checkBase.clicked.connect(self.on_checkBase_clicked)

		self.heightBaseLbl = QtGui.QLabel(self.central_wdgt)
		self.heightBaseLbl.setGeometry(QtCore.QRect(self.w*0.4, self.h*0.45, 32, 16))
		self.heightBaseLbl.setObjectName("heightBaseLbl")
		self.heightBaseLbl.hide()
		
		self.height_base = QtGui.QDoubleSpinBox(self.central_wdgt)                       
		self.height_base.setGeometry(QtCore.QRect(self.w*0.45, self.h*0.45, 100, 22))                 
		self.height_base.setMinimum(0.01)                                      
		self.height_base.setMaximum(100.0)                                        
		self.height_base.setSingleStep(0.5)
		self.height_base.setValue(self.base_height)                                        
		self.height_base.setObjectName(_fromUtf8("height_base"))                  
		self.height_base.valueChanged.connect(self.on_height_base_valuechanged)   
		self.height_base.hide()
		
		self.mm3Lbl = QtGui.QLabel(self.central_wdgt)
		self.mm3Lbl.setGeometry(QtCore.QRect(self.w*0.8, self.h*0.45, 32, 16))
		self.mm3Lbl.setObjectName("mm3Lbl")
		self.mm3Lbl.hide()
			
		self.radiusBaseLbl = QtGui.QLabel(self.central_wdgt)
		self.radiusBaseLbl.setGeometry(QtCore.QRect(self.w*0.4, self.h*0.54, 32, 16))
		self.radiusBaseLbl.setObjectName("radiusBaseLbl")
		self.radiusBaseLbl.hide()
		
		self.diameter_base = QtGui.QDoubleSpinBox(self.central_wdgt)                       
		self.diameter_base.setGeometry(QtCore.QRect(self.w*0.45, self.h*0.54, 100, 22))                 
		self.diameter_base.setMinimum(self.shaft_diameter)                                      
		self.diameter_base.setMaximum(500.0)                                        
		self.diameter_base.setSingleStep(0.5)
		self.diameter_base.setValue(self.base_diameter)                                        
		self.diameter_base.setObjectName(_fromUtf8("diameter_base"))                  
		self.diameter_base.valueChanged.connect(self.on_diameter_base_valuechanged)   
		self.diameter_base.hide()
		
		self.mm4Lbl = QtGui.QLabel(self.central_wdgt)
		self.mm4Lbl.setGeometry(QtCore.QRect(self.w*0.8, self.h*0.54, 32, 16))
		self.mm4Lbl.setObjectName("mm4Lbl")
		self.mm4Lbl.hide()
		
		# Top information
		self.checkTop = QtGui.QCheckBox("Add top", self.central_wdgt)
		self.checkTop.move(self.w*0.05, self.h*0.63)                    
		self.checkTop.setChecked(self.addBase)                                                 
		self.checkTop.clicked.connect(self.on_checkTop_clicked)

		self.heightTopLbl = QtGui.QLabel(self.central_wdgt)
		self.heightTopLbl.setGeometry(QtCore.QRect(self.w*0.4, self.h*0.63, 32, 16))
		self.heightTopLbl.setObjectName("heightTopLbl")
		self.heightTopLbl.hide()
		
		self.height_top = QtGui.QDoubleSpinBox(self.central_wdgt)                       
		self.height_top.setGeometry(QtCore.QRect(self.w*0.45, self.h*0.63, 100, 22))                 
		self.height_top.setMinimum(0.01)                                      
		self.height_top.setMaximum(100.0)                                        
		self.height_top.setSingleStep(0.5)
		self.height_top.setValue(self.base_height)                                        
		self.height_top.setObjectName(_fromUtf8("height_top"))                  
		self.height_top.valueChanged.connect(self.on_height_top_valuechanged)   
		self.height_top.hide()
		
		self.mm5Lbl = QtGui.QLabel(self.central_wdgt)
		self.mm5Lbl.setGeometry(QtCore.QRect(self.w*0.8, self.h*0.63, 32, 16))
		self.mm5Lbl.setObjectName("mm5Lbl")
		self.mm5Lbl.hide()
			
		self.radiusTopLbl = QtGui.QLabel(self.central_wdgt)
		self.radiusTopLbl.setGeometry(QtCore.QRect(self.w*0.4, self.h*0.72, 32, 16))
		self.radiusTopLbl.setObjectName("radiusTopLbl")
		self.radiusTopLbl.hide()
		
		self.diameter_top = QtGui.QDoubleSpinBox(self.central_wdgt)                       
		self.diameter_top.setGeometry(QtCore.QRect(self.w*0.45, self.h*0.72, 100, 22))                 
		self.diameter_top.setMinimum(self.shaft_diameter)                                      
		self.diameter_top.setMaximum(500.0)                                        
		self.diameter_top.setSingleStep(0.5)
		self.diameter_top.setValue(self.top_diameter)                                        
		self.diameter_top.setObjectName(_fromUtf8("diameter_top"))                  
		self.diameter_top.valueChanged.connect(self.on_diameter_top_valuechanged)   
		self.diameter_top.hide()
		
		self.mm6Lbl = QtGui.QLabel(self.central_wdgt)
		self.mm6Lbl.setGeometry(QtCore.QRect(self.w*0.8, self.h*0.72, 32, 16))
		self.mm6Lbl.setObjectName("mm6Lbl")
		self.mm6Lbl.hide()
		
		self.createBtn = QtGui.QPushButton(self.central_wdgt)
		self.createBtn.setGeometry(QtCore.QRect(self.w*0.65, self.h*0.81, 80, 28))
		self.createBtn.setObjectName(_fromUtf8("Create"))
		self.createBtn.clicked.connect(self.on_create_clicked)

		self.cancelBtn = QtGui.QPushButton(self.central_wdgt)
		self.cancelBtn.setGeometry(QtCore.QRect(self.w*0.2, self.h*0.81, 80, 28))
		self.cancelBtn.setObjectName(_fromUtf8("cancel"))
		self.cancelBtn.clicked.connect(self.on_cancel_clicked)
		
		# Set UI elements to window
		MainWindow.setCentralWidget(self.central_wdgt)
		
		# Set strings to UI
		self.retranslateUi(MainWindow)
		
		# ----------------------------------------------------------------------
		#  Key Size Chart Standard Metric Keys/Keyways Engineering
		# ----------------------------------------------------------------------
		self.metric_keys = [
			{'over':6,'upto':8,'b':2,'h':2,'t1':1.2,'t2':1,'r':0.08},
			{'over':8,'upto':10,'b':3,'h':3,'t1':1.8,'t2':1.4,'r':0.08},
			{'over':10,'upto':12,'b':4,'h':4,'t1':2.5,'t2':1.8,'r':0.08},
			{'over':12,'upto':17,'b':5,'h':5,'t1':3,'t2':2.3,'r':0.16},
			{'over':17,'upto':22,'b':6,'h':6,'t1':3.5,'t2':2.8,'r':0.16},
			{'over':22,'upto':30,'b':8,'h':7,'t1':4,'t2':3.3,'r':0.16},
			{'over':30,'upto':38,'b':10,'h':8,'t1':5,'t2':3.3,'r':0.25},
			{'over':38,'upto':44,'b':12,'h':8,'t1':5,'t2':3.3,'r':0.25},
			{'over':44,'upto':50,'b':14,'h':9,'t1':5.5,'t2':3.8,'r':0.25},
			{'over':50,'upto':58,'b':16,'h':10,'t1':6,'t2':4.3,'r':0.25},
			{'over':58,'upto':65,'b':18,'h':11,'t1':7,'t2':4.4,'r':0.25},
			{'over':65,'upto':75,'b':20,'h':12,'t1':7.5,'t2':4.9,'r':0.40},
			{'over':75,'upto':85,'b':22,'h':14,'t1':9,'t2':5.4,'r':0.40},
			{'over':85,'upto':95,'b':25,'h':14,'t1':9,'t2':5.4,'r':0.40},
			{'over':95,'upto':110,'b':28,'h':16,'t1':10,'t2':6.4,'r':0.40},
			{'over':110,'upto':130,'b':32,'h':18,'t1':11,'t2':7.4,'r':0.40},
			{'over':130,'upto':150,'b':36,'h':20,'t1':12,'t2':8.4,'r':0.70},
			{'over':150,'upto':170,'b':40,'h':22,'t1':13,'t2':9.4,'r':0.70},
			{'over':170,'upto':200,'b':45,'h':25,'t1':15,'t2':10.4,'r':0.70},
			{'over':200,'upto':230,'b':50,'h':28,'t1':17,'t2':11.4,'r':0.70}
		]
		
		
		# ----------------------------------------------------------------------
		# Gear Data
		# pitch - distance between two teeth
		# u     - pitch differential. The radial distance between pitch diameter 
		#		  and pulley outer diameter is called pitch differential.
		# h     - Tooth height
		# H     - Belt height
		# r0	- Inner circle radius
		# r1    - Side circle radius that define the side of a tooth
		# rs    - Small circle radius that define the corner of a tooth
		# offset- Offset of the side circle center 
		# name  - Gear name
		# group - Type of Gear
		# ----------------------------------------------------------------------
		
		# GT2 Gear Data 
		self.gt2 = {'pitch':2.0,
			'u':0.254,
			'h':0.75,
			'H':1.38,
			'r0':0.555,
			'r1':1.0,
			'rs':0.15,
			'offset':0.40,
			'name':'GT2',
			'group':'GT'
			}
		# GT3 Gear Data
		self.gt3 = {'pitch':3.0,
			'u':0.381,
			'h':1.14,
			'H':2.40,
			'r0':0.85,
			'r1':1.52,
			'rs':0.25,
			'offset':0.61,
			'name':'GT3',
			'group':'GT'
			}
		# GT5 Gear Data
		self.gt5 = {'pitch':5.0,
			'u':0.5715,
			'h':1.93,
			'H':3.81,
			'r0':1.44,
			'r1':2.57,
			'rs':0.416,
			'offset':1.03,
			'name':'GT5',
			'group':'GT'
			}
	
	def circle_intersect_vline(self,x,r):
		y = math.sqrt((r*r) - (x*x))
		return y
		
	def polar(self, angle, radio, pt):
		"""
			Convert from polar coordinates (Theta, radius) to
			cartesian coordinates. The result is added to the
			given vector pt
		"""
		p = App.Vector(0,0,0)
		p[0] = pt[0] + (radio * math.cos(math.radians(angle)))
		p[1] = pt[1] + (radio * math.sin(math.radians(angle)))
		return p

	def get_middle_vector(self,v1, v2, m):
		"""
			Find the middle vector between two vectors. 
		"""
		return (v1 + v2).normalize() * m

	def gt_tooth(self, step, data):
		"""
			Calculate the coordinates of the GT tooth vertices.
			(the teeth of the gear, not the teeth of the timing belt)
			This calculates the right size of the previous tooth
			and the left side of the next tooth
		"""
		up = App.Vector(0,0,1)
		zero = App.Vector(0,0,0)
	
		r = (data['dr0'] - data['h']) + data['r0']	
		c0 = self.polar(step, r, zero)
		cm = self.polar(step, r - data['r0'], zero)
		pt = self.polar(step, data['dr0'],zero)
		ptn = pt.cross(up).normalize()
		ptd = App.Vector(pt).normalize() * -1
	
		pr = pt + (ptn * data['offset'])
		pl = pt + (ptn * -data['offset'])
		a = data['r1']/2
		b = a * math.sqrt(3)

		cl = pr + (ptn * -b) + (ptd * a)
		cl0 = pr + (ptn * -(data['r1']+data['rs'])) 
		cl1 = pr + (ptn * -data['r1']) + (ptd * data['rs'])
		ecl = cl0 + (ptd * data['rs'])
		cl2 = ecl + self.get_middle_vector(cl0 - ecl, cl1 - ecl, data['rs'])
		cl3 = pr + self.get_middle_vector(cl - pr, cl1 - pr, data['r1'])
	
		cr = pl + (ptn * b)  + (ptd * a)
		cr0 = pl + (ptn * (data['r1']+data['rs']))
		cr1 = pl + (ptn * data['r1']) + (ptd * data['rs'])
		ecr = cr0 + (ptd * data['rs'])
		cr2 = ecr + self.get_middle_vector(cr0 - ecr, cr1 - ecr, data['rs'])
		cr3 = pl + self.get_middle_vector(cr - pl, cr1 - pl, data['r1'])
		return [cr0, cr2, cr1, cr1, cr3, cr, cr, cm, cl, cl, cl3, cl1, cl1, cl2, cl0]

	def create_gear(self, doc, data):
		"""
			Create the geometry of the gear. Each tooth is a sequence of arcs 
			(3 points non coincidental vertices). 
		"""
		teeth = data['teeth']
		angle = 360.0/teeth
		gear = []
		for idx in range(teeth):
			step = angle * idx
			t = None
			if data['group'] == "GT":
				t = self.gt_tooth(step, data)
			else:
				raise Exception("Invalid group %s" % data['group'])	
			if len(gear)>0:
				doc.SketchGear.addGeometry(Part.LineSegment(gear[-1], t[0]))
			gear.extend(t)
			for idx in range(0,len(t)-1,3):
				doc.SketchGear.addGeometry(Part.ArcOfCircle(t[idx], t[idx+1], t[idx+2]))
		doc.SketchGear.addGeometry(Part.LineSegment(gear[-1], gear[0]))
		doc.recompute()
	
	def create_key(self, d, z):
		y1 = (d - self.t1) + (self.key_h/2)
		y2 = (d + self.t2)
		yb = self.circle_intersect_vline(-self.key_b/2,d)
		pt = self.polar(90.0, yb, App.Vector(0,0,z))
		c1 = self.polar(180, self.key_b/2, pt)
		c4 = self.polar(0, self.key_b, c1)
		pt = self.polar(90.0, y2, App.Vector(0,0,z))
		c2 = self.polar(180, self.key_b/2 ,pt)
		c3 = self.polar(0,self.key_b, c2)
		c5 = self.polar(270, d, App.Vector(0,0,z))
		return [c1,c2,c3,c4,c5]	
		
		
	def create(self, data):
		"""
			Creating the Freecad elements inside a new document
		"""
		progress_bar = Base.ProgressIndicator()
		progress_bar.start("Running creating  gear...", 0)

		FreeCAD.newDocument(data['name'])
		doc = FreeCAD.ActiveDocument

		App.activeDocument().addObject('PartDesign::Body','Gear')
		Gui.activeView().setActiveObject('pdbody', App.activeDocument().Gear)
		App.activeDocument().Gear.newObject('Sketcher::SketchObject','SketchGear')
		App.activeDocument().SketchGear.Support = (App.activeDocument().XY_Plane, [''])
		App.activeDocument().SketchGear.MapMode = 'FlatFace'
		App.activeDocument().SketchGear.Placement = App.Placement(
									App.Vector(0.000000,0.000000,0.000000),
									App.Rotation(0.000000,0.000000,0.000000,1.000000))
		App.activeDocument().recompute()
		
		self.create_gear(doc, data)
		
		d = float(self.shaft_diameter/2)
		if self.shaft:
			if self.isCircle:
				if self.addKey:
					c = self.create_key(d, 0)
					keyLst = []
					keyLst.append(Part.LineSegment(c[0],c[1]))
					keyLst.append(Part.LineSegment(c[1],c[2]))
					keyLst.append(Part.LineSegment(c[2],c[3]))
					doc.SketchGear.addGeometry(keyLst,False)
					doc.SketchGear.addGeometry(Part.ArcOfCircle(c[3],c[4],c[0]))
				else:
					doc.SketchGear.addGeometry(Part.Circle(App.Vector(0,0,0),
							 App.Vector(0,0,1),
							 d))
			else:
				ProfileLib.RegularPolygon.makeRegularPolygon(
					'SketchGear',6,App.Vector(0.000000,0.000000,0),
					App.Vector(d,0,0),False)
		
		Gui.activeView().setActiveObject('pdbody', App.activeDocument().Gear)
		App.activeDocument().Gear.newObject("PartDesign::Pad","Pad")
		App.activeDocument().Pad.Profile = App.activeDocument().SketchGear
		
		App.activeDocument().Pad.Profile = doc.SketchGear
		App.activeDocument().Pad.Length = float(self.hgear)
		App.activeDocument().recompute()
		Gui.activeDocument().hide("SketchGear")
		Gui.activeDocument().resetEdit()
		
		# Add base to the Gear
		if self.addBase:
			Gui.activeView().setActiveObject('pdbody', App.activeDocument().Gear)
			App.activeDocument().Gear.newObject('Sketcher::SketchObject','SketchBase')
			App.activeDocument().SketchBase.Support = (App.activeDocument().XY_Plane, [''])
			App.activeDocument().SketchBase.MapMode = 'FlatFace'
			App.activeDocument().SketchBase.Placement = App.Placement(
										App.Vector(0.000000,0.000000,0.000000),
										App.Rotation(0.000000,0.000000,0.000000,1.000000))
			App.activeDocument().recompute()
		
			doc.SketchBase.addGeometry(Part.Circle(App.Vector(0,0,-float(self.base_height)),
								 App.Vector(0,0,1),
								 self.base_diameter))
			if self.shaft:
				if self.isCircle:
					if self.addKey:
						c = self.create_key(d, -float(self.base_height))
						keyLst = []
						keyLst.append(Part.LineSegment(c[0],c[1]))
						keyLst.append(Part.LineSegment(c[1],c[2]))
						keyLst.append(Part.LineSegment(c[2],c[3]))
						doc.SketchBase.addGeometry(keyLst,False)
						doc.SketchBase.addGeometry(Part.ArcOfCircle(c[3],c[4],c[0]))
					else:
						doc.SketchBase.addGeometry(Part.Circle(App.Vector(0,0,0),
								 App.Vector(0,0,1),
								 d))
				else:
					ProfileLib.RegularPolygon.makeRegularPolygon(
						'SketchBase',6,App.Vector(0.000000,0.000000,-float(self.base_height)),
						App.Vector(self.shaft_diameter/2,0,0),False)
						
			Gui.activeView().setActiveObject('pdbody', App.activeDocument().Gear)
			App.activeDocument().Gear.newObject("PartDesign::Pad","PadBase")
			App.activeDocument().PadBase.Profile = App.activeDocument().SketchBase
		
			App.activeDocument().PadBase.Profile = doc.SketchBase
			App.activeDocument().PadBase.Length = float(self.base_height)
			App.activeDocument().recompute()
		
			Gui.activeDocument().hide("SketchBase")
			Gui.activeDocument().resetEdit()
		
		# Add Top to the Gear
		if self.addTop:
			Gui.activeView().setActiveObject('pdbody', App.activeDocument().Gear)
			App.activeDocument().Gear.newObject('Sketcher::SketchObject','SketchTop')
			#App.activeDocument().SketchTop.Support = (App.activeDocument().XY_Plane, [''])
			App.activeDocument().SketchTop.MapMode = 'FlatFace'
			App.activeDocument().SketchTop.Placement = App.Placement(
										App.Vector(0.000000,0.000000,float(self.hgear)),
										App.Rotation(0.000000,0.000000,0.000000,1.000000))
			App.activeDocument().recompute()
		
			doc.SketchTop.addGeometry(Part.Circle(App.Vector(0,0,0),
								 App.Vector(0,0,1),
								 self.top_diameter))
			if self.shaft:
				if self.isCircle:
					if self.addKey:
						c = self.create_key(d, 0)
						keyLst = []
						keyLst.append(Part.LineSegment(c[0],c[1]))
						keyLst.append(Part.LineSegment(c[1],c[2]))
						keyLst.append(Part.LineSegment(c[2],c[3]))
						doc.SketchTop.addGeometry(keyLst,False)
						doc.SketchTop.addGeometry(Part.ArcOfCircle(c[3],c[4],c[0]))
					else:
						doc.SketchTop.addGeometry(Part.Circle(App.Vector(0,0,0),
								 App.Vector(0,0,1),
								 d))
				else:
					ProfileLib.RegularPolygon.makeRegularPolygon(
						'SketchTop',6,App.Vector(0.000000,0.000000,0),
						App.Vector(d,0,0),False)
						
			Gui.activeView().setActiveObject('pdbody', App.activeDocument().Gear)
			App.activeDocument().Gear.newObject("PartDesign::Pad","PadTop")
			App.activeDocument().PadTop.Profile = App.activeDocument().SketchTop
		
			App.activeDocument().PadTop.Profile = doc.SketchTop
			App.activeDocument().PadTop.Length = float(self.top_height)
			App.activeDocument().recompute()
		
			Gui.activeDocument().hide("SketchTop")
			Gui.activeDocument().resetEdit()
			
		Gui.SendMsgToActiveView("ViewFit")
		progress_bar.stop()

		
	def retranslateUi(self, window):
		"""
			Setting the UI text
		"""
		window.setWindowTitle(_translate("MainWindow", "GT2/GT3/GT5 Gear Creator",
				 None))
		self.createBtn.setText(_translate("MainWindow", "Create", None))
		self.cancelBtn.setText(_translate("MainWindow", "Exit", None))
	
		self.teethLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "No. of teeth:", None))
		self.heightLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "Height gear:", None))
		self.typeLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "Pick type of gear:", None))
		self.mmLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "mm", None))
		self.mm2Lbl.setText(QtGui.QApplication.translate("MainWindow",
						 "mm", None))
		self.mm3Lbl.setText(QtGui.QApplication.translate("MainWindow",
						 "mm", None))
		self.mm4Lbl.setText(QtGui.QApplication.translate("MainWindow",
						 "mm", None))
		self.mm5Lbl.setText(QtGui.QApplication.translate("MainWindow",
						 "mm", None))
		self.mm6Lbl.setText(QtGui.QApplication.translate("MainWindow",
						 "mm", None))
		self.rangeLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "(5 ~ 360)", None))
		self.checkShaft.setText(QtGui.QApplication.translate("MainWindow",
						 "Add shaft\r\n(Diameter)", None))
		self.radioHex.setText(QtGui.QApplication.translate("MainWindow",
						 "Hexagon", None))
		self.heightBaseLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "H:", None))
		self.radiusBaseLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "D:", None))
		self.heightTopLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "H:", None))
		self.radiusTopLbl.setText(QtGui.QApplication.translate("MainWindow",
						 "D:", None))
		self.checkKeyHub.setText(QtGui.QApplication.translate("MainWindow",
						 "Add key hub", None))
	
	
	def update_max_shaft_diameter(self):
		info = None					
		type_gear = str(self.gt_type.currentText())
		if type_gear== "GT2":
			info = dict(self.gt2)
		elif type_gear == "GT3":
			info = dict(self.gt3)
		else:
			info = dict(self.gt5)
		
		self.max_shaft_diameter = ((self.teeth * info['pitch'])/ math.pi)/2
		self.diameter_shaft.setMaximum(self.max_shaft_diameter)  
		self.checkShaft.setText(QtGui.QApplication.translate("MainWindow",
						'Add shaft\r\n(max ' + 
						'{0:.2f}'.format(self.max_shaft_diameter) + ' mm)',
						 None))
		self.diameter_base.setValue(self.max_shaft_diameter)     
		self.diameter_top.setValue(self.max_shaft_diameter)     
				 
	def update_key_hub(self):
		if self.shaft_diameter >= 6:
			found = False
			for idx in range(len(self.metric_keys)):
				k = self.metric_keys[idx]
				if self.shaft_diameter >= k['over'] and self.shaft_diameter < k['upto']:
					self.key_b = k['b'] 
					self.key_h = k['h'] 
					self.t1 = k['t1'] 
					self.t2 = k['t2'] 
					found = True
					self.checkKeyHub.setText(QtGui.QApplication.translate("MainWindow",
						 "Add key hub\r\n(b:%d h:%d)" % (self.key_b,self.key_h), None))
					break
			
			if not found:
				msg = 'Cound not found a valid key values for shaft radius: %s' % shaft_diameter
				self.errorDialog(msg)
				self.addKey = False
				self.checkKeyHub.setText(QtGui.QApplication.translate("MainWindow",
						 "Add key hub", None))
		else:
			self.addKey = False
	
	# -----------------------------------		
	# 		UI widgets callbacks
	# -----------------------------------
	def on_gt_type_change(self,idx):
		App.Console.PrintMessage("Current index %d selection changed %s\r\n" % 
				(idx,self.gt_type.currentText()))
		self.update_max_shaft_diameter()
	
	def on_num_teeth_changed(self,value):
		App.Console.PrintMessage("%s Number of Teeths\r\n" % value)
		self.teeth = value
		self.update_max_shaft_diameter()
	
	def errorDialog(self,msg):
		diag = QtGui.QMessageBox(QtGui.QMessageBox.Warning, 'Error in macro MessageBox',
								 msg)
		diag.setWindowModality(QtCore.Qt.ApplicationModal)
		diag.exec_()
    
	def on_create_clicked(self):
		if self.teeth>=5 and self.teeth<=360:
			App.Console.PrintMessage("Creating Gear %s \r\n" % self.gt_type.currentText())
			type_gear = str(self.gt_type.currentText())
			if type_gear== "GT2":
				data = dict(self.gt2)
			elif type_gear == "GT3":
				data = dict(self.gt3)
			else:
				data = dict(self.gt5)
			data['teeth'] = self.teeth
			data['d'] = (data['teeth'] * data['pitch'])/ math.pi
			data['d0'] = data['d'] - (2 * data['u'])
			data['dr0'] = data['d0']/2	
			App.Console.PrintMessage("pitch %s \r\n" % data['pitch'])
			App.Console.PrintMessage("teeth %s \r\n" % data['teeth'])
			App.Console.PrintMessage("u %s \r\n" % data['u'])
			App.Console.PrintMessage("d %s \r\n" % data['d'])
			App.Console.PrintMessage("d0 %s \r\n" % data['d0'])
			App.Console.PrintMessage("dr0 %s \r\n" % data['dr0'])
			self.create(data)	
		else:
			msg = 'The number of teeth should be between 5 and 360!'
			self.errorDialog(msg)
				
	def on_cancel_clicked(self):
		App.Console.PrintMessage("Exit Gear Generator\r\n")
		self.window.hide()

	def on_hgearear_valuechanged(self, value):
		App.Console.PrintMessage(str(value)+
									" height gear\r\n")
		self.hgear = value

	def on_radioCircle_clicked(self):
		self.isCircle = True
		if self.shaft_diameter >= 6 and self.isCircle:
			self.checkKeyHub.show()
			self.update_key_hub()
		
	def on_radioHex_clicked(self):
		self.isCircle = False
		self.checkKeyHub.setChecked(False) 
		self.checkKeyHub.hide()
		
	def on_diameter_shaft_valuechanged(self, value):
		App.Console.PrintMessage(str(value)+
									" Shaft radius\r\n")
		if value <= self.max_shaft_diameter:
			self.shaft_diameter = value
			self.diameter_base.setMinimum(self.shaft_diameter)
			if self.base_diameter < self.shaft_diameter:
				self.base_diameter = self.shaft_diameter
			
			self.diameter_top.setMinimum(self.shaft_diameter) 
			if self.top_diameter < self.shaft_diameter:
				self.top_diameter = self.shaft_diameter

			if self.shaft_diameter >= 6 and self.isCircle:
				self.checkKeyHub.show()
				self.update_key_hub()
			else:
				self.checkKeyHub.hide()
		else:
			self.shaft_diameter = self.max_shaft_diameter
			msg = 'The shaft radius should be less than: %s' % self.max_shaft_diameter
			self.errorDialog(msg)
		
	def on_height_base_valuechanged(self, value):
		App.Console.PrintMessage(str(value)+
									" Height base\r\n")
		self.base_height = value
		
	def on_diameter_base_valuechanged(self, value):
		App.Console.PrintMessage(str(value)+
									" Radius base\r\n")
		self.base_diameter = value
	
	def on_height_top_valuechanged(self, value):
		App.Console.PrintMessage(str(value)+
									" Height top\r\n")
		self.top_height = value
		
	def on_diameter_top_valuechanged(self, value):
		App.Console.PrintMessage(str(value)+
									" Radius top\r\n")
		self.top_diameter = value
		
	def on_checkShaft_clicked(self):
		self.shaft = not self.shaft
		if self.shaft:
			self.radioCircle.show()
			self.radioHex.show()
			self.diameter_shaft.show()
			self.mm2Lbl.show()
			if self.shaft_diameter >= 6 and self.isCircle:
				self.checkKeyHub.show()
		else:
			self.radioCircle.hide()
			self.radioHex.hide()
			self.diameter_shaft.hide()
			self.mm2Lbl.hide()
			self.checkKeyHub.setChecked(False) 
			self.checkKeyHub.hide()
			
	def on_checkKeyHub_clicked(self):
		self.addKey = not self.addKey
		if self.addKey:
			self.update_key_hub()
	
	def on_checkBase_clicked(self):
		self.addBase = not self.addBase
		if self.addBase:
			self.height_base.show()
			self.diameter_base.show()
			self.heightBaseLbl.show()
			self.radiusBaseLbl.show()
			self.mm3Lbl.show()
			self.mm4Lbl.show()
		else:
			self.height_base.hide()
			self.diameter_base.hide()
			self.heightBaseLbl.hide()
			self.radiusBaseLbl.hide()
			self.mm3Lbl.hide()
			self.mm4Lbl.hide()
			
	def on_checkTop_clicked(self):
		self.addTop = not self.addTop
		if self.addTop:
			self.height_top.show()
			self.diameter_top.show()
			self.heightTopLbl.show()
			self.radiusTopLbl.show()
			self.mm5Lbl.show()
			self.mm6Lbl.show()
		else:
			self.height_top.hide()
			self.diameter_top.hide()
			self.heightTopLbl.hide()
			self.radiusTopLbl.hide()
			self.mm5Lbl.hide()
			self.mm6Lbl.hide()
# -----------------------------------
# Create and display the main window
# -----------------------------------
MainWindow = QtGui.QMainWindow()
ui = GTWnd(MainWindow)
MainWindow.show()
