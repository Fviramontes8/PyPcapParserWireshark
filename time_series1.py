# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 11:31:55 2017

Author: Francisco Viramontes

Description: Intended to receive data from a PostgreSQL database in the form 
of tuples and create a time series graphs based on the respective data.
"""

import DatabaseConnect as dc
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from random import seed
from random import randrange
import time
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C


'''
Little time pocket

import time
time.gmtime(1499722623)
'''

def to_float(dataset, column):
    for row in dataset:
        row[column] = float(row[column].strip())

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

def exp_cov(x, y, params):
    return params[0] * np.exp(-0.5 * params[1] * np.subtract.outer(x,y)**2)

def conditional(x_new, x, y, params):
    A = exp_cov(x_new, x_new, params)
    B = exp_cov(x_new, x, params)
    C = exp_cov(x, x, params)
    
    mu = np.linalg.inv(C).dot(B.T).T.dot(y)
    sigma = A - B.dot(np.linalg.inv(C).dot(B.T))
    
    return (mu.squeeze(), sigma.squeeze())

def predict(x, data, kernel, params, sigma, t):
    k = [kernel(x, y, params) for y in data]
    Sinv = np.linalg.inv(sigma)
    y_pred = np.dot(k, Sinv).dot(t)
    new_sigma = kernel(x, x, params) - np.dot(k, Sinv).dot(k)
    return y_pred, new_sigma

def sub_sample(sample_arr, sample_size):
    new_sample = sample_arr
    #mean_sample = []
    return_sample = []
    p = 0
    q = (sample_size - 1)
    while q < len(sample_arr):
        #mean_sample.append(new_sample[p])
        #mean_sample.append(new_sample[q])
        return_sample.append(new_sample[q])
        p += sample_size
        q += sample_size
        
        if q > len(sample_arr):
            q = len(sample_arr) - 1
            #mean_sample.append(new_sample[p])
            #mean_sample.append(new_sample[q])
            return_sample.append(new_sample[q])
            #return_sample.append(int(mean(mean_sample)))
            break
    return return_sample

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

train = db.readTable("sat")
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

nou_minute = []

for i in range(0, 1999):
    nou_minute.append(nou[i])
#nou_minute = sub_sample(nou, 60)
sub_time = list(range(len(nou_minute)))

#  First the noiseless case
X = np.atleast_2d(sub_time).T

# Observations
y = nou_minute

# Mesh the input space for evaluations of the real function, the prediction and
# its MSE
x = np.atleast_2d(np.linspace(0, 2500, 1000)).T

# Instanciate a Gaussian Process model
kernel = C(1.0, (1e-3, 1e3)) * RBF(10, (1e-1, 1e1))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9)

# Fit to data using Maximum Likelihood Estimation of the parameters
gp.fit(X, y)

# Make the prediction on the meshed x-axis (ask for MSE as well)
y_pred, sigma = gp.predict(x, return_std=True)

# Plot the function, the prediction and the 95% confidence interval based on
# the MSE
fig = plt.figure()
plt.plot(X, y, 'r.', markersize=10)
plt.plot(x, y_pred, 'b-')
plt.fill(np.concatenate([x, x[::-1]]),
         np.concatenate([y_pred - 1.9600 * sigma,
                        (y_pred + 1.9600 * sigma)[::-1]]),
         alpha=.5, fc='b', ec='None')
plt.xlabel('$x$')
plt.ylabel('$y$')
plt.ylim(-10, 20)
plt.xlim(0, len(nou_minute))
plt.show()

'''
#xpts = np.arange(-3, 3, step=0.01)
#plt.errorbar(xpts, np.zeros(len(xpts)), yerr = sig_theta, capsize=0)


human_time = []
for u in timestamps:
    human_time.append((time.localtime(u).tm_hour * 10000) + \
                     (time.localtime(u).tm_min * 100) + time.localtime(u).tm_sec)

print len(nou)

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
