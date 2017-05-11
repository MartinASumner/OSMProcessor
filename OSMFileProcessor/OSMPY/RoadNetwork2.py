# -*- coding: utf-8 -*-
"""
Created on Thu May 11 01:47:17 2017

@author: Martin
"""

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

class OSMArcs():
    """
    Processes a OSM file to extract the road networks nodes and ways and returns an array of arcs.

    Parameters
    ----------
    OSMfile: Path of the OSM formated file to be processed
        
    **kwargs
        Further parameters available. See folium.map.FeatureGroup

    Returns
    -------
    An np.ndarray of nodes and associated list of connected nodes and distances.

    """    
    def __init__(self, OSM_file=None, required_highways=None):
        self.OSM_file=OSM_file
        if required_highways is None:
            self.required_highways=['motorway','trunk','primary','secondary','tertiary','motorway_link',
                           'trunk_link','primary_link','secondary_link','road','unclassified',
                           'residential','unsurfaced','living_street','service']
        else:
                self.required_highways=required_highways
        
    def _find_attrib(self,line="",attrib=""):
        st=line.find(attrib+'="')+len(attrib)+2
        en=line.find('"',st)
        return line[st:en]
    
    def _parse_node(self,line=""):
        id=np.int64(self._find_attrib(line,"id"))
        lat=np.int64(np.float(self._find_attrib(line,"lat"))*10000000)
        lon=np.int64(np.float(self._find_attrib(line,"lon"))*10000000)
        return (id,lat,lon)
    
    def _parse_ways(self,line=""):
        ref=self._find_attrib(line,"ref")
        return ref
    
    def _distance(self, start_node, end_node):
        lattometers=111229.0
        longtometers=71695.0
        dist=math.sqrt(
             math.pow((end_node[1]/10000000.0-start_node[1]/10000000.0)*lattometers,2) + 
             math.pow((end_node[2]/10000000.0-start_node[2]/10000000.0)*longtometers,2)
        )
        return dist
    
    
    def parse_file(self,OSM_filename=None):
        if OSM_filename is not None:
            self.OSM_file=OSM_filename
        try:
            f=open(self.OSM_file,"r")
        except (IOError, EOFError) as e:
            print("An error occurred. {}".format(e.args[-1]))
            raise e
        # reserve node space
        nodes=np.empty((100000000),dtype=[('a',np.int64),('b',np.int64),('c',np.int64)])
        nodes_i=0;
        ways=[]
        inway=False
        required_highway=False
        for line in f:
            if line.lower().find('<node')!=-1:
                #nodes.append(parse_node(line))
                nodes[nodes_i]=self._parse_node(line)
                nodes_i+=1
            if line.lower().find('<way')!=-1:
                inway=True
                required_highway=False
                ways_tmp=[]
            if line.lower().find('</way')!=-1:
                inway=False
                if required_highway:
                    ways.append(map(lambda x:self._parse_ways(x),ways_tmp))
                    required_highway=False
            if inway:
                if line.lower().find('<nd')!=-1:
                    ways_tmp.append(line)
                if line.lower().find('<tag')!=-1 and required_highway==False:
                    if line.lower().find('highway')!=-1:
                        for highway in self.required_highways:        
                            if line.lower().find('"'+highway+'"')!=-1:
                                required_highway=True
                                break
        f.close()
        nodes.resize(nodes_i)
    #    print(nodes[nodes[:,0]==1553582788])
        nodes.sort(axis=0,order='a')
    #    print(nodes[nodes[:,0]==1553582788])
        ways=[map(lambda x:np.searchsorted(nodes[:]['a'],np.int64(x)),y) for y in ways]
        
        arcs=np.empty((nodes.size),dtype=object)
        for way in ways:#[1:5]:
            for node1,node2 in zip(way[:-1],way[1:]):
                d=self._distance(nodes[node1],nodes[node2])
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
                
        return arcs, nodes

#nodes,ways=parse_file(r"..\OSMFiles\baden-wuerttemberg.osm")
#nodes,ways=parse_file(r"..\OSMFiles\saarland.osm")
#nodes,ways=parse_file(r"..\OSMFiles\map.osm")
#nodes,ways=parse_file(r"..\OSMFiles\test1.osm")
#==============================================================================
# for way in ways[1:10]:
#     st_node=way[0]
#     for node in way[1:]:
#         print(st_node,node)
#==============================================================================

f=OSMArcs(OSM_file=r"..\OSMFiles\baden-wuerttemberg.osm")
arcs,nodes=f.parse_file()

np.save(r"..\OSMFiles\baden-wuerttemberg.npy",arcs)
arcs=np.load(r"..\OSMFiles\baden-wuerttemberg.npy")
