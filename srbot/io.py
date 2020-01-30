import pyautogui
import time
import numpy as np

from .global_vals import *

def sleep(sec):
    time.sleep(sec)
    
def mark_time():
    return time.monotonic()
    
def move_mouse(x,y,speed=1.0):
    '''moves the mouse to a point'''
    cx,cy = pyautogui.position()
    ex,ey = x+client_pos[0],y+client_pos[1]
    dt = np.sqrt((cx-x)**2.0+(cy-y)**2.0)/(speed*1000)
    pyautogui.moveTo(ex,ey,dt,pyautogui.easeOutQuad)

def click_mouse(x,y,left=True,speed=1.0):
    '''moves to and clicks a point'''
    move_mouse(x,y,speed=speed)
    pyautogui.click(button='left' if left else 'right')
    
def send_keys(text,speed=1.0):
    '''sends text to the client (\n for enter)'''
    pyautogui.typewrite(text,interval=0.05*speed)
    
#functions to grab images of client - smaller region is faster maybe?
def get_client():
    return np.asarray(pyautogui.screenshot(region=(client_pos[0],client_pos[1],w,h)))
def get_mainscreen():
    return np.asarray(pyautogui.screenshot(region=(client_pos[0]+msxs,client_pos[1]+msys,msxe-msxs+1,msye-msys+1)))
def get_uptext(width=400):
    return np.asarray(pyautogui.screenshot(region=(client_pos[0]+7,client_pos[1]+7,width-7+1,23-7+1)))
def get_minimap():
    return np.asarray(pyautogui.screenshot(region=(client_pos[0]+mmxs,client_pos[1]+mmys,mmxe-mmxs+1,mmye-mmys+1)))
def get_compass():
    return np.asarray(pyautogui.screenshot(region=(client_pos[0]+mmxs,client_pos[1]+mmys,37,35)))
def get_inventory():
    return np.asarray(pyautogui.screenshot(region=(client_pos[0]+ivxs,client_pos[1]+ivys,ivxe-ivxs+1,ivye-ivys+1)))