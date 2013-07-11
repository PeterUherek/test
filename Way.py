import xml.etree.ElementTree as ET
import math
from collections import defaultdict
import random



class Node:
    """
    Trieda reprezentujuca jeden nod. Mala by mat dobre definovane funckie __hash__ a __eq__ aby sme
    ju vedeli davat do mnozin, dictov a porovnavat
    """

    def __init__(self, elem):
        self.ways=set()
        #pozor, id je string, nie cislo!
        self.id=elem.attrib['id']
        self.lon=elem.attrib['lon']
        self.lat=elem.attrib['lat']
        #TODO 
    

    def __hash__(self):
       return self.id.__hash__()

    def __eq__(self, other):
        #TODO: rovnost by mala fungovat na baze id-ciek
        if self.id==other.id:
            return True
        else:
            return False
        

    def __repr__(self):
        return "Node(id=%s, way=%s)"%(self.id, ', '.join({way.name for way in self.ways if way.name!='unnamed'}))

    def __str__(self):
        return self.__repr__()

class Way:
    def __init__(self, elem):
        self.nodes=set()
        self.elem=elem
        try:
            self.id=elem.findall("./tag[@k='id']")[0].attrib['v']
        except Exception:
            self.id=0
            
        try:
            self.name=elem.findall("./tag[@k='name']")[0].attrib['v']
        except Exception:
            self.name='unnamed'
        


    def __hash__(self):
        return self.id.__hash__() 
        

    def __eq__(self, other):
        return self.id.__eq__(other)

    def __repr__(self):
        pass
        #TODO: staci hocico jednoduche

def dist(node1, node2):
    return node1.lon-node2.lat

def is_way(elem):
    motorways={'living_street', 'motorway_link', 'trunk', 'track', 'give_way', 'tertiary_link',
            'tertiary', 'motorway_junction', 'residential', 'secondary_link', 'service',
            'motorway', 'crossing', 'secondary'}
            

    #TODO: zistit na zaklade xml elementu elem, ci sa jedna o motorovu cestu, hodi sa pouzit mnozinu
    #motorways
    try:
        hw=elem.findall("./tag[@k='highway']")[0].attrib['v']
    except Exception:
        hw='nic'
        
    if (hw in motorways):
        return True
    else:
        return False
    

def graph_from_dict(graph_dict):
    """
    creates graph from dict representration.

    arguments:
       graph_dict[vertex] is iterable of all (neighbour, distance) pairs

    returns:
       function acceptable by dijkstra function

    """
    def graph(vertex):
        return graph_dict[vertex]
    return graph

def dijkstra(graph, ver_start, ver_end):
    """
    find optimal path between vertices ver_start and ver_end. Graph is function, that accepts vertex
    and returns list of (neighbour, distance) pairs.

    returns tuple (dist, path) where dist is optimal distance and path is sequence of vertices
    """
    #boundary and final have the following structure: {vertex: (distance, previous_vertex)} where
    #distance is the distance from node_start to vertex and previous_vertex is semi-last vertex on
    #the ver_start - vertext path optimal path.

    boundary={}
    final={}
    boundary[ver_start]=(0, None)
    while True:
        if not boundary:
            return None, None
        closest_ver, (closest_dist, prev_vertex) = min(boundary.items(), key=lambda item: item[1][0])
        final[closest_ver] = closest_dist, prev_vertex
        del boundary[closest_ver]
        for ver, dst in graph(closest_ver):
            if ver not in final:
                if ver not in boundary or boundary[ver][0]>closest_dist+dst:
                    boundary[ver]=(closest_dist+dst, closest_ver)
        if closest_ver == ver_end:
            break
    path=[ver_end]
    iterator=ver_end
    while not iterator is ver_start:
        iterator=final[iterator][1]
        path.append(iterator)

    return final[ver_end][0], path


if __name__=="__main__":
    tree = ET.parse('map.osm')

    all_ways={Way(elem) for elem in tree.findall(".//way") if is_way(elem)}
    all_nodes={Node(elem) for elem in tree.findall(".//node")}  #TODO: podobne ako all_ways chceme nacitat vsetky nody
    all_nodes_dict={Node.id:Node for Node in all_nodes}#TODO; all_nodes_dicts je pomocna struktura, ktora mapuje node.id na prislusny
    #node object. zahrna vsetky nody z all_nodes
    
    # {vertex: {(sused1, vzd1), (sused2, vzd2), ...}}
    graph_dict=defaultdict(set)

    for way in all_ways:
        elem_nodes=list(way.elem.findall(".//nd"))
        nodes = [all_nodes_dict[elem_node.attrib['ref']] for elem_node in elem_nodes]
        for node in nodes:
            f=node
            way.nodes.add(node)
            node.ways.add(way)
            x=random.randint(10,100)
            grap_dict={(node,x),(f,x)}
            
        #TODO: pridat node do way.nodes, way do node.ways
        #TODO: preiterovat cez susedov node1, node2 a pridat ich do graph_dict
                    
    #vyfiltrujeme nody patriace nejakej ulici
    all_street_nodes=[node for node in all_nodes if node.ways]
    
    graph=graph_from_dict(graph_dict)
    #najdeme nejake 2 nahodne nody, ktore patria nejakej ulici a hadam budu spojene
    node1=random.choice(all_street_nodes)
    node2=random.choice(all_street_nodes)
    print(dijkstra(graph, node1, node2))