"""
Author: ByteProductions

Time Attack Andy

Time Attack Andy is a basic 2D platformer with one main objective: Get to the end of the stage in as few deaths as possible. The player will
navigate through the map, avoiding any obstacles in the path, and collect the required amount of coins for progression. They will have to do so
before the stage timer runs out, or else they will die. Time Attack Andy engages the player through challenging platforming sequences and provides
urgency through the short time frames allowed for precise platforming.

Pre-Release 2
    - Buffed players base speed from 3 to 4
    - Slightly modified level design in stage 6
    - increased timer on most levels. This is now the "Normal" difficulty.
    - added a Hard and Normal difficulty, as well as a way to toggle between the two.
    - added ability to see interface controls from main page.
    - adjusted it so map is scaled according to the screen width, and not a fixed constant.
"""

import arcade
import os
import sys
import assets.environment_logic as envl
import assets.player_logic as pl


# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = arcade.window_commands.get_display_size()
WINDOW_TITLE = "Time Attack Andy"
GRAVITY = 0.6
PLAYER_JUMP_VELOCITY = 10
MAX_JUMPS = 2
BASE_HORIZONTAL_PIXELS = 640
BASE_VERTICAL_PIXELS = 360
SCALE_FACTOR = WINDOW_WIDTH // BASE_HORIZONTAL_PIXELS

print("INITIALIZING...")
print(f"WINDOW_WIDTH: {WINDOW_WIDTH}\nWINDOW_HEIGHT: {WINDOW_HEIGHT}\nSCALE_FACTOR: { SCALE_FACTOR }")


