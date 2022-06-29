# -*- coding: utf-8 -*-
"""
Created on Mon May 30 14:07:41 2022

@author: chath
"""
import re

class Entity:
    def __init__(self,cin,cout):
        self.cin=cin
        self.cout=cout

    def propagate(self):
        self.cout=self.cin
        
class Contact(Entity):
    inp=False
    def propagate(self):
        self.cout=self.inp & self.cin

class Coil(Entity):
    pass

class SetCoil(Entity):
    def __init__(self):
        self.cin=False
        self.cout=True
        
    def propagate(self):
        return None
    
class ResetCoil(Entity):
    def __init__(self):
        self.cin=False
        self.cout=False
        
    def propagate(self):
        return None

class Source(Entity):
    def __init__(self):
        self.cin=True
        self.cout=True

class Neutral(Entity):
    def __init__(self):
        self.cin=False
        self.cout=False
    
    def propagate(self):
        return None

class Integer:
    
#==============================================================================
def objtranscode(l):
    d={'Source':Source()}
    
    ty=l[0]
    tyv=l[1]
    id0=l[2]
    
    for i,j,k in l:
        if (i=='con'):
            d[k]=Contact(False,False)
        elif(i=='coil'):
            d[k]=Coil(False,False)
            
    return d

def prop(curr,d,lb):
    d[curr].cin=False # Flushing old input
    for prev in lb[curr]:
        if (prev=='Source'):
            d[curr].cin=True
            break
        d[curr].cin|=prop(prev,d,lb)
    d[curr].propagate()
    return d[curr].cout

def enum(d):
    items=list(d.keys())
    for key in items:
        print(key,type(d[key]).__name__,d[key].cin,d[key].cout)
    return None

def passin(d,inputlist):
    for item in inputlist.keys():
        d[item].inp=inputlist[item]
    return None


#==============================================================================

# AND gate demo

andrung='con{bool-A},con{bool-B},coil{bool-C}'

# split [() ()]
orrung='split(con{bool-A}),(con{bool-B}),coil{bool-C},split(coil{bool-D},coil{bool-N}),(split(coil{bool-E}),(coil{bool-F}))'

capture=r'(con|coil){(bool)-(.)}'

pattern = re.compile(capture, re.IGNORECASE)

ma = pattern.findall(andrung)
#==============================================================================
# 2 input system

# inputset1={'A':False,'B':False}
# inputset2={'A':False,'B':True}
# inputset3={'A':True,'B':False}
# inputset4={'A':True,'B':True}

# di=objtranscode(ma)

# #AND Gate

# layout_forward1={'Source':['A'],'A':['B'],'B':['C'],'C':['End']}
# lb1={'C':['B'],'B':['A'],'A':['Source']}

# #OR Gate

# layout_forward2={'Source':['A','B'],'A':['C'],'B':['C'],'C':['End']}
# lb2={'C':['A','B'],'A':['Source'],'B':['Source']}

# end_node='C'
#==============================================================================
#3 input system

di={'Source':Source(),'A':Contact(False,False),'B':Contact(False,False),'C':Contact(False,False),
    'D':Coil(False,False),'Neutral':Neutral()}

lb1={'Neutral':['D'],'D':['C'],'C':['A','B'],'A':['Source'],'B':['Source']}

lb2={'Neutral':['D'],'D':['A','B'],'A':['C'],'B':['C'],'C':['Source']}

inputset1={'A':False,'B':False,'C':False}
inputset2={'A':False,'B':False,'C':True}
inputset3={'A':False,'B':True,'C':False}
inputset4={'A':False,'B':True,'C':True}
inputset5={'A':True,'B':False,'C':False}
inputset6={'A':True,'B':False,'C':True}
inputset7={'A':True,'B':True,'C':False}
inputset8={'A':True,'B':True,'C':True}





    

        
        
        