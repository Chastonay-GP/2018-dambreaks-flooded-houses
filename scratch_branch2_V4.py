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
import pandas as pd
import xlsxwriter
import csv
#---------------------------------------
##############
##--Inputs--##
##############
#--------------
basepath = "C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster"
with open(basepath+'/VersionGrobaufloesung/BASEMENT/aare.edg','r') as E:
    lines=E.readlines()  # type: List[str] #open .edg file in read-mode and shapefile for localisation of nodes
shape = shapefile.Reader(basepath+"/VersionGrobaufloesung/aareV10rechtsGrob_Quality_nodes.shp")
input = open(basepath+'/VersionGrobaufloesung/BASEMENT/aare_nds_depth.sol','r').read().strip('\n').split()
houses = shapefile.Reader(basepath+"/gebaeudeCentroids_LV03.shp") #adding houses as point-dataset from shapefile
Path=basepath+"/VersionGrobaufloesung/work.gdb"
houses_fc = basepath+"/gebaeudeCentroids_LV03.shp"
houses_fc_copy = houses_fc
houses_fc_dbf = basepath+"/gebaeudeCentroids_LV03.dbf"
houses_fc_table=Path+"/houses_fc_table.dbf"
Coordinates =basepath+"/VersionGrobaufloesung/aareV10rechtsGrob_Quality_nodes.shp"
NodesHousesJoined = shapefile.Reader(basepath+"/VersionGrobaufloesung/JoinGebaudeNodes.shp")
AllHouses_Waterdepth=basepath+'/AllHouses_Waterdepth.csv'
FloodedHouses_Waterdepth=basepath+'/CSV_exports/FloodedHouses_Waterdepth.csv'
FloodedHouses_Waterdepth=basepath+'/CSV_exports/FloodedHouses_Waterdepth.csv'
Temp_csv1=basepath+'/CSV_exports/Temp1.csv'
Temp_csv2=basepath+'/CSV_exports/Temp2.csv'
Temp_csv3=basepath+'/CSV_exports/Temp3.csv'
Test_csv=basepath+'/CSV_exports/array_Depth_TS_test.csv'
Datavalues_array_transpose=basepath + "CSV_exports/datavaluesarray_transpose.csv"
ArrayFlodded=basepath+"CSV_exports/array_flodded.csv"
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
Attribute_pos_ID = zip(Attribute_pos,Attribute_nodes)

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

#next step: integrating above code into for loop with splitting .sol-file into timesteps and add them to the subdictionarys from 'Depth_TS_out'
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
#------------------------------------------------------------------------
#############################################################################
##--Script part 3a: only carry out once as it creates permanent new files--##
#############################################################################
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
##########################################################
##--Script part 3b: converting the shp to a dictionary--##
##########################################################
#---------------------
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
Attribute_NodesHouses_pos_ID=zip(Attribute_NodesHouses_pos,Attribute_NodesHouses_houseID)

#making dictionary; not sure whether to make a dictionary based on the location as key (XY) or the NodeID
housesNodes_dict={}
housesNodes_dict=dict(zip(Attribute_NodesHouses_nodeID,Attribute_NodesHouses_houseID))

#adding housesNodes_dict as attributes to the graph
nx.set_node_attributes(G, 'HouseID', housesNodes_dict)

#----------------------------------------------------------------------------------
###################################################################################
##--Script part 4: Converting list with water depths to array for export to csv--##
###################################################################################
#---------------------

#converting list with water depths to array to be able to export as csv and visualise the table in excel
datavaluesarray = np.asarray(datavalues_float)
print datavaluesarray.shape #first element is number of rows, second element number of columns
x,y = datavaluesarray.shape
indices=np.tile(np.arange(1, y+1), (x, 1))
result=np.dstack((datavaluesarray , indices)).astype(float, int)
datavaluesarray_transpose=datavaluesarray.transpose()

#exporting array to csv
df=pd.DataFrame(datavaluesarray_transpose)
df.to_csv(Datavalues_array_transpose)

#the aim is to remove all values with 0 water depth. Not sure yet, whether to store it in a array, list or dictionary or
#to simply return the values bigger 0 and export those to csv
water_points=np.where(datavaluesarray_transpose>0)
water_points_array=np.asarray(water_points)
water_points_transpose=water_points_array.transpose()
df_new=pd.DataFrame(water_points_transpose)
df_new.to_csv(ArrayFlodded)

