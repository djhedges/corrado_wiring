#!/usr/bin/python3

import pygraphviz as pgv

G = pgv.AGraph()

class Node(object):
  def __init__(self, name, pin_names):
    label = f'{name} '
    for pin_name in pin_names:
      label += f'| <{pin_name}> {pin_name} '
    G.add_node(name, label=label)


def AddPath(node_pins, color):
  for i in range(len(node_pins) - 1):
      node, pin = node_pins[i]
      next_node, next_pin = node_pins[i + 1]
      G.add_edge(node, next_node, tailport=pin, headport=next_pin, color=color, penwidth=5)


G.node_attr['shape'] = 'record'
Node('battery', ['pos', 'neg'])
Node('connector', ['1', '2'])
Node('fuel_pump', ['pos', 'neg'])

AddPath((
  ('battery', 'pos'),
  ('connector', '1'),
  ('fuel_pump', 'pos'),
), 'red')

G.layout(prog='dot')
G.write('corrado_wiring.dot')
G.draw('corrado_wiring.png')
