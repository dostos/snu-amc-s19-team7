import csv
import sys
import numpy as np
from datetime import datetime

import plotly
import plotly.graph_objs as graph_objs

sys.stdout = open('file', 'w')

ipad_bus_data = "../Data/6512_ipad_bongcheon_to_snu.csv"
iphone_bus_data = "../Data/6512_iphone_bongcheon_to_snu.csv"
ipad_subway_data = "../Data/subway_ipad_snu_to_bongcheon.csv"
iphone_subway_data = "../Data/subway_iphone_snu_to_bongcheon.csv"

def strptime(val):
    if '.' not in val:
        return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")

    nofrag, frag = val.split(".")
    date = datetime.strptime(nofrag, "%Y-%m-%d %H:%M:%S")

    frag = frag[:6]  # truncate to microseconds
    frag += (6 - len(frag)) * '0'  # add 0s
    return date.replace(microsecond=int(frag))

def read_csv(path, crop_length):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        data_list = list(reader)
    
    result = []
    for element in data_list[1:]:
        time = strptime(element[0])
        if len(result) == 0 or result[-1][0] < time:
            result.append([ time ] + list(map(np.float32,element[1:4])))
        if len(result) > 0 and (time - result[0][0]).seconds > crop_length:
            break
    return np.array(result)

def extract_peak(data, threshold = 1.2):
    avg = np.average(data[:,1:]) * 3

    peak_list = []

    for i in range(len(data)):
        if np.sum(data[i][1:]) > avg * threshold:
            peak_index = i
            peak_value = np.sum(data[i][1:])
            while(i < len(data) and np.sum(data[i][1:]) > avg * threshold):
                value = np.sum(data[i][1:])
                if  value > peak_value:
                    peak_index = i
                    peak_value = value
                i += 1
            peak_list.append([data[peak_index][0], peak_value])

    return np.array(peak_list)

def plot_data(path):
    data = read_csv(path, 30)

    peak = extract_peak(data)

    data = [graph_objs.Scatter(x=data[:,0],y=data[:,1],name="x"),
            graph_objs.Scatter(x=data[:,0],y=data[:,2],name="y"),
            graph_objs.Scatter(x=data[:,0],y=data[:,3],name="z"),
            graph_objs.Scatter(x=peak[:,0],y=peak[:,1],mode='markers',name="Peak")]
            

    plotly.offline.plot(data,show_link=True,)

plot_data(ipad_subway_data)
plot_data(iphone_subway_data)