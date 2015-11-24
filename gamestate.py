"""
Tic Tac Toe game definition

Defines a Tic Tac Toe game state object with an associated transition function,
a legal moves function, a move function, and a terminal state detector.
Includes unit tests to verify proper functionality.
"""


class GameState(object):
    """
    Represents a Tic Tac Toe game.
    The state consists of a 3x3 game board with each position occupied by:
      ' ' (empty square)
      'X' (X mark)
      'O' (O mark)
    as well as the following terminal states:
      X won
      O won
      Tie
    """
    def __init__(self):
        # Begin with an empty game board
        # self.board = ['   ',
        #               '   ',
        #               '   ']
        self.board = [[' ', ' ', ' '],
                      [' ', ' ', ' '],
                      [' ', ' ', ' ']]
        # The first player is 'X'
        self.turn = 'X'
        # # Terminal state indicator, can be either of: 'X', 'O' or None to
        # # indicate if the game has been won
        # self.terminal = None

    def __str__(self):
        """
        Returns a string that is a visual representation of the game
        state. Can be used to print the current game state of a game:
          print(game.state)
        will print a game board:
           |X|
          -----
          O| |
          -----
           | |X

        """
        output = ''
        for row in range(3):
            for col in range(3):
                contents = self.board[row][col]
                if col < 2:
                    output += '{}|'.format(contents)
                else:
                    output += '{}\n'.format(contents)
            if row < 2:
                output += '-----\n'

        output += 'Winner: {}'.format(self.winner())

        return output

    def move(self, row, col):
        """
        Places a marker at the position (row, col). The marker placed is
        determined by whose turn it is, either 'X' or 'O'.
        """
        self.board[row][col] = self.turn

        # # Check if it results in a terminal state
        # self.terminal = self.winner()

        self._advance_turn()

    def _advance_turn(self):
        """
        Marks the current player's turn as over and keeps track of whose turn
        is next
        """
        if self.turn == 'X':
            self.turn = 'O'
        else:
            self.turn = 'X'

    def legal_moves(self):
        """
        Returns a list of the legal actions from the current state,
        where an action is the placement of a marker 'X' or 'O' on a board
        position, represented as a (row, col) tuple, for example:
          [(2, 1), (0, 0)]
        would indicate that the positions (2, 1) and (0, 0) are available to
        place a marker on. If the game is in a terminal state, returns an
        empty list.
        """
        # Check if terminal state
        if self.winner() is not None:
            return []

        possible_moves = []
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == ' ':
                    possible_moves.append((row, col))
        return possible_moves

    def transition_function(self, row, col):
        """
        Applies the specified action to the current state and returns the new
        state that would result. Can be used to simulate the effect of
        different actions. The action is applied to the player whose turn
        it currently is.

        :param state: The starting state before applying the action
        :param row: The row in which to place a marker
        :param col: The column in which to place a marker
        :return: The resulting new state that would occur
        """
        # Verify that the specified action is legal
        assert (row, col) in self.legal_moves()

        # First, make a copy of the current state
        new_state = GameState()
        new_state.board = self.board
        new_state.turn = self.turn
        # Then, apply the action to produce the new state
        new_state.move(row, col)

    def winner(self):
        """
        Checks if the game state is a terminal state.
        :return: If it is not, returns None; if it is, returns 'X' or 'O'
        indicating who is the winner; if it is a tie, returns 'Tie'
        """
        for player in ['X', 'O']:
            # Check for winning horizontal lines
            for row in range(3):
                accum = 0
                for col in range(3):
                    if self.board[row][col] == player:
                        accum += 1
                if accum == 3:
                    return player

            # Check for winning vertical lines
            for col in range(3):
                accum = 0
                for row in range(3):
                    if self.board[row][col] == player:
                        accum += 1
                if accum == 3:
                    return player

            # Check for winning diagonal lines (there are 2 possibilities)
            option1 = [self.board[0][0],
                       self.board[1][1],
                       self.board[2][2]]
            option2 = [self.board[2][0],
                       self.board[1][1],
                       self.board[0][2]]
            if all(marker == player for marker in option1) \
                    or all(marker == player for marker in option2):
                return player

        # Check for ties, defined as a board arrangement in which there are no
        # open board positions left and there are no winners (note that the
        # tie is not being detected ahead of time, as could potentially be
        # done)
        accum = 0
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == ' ':
                    accum += 1
        if accum == 0:
            return 'Tie'

        return None


import unittest


class TestGamePlay(unittest.TestCase):
    def test_play(self):
        """
        Plays three different games and verifies that the game accurately
        models the state transitions, winners and board information for them
        """

        game = GameState()

        assert str(game) == (" | | \n"
                             "-----\n"
                             " | | \n"
                             "-----\n"
                             " | | \n"
                             "Winner: None")

        assert game.legal_moves() == [(0, 0), (0, 1), (0, 2),
                                      (1, 0), (1, 1), (1, 2),
                                      (2, 0), (2, 1), (2, 2)]

        # Opening game
        game.move(1, 1)  # X
        game.move(0, 2)  # O
        game.move(1, 2)  # X
        game.move(1, 0)  # O
        game.move(2, 1)  # X

        assert str(game) == (" | |O\n"
                             "-----\n"
                             "O|X|X\n"
                             "-----\n"
                             " |X| \n"
                             "Winner: None")

        # Keep track of the current game state so we can some alternate end
        # games from this point later
        import copy
        game_copy1 = copy.deepcopy(game)
        game_copy2 = copy.deepcopy(game)

        # End game #1
        game.move(0, 0)  # O
        game.move(0, 1)  # X plays a winning horizontal line

        assert game.winner() == 'X'

        # End game #2
        game_copy1.move(0, 0)  # O
        game_copy1.move(2, 2)  # X
        game_copy1.move(2, 0)  # O plays a winning vertical line

        assert game_copy1.winner() == 'O'
        assert not game_copy1.legal_moves()

        # End game #3
        game_copy2.move(2, 2)  # O
        game_copy2.move(0, 0)  # X
        game_copy2.move(0, 1)  # O
        game_copy2.move(2, 0)  # X
        assert game_copy2.winner() == 'Tie'
        assert str(game_copy2) == ("X|O|O\n"
                                   "-----\n"
                                   "O|X|X\n"
                                   "-----\n"
                                   "X|X|O\n"
                                   "Winner: Tie")


if __name__ == '__main__':
    unittest.main()
