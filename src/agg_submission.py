
# Imports helper functions
from kaggle_environments.envs.halite.helpers import *

import math

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
            if ship.halite == 0 and me.halite>500:
                ship_states[ship.id] = "ATTACK"
            elif ship.halite <= 500: # Collect halite
                ship_states[ship.id] = "COLLECT"
            elif ship.halite > 500: # If cargo gets very big, deposit halite
                ship_states[ship.id] = "DEPOSIT"
                
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
