import os
import sys
from sumolib import checkBinary
import traci
from core.STR_SUMO import *
from core.Util import *
from xml.dom.minidom import parse
from core.vehicle_generation import *
from controllers.RouteController import *
from typing import List

def start_simulation(controller: RouteController, vehicles: List[Vehicle], config_folder: str, config_file: str, sumotype: str):
  sumo_binary = checkBinary('sumo-gui') if sumotype == 'sumo-gui' else checkBinary('sumo')

  traci.start([sumo_binary, '-c', f'./configurations/{config_folder}/{config_file}', '--tripinfo-output', \
    f'./configurations/{config_folder}/trips_using_controller.trips.xml'])

  dom = parse(f'./configurations/{config_folder}/{config_file}')
  net_file = dom.getElementsByTagName('net-file')[0].attributes

  connection_info = ConnectionInfo(f'./configurations/{config_folder}/{config_file}/{net_file}')
  simulation = StrSumo(controller, connection_info, vehicles)
  total_time, end_number, deadlines_missed = simulation.run()
  print("Average timespan: {}, total vehicle number: {}".format(str(total_time/end_number),\
      str(end_number)))
  print(str(deadlines_missed) + ' deadlines missed.')
  traci.close()

if __name__ == '__main__':
  if 'SUMO_HOME' not in os.environ:
    sys.exit('environment variable: SUMO_HOME must be set')
  else:
    print(os.getenv('SUMO_HOME'))
  
  WithControlledAndUncontrolled_OneStartOneDest("my_configurations", "CONFIG.sumocfg", "E0 E3 E8", "E8", 50, 50, 50)