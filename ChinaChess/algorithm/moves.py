#!/usr/bin/python3
# encoding: utf-8

"""
@author: chsh
@file:  moves.py
@time:  2020/6/15 17:03
@title:
@content: 获取AI的可走棋内容
"""
from ChinaChess.gameFunction import GameFunction
from ChinaChess.settings import Settings
from ChinaChess.algorithm.scores import Scores
from math import fabs

class MoveNodes():
    def __init__(self, box_name_from, box_from, box_action, box_name_to, box_to, box_res, score=10):
        self.box_name_from = box_name_from
        self.box_action = box_action
        self.box_from = box_from
        self.box_to = box_to
        self.box_name_to = box_name_to
        self.box_res = box_res
        self.score = score

class Moves():
    def __init__(self, all_pieces, player1Color):
        self.all_pieces = all_pieces
        self.player1_color = player1Color
        #
        self.settings = Settings()
        self.game_func = GameFunction(self.settings)

    # 获得所有棋子可能的走棋内容（省略了很多不关联的走棋内容，比如不关联的打开棋子，走动棋子等等）
    def generate_all_moves(self):
        moves = []
        for box_xy, value in self.all_pieces.items():
            # 根据打开的棋子，列举棋子的所有走法
            if value['state'] is True:
                box_key = value['box_key']
                box_color, box_name = box_key.split('_')
                box_name = box_name[:-1]
                # 这是一个player2方阵的棋子
                if box_color != self.player1_color:
                    # 不等于'pao'，而且棋子偏大，可以翻开或移动到临近的棋子
                    if box_name in ['shi', 'xiang', 'ma']:
                        box_open = self._open_piece_for_near(box_xy)
                        for box1 in box_open:
                            box1_xy, box1_key, box1_state, box1_color, box1_name = self._get_box(box1)
                            if box1_state is True:
                                result = self.game_func.piece_VS_piece(box_xy, box1_xy, self.all_pieces)
                                if result[2] is True:
                                    if result[1] in ['jiang_zu', 'box1<box2']:
                                        score, box1_key, box1_xy = self._danger_box_yes_or_no(box_xy, box_name, box_color, box1_name, box1)
                                        if score is not None:
                                            moves.append(MoveNodes(box_key, box_xy, '移动', box1_key, box1_xy, None, score=score))
                                    else:
                                        moves.append(MoveNodes(box_key, box_xy, '吃棋', box1_key, box1_xy, result[1]))
                            elif box1_state is None:
                                yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box1_xy, box1_state=None)
                                if yesOrNo[0] is True:
                                    moves.append(MoveNodes(box_key, box_xy, '移动', None, box1_xy, None, score=yesOrNo[1]))
                            else:
                                # 判断打开当前位置的棋子的威胁度有多大，适不适合打开
                                yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box1_xy)
                                if yesOrNo[0] is True:
                                    moves.append(MoveNodes(box_key, box_xy, '打开', None, box1_xy, None, score=yesOrNo[1]))
                    # 棋子偏小，可以翻开斜角的棋子来保护，也可以移动到临近的棋子
                    elif box_name in ['jiang', 'ju', 'zu']:
                        # 打开棋子的所有走棋
                        box_open_corner = self._open_piece_for_corner(box_xy)
                        for box1 in box_open_corner:
                            box1_xy, box1_key, box1_state, box1_color, box1_name = self._get_box(box1)
                            # 判断打开当前位置的棋子的威胁度有多大，适不适合打开
                            if box1_state is False:
                                yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box1_xy)
                                if yesOrNo[0] is True:
                                    moves.append(MoveNodes(box_key, box_xy, '打开', None, box1_xy, None, score=yesOrNo[1]))
                        # 移动或者吃棋的所有走棋
                        box_open_near = self._open_piece_for_near(box_xy)
                        for box2 in box_open_near:
                            box2_xy, box2_key, box2_state, box2_color, box2_name = self._get_box(box2)
                            if box2_state is True:
                                result = self.game_func.piece_VS_piece(box_xy, box2_xy, self.all_pieces)
                                if result[2] is True:
                                    if result[1] in ['jiang_zu', 'box1<box2']:
                                        score, box1_key, box1_xy = self._danger_box_yes_or_no(box_xy, box_name, box_color, box2_name, box2)
                                        if score is not None:
                                            moves.append(MoveNodes(box_key, box_xy, '移动', box1_key, box1_xy, None, score=score))
                                    else:
                                        moves.append(MoveNodes(box_key, box_xy, '吃棋', box2_key, box2_xy, result[1]))
                            elif box2_state is None:
                                yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box2_xy, box1_state=None)
                                if yesOrNo[0] is True:
                                    moves.append(MoveNodes(box_key, box_xy, '移动', box2_key, box2_xy, None, score=yesOrNo[1]))
                    # 等于'pao'分两种情况：吃棋要跳着吃，走棋只能移动
                    elif box_name == 'pao':
                        # 吃棋的情况
                        box_open_pao = self._open_piece_for_pao(box_xy)
                        for box1 in box_open_pao:
                            box1_xy, box1_key, box1_state, box1_color, box1_name = self._get_box(box1)
                            if box1_state is True:
                                result = self.game_func.piece_VS_piece(box_xy, box1_xy, self.all_pieces)
                                if result[2] is True:
                                    moves.append(MoveNodes(box_key, box_xy, '吃棋', box1_key, box1_xy, result[1]))
                            elif box1_state is False:
                                # 判断打开当前位置的棋子的威胁度有多大，适不适合打开
                                yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box1_xy)
                                if yesOrNo[0] is True:
                                    moves.append(MoveNodes(box_key, box_xy, '打开', None, box1_xy, None, score=yesOrNo[1]))
                        # 移动的情况
                        box_open_near = self._open_piece_for_near(box_xy)
                        for box2 in box_open_near:
                            box2_xy, box2_key, box2_state, box2_color, box2_name = self._get_box(box2)
                            # if box2_state is None:
                            #     yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box2_xy, box1_state=None)
                            #     if yesOrNo[0] is True:
                            #         moves.append(MoveNodes(box_key, box_xy, '移动', box2_key, box2_xy, None, score=yesOrNo[1]))
                            # 这个特殊情况，要判断'pao'是否被旁边的对方棋子威胁
                            if box2_state is True:
                                # 判断为对方棋子而且为['shi', 'xiang', 'ma', 'ju']
                                if box2_color != box_color and box2_name in ['shi', 'xiang', 'ma', 'ju']:
                                    score, box1_key, box1_xy = self._danger_box_yes_or_no(box_xy, box_name, box_color, box2_name, box2)
                                    if score is not None:
                                        moves.append(MoveNodes(box_key, box_xy, '移动', box1_key, box1_xy, None, score=score))
                                    # score = Scores.eat_score(f"{box2_name}_pao")
                                    # box_open_near2 = self._open_piece_for_near(box_xy)
                                    # # 从box_open_near2中寻找能保护box的棋子
                                    # for box3 in box_open_near2:
                                    #     box3_xy, box3_key, box3_state, box3_color, box3_name = self._get_box(box3)
                                    #     if box3_state is True and box3_color == box_color:
                                    #         box2_index = self.settings.pieces_list.index(box2_name)
                                    #         box3_index = self.settings.pieces_list.index(box3_name)
                                    #         # 确认box_open_near2中有比box2大的棋子
                                    #         if box3_index <= box2_index:
                                    #             box_open_corner1 = self._open_piece_for_corner(box3_xy)
                                    #             # 寻找box3对角线上的棋子，为box移动找空缺的棋子位置
                                    #             for box4 in box_open_corner1:
                                    #                 box4_x, box4_y = box4
                                    #                 box4_xy, box4_key, box4_state, box4_color, box4_name = self._get_box(box4)
                                    #                 if box4 != box2:
                                    #                     box_x = int(box_xy.split('_')[1])
                                    #                     box_y = int(box_xy.split('_')[-1])
                                    #                     # 找到了可移动空缺的棋子位置
                                    #                     if (box_x == box4_x or box_y == box4_y) and box4_state is None:
                                    #                         # 对空缺的棋子位置判断是否有新的威胁
                                    #                         yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box4_xy, box1_state=None)
                                    #                         if yesOrNo[0] is True:
                                    #                             score += 2
                                    #                             moves.append(MoveNodes(box_key, box_xy, '移动', box4_key, box4_xy, None, score=score))

                # 这里表示当前的棋子是player1方阵的棋子
                else:
                    # 如果该棋子为"ma\ju\pao\zu",就可以在其旁边位置翻开棋子，有几率翻开电脑的棋子比它大（冒险一点的走法）
                    # 保守一点的走法就是该棋子为"ju\pao\zu"
                    box_open = []
                    if box_name in ['jiang', 'ju', 'pao', 'zu']:
                        box_open = self._open_piece_for_near(box_xy)
                    # 如果棋子偏大，就去翻开棋子找'pao'，这样'pao'就可以直接吃掉这个棋子
                    box_open_pao = self._open_piece_for_pao(box_xy)
                    box_open += box_open_pao
                    for box1 in box_open:
                        box1_xy, box1_key, box1_state, box1_color, box1_name = self._get_box(box1)
                        if box1_state is False:
                            # 判断打开当前位置的棋子的威胁度有多大，适不适合打开
                            yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box1_xy)
                            if yesOrNo[0] is True:
                                moves.append(MoveNodes(box_key, box_xy, '打开', None, box1_xy, None, score=yesOrNo[1]))
        return moves

    # 对受威胁的棋子寻找可避开的走棋（如果有）
    def _danger_box_yes_or_no(self, box_xy, box_name, box_color, box1_name, box1):
        score = Scores.eat_score(f"{box1_name}_{box_name}")
        box_open_near2 = self._open_piece_for_near(box_xy)
        # 从box_open_near2中寻找能保护box的棋子
        for box3 in box_open_near2:
            box3_xy, box3_key, box3_state, box3_color, box3_name = self._get_box(box3)
            if box3_state is True and box3_color == box_color:
                box1_index = self.settings.pieces_list.index(box1_name)
                box3_index = self.settings.pieces_list.index(box3_name)
                # 确认box_open_near2中有比box2大的棋子
                if box3_index <= box1_index:
                    box_open_corner1 = self._open_piece_for_corner(box3_xy)
                    # 寻找box3对角线上的棋子，为box移动找空缺的棋子位置
                    for box4 in box_open_corner1:
                        box4_x, box4_y = box4
                        box4_xy, box4_key, box4_state, box4_color, box4_name = self._get_box(box4)
                        if box4 != box1:
                            box_x = int(box_xy.split('_')[1])
                            box_y = int(box_xy.split('_')[-1])
                            # 找到了可移动空缺的棋子位置
                            if (box_x == box4_x or box_y == box4_y) and box4_state is None:
                                # 对空缺的棋子位置判断是否有新的威胁
                                yesOrNo = self._box_open_yes_or_on(box_xy, box_name, box4_xy, box1_state=None)
                                if yesOrNo[0] is True:
                                    score_piece = int(Scores.piece_score(box1_name) / 10000)
                                    score += score_piece
                                    return [score, box4_key, box4_xy]
        return [None, None, None]

    # 判断当前的box可否打开
    def _box_open_yes_or_on(self, box_xy, box_name, box1_xy, box1_state=False):
        # box1_flag为true表示该棋子不在pao路上，需要继续判断相邻的棋子是否有威胁
        box1_flag = True
        box_open_pao = self._open_piece_for_pao(box1_xy)
        # 是否在对方的pao路上
        for box2 in box_open_pao:
            box2_xy, box2_key, box2_state, box2_color, box2_name = self._get_box(box2)
            if box2_state is True:
                # 在对方pao的进攻路上，没有打开的box_to的必要了
                if box2_color == self.player1_color and box2_name == 'pao':
                    box1_flag = False
                    break
        # 判断临近的棋子是否会对自己的棋子产生威胁
        if box1_flag is True:
            score = 0
            if box1_state is False:
                # 判断双方的jiang是否都还存在
                red_jiang_is_true, black_jiang_is_true = False, False
                for _, piece in self.all_pieces.items():
                    if piece['box_key'] == 'red_jiang1':
                        red_jiang_is_true = True
                    elif piece['box_key'] == 'black_jiang1':
                        black_jiang_is_true = True
                # 对zu有不同的score
                box_color = 'red' if self.player1_color == 'black' else 'black'
                if (box_color == 'red' and red_jiang_is_true is True and box_name == 'zu'):
                    if black_jiang_is_true is False:
                        score = int(Scores.piece_score(f"zu_no_jiang") / 10000) + 10
                    else:
                        score = int(Scores.piece_score(f"zu") / 10000) + 10
                elif (box_color == 'black' and black_jiang_is_true is True and box_name == 'zu'):
                    if red_jiang_is_true is False:
                        score = int(Scores.piece_score(f"zu_no_jiang") / 10000) + 10
                    else:
                        score = int(Scores.piece_score(f"zu") / 10000) + 10
                else:
                    score = int(Scores.piece_score(f"{box_name}") / 10000) + 10
            #
            box_open_near = self._open_piece_for_near(box1_xy)
            for i, box3 in enumerate(box_open_near, 1):
                box3_xy, box3_key, box3_state, box3_color, box3_name = self._get_box(box3)
                if box3_state is True and box3_xy != box_xy:
                    if box3_color == self.player1_color:
                        box3_index = self.settings.pieces_list.index(box3_name)
                        box_index = self.settings.pieces_list.index(box_name)
                        # 这个位置的棋子是否比己方box_from的棋子大，如果大就没有必要打开box_to的棋子了
                        if box_index > box3_index:
                            # 特殊情况：box_name为zu，box3_name为jiang，是可以被吃掉的
                            if box_name == 'zu' and box3_name == 'jiang':
                                if box1_state is not None:
                                    score += 1000
                            elif box_name == 'zu' and box3_name == 'ju':
                                if box1_state is False:
                                    score += Scores.other_pieces_score('zu_ju')
                            elif box_name == 'zu' and box3_name == 'pao':
                                if box1_state is False:
                                    score += Scores.other_pieces_score('zu_pao')
                            elif box_name == 'pao' and box3_name  == 'jiang':
                                if box1_state is False:
                                    score += Scores.other_pieces_score('pao_jiang')
                            elif box_name == 'pao' and box3_name == 'ju':
                                if box1_state is False:
                                    score += Scores.other_pieces_score('pao_ju')
                            else:
                                break
                        else:
                            # box1_state为False表示打开棋子，为None表示移动棋子
                            if box1_state is None:
                                if box_name == 'jiang' and box3_name in ['pao', 'zu']:
                                    score = 0
                                elif box_name == 'pao' and box3_name == 'zu':
                                    score = 0
                                else:
                                    # 判断两个棋子是否在对角线上，而且田字格里没有其他的棋子
                                    box_x = int(box_xy.split('_')[1])
                                    box_y = int(box_xy.split('_')[-1])
                                    box3_x, box3_y = box3
                                    if (box3_x-box_x == 1 and box3_y-box_y == 1) or (box3_x-box_x == -1 and box3_y-box_y == 1):
                                        box4_x, box4_y = box3_x, box_y
                                        box5_x, box5_y = box_x, box3_y
                                        box4_xy, box4_key, box4_state, box4_color, box4_name = self._get_box((box4_x, box4_y))
                                        box5_xy, box5_key, box5_state, box5_color, box5_name = self._get_box((box5_x, box5_y))
                                        if box4_state is None and box5_state is None:
                                            score = 0
                                    elif (box3_x-box_x == -1 and box3_y-box_y == -1) or (box3_x-box_x == 1 and box3_y-box_y == -1):
                                        box4_x, box4_y = box_x, box3_y
                                        box5_x, box5_y = box3_x, box_y
                                        box4_xy, box4_key, box4_state, box4_color, box4_name = self._get_box((box4_x, box4_y))
                                        box5_xy, box5_key, box5_state, box5_color, box5_name = self._get_box((box5_x, box5_y))
                                        if box4_state is None and box5_state is None:
                                            score = 0
                                    else:
                                        score += 1000
                if i == len(box_open_near):
                    # 可移动空位得分丢弃
                    # if self.all_pieces[box1_xy]['state'] is None:
                    #     score += 100
                    return [True, score]
        return [False, None]

    # 根据getallmoves返回的box，找到box对应的box_key, box_state, box_color, box_name
    def _get_box(self, box):
        box_x, box_y = box
        box_xy = f'box_{box_x}_{box_y}'
        box_state = self.all_pieces[box_xy]['state']
        if box_state is True:
            box_key = self.all_pieces[box_xy]['box_key']
            box_value = box_key.split('_')
            box_color, box_name = box_value
            box_name = box_name[:-1]
        else:
            box_key, box_color, box_name = None, None, None
        return (box_xy, box_key, box_state, box_color, box_name)

    # 走棋内容为打开相邻位置的任意一个棋子
    def _open_piece_for_near(self, box_xy):
        box_x = int(box_xy.split('_')[1])
        box_y = int(box_xy.split('_')[-1])
        box_open = []
        # 计算box相邻的四个方向是否能打开
        # box位于棋盘的4个角上，则只能打开两个相邻位置的棋子
        if box_x == 0 and box_y == 0:
            box_open.append((box_x, box_y+1))
            box_open.append((box_x+1, box_y))
        elif box_x == 0 and box_y == 3:
            box_open.append((box_x, box_y-1))
            box_open.append((box_x+1, box_y))
        elif box_x == 7 and box_y == 0:
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y+1))
        elif box_x == 7 and box_y == 3:
            box_open.append((box_x, box_y-1))
            box_open.append((box_x-1, box_y))
        # box位于棋盘的4条边线上，则可以打开3个相邻位置的棋子
        elif box_x == 0 and 0 < box_y < 3:
            box_open.append((box_x, box_y-1))
            box_open.append((box_x+1, box_y))
            box_open.append((box_x, box_y+1))
        elif box_x == 7 and 0 < box_y < 3:
            box_open.append((box_x, box_y-1))
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y+1))
        elif 0 < box_x < 7 and box_y == 0:
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y+1))
            box_open.append((box_x+1, box_y))
        elif 0 < box_x < 7 and box_y == 3:
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y-1))
            box_open.append((box_x+1, box_y))
        # box位于棋盘中间，则可以打开4个相邻位置的棋子
        else:
            box_open.append((box_x-1, box_y))
            box_open.append((box_x, box_y-1))
            box_open.append((box_x+1, box_y))
            box_open.append((box_x, box_y+1))
        return box_open

    # 走棋内容为打开隔一个棋子的棋子，即假设翻开的棋子为'pao'就可以吃掉当前这个棋子
    def _open_piece_for_pao(self, box_xy):
        box_x = int(box_xy.split('_')[1])
        box_y = int(box_xy.split('_')[-1])
        box_open = []
        # box位于棋盘的第1，2纵列，则只能打开两个隔开的棋子
        if (box_x in [0, 1]) and (box_y in [0, 1]):
            for i in range(box_x+1, 8):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i+1, 8):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_y+1, 4):
                if self.all_pieces[f'box_{box_x}_{k}']['state'] is not None:
                    for m in range(k+1, 4):
                        if self.all_pieces[f'box_{box_x}_{m}']['state'] is not None:
                            box_open.append((box_x, m))
                            break
                    break
        elif (box_x in [0, 1]) and (box_y in [2, 3]):
            for i in range(box_x + 1, 8):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i + 1, 8):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_y - 1, -1, -1):
                if self.all_pieces[f'box_{box_x}_{k}']['state'] is not None:
                    for m in range(k - 1, -1, -1):
                        if self.all_pieces[f'box_{box_x}_{m}']['state'] is not None:
                            box_open.append((box_x, m))
                            break
                    break
        # box位于棋盘的第7，8纵列，则只能打开两个隔开的棋子
        elif (box_x in [6, 7]) and (box_y in [0, 1]):
            for i in range(box_x-1, -1, -1):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i - 1, -1, -1):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_y+1, 4):
                if self.all_pieces[f'box_{box_x}_{k}']['state'] is not None:
                    for m in range(k+1, 4):
                        if self.all_pieces[f'box_{box_x}_{m}']['state'] is not None:
                            box_open.append((box_x, m))
                            break
                    break
        elif (box_x in [6, 7]) and (box_y in [2, 3]):
            for i in range(box_x-1, -1, -1):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i - 1, -1, -1):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_y-1, -1, -1):
                if self.all_pieces[f'box_{box_x}_{k}']['state'] is not None:
                    for m in range(k - 1, -1, -1):
                        if self.all_pieces[f'box_{box_x}_{m}']['state'] is not None:
                            box_open.append((box_x, m))
                            break
                    break
        #
        else:
            for i in range(box_x + 1, 8):
                if self.all_pieces[f'box_{i}_{box_y}']['state'] is not None:
                    for j in range(i + 1, 8):
                        if self.all_pieces[f'box_{j}_{box_y}']['state'] is not None:
                            box_open.append((j, box_y))
                            break
                    break
            for k in range(box_x-1, -1, -1):
                if self.all_pieces[f'box_{k}_{box_y}']['state'] is not None:
                    for m in range(k - 1, -1, -1):
                        if self.all_pieces[f'box_{m}_{box_y}']['state'] is not None:
                            box_open.append((m, box_y))
                            break
                    break
            if box_y in [0, 1]:
                for p in range(box_y + 1, 4):
                    if self.all_pieces[f'box_{box_x}_{p}']['state'] is not None:
                        for q in range(p + 1, 4):
                            if self.all_pieces[f'box_{box_x}_{q}']['state'] is not None:
                                box_open.append((box_x, q))
                                break
                        break
            elif box_y in [2, 3]:
                for r in range(box_y-1, -1, -1):
                    if self.all_pieces[f'box_{box_x}_{r}']['state'] is not None:
                        for s in range(r - 1, -1, -1):
                            if self.all_pieces[f'box_{box_x}_{s}']['state'] is not None:
                                box_open.append((box_x, s))
                                break
                        break
        return box_open

    # 走棋内容为打开斜角上的棋子，起到保护本方棋子的作用
    def _open_piece_for_corner(self, box_xy):
        box_x = int(box_xy.split('_')[1])
        box_y = int(box_xy.split('_')[-1])
        box_open = []
        # box位于4个角上，只有1个斜角棋子可用
        if box_x == 0 and box_y == 0:
            box_open.append((1, 1))
        elif box_x == 0 and box_y == 3:
            box_open.append((1, 2))
        elif box_x == 7 and box_y == 0:
            box_open.append((6, 1))
        elif box_x == 7 and box_y == 3:
            box_open.append((6, 2))
        # box位于第1列上，有2个斜角可用
        elif box_x == 0 and box_y in [1, 2]:
            box_open.append((1, box_y-1))
            box_open.append((1, box_y+1))
        # box位于第8列上，有2个斜角可用
        elif box_x == 7 and box_y in [1, 2]:
            box_open.append((6, box_y-1))
            box_open.append((6, box_y+1))
        # box位于第1行上，有2个斜角可用
        elif (0 < box_x < 7) and box_y == 0:
            box_open.append((box_x-1, 1))
            box_open.append((box_x+1, 1))
        # box位于第4行上，有2个斜角可用
        elif (0 < box_x < 7) and box_y == 3:
            box_open.append((box_x-1, 2))
            box_open.append((box_x+1, 2))
        # 其他位置上都有4个斜角可用
        else:
            box_open.append((box_x-1, box_y-1))
            box_open.append((box_x+1, box_y-1))
            box_open.append((box_x-1, box_y+1))
            box_open.append((box_x+1, box_y+1))
        return box_open

if __name__ == '__main__':
    all_pieces = {'box_0_0': {'box_key': 'red_pao2', 'state': False},
                  'box_0_1': {'box_key': 'red_ma2', 'state': False},
                  'box_0_2': {'box_key': 'red_xiang2', 'state': False},
                 'box_0_3': {'box_key': 'black_zu3', 'state': None},
                 'box_1_0': {'box_key': 'black_pao2', 'state': False},
                 'box_1_1': {'box_key': 'black_shi1', 'state': False},
                 'box_1_2': {'box_key': 'black_xiang2', 'state': False},
                 'box_1_3': {'box_key': 'black_xiang1', 'state': None},
                 'box_2_0': {'box_key': 'black_zu5', 'state': False},
                 'box_2_1': {'box_key': 'black_shi2', 'state': False},
                 'box_2_2': {'box_key': 'red_zu3', 'state': False},
                  'box_2_3': {'box_key': 'red_shi2', 'state': False},
                 'box_3_0': {'box_key': 'black_zu2', 'state': False},
                 'box_3_1': {'box_key': 'black_ma2', 'state': False},
                 'box_3_2': {'box_key': 'red_jiang1', 'state': False},
                  'box_3_3': {'box_key': 'red_zu1', 'state': False},
                 'box_4_0': {'box_key': 'red_zu4', 'state': False},
                  'box_4_1': {'box_key': 'red_ju1', 'state': False},
                 'box_4_2': {'box_key': 'red_pao1', 'state': True},
                 'box_4_3': {'box_key': 'black_zu4', 'state': None},
                 'box_5_0': {'box_key': 'black_zu1', 'state': False},
                 'box_5_1': {'box_key': 'black_ju2', 'state': False},
                 'box_5_2': {'box_key': 'red_xiang1', 'state': False},
                 'box_5_3': {'box_key': 'black_pao1', 'state': None},
                 'box_6_0': {'box_key': 'black_ma1', 'state': False},
                 'box_6_1': {'box_key': 'black_ju1', 'state': False},
                  'box_6_2': {'box_key': 'red_zu5', 'state': True},
                 'box_6_3': {'box_key': 'black_jiang1', 'state': True},
                 'box_7_0': {'box_key': 'red_ma1', 'state': False},
                  'box_7_1': {'box_key': 'red_ju2', 'state': False},
                 'box_7_2': {'box_key': 'red_zu2', 'state': False},
                  'box_7_3': {'box_key': 'red_shi1', 'state': False}}
    moves = Moves(all_pieces, 'red')
    get_moves = moves.generate_all_moves()
    for i, move in enumerate(get_moves, 1):
        print(f"{move.box_name_from}===>>>{move.box_from}===>>>{move.box_action}===>>>{move.box_name_to}===>>>{move.box_to}===>>>{move.box_res}===>>>{move.score}")


