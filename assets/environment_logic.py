# Author: ByteProductions
# Holds additional methods needed for "Time Attack Andy"

import arcade
import os
import sys
from random import randint
from math import sin, cos, fabs
from assets.constants import resource_path, STAGE_CONFIG

# Loading sounds that will be used for environment interactions.
coin_collect_sound = arcade.load_sound(resource_path("assets/sounds/coin1.wav"))

def setup_animated_coins(coins: arcade.SpriteList, textures: arcade.SpriteSheet) -> None:
    '''
    Assigns the pre-loaded texture list to each coin sprite in a stage once.
    '''
    # Load coin textures onto coins.
    for coin in coins:
        coin.textures = textures

def animate_coin(animation_clock: float, coins: arcade.SpriteList) -> None:
    ''' 
    Takes in animation_clock, the amount of time passed in an animation cycle. 
    Adjusts the coins sprite to the correct texture based on time passed in animation cycle.
    '''
    # Determine which stage of the coin animation we are at.
    coin_animation_frame = int(animation_clock * 4) % 4
    
    # Updating coins to match animation frame.    
    for coin in coins:
        coin.set_texture(coin_animation_frame)


def collect_coin(player: arcade.Sprite, coins: arcade.SpriteList, coins_collected: int) -> int:
    '''
    Logic for when a player interacts with a coin.
    Will update the coins collected counter by 1 for each coin collected.
    Removes collected coins from the screen.
    '''

    # Determining which coins were hit by the player. Store them in a list.
    coins_player_touched = arcade.check_for_collision_with_list(player, coins)

    # If any coins were hit, remove them from screen and increment amount of coins collected.
    for coin in coins_player_touched:
        coin.kill()
        arcade.play_sound(coin_collect_sound)
        coins_collected += 1
    
    # Return the amount of coins collected thus far.
    return coins_collected


def coin_run_away(player: arcade.Sprite, coins: arcade.SpriteList) -> None:
    '''
    Have the coin move away from the player when they get too close.
    '''
    speed = 5
    coin_boundary_distance = 45
    for coin in coins:
        squared_distance = (player.center_x - coin.center_x)**2 + (player.center_y - coin.center_y)**2
        if squared_distance < coin_boundary_distance**2:
            x = -1 * speed * sin(arcade.math.get_angle_radians(coin.center_x, coin.center_y, player.center_x, player.center_y))
            y = -1 * speed * cos(arcade.math.get_angle_radians(coin.center_x, coin.center_y, player.center_x, player.center_y))
            coin.velocity = (x, y)
        else:
             coin.velocity = (0, 0)



def check_for_environment_contact(player: arcade.Sprite, zone: arcade.SpriteList) -> bool:
    '''
    Check if a designated section of the environment is colliding with the player. If so, return True. Otherwise, return False.
    '''
    environment_contacting_player = arcade.check_for_collision_with_list(player, zone)
    return True if len(environment_contacting_player) != 0 else False
        

def check_coins_collected(coins_collected: int, coins_to_collect: int) -> bool:
    '''
    Determine if the player has collected all of the coins in the stage. Return True if yes, False otherwise.
    '''
    return True if coins_collected == coins_to_collect else False


def move_floating_enemies(player: arcade.Sprite, enemies: arcade.SpriteList, speed: int) -> None:
    '''
    Move enemies that float towards the player.
    ''' 
    for enemy in enemies:
            if fabs(player.change_x) > 1:
                x = speed * sin(arcade.math.get_angle_radians(enemy.center_x, enemy.center_y, player.center_x, player.center_y))
                y = speed * cos(arcade.math.get_angle_radians(enemy.center_x, enemy.center_y, player.center_x, player.center_y))
                enemy.velocity = (x, y)
            else:
                enemy.velocity = (0, 0)

# Define a mapping of colors and special behaviors.
# Is a dictionary where key is stage level and value is another dictionary with properties.

def unique_stage_logic(stage_level: int, player: arcade.Sprite, entities: arcade.SpriteList, animation_clock: float, background_color: arcade.color) -> arcade.color:
    config = STAGE_CONFIG.get(stage_level, {})
    
    # Handle Enemy Movement
    if "speed" in config:
        move_floating_enemies(player, entities, config["speed"])
    
    # Handle Animations for Level 15
    if stage_level == 15:
        animate_coin(animation_clock, entities)
        
    # Return new color if defined, otherwise keep existing
    return config.get("color", background_color)