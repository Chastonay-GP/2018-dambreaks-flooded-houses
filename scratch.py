import networkx as nx
import matplotlib.pyplot as plt
import itertools
import shapefile

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
print Tuple_Nodes

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
len(Node1Copy)

#Access shapefile for nodes and coordinates
fields =shape.fields[1:]
fields_name = [field[0] for field in fields] #-> the fields names in a list
print fields_name
attributes = shape.records()
print attributes

#--------------------------------------------------------------------------------
print nx.info(G)

pe = nx.Graph()
pe.add_node('p1', posxy=(ap[0][0], ap[0][1]))
pe.add_node('p2', posxy=(ap[1][0], ap[1][2]))
pe.add_node('p3', posxy=(ap[2][0], ap[2][3]))
pe.add_node('p4', posxy=(ap[3][0], ap[3][4]))
pe.add_node('p5', posxy=(ap[4][0], ap[4][5]))
pe.add_cycle(['p1','p2','p3','p4','p5'])
positions = nx.get_node_attributes(pe,'posxy')
nx.draw(pe, positions, node_size=500)
#nx.draw_networkx(G)
#nx.draw_networkx_edges(G)
#plt.show(G)
#nx.draw(G)
#nx.draw(G,pos=nx.spring_layout(G))



