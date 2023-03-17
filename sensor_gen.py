import numpy as np
import brains
import hexcoords
import unittest


def get_matrix_pos(position: hexcoords.Position, direction: hexcoords.Direction, idx, depth):
    return (position + (direction + hexcoords.DIRECTION_STEP * idx).vector() * depth).matrix_coordinates


def get_pheromone_data(position: hexcoords.Position, direction: hexcoords.Direction, pheros) -> brains.PheromoneData:
    [pheros_r, pheros_g, pheros_b] = pheros
    result = np.zeros((6, 2, 3))
    for idx in range(-2, 4):
        for depth in phero_depth_function(idx):
            try:
                coords = get_matrix_pos(position, direction, idx, depth)
                result[idx + 2, depth-1] = np.array([pheros_r[coords], pheros_g[coords], pheros_b[coords]])
            except:
                pass
    return result * (1/255)


def phero_depth_function(idx):
    return [1, 2]


def vision_depth_function(idx):
    if idx in [-2,-1,1,2,3]:
        return [1, 2]
    if idx == 0:
        return [1, 2, 3, 4, 5, 6]

def get_vision_data(position: hexcoords.Position, direction: hexcoords.Direction, world_map, enemies, friends) \
        -> brains.ViewData:
    result = np.zeros((6))
    for idx in range(-2, 4):
        depth_vals = vision_depth_function(idx)
        for depth in depth_vals:
            try:
                coords = get_matrix_pos(position, direction, idx, depth)
                if world_map[coords] == 1 or friends[coords] != -1:
                    result[idx + 2] = 1 / depth
                    break
                if enemies[coords] != -1:
                    result[idx + 2] = -1 / depth
                    break
            except:
                break
    return result





def get_sensor_data(position: hexcoords.Position, direction: hexcoords.Direction, world_map, enemies, friends) \
        -> brains.SensorData:
    result = np.full((6, 2),-1)
    for idx in range(-2, 4):
        for depth in sensor_depth_function(idx):
            try:
                coords = get_matrix_pos(position, direction, idx, depth)
                if world_map[coords] == 1:
                    result[idx+2, depth-1] = -2
                else:
                    result[idx+2, depth-1] = max(enemies[coords], friends[coords])
            except:
                pass
    return result


def sensor_depth_function(idx):
    return [1, 2]
