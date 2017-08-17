# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:45:17 2017

@author: fviramontes8
"""

import numpy as np
np.set_printoptions(threshold=np.inf)

import matplotlib.pyplot as plt

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

#x = np.array(list(range(100)))
x = np.random.random(200)
#print x

X= buffer(x, 4, 3, opt="nodelay")
#print "Data: ", X


inputing, outputing = IOfy(X)

Ytr = np.array(outputing)
Xtr = bottom_row_ones(X)
#print "Training X: \n", Xtr
#print "Observations:\n", Ytr
gamma = 0.001
w = np.linalg.inv(Xtr.dot(Xtr.T) + gamma * np.eye(4)).dot(Xtr.dot(Ytr.T))

#print "Weights:\n", w

X_data = list(np.random.random(200))
#print "Data:\n" , X_data
Xdata = buffer(X_data, 4, 3, "nodelay")
#print "Molded data:\n", Xdata
inputin, outputin = IOfy(Xdata)
#print "Inputin:\n", inputin
#print "Outputin:\n", outputin

Ytst = np.array(outputin)
Xtst = bottom_row_ones(Xdata)
#print "X test:\n", Xtst
#print "Y test:\n", Ytst

y =(w.T).dot(Xtst)
#print y

plt.plot(Ytst, "b-")
plt.plot(y, "g-")

