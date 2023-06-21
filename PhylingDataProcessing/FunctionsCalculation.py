"""
@author: arnaultcamille@univ-poitiers.fr
"""

from FunctionsBasics import *
import imufusion


def DecoupageZonesActives(Data,NbZones):
    """
    USES 
    
    * manual method for delimiting the areas to be studied.
    
    PARAMETERS
    
    * Data : Data set for visualizing different work areas. - Cadence for example. (Nx1) 
    
    * NbZones : Number of work areas to be studied. (int)
    
    """
    FrameLimite = np.zeros([NbZones,2])
    # For all work area...
    for i in range(0,NbZones) :
        # Plot the data set
        plt.figure()
        plt.plot(Data)
        plt.xlabel('frame')
        plt.ylabel('Cadence (Tr/min)')
        plt.suptitle('ENCADRER ZONE : '+str(i+1)+'/'+str(NbZones))
        # Let user define left/start limit
        NewLeftLim = plt.ginput(n=1)
        FrameLimite[i,0] = round(NewLeftLim[0][0])
        # Let user define right/end limit
        NewRightLim = plt.ginput(n=1)
        FrameLimite[i,1] = NewRightLim[0][0]
        # Plot limits
        plt.xlim(left=round(FrameLimite[i,0]))
        plt.xlim(right=round(FrameLimite[i,1]))
        # Close graph (need to be commented to see previous plot)
        plt.close()
    return FrameLimite 

def DetectionNbZones(Data):
    """
    USES 
    
    * Automatic method for finding number of areas to be studied.
    
    PARAMETERS
    
    * Data : Crank gyroscope (Nx1)
    
    """
    # Find peaks with 100s min distance between each
    Pics,_ = find_peaks(Data,height=(800), prominence=500, distance = 20000)
    NbZones = len(Pics)
    print("Number of areas found : " + str(NbZones))
    # Determination of apprixomative start & end of each area,
    # considering that peak appears in roughly the same place for each area
    FramesLimite=np.zeros((NbZones,2))
    for i in range(0,NbZones):
        FramesLimite[i,0]=Pics[i]-2000
        FramesLimite[i,1]=Pics[i]+7000
    # Specified limits should be in available frames
    FramesLimite[FramesLimite < 0] = 0
    FrameMax = NumberOfNonNans(Data)
    FramesLimite[FramesLimite > FrameMax] = FrameMax  
    del FrameMax  
    
    return NbZones, FramesLimite

def CalculVitesseTopTourArriere(Time,DataMagneto,MagnetSpacingDegrees,WheelCircumference):
    """
    USES 
    
    * Calculate Speed thanks to revolution counter at the rear wheel.
    
    PARAMETERS
    
    * Time : Time data of Revolution counter (Nx1)
        
    * DataMagneto : Revolution counter Data (Nx1)
        
    * MagnetSpacingDegrees : Spacement between magnets. (int)
        
    * WheelCircumference : in mm (int)
    
    """
    
    # Centering data around 0 and define approximative up and down min limits to search peaks
    Offset = np.mean(DataMagneto[0:5000])
    UpThreshold = (np.max(DataMagneto[0:5000])-np.mean(DataMagneto[0:5000]))*6
    DownThreshold = (np.mean(DataMagneto[0:5000])-np.min(DataMagneto[0:5000]))*6
    DataOffset = DataMagneto - Offset
    # Finding peaks
    FrameInitTemps = Time.index[0] 
    try :
        PeaksNeg,_ = find_peaks((DataOffset*(-1)),height=(DownThreshold,None),prominence=(DownThreshold,None),threshold=(0,None))
        PeaksPos,_ = find_peaks(DataOffset,height=(UpThreshold,None),prominence=(UpThreshold,None),threshold=(0,None))
        print("- Magnetic peaks detected.")
    except :
        print(Fore.RED + 'ERROR : Magnetic peaks could not be detected.') 
    try :
        # Group all peaks in same var
        A = PeaksNeg
        PeaksTotal = np.sort((np.append(A,PeaksPos))) 
        del A
        # Distance calculation between two magnets
        MagnetSpacingWheelRound = MagnetSpacingDegrees/360
        DisplacementWheelRound = (WheelCircumference/1000)*MagnetSpacingWheelRound
        # Data initialization
        RevolutionCounterSpeedMeterSecond = [0 for i in range(len(PeaksTotal))]
        RevolutionCounterSpeedKilometerHour = [0 for i in range(len(PeaksTotal))]
        DisplacementRevolutionCounterMeter = [0 for i in range(len(PeaksTotal))]
        Xpeaks = PeaksTotal + FrameInitTemps
        # Speed calculation
        for i in range(1,len(PeaksTotal)-1):
            DisplacementRevolutionCounterMeter[i] = (i+1) * DisplacementWheelRound
            RevolutionCounterSpeedMeterSecond[i]= (2*DisplacementWheelRound)/(Time[Xpeaks[i+1]]-Time[Xpeaks[i-1]])
        RevolutionCounterSpeedKilometerHour = [i * 3.6 for i in RevolutionCounterSpeedMeterSecond]
        print('- Speed calculation successful.')
    except :
        print(Fore.RED + "ERROR : Speed could not be calculated.")
    return Xpeaks[1:], PeaksTotal[1:], RevolutionCounterSpeedKilometerHour, DisplacementRevolutionCounterMeter, PeaksNeg, PeaksPos

