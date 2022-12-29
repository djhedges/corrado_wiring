#!/usr/bin/python3

import pygraphviz as pgv

G = pgv.AGraph(strict=False)

class Node(object):
  def __init__(self, name, pin_names):
    label = f'{name} '
    for pin_name in pin_names:
      label += f'| <{pin_name}> {pin_name} '
    self.node = G.add_node(name, label=label, ranksep=2.0)


def ParseColor(color):
  if ':' in color:
    color += ':' + color.split(':')[0]
  return f'{color}'

def AddPath(node_pins, color):
  for i in range(len(node_pins) - 1):
      node, pin = node_pins[i]
      next_node, next_pin = node_pins[i + 1]
      G.add_edge(node, next_node,
                 tailport=pin, headport=next_pin,
                 color=ParseColor(color), penwidth=3)


def AddPathWithMap(node_pins):
  node_color_map = {
    'link_ecu_a': LINK_ECU_A_PIN_COLOR_MAP,
    'link_ecu_b': LINK_ECU_B_PIN_COLOR_MAP,
  }
  first_node = node_pins[0][0]
  first_pin = node_pins[0][1]
  AddPath(node_pins, LINK_ECU_A_PIN_COLOR_MAP[first_pin])


LINK_ECU_A_PIN_COLOR_MAP = {
    'Inj4': 'brown:orange',
    'Inj3': 'brown:red',
    'Inj2': 'brown',
    'Inj1': 'brown:black',
    '+14V': 'red',
    '+8V': 'red:white',
    'Shield/Gnd': 'green',
    'Trig1': 'black',
    'Trig2': 'red',
    'Ign4': 'blue:orange',
    'Ign3': 'blue:red',
    'Ign2': 'blue:brown',
    'Ign1': 'blue',
    'AnVolt4': 'white:black',
    'Temp1': 'yellow',
    'Temp2': 'yellow:brown',
    'AnVolt1': 'yellow:blue',
    'Aux4': 'orange',
    'Aux3': 'orange:red',
    'Aux2': 'orange:brown',
    'Aux1': 'orange:black',
    'AnVolt2': 'white:brown',
    'DI3': 'grey:red',
    'GndOut': 'green',
    'Ground1': 'black',
    'Aux8': 'orange:VT',
    'Aux7': 'orange:blue',
    'Aux6': 'orange:green',
    'Aux5': 'orange:yellow',
    'DI1': 'grey:black',
    'DI2': 'grey:brown',
    '+5V': 'red:blue',
    'AnVolt3': 'yellow:black',
    'Ground2': 'black',
}
LINK_ECU_B_PIN_COLOR_MAP = {
    'Inj8': 'brown:violet',
    'Inj7': 'brown:blue',
    'Inj6': 'brown:green',
    'Inj5': 'brown:yellow',
    '+14V Aux9/10': 'red',
    'Temp3': 'yellow:red',
    'Temp4': 'yellow:orange',
    'Knock2': 'white',
    'Knock1': 'white',
    'Heater': 'blue:violet',
    'MES': 'blue:black',
    'Ign6': 'blue:green',
    'Ign5': 'blue:yellow',
    'RE': 'bluewhite',
    'Volt6': 'white:red',
    'Volt7': 'white:orange',
    'Shield/Gnd': 'green',
    'Aux9': 'violet',
    'DI6': 'grey:green',
    'DI5': 'grey:yellow',
    'DI4': 'grey:orange',
    'GndOut': 'green',
    'An Volt8': 'white:yellow',
    'An Volt9': 'white:green',
    'Ground1': 'black',
    'Aux10': 'violet:white',
    'DI10/CAN2H': 'grey:violet',
    'DI9/CAN2L': 'grey:white',
    'DI8': 'grey',
    'DI7': 'grey:blue',
    'IPE': 'white:blue',
    'APE': 'white',
    'AN Volt5': 'yellow:green',
    'Ground2': 'black',
}

G.node_attr['shape'] = 'record'
G.node_attr['style'] = 'bold'
Node('battery', ['pos', 'neg'])
Node('main_fuse', ['fuse'])
Node('alternator', ['pos', 'sense'])
# TODO: Verify the pins match this diagram.
# https://www.pegasusautoracing.com/document.asp?DocID=TECH00109
Node('kill_switch', ['battery', 'z', 'w', 'starter'])
Node('kill_switch_resistor', ['resistor'])
Node('ign_switch', ['1', '2'])
Node('razor_pdm', [
    'pos', 'neg',
    'PWROUT2a', 'NC1', 'CANH', 'IGNSW', 'SENSOR 5V1', 'SENSOR GND1', 'PWROUT3a',
    'PWROUT2b', 'NC2', 'CANL', 'SENSOR 5V2', 'SENSOR GND2', 'PWROUT3b',
    'PWROUT1a', 'ADIO2', 'ADIO4', 'ADIO6', 'ADIO8', 'PWROUT4a',
    'PWROUT1b', 'ADIO1', 'ADIO3', 'ADIO5', 'ADIO7', 'NC3', 'PWROUT4b'
])
Node('fuel_pump', ['pos', 'SendingA', 'SendingB', 'gnd'])
Node('link_ecu_a', LINK_ECU_A_PIN_COLOR_MAP.keys())
Node('deutsch_ecu_connector', [1,2,3])
Node('tps', ['5v', 'Sensor', 'Gnd'])

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

# TODO: Verify blue is not already in use.
AddPath((
  ('kill_switch', 'z'),
  ('ign_switch', '1'),
), 'blue')
AddPath((
  ('ign_switch', '2'),
  ('razor_pdm', 'IGNSW'),
), 'blue')

AddPath((
  ('fuel_pump', 'pos'),
  ('razor_pdm', 'PWROUT2a'),
), 'red')

AddPath((
  ('battery', 'neg'),
  ('fuel_pump', 'gnd'),
), 'black')

AddPathWithMap((
  ('link_ecu_a', 'AnVolt1'),
  ('deutsch_ecu_connector', '1'),
  ('tps', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('deutsch_ecu_connector', '2'),
  ('tps', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  ('deutsch_ecu_connector', '3'),
  ('tps', 'Gnd'),
))

G.layout(prog='dot')
G.write('corrado_wiring.dot')
G.draw('corrado_wiring.png')
