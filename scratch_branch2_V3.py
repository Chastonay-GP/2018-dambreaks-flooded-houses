#---------------------------------------
###############
##--Imports--##
###############
#--------------
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
import copy
#---------------------------------------
##############
##--Inputs--##
##############
#--------------
with open('C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/BASEMENT/aare.edg','r') as E:
    lines=E.readlines()  # type: List[str] #open .edg file in read-mode and shapefile for localisation of nodes
shape = shapefile.Reader("C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/aareV10rechtsGrob_Quality_nodes.shp")
input = open('C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/BASEMENT/aare_nds_depth.sol','r').read().strip('\n').split()
houses = shapefile.Reader("C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/gebaeudeCentroids_LV03.shp") #adding houses as point-dataset from shapefile
Path="C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/work.gdb"
houses_fc = "C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/gebaeudeCentroids_LV03.shp"
houses_fc_copy = houses_fc
houses_fc_dbf = "C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/gebaeudeCentroids_LV03.dbf"
houses_fc_table=Path+"/houses_fc_table.dbf"
Coordinates ="C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/aareV10rechtsGrob_Quality_nodes.shp"
NodesHousesJoined = shapefile.Reader("C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/JoinGebaudeNodes.shp")
#---------------------------------------
##########################
##--Defining functions--##
##########################
#-------------------------
#function to check whether there are dublicates
def isDuplicate(inValue):
  if inValue in uniqueList:
    return 1
  else:
    uniqueList.append(inValue)
    return 0

#function to calculate the closest node
def closest_node(node, nodes):
    closest_index = distance.cdist([node], nodes).argmin()
    return nodes[closest_index]

a = random.randint(1000, size=(50000, 2))

some_pt = (1, 2)

closest_node(some_pt, a)

#----------------------------------------
#########################################
##--Script part 1: Creating the graph--##
#########################################

#Plotting the network on basis of the edges from the .edg file (output of basement-simulation) and the nodes from a shapefile
#---------------------------------------
#Create empty graph
G=nx.Graph()

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

#Extend the list from Node2 two the copied list Node1Copy
Node1Copy.extend(Node2)

#Setting Node1 back to the original list. Why ever I need to do this... Do not understand why Python changes the variable Node1 with the code from the previous line
Node1 = [int(row[1]) for row in rows]

#Creating Edges and check the graph info
G.add_edges_from(Tuple_Nodes)

#Access shapefile for nodes and coordinates
fields =shape.fields[1:]
fields_name = [field[0] for field in fields] #-> the fields names in a list #print fields_name
attributes = shape.records()
#Idea: Taking nodes and location from shp because networkx is not able to process 20'000 points

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

#creating empty dictionary
d={}
#fill dictionary with nodes as keys and xy-position as values
d=dict(zip(Attribute_nodes,Attribute_pos))
#warnings: internet forum suggest to ignore the warnings: https://github.com/networkx/networkx/issues/2407
#nx.draw(G,pos=d, node_size=10) # ist um einiges schneller wie nx.draw_networkx
#nx.draw_networkx(G,pos=d, node_size=10, with_labels=False)

#---------------------------------------------------------------------------
############################################################################
##--Script part 2: Adding the water depth as an attribute to the network--##
############################################################################
#---------------------
#Adding attributes to the nodes (water depth, velocity and water surface elevation)
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

string="Yes"
for count in range(1, 3):
    print (string + str(" ") + str(count))

#Adding position of points to the values. Problem: strings are immutable
datavalues_position=[]
for lists in datavalues:
    datavalues_position.append([parts + str(" ") + str("hello") for parts in lists])


#new try
datavalues_position=[]
#sequence=[]
#for numbers in range (1,21134):
#    sequence.append(numbers)
for lists in datavalues:
    for numbers in range (1,21134):
        datavalues_position.append([parts + str(" ") + str(parts.index(numbers)) for parts in lists])



#converting string in datavalues to float
datavalues_float=[]
for parts in datavalues:
    datavalues_float.append([float(q) for q in parts])

n=0
for parts in datavalues_float:
    parts+str(n)
    n=n+1

datavalues_tuple=tuple(datavalues_float)

#NetworkX needs a dictionary for the attribute.
#Creating dictionary with timesteps as keys and datavalues (depth) as values.
Depth_TS={}
Depth_TS=dict(zip(Timesteps_tuple,datavalues_tuple))

#adding Depth_TS as attributes to the graph
for timesteps in Depth_TS:
    nx.set_node_attributes(G, 'Water_Depth', Depth_TS[timesteps])

