#!/usr/bin/python3

import pygraphviz as pgv

G = pgv.AGraph(strict=False, rankdir='LR', ranksep=10)

AEM_GAUGES = ['coolant_temp_gauge', 'transmission_temp_gauge', 'fuel_pressure_gauge']
AEM_SENSORS = ['aem_coolant_temp_sensor', 'aem_transmission_temp_sensor', 'aem_fuel_pressure_sensor']


class DeutschConnector(object):

  def __init__(self):
    self.index = 0

  def GetFreePin(self):
    self.index += 1
    return self.index

DCE = DeutschConnector()
DCP = DeutschConnector()
DCC = DeutschConnector()  # Console (keypad & gauges)
DCC_PWR = DCC.GetFreePin()
DCC_GND = DCC.GetFreePin()


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
  def __init__(self, name, pin_names, label_func=BuildLabel):
    label = label_func(name, pin_names)
    self.node = G.add_node(name, label=label, shape='record', style='bold')


def ParseColor(color):
  if ':' in color:
    color += ':' + color.split(':')[0]
  return f'black:{color}:black'

def AddPath(node_pins, color):
  for i in range(len(node_pins) - 1):
      node, pin = node_pins[i]
      next_node, next_pin = node_pins[i + 1]
      G.add_edge(node, next_node,
                 tailport=pin, headport=next_pin,
                 label=f'{node}:{pin}<{color}>{next_node}:{next_pin}',
                 labeltooltip=f'{node}:{pin}<{color}>{next_node}:{next_pin}',
                 color=ParseColor(color),
                 penwidth=2.5)

def ClusterNodes(nodes, label):
  G.add_subgraph(nodes, name=f'cluster_{label}', style='filled', color='grey', label=label)


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
Node('link_ecu_a', LINK_ECU_A_PIN_COLOR_MAP.keys())#, label_func=BuildLinkLabel)
Node('link_ecu_b', LINK_ECU_B_PIN_COLOR_MAP.keys())#, label_func=BuildLinkLabel)
Node('link_keypad', [1, 2, 3, 4])
Node('engine_ground', ['Gnd'])
Node('deutsch_ecu_connector', list(range(1,48)))
Node('deutsch_pdm_connector', list(range(1,5)))
Node('deutsch_console_connector', list(range(1,16)))

Node('tps', ['5v', 'Sensor', 'Gnd'])
Node('map_sensor', ['Gnd', 'Sensor', '5v'])

Node('cam_sensor', ['5v', 'Sensor', 'Gnd'])
Node('crank_sensor', ['5v', 'Sensor', 'Gnd'])

Node('knock1', ['Sig+', 'Sig-', 'Scr'])
Node('knock2', ['Sig+', 'Sig-', 'Scr'])
ClusterNodes(['knock1', 'knock2'], 'Knock Sensors')

Node('intake_temp_sensor', ['Sig+', 'Sig-'])
Node('oil_temp_sensor', ['Sig+', 'Sig-'])
Node('coolant_temp_sensor', ['Sig+', 'Sig-'])

Node('idle_stablizer_valve', ['Pos', 'Gnd'])
Node('vapor_purge_valve', ['Pos', 'Gnd'])

Node('fuel_pump', ['pos', 'SendingA', 'SendingB', 'gnd'])
Node('aux_coolant_pump', ['Pos', 'Gnd'])

for aem_gauge in AEM_GAUGES:
  Node(aem_gauge, ['Ground', '12v', 'RS232', '5vOut', 'Sig+', 'Sig-'])
for aem_sensor in AEM_SENSORS:
  Node(aem_sensor, ['Sig+', 'Sig-'])

for i in range(1, 7):
    Node(f'injector{i}', ['Pos', 'Gnd'])
ClusterNodes([f'injector{i}' for i in range(1, 7)], 'Injectors')

Node('icm', ['Transistor1ecu', 'Transistor2ecu', 'Transistor3ecu',
             'Transistor3coil', 'Gnd', 'Transistor2coil', 'Transistor1coil'])
