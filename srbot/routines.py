import numpy as np

from .global_vals import *
from .io import *
from .color import *
from .bitmap import *
from .minimap import *
from .algorithm import *

loginscreen = load_image('loginscreen.png')
existinguser = load_image('existinguser.png')
no_user_pass = load_image('no_user_pass.png')
use_booth = load_image('use_booth.png')
bank_window = load_image('bank_window.png')
store_all = load_image('store_all.png')
climb = load_image('climb.png')
run_already_on = load_image('run_on.png')
drop_txt = load_image('drop.png')

def login_screen(client=None):
    if client is None:
        client = get_client()
    return len(find_bitmap(loginscreen,client)) > 0

def login(client=None):    
    '''basic login routine - assumes current state is login window'''
    try:
        import creds
    except:
        print('Please make creds.py with username and password variables!')
        raise
    if client is None:
        client = get_client()
    print('logging in')
    if len(find_best_bitmap(existinguser,client,tol=0.25,mode='xcorr')) > 0:
        click_mouse(463,291)
        sleep(2.0)
    click_mouse(355,240)
    sleep(2.0)
    client = get_client()
    if len(find_bitmap(no_user_pass,client)) > 0:
        send_keys('%s\n%s'%(creds.username,creds.password))
    sleep(1.0)
    click_mouse(305,326)
    sleep(5.0)
    click_mouse(401,335)
    sleep(5.0)

def count_inv(mask=False,color=[1,0,0],tol=0.02):
    '''counts the number of items with the given color (default is shadow, so all) in the inventory'''
    inventory = get_inventory()
    w,h = 42,36
    grid = [[len(find_colors(color,inventory[h*i:h*i+h,w*j:w*j+w],tol=tol))>0 for i in range(7)] for j in range(4)]
    return grid if mask else np.count_nonzero(grid)

def drop_all(color=[1,0,0],tol=0.02):
    while True:
        inventory = get_inventory()
        drop = find_colors(color,inventory,tol=tol)
        if len(drop) > 50:
            np.random.shuffle(drop)
            click_mouse(*(drop[0]+[ivxs,ivys]),left=False)
            sleep(0.2)
            client = get_client()
            found = find_bitmap(drop_txt,client,tol=0.02)
            if len(found) > 0:
                click_mouse(*(found[0]+[10,5]))
            else:
                move_mouse(*(drop[0]+[ivxs,ivys-100]))
            sleep(0.5)
        else:
            break

bank_floor_colors = [[130,60,47],[170,104,80]]
def open_bank():
    '''opens bank window if not already open - FALADOR WEST ONLY
       bank is found by proximity of npc points to a unique bank floor color
       booth is found by proximity of two colors on the booth (dark top and light mid area)
       right clicks booth and checks for Use Quickly, tries next option if not found'''
    mainscreen = get_mainscreen()
    if len(find_bitmap(bank_window,mainscreen)) > 0:
        return True
    minimap = get_minimap()
    npc_points = find_colors([255,255,0],minimap,tol=0.05,mode='hsl')
    bank_points = np.concatenate([find_colors(bank_floor,minimap,tol=0.085,mode='hsl') for bank_floor in bank_floor_colors])
    print('Bank points:',len(bank_points))
    clusters,counts = cluster(bank_points)
    if len(counts) < 1 or np.count_nonzero(counts>20) < 1:
        bank_points = np.asarray([])
    else:
        bank_points = clusters[np.random.choice(np.nonzero(counts>20)[0])]
    print('Clustered bank points:',len(bank_points))
    bank_points = filter_near(npc_points,bank_points,6)
    print('Points near NPCs:',len(bank_points))
    np.random.shuffle(bank_points)
    if len(bank_points) < 15:
        return False
    click_mouse(*(bank_points[0]+[mmxs,mmys-8]))
    sleep(1.0)
    flag_wait()
    sleep(1.0)
    mainscreen = get_mainscreen()
    pa = find_colors([74,70,70],mainscreen,tol=0.02,mode='hsl')
    pb = find_colors([118,96,68],mainscreen,tol=0.02,mode='hsl')
    points = filter_near(pa,pb,20)
    points = closest_shuffle([msxc-msxs,msyc-msys],points,15)
    for point in points[:min(5,len(points))]:
        click_mouse(*point,left=False)
        sleep(0.05)
        use = find_bitmap(use_booth,get_mainscreen())
        if len(use) > 0:
            click_mouse(*(use[0]+[10,10]))
            flag_wait()
            return True
        move_mouse(*(point+[0,-25]))
    return False
            
def deposit_all(ignore_first=False):
    '''searches for border colors in inventory and deposits them all to bank
       assumes bank window already open'''
    mainscreen = get_mainscreen()
    while len(find_bitmap(bank_window,mainscreen)) > 0:
        inventory = get_inventory()
        found = find_colors([1,0,0],inventory)
        if ignore_first:
            found = filter_far(found,[[586-ivxs,230-ivys]],25)
        if len(found):
            np.random.shuffle(found)
            click_mouse(*found[0]+[ivxs,ivys],left=False)
            sleep(0.5)
            client = get_client()
            opt = find_bitmap(store_all,client)
            if len(opt):
                click_mouse(*opt[0]+[10,10])
                sleep(1.0)
            else:
                move_mouse(*found[0]+[ivxs,ivys-15])
        else:
            break
        mainscreen = get_mainscreen()
    
tabs = {'settings':[681,484],'inventory':[645,187],'stats':[584,190]}
def open_tab(tab):
    if tab not in tabs:
        raise RuntimeException('Unknown tab %s'%tab)
    click_mouse(*tabs[tab])
    sleep(0.5)

def run_on(restore_tab='inventory'):
    open_tab('settings')
    inventory = get_inventory()
    if len(find_bitmap(run_already_on,inventory,tol=0.02)) == 0:
        click_mouse(646,435)
        sleep(0.5)
    open_tab(restore_tab)