#nx.draw_networkx(G,pos=d, node_size=10, with_labels=False)
#-------------------------------------------------------------
##############################################################
##--insertion: tidy up unnecessary variables from workspace-##
##############################################################
#---------------------
#del(Attribute_nodes, Attribute_pos, Attribute_yPos, Attribute_xPos, Attributes_List_Simple)
#del(Edge, Elem_R, Elem_L, Node1, Node1Copy, Node2, Steps, Timesteps, attributes, d, datavalues_float, datavalues, datavalues_tuple, field)
#del(row, rows, timesteps, splitLen, shape, q, parts, outputData, outputBase)
#del(data, fields, Tuple_Nodes, Depth_TS_out)
#del(line, lines, item, input)
#del(Timesteps_tuple, inner_l, shape, k)
#---------------------------------------

#------------------------------------------------------------------------
#########################################################################
##--Script part 3: Adding the house ID as an attribute to the network--##
#########################################################################
#---------------------
#converting the shapefile into a dictionary with XY-Location as keys and Feature-ID as house number. Therefore the attribute list needs to contain a field with the X and Y coordinates.
#In case it does not exist, manually add it to the shp.
#Access shapefile for nodes and coordinates
#manually join the table to shapefile of the nodes and then export the file and join again to the nodes. In the end delete not used attributes
#next: extract X, Y, Z-values and house ID from the joinedHouseNodes-dataset
#----------------------
##only carry out once as it creates permanent new files:
#arr = arcpy.da.FeatureClassToNumPyArray(houses_fc, ('idper_2d', 'X_Koord', 'Y_Koord'))
#print arr[1]
#shutil.copyfile(houses_fc_dbf, houses_fc_table)
#arcpy.TableToTable_conversion(houses_fc, "C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/", "outTable.dbf")
#arcpy.GenerateNearTable_analysis(houses_fc, Coordinates, Path + "/NearestPoints.dbf", "1000")
#arcpy.Near_analysis(houses_fc, Coordinates)
#----------------------
#converting the shapefile into a dictionary with XY-Location as keys and Feature-ID as house number. Therefore the attribute list needs to contain a field with the X and Y coordinates.
#Access shapefile for nodes and coordinates
fields_NodesHouses =NodesHousesJoined.fields[1:]
fields_name_NodesHousesJoined = [field[0] for field in fields_NodesHouses] #-> the fields names in a list
attributes_NodesHouses = NodesHousesJoined.records()

#Extract the nested list into a simplier list
Attributes_HousesNodes_List_Simple=[]
for inner_l in attributes_NodesHouses:
    for item in inner_l:
        Attributes_HousesNodes_List_Simple.append(item)

#extract nodeID, X-Koordinate, Y-Coordinate, Z-Coordinate, House-ID from attribute table from shapefile
Attribute_NodesHouses_nodeID = Attributes_HousesNodes_List_Simple[0::9]
Attribute_NodesHouses_xPos = Attributes_HousesNodes_List_Simple[1::9]
Attribute_NodesHouses_yPos = Attributes_HousesNodes_List_Simple[2::9]
Attribute_NodesHouses_zPos = Attributes_HousesNodes_List_Simple[3::9]
Attribute_NodesHouses_houseID = Attributes_HousesNodes_List_Simple[4::9]
Attribute_NodesHouses_pos = zip(Attribute_NodesHouses_xPos,Attribute_NodesHouses_yPos)

#making dictionary; not sure whether to make a dictionary based on the location as key (XY) or the NodeID
housesNodes_dict={}
housesNodes_dict=dict(zip(Attribute_NodesHouses_nodeID,Attribute_NodesHouses_houseID))

#adding housesNodes_dict as attributes to the graph
nx.set_node_attributes(G, 'HouseID', housesNodes_dict)

#Above lines ok
#--------------------------------------------------------------------------------
#lines bellow in testing
#---------------------------------------
#getting a table with houses affected from floods and the water depth at each time step
#nx.get_node_attributes(G, 'HouseID')
#nx.get_node_attributes(G, 'Water_Depth')

Depth_TS_copy=copy.deepcopy(Depth_TS)
EmptyList=[]
for TS in Depth_TS_copy:
    EmptyList.append(TS)

i=0
for lists in Depth_TS_copy:
    print type(lists)
    i=i+1
i=0
for lists in Depth_TS_copy:
    map(list, lists)
    i=i+1


i=1
for item in Depth_TS_copy.values():
    for parts in item:
        while i<21133:
            a= item.index(parts)
            [item.append(a)]
            i=i+1
for item in Depth_TS_copy.values():
    map(tuple,item)
    for i in range(1,21133):
        item.insert(i, i)



###########################
j=1
n=1
FloodedPoints=[]
for val in Depth_TS.keys():
    FloodedPoints.extend(val)
    for item in Depth_TS.values():
        for parts in item:
            if parts>0.0:
                Depth_TS.k
        #j=j+1


########################
i=1
k=0
for TS in Depth_TS:
    for location in TS:
        for items in location:
            k=k+1
            if items>0.0:
                print items
            #print "TS "+str(i)+" at location " +str(k) + " is " + location
    i=i+1