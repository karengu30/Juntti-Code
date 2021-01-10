#same as RFID proofing_1.3.1, except 
#   only counts for hours between 08:00 and 20:00
#   removes duplicate RFID readings that appear in some sheets, and deletes the 'Download Time' and 'Download Date' columns in the process
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xlrd
from datetime import datetime

# ENTER FILENAME/PATH AND FISHID
input_file = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/tagmanager/09-25-2020_tagmanager.xlsx' #paste filepath here, including file name- end with .xlsx
target_fishid = '3D6.1D599FBF57' #from spreadsheet, paste fishid name here in quotes

# ENTER START AND END DATES
start_date, end_date = str('09/01/2020'), str('10/24/2020')
def convertdate(input_date): #function converts a string of text into a readable date format (requires m/d/y input)
    output_date = datetime.strptime(input_date, '%m/%d/%Y') #converts input date (string) into a datetime function
    return(output_date)
start_date = convertdate(start_date) #converts start date to date format
end_date = convertdate(end_date)

# READ IN RFID SHEET AND SELECT TARGET FISH AND DATE RANGE
df1 = pd.read_excel(input_file) #import RFID output sheet from filepath
df = df1.drop(columns= ['Download Time', 'Download Date'])
df = df.drop_duplicates()
df.columns = df.columns.str.replace(" ","") #remove spaces from column names
print(df.columns) #prints a list of column names
df_culled = df[(df['HEXTagID'] == target_fishid) & (df['ScanDate'].apply(convertdate) >= start_date) & (df['ScanDate'].apply(convertdate) < end_date)]
#^culls RFID sheet to only readings for selected fishid and range of dates
df_culled['DateTimeRaw'] = df_culled.ScanDate + " " + df_culled.ScanTime #combines ScanDate and ScanTime string into one column
df_out = pd.DataFrame(pd.to_datetime(df_culled['DateTimeRaw'], format = '%m/%d/%Y %H:%M:%S.%f')) #converts datetime string column to datetime format
df_out['DateTimeShort'] = df_out['DateTimeRaw'].values.astype('datetime64[h]') #cuts the datetime column to just month, day and hour

# CREATE LIST OF DAYHOURS IN DATE RANGE, between 08:00 and 20:00
possible = pd.date_range(start_date, end_date, freq='h') #creates list of all datetimes between start dayhour and end dayhour
possible = possible[:-1] #removes the first hour of end date (output will not include any hour in end date)
possible_culled = []
for i in possible: #adds hours between 08:00 and 20:00 to a new series, then makes that series into 'possible'
    if ((i.hour <= 19) and (i.hour >= 8)):
        possible_culled.append(i)
possible = pd.Series(possible_culled)
possible_frame = possible.to_frame() #turns it into a dataframe

# CREATE DATAFRAME WITH HOURS WITH 0 RFID READINGS
datetimelist = [] #creates empty list to hold all dayhours between target times
freqlist = [] #creates empty list to hold frequencies of RFID readings for each dayhour (0 for some)
for i in possible: #for each dayhour in the range...
    datetimelist.append(i) #add it to datetimelist
    if (i in df_out['DateTimeShort'].values): #if that dayhour is in the list of dayhours with an RFID reading...
        freqlist.append(df_out['DateTimeShort'].value_counts()[i]) #return the number of RFID readings for that hour 
    else: #if there are no RFID readings for that hour (dayhour not in RFID sheet)...
        freqlist.append(0) #add 0 to the list of RFID readings for that dayhour
d = {'datetimes': datetimelist, 'occurence': freqlist} 
df_datetimefreq = pd.DataFrame(d) #dataframe pairing list of dayhours with number of RFID readings for each dayhour
print(df_datetimefreq)

# EXPORT DATAFRAME AS .xlsx FILE (TYPE IN PREFERRED FILEPATH/NAME)
export_filename = ('RFID frequency for fish ' + target_fishid + ": " + str(start_date) + " to " + str(end_date) + " (between 08:00 and 20:00)") #names the output spreadsheet with target RFID name and dates
export_path = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/RFID Reader Code Export Sheets/' #type in preferred filepath to export to
export_string = export_path + export_filename + '.xlsx' #combines export filename and path
df_datetimefreq.to_excel(export_string) #saves output spreadsheet

# GRAPH DATA
fig, ax = plt.subplots(figsize = (8,6)) #creates bar graph
idx = np.asarray([i for i in range(len(datetimelist))])
ax.bar(idx, freqlist)
ax.set_xticks(idx)
ax.set_xticklabels(datetimelist, rotation=90)
fig.tight_layout()
title_name = ('RFID frequency for fish ' + target_fishid + ": " + str(start_date) + " to " + str(end_date) + "(between 08:00 and 20:00)") 
#^puts together graph title, using name of fish in question, and target dates
plt.title(title_name)
plt.xlabel('Date and Time')
plt.ylabel('Number of RFID Readings')
plt.show()
