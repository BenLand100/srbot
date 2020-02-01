import numpy as np

def filter_near(a,b,dist):    
    '''returns all points in a within some distance to a point in b'''
    if len(a) == 0 or len(b) == 0:
        return np.asarray([])
    diffs = np.asarray([(i,np.min(np.sum(np.square(p-b),axis=-1))) for i,p in enumerate(a)])
    return a[diffs[:,1]<dist*dist]

def filter_far(a,b,dist):    
    '''returns all points in a within some distance to a point in b'''
    if len(a) == 0:
        return np.asarray([])
    if len(b) == 0:
        return a
    diffs = np.asarray([(i,np.min(np.sum(np.square(p-b),axis=-1))) for i,p in enumerate(a)])
    return a[diffs[:,1]>dist*dist]

def filter_radius(pts,center,radius):
    '''returns all points in pts within radius of the center point'''
    return pts[np.sum(np.square(pts-center),axis=-1)<radius*radius]

def closest(point,points):
    '''returns the closest value in points to the given point'''
    sorter = np.sum(np.square(points-point),axis=-1)
    return points[np.argmin(sorter)]

def closest_exp(pt,pts,scale,N=None):
    '''Samples the pts array based on exp(dist/scale) where dist is distance of pts to pt.
       returns N samples from pts (can repeat).'''
    pts = np.asarray(pts)
    pt = np.asarray(pt)
    dists = np.sqrt(np.sum(np.square(pts - pt),axis=1))
    p = np.exp(-dists/scale)
    p = p/np.sum(p)
    if N is None:
        return pts[np.searchsorted(np.cumsum(p),np.random.random())]
    else:
        return pts[np.searchsorted(np.cumsum(p),np.random.random(N))]

def closest_shuffle(pt,pts,sigma):
    '''Sorts pts by distance to pt where distance is perturbed by a gaussian width sigma.'''
    if len(pts) == 0:
        return pts
    pts = np.asarray(pts)
    pt = np.asarray(pt)
    dists = np.sqrt(np.sum(np.square(pts - pt),axis=1)) + np.random.normal(0,sigma,len(pts))
    return pts[np.argsort(dists)] 

def cluster(points,radius=5):
    '''groups points separated by no more than radius from another point in the group
       returns a list of the groups, and the length of each group'''
    clusters = np.zeros(len(points),dtype='uint32')
    while True: #loop until all points are clustered
        unclustered = clusters==0
        remaining = np.count_nonzero(unclustered)
        if remaining == 0:
            break 
        # any points near this group (and their points) become a new group
        candidate = points[unclustered][np.random.randint(remaining)] #do this randomly to save time
        dist = np.sum(np.square(points-candidate),axis=1)
        nearby_mask = dist<=radius*radius #importantly includes candidate point
        overlaps = set(list(clusters[nearby_mask])) #groups that were close
        overlaps.remove(0)
        if len(overlaps) == 0:
            G = np.max(clusters)+1 #new cluster
        else:
            G = np.min(list(overlaps)) #prefer smaller numbers
        #set all nearby clusters to index G
        clusters[nearby_mask] = G
        for g in overlaps:
            if g == G or g == 0:
                continue
            clusters[clusters==g] = G
    unique, counts = np.unique(clusters, return_counts=True)
    cluster_points = np.asarray([points[clusters==c] for c in unique],dtype='object')
    return cluster_points,counts