"""
@author: arnaultcamille@univ-poitiers.fr
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter
from scipy.signal import filtfilt
from scipy.signal import find_peaks
from colorama import Fore
from scipy.interpolate import CubicSpline

def InterpolationResample(xinit,xfinal,y):
    """
    USES
    
    * Resample data with specific frequency.
    
    
    PARAMETERS
    
    * xinit : original abscissa of the data to be resampled (Nx1)
    
    * xfinal : abscissa needed (Nx1)
    
    * y : original ordinate of the data to be resampled (Nx1)
    
    """
    InterpolatedData = CubicSpline(xinit,y)
    ResampledData=InterpolatedData(xfinal)
    return ResampledData

def NumberOfNonNans(Data):
    """
    USES
    
    * Find number of non Nans in data.
    
    PARAMETERS
    
    * Data : Data set for which you want to know the number of non Nans. (Nx1)
    """
    Count = 0
    for i in Data:
        if not np.isnan(i):
            Count += 1
    return Count
 
def FiltrageButterworth(Data,FreqAcq,FreqCut):
    """
    USES
    
    * Apply Butterworth filter on data.
    
    
    PARAMETERS
    
    * Data : Data you want to filter. (Nx1)
    
    * FreqAcq : Data frequency. (int)
    
    * FreqCut : Maximum high frequency. (int)
    
    """
    w = FreqCut / (FreqAcq / 2) # Normalize the frequency
    b, a = butter(5, w, 'low')
    DataFiltered  = filtfilt(b, a, Data)
    return DataFiltered 

def IntegrationTrapeze(Data,FreqAcq):
    """
    USES
    
    * Apply the trapezoidal method integration.
    
    
    PARAMETERS
    
    * Data : Data you want to integrate. (Nx1)
    
    * FreqAcq : Data frequency. (int)
    
    """
    IntegratedData = np.zeros(shape=(len(Data),1))
    for i in range(1,len(Data)) :
        RectangleArea = (min(Data[i],Data[i-1]))*(1/FreqAcq)
        TriangleArea = (abs(Data[i]-Data[i-1])*(1/FreqAcq))/2
        IntegratedData[i] = RectangleArea + TriangleArea
    return IntegratedData

def IndexNearestValue(Array, Value): 
    """
    USES
    
    * Find the index of the value that is closest to a given value.
    
    PARAMETERS
    
    * Array : data in which to search Value. (Nx1)
        
    * Value : Value you want to find. (int)
        
    """
    Array = np.asarray(Array)
    Index = (np.abs(Array - Value)).argmin()
    return Index

def DetectionFrontMontant(DataToDerive,TimeDataToDerive,LimInit,LimEnd):
    """
    USES
    
    * Detect rising
    
    PARAMETERS
    
    * DataToDerive : Data in which you want detect the rising instant. (Nx1)
        
    * TimeDataToDerive : Abscissa of DataToDerive. (Nx1)
        
    * LimInit : Analysis start frame. (int)
        
    * LimEnd : Analysis end frame. (int)
        
    """
    # Derivative calculation
    DerivatedData = [0 for i in range(0,len(DataToDerive))]
    for i in range(1,len(DataToDerive)-1):
        DerivatedData[i]=(DataToDerive[i+1]-DataToDerive[i-1])/(TimeDataToDerive[i+1]-TimeDataToDerive[i-1])
    # Standard deviation calculation
    DerivatedDataSTD = np.std(DerivatedData[LimInit:LimEnd])
    # Find frame at which DerivatedData > 3*std
    RisingFrame = LimEnd
    while abs(DerivatedData[RisingFrame]) < DerivatedDataSTD *3 :
        RisingFrame = RisingFrame +1   
    return RisingFrame, DerivatedDataSTD



