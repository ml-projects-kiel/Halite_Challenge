
# Imports helper functions
from turtle import pos
from kaggle_environments.envs.halite.helpers import *
import numpy as np
import math
from numpy import linalg as LA
import random


# Returns best direction to move from one position (fromPos) to another (toPos)
def getDirTo(fromPos, toPos, size):
    fromX, fromY = divmod(fromPos[0],size), divmod(fromPos[1],size)
    toX, toY = divmod(toPos[0],size), divmod(toPos[1],size)
    if fromY < toY: return ShipAction.NORTH
    if fromY > toY: return ShipAction.SOUTH
    if fromX < toX: return ShipAction.EAST
    if fromX > toX: return ShipAction.WEST


# Find objects of other players
def objectsOfOthers(board):
    # list of (x, y) coords
    other_ships = []
    other_shipyards = []
    
    for player in board.opponents:
        for ship in player.ships:
            pos = ship.position
            halite_ship = ship.halite
            other_ships.append((pos, halite_ship))
        for shipyard in player.shipyards:
            pos = shipyard.position
            num_ships = len(player.ships)
            other_shipyards.append((pos, num_ships))
                
    return other_ships, other_shipyards

# Find nearest objects to ships
def nearestObject(fromPos, positions, size):
    fromX, fromY = fromPos
    distance = []
    for obj, halite in positions:
        toX, toY = obj
        distance.append(math.sqrt((toX-fromX)**2 + (toY-fromY)**2))
    nearest = min(distance)
    index = distance.index(nearest)
    return positions[index]

# Code to attack closest ship
def attackShip(ship, other_ships, size):
    attack = nearestObject(ship.position, other_ships, size)
    pos, halite = attack
    if halite > 0:
        return getDirTo(ship.position, pos, size)

def newPosition (old_position, next_step):
    x, y = old_position
    if next_step == ShipAction.NORTH: return (x, y+1)
    if next_step == ShipAction.SOUTH: return (x, y-1)
    if next_step == ShipAction.EAST: return (x+1, y)
    if next_step == ShipAction.WEST: return (x-1, y)
    if next_step == None: return (x, y)
    
def manhattan_distance_single(i1, i2):
            """Gets the distance in one dimension between two columns or two rows, including wraparound."""
            iMin = min(i1, i2)
            iMax = max(i1, i2)
            return min(iMax - iMin, iMin + size - iMax)

def manhattan_distance(pos1, pos2):
            """Gets the Manhattan distance between two positions, i.e.,
            how many moves it would take a ship to move between them."""
            dx = manhattan_distance_single(pos1 % size, pos2 % size)
            dy = manhattan_distance_single(pos1 // size, pos2 // size)
            return dx + dy

"""
1. Wie nah darf Gegner kommen?
2. Wenn Gegener zu Nahe an Hub kommt, dann Role zu Defender übergeben
2. Positiion Schiff am nächsten zum Hub

"""
def return_to_shipyard(shipPos: tuple[int, int], shipyardPos: tuple[int, int], size:int):
    direction = getDirTo(shipPos, shipyardPos, size)
    if direction: shipPos.next_action = direction 


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
    board_array: np.ndarray):
    
    bigshipPos = (shipPos[0] + board.configuration.size, shipPos[1] + board.configuration.size)
    closest_yard = closest_shipyard(bigshipPos, board_array)
    closest_yardTuple = (closest_yard[1], closest_yard[0])
    direction = return_to_shipyard(bigshipPos, closest_yardTuple, board.configuration.size)
    

    # Attack enemy
    return direction

def ownpos(board):
    me = board.current_player
    for ship in me.ships: 
        return ship.position

def next_enemy(board):
    other_ships, other_shipyards = objectsOfOthers(board)
    distance = []
    
    distances = [LA.norm(my_ship - pos, ord=1) for pos in other_ships]
    min_index = [idx for idx, dis in enumerate(distances) if dis == min(distances)]

    for position in other_ships:
        distance.append(manhattan_distance(ownpos, position))
        nearest = min(distance)
        index = distance.index(nearest)
        return other_ships[index]

def world_feature(board):
    size = board.configuration.size
    me = board.current_player
    
    ships = np.zeros((1, size, size))
    ship_cargo = np.zeros((1, size, size))
    bases = np.zeros((1, size, size))

    map_halite = np.array(board.observation['halite']).reshape(1, size, size)/1000

    for iid, ship in board.ships.items():
        ships[0, ship.position[1], ship.position[0]] = 1 if ship.player_id == me.id else -1
        ship_cargo[0, ship.position[1], ship.position[0]] = ship.halite/1000

    for iid, yard in board.shipyards.items():
        bases[0, yard.position[1], yard.position[0]] = 1 if yard.player_id == me.id else -1
        
    return np.concatenate([
        map_halite, 
        ships, 
        ship_cargo, 
        bases
    ], axis=0)

# Code to attack shipyard: write if's in agent
#def attackShipyard(ship, other_shipyards, size):
#    attack = nearestObject(ship.position, other_shipyards, size)
#    pos, halite = attack
#    return getDirTo(ship.position, pos, size)
    

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
        
        
    other_ships, other_shipyards = objectsOfOthers(board)
    ship_positions = []
        
    # Actions for each ships
    for ship in me.ships:
        if ship.next_action == None:
            
            ### Part 1: Set the ship's state 
            # if ship.halite == 0 and me.halite>500:
            #     ship_states[ship.id] = "ATTACK"
            # elif ship.halite <= 500: # Collect halite
            #     ship_states[ship.id] = "COLLECT"
            # elif ship.halite > 500: # If cargo gets very big, deposit halite
            #     ship_states[ship.id] = "DEPOSIT"    
            # if enemycargo>me.halite:
            ship_states[ship.id] = "DEFEND"
                
            ### Part 2: Use the ship's state to select an action
            if ship_states[ship.id] == "ATTACK":
                direction = attackShip(ship, other_ships, size)
                if direction: ship.next_action = direction
            if ship_states[ship.id] == "COLLECT":
                # If halite at current location running low, 
                # move to the adjacent square containing the most halite
                if ship.cell.halite < 100:
                    neighbors = [ship.cell.north.halite, ship.cell.east.halite, 
                                 ship.cell.south.halite, ship.cell.west.halite]
                    best = max(range(len(neighbors)), key=neighbors.__getitem__)
                    ship.next_action = directions[best]
            if ship_states[ship.id] == "DEPOSIT":
                # Move towards shipyard to deposit cargo
                direction = getDirTo(ship.position, me.shipyards[0].position, size)
                if direction: ship.next_action = direction
            
            if ship_states[ship.id] == "DEFEND":
                    direction = defend(ship.position, board, feature)
                    if direction: ship.next_action = direction
                      
            new_position = newPosition(ship.position, ship.next_action)
            for other_position in ship_positions:
                if new_position == other_position:
                    ship.next_action = None
                    new_position = ship.position
            ship_positions.append(new_position)
            
    
    for shipyards in me.shipyards:
        spawnShip = True
        for position in ship_positions:
            if position == shipyards.position:
                spawnShip = False
        if shipyards.next_action == None and spawnShip == True:
            if me.halite > 500 and len(me.ships) <= 10 and board.step > 5:
                shipyards.next_action = ShipyardAction.SPAWN
                
                
    return me.next_actions
