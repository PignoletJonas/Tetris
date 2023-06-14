import sys
import pygame
from pygame import mixer
from shape import *
from shape import get_random_shape

########
# INIT #
# :260

pg.init()

####################
# SOUNDS AND MUSIC #
####################

# mixer.music.load('background.wav')
# mixer.music.set_volume(0.2)
# mixer.music.play(-1)

# #rotate_sound = mixer.Sound('can_rotate.wav')
# #rotate_sound.set_volume(1)#

# #tilt_rotate_sound = mixer.Sound('tilt_rotate.wav')
# tilt_rotate_sound.set_volume(1)

# speed_mode_sound = mixer.Sound('speed_mode.wav')
# speed_mode_sound.set_volume(1)


class GameMetaData(object):
    font_type = 'tetris_font.ttf'
    map_row_no = 20
    map_column_no = 10
    screen_width = map_column_no * 30 + 250
    screen_height = map_row_no * 30 + 100
    screen_center_width = int(screen_width / 2)
    screen_center_height = int(screen_height / 2)
    width_offset = 50
    height_offset = 50
    score_window_pos = 30 * map_column_no + width_offset + 30
    score_window_text_pos = 30 * map_column_no + width_offset + 50


class Scenes(object):
    titleScene = None
    gameScene = None
    active_scene = None


class State(object):
    level = 1
    score = 0
    full_line_no = 0

    @staticmethod
    def reset_new_game():
        State.score = 0
        State.full_line_no = 0
        State.level = 1


class SceneBase:
    def __init__(self):
        self.next = self
        self.score_font = pg.font.Font(GameMetaData.font_type, 18)
        self.full_line_font = pg.font.Font(GameMetaData.font_type, 18)
        self.level_font = pg.font.Font(GameMetaData.font_type, 18)
        self.next_font = pg.font.Font(GameMetaData.font_type, 16)

    def process_input(self, events):
        raise NotImplementedError(
            "Uh-oh, you didn't override this (process_input) in the child class")

    def update(self):
        raise NotImplementedError(
            "Uh-oh, you didn't override this (update) in the child class")

    def render(self, screen):
        raise NotImplementedError(
            "Uh-oh, you didn't override this (render) in the child class")

    def draw_score_area(self, main_screen):
        pg.draw.rect(main_screen, Colour.FIREBRICK.value,
                     (GameMetaData.score_window_pos, 50, 155, 85), 1)
        score_text = self.score_font.render(
            "Score: " + str(State.score), True, Colour.WHITE.value)
        full_line_text = self.full_line_font.render("Lines: " + str(State.full_line_no), True,
                                                    Colour.WHITE.value)
        level_text = self.level_font.render(
            "Level: " + str(State.level), True, Colour.WHITE.value)

        main_screen.blit(score_text, (GameMetaData.score_window_text_pos, 60))
        main_screen.blit(
            full_line_text, (GameMetaData.score_window_text_pos, 85))
        main_screen.blit(level_text, (GameMetaData.score_window_text_pos, 110))

        # Draw the next shape
        pg.draw.rect(main_screen, Colour.FIREBRICK.value,
                     (GameMetaData.score_window_pos, 140, 155, 80), 1)
        next_text = self.next_font.render('Next: ', True, Colour.WHITE.value)
        main_screen.blit(
            next_text, (GameMetaData.score_window_text_pos - 15, 145))

    @staticmethod
    def draw_area_grid(main_screen):
        for row_no in range(0, GameMetaData.map_row_no + 1):
            pg.draw.line(main_screen, Colour.LIGHT_BLUE.value, (GameMetaData.width_offset, 50 + (row_no * 30)),
                         (30 * GameMetaData.map_column_no + GameMetaData.width_offset, 50 + (row_no * 30)), 1)
            if row_no < GameMetaData.map_column_no + 1:
                pg.draw.line(main_screen, Colour.LIGHT_BLUE.value, (GameMetaData.width_offset + (row_no * 30),
                                                                    GameMetaData.height_offset),
                             (GameMetaData.width_offset + (row_no * 30),
                              30 * GameMetaData.map_row_no + GameMetaData.height_offset))

    def switch_to_scene(self, next_scene):
        self.next = next_scene


class TitleScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self._is_continue = False
        self._is_game_over = False
        self.options = 0 if self.is_continue else 1
        self.default = Colour.WHITE.value
        self.selected = Colour.RED.value
        self.continue_font = pygame.font.Font(GameMetaData.font_type, 36)
        self.new_game_font = pygame.font.Font(GameMetaData.font_type, 36)
        self.options_font = pygame.font.Font(GameMetaData.font_type, 36)
        self.exit_game_font = pygame.font.Font(GameMetaData.font_type, 36)

    @property
    def is_continue(self):
        return self._is_continue

    @is_continue.setter
    def is_continue(self, is_continue):
        self._is_continue = is_continue
        self.options = 0

    @property
    def is_game_over(self):
        return self._is_game_over

    @is_game_over.setter
    def is_game_over(self, is_game_over):
        self._is_game_over = is_game_over
        self._is_continue = False
        self.options = 1

    def process_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.options += 1
                    if self.options > 3:
                        self.options = 0 if self.is_continue else 1
                if event.key == pygame.K_UP:
                    self.options -= 1
                    lower_limit = 0 if self.is_continue else 1
                    if self.options < lower_limit:
                        self.options = 3
                if event.key == pygame.K_ESCAPE:
                    if self.is_continue:
                        Scenes.active_scene = Scenes.gameScene
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if self.options == 0:  # Continue
                        Scenes.active_scene = Scenes.gameScene
                    if self.options == 1:  # New Game
                        self._is_game_over = False
                        State.reset_new_game()
                        Scenes.gameScene = GameScene()
                        Scenes.active_scene = Scenes.gameScene
                    if self.options == 2:  # Options
                        Scenes.active_scene = OptionScene()
                    if self.options == 3:  # Quit
                        quit_game()
            if event.type == pygame.QUIT:
                quit_game()

    def update(self):
        pass

    def render(self, screen):

        if not self.is_game_over:
            screen.fill(Colour.BLACK.value)
            self.draw_score_area(screen)

        SceneBase.draw_area_grid(screen)
        new_game_text = self.new_game_font.render("NEW GAME", True,
                                                  self.selected if self.options == 1 else self.default)
        options_text = self.options_font.render("OPTIONS", True,
                                                self.selected if self.options == 2 else self.default)
        exit_game_text = self.exit_game_font.render("EXIT", True,
                                                    self.selected if self.options == 3 else self.default)

        menu_background = pygame.Rect((0, 0), (250, 250))
        menu_rect = options_text.get_rect(center=(GameMetaData.screen_center_width,
                                                  GameMetaData.screen_center_height))
        menu_offset = 25 if self.is_continue else 0
        menu_background.center = (menu_rect.width / 2 + menu_rect.x,
                                  (menu_rect.height / 2 + menu_rect.y) - menu_offset)
        pg.draw.rect(screen, Colour.BLACK.value, menu_background, 0)
        pg.draw.rect(screen, Colour.WHITE.value, menu_background, 1)

        if self.is_game_over:
            game_over_font = pg.font.Font(GameMetaData.font_type, 72)
            game_over_text = game_over_font.render(
                "GAME OVER", True, Colour.RED.value)
            screen.blit(game_over_text,
                        game_over_text.get_rect(center=(GameMetaData.screen_center_width,
                                                        GameMetaData.screen_center_height - 160)))

        if self.is_continue:
            continue_game_text = self.continue_font.render("CONTINUE", True,
                                                           self.selected if self.options == 0 else self.default)
            screen.blit(continue_game_text, continue_game_text.get_rect(center=(GameMetaData.screen_center_width,
                                                                                GameMetaData.screen_center_height - 100)))

        screen.blit(new_game_text, new_game_text.get_rect(center=(GameMetaData.screen_center_width,
                                                                  GameMetaData.screen_center_height - 50)))
        screen.blit(options_text, menu_rect)
        screen.blit(exit_game_text, exit_game_text.get_rect(center=(GameMetaData.screen_center_width,
                                                                    GameMetaData.screen_center_height + 50)))
        pygame.display.update()


class OptionScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self._is_continue = False
        self.difficulty = 0 if self.is_continue else 1
        self.default = Colour.WHITE.value
        self.selected = Colour.RED.value
        self.easy_font = pygame.font.Font(GameMetaData.font_type, 36)
        self.intermediate_font = pygame.font.Font(GameMetaData.font_type, 36)
        self.hard_font = pygame.font.Font(GameMetaData.font_type, 36)
        self.return_font = pygame.font.Font(GameMetaData.font_type, 36)
        self.continue_font = pygame.font.Font(GameMetaData.font_type, 36)

    @property
    def is_continue(self):
        return self._is_continue

    @is_continue.setter
    def is_continue(self, is_continue):
        self._is_continue = is_continue
        self.options = 0

    def process_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.difficulty += 1
                    if self.difficulty > 3:
                        self.difficulty = 0 if self.is_continue else 1
                if event.key == pygame.K_UP:
                    self.difficulty -= 1
                    lower_limit = 0 if self.is_continue else 1
                    if self.difficulty < lower_limit:
                        self.difficulty = 3
                if event.key == pygame.K_ESCAPE:
                    if self.is_continue:
                        Scenes.active_scene = Scenes.gameScene
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if self.difficulty == 0:  # CONTINUE
                        Scenes.active_scene = Scenes.gameScene
                    if self.difficulty == 1:  # EASY
                        pass
                        # Scenes.active_scene = Scenes.gameScene
                    if self.difficulty == 2:  # INTERMEDIATE
                        pass
                        # self._is_game_over = False
                        # State.reset_new_game()
                        # Scenes.gameScene = GameScene()
                        # Scenes.active_scene = Scenes.gameScene
                    if self.difficulty == 3:  # HARD
                        pass
            if event.type == pygame.QUIT:
                quit_game()

    def update(self):
        pass

    def render(self, screen):

        SceneBase.draw_area_grid(screen)
        difficulty_continue_text = self.continue_font.render("CONTINUE", True,
                                                             self.selected if self.difficulty == 0 else self.default)
        difficulty_easy_text = self.easy_font.render("EASY", True,
                                                     self.selected if self.difficulty == 1 else self.default)
        difficulty_intermediate_text = self.intermediate_font.render("INTERMEDIATE", True,
                                                                     self.selected if self.difficulty == 2 else self.default)
        difficulty_hard_text = self.hard_font.render("HARD", True,
                                                     self.selected if self.difficulty == 3 else self.default)

        menu_background = pygame.Rect((0, 0), (325, 325))
        menu_rect = difficulty_intermediate_text.get_rect(center=(GameMetaData.screen_center_width,
                                                          GameMetaData.screen_center_height))
        menu_offset = 25 if self.is_continue else 0
        menu_background.center = (menu_rect.width / 2 + menu_rect.x,
                                  (menu_rect.height / 2 + menu_rect.y) - menu_offset)
        pg.draw.rect(screen, Colour.BLACK.value, menu_background, 0)
        pg.draw.rect(screen, Colour.WHITE.value, menu_background, 1)

        screen.blit(difficulty_continue_text, difficulty_continue_text.get_rect(center=(GameMetaData.screen_center_width,
                                                                                        GameMetaData.screen_center_height - 150)))
        screen.blit(difficulty_easy_text, difficulty_easy_text.get_rect(center=(GameMetaData.screen_center_width,
                                                                                GameMetaData.screen_center_height - 25)))
        screen.blit(difficulty_intermediate_text, menu_rect)
        screen.blit(difficulty_hard_text, difficulty_hard_text.get_rect(center=(GameMetaData.screen_center_width,
                                                                                GameMetaData.screen_center_height + 150)))
        pygame.display.update()


