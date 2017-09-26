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
from sklearn.gaussian_process.kernels import DotProduct as LK, ConstantKernel as CK, Sum
#sig_b**2 + (sig_v**2)*(x-c)(xprime-c)
#from sklearn.metrics.pairwise import linear_kernel
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
#(nou, nou_tst, 60, 0, 100, 15)
def GP_prep(train, test, avg_samp, sub_samp_begin, sub_samp_end, window):
    samp_train = avg_sample(train, avg_samp) #samp_nou
    tot_samp = len(samp_train)
    #noutr = np.atleast_2d([grab_nz(samp_nou, m, n) for m, n in zip(range(samp_nou.shape[0]), range(D,samp_nou.shape[0]))])
    tr = np.atleast_2d([grab_nz(samp_train, m, n) for m, n in zip(range(samp_train.shape[0]), range(window, samp_train.shape[0]))])
    Xtr = np.atleast_2d(tr)
    #nou_ob = np.atleast_2d([[samp_nou[i] for i in range(D, samp_nou.shape[0])]])
    ob = np.atleast_2d([[samp_train[i] for i in range(window, samp_train.shape[0])]])
    Ytr = np.atleast_2d(ob).T 
    #samp_nou_tst = avg_sample(nou_tst, 60)
    samp_test = avg_sample(test, avg_samp) 
    #samp_nou_tst1 = grab_nz(samp_nou_tst, p, r)
    samp_test1 = grab_nz(samp_test, sub_samp_begin, sub_samp_end) 
    ##nou_tst1 = [grab_nz(samp_nou_tst1, m, n) for m, n in zip(range(samp_nou_tst1.shape[0]), range(D,samp_nou_tst1.shape[0]))]
    feat_xtest = [grab_nz(samp_test1, m, n) for m, n in zip(range(samp_test1.shape[0]), range(window, samp_test1.shape[0]))]
    xtst =  np.atleast_2d(feat_xtest)
    #nou_comp = [samp_nou[i] for i in range(D,samp_nou_tst1.shape[0])]
    feat_comp = [samp_train[i] for i in range(window, samp_test1.shape[0])]
    ycomp = np.atleast_2d(feat_comp).T
    #nou_ytst = [samp_nou_tst[i] for i in range(D,samp_nou_tst1.shape[0])]
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
#print "Average number of users: " + str(int(mean(nou)))
#print "Standard deviation: " + str(int(np.sqrt(sample_var(nou, mean(nou)))))

training_data=[nou, bits, pktNum, sigS, dataRate, phyB, phyG, phyN]
test_data = [nou_tst, bits_tst, pkt_tst, sigS_tst, dR_tst, b_tst, g_tst, n_tst]
labels = {"nou" : "Number of users", "bits" : "Bits", "pktNum": "Number of Packets",\
          "sigS": "Signal Strength", "dataRate": "Data Rate(MB)", "phyB": "802.11b bits",\
          "phyG": "802.11g bits", "phyN": "802.11n bits"}
samp_nou = avg_sample(nou, 60)
q = len(samp_nou)

#Preparation of subsampling test data
samp_nou_tst = avg_sample(nou_tst, 60)
#Number of test samples
p = 0
r = 100
#Subsampling features
samp_nou_tst1 = grab_nz(samp_nou_tst, p, r)

#Window size
D = 15

#Column features, rows samples
#Training samples
noutr = np.atleast_2d([grab_nz(samp_nou, m, n) for m, n in zip(range(samp_nou.shape[0]), range(D,samp_nou.shape[0]))])
Xtr = np.atleast_2d(noutr) #Training
#print "Xtr:\n", Xtr
print len(Xtr)

#Training Observations
nou_ob = np.atleast_2d([[samp_nou[i] for i in range(D, samp_nou.shape[0])]])
ytr = np.atleast_2d(nou_ob).T 
#print "ytr:\n", ytr

#Test samples
nou_tst1 = [grab_nz(samp_nou_tst1, m, n) for m, n in zip(range(samp_nou_tst1.shape[0]), range(D,samp_nou_tst1.shape[0]))]
xtst =  np.atleast_2d(nou_tst1) 
#print "xtst:\n", xtst

#Comparison
nou_comp = [samp_nou[i] for i in range(D,samp_nou_tst1.shape[0])]
ycompare = np.atleast_2d(nou_comp).T

#Test Observations
nou_ytst = [samp_nou_tst[i] for i in range(D,samp_nou_tst1.shape[0])]
ytst = np.atleast_2d(nou_ytst).T
#print "ytst:\n", ytst.T[0]


kernel1 = LK(sigma_0 = 1, sigma_0_bounds = (1e-1, 1e1))
kernel2 = CK(constant_value=1.0)
kernel = Sum(kernel1, kernel2)
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10,\
                              normalize_y=True, alpha=1e-6)

gp.fit(Xtr, ytr)

print "Marginal likelihood:", gp.log_marginal_likelihood()

Xtr_1 = [Xtr[i] for i in range(xtst.shape[0])]

y_p, y_sig = gp.predict(Xtr_1, return_std=True)
#print y_p.T[0]
#print y_sig

result_time = [i+1 for i in range(D, samp_nou_tst1.shape[0])]

#Axes and graph titling 
s = "Time interval between "+str(result_time[0])+" and "+str(result_time[-1])+\
" minutes\n Window is "+str(D)
plt.xlabel(s=s)
yLab = "Number of packets"
plt.ylabel(yLab)
o = "Using RBF Kernel with "+str(q)+" averaged training samples\nand "+str(r)+\
" averaged test samples"
plt.title(s=o)

#Ploting data
plt.plot(result_time, ycompare, "y-", label="Training")
plt.plot(result_time, y_p.T[0], "g-", label="Predicted")
#plt.plot(result_time, ytst.T[0], "m-", label="Real")
plt.fill(np.concatenate([result_time, result_time[::-1]]),
         np.concatenate([y_p-1.96*y_sig,
                        (y_p+1.96*y_sig)[::-1]]),
         alpha=.5, fc='b', ec='None')
plt.legend()
plt.show()

total_samp, Xtr, Ytr, Xtst, Ycomp, Ytst = GP_prep(nou, nou_tst, 60, p, r, D)

gp.fit(Xtr, Ytr)
y_pred, y_sigma = gp.predict(Xtst, return_std=True)

s = "Time interval between "+str(result_time[0])+" and "+str(result_time[-1])+\
" minutes\n Window is "+str(D)
plt.xlabel(s=s)
yLab = "Number of users"
plt.ylabel(yLab)
o = "Using RBF Kernel with "+str(q)+" averaged training samples\nand "+str(r)+\
" averaged test samples"
plt.title(s=o)

#Ploting data
plt.plot(result_time, Ycomp, "y-", label="Training")
plt.plot(result_time, y_pred.T[0], "g-", label="Predicted")
#plt.plot(result_time, ytst.T[0], "m-", label="Real")
plt.fill(np.concatenate([result_time, result_time[::-1]]),
         np.concatenate([y_pred-1.96*y_sigma,
                        (y_pred+1.96*y_sigma)[::-1]]),
         alpha=.5, fc='b', ec='None')
plt.legend()
plt.show()