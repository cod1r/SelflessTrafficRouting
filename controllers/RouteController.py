from abc import ABC, abstractmethod
import random
import os
import sys
from core.Util import *
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("No environment variable SUMO_HOME!")
import traci
import sumolib

class RouteController(ABC):
    """
    Base class for routing policy

    To implement a scheduling algorithm, implement the make_decisions() method.
    Please use the boilerplate code from the example, and implement your algorithm between
    the 'Your algo...' comments.

    make_decisions takes in a list of vehicles and network information (connection_info).
        Using this data, it should return a dictionary of {vehicle_id: decision}, where "decision"
        is one of the directions defined by SUMO (see constants above). Any scheduling algorithm
        may be injected into the simulation, as long as it is wrapped by the RouteController class
        and implements the make_decisions method.

    :param connection_info: object containing network information, including:
                            - out_going_edges_dict {edge_id: {direction: out_edge}}
                            - edge_length_dict {edge_id: edge_length}
                            - edge_index_dict {edge_index_dict} keep track of edge ids by an index
                            - edge_vehicle_count {edge_id: number of vehicles at edge}
                            - edge_list [edge_id]

    """
    def __init__(self, connection_info: ConnectionInfo):
        self.connection_info = connection_info

    def compute_local_target(self, decision_list, vehicle):
        current_target_edge = vehicle.current_edge
        try:
            path_length = 0
            i = 0

            #the while is used to make sure the vehicle will not assume it arrives the destination beacuse the target edge is too short.
            while path_length <= max(vehicle.current_speed, 20):
                if current_target_edge == vehicle.destination:
                    break
                if i >= len(decision_list):
                    raise UserWarning(
                        "Not enough decisions provided to compute valid local target. TRACI will remove vehicle."
                    )

                choice = decision_list[i]
                if choice not in self.connection_info.outgoing_edges_dict[current_target_edge]:
                    raise UserWarning(
                            "Invalid direction. TRACI will remove vehicle."
                        )
                current_target_edge = self.connection_info.outgoing_edges_dict[current_target_edge][choice]
                path_length += self.connection_info.edge_length_dict[current_target_edge]

                if i > 0:
                    if decision_list[i - 1] == decision_list[i] and decision_list[i] == 't':
                        # stuck in a turnaround loop, let TRACI remove vehicle
                        return current_target_edge

                i += 1

        except UserWarning as warning:
            print(warning)

        return current_target_edge


    @abstractmethod
    def make_decisions(self, vehicles, connection_info):
        pass