class GameView(arcade.View):
    """
    The main application View associated with this game.
    """

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and PyInstaller """
        try:
            base_path = sys._MEIPASS  # This is where PyInstaller unpacks files
        except AttributeError:
            base_path = os.path.abspath(".")  # Normal dev path
        return os.path.join(base_path, relative_path)

    def __init__(self):
        """ Called when the View is created. """
        super().__init__()

        # Initializing full screen state.
        self.fullscreen_mode = True
        self.window.set_fullscreen(self.fullscreen_mode)

        # Setting initial background color.
        # Setting background color
        self.background_color = arcade.color.DARK_BROWN

        # Initializing death counter.
        self.deaths = 0

        # Setting initial stage count to level 1.
        self.stage_level = 0

        # Initializing total playtime to 0.
        self.total_time = 0

        # Initializing game checks.
        self.game_over = False
        self.dev_mode = False
        self.start = False

        # Creating a list with the timers for each stage.
        self.stage_time_list = []
        with open(self.resource_path("assets/stage_times.txt"), 'r') as file:
            for line in file:
                amount_of_stage_time = line.split()
                self.stage_time_list.append(int(amount_of_stage_time[1]))
        
        self.difficulty = -1 # -1 represents normal difficulty. 20 represents hard difficulty.

        # Loading font that will be used for game.
        arcade.load_font(self.resource_path("assets/PublicPixel-rv0pA.ttf"))
        
        # Setting up rest of game logic.
        self.reset()

        # Setting the player height constant (needed player to be initialized first.)
        self.PLAYER_HEIGHT_DEFAULT = self.player.height

        # Loading background music.
        self.background_music = arcade.Sound(self.resource_path("assets/sounds/jungle_driver.mp3"))

        # Starting background music
        self.music_volume = 0.4
        self.music_player = self.background_music.play(volume = self.music_volume, loop = True)

        # Initialize the GUI
        anchorx = 25
        anchory = 850
        self.gui_timer = arcade.Text("Time: " + str(round(self.stage_time)), anchorx, anchory, arcade.color.CELADON_GREEN, font_size= 30, font_name = "Public Pixel", bold = True)
        self.gui_death_count = arcade.Text("Deaths: " + str(self.deaths), anchorx, anchory - 100, arcade.color.CELADON_GREEN, font_size = 30, font_name = "Public Pixel", bold = True)
        self.gui_remaining_coins = arcade.Text("Coins Left: " + str(self.coins_to_collect - self.coins_collected), anchorx, anchory - 200, arcade.color.CELADON_GREEN, font_size = 30, font_name = "Public Pixel", bold = True)
        self.gui_stage_level = arcade.Text("Level " + str(self.stage_level), anchorx, anchory - 300, arcade.color.CELADON_GREEN, font_size = 30, font_name = "Public Pixel", bold = True)
        self.gui_total_time = arcade.Text("Total Time: " + str(round(self.total_time, 2)), 9, anchory - 400, arcade.color.CELADON_GREEN, font_size = 20, font_name = "Public Pixel", bold = True)
        self.gui_start = arcade.Text("Press 'B' to begin, 'C' for controls", 450, 50, arcade.color.WHITE, font_size = 25, font_name = "Public Pixel", bold = True)

        self.gui_controls_1 = arcade.Text(f"Press ESC to restart a level. Adds 1 to death count.", 78, 1000, arcade.color.BEIGE, 20, font_name = "Public Pixel", bold = True)
        self.gui_controls_2 = arcade.Text(f"Press F12 to restart whole game from title screen.", 78, 900, arcade.color.BEIGE, 20, font_name = "Public Pixel", bold = True)
        self.gui_controls_3 = arcade.Text(f"Press F11 to toggle fullscreen.", 78, 800, arcade.color.BEIGE, 20, font_name = "Public Pixel", bold = True)
        self.gui_controls_4 = arcade.Text(f"Press F10 to raise volume.", 78, 700, arcade.color.BEIGE, 20, font_name = "Public Pixel", bold = True)
        self.gui_controls_5 = arcade.Text(f"Press F9 to lower volume.", 78, 600, arcade.color.BEIGE, 20, font_name = "Public Pixel", bold = True)
        self.gui_controls_6 = arcade.Text(f"Press M to switch between Normal and Hard mode.", 78, 500, arcade.color.BEIGE, 20, font_name = "Public Pixel", bold = True)
        self.gui_controls_7 = arcade.Text(f"Press \\ to enter DEV mode. Use the UP and DOWN arrow keys to cycle through different stages.", 78, 400, arcade.color.BEIGE, 10, font_name = "Public Pixel", bold = True)
        self.gui_controls_8 = arcade.Text(f"Click to return to title screen.", 78, 200, arcade.color.BEIGE, 20, font_name = "Public Pixel", bold = True)

        # Initializing the keys counter.
        self.keys = set()


    def reset(self):
        """Resets the game to the initial state."""

        # Initializing the map.
        MAP_FILE = self.resource_path(os.path.join("assets/stage_files", f"taa_stage_{self.stage_level}.tmx")) # concatentate string with the level number. have naming convention where file ends with the level number.
        self.map = arcade.TileMap(MAP_FILE, scaling = SCALE_FACTOR)
        #self.map = arcade.TileMap(MAP_FILE, scaling = 2.5)
        self.stage_time = self.stage_time_list[self.stage_level + self.difficulty]

        # Initializing the relevant layers for easy access. Note: These are all sprite lists.
        self.enemies = self.map.sprite_lists["enemies"]
        self.dangerous_terrain = self.map.sprite_lists["dangerous_terrain"]
        self.terrain = self.map.sprite_lists["terrain"]
        self.coins = self.map.sprite_lists["coins"]
        self.starting_position = self.map.sprite_lists["starting_position"]
        self.portal = self.map.sprite_lists["portal"]

        # Adding different textures for coin animation.
        envl.add_coin_textures(self.coins)
        self.animation_clock = 0

        # Determine amount of coins to collect in the stage.
        self.coins_to_collect = len(self.coins)

        # Moving the portal offscreen so player can't interact with it. (will return to screen when player collects all coins in a stage.)
        for section in self.portal:
            section.center_x -= self.width
            section.center_y -= self.height        
        
        self.portal_hidden = True

        # Initializing the player and some key attributes.
        self.players = arcade.SpriteList()
        self.player = arcade.Sprite(self.resource_path("assets/player_textures/player.png"), scale = SCALE_FACTOR) # giving player blob texture.
        
        start_x = self.starting_position[0].center_x #+ 18   # Setting up starting position.
        start_y = self.starting_position[0].center_y        # Determined by position of starting tile in map.
        self.player.position = (start_x, start_y)
        
        self.players.append(self.player) # adding player to sprite list.

        # Adding textures for the player facing different ways.
        pl.add_player_textures(self.player)

        # Initializing coin counter.
        self.coins_collected = 0

        # Initializing the physics engine.
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, walls=self.terrain, gravity_constant=GRAVITY)
        self.JUMP_COUNTER = 1 # Keep track of jumps the player has taken. Initialized to 1 to account for update() moving faster than the player will from the ground.

        
    def on_draw(self):
        """
        Render the screen each frame.
        """
        # Clear the scene every frame.
        self.clear()

        # Draw the map every frame.
        for layer in self.map.sprite_lists:
            self.map.sprite_lists[layer].draw()
        
        # Drawing the player.
        self.players.draw()

        # Drawing the GUI.
        
        if self.start:
            self.gui_timer.draw()
            self.gui_death_count.draw()
            self.gui_remaining_coins.draw()
            self.gui_stage_level.draw()
            self.gui_total_time.draw()
        
        elif not self.start and self.stage_level == 0:
            self.gui_start.draw()

        if self.stage_level == 21:
            if not self.dev_mode:
                self.final_time.draw()
                self.final_deaths.draw()
                self.instructions.draw()
            else:
                self.background_color = arcade.color.DARK_RED
                self.sorry.draw()
                self.instructions.draw()

        if self.stage_level == 22:
            self.gui_controls_1.draw()
            self.gui_controls_2.draw()
            self.gui_controls_3.draw()
            self.gui_controls_4.draw()
            self.gui_controls_5.draw()
            self.gui_controls_6.draw()
            self.gui_controls_7.draw()
            self.gui_controls_8.draw()
            

    def on_update(self, delta_time: float):
        """
        Contains the logic for updating the game's state each frame.
        """
        
        # Update level timer. If time runs out, reset the level.
        self.stage_time -= delta_time
        if not self.game_over:
            self.total_time += delta_time

        # Update GUI
        self.gui_timer.value = "Time: " + str(round(self.stage_time))
        self.gui_death_count.value = "Deaths: " + str(self.deaths)
        self.gui_remaining_coins.value = "Coins Left: " + str(self.coins_to_collect - self.coins_collected)
        self.gui_stage_level.value = "Level " + str(self.stage_level)
        self.gui_total_time.value = "Total Time: " + str(round(self.total_time, 2))

        # Check stage timer. Reset level if time runs out.
        if self.stage_time < 0:
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.reset()

        # Move the player in response to the keys the player pressed.
        pl.player_movement(self.player, self.PLAYER_HEIGHT_DEFAULT, self.keys)

        # Check if player is in bounds of map.
        if pl.player_out_of_bounds(self.player, self.width, self.height):
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.reset()

        # Check if player collected coins. If so, update counter and remove them from screen.
        self.coins_collected = envl.collect_coin(self.player, self.coins, self.coins_collected)
        self.gui_remaining_coins.value  = "Coins Left: " + str(self.coins_to_collect - self.coins_collected)

        # Animate coin sprites.
        self.animation_clock += delta_time
        envl.animate_coin(self.animation_clock, self.coins)

        if self.animation_clock > 1:
            self.animation_clock = 0

        # Check if the player made contact with dangerous terrain. If so, kill them and restart level.
        if envl.check_for_environment_contact(self.player, self.dangerous_terrain):
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.reset()

        # Check if the player made contact with enemies. If so, kill them and restart level.
        if envl.check_for_environment_contact(self.player, self.enemies):
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.reset()
        
        # Animate the player in response to their movement.
        pl.animate_player(self.player, self.physics_engine)
        pl.player_idle(self.player, self.animation_clock)

        # Updating jump counter when player hits ground.
        if self.physics_engine.can_jump(18):
            self.JUMP_COUNTER = 1
        
        # Checking for unique stages. If so, implement their logic.
        self.background_color = envl.unique_stage_logic(self.stage_level, self.player, self.enemies, self.animation_clock, self.background_color)

        # Check if portal can return to main screen.
        if envl.check_coins_collected(self.coins_collected, self.coins_to_collect) and self.portal_hidden:
            for section in self.portal:
                section.center_x += self.width
                section.center_y += self.height

            self.portal_hidden = not self.portal_hidden

        # Check if player entered portal. If so, move player to next level
        if not self.portal_hidden and envl.check_for_environment_contact(self.player, self.portal):
            self.stage_level += 1
            self.reset()
        
        # Check if level 18. If so, execute special code.
        if self.stage_level == 18:
            envl.coin_run_away(self.player, self.coins)
            if not self.portal_hidden:
                for portal in self.portal:
                    portal.forward(5)
        
        # Check if player completed game.
        if self.stage_level == 21 and not self.game_over:
            self.game_over = True
            if not self.dev_mode:
                self.final_time = arcade.Text(f"Your final time was {round(self.total_time, 2)}", 678, 400, arcade.color.BEIGE, 30, font_name = "Public Pixel", bold = True)
                self.final_deaths = arcade.Text(f"Your final deaths was {self.deaths}", 678, 300, arcade.color.BEIGE, 30, font_name = "Public Pixel", bold = True)
                self.instructions = arcade.Text("Thank you for playing my game! Click to play again!", 678, 200, arcade.color.BEIGE, 30, font_name = "Public Pixel", width = 1200, bold = True, multiline = True)
            else:
                self.sorry = arcade.Text(f"Sorry, you are in DEV mode and can not get a final time or death count. :(", 678, 400, arcade.color.BEIGE, 30, font_name = "Public Pixel", width = 1100, bold = True, multiline = True)
                self.instructions = arcade.Text("Thank you for playing my game! Click to play again!", 678, 200, arcade.color.BEIGE, 30, font_name = "Public Pixel", width = 1200, bold = True, multiline = True)
            

        # Updating necesary sprite lists/objects.
        self.players.update()
        self.physics_engine.update()
        self.enemies.update()
        self.coins.update()
        self.portal.update()

        
    def on_key_press(self, key: int, key_modifiers: int):
        """
        Called whenever a key is pressed.
        """

        # Allow player to restart.
        if key == arcade.key.ESCAPE:
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.reset()

        # Toggle fullscreen
        if key == arcade.key.F11:
            self.fullscreen_mode = not self.fullscreen_mode
            self.window.set_fullscreen(self.fullscreen_mode)

        # Player jumping mechanism.
        if key == arcade.key.SPACE and self.JUMP_COUNTER < MAX_JUMPS:
                self.player.change_y = PLAYER_JUMP_VELOCITY
                self.JUMP_COUNTER += 1
                          
        # Game reset.
        if key == arcade.key.F12:
            self.stage_level = 0
            self.reset()
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.game_over = False
            self.deaths = 0
            self.total_time = 0
            self.dev_mode = False
            self.start = False
            self.background_color = arcade.color.DARK_BROWN
        
        # Start game.
        if self.stage_level == 0 and key == arcade.key.B:
            self.start = True
            self.stage_level += 1
            self.reset()
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.game_over = False
            self.deaths = 0
            self.total_time = 0
            self.background_color = arcade.color.DARK_BROWN
        
        # Allow player to adjust difficulty.
        if self.stage_level == 0 and key == arcade.key.M and not self.dev_mode:
            if self.difficulty == -1:
                self.difficulty = 20
                print("Hard Mode Enabled")
            else:
                self.difficulty = -1
                print("Normal Mode Enabled")
        
        # For dev purposes.
        if key == arcade.key.BACKSLASH:
            self.dev_mode = True

        if self.dev_mode and key == arcade.key.UP:
            self.stage_level += 1
            self.reset()
        
        if self.dev_mode and key == arcade.key.DOWN:
            self.stage_level -= 1
            self.reset()

        # Adjust the music volume.
        if key == arcade.key.F10:
            self.music_volume += 0.1
            self.background_music.set_volume(self.music_volume, self.music_player)
            
        if key == arcade.key.F9:
            self.music_volume -= 0.1
            self.background_music.set_volume(self.music_volume, self.music_player)

        # Allow player to see the controls.
        if self.stage_level == 0 and key == arcade.key.C:
            self.stage_level = 22
            self.reset()
            self.deaths = pl.player_dies_sequence(self.deaths)

        # Add pressed keys to list of keys held down.
        self.keys.add(key)


    def on_key_release(self, key: int, key_modifiers: int):
        """
        Called whenever the user lets off a previously pressed key.
        """
        
        # Remove released keys from the pressed keys list.
        self.keys.discard(key)


    def on_mouse_press(self, x: float, y: float, button: int, key_modifiers: int):
        """
        Called when the user presses a mouse button.
        """
        if self.stage_level == 21 or self.stage_level == 22:
            self.stage_level = 0
            self.reset()
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.game_over = False
            self.deaths = 0
            self.total_time = 0
            self.dev_mode = False
            self.start = False
            self.background_color = arcade.color.DARK_BROWN

def main():
    """ Contains the logic for launching and running the game. """
    # Create a Window object. This is what actually shows up on screen
    window = arcade.Window(BASE_HORIZONTAL_PIXELS, BASE_VERTICAL_PIXELS, WINDOW_TITLE)

    # Associate the main GameView with the Window
    game = GameView()

    # Associate the GameView with the Window
    window.show_view(game)

    # Start the arcade game loop
    arcade.run()


# Main Guard 
# Skips running the main() function when this file is imported in another Python program.
if __name__ == "__main__":
    main()