import glob
import os
import sys


try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random
import time

def main():
    actor_list = []

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(20.0)
        client.load_world("Town06")
        world = client.get_world()

        settings = world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05
        world.apply_settings(settings)

        traffic_manager = client.get_trafficmanager()
        traffic_manager.set_synchronous_mode(True)

        traffic_manager.set_random_device_seed(0)
        random.seed(0)

        spectator = world.get_spectator()

        # spawn_points = world.get_map().get_spawn_points()

        # for i, spawn_point in enumerate(spawn_points):
        #     world.debug.draw_string(spawn_point.location, str(i), life_time=20)


        # print(world.get_map().get_spawn_points()) 

        spawn_points = world.get_map().get_spawn_points()
        specified_spawn_points = [spawn_points[361], spawn_points[360], spawn_points[359], spawn_points[357], spawn_points[287], spawn_points[430]]
        models = ['dodge', 'audi', 'mini', 'mustang', 'prius']
        npc_blueprints = []
        for vehicle in world.get_blueprint_library().filter('*vehicle*'):
            if any(model in vehicle.id for model in models):
                npc_blueprints.append(vehicle) 

        max_vehicles = 50
        max_vehicles = min([max_vehicles, len(specified_spawn_points)])

        for i, spawn_point in enumerate(random.sample(specified_spawn_points, max_vehicles)):
            temp = world.try_spawn_actor(random.choice(npc_blueprints), spawn_point)
            if temp is not None:
                actor_list.append(temp)

        for vehicle in actor_list:
            vehicle.set_autopilot(True)

        danger_car1 = actor_list[0]
        danger_car2 = actor_list[1]

        traffic_manager.distance_to_leading_vehicle(danger_car1, 0)
        traffic_manager.vehicle_percentage_speed_difference(danger_car1, -20)
        traffic_manager.distance_to_leading_vehicle(danger_car2, 0)
        traffic_manager.vehicle_percentage_speed_difference(danger_car2, -20)
        


        while True:
            world.tick()

    finally:
        for actor in actor_list:
            actor.destroy()
        print("all cleaned up")





if __name__ == '__main__':

    main()