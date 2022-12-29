#!/usr/bin/python3

import pygraphviz as pgv

G = pgv.AGraph(strict=False)

def BuildLabel(name, pin_names):
  label = f'{name} '
  for pin_name in pin_names:
    label += f'| <{pin_name}> {pin_name} '
  return label


def BuildLinkLabel(name, pin_names):
  bracket_index = (9, 17, 25)
  label = f'{name} | '
  label += '{ '
  for i, pin_name in enumerate(pin_names):
    if i in bracket_index:
      label += '} | {'
    else:
      label += ' | '
    label += f'<{pin_name}> {pin_name} '
  label += '} '
  return label


class Node(object):
  def __init__(self, name, pin_names):
    if name.startswith('link_ecu') or name.startswith('razor_pdm'):
      label = BuildLinkLabel(name, pin_names)
    else:
      label = BuildLabel(name, pin_names)
    self.node = G.add_node(name, label=label, shape='record', style='bold')


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
  for node, pin in node_pins:
      color = node_color_map.get(node,{}).get(pin)
      if color:
        AddPath(node_pins, color)
        break

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
Node('link_ecu_b', LINK_ECU_B_PIN_COLOR_MAP.keys())
Node('engine_ground', ['Gnd'])
Node('deutsch_ecu_connector', list(range(1,24)))

Node('tps', ['5v', 'Sensor', 'Gnd'])
Node('map_sensor', ['Gnd', 'Sensor', '5v'])

AddPath((
  ('battery', 'pos'),
  ('main_fuse', 'fuse'),
  ('kill_switch', 'battery'),
), 'red')
AddPath((
  ('battery', 'neg'),
  ('engine_ground', 'Gnd'),
), 'black')
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

# ECU Power
AddPathWithMap((
  ('razor_pdm', 'PWROUT2a'),
  ('link_ecu_a', '+14V'),
))
AddPathWithMap((
  ('razor_pdm', 'PWROUT2b'),
  ('link_ecu_b', '+14V Aux9/10'),
))

# ECU Grounds
AddPath((
  ('link_ecu_a', 'Ground1'),
  ('deutsch_ecu_connector', '1'),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('link_ecu_a', 'Ground2'),
  ('deutsch_ecu_connector', '2'),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('link_ecu_b', 'Ground1'),
  ('deutsch_ecu_connector', '3'),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('link_ecu_b', 'Ground2'),
  ('deutsch_ecu_connector', '4'),
  ('engine_ground', 'Gnd'),
), 'black')

# TPS
AddPathWithMap((
  ('link_ecu_a', 'AnVolt1'),
  ('deutsch_ecu_connector', '5'),
  ('tps', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('deutsch_ecu_connector', '6'),
  ('tps', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  ('deutsch_ecu_connector', '7'),
  ('tps', 'Gnd'),
))

# MAP Sensor
AddPathWithMap((
  ('link_ecu_a', 'AnVolt2'),
  ('deutsch_ecu_connector', '8'),
  ('map_sensor', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('deutsch_ecu_connector', '9'),
  ('map_sensor', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  ('deutsch_ecu_connector', '10'),
  ('map_sensor', 'Gnd'),
))

G.layout(prog='dot')
G.write('corrado_wiring.dot')
G.draw('corrado_wiring.png')
