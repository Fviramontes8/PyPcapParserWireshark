# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 11:31:55 2017

Author: Francisco Viramontes

Description: Intended to receive data from a PostgreSQL database in the form 
of tuples and create a time series graphs based on the respective data.
"""

import DatabaseConnect as dc
import matplotlib.pyplot as plt
from math import sqrt
from random import seed
from random import randrange
import time


'''
Little time pocket

import time
time.gmtime(1499722623)
'''

#Linear regression stuff

def to_float(dataset, column):
    for row in dataset:
        row[column] = float(row[column].strip())

def train_test_split(dataset, split):
    train = []
    train_size = split * len(dataset)
    dataset_copy = list(dataset)
    while len(train) < train_size:
        index = randrange(len(dataset_copy))
        train.append(dataset_copy.pop(index))
    return train, dataset_copy

def rmse(actual, predicted):
    sum_error = 0.0
    for i in range(len(actual)):
        prediction_error = predicted[i] - actual[i]
        sum_error += (prediction_error ** 2)
    mean_error = sum_error / float(len(actual))
    return sqrt(mean_error)

def eval_algor(dataset, algor, split, *args):
    train, test = train_test_split(dataset, split)
    test_set = []
    for row in test:
        row_copy = list(row)
        row_copy[-1] = None
        test_set.append(row_copy)
    predicted = algor(train, test_set, *args)
    #actual = [row[-1] for row in test]
    #rmse_val = rmse(actual, predicted)
    return predicted
    #return rmse_val

def mean(values):
    return sum(values) / float(len(values))

def variance(values, mean):
    return sum([(x-mean)**2 for x in values])

def sample_var(values, mean):
    return sum([(x-mean)**2 for x in values])/len(values)

def covariance(x, mean_x, y, mean_y):
    cov = 0.0
    for i in range(len(x)):
        cov += (x[i] - mean_x) * (y[i] - mean_y)
    return cov

def coeff(dataset):
    x = [row[0] for row in dataset]
    y = [row[1] for row in dataset]
    mean_x, mean_y = mean(x), mean(y)
    b1 = covariance(x, mean_x, y, mean_y) / variance(x, mean_x)
    b0 = mean_y - b1 * mean_x
    return[b0, b1]

def lin_regress(train, test):
    predict = []
    b0, b1 = coeff(train)
    for row in test:
        y_hat = b0 + b1 * row[0]
        predict.append(y_hat)
    return predict

def datafy(data1, data2):
    dataset = []
    for f, b in zip(data1, data2):
        mini_data = [f,b]
        dataset.append(mini_data)
    return dataset

def sub_sample(sample_arr, sample_size):
    new_sample = sample_arr.copy()
    mean_sample = []
    return_sample = []
    p, new_ele = 0
    q = (sample_size - 1)
    while q < len(sample_arr):
        for t in range(p, q):
            mean_sample.append(new_sample[t])
            
        return_sample.append(mean(mean_sample))
        p += (sample_size - 1)
        q += (sample_size - 1)
        
        if p > len(sample_arr):
            p = len(sample_arr)
            for t in range(p, q):
                mean_sample.append(new_sample[t])
            return_sample.append(mean(mean_sample))

timestamps = []
ts_test = []
nou = []
nou_test = []
bits = []
bits_test = []
pktNum = []
pktNum_test = []
sigS = []
sigS_test = []
dataRate = []
dr_test = []
phyB = []
b_test = []
phyG = []
g_test = []
phyN = []
n_test = []

db = dc.DatabaseConnect()
db.connect()
#Gotta read from pcap table bb

train = db.readTable("wed")
#db.writeDataTable("pcap_6h")

db.disconnect()

#Data from table (in form of tuple)
for k in sorted(train, key=lambda hello: hello[0]):
    timestamps.append(int(k[1]))
    nou.append(int(k[2]))
    bits.append(int(k[3]))
    pktNum.append(int(k[4]))
    sigS.append(int(k[5]))
    dataRate.append(int(k[6]))
    phyB.append(int(k[7]))
    phyG.append(int(k[8]))
    phyN.append(int(k[9]))

    
#print db.readDataTable("cpp_yo")
#print db.getTableNames()

'''
#To edit only y axis of plot
plt.ylim([y_begin, y_end])
#plt.plot([y_values], [x_values], "color/line_styling)
plt.plot([1,2,3,4], [1, 4, 9, 16], "ro")
#plt.axis([x_begin, x_end, y_begin, y_end])
plt.axis([0, 6, 0, 20])
plt.ylabel("Numbers yo")
plt.show()

'''

#dataset1 = [timestamps, nou]

seed(1)

print len(timestamps)

human_time = []
for u in timestamps:
    human_time.append((time.localtime(u).tm_hour * 10000) + \
                     (time.localtime(u).tm_min * 100) + time.localtime(u).tm_sec)

#fri_sat & mon_tues last three are % of b/g/n tues_wed is bits for b/g/n
plt.plot(human_time, nou, "r-")
plt.ylabel("Number of users")
plt.xlabel("Timestamp")
plt.show()

plt.plot(timestamps, nou, "r-")
plt.ylabel("Number of users")
plt.xlabel("Timestamp")
plt.show()

print "Average number of users: " + str(int(mean(nou)))
print "Standard deviation: " + str(int(sqrt(sample_var(nou, mean(nou)))))

'''
plt.plot(timestamps, bits, "r-")
plt.ylabel("Bits")
plt.xlabel("Timestamp")
plt.show()

print "Average bits: " + str(int(mean(bits)))
print "Standard deviation: " + str(int(sqrt(sample_var(bits, mean(bits)))))

plt.plot(timestamps, pktNum, "r-")
plt.ylabel("Number of packets")
plt.xlabel("Timestamp")
plt.show()

print "Average number of packets: " + str(int(mean(pktNum)))
print "Standard deviation: " + str(int(sqrt(sample_var(pktNum, mean(pktNum)))))

plt.plot(timestamps, sigS, "r-")
plt.ylabel("Average signal strength")
plt.xlabel("Timestamp")
plt.show()

print "Average signal strength: " + str(int(mean(sigS)))
print "Standard deviation: " + str(int(sqrt(sample_var(sigS, mean(sigS)))))

plt.plot(timestamps, dataRate, "r-")
plt.ylabel("Average data rate")
plt.xlabel("Timestamp")
plt.show()

print "Average data rate: " + str(int(mean(dataRate)))
print "Standard deviation: " + str(int(sqrt(sample_var(dataRate, mean(dataRate)))))

plt.plot(timestamps, phyB, "r-")
plt.ylabel("Bits of 802.11b packets")
plt.xlabel("Timestamp")
plt.show()

print "Average percentage of 802.11b packets: " + str(int(mean(phyB)))
print "Standard deviation: " + str(int(sqrt(sample_var(phyB, mean(phyB)))))

plt.plot(timestamps, phyG, "r-")
plt.ylabel("Bits of 802.11g packets")
plt.xlabel("Timestamp")
plt.show()

print "Average percentage of 802.11g packets: " + str(int(mean(phyG)))
print "Standard deviation: " + str(int(sqrt(sample_var(phyG, mean(phyG)))))

plt.plot(timestamps, phyN, "r-")
plt.ylabel("Bits  of 802.11n packets")
plt.xlabel("Timestamp")
plt.show()

print "Average percentage of 802.11n packets: " + str(int(mean(phyN)))
print "Standard deviation: " + str(int(sqrt(sample_var(phyN, mean(phyN)))))
'''
