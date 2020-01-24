from dataclasses import dataclass
from enum import Enum

@dataclass
class Mob:
    sdesc: str
    x: int
    y: int
    speed: int


class Direction:
    N = 'north'
    NE = 'northeast'
    E = 'east'
    SE = 'southeast'
    S = 'south'
    SW = 'southwest'
    W = 'west'
    NW = 'northwest'


@dataclass
class Move:
    mob: Mob
    direction: Direction
    x: int
    y: int

    def handle(self):
        self.mob.x = self.x
        self.mob.y = self.y

# initial map
#
#  012
# 0..o
# 1w_.
# 2.gh


halfling = Mob(sdesc='halfling', x=2, y=2, speed=13)
gnome = Mob(sdesc='gnome', x=1, y=2, speed=10)
orc = Mob(sdesc='orc', x=2, y=0, speed=9)
wolf = Mob(sdesc='wolf', x=0, y=1, speed=14)

mobs = [gnome, orc, wolf]

moves = [
    Move(mob=orc, direction=Direction.SW, x=1, y=1),
    Move(mob=gnome, direction=Direction.N, x=1, y=1),
    Move(mob=wolf, direction=Direction.E, x=1, y=1),
    Move(mob=halfling, direction=Direction.W, x=1, y=2),
]


# halfling move to (2,1)
# gnome move to (1,1)
# orc move to (1,1)
# wolf move to (1,1)
# -> remove blocked moves ->
# gnome move to (1,1)
# orc move to (1,1)
# wolf move to (1,1)
# -> sort for speed ->
# wolf move from (0,1) to (1,1)
# orc move from (2,0) to (1,1)
# gnome move from (1,2) to (1,1)
# -> choose tile winners based on order ->
# wolf move from (0,1) to (1,1)
# wolf blocks orc
# wolf blocks gnome

# The logic below doesn't handle cases where the destination tile is
# blocked by another mob that isn't moving (i.e., an attack)
# or an inanimate object (e.g., a wall).
# To handle that we would need to translate moves into attacks
# when the destination tile is occupied to begin with.
# Might want to add a wimpy mode where no move will ever be translated
# to an attack. If the tile is occupied the move will become a no-op.

# From the moves above we could run the translation logic above
# to determine attack moves/blocked moves/actual moves, then sort
# by speed below.

messages = []

valid_moves = []
for m in moves:
    valid = True
    for mob in mobs:
        if mob == m.mob:
            continue
        if mob.x == m.x and mob.y == m.y:
            valid = False
            messages.append(f'{mob.sdesc} blocks {m.mob.sdesc}')
            break
    if valid:
        valid_moves.append(m)

proposed_moves = sorted(valid_moves, reverse=True, key=lambda c: c.mob.speed)

accepted_moves = []
for pm in proposed_moves:
    # Accept any moves that are not blocked
    accept = True
    for am in accepted_moves:
        if pm.x == am.x and pm.y == am.x:
            accept = False
            messages.append(f'{am.mob.sdesc} blocks {pm.mob.sdesc}')
            break
    if accept:
        accepted_moves.append(pm)

print('=== MOBS BEFORE ===')
for mob in mobs:
    print(mob)

print('=== MOVES ===')
for m in moves:
    print(m)

print('=== VALID MOVES ===')
for vm in valid_moves:
    print(vm)

print('=== ACCEPTED MOVES ===')
for am in accepted_moves:
    print(am)
    am.handle()

print('=== MESSAGES ===')
for msg in messages:
    print(msg)

print('=== MOBS AFTER ===')
for mob in mobs:
    print(mob)
