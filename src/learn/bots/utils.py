"""Utils

The multiple bots here are just all combinations of input and output type
presented in the markdown. It therefore makes sense to define the
generation of those data formats here, as they will be shared accross
multiple bots.
"""
import numpy as np
from scipy import ndimage
from keras.utils import to_categorical

from src.play.model.Game import BLACK, WHITE, EMPTY


def separate_data(data):
    """Given the output of the SQL call separate that array into it's parts"""
    results = data[:, -1]
    ids = data[:, 0]
    colors = data[:, 1].astype(int)[:, None]
    moves = data[:, 2].astype(int)[:, None]
    boards = data[:, 3:-1].astype(np.float64)
    out = {'results': results,
           'ids': ids,
           'colors': colors,
           'moves': moves,
           'boards': boards}
    return out


def value_output(results):
    r = np.chararray(results.shape)
    r[:] = results[:]
    black_wins = r.lower().startswith(b'b')[:, None]
    white_wins = r.lower().startswith(b'w')[:, None]
    # draws = results.lower().startswith('D')
    out = np.concatenate((black_wins, white_wins), axis=1)
    return out


def policy_output(moves):
    moves[moves==-1] = 81
    out = to_categorical(moves)
    assert out.shape[1] == 82
    assert (out.sum(axis=1) == 1).all()

    return out


def simple_board(boards):
    """Generate the simplest board encoding

    The board will be encoded into a 81-vector, with -1, 0, 1 values.
    The boards are actually already given in this format
    """
    return boards


def encode_board(boards, colors):
    """Generate a categorical board encoding

    The board will be encoded into a 3*81-vector.
    Each of those 81-vectors basically stand for a True/False-encoding for
    player, opponent, and "empty".
    """
    player_board = np.where(
        colors==WHITE,
        boards==WHITE,
        boards==BLACK)
    opponent_board = np.where(
        colors==WHITE,
        boards==BLACK,
        boards==WHITE)
    empty_board = (boards==EMPTY)

    def normalize(board):
        return (board * 3 - 1)/np.sqrt(2)

    out = np.concatenate(
        (normalize(player_board),
         normalize(opponent_board),
         normalize(empty_board)),
        axis=1)

    return out


def get_liberties(binary_board, empty_board):
    """Generate Liberties

    In goes a binary board with the stones of one of the player.
    Out comes a board with the liberties encoded as scalar.
    """
    groups = ndimage.label(binary_board)
    liberties = np.array([[0]*9]*9)
    for label in range(1, groups[1]+1):
        b = groups[0]==label
        dilated = ndimage.binary_dilation(b)
        libs = dilated & empty_board
        n_libs = libs.sum()
        liberties[b] = n_libs
    return liberties


def liberties_to_planes(liberties, n=4):
    """Reformat liberties to a more categorical encoding

    In goes the board with the liberties
    Out come multiple boards with binary values
    """
    out = []
    for i in range(n-1):
        out.append(liberties==(i+1))
    out.append(liberties>=n)
    out = np.stack(out)
    return out


def get_liberties_vectorized(flat_boards, color):
    """This uses multiple boards as input and outputs the liberties!"""
    data = np.append(flat_boards, color, axis=1)

    def foo(data):
        flat_board, color = data[:-1], data[-1]
        board = flat_board.reshape((9, 9))
        liberties = get_liberties(board==color, board==EMPTY)
        return liberties

    liberties = np.apply_along_axis(foo, 1, data)
    planes = np.apply_along_axis(liberties_to_planes, 1, liberties)
    planes = planes.reshape((flat_boards.shape[0], 4*81))
    return planes
