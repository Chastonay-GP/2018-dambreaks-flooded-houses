import networkx as nx
import matplotlib.pyplot as plt
import itertools
import shapefile
import numpy as np
from numpy import random
import re
import os
import sys #to exit command / abort script: sys.exit()
from scipy.spatial import distance
import arcpy
import shutil

#Plotting the network on basis of the edges from the .edg file (output of basement-simulation) and the nodes from a shapefile
#---------------------------------------
#Create empty graph
G=nx.Graph()
#M=nx.DiGraph()

#open .edg file in read-mode and shapefile for localisation of nodes
with open('C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/BASEMENT/aare.edg','r') as E:
    lines=E.readlines()  # type: List[str]
shape = shapefile.Reader("C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/aareV10rechtsGrob_Quality_nodes.shp")

#This gets the limits of the lines that contain the header / footer delimiters
data = lines[5:]

#Now, you can parse the lines into rows by splitting the line on whitespace
rows=[line.split() for line in data]

# Columns have integer data, so we convert the string data to float
Edge = [int(row[0]) for row in rows]
Node1 = [int(row[1]) for row in rows]
#Making a copy of Node1 as we extend the list further down with the values from Node2)
Node1Copy=Node1
Node2 = [int(row[2]) for row in rows]
Elem_L = [int(row[3]) for row in rows]
Elem_R = [row[4] for row in rows]

#Replace NULL values with -9999 in the row Elem_R
Elem_R = [w.replace('NULL', '-9999')for w in Elem_R]

#Convert strings in List Elem_R to integer:
##with python 2.x:
Elem_R=map(int,Elem_R)
##with python 3.x:
#Elem_R=list(map(int,Elem_R))

#Adding leading zeros to data
[str(item).zfill(5) for item in Edge]

#To create Edges we combine the two Node rows in a single tuple.
#E.g. Node1=(1,2,3) and Node2=(a,b,c) => Edges=(1,a),(2,b),(3,b)
Tuple_Nodes = zip(Node1, Node2)
#print Tuple_Nodes

#Extend the list from Node2 two the copied list Node1Copy
Node1Copy.extend(Node2)

#Setting Node1 back to the original list. Why ever I need to do this... Do not understand why Python changes the variable Node1 with the code from the previous line
Node1 = [int(row[1]) for row in rows]
print nx.info(G)

#Creating Edges and check the graph info
G.add_edges_from(Tuple_Nodes)
print nx.info(G)

#Access shapefile for nodes and coordinates
fields =shape.fields[1:]
fields_name = [field[0] for field in fields] #-> the fields names in a list
#print fields_name
attributes = shape.records()
#print attributes
#Idee: Von shp die nodes nehmen und dabei die Georefernzierung der Punkte verwenden, da ansonsten networkX überlastet ist mit 20'000 punkten

#Extract the nested list into a simplier list
Attributes_List_Simple=[]
for inner_l in attributes:
    for item in inner_l:
        Attributes_List_Simple.append(item)

#extract nodes, x- and y-position from attribute table from shapefile
#list[0::4] means x[startAt:endBefore:skip]
Attribute_nodes = Attributes_List_Simple[0::4]
Attribute_xPos = Attributes_List_Simple [1::4]
Attribute_yPos = Attributes_List_Simple[2::4]
Attribute_pos = zip(Attribute_xPos,Attribute_yPos)

#Adding nodes to Graph
G.add_nodes_from(Attribute_nodes)
print nx.info(G)

#creating empty dictionary
d={}
#fill dictionary with nodes as keys and xy-position as values
d=dict(zip(Attribute_nodes,Attribute_pos))
#warnings: internet forum suggest to ignore the warnings: https://github.com/networkx/networkx/issues/2407
nx.draw(G,pos=d, node_size=10) # ist um einiges schneller wie nx.draw_networkx
nx.draw_networkx(G,pos=d, node_size=10, with_labels=False)

#Adding attributes to the nodes (water depth, velocity and water surface elevation)
#---------------------------------------------------------------------------
#create outer dictionary with TS1 - TS25 as keys
Steps=range(1,26)
Timesteps=[]
for i in Steps:
    Timesteps.append("TS"+str(i))
    i=i+1
Timesteps_tuple=tuple(Timesteps)

Depth_TS_out={}
Depth_TS_out=dict.fromkeys(Timesteps)

#next step: integrating above code into for loope with splitting .sol-file into timesteps and add them to the subdictionarys from 'Depth_TS_out'
splitLen = 21134
outputBase = 'Depth_TS'
input = open('C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/BASEMENT/aare_nds_depth.sol','r').read().strip('\n').split()

