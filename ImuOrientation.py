# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 11:16:29 2023

@author: admin
"""




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
    import imufusion
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from StandardFunctions import DetectionFrontMontant, FiltrageButterworth
    from colorama import Fore
    
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