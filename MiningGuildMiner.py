#!/usr/bin/env python3

from srbot import *

max_mith = 0

mm_cave = [121,93,28]
mm_ladder = [85,49,0]
mm_bank = [185,174,147]

mine_icon = load_image('mine_icon.png')

def mine(points):
    counts = count_inv(color=[119,96,67],tol=0.02)
    clusters,_ = cluster(points,10)
    points = np.asarray([np.mean(cluster,axis=0) for cluster in clusters])
    if len(points) == 1:
        point = points[0]
    else:
        point = closest_exp([msw/2,msh/2],points,10)
    move_mouse(*(point+[msxs,msys]))
    sleep(0.2)
    uptext = get_uptext(width=80)
    cyan = find_colors([0,238,238],uptext,mode='hsl',tol=0.15)
    print('cyan',len(cyan))
    if len(cyan) > 50:
        click_mouse(*(point+[msxs,msys]))
    else:
        return False
    for i in range(100):
        mainscreen = get_mainscreen()
        sleep(0.05)
        if np.any(count_inv(color=[119,96,67],tol=0.02) != counts):
            return True
    return False

target()
click_mouse(mmxc,mmyc)
total_trips = 0
last_mine = mark_time()
while True:
    if login_screen():
        login()
        continue
    if mark_time()-last_mine > 10*60:
        raise RuntimeError('Haven\'t mined in 10 minutes, giving up because something ain\'t right.')
    inv_full = count_inv() == 28
    minimap = get_minimap()
    map_dark = find_colors([0,0,0],minimap,0.001)
    underground = len(map_dark) > 5000
    mith_count = count_inv(color=[84,85,126],tol=0.1)
    coal_count = count_inv(color=[53,53,37],tol=0.015)
    print('%i mith %i coal'%(mith_count,coal_count))
    if inv_full: #go to bank
        if underground: #going to bank underground
            print('leaving mine')
            b = find_colors(mm_ladder,minimap,tol=0.05,mode='dist')
            b = filter_near(b,map_dark,20)
            b = filter_radius(b,[mmxc-mmxs,mmyc-mmys],55)
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
                click_mouse(*(pt+[mmxs,mmys]))
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
                            flag_wait()
                            sleep(0.5)
                            run_on()
                            break
                        move_mouse(*(point+[0,-25]))
            else:
                a = find_colors(mm_cave,minimap,tol=0.12,mode='dist')
                a = filter_radius(a,[mmxc-mmxs,mmyc-mmys],55)
                pt = closest([mmxc-mmxs-50,mmyc-mmys],a)
                click_mouse(*(pt+[mmxs+5,mmys+5]))
                sleep(0.2)
        else: #going to bank above ground
            bank = find_colors(mm_bank,minimap,mode='hsl',tol=(0.05,0.2,0.08))
            bank = filter_radius(bank,[mmxc-mmxs,mmyc-mmys],65)
            npc = find_colors([238,238,0],minimap,mode='hsl',tol=0.15)
            clusters,counts = cluster(npc,radius=5)
            if len(bank) and len(counts) and np.max(counts) > 50:
                npc = clusters[np.argmax(counts)]
                bank = filter_near(npc,bank,5)
            else:
                bank = []
            if len(bank) < 10:
                print('trying to find bank')
                click_mouse(*[mmxc-25+np.random.random()*4,mmyc-45+np.random.random()*5])
                sleep(1.5)
            else:
                print('walking to bank')
                np.random.shuffle(bank)
                point = bank[0]
                dist = np.sqrt(np.sum(np.square(point-[mmxc-mmxs,mmyc-mmys])))
                print('bank dist',dist)
                click_mouse(*(bank[0]+[mmxs,mmys-10]))
                if dist > 30:
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
                        total_trips = total_trips + 1
                        if np.random.random() < 0.5:
                            polish_minimap(min_same=27)
                        print('Completed %i inventories'%total_trips)
                        break
                    move_mouse(*(point+[0,-25]))
            
    else: #go to mine
        if underground: #go to ore and mine
            print('looking for ore')
            mainscreen = get_mainscreen()
            
            gas = find_colors([163,151,126],mainscreen,mode='hsl',tol=(0.08,0.1,0.2))
            
            a = find_colors([84,85,126],mainscreen,tol=(0.07,0.1,0.1),mode='hsl')
            b = find_colors([45,45,66],mainscreen,tol=(0.07,0.1,0.1),mode='hsl')
            mith = filter_near(a,b,4)
            mith = filter_far(mith,gas,50)
        
            a = find_colors([63,63,41],mainscreen,tol=(0.07,0.1,0.05),mode='hsl')
            b = find_colors([35,35,23],mainscreen,tol=(0.07,0.1,0.05),mode='hsl')
            coal = filter_near(a,b,4)
            coal = filter_far(coal,gas,50)
            
            rocks = None
            if len(mith) > 20 and mith_count < max_mith:
                print('mining mith')
                rocks = mith
            elif len(coal) > 100:
                print('mining coal')
                rocks = coal
            else:
                print('Lost!')
            if rocks is None or (np.random.random()<0.05 and mith_count < max_mith):
                print('trying to find mith')
                center_of_dark = np.mean(map_dark-[mmxc-mmxs,mmyc-mmys],axis=0)
                if np.any(center_of_dark < 0): #not at bottom right corner
                    a = find_colors(mm_cave,minimap,tol=0.12,mode='dist')
                    a = filter_radius(a,[mmxc-mmxs,mmyc-mmys],55)
                    if len(a) > 0:
                        pt = closest([mmxc-mmxs+50,mmyc-mmys+50],a)
                        click_mouse(*(pt+[mmxs+5,mmys+5]))
                        flag_wait()
                continue
                    
            if mine(rocks):
                last_mine = mark_time()
        else: #go to mining guild
            if len(map_dark) < 10:
                print('trying to find ladder')
                click_mouse(*[mmxc+30+np.random.random()*5,mmyc+45+np.random.random()*5])
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
                            flag_wait()
                            sleep(0.5)
                            run_on()
                            break
                        move_mouse(*(point+[0,-25]))
            


# In[ ]:




