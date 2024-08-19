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
    ego_vehicles = []
    actor_list = []
    npc_blueprints = []

    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(20.0)
        client.load_world("Town06")
        world = client.get_world()
        spectator = world.get_spectator()
        spectator.set_transform(carla.Transform(carla.Location(x=155.4,y=162.4, z=20),carla.Rotation(pitch=-30, yaw=-20, roll=0.000000)))

        blueprint_library = world.get_blueprint_library()
        ego_bp = blueprint_library.filter("model3")[0]
        
        spawn_point = carla.Transform(carla.Location(x=105,y=146.7, z=0.568),carla.Rotation(pitch=0.0, yaw=0.0, roll=0.000000))
        ego_vehicle = world.spawn_actor(ego_bp, spawn_point)
        ego_vehicles.append(ego_vehicle)
        

        ego_vehicle.apply_control(carla.VehicleControl(throttle=0.42, steer=0.0))


        tm = client.get_trafficmanager()
        tm.set_random_device_seed(0)
        random.seed(0)

        spawn_points = world.get_map().get_spawn_points()
        specified_spawn_points = [spawn_points[361], spawn_points[360], spawn_points[359], spawn_points[357], spawn_points[287], spawn_points[430]]
        models = ['dodge', 'audi', 'mini', 'mustang', 'prius']

        for vehicle in world.get_blueprint_library().filter('*vehicle*'):
            if any(model in vehicle.id for model in models):
                npc_blueprints.append(vehicle) 

        max_vehicles = len(specified_spawn_points)


        while True:
            world.tick()

            for i, spawn_point in enumerate(random.sample(specified_spawn_points, max_vehicles)):
                temp = world.try_spawn_actor(random.choice(npc_blueprints), spawn_point)
                if temp is not None:
                    actor_list.append(temp)

            for vehicle in actor_list:
                vehicle.set_autopilot(True)

            time.sleep(5)

            danger_car1 = random.choice(actor_list)
            danger_car2 = random.choice(actor_list)

            tm.distance_to_leading_vehicle(danger_car1, 0)
            tm.vehicle_percentage_speed_difference(danger_car1, -20)
            tm.distance_to_leading_vehicle(danger_car2, 0)
            tm.vehicle_percentage_speed_difference(danger_car2, -20)

    finally:

        for vehicle in ego_vehicles:
            vehicle.destroy()
     
        for actor in actor_list:
            actor.destroy()

        print("all cleaned up")

    
if __name__ == '__main__':

    main()