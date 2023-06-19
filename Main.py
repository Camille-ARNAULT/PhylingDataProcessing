# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 11:39:07 2023

@author: admin
"""

#%% EXTRACTION DES DONNEES BRUTES

from PhylingDecoderExtractor import PhylingDecoder
from StandardFunctions import *

Path = "C:\\Users\\carnau22\\Documents\\BMX\\Datas\\202305_Glasgow\\2023_05_17_AM\\"
RawFileName = "phyling_120_59_20230517_090706"

PhylingDecoder(Path,RawFileName=RawFileName)

#%% EXTRACTION DES DONNEES TRAITEES

from DataHarmonization import DataHarmonization

# SeuilTopTour = 2015
# IntensitePos = 20
# IntensiteNeg = 23

DataHarmonization(Path+RawFileName+'.csv',NbZones=4,
                  CirconferenceRoue=1591.67,Braquet=50/18,LongueurManivelle=177.5,AngleCadre=6,
                  FreqAcq=200,
                  OffsetCalibrationFG=-2750,OffsetCalibrationFD=-3540,
                  SeuilTopTour=1.627,IntensitePos=0.015,IntensiteNeg=0.02,EspacementAimant=90)

#%% EXPLOITATION DES DONNEES TRAITEES

from DataVisualization import *
from StandardFunctions import *

ZoneList=['' for i in range(0,NbZones)]
Legend=['' for i in range(0,NbZones)]
for i in range(0,NbZones) :
    ZoneList[i]= RawFileName + '_Zone' + str(i+1) + '.csv'
    Legend[i] = 'Départ ' + str(i+1)
    

for zone in range(0,len(ZoneList)):
    print('----------')
    print('Area '+str(zone))
    print('----------')
    #Data importation
    Data = pd.read_csv(Path+ZoneList[zone])
    
    # Start parameters calculation
    FrameInit,FrameEnd,IndexCP,ImpulsionDCP,TravailDCP,AngleManivelleReculMax,AngleTotalRecul = DataVisualizationStart(Data)
    # Storage
    locals()["Zone"+str(zone+1)] = {}
    locals()["Zone"+str(zone+1)]['Data'] = Data
    locals()["Zone"+str(zone+1)]['FrameInit'] = FrameInit
    locals()["Zone"+str(zone+1)]['FrameEnd'] = FrameEnd
    locals()["Zone"+str(zone+1)]['Temps'] = np.arange(0,(locals()["Zone"+str(zone+1)]['FrameEnd']-locals()["Zone"+str(zone+1)]['FrameInit'])*0.005,0.005)
    locals()["Zone"+str(zone+1)]['IndexCP'] = IndexCP
    locals()["Zone"+str(zone+1)]['ImpulsionDCP'] = ImpulsionDCP
    locals()["Zone"+str(zone+1)]['TravailDCP'] = TravailDCP
    locals()["Zone"+str(zone+1)]['AngleManivelleReculMax'] = AngleManivelleReculMax
    locals()["Zone"+str(zone+1)]['AngleTotalRecul'] = AngleTotalRecul
    
    # Time end start calculation
    TempsBasButte = DataVisualizationEndOfDeparture(Data,FrameInit)
    # Storage
    locals()["Zone"+str(zone+1)]['TempsBasButte'] = TempsBasButte
    
    # Time first jump
    TempsDecollage, VitesseDecollage, StdVitesseDecollage = DataVisualizationFirstJump(Data,FrameInit)
    locals()["Zone"+str(zone+1)]['TempsDecollage'] = TempsDecollage
    locals()["Zone"+str(zone+1)]['VitesseDecollage'] = VitesseDecollage
    locals()["Zone"+str(zone+1)]['StdVitesseDecollage'] = StdVitesseDecollage 
    
        
#%% Comparaison de la cadence 

#Définition des couleurs pour les graph
RougeClair = "#FF0000"
RougeFonce = "#8C0001"
BleuClair = "#5790C1" 
BleuFonce = "#0C1365"

CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,"#FF000000",BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]
# CouleurFonctionTypeDepart = [RougeFonce,RougeFonce,BleuFonce,BleuFonce,RougeClair]

# plt.figure()
plt.grid()
plt.title('Superposition des cadences')
plt.xlabel('Temps (s)')
plt.ylabel('Cadence (Tr/min)')
for zone in range(0,NbZones):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:2200]
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['CadenceTrMin'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+2200]*10,color=CouleurFonctionTypeDepart[zone]) #,color=CouleurFonctionTypeDepart[zone]
plt.legend(Legend)  

#%% Comparaison des distances


plt.figure()
plt.grid()
plt.title('Superposition des distances')
plt.xlabel('Temps (s)')
plt.ylabel('Distance (m)')
for zone in range(0,NbZones):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:1200]
    # plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['DistanceTopTour'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200]-locals()["Zone"+str(zone+1)]['Data']['DistanceTopTour'][locals()["Zone"+str(zone+1)]['FrameInit']],color=CouleurFonctionTypeDepart[zone])
    plt.plot(x,np.cumsum(locals()["Zone"+str(zone+1)]['Data']['DistancePedalier'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200]),color=CouleurFonctionTypeDepart[zone])

#%% Comparaison de la Puissance Totale

plt.figure()
plt.grid()
plt.title('Superposition des puissances totales')
plt.xlabel('Temps (s)')
plt.ylabel('Puissance Totale (W)')

CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,RougeClair,BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]

for zone in range(0,NbZones):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:800]
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['PuissanceTotale'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+800],color=CouleurFonctionTypeDepart[zone])   
plt.legend(Legend)


#%% Comparaison de la vitesse

CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,RougeClair,BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]
CouleurFatigue = ["#C00000","#BF101C","#BC1F35","#B82D4D","#B23962","#AB4475","#A34F87","#995796","#8E5FA4","#FF000000","#746BB8","#656FBE","#5571C2","#4472C4"]   

    
plt.figure()
plt.grid()
plt.title('Superposition des vitesses')
plt.xlabel('Temps (s)')
plt.xlabel('Vitesse (km/h)')
for zone in range(0,NbZones):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:1200]
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['VitesseTopTour'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200],color=CouleurFatigue[zone]) 
plt.legend(Legend)


       
#%% Comparaison de la force Totale Absolue
plt.figure()
plt.grid()
plt.title('Superposition des forces totales absolues cumulées')
plt.xlabel('Temps (s)')
plt.ylabel('Force totale absolue cumulée (N)')
for zone in range(0,NbZones):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:500]
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['ForceTotaleAbsolue'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+500],color=CouleurFonctionTypeDepartSansFatigue[zone]) 
# plt.legend(Legend)  

#%%Comparaison force Gauche/Droite
plt.figure()
plt.grid()
plt.title('Superposition des forces totales absolues')
plt.xlabel('Temps (s)')
plt.ylabel('Force totale absolue (N)')
for zone in range(0,9):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:2200]
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['ForceGauche'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+2200],color=RougeClair) 
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['ForceDroite'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+2200],color=BleuClair) 
# plt.legend(Legend)  
       
#%% Comparaison du travail total

CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,RougeClair,BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]

plt.figure()
plt.grid()
plt.title('Superposition des travaux totaux')
plt.xlabel('Temps (s)')
plt.ylabel('Travail Total (J)')
for zone in range(0,len(ZoneList)):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:1200]
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['TravailTotal'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200],color = CouleurFonctionTypeDepart[zone]) 
plt.legend(Legend)    


#%% Comparaison du travail cumulé


CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,"#FF000000",BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]
CouleurFonctionTypeDepartSansFatigue = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,"#FF000000","#FF000000","#FF000000","#FF000000","#FF000000","#FF000000","#FF000000","#FF000000"]
# CouleurFonctionTypeDepart = [RougeFonce,RougeFonce,BleuFonce,BleuFonce,RougeClair]
CouleurFatigue = ["#EAEAEA","#CFCFCF","#C0C0C0","#AFAFAF","#A2A2A2","#939393","#868686","#747474","#606060","#454545","#333333","#1E1E1E","#131313","#000000"]   

plt.figure()
plt.grid()
plt.title('Superposition des travaux totaux cumulés')
plt.xlabel('Temps (s)')
plt.ylabel('Travail Total Cumulé (J)')
for zone in range(0,NbZones):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:1200]
    plt.plot(x,np.cumsum(locals()["Zone"+str(zone+1)]['Data']['TravailTotal'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200]),color=CouleurFonctionTypeDepartSansFatigue[zone]) #,color=CouleurFonctionTypeDepart[zone]
# plt.legend(Legend)    

#%% Travail par coup de pédale

# V1 : un histogramme par coup de pédale
fig, axs = plt.subplots(nrows=8, ncols=1)
for CP in range(0,8):
    axs[CP].set_title("Coup de pédale"+str(CP+1))
    axs[CP].set_xlabel("Départs")
    axs[CP].set_ylabel("Travail (J)")
    for zone in range(0,NbZones):
        axs[CP].grid()
        axs[CP].bar(zone,locals()["Zone"+str(zone+1)]['TravailDCP'][CP],color=CouleurFonctionTypeDepart[zone]) 

#V2 : Un seul histogramme avec travail par CP empilé pour chaque départ
for CP in range(0,8):
    locals()["CoupPedale"+str(CP+1)]=[0 for i in range(0,NbZones)]
    for zone in range(0,NbZones):
        locals()["CoupPedale"+str(CP+1)][zone]=locals()["Zone"+str(zone+1)]['TravailDCP'][CP]

ListeDeparts = ['Départ '+str(i+1) for i in range(0,NbZones)]
Departs = ListeDeparts
CoupsPedale = {
    "CP1": np.array(CoupPedale1),
    "CP2": np.array(CoupPedale2),
    "CP3": np.array(CoupPedale3),
    "CP4": np.array(CoupPedale4),
    "CP5": np.array(CoupPedale5),
    "CP6": np.array(CoupPedale6),
    "CP7": np.array(CoupPedale7),
    "CP8": np.array(CoupPedale8)
}
fig, ax = plt.subplots()
bottom = np.zeros(NbZones)
a=0
for boolean, CoupsPedale in CoupsPedale.items():
    a=a+1
    for i in range(0,len(Departs)):
        p = ax.bar(Departs[i], CoupsPedale, width=0.5, label=boolean, bottom=bottom, color=df.loc[int(boolean[2])-1,a])
    bottom += CoupsPedale
ax.set_title("Number of penguins with above average body mass")
ax.legend(loc="upper right")
plt.show()

CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,RougeClair,BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]
CouleurBarre = ["#D92F2F","#EF8F25","#FFC000","#70AD47","#2DE0F3","#5050F2","#AD4AF8","#F05296"]   
CouleurBarreRougeFonce = ["#8C0001","#FF0000","#8C0001","#FF0000","#8C0001","#FF0000","#8C0001","#FF0000"]
CouleurBarreRougeClair =["#FF0000","#FF7575","#FF0000","#FF7575","#FF0000","#FF7575","#FF0000","#FF7575"]
CouleurBarreBleuFonce = ["#0C1365","#2A37E6","#0C1365","#2A37E6","#0C1365","#2A37E6","#0C1365","#2A37E6"]
CouleurBarreBleuClair = ["#5790C1","#89B2D3","#5790C1","#89B2D3","#5790C1","#89B2D3","#5790C1","#89B2D3"]
df=pd.DataFrame(np.array([CouleurBarreBleuFonce,CouleurBarreRougeClair,CouleurBarreBleuFonce,
                          CouleurBarreRougeFonce,CouleurBarreBleuClair,CouleurBarreBleuFonce,
                          CouleurBarreBleuFonce,CouleurBarreRougeFonce,CouleurBarreRougeFonce,
                          CouleurBarreRougeClair,CouleurBarreBleuFonce,CouleurBarreBleuClair,
                          CouleurBarreRougeClair,CouleurBarreBleuFonce]))

# create data
x = ['A', 'B', 'C', 'D']
y1 = np.array(CoupPedale1)
y2 = np.array(CoupPedale2)
y3 = np.array(CoupPedale3)
y4 = np.array(CoupPedale4)
y5 = np.array(CoupPedale5)
y6 = np.array(CoupPedale6)
y7 = np.array(CoupPedale7)
y8 = np.array(CoupPedale8)

 
# plot bars in stack manner
for zone in range(0,NbZones):
    plt.bar(ListeDeparts[zone], y1[zone], color=df.loc[zone,0])
    plt.bar(ListeDeparts[zone], y2[zone], bottom=y1[zone], color=df.loc[zone,1])
    plt.bar(ListeDeparts[zone], y3[zone], bottom=y1[zone]+y2[zone], color=df.loc[zone,2])
    plt.bar(ListeDeparts[zone], y4[zone], bottom=y1[zone]+y2[zone]+y3[zone], color=df.loc[zone,3])
    plt.bar(ListeDeparts[zone], y5[zone], bottom=y1[zone]+y2[zone]+y3[zone]+y4[zone], color=df.loc[zone,4])
    plt.bar(ListeDeparts[zone], y6[zone], bottom=y1[zone]+y2[zone]+y3[zone]+y4[zone]+y5[zone], color=df.loc[zone,5])
    plt.bar(ListeDeparts[zone], y7[zone], bottom=y1[zone]+y2[zone]+y3[zone]+y4[zone]+y5[zone]+y6[zone], color=df.loc[zone,6])
    plt.bar(ListeDeparts[zone], y8[zone], bottom=y1[zone]+y2[zone]+y3[zone]+y4[zone]+y5[zone]+y6[zone]+y7[zone], color=df.loc[zone,7])

plt.xlabel("Départ")
plt.ylabel("Travail (J)")
# plt.legend(["Round 1", "Round 2", "Round 3", "Round 4"])
# plt.title("Scores by Teams in 4 Rounds")

#%% Comparaison de l'impulsion Gauche/Droite

CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,RougeClair,BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]
# CouleurFonctionTypeDepart = [RougeFonce,RougeFonce,BleuFonce,BleuFonce,RougeClair]

plt.figure()
plt.grid()
plt.title('Superposition des impulsions')
plt.xlabel('Temps (s)')
plt.ylabel('Impulsion (N.s)')
for zone in range(0,9):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:1200]
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['ImpulsionGauche'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200],color = RougeClair)
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['ImpulsionDroite'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200],color = BleuClair) 
# plt.legend(Legend) 

#%% Comparaison de l'impulsion instantanée

CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,RougeFonce,BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,RougeClair,BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]
# CouleurFonctionTypeDepart = [RougeFonce,RougeFonce,BleuFonce,BleuFonce,RougeClair]

plt.figure()
plt.grid()
plt.title('Superposition des impulsions')
plt.xlabel('Temps (s)')
plt.ylabel('Impulsion (N.s)')
for zone in range(0,9):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:1200]
    plt.plot(x,locals()["Zone"+str(zone+1)]['Data']['ImpulsionTotale'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200],color = CouleurFonctionTypeDepartSansFatigue[zone])
    plt.legend(Legend)    


#%% Comparaison de l'impulsion cumulé

CouleurFonctionTypeDepart = [BleuFonce,RougeClair,BleuFonce,"#FF000000",BleuClair,BleuFonce,BleuFonce,RougeFonce,RougeFonce,"#FF000000",BleuFonce,BleuClair,RougeClair,BleuFonce,"#FF000000","#FF000000","#FF000000"]
# CouleurFonctionTypeDepart = [RougeFonce,RougeFonce,BleuFonce,BleuFonce,RougeClair]

plt.figure()
plt.grid()
plt.title('Superposition des impulsion totales cumulées')
plt.xlabel('Temps (s)')
plt.ylabel('Impulsion Totale Cumulée (N.s)')
for zone in range(0,NbZones):
    x=locals()["Zone"+str(zone+1)]['Temps'][0:1200]
    plt.plot(x,np.cumsum(locals()["Zone"+str(zone+1)]['Data']['ImpulsionTotale'][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+1200]),color=CouleurFonctionTypeDepart[zone]) 
plt.legend(Legend) 
        
        
#%% Corrélation temps/vitesse/perf


plt.figure()
for zone in range(0,NbZones):
    plt.plot(zone,locals()["Zone"+str(zone+1)]['TempsDecollage'],'x',color=CouleurFonctionTypeDepart[zone]) 
plt.legend(Legend) 
     