Node('coil', ['Coil3', 'Coil2', 'Coil1', 'Ubatt'])
ClusterNodes(['icm', 'coil'], label='Coilpack')

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

# Fuel Pump
AddPath((
  ('fuel_pump', 'pos'),
  ('razor_pdm', 'PWROUT3a'),
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

# Keypad
AddPath((
  ('razor_pdm', 'ADIO3'),
  ('deutsch_console_connector', DCC_PWR),
  ('link_keypad', 1),
), 'red')
AddPath((
  ('battery', 'neg'),
  ('deutsch_console_connector', DCC_GND),
  ('link_keypad', 2),
), 'black')

# CAN
AddPathWithMap((
  ('razor_pdm', 'CANH'),
  ('link_ecu_b', 'DI10/CAN2H'),
))
AddPathWithMap((
  ('razor_pdm', 'CANL'),
  ('link_ecu_b', 'DI9/CAN2L'),
))
AddPathWithMap((
  ('link_keypad', '4'),
  ('deutsch_console_connector', DCC.GetFreePin()),
  ('link_ecu_b', 'DI10/CAN2H'),
))
AddPathWithMap((
  ('link_keypad', '3'),
  ('deutsch_console_connector', DCC.GetFreePin()),
  ('link_ecu_b', 'DI9/CAN2L'),
))

# Injectors
inj_pwr_pin = DCP.GetFreePin()
AddPath((
  ('razor_pdm', 'PWROUT1a'),
  ('deutsch_pdm_connector', inj_pwr_pin),
), 'red')
for i in range(1, 7):
  AddPath((
    ('deutsch_pdm_connector', inj_pwr_pin),
    (f'injector{i}', 'Pos'),
  ), 'red')
  a_or_b = 'a' if i < 5 else 'b'
  AddPathWithMap((
    (f'link_ecu_{a_or_b}', f'Inj{i}'),
    ('deutsch_ecu_connector', DCE.GetFreePin()),
    (f'injector{i}', 'Gnd'),
  ))

# Cam Sensor
DCE_5v = DCE.GetFreePin()
AddPathWithMap((
  ('link_ecu_a', 'Trig1'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('cam_sensor', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('deutsch_ecu_connector', DCE_5v),
  ('cam_sensor', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'Shield/Gnd'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('cam_sensor', 'Gnd'),
))

# Crank Sensor
AddPathWithMap((
  ('link_ecu_a', 'Trig2'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('crank_sensor', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('deutsch_ecu_connector', DCE_5v),
  ('crank_sensor', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'Shield/Gnd'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('crank_sensor', 'Gnd'),
))

# Coils
AddPath((
  ('razor_pdm', 'PWROUT4a'),
  ('coil', 'Ubatt'),
), 'red')
AddPath((
  ('icm', 'Gnd'),
  ('engine_ground', 'Gnd'),
), 'black')
for i in range(1, 4):
  AddPathWithMap((
    ('link_ecu_a', f'Ign{i}'),
    ('icm', f'Transistor{i}ecu'),
  ))
  AddPath((
    ('icm', f'Transistor{i}coil'),
    ('coil', f'Coil{i}'),
  ), 'white')  # TODO: Decide on wire color.

# Coolant Temp Sensor
AddPathWithMap((
  ('link_ecu_a', 'Temp1'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('coolant_temp_sensor', 'Sig+'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('coolant_temp_sensor', 'Sig-'),
))

# TPS
AddPathWithMap((
  ('link_ecu_a', 'AnVolt1'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('tps', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('deutsch_ecu_connector', DCE_5v),
  ('tps', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('tps', 'Gnd'),
))

# MAP Sensor
AddPathWithMap((
  ('link_ecu_a', 'AnVolt2'),
  # TODO: Figure out where MAP Sensor will be mounted and
  # if this will still be connected to the deutsch connector.
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('map_sensor', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('deutsch_ecu_connector', DCE_5v),
  ('map_sensor', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('map_sensor', 'Gnd'),
))

# ECU Grounds
AddPath((
  ('link_ecu_a', 'Ground1'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('link_ecu_a', 'Ground2'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('link_ecu_b', 'Ground1'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('link_ecu_b', 'Ground2'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('engine_ground', 'Gnd'),
), 'black')

# Knock Sensors
for i in range(1, 3):
  AddPathWithMap((
    ('link_ecu_b', f'Knock{i}'),
    ('deutsch_ecu_connector', DCE.GetFreePin()),
    (f'knock{i}', 'Sig+'),
  ))
  AddPathWithMap((
    ('link_ecu_b', 'Shield/Gnd'),
    ('deutsch_ecu_connector', DCE.GetFreePin()),
    (f'knock{i}', 'Sig-'),
  ))
  AddPathWithMap((
    ('link_ecu_b', 'Shield/Gnd'),
    ('deutsch_ecu_connector', DCE.GetFreePin()),
    (f'knock{i}', 'Scr'),
  ))

# Intake Temp Sensor
AddPathWithMap((
  ('link_ecu_b', 'Temp3'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('intake_temp_sensor', 'Sig+'),
))
AddPathWithMap((
  ('link_ecu_b', 'GndOut'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('intake_temp_sensor', 'Sig-'),
))

# Oil Temp Sensor
AddPathWithMap((
  ('link_ecu_b', 'Temp4'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('oil_temp_sensor', 'Sig+'),
))
AddPathWithMap((
  ('link_ecu_b', 'GndOut'),
  ('deutsch_ecu_connector', DCE.GetFreePin()),
  ('oil_temp_sensor', 'Sig-'),
))

# Idle Stablizer Valve
AddPath((
  ('razor_pdm', 'ADIO7'),
  ('deutsch_pdm_connector', DCP.GetFreePin()),
  ('idle_stablizer_valve', 'Pos'),
), 'red')  # TODO: Decide on color.
AddPath((
  ('idle_stablizer_valve', 'Gnd'),
  ('engine_ground', 'Gnd'),
), 'black')

# Purge Valve
AddPath((
  ('razor_pdm', 'ADIO5'),
  ('deutsch_pdm_connector', DCP.GetFreePin()),
  ('vapor_purge_valve', 'Pos'),
), 'red')  # TODO: Decide on color.
AddPath((
  ('vapor_purge_valve', 'Gnd'),
  ('engine_ground', 'Gnd'),
), 'black')

# Aux Coolant Pump
AddPath((
  ('razor_pdm', 'ADIO1'),
  ('deutsch_pdm_connector', DCP.GetFreePin()),
  ('aux_coolant_pump', 'Pos'),
), 'red')
AddPath((
  ('aux_coolant_pump', 'Gnd'),
  ('engine_ground', 'Gnd'),
), 'black')

# Gauages
for aem_gauge in AEM_GAUGES:
  AddPath((
    (aem_gauge, '12v'),
    ('deutsch_console_connector', DCC_PWR),
  ), 'red')
  AddPath((
    (aem_gauge, 'Ground'),
    ('deutsch_console_connector', DCC_GND),
  ), 'black')
for i, aem_sensor in enumerate(AEM_SENSORS):
  for sign in ('+', '-'):
    AddPath((
      (AEM_GAUGES[i], f'Sig{sign}'),
      ('deutsch_console_connector', DCP.GetFreePin()),
      ('deutsch_ecu_connector', DCE.GetFreePin()),
      (aem_sensor, f'Sig{sign}'),
    ), 'white')  # TODO: Decide on wire color.
ClusterNodes(AEM_GAUGES + ['link_keypad'], 'Console')
ClusterNodes(AEM_SENSORS, 'AEM Sensors')



G.layout(prog='dot')
G.write('corrado_wiring.dot')
print('Rendering PNG')
G.draw('corrado_wiring.png')
print('Rendering SVG')
G.draw('corrado_wiring.svg')
