import numpy as np
from PIL import Image

from .color import *

import os.path
bmp_root = os.path.join(os.path.dirname(__file__),'bmp')

def load_image(fname):
    if os.path.exists(fname):
        return np.asarray(Image.open(fname))[...,:3] #strip alpha
    else:
        return np.asarray(Image.open(os.path.join(bmp_root,fname)))[...,:3] #strip alpha

def img_norm(x):
    x = x - np.mean(x)
    return x / np.sqrt(np.sum(np.square(x)))

def cross_correlate(bmp,region):
    result = np.zeros(region.shape[:2])
    for i in range(3): #compute each color channel
        haystack = region[...,i]
        needle = bmp[...,i]

        haystack = img_norm(haystack)
        needle = img_norm(needle)

        hsdim = np.asarray(haystack.shape)
        nldim = np.asarray(needle.shape)

        haystack = np.pad(haystack,[(0,x+y) for x,y in zip(hsdim,nldim)],'constant')
        needle = np.pad(needle,[(0,2*x) for x,y in zip(hsdim,nldim)],'constant')

        fhs = np.fft.rfft2(haystack)
        fnl = np.fft.rfft2(needle)

        result += np.fft.irfft2(fhs*np.conj(fnl))[:hsdim[0],:hsdim[1]]
    return result

def find_bitmap_prob(bmp,region,mask=None,mode='dist'):
    '''compare to matchTemplate in opencv - returns the distance between bmp and every possible location in region'''
    hr,wr=region.shape[:2]
    hs,ws=bmp.shape[:2]
    if mode == 'xcorr':
        assert mask is None,'cross correlation does not support masks'
        return cross_correlate(bmp,region)
    elif mode == 'hsl': #N.B. historically this /only/ compares hues
        bmp = rgb2hsl(bmp)
        region = rgb2hsl(region)
        val = get_val(mode)
        if mask is not None:
            return np.asarray([[np.sum(val(bmp[mask],region[i:i+hs,j:j+ws][mask],a_rgb=False,b_rgb=False)[0]) for j in range(wr-ws)] for i in range(hr-hs)])
        else:
            return np.asarray([[np.sum(val(bmp,region[i:i+hs,j:j+ws],a_rgb=False,b_rgb=False)[0]) for j in range(wr-ws)] for i in range(hr-hs)])
    else:
        val = get_val(mode)
        if mask is not None:
            return np.asarray([[np.sum(val(bmp[mask],region[i:i+hs,j:j+ws][mask])) for j in range(wr-ws)] for i in range(hr-hs)])
        else:
            return np.asarray([[np.sum(val(bmp,region[i:i+hs,j:j+ws])) for j in range(wr-ws)] for i in range(hr-hs)])

def find_best_bitmap(bmp,region,tol=0.2,mode='hsl'):
    '''returns the match position of all matches satisfying the tolerance requirement'''
    if mode == 'xcorr':
        xcorr = cross_correlate(bmp,region)
        found = np.asarray(np.nonzero(xcorr > tol))
        return found[[1,0]].T
    else:
        probs = find_bitmap_prob(bmp,region,mode=mode)
        found = np.asarray(np.nonzero(probs < tol))
        return found[[1,0]].T
        
def find_bitmap(bmp,region,tol=0.01,mask=None,mode='dist'):
    '''similar to find_bitmap_prob but uses the heuristic that each pixel must match better than some tolerance.
       Only returns the coordinates of potential matches.'''
    xs,ys=0,0
    hr,wr=region.shape[:2]
    hs,ws=bmp.shape[:2]
    cmp = get_cmp(mode)
    if mask is None:
        candidates = np.asarray(np.nonzero(cmp(bmp[0,0],region[:-hs,:-ws],tol)))
    else:
        candidates = np.asarray(np.nonzero(np.ones((hr-hs+1,wr-ws+1))))
    for i in np.arange(0,hs):
        for j in np.arange(0,ws):
            if (mask is None and i==0 and j==0) or (mask is not None and not mask[i,j]):
                continue
            view = region[candidates[0]+i,candidates[1]+j,:]
            passed = cmp(bmp[i,j],view,tol)
            candidates = candidates.T[passed].T
        
    return candidates[[1,0],:].T

def uptext_mask(uptext,width=None):
    '''provides a black-on-white mask of an uptext image for OCR'''
    uptext = uptext[:,:width] if width is not None else uptext
    white = find_colors([225,225,225],uptext,tol=0.1)
    cyan = find_colors([0,225,225],uptext,tol=0.1)
    yel = find_colors([225,225,0],uptext,tol=0.1)
    thresh = np.full_like(uptext,255)
    
    for c in [white,cyan,yel]:
        thresh[c[:,1],c[:,0]] = [0,0,0]

    return uptext,thresh