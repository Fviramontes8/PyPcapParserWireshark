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
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF
#, ConstantKernel as CK
#, Matern
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

def grab_n(array, length):
    return np.atleast_1d([array[i] for i in range(length)]).T
def grab_nz(array, n ,z):
    return np.atleast_1d([array[i] for i in range(n, z)]).T

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
'''  
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
'''
print "Average number of users: " + str(int(mean(nou)))
print "Standard deviation: " + str(int(np.sqrt(sample_var(nou, mean(nou)))))

#Trying grabbing the first ten to predict 11th
n = 10
print n
nou10 = grab_n(nou, n)
nounz = grab_nz(nou, 0, 10)
print "nou10:", nou10, "\nnounz:", nounz
#sub_sample(nou, 3600)
#avg_sample(nou, 3600)
bits10 = grab_n(bits, n)
#sub_sample(bits, 3600)
#avg_sample(bits, 3600)
pktN10 = grab_n(pktNum, n)
#sub_sample(pktNum, 3600)
#avg_sample(pktNum, 3600)
sigS10 = grab_n(sigS, n)
#sub_sample(sigS, 3600)
#avg_sample(sigS, 3600)
dR10 = grab_n(dataRate, n)
#sub_sample(dataRate, 3600)
#avg_sample(dataRate, 3600)
pB10 = grab_n(phyB, n)
#sub_sample(phyB, 3600)
#avg_sample(phyB, 3600)
pG10 = grab_n(phyG, n)
#sub_sample(phyG, 3600)
#avg_sample(phyG, 3600)
pN10 = grab_n(phyN, n)
#sub_sample(phyN, 3600) 
#avg_sample(phyN, 3600)

y = np.atleast_2d([nou10, bits10, pktN10, sigS10, dR10, pB10, pG10, pN10]).T
nu = y.shape[0]

X = np.atleast_2d([[i for i in range(nu)]]).T
x =  np.atleast_2d([[i for i in range(nu, nu + 1)]]).T


kernel = RBF(length_scale=2, length_scale_bounds=(2e-1, 2))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10,\
                              normalize_y=True)
#print X
#print y
gp.fit(X, y)

print ("Marginal likelihood: ", gp.log_marginal_likelihood())

#print x
y_p = gp.predict(X)
#print y_p

y_p1, sigma_p1 = gp.predict(x, return_std=True)
print "Means:\t", [int(mean(nou10)), int(mean(bits10)), int(mean(pktN10)),\
                 int(mean(sigS10)), int(mean(dR10)), int(mean(pB10)),\
                 int(mean(pG10)), int(mean(pN10))]
print "Predicted:", [int(y_p1[0][0]), int(y_p1[0][1]), int(y_p1[0][2]),\
                      int(y_p1[0][3]), int(y_p1[0][4]), int(y_p1[0][5]),\
                      int(y_p1[0][6]), int(y_p1[0][7])]

print "Real:\t", [nou[nu], bits[nu], pktNum[nu], sigS[nu], dataRate[nu],\
                phyB[nu], phyG[nu], phyN[nu]]
###############################################################################
#Move the window yo
###############################################################################
'''
print (y_p.T)

plt.plot(nou10, "k-")
plt.show()
plt.plot((y_p)[0], "m-")
plt.show()
plt.plot(x, y_p1, "c-.")
plt.xlabel('$x$')
plt.ylabel('$y$')
plt.show()
'''