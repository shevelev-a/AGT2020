import numpy as np
import re
import musicalbeeps
from audiolazy import midi2str
import sympy
import sys

def get_adjacency(dict_incs,size):
    m_adj = np.zeros((size,size), dtype=int)
    for key, value in dict_incs.items():
        for link in value:
            m_adj[key-1][link[0]-1] = link[1]
            m_adj[link[0]-1][key-1] = link[1]
    return m_adj

def get_L(m_adj):
    size = m_adj.shape[0] 
    m_deg = np.zeros((size,size), dtype=int)
    for i in range(size):
        m_deg[i][i] = sum(m_adj[i])
    return m_deg - m_adj,m_deg

def get_norm_L(m_adj):
    size = m_adj.shape[0] 
    D = np.zeros((size,size), dtype=int)
    for i in range(size):
        D[i][i] = sum(m_adj[i])
    D_inv_sqrt = np.sqrt(np.linalg.inv(D))
    L = D - m_adj
    normL  = np.matmul(np.matmul(D_inv_sqrt,L),D_inv_sqrt)
    return normL

def split_equal(value, parts):
    value = float(value)
    return [i*value/parts for i in range(0,parts+1)]

def get_graphs(file):
    list_graphs = []
    with open('test.txt','r') as f:
        for line in f:
            dict_incs = {}
            size = int(line[:line.find(',')])
            for link in re.finditer(r"\(.*?\)", line, re.MULTILINE):
                inc = link.group()[1:-1].split(',')
                if int(inc[0]) not in list(dict_incs):
                    dict_incs[int(inc[0])] = []
                dict_incs[int(inc[0])].append([int(inc[1]),int(inc[2])])
            list_graphs.append(get_adjacency(dict_incs,size))
    return list_graphs

if __name__ == "__main__":
    split_list = split_equal(2,51)
    player = musicalbeeps.Player(volume = 0.3, mute_output = False)

    path_to_file = sys.argv[-1]
    list_graphs = get_graphs(path_to_file)
    
    str_notes = []
    for graph in list_graphs:
        normL = get_norm_L(graph)
        spect = sympy.Matrix(normL).eigenvals()
        number_notes = {}
        for eigenvalue in list(spect):
            number_notes[np.argmin([abs(eigenvalue-i) for i in split_list])] = spect[eigenvalue]
        for num_note in list(number_notes):
            str_notes.append([re.sub('[#b]','',midi2str(num_note+69)) , number_notes[num_note]])
    
    for note in str_notes:
        player.play_note(note[0],note[1]*0.5)

