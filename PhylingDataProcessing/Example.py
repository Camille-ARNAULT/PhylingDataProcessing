"""
@author: arnaultcamille@univ-poitiers.fr
"""

#%% RAW DATA EWTRACTION

# User input :
Path = "C:\\Users\\admin\\Desktop\\TestModuleGitHub\\"
RawFileName = "DonneesTestGitHub_Sylvain17PM"

#------------------------------------------------------------------------------

# Code :
from PhylingDecoderExtractor import PhylingDecoder
PhylingDecoder(Path,RawFileName=RawFileName)

#%% GLOBAL DATA CALCULATION

# User input :
NbZones = 5 
CirconferenceRoue = 1591.67
Braquet = 50/18
LongueurManivelle = 177.5

# Analysis Parameters :
AngleCadre = 6
OffsetCalibrationFG = -2441
OffsetCalibrationFD = -3961
SeuilTopTour = 1.633
IntensitePos = 0.015
IntensiteNeg = 0.02
EspacementAimant = 90

"""
-> How to get NbZones ?
    raw = pd.read_csv(Path+RawFileName+'.csv')
    plt.plot(raw['gyro_pedalier']) 
    
-> How to define OffsetCalibration ?
    Open .txt file and go to <== calibration ==>.
    get "offset" Force1 => OffsetCalibrationFD
    get "offset" Force2 => OffsetCalibrationFG
    
-> How to get SeuilTopTour, IntensitePos & IntensiteNeg ?
    raw = pd.read_csv(Path+RawFileName+'.csv')
    plt.plot(raw['magneto_toptour'])
"""
    
#------------------------------------------------------------------------------

# Code :
from Calculation import Calculation
Calculation(Path+RawFileName+'.csv',NbZones=NbZones,
                  CirconferenceRoue=CirconferenceRoue,Braquet=Braquet,LongueurManivelle=LongueurManivelle,AngleCadre=AngleCadre,
                  FreqAcq=200,
                  OffsetCalibrationFG=OffsetCalibrationFG,OffsetCalibrationFD=OffsetCalibrationFD,
                  SeuilTopTour=SeuilTopTour,IntensitePos=IntensitePos,IntensiteNeg=IntensiteNeg,EspacementAimant=EspacementAimant)

#%% START DATA EXTRACTION

# User input :    
StartAnalysis = "Yes"  
EndMoundAnalysis = "Yes" 
FirstJumpAnalysis = "Yes"

#------------------------------------------------------------------------------    
    
# Code :

from AreaAnalysis import *

ZoneList=['' for i in range(0,NbZones)]
for i in range(0,NbZones) :
    ZoneList[i]= RawFileName + '_Zone' + str(i+1) + '.csv'    

for zone in range(0,NbZones):
    print('----------')
    print('Area '+str(zone))
    print('----------')
    #Data importation
    Data = pd.read_csv(Path+ZoneList[zone])
    
    # Start parameters calculation
    if StartAnalysis in ["YES","Yes","yes","Y","y","OUI","Oui","oui","O","o"]:
        FrameInit,FrameEnd,IndexCP,ImpulsionDCP,TravailDCP,AngleManivelleReculMax,AngleTotalRecul = Start(Data)
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
        del AngleManivelleReculMax, AngleTotalRecul,FrameInit,FrameEnd,ImpulsionDCP,IndexCP,TravailDCP
    
    # End mound time calculation
    if EndMoundAnalysis in ["YES","Yes","yes","Y","y","OUI","Oui","oui","O","o"]:
        TempsBasButte = EndMound(Data,FrameInit)
        # Storage
        locals()["Zone"+str(zone+1)]['TempsBasButte'] = TempsBasButte
        del TempsBasButte
        
    # First jump time
    if FirstJumpAnalysis in ["YES","Yes","yes","Y","y","OUI","Oui","oui","O","o"]:
        TempsDecollage, VitesseDecollage, StdVitesseDecollage = FirstJump(Data,FrameInit)
        locals()["Zone"+str(zone+1)]['TempsDecollage'] = TempsDecollage
        locals()["Zone"+str(zone+1)]['VitesseDecollage'] = VitesseDecollage
        locals()["Zone"+str(zone+1)]['StdVitesseDecollage'] = StdVitesseDecollage 
        del StdVitesseDecollage,TempsDecollage,VitesseDecollage
    