class GameScene(SceneBase):
    def __init__(self):
        SceneBase.__init__(self)
        self.empty_line = []
        for i in range(GameMetaData.map_column_no):
            self.empty_line.append(0)
        self.tetris_map = [self.empty_line[:]
                           for _ in range(GameMetaData.map_row_no)]
        self.moving_object = [get_random_shape(GameMetaData.map_row_no, GameMetaData.map_column_no),
                              get_random_shape(GameMetaData.map_row_no, GameMetaData.map_column_no)]
        self.movement_fps = 0
        self.keyboard_speed = 0
        self.movement_speed = 50
        self.maximum_movement_speed = 5
        self.super_speed_mode = False
        self.game_over = False

    def process_input(self, events):
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == pg.QUIT:
                quit_game()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    Scenes.titleScene.is_continue = True
                    Scenes.active_scene = Scenes.titleScene
                if event.key == pg.K_LEFT:
                    self.keyboard_speed = -2
                    self.moving_object[0].move_left(self.tetris_map)
                if event.key == pg.K_RIGHT:
                    self.keyboard_speed = -2
                    self.moving_object[0].move_right(self.tetris_map)
                if event.key == pg.K_DOWN and not self.super_speed_mode:
                    self.keyboard_speed = -2
                    self.moving_object[0].move_down(self.tetris_map)
                    State.score += 2
                if event.key == pg.K_UP:
                    could_rotate = self.moving_object[0].rotate(
                        self.tetris_map)

                if event.key == pg.K_SPACE:
                    if not self.super_speed_mode:
                        self.super_speed_mode = True
                        # speed_mode_sound.play()
                        self.movement_speed = 1
                    else:
                        self.super_speed_mode = False
                        self.calculate_speed()

        if keys[pg.K_LEFT]:
            self.keyboard_speed += 1
            if self.keyboard_speed >= 4:
                self.keyboard_speed = 0
                self.moving_object[0].move_left(self.tetris_map)
        if keys[pg.K_RIGHT]:
            self.keyboard_speed += 1
            if self.keyboard_speed >= 4:
                self.keyboard_speed = 0
                self.moving_object[0].move_right(self.tetris_map)

    def update(self):
        self.movement_fps += 1
        if self.movement_fps >= self.movement_speed:
            self.movement_fps = 0
            self.move_object_down_or_game_over()

    def draw_next_shape(self, main_screen):
        self.moving_object[1].draw_next(
            main_screen, GameMetaData.score_window_text_pos - 20)

    def render(self, main_screen):
        main_screen.fill(Colour.BLACK.value)

        # Draw Scores
        self.draw_score_area(main_screen)
        # Draw next shape
        self.draw_next_shape(main_screen)
        # Draw the moving object to the Screen
        self.moving_object[0].draw(main_screen)
        # Draw the blocks that are occupied
        self.draw_used_blocks(main_screen)

        if self.game_over:
            GameScene.draw_game_over()

        pg.display.update()

    def draw_used_blocks(self, main_screen):
        for row_no, row in enumerate(self.tetris_map):
            for column_no, column_value in enumerate(row):
                if column_value != 0:
                    block_color = get_colour_by_number(column_value)
                    pg.draw.rect(main_screen, block_color.value, (50 +
                                 (column_no * 30), 50 + (row_no * 30), 30, 30), 2)
                    pg.draw.rect(main_screen, block_color.value, (50 + (column_no * 30) + 5, 50 + (row_no * 30) + 5, 21,
                                                                  21))
        SceneBase.draw_area_grid(main_screen)

    @staticmethod
    def draw_game_over():
        Scenes.titleScene.is_game_over = True
        Scenes.active_scene = Scenes.titleScene

    def calculate_speed(self):
        if State.level < 10:
            State.level = int(State.full_line_no / 10) + 1
            new_movement_speed = 50 - ((State.level - 1) * 5)
            if not self.super_speed_mode and self.movement_speed != new_movement_speed:
                self.movement_speed = new_movement_speed
        elif not self.super_speed_mode:
            self.movement_speed = self.maximum_movement_speed

    def move_object_down_or_game_over(self):
        if self.moving_object[0].is_finished_or_collided(self.tetris_map):
            self.movement_speed = 0
            is_game_over = False
            for block in self.moving_object[0].blocks:
                if block[0] == 0:
                    is_game_over = True
                self.tetris_map[block[0]][block[1]] = get_colour_number_by_name(
                    self.moving_object[0].colour.name)

            if not is_game_over:
                temp = []
                full_line = 0
                for row in list(reversed(self.tetris_map)):
                    if 0 not in row:
                        full_line += 1
                    else:
                        temp.append(row)

                if full_line > 0:
                    State.full_line_no += full_line
                    State.score += full_line * 100
                    for _ in range(full_line):
                        temp.append(self.empty_line[:])

                self.tetris_map = list(reversed(temp))
                self.moving_object.append(get_random_shape(
                    GameMetaData.map_row_no, GameMetaData.map_column_no))
                self.moving_object.pop(0)

            if self.super_speed_mode:
                self.super_speed_mode = False

            self.calculate_speed()

            self.game_over = is_game_over
        else:
            if self.super_speed_mode:
                State.score += 2
            self.moving_object[0].move_down(self.tetris_map)


def quit_game():
    pygame.quit()
    sys.exit()
