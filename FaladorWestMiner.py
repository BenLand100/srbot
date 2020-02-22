#!/usr/bin/env python3

from srbot import *

#Mining script requires agility shortcut Falador west

west_road = [122,117,70]
east_road = [121,119,97]
wall_color = [190,184,155]
mine_rock_color = [154,91,39]
mine_area_color = [98,80,23]
inner_wall_color = [60,60,50]
outer_wall_color = [73,64,41]

copper_color = [168,120,76]
tin_color = [149,138,138]
iron_color = [60,35,28]
gold_color = [251,204,31]

#rocks = [(1,copper_color,(0.02,0.08,0.08),[223,129,59]),(1,tin_color,0.025,[139,130,129])] #copper&tin
rocks = [(1,iron_color,(0.02,0.08,0.08),[78,48,36])] #iron

mm_east_tol = (0.05,0.1,0.1)
mm_west_tol = (0.05,0.08,0.08)

mine_icon = load_image('mine_icon.png')
agility_icon = load_image('agility_icon.png')

def count_rocks(weighted=True,rocks=None):
    '''finds the weighted count of each rock in the inventory for each rock the rocks list'''
    raw_counts = np.asarray([(count_inv(color=invc,tol=tol,mode='hsl'),weight) for weight,color,tol,invc in rocks])
    return raw_counts[:,0]/raw_counts[:,1] if weighted else raw_counts[:,0]

def fast_mine(points,noob_factor=1.0):
    if len(points) == 0:
        return False
    counts = count_inv(color=[119,96,67],tol=0.02)
    clusters,_ = cluster(points,10)
    points = np.asarray([np.mean(cluster,axis=0) for cluster in clusters],dtype=np.float64)
    points = closest_exp([msw/2,msh/2],points,10,N=5)
    if points is None or not confirm_click(points):
        return False
    for i in range(int(100*noob_factor)):
        sleep(0.05)
        if np.any(count_inv(color=[119,96,67],tol=0.02) != counts):
            return True
    return False

def mine(rocks=rocks,noob_factor=2.0):
    '''mines the next rock based on weights in rocks structure
       finds rock based on color of ore plus proximity to generic rock color
       confirms uptext hovering over rock before mining
       waits for rock to appear in inventory before proceeding'''
    counts = count_rocks(rocks=rocks)
    print('Weighted totals:',counts)
    minidx = np.argmin(counts)
    weight,color,tol,bmp = rocks[minidx]
    mainscreen = get_mainscreen()
    found = find_colors(color,mainscreen,tol=tol,mode='hsl')
    b = find_colors(np.asarray([107,88,28]),mainscreen,tol=0.02)
    found = filter_near(found,b,10)
    return fast_mine(found,noob_factor=noob_factor)

def west_of_wall():
    '''returns true if character is closer to west road or mine colors than east road or mine colors'''
    minimap = get_minimap()
    if len(find_best_bitmap(mine_icon,minimap,0.05)) > 0:
        print('at mine')
        return True
    west = find_colors(west_road,minimap,tol=mm_west_tol,mode='hsl')
    clusters,counts = cluster(west,radius=2)
    if len(counts) > 0 and np.max(counts) > 100:
        west = concatenate(*clusters[counts > 25])
    else:
        west = []
    npc_points = find_colors([255,255,0],minimap,tol=0.05,mode='hsl')
    bank_points = concatenate(*[find_colors(bank_floor,minimap,tol=0.085,mode='hsl') for bank_floor in bank_floor_colors])
    clusters,counts = cluster(bank_points)
    if len(counts) < 1 or np.count_nonzero(counts>20) < 1:
        bank_points = np.asarray([])
    else:
        bank_points = clusters[np.random.choice(np.nonzero(counts>20)[0])]
    bank_points = filter_near(bank_points,npc_points,6)
    if len(bank_points) < 10:
        a = find_colors([154,91,39],minimap,tol=(0.05,0.08,0.1),mode='hsl')
        b = find_colors([54,43,8],minimap,tol=(0.03,0.05,0.05),mode='hsl')
        rocks = filter_near(a,b,5)
        west = concatenate(rocks,west)
    east = find_colors(east_road,minimap,tol=mm_east_tol,mode='hsl')
    clusters,counts = cluster(east,radius=2)
    if len(counts) > 0 and np.max(counts) > 100:
        east = concatenate(*clusters[counts > 10])
    else:
        east = []
    print('Locating... E:',len(east),'W:',len(west),'B',len(bank_points))
    west_best = 9001 if len(west) == 0 else np.min(np.sum(np.square(west-[mmxc-mmxs,mmyc-mmys]),axis=-1))
    east_best = 9001 if len(east) == 0 else np.min(np.sum(np.square(east-[mmxc-mmxs,mmyc-mmys]),axis=-1))
    if west_best <= east_best:
        print('west of wall')
        return True
    else:
        print('east of wall')
        return False
            
            
