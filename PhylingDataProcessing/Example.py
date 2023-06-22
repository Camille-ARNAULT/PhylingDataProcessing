"""
@author: arnaultcamille@univ-poitiers.fr
"""

#%% INITIALIZATION
import os
os.getcwd()
CurrentPath = os.path.dirname(__file__)
os.chdir(CurrentPath)


#%% RAW DATA EWTRACTION

# User input :
Path = "C:\\Users\\admin\\Desktop\\TestModuleGitHub\\"
RawFileName = "DonneesTestGitHub"

Path = "C:\\Users\\carnau22\\Documents\\BMX\Datas\\202305_Glasgow\\2023_05_17_AM\\"
RawFileName = "phyling_120_59_20230517_090706"

#------------------------------------------------------------------------------

# Code :
from PhylingDecoderExtractor import PhylingDecoder
PhylingDecoder(Path,RawFileName=RawFileName)

#%% GLOBAL DATA CALCULATION

# User input :
CirconferenceRoue = 1591.67
Braquet = 50/18
LongueurManivelle = 177.5
AngleCadre = 6
EspacementAimant = 90

VerificationResynchro = "No"
VerificationCrankPeaks = "No"
VerificationImuOrientation = "No"
VerificationRevolutionCounterPeaks = "No"
VerificationRevolutionCounterSpeed= "No"

    
#------------------------------------------------------------------------------

# Code :
from Calculation import Calculation
NbZones = Calculation(Path+RawFileName+'.csv',
                      CirconferenceRoue=CirconferenceRoue,Braquet=Braquet,LongueurManivelle=LongueurManivelle,AngleCadre=AngleCadre,
                      EspacementAimant=EspacementAimant,
                      VerificationResynchro=VerificationResynchro,
                      VerificationCrankPeaks=VerificationCrankPeaks,
                      VerificationRevolutionCounterPeaks=VerificationRevolutionCounterPeaks,
                      VerificationRevolutionCounterSpeed=VerificationRevolutionCounterSpeed,
                      VerificationImuOrientation=VerificationImuOrientation)

#%% START DATA EXTRACTION

# User input :    
StartAnalysis = "Yes"  
EndMoundAnalysis = "Yes" 
FirstJumpAnalysis = "Yes"


VerificationStartDetection = "No"
VerificationPedalStroke = "No"
VerificationEndStartHill = "No"
VerificationFirstJump = "No"

#------------------------------------------------------------------------------    
    
# Code :

from AreaAnalysis import *

ZoneList=['' for i in range(0,NbZones)]
for i in range(0,NbZones) :
    ZoneList[i]= RawFileName + '_Zone' + str(i+1) + '.csv'    

for zone in range(0,NbZones):
    print('----------')
    print('Area '+str(zone+1))
    print('----------')
    #Data importation
    Data = pd.read_csv(Path+ZoneList[zone])
    
    # Start parameters calculation
    if StartAnalysis in ["YES","Yes","yes","Y","y","OUI","Oui","oui","O","o"]:
        FrameInit,FrameEnd,IndexCP,ImpulsionDCP,TravailDCP,AngleManivelleGaucheReculMax,AngleTotalRecul = Start(Data,VerificationStartDetection,VerificationPedalStroke)
        # Storage
        locals()["Zone"+str(zone+1)] = {}
        locals()["Zone"+str(zone+1)]['Data'] = Data
        locals()["Zone"+str(zone+1)]['FrameInit'] = FrameInit
        locals()["Zone"+str(zone+1)]['FrameEnd'] = FrameEnd
        locals()["Zone"+str(zone+1)]['Temps'] = np.arange(0,(locals()["Zone"+str(zone+1)]['FrameEnd']-locals()["Zone"+str(zone+1)]['FrameInit'])*0.005,0.005)
        locals()["Zone"+str(zone+1)]['IndexCP'] = IndexCP
        locals()["Zone"+str(zone+1)]['ImpulsionDCP'] = ImpulsionDCP
        locals()["Zone"+str(zone+1)]['TravailDCP'] = TravailDCP
        locals()["Zone"+str(zone+1)]['AngleManivelleGaucheReculMax'] = AngleManivelleGaucheReculMax
        locals()["Zone"+str(zone+1)]['AngleTotalRecul'] = AngleTotalRecul
        del AngleManivelleGaucheReculMax, AngleTotalRecul,FrameEnd,ImpulsionDCP,IndexCP,TravailDCP
    
    # End mound time calculation
    if EndMoundAnalysis in ["YES","Yes","yes","Y","y","OUI","Oui","oui","O","o"]:
        TempsBasButte = EndStartHill(Data,FrameInit,VerificationEndStartHill=VerificationEndStartHill)
        # Storage
        locals()["Zone"+str(zone+1)]['TempsBasButte'] = TempsBasButte
        del TempsBasButte
        
    # First jump time
    if FirstJumpAnalysis in ["YES","Yes","yes","Y","y","OUI","Oui","oui","O","o"]:
        TempsDecollage, VitesseDecollage, StdVitesseDecollage = FirstJump(Data,FrameInit,VerificationFirstJump=VerificationFirstJump)
        locals()["Zone"+str(zone+1)]['TempsDecollage'] = TempsDecollage
        locals()["Zone"+str(zone+1)]['VitesseDecollage'] = VitesseDecollage
        locals()["Zone"+str(zone+1)]['StdVitesseDecollage'] = StdVitesseDecollage 
        del StdVitesseDecollage,TempsDecollage,VitesseDecollage
    

#%% ANALYSE GRAPHIQUE

# User input :
DataToPlot = "TimestampGPS"
Unit = "N"
TypeAffichage = "Instant" # "Instant" ou "Cumulative"
ZonesEtudiees = range(0,NbZones)
Color = []


''' Select DataToPlot and its unit in this list :
        
        - Left crank angle in ° : PositionManivelleGauche
        - Right crank angle in ° = PositionManivelleDroite
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
    
