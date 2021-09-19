import numpy as np
import cv2
from bs4 import BeautifulSoup
from agentspace import Agent, Space

map = cv2.imread('map.png')

with open('map.osm', 'r', encoding="utf-8") as f:
    data = f.read()

bs = BeautifulSoup(data, "xml")

maxlat = float(bs.bounds['maxlat'])
minlat = float(bs.bounds['minlat'])
maxlon = float(bs.bounds['maxlon'])
minlon = float(bs.bounds['minlon'])

def pin(point):
    lat, lon = point
    y = (map.shape[0]-1) - map.shape[0]*(lat-minlat)/(maxlat-minlat)
    x = map.shape[1]*(lon-minlon)/(maxlon-minlon)
    return (int(x), int(y))

nodes = dict()
for node in bs.select("node"):
    id = int(node['id'])
    lat= float(node['lat'])
    lon= float(node['lon'])
    nodes[id] = (lat,lon)
    
#for id in nodes.keys():
#    cv2.circle(map,pin(nodes[id]),1,(0,0,255),cv2.FILLED)
#    
#cv2.imwrite('nodes.png',map)

ways = []
for way in bs.select("way"):
    nds = [ int(nd['ref']) for nd in way.select("nd") ]
    tags = [ tag['k'] for tag in way.select('tag') ]
    if (("highway" in tags) or ("footage" in tags)) and not ("barrier" in tags) and not("indoor" in tags):
        #print(tags)
        ways.append(nds)

for way in ways:
    prev = None
    for nd in way:
        if prev is not None:
            cv2.line(map,pin(nodes[prev]),pin(nodes[nd]),(0,255,0),1)
        prev = nd

cnt = 0
indices = dict()
for way in ways:
    for nd in way:
        indices[nd] = cnt
        cnt += 1
        cv2.circle(map,pin(nodes[nd]),1,(0,0,255),cv2.FILLED)

cv2.imwrite('ways.png',map)

mat = np.zeros((cnt,cnt),np.bool)
lats = np.zeros((cnt),np.float32)
lons = np.zeros((cnt),np.float32)
for way in ways:
    prev = None
    for nd in way:
        lat, lon = nodes[nd]
        index2 = indices[nd]
        lats[index2] = lat
        lons[index2] = lon
        if prev is not None:
            index1 = indices[prev]
            mat[index1,index2] = True
            mat[index2,index1] = True
        prev = nd

map = cv2.imread('map.png')

for n1 in range(cnt-1):
    for n2 in range(n1+1,cnt):
        if mat[n1,n2]:
            p1 = (lats[n1],lons[n1])
            p2 = (lats[n2],lons[n2])
            cv2.line(map,pin(p1),pin(p2),(0,255,0),1)

for n in range(cnt):
    p = (lats[n],lons[n])
    cv2.circle(map,pin(p),1,(0,0,255),cv2.FILLED)

cv2.imwrite('ways2.png',map)

print("map ready")

def localize(p):
    lat, lon = p
    distances = np.sqrt((lats-lat)**2 + (lons-lon)**2)
    n = np.argmin(distances)
    return n
    
def dijkstra(i,j):
    infinity = 10000000
    v = np.full((cnt),infinity,np.int)
    b = np.full((cnt),True,np.bool)
    u = np.full((cnt),-1,np.int)
    v[i] = 0
    while v[j] == infinity:
        vv = infinity
        m = -1
        for n in range(cnt):
            if b[n]:
                if v[n] < infinity:
                    m = n
        if m == -1:
            return []
        b[m] = False
        for n in range(cnt):
            if mat[m,n]:
                if v[m]+1 < v[n]:
                    v[n] = v[m]+1
                    u[n] = m
    ret = [j]
    n = j
    while u[n] != -1:
        ret.append(u[n])
        n = u[n]
        
    return ret
    
def findPath(p,q):
    pi = localize(p)
    qi = localize(q)
    pathi = dijkstra(pi,qi)
    return [ (lats[i],lons[i]) for i in pathi ]

#s1 = (48.0915292, 17.0426958)
#s2 = (48.0899065, 17.0440434)
#path = findPath(s1,s2)
#print(path)
#
#for p in path:
#    cv2.circle(map,pin(p),2,(255,255,0),cv2.FILLED)
#
#cv2.imwrite('path.png',map)

class OsmAgent(Agent):

    def __init__(self,gpsName,qrName,goalName):
        self.gpsName = gpsName
        self.qrName = qrName
        self.goalName = goalName
        super().__init__()

    def init(self):
        self.attach_trigger(self.qrName)

    def senseSelectAct(self):
        position = Space.read(self.gpsName,None)
        if position is None:
            return

        qr = Space.read(self.qrName,None)
        if qr is None:
            return
            
        print(qr) # geo:48.1491242,17.0737278
        values = qr[4:].split(',')
        goal = (float(values[0]),float(values[1]))
        #goal = (48.1491242,17.0737278) # prva nakladka
        
        path = findPath(position,goal)
        
        map2 = np.copy(map)
        prev = None
        for p in path:
            cv2.circle(map2,pin(p),3,(255,0,255),cv2.FILLED)
            if prev is not None:
                cv2.line(map2,pin(prev),pin(p),(255,0,255),2)
            prev = p

        for i in range(1,len(path)):
            subgoal = path[i]
            print('subgoal',subgoal)
            Space.write(self.goalName,subgoal)
            while True:
                gps = Space.read('gps',[-1,-1])
                if gps[0] == -1:
                    continue
                cv2.circle(map2,pin(gps),3,(255,0,0),cv2.FILLED)
                cv2.imshow("map",map2)
                cv2.waitKey(1)
                distance = np.sqrt((gps[0]-subgoal[0])**2 + (gps[0]-subgoal[1])**2)
                #print('distance to subgoal',subgoal,'=',distance)
                if distance < 0.0001:
                    break
                    
        cv2.destroyWindow("map")
        
