#this function allows you to enter the tagmanager files you want to read in, the fishid you want, and the location you want the files to be saved to
    #for the program to add new rows onto the end of previous files, the location you send the file to must match the location it is already saved to
    #files will save (and update) with the filename 'fishid_alldates.xlsx'
import numpy as np
import pandas as pd
from os import path #imported to test if file exists

#output sheet names will be 'fishid_all.xlsx' (filepath of choice)

class FishAggregator: #create class
    def __init__(self, fishid, filenames, filepath_in, filepath_out): #define class variables
        self.fishid = fishid
        self.filenames = filenames
        self.filepath_in = filepath_in
        self.filepath_out = filepath_out

    def fishname_cycler(self): #this function reads in every new file, and compiles them 
        fishlist = pd.DataFrame() #create dataframe
        for i in self.filenames: #for every filename
            pathname = self.filepath_in + i + '.xlsx' #combines file and path for reading in
            new_file = pd.read_excel(pathname) #loads in new excel as a dataframe
            fishlist = fishlist.append(new_file) #for each reading, appends the imported dataframe to the main dataframe for export
            print('READING IN FILE: ' + i + '...')
            print(fishlist.head(2)) #print head
        fishlist.columns = fishlist.columns.str.replace(" ","") #removes spaces from column names (useful later)
        fishlist = fishlist[(fishlist['HEXTagID'] == self.fishid)] #takes only the RFID readings for the fishid of choice
        fishlist = fishlist.drop(columns= ['DownloadTime', 'DownloadDate', 'IsDuplicate']) #drops columns to allow duplicate RFID readings to be recognized
        return(fishlist)

    def check_and_export(self): #this function checks whether the fishid already has a saved spreadsheet
        pathname = self.filepath_out + self.fishid + '_alldates.xlsx' #combines name and filepath to test if there is already a sheet for the fishid
        print('CHECKING FOR EXISTING FILENAMES...')
        if path.exists(pathname): #if there is already a spreadsheet with that filename...
            previous_file = pd.read_excel(pathname) #read in that spreadsheet as a dataframe
            print('THERE IS ALREADY A SHEET FOR THIS FISHID.')
            output_file = previous_file.append(self.fishlist) #adds new list to end of existing list
        else: #if there is no previous spreadsheet...
            print('THERE IS NO PREVIOUS SHEET FOR THIS FISHID.')
            output_file = self.fishlist #the output file is the same as the input file
        output_file = output_file.drop_duplicates() #removes any overlap readings from the old and new file. 
        output_file = output_file.sort_values(by=['ScanDate', 'ScanTime']) #sort sheet by scandate and then scantime
        output_file.to_excel(pathname, index= False) #export to folder

    def aggregate_export(self):
        self.fishlist = self.fishname_cycler() #gets aggregate dataframe of inputs for fishid by running fishname_cycler
        self.check_and_export() #appends to existing dataframe (or not), and exports to folder by running check_and_export

#set sample variables
fishid = '3D6.1D59B07986' #fishid being targeted
filenames = ['10-08-2020_tagmanager','10-23-2020_tagmanager','11-06-2020_tagmanager','09-25-2020_tagmanager','10-02-2020_tagmanager'] #names of each file to be added (without path or .xlsx)
filepath_in = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/tagmanager/' #shared filepath of files to be read in (assumes they are in same folder)
filepath_out = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/Split FishIDs/' #filepath of destination for aggregate sheet
fishobject = FishAggregator(fishid, filenames, filepath_in, filepath_out) 
fishobject.aggregate_export() #command that combines the sheets
print('DONE')
