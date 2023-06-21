"""
@author: arnaultcamille@univ-poitiers.fr
"""

from FunctionsCalculation import * #DecoupageZonesActives,CalculVitesseTopTourArriere,Resynchro,ImuOrientation
from sklearn.linear_model import LinearRegression
from datetime import datetime

def Calculation(DecodedFile,CirconferenceRoue=1591.67,Braquet=44/16,LongueurManivelle=177.5,AngleCadre=6,EspacementAimant=90,VerificationResynchro="No",VerificationCrankPeaks='No',VerificationRevolutionCounterPeaks='No',VerificationRevolutionCounterSpeed='No',VerificationImuOrientation = "No"):
    
    print("----------> READING DATA...")
    
    # Get decoded data
    Raw = pd.read_csv(DecodedFile)
    print("Reading OK")
    
    # MiniPhyling-MaxiPhyling resynchronization
    Raw["temps_pedalier"] = Resynchro(Raw["temps_pedalier"],VerificationResynchro=VerificationResynchro)
    print("Resynchronisation OK")
    
    # Extract data for each sensor
    try :        
        DataPedalier = Raw[["temps_pedalier","gyro_pedalier","force_d","force_g","magneto_pedalier"]]
        DataPedalier = DataPedalier[0:NumberOfNonNans(Raw['temps_pedalier'])]
        print('Pedalier data extraction OK')
    except : 
        print(Fore.RED + "No pedalier data found.")
    try :
        DataImu = Raw[["temps_imu","acc_x","acc_y","acc_z","gyro_x","gyro_y","gyro_z"]]
        DataImu = DataImu[0:NumberOfNonNans(Raw['temps_imu'])]
        print('IMU data extraction OK')
    except :
        print(Fore.RED + "No IMU data found.")
    try :    
        DataTopTour = Raw[["temps_toptour","magneto_toptour"]]
        print('Top tour data extraction OK')
    except : 
        print(Fore.RED + "No top tour data found.")
    try :
        DataGps = Raw[["temps_gps","timestamp_gps","longitude","latitude","vitesse_gps"]]
        DataGps = DataGps[0:NumberOfNonNans(Raw['temps_gps'])]   
        print('GPS data extraction OK')     
    except :
        print(Fore.RED + "No GPS data found.")                   

    print("----------> DELIMITATION OF WORKING SPACE...")
    
    #Detection NbZones
    NbZones,FramesLimite = DetectionNbZones(Raw['gyro_pedalier'])    
    
    #Activate it in case of bad zones detection
    # UserInput :
    # NbZones = 1 
    # Code :
    # FramesLimite = DecoupageZonesActives(Raw['gyro_pedalier'],NbZones)
    # FramesLimite[FramesLimite < 0] = 20
    
    
    #Create var for each area
    ZoneList=[0 for i in range(NbZones)]
    for zone in range(1,NbZones+1):
        num = str(zone)
        ZoneList[zone-1]='Zone'+num 
    
    print("----------> CALCULATION FOR EACH AREA...")
    
    for zone in range(0,NbZones):
        print("==========")
        print("AREA "+str(zone+1))
        print("==========")
        
        #%%
        print("Resample Data...")
        
        #Specify Frequency we want to use for resample
        FreqAcq = 200
        
        #Extract data sensors with limits defined before (needs to be rounded because of the ginput) 
        #Pedalier
        try :
            DataPedalierCrop = DataPedalier[list(DataPedalier)][round(FramesLimite[zone,0]):round(FramesLimite[zone,1])]
            #IMU (5 values around because of the initial record delay of MaxiPhyling comparing to MiniPhyling)
            IndexInitIMU = IndexNearestValue(DataImu["temps_imu"],Raw["temps_pedalier"][round(FramesLimite[zone,0])])
            IndexEndIMU = IndexNearestValue(DataImu["temps_imu"],Raw["temps_pedalier"][round(FramesLimite[zone,1])])
            if IndexInitIMU < 5 :
                DataImuCrop = DataImu[list(DataImu)][0:IndexEndIMU+5]
            else :
                DataImuCrop = DataImu[list(DataImu)][IndexInitIMU-5:IndexEndIMU+5]
        except :
            print('ERROR : IMU resample prep failed.')
            
        #GPS (5 values around because of the initial record delay of MaxiPhyling comparing to MiniPhyling)
        try :
            IndexInitGPS = IndexNearestValue(DataGps["temps_gps"],Raw["temps_pedalier"][round(FramesLimite[zone,0])])
            IndexEndGPS = IndexNearestValue(DataGps["temps_gps"], Raw["temps_pedalier"][round(FramesLimite[zone,1])])
            if IndexInitGPS < 5 :
                DataGpsCrop = DataGps[list(DataGps)][0:IndexEndGPS+5]
            else :
                DataGpsCrop = DataGps[list(DataGps)][IndexInitGPS-5:IndexEndGPS+5]
        except :
            print('ERROR : GPS resample prep failed.')
        #Top Tour (5 values around because of the initial record delay of MaxiPhyling comparing to MiniPhyling)
        try :
            IndexInitTT = IndexNearestValue(DataTopTour["temps_toptour"],Raw["temps_pedalier"][round(FramesLimite[zone,0])])
            IndexEndTT = IndexNearestValue(DataTopTour["temps_toptour"], Raw["temps_pedalier"][round(FramesLimite[zone,1])])
            if IndexInitTT < 5 :
                DataTopTourCrop = DataTopTour[list(DataTopTour)][0:IndexEndTT+5]
            else :
                DataTopTourCrop = DataTopTour[list(DataTopTour)][IndexInitTT-5:IndexEndTT+5]
        except :
            print('ERROR : Revolution counter resample prep failed.')
        #Create new time base according to MinPhyling Time (longer than MaxiPhyling Time)
        try : 
            #Get time limits
            TimeInit = DataPedalier["temps_pedalier"][round(FramesLimite[zone,0])]
            TimeEnd = DataPedalier["temps_pedalier"][round(FramesLimite[zone,1])]
            #Create time axis with controled frequency
            x = np.arange(TimeInit,TimeEnd+(1/FreqAcq),(1/FreqAcq),dtype=float)
            print('- MiniPhyling time based.')
        except :
            print(Fore.RED + "ERROR : Creation time base failed.")
            
        #Resample Pedalier data according to the new base time with CubicSpline   
        try : 
            gyro_pedalier_resample=InterpolationResample(DataPedalierCrop['temps_pedalier'],x,DataPedalierCrop['gyro_pedalier']) 
            force_g_resample=InterpolationResample(DataPedalierCrop['temps_pedalier'],x,DataPedalierCrop['force_g'])
            force_d_resample=InterpolationResample(DataPedalierCrop['temps_pedalier'],x,DataPedalierCrop['force_d'])
            magneto_resample=InterpolationResample(DataPedalierCrop['temps_pedalier'],x,DataPedalierCrop['magneto_pedalier']) #MAGNETO POUR LES ANCIENS ESSAIS
            print("- Crankset data resample.")
        except :
            print(Fore.RED + "ERROR : Crankset data resample failed.")
        
        #Resample IMU Data according to the new base time with CubicSpline    
        try : 
            acc_x_resample=InterpolationResample(DataImuCrop['temps_imu'],x,DataImuCrop['acc_x']) 
            acc_y_resample=InterpolationResample(DataImuCrop['temps_imu'],x,DataImuCrop['acc_y'])
            acc_z_resample=InterpolationResample(DataImuCrop['temps_imu'],x,DataImuCrop['acc_z'])
            gyro_x_resample=InterpolationResample(DataImuCrop['temps_imu'],x,DataImuCrop['gyro_x'])
            gyro_y_resample=InterpolationResample(DataImuCrop['temps_imu'],x,DataImuCrop['gyro_y'])
            gyro_z_resample=InterpolationResample(DataImuCrop['temps_imu'],x,DataImuCrop['gyro_z'])
            print("- IMU data resample.")
        except :
            print(Fore.RED + "ERROR : IMU data resample failed.")    
        
        #Resample GPS Data according to the new base time with Linear Regression  
        try : 
            #Linear Regression Model Creation
            x_model = np.array(DataGps['temps_gps']).reshape((-1, 1))
            y_model = np.array(DataGps['timestamp_gps'])
            model = LinearRegression().fit(x_model,y_model)
            RcarreRegressionTimestamp = model.score(x_model,y_model)
            OrdonneeOrigineTimestamp = model.intercept_
            PenteTimestamp = model.coef_
            #Data prediction
            temps_gps_resample = x
            timestamp_gps_resample = model.predict(np.array(temps_gps_resample).reshape(-1, 1))
            dt_object = [0 for i in range(0,len(timestamp_gps_resample))]
            #Convert timestamp type to date & time type
            for timestamp in range(0,len(timestamp_gps_resample)):
                dt_object[timestamp] = datetime.fromtimestamp(timestamp_gps_resample[timestamp])
            print("- GPS data resample.")
        except :
            print(Fore.RED + "ERROR : GPS data resample failed.")
        
        #Data Pedalier & IMU Storage in Dataframe
        locals()[ZoneList[zone]] = {}
        try :               
            locals()[ZoneList[zone]]['RawData'] = {}
            locals()[ZoneList[zone]]['RawData'] = pd.DataFrame(data = {'time':x,'gyro_pedalier':gyro_pedalier_resample,'force_g':force_g_resample,'force_d':force_d_resample,'magneto':magneto_resample,'acc_x':acc_x_resample,'acc_y':acc_y_resample,'acc_z':acc_z_resample,'gyro_x':gyro_x_resample,'gyro_y':gyro_y_resample,'gyro_z':gyro_z_resample})
            del gyro_pedalier_resample, force_g_resample, force_d_resample, magneto_resample, acc_x_resample, acc_y_resample, acc_z_resample, gyro_x_resample, gyro_y_resample, gyro_z_resample
            print("- Resampled crankset data stored.")
        except :
            print(Fore.RED + "ERROR : Crankset resampled data could not be stored.")
            
        #Data GPS Storage in DataFrame
        try :
            locals()[ZoneList[zone]]['DataGPS'] = {}
            locals()[ZoneList[zone]]['DataGPS'] = pd.DataFrame(data = {'TimestampGPS':timestamp_gps_resample,'DateTimeGPS':dt_object})
            print("- Resampled GPS data stored.")
        except :
            print(Fore.RED + "ERROR : GPS resampled data could not be stored.")
            
        #%%    
        print("-----------------------------")
        print("Crankset data calculation...")

        try:
            #Butterworth filter of 20Hz cut off
            ForceGaucheFiltree = FiltrageButterworth(locals()[ZoneList[zone]]['RawData']['force_g'],FreqAcq,20)
            ForceDroiteFiltree = FiltrageButterworth(locals()[ZoneList[zone]]['RawData']['force_d'],FreqAcq,20)
            GyroPedalierFiltre = FiltrageButterworth(locals()[ZoneList[zone]]['RawData']['gyro_pedalier'],FreqAcq,20)
            print("- Crankset data filtered.")
        except:
            print(Fore.RED + "ERROR : Crankset data could not be filtered.")
            
        try :
            # Calculer la cadence, la vitesse et la distance
            CadenceTrMin = GyroPedalierFiltre*(60/360)
            Developpement = (CirconferenceRoue/1000)*Braquet #m/tr
            VitessePedalier = CadenceTrMin * Developpement * (60/1000) #km/h
            DistancePedalier = VitessePedalier*((1/FreqAcq)/3600)*1000 #m
            # Calculer la Force, le Couple et la Puissance
            ForceTotale = ForceGaucheFiltree + ForceDroiteFiltree
            ForceTotaleAbsolue = abs(ForceGaucheFiltree) + abs(ForceDroiteFiltree)
            CoupleGauche = ForceGaucheFiltree * (LongueurManivelle/1000)
            CoupleDroite = ForceDroiteFiltree * (LongueurManivelle/1000)
            CoupleTotal = CoupleGauche + CoupleDroite
            PuissanceGauche = CoupleGauche * np.radians(GyroPedalierFiltre)
            PuissanceDroite = CoupleDroite * np.radians(GyroPedalierFiltre)
            PuissanceTotale = PuissanceGauche + PuissanceDroite
            # Calculer l'Impulsion et le Travail
            ImpulsionGauche = IntegrationTrapeze(ForceGaucheFiltree,FreqAcq)
            ImpulsionDroite = IntegrationTrapeze(ForceDroiteFiltree,FreqAcq)
            Impulsion = IntegrationTrapeze(ForceTotale,FreqAcq)
            TravailGauche = IntegrationTrapeze(PuissanceGauche,FreqAcq)
            TravailDroite = IntegrationTrapeze(PuissanceDroite,FreqAcq)
            Travail = IntegrationTrapeze(PuissanceTotale,FreqAcq)
            print("- Forces calculation successful.")
        except : 
            print(Fore.RED + "ERROR : Forces could not be calculated.")
            
        #Angular displacement calculation
        try :
            DeplacementAngulairePedalier = IntegrationTrapeze(GyroPedalierFiltre,FreqAcq)
            print("- Crank calculation successful.")
        except :
            print(Fore.RED + "ERROR : Crank displacement could not be calculated.")
        #Magneto data filtering & magneto pedalier peaks detection
        try :
            DataMagnetoPedalierFiltrees = FiltrageButterworth(DataPedalierCrop['magneto_pedalier'],200,50)
            MagnetoPeaks,_ = find_peaks(DataMagnetoPedalierFiltrees,height=(10000,None),prominence=(500,None)) 
            if VerificationCrankPeaks in ['Oui','oui','OUI','o','O','YES','Yes','yes','Y','y'] :
                plt.figure()
                plt.plot(MagnetoPeaks,DataMagnetoPedalierFiltrees[MagnetoPeaks],'x')
                plt.plot(DataMagnetoPedalierFiltrees)            
            print("- Crank magnetic peaks detected.")
        except :
            print(Fore.RED + "ERROR : Crank magnetic peaks could not be detected.")

        try : 
            #Angular correction
            AngleReel = 270-AngleCadre
            SommeDeplacementAngulairePedalier = np.cumsum(DeplacementAngulairePedalier)
            SommeDeplacementAngulairePedalierCorrige=[0 for i in range(0,len(SommeDeplacementAngulairePedalier))]
                                                                       
            for i in range(0,len(MagnetoPeaks)+1):
                if i==0 :
                    offset = AngleReel-SommeDeplacementAngulairePedalier[MagnetoPeaks[i]]
                    for j in range(0,MagnetoPeaks[0]+1):
                        SommeDeplacementAngulairePedalierCorrige[j]=SommeDeplacementAngulairePedalier[j]+offset
                if i==len(MagnetoPeaks) :
                    OffsetContinu = (360*(i-1)+AngleReel)-SommeDeplacementAngulairePedalier[MagnetoPeaks[i-1]]
                    for j in range(MagnetoPeaks[i-1],len(SommeDeplacementAngulairePedalier)):
                        SommeDeplacementAngulairePedalierCorrige[j]=SommeDeplacementAngulairePedalier[j]+OffsetContinu
                else :
                    OffsetContinu = (360*(i-1)+AngleReel)-SommeDeplacementAngulairePedalier[MagnetoPeaks[i-1]]
                    for j in range(MagnetoPeaks[i-1],MagnetoPeaks[i]+1):
                        SommeDeplacementAngulairePedalierCorrige[j]=SommeDeplacementAngulairePedalier[j]+OffsetContinu
                    
                    OffsetVariable = (360*i+AngleReel)-SommeDeplacementAngulairePedalierCorrige[MagnetoPeaks[i]]
                    LongueurApplicationOffset = MagnetoPeaks[i]-MagnetoPeaks[i-1]
                    Inc = 0
                    for j in range(MagnetoPeaks[i-1],MagnetoPeaks[i]+1):
                        Coef = (OffsetVariable/LongueurApplicationOffset)*Inc
                        SommeDeplacementAngulairePedalierCorrige[j]=SommeDeplacementAngulairePedalierCorrige[j]+Coef
                        Inc = Inc+1              
                
                #Modulo 360
                AngleManivelleGauche = [0 for i in range(0,len(SommeDeplacementAngulairePedalierCorrige))]
                AngleManivelleDroite = [0 for i in range(0,len(SommeDeplacementAngulairePedalierCorrige))]
                for j in range(0,len(SommeDeplacementAngulairePedalierCorrige)):
                    AngleManivelleGauche[j]=SommeDeplacementAngulairePedalierCorrige[j]%360
                    AngleManivelleDroite[j]=(SommeDeplacementAngulairePedalierCorrige[j]-180)%360
        except :
            print(Fore.RED + "ERROR : Total crank displacement could not be calculated.")
        #Data Storage in Dataframe
        try :
            locals()[ZoneList[zone]]['DataPedalier'] = {}
            locals()[ZoneList[zone]]['DataPedalier'] = pd.DataFrame(data = {'time':x,'CadenceTrMin':CadenceTrMin,'VitessePedalier':VitessePedalier,'DistancePedalier':DistancePedalier,
                                                                            'PositionManivelleGauche':AngleManivelleGauche,'PositionManivelleDroite':AngleManivelleDroite,
                                                                            'ForceGauche':ForceGaucheFiltree,'ForceDroite':ForceDroiteFiltree,'ForceTotale':ForceTotale,'ForceTotaleAbsolue':ForceTotaleAbsolue,
                                                                            'CoupleGauche':CoupleGauche,'CoupleDroite':CoupleDroite,'CoupleTotal':CoupleTotal,
                                                                            'PuissanceGauche':PuissanceGauche,'PuissanceDroite':PuissanceDroite,'PuissanceTotale':PuissanceTotale,
                                                                            'ImpulsionGauche':ImpulsionGauche.flatten(),'ImpulsionDroite':ImpulsionDroite.flatten(),'ImpulsionTotale':Impulsion.flatten(),
                                                                            'TravailGauche':TravailGauche.flatten(),'TravailDroite':TravailDroite.flatten(),'TravailTotal':Travail.flatten()})
            print("- Crankset calculated data stored.")
        except :
            print(Fore.RED + "ERROR : Crankset calculated data could not be stored.")

        #%%
        print("--------------------------------------")
        print("Revolution counter data calculation...")
        try :
            # Filtering
            DataMagnetoFiltrees = FiltrageButterworth(DataTopTourCrop['magneto_toptour'],800,50)
            
            # Magnetic peaks detection & Velocity calculation
            XVitesseTopTour, XDistanceTopTour, VitesseTopTour, DistanceTopTourM, PeaksNeg, PeaksPos = CalculVitesseTopTourArriere(DataTopTourCrop['temps_toptour'],DataMagnetoFiltrees,EspacementAimant,CirconferenceRoue)
            # Verification of Magnetic peaks detection
            if VerificationRevolutionCounterPeaks in ['Oui','oui','OUI','o','O','YES','Yes','yes','Y','y'] :
                plt.figure()
                plt.plot(DataMagnetoFiltrees)
                plt.plot(PeaksPos,DataMagnetoFiltrees[PeaksPos],'x')
                plt.plot(PeaksNeg,DataMagnetoFiltrees[PeaksNeg],'x')
                plt.grid()
            
            #Top Tour Velocity Resample
            # Create time data before first velocity calculated (because of the spacement between magnet, velocity is not calculated at specific frequency as other mesurement could.)          
            ttoptour = DataTopTourCrop['temps_toptour'][XVitesseTopTour][DataTopTourCrop['temps_toptour'][XVitesseTopTour].index[0]]
            LongueurIntervalle1 = IndexNearestValue(x,ttoptour)
            if x[LongueurIntervalle1]>ttoptour:
                LongueurIntervalle1 = LongueurIntervalle1 -1  
            IntervalleZeros1 = pd.Series([0 for i in range(0,LongueurIntervalle1)])
            IntervalleTemps1 = pd.Series([x[0]+(1/FreqAcq)*i for i in range(0,LongueurIntervalle1)])
            # Create time data after last velocity calculated
            ttoptour = DataTopTourCrop['temps_toptour'][XVitesseTopTour][DataTopTourCrop['temps_toptour'][XVitesseTopTour].index[len(DataTopTourCrop['temps_toptour'][XVitesseTopTour])-1]]
            LongueurIntervalle2 = IndexNearestValue(x,ttoptour)
            if x[LongueurIntervalle2]<ttoptour:
                LongueurIntervalle2 = LongueurIntervalle2 +1 
            IntervalleZeros2 = pd.Series([0 for i in range(0,len(x)-LongueurIntervalle2)])
            IntervalleTemps2 = pd.Series([x[LongueurIntervalle2]+(1/FreqAcq)*i for i in range(0,len(x)-LongueurIntervalle2+1)])
            IntervalleDistance2 = pd.Series([DistanceTopTourM[len(DistanceTopTourM)-1] for i in range(0,len(x)-LongueurIntervalle2)])
            # Intervalle1 + Données TopTour + Intervalle2
            NewTempsTopTour = pd.concat([IntervalleTemps1, DataTopTourCrop['temps_toptour'][XVitesseTopTour],IntervalleTemps2], ignore_index=True)
            NewVitesseTopTour = pd.concat([IntervalleZeros1, pd.Series(VitesseTopTour),IntervalleZeros2], ignore_index=True)
            NewDistanceTopTour = pd.concat([IntervalleZeros1, pd.Series(DistanceTopTourM),IntervalleDistance2], ignore_index=True)
        except :
            print('ERROR : Revolution counter resize prep failed.')
        # Linear interpolation between each point
        try : 
            vitesse_toptour_resample=np.interp(x,NewTempsTopTour,NewVitesseTopTour) 
            distance_toptour_resample=np.interp(x,NewTempsTopTour,NewDistanceTopTour) 
            print("- Revolution counter data resampled.")
        except :
            print(Fore.RED + "ERROR : Revolution counter data could not be resample.")
            
        try :    
            #Filtring
            vitesse_toptour_resample = FiltrageButterworth(vitesse_toptour_resample,FreqAcq,20)
            # Comparison between TopTour & Pedalier Velocity
            if VerificationRevolutionCounterSpeed in ['Oui','oui','OUI','o','O','YES','Yes','yes','Y','y'] :
                plt.figure()
                plt.title('Comparaison vitesse Top Tour/Pédalier : Zone '+str(zone+1))
                plt.plot(x,VitessePedalier)
                plt.plot(NewTempsTopTour,NewVitesseTopTour)
                plt.plot(x,vitesse_toptour_resample) 
                plt.grid()
                plt.legend(['VitessePedalier','Vitesse Top Tour Initiale','Vitesse Top Tour Interpolée'])
        except :
            print('ERROR : Revolution counter resample prep failed.')
        #DataStorage in DataFrame
        try :
            locals()[ZoneList[zone]]['DataTopTour'] = {}
            locals()[ZoneList[zone]]['DataTopTour'] = pd.DataFrame(data = {'VitesseTopTour':vitesse_toptour_resample,'DistanceTopTour':distance_toptour_resample})
            print("- Revolution counter calculated data stored.")
        except :
            print(Fore.RED + "ERROR : Revolution counter calculated data could not be stored.")

        
        #%%
        print("-----------------------")
        print("IMU data calculation...")
        
        try :
            BmxOrientation = ImuOrientation(locals()[ZoneList[zone]]['DataPedalier']['time'],locals()[ZoneList[zone]]['RawData'].iloc[:,len(locals()[ZoneList[zone]]['RawData'].columns)-6:len(locals()[ZoneList[zone]]['RawData'].columns)],VerificationImuOrientation=VerificationImuOrientation)
            locals()[ZoneList[zone]]['DataIMU'] = {}
            locals()[ZoneList[zone]]['DataIMU'] = pd.DataFrame(data = {'GyroX':locals()[ZoneList[zone]]['RawData']['gyro_x'],'GyroY':locals()[ZoneList[zone]]['RawData']['gyro_y'],'GyroZ':locals()[ZoneList[zone]]['RawData']['gyro_z'],
                                                                       'AccX':locals()[ZoneList[zone]]['RawData']['acc_x'],'AccY':locals()[ZoneList[zone]]['RawData']['acc_y'],'AccZ':locals()[ZoneList[zone]]['RawData']['acc_z'],
                                                                       'Roulis':BmxOrientation[:,0],'Tangage':BmxOrientation[:,1],'Lacet':BmxOrientation[:,2]})
            print('- Orientation calculation successful.')
        except :
            print(Fore.RED + "ERROR : IMU Orientation calculation failed.")
        

        
    #%% ===========================================================================
    # EXPORT DES DONNEES AU FORMAT CSV
    # =============================================================================
    print("------------------------------")   
    for zone in range(0,NbZones):
        try :
            all_data = pd.concat([locals()[ZoneList[zone]]['DataPedalier'], locals()[ZoneList[zone]]['DataTopTour'],locals()[ZoneList[zone]]['DataGPS'],locals()[ZoneList[zone]]['DataIMU']],axis=1,sort=False)
            all_data.to_csv(DecodedFile[:len(DecodedFile)-4] + '_' + ZoneList[zone] + '.csv',index=False)
            print("EXTRACTION CSV ZONE " + str(zone+1) + " REUSSIE.")    
        except :
            try :
                all_data = pd.concat([locals()[ZoneList[zone]]['DataPedalier'], locals()[ZoneList[zone]]['DataTopTour'],locals()[ZoneList[zone]]['DataIMU']],axis=1,sort=False)
                all_data.to_csv(DecodedFile[:len(DecodedFile)-4] + '_' + ZoneList[zone] + '.csv',index=False)
                print("EXTRACTION CSV ZONE " + str(zone+1) + " REUSSIE.")  
                print("(Missing GPS Data.)")
            except :
                try :
                    all_data = pd.concat([locals()[ZoneList[zone]]['DataPedalier'], locals()[ZoneList[zone]]['DataGPS'],locals()[ZoneList[zone]]['DataIMU']],axis=1,sort=False)
                    all_data.to_csv(DecodedFile[:len(DecodedFile)-4] + '_' + ZoneList[zone] + '.csv',index=False)
                    print("EXTRACTION CSV ZONE " + str(zone+1) + " REUSSIE.")    
                    print("(Missing Revolution counter Data.)")
                except :
                    try :
                        all_data = pd.concat([locals()[ZoneList[zone]]['DataTopTour'], locals()[ZoneList[zone]]['DataGPS'],locals()[ZoneList[zone]]['DataIMU']],axis=1,sort=False)
                        all_data.to_csv(DecodedFile[:len(DecodedFile)-4] + '_' + ZoneList[zone] + '.csv',index=False)
                        print("EXTRACTION CSV ZONE " + str(zone+1) + " REUSSIE.")
                        print("(Missing Crankset Data.)")                         
                    except :
                        try :
                            all_data = pd.concat([locals()[ZoneList[zone]]['DataPedalier'], locals()[ZoneList[zone]]['DataTopTour'],locals()[ZoneList[zone]]['DataGPS']],axis=1,sort=False)
                            all_data.to_csv(DecodedFile[:len(DecodedFile)-4] + '_' + ZoneList[zone] + '.csv',index=False)
                            print("EXTRACTION CSV ZONE " + str(zone+1) + " REUSSIE.")
                            print("(Missing IMU Data.)")   
                        except:
                            try :
                                all_data = pd.concat([locals()[ZoneList[zone]]['DataPedalier']],axis=1,sort=False)
                                all_data.to_csv(DecodedFile[:len(DecodedFile)-4] + '_' + ZoneList[zone] + '.csv',index=False)
                                print("EXTRACTION CSV ZONE " + str(zone+1) + " REUSSIE.") 
                                print("(Missing GPS & Top Tour Data.)")
                            except :
                                print ('Missing 2 or more sensors : csv writing failed. ')
        
            
    return NbZones            
            
            
            
            