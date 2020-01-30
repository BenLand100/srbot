import pyautogui
import numpy as np

from .io import *
from .color import *
from .algorithm import *

flag = load_image('flag.png')

def get_compass_angle():
    compass = get_compass()
    red = find_colors([238,0,0],compass,tol=0.2)-np.asarray(compass.shape)[[1,0]]/2
    clusters,counts = cluster(red,radius=5)
    tips = clusters[counts<5]
    if np.count_nonzero(counts<5) > 0:
        meanxy = np.asarray([np.mean(tip.T,axis=1) for tip in clusters[counts<5]])
        meanxy = np.mean(meanxy.T,axis=1)
        direction = [-1,1]*meanxy/np.sqrt(np.sum(np.square(meanxy)))
        return np.mod(np.arctan2(direction[1],direction[0])/np.pi*180-90,360)
    else:
        return 0

def set_compass_angle(angle,tol=15,click=True):
    if click:
        click_mouse(mmxc,mmyc)
    pyautogui.PAUSE = 0.001
    left = False
    while True:
        deg = get_compass_angle()
        deg = np.mod(deg-angle,360)
        if deg < tol or deg > 360-tol:
            return True
        if deg < 360 and deg > 180:
            left = True
        if deg < 180 and deg > 0:
            left = False
        if left:
            pyautogui.keyDown('left')
            sleep(0.2*np.random.random())
            pyautogui.keyUp('left')
        else:
            pyautogui.keyDown('right')
            sleep(0.2*np.random.random())
            pyautogui.keyUp('right')
    pyautogui.PAUSE = 0.1
    
def polish_minimap(min_same=28,horizontal=True,bounds=30,click=True):
    if click:
        click_mouse(mmxc,mmyc)
    bestn = 0
    left = True
    pyautogui.PAUSE = 0.001
    while True:
        deg = get_compass_angle()
        left = np.random.random() < 0.5
        if deg < 360-bounds and deg > 180:
            left = True
        if deg < 180 and deg > bounds:
            left = False
        if left:
            pyautogui.keyDown('left')
            sleep(0.1*np.random.random())
            pyautogui.keyUp('left')
        else:
            pyautogui.keyDown('right')
            sleep(0.1*np.random.random())
            pyautogui.keyUp('right')
            
        minimap = get_minimap()
        walls = find_colors([238,238,238],minimap,tol=0.05)
        vals,counts = np.unique(walls[:,1 if horizontal else 0],return_counts=True)
        maxn = np.max(counts)
        print(maxn)
        if maxn >= min_same and (deg > 360-bounds or deg < bounds):
            break
    pyautogui.PAUSE = 0.1

def flag_wait(init=2.0,step=0.2,post=1.5,imax=50):
    '''sleeps the init time, then each step while the flag stem is visible up to imax times, finally sleeping post'''
    sleep(init)
    i = 0
    while True:
        minimap = get_minimap()
        i = i+1
        if i > imax:
            break
        if len(find_bitmap(flag,minimap)) == 0:
            sleep(post)
            break
        sleep(step)