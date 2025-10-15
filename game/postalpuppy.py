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

        #for npc text
        self.show_npc_text = False
        self.npc_text = ""
        self.name_text = ""

        #for dialogue choices
        self.npc_options = []
        self.selected_option = 0
        self.in_dialogue = False
        self.dialogue_waiting_close = False
        # When non-empty, E/Enter will advance these follow-up lines
        # before finally closing the dialogue.
        self.dialogue_followups = []
        # End-screen controls
        self.trigger_end_on_followups = False
        self.show_end_screen = False
        


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
        self.scene.add_sprite_list("Rocks", use_spatial_hash=True)
        self.scene.add_sprite_list("NPCs", use_spatial_hash=True)

        #bear npc
        bear_textures = [arcade.load_texture("assets/Bear-1.png"),
                         arcade.load_texture("assets/Bear-2.png"),
                         arcade.load_texture("assets/Bear-3.png"),
                         arcade.load_texture("assets/Bear-2.png"),
                         arcade.load_texture("assets/Bear-1.png")]
        bear = AnimatedTile(bear_textures, update_interval=1)
        bear.scale = 1.25
        bear.center_x = 1960
        bear.center_y = 576
        bear.angle = 7.4 #rotate the bear
        self.scene["NPCs"].append(bear)
        self.scene["Walls"].append(bear)

        #bear textbox
        self.show_npc_text = False

        self.textbox_list = arcade.SpriteList(0)
        self.textbox_sprite = arcade.Sprite("assets/Textbox.png", scale=1)
        self.textbox_list.append(self.textbox_sprite)

        self.camera = arcade.Camera2D()

        # from better keyboard
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        self.gui_camera = arcade.Camera2D() #gui camera for things that do not move on the screen (like score)
        self.score = 0
        self.score_text = arcade.Text(f"Score: {self.score}", x=0, y=5)

        #for debugging purposes. Shows player coordinated
        #self.coord_text = arcade.Text("", x=700, y=500, color=arcade.color.BLACK)
        #self.instruction_text = arcade.Text("Deliver all the mail to the bear", x=500, y=1000, color=arcade.color.BLACK)


        platforms = [ #for floating platforms. Add as needed
            [1620,300,5],
            [512,256,3],[1100,650,5],
            [800,400,4], [200,650,3],
            [400, 526, 2],[2000,500,7],[1365,500,3]

        ]
        # Collect platform tile positions so we can add grass on them later
        platform_tile_positions = []
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
                platform_tile_positions.append((tile_x, y))


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


        self.rock_list = arcade.SpriteList()
        coordinate_list = [[512, 75], [256, 75], [768, 75]]
        for coordinate in coordinate_list:
            rock = arcade.Sprite(
                "assets/Box.png", scale=1)
            rock.position = coordinate
            self.scene.add_sprite("Rocks", rock)
            self.rock_list.append(rock)
        self.rocks = self.scene["Rocks"]

        #for rock-1 pngs (this is only for rocks on the floating platforms.
        #character is able to jump on, but not push)
        actual_rocks = [[750,440], [1700,545]]
        for item in actual_rocks:
            rock = arcade.Sprite("assets/Rock-1.png", scale=1)
            rock.position = item
            self.scene.add_sprite("Walls", rock)
        self.actual_rocks = self.scene["Walls"]
        # for the second rock sprite
        actual_rocks2 = [[1472,340]]
        for item in actual_rocks2:
            rock = arcade.Sprite("assets/Rock-2.png", scale=1)
            rock.position = item
            self.scene.add_sprite("Walls", rock)
        self.actual_rocks2 = self.scene["Walls"]




        floor_tile = arcade.Sprite("assets/Doghouse.png", scale = 2)
        floor_tile.position = [65,85]
        self.scene.add_sprite("Walls", floor_tile)

        #mail

        mail_textures = [
            arcade.load_texture("assets/Mail-1.png"),
            arcade.load_texture("assets/Mail-2.png"),
            arcade.load_texture("assets/Mail-3.png")
        ]

        mail_coords = [[132,684], [136,850], [527,600], [762,124],[1932,66],
                       [1252,250],[1290,534],[1690,586],[970,810]]
        for coord in mail_coords:
            mail = AnimatedTile(mail_textures)
            mail.position = coord
            self.scene.add_sprite("Mail", mail)

        #foreground
        #the grass animation. has two different animations that it alternates through
        self.scene.add_sprite_list("Foreground", use_spatial_hash=False)

        desired_scale = 0.5

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

        # Add animated grass to floating platform tiles collected earlier
        for (px, py) in platform_tile_positions:
            index = int(px // 64) #tells how many grass tiles can fit on a platform
            textures = grass_animation_1 if index % 2 == 0 else grass_animation_2
            grass = AnimatedTile(textures)
            grass.center_x = px
            grass.center_y = py + (grass.height) / 2 + 6.5
            grass.update_interval = .5
            self.scene.add_sprite("Foreground", grass)


        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite, walls=self.scene["Walls"], gravity_constant = GRAVITY
        )
    
    #methods for image alterations
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
        self.clear()
        self.camera.use()

        self.scene.draw()

        self.gui_camera.use()
        self.score_text.draw()
        #enable to show coordinates (along with section in setup)
        #self.coord_text.draw()
        #self.instruction_text.draw()

        #for bear textbox
        if self.show_npc_text:
            screen_width, screen_height = self.get_size()
            self.textbox_sprite.center_x = screen_width / 2
            self.textbox_sprite.bottom = 20
            self.textbox_list.draw()

            arcade.draw_text(self.npc_text,
                             self.textbox_sprite.left + 10,
                             self.textbox_sprite.center_y - 30,
                             color=arcade.color.BLACK,
                             font_size = self.npc_font_size,
                             font_name="Pixelated Elegance",
                             width=self.textbox_sprite.width -20,
                             align="center")
            #bears name tag
            arcade.draw_text(self.name_text,
                             self.textbox_sprite.left + 70,
                             self.textbox_sprite.center_y + 62,
                             color= arcade.color.BLACK,
                             font_size = 19,
                             width = self.textbox_sprite.width-20,
                             font_name = "Pixelated Elegance",
                             align = "left")

            option_y = self.textbox_sprite.top + 10
            for i, option in enumerate(self.npc_options):
                # changes color and font size for the selected dialogue option
                if i == self.selected_option:
                    color = arcade.color.RED
                    font_size = 16
                else:
                    color = arcade.color.BLACK
                    font_size = 14

                arcade.draw_text(
                    f"{i+1}. {option}",
                    self.textbox_sprite.right - 300,
                    option_y + i * 20,
                    color = color,
                    font_size= font_size,
                    font_name = "Pixelated Elegance"
                )
        
        if self.show_end_screen:
            screen_w, screen_h = self.get_size()

            arcade.draw_lrbt_rectangle_filled(0,screen_w,1,screen_h, (0,0,0,180))

            arcade.draw_text(
                "Delivery Complete!",
                screen_w / 2,
                screen_h / 2 + 50,
                color = arcade.color.WHITE,
                font_size=36,
                font_name="Pixelated Elegance",
                anchor_x="center"
            )
            arcade.draw_text(
                f"Final Score: {self.score}",
                screen_w / 2 - 160,
                screen_h / 2 -10,
                color=arcade.color.WHITE,
                font_size = 24,
                font_name="Pixelated Elegance",
                anchor_y = "center"
            )
            arcade.draw_text(
                "Press ESC to quit",
                screen_w / 2,
                screen_h / 2 - 80,
                color=arcade.color.LIGHT_GRAY,
                font_size=16,
                font_name = "Pixelated Elegance",
                anchor_x="center"
            )

    
    # from better keyboard controls
    def update_player_speed(self):

        if not self.in_dialogue:
            self.player_sprite.change_x = 0

            if self.left_pressed and not self.right_pressed:
                self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
                self.player_sprite.facing_direction = 1
                self.push_rocks(-PLAYER_MOVEMENT_SPEED)
            elif self.right_pressed and not self.left_pressed:
                self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
                self.player_sprite.facing_direction = 0
                self.push_rocks(PLAYER_MOVEMENT_SPEED)
        
            half_width = self.player_sprite.width / 2
            if self.player_sprite.center_x < half_width:
                self.player_sprite.center_x = half_width
            elif self.player_sprite.center_x > WORLD_WIDTH - half_width:
                self.player_sprite.center_x = WORLD_WIDTH - half_width
        else: 
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0


    def push_rocks(self, amount):
        left, right, bottom, top = self.player_front_hitbox()
        #now just for the boxes!
        for rock in self.rocks:
            # Check if nose overlaps rock
            if right > rock.left and left < rock.right and top > rock.bottom and bottom < rock.top:
                rock.center_x += amount

                # Don't let rocks move into walls
                if arcade.check_for_collision_with_list(rock, self.scene["Walls"]):
                    rock.center_x -= amount

                # Don't let rocks move into other rocks
                for other_rock in self.rocks:
                    if other_rock == rock:
                        continue
                    if rock.collides_with_sprite(other_rock):
                        rock.center_x -= amount
                        break

    
    def is_on_ground(self):
        # Slightly below the player to detect ground
        epsilon = 2

        # Walls
        for wall in self.scene["Walls"]:
            if (self.player_sprite.bottom - epsilon <= wall.top and
                self.player_sprite.bottom >= wall.top - 5 and
                self.player_sprite.right > wall.left and
                self.player_sprite.left < wall.right):
                return True

        # Rocks
        for rock in self.rocks:
            if (self.player_sprite.bottom - epsilon <= rock.top and
                self.player_sprite.bottom >= rock.top - 5 and
                self.player_sprite.right > rock.left and
                self.player_sprite.left < rock.right):
                return True

        return False
    

    def player_front_hitbox(self):
        nose_width = 5  # pixels wide
        # Extend the nose vertically to cover the whole player
        bottom = self.player_sprite.bottom
        top = self.player_sprite.top
        if self.player_sprite.facing_direction == 0:  # right
            left = self.player_sprite.right
        else:  # left
            left = self.player_sprite.left - nose_width
        right = left + nose_width
        return left, right, bottom, top
        
    def on_key_press(self, key, modifiers):
        if self.in_dialogue:
        
            if self.dialogue_waiting_close:
                if key == arcade.key.ENTER or key == arcade.key.E:
                    # If there are follow-up lines, advance to the next one.
                    if self.dialogue_followups:
                        self.npc_text = self.dialogue_followups.pop(0)
                        # If followups are exhausted now, check whether we
                        # should show the end screen (trigger set by a Yes
                        # response).
                        if not self.dialogue_followups:
                            if self.trigger_end_on_followups:
                                # Show end screen overlay and stop dialogue
                                self.show_end_screen = True
                                self.show_npc_text = False
                                self.in_dialogue = False
                                self.dialogue_waiting_close = False
                                self.trigger_end_on_followups = False
                    else:
                        # No follow-ups: close the dialogue.
                        self.in_dialogue = False
                        self.show_npc_text = False
                        self.dialogue_waiting_close = False
                return

            #controls for dialogue selection
            if len(self.npc_options) > 0:
                if key == arcade.key.UP:
                    self.selected_option = (self.selected_option + 1) % len(self.npc_options)
                elif key == arcade.key.DOWN:
                    self.selected_option = (self.selected_option - 1) % len(self.npc_options)
                elif key == arcade.key.ENTER or key == arcade.key.E:
                    chosen = self.npc_options[self.selected_option]

                    #dialogue options
                    lowered = chosen.lower()
                    if "not yet" in lowered:
                        self.npc_text = "Oh, alright. Come back when you find them."
                        self.npc_font_size = 20
                        self.npc_options = []
                        self.selected_option = 0
                        self.dialogue_followups = []
                        self.dialogue_waiting_close = True
                    elif "yes, here they are" in lowered:
                        # First reply
                        self.npc_text = "Thanks."
                        self.npc_font_size = 20
                        #once the player presses e or enter, it displays new text
                        self.dialogue_followups = ["No, idea what I'm going to do with them."]
                        self.npc_options = []
                        self.selected_option = 0
                        self.dialogue_waiting_close = True
                        self.trigger_end_on_followups = True
                    else:
                        #the other option is leave, so it is fine as it is
                        self.in_dialogue = False
                        self.show_npc_text = False
        else:

            if key == arcade.key.UP or key == arcade.key.W:
                if self.is_on_ground():
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
            elif key == arcade.key.E or key == arcade.key.ENTER:
                for npc in self.scene["NPCs"]:
                    bear = self.scene["NPCs"][0]
                    dist = arcade.get_distance_between_sprites(self.player_sprite, bear)
                    if dist < 300:
                        self.show_npc_text = True
                        # allows for variable font size
                        self.npc_font_size = 30
                        self.npc_text = "Do you have all my letters?"
                        self.name_text = "Bear"
                        self.npc_options = ["Yes, here they are", "Not Yet", "Leave"]
                        self.selected_option = 0
                        # Enter dialogue mode: stop the player's movement and
                        # clear any movement keys so arrow keys control the
                        # dialogue selection instead of moving the character.
                        self.in_dialogue = True
                        self.left_pressed = False
                        self.right_pressed = False
                        self.down_pressed = False
                        self.player_sprite.change_x = 0
                        self.player_sprite.change_y = 0
                        self.update_player_speed()
                        break
        if self.show_end_screen and key==arcade.key.ESCAPE:
            arcade.exit()



    def on_key_release(self, key, modifiers):

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


        self.player_sprite.center_y += self.player_sprite.change_y

        #for rock gravity
        for rock in self.rock_list:
            rock.change_y -= GRAVITY
            rock.center_y += rock.change_y

            walls_hit = arcade.check_for_collision_with_list(rock, self.scene["Walls"])
            for wall in walls_hit:
                if rock.change_y < 0:  # falling
                    rock.bottom = wall.top
                    rock.change_y = 0
                elif rock.change_y > 0:  # moving up
                    rock.top = wall.bottom
                    rock.change_y = 0

            # Collision with other rocks
            for other_rock in self.rock_list:
                if other_rock == rock:
                    continue
                if rock.collides_with_sprite(other_rock):
                    # Simple resolution: move back
                    rock.center_y = other_rock.top
                    rock.change_y = 0

        for grass in self.scene["Foreground"]:
            grass.update_animation(delta_time)

        for mail in self.scene["Mail"]:
            mail.update_animation(delta_time)

        for npc in self.scene["NPCs"]:
            npc.update_animation(delta_time)

        mail_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Mail"]
        )

        for mail in mail_hit_list:
            mail.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 75
            self.score_text.text = f"Score: {self.score}"
        #for debug. Other parts are in draw and setup
        #self.coord_text.text = f"X: {int(self.player_sprite.center_x)}, Y: {int(self.player_sprite.center_y)}"

        #collision with walls and rocks
        walls_hit = arcade.check_for_collision_with_list(self.player_sprite, self.scene["Walls"])
        for wall in walls_hit:
            if self.player_sprite.change_y < 0:  # falling
                self.player_sprite.bottom = wall.top
                self.player_sprite.change_y = 0
            elif self.player_sprite.change_y > 0:  # jumping
                self.player_sprite.top = wall.bottom
                self.player_sprite.change_y = 0

        for rock in self.rocks:
            if self.player_sprite.collides_with_sprite(rock):
                if self.player_sprite.change_y < 0:  # falling
                    self.player_sprite.bottom = rock.top
                    self.player_sprite.change_y = 0
                elif self.player_sprite.change_y > 0:  # jumping
                    self.player_sprite.top = rock.bottom
                    self.player_sprite.change_y = 0
        
        
        self.player_sprite.change_y -= GRAVITY

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

# for animating things that are not sprites, and do not work with animatedwalkingsprite, like the grass, mail, and bear
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