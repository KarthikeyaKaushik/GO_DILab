from src import Game, ConsoleView, TkinterPlotGuiView, PygameGuiView, HumanConsolePlayer, RandomBotPlayer, GameController
from src.utils.Utils import call_method_on_each


def main():
    
    game = Game()

    views = [
        ConsoleView(game),
        PygameGuiView(game)
    ]

    player1 = HumanConsolePlayer("PersonA", "w", game)
    player2 = RandomBotPlayer("RandomBot", "b", game)

    game_controller = GameController(game, views, player1, player2)
    call_method_on_each(views, "open", game_controller)
    game_controller.start()


if __name__ == '__main__':
    main()
