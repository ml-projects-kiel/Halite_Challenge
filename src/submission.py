# Imports helper functions
import random

import numpy as np
from kaggle_environments import make
from kaggle_environments.envs.halite.helpers import *
from numpy import linalg as LA


# Returns best direction to move from one position (fromPos) to another (toPos)
# Example: If I'm at pos 0 and want to get to pos 55, which direction should I choose?
def getDirTo(fromPos, toPos, size):
    fromX, fromY = divmod(fromPos[0], size), divmod(fromPos[1], size)
    toX, toY = divmod(toPos[0], size), divmod(toPos[1], size)
    if fromY < toY:
        return ShipAction.NORTH
    if fromY > toY:
        return ShipAction.SOUTH
    if fromX < toX:
        return ShipAction.EAST
    if fromX > toX:
        return ShipAction.WEST


def world_feature(board):
    size = board.configuration.size
    me = board.current_player

    ships = np.zeros((1, size, size))
    ship_cargo = np.zeros((1, size, size))
    bases = np.zeros((1, size, size))

    map_halite = np.array(board.observation["halite"]).reshape(1, size, size) / 1000

    for iid, ship in board.ships.items():
        ships[0, ship.position[1], ship.position[0]] = 1 if ship.player_id == me.id else -1
        ship_cargo[0, ship.position[1], ship.position[0]] = ship.halite / 1000

    for iid, yard in board.shipyards.items():
        bases[0, yard.position[1], yard.position[0]] = 1 if yard.player_id == me.id else -1

    return np.concatenate([map_halite, ships, ship_cargo, bases], axis=0)


def neighboring_ships(shipPosS: np.ndarray, board_array: np.ndarray, size: int) -> int:
    cargo = board_array[2]
    cargo_val = [cargo[ship[0] % size, ship[1] % size] for ship in shipPosS]
    max_val = [idx for idx, car in enumerate(cargo_val) if car == max(cargo_val)]
    if len(max_val) > 1:
        return random.choice(max_val)
    else:
        return max_val[0]


def find_closest_enemy(shipPos: tuple[int, int], board_array: np.ndarray) -> np.ndarray:
    my_ship = np.array([shipPos[1], shipPos[0]])

    # Create big board
    arrays = [board_array[1] for _ in range(3)]
    stack_col = np.concatenate(arrays, axis=0)
    stack_all = np.concatenate([stack_col for _ in range(3)], axis=1)

    enemy_ships = np.argwhere(stack_all == -1)
    distances = [LA.norm(my_ship - pos, ord=1) for pos in enemy_ships]
    min_index = [idx for idx, dis in enumerate(distances) if dis == min(distances)]
    return enemy_ships[min_index]


def return_to_shipyard(shipPos: tuple[int, int], shipyardPos: tuple[int, int], size: int):
    direction = getDirTo(shipPos, shipyardPos, size)
    if direction:
        shipPos.next_action = direction


def closest_shipyard(shipPos: tuple[int, int], board_array: np.ndarray) -> np.ndarray:
    my_ship = np.array([shipPos[1], shipPos[0]])

    # Create big board
    arrays = [board_array[3] for _ in range(3)]
    stack_col = np.concatenate(arrays, axis=0)
    stack_all = np.concatenate([stack_col for _ in range(3)], axis=1)

    yard = np.argwhere(stack_all == 1)
    distances = [LA.norm(my_ship - pos, ord=1) for pos in yard]
    min_index = [idx for idx, dis in enumerate(distances) if dis == min(distances)]
    if len(min_index) > 1:
        idx = random.choice(min_index)
    else:
        idx = min_index[0]
    return yard[idx]


def defend(
    shipPos: tuple[int, int],
    board: kaggle_environments.envs.halite.helpers.Board,
    board_array: np.ndarray,
):

    bigshipPos = (shipPos[0] + board.configuration.size, shipPos[1] + board.configuration.size)
    closest_yard = closest_shipyard(bigshipPos, board_array)
    closest_yardTuple = (closest_yard[1], closest_yard[0])
    direction = return_to_shipyard(bigshipPos, closest_yardTuple, board.configuration.size)
    # Attack enemy
    return direction


def attack(
    shipPos: tuple[int, int],
    board: kaggle_environments.envs.halite.helpers.Board,
    board_array: np.ndarray,
):
    bigshipPos = (shipPos[0] + board.configuration.size, shipPos[1] + board.configuration.size)
    enemyPos = find_closest_enemy(bigshipPos, board_array)
    if enemyPos.shape[0] > 1:
        idx = neighboring_ships(enemyPos, board_array, board.configuration.size)
    else:
        idx = 0
    enemyPosTuple = (enemyPos[idx][1], enemyPos[idx][0])
    # get the direction to the enemy
    direction = getDirTo(bigshipPos, enemyPosTuple, board.configuration.size)
    return direction


# Directions a ship can move
directions = [ShipAction.NORTH, ShipAction.EAST, ShipAction.SOUTH, ShipAction.WEST]

# Will keep track of whether a ship is collecting halite or carrying cargo to a shipyard
ship_states = {}

# Returns the commands we send to our ships and shipyards
def agent(obs, config):
    size = config.size
    board = Board(obs, config)
    me = board.current_player

    feature = world_feature(board)

    # If there are no ships, use first shipyard to spawn a ship.
    if len(me.ships) == 0 and len(me.shipyards) > 0:
        me.shipyards[0].next_action = ShipyardAction.SPAWN

    # If there are no shipyards, convert first ship into shipyard.
    if len(me.shipyards) == 0 and len(me.ships) > 0:
        me.ships[0].next_action = ShipAction.CONVERT

    for ship in me.ships:
        if ship.next_action == None:

            ### Part 1: Set the ship's state
            # if ship.halite < 100:
            ship_states[ship.id] = "ATTACK"
            # if ship.halite < 200:  # If cargo is too low, collect halite
            # ship_states[ship.id] = "COLLECT"
            # if ship.halite > 500:  # If cargo gets very big, deposit halite
            # ship_states[ship.id] = "DEPOSIT"

            ### Part 2: Use the ship's state to select an action
            if ship_states[ship.id] == "COLLECT":
                # If halite at current location running low,
                # move to the adjacent square containing the most halite
                if ship.cell.halite < 100:
                    neighbors = [
                        ship.cell.north.halite,
                        ship.cell.east.halite,
                        ship.cell.south.halite,
                        ship.cell.west.halite,
                    ]
                    best = max(range(len(neighbors)), key=neighbors.__getitem__)
                    ship.next_action = directions[best]
            if ship_states[ship.id] == "DEPOSIT":
                # Move towards shipyard to deposit cargo
                direction = getDirTo(ship.position, me.shipyards[0].position, size)
                if direction:
                    ship.next_action = direction
            if ship_states[ship.id] == "ATTACK":
                direction = attack(ship.position, board, feature)
                if direction:
                    ship.next_action = direction
            if ship_states[ship.id] == "DEFEND":
                direction = defend(ship.position, board, feature)
                if direction:
                    ship.next_action = direction

    return me.next_actions