#%% ANALYSE GRAPHIQUE

# User input :
DataToPlot = "ForceGauche"
Unit = "J"
TypeAffichage = "Instant" # "Instant" ou "Cumulative"
ZonesEtudiees = range(0,NbZones)
Color=[]

''' Select DataToPlot and its unit in this list :
        
        - Cadence in tr/min : CadenceTrMin
        - Linear Speed in km/h : VitesseTopTour
        
        - Left Force in N : ForceGauche
        - Right Force in N : ForceDroite
        - Sum of Left+Right Forces in N : ForceTotale
        - Sum of Left+Right absolute Forces in N : ForceTotaleAbsolue
        
        - Left Power in W : PuissanceGauche
        - Right Power in W : PuissanceDroite
        - Sum of Left+Right Power in W : PuissanceTotale
        
        - Left Work in J : TravailGauche
        - Right Work in J : TravailDroite
        - Sum of Left+Right Work in J : TravailTotal
        
        - roll in ° : Roulis
        - pitch in ° : Tangage
        - yaw in ° : Lacet
''' 

#------------------------------------------------------------------------------    
    
# Code :
import matplotlib.colors as mcolors

plt.figure()
plt.grid()
plt.title(DataToPlot)
plt.xlabel('Temps (s)')
plt.ylabel(DataToPlot+' ('+Unit+')')

if Color:
    0
else :
    Color = [mcolors.CSS4_COLORS["firebrick"],mcolors.CSS4_COLORS["red"],mcolors.CSS4_COLORS["tomato"],
             mcolors.CSS4_COLORS["lightsalmon"],mcolors.CSS4_COLORS["chocolate"],mcolors.CSS4_COLORS["saddlebrown"],
             mcolors.CSS4_COLORS["darkorange"],mcolors.CSS4_COLORS["gold"],mcolors.CSS4_COLORS["yellow"],
             mcolors.CSS4_COLORS["darkkhaki"],mcolors.CSS4_COLORS["olive"],mcolors.CSS4_COLORS["yellowgreen"],
             mcolors.CSS4_COLORS["greenyellow"],mcolors.CSS4_COLORS["mediumseagreen"],mcolors.CSS4_COLORS["mediumspringgreen"],
             mcolors.CSS4_COLORS["turquoise"],mcolors.CSS4_COLORS["darkcyan"],mcolors.CSS4_COLORS["lightskyblue"],
             mcolors.CSS4_COLORS["dodgerblue"],mcolors.CSS4_COLORS["steelblue"],mcolors.CSS4_COLORS["slateblue"],
             mcolors.CSS4_COLORS["mediumorchid"],mcolors.CSS4_COLORS["orchid"],mcolors.CSS4_COLORS["palevioletred"]]

Legend=['' for i in ZonesEtudiees]
for zone in ZonesEtudiees:
    Legend[zone] = 'Départ ' + str(zone+1)
    x=locals()["Zone"+str(zone+1)]['Temps'][0:2200]
    if TypeAffichage in ['Instant','instant','instantane','Instantane']:
        plt.plot(x,locals()["Zone"+str(zone+1)]['Data'][DataToPlot][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+2200],color=Color[zone])
    elif TypeAffichage in ['Cumulative','cumulative','Cumule','cumule']:
        plt.plot(x,np.cumsum(locals()["Zone"+str(zone+1)]['Data'][DataToPlot][locals()["Zone"+str(zone+1)]['FrameInit']:locals()["Zone"+str(zone+1)]['FrameInit']+2200]),color=Color[zone])
plt.legend(Legend) 
    
