import random
import arcade

WIDTH = 800
HEIGHT = 600
TITLE = "SPACE SHOOTER"

PLAYER_IMAGE = ":resources:images/space_shooter/playerShip1_orange.png"
ENEMY_IMAGE = ":resources:images/space_shooter/playerShip2_orange.png"
BULLET_IMAGE = ":resources:images/space_shooter/laserBlue01.png"
MENU_OPTIONS = ["Play", "How to Play", "Quit"]
MENU = "menu"
HOW_TO_PLAY = "how to play"
GAME = "game"
GAME_OVER = "game over"
PAUSED = "paused"

ENEMY_SPAWN_SECONDS = 1.5

class HUD:

    def __init__(self):
        self.score_text = arcade.Text("Score = 0", 20, HEIGHT - 40, arcade.color.WHITE, 20)
        self.wave_text = arcade.Text("Wave: 1", WIDTH / 2, HEIGHT - 40, arcade.color.WHITE, 20, anchor_x="center")
        self.best_text = arcade.Text("Best: 0", WIDTH - 20, HEIGHT - 40, arcade.color.GOLD, 20, anchor_x="right")
        self.lives = 3

    def update(self, score, wave, best, lives):
        self.score_text.text = f"Score: {score}"
        self.wave_text.text = f"Wave: {wave}"
        self.best_text.text = f"Best: {best}"
        self.lives = lives

    def draw(self):
        self.score_text.draw()
        self.wave_text.draw()
        self.best_text.draw()
        self.draw_lives()

    def draw_lives(self):
        for i in range(self.lives):
            x = WIDTH - 35 - i * 30
            y = 20
            arcade.draw_triangle_filled(x, y + 12, x - 12, y - 10, x + 12, y - 10, arcade.color.SKY_BLUE)

class Bullet(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__(BULLET_IMAGE, scale=0.8)
        self.center_x = x
        self.center_y = y
        self.change_y = 5

    def update(self, delta_time=1 / 60):
        super().update()
        if self.top > HEIGHT:
            self.remove_from_sprite_lists()


class Player(arcade.Sprite):

    def __init__(self):
        super().__init__(PLAYER_IMAGE, scale=0.5)
        self.center_x = WIDTH / 2
        self.center_y = 60
        self.speed = 5
        self.shot_timer = 0.0

    def recharge(self, delta_time):
        self.shot_timer += delta_time

    def shoot(self):
        if self.shot_timer < 0.25:
            return None
        self.shot_timer = 0.0
        return Bullet(self.center_x, self.top)

    def update(self, delta_time=1 / 60):
        super().update()
        if self.left < 0:
            self.left = 0
        if self.right > WIDTH:
            self.right = WIDTH

class Enemy(arcade.Sprite):

    def __init__(self, target):
        super().__init__(ENEMY_IMAGE, scale=0.4)
        self.target = target
        self.speed = random.uniform(1.5, 3.0)
        self.center_x = random.randint(0, HEIGHT)
        self.bottom = HEIGHT + 20
        self.change_y = -self.speed

    def update(self, delta_time=1 /60):
        self.change_x = (self.target.center_x - self.center_x) * 0.02
        self.change_y = -self.speed
        super().update()
        if self.bottom < 0:
            self.remove_from_sprite_lists()


class Menu(arcade.View):
    def __init__(self):
        super().__init__()
        self.state = MENU
        self.background_color = arcade.color.BLACK
        self.selected = 0
        self.title_text = arcade.Text("SPACE SHOOTER", WIDTH / 2, 430,
                                      arcade.color.SKY_BLUE, 54, anchor_x="center",
                                      bold=True)
        self.best_text = arcade.Text("", WIDTH / 2, 80, arcade.color.GOLD, 18,
                                     anchor_x="center")
        self.option_texts = []
        for i, option in enumerate(MENU_OPTIONS):
            y = 300 - i * 60
            self.option_texts.append(arcade.Text(option, WIDTH / 2, y,
                                                 arcade.color.WHITE, 28,
                                                 anchor_x="center"))

    def on_draw(self):
        self.clear()
        self.title_text.draw()
        for i, text in enumerate(self.option_texts):
            if i == self.selected:
                text.text = f"> {MENU_OPTIONS[i]} <"    # marker, not just color
                text.color = arcade.color.LAVENDER
            else:
                text.text = MENU_OPTIONS[i]
                text.color = arcade.color.BLUE
            text.draw()
        self.best_text.text = f"Best: {self.window.best_score}"
        self.best_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.DOWN:
            self.selected = (self.selected + 1) % len(MENU_OPTIONS)   # wrap around
        elif key == arcade.key.UP:
            self.selected = (self.selected - 1) % len(MENU_OPTIONS)
        elif key == arcade.key.ENTER:
            self.choose()

    def choose(self):
        choice = MENU_OPTIONS[self.selected]
        if choice == "Play":
            self.window.show_view(Game())
        elif choice == "How to Play":
            self.window.show_view(HowToPlay(self))   # remember the menu
        elif choice == "Quit":
            self.window.close()


class HowToPlay(arcade.View):
    def __init__(self, menu_view):
        super().__init__()
        self.state = HOW_TO_PLAY
        self.menu_view = menu_view              # where ESC goes back to
        self.background_color = arcade.color.BLACK
        self.lines = arcade.Text(
            "LEFT / RIGHT   move\nSPACE   shoot\nP   pause\n\n"
            "Shoot the falling ships. You have three lives.\n\nESC to go back",
            410, 400, arcade.color.GREEN, 22, anchor_x="center",
            multiline=True, width=600, align="left")

    def on_draw(self):
        self.clear()
        arcade.draw_lrbt_rectangle_filled(100, 700, 430, 500, arcade.color.BLUE)
        arcade.draw_line(100, 500, 100, 100, arcade.color.GRAY, 1)
        arcade.draw_line(100, 100, 700, 100, arcade.color.GRAY, 1)
        arcade.draw_line(700, 100, 700, 500, arcade.color.GRAY, 1)
        arcade.draw_line(700, 500, 100, 500, arcade.color.GRAY, 1)
        arcade.draw_text("HOW TO PLAY", 110, 450, arcade.color.GREEN, 40)
        self.lines.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.menu_view)   # same menu, same selection


