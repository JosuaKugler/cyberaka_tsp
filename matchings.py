#! /usr/bin/python3
import networkx as nx 
import matplotlib.pyplot as plt
import copy

G = nx.Graph()

edges = [(0,1,0.2),(1,2,0.4),(0,2,0.5),(0,4,0.4),(2,4,1.5),(4,3,0.4)]

G.add_weighted_edges_from(edges)

def draw(G, edges):
    pos = nx.circular_layout(G)

    # draw it
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edge_color='k', width=0.5) # show all edges, thin lines
    nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='b', width=2) # highlight elist

    plt.show()

def matching(G):
    edges = list(G.edges())
    edges.sort(key = lambda edge: G.edges[edge]["weight"]) # O(E log E)

    newedges = []
    for edge in edges:#gehe alle kanten durch
        testGraph = nx.Graph(newedges)
        testGraph.add_edge(*edge)
        isMatching = True
        for node in testGraph.nodes:
            if testGraph.degree[node] > 1:
                isMatching = False
                break
        if isMatching:
            newedges.append(edge)
        else:
            testGraph.clear()
    
    draw(G, newedges)
    return nx.Graph(newedges)


matching(G)
