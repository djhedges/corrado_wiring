#!/usr/bin/python3

import pygraphviz as pgv

G = pgv.AGraph()

G = pgv.AGraph()

G.node_attr['shape'] = 'record'
G.add_node('battery', label='{battery | {<pos> + |<neg> - }}')
G.add_node('fuel_pump', label='{fuel pump | {<pos> + |<neg> - }}')

G.add_edge('battery', 'fuel_pump', headport='pos', tailport='pos', color='red', penwidth=5)

G.layout(prog='dot')
G.write('corrado_wiring.dot')
G.draw('corrado_wiring.png')
