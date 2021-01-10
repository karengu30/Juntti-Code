### to run this code ###
# >>> e = ExcelAnalysis("/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/11-06-2020_tagmanager.xlsx")
# >>> e.something('3D6.1D59B07978','11/04/2020','11/05/2020')
# >>> e.exportdata()
# then you can continue changing parameters in e.something without reloading the entire script 
# for example type in next:
# >>> e.something('3D6.1D59B0796C','11/04/2020','11/05/2020')
# >>> e.exportdata()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xlrd
from datetime import datetime

class ExcelAnalysis:
    def __init__(self, input_file):
        self.input_file = input_file
        self.df = pd.read_excel(input_file)  #load the file
        # /Users/karen/OneDrive/Documents/0_RESEARCH/RFID/11-06-2020_tagmanager.xlsx

        #adjust dataframe into readable format
        self.df.columns = self.df.columns.str.replace(" ", "")  #remove space from column names
        self.df2 = self.df[['ScanDate','ScanTime','AntennaID','HEXTagID']].copy()
        #self.df2['ScanDate'] = pd.to_datetime(self.df2['ScanDate'])
        #self.df2['ScanTime'] = pd.to_timedelta(self.df2['ScanTime'])
        #self.df2['DateTime'] = self.df2['ScanDate'] + self.df2['ScanTime'] #new column of DateTime with combined Date and times


    def tagnames(self): #identify tag names and unique instances
        for i in range(len(self.df['HEXTagID'].unique())): #list tag names and unique instances
        	print(self.df['HEXTagID'].unique()[i])
        	print(len(self.df[self.df.HEXTagID==self.df['HEXTagID'].unique()[i]]))

    def convertdate(self, input_date): #function converts a string of text into a readable date format (requires m/d/y input)
        output_date = datetime.strptime(input_date, '%m/%d/%Y') #converts input date (string) into a datetime function
        return(output_date)

    def something(self, fishid, start_date, end_date):
        #start_date = pd.to_datetime(start_date)
        #end_date = pd.to_datetime(end_date)
        self.fishid=fishid
        self.start_date= start_date
        self.end_date= end_date
        start_date = self.convertdate(start_date) #converts start date to date format
        end_date = self.convertdate(end_date)

        self.df_culled = self.df2[(self.df2['HEXTagID'] == self.fishid) & (self.df2['ScanDate'].apply(self.convertdate) >= start_date) & (self.df2['ScanDate'].apply(self.convertdate) <= end_date)]
        #^culls RFID sheet to only readings for selected fishid and range of dates
        self.df_culled['DateTimeRaw'] = self.df_culled.ScanDate + " " + self.df_culled.ScanTime #combines ScanDate and ScanTime string into one column
        self.df_out = pd.DataFrame(pd.to_datetime(self.df_culled['DateTimeRaw'], format = '%m/%d/%Y %H:%M:%S.%f')) #converts datetime string column to datetime format
        self.df_out['DateTimeShort'] = self.df_out['DateTimeRaw'].values.astype('datetime64[h]') #cuts the datetime column to just month, day and hour

        # CREATE LIST OF DAYHOURS IN DATE RANGE, between 08:00 and 20:00
        possible = pd.date_range(start_date, end_date, freq='h') #creates list of all datetimes between start dayhour and end dayhour
        possible = possible[:-1] #removes the first hour of end date (output will not include any hour in end date)
        possible_culled = []
        for i in possible: #adds hours between 08:00 and 20:00 to a new series, then makes that series into 'possible'
            if ((i.hour <= 19) and (i.hour >= 8)):
                possible_culled.append(i)
        self.possible = pd.Series(possible_culled)
        self.possible_frame = possible.to_frame() #turns it into a dataframe

        # CREATE DATAFRAME WITH HOURS WITH 0 RFID READINGS
        self.datetimelist = [] #creates empty list to hold all dayhours between target times
        self.freqlist = [] #creates empty list to hold frequencies of RFID readings for each dayhour (0 for some)
        for i in self.possible: #for each dayhour in the range...
            self.datetimelist.append(i) #add it to datetimelist
            if (i in self.df_out['DateTimeShort'].values): #if that dayhour is in the list of dayhours with an RFID reading...
                self.freqlist.append(self.df_out['DateTimeShort'].value_counts()[i]) #return the number of RFID readings for that hour
            else: #if there are no RFID readings for that hour (dayhour not in RFID sheet)
                self.freqlist.append(0) #add 0 to the list of RFID readings for that dayhour
        d = {'datetimes': self.datetimelist, 'occurence': self.freqlist}
        self.df_datetimefreq = pd.DataFrame(d) #dataframe pairing list of dayhours with number of RFID readings for each dayhour
        print(self.df_datetimefreq)

    # EXPORT DATAFRAME AS .xlsx FILE (TYPE IN PREFERRED FILEPATH/NAME)
    def exportdata(self):
        start_date = self.start_date.replace('/','')
        end_date = self.end_date.replace('/','')
        export_filename = ('Fish' + self.fishid + "_" + str(start_date) + "_" + str(end_date)) #names the output spreadsheet with target RFID name and dates
        export_path = '/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/ExportedData/' #type in preferred filepath to export to
        export_string = export_path + export_filename + '.xlsx' #combines export filename and path
        self.df_datetimefreq.to_excel(export_string) #saves output spreadsheet

    def graph(self): #graph the data
        fig, ax = plt.subplots(figsize = (8,6)) #creates bar graph
        idx = np.asarray([i for i in range(len(self.datetimelist))])
        ax.bar(idx, self.freqlist)
        ax.set_xticks(idx)
        ax.set_xticklabels(self.datetimelist, rotation=90)
        fig.tight_layout()
        title_name = ('RFID frequency for fish ' + self.fishid + ": " + str(self.start_date) + " to " + str(self.end_date))
        #^puts together graph title, using name of fish in question, and target dates
        plt.title(title_name)
        plt.xlabel('Date and Time')
        plt.ylabel('Number of RFID Readings')
        plt.show()