def Resynchro(CranksetTime,VerificationResynchro="No"):
    """
    USES
    
    * Resynchronize data at each frame thanks to ponctual Phyling resynchronization.
    
    PARAMETERS
    
    * CranksetTime : Crankset time data.  (Nx1)
        
    * VerificationResynchro : Yes/No var to verify graphically the resynchronization. (str)
        
    """
    
    diff = np.diff(CranksetTime)
    index_diff = np.where(diff < 0)
    #Nous retourne les index du temps juste avant la resynchro (t1)
    NbResynchro = len(index_diff[0])
    
    CranksetTimeResynchro=(np.zeros(shape=[len(CranksetTime),1]))*np.nan
    if NbResynchro>0:
        for r in range(0,NbResynchro):
            
            #Calculer 1/F moyen
            if r==0 :
                FrameDepartResynchro = 0
                
            else :
                FrameDepartResynchro = (index_diff[0][r-1])+1
        
            Pmoy = np.mean(diff[FrameDepartResynchro:index_diff[0][r]])    
            #Calculer l'offset deresynchro
            OffsetTotal = CranksetTime[index_diff[0][r]]-(CranksetTime[index_diff[0][r]+1]-Pmoy)  
            
            #Appliquer l'Offset proportionnellement à la frame depuis la dernière synchro
            for t in range(FrameDepartResynchro,index_diff[0][r]+1) :
                Correction = ((CranksetTime[t]-CranksetTime[FrameDepartResynchro])*OffsetTotal)/(CranksetTime[index_diff[0][r]+1]-CranksetTime[FrameDepartResynchro])
                CranksetTimeResynchro[t]=CranksetTime[t]-Correction
                
            #Rajouter les dernières frames qui ne peuvent pas être resynchro
            if r == NbResynchro-1 :
                for t in range((index_diff[0][r])+1,NumberOfNonNans(CranksetTime)):
                    CranksetTimeResynchro[t]=CranksetTime[t]
          
        # Vérification
        if VerificationResynchro in ['Oui','oui','OUI','o','O','YES','Yes','yes','Y','y'] :
            plt.figure()
            plt.plot(CranksetTime) 
            plt.plot(CranksetTimeResynchro)
            plt.title('VERIFICATION : Resynchro')
            plt.legend(['Raw crankset time','Resynchro crankset time']) 
            plt.xlabel('Frame')
            plt.ylabel('Temps (s)') 
    elif NbResynchro == 0:
        CranksetTimeResynchro = CranksetTime
        
    return CranksetTimeResynchro

def ImuOrientation(Time,Data,VerificationImuOrientation='No'):
    
    """
    USES 
    
    * Determination of IMU orientation in Eulerian parameters thanks to Fusion algorithm (gyrometer + accelerometer).
    
    
    PARAMETERS
    
    * Time : Time associate to Data. (Nx1)

    * Data : X-Y-Z Gyro & X-Y-Z Accelero data. (Nx6)
        
    * VerificationImuOrientation : Yes/No var to verify graphically the Orientation. (str) 
 
    """
    
    #----------------------------------------------------------- Calcul Offset Gyro
        
    try :
        #Offset determination & application
        # GyroX
        FrameFinIntOffsetGyroX,_ = DetectionFrontMontant(Data['gyro_x'],Time,0,100)
        OffsetGyroX= np.mean(Data['gyro_x'][0:FrameFinIntOffsetGyroX-20])
        GyroX = Data['gyro_x'] - OffsetGyroX
        # GyroY
        FrameFinIntOffsetGyroY,_ = DetectionFrontMontant(Data['gyro_y'],Time,0,100)
        OffsetGyroY= np.mean(Data['gyro_y'][0:FrameFinIntOffsetGyroY-20])
        GyroY = Data['gyro_y'] - OffsetGyroY
        # GyroZ
        FrameFinIntOffsetGyroZ,_ = DetectionFrontMontant(Data['gyro_z'],Time,0,100)
        OffsetGyroZ= np.mean(Data['gyro_z'][0:FrameFinIntOffsetGyroZ-20])
        GyroZ = Data['gyro_z'] - OffsetGyroZ
        
        #Filtering
        GyroX = FiltrageButterworth(GyroX,200,20)
        GyroY = FiltrageButterworth(GyroY,200,20)
        GyroZ = FiltrageButterworth(GyroZ,200,20)
                
    except :
        print(Fore.RED + "ERROR : Gyroscope offset could not be calculated.")

    # =============================================================================
    # ORIENTATION CALCULATION
    # =============================================================================    

    #csv creation for data formatting   
    d = {'Time (s)':Time,'Gyroscope X (deg/s)':GyroX,'Gyroscope Y (deg/s)':GyroY,'Gyroscope Z (deg/s)':GyroZ,'Accelerometer X (g)':Data['acc_x'],'Accelerometer Y (g)':Data['acc_y'],'Accelerometer Z (g)':Data['acc_z']}
    DataIMU = pd.DataFrame(data = d)
    DataIMU.to_csv("TEMPORAIRE_DataForOrientationExtraction.csv")

    #Data extraction thanks to fusion algorithm
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


    #Changing orientation to be more comprehensive :
        # X = axe dans le sens d'avancement, rotation positive vers la droite
        # Y = axe medio-latéral, rotation positive vers le haut
        # Z = Axe antéro-postérieur, position vers la droite 
    OrientationIMU = euler*[-1,-1,1]
       
    # Tempory file supression   
    import os
    os.remove("TEMPORAIRE_DataForOrientationExtraction.csv") 

    if VerificationImuOrientation in ['OUI','Oui','oui','O','o','YES','Yes','yes','Y','y']:
        plt.figure()
        plt.plot(OrientationIMU[:,0]) 
        plt.plot(OrientationIMU[:,1])
        plt.plot(OrientationIMU[:,2])
        plt.grid()
        plt.legend(["Autour de x","Autour de y","Autour de Z"])  
        plt.xlabel("Frame") 
        plt.ylabel("Angle (°)") 
        plt.title('VERIFICATION : Orientation IMU')
        
    return OrientationIMU