# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 11:31:55 2017

Author: Francisco Viramontes

Description: Intended to receive data from a PostgreSQL database in the form 
of tuples and create a time series graphs based on the respective data.
"""

import DatabaseConnect as dc
import numpy as np
import scipy as sp
import pylab as pb
import matplotlib.pyplot as plt
from random import seed
from math import sqrt
import time
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as CK, Matern
from sklearn.gaussian_process.kernels import RationalQuadratic as RQ, ExpSineSquared as ESS 


'''
Little time pocket

import time
time.gmtime(1499722623)
'''

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
#plt.xlim(timestamps[0], timestamps[0] + 1500)
plt.show()

print "Average number of users: " + str(int(mean(nou)))
print "Standard deviation: " + str(int(sqrt(sample_var(nou, mean(nou)))))
'''
###########################
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

'''
1.0 * RBF(length_scale=1.0, length_scale_bounds=(1e-1, 10.0))

1.0 * RationalQuadratic(length_scale=1.0, alpha=0.1)
1.0 * ExpSineSquared(length_scale=1.0, periodicity=3.0, 
                     length_scale_bounds=(0.1, 10.0),
                     periodicity_bounds=(1.0, 10.0))
ConstantKernel(0.1, (0.01, 10.0))*(DotProduct(sigma_0=1.0, sigma_0_bounds=(0.0, 10.0)) ** 2)
1.0 * Matern(length_scale=1.0, length_scale_bounds=(1e-1, 10.0), nu=1.5)
'''


seed(1)

nou_minute = []
nou_ts = []

#Overfits
'''
print ("\t\t\t 1 min")
avg_n1m = avg_sample(nou, 60) #len = 1242
sub_n1m = sub_sample(nou, 60) #len = 1222
plt.plot(avg_n1m, "y-")
plt.show()
plt.plot(sub_n1m, "m-")
plt.show()

#Also Overfits
print ("\n\t\t\t 10 min")
avg_n10m = avg_sample(nou, 600) #len = 123
sub_n10m = sub_sample(nou, 600) #len = 123
plt.plot(avg_n10m, "y-")
plt.show()
plt.plot(sub_n10m, "m-")
plt.show()


print ("\n\t\t\t 30 min")
avg_n30m = avg_sample(nou, 1800) #len = 41
sub_n30m = sub_sample(nou, 1800) #len = 41
plt.plot(avg_n30m, "c-")
plt.show()
plt.plot(sub_n30m, "g-")
plt.show()
'''
print ("\n\t\t\t 1 hr")
avg_n1hr = avg_sample(nou, 3600) #len = 21
sub_n1hr = sub_sample(nou, 3600) #len = 21
plt.plot(avg_n1hr, "c-")
plt.show()
plt.plot(sub_n1hr, "g-")
plt.show()


'''
for i in range(0, 110):
    nou_minute.append(nou[i])
    nou_ts.append(timestamps[i])
    
nou_cross_test = []
ts_cross_test = []
for j in range(110, 130):
    nou_cross_test.append(nou[j])
    ts_cross_test.append(timestamps[j])

y_test = np.atleast_2d(nou_cross_test).T

#nou_minute = sub_sample(nou, 60)
#sub_time = list(range(len(nou_minute)))
'''
#  First the noiseless case
avg_zed1 = list(range(len(avg_n1hr)))
X_avg1 = np.atleast_2d(avg_zed1).T
#print X

# Observations
y_avg1 = avg_n1hr

# Mesh the input space for evaluations of the real function, the prediction and
# its MSE
x_avg1 = np.atleast_2d(list(range(len(avg_n1hr), 2 * len(avg_n1hr)))).T #np.linspace(1000, 1999, 1000)
#print "______________\n", x

# Instanciate a Gaussian Process model
# Changing nu value does not make notable difference for matern kernel

kernel = RBF(length_scale=1, length_scale_bounds=(1e-1,1e1))
#ESS(length_scale=2, periodicity=10, length_scale_bounds=(5e-3, 5e3),periodicity_bounds=(5e-3, 5e3)) 

gp = GaussianProcessRegressor(kernel=kernel, normalize_y=False,\
                              n_restarts_optimizer=15)


# Fit to data using Maximum Likelihood Estimation of the parameters
gp.fit(X_avg1, y_avg1)
#print "Fitting done"
#print gp.get_params()

print "Marginal likelihood: ", gp.log_marginal_likelihood()
#print gp.score(X, y)
# Make the prediction on the meshed x-axis (ask for MSE as well)
y_pred0, sigma0 = gp.predict(X_avg1, return_std=True)
y_pred, sigma = gp.predict(x_avg1, return_std=True)
print "Predicting done"
#print "__________\n", gp.score(y_pred.reshape(-1, 1), y_test)

# Plot the function, the prediction and the 95% confidence interval based on
# the MSE
fig = plt.figure()
nounou_minute = []

plt.plot(X_avg1, y_pred0, "g--")
plt.plot(x_avg1, y_pred, 'b--')
plt.fill(np.concatenate([X_avg1, X_avg1[::-1]]),
         np.concatenate([y_pred0-1.96*sigma0,
                         (y_pred0+1.96*sigma0)[::-1]]),
        alpha=0.5, fc="g", ec="None")
plt.fill(np.concatenate([x_avg1, x_avg1[::-1]]),
         np.concatenate([y_pred-1.96*sigma,
                        (y_pred+1.96*sigma)[::-1]]),
         alpha=.5, fc='b', ec='None')
plt.xlabel('$x$')
plt.ylabel('$y$')
plt.ylim(-1, 20)
plt.show()

sub_zed1 = list(range(len(sub_n1hr)))
X_sub1 = np.atleast_2d(sub_zed1).T
y_sub1 = sub_n1hr
x_sub1 = np.atleast_2d(list(range(len(sub_n1hr), 2 * len(sub_n1hr)))).T
gp.fit(X_sub1, y_sub1)
y_pred01, sigma01 = gp.predict(X_sub1, return_std=True)
y_pred1, sigma1 = gp.predict(x_sub1, return_std=True)
fig = plt.figure()
plt.plot(X_sub1, y_pred01, "g--")
plt.plot(x_sub1, y_pred1, 'b--')
plt.fill(np.concatenate([X_sub1, X_sub1[::-1]]),
         np.concatenate([y_pred01-1.96*sigma01,
                         (y_pred01+1.96*sigma01)[::-1]]),
        alpha=0.5, fc="g", ec="None")
plt.fill(np.concatenate([x_sub1, x_sub1[::-1]]),
         np.concatenate([y_pred1-1.96*sigma1,
                        (y_pred1+1.96*sigma1)[::-1]]),
         alpha=.5, fc='b', ec='None')
plt.xlabel('$x$')
plt.ylabel('$y$')
plt.ylim(-1, 20)
plt.show()
