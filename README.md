# Phyling Data Processing

## About the project

### Description

Start-up Phyling (https://www.phyling.fr/) has equipped the BMX bikes of the French team with three sensors:
- A top turn on the rear wheel,
- A gyroscope on the crankset,
- An IMU attached to the frame.

Codes in this Git are intended to enable the entire R&D staff of the French Cycling Federation (FFC) to extract the main data from these sensors. 

### Warning

Because of the confidenciality & personal data clauses, this code can not contains :
- a set of data from recordings made with the pilots ;
- The Phyling decoding key ;

## Contents 

### Functions...
All .py starting with *Functions* are small modules containing the functions required to execute the associated code. Especially, `FunctionBasics.py` contains functions needed in several of this modules. 

### 1 - PhylingDecoderExtractor
This is the first code you need to execute if you have a .txt file coming from Phyling sensors. You only have to precise path and name of your .txt file (without extension).
After decoding and ready the data, code will extract them in a .csv file. Pay attention to Console messages. It will inform you if some data are missing compared with all the data that can theoretically be extracted.

*Notes : to execute it, you need the Phyling Decoder key.*

### 2 - Calculation


### 3 - AreaAnalysis
This module contains 3 functions.

## Example

You will find `Example.py` in PhylingDataProcessing file.


