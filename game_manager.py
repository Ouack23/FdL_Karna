import logging, os, sys
import games
from games.game import Game
from games.simon import Simon

def get_games():
    game_list = []
    ignore_list = ["__init__.py", "game.py"]

    for tmp in os.listdir("./games"):
        if tmp.endswith(".py"):
            try:
                ignore_list.index(tmp)
            except ValueError:
                tmp = tmp.rstrip(".py").title()
                game_list.append(tmp)
                logging.debug("Adding " + tmp + " to game list")

    return game_list


class GameManager(object):
    def __init__(self):
        self.game_list = get_games()
        self.current_game = Game("Simon")
        self.current_game_name = str(self.current_game)
        logging.debug("Setting default game to " + self.current_game_name)

    def change_game(self, new_game):
        if self.check_game(new_game):
            self.current_game = self.str_to_class(new_game)
            self.current_game_name = str(new_game)
            logging.info("Successfully changed current game to " + self.current_game_name)
        else:
            logging.error("Cannot change current game to " + new_game)

    def run_game(self):
        self.current_game.run()

    def check_game(self, game_name):
        try:
            self.game_list.index(game_name)
            logging.debug("Game " + game_name + " is in folder games/ !")
            return True
        except ValueError:
            logging.error("Game " + game_name + " is not in folder games/ !")
            return False

    def str_to_class(self, string):
        if self.check_game(string):
            cmd = string.title() + "()"
            result = eval(cmd)
            logging.debug("STR_TO_CLASS result : " + str(result))
            return result