datavalues=[]
i=3
k=21136
for line in input:
    if line.startswith("TS"):
        outputData = (input[i:k])
        datavalues.append(outputData)
        i=i+1
        k=k+1
    else:
        i=i+1
        k=k+1

#converting string in datavalues to float
datavalues_float=[]
for parts in datavalues:
    datavalues_float.append([float(q) for q in parts])

datavalues_tuple=tuple(datavalues_float)

#NetworkX needs a dictionary for the attribute.
#Creating dictionary with timesteps as keys and datavalues (depth) as values.
Depth_TS={}
Depth_TS=dict(zip(Timesteps_tuple,datavalues_tuple))

#adding Depth_TS as attributes to the graph
for timesteps in Depth_TS:
    nx.set_node_attributes(G, 'Water_Depth', Depth_TS[timesteps])

nx.draw_networkx(G,pos=d, node_size=10, with_labels=False)
#--------------------------------------------------------------------------------
#Clearing unnecessary stuff from workspace
#del(Attribute_nodes, Attribute_pos, Attribute_yPos, Attribute_xPos, Attributes_List_Simple)
#del(Edge, Elem_R, Elem_L, Node1, Node1Copy, Node2, Steps, Timesteps, attributes, d, datavalues_float, datavalues, datavalues_tuple, field)
#del(row, rows, timesteps, splitLen, shape, q, parts, outputData, outputBase)
#del(data, fields, Tuple_Nodes, Depth_TS_out)
#del(line, lines, item, input)
#del(Timesteps_tuple, inner_l, shape, k)
#---------------------------------------


#Above lines ok
#--------------------------------------------------------------------------------
#lines bellow in testing
#---------------------------------------

nx.get_node_attributes(G,'Water_Depth')

#adding houses as point-dataset from shapefile
houses = shapefile.Reader("C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/gebaeudeCentroids_LV03.shp")

#converting the shapefile into a dictionary with XY-Location as keys and Feature-ID as house number. Therefore the attribute list needs to contain a field with the X and Y coordinates.
#In case it does not exist, manually add it to the shp.
#Access shapefile for nodes and coordinates
fields_houses =houses.fields[1:]
fields_name_houses = [field[0] for field in fields_houses] #-> the fields names in a list
#print fields_name
attributes_houses = houses.records()
print attributes_houses
#Idee: Von shp die nodes nehmen und dabei die Georefernzierung der Punkte verwenden, da ansonsten networkX überlastet ist mit 20'000 punkten

#Extract the nested list into a simplier list
Attributes_houses_List_Simple=[]
for inner_l in attributes_houses:
    for item in inner_l:
        Attributes_houses_List_Simple.append(item)

#extract nodes, x- and y-position from attribute table from shapefile
Attribute_houses_nodes = Attributes_houses_List_Simple[0::21]
Attribute_houses_xPos = Attributes_houses_List_Simple[19::21]
Attribute_houses_yPos = Attributes_houses_List_Simple[20::21]
Attribute_houses_pos = zip(Attribute_houses_xPos,Attribute_houses_yPos)

#To check weather Attribute_houses_nodes is unique and can be used as house identifier. Feature ID can not be used, it does not show up in python
uniqueList = []
def isDuplicate(inValue):
  if inValue in uniqueList:
    return 1
  else:
    uniqueList.append(inValue)
    return 0
isDuplicate(Attribute_houses_nodes)
del(uniqueList)

#Creating dictionary
houses_dict={}
houses_dict=dict(zip(Attribute_houses_nodes,Attribute_houses_pos))

#adding the houses_dict as attributes to the Graph
#idee: if position von houses stimmt mit position von nodes überein, mach ein neues Attribut "houses" mit Wert 1, sonst Wert 0

#script from internet to create a list with matching items from two lists with sublists
Attribute_Houses = []
for item in Attribute_houses_pos:
    if not any(x[0] == item[0] for x in Attribute_pos):
        #print("Different chromosome")
        Attribute_Houses.append(item)
    elif any(x[1] < item[1] < x[2] or x[1] < item[2] < x[2]
             for x in Attribute_pos):
        print("Discard")
    else:
        print("New")
        Attribute_Houses.append(item)
#expos_list.extend(new_items)
#print(expos_list)
Attribute_pos_copy = Attribute_pos #in case anything goes wrong in the following

