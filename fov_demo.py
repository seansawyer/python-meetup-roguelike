import random
import time
from typing import Any, Dict, Optional, List, NamedTuple

import numpy
import tcod as libtcod
from shapely.geometry import MultiPoint, MultiPolygon, box
from shapely.ops import unary_union


screen_width = 80
screen_height = 50
map_width = screen_width
map_height = screen_height - 2


class Coordinates(NamedTuple):
    x: int
    y: int


def generate_map() -> List[List[str]]:
    # start with all walls
    map_tiles = [['#'] * map_width for y in range(map_height)]
    # choose a random starting point
    x = random.randint(1, map_width - 2)
    y = random.randint(1, map_height - 2)
    # walk in a random direction
    possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    map_tiles[y][x] = '.'
    for i in range(10000):
        choice = random.randint(0, len(possible_moves) - 1)
        dx, dy = possible_moves[choice]
        if 0 < x + dx < map_width - 2 and 0 < y + dy < map_height - 2:
            x = x + dx
            y = y + dy
        if map_tiles[y][x] == '#':
            map_tiles[y][x] = '.'
            draw_map(map_tiles, Coordinates(x, y))
            libtcod.console_flush()
    return map_tiles


def measure_distance(a: Coordinates, b: Coordinates) -> float:
    a_arr = numpy.array(a)
    b_arr = numpy.array(b)
    return numpy.sqrt(numpy.sum((a_arr - b_arr) ** 2))


def is_visible(
    player_coords: Coordinates,
    tile_coords: Coordinates,
    blocking_shape: Optional[Any]
) -> bool:
    if blocking_shape is None:
        return True
    # the player's "eyes" are at the midpoint of its tile
    eyes_x = player_coords.x + 0.5
    eyes_y = player_coords.y + 0.5
    # take the convex hull of the player's eyes and the tile's corners,
    # which gives you the full potential field of view for the tile
    fov_polygon = MultiPoint([
        (eyes_x, eyes_y),
        (tile_coords.x, tile_coords.y),
        (tile_coords.x + 1, tile_coords.y),
        (tile_coords.x + 1, tile_coords.y + 1),
        (tile_coords.x, tile_coords.y + 1),
    ]).convex_hull
    # if no blocking tiles intesect the FOV polygon, we can see the tile
    if not blocking_shape.intersects(fov_polygon):
        return True
    fov_polygon = fov_polygon.difference(blocking_shape)
    # if our FOV polygon was split into multiple polygons,
    # then our field of view for this tile is blocked
    return not isinstance(fov_polygon, MultiPolygon)


def draw_fov(
    map_tiles: List[List[str]],
    player_coords: Coordinates,
    sight_distance: int
):
    # for blocking tiles, record coordinates and polygons as we find them
    blocking_shape = None
    # a little something to prevent a jagged single tile at the edges of the field of view
    # examine the field of view one square at a time, up to our sight distance
    for i in range(sight_distance + 1):
        sight_smoothing_factor = i * 0.045
        if i == 0:
            x, y = player_coords
            libtcod.console_put_char(0, player_coords.x, player_coords.y, '@', libtcod.BKGND_NONE)
            continue
        # all of the tiles at this "radius" will be collected here
        tiles_coords = []
        for delta in range(-i, i+1):
            # generate top tiles by moving right
            top = Coordinates(player_coords.x + delta, player_coords.y - i)
            # since we are checking the corresponding tiles for each side with each iteration,
            # starting from the outer corners,  we can bail on this iteration entirely as soon
            # as we know the "top" one is outside our sight distance
            distance = measure_distance(top, player_coords)
            if distance > sight_distance + sight_smoothing_factor:
                continue
            # all of the tiles at this delta will be collected here
            #tiles_coords = []
            # otherwise, we generate and draw all four tiles at this delta
            if 0 <= top.y < map_height and 0 <= top.x < map_width:
                tiles_coords.append(top)
            # generate right tiles by moving down
            right = Coordinates(player_coords.x + i, player_coords.y + delta)
            if 0 <= right.y < map_height and 0 <= right.x < map_width:
                tiles_coords.append(right)
            # generate bottom tiles by moving left
            bottom = Coordinates(player_coords.x - delta, player_coords.y + i)
            if 0 <= bottom.y < map_height and 0 <= bottom.x < map_width:
                tiles_coords.append(bottom)
            # generate left tiles by moving up
            left = Coordinates(player_coords.x - i, player_coords.y - delta)
            if 0 <= left.y < map_height and 0 <= left.x < map_width:
                tiles_coords.append(left)
        # polygons for new blocking tiles will be collected here
        new_blocking_geoms = []
        for tc in tiles_coords:
            # draw the tile at `tc` if visible
            if is_visible(player_coords, tc, blocking_shape):
                libtcod.console_put_char(0, tc.x, tc.y, map_tiles[tc.y][tc.x], libtcod.BKGND_NONE)
            # collect a blocking polygon if this is a blocking tile
            if map_tiles[tc.y][tc.x] == '#':
                bb = box(tc.x, tc.y, tc.x + 1, tc.y + 1)
                new_blocking_geoms.append(bb)
        # combine the new blocking polygons with the existing blocking geom
        if new_blocking_geoms:
            if blocking_shape is None:
                blocking_shape = unary_union(new_blocking_geoms)
            else:
                blocking_shape = unary_union([blocking_shape] + new_blocking_geoms)


def draw_map(
    map_tiles: List[List[str]],
    current_coords: Coordinates
) -> None:
    y = 0
    for row in map_tiles:
        x = 0
        for tile in row:
            if Coordinates(x, y) == current_coords:
                tile = '*'
            libtcod.console_put_char(0, x, y, tile, libtcod.BKGND_NONE)
            x += 1
        y += 1


def traverse_sight_range(player_coords: Coordinates, distance: int):
    print('player coords', player_coords)
    for i in range(distance + 1):
        print(f'==== {i} ====')
        if i == 0:
            tiles = [player_coords]
            print(tiles)
        else:
            tiles = set()
            for delta in range(-i, i):
                # generate top tiles by moving right
                top_tile = player_coords.x + delta, player_coords.y - i
                tiles.add(top_tile)
                # generate right tiles by moving down
                right_tile = player_coords.x + i, player_coords.y + delta
                tiles.add(right_tile)
                # generate bottom tiles by moving left
                bottom_tile = player_coords.x - delta, player_coords.y + i
                tiles.add(bottom_tile)
                # generate left tiles by moving up
                left_tile = player_coords.x - i, player_coords.y - delta
                tiles.add(left_tile)
            print(tiles)


def choose_random_open_tile(
    map_tiles: List[List[str]]
) -> Coordinates:
    coords = None
    tile = '#'
    while tile != '.':
        x = random.randint(1, map_width - 2)
        y = random.randint(1, map_height - 2)
        tile = map_tiles[y][x]
        coords = Coordinates(x, y)
    return coords


def main() -> None:
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(screen_width, screen_height, 'pmrl', False)
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.console_flush()
    map_tiles = generate_map()
    libtcod.console_clear(0)
    player_coords = choose_random_open_tile(map_tiles)
    time.sleep(3)
    for sight_distance in range(0, 25):
        draw_fov(map_tiles, player_coords, sight_distance)
        libtcod.console_flush()
        time.sleep(0.5)
    time.sleep(10)


if __name__ == '__main__':
    main()
