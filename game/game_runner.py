import logging
from typing import List, Optional,Union

from game.codenames import Codenames, Phase
from game.observation import SpymasterObservation, GuesserObservation
from players.interfaces.guesser import Guesser
from players.interfaces.spymaster import SpyMaster
from utils.game_logger import GameLogger

logger = logging.getLogger("GameRunner")

class GameRunner:
    C_GREEN = '\033[92m'
    C_RED = '\033[91m'
    C_GRAY = '\033[90m'
    C_WHITE = '\033[97m'
    C_RESET = '\033[0m'
    C_BG_REVEALED = '\033[40m'

    def __init__(self, spymaster: SpyMaster,guesser: Guesser, game: Codenames, render: bool = True, game_logger: Optional[GameLogger] = None):
        self.game = game
        self.spymaster = spymaster
        self.guesser = guesser
        self.render = render
        self.eval_logger = game_logger

        if self.eval_logger:
            self.eval_logger.set_initial_board(self.game.board)

    def _draw_board(self, observation: Union[SpymasterObservation,GuesserObservation], is_spymaster: bool):
        if not self.render:
            return
        logger.info("\n" + "="*60)
        logger.info(" PLANSZA ".center(60, "="))
        logger.info("=" * 60)
        board = observation.board
        for i in range(0, 25, 5):
            row = board[i:i + 5]
            row_str = ""
            for card in row:
                word = card.word.center(11)
                ctype = card.type
                revealed = card.revealed
                color = self.C_WHITE
                bg = self.C_BG_REVEALED if revealed else ""
                if ctype == "TARGET": color = self.C_GREEN
                elif ctype == "NEUTRAL": color = self.C_GRAY
                elif ctype == "ASSASSIN": color = self.C_RED
                elif ctype == "UNKNOWN": color = self.C_WHITE

                marker = "[X]" if revealed else "   "
                if revealed and not is_spymaster:
                    if card.type == "TARGET": color = self.C_GREEN
                    elif card.type == "ASSASSIN": color = self.C_RED
                    else: color = self.C_GRAY
                row_str += f"{color}{bg}{marker}{word}{self.C_RESET} | "
            logger.info(row_str)
        logger.info("=" * 60)

    def run(self):
        MAX_ERRORS = 3
        consecutive_errors = 0
        b_id = f"[Board ID: {self.eval_logger.board_id}]" if self.eval_logger else "[Single Game]"
        while self.game.phase != Phase.GAME_OVER:
            if consecutive_errors >= MAX_ERRORS:
                logger.error(f"{b_id} [!] Bot disqualified after {MAX_ERRORS} invalid attempts in a row.")
                print(f"{self.C_RED}Game terminated due to repeated AI errors.{self.C_RESET}")
                self.game.is_victory = False
                self.game.phase = Phase.GAME_OVER
                break
            if self.game.phase == Phase.GIVING_CLUE:
                obs = self.game.get_observation_for_spymaster()
                if self.render:
                    self._draw_board(obs, True)
                clue, count = self.spymaster.get_clue(obs)
                success, message = self.game.give_clue(clue, count)
                if success:
                    consecutive_errors = 0
                    logger.info(f"Spymaster gave clue: ({clue} ,{count})")
                    if self.eval_logger:
                        self.eval_logger.log_clue(clue, count)
                else:
                    consecutive_errors += 1
                    logger.warning(f"{b_id} Error: {message}")
                    if self.render:
                        logger.info(f"{self.C_RED}Invalid clue: {message} Please try again.{self.C_RESET}")
            elif self.game.phase == Phase.GUESSING:
                obs = self.game.get_observation_for_guesser()
                if self.render:
                    self._draw_board(obs, False)
                guess = self.guesser.get_guess(obs)
                if guess.upper() == "PASS":
                    self.game.end_guessing_early()
                    logger.info("Passing turn...")
                    if self.eval_logger:
                        self.eval_logger.log_guess("PASS","PASS")
                else:
                    success, message = self.game.guess(guess)
                    if not success:
                        consecutive_errors += 1
                        logger.warning(f"{b_id} [!] INVALID GUESS ATTEMPT: '{guess}' - {message}")
                        if self.render:
                            logger.info(f"{self.C_RED}Invalid guess: {message} Please try again.{self.C_RESET}")

                    else:
                        consecutive_errors = 0
                        logger.info(f"Guess: {guess} - {message}")
                        card_type = next((c.card_type.value for c in self.game.board if c.word == guess), "UNKNOWN")
                        if self.eval_logger:
                            self.eval_logger.log_guess(guess, card_type)
        logger.info(f"Game over!")
        if self.game.is_victory:
            logger.info(f"You won in {self.game.turn_taken} turns!")
        else:
            logger.info(f"You lost in {self.game.turn_taken} turns!")
        if self.eval_logger:
            self.eval_logger.finalize_game(self.game)
