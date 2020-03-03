#!/usr/bin/env python3

from srbot import *
import argparse


parser = argparse.ArgumentParser('Mines in West Falador mine and bankes in Falador West Bank')
parser.add_argument('-m','--max-mith',type=int,default=0,help='maximum mith to mine per trip')

args = parser.parse_args()

max_mith = 0

mm_cave = [121,93,28]
mm_ladder = [85,49,0]
mm_bank = [185,174,147]
mm_grass = [132,138,48]
mm_rock = [95,94,95]

mine_icon = load_image('mine_icon.png')
bank_icon = load_image('bank_icon.png')

def mine(points):
    counts = count_inv(color=[119,96,67],tol=0.02)
    clusters,_ = cluster(points,10)
    points = np.asarray([np.mean(cluster,axis=0) for cluster in clusters])
    if len(points) == 0:
        return False
    elif len(points) == 1:
        point = points[0]
    else:
        point = closest_exp(np.asarray([msw/2-150*((mith_count+coal_count)/28)**3.5,msh/2],dtype=np.float64),points,10)
    point = point+[msxs,msys]+np.random.normal(0,5,size=(2,))
    move_mouse(*point)
    sleep(0.05)
    uptext = get_uptext(width=80)
    cyan = find_colors([0,238,238],uptext,mode='hsl',tol=0.15)
    print('cyan',len(cyan))
    if len(cyan) > 50:
        click_mouse(*point)
    else:
        return False
    for i in range(40):
        sleep(0.05)
        if np.any(count_inv(color=[119,96,67],tol=0.02) != counts):
            return True
    return False

def find_rocks():
    mainscreen = get_mainscreen()
            
    #gas = find_colors([163,151,126],mainscreen,mode='hsl',tol=(0.08,0.1,0.2))
    
    if mith_count < max_mith:
        a = find_colors([84,85,126],mainscreen,tol=(0.07,0.1,0.1),mode='hsl')
        b = find_colors([45,45,66],mainscreen,tol=(0.07,0.1,0.1),mode='hsl')
        mith = filter_near(a,b,4)
        #mith = filter_far(mith,gas,50)

    a = find_colors([63,63,41],mainscreen,tol=(0.07,0.1,0.05),mode='hsl')
    b = find_colors([35,35,23],mainscreen,tol=(0.07,0.1,0.05),mode='hsl')
    coal = filter_near(a,b,4)
    #coal = filter_far(coal,gas,50)
    
    if mith_count < max_mith and len(mith) > 20:
        print('mining mith')
        rocks = mith
    elif len(coal) > 100:
        print('mining coal')
        rocks = coal
    else:
        print('no rocks!')
        rocks = None
        
    return rocks

