import csv
import sys
import numpy as np
from datetime import datetime
from scipy import spatial

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



def thresholding_algo(y, lag, threshold, influence):
    signals = np.zeros(len(y))
    filteredY = np.array(y)
    avgFilter = [0]*len(y)
    stdFilter = [0]*len(y)
    avgFilter[lag - 1] = np.mean(y[0:lag])
    stdFilter[lag - 1] = np.std(y[0:lag])
    for i in range(lag, len(y) - 1):
        if abs(y[i] - avgFilter[i-1]) > threshold * stdFilter [i-1]:
            if y[i] > avgFilter[i-1]:
                signals[i] = 1
            else:
                signals[i] = -1

            filteredY[i] = influence * y[i] + (1 - influence) * filteredY[i-1]
            avgFilter[i] = np.mean(filteredY[(i-lag):i])
            stdFilter[i] = np.std(filteredY[(i-lag):i])
        else:
            signals[i] = 0
            filteredY[i] = y[i]
            avgFilter[i] = np.mean(filteredY[(i-lag):i])
            stdFilter[i] = np.std(filteredY[(i-lag):i])

    return dict(signals = np.asarray(signals),
                avgFilter = np.asarray(avgFilter),
                stdFilter = np.asarray(stdFilter))

def get_data_peak(path):
    data = read_csv(path, 3000)

    magnitude_data = data[:,3]

    lag = 50
    threshold = 4
    influence = 0.1

    result = thresholding_algo(magnitude_data, lag, threshold, influence)

    peak_data = []
    for i in range(len(result["signals"])):
        if result["signals"][i] != 0:
            peak_data.append([data[:,0][i], 1])
    peak_data = np.array(peak_data)

    return data, peak_data

def is_similar(peak0, peak1, threshold_time, thresold_peak_count):
    def nearest_neighbour(points_a, points_b):
        tree = spatial.cKDTree(points_b)
        return tree.query(points_a, distance_upper_bound=threshold_time)
    
    def datetime_to_ms(data):
        result = np.zeros((len(data), 1))
        for i in range(len(data)):
            result[i][0] = data[i][0].timestamp()
        return result

    peak0_ms = datetime_to_ms(peak0)
    peak1_ms = datetime_to_ms(peak1)

    nn = nearest_neighbour(peak0_ms, peak1_ms)
    thresholded_nn = []

    for i in range(len(peak0)):
        if nn[1][i] != len(peak1):
            thresholded_nn.append([peak0[i][0], peak1[nn[1][i]][0]])

    return np.array(thresholded_nn)

def plot_data(data, peak_data, selected_peak):
    data = [graph_objs.Scatter(x=data[:,0],y=data[:,3],name="magnitude"),
            graph_objs.Scatter(x=peak_data[:,0],y=np.zeros_like(peak_data[:,1]),mode='markers',name="Peak"),
            graph_objs.Scatter(x=selected_peak,y=np.zeros_like(selected_peak),mode='markers',name="Selected Peak")]
        
    plotly.offline.plot(data, show_link=True)

data0, peak0 = get_data_peak(iphone_subway_data)
data1, peak1 = get_data_peak(ipad_subway_data)

similar_peak_times = is_similar(peak0, peak1, 0.1, 3)
plot_data(data0, peak0, similar_peak_times[:,0])
plot_data(data1, peak1, similar_peak_times[:,1])


