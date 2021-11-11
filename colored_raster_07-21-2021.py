from datetime import datetime
import pandas as pd
import numpy as np
from datetime import timedelta
import timeit
import matplotlib.pyplot as plt
import matplotlib.axes as axs
import matplotlib.colors as mcolors
import seaborn as sns
import xlrd
pd.options.mode.chained_assignment = None  # default='warn'

filepath_in_rfid = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/BORIS/AQ projects/2021-09-19 AQ/'
filepath_in_boris = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/BORIS/AQ projects/2021-09-19 AQ/'
boris_file = "BORIS_OutputTest_converttimes_MALE_AQ_123025-1430_2021-09-19.xlsx"  #BORIS_OutputTest_WITHDIVIDEDTIMES_2021-02-09_male2.xlsx
rfid_file = "RFID_OutputTest_MALE_AQ_123025-1430_2021-09-19.xlsx" #RFID_MatchPot_2021-02-09_male.xlsx
#boris_file = "BORIS_OutputTest_WITHDIVIDEDTIMES_2021-02-09_male2.xlsx"
#rfid_file = "RFID_MatchPot_2021-02-09_male.xlsx"

bf = pd.read_excel(filepath_in_boris + boris_file)
rf = pd.read_excel(filepath_in_rfid + rfid_file)

#bf.columns = bf.columns.str.replace(" ","")
#bf = bf.drop(bf[bf.Behavior == 'Right pot occupied'].index) #only looking at left pot
#rf = rf.drop(rf[rf.Behavior == 'Right pot occupied'].index)
#rf = rf.reset_index()
bf.rename(columns={'Stop (s)': 'Stop', 'Start (s)': 'Start'}, inplace=True)
start_list = bf['Start'].tolist()
start_minus_1 = bf['Start'] - timedelta(seconds=0)
start_minus_1 = start_minus_1.tolist()
#stop_list = bf['Stop'].tolist()
stop_plus_1 = bf['Stop'] + timedelta(seconds=0)
stop_plus_1 = stop_plus_1.tolist()
#start_stop = list(zip(start_list, stop_list))
start_stop_1 = list(zip(start_minus_1, stop_plus_1))

rf ["within"] = ""
for i in range(len(rf['ScanDateTime'])):
    if any(lower <= rf['ScanDateTime'][i] <= upper for (lower, upper) in start_stop_1):  #changed start_stop
        rf['within'][i] = 1
        print(str(i), ' True')
    else:
        rf['within'][i] = 0
        print(str(i), ' False')

def boris_check(): #false negatives
    event_dict = {key: 0 for key in start_stop_1} #makes dict with key values from start/stop boris list
    for key in event_dict.keys():
        for t in rf['ScanDateTime']:
            if key[0] <= t <= key[1]:
                event_dict[key] += 1
    return(event_dict)

# b = boris_check()
# sum(b.values())  #number of TRUE RFID reads
# sum(value == 0 for value in b.values())  #number of BORIS events without RFID reads
# len(rf) # gives total RFID reads
# len(b) #gives total BORIS events

def average_duration(adict):
    bdict = {}
    for key in adict.keys():
         boris_duration = (key[1]-key[0]).total_seconds()
         num_rfid = adict[key]
         average = num_rfid / boris_duration
         bdict[boris_duration] = average
         #print(boris_duration, average)
    return(bdict)

# c = average_duration(b)
# c.keys() #durations of BORIS events
# c.values() # average reads/sec per BORIS event

#    for j in start_stop:
#        if rf_left['ScanDateTime'][i] >= j[0] and rf_left['ScanDateTime'][i] <= j[1]:
#            #rf_left['within'][i] = 1
#            print(str(i), str(j), ' True')
#            break
#        else:
#            #rf_left['within'][i] = 0
#            print(str(i), str(j), ' False')

#outfile = filepath_in_boris+'RFID_CONVERTEDTIMES_within_male_rightpot.xlsx'
#rf_left.to_excel(outfile, index=False)
"""
rf_left['yval']=rf_left['within']*0+0.1
plt.scatter(rf_left.ScanDateTime, rf_left.yval, c=rf_left.within, marker='|')
plt.show()
"""
#HERE HERE THERE

rf['yval']=rf['within']*0+0.1
begin = datetime.strptime(('2021-09-19 ' + '12:30:00.00'), '%Y-%m-%d %H:%M:%S.%f')
end = datetime.strptime(('2021-09-19 ' + '14:30:00.00'), '%Y-%m-%d %H:%M:%S.%f')


fig, ax = plt.subplots()
plt.scatter(rf.ScanDateTime, rf.yval, c=rf.within, marker='|', s=200, cmap = mcolors.ListedColormap(["orange", "blue"]))
for x_1 , x_2 in zip(bf['Start'] ,bf['Stop']):
    ax.add_patch(plt.Rectangle((x_1,0.102),x_2-x_1,0.005))
ax.set_xlim([begin, end])
ax.set_ylim([0.095, 0.110])
plt.show()

#rf['within'].value_counts()

"""
fig, ax = plt.subplots()
#ax.scatter(df['population'], df['Area'], c=df['continent'].map(colors))


#colors = {'North America':'red', 'Europe':'green', 'Asia':'blue', 'Australia':'yellow'}
#sns.scatterplot(x= df_antennaid_1.ScanDateTime, y= df_antennaid_1.HEXTagID, data= df_antennaid_1, marker = '|', hue = df_antennaid_1.HEXTagID, s = 100, ax= ax1) #creates raster plot for AntennaID1

fig, (ax1, ax2) = plt.subplots(2, figsize=(18,7)) #makes 2 stacked subplots in one image, image size is 18x8 inches
fig.suptitle('RFID readings for fishids: ' + str(self.target_fishids) + ' between dates: ' + self.target_start + ' - ' + self.target_end) #creates title for figure, noting fishid and dates
sns.scatterplot(x= df_antennaid_1.ScanDateTime, y= df_antennaid_1.HEXTagID, data= df_antennaid_1, marker = '|', hue = df_antennaid_1.HEXTagID, s = 100, ax= ax1) #creates raster plot for AntennaID1
sns.scatterplot(x= df_antennaid_3.ScanDateTime, y= df_antennaid_3.HEXTagID, data= df_antennaid_3, marker = '|', hue = df_antennaid_3.HEXTagID, s = 100, ax= ax2) #creates raster plot for AntennaID3
ax1.title.set_text('AntennaID 1') #subtitle
ax2.title.set_text('AntennaID 3') #subtitle
#sns.scatterplot(x= df_antennaid_5.ScanDateTime, y= df_antennaid_5.HEXTagID, data= df_antennaid_5, marker = '|', hue = df_antennaid_5.HEXTagID, s = 100, ax= ax3)
plt.subplots_adjust(bottom=0.2, hspace=0.5) #creates space at bottom of figure and between plots
plt.show() #display plots- TODO save plots as image file
"""
