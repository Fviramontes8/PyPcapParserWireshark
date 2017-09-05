# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:45:17 2017

@author: fviramontes8
"""

import numpy as np
np.set_printoptions(threshold=np.inf)

import matplotlib
import matplotlib.pyplot as plt

def mean(values):
    return sum(values) / float(len(values))

def variance(values, mean):
    return sum([(x-mean)**2 for x in values])

def buffer(x, n, p=0, opt=None):
    #Original author: ryanjdillon
    #Link: https://stackoverflow.com/questions/38453249/is-there-a-matlabs-buffer-equivalent-in-numpy
    '''Mimic MATLAB routine to generate buffer array

    MATLAB docs here: https://se.mathworks.com/help/signal/ref/buffer.html

    Args
    ----
    x:   signal array
    n:   number of data segments
    p:   number of values to overlap
    opt: initial condition options. default sets the first `p` values
         to zero, while 'nodelay' begins filling the buffer immediately.
    '''
    if p >= n:
        raise ValueError('p ({}) must be less than n ({}).'.format(p,n))

    # Calculate number of columns of buffer array
    '''
    Modification of:
    cols = int(np.ceil(len(x)/(n-p)))
    to:
    cols = int(np.floor(len(x)-n/float((n-p)))) + 1
    '''
    cols = int(np.floor(len(x)-n/float((n-p)))) + 1
    
    # Check for opt parameters
    if opt == 'nodelay':
        # Need extra column to handle additional values left
        #cols += 1
        hello = 1
    elif opt != None:
        raise SystemError('Only `None` (default initial condition) and '
                          '`nodelay` (skip initial condition) have been '
                          'implemented')

    # Create empty buffer array
    b = np.zeros((n, cols))

    # Fill buffer by column handling for initial condition and overlap
    j = 0
    for i in range(cols):
        # Set first column to n values from x, move to next iteration
        if i == 0 and opt == 'nodelay':
            b[0:n,i] = x[0:n]
            continue
        # set first values of row to last p values
        elif i != 0 and p != 0:
            b[:p, i] = b[-p:, i-1]
        # If initial condition, set p elements in buffer array to zero
        else:
            b[:p, i] = 0

        # Get stop index positions for x
        k = j + n - p

        # Get stop index position for b, matching number sliced from x
        n_end = p+len(x[j:k])

        # Assign values to buffer array from x
        '''
        Modification of:
        b[p:n_end,i] = x[j:k]
        to:
        b[p:n_end,i] = x[j:k] + 4
        '''
        b[p:n_end,i] = x[j + 4]

        # Update start index location for next iteration of x
        j = k

    return b

def bottom_row_ones(z):
    b = z
    k= len(z) - 1
    for i in range(len(z[k])):
        b[k][i] = 1
    return b

def IOfy(x):
    g = []
    for i in range(len(x) - 1):
        g.append(list(x[i]))
        for r, t in zip(g[i], range(len(g[i]))) :
            #r = int(r)
            g[i][t] = r
    h = x[len(x) - 1]
    return g, h

def chi_test(x, y):
    #x is test and y is true values
    u = sum((y-x)**2)
    v = sum((y - mean(y))**2)
    return 1 - (u/v)

from scipy.signal import lfilter
a = [1,-1.161917483671733,0.695942755789651,-0.137761301259893]
b = [0.049532996357253,0.148598989071760,0.148598989071760,0.049532996357253]
hu = lfilter(b, a, np.random.randn(1,100))[0]

X= buffer(hu, 4, 3, opt="nodelay")
#print "Data: ", X


inputing, outputing = IOfy(X)

Ytr = np.array(outputing)
Xtr = bottom_row_ones(X)
#print "Training X: \n", Xtr
#print "Observations:\n", Ytr
gamma = 1e-3
w = np.linalg.inv(Xtr.dot(Xtr.T) + gamma * np.eye(4)).dot(Xtr.dot(Ytr.T))

#print "Weights:\n", w

        #Prediction
X_data = lfilter(b, a, np.random.randn(1,100))[0]
#print "Data:\n" , X_data
#xdata = 100 * np.sin(X_data)
Xdata = buffer(X_data, 4, 3, "nodelay")
#print "Molded data:\n", Xdata
inputin, outputin = IOfy(Xdata)
#print "Inputin:\n", inputin
#print "Outputin:\n", outputin

Ytst = np.array(outputin)
Xtst = bottom_row_ones(Xdata)
#print "X test:\n", Xtst
#print "Y test:\n", Ytst

y = w.T.dot(Xtst)
#print "Predicted values", y

plt.plot(Ytst, "b-.", label="Real")
plt.plot(y, "g--.", label="Predicted")
plt.legend()
plt.show()

#print chi_test(y, Ytst)



from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF


skxtr = np.atleast_2d(Xtr).T
skytr = list(Ytr)

skxtst = np.atleast_2d(Xtst).T

kernel = RBF(length_scale=1, length_scale_bounds=(1e-4, 1e4))

gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True,\
                              optimizer='fmin_l_bfgs_b',\
                              n_restarts_optimizer = 10)


y_pred = gp.predict(skxtst)
plt.plot(Ytst, "r-", label="Real")
plt.plot(y_pred, "k--", label="Predicted")
plt.legend()
plt.show()


import GPy


kernel = GPy.kern.RBF(input_dim=1, variance=1, lengthscale=1)
iop = np.atleast_2d([u for u in Xtr[0]]).T
chiop = np.atleast_2d(Ytr).T

m = GPy.models.GPRegression(X=iop, Y=chiop, kernel=kernel)
iop_new = np.atleast_2d(Xtst)

m.plot(plot_limits=(-2.0, 5.0))
plt.show()

print "likelihood: ", m.log_likelihood()

ypred, ysigma = m.predict(Xnew=iop_new, kern=kernel)

plt.plot(ypred, "r--", label="GPy")

m.optimize(optimizer="lbfgs")

#print m

ypred, ysigma = m.predict(Xnew=iop_new, kern=kernel)

plt.plot(ypred, "c-", label="GPy2")

plt.legend()
plt.show()

m.optimize_restarts(num_restarts=4)

ypred, ysigma = m.predict(Xnew=iop_new, kern=kernel)

m.plot(plot_limits=(-2.0, 5.0))
