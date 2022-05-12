import math
import random

import numpy as np
from kaggle_environments import make
from kaggle_environments.envs.halite.helpers import *
from numpy import linalg as LA

#################
# Basic functions
#################

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


def newPosition(old_position, next_step):
    x, y = old_position
    if next_step == ShipAction.NORTH:
        return (x, y + 1)
    if next_step == ShipAction.SOUTH:
        return (x, y - 1)
    if next_step == ShipAction.EAST:
        return (x + 1, y)
    if next_step == ShipAction.WEST:
        return (x - 1, y)
    if next_step == None:
        return (x, y)


# better way to get information about the ships, halite, hubs and enemies
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


def create_big_board(sub_board_array: np.ndarray) -> np.ndarray:
    arrays = [sub_board_array for _ in range(3)]
    stack_col = np.concatenate(arrays, axis=0)
    return np.concatenate([stack_col for _ in range(3)], axis=1)
    #     x x x
    #     x O x
    #     x x x


####################
# Shipyard functions
####################


def find_closest_shipyard(shipPos: tuple[int, int], board_array: np.ndarray) -> np.ndarray:
    my_ship = np.array([shipPos[1], shipPos[0]])

    # Create big board
    stack_all = create_big_board(board_array[3])

    yard = np.argwhere(stack_all == 1)
    distances = [LA.norm(my_ship - pos, ord=1) for pos in yard]
    min_index = [idx for idx, dis in enumerate(distances) if dis == min(distances)]
    if len(min_index) == 0:
        return None
    elif len(min_index) == 1:
        idx = min_index[0]
    elif len(min_index) > 1:
        idx = random.choice(min_index)
    return yard[idx]


# Besten Port Builder finden
def best_port_builder(board):
    me = board.current_player
    ships, halite = list(), list()
    for ship in me.ships:
        ships.append(ship.id)
        halite.append(ship.halite)
    max_val = [idx for idx, hal in enumerate(halite) if hal == max(halite)]
    if len(max_val) > 1:
        idx = random.choice(max_val)
    else:
        idx = max_val[0]
    return ships[idx]


# Basischeck
def shipyard_alive(board: kaggle_environments.envs.halite.helpers.Board) -> bool:
    me = board.current_player
    return len(me.shipyards) != 0


def move_to_closest_shipyard(
    shipPos: tuple[int, int],
    board: kaggle_environments.envs.halite.helpers.Board,
    board_array: np.ndarray,
):

    bigshipPos = (shipPos[0] + board.configuration.size, shipPos[1] + board.configuration.size)
    closest_yard = find_closest_shipyard(bigshipPos, board_array)
    if closest_yard is None:
        return None
    closest_yardTuple = (closest_yard[1], closest_yard[0])
    direction = getDirTo(bigshipPos, closest_yardTuple, board.configuration.size)
    # Attack enemy
    return direction


###################
# Minning functions
###################


def get_halite_pos(halite_map: np.ndarray) -> list[tuple[int, int, int]]:
    list_of_pos = []
    for i in range(halite_map.shape[0]):
        for j in range(halite_map.shape[1]):
            element = halite_map[i][j]
            if element > 0:
                list_of_pos.append((i, j, element))
    return list_of_pos


def manhattanDist(X1, Y1, X2, Y2):
    dist = math.fabs(X2 - X1) + math.fabs(Y2 - Y1)
    return (int)(dist)


def find_halite(
    shipPos: tuple[int, int], halite_map: list[tuple[int, int, int]]
) -> list[tuple[int, int, int, int]]:
    halite_score = []
    for _, halite_coords in enumerate(halite_map):
        score = halite_coords[2]
        distance = manhattanDist(
            X1=shipPos[0], Y1=shipPos[1], X2=halite_coords[0], Y2=halite_coords[1]
        )
        halite_score.append((distance, score, halite_coords[0], halite_coords[1]))
    return halite_score


def calc_best_pos_halite(halite: list[tuple[int, int, int, int]]) -> tuple[int, int]:
    result_list = list()
    for _, halite_coords in enumerate(halite):
        distance = halite_coords[0]
        value = halite_coords[1]
        result = distance * value
        result_list.append((result, halite_coords[2], halite_coords[3]))
    min_value = optimize(result_list)
    for _, halite_coords in enumerate(halite):
        if halite_coords[0] == min_value:
            return halite_coords[2], halite_coords[3]


def optimize(value_list) -> int:
    tmp_list = []
    for elements in range(len(value_list)):
        tmp_list.append(value_list[elements][0])
    return min(tmp_list)


def mining(
    shipPos: tuple[int, int],
    board: kaggle_environments.envs.halite.helpers.Board,
    board_array: np.ndarray,
):
    """find coordination of best halite storage"""
    size = board.configuration.size
    pos_halite = get_halite_pos(board_array[0])
    list_of_halite_pos_and_distance = find_halite(shipPos, pos_halite)
    best_halite_pos = calc_best_pos_halite(list_of_halite_pos_and_distance)
    direction = getDirTo(shipPos, best_halite_pos, size)
    return direction


##################
# Attack functions
##################

def find_closest_enemy(shipPos: tuple[int, int], board_array: np.ndarray) -> np.ndarray:
    my_ship = np.array([shipPos[1], shipPos[0]])

    # Create big board
    stack_all = create_big_board(board_array[1])

    enemy_ships = np.argwhere(stack_all == -1)
    distances = [LA.norm(my_ship - pos, ord=1) for pos in enemy_ships]
    min_index = [idx for idx, dis in enumerate(distances) if dis == min(distances)]
    return enemy_ships[min_index]

def find_closest_ship(shipPos: tuple[int, int], board_array: np.ndarray) -> np.ndarray:
    my_ship = np.array([shipPos[1], shipPos[0]])

    # Create big board
    stack_all = create_big_board(board_array[1])

    ship = np.argwhere(stack_all == -1)
    distances = [LA.norm(my_ship - pos, ord=1) for pos in ship]
    min_index = [idx for idx, dis in enumerate(distances) if dis == min(distances)]
    return ship[min_index]

def enemy_yard_distance(yard_pos: tuple[int, int], board_array: np.ndarray):
    yard = np.array([yard_pos[1], yard_pos[0]])
    # Create big board
    stack_all = create_big_board(board_array[1])
    enemy_ships = np.argwhere(stack_all == -1)
    distances = [LA.norm(yard - pos, ord=1) for pos in enemy_ships]
    return min(distances)

def ship_yard_distance(yard_pos: tuple[int, int], board_array: np.ndarray):
    yard = np.array([yard_pos[1], yard_pos[0]])
    # Create big board
    stack_all = create_big_board(board_array[1])
    ships = np.argwhere(stack_all == 1)
    distances = [LA.norm(yard - pos, ord=1) for pos in ships]
    return min(distances)


def neighboring_ships(shipPosS: np.ndarray, board_array: np.ndarray, size: int) -> int:
    cargo = board_array[2]
    cargo_val = [cargo[ship[0] % size, ship[1] % size] for ship in shipPosS]
    max_val = [idx for idx, car in enumerate(cargo_val) if car == max(cargo_val)]
    if len(max_val) > 1:
        return random.choice(max_val)
    else:
        return max_val[0]


def attack(
    shipPos: tuple[int, int],
    board: kaggle_environments.envs.halite.helpers.Board,
    board_array: np.ndarray,
):
    bigshipPos = (shipPos[0] + board.configuration.size, shipPos[1] + board.configuration.size)
    enemyPos = find_closest_enemy(bigshipPos, board_array)
    if enemyPos.shape[0] == 0:
        return None
    elif enemyPos.shape[0] == 1:
        idx = 0
    elif enemyPos.shape[0] > 1:
        idx = neighboring_ships(enemyPos, board_array, board.configuration.size)
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
    board = Board(obs, config)
    me = board.current_player

    feature = world_feature(board)

    # If there are no ships, use first shipyard to spawn a ship.
    if len(me.ships) == 0 and len(me.shipyards) > 0:
        me.shipyards[0].next_action = ShipyardAction.SPAWN

    # If there are no shipyards, convert first ship into shipyard.
    if not shipyard_alive(board):
        builder_id = best_port_builder(board)
        for ship in me.ships:
            if ship.id == builder_id:
                ship.next_action = ShipAction.CONVERT

    ship_positions = []

    ### Part 1: Set the ship's state
    for ship in me.ships:
        if ship.next_action == None:
            #######################
            # Logic
            #######################
            shipPos = ship.position
            bigshipPos = (shipPos[0] + board.configuration.size, shipPos[1] + board.configuration.size)

            if sum(value == "MINE" for value in ship_states.values())<=5 and ship.halite < 200: #If less than 5 miners and cargo of ship is too low, collect halite
                
                ship_states[ship.id] = "MINE"

            if ship.halite >= 250:
                ship_states[ship.id] = "DEPOSIT" # If cargo gets very big, deposit halite
                
            if sum(value == "MINE" for value in ship_states.values())>5 and ship.halite < 100 and sum(value == "ATTACK" for value in ship_states.values())<5:
                ship_states[ship.id] = "ATTACK"
                            
            if enemy_yard_distance(bigshipPos, feature)-1==ship_yard_distance(bigshipPos, feature):
                    shipPos = find_closest_ship(bigshipPos, feature)
                    if shipPos.shape[0] == 0:
                        return None
                    elif shipPos.shape[0] == 1:
                        idx = 0
                    elif shipPos.shape[0] > 1:
                        idx = neighboring_ships(shipPos, feature, board.configuration.size)
                    shipPosTuple = (shipPos[idx][1], shipPos[idx][0])
                    if ship_states[ship.position] == shipPosTuple:
                        ship_states[ship.id] = "DEFEND"
            
            ### Part 2: Use the ship's state to select an action
            if ship_states[ship.id] == "MINE":
                direction = mining(ship.position, board, feature)
                if direction:
                    ship.next_action = direction
            elif ship_states[ship.id] == "DEPOSIT":
                # Move towards shipyard to deposit cargo
                direction = move_to_closest_shipyard(ship.position, board, feature)
                if direction:
                    ship.next_action = direction
            elif ship_states[ship.id] == "ATTACK":
                direction = attack(ship.position, board, feature)
                if direction:
                    ship.next_action = direction
            elif ship_states[ship.id] == "DEFEND":
                direction = move_to_closest_shipyard(ship.position, board, feature)
                if direction:
                    ship.next_action = direction

            new_position = newPosition(ship.position, ship.next_action)
            for other_position in ship_positions:
                if new_position == other_position:
                    ship.next_action = None
                    new_position = ship.position
            ship_positions.append(new_position)

    ##############
    # Build Ships
    ##############
    for shipyards in me.shipyards:
        spawnShip = True
        for position in ship_positions:
            if position == shipyards.position:
                spawnShip = False
        if shipyards.next_action == None and spawnShip == True:
            if me.halite > 500 and len(me.ships) <= 10 and board.step > 5:
                shipyards.next_action = ShipyardAction.SPAWN

    return me.next_actions