#Test whether datavalues_float even has numbers bigger 0 or not
#for lists in datavalues_float:
#    k=sum(lists)

#How many cells are bigger than 0? --> 26262
#n=0
#for points in water_points_transpose:
#    if points[1] >0:
#        n=n+1
#        print n

Depth_TS_copy=copy.deepcopy(Depth_TS)
#df_Depth_TS=pd.DataFrame(Depth_TS_copy)
#df_Depth_TS.to_csv(Test_csv)

#Adding new list to dictionary containing the Node_ID. As the list is sorted, the range(...) function works
Node_ID=[]
for i in range (1,21334):
    Node_ID.append(i)

Depth_TS_copy['Node_ID']=Node_ID
#print (len(Depth_TS_copy))

#add another column with house ID (in houses_Nodes_dict) if the snapped location of the houses matches with the location of a node
#in the following NodeID_HouseID is a list containing tuples where the first value is the Node ID and the second one the House ID if a house exists at that point
#otherwise 0 for no house
NodeID_HouseID=zip(Attribute_NodesHouses_nodeID,Attribute_NodesHouses_houseID)
NodeID_HouseID_sorted=sorted(NodeID_HouseID, key=lambda tup: tup[0])

#Test whether amount of houses is still the same as in input shapefile: 4789 --> correct
#n=0
#for points in NodeID_HouseID_sorted:
#    if points[1] >0:
#        n=n+1
#        print n

#Append the newly created sorted list NodeID_HouseID_sorted to the dictionary Depth_TS_copy
Depth_TS_copy['NodeID_HouseID']=NodeID_HouseID_sorted

#create List from dictionary
temp=[]
Depth_TS_total_List=[]

for key, value in Depth_TS_copy.items():
    temp=[key, value]
    Depth_TS_total_List.append(temp)

New =[list(i) for i in zip(*Depth_TS_total_List)]
#df_total=pd.DataFrame(New)
#df_total.to_csv("test.csv", index=True, header=True)


#reorganising list so that headers are included in sub-sublists
Depth_TS_total_List_corrected=[]
for m in range(1,28):
    Depth_TS_total_List_corrected.append([])

for part in Depth_TS_total_List:
    for subparts in part:
        if isinstance(subparts, (list,)):
            subparts.insert(0,part[0])

#deleting item with header as it is now included in the sub-sublist itself
Depth_TS_total_List_2=copy.deepcopy((Depth_TS_total_List))
for part in Depth_TS_total_List_2:
    part.pop(0)

##Problem: list is too nested: make it simpler
Depth_TS_easierList=[]

for nest in Depth_TS_total_List_2:
    Depth_TS_easierList.append(nest[0])
    Depth_TS_easierList.sort()

##Exporting to csv file
with open(Temp_csv1, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(Depth_TS_easierList)

#transpose table in csv
a=itertools.izip(*csv.reader(open(Temp_csv1, "rb")))
csv.writer(open(Temp_csv2, "wb")).writerows(a)

#filter list by points/nodes that have houses
Depth_TS_easierList_array=np.asarray(Depth_TS_easierList)

#transpose array again
Depth_TS_easierList_array_transposed=(list(zip(*Depth_TS_easierList_array)))

#make new list with only nodes with houses left
HouseNodesList=[]
HouseNodesList.append(Depth_TS_easierList_array_transposed[0])
for tuples in Depth_TS_easierList_array_transposed:
    for parts in tuples:
        if type(parts)==tuple:
            if parts[1]!=0:
                HouseNodesList.append(tuples)

#export to csv.
with open(AllHouses_Waterdepth, 'wb') as test:
    wr = csv.writer(test)
    wr.writerows(HouseNodesList)

#--------------------------------------------------------------------------------------------
#############################################################################################
##--Script part 5: Create another csv-file with only houses with are flodded at any point--##
#############################################################################################
#---------------------
FloodedHouses=[]
FloodedHouses.append(HouseNodesList[0])
for HouseTuples in HouseNodesList[1:]:
    if sum(HouseTuples[2:])>0.0:
        FloodedHouses.append(HouseTuples)

#export to csv
with open(FloodedHouses_Waterdepth, 'wb') as final:
    wr = csv.writer(final)
    wr.writerows(FloodedHouses)