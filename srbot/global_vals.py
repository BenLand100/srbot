import pyautogui
import numpy as np

from .bitmap import load_image,find_bitmap

#global bitmaps
minimap_mask = load_image('minimap_mask.png')[:,:,0] == 255
anchor = load_image('anchor.png') #image (always) on the client's banner

# misc useful coordinates
client_pos = [0,0] #set by target() used throughout.
w,h = 765,503
msxs,msxe,msys,msye = 5,517,5,337
msw,msh = (msxe-msxs+1),(msye-msys+1)
msxc,msyc = msxs+msw/2,msys+msh/2
ivxs,ivxe,ivys,ivye = 560,737,207,460
ivw,ivh = (ivxe-ivxs+1),(ivye-ivys+1)
mmxs,mmxe,mmys,mmye = 548,726,3,165
mmxc,mmyc=647,85

def target():
    '''looks for the client and caches its location'''
    pyautogui.PAUSE = 0.1
    desktop = np.asarray(pyautogui.screenshot())
    pts = find_bitmap(anchor,desktop)
    assert len(pts)==1,'window ambiguious or not found'
    client_pos[0],client_pos[1] = pts[0]+[0,anchor.shape[1]]
