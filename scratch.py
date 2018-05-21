import networkx as nx
import matplotlib.pyplot as plt
import itertools
import shapefile
import numpy as np

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


#Adding nodes from Node1Copy --> Error: Too many values??
#G.add_nodes_from(Node1Copy)
#type(Node1Copy)
#len(Node1Copy)
#G.nodes()

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
nx.draw_networkx(G,pos=d)

#--------------------------------------------------------------------------------
Test=nx.read_shp('C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/aareV10rechtsGrob_Quality_nodes.shp')
Test = shapefile.Reader('C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/aareV10rechtsGrob_Quality_nodes.shp')
pos = {k: v for k,v in enumerate(Test.nodes())}
X=nx.Graph() #Empty graph
X.add_nodes_from(pos.keys()) #Add nodes preserving coordinates
l=[set(x) for x in Test.edges()] #To speed things up in case of large objects
edg=Tuple_Nodes
X.add_edges_from(edg)
#edg=[tuple(k for k,v in pos.items() if v in sl) for sl in l] #Map the G.edges start and endpoints onto pos
nx.draw_networkx_nodes(X,pos,node_size=100,node_color='r')
X.add_edges_from(edg)
nx.draw_networkx_edges(X,pos)