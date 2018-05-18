import networkx as nx
import matplotlib.pyplot as plt
import itertools

#Create empty graph
G=nx.Graph()

#open .edg file in read-mode
with open('C:/Users/Dominik/OneDrive/Dokumente/UniBe/Master/FS18/Geodatenanalyse/Projekt/VogtEugster/VersionGrobaufloesung/BASEMENT/aare.edg','r') as E:
    lines=E.readlines()  # type: List[str]

#This gets the limits of the lines that contain the header / footer delimiters
data=lines[5:]

#Now, you can parse the lines into rows by splitting the line on whitespace
rows=[line.split() for line in data]

# Columns have integer data, so we convert the string data to float
Edge = [int(row[0]) for row in rows]
Node1 = [int(row[1]) for row in rows]
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

type(Elem_R)
print len(Edge), len(Node1), len(Node2), len(Elem_L), len(Elem_R)

#Adding leading zeros to data
[str(item).zfill(5) for item in Edge]
#--------------------------------------------------------------------------------
#Problem from here on is that the add.nodes_from-function only takes tuples as inputs. To have numbers with equal digits I had to include leading zeros.
#Now the integers in the list of Edge must be tuples, but does not work somehow... why??

Edge_T = tuple(Edge)

Node1 = [row[1] for row in rows]
Node2 = [row[2] for row in rows]
Elem_L = [row[3] for row in rows]
Elem_R = [row[4] for row in rows]

Edge_S=str(Edge)
Edge_T =tuple(Edge_S)
G.add_nodes_from(Node1)
G.add_edges_from(Edge)

nx.draw_networkx(G, node_color='orange', node_size=400)
print nx.info(G)

#G.add_edges_from(Edge)