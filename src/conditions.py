# Basischeck
def check_shipyard (board):
    me = board.current_player
    return bool (len(me.shipyards) == 0)

# Besten Port Builder finden
def best_port_builder (board):
    me = board.current_player
    for ship in me.ships:
        global port_builder
        port_builder = ship.ID (max (me.ships))
    return port_builder
        
# Port bauen
def build_port():
    if check_port(board):
        port_builder.next_action = ShipAction.CONVERT

# Zur Basis zurückkehren    
def return_to_shipyard():
    me = board.current_player
    for ship in me.ships:
        if ship_states[ship.id] == "DEPOSIT":
            direction = getDirTo(ship.position, me.shipyards[0].position, size)
            if direction:
                ship.next_action = direction
