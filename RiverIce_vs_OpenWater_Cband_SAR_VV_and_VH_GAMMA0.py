#Script for Fresh Eyes on Ice SAR river ice classification
#written by Melanie Engram
#February 6, 2024

#This script automates standard ArcMap workflow to  
#access VV and VH C-band SAR rasters from the same frame
#determines if pixel with VH and VV value is ice, open water zone (OWZ),or
#less-certain ice or less-certain water.
#
#Class is decided by which side of line VH and VV values fall (x-VH, y=VV)
#
#This tuple format pairs VV and VH images according to thier position in their ListRasters lists
#
#writes the tuple pairs to a text file, for checking that rasters are correctly paired 
#***
#Before running script:
#
#calibrate to gamma naught
#apply a speckle filter
#terrain correct SAR
#
#Tifs must be both VV and VH imagery in dB format with NoData values as background (not zeros)
#Put VV and VH pairs from same calendar year in the same folder.
#Name the tifs with VV or VH in the name
#You must use a different folder for different calendar years.
#
#parameters: Created with equivalant OWZ and All ice pixels (~2500) and All ice is half rough and half smooth
#All pixels higher than threshold line are ice. Threshold is PC(1)= -0.4869. All pixels lower than threshold line are OWZ
#
#Threshold values are in terms of GAMMA-NAUGHT.
#equation for PC(1) threshold, in terms of VV and VH: VV_thresh = -1.0705496*VH + (-43.60913)
#parameters for less certain region: all pixels with VV>-18.0434664 and VH<-25.532220 are "less certain"
#results: Ice is 1, OWZ is 2,lessCertain_Ice is 10, lessCertain_OWZ is 20 (AMBmask is 10)

import arcpy, os, string, math
from arcpy import env
from arcpy.sa import *

try:
    arcpy.CheckOutExtension("Spatial")

##******#### Set the current workspace where VV and VH rasters are stored from the SAME CALENDAR YEAR
    env.workspace = "C:/set this to the path where the data are"
    ## Set output path
    path1 = "C:/ /endFolder/"
    
###*******### Set the path and name of file to write the list of SAR pair for checking correct pairing list:
    ######File name can be edited. Location will be in endFolder
    TextFileName = path1 + "_PairList.txt"
    print "Text file name is " + TextFileName

    # Get and print a list of VH and VV Rasters from the workspace
    VHrasters = arcpy.ListRasters("*VH*", "TIF")
    VVrasters = arcpy.ListRasters("*VV*", "TIF")

    #Use the zip() function to create a list of tuples to iterate through
    #The first tuple will havae the first raster from the VHraster list
    #and the first raster from the VVraster list, and so on.
    Pairs = zip(VHrasters,VVrasters)

    
    # Create and open the text file to write
    f=open(TextFileName,'w')

    ##Iterate through each tuple member, convert to string type, write the pair to the text file, go to new line, write the next tuple member, etc.
    #then close the text file
    j=0
    for Pair in Pairs:
        #print Pairs[j]
        StrPair=str(Pairs[j])
        f.write(StrPair)
        f.write("\n")
        j=j+1
    f.close()

####Check the text file to be sure the VV and VH rasters from the same date are paired correctly
    ###They shoule be paired correctly if only one calendar year is processed at a time.

    #Start the classification
    for VHrasters, VVrasters in Pairs:
        rVH = arcpy.sa.Raster(VHrasters)
        rVV = arcpy.sa.Raster(VVrasters)
        #print rVH
        #print rVV
        
        
    #Use these generalized values for gamma0 data, or enter the yint and xint of a cusomized *****threshold**** orthoequation
        Xa = 0
        yint = -43.60913
        xint = -40.73528
        Yb = 0
        #Set ice pixels to 1, OWZ pixels 2
        out_r = Con(((xint*(rVV-yint))<=(-yint* rVH)),1,2)


        ###########creates the name of the output classified raster, using the VV raster name as a source
        name =str(VVrasters[0:17]+ VVrasters[20:32])
        print "file root name it " + name
        
        ClassName=str(VVrasters[0:29])+ "_IceMask_thresh.tif"
        
        print ClassName
        #Following will not support a floating point raster
        out_r.save(os.path.join(path1,ClassName))

        print "Ice_OWZ classification complete for "+ClassName+". Calculating the Less Certain zone..."

        #This section adds the conditions for "less certain" by creating a ten/zero mask where AMB =10, all other pixels =1
        #When VV> -18.0434664 AND VH < -25.532220, set output raster to ten, otherwise set output to 1
        ClassName3=str(VVrasters[0:17])+ "_AMBmask.tif"
        out_AMBmask=Con((rVV>= -18.0434664)&(rVH<= -25.532220),10,1)

        out_AMBmask.save(os.path.join(path1,ClassName3))
        

        #Multiply the ice/water mask by the AMB mask (value is 10 where less certain, else value is 1)
        #water will be 2, ice will be 1, and low certainty water will be 20, low certainty ice will be 10
        
        ClassName5= name + "_class.tif"
        outPCAclass=out_r*out_AMBmask
        outPCAclass.save(os.path.join(path1,ClassName5))

        #Delete intermediate products
        arcpy.Delete_management(os.path.join(path1,ClassName3))
        arcpy.Delete_management(os.path.join(path1,ClassName))
        

        print "Classification complete for this pair. On to the next pair..."
except Exception, e:
    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    print "Line %i" % tb.tb_lineno
    print e.message


print "Done"


