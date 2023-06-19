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
    - Description -
    This function is used to resample data with specific frequency.
    
    - Parameters - 
    xinit : original abscissa of the data to be resampled
    xfinal : abscissa needed
    y : original ordinate of the data to be resampled
    """
    data_interpolated = CubicSpline(xinit,y)
    data_resample=data_interpolated(xfinal)
    return data_resample

def NumberOfNonNans(data):
    """
    - Description -
    This function is used to find number of non Nans in data.
    
    - Parameters -
    data : Data you need to know number of non Nans.
    """
    count = 0
    for i in data:
        if not np.isnan(i):
            count += 1
    return count
 
def FiltrageButterworth(Data,FreqAcq,FreqCut):
    """
    - Description -
    This function is used to apply Butterworth filter on data.
    
    - Parameters -
    Data : Data you want to filter.
    FreqAcq : Data frequency.
    FreqCut: Maximum high frequency. 
    """
    w = FreqCut / (FreqAcq / 2) # Normalize the frequency
    b, a = butter(5, w, 'low')
    DataFiltered  = filtfilt(b, a, Data)
    return DataFiltered 

def IntegrationTrapeze(Data,FreqAcq):
    """
    - Description -
    This function is used to apply the trapezoidal method integration.
    
    - Parameters -
    Data : Data you want to integrate.
    FreqAcq : Data frequency.
    """
    donnees_integrees = np.zeros(shape=(len(Data),1))
    for i in range(1,len(Data)) :
        aire_rectangle = (min(Data[i],Data[i-1]))*(1/FreqAcq)
        aire_triangle = (abs(Data[i]-Data[i-1])*(1/FreqAcq))/2
        donnees_integrees[i] = aire_rectangle + aire_triangle
    return donnees_integrees

def IndexNearestValue(Array, Value): 
    """
    - Description -
    This function is used to 
    
    - Parameters -
    Array : 
    Value : 
    """
    Array = np.asarray(Array)
    Index = (np.abs(Array - Value)).argmin()
    return Index

def DetectionFrontMontant(DataADeriver,TempsDataADeriver,LimInit,LimEnd):
    """
    - Description -
    This function is used to 
    
    - Parameters -
    DataADeriver : 
    TempsDataADeriver : 
    LimInit :
    LimEnd :
    """
    # Calcul de la dérivée de la donnée
    DataDerivee = [0 for i in range(0,len(DataADeriver))]
    for i in range(1,len(DataADeriver)-1):
        DataDerivee[i]=(DataADeriver[i+1]-DataADeriver[i-1])/(TempsDataADeriver[i+1]-TempsDataADeriver[i-1])
    
    # Calcul de l'écart-type dans l'intervalle fourni par l'utilisateur
    DataDerivee_STD = np.std(DataDerivee[LimInit:LimEnd])
    
    # Recherche de la frame à laquelle DataDerivee > 3*std
    FrameSup3Std = LimEnd
    while abs(DataDerivee[FrameSup3Std]) < DataDerivee_STD *3 :
        FrameSup3Std = FrameSup3Std +1   
    return FrameSup3Std, DataDerivee_STD



