import os
import networkx as nx
import pygraphviz
from networkx.drawing.nx_agraph import write_dot
import matplotlib.pyplot as plt
import copy
import sys

plotframe = sys.argv[1]
print(plotframe)
with open(plotframe, "r") as f:
    lines = f.readlines()

importantlines = []
for line in lines:
    if "%END" in line:
        break
    else:
        importantlines.append(line)

functioncodewords = []
for line in importantlines:
    for word in line.split():
        functioncodewords.append(word)

functioncodewithpercent = ''.join(functioncodewords)
functioncode = ''
for char in functioncodewithpercent:
    if char != '%':
        functioncode += char

def isCyclicUtil(G, v, visited, parent):
    visited[v] = True
    for i in G.neighbors(v): 
        # If the node is not visited then recurse on it 
        if  visited[i]==False :  
            if(isCyclicUtil(G,i,visited,v)): 
                return True
        # If an adjacent vertex is visited and not parent of current vertex, 
        # then there is a cycle 
        elif  parent!=i:
            return True
    return False


def isCyclic(G): #gleich wie Tiefensuche, im Idealfall O(V+E)
        visited = {}
        for node in G.nodes():
            visited[node] = False

        for i in G.nodes(): 
            if visited[i] ==False:
                if(isCyclicUtil(G, i,visited,list(G.nodes())[-1]))== True: 
                    return True

        return False

def graphListFromKruskal(G): # in dieser Implementierung O(E*(E + V)), optimal ist O(E log E)
    graphlist = [copy.deepcopy(G)]
    nodes = set(G)
    edges = list(G.edges)
    edges.sort(key = lambda edge: G.edges[edge]["weight"]) # O(E log E)
    edges.reverse()
    
    colorededges = set([])
    while len(colorededges) < len(nodes)-1:
        edge = edges.pop() # lowest weight
        if not isCyclic(nx.Graph(colorededges | set([edge]))): # isCyclic: <= O(V + E)
            colorededges.add(edge)
            G.edges[edge]['color'] = 'red'
            graphlist.append(copy.deepcopy(G))

    return graphlist


def graphListFromDepthSearch(G): #schlechte implementierung, im Idealfall O(V+E)
    nodes = set(G)
    edges = set(G.edges)

    Gtilde = copy.deepcopy(G)
    v = nodes.pop()
    nodestack = [v]
    colorednodes = {v}
    G.nodes[v]['color'] = 'red'
    colorededges = set([])
    graphlist = [copy.deepcopy(G)]
    while nodes:
        #problem: direction of edge not guaranteed!
        adjacentedges = set(Gtilde.edges(v))
        for (start, end) in colorededges: #get all non-marked adjacent edges
            if (start, end) in adjacentedges:
                adjacentedges.remove((start, end))
            if (end, start) in adjacentedges:
                adjacentedges.remove((end, start))
        if len(adjacentedges) == 0:
            nodestack = nodestack[:-1] # remove current v
            try:
                v = nodestack[-1]
            except:
                break
        else:
            for (a,b) in adjacentedges:
                if a == v:
                    w = b
                else:
                    w = a
                if w in colorednodes:
                    Gtilde.remove_edge(v,w)
                else:
                    colorededges.add((w,v))
                    G.edges[(w,v)]['color'] = 'red'
                    colorednodes.add(w)
                    G.nodes[w]['color'] = 'red'
                    v = w
                    nodestack.append(w)
                    graphlist.append(copy.deepcopy(G))
                    break

    return graphlist


def graphListFromPrim(G):   #hier: sehr ineffiziente implementierung, mit geeigneter Datenstruktur: O(E + V log V)
    graphlist = [copy.deepcopy(G)]
    nodes = set(G)
    edges = set(G.edges)

    colorednodes = {nodes.pop()}
    colorededges = set([])
    while nodes:
        #problem: direction of edge not guaranteed!
        adjacentedges = set(G.edges(colorednodes))
        for (start, end) in colorededges: #get all non-marked adjacent edges
            if (start, end) in adjacentedges:
                adjacentedges.remove((start, end))
            if (end, start) in adjacentedges:
                adjacentedges.remove((end, start))
        #now find out which of these edges form a circle
        no_circle_adjacent_edges = set([])
        for edge in adjacentedges:
            hypoGraph = nx.Graph()
            hypoGraph.add_edges_from(colorededges)
            hypoGraph.add_edge(*edge)
            if not isCyclic(hypoGraph):# found cycle, so it is not usable
                no_circle_adjacent_edges.add(edge)
        
        #print("no_circle_adjacent_edges: ", no_circle_adjacent_edges)
        min_edge = no_circle_adjacent_edges.pop()
        min_val = G.edges[min_edge]['weight']
        for edge in no_circle_adjacent_edges:
            if (G.edges[edge]['weight'] < min_val):
                min_edge = edge
                min_val = G.edges[min_edge]['weight']
        
        #print('min_edge: ', min_edge)
        
        colorededges.add(min_edge) #gets colored
        G.edges[min_edge]['color'] = 'red'
        startnode, endnode = min_edge[0], min_edge[1]
        if startnode not in colorednodes:
            colorednodes.add(startnode)
            nodes.remove(startnode)
        else:
            colorednodes.add(endnode)
            nodes.remove(endnode)
        graphlist.append(copy.deepcopy(G))

    return graphlist

def setlabelweight(G):
    for edge in G.edges():
        try:
            G.edges[edge]['label'] = G.edges[edge]['weight']
            #G.edges[edge]['minlen'] = G.edges[edge]['weight']
        except:
            print("no weights given")
            pass
        G.edges[edge]['style'] = 'edge'
    for node in G.nodes():
        G.nodes[node]['style'] = 'vertex'
        try: 
            if G.nodes[node]['color'] == 'red':
                G.nodes[node]['style'] = 'selected vertex'
        except:
            pass


def visualizegraphalgorithm(algorithm, name, nodes, edges, scale):
    G = nx.Graph()
    G.add_nodes_from(nodes)
    try:
        G.add_weighted_edges_from(edges, color = 'black')
    except:
        G.add_edges_from(edges, color = 'black')
    algorithms = {"prim":graphListFromPrim, "kruskal":graphListFromKruskal, "depthsearch":graphListFromDepthSearch}
    graphlist = algorithms[algorithm](G)

    for graph in graphlist:
        setlabelweight(graph)

    importantlines.append(r"%END" + "\n")
    importantlines.append(r"\begin{frame}" + "\n")
    if not os.path.exists(name):
        os.mkdir(name)
    parentpath = os.getcwd()
    os.chdir(name)
    for index, graph in enumerate(graphlist):
        filename = 'graph' + str(index) + '.dot'
        filenametikz = 'graph' + str(index) + '.tex'
        write_dot(graph, filename)
        os.system(f"dot -Txdot {filename} | dot2tex -ftikz -tmath --figonly --tikzedgelabels --prog=circo --graphstyle='scale={scale}, auto' > {filenametikz}")#--nodeoptions scale=0.5
        importantlines.append(f"\\only<{index+1}>" + "{\n")
        importantlines.append(r"\input{" + name + "/" + filenametikz + "}\n")
        importantlines.append("}\n")
    importantlines.append(r"\end{frame}")
    os.chdir(parentpath)
    with open(plotframe, "w") as f:
        f.writelines(importantlines)

print(functioncode)
exec(functioncode, {"visualizegraphalgorithm": visualizegraphalgorithm})
