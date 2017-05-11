# -*- coding: utf-8 -*-
"""
Created on Wed May 10 22:19:47 2017

@author: Martin
"""

# -*- coding: utf-8 -*-
"""
Created on Mon May 01 22:14:21 2017 

"""
import numpy as np
import math
import sys

def find_attrib(line="",attrib=""):
    st=line.find(attrib+'="')+len(attrib)+2
    en=line.find('"',st)
    return line[st:en]

def parse_node(line=""):
    id=np.int64(find_attrib(line,"id"))
    lat=np.int64(np.float(find_attrib(line,"lat"))*10000000)
    lon=np.int64(np.float(find_attrib(line,"lon"))*10000000)
    return (id,lat,lon)

def parse_ways(line=""):
    ref=find_attrib(line,"ref")
    return ref

def parse_file(filename):
    f=open(filename,"r")
    #nodes=np.empty((100000000),dtype=np.int64)
    nodes=np.empty((100000000),dtype=[('a',np.int64),('b',np.int64),('c',np.int64)])
    nodes_i=0;
    ways=[]
    inway=False
    required_highways=['motorway','trunk','primary','secondary','tertiary','motorway_link',
                       'trunk_link','primary_link','secondary_link','road','unclassified',
                       'residential','unsurfaced','living_street','service']
    required_highway=False
    for line in f:
        if line.lower().find('<node')!=-1:
            #nodes.append(parse_node(line))
            nodes[nodes_i]=parse_node(line)
            nodes_i+=1
        if line.lower().find('<way')!=-1:
            inway=True
            required_highway=False
            ways_tmp=[]
        if line.lower().find('</way')!=-1:
            inway=False
            if required_highway:
                ways.append(map(lambda x:parse_ways(x),ways_tmp))
                required_highway=False
        if inway:
            if line.lower().find('<nd')!=-1:
                ways_tmp.append(line)
            if line.lower().find('<tag')!=-1 and required_highway==False:
                if line.lower().find('highway')!=-1:
                    for highway in required_highways:        
                        if line.lower().find('"'+highway+'"')!=-1:
                            required_highway=True
                            break
    f.close()
    nodes.resize(nodes_i)
#    print(nodes[nodes[:,0]==1553582788])
    nodes.sort(axis=0,order='a')
#    print(nodes[nodes[:,0]==1553582788])
    ways=[map(lambda x:np.searchsorted(nodes[:]['a'],np.int64(x)),y) for y in ways]
    return nodes,ways
    
nodes,ways=parse_file(r"..\OSMFiles\baden-wuerttemberg.osm")
#nodes,ways=parse_file(r"..\OSMFiles\saarland.osm")
#nodes,ways=parse_file(r"..\OSMFiles\map.osm")
#nodes,ways=parse_file(r"..\OSMFiles\test1.osm")
#==============================================================================
# for way in ways[1:10]:
#     st_node=way[0]
#     for node in way[1:]:
#         print(st_node,node)
#==============================================================================
def distance(start_node, end_node):
    lattometers=111229.0
    longtometers=71695.0
    dist=math.sqrt(
         math.pow((end_node[1]/10000000.0-start_node[1]/10000000.0)*lattometers,2) + 
         math.pow((end_node[2]/10000000.0-start_node[2]/10000000.0)*longtometers,2)
    )
    return dist

arcs=np.empty((nodes.size),dtype=object)
for way in ways:#[1:5]:
    for node1,node2 in zip(way[:-1],way[1:]):
        d=distance(nodes[node1],nodes[node2])
        try:
            arcs[node1].append((node2,d))
        except:
            arcs[node1]=[]
            arcs[node1].append((node2,d))
        try:
            arcs[node2].append((node1,d))
        except:
            arcs[node2]=[]
            arcs[node2].append((node1,d))

np.save(r"..\OSMFiles\baden-wuerttemberg.npy",arcs)

arcs=np.load(r"..\OSMFiles\baden-wuerttemberg.npy")
