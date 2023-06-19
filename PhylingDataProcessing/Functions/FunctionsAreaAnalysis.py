"""
@author: arnaultcamille@univ-poitiers.fr
"""

from FunctionsBasics import *

def DetectionCoupPedaleDepart(DataPuissance,FrameInit,FrameEnd,IndexZonesPedalees,Affichage):
    """
    - Description -
    This function is used to 
    
    - Parameters -
    DataPuissance : 
    FrameInit : 
    FrameEnd :
    IndexZonesPedalees :
    Affichage :
    """
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

def DetectionDepartsSemiAuto(CadenceTrMin,NbZones,Etendue):
    """
    - Description -
    This function is used to 
    
    - Parameters -
    CadenceTrMin : 
    NbZones :
    Etendue :
    """
    plt.figure()
    plt.plot(CadenceTrMin,'-')
    plt.title("Détection des Départs : Cliquer avant l'augmentation de la cadence.")
    #Détermination début
    FrameInitUser = plt.ginput(n=NbZones,timeout=30,show_clicks=True)
    FrameInit = [0 for i in range(NbZones)]
    for depart in range(0,NbZones):
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
    for i in range(0,NbZones):
        FrameInit[i]=FrameInit[i]-20
    plt.plot(FrameInit,CadenceTrMin[FrameInit],'x') 
    #Détermination fin           
    FrameEnd = [0 for i in range(NbZones)]
    for depart in range(0,NbZones):
        it = 0
        MeanCad = np.mean(CadenceTrMin[FrameInit[depart]:FrameInit[depart]+Etendue])
        StdCad = np.std(CadenceTrMin[FrameInit[depart]:FrameInit[depart]+Etendue])
        while not (StdCad < 0.5 and StdCad > -0.5) and (MeanCad < 0.5 or MeanCad > -0.5) :
            it = it+1
            MeanCad = np.mean(CadenceTrMin[FrameInit[depart]+it:FrameInit[depart]+Etendue+it])  
            StdCad = np.std(CadenceTrMin[FrameInit[depart]+it:FrameInit[depart]+Etendue+it])  
        FrameEnd[depart] = FrameInit[depart]+it
    plt.plot(FrameInit,CadenceTrMin[FrameInit],'x')
    plt.plot(FrameEnd,CadenceTrMin[FrameEnd],'x') 
    return FrameInit,FrameEnd 

def FindZonesPedalees(Data,IntRecherche,FrameInit,FrameEnd):
    """
    - Description -
    This function is used to 
    
    - Parameters -
    Data : 
    IntRecherche :
    FrameInit :
    FrameEnd :
    """
    
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