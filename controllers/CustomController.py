from controller.RouteController import RouteController
from core.Util import ConnectionInfo, Vehicle
import heapq
import sumolib
import traci
from typing import List, Dict, Tuple, Union

class CustomController(RouteController):

    def __init__(self, connection_info: ConnectionInfo) -> None:
        super().__init__(connection_info)

    def make_decisions(self, vehicles: List[Vehicle], \
            connection_info: ConnectionInfo) -> Dict[str, str]:
        local_targets: Dict[str, str] = {}
        for vehicle in vehicles:
            # Our STR solution here
            decision_list = \
                    self.path_finding_with_vehicle_per_edge(
                        vehicle.current_edge, vehicle.destination
                    )
            # Our STR solution ends
            local_targets[vehicle.vehicle_id] = \
                    self.compute_local_target(decision_list, vehicle)
        return local_targets

    def dijkstra(self, start: str, end: str) -> List[str]:
        heap: List[Tuple[Union[float, int], str]] = []
        decision_list: List[str] = []
        edge_cost: Dict[str, Union[float, int]] = {
            edge: float('inf') for edge in self.connection_info.edge_list
        }
        edge_cost[start] = 0
        heapq.heappush(heap, (0, start))
        path_list: Dict[str, Tuple[str, str]] = {}
        while len(heap) > 0:
            min_edge: Tuple[Union[float, int], str] = heapq.heappop(heap)
            if min_edge[1] == end:
                break
            for direction, out_going_edge in \
                    self.connection_info.outgoing_edges_dict[min_edge[1]].items():
                cost = min_edge[0] + self.connection_info.edge_length_dict[out_going_edge]
                if out_going_edge not in path_list and cost < edge_cost[out_going_edge]:
                    edge_cost[out_going_edge] = cost
                    heapq.heappush(heap, (cost, out_going_edge))
                    path_list[out_going_edge] = (direction, min_edge[1])
        temp_edge = end
        while temp_edge != start and end in path_list:
            decision_list.append(path_list[temp_edge][0])
            temp_edge = path_list[temp_edge][1]
        decision_list.reverse()
        return decision_list

    def path_finding_with_vehicle_per_edge(self, start: str, end: str) -> List[str]:
        heap: List[Tuple[Union[float, int], str]] = []
        decision_list: List[str] = []
        edge_cost: Dict[str, Union[float, int]] = {
            edge: float('inf') for edge in self.connection_info.edge_list
        }
        edge_cost[start] = 0
        heapq.heappush(heap, (0, start))
        path_list: Dict[str, Tuple[str, str]] = {}
        while len(heap) > 0:
            min_edge: Tuple[Union[float, int], str] = heapq.heappop(heap)
            if min_edge[1] == end:
                break
            for direction, out_going_edge in \
                    self.connection_info.outgoing_edges_dict[min_edge[1]].items():
                out_going_edge_length = self.connection_info.edge_length_dict[out_going_edge]
                edge_vehicle_count = self.connection_info.edge_vehicle_count[out_going_edge]
                cost = (1+(edge_vehicle_count/out_going_edge_length)) * \
                        (min_edge[0] + out_going_edge_length)
                if out_going_edge not in path_list and cost < edge_cost[out_going_edge]:
                    edge_cost[out_going_edge] = cost
                    heapq.heappush(heap, (cost, out_going_edge))
                    path_list[out_going_edge] = (direction, min_edge[1])
        temp_edge = end
        while temp_edge != start and end in path_list:
            decision_list.append(path_list[temp_edge][0])
            temp_edge = path_list[temp_edge][1]
        decision_list.reverse()
        return decision_list

    def path_finding_with_speed(self, start: str, end: str, vehicles: List[Vehicle]) -> List[str]:
        heap: List[Tuple[Union[float, int], str]] = []
        decision_list: List[str] = []
        edge_cost: Dict[str, Union[float, int]] = {
            edge: float('inf') for edge in self.connection_info.edge_list
        }
        edge_cost[start] = 0
        heapq.heappush(heap, (0, start))
        path_list: Dict[str, Tuple[str, str]] = {}
        while len(heap) > 0:
            min_edge: Tuple[Union[float, int], str] = heapq.heappop(heap)
            if min_edge[1] == end:
                break
            for direction, out_going_edge in \
                    self.connection_info.outgoing_edges_dict[min_edge[1]].items():
                ids: List[str] = traci.edge.getLastStepVehicleIDs(out_going_edge)
                avg_speed_for_edge: Union[float, int] = \
                        sum(list(map(lambda x: x.vehicle_id, vehicles)))/len(ids)
                cost = (min_edge[0] + \
                        self.connection_info.edge_length_dict[out_going_edge]) / avg_speed_for_edge
                if out_going_edge not in path_list and cost < edge_cost[out_going_edge]:
                    edge_cost[out_going_edge] = cost
                    heapq.heappush(heap, (cost, out_going_edge))
                    path_list[out_going_edge] = (direction, min_edge[1])
        temp_edge = end
        while temp_edge != start and end in path_list:
            decision_list.append(path_list[temp_edge][0])
            temp_edge = path_list[temp_edge][1]
        decision_list.reverse()
        return decision_list