class Game(arcade.View):
    def __init__(self):
        super().__init__()
        self.state = GAME
        self.background_color = arcade.color.BLACK
        self.player = None
        self.player_list = None
        self.enemy = None
        self.enemy_list = None
        self.bullet = None
        self.bullet_list = None
        self.spawn_timer = 0.0
        self.score = 0
        self.best = 0
        self.firing = False
        self.explosion_sound = arcade.load_sound(":resources:sounds/explosion1.wav")
        self.shooting_sound = arcade.load_sound(":resources:sounds/laser2.wav")
        self.setup()

    def setup(self):
        self.player = Player()
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.enemy = Enemy(self.player)
        self.enemy_list = arcade.SpriteList()
        self.enemy_list.append(self.enemy)
        self.bullet = Bullet(self.player.center_x, self.player.top)
        self.bullet_list = arcade.SpriteList()
        self.bullet_list.append(self.bullet)
        self.spawn_timer = 0.0
        self.firing = False
        self.wave = 1
        self.lives = 3
        self.hud = HUD()
        sheet = arcade.load_spritesheet(":resources"
                                        ":images/spritesheets/explosion.png")
        self.explosion_textures = sheet.get_texture_grid(size=(256, 256), columns=16, count=60)
        print("Explosion frames:", len(self.explosion_textures))
        self.explosion_list = arcade.SpriteList()
        self.explosion = None
        self.explosion_timer = 0
        self.explosion_frame = 0

    def on_draw(self):
        if self.player is None or self.hud is None:
            return
        self.clear()
        self.enemy_list.draw()
        self.bullet_list.draw()
        self.player_list.draw()
        self.hud.draw()
        self.explosion_list.draw()

        if self.state == PAUSED:
            arcade.draw_lrbt_rectangle_filled(100, 700, 430, 500, arcade.color.BLUE)
            arcade.draw_line(100, 500, 100, 100, arcade.color.GRAY, 1)
            arcade.draw_line(100, 100, 700, 100, arcade.color.GRAY, 1)
            arcade.draw_line(700, 100, 700, 500, arcade.color.GRAY, 1)
            arcade.draw_line(700, 500, 100, 500, arcade.color.GRAY, 1)
            arcade.draw_text("PAUSED", 110, 450, arcade.color.GREEN, 40)
            arcade.draw_text("C FOR CONTINUE", 110, 400, arcade.color.GREEN, 18)
            arcade.draw_text("M FOR MENU", 110, 350, arcade.color.GREEN, 18)

    def on_update(self, delta_time):
        if self.player is None:
            self.setup()
            return

        if self.state != GAME:
            return

        self.player.recharge(delta_time)
        if self.firing:
            bullet = self.player.shoot()
            if bullet:
                self.bullet_list.append(bullet)
                arcade.play_sound(self.shooting_sound)

        self.spawn_timer += delta_time
        if self.spawn_timer >= ENEMY_SPAWN_SECONDS:
            self.spawn_timer = 0.0
            self.enemy_list.append(Enemy(self.player))

        self.player_list.update()
        self.enemy_list.update()
        self.bullet_list.update()

        for enemy in arcade.check_for_collision_with_list(self.player, self.enemy_list):
            enemy.remove_from_sprite_lists()
            arcade.play_sound(self.explosion_sound)
            self.explosion = arcade.Sprite(
                self.explosion_textures[0],
                center_x=self.player.center_x,
                center_y=self.player.center_y,
            )
            self.explosion_list.clear()
            self.explosion_list.append(self.explosion)
            self.explosion_frame = 0
            self.explosion_timer = 0
            self.lives = self.lives - 1
            if self.lives == 0:
                self.window.show_view(GameOver(self.score))

        for self.bullet in self.bullet_list:
            hits = arcade.check_for_collision_with_list(self.bullet, self.enemy_list)
            for enemy in hits:
                enemy.remove_from_sprite_lists()
                self.score += 10

        if self.explosion is not None:
            self.explosion_timer += delta_time
            if self.explosion_timer > 0.02:
                self.explosion_timer = 0
                self.explosion_frame += 1
                if self.explosion_frame >= len(self.explosion_textures):
                    self.explosion.remove_from_sprite_lists()
                    self.explosion = None
                else:
                    self.explosion_texture = self.explosion_textures[self.explosion_frame]
        self.best = max(self.best, self.score)
        self.hud.update(self.score, self.wave, self.best, self.lives)

    def on_key_press(self, key, modifiers):
        if self.player is None:
            return
        if self.state == GAME:
            if key == arcade.key.LEFT:
                self.player.change_x = -self.player.speed
            elif key == arcade.key.RIGHT:
                self.player.change_x = self.player.speed
            if key == arcade.key.SPACE:
                self.firing = True
            if key == arcade.key.P:
                self.player.change_x = 0
                self.state = PAUSED
        elif self.state == PAUSED:
            if key == arcade.key.C:
                self.state = GAME
            elif key == arcade.key.M:
                self.state = MENU
                self.window.show_view(Menu())

    def on_key_release(self, key, modifiers):
        if self.player is None:
            return
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0
        if key == arcade.key.SPACE:
            self.firing = False

class GameOver(arcade.View):
    def __init__(self, score):
        super().__init__()
        self.background_color = arcade.color.BLACK_BEAN
        self.new_best = score > self.window.best_score
        self.window.best_score = max(self.window.best_score, score)
        headline = "NEW BEST!" if self.new_best else "GAME OVER"
        self.headline = arcade.Text(headline, WIDTH / 2, 380, arcade.color.GOLD, 48,
                                    anchor_x="center", bold=True)
        self.details = arcade.Text(f"Score: {score}     Best: {self.window.best_score}",
                                   WIDTH / 2, 300, arcade.color.WHITE, 24, anchor_x="center")
        self.keys = arcade.Text("R  play again        M  main menu", WIDTH / 2, 200,
                                arcade.color.LIGHT_GRAY, 20, anchor_x="center")

    def on_draw(self):
        self.clear()
        self.headline.draw()
        self.details.draw()
        self.keys.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.window.show_view(Game())        # restart = a NEW game
        elif key == arcade.key.M:
            self.window.show_view(Menu())


def main():
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    window.best_score = 0          # lives on the window, so every view can see it
    window.show_view(Menu())
    arcade.run()


if __name__ == "__main__":
    main()
