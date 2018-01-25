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
from sklearn.gaussian_process.kernels import DotProduct as LK, WhiteKernel as WK
from sklearn.gaussian_process.kernels import ConstantKernel as CK, Sum
#from sklearn.gaussian_process.kernels import RationalQuadratic as RQ, ExpSineSquared as ESS 


class MyError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

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
#(nou, nou_tst, 60, 0, 100, 15)
def GP_prep(train, test, avg_samp, sub_samp_begin, sub_samp_end, window):
    samp_train = avg_sample(train, avg_samp)
    tot_samp = len(samp_train)
    tr = np.atleast_2d([grab_nz(samp_train, m, n) for m, n in zip(range(samp_train.shape[0]), range(window, samp_train.shape[0]))])
    Xtr = np.atleast_2d(tr)
    ob = np.atleast_2d([[samp_train[i] for i in range(window, samp_train.shape[0])]])
    Ytr = np.atleast_2d(ob).T 
    samp_test = avg_sample(test, avg_samp) 
    samp_test1 = grab_nz(samp_test, sub_samp_begin, sub_samp_end) 
    feat_xtest = [grab_nz(samp_test1, m, n) for m, n in zip(range(samp_test1.shape[0]), range(window, samp_test1.shape[0]))]
    xtst =  np.atleast_2d(feat_xtest)
    feat_comp = [samp_train[i] for i in range(window, samp_test1.shape[0])]
    ycomp = np.atleast_2d(feat_comp).T
    feat_ytest = [samp_test[i] for i in range(window, samp_test1.shape[0])]
    ytst = np.atleast_2d(feat_ytest).T
    return tot_samp, Xtr, Ytr, xtst, ycomp, ytst
    
#Main:
timestamps = []
nou = []
nou_tst = []
bits = []
bits_tst = []
pktNum = []
pkt_tst = []
sigS = []
sigS_tst = []
dataRate = []
dR_tst = []
phyB = []
b_tst = []
phyG = []
g_tst = []
phyN = []
n_tst = []

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
    bits_tst.append(int(l[3]))
    pkt_tst.append(int(l[4]))
    sigS_tst.append(int(l[5]))
    dR_tst.append(int(l[6]))
    b_tst.append(int(l[7]))
    g_tst.append(int(l[8]))
    n_tst.append(int(l[9]))


plt.plot(timestamps, nou, "r-")
plt.ylabel("Number of users")
plt.xlabel("Timestamp")
plt.show()

#print "Average number of users: " + str(int(mean(nou)))
#print "Standard deviation: " + str(int(np.sqrt(sample_var(nou, mean(nou)))))

training_data=[nou, bits, pktNum, sigS, dataRate, phyB, phyG, phyN]
test_data = [nou_tst, bits_tst, pkt_tst, sigS_tst, dR_tst, b_tst, g_tst, n_tst]
labels = ["Number of users", "Bits", "Number of Packets", "Signal Strength",\
          "Data Rate(MB)", "802.11b bits", "802.11g bits", "802.11n bits"]
#
#Number of test samples
p = 0
r = 100
#Window size
D = 15


kernel1 = LK(sigma_0 = 1, sigma_0_bounds = (1e-1, 1e1))
kernel2 = CK(constant_value=1)
kernel3 = WK(0.1)
kernel = Sum(kernel1, kernel2)
kernel = Sum(kernel, kernel3)
#1e-1 for linear + constant, 1e-3 for RBF
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10,\
                              normalize_y=False, alpha=1e-1)
#print gp.get_params()['kernel']

for z in range(len(labels)): #len(labels)
    total_samp, Xtr, Ytr, Xtst, Ycomp, Ytst = GP_prep(training_data[z], test_data[z], 60, p, r, D)
    
    print(Xtr.shape, Ytr.shape, Xtst.shape, Ytst.shape)
    #Testing if it overfits
    Xtr_1 = [Xtr[i] for i in range(D, r)]
    
    #y_sample_yo = gp.sample_y(Xtr_1, 1)
    try:
        gp.fit(Xtr, Ytr)
        print "marginal likelihood:", gp.log_marginal_likelihood()
        y_pred, y_sigma = gp.predict(Xtst, return_std=True)
        print(y_pred.shape)
        
        result_time = [g+1 for g in range(D, r)]
        
        s = "time interval between "+str(result_time[0])+" and "+str(result_time[-1])+\
        " minutes\n window is "+str(D)
        plt.xlabel(s=s)
        ylab = labels[z]
        plt.ylabel(ylab)
        o = "Using "+str(gp.get_params()['kernel'])+" kernel\nwith "+str(total_samp)+" averaged training samples\nand "+str(r)+\
        " averaged test samples"
        plt.title(s=o)
        
        #ploting data
        #plt.plot(result_time, y_sample_yo, "c-", label= "kernel sample")
        plt.plot(result_time, Ycomp, "y-", label="training")
        plt.plot(result_time, y_pred.T[0], "g-", label="predicted")
        plt.plot(result_time, Ytst.T[0], "m-", label="real")
        plt.fill(np.concatenate([result_time, result_time[::-1]]),
                 np.concatenate([y_pred-1.96*y_sigma,
                                (y_pred+1.96*y_sigma)[::-1]]),
                 alpha=.5, fc='b', ec='none')
        plt.legend()
        plt.show()
        
    except:
        print "Feature "+str(labels[z])+" did not work!"
        continue