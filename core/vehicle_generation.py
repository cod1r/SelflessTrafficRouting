from random import randint
from core.Util import *
import sumolib
import subprocess
from xml.dom.minidom import parse
from typing import List
# This file generates vehicles, then writes them to a rou.xml file which the traci package will parse

def WithControlledAndUncontrolled_OneStartOneDest(config_folder: str, config_file, \
  start_location: str, end_location: str, num_controlled_vehicles: int, num_uncontrolled_vehicles: int, trip_end_time: int):

  CONFIG_DOM = parse(f'./configurations/{config_folder}/{config_file}')
  net_file: str = CONFIG_DOM.getElementsByTagName('net-file')[0].attributes['value'].nodeValue
  route_file_name: str = CONFIG_DOM.getElementsByTagName('route-files')[0].attributes['value'].nodeValue

  print(net_file, route_file_name)
  # Keep in mind that the amount of vehicles generated also depends on the network file
  subprocess.run([f"{os.getenv('SUMO_HOME')}/tools/randomTrips.py", "-n", net_file, "--random", "-r", \
    route_file_name, "-o", f"./configurations/{config_folder}/trips.trips.xml", "-p", f"{trip_end_time/num_uncontrolled_vehicles}", "-e", f"{trip_end_time}"])

  XML_FILE = parse(route_file_name)
  XML_ROOT = XML_FILE.documentElement
  vehicles_generated = XML_ROOT.getElementsByTagName('vehicle')
  interval: float | int = trip_end_time / num_controlled_vehicles
  # starting ID of our generated vehicles
  current_ID = len(vehicles_generated) + 100
  vehicles: List[Vehicle] = []
  release_time: float | int = float(vehicles_generated[-1].attributes['depart'].nodeValue)
  for _ in range(num_controlled_vehicles):
    deadline: int = randint(500, 700)
    vehicles.append(Vehicle(current_ID, end_location, release_time, deadline))
    current_ID += 1
    release_time += interval
  vehicles.sort(key=lambda x: x.start_time)
  for vehicle in vehicles:
    vhcl = XML_FILE.createElement('vehicle')
    vhcl.setAttribute('id', str(vehicle.vehicle_id))
    vhcl.setAttribute('depart', str(vehicle.start_time))
    
    route = XML_FILE.createElement('route')
    route.setAttribute('edges', str(start_location))
    vhcl.appendChild(route)
    XML_ROOT.appendChild(vhcl)
  
  with open(route_file_name, 'w') as R:
    R.write(XML_FILE.toprettyxml())
    R.flush()
  

def OnlyControlled_OneStartOneDest(config_folder: str, start_location: str, end_location: str):
  pass