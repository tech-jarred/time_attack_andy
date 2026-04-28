import arcade
import os
import sys
import assets.environment_logic as envl
import assets.player_logic as pl
import assets.constants as const


### Constants ###
# Window Constants
WINDOW_WIDTH, WINDOW_HEIGHT = arcade.window_commands.get_display_size()
WINDOW_TITLE = "Time Attack Andy"
BASE_HORIZONTAL_PIXELS = 640
BASE_VERTICAL_PIXELS = 360

# Environment Constants
GRAVITY = const.GRAVITY

# Player Movement Constants
PLAYER_JUMP_VELOCITY = const.PLAYER_JUMP_VELOCITY
PLAYER_MOVE_ACCEL = const.PLAYER_MOVE_ACCEL
PLAYER_FRICTION = const.PLAYER_FRICTION

CRAWL_VELOCITY = const.CRAWL_VELOCITY
NORMAL_VELOCITY = const.NORMAL_VELOCITY
SPRINT_VELOCITY = const.SPRINT_VELOCITY

MAX_JUMPS = const.MAX_JUMPS

# Texture Constants
COIN_TEXTURE = arcade.load_spritesheet(const.resource_path("assets/coin_textures/coin_sheet.png")).get_texture_grid(size = (18, 18), columns = 4, count = 4)
EVIL_COIN_TEXTURE = arcade.load_spritesheet(const.resource_path("assets/coin_textures/evil_coin_sheet.png")).get_texture_grid(size = (18, 18), columns = 4, count = 4)
### END CONSTANTS ###

