import os
import sys
from sumolib import checkBinary
import traci
from core.STR_SUMO import *
from core.Util import *
from controllers.RouteController import RouteController
from controllers.CustomController import CustomController
from core.vehicle_generation import *
from typing import List

def start_simulation(controller: RouteController, vehicles: List[Vehicle], config_folder: str, config_file: str, sumotype: str) -> None:
  sumo_binary = checkBinary('sumo-gui') if sumotype == 'sumo-gui' else checkBinary('sumo')

  traci.start([sumo_binary, '-c', f'./configurations/{config_folder}/{config_file}', '--tripinfo-output', \
    f'./configurations/{config_folder}/trips_using_controller.trips.xml'])

  simulation = StrSumo(controller, controller.connection_info, {str(vehicle.vehicle_id): vehicle for vehicle in vehicles})
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
  
  vehicles: List[Vehicle] = WithControlledAndUncontrolled_OneStartOneDest("my_configurations", "CONFIG.sumocfg", "E0 E3 E8", "E8", 50, 50, 50)
  for v in vehicles:
    print(v.vehicle_id)
  connection_info = ConnectionInfo('./configurations/my_configurations/legitnet.net.xml')
  controller = CustomController(connection_info)
  start_simulation(controller, vehicles, 'my_configurations', 'CONFIG.sumocfg', 'sumo-gui')