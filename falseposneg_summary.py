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

class FalsePN:
    def __init__(self, filepath_in_rfid, filepath_in_boris, boris_file, rfid_file):
        self.filepath_in_rfid = filepath_in_rfid
        self.filepath_in_boris = filepath_in_boris
        self.boris_file = boris_file
        self.rfid_file = rfid_file
        self.bf = pd.read_excel(filepath_in_boris + boris_file)
        self.rf = pd.read_excel(filepath_in_rfid + rfid_file)
        self.bf.rename(columns={'Stop (s)': 'Stop', 'Start (s)': 'Start'}, inplace=True)

    def minusplus(self, minus, plus):
        start_minus = self.bf['Start'] - timedelta(seconds = minus)
        start_minus = start_minus.tolist()
        stop_plus = self.bf['Stop'] + timedelta(seconds = plus)
        stop_plus = stop_plus.tolist()
        start_stop = list(zip(start_minus, stop_plus))
        return(start_stop)

    def boris_check(self, start_stop): #false negatives
        event_dict = {key: 0 for key in start_stop} #makes dict with key values from start/stop boris list
        for key in event_dict.keys():
            for t in self.rf['ScanDateTime']:
                if key[0] <= t <= key[1]:
                    event_dict[key] += 1
        return(event_dict)

# b = boris_check()
# sum(b.values())  #number of TRUE RFID reads
# sum(value == 0 for value in b.values())  #number of BORIS events without RFID reads

    def average_duration(self, adict):
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

filepath_in_rfid = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/BORIS/AQ projects/2021-09-19 AQ/'
filepath_in_boris = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/BORIS/AQ projects/2021-09-19 AQ/'
boris_file = "BORIS_OutputTest_converttimes_MALE_AQ_123025-1430_2021-09-19.xlsx"  #BORIS_OutputTest_WITHDIVIDEDTIMES_2021-02-09_male2.xlsx
rfid_file = "RFID_OutputTest_MALE_AQ_123025-1430_2021-09-19.xlsx" #RFID_MatchPot_2021-02-09_male.xlsx
#boris_file = "BORIS_OutputTest_WITHDIVIDEDTIMES_2021-02-09_male2.xlsx"
#rfid_file = "RFID_MatchPot_2021-02-09_male.xlsx"

pn = FalsePN(filepath_in_rfid, filepath_in_boris, boris_file, rfid_file)
start = [(0,0), (1,0), (2,0), (3,0)]
end = [(0,0), (0,1), (0,2), (0,3)]
startend = [(0,0), (1,1), (2,2), (3,3)]

for pair in end+start+startend:
    zz = pn.minusplus(pair[0],pair[1])
    b = pn.boris_check(zz)
    trueRFID = sum(b.values())
    print(pair, " TrueRFID: ", trueRFID)
    BORISout = sum(value == 0 for value in b.values())
    print(pair, " BORIS Out: ", BORISout)


c = pn.average_duration(b)
c.keys()
c.values()
