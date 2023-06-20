"""
@author: arnaultcamille@univ-poitiers.fr
"""

from FunctionsBasics import *
import imufusion

def DetectionNbZones(Data):
    #Moyenne glissante
    Pics,_ = find_peaks(Data,height=(800), prominence=500, distance = 20000)
    NbZones = len(Pics)
    # plt.figure()
    # plt.plot(Data)
    # plt.plot(Pics,Data[Pics],'x')
    print("NbZones = " + str(NbZones))
    return NbZones,Pics

def DecoupageZonesActives(Data,NbZones):
    """
    - Description -
    This function is used to 
    
    - Parameters -
    Data : 
    NbZones : 
    """
    FrameLimite = np.zeros([NbZones,2])
    for i in range(0,NbZones) :
        plt.figure()
        plt.plot(Data)
        plt.xlabel('frame')
        plt.ylabel('Cadence (Tr/min)')
        plt.suptitle('ENCADRER ZONE : '+str(i+1)+'/'+str(NbZones))
        newleftlim = plt.ginput(n=1)
        FrameLimite[i,0] = round(newleftlim[0][0])
        newrightlim = plt.ginput(n=1)
        FrameLimite[i,1] = newrightlim[0][0]
        plt.xlim(left=round(FrameLimite[i,0]))
        plt.xlim(right=round(FrameLimite[i,1]))
        plt.close()
    return FrameLimite 

   

def CalculVitesseTopTourArriere(Temps,DataMagneto,IntensitePos,IntensiteNeg,EspacementAimantDeg,Seuil,CirconferenceRoue):
    """
    - Description -
    This function is used to 
    
    - Parameters -
    Temps : 
    DataMagneto : 
    IntensitePos :
    IntensiteNeg :
    EspacementAimantDeg :
    Seuil :
    CirconferenceRoue :
    """
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
        DeplacementParTour = (CirconferenceRoue/1000)*EspacementAimantTr
        
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
    """
    - Description -
    This function is used to 
    
    - Parameters -
    TempsPedalier : 
    Verification : 
    """
    
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

def ImuOrientation(Temps,Data,Verification='Oui'):
    
    """
    Determination of IMU orientation in Eulerian parameters 
    thanks to Fusion algorithm (gyrometer + accelerometer)
    
    :param Path:
    :type Path: str
        
    :param Temps: n x 1 serie
    :type Temps: pd.series
        
    :param Data: n x 6 series, containing gyro & accelero data
    :type Data: pd.DataFrame
        
    :param Verification: Boolean to hide/unhide orientation plot
    :type Verification: str
 
    """
    
    #----------------------------------------------------------- Calcul Offset Gyro
        
    try :
        #OFFSET
        # GyroX
        FrameFinIntOffsetGyroX,_ = DetectionFrontMontant(Data['gyro_x'],Temps,0,100)
        OffsetGyroX= np.mean(Data['gyro_x'][0:FrameFinIntOffsetGyroX-20])
        GyroX = Data['gyro_x'] - OffsetGyroX
        # GyroY
        FrameFinIntOffsetGyroY,_ = DetectionFrontMontant(Data['gyro_y'],Temps,0,100)
        OffsetGyroY= np.mean(Data['gyro_y'][0:FrameFinIntOffsetGyroY-20])
        GyroY = Data['gyro_y'] - OffsetGyroY
        # GyroZ
        FrameFinIntOffsetGyroZ,_ = DetectionFrontMontant(Data['gyro_z'],Temps,0,100)
        OffsetGyroZ= np.mean(Data['gyro_z'][0:FrameFinIntOffsetGyroZ-20])
        GyroZ = Data['gyro_z'] - OffsetGyroZ
        
        #FILTRAGE
        GyroX = FiltrageButterworth(GyroX,200,20)
        GyroY = FiltrageButterworth(GyroY,200,20)
        GyroZ = FiltrageButterworth(GyroZ,200,20)
                
    except :
        print(Fore.RED + "IMU : ERREUR LORS DU CALCUL DE L'OFFSET DES GYRO")

    # =============================================================================
    # CALCUL DE L'ORIENTATION
    # =============================================================================    

    #Créer le csv pour la mise en forme des données    
    d = {'Time (s)':Temps,'Gyroscope X (deg/s)':GyroX,'Gyroscope Y (deg/s)':GyroY,'Gyroscope Z (deg/s)':GyroZ,'Accelerometer X (g)':Data['acc_x'],'Accelerometer Y (g)':Data['acc_y'],'Accelerometer Z (g)':Data['acc_z']}
    DataIMU = pd.DataFrame(data = d)
    DataIMU.to_csv("TEMPORAIRE_DataForOrientationExtraction.csv")

    #Extraire les données grace à l'algo de fusion
    # Import sensor data
    data = np.genfromtxt("TEMPORAIRE_DataForOrientationExtraction.csv", delimiter=",", skip_header=1)
    timestamp = data[:, 1]
    gyroscope = data[:, 2:5]
    accelerometer = data[:, 5:8]
    
    # Process sensor data
    ahrs = imufusion.Ahrs()
    euler = np.empty((len(timestamp), 3))
    
    ahrs.settings = imufusion.Settings(imufusion.CONVENTION_NWU,  # convention
                                       0.5,  # gain
                                       10,  # acceleration rejection
                                       20,  # magnetic rejection
                                       5 * 200)  # rejection timeout = 5 seconds
    
    for index in range(len(timestamp)):
        ahrs.update_no_magnetometer(gyroscope[index], accelerometer[index], 1 / 200)  # 200 Hz sample rate
        euler[index] = ahrs.quaternion.to_euler()


    #Changement de l'orientation pour plus de compréhesion :
        # X = axe dans le sens d'avancement, rotation positive vers la droite
        # Y = axe medio-latéral, rotation positive vers le haut
        # Z = Axe antéro-postérieur, position vers la droite 
    OrientationIMU = euler*[-1,-1,1]
       
    #Supprimer le fichier temporaire     
    import os
    os.remove("TEMPORAIRE_DataForOrientationExtraction.csv") 

    if Verification in ['OUI','Oui','oui','O','o','YES','Yes','yes','Y','y']:
        plt.figure()
        plt.plot(OrientationIMU[:,0]) 
        plt.plot(OrientationIMU[:,1])
        plt.plot(OrientationIMU[:,2])
        plt.grid()
        plt.legend(["Autour de x","Autour de y","Autour de Z"])  
        plt.xlabel("Frame") 
        plt.ylabel("Angle (°)")    
        
        
        
    return OrientationIMU