# Phyling Data Processing

## About the project

### Description

Start-up Phyling (https://www.phyling.fr/) has equipped the BMX bikes of the French team with three sensors:
- A revolution counter on the rear wheel,
- A gyroscope on the crankset,
- An IMU attached to the frame.

Python codes in this Git are intended to enable the entire R&D staff of the French Cycling Federation (FFC) to extract the main data from these sensors. 

### Warning

Because of the confidenciality & personal data clauses, this code can not contains :
- a set of data from recordings made with the pilots ;
- The Phyling decoding key ;

## Contents 

### Functions...
All .py starting with *Functions* are small modules containing the functions required to execute the associated code. Especially, `FunctionBasics.py` contains functions needed in several of this modules. 

### 1 - PhylingDecoderExtractor
This is the first code you need to execute if you have a .txt file coming from Phyling sensors. You only have to precise path and name of your .txt file (without extension).
After decoding and read the data, code will extract them in a .csv file. Pay attention to Console messages. It will inform you if some data are missing compared with all the data that can theoretically be extracted.

*Notes : to execute it, you need the Phyling Decoder key.*

### 2 - Calculation
Extracted data only contains raw sensors data. Because of the file size, you must delimit start and end of each area you want to study to facilitate calculation. 
In fact, this code is used, among other things, to filter data, calculate cadence, speed, power, work... 

### 3 - AreaAnalysis
The aim of this module is to suggest analysis of specific and caracteristics phases of BMX races. Currently, 3 functions are available, allowing to analyze :
-> Start : It detects the first movement of the pilot under the start gate and pedale stroke.
-> EndMound : It detects transition instant between start hill and first flat part and return time from start.
-> FirstJump : It detects the take-off of the jump on the 1st bump and return speed and time from start.

### 4 - Example
You will find `Example.py` in PhylingDataProcessing file. This program is devided in 4 parts :
-> Raw data extraction
-> Global data calculation
-> Area analysis
-> Graphical analysis

For each of them, User Input are specified allowing you tu use functions without touching the code.

## Goals

### Automation
We would like to develop automatic or semi-automatic method to find magnetic threshold of the revolution counter and detect how many areas there is in a record.

### Area Analysis
We would like to find other recurrent and detectable patterns on our data.

### Bug correction
We would like to improve the estimation of the crank angle.


