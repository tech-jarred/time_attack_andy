# Author: ByteProductions
# Holds additional methods needed for "Time Attack Andy"

import arcade
import os
import sys
from random import randint
from math import sin, cos, fabs
import assets.player_logic as pl



def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and PyInstaller """
        try:
            base_path = sys._MEIPASS  # This is where PyInstaller unpacks files
        except AttributeError:
            base_path = os.path.abspath(".")  # Normal dev path
        return os.path.join(base_path, relative_path)

# Loading sounds that will be used for environment interactions.
coin_collect_sound = arcade.load_sound(resource_path("assets/sounds/coin1.wav"))

def add_coin_textures(coins: arcade.SpriteList) -> None:
     '''
     Add the additional textures for coin animation.
     '''
     for coin in coins:
        coin.textures.append(arcade.load_texture(resource_path("assets/coin_textures/coin_rotate_1.png")))
        coin.textures.append(arcade.load_texture(resource_path("assets/coin_textures/coin_rotate_2.png")))
        coin.textures.append(arcade.load_texture(resource_path("assets/coin_textures/coin_rotate_3.png")))


def animate_coin(animation_clock: float, coins: arcade.SpriteList) -> None:
    ''' 
    Takes in animation_clock, the amount of time passed in an animation cycle. 
    Adjusts the coins sprite to the correct texture based on time passed in animation cycle.
    '''
    
    # Setting an animation frame.
    coin_animation_frame = 0
        
    if animation_clock < 0.25:
        coin_animation_frame = 0
    elif animation_clock < 0.5:
        coin_animation_frame = 1
    elif animation_clock < 0.75:
        coin_animation_frame = 2
    elif animation_clock < 1:
        coin_animation_frame = 3
    
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
    for coin in coins:
        if arcade.math.get_distance(player.center_x, player.center_y, coin.center_x, coin.center_y) < 45:
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


def unique_stage_logic(stage_level: int, player: arcade.Sprite, entities: arcade.SpriteList,  animation_clock: float, background_color: arcade.color) -> arcade.color:
    '''
    For certain levels, different elements will have custom logic. This will be handled by this function.
    '''

    if stage_level == 4:
            move_floating_enemies(player, entities, 5.5)
            return arcade.color.DARK_OLIVE_GREEN

    elif stage_level == 8:
            return arcade.color.GRAY

    elif stage_level == 10:
            move_floating_enemies(player, entities, 1.5)

    elif stage_level == 11:
            return arcade.color.SKY_BLUE
    
    elif stage_level == 14:
            move_floating_enemies(player, entities, 4)
            return arcade.color.DESERT_SAND

    elif stage_level == 15:
         add_coin_textures(entities)
         animate_coin(animation_clock, entities)
        
    elif stage_level == 16:
         return arcade.color.BABY_PINK
    
    elif stage_level == 18:
         return arcade.color.YELLOW_ORANGE
    
    elif stage_level == 20:
         return arcade.color.BLUEBERRY
    
    return background_color # Keep current background color.