#finding closest nodes for the houses
def closest_node(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return nodes[closest_index]


a = random.randint(1000, size=(50000, 2))

some_pt = (1, 2)

closest_node(some_pt, a)

#Creates a new list with closest points
ClosestNodes=[]
for points in Attribute_houses_pos:
    ClosestNodes.append(closest_node(points, Attribute_pos))

#Check whether created points are contained in nodes
if set(ClosestNodes) <= set(Attribute_pos):
    print "Punkte sind in Nodes"
else:
    print "Punkte sind NICHT in Nodes"

#Adding number 1 at the end of the points to see whether the nodes are at the same location as a house
Nodes_Houses=[xs+(int('1'),) for xs in ClosestNodes]

#next step: Comparing the newly created list containing the nodes with houses with the original list of nodes. If the coordinates are correct, add 1 for a house, otherwise add 0.
result=Attribute_pos
result=map(list, result)

#felder=arcpy.gp.listFields(houses, "*", "ALL")
#for feld in felder:
#    print feld.Name,';',feld.Type

#approach from Andreas:
Path="C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/work.gdb"
houses_fc = "C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/gebaeudeCentroids_LV03.shp"
houses_fc_copy = houses_fc
houses_fc_dbf = "C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/gebaeudeCentroids_LV03.dbf"
houses_fc_table=Path+"/houses_fc_table.dbf"
Coordinates ="C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/aareV10rechtsGrob_Quality_nodes.shp"

arr = arcpy.da.FeatureClassToNumPyArray(houses_fc, ('idper_2d', 'X_Koord', 'Y_Koord'))
print arr[1]
shutil.copyfile(houses_fc_dbf, houses_fc_table)
arcpy.TableToTable_conversion(houses_fc, "C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/", "outTable.dbf")


arcpy.GenerateNearTable_analysis(houses_fc, Coordinates, Path + "/NearestPoints.dbf", "1000")
arcpy.Near_analysis(houses_fc, Coordinates)
#manually join the table to shapefile of the nodes and then export the file and join again to the nodes. In the end delete not used attributes

#next: extract X, Y, Z-values and house ID from the joinedHouseNodes-dataset
NodesHousesJoined = shapefile.Reader("C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/JoinGebaudeNodes.shp")

#converting the shapefile into a dictionary with XY-Location as keys and Feature-ID as house number. Therefore the attribute list needs to contain a field with the X and Y coordinates.
#In case it does not exist, manually add it to the shp.
#Access shapefile for nodes and coordinates
fields_NodesHouses =NodesHousesJoined.fields[1:]
fields_name_NodesHousesJoined = [field[0] for field in fields_NodesHouses] #-> the fields names in a list
#print fields_name
attributes_NodesHouses = NodesHousesJoined.records()
print attributes_NodesHouses
#Idee: Von shp die nodes nehmen und dabei die Georefernzierung der Punkte verwenden, da ansonsten networkX überlastet ist mit 20'000 punkten

#Extract the nested list into a simplier list
Attributes_HousesNodes_List_Simple=[]
for inner_l in attributes_NodesHouses:
    for item in inner_l:
        Attributes_HousesNodes_List_Simple.append(item)

print Attributes_HousesNodes_List_Simple[0:20]

#extract nodeID, X-Koordinate, Y-Coordinate, Z-Coordinate, House-ID from attribute table from shapefile
Attribute_NodesHouses_nodeID = Attributes_HousesNodes_List_Simple[0::9]
Attribute_NodesHouses_xPos = Attributes_HousesNodes_List_Simple[1::9]
Attribute_NodesHouses_yPos = Attributes_HousesNodes_List_Simple[2::9]
Attribute_NodesHouses_zPos = Attributes_HousesNodes_List_Simple[3::9]
Attribute_NodesHouses_houseID = Attributes_HousesNodes_List_Simple[4::9]
print Attributes_HousesNodes_List_Simple
len(Attributes_HousesNodes_List_Simple)
print fields_name_NodesHousesJoined
print Attribute_NodesHouses_nodeID
Attribute_NodesHouses_pos = zip(Attribute_NodesHouses_xPos,Attribute_NodesHouses_yPos)

#making dictionary; not sure whether to make a dictionary based on the location as key (XY) or the NodeID
housesNodes_dict={}
housesNodes_dict=dict(zip(Attribute_NodesHouses_nodeID,Attribute_NodesHouses_houseID))

#adding housesNodes_dict as attributes to the graph
for nodes in housesNodes_dict:
    nx.set_node_attributes(G, 'HouseID', housesNodes_dict[nodes])

nx.draw_networkx(G,pos=d, node_size=10, with_labels=False)