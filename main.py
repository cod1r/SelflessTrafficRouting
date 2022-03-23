'''
This test file needs the following files:
STR_SUMO.py, RouteController.py, Util.py, test.net.xml, test.rou.xml, myconfig.sumocfg and corresponding SUMO libraries.
'''
from core.STR_SUMO import StrSumo
import os
import sys
from xml.dom.minidom import parse, parseString
from core.Util import *
from controller.RouteController import *
from controller.DijkstraController import DijkstraPolicy
from controller.CustomController import *
from core.target_vehicles_generation_protocols import *
from typing import List
import csv
from multiprocessing import Process

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    # sys.path.append(tools)
else:
    sys.exit("No environment variable SUMO_HOME!")

from sumolib import checkBinary
import traci

# use vehicle generation protocols to generate vehicle list
def get_controlled_vehicles(route_filename, connection_info, \
    num_controlled_vehicles=10, num_uncontrolled_vehicles=20, pattern = 1):
    '''
    :param @route_filename <str>: the name of the route file to generate
    :param @connection_info <object>: an object that includes the map inforamtion
    :param @num_controlled_vehicles <int>: the number of vehicles controlled by the route controller
    :param @num_uncontrolled_vehicles <int>: the number of vehicles not controlled by the route controller
    :param @pattern <int>: one of four possible patterns. FORMAT:
            -- CASES BEGIN --
                #1. one start point, one destination for all target vehicles
                #2. ranged start point, one destination for all target vehicles
                #3. ranged start points, ranged destination for all target vehicles
            -- CASES ENDS --
    '''
    vehicle_dict = {}
    print(connection_info.net_filename)
    generator = target_vehicles_generator(connection_info.net_filename)

    # list of target vehicles is returned by generate_vehicles
    vehicle_list: List[Vehicle] = generator.generate_vehicles(num_controlled_vehicles, \
        num_uncontrolled_vehicles, \
        pattern, route_filename, connection_info.net_filename)

    for vehicle in vehicle_list:
        vehicle_dict[str(vehicle.vehicle_id)] = vehicle

    return vehicle_dict

def test_dijkstra_policy(vehicles):
    print("Testing Dijkstra's Algorithm Route Controller")
    scheduler = DijkstraPolicy(init_connection_info)
    run_simulation(scheduler, vehicles)

def test_custom_policy(vehicles):
    print("Testing Jason's Algorithm Route Controller")
    scheduler = CustomController(init_connection_info)
    run_simulation(scheduler, vehicles)

def run_simulation(scheduler, vehicles):

    simulation = StrSumo(scheduler, init_connection_info, vehicles)

    traci.start([sumo_binary, "-c", "./configurations/myconfig.sumocfg", \
                 "--tripinfo-output", "./configurations/trips.trips.xml", \
                 "--fcd-output", "./configurations/testTrace.xml"])

    total_time, end_number, deadlines_missed = simulation.run()
    with open(f"{str(type(scheduler).__name__)}.csv", "a") as O:
        csvwriter = csv.writer(O)
        csvwriter.writerow([total_time/end_number, end_number, deadlines_missed])
    traci.close()

if __name__ == "__main__":
    match sys.argv[1]:
        case '--sumo-gui':
            sumo_binary = checkBinary('sumo-gui')
        case '--sumo':
            sumo_binary = checkBinary('sumo')

    # parse config file for map file name
    dom = parse("./configurations/myconfig.sumocfg")

    net_file_node = dom.getElementsByTagName('net-file')
    net_file_attr = net_file_node[0].attributes

    net_file = net_file_attr['value'].nodeValue
    init_connection_info = ConnectionInfo("./configurations/"+net_file)

    route_file_node = dom.getElementsByTagName('route-files')
    route_file_attr = route_file_node[0].attributes
    route_file = "./configurations/"+route_file_attr['value'].nodeValue
    
    process_list: List[Process] = []
    for _ in range(int(sys.argv[2])):
        vehicles = get_controlled_vehicles(route_file, init_connection_info, 50, 50)
        #print the controlled vehicles generated
        for vid, v in vehicles.items():
            print("id: {}, destination: {}, start time:{}, deadline: {};".format(vid, \
                v.destination, v.start_time, v.deadline))
        p1 = Process(target=test_dijkstra_policy, args=(vehicles,))
        p2 = Process(target=test_custom_policy, args=(vehicles,))
        p1.start()
        p2.start()
        process_list += [p1, p2]

    for process in process_list:
        process.join()
