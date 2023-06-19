# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 11:22:28 2023

@author: admin
"""
import numpy as np
import pandas as pd
from scipy.signal import butter
from scipy.signal import filtfilt
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from colorama import Fore
from scipy.signal import find_peaks



def InterpolationResample(xinit,xfinal,y):
    data_interpolated = CubicSpline(xinit,y)
    data_resample=data_interpolated(xfinal)
    return data_resample

def NumberOfNonNans(data):
    count = 0
    for i in data:
        if not np.isnan(i):
            count += 1
    return count
 
def FiltrageButterworth(Data,FreqAcq,FreqCut):
    w = FreqCut / (FreqAcq / 2) # Normalize the frequency
    b, a = butter(5, w, 'low')
    DataFiltered  = filtfilt(b, a, Data)
    return DataFiltered

def DetectionFrontMontant(DataADeriver,TempsDataADeriver,LimInit,LimEnd):
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


def IntegrationTrapeze(data,FreqAcq):
    donnees_integrees = np.zeros(shape=(len(data),1))
    for i in range(1,len(data)) :
        aire_rectangle = (min(data[i],data[i-1]))*(1/FreqAcq)
        aire_triangle = (abs(data[i]-data[i-1])*(1/FreqAcq))/2
        donnees_integrees[i] = aire_rectangle + aire_triangle
    return donnees_integrees



def DecoupageZonesActives(Data,nb_zones):
    FrameLimite = np.zeros([nb_zones,2])
    for i in range(0,nb_zones) :
        plt.figure()
        plt.plot(Data)
        plt.xlabel('frame')
        plt.ylabel('Cadence (Tr/min)')
        plt.suptitle('ENCADRER ZONE : '+str(i+1)+'/'+str(nb_zones))
        newleftlim = plt.ginput(n=1)
        FrameLimite[i,0] = round(newleftlim[0][0])
        newrightlim = plt.ginput(n=1)
        FrameLimite[i,1] = newrightlim[0][0]
        plt.xlim(left=round(FrameLimite[i,0]))
        plt.xlim(right=round(FrameLimite[i,1]))
        plt.close()
    return FrameLimite 


def IndexNearestValue(array, value):  
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx




def CalculVitesseTopTourArriere(Temps,DataMagneto,IntensitePos,IntensiteNeg,EspacementAimantDeg,Seuil,circonference_roue):  
    DataOffset = DataMagneto - Seuil
    FrameInitTemps = Temps.index[0] 
    try :
        PeaksNeg,_ = find_peaks((DataOffset*(-1)),height=(IntensiteNeg,None),prominence=(IntensiteNeg,None),threshold=(0,None))
        PeaksPos,_ = find_peaks(DataOffset,height=(IntensitePos,None),prominence=(IntensitePos,None),threshold=(0,None))
        print("TOP TOUR : Détection des pics magnétiques du top tour arrière OK")
    except :
        print(Fore.RED + 'TOP TOUR : ERREUR DE DETECTION DES PICS')
        
    # try :
    #     fig,axs = plt.subplots(2)
    #     fig.suptitle("Zone "+str(zone+1))
    #     axs[0].plot(DataOffset,'-')
    #     axs[0].plot(PeaksNeg,DataOffset[PeaksNeg],'x')
    #     axs[0].set_title("Detection pics négatifs")
    #     axs[1].plot(DataOffset,'-')
    #     axs[1].plot(PeaksPos,DataOffset[PeaksPos],'x')
    #     axs[1].set_title("Detection pics positifs")
    # except :
    #     print(Fore.RED + "TOP TOUR : ERREUR D'AFFICHAGE DES PICS DETECTES.")
        
    try :
        
        # Assemblage de tous les pics dans le même tableau
        A = PeaksNeg
        PeaksTotal = np.sort((np.append(A,PeaksPos))) 
        del A
        
        # Calcul de la distance parcourue entre deux passages d'aimants
        EspacementAimantTr = EspacementAimantDeg/360
        DeplacementParTour = (circonference_roue/1000)*EspacementAimantTr
        
        # Initialisation des données
        VitesseTopTourMpS = [0 for i in range(len(PeaksTotal))]
        VitesseTopTourKmh = [0 for i in range(len(PeaksTotal))]
        DistanceTopTourM = [0 for i in range(len(PeaksTotal))]
        Xpeaks = PeaksTotal + FrameInitTemps
        
        # Calcul de la vitesse en km/h
        for i in range(1,len(PeaksTotal)-1):
            DistanceTopTourM[i] = (i+1) * DeplacementParTour
            VitesseTopTourMpS[i]= (2*DeplacementParTour)/(Temps[Xpeaks[i+1]]-Temps[Xpeaks[i-1]])
        VitesseTopTourKmh = [i * 3.6 for i in VitesseTopTourMpS]
        
        print('TOP TOUR : Calcul de la vitesse via le top tour OK')
    except :
        print(Fore.RED + "TOP TOUR : ERREUR DE CALCUL DE LA VITESSE PAR ROUE ARRIERE.")
        
    return Xpeaks[1:], PeaksTotal[1:], VitesseTopTourKmh, DistanceTopTourM, PeaksNeg, PeaksPos




def Resynchro(TempsPedalier,Verification="Oui"):
    diff = np.diff(TempsPedalier)
    index_diff = np.where(diff < 0)
    #Nous retourne les index du temps juste avant la resynchro (t1)
    NbResynchro = len(index_diff[0])
    
    TempsPedalierResynchro=(np.zeros(shape=[len(TempsPedalier),1]))*np.nan
    if NbResynchro>0:
        for r in range(0,NbResynchro):
            
            #Calculer 1/F moyen
            if r==0 :
                FrameDepartResynchro = 0
                
            else :
                FrameDepartResynchro = (index_diff[0][r-1])+1
        
            Pmoy = np.mean(diff[FrameDepartResynchro:index_diff[0][r]])    
            #Calculer l'offset deresynchro
            OffsetTotal = TempsPedalier[index_diff[0][r]]-(TempsPedalier[index_diff[0][r]+1]-Pmoy)  
            
            #Appliquer l'Offset proportionnellement à la frame depuis la dernière synchro
            for t in range(FrameDepartResynchro,index_diff[0][r]+1) :
                Correction = ((TempsPedalier[t]-TempsPedalier[FrameDepartResynchro])*OffsetTotal)/(TempsPedalier[index_diff[0][r]+1]-TempsPedalier[FrameDepartResynchro])
                TempsPedalierResynchro[t]=TempsPedalier[t]-Correction
                
            #Rajouter les dernières frames qui ne peuvent pas être resynchro
            if r == NbResynchro-1 :
                for t in range((index_diff[0][r])+1,NumberOfNonNans(TempsPedalier)):
                    TempsPedalierResynchro[t]=TempsPedalier[t]
          
        # Vérification
        if Verification in ['Oui','oui','OUI','o','O','YES','Yes','yes','Y','y'] :
            plt.figure()
            plt.plot(TempsPedalier) 
            plt.plot(TempsPedalierResynchro)
            plt.legend(['Temps pédalier Raw','Temps pédalier resynchro']) 
            plt.xlabel('Frame')
            plt.ylabel('Temps (s)') 
    elif NbResynchro == 0:
        TempsPedalierResynchro = TempsPedalier
        
    return TempsPedalierResynchro




def DetectionCoupPedaleDepart(DataPuissance,FrameInit,FrameEnd,IndexZonesPedalees,Affichage):
    PuissancePeaks,_ = find_peaks(-DataPuissance[IndexZonesPedalees[0]:IndexZonesPedalees[1]],height=(None,1500),prominence=(500,None))
    PuissancePeaks = PuissancePeaks+IndexZonesPedalees[0]
    PuissancePeaks = np.insert(PuissancePeaks,0,IndexZonesPedalees[0])
    IndexCoupsPedaleDepart = PuissancePeaks
    if Affichage in ['O','o','OUI','Oui','oui','Y','y','YES','Yes','yes'] :
        plt.figure()
        plt.title('Coups de pédale détectés :')
        plt.plot(DataPuissance[FrameInit:FrameInit+800])
        plt.plot(PuissancePeaks,DataPuissance[PuissancePeaks],'x')
    return IndexCoupsPedaleDepart

def CalculImpTravZonePedalee(Depart,IndexZonesPedalees,Index1,Index2,FrameInit,FreqAcq,Affichage) :
    DeriveeCadence = [0 for i in range(len(Depart['Cadence']))]
    for i in range(1+Depart.index[0],len(Depart['Cadence'])-1+Depart.index[0]):
        DeriveeCadence[i-Depart.index[0]] = (Depart['Cadence'][i+1]-Depart['Cadence'][i-1])/(2/FreqAcq)
    if Affichage in ['O','o','OUI','Oui','oui','Y','y','YES','Yes','yes'] :
        indices=range(Depart['PuissanceTotale'].index[0],Depart['PuissanceTotale'].index[-1]+1)
        DeriveeCadence=pd.Series(DeriveeCadence)
        DeriveeCadence.index = indices
        plt.figure()
        plt.plot(DeriveeCadence[IndexZonesPedalees[Index1]-IndexInit:IndexZonesPedalees[Index2]-IndexInit])
        plt.plot(Depart['Cadence'][IndexZonesPedalees[Index1]-IndexInit:IndexZonesPedalees[Index2]-IndexInit]*10)
        plt.plot(Depart['ForceTotale'][IndexZonesPedalees[Index1]-IndexInit:IndexZonesPedalees[Index2]-IndexInit])
        plt.plot(Depart['PuissanceTotale'][IndexZonesPedalees[Index1]-IndexInit:IndexZonesPedalees[Index2]-IndexInit])
        plt.legend(['DeriveeCadence','Cadence','ForceTotale','PuissanceTotale'])
        DeriveeCadence=DeriveeCadence.tolist()
    IndexInitCalculImpTra = (np.argmax(DeriveeCadence[IndexZonesPedalees[Index1]-IndexInit:IndexZonesPedalees[Index2]-IndexInit]))
    IndexEndCalculImpTra = (np.argmin(DeriveeCadence[IndexZonesPedalees[Index1]-IndexInit:IndexZonesPedalees[Index2]-IndexInit]))
    if Affichage in ['O','o','OUI','Oui','oui','Y','y','YES','Yes','yes'] :
        plt.plot(IndexInitCalculImpTra+IndexZonesPedalees[Index1],Depart['ForceTotale'][IndexInitCalculImpTra+IndexZonesPedalees[Index1]],'x')
        plt.plot(IndexEndCalculImpTra+IndexZonesPedalees[Index1],Depart['ForceTotale'][IndexEndCalculImpTra+IndexZonesPedalees[Index1]],'x')
        plt.plot(IndexInitCalculImpTra+IndexZonesPedalees[Index1],Depart['PuissanceTotale'][IndexInitCalculImpTra+IndexZonesPedalees[Index1]],'x')
        plt.plot(IndexEndCalculImpTra+IndexZonesPedalees[Index1],Depart['PuissanceTotale'][IndexEndCalculImpTra+IndexZonesPedalees[Index1]],'x')
    Impulsion = np.sum(Depart['Impulsion'][IndexInitCalculImpTra+(IndexZonesPedalees[Index1]-IndexInit):IndexEndCalculImpTra+(IndexZonesPedalees[Index1]-IndexInit)])
    Travail =  np.sum(Depart['Travail'][IndexInitCalculImpTra+(IndexZonesPedalees[Index1]-IndexInit):IndexEndCalculImpTra+(IndexZonesPedalees[Index1]-IndexInit)])
    return Impulsion,Travail

    plt.figure()
    plt.plot(CadenceTrMin,'-')
    #Détermination début
    FrameInitUser = plt.ginput(n=nb_zones,timeout=30,show_clicks=True)
    FrameInit = [0 for i in range(nb_zones)]
    for depart in range(0,nb_zones):
        it = 0
        FrameInit[depart] = round(FrameInitUser[depart][0])
        ValInit = CadenceTrMin[FrameInit[depart]]
        if (FrameInit[depart]+10000) < len(CadenceTrMin) :
            while ValInit > -2 and it < 10000 :
                FrameInit[depart] = FrameInit[depart]+1
                ValInit = CadenceTrMin[FrameInit[depart]]
                it = it+1
        else  :
            while ValInit > -2 and it < (len(CadenceTrMin)-FrameInit[depart]-1) :
                FrameInit[depart] = FrameInit[depart]+1
                ValInit = CadenceTrMin[FrameInit[depart]]
                it = it+1  
    for i in range(0,nb_zones):
        FrameInit[i]=FrameInit[i]-20
    plt.plot(FrameInit,CadenceTrMin[FrameInit],'x') 
    #Détermination fin           
    FrameEnd = [0 for i in range(nb_zones)]
    for depart in range(0,nb_zones):
        it = 0
        MeanCad = np.mean(CadenceTrMin[FrameInit[depart]:FrameInit[depart]+etendue])
        StdCad = np.std(CadenceTrMin[FrameInit[depart]:FrameInit[depart]+etendue])
        while not (StdCad < 0.5 and StdCad > -0.5) and (MeanCad < 0.5 or MeanCad > -0.5) :
            it = it+1
            MeanCad = np.mean(CadenceTrMin[FrameInit[depart]+it:FrameInit[depart]+etendue+it])  
            StdCad = np.std(CadenceTrMin[FrameInit[depart]+it:FrameInit[depart]+etendue+it])  
        FrameEnd[depart] = FrameInit[depart]+it
    plt.plot(FrameInit,CadenceTrMin[FrameInit],'x')
    plt.plot(FrameEnd,CadenceTrMin[FrameEnd],'x') 
    return FrameInit,FrameEnd 

def DetectionDepartsSemiAuto(CadenceTrMin,nb_zones,etendue):
    plt.figure()
    plt.plot(CadenceTrMin,'-')
    plt.title("Détection des Départs : Cliquer avant l'augmentation de la cadence.")
    #Détermination début
    FrameInitUser = plt.ginput(n=nb_zones,timeout=30,show_clicks=True)
    FrameInit = [0 for i in range(nb_zones)]
    for depart in range(0,nb_zones):
        it = 0
        FrameInit[depart] = round(FrameInitUser[depart][0])
        ValInit = CadenceTrMin[FrameInit[depart]]
        if (FrameInit[depart]+10000) < len(CadenceTrMin) :
            while ValInit > -2 and it < 10000 :
                FrameInit[depart] = FrameInit[depart]+1
                ValInit = CadenceTrMin[FrameInit[depart]]
                it = it+1
        else  :
            while ValInit > -2 and it < (len(CadenceTrMin)-FrameInit[depart]-1) :
                FrameInit[depart] = FrameInit[depart]+1
                ValInit = CadenceTrMin[FrameInit[depart]]
                it = it+1  
    for i in range(0,nb_zones):
        FrameInit[i]=FrameInit[i]-20
    plt.plot(FrameInit,CadenceTrMin[FrameInit],'x') 
    #Détermination fin           
    FrameEnd = [0 for i in range(nb_zones)]
    for depart in range(0,nb_zones):
        it = 0
        MeanCad = np.mean(CadenceTrMin[FrameInit[depart]:FrameInit[depart]+etendue])
        StdCad = np.std(CadenceTrMin[FrameInit[depart]:FrameInit[depart]+etendue])
        while not (StdCad < 0.5 and StdCad > -0.5) and (MeanCad < 0.5 or MeanCad > -0.5) :
            it = it+1
            MeanCad = np.mean(CadenceTrMin[FrameInit[depart]+it:FrameInit[depart]+etendue+it])  
            StdCad = np.std(CadenceTrMin[FrameInit[depart]+it:FrameInit[depart]+etendue+it])  
        FrameEnd[depart] = FrameInit[depart]+it
    plt.plot(FrameInit,CadenceTrMin[FrameInit],'x')
    plt.plot(FrameEnd,CadenceTrMin[FrameEnd],'x') 
    return FrameInit,FrameEnd 

def FindZonesPedalees(Data,IntRecherche,FrameInit,FrameEnd):
    #Récupération des points délimitants renseignés par User
    plt.figure()
    plt.plot(Data[FrameInit:FrameEnd],'-')
    plt.xlabel('frame')
    plt.ylabel('Cadence (Tr/min)')
    plt.title('Cliquez sur les minimums de cadence délimitant les zones de pédalage.')
    FrameUserPedalage = plt.ginput(n=-1,timeout=30,show_clicks=True)
    
    # Récupération de la longueur des données totales
    FrameReellePedalage = [0 for i in range(len(FrameUserPedalage))]
    
    for NumInt in range(0,len(FrameUserPedalage)):
        DataIntervalle=Data[round(FrameUserPedalage[NumInt][0])-IntRecherche:round(FrameUserPedalage[NumInt][0])+IntRecherche]
        FrameReellePedalage[NumInt]=np.argmin(DataIntervalle)+(round(FrameUserPedalage[NumInt][0])-IntRecherche)
    plt.plot(FrameReellePedalage,Data[FrameReellePedalage],'x') 
    return FrameReellePedalage