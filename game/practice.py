import arcade
from arcade import PymunkPhysicsEngine
from PIL import Image, ImageOps
import random


# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Postal Puppy"

WORLD_WIDTH = 2000
WORLD_HEIGHT = 1000

TILE_SCALING = 0.5
COIN_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20


class GameView(arcade.Window):

    def __init__(self):

        # Call the parent class to set up the window
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        self.background_color = arcade.csscolor.WHITE

        self.player_texture = None
        self.player_sprite = None

        self.camera = None

        self.scene = None

        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        self.gui_camera = None
        self.score = 0
        self.score_text = None

        self.jump_texture_index = 0
        self.fall_texture_index = 0
        self.jump_animation_speed = 0.15  # seconds per frame
        self.jump_timer = 0
        


    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        self.scene = arcade.Scene()

        self.player_sprite = arcade.AnimatedWalkingSprite()
        self.player_sprite.facing_direction = 0
        
        self.player_sprite.stand_right_textures = [arcade.load_texture("assets/walking-1.png")]
        self.player_sprite.walk_right_textures = [
            arcade.load_texture("assets/Walking-1.png"),
            arcade.load_texture("assets/Walking-2.png"),
            arcade.load_texture("assets/Walking-3.png"),
            arcade.load_texture("assets/Walking-4.png")]

        self.player_sprite.stand_left_textures = [self.load_texture_flipped("assets/Walking-1.png")]
        self.player_sprite.walk_left_textures = [
            self.load_texture_flipped("assets/Walking-1.png"),
            self.load_texture_flipped("assets/Walking-2.png"),
            self.load_texture_flipped("assets/Walking-3.png"),
            self.load_texture_flipped("assets/Walking-4.png")]
        
        self.player_sprite.jump_right_textures = [
            arcade.load_texture("assets/Jumping-2.png"),
            arcade.load_texture("assets/Jumping-3.png"),
            arcade.load_texture("assets/Jumping-4.png"),
            arcade.load_texture("assets/Jumping-5.png"),
            arcade.load_texture("assets/Jumping-6.png"),
            arcade.load_texture("assets/Jumping-7.png")
        ]

        self.player_sprite.jump_left_textures = [
            self.load_texture_flipped("assets/Jumping-2.png"),
            self.load_texture_flipped("assets/Jumping-3.png"),
            self.load_texture_flipped("assets/Jumping-4.png"),
            self.load_texture_flipped("assets/Jumping-5.png"),
            self.load_texture_flipped("assets/Jumping-6.png"),
            self.load_texture_flipped("assets/Jumping-7.png")
        ]
        

        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128


        self.scene.add_sprite("Player", self.player_sprite)
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Mail", use_spatial_hash=True)


        self.camera = arcade.Camera2D()

        # from better keyboard
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.gui_camera = arcade.Camera2D()
        self.score = 0
        self.score_text = arcade.Text(f"Score: {self.score}", x=0, y=5)


        platforms = [ #for floating platforms. Add as needed
            [1620,300,5],
            [512,256,3],[1100,650,5],
            [800,400,4],
            [400, 526, 2],[2000,500,7]
        ]
        for right_x, y, length in platforms:
            for i in range(length):
                if i == 0:
                    texture_file = "assets/Platform-1.png"
                elif i == length - 1:
                    texture_file = "assets/Platform-3.png"
                else:
                    texture_file = "assets/Platform-2.png"

                tile_x = right_x - (length - 1 - i) * 64
                wall = arcade.Sprite(texture_file, scale=1)
                wall.center_x = tile_x
                wall.center_y = y
                self.scene.add_sprite("Walls", wall)


        #the floor
        num_floor_tiles = WORLD_WIDTH // 64

        for i in range(num_floor_tiles):
            if i == 0:
                texture_file = "assets/Platform-1.png"
            elif i == num_floor_tiles - 1:
                texture_file = "assets/Platform-3.png"
            else:
                texture_file = "assets/Platform-2.png"
            
            floor_tile = arcade.Sprite(texture_file, scale = 1)
            floor_tile.center_x = i * 64 + 32
            floor_tile.center_y = 32
            self.scene.add_sprite("Walls", floor_tile)


        self.scene.add_sprite_list("Rocks", use_spatial_hash=False)
        coordinate_list = [[512, 75], [256, 75], [768, 75],[750,440]]
        for coordinate in coordinate_list:
            rock = arcade.Sprite(
                "assets/Rock-2.png", scale=1)
            rock.position = coordinate
            self.scene.add_sprite("Rocks", rock)

        floor_tile = arcade.Sprite("assets/Doghouse.png", scale = 2)
        floor_tile.position = [65,85]
        self.scene.add_sprite("Walls", floor_tile)

        #mail

        mail_textures = [
            arcade.load_texture("assets/Mail-1.png"),
            arcade.load_texture("assets/Mail-2.png"),
            arcade.load_texture("assets/Mail-3.png")
        ]

        for x in range(128, 1250, 256):
            mail = AnimatedTile(mail_textures)
            mail.center_x = x
            mail.center_y = 90
            self.scene.add_sprite("Mail", mail)

        #foreground
        
        self.scene.add_sprite_list("Foreground", use_spatial_hash=False)

        desired_scale = 0.47

        grass_animation_1 = [
            self.load_scaled_texture("assets/Grass-1-1.png", desired_scale),
            self.load_scaled_texture("assets/Grass-1-2.png", desired_scale),
            self.load_scaled_texture("assets/Grass-1-3.png", desired_scale),
        ]

        grass_animation_2 = [
            self.load_scaled_texture("assets/Grass-2-1.png", desired_scale),
            self.load_scaled_texture("assets/Grass-2-2.png", desired_scale),
            self.load_scaled_texture("assets/Grass-2-3.png", desired_scale),
        ]

        for i in range(num_floor_tiles):
            if i % 2 == 0:
                textures = grass_animation_1
            else:
                textures = grass_animation_2
            
            grass_textures = textures
            grass = AnimatedTile(grass_textures)
            grass_scale = 0.5
            grass.center_x = i * 64 + 32
            grass.center_y = 32 + (grass.height) / 2 + 6.5
            grass.update_interval = .5
            self.scene.add_sprite("Foreground", grass) 

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls=self.scene["Walls"], gravity_constant = GRAVITY
        )
    
    @staticmethod
    def load_texture_flipped(filename):
        image = Image.open(filename)
        flipped = ImageOps.mirror(image)
        return arcade.Texture(name=filename + "_flipped", image=flipped)
    @staticmethod
    def load_scaled_texture(filename, scale):
        img = Image.open(filename)
        new_width = int(img.width * scale)
        new_height = int(img.height * scale)
        img = img.resize((new_width, new_height))
        return arcade.Texture(name=filename, image=img)


    def on_draw(self):
        """Render the screen."""

        # The clear method should always be called at the start of on_draw.
        # It clears the whole screen to whatever the background color is
        # set to. This ensures that you have a clean slate for drawing each
        # frame of the game.
        self.clear()

        # Code to draw other things will go here
        # Code to draw other things will go here
        self.camera.use()

        self.scene.draw()

        self.gui_camera.use()
        self.score_text.draw()

    
    # from better keyboard
    def update_player_speed(self):
        self.player_sprite.change_x = 0

        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.player_sprite.facing_direction = 1
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.player_sprite.facing_direction = 0
    
        half_width = self.player_sprite.width / 2
        if self.player_sprite.center_x < half_width:
            self.player_sprite.center_x = half_width
        elif self.player_sprite.center_x > WORLD_WIDTH - half_width:
            self.player_sprite.center_x = WORLD_WIDTH - half_width

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""
        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()


    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""
        if key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()


    def on_update(self, delta_time):
        self.camera.position = self.player_sprite.position
        self.update_player_speed()
        self.physics_engine.update()
        self.player_sprite.update_animation(delta_time)

        for grass in self.scene["Foreground"]:
            grass.update_animation(delta_time)

        for mail in self.scene["Mail"]:
            mail.update_animation(delta_time)

        mail_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Mail"]
        )

        for mail in mail_hit_list:
            mail.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 75
            self.score_text.text = f"Score: {self.score}"

        #for jumping animation
        self.jump_timer += delta_time

        if self.player_sprite.change_y > 0:
            if self.jump_timer > self.jump_animation_speed:
                self.jump_texture_index = (self.jump_texture_index + 1) % len(self.player_sprite.jump_right_textures)
                self.jump_timer = 0
            if self.player_sprite.facing_direction == 0:
                self.player_sprite.texture = self.player_sprite.jump_right_textures[self.jump_texture_index]
            else:
                self.player_sprite.texture = self.player_sprite.jump_left_textures[self.jump_texture_index]
        
        else:
            self.player_sprite.update_animation(delta_time)
            self.jump_texture_index = 0

class AnimatedTile(arcade.Sprite):
    def __init__(self, textures, update_interval=0.2):
        super().__init__()
        self.textures_list = textures
        self.current_index = 0
        self.update_interval = update_interval
        self.timer = 0
        self.texture = self.textures_list[0]

    def update_animation(self, delta_time: float = 1/60):
        self.timer += delta_time
        if self.timer > self.update_interval:
            self.current_index = (self.current_index + 1) % len(self.textures_list)
            self.texture = self.textures_list[self.current_index]
            self.timer = 0



def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()