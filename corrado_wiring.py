#!/usr/bin/python3

import pygraphviz as pgv

G = pgv.AGraph()

class Node(object):
  def __init__(self, name, pin_names):
    label = f'{name} '
    for pin_name in pin_names:
      label += f'| <{pin_name}> {pin_name} '
    G.add_node(name, label=label, ranksep=2.0)


def AddPath(node_pins, color):
  for i in range(len(node_pins) - 1):
      node, pin = node_pins[i]
      next_node, next_pin = node_pins[i + 1]
      G.add_edge(node, next_node, tailport=pin, headport=next_pin, color=color, penwidth=5)


G.node_attr['shape'] = 'record'
Node('battery', ['pos', 'neg'])
Node('main_fuse', ['fuse'])
Node('alternator', ['pos', 'sense'])
# TODO: Verify the pins match this diagram.
# https://www.pegasusautoracing.com/document.asp?DocID=TECH00109
Node('kill_switch', ['battery', 'z', 'w', 'starter'])
# TODO: Wire ignition coils pdm > z > coils.
Node('kill_switch_resistor', ['resistor'])
Node('ign_switch', ['1', '2'])
Node('razor_pdm', [
    'pos', 'neg',
    'PWROUT2a', 'NC1', 'CANH', 'IGNSW', 'SENSOR 5V1', 'SENSOR GND1', 'PWROUT3a,'
    'PWROUT2b', 'NC2', 'CANL', 'SENSOR 5V2', 'SENSOR GND2', 'PWROUT3b,'
    'PWROUT1a', 'ADIO2', 'ADIO4', 'ADIO6', 'ADIO8', 'PWROUT4a,'
    'PWROUT1b', 'ADIO1', 'ADIO3', 'ADIO5', 'ADIO7', 'NC3', 'PWROUT4b'
])
# TODO: Connect fuel pump.
# Node('fuel_pump', ['pos', 'neg'])

AddPath((
  ('battery', 'pos'),
  ('main_fuse', 'fuse'),
  ('kill_switch', 'battery'),
), 'red')
AddPath((
  ('alternator', 'pos'),
  ('kill_switch', 'starter'),
), 'red')
AddPath((
  ('kill_switch', 'starter'),
  ('kill_switch', 'w'),
  ('kill_switch_resistor', 'resistor'),
), 'red')
AddPath((
  ('kill_switch', 'starter'),
  ('razor_pdm', 'pos'),
), 'red')
AddPath((
  ('battery', 'neg'),
  ('razor_pdm', 'neg'),
), 'black')

# TODO: Verify blue is not in use for IGNSW.
AddPath((
  ('kill_switch', 'z'),
  ('ign_switch', '1'),
), 'blue')
AddPath((
  ('ign_switch', '2'),
  ('razor_pdm', 'IGNSW'),
), 'blue')

G.layout(prog='dot')
G.write('corrado_wiring.dot')
G.draw('corrado_wiring.png')
