# -*- coding: utf-8 -*-
"""
Created on Fri Sep 01 11:06:34 2017

@author: fviramontes8
"""
import DatabaseConnect as dc
import numpy as np
np.set_printoptions(threshold=np.nan)
#import scipy as sp
#import pylab as pb
import matplotlib.pyplot as plt
#from random import seed
from math import sqrt
import time
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
#, ConstantKernel as CK, Matern
#from sklearn.gaussian_process.kernels import RationalQuadratic as RQ, ExpSineSquared as ESS 

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

def sub_sample(sample_arr, sample_size):
    new_sample = sample_arr
    return_sample = []
    p = 0
    q = (sample_size - 1)
    while q < len(sample_arr):
        return_sample.append(new_sample[q])
        p += sample_size
        q += sample_size
        
        if q >= len(sample_arr) - 1:
            q = len(sample_arr) - 1
            return_sample.append(new_sample[q])
            break
    return return_sample

def grab_n(array, length):
    return np.atleast_1d([array[i] for i in range(length)]).T

def avg_sample(sample_arr, sample_size):
    a = sample_arr
    sample_return = []
    j = 0
    k = sample_size - 1
    while k < len(a):
        m = []
        for i in range(j, k):
            m.append(a[i])
        sample_return.append(int(mean(m)))
        j += sample_size - 1
        k += sample_size - 1
        if k >= len(a):
            m = []
            k = len(a)
            for i in range(j, k):
                m.append(a[i])
            sample_return.append(int(mean(m)))
            break
        
    return sample_return

#Main:
timestamps = []
nou = []
bits = []
pktNum = []
sigS = []
dataRate = []
phyB = []
phyG = []
phyN = []

db = dc.DatabaseConnect()
db.connect()
#Gotta read from pcap table bb

#Need to do recapture of wed
train = db.readTable("mon")
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

#Trying grabbing the first ten to predict 11th
n = 10
nou10 = grab_n(nou, n)
bits10 = grab_n(bits, n)
pktN10 = grab_n(pktNum, n)
sigS10 = grab_n(sigS, n)
dR10 = grab_n(dataRate, n)
pB10 = grab_n(phyB, n)
pG10 = grab_n(phyG, n)
pN10 = grab_n(phyN, n)

y = np.atleast_2d([nou10, bits10, pktN10, sigS10, dR10, pB10, pG10, pN10])
print y
X = np.atleast_2d([[i for i in range(10)]]*8)
x = np.atleast_2d([[i for i in range(10, 20)]]*8)
print x

kernel = RBF(length_scale=1, length_scale_bounds=(1e-1, 1e1))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10,\
                              normalize_y=True)
print X
gp.fit(X, y)

print ("Marginal likelihood: ", gp.log_marginal_likelihood())

y_p, sigma_p = gp.predict(X, return_std=True)
y_p1, sigma_p1 = gp.predict(x, return_std=True)

print (y_p)

plt.plot(nou10, "k-")
plt.show()
plt.plot((y_p.T)[0], "m-")
plt.show()
'''
plt.plot(X, y_p, "m-.")
plt.plot(x, y_p1, "c-.")
plt.fill(np.concatenate([x, x[::-1]]),
         np.concatenate([y_p1-1.96*sigma_p1,(y_p1+1.96*sigma_p1)[::-1]]),
         alpha=0.5, fc="c", ec="None")
plt.xlabel('$x$')
plt.ylabel('$y$')
plt.show()
'''
