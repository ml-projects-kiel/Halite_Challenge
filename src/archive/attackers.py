import random

import numpy as np
from kaggle_environments import make
from kaggle_environments.envs.halite.helpers import *
from numpy import linalg as LA


def getDirTo(fromPos: tuple[int, int], toPos: tuple[int, int], size):
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


def main():
    NUM_AGENTS = 4
    BOARD_SIZE = 7
    TURNS = 6

    env = make(
        "halite",
        configuration={"randomSeed": 1, "episodeSteps": TURNS, "size": BOARD_SIZE},
        debug=True,
    )
    _ = env.reset(num_agents=NUM_AGENTS)

    # As example take the first frame of the game
    sample_obs = env.state[0].observation
    board = Board(sample_obs, env.configuration)

    feature = world_feature(board)

    me = board.current_player
    attacker_id = [ship.id for ship in me.ships][0]
    shipPos = [ship.position for iid, ship in board.ships.items() if iid == attacker_id][0]
    attack(shipPos, board, feature)


if __name__ == "__main__":
    main()
