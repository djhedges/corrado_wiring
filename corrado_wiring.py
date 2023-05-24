#!/usr/bin/python3

# TODOs:
# Oil gauges 
# Pi
# Cameras
# 4G Router
# EGT
# Reverse?
# Clutch switch?
# Alternator one wire sense to resistor or dash light

import csv
import os
import pygraphviz as pgv


class PerNodeGraphs(pgv.AGraph):
  """Memorizes args for recreating per node graphs and images at the end."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.initial_args = args
    self.initial_kwargs = kwargs
    self.add_node_kwargs = {}
    self.node_graph = {}

  def add_node(self, node, **kwargs):
    super().add_node(node, **kwargs)
    self.add_node_kwargs[node] = kwargs
    self.node_graph[node] = pgv.AGraph(*self.initial_args, **self.initial_kwargs)
    self.node_graph[node].add_node(node, **kwargs)

  def add_edge(self, node, next_node, **kwargs):
    super().add_edge(node, next_node, **kwargs)
    for n in (node, next_node):
      graph = self.node_graph[n]
      graph.add_edge(node, next_node, **kwargs)

G = PerNodeGraphs(strict=False, rankdir='LR', ranksep=1.5, concentrate='true')
CSV_ROWS = []

AEM_GAUGES = ['coolant_temp_gauge', 'transmission_temp_gauge', 'fuel_pressure_gauge']
AEM_SENSORS = ['aem_coolant_temp_sensor', 'aem_transmission_temp_sensor', 'aem_fuel_pressure_sensor']

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
    'Inj7': 'brown:blue',  # Wire color stolen for Ign switch.
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
    'RE': 'blue:white',
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


def BuildLabel(name, pin_names):
  label = f'{name} '
  for pin_name in pin_names:
    label += f'| <{pin_name}> {pin_name} '
  return label


class Node(object):
  def __init__(self, name, pin_names):
    self.node = G.add_node(name, label=BuildLabel(name, pin_names), shape='record', style='bold')


class DeutschConnector(object):

  def __init__(self, name, total_pins, high_pins=None):
    self.name = name
    self.node = Node(name, list(range(1, total_pins + 1)))
    self.pins = list(range(1, total_pins + 1))
    if high_pins:
      for pin in high_pins:
        self.pins.remove(pin)
    self.high_pins = high_pins or []

  def GetFreePin(self, pin=None):
    if pin:
      self.pins.remove(pin)
    pin = pin if pin else self.pins.pop(0)
    return self.name, str(pin)

  def GetHighPin(self, pin=None):
    if pin:
      self.high_pins.remove(pin)
    pin = pin if pin else self.high_pins.pop(0)
    return self.name, str(pin)


# https://mavenspeed.com/collections/b2t-engineering/products/dual-connector-bulkhead
DCE = DeutschConnector('deutsch_engine_connector', 47, high_pins=[1,2,3,4,34])  # Engine
DCE_5v = DCE.GetFreePin(5)
DCE_5v_Gnd = DCE.GetFreePin()
DCE_INJ_PWR_PIN = DCE.GetFreePin()
DCE_12v = DCE.GetFreePin()
DCEB = DeutschConnector('deutsch_engine_bay_connector', 47, high_pins=[1,2,3,4,34])  # Engine Bay
DCEB_5v = DCEB.GetFreePin(5)
DCEB_5v_Gnd = DCEB.GetFreePin()
DCEB_12v = DCEB.GetHighPin()
# DT 12 Way https://www.prowireusa.com/deutsch-dt-series-connector-kits.html
DCC = DeutschConnector('deutsch_console_connector', 12)  # Console (keypad)
DCC_PWR = DCC.GetFreePin(1)
DCC_GND = DCC.GetFreePin(2)
DCG = DeutschConnector('deutsch_gauge_connector', 12)  # Gauges
DCG_PWR = DCG.GetFreePin(1)
DCG_GND = DCG.GetFreePin(2)
# DT 4 Way
DCF = DeutschConnector('deutsch_fan_connector', 4)

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
  CSV_ROWS.append((':'.join(node_pins[0]), ':'.join(node_pins[-1])))

def ClusterNodes(nodes, label, color='grey'):
  G.add_subgraph(nodes, name=f'cluster_{label}', style='filled', color=color, label=label)


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

Node('battery', ['pos', 'neg'])
Node('alternator', ['pos', 'sense'])
Node('starter', ['pos', 'gnd', 'solenoid'])
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
Node('link_ecu_a', LINK_ECU_A_PIN_COLOR_MAP.keys())
Node('link_ecu_b', LINK_ECU_B_PIN_COLOR_MAP.keys())
Node('link_keypad', 
     ['+12V',      # Pin1/Red
      'Ground',    # Pin2/Black
      'CAN Low',   # Pin3/Blue
      'CAN High']) # Pin4/White

# Grounds
Node('engine_ground', ['Gnd'])
Node('engine_bay_ground', ['Gnd'])
Node('acc_ground', ['ground'])
Node('trunk_ground', ['ground'])

Node('traqmate', ['pos', 'gnd', 'rpm'])
Node('labjack', [
    'sgnd0', ' spc', ' sgnd1', ' vs0',
    'fio7', ' fio6', ' gnd0', ' vs1',
    'fio5', ' fio4', ' gnd1', ' vs2',
    'vs3', ' gnd2', ' dac0', ' dac1',
    'vs4', ' gnd3', ' fio2', ' fio3',
    'vs5', ' gnd4', ' fio0', ' fio1',
])
Node('usb_hub', ['+', '_', '-'])

Node('tps', ['5v', 'Sensor', 'Gnd'])
Node('map_sensor', ['Gnd', 'Sensor', '5v'])
Node('LSU4.9', ['APE', 'IPE', 'Heater', 'Heater Power', 'MES', 'RE'])

Node('cam_sensor', ['5v', 'Sensor', 'Gnd'])
Node('crank_sensor', ['5v', 'Sensor', 'Gnd'])

Node('knock1', ['Sig+', 'Sig-', 'Scr'])
Node('knock2', ['Sig+', 'Sig-', 'Scr'])

Node('intake_temp_sensor', ['Sig+', 'Sig-'])
Node('oil_pressure_sensor', ['Sig+', 'Sig-'])
Node('coolant_low_sensor', ['Sig+', 'Sig-'])
Node('oil_switch_0.25_bar', ['Switch'])
Node('oil_switch_1.40_bar', ['Switch'])

Node('idle_stablizer_valve', ['Pos', 'Gnd'])
Node('vapor_purge_valve', ['Pos', 'Gnd'])

Node('brake_lights', ['pos', 'gnd'])
Node('fuel_pump', ['pos', 'SendingA', 'SendingB', 'gnd'])
Node('aux_coolant_pump', ['Pos', 'Gnd'])

Node('spal_fan_1', ['pos', 'gnd'])
Node('spal_fan_2', ['pos', 'gnd'])
Node('transponder', ['pos', 'gnd'])

for aem_gauge in AEM_GAUGES:
  Node(aem_gauge, ['Ground', '12v', 'RS232', '5vOut', 'Sig+', 'Sig-'])
for aem_sensor in AEM_SENSORS:
  Node(aem_sensor, ['Sig+', 'Sig-'])
Node('front_brake_pressure', ['0v', '5v', 'Sig'])
Node('rear_brake_pressure', ['0v', '5v', 'Sig'])

for i in range(1, 7):
    Node(f'injector{i}', ['Pos', 'Gnd'])

Node('icm', ['Transistor1ecu', 'Transistor2ecu', 'Transistor3ecu',
             'Transistor3coil', 'Gnd', 'Transistor2coil', 'Transistor1coil'])
Node('coil', ['Coil3', 'Coil2', 'Coil1', 'Ubatt'])
Node('wiper', ['high', 'low', 'park', 'gnd'])

AddPath((
  ('battery', 'pos'),
  ('kill_switch', 'battery'),
), 'red')
AddPath((
  ('battery', 'neg'),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('engine_ground', 'Gnd'),
  ('engine_bay_ground', 'Gnd'),
), 'black')
AddPath((
  ('kill_switch', 'starter'),
  ('starter', 'pos'),
), 'red')
AddPath((
  ('razor_pdm', 'PWROUT3a'),
  DCE.GetHighPin(),
  ('starter', 'solenoid'),
), 'red')
AddPath((
  ('razor_pdm', 'PWROUT3b'),
  DCE.GetHighPin(),
  ('starter', 'solenoid'),
), 'red')
AddPath((
  ('kill_switch', 'starter'),
  # Ensure it goes back to killswitch per hpacademy.
  DCE.GetHighPin(),  
  ('alternator', 'pos'),
), 'red')
AddPath((
  # Ensure it goes back to killswitch per hpacademy.
  ('kill_switch', 'starter'),
  DCE.GetFreePin(),  
  ('alternator', 'sense'),
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

AddPath((
  ('kill_switch', 'z'),
  ('ign_switch', '1'),
), 'brown:blue')
AddPath((
  ('razor_pdm', 'IGNSW'),
  DCC.GetFreePin(),
  ('ign_switch', '2'),
), 'blue')

# Brake Lights
AddPath((
  ('battery', 'neg'),
  ('trunk_ground', 'ground'),
), 'black')
AddPath((
  ('brake_lights', 'pos'),
  ('razor_pdm', 'PWROUT2a'),
), 'red')
AddPath((
  ('brake_lights', 'pos'),
  ('razor_pdm', 'PWROUT2b'),
), 'red')
AddPath((
  ('trunk_ground', 'ground'),
  ('brake_lights', 'gnd'),
), 'black')

# Fuel Pump - Rockauto listed a fuel pump with avg 8amp current draw.
AddPath((
  ('fuel_pump', 'pos'),
  ('razor_pdm', 'PWROUT1a'),
), 'red')
AddPath((
  ('trunk_ground', 'neg'),
  ('fuel_pump', 'gnd'),
), 'black')

# ECU Power  (hpacademy Fury 10A steady current draw)
AddPathWithMap((
  ('razor_pdm', 'ADIO1'),
  ('link_ecu_a', '+14V'),
))
AddPathWithMap((
  ('razor_pdm', 'ADIO1'),
  ('link_ecu_b', '+14V Aux9/10'),
))

# Keypad
AddPath((
  ('link_keypad', '+12V'),
  DCC_PWR,
  ('razor_pdm', 'ADIO6'),
), 'red')
AddPath((
  ('battery', 'neg'),
  ('acc_ground', 'ground'),
  DCC_GND,
  ('link_keypad', 'Ground'),
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
  ('link_keypad', 'CAN High'),
  DCC.GetFreePin(),
  ('link_ecu_b', 'DI10/CAN2H'),
))
AddPathWithMap((
  ('link_keypad', 'CAN Low'),
  DCC.GetFreePin(),
  ('link_ecu_b', 'DI9/CAN2L'),
))

# Injectors
AddPath((
  ('razor_pdm', 'ADIO3'),
  DCE_INJ_PWR_PIN,
), 'red')
for i in range(1, 7):
  AddPath((
    DCE_INJ_PWR_PIN,
    (f'injector{i}', 'Pos'),
  ), 'red')
  a_or_b = 'a' if i < 5 else 'b'
  AddPathWithMap((
    (f'link_ecu_{a_or_b}', f'Inj{i}'),
    DCE.GetFreePin(),
    (f'injector{i}', 'Gnd'),
  ))

# Cam Sensor
AddPathWithMap((
  ('link_ecu_a', 'Trig1'),
  DCE.GetFreePin(),
  ('cam_sensor', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  DCE_5v,
  ('cam_sensor', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'Shield/Gnd'),
  DCE.GetFreePin(),
  ('cam_sensor', 'Gnd'),
))

# Crank Sensor
AddPathWithMap((
  ('link_ecu_a', 'Trig2'),
  DCE.GetFreePin(),
  ('crank_sensor', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  DCE_5v,
  ('crank_sensor', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'Shield/Gnd'),
  DCE.GetFreePin(),
  ('crank_sensor', 'Gnd'),
))

# Coils <8 amps according to bosch motorsports catalog.
AddPath((
  ('razor_pdm', 'PWROUT1b'),
  DCE.GetHighPin(),
  ('coil', 'Ubatt'),
), 'red')
AddPath((
  ('icm', 'Gnd'),
  ('engine_bay_ground', 'Gnd'),
), 'black')
for i in range(1, 4):
  AddPathWithMap((
    ('link_ecu_a', f'Ign{i}'),
    DCEB.GetFreePin(),
    ('icm', f'Transistor{i}ecu'),
  ))
  AddPath((
    ('icm', f'Transistor{i}coil'),
    ('coil', f'Coil{i}'),
  ), 'white')  # TODO: Decide on wire color.

# Wiper Motor
AddPath((
  ('razor_pdm', 'ADIO7'),
  DCEB.GetFreePin(),
  ('wiper', 'high'),
), 'red')
AddPath((
  ('razor_pdm', 'ADIO8'),
  DCEB.GetFreePin(),
  ('wiper', 'park'),
), 'white')  # TODO: Decide on wire color.
AddPath((
  ('wiper', 'gnd'),
  ('engine_bay_ground', 'Gnd'),
), 'black')

# Coolant Low Sensor
AddPathWithMap((
  ('link_ecu_a', 'Aux4'),
  DCEB.GetFreePin(),
  ('coolant_low_sensor', 'Sig+'),
))
AddPathWithMap((
  ('link_ecu_b', 'GndOut'),
  DCEB_5v_Gnd,
  ('coolant_low_sensor', 'Sig-'),
))

# TPS
AddPathWithMap((
  ('link_ecu_a', 'AnVolt1'),
  DCE.GetFreePin(),
  ('tps', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  DCE.GetFreePin(),
  ('tps', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  DCE_5v_Gnd,
  ('tps', 'Gnd'),
))

# MAP Sensor
AddPathWithMap((
  ('link_ecu_a', 'AnVolt2'),
  DCEB.GetFreePin(),
  ('map_sensor', 'Sensor'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  DCEB_5v,
  ('map_sensor', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  DCEB_5v_Gnd,
  ('map_sensor', 'Gnd'),
))

# Oil Pressure Switches
AddPathWithMap((
  ('link_ecu_a', 'DI1'),
  DCE.GetFreePin(),
  ('oil_switch_0.25_bar', 'Switch'),
))
AddPathWithMap((
  ('link_ecu_a', 'DI2'),
  DCE.GetFreePin(),
  ('oil_switch_1.40_bar', 'Switch'),
))

# ECU A Grounds
AddPath((
  ('link_ecu_a', 'Ground1'),
  DCE.GetFreePin(),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('link_ecu_a', 'Ground2'),
  DCE.GetFreePin(),
  ('engine_ground', 'Gnd'),
), 'black')

# Intake Temp Sensor
AddPathWithMap((
  ('link_ecu_b', 'Temp3'),
  DCE.GetFreePin(),
  ('intake_temp_sensor', 'Sig+'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  DCE_5v_Gnd,
  ('intake_temp_sensor', 'Sig-'),
))

# Oil Temp Sensor
AddPathWithMap((
  ('link_ecu_a', 'AnVolt3'),
  DCE.GetFreePin(),
  ('oil_pressure_sensor', 'Sig+'),
))
AddPathWithMap((
  ('link_ecu_b', 'GndOut'),
  DCE_5v_Gnd,
  ('oil_pressure_sensor', 'Sig-'),
))

# Knock Sensors
for i in range(1, 3):
  AddPathWithMap((
    ('link_ecu_b', f'Knock{i}'),
    DCE.GetFreePin(),
    (f'knock{i}', 'Sig+'),
  ))
  AddPathWithMap((
    ('link_ecu_b', 'Shield/Gnd'),
    DCE.GetFreePin(),
    (f'knock{i}', 'Sig-'),
  ))
  AddPathWithMap((
    ('link_ecu_b', 'Shield/Gnd'),
    DCE.GetFreePin(),
    (f'knock{i}', 'Scr'),
  ))

# ECU B Grounds
AddPath((
  ('link_ecu_b', 'Ground1'),
  DCE.GetFreePin(),
  ('engine_ground', 'Gnd'),
), 'black')
AddPath((
  ('link_ecu_b', 'Ground2'),
  DCE.GetFreePin(),
  ('engine_ground', 'Gnd'),
), 'black')

# LSU4.9
# Quick start guide
# https://dealers.linkecu.com/can-lambda
AddPathWithMap((
  ('link_ecu_b', 'Heater'),
  DCEB.GetFreePin(),
  ('LSU4.9', 'Heater'),
))
AddPathWithMap((
  ('link_ecu_b', 'MES'),
  DCEB.GetFreePin(),
  ('LSU4.9', 'MES',),
))
AddPathWithMap((
  ('link_ecu_b', 'RE'),
  DCEB.GetFreePin(),
  ('LSU4.9', 'RE'),
))
AddPathWithMap((
  ('link_ecu_b', 'IPE'),
  DCEB.GetFreePin(),
  ('LSU4.9', 'IPE'),
))
AddPathWithMap((
  ('link_ecu_b', 'APE'),
  DCEB.GetFreePin(),
  ('LSU4.9', 'APE'),
))
AddPath((
  ('razor_pdm', 'ADIO2'),
  DCEB_12v,
  ('LSU4.9', 'Heater Power'),
), 'red')

# Idle Stablizer Valve
AddPath((
  ('razor_pdm', 'ADIO5'),
  DCE_12v,
  ('idle_stablizer_valve', 'Pos'),
), 'red')  # TODO: Decide on color.
AddPathWithMap((
  ('link_ecu_a', 'Aux2'),
  DCE.GetFreePin(),
  ('idle_stablizer_valve', 'Gnd'),
))

# Purge Valve
AddPath((
  ('razor_pdm', 'ADIO2'),
  DCEB_12v,
  ('vapor_purge_valve', 'Pos'),
), 'red')  # TODO: Decide on color.
AddPathWithMap((
  ('link_ecu_a', 'Aux3'),
  DCEB.GetFreePin(),
  ('vapor_purge_valve', 'Gnd'),
))

# Aux Coolant Pump 5 amp fuse
AddPath((
  ('razor_pdm', 'ADIO5'),
  DCE_12v,
  ('aux_coolant_pump', 'Pos'),
), 'red')
AddPath((
  ('aux_coolant_pump', 'Gnd'),
  ('engine_ground', 'Gnd'),
), 'black')

# Fans
# 16 awg
# 7.6 amp part #30100398 
# https://www.holley.com/products/cooling/fans/parts/30100398
# 6.3 amps part #30100392
# https://www.holley.com/products/discontinued_product/parts/30100392
AddPath((
  ('razor_pdm', 'PWROUT4a'),
  DCEB.GetHighPin(),
  DCF.GetFreePin(),
  ('spal_fan_1', 'pos'),
), 'red')
AddPath((
  ('razor_pdm', 'PWROUT4b'),
  DCEB.GetHighPin(),
  DCF.GetFreePin(),
  ('spal_fan_2', 'pos'),
), 'red')
AddPath((
  ('engine_bay_ground', 'Gnd'),
  DCF.GetFreePin(),
  ('spal_fan_1', 'gnd'),
), 'black')
AddPath((
  ('engine_bay_ground', 'Gnd'),
  DCF.GetFreePin(),
  ('spal_fan_2', 'gnd'),
), 'black')

# Transponder
AddPath((
  ('razor_pdm', 'ADIO2'),
  DCEB_12v,
  ('transponder', 'pos'),
), 'red')
AddPath((
  ('engine_bay_ground', 'Gnd'),
  ('transponder', 'gnd'),
), 'black')


# AEM Gauages
for aem_gauge in AEM_GAUGES:
  AddPath((
    (aem_gauge, '12v'),
    DCG_PWR,
    ('razor_pdm', 'ADIO6'),
  ), 'red')
  AddPath((
    (aem_gauge, 'Ground'),
    DCG_GND,
    ('acc_ground', 'ground'),
  ), 'black')
for i, aem_sensor in enumerate(AEM_SENSORS):
  for sign in ('+', '-'):
    AddPath((
      (AEM_GAUGES[i], f'Sig{sign}'),
      DCG.GetFreePin(),
      DCE.GetFreePin(),
      (aem_sensor, f'Sig{sign}'),
    ), 'white')  # TODO: Decide on wire color.
AddPathWithMap((
  ('link_ecu_a', 'Temp1'),
  DCG.GetFreePin(),
  ('coolant_temp_gauge', '5vOut'),
))

# Traqmate
AddPath((
  ('traqmate', 'pos'),
  DCC_PWR,
  ('razor_pdm', 'ADIO6'),
), 'red')
AddPath((
  ('traqmate', 'gnd'),
  DCC_GND,
  ('acc_ground', 'ground'),
), 'black')
AddPathWithMap((
  ('traqmate', 'rpm'),
  DCC.GetFreePin(),
  ('link_ecu_a', 'Aux1'),
))

# USB Hub
AddPath((
  ('usb_hub', '+'),
  DCC_PWR,
), 'red')
AddPath((
  ('usb_hub', '-'),
  DCC_GND,
), 'black')

## Brake Pressure Sensors
AddPathWithMap((
  ('link_ecu_b', 'An Volt8'),
  ('front_brake_pressure', 'Sig'),
))
AddPathWithMap((
  ('link_ecu_b', 'An Volt9'),
  ('rear_brake_pressure', 'Sig'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('front_brake_pressure', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', '+5V'),
  ('rear_brake_pressure', '5v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  ('front_brake_pressure', '0v'),
))
AddPathWithMap((
  ('link_ecu_a', 'GndOut'),
  ('rear_brake_pressure', '0v'),
))
## /Brake Pressure Sensors

# Labjack
AddPath((
  ('coolant_temp_gauge', '5vOut'),
  DCG.GetFreePin(),
  ('labjack', 'fio0'),
), color='white') # TODO: Decide on wire color.
AddPath((
  ('fuel_pressure_gauge', '5vOut'),
  DCG.GetFreePin(),
  ('labjack', 'fio6'),
), color='white') # TODO: Decide on wire color.
AddPath((
  ('transmission_temp_gauge', '5vOut'),
  DCG.GetFreePin(),
  ('labjack', 'fio7'),
), color='white') # TODO: Decide on wire color.
# /Labjack

ClusterNodes(['battery', 'kill_switch', 'alternator', 'kill_switch_resistor'], 
             'Kill Switch')
ClusterNodes(['razor_pdm', 'link_ecu_a', 'link_ecu_b'], 'Link ECU & PDM')
ClusterNodes(['icm', 'coil', 'LSU4.9', 'map_sensor', 'coolant_low_sensor', 'vapor_purge_valve', 
              'spal_fan_1', 'spal_fan_2', 'deutsch_fan_connector', 'engine_bay_ground', 'wiper',
              'deutsch_engine_bay_connector', 'transponder'], 
              label='Engine Bay')
ClusterNodes(AEM_GAUGES + [
             'link_keypad', 'ign_switch', 'usb_hub', 'labjack', 'traqmate',
             'deutsch_gauge_connector', 'deutsch_console_connector'], 
             'Console')
ClusterNodes([
    'deutsch_engine_connector',
    'cam_sensor', 'crank_sensor', 'tps', 
    'oil_switch_0.25_bar',  'oil_switch_1.40_bar', 'oil_pressure_sensor',
    'intake_temp_sensor', 'knock1', 'knock2', 'engine_ground',
    'idle_stablizer_valve', 'aux_coolant_pump', 'starter',
    ] + AEM_SENSORS + [f'injector{i}' for i in range(1, 7)], 'Engine')
ClusterNodes(['fuel_pump', 'brake_lights', 'trunk_ground'], 'Trunk')

# Ensures any deleted nodes are removed and not lingering around.
cwd_files = os.listdir()
for filename in os.listdir():
  if 'corrado_wiring.py' in cwd_files and filename.endswith('.png'):
   os.rename(filename, os.path.join('/tmp/', filename))

G.layout(prog='dot')
print('Rendering DOT')
G.write('corrado_wiring.dot')
print('Rendering PNG')
G.draw('corrado_wiring.png')
print('Rendering SVG')
G.draw('corrado_wiring.svg')
print('Writing corrado_ecu_pdm_pinout.csv')
with open('corrado_ecu_pdm_pinout.csv', 'w', newline='') as csv_file:
  writer = csv.writer(csv_file)
  writer.writerow(('-', '-'))
  dupe_rows = []
  for i, row in enumerate(CSV_ROWS):
    if 'link_ecu' in row[1] or 'razor_pdm' in row[1]:
      CSV_ROWS[i] = (row[1], row[0])  # Swap so ECU/PDM is first.
    if (('link_ecu' in row[0] or 'link_ecu' in row[1]) and 
        ('razor_pdm' in row[0] or 'razor_pdm' in row[1]) and
        row not in CSV_ROWS):
      dupe_rows.append(row)  # Duplicate row to provide a clear indication of used pins in first column.
    if row[1] == ':'.join(DCE_INJ_PWR_PIN):
      CSV_ROWS[i] = (row[0], 'injectors:Pos')
  for row in sorted(CSV_ROWS + dupe_rows):
    if 'link_ecu' in row[0] or 'razor_pdm' in row[0]: # Filter on ECU/PDM.
      writer.writerow(row)

# Adds neighbor pins to per node graphs.
for node, graph in G.node_graph.items():
  for neighbor in G.neighbors(node):
    graph.add_node(neighbor, **G.add_node_kwargs[neighbor])
  graph.layout(prog='dot')
  print(f'Rendering {node} PNG')
  graph.draw(f'{node}.png')