target()
click_mouse(mmxc,mmyc)
total_trips = 0
total_mith,total_coal = 0,0
start_time = mark_time()
last_mine = mark_time()
unsuccessful_mines = 0
while True:
    if login_screen():
        login()
        continue
    #if mark_time()-last_mine > 10*60:
    #    raise RuntimeError('Haven\'t mined in 10 minutes, giving up because something ain\'t right.')
    inv_full = count_inv() == 28
    minimap = get_minimap()
    map_dark = find_colors([0,0,0],minimap,0.001)
    underground = len(map_dark) > 5000
    mith_count = count_inv(color=[84,85,126],tol=0.1)
    coal_count = count_inv(color=[53,53,37],tol=0.015)
    #print('%i mith %i coal'%(mith_count,coal_count))
    if inv_full: #go to bank
        if underground: #going to bank underground
            print('leaving mine')
            b = find_colors(mm_ladder,minimap,tol=0.05,mode='dist')
            b = filter_near(b,map_dark,20)
            b = filter_radius(b,[mmxc-mmxs,mmyc-mmys],55)
            if len(b) > 0:
                b = b[b[:,0]<(mmxc-mmxs+20)]
            clusters,counts = cluster(b,radius=2)
            mask = counts < 200
            icon = find_best_bitmap(mine_icon,minimap,tol=0.2,mode='xcorr')
            print(len(icon),'icons')
            if len(icon) == 0 and len(counts) > 0 and np.max(counts) > 20:
                clusters = clusters[mask]
                counts = counts[mask]
                ladder = clusters[np.argmax(counts)]
                pt = np.mean(ladder,axis=0)
                print('found ladder',pt)
                click_mouse(*(pt+[mmxs+10,mmys]))
                flag_wait()
                
                mainscreen = get_mainscreen()
                a = find_colors([104,64,12],mainscreen,tol=0.02)
                b = find_colors([105,77,37],mainscreen,tol=0.02)
                c = find_colors([128,104,54],mainscreen,tol=0.02)
                ladder = filter_near(a,b,10)
                ladder = filter_near(ladder,c,10)
                if len(ladder) > 0:
                    ladder = closest_shuffle([msxc-msxs,msyc-msys],ladder,15)
                    for point in ladder[:min(5,len(ladder))]:
                        #point = np.random.random(2)*[100,100]-[50,50]+[msxc,msyc]
                        point = point + [msxs,msys]
                        click_mouse(*point,left=False)
                        sleep(0.05)
                        pt = find_bitmap(climb,get_mainscreen())
                        if len(pt) > 0:
                            click_mouse(*(pt[0]+[10,10]))
                            run_on()
                            break
                        move_mouse(*(point+[0,-25]))
            else:
                a = find_colors(mm_cave,minimap,tol=0.12,mode='dist')
                a = filter_radius(a,[mmxc-mmxs,mmyc-mmys],55)
                pt = closest([mmxc-mmxs-50,mmyc-mmys],a)
                click_mouse(*(pt+[mmxs,mmys]+np.random.normal(0,3,size=2)))
                sleep(0.2)
        else: #going to bank above ground
            bank = find_best_bitmap(bank_icon,minimap,tol=0.1,mode='xcorr')
            bank = filter_radius(bank,[mmxc-mmxs,mmyc-mmys],65)
            npc = find_colors([238,238,0],minimap,mode='hsl',tol=0.15)
            npc = filter_radius(npc,[mmxc-mmxs,mmyc-mmys],65)
            clusters,counts = cluster(npc,radius=5)
            if len(counts) and np.max(counts) > 50:
                click_here = clusters[np.argmax(counts)]-[0,7]
            elif len(bank):
                click_here = bank
            else:
                print('trying to find bank')
                angle = np.random.normal(50+180,10)/180*np.pi
                r = np.random.normal(60,10)
                target = [mmxc-mmxs+r*np.cos(angle),mmyc-mmys+r*np.sin(angle)]
                grass = find_colors(mm_grass,minimap,tol=(0.05,0.2,0.2),mode='hsl')
                if len(grass) > 0:
                    point = closest(target,grass)
                    click_mouse(*(point+[mmxs,mmys]))
                    sleep(1.5)
                continue
            
            print('walking to bank')
            np.random.shuffle(click_here)
            point = click_here[0]
            dist = np.sqrt(np.sum(np.square(point-[mmxc-mmxs,mmyc-mmys])))
            print('bank dist',dist)
            click_mouse(*(point+[mmxs,mmys]))
            if dist > 70:
                flag_wait()
                sleep(10.0)
            flag_wait()
            sleep(1.0)
            mainscreen = get_mainscreen()
            a = find_colors([125,101,71],mainscreen,tol=0.02,mode='hsl')
            b = find_colors([143,116,82],mainscreen,tol=0.02,mode='hsl')
            points = filter_near(a,b,40)
            points = closest_shuffle([msxc-msxs,msyc-msys],points,25)
            for point in points[:min(5,len(points))]:
                click_mouse(*point,left=False)
                sleep(0.05)
                use = find_bitmap(use_booth,get_client())
                if len(use) > 0:
                    click_mouse(*(use[0]+[10,10]))
                    flag_wait()
                    sleep(1.0)
                    deposit_all()
                    if np.random.random() < 0.5:
                        polish_minimap(min_same=27)
                    total_trips = total_trips + 1
                    total_mith += mith_count
                    total_coal += coal_count
                    total_time = mark_time()-start_time
                    print('Completed %i inventories in %0.1f hr (%i coal, %i mith; %0.2fs/ore)'%(total_trips,total_time/3600,total_coal,total_mith,total_time/(total_coal+total_mith)))
                    break
                move_mouse(*(point+[0,-25]))
            
    else: #go to mine
        if underground: #go to ore and mine
            print('looking for ore')
            rocks = find_rocks() if unsuccessful_mines < 10 else None
            if (mith_count < max_mith and np.random.random()<0.05):
                print('trying to find mith')
                center_of_dark = np.mean(map_dark-[mmxc-mmxs,mmyc-mmys],axis=0)
                if np.any(center_of_dark < 0): #not at bottom right corner
                    a = find_colors(mm_cave,minimap,tol=0.12,mode='dist')
                    a = filter_radius(a,[mmxc-mmxs,mmyc-mmys],55)
                    if len(a) > 0:
                        pt = closest([mmxc-mmxs+50,mmyc-mmys+50],a)
                        click_mouse(*(pt+[mmxs,mmys]))
                        flag_wait()
            elif rocks is None:
                print('trying to find rocks')
                rocks = find_colors(mm_rock,minimap,mode='hsl',tol=(0.08,0.2,0.2))
                if len(rocks):
                    com = np.mean(rocks,axis=0)
                    dist = np.sqrt(np.sum(np.square(rocks-com),axis=1))
                    dist_mu = 35
                    dist_sigma = 5
                    weight = np.exp(-np.square((dist-dist_mu)/dist_sigma)/2.0)
                    cumsum = np.cumsum(weight)
                    cumsum /= cumsum[-1]
                    pt = rocks[np.searchsorted(cumsum,np.random.random())]
                    click_mouse(*(pt+[mmxs,mmys]))
                    unsuccessful_mines = 0
                    flag_wait()
            else:    
                while rocks is not None:
                    if mine(rocks):
                        last_mine = mark_time()
                        unsuccessful_mines = 0
                        if count_inv() == 28:
                            break
                        rocks = find_rocks()
                    else:
                        unsuccessful_mines = unsuccessful_mines + 1
                        break
                    
        else: #go to mining guild
            if len(map_dark) < 10:
                print('trying to find ladder')
                angle = np.random.normal(60,10)/180*np.pi
                r = np.random.normal(65,10)
                target = [mmxc-mmxs+r*np.cos(angle),mmyc-mmys+r*np.sin(angle)]
                grass = find_colors(mm_grass,minimap,tol=(0.05,0.2,0.2),mode='hsl')
                if len(grass) > 0:
                    point = closest(target,grass)
                    click_mouse(*(point+[mmxs,mmys]))
                    sleep(1.5)
            else:
                center_of_dark = np.mean(map_dark-[mmxc-mmxs,mmyc-mmys],axis=0)
                dist_to_dark = np.sqrt(np.sum(np.square(center_of_dark)))
                print(dist_to_dark,center_of_dark)
                print('going to mine')
                click_mouse(*(center_of_dark+[mmxc,mmyc]))
                flag_wait()
                mainscreen = get_mainscreen()
                a = find_colors([0,0,0],mainscreen,tol=0.05)
                b = find_colors([105,77,37],mainscreen,tol=0.05)
                going_down = filter_near(b,a,10)
                if len(going_down) > 0:
                    going_down = closest_shuffle([msxc-msxs,msyc-msys],going_down,25)
                    for point in going_down[:min(5,len(going_down))]:
                        click_mouse(*point,left=False)
                        sleep(0.05)
                        pt = find_bitmap(climb,get_mainscreen())
                        if len(pt) > 0:
                            click_mouse(*(pt[0]+[10,10]))
                            run_on()
                            break
                        move_mouse(*(point+[0,-25]))
            


# In[ ]:




