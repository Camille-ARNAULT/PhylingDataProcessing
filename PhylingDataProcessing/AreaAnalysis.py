# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 08:52:46 2023

@author: admin
"""

from FunctionsBasics import *
from FunctionsAreaAnalysis import *


def Start(Data):
        
    #Start Detection
    print('Start Analsysis...')
    try :
        # 1 = nb area to detect
        # 200 = who much frame will be analyzed after the user selection to detect start
        FrameInit,FrameEnd = DetectionDepartsSemiAuto(Data['CadenceTrMin'],1,200)
        FrameInit = FrameInit[0]
        FrameEnd = FrameEnd[0]
        print("- Start detected")
    except : 
        print(Fore.RED + "ERROR : Start could not be detected.")

    #Pedal stroke area detection
    try :
        # 25 = How much frame will be analyzed before and after the user selection to find the pedal stroke area
        IndexZP = FindZonesPedalees(Data["CadenceTrMin"],25,FrameInit,FrameEnd)
        print("- Pedal stroke area detected.")
    except :
        print(Fore.RED + 'ERROR : Pedal stroke area could not be detected.')    
        
    # Pedal stroke detection
    try :
        IndexCP = DetectionCoupPedaleDepart(Data["PuissanceTotale"],FrameInit,FrameEnd,IndexZP,'oui')
        print("- Pedal stroke cycle detected.")
    except :
        print(Fore.RED + "ERROR : Pedal stroke cycle could not be detected.")
    # Impulse & work by pedal stroke for start area
    try :
        ImpulsionDCP = [0 for i in range(len(IndexCP)-1)]
        TravailDCP = [0 for i in range(len(IndexCP)-1)]
        for j in range(0,len(ImpulsionDCP)):
            ImpulsionDCP[j]=np.sum(Data["ImpulsionTotale"][IndexCP[j]:IndexCP[j+1]])
            TravailDCP[j]=np.sum(Data["TravailTotal"][IndexCP[j]:IndexCP[j+1]])
        print("- Impulse & work successfully calculated.")
    except :
        print(Fore.RED + "ERROR : Impulse & work could not be calculated.")
    
    # Max retreat Crank Angle at starting gate
    FrameReculMax = FrameInit+np.argmin(Data['PositionManivelleGauche'][FrameInit:FrameInit+100])
    AngleManivelleGaucheReculMax = Data['PositionManivelleGauche'][FrameReculMax]
    AngleTotalRecul = Data['PositionManivelleGauche'][FrameReculMax]-Data['PositionManivelleGauche'][FrameInit]
         
    return FrameInit, FrameEnd, IndexCP, ImpulsionDCP, TravailDCP, AngleManivelleGaucheReculMax, AngleTotalRecul

def EndMound(Data,FrameInit):
    # Trouver le temps en bas de butte
    plt.figure()
    plt.plot(Data['ForceTotaleAbsolue'][FrameInit:FrameInit+800])
    plt.plot(Data['CadenceTrMin'][FrameInit:FrameInit+800]*10,'--')
    plt.legend(['Force Totale Absolue (N)','Cadence*10 (tr/min)'])
    plt.suptitle('RECUPERATION TEMPS BAS DE BUTTE')
    plt.title('Cliquer sur le pic de force après la reprise de pédalage :')
    plt.grid()
    plt.xlabel('Frame')
    FrameEncaissement = plt.ginput(n=1)
    FrameEncaissement = int(FrameEncaissement[0][0])
    FrameEncaissement = np.argmax(Data['ForceTotaleAbsolue'][FrameEncaissement-10:FrameEncaissement+10])+(FrameEncaissement-10)
    plt.plot(FrameEncaissement,Data['ForceTotaleAbsolue'][FrameEncaissement],'x')
    TempsBasButte = (FrameEncaissement-FrameInit)*0.005
    # plt.close()
    
    return TempsBasButte

def FirstJump(Data,FrameInit):
    
    plt.figure()
    plt.plot(Data['ForceTotaleAbsolue'][FrameInit:FrameInit+800],label='Force Totale Absolue (N)')  
    plt.plot(Data['CadenceTrMin'][FrameInit:FrameInit+800]*10,'--',label='Cadence x10 (tr/min)')  
    plt.legend()
    plt.suptitle('PHASE AERIENNE 1ere BOSSE')
    plt.title("Cliquer au pic de force lié au décollage, puis au min qui suit :")
    plt.xlabel('Frame')
    
    #Définir les limites d'étude pour trouver l'instant de décollage
    DebutDecollage = plt.ginput(n=1)
    DebutDecollage = int(DebutDecollage[0][0])
    DebutDecollage = np.argmax(Data['ForceTotaleAbsolue'][DebutDecollage-10:DebutDecollage+10])+(DebutDecollage-10)
    plt.plot(DebutDecollage,Data['ForceTotaleAbsolue'][DebutDecollage],'x')
    FinDecollage = plt.ginput(n=1)
    FinDecollage = int(FinDecollage[0][0])
    FinDecollage = np.argmin(Data['ForceTotaleAbsolue'][FinDecollage-10:FinDecollage+10])+(FinDecollage-10)
    plt.plot(FinDecollage,Data['ForceTotaleAbsolue'][FinDecollage],'x')
    plt.title("Résultats :")
    
    #Trouver la pente max de la force (=dérivée min) => considéré comme l'instant de décollage le plus répétable
    DeriveeForceTotaleAbsolue = [0 for i in range(DebutDecollage,FinDecollage)]
    a = 1
    for i in range(DebutDecollage+1,FinDecollage):
        DeriveeForceTotaleAbsolue[a] = (Data['ForceTotaleAbsolue'][i+1]-Data['ForceTotaleAbsolue'][i-1])/(0.005*2)
        a = a+1
    InstantDecollage = np.argmin(DeriveeForceTotaleAbsolue)+DebutDecollage
    TempsDecollage = (InstantDecollage-FrameInit)*0.005
    plt.plot(InstantDecollage,Data['ForceTotaleAbsolue'][InstantDecollage],'x')
    # plt.close()
    
    #Vitesse de décollage calculée comme la moyenne de la vitesse lors de la chute de la force
    VitesseDecollage = np.mean(Data['VitesseTopTour'][InstantDecollage-5:InstantDecollage+5])
    StdVitesseDecollage =  np.std(Data['VitesseTopTour'][InstantDecollage-5:InstantDecollage+5])
    
    return TempsDecollage, VitesseDecollage, StdVitesseDecollage
        