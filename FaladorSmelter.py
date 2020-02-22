#!/usr/bin/env python3

from srbot import *
import argparse

#Smelting script banks Falador west and uses Falador furnace

east_road = [121,119,97]

parser = argparse.ArgumentParser('Smelt bars from Falador West Bank')
parser.add_argument('item',help='bronze,iron,steel,mith,gold,bracelets')

args = parser.parse_args()

if args.item == 'bracelets':
    #for bracelets
    bar = load_image('gold_bar.png')
    inputs = [(1,bar)]
    bar_pos = np.asarray([130,282]) #location of jewlery icon
    using_mold = True #changes behavior to withdraw bars and create jewlery
elif args.item == 'gold':
    #for gold
    bar = load_image('gold_bar.png')
    ore = load_image('gold_ore.png')
    inputs = [(1,ore)]
    bar_pos = np.asarray([310,405])
    using_mold = False
elif args.item == 'iron':
    #for iron
    bar = load_image('iron_bar.png')
    ore = load_image('iron_ore.png')
    inputs = [(1,ore)]
    bar_pos = np.asarray([100,405])
    using_mold = False
elif args.item == 'steel':
    #for steel
    coal = load_image('coal_ore.png')
    ore = load_image('iron_ore.png')
    inputs = [(1,ore),(2,coal)]
    bar_pos = np.asarray([259,410])
    using_mold = False
elif args.item == 'mith':
    #for mith
    coal = load_image('coal_ore.png')
    ore = load_image('mith_ore.png')
    inputs = [(1,ore),(4,coal)]
    bar_pos = np.asarray([361,410])
    using_mold = False
elif args.item == 'bronze':
    #for bronze 
    tin = load_image('tin_ore.png')
    copper = load_image('copper_ore.png')
    inputs = [(1,copper),(1,tin)]
    bar_pos = np.asarray([50,405]) #position of bar on furnace menu 
    using_mold = False

def count_inputs():
    inventory = get_inventory()
    return np.asarray([len(find_bitmap(bmp,inventory,mode='hsl',tol=(0.1,0.2,0.2)))//unit for unit,bmp in inputs])
        
furnace_icon = load_image('furnace_icon.png')
smelt_x = load_image('smelt_x.png')
def go_smelt():
    '''finds furnace icon on minimap and walks to it, then locates furnace by proximity of metal and fire colors
       if found, starts smelting and waits until out of rocks or timed out'''
    minimap = get_minimap()
    icon = find_best_bitmap(furnace_icon,minimap,tol=0.2,mode='xcorr')
    #icon = find_colors(np.asarray([255,115,41]),minimap,tol=0.05,mode='hsl')
    icon = filter_radius(icon,[mmxc-mmxs,mmyc-mmys],70) 
    np.random.shuffle(icon)
    print('Furnace icon points:',len(icon))
    if len(icon) == 1:
        click_mouse(*(icon[0]+(mmxs+4,mmys)))
        set_compass_angle(45,tol=7,click=False)
        flag_wait()    
        mainscreen = get_mainscreen()
        fire = find_colors([192,79,48],mainscreen,mode='hsl',tol=0.04)
        furnace = find_colors([192,79,48],mainscreen,mode='hsl',tol=0.04)
        furnace = filter_near(furnace,fire,10)
        np.random.shuffle(furnace)
        if len(furnace) > 0:
            print('Found furnace, starting smelting...')
            if not using_mold:
                click_mouse(*(furnace[-1]+[msxs+15,msys-15]))
            else:
                inventory = get_inventory()
                bar_loc = find_bitmap(bar,inventory,tol=0.2,mode='hsl')
                if len(bar_loc) == 0:
                    return False
                np.random.shuffle(bar_loc)
                move_mouse(*(bar_loc[0]+[ivxs+10,ivys+10]))
                sleep(0.5)
                click_mouse(*(bar_loc[0]+[ivxs+10,ivys+10]))
                sleep(0.75)
                click_mouse(*(furnace[-1]+[msxs+15,msys-15]))
            flag_wait()
            inv = count_inputs()
            sleep(1.0)
            move_mouse(*bar_pos)
            sleep(0.5)
            click_mouse(*bar_pos,left=False)
            sleep(0.5)
            client = get_client()
            smelt_pos = find_bitmap(smelt_x,client)
            if len(smelt_pos) < 1:
                print('No smelt option!')
                return True
            click_mouse(*smelt_pos[0])
            sleep(0.75)
            send_keys(str(np.min(inv))+'\n')
            polish_minimap(min_same=27,horizontal=False,click=False)
            run_on()
            i = 0
            while True:
                sleep(0.5)
                i = i+1
                cur_inv = count_inputs()
                if np.any(cur_inv != inv):
                    inv = cur_inv
                    i = 0
                if np.sum(cur_inv) == 0:
                    print('Success, getting more materials!')
                    return True
                if i > 6:
                    print('Timed out, trying again')
                    return True
        return True # didn't smelt but don't run away...
    return False
    
target()
click_mouse(mmxc,mmyc)
done = False
total_trips = 0
last_smelt = mark_time()
while True:
    client = get_client()
    if len(find_bitmap(loginscreen,client)) > 0:
        login()
        continue
    if mark_time() - last_smelt > 10*60:
        raise RuntimeError('Been a loooong time since a smelt. Probably horribly lost. Maybe.')
        
    inv = count_inputs()
    print('inventory',inv)
    if np.all(inv != 0): #ready to smelt
        done = False
        if go_smelt():
            last_smelt = mark_time()
        else:
            minimap = get_minimap()
            east = filter_radius(find_colors(east_road,minimap,tol=0.08),[mmxc-mmxs,mmyc-mmys],55)
            print('Moving east:',len(east))
            if len(east):
                click_mouse(*(east[np.argsort(-east[:,0]+np.abs(east[:,1]-mmyc+mmys+10)*0.5)[0]]+(mmxs,mmys)))
                sleep(1.0)
            else:
                print('Lost looking for furnace!')
    else: #go to bank
        if done:
            break
        if open_bank():
            deposit_all(ignore_first=using_mold)
            total_trips = total_trips + 1
            print('Completed %i invetories'%total_trips)
            done = True
            sleep(0.5)
            mainscreen = get_mainscreen()
            batch = np.sum([unit for unit,_ in inputs])
            for unit,bmp in inputs:
                coords = find_bitmap(bmp,mainscreen,mode='hsl',tol=0.2)+[10,10]
                print('raw found:',len(coords))
                np.random.shuffle(coords)
                if len(coords) > 0:
                    done = False
                    click_mouse(*(coords[0]+[msxs,msys]),left=False)
                    sleep(0.5)
                    click_mouse(*(coords[0]+[msxs,msys]+[0,87]))
                    sleep(1.0)
                    send_keys('%i'%(unit*((28 if not using_mold else 27)//batch)))
                    sleep(0.5)
                    send_keys('\n')
                    sleep(0.5)
                else:
                    print('Out of supplies!')
            sleep(1.0)
        else:                
            minimap = get_minimap()
            east = filter_radius(find_colors(east_road,minimap,tol=(0.05,0.1,0.1),mode='hsl'),[mmxc-mmxs,mmyc-mmys],50)
            print('Moving west:',len(east))
            if len(east):
                click_mouse(*(east[np.argsort(east[:,0]+np.abs(east[:,1]-mmyc+mmys)*0.5)[0]]+(mmxs,mmys)))
                sleep(1.0)
            else:
                print('Lost looking for bank!')


# In[ ]:




