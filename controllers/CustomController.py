from controllers.RouteController import RouteController
from core.Util import ConnectionInfo, Vehicle
import sumolib
from typing import List, Dict

class CustomController(RouteController):

  def __init__(self, connection_info: ConnectionInfo) -> None:
    super().__init__(connection_info)
    self.net = sumolib.net.readNet(connection_info.net_filename)

  def make_decisions(self, vehicles: List[Vehicle], connection_info: ConnectionInfo) -> Dict[str, str]:
    local_targets: Dict[str, str] = {}
    for vehicle in vehicles:
      decision_list: List[str] = []
      # Our STR solution here
      
      # Our STR solution ends
      local_targets[str(vehicle.vehicle_id)] = self.compute_local_target(decision_list, vehicle)
    return local_targets