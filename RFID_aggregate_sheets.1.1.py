#reads all of the indicated tagmanager sheets into a dictionary of dataframes
#get_fish() compiles all RFID readings between dataframes for the selected fishid, and outputs them as one .xlsx file
#contains lines (.drop_columns and .drop_duplicates) that remove 'Scan Date' and 'Scan Time' columns, and remove duplicate RFID readings, but increase the execution time

import numpy as np
import pandas as pd

class FishAggregator:
    def __init__(self, fishid): #this function reads in all of the tagmanager sheets, and combines them into a dictionary
        self.fishid = fishid

        input_filepath = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/tagmanager/' #paste filepath here
        sheet1name = '09-25-2020_tagmanager' #paste filenames here- add extra sheetnames if adding extra files
        sheet2name = '10-02-2020_tagmanager'
        sheet3name = '10-08-2020_tagmanager'
        sheet4name = '10-23-2020_tagmanager'
        sheet5name = '11-06-2020_tagmanager'
        sheetnames = [sheet1name, sheet2name, sheet3name, sheet4name, sheet5name] #combines sheetnames into a list- add extra if needed

        dataframe_collection = {} #creates empty dictionary to hold dataframes

        for i in sheetnames: #for each sheetname
            pathname = input_filepath + i + '.xlsx' #creates usable filepath
            read_in = pd.read_excel(pathname) #imports that sheet as a dataframe
            dataframe_collection[i] = read_in #adds the dataframe to the dictionary, with the same name as in the sheetnames
        self.dictionary = dataframe_collection #designates the dictionary as self.df
    
    def get_fish(self): #this function compiles sheets for individual fishids, incoporating all sheets into one
        culled_fishid = pd.DataFrame() #creates empty dataframe
        for j in self.dictionary: #for each dataframe in the dictionary self.dictionary:
            df = self.dictionary[j] #renames that dataframe as df for convenience
            df_culled = df[(df['HEX Tag ID'] == self.fishid)] #takes only the RFID readings for the fishid of choice
            df_culled = df_culled.drop(columns= ['Download Time', 'Download Date']) #drops columns to allow duplicate RFID readings to be recognized
            df_culled = df_culled.drop_duplicates() #removes duplicate readings
            culled_fishid = culled_fishid.append(df_culled) #appends those (for each sheet) to the output dataframe
        export_name = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/Split FishIDs/' + self.fishid + '_alldates.xlsx' #enter filepath for export
        #the exported dataframe will have fishid_alldates as its name
        print('EXPORTING...')
        culled_fishid.to_excel(export_name, index = False) #exports as a .xlsx file to the selected location
        print(culled_fishid) #prints in terminal

p1 = FishAggregator('3D6.1D59B07986') #example for fishid 3D6.1D59B07986
p1.get_fish() #applies function for that fishid
print('DONE')
