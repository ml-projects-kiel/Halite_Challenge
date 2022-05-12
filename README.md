# Halite-Challenge
# Team: noAdmin (meh)

## Agent: [Halite Bot: Aggressive Bot Starter Code](https://www.kaggle.com/code/alicia183/halite-bot-aggressive-bot-starter-code/notebook)

## Strategie 
- regelbasiertes Vorgehen
- erstmal keine Anwendung von ML
- Reduzierung der Anwendung auf einfache Teiloperationen

## Actions
Aktionen werden nach Status des Schiffes festgelegt 
- **ATTACK**: Wenn generisches Schiff 0 Halite besitzt und selber mehr als 500
- **COLLECT**: Wenn weniger als 500 Halite, dann weitersammeln
- **DEPOSIT**: Wenn mehr als 500 Halite, dann entladen

## Umfang

- Konstrukt aus if-else Anweisungen
- mögliche Szenarieren bewerten und handeln

## Requirements 
- erste schritte definieren
    - 1. baue Hafen (wo ist optimal?) -> wenn nicht spawn hafen
    - 2. baue Schiffe (wie viele?) -> 5 Schiffe?
    - 3. 

## Rules
- Wann `spawnen`?
    - Wann/wie viele Schiffe/Häfen?
- Wann `collect`? --> mining Algo? 
    - Distanz zu Hafen?
    - Distanz zu Resourcen?
    - Menge der Resourcen in Nachbarschaft?
    - 
- Wann `deposit`?
- Wann `attack`? --> (attack function: Idea, wenn unser Schiff weniger Cargo als Gegner Schiff hat)
-  Wann und Wo `build`? -->
- Conditions:
cargo voll - Gegner nah + viel Halite in Cargo
- fliehen() -> wenn unserer schiff mehr cargo hath?

## Current status

- use existing functions of **Halite Bot: Aggressive Bot Starter Code**
- optimize procedure 

## Execute functions
  ****### **Miners**
- find_best_ship_for_hub()
- locationhub()-> 

- starting_build_order()

  ### **Attackers**
- find_closest_enemy(ship.ID, board) => neighboring_ships(): -> enemy:ID
- get_dir_to_obj(enemy.ID) -> DIR

  ### **Miners**
- find_best_halite() -> halite.ID
- get_dir_to_obj(halite.ID) -> DIR
- collect()
- deposit() => Wenn Hub in der Nähe && Ladung > X
    - get_dir_to_obj(base.ID)

- find_best_hafen() -> scanne umkreis nach halite (3x3 umkreis) 
- collect() -> Gegner weit weg | nahe an der Base | 
- attack() -> Gegner in der Nähe |  Base zu weit entfernt | me.cargo < gegner.cargo
- buildhub () -> wenn keine Basis | wenn ship.cargo > 1000 && distance to base > threshold |


- starting_position()

### Condition functions 
- check_base_alive(base_id) # highest priority -> wenn Hafen kaputt ist, rufe find_best_hafen() auf - Wieviel cargo?
- attacker_or_miner()

- distance_to_base() 
- neighboring_ships() 

## Tasks

**Paul**
- [x] check_port(board): bool => Does port exist?
- [x] find_best_port_builder(ship.ID:list, board): take ship with most halite-cargo => return ship.ID
- [x] build_port(ship.ID, board, costs)

**Janosch**
- [x] attack()
- [x] find_closest_enemy(ship.ID, board) => neighboring_ships(): -> enemy:ID
- [x] get_dir_to_obj(enemy.ID) -> DIR

**Tom**
- [x] mine()
- [x] find_best_halite(ship.ID) -> halite.ID
- [x] get_dir_to_obj(halite.ID) -> DIR
- [x] collect()
- [x] deposit() => Wenn Hub in der Nähe && Ladung > X
    - [x] get_dir_to_obj(base.ID)

**Nils**
- [x] defend()
- [x] when_defend()

<table>
  <thead>
    <tr>
      <th>Tom</th>
      <th>Janosch</th>
      <th>Paul</th>
      <th>Nils</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>mining()</td>
      <td>attack()</td>
      <td>check_port()</td>
      <td>defence()</td>
    </tr>
    <tr>
      <td>-</td>
      <td>-</td>
      <td>find_best_port()</td>
      <td>-</td>
    </tr>
    <tr>
      <td>-</td>
      <td>-</td>
      <td>build_port()</td>
      <td>-</td>
    </tr>
  </tbody>
</table>