# Author: ByteProductions
# Holds additional methods needed for "Time Attack Andy"
# Player Focused Section.

import arcade
import sys
import os
from math import fabs

# Import player movement information from main.
from main import PLAYER_MOVE_ACCEL, PLAYER_FRICTION, CRAWL_VELOCITY, NORMAL_VELOCITY, SPRINT_VELOCITY


def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and PyInstaller """
        try:
            base_path = sys._MEIPASS  # This is where PyInstaller unpacks files
        except AttributeError:
            base_path = os.path.abspath(".")  # Normal dev path
        return os.path.join(base_path, relative_path)


# Loading sounds that will be used for the player.
death_sound = arcade.load_sound(resource_path("assets/sounds/error3.wav"))


def add_player_textures(player: arcade.Sprite) -> None:
    texture = player.texture                                                                                   # Normal texture stored at index 0.
    texture = texture.flip_horizontally()       
    player.textures.append(texture)                                                                            # Stored at index 1.

    player.textures.append(arcade.load_texture(resource_path("assets/player_textures/player_jump.png")))                       # Stored at index 2.
    player.textures.append(arcade.load_texture(resource_path("assets/player_textures/player_jump.png")).flip_horizontally())   # Stored at index 3.
    player.textures.append(arcade.load_texture(resource_path("assets/player_textures/player_fall.png")))                       # Stored at index 4.
    player.textures.append(arcade.load_texture(resource_path("assets/player_textures/player_fall.png")).flip_horizontally())   # Stored at index 5.


def player_movement(player: arcade.Sprite, player_height: float, keys: set) -> None:    
    '''
    Move the player in response to their inputs from the keyboard.
    '''
    # # Setting up player heights for different speeds.
    PLAYER_HEIGHT_SPRINT = player_height * 0.8
    PLAYER_HEIGHT_CRAWL = player_height * 1.2
    
    # Check for sprinting or crouching.
    if arcade.key.LSHIFT in keys: # Establish sprinting versus walking velocity.
        velocity = SPRINT_VELOCITY
        player.height = PLAYER_HEIGHT_SPRINT

    elif arcade.key.LCTRL in keys:
        velocity = CRAWL_VELOCITY
        player.height = PLAYER_HEIGHT_CRAWL
    
    else:
        velocity = NORMAL_VELOCITY
        player.height = player_height

    # Check for left/right movement.
    if arcade.key.A in keys or arcade.key.LEFT in keys:
        player.change_x -= PLAYER_MOVE_ACCEL
        if player.change_x < -velocity:
            player.change_x = -velocity
    
    if arcade.key.D in keys or arcade.key.RIGHT in keys:
        player.change_x += PLAYER_MOVE_ACCEL
        if player.change_x > velocity:
            player.change_x = velocity

    # Determine player movement when a key is released.
    if not (arcade.key.A in keys) and not (arcade.key.D in keys):      # Determine direction moving.
        player.change_x *= PLAYER_FRICTION
    
    # To prevent player from infinitely moving, set a cap for when they hard stop.
    if abs(player.change_x) < 0.01:
        player.change_x = 0
    
    


def animate_player(player: arcade.Sprite, physics_engine: arcade.PhysicsEnginePlatformer) -> None:
    '''
    Animate the player in response to their movement.
    '''
    if physics_engine.can_jump() and player.change_x > 0:
        player.set_texture(0)
    elif physics_engine.can_jump() and player.change_x < 0:
        player.set_texture(1)
    elif player.change_y > 0 and player.change_x > 0:
            player.set_texture(2)
    elif player.change_y > 0 and player.change_x < 0:
        player.set_texture(3)
    elif player.change_y < 0 and player.change_x > 0:
        player.set_texture(4)
    elif player.change_y < 0 and player.change_x < 0:
        player.set_texture(5)


def player_idle(player: arcade.Sprite, animation_time: float) -> None:
    '''
    An idle animaton for the player when not moving.
    '''
    state_1 = player.height
    state_2 = player.height * 0.9
    if fabs(player.change_x) < 0.1:
        if animation_time < 0.5:
            player.height = state_1
        else:
            player.height = state_2


def player_dies_sequence(death_count: int) -> int:
    '''
    Play a death sound when player dies and increment death counter.
    '''

    # Print the player's death in terminal.
    print("Player Died. Resetting...")

    # Play a noise to indiciate death.
    arcade.play_sound(death_sound, volume = 2)
    
    # Increment death counter and return it to main game.
    death_count += 1
    return death_count


def player_out_of_bounds(player: arcade.Sprite, screen_width: float, screen_height: float) -> bool:
    '''
    Checks if the player is out of bounds.
    If done on the x-axis, prevents player from going beyond the window.
    If done in the y-axis, kills player and resets the stage.
    Returns true if player is below the map.
    '''

    # Prevent player from exiting the map on x-axis.
    if player.left < 0:
        player.left = 0
    
    if player.right > screen_width:
        player.right = screen_width

    # Check if player is below the map.
    return True if player.center_y < -5 * player.height else False