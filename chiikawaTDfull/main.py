import pygame as pg
import json
from enemy import Enemy
from world import World
from turret import Turret
from button import Button
import constants as c

#init pygame
pg.init()

#clock
clock = pg.time.Clock()

#display
screen = pg.display.set_mode((c.SCREEN_WIDTH + c.SIDE_PANEL, c.SCREEN_HEIGHT))
pg.display.set_caption("Chiikawa's Tower Defense")

#game variables
last_spawn_time = pg.time.get_ticks()
placing_turrets = False
selected_turret = None
level_started = False
level_just_finished = False

#map
map_image = pg.image.load('levels/level.png').convert_alpha()

#turret upgrade list
turret_spritesheets = []
for x in range (1, c.TURRET_LEVELS + 1):
    turret_sheet = pg.image.load(f'assets/images/turrets/turret_{x}.png').convert_alpha()
    turret_spritesheets.append(turret_sheet)

#enemy type images
enemy_images = {
    "norm": pg.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
    "blue": pg.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
    "angry": pg.image.load('assets/images/enemies/enemy_3.png').convert_alpha()
}

#side buttons!
buy_turret_image = pg.image.load('assets/images/buttons/buy_turret.png').convert_alpha()
cancel_image = pg.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_image = pg.image.load('assets/images/buttons/upgrade.png').convert_alpha()
start_image = pg.image.load('assets/images/buttons/start.png').convert_alpha()

#load json data for level waypoints
with open('levels/level.tmj') as file:
    world_data = json.load(file)

#make text for health and money
text_font = pg.font.SysFont("Arial", 24, bold = True)
large_font = pg.font.SysFont("Arial", 36)

#display text for health and money
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def create_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    if mouse_tile_x < 0 or mouse_tile_y < 0:
        return
    mouse_tile_num = mouse_tile_y * c.COLS + mouse_tile_x

    # ensure tile index is within the map bounds before indexing
    if mouse_tile_num < 0 or mouse_tile_num >= len(world.tile_map):
        return

    #check if tile is grass or dirt before placing turret
    if world.tile_map[mouse_tile_num] == 188:
        #check if the space is empty (no turret already there)
        space_is_empty = True
        for turret in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
                space_is_empty = False
        #if space is empty + grass, place turret and deduct money
        if space_is_empty == True:
            new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y)
            turret_group.add(new_turret)
            #minus money for turret placement
            world.money -= c.BUY_COST


def select_turret(mouse_pos):
    mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
    mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
    for turret in turret_group:
        if (turret.tile_x, turret.tile_y) == (mouse_tile_x, mouse_tile_y):
            return turret
        
def clear_selected_turret():
    for turret in turret_group:
        turret.selected = False

#individual turret image for mouse cursor
cursor_turret = pg.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
turret_group = pg.sprite.Group()

#generate level map and waypoints
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

#create enemy group
enemy_group = pg.sprite.Group()

#create buttons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 30, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_image, True)
start_button = Button(c.SCREEN_WIDTH + 60, 300, start_image, True)

#game loop
run = True
while run:

    clock.tick(c.FPS)  # Limit to 60 frames per second

    ########### UPDATE INFORMATION

    #update groups
    enemy_group.update(world)
    turret_group.update(enemy_group)
    
    #highlight selected turret and show range when selected!
    if selected_turret:
        selected_turret.selected = True

    ########### DRAWING INFORMATION

    screen.fill(("grey100"))  # Clear screen each frame with white background

    #draw the game map
    world.draw(screen)

    #draw different groups of enemies and turrets
    enemy_group.draw(screen)
    for turret in turret_group:
        turret.draw(screen)

    draw_text("health: " + str(world.health), text_font, "red", 0, 0)
    draw_text("money: " + str(world.money), text_font, "red", 0, 30)
    draw_text("level: " + str(world.level), text_font, "red", 0, 60)
    draw_text("Turret Cost: 250", text_font, "red", 780, 530)
    draw_text("Upgrade Cost: 100", text_font, "red", 780, 560)
    draw_text("Chiikawa's Tower Defense", text_font, "grey100", 780, 600)

    level_complete = (world.spawned_momonga >= len(world.momonga_list) and len(enemy_group) == 0)

    #check level status
if not level_started:
    start_button.draw(screen)

    if start_button.clicked: 
        world.next_level()
        enemy_group.empty()

        world.restart_level()
        world.process_enemies()

        level_started = True
        last_spawn_time = pg.time.get_ticks()
    else:
        #spawn momonga wave
        if pg.time.get_ticks() - last_spawn_time > c.SPAWN_COOLDOWN:
            if world.spawned_momonga < len(world.momonga_list):
                momonga_type = world.momonga_list[world.spawned_momonga]
                enemy = Enemy(momonga_type,world.waypoints, enemy_images)
                enemy_group.add(enemy)
                world.spawned_momonga += 1
                last_spawn_time = pg.time.get_ticks()

    #check level completion status first, so the start button can reappear immediately
    if level_complete and not level_just_finished:
        world.money += c.LEVEL_REWARD
        level_started = False
        level_just_finished = True
        last_spawn_time = pg.time.get_ticks()

    #draw button for turret placement
    if turret_button.draw(screen):
            placing_turrets = True
    #if placing turret, show cancel button aswell as an option
    if placing_turrets == True:
        #show turret on mouse cursor
        cursor_rect = cursor_turret.get_rect()
        cursor_pos = pg.mouse.get_pos()
        cursor_rect.center = cursor_pos
        if cursor_pos [0] < c.SCREEN_WIDTH and cursor_pos[1] < c.SCREEN_HEIGHT:
            screen.blit(cursor_turret, cursor_rect)
        if cancel_button.draw(screen):
            placing_turrets = False
    #if turret is selected, show upgrade button
    if selected_turret:
        #check if turret can be upgraded, then show upgrade button
        if selected_turret.upgrade_lvl < c.TURRET_LEVELS:
            if upgrade_button.draw(screen):
                if world.money >= c.UPGRADE_COST:
                    world.money -= c.UPGRADE_COST
                    selected_turret.upgrade_recruit()

    #events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
        #detect if mouse has been clicked to place turret
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            #check if mouse is on screen
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
                #clear selected turrets
                selected_turret = None
                clear_selected_turret()
                if placing_turrets == True:
                    #check if player has enough money to place turret
                    if world.money >= c.BUY_COST:
                        create_turret(mouse_pos)
                else:
                    selected_turret = select_turret(mouse_pos)

    #update display
    pg.display.flip()

pg.quit()