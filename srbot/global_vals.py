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

import pyautogui
import numpy as np

from .bitmap import load_image,find_bitmap

#global bitmaps
minimap_mask = load_image('minimap_mask.png')[:,:,0] == 255
anchor = load_image('anchor.png') #image (always) on the client's banner

# misc useful coordinates
client_pos = [0,0] #set by target() used throughout.
w,h = 765,503
xoff,yoff = -1,-1
msxs,msxe,msys,msye = 5+xoff,515+xoff,5+yoff,337+yoff
msw,msh = (msxe-msxs+1),(msye-msys+1)
msxc,msyc = msxs+msw/2,msys+msh/2
ivxs,ivxe,ivys,ivye = 560+xoff,737+xoff,207+yoff,460+yoff
ivw,ivh = (ivxe-ivxs+1),(ivye-ivys+1)
mmxs,mmxe,mmys,mmye = 548+xoff,726+xoff,3+yoff,165+yoff
mmxc,mmyc=mmxs+101,mmys+82

def target():
    '''looks for the client and caches its location'''
    pyautogui.PAUSE = 0.1
    desktop = np.asarray(pyautogui.screenshot())
    pts = find_bitmap(anchor,desktop)
    assert len(pts)==1,'window ambiguious or not found'
    client_pos[0],client_pos[1] = pts[0]+[-520,0] 
