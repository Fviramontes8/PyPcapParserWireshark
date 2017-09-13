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
from sklearn.metrics.pairwise import linear_kernel
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
    return np.atleast_1d(sample_return)

def grab_n(array, length):
    return np.atleast_1d([array[i] for i in range(length)]).T
def grab_nz(array, n ,z):
    return np.atleast_1d([array[i] for i in range(n, z)]).T

#Main:
timestamps = []
nou = []
nou_tst = []
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
test = db.readTable("tues")
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
for l in sorted(test, key=lambda yello: yello[0]):
    nou_tst.append(int(l[2]))
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

#

#samp_ts = sub_sample(timestamps, 3600)
samp_Nou = avg_sample(nou, 3600)
samp_nou_tst = avg_sample(nou_tst, 3600)
#sub_sample(nou, 3600)
#grab_nz(nou, m, n)
samp_Bits = avg_sample(bits, 3600)
#sub_sample(bits, 3600)
#grab_nz(bits, m, n)
samp_Pkts = avg_sample(pktNum, 3600)
#sub_sample(pktNum, 3600)
#grab_nz(pktNum, m, n)
samp_sigS = avg_sample(sigS, 3600)
#sub_sample(sigS, 3600)
#grab_nz(sigS, m, n)
samp_dR = avg_sample(dataRate, 3600)
#sub_sample(dataRate, 3600)
#grab_nz(dataRate, m, n)
samp_pB = avg_sample(phyB, 3600)
#sub_sample(phyB, 3600)
#grab_nz(phyB, m, n)
samp_pG = avg_sample(phyG, 3600)
#sub_sample(phyG, 3600)
#grab_nz(phyG, m, n)
samp_pN = avg_sample(phyN, 3600)
#sub_sample(phyN, 3600) 
#grab_nz(phyN, m, n)

#y = np.atleast_2d([samp_Nou, samp_Bits, samp_Pkts, samp_sigS, samp_dR,\
                   #samp_pB, samp_pG, samp_pN]).T
#nu = y.shape[0]
print samp_Nou
print samp_nou_tst
D = 10 #Window size

Xtr = np.atleast_2d([grab_nz(samp_Nou, m, n) for m, n in zip(range(D+1), range(D,samp_Nou.shape[0]))]) #Training
print Xtr
ytr = np.atleast_2d([[samp_Nou[i] for i in range(D,samp_Nou.shape[0])]]).T #Observations
print ytr

xtst =  np.atleast_2d([grab_nz(samp_nou_tst, m, n) for m, n in zip(range(D+1), range(D,samp_nou_tst.shape[0]))]) #Test
print xtst
ytst = np.atleast_2d([samp_nou_tst[i] for i in range(D,samp_nou_tst.shape[0])]).T
print ytst.T[0]
#Column features, rows samples

kernel = RBF(length_scale=1, length_scale_bounds=(1e-1, 1e1))
#linear_kernel(X, y)
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10,\
                              normalize_y=True)

gp.fit(Xtr, ytr)

print "Marginal likelihood:", gp.log_marginal_likelihood()

y_p = gp.predict(xtst)
print y_p.T[0]

tues_hrs = [i+1 for i in range(D, samp_nou_tst.shape[0])]
print tues_hrs

plt.xlabel("Time of day (hrs)")
plt.ylabel("Number of Users")
plt.plot(tues_hrs, (y_p.T)[0], "g-", label="Predicted")
plt.plot(tues_hrs, ytst.T[0], "m-", label="Real")
plt.legend()
plt.show()
'''
y_p1, sigma_p1 = gp.predict(x, return_std=True)

print "Means:\t\t", [int(mean(samp_Nou)), int(mean(samp_Bits)),\
                   int(mean(samp_Pkts)), int(mean(samp_sigS)),\
                   int(mean(samp_dR)), int(mean(samp_pB)),\
                   int(mean(samp_pG)), int(mean(samp_pN))]
print "Predicted:\t", [int(y_p1[0][0]), int(y_p1[0][1]), int(y_p1[0][2]),\
                      int(y_p1[0][3]), int(y_p1[0][4]), int(y_p1[0][5]),\
                      int(y_p1[0][6]), int(y_p1[0][7])]

print "Real:\t\t", [nou[nu+m], bits[nu+m], pktNum[nu+m], sigS[nu+m],\
                  dataRate[nu+m], phyB[nu+m], phyG[nu+m], phyN[nu+m]], "\n"

'''
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