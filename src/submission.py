# Imports helper functions
import random
import math
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

def newPosition (old_position, next_step):
    x, y = old_position
    if next_step == ShipAction.NORTH: return (x, y+1)
    if next_step == ShipAction.SOUTH: return (x, y-1)
    if next_step == ShipAction.EAST: return (x+1, y)
    if next_step == ShipAction.WEST: return (x-1, y)
    if next_step == None: return (x, y)

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

def return_to_shipyard(shipPos: tuple[int, int], shipyardPos: tuple[int, int], size: int):
    direction = getDirTo(shipPos, shipyardPos, size)
    if direction:
        shipPos.next_action = direction

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
def shipyard_alive(board:kaggle_environments.envs.halite.helpers.Board) -> bool:
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
    direction = return_to_shipyard(bigshipPos, closest_yardTuple, board.configuration.size)
    # Attack enemy
    return direction

###################
# Minning functions
###################

sample_obs = env.state[0].observation
board = Board(sample_obs, env.configuration)
features = world_feature(board)
cargo = features[2]
cargo[0][1]

def get_halite_pos(halite_map):
    list_of_pos = []
    for i in range(halite_map.shape[0]):
        for j in range(halite_map.shape[1]):
            element = halite_map[i][j]
            if element > 0:
                pos_tuple = (i,j, element)
                list_of_pos.append(pos_tuple)
    return list_of_pos


halie = get_halite_pos(features[0])
type(halie)

def manhattanDist(X1, Y1, X2, Y2):
    dist = math.fabs(X2 - X1) + math.fabs(Y2 - Y1)
    return (int)(dist)

def find_halite(ship, halite_map):
    distance = []
    score = []
    halite_score = []
    me = board.current_player
    for index, tuple in enumerate(halite_map):
        score = tuple[2]
        distance = manhattanDist(X1=ship.position[0],Y1=ship.position[1],X2= tuple[0], Y2= tuple[1])
        result_tuple = (distance,score, tuple[0],tuple[1])
        halite_score.append(result_tuple)
    return halite_score

result_list = []

def calc_best_pos_halite(halite):
    for index, tuple in enumerate(halite[0]):
        distance = tuple[0]
        value = tuple[1]
        result = distance * value
        new_result = result,tuple[2], tuple[3]
        result_list.append(new_result)
    min_value = optimize(result_list)
    print(min_value)
    for index, tuple in enumerate(halite[0]):
        if tuple[0] == min_value:
            pos = tuple[2], tuple[3]
    return pos

def optimize(value_list):
    tmp_list = []
    for elements in range(len(value_list)):
        tmp_list.append(result_list[elements][0])
    min_value = min(tmp_list)
    return min_value

def mining(halite_map):
    """find coordination of best halite storage"""
    size = config.size
    me = board.current_player
    ship_states = {}
    for ship in me.ships:
        pos_halite = get_halite_pos(halite_map)
        list_of_halite_pos_and_distance = find_halite(ship,pos_halite)
        best_halite = calc_best_pos_halite(list_of_halite_pos_and_distance)
        direction = getDirTo(ship.position, best_halite, size)
        if direction:
            ship.next_action = direction

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
    size = config.size
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
            # if ship.halite < 100:
            ship_states[ship.id] = "ATTACK"
            # if ship.halite < 200:  # If cargo is too low, collect halite
            # ship_states[ship.id] = "COLLECT"
            # if ship.halite > 500:  # If cargo gets very big, deposit halite
            # ship_states[ship.id] = "DEPOSIT"

        ### Part 2: Use the ship's state to select an action
            if ship_states[ship.id] == "COLLECT":
                direction = mining()
                if direction:
                    ship.next_action = direction
            if ship_states[ship.id] == "DEPOSIT":
                # Move towards shipyard to deposit cargo
                direction = move_to_closest_shipyard(ship.position, board, feature)
                if direction:
                    ship.next_action = direction
            if ship_states[ship.id] == "ATTACK":
                direction = attack(ship.position, board, feature)
                if direction:
                    ship.next_action = direction
            if ship_states[ship.id] == "DEFEND":
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