def jump_wall():
    '''The Donald can't stop us!
       tries to get as close as possible to boundary between east and west road colors on minimap
       looks for proximity of wall color, east, and west road colors on mainscreen
       attempts to confirm uptext hovering over possible wall locations
       returns true if successfully jumped'''
    minimap = get_minimap()
    east = find_colors(east_road,minimap,tol=mm_east_tol,mode='hsl')
    west = find_colors(west_road,minimap,tol=mm_west_tol,mode='hsl')
    print('Road points... E:',len(east),'W:',len(west))
    if len(west) == 0 or len(east) == 0:
        return False
    border = filter_near(east,west,3)
    print('Boundary:',len(border))
    if len(border) <= 3: #try the agility icon
        agility = find_best_bitmap(agility_icon,minimap,mode='xcorr',tol=0.18)
    else:
        agility = None
    np.random.shuffle(border)
    if len(border) > 3 or len(agility) > 0:
        border = border[0] if len(border) > 3 else (agility[np.random.randint(len(agility))]+[5,5])
        click_mouse(*(border+[mmxs,mmys]))
        flag_wait(imax=10)
        mainscreen = get_mainscreen()
        wall_points = find_colors(wall_color,mainscreen,tol=0.07,mode='hsl')
        inner_wall_points = find_colors(inner_wall_color,mainscreen,tol=0.07,mode='hsl')
        outer_wall_points = find_colors([73,64,41],mainscreen,tol=0.07,mode='hsl')
        wall_points = filter_near(filter_near(wall_points,inner_wall_points,10),outer_wall_points,10)
        return confirm_click(wall_points)
    return False

target()
miss = 0
total_trips = 0
total_ores = 0
start_time = mark_time()
last_mine = mark_time()
while True:
    client = get_client()
    if len(find_bitmap(loginscreen,client)) > 0:
        login()
        continue
    if mark_time()-last_mine > 10*60:
        raise RuntimeError('Haven\'t mined in 10 minutes, giving up because something ain\'t right.')
    inv_count = count_inv()
    inv_full = inv_count == 28
    print('Total items:',inv_count)
    if inv_full:
        if west_of_wall():
            if not jump_wall():
                minimap = get_minimap()
                west = filter_radius(find_colors(west_road,minimap,tol=mm_west_tol,mode='hsl'),[mmxc-mmxs,mmyc-mmys],70)
                print('Moving east:',len(west))
                if len(west):
                    click_mouse(*(west[np.argsort(west[:,0])[-1]]+(mmxs,mmys)))
                    sleep(2.0)
            else:
                click_mouse(mmxc+20,mmyc)
                flag_wait(imax=10)
                print('Crossed wall west->east')
        else: 
            if open_bank():
                deposit_all()
                total_ores += inv_count
                total_trips = total_trips + 1
                if np.random.random() < 0.5:
                    polish_minimap(min_same=35,horizontal=False)
                print('Completed %i inventories (%i ore @ %0.2f s/ore)'%(total_trips,total_ores,(mark_time()-start_time)/total_ores))
                continue
    else:
        if west_of_wall():
            if not mine(rocks):
                print('No rock found!')
                miss = miss + 1
                if miss < 5:
                    sleep(0.5)
                    continue
                print('Trying new position...')
                minimap = get_minimap()
                a = find_colors(mine_rock_color,minimap,tol=(0.05,0.08,0.1),mode='hsl')
                b = find_colors(mine_area_color,minimap,tol=(0.03,0.05,0.05),mode='hsl')
                mine_loc = filter_near(a,b,5)
                mine_loc = filter_radius(mine_loc,[mmxc-mmxs,mmyc-mmys],50)
                if len(mine_loc):
                    np.random.shuffle(mine_loc)
                    #delta = np.random.random()*30-20
                    click_mouse(*(mine_loc[0]+(mmxs,mmys)))#+(delta,-2*delta)))
                    flag_wait()
                    continue
                west = find_colors(west_road,minimap,tol=mm_west_tol,mode='hsl')
                west = filter_radius(west,[mmxc-mmxs,mmyc-mmys],70)
                print('Moving west:',len(west))
                if len(west):
                    click_mouse(*(west[np.argsort(west[:,0])[0]]+(mmxs,mmys)))
                    sleep(2.0)
                else:
                    print('Got lost going to mine!')
            else:
                last_mine = mark_time()
                miss = 0
        else: 
            if not jump_wall():
                minimap = get_minimap()
                east = filter_radius(find_colors(east_road,minimap,tol=mm_east_tol,mode='hsl'),[mmxc-mmxs,mmyc-mmys],70)
                print('Moving west:',len(east))
                if len(east):
                    click_mouse(*(east[np.argsort(east[:,0]-0.5*east[:,1])[0]]+(mmxs,mmys)))
                    sleep(2.0)
                else:
                    print('Got lost going to wall!')
            else:
                miss = 9999 #to move west immediately
                run_on()
                click_mouse(mmxc-20,mmyc)
                flag_wait(imax=10)
                print('Crossed wall east->west')