# For debugging purposes, log recorded height of monitor.
print("INITIALIZING...")
print(f"WINDOW_WIDTH: {WINDOW_WIDTH}\nWINDOW_HEIGHT: {WINDOW_HEIGHT}")


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

        # Allows us to be able to display the framerate.
        arcade.enable_timings()
        self.display_fps = False

        # Initializing full screen state.
        self.fullscreen_mode = True
        self.window.set_fullscreen(self.fullscreen_mode)

        # Initialize game difficulty.
        self.difficulty = -1 # -1 represents normal difficulty. 20 represents hard difficulty.
        
        # Setting initial background color.
        # Setting background color
        self.background_color = arcade.color.DARK_BROWN if self.difficulty == -1 else arcade.color.DARK_RED

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

        # Loading font that will be used for game.
        arcade.load_font(self.resource_path("assets/PublicPixel-rv0pA.ttf"))
        
        # Initialize 2D cameras. (Note, Camera2D is exlusive to Arcade 3.3.3)
        self.game_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        # Setting up rest of game logic.
        self.reset()

        # Setting the player height constant (needed player to be initialized first.)
        self.PLAYER_HEIGHT_DEFAULT = self.player.height

        # Loading portal noise.
        self.portal_sound = arcade.load_sound(const.resource_path("assets/sounds/upgrade5.wav"))

        # Loading background music.
        self.background_music = arcade.Sound(self.resource_path("assets/sounds/jungle_driver.mp3"))

        # Starting background music
        self.music_volume = 0.4
        self.music_player = self.background_music.play(volume = self.music_volume, loop = True)

        # Initialize the GUI
        anchorx = 8
        anchory = 330
        self.gui_timer = arcade.Text(text = "Time: " + str(round(self.stage_time)), x = anchorx, y = anchory, color = arcade.color.CELADON_GREEN, font_size= 10, font_name = "Public Pixel", bold = True)
        self.gui_death_count = arcade.Text(text = "Deaths: " + str(self.deaths), x = anchorx, y = anchory - 25, color = arcade.color.CELADON_GREEN, font_size = 10, font_name = "Public Pixel", bold = True)
        self.gui_remaining_coins = arcade.Text(text = "Coins Left: " + str(self.coins_to_collect - self.coins_collected), x = anchorx, y = anchory - 50, color = arcade.color.CELADON_GREEN, font_size = 8, font_name = "Public Pixel", bold = True)
        self.gui_stage_level = arcade.Text(text = "Level " + str(self.stage_level), x = anchorx, y = anchory - 75, color = arcade.color.CELADON_GREEN, font_size = 10, font_name = "Public Pixel", bold = True)
        self.gui_total_time_text = arcade.Text(text = "Total Time:", x = anchorx, y = anchory - 100, color = arcade.color.CELADON_GREEN, font_size = 10, font_name = "Public Pixel", bold = True)
        self.gui_total_time_number = arcade.Text(text = str(round(self.total_time, 2)), x = 32, y = anchory - 125, color = arcade.color.CELADON_GREEN, font_size = 10, font_name = "Public Pixel", bold = False, anchor_x = "left")

        self.gui_start = arcade.Text(text = "Press 'B' to begin, 'C' for controls", x = 320, y = 50, color = arcade.color.WHITE, font_size = 12, font_name = "Public Pixel", bold = True, anchor_x = "center")
        arcade.Text(text="hi", x=3, y=anchory, )

        GUI_FONT_LEFT_ANCHOR = 30
        GUI_CONTROL_FONT_SIZE = 7
        self.gui_controls_1 = arcade.Text(f"Press ESC to restart a level. Adds 1 to death count.", GUI_FONT_LEFT_ANCHOR, 320, arcade.color.BEIGE, font_size = GUI_CONTROL_FONT_SIZE, font_name = "Public Pixel", bold = True)
        self.gui_controls_2 = arcade.Text(f"Press F12 to restart whole game from title screen.", GUI_FONT_LEFT_ANCHOR, 290, arcade.color.BEIGE, font_size = GUI_CONTROL_FONT_SIZE, font_name = "Public Pixel", bold = True)
        self.gui_controls_3 = arcade.Text(f"Press F11 to toggle fullscreen.", GUI_FONT_LEFT_ANCHOR, 260, arcade.color.BEIGE,font_size = GUI_CONTROL_FONT_SIZE, font_name = "Public Pixel", bold = True)
        self.gui_controls_4 = arcade.Text(f"Press F10 to raise volume.", GUI_FONT_LEFT_ANCHOR, 230, arcade.color.BEIGE, font_size = GUI_CONTROL_FONT_SIZE, font_name = "Public Pixel", bold = True)
        self.gui_controls_5 = arcade.Text(f"Press F9 to lower volume.", GUI_FONT_LEFT_ANCHOR, 200, arcade.color.BEIGE, font_size = GUI_CONTROL_FONT_SIZE, font_name = "Public Pixel", bold = True)
        self.gui_controls_6 = arcade.Text(f"Press M to switch between Normal and Hard mode.", GUI_FONT_LEFT_ANCHOR, 170, arcade.color.BEIGE, font_size = GUI_CONTROL_FONT_SIZE, font_name = "Public Pixel", bold = True)
        self.gui_controls_7 = arcade.Text(f"Press \\ to enter DEV mode. Use the UP and DOWN arrow keys to cycle through different stages.", GUI_FONT_LEFT_ANCHOR, 140, arcade.color.BEIGE, font_size = GUI_CONTROL_FONT_SIZE, font_name = "Public Pixel", bold = True, multiline = "True", width = 500)
        self.gui_controls_8 = arcade.Text(f"Click to return to title screen.", GUI_FONT_LEFT_ANCHOR, 110, arcade.color.BEIGE, font_size = GUI_CONTROL_FONT_SIZE, font_name = "Public Pixel", bold = True)

        # Initializing the keys counter.
        self.keys = set()


    def reset(self):
        """Resets the game to the initial state."""

        # Position the game camera and adjust its scope to match that of window.
        sw, sh = BASE_HORIZONTAL_PIXELS, BASE_VERTICAL_PIXELS
        self.game_camera.projection = arcade.LRBT(0, sw, 0, sh)
        self.game_camera.viewport = arcade.LRBT(0, self.window.width, 0, self.window.height)
        
        # Position the gui camera and adjust its scope to match that of window.
        self.game_camera.position = (0, 0)
        self.gui_camera.projection = arcade.LRBT(0, sw, 0, sh)
        self.gui_camera.viewport = arcade.LRBT(0, self.window.width, 0, self.window.height)
        self.gui_camera.position = (0, 0)

        # Initializing the map.
        MAP_FILE = self.resource_path(os.path.join("assets/stage_files", f"taa_stage_{self.stage_level}.tmx")) # concatentate string with the level number. have naming convention where file ends with the level number.
        self.map = arcade.TileMap(MAP_FILE, scaling = 1)

        self.stage_time = self.stage_time_list[self.stage_level + self.difficulty]

        # Initializing the relevant layers for easy access. Note: These are all sprite lists.
        self.enemies = self.map.sprite_lists["enemies"]
        self.dangerous_terrain = self.map.sprite_lists["dangerous_terrain"]
        self.terrain = self.map.sprite_lists["terrain"]
        self.coins = self.map.sprite_lists["coins"]
        self.starting_position = self.map.sprite_lists["starting_position"]
        self.portal = self.map.sprite_lists["portal"]

        # Adding different textures for coin animation.
        envl.setup_animated_coins(self.coins, COIN_TEXTURE)
        self.animation_clock = 0

        # Add different textures for evil coin entities.
        if self.stage_level == 15:
            envl.setup_animated_coins(self.enemies, EVIL_COIN_TEXTURE)

        # Determine amount of coins to collect in the stage.
        self.coins_to_collect = len(self.coins)

        # Moving the portal offscreen so player can't interact with it. (will return to screen when player collects all coins in a stage.)
        for section in self.portal:
            # Use virtual dimensions for portal offset. Stores it off screen until user has collected all coins.
            section.center_x -= BASE_HORIZONTAL_PIXELS
            section.center_y -= BASE_VERTICAL_PIXELS           
        
        self.portal_hidden = True

        # Initializing the player and some key attributes.
        self.players = arcade.SpriteList()
        self.player = arcade.Sprite(self.resource_path("assets/player_textures/player.png"), scale = 1) # giving player blob texture.
        
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

        # Activate game camera before drawing world objects.
        self.game_camera.use()

        # Draw the map every frame.
        for layer in self.map.sprite_lists:
            self.map.sprite_lists[layer].draw(pixelated=True)
        
        # Drawing the player.
        self.players.draw(pixelated=True)

        # Drawing the GUI.
        # Gemini edited this. Use dedicated GUI camera for HUD.
        self.gui_camera.use()
        
        if self.start:
            self.gui_timer.draw()
            self.gui_death_count.draw()
            self.gui_remaining_coins.draw()
            self.gui_stage_level.draw()
            self.gui_total_time_text.draw()
            self.gui_total_time_number.draw()
        
        elif not self.start and self.stage_level == 0:
            self.gui_start.draw()

        if self.stage_level == 21:
            if not self.dev_mode:
                self.final_time.draw()
                self.final_deaths.draw()
                self.instructions.draw()
            else:
                self.background_color = arcade.color.DARK_PASTEL_RED
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
        
        # Draw the framerate.
        if self.display_fps:
            fps = arcade.get_fps()
            arcade.draw_text(f"FPS: {fps:.0f}", 10, 10, arcade.color.WHITE, 14)
            

    def on_update(self, delta_time: float):
        """
        Contains the logic for updating the game's state each frame.
        """
        
        # Update level timer. If time runs out, reset the level.
        self.stage_time -= delta_time
        if not self.game_over:
            self.total_time += delta_time

        # Update GUI
        self.gui_timer.text = "Time: " + str(round(self.stage_time))
        self.gui_death_count.text = "Deaths: " + str(self.deaths)
        self.gui_remaining_coins.text = "Coins Left: " + str(self.coins_to_collect - self.coins_collected)
        self.gui_stage_level.text = "Level " + str(self.stage_level)
        self.gui_total_time_number.text = str(round(self.total_time, 2))

        # Check stage timer. Reset level if time runs out.
        if self.stage_time < 0:
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.reset()

        # Move the player in response to the keys the player pressed.
        pl.player_movement(self.player, self.PLAYER_HEIGHT_DEFAULT, self.keys)

        # Check if player is in bounds of map.
        # Gemini edited this. Use virtual dimensions for bounds check.
        if pl.player_out_of_bounds(self.player, BASE_HORIZONTAL_PIXELS, BASE_VERTICAL_PIXELS):
        # if pl.player_out_of_bounds(self.player, self.width, self.height):
            self.deaths = pl.player_dies_sequence(self.deaths)
            self.reset()

        # Check if player collected coins. If so, update counter and remove them from screen.
        self.coins_collected = envl.collect_coin(self.player, self.coins, self.coins_collected)
        self.gui_remaining_coins.text  = "Coins Left: " + str(self.coins_to_collect - self.coins_collected)

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
                # Gemini edited this. Use virtual dimensions for portal return.
                section.center_x += BASE_HORIZONTAL_PIXELS
                section.center_y += BASE_VERTICAL_PIXELS
                # section.center_x += self.width
                # section.center_y += self.height

            self.portal_hidden = not self.portal_hidden

        # Check if player entered portal. If so, move player to next level
        if not self.portal_hidden and envl.check_for_environment_contact(self.player, self.portal):
            arcade.play_sound(self.portal_sound)
            self.stage_level += 1
            self.reset()
        
        # Check if level 18. If so, execute special code.
        if self.stage_level == 18:
            envl.coin_run_away(self.player, self.coins)
            if not self.portal_hidden:
                for portal in self.portal:
                    portal.forward(2)
        
        # Check if player completed game.
        if self.stage_level == 21 and not self.game_over:
            self.game_over = True
            if not self.dev_mode:
                self.final_time = arcade.Text(f"Your final time was {round(self.total_time, 2)}", 400, 125, arcade.color.BEIGE, 10, font_name = "Public Pixel", bold = True, anchor_x = "center")
                self.final_deaths = arcade.Text(f"Your final deaths was {self.deaths}", 400, 75, arcade.color.BEIGE, 10, font_name = "Public Pixel", bold = True,  anchor_x = "center")
                self.instructions = arcade.Text("Thank you for playing my game! Click to play again!", 400, 25, arcade.color.BEIGE, 10, font_name = "Public Pixel", width = 448, bold = True, anchor_x = "center", multiline = True)
            else:
                self.sorry = arcade.Text(f"Sorry, you are in DEV mode and can not get a final time or death count. :(", 400, 125, arcade.color.BEIGE, 10, font_name = "Public Pixel", width = 448, bold = True, anchor_x = "center", multiline = True)
                self.instructions = arcade.Text("Thank you for playing my game! Click to play again!", 400, 75, arcade.color.BEIGE, 10, font_name = "Public Pixel", width = 448, bold = True, anchor_x = "center", multiline = True)
            

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

            # Re-call reset to update camera viewport for new window size.
            self.reset()

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
            self.background_color = arcade.color.DARK_BROWN if self.difficulty == -1 else arcade.color.DARK_RED
        
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
                self.background_color = arcade.color.DARK_RED
                print("Hard Mode Enabled")
            else:
                self.difficulty = -1
                self.background_color = arcade.color.DARK_BROWN
                print("Normal Mode Enabled")
        
        # For dev purposes.
        if key == arcade.key.BACKSLASH and not self.stage_level == 21:
            self.dev_mode = True
            print(f"DEV Mode: {self.dev_mode}")

        if self.dev_mode and key == arcade.key.UP:
            self.stage_level = (self.stage_level % 22) + 1
            self.reset()
        
        if self.dev_mode and key == arcade.key.DOWN:
            self.stage_level = (self.stage_level % 22) - 1
            self.reset()

        if key == arcade.key.TAB:
            self.display_fps = False if self.display_fps else True

        # Adjust the music volume.
        if key == arcade.key.F10:
            self.music_volume += 0.05
            if self.music_volume >= 1: # hard cap to prevent music volume from going above 1.
                self.music_volume = 1
            self.background_music.set_volume(self.music_volume, self.music_player)
            
        if key == arcade.key.F9:
            self.music_volume -= 0.05
            if self.music_volume <= 0: # hard cap to prevent volume from looping around.
                self.music_volume = 0
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
            self.background_color = arcade.color.DARK_BROWN if self.difficulty == -1 else arcade.color.DARK_RED 

def main():
    """ Contains the logic for launching and running the game. """
    # Initialize the window (for non-fullscreen)
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