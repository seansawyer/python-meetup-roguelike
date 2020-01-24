from typing import List, NamedTuple
from shapely.geometry import MultiPoint, MultiPolygon, Polygon, box
from shapely import speedups


class Coordinates(NamedTuple):
    x: float
    y: float


def is_visible(player: Coordinates, tile: Coordinates, blocking_tiles: List[Coordinates]) -> bool:
    # take the convex hull of the player's eyes and the corners of the tile
    fov_polygon = MultiPoint([
        (player.x + 0.5, player.y + 0.5),
        (tile.x, tile.y),
        (tile.x + 1, tile.y),
        (tile.x + 1, tile.y + 1),
        (tile.x, tile.y + 1),
    ]).convex_hull
    # carve out all the blocking tiles
    for bt in blocking_tiles:
        blocking_box = box(bt.x, bt.y, bt.x + 1, bt.y + 1)
        fov_polygon = fov_polygon.difference(blocking_box)
        if isinstance(fov_polygon, MultiPolygon):
            return False
    return True



# where the player tile is
player_x, player_y = 5.0, 5.0
# where the players "eyes" are - this is where we will trace back to
eyes_x, eyes_y = player_x + 0.5, player_y + 0.5

# blocking tile
blocking_x, blocking_y = 6.0, 6.0
blocking_box = box(blocking_x, blocking_y, blocking_x+1, blocking_y+1)

print('TILE 1')
# tile we want to check for visibility - should be blocked
tile1_x, tile1_y = 7.0, 7.0
# take the convex hull of the player's eyes and the corners of the tile
tile1_fov_polygon = MultiPoint([
    (eyes_x, eyes_y),
    (tile1_x, tile1_y),
    (tile1_x+1, tile1_y),
    (tile1_x+1, tile1_y+1),
    (tile1_x, tile1_y+1),
]).convex_hull
print(tile1_fov_polygon)
# find all of the blocking boxes that intersect that convex hull polygon
print(blocking_box.intersects(tile1_fov_polygon))
# take the difference of the convex hull and the intersecting boxes
print(tile1_fov_polygon.difference(blocking_box))
# you know the tile is blocked as soon as you wind up with a multipolygon
print(type(tile1_fov_polygon.difference(blocking_box)))
# which is already the case here
print('is_visible?', is_visible(Coordinates(player_x, player_y), Coordinates(tile1_x, tile1_y), [Coordinates(blocking_x, blocking_y)]))

print('\nTILE 2')
# another tile to check for visibility - should be visible
tile2_x, tile2_y = 5.0, 6.0
# take the convex hull of the player's eyes and the corners of the tile
tile2_fov_polygon = MultiPoint([
    (eyes_x, eyes_y),
    (tile2_x, tile2_y),
    (tile2_x+1, tile2_y),
    (tile2_x+1, tile2_y+1),
    (tile2_x, tile2_y+1),
]).convex_hull
print(tile2_fov_polygon)
# find all of the blocking boxes that intersect that convex hull polygon
print(blocking_box.intersects(tile2_fov_polygon))
# take the difference of the convex hull and the intersecting boxes
print(tile2_fov_polygon.difference(blocking_box))
# you know the tile is blocked as soon as you wind up with a multipolygon
print(type(tile2_fov_polygon.difference(blocking_box)))
# but here that's not the case
print('is_visible?', is_visible(Coordinates(player_x, player_y), Coordinates(tile2_x, tile2_y), [Coordinates(blocking_x, blocking_y)]))

print('\nTILE 3')
# another tile to check for visibility - should be visible
tile3_x, tile3_y = 6.0, 7.0
# take the convex hull of the player's eyes and the corners of the tile
tile3_fov_polygon = MultiPoint([
    (eyes_x, eyes_y),
    (tile3_x, tile3_y),
    (tile3_x+1, tile3_y),
    (tile3_x+1, tile3_y+1),
    (tile3_x, tile3_y+1),
]).convex_hull
print(tile3_fov_polygon)
# find all of the blocking boxes that intersect that convex hull polygon
print(blocking_box.intersects(tile3_fov_polygon))
# take the difference of the convex hull and the intersecting boxes
print(tile3_fov_polygon.difference(blocking_box))
# you know the tile is blocked as soon as you wind up with a multipolygon
print(type(tile3_fov_polygon.difference(blocking_box)))
# but here that's not the case
print('is_visible?', is_visible(Coordinates(player_x, player_y), Coordinates(tile3_x, tile3_y), [Coordinates(blocking_x, blocking_y)]))
