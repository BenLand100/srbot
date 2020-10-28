#    Copyright 2020 by Benjamin J. Land (a.k.a. BenLand100)
#
#    This file is part of srbot.
#
#    srbot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    srbot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with srbot.  If not, see <https://www.gnu.org/licenses/>.

import numpy as np

def rgb2hsl(x):
    '''converts an [...,3] RGB image to an [...,3] HSL image'''
    hsl = np.empty_like(x,dtype='float32')
    x = np.asarray(x,dtype='float32')/255.0
    m = np.min(x,axis=-1)
    M = np.max(x,axis=-1)
    c = M-m
    dg = c==0
    ndg = ~dg
    r = x[...,0]
    g = x[...,1]
    b = x[...,2]
    hsl[...,2]=(M+m)/2
    hsl[ndg,1]=c[ndg]/(1.0-np.abs(2.0*hsl[ndg,2]-1.0))
    maskr = np.logical_and(np.equal(r,M),ndg)
    hsl[maskr,0] = (g[maskr] - b[maskr]) / c[maskr] / 6.0 + np.where(g[maskr] < b[maskr],1.0,0.0)
    maskg = np.logical_and(np.equal(g,M),ndg)
    hsl[maskg,0] = (b[maskg] - r[maskg]) / c[maskg] / 6.0 + 1.0/3.0
    maskb = np.logical_and(np.equal(b,M),ndg)
    hsl[maskb,0] = (r[maskb] - g[maskb]) / c[maskb] / 6.0 + 2.0/3.0
    hsl[dg,0] = 0.0
    hsl[dg,1] = 0.0
    return hsl

def hsl_val(a,b,a_rgb=True,b_rgb=True):
    '''returns the change in hue,sat,lum for each coordinate in a,b
       a,b can be preconverted to hsl and the *_rgb kwarg set to save time'''
    a = rgb2hsl(a) if a_rgb else a
    b = rgb2hsl(b) if b_rgb else b
    dh = np.abs(a[...,0]-b[...,0])
    dh[dh>0.5] = 1.0 - dh[dh>0.5]
    ds = np.abs(a[...,1]-b[...,1])
    dl = np.abs(a[...,2]-b[...,2])
    return dh,ds,dl
def hsl_cmp(a,b,tol,a_rgb=True,b_rgb=True):
    '''returns a boolean mask for values that satisfy tolerange requirements between a,b
       tolerance requires difference between hue,sat,lum to be separately less than tol
       a,b can be preconverted to hsl and the *_rgb kwarg set to save time'''
    dh,ds,dl = hsl_val(a,b,a_rgb,b_rgb)
    try:
        return np.logical_and(dh < tol[0],np.logical_and(ds < tol[1],dl < tol[2]))
    except TypeError:
        return np.logical_and(dh < tol,np.logical_and(ds < tol,dl < tol))

def dist_val(a,b):
    '''returns the sum of squared RGB color distance for each coordinate of a,b normalized such that dist(black,white)=1.0'''
    return np.sum(np.square(a-b),axis=-1) / (3*255**2.0)
def dist_cmp(a,b,tol):
    '''returns a boolean mask for values that satisfy tolerange requirements between a,b
       tolerance requires the quadrature sum of channel distances to be less than tol'''
    return dist_val(a,b) < tol*tol

def diff_val(a,b):
    '''returns the sum of absolute RGB distance for each coordinate of a,b normalized such that dist(black,white)=1.0'''
    return np.sum(np.abs(a-b),axis=-1) / (3*255)
def diff_cmp(a,b,tol):
    '''returns a boolean mask for values that satisfy tolerange requirements between a,b
       tolerance requires the sum of channel distances to be less than tol'''
    return diff_val(a,b) < tol

def get_val(mode):
    '''return the distance function for the given color mode'''
    if mode == 'diff':
        val = diff_val
    elif mode == 'dist':
        val = dist_val
    elif mode == 'hsl':
        val = hsl_val
    else:
        raise RuntimeError('Unknown tolerance mode: %s'%mode)
    return val
def get_cmp(mode):
    '''return the comparator function for the given color mode'''
    if mode == 'diff':
        cmp = diff_cmp
    elif mode == 'dist':
        cmp = dist_cmp
    elif mode == 'hsl':
        cmp = hsl_cmp
    else:
        raise RuntimeError('Unknown tolerance mode: %s'%mode)
    return cmp

def find_colors(color,region,tol=0.1,mode='dist'):
    '''finds all instance of color in region'''
    cmp = get_cmp(mode)
    mask = cmp(region,color,tol)
    found = np.argwhere(mask)[:,[1,0]]
    return found
