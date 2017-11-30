import os
import sgf
from os.path import dirname, abspath
import numpy as np
import string
from src.play.model.Board import Board


# expectation approx. 0, variance approx. 1
BLACK_VAL = -1.35
WHITE_VAL = 1.25
EMPTY_VAL = 0.25

# center of the board
CENTER = np.array([4,-4])

data_dir = os.path.join(dirname(dirname(dirname(dirname(abspath(__file__))))), 'data')
sgf_files = [
    os.path.join(data_dir, 'some_game.sgf'),
]

training_set_dir = os.path.join(data_dir, 'training_set')
if not os.path.exists(training_set_dir):  # create the folder if it does not exist yet
    os.makedirs(training_set_dir)


def invert_entry(entry):
    if entry == EMPTY_VAL:
        return entry
    if entry == BLACK_VAL:
        return WHITE_VAL
    if entry == WHITE_VAL:
        return BLACK_VAL

def flatten_matrix(m, invert_color=False):  # Board.matrix2csv(), with inversion added
    ls = m.tolist()
    if invert_color:
        ls = [str(invert_entry(entry)) for row in ls for entry in row]
    else:
        ls = [str(entry) for row in ls for entry in row]
    return ';'.join(ls)

lines = []

# see https://github.com/jtauber/sgf
for path in sgf_files:
    sgf_file = open(path, 'r')
    training_set_file = open(os.path.join(training_set_dir, os.path.basename(path) + '.csv'), 'w')
    collection = sgf.parse(sgf_file.read())
    game_trees = collection.children


    for i in range(0, 1):
        moves = game_trees[i].nodes[1:]
        # meta = game_trees[i].nodes[0].properties

        board = Board([[EMPTY_VAL]*9]*9)

        for move in moves:
            board_cur = board.copy()

            keys = move.properties.keys()
            if 'B' not in keys and 'W' not in keys:  # don't know how to deal with special stuff yet
                continue
            player_color = 'B' if 'B' in move.properties.keys() else 'W'
            sgf_move = move.properties[player_color][0]

            loc = None
            if len(sgf_move) is 2:  # otherwise it's a pass
                coord = string.ascii_lowercase.index(sgf_move[0]), -string.ascii_lowercase.index(sgf_move[1]) #  as coordinate (column, -row)
                loc = string.ascii_lowercase.index(sgf_move[1]), string.ascii_lowercase.index(sgf_move[0]) #  (row, column)
                player_val = BLACK_VAL if player_color == 'B' else WHITE_VAL
                opponent_val = WHITE_VAL if player_color == 'B' else BLACK_VAL
                board.place_stone_and_capture_if_applicable(loc, player_val, opponent_val, EMPTY_VAL)

            loc_str = '0'

        # 8 symmetries (dihedral group D4)
        # ----- 1
            if loc is not None:
                loc_str = str(-coord[1] * 9 + coord[0])
            lines.append(flatten_matrix(board_cur) + ';' + loc_str + ';' + str(player_val) + ';0')  # original
            lines.append(flatten_matrix(board_cur, True) + ';' + loc_str + ';' + str(opponent_val) + ';-0')  # original inv
        # ----- 2
            if loc is not None:
                r = np.array([[0,-1], [1,0]])
                coord_new = np.dot(r, coord - CENTER) + CENTER
                loc_str = str(-coord_new[1] * 9 + coord_new[0])
            board_cur = np.rot90(board_cur)
            lines.append(flatten_matrix(board_cur) + ';' + loc_str + ';' + str(player_val) + ';90')  # rot90
            lines.append(flatten_matrix(board_cur, True) + ';' + loc_str + ';' + str(opponent_val) + ';-90')  # rot90 inv
        # ----- 3
            if loc is not None:
                r = np.array([[-1,0], [0,-1]])
                coord_new = np.dot(r, coord - CENTER) + CENTER
                loc_str = str(-coord_new[1] * 9 + coord_new[0])
            board_cur = np.rot90(board_cur, 2)
            lines.append(flatten_matrix(board_cur) + ';' + loc_str + ';' + str(player_val) + ';180')  # rot180
            lines.append(flatten_matrix(board_cur, True) + ';' + loc_str + ';' + str(opponent_val) + ';-180')  # rot180 inv
        # ----- 4
            if loc is not None:
                r = np.array([[0,1], [-1,0]])
                coord_new = np.dot(r, coord - CENTER) + CENTER
                loc_str = str(-coord_new[1] * 9 + coord_new[0])
            board_cur = np.rot90(board_cur, 3)
            lines.append(flatten_matrix(board_cur) + ';' + loc_str + ';' + str(player_val) + ';270')  # rot270
            lines.append(flatten_matrix(board_cur, True) + ';' + loc_str + ';' + str(opponent_val) + ';-270')  # rot270 inv
        # ----- 5
            if loc is not None:
                r = np.array([[-1,0], [0,1]])
                coord_new = np.dot(r, coord - CENTER) + CENTER
                loc_str = str(-coord_new[1] * 9 + coord_new[0])
            board_cur = np.fliplr(board_cur)
            lines.append(flatten_matrix(board_cur) + ';' + loc_str + ';' + str(player_val) + ';0.5')  # hflip
            lines.append(flatten_matrix(board_cur, True) + ';' + loc_str + ';' + str(opponent_val) + ';-0.5')  # hflip inv
        # ----- 6
            if loc is not None:
                r = np.array([[0,-1], [-1,0]])
                coord_new = np.dot(r, coord - CENTER) + CENTER
                loc_str = str(-coord_new[1] * 9 + coord_new[0])
            board_cur = np.rot90(np.fliplr(board_cur))
            lines.append(flatten_matrix(board_cur) + ';' + loc_str + ';' + str(player_val) + ';90.5')  # hflip rot90
            lines.append(flatten_matrix(board_cur, True) + ';' + loc_str + ';' + str(opponent_val) + ';-90.5')  # hflip rot90 inv
        # ----- 7
            if loc is not None:
                r = np.array([[1,0], [0,-1]])
                coord_new = np.dot(r, coord - CENTER) + CENTER
                loc_str = str(-coord_new[1] * 9 + coord_new[0])
            board_cur = np.rot90(np.fliplr(board_cur), 2)
            lines.append(flatten_matrix(board_cur) + ';' + loc_str + ';' + str(player_val) + ';180.5')  # hflip rot180
            lines.append(flatten_matrix(board_cur, True) + ';' + loc_str + ';' + str(opponent_val) + ';-180.5')  # hflip rot180 inv
        # ----- 8
            if loc is not None:
                r = np.array([[0,1], [1,0]])
                coord_new = np.dot(r, coord - CENTER) + CENTER
                loc_str = str(-coord_new[1] * 9 + coord_new[0])
            board_cur = np.rot90(np.fliplr(board_cur), 3)
            lines.append(flatten_matrix(board_cur) + ';' + loc_str + ';' + str(player_val) + ';270.5')  # hflip rot270
            lines.append(flatten_matrix(board_cur, True) + ';' + loc_str + ';' + str(opponent_val) + ';-270.5')  # hflip rot270 inv


        for line in lines:
            training_set_file.write(line + '\n')
    training_set_file.close()


