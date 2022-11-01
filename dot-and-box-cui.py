#####################################
# dot-and-box cui app

# Copyright (c) [2022-] [Koki Yumoto]

# This software is released under the MIT License.
# http://opensource.org/licenses/mit-license.php
#####################################

import copy
import re
import time

DOTS = [
    ['ａ', 'ｂ', 'ｃ', 'ｄ', 'ｅ', ],
    ['ｆ', 'ｇ', 'ｈ', 'ｉ', 'ｊ', ],
    ['ｋ', 'ｌ', 'ｍ', 'ｎ', 'ｏ', ],
    ['ｐ', 'ｑ', 'ｒ', 'ｓ', 'ｔ', ],
    ['ｕ', 'ｖ', 'ｗ', 'ｘ', 'ｙ', ],
]

CELLS = [
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
]

ROWS = [
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
]

COLS = [
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
    [0, 0, 0, 0, ],
]

# ターミナルの文字色・背景色・太さなど
class Color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_PURPLE = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE = '\033[07m'


# idは変更不可
class PLAYER1:
    id = 'player1'
    name = 'プレイヤー1'
    color = Color.YELLOW
    bg_color = Color.BG_YELLOW
    number = 1
    count = 0

# idは変更不可
class PLAYER2:
    id = 'player2'
    name = 'プレイヤー2'
    color = Color.PURPLE
    bg_color = Color.BG_PURPLE
    number = 2
    count = 0


ROW_LINE = 'ーー'
COL_LINE = '｜'
HR = '------------------------------------------'
PADDING_LEFT = '　　　　'

def main():
    # ゲーム開始アナウンス
    print(Color.BOLD + 'ドットアンドボックスへようこそ！\nゲームを開始します' + Color.END)
    # 2秒
    time.sleep(2)

    retry = True
    retry_text_color = Color.BOLD
    while retry:
        dotAndBox()
        retry = yes_no_input('もう一度遊ぶ？\n', retry_text_color)


def dotAndBox():
    # 初期化
    cells = copy.deepcopy(CELLS)
    rows = copy.deepcopy(ROWS)
    cols = copy.deepcopy(COLS)
    current_player = None
    player1 = PLAYER1
    player2 = PLAYER2
    current_player = togglePlayer(current_player, player1, player2)
    # 現ターンでマスが埋められたかどうか
    filled = False

    display(cells, rows, cols, [player1, player2])

    while True:
        print(current_player.color + current_player.name + 'のターン！' + Color.END)

        #　入力値から始点と終点を取得
        start_xy, end_xy = getInput()

        # データを更新する
        cells, rows, cols, start_xy, end_xy, player, filled = update(cells, rows, cols, start_xy, end_xy, current_player, filled)

        # 結果を表示する
        display(cells, rows, cols, [player1, player2])

        if isEnd(cells):
            # 終了
            print('ゲーム終了！')
            winner = player1
            if player1.count == player2.count:
                print('引き分け！')
                break

            if winner.count < player2.count:
                winner = player2
            print(winner.color + winner.name + 'の勝ち！' + Color.END + '\n')

            # リセット
            player1.count = 0
            player2.count = 0

            break
        else:
            # 継続
            if not filled:
                current_player = togglePlayer(current_player, player1, player2)


# プレイヤーのターンをチェンジ
def togglePlayer(current_player, player1, player2):
    if current_player is None:
        return player1
    elif current_player.id == 'player1':
        return player2
    elif current_player.id == 'player2':
        return player1
    else:
        raise Exception('現在ターンのプレイヤーが不適切です。')

# 入力値を取得する
def getInput():
    # 始点を入力
    while True:
        start_input = input("始点を入力してください\n>>")
        start_xy = getCoordinates(start_input)

        if not start_xy:
            # 再入力
            continue

        # 問題がなければ次の処理へ進む
        break

    # 終点を入力
    while True:
        end_input = input("終点を入力してください\n(zで始点の入力に戻る)\n>>")

        # zが入力されたら始点の入力に戻る
        if end_input == 'z':
            print(Color.RED + '再入力します' + Color.END)
            start_xy, end_xy = getInput()
            return start_xy, end_xy
        end_xy = getCoordinates(end_input)

        if not end_xy:
            # 再入力
            continue

        # 問題がなければ次の処理へ進む
        break

    # 始点と終点の関係を検証
    while not validateStartAndEndXY(start_xy, end_xy):
        # 再入力
        start_xy, end_xy = getInput()

    return start_xy, end_xy

# 座標を取得
def getCoordinates(point):
    # 入力値の妥当性を検証
    if not validateInput(point):
        return False

    # 半角英->全角英
    point = point.translate(str.maketrans(
        {chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))

    # DOTS配列から座標を取得
    for y, dot_row in enumerate(DOTS):
        for x, dot in enumerate(dot_row):
            if dot == point:
                return [x, y]

    # DOTS配列に該当する値がなければ真偽値Falseを戻す
    return False

# 入力された値の妥当性を検証し、真偽値を返す


def validateInput(input):
    # 半角a-yであるかどうか
    if not re.match(r'^[a-y]$', input):
        print(Color.RED + 'aからyまでの半角英数を入力してください' + Color.END)
        return False
    else:
        return True

# 始点と終点の関係を検証
# 隣り合っている点同士かどうかを検証する


def validateStartAndEndXY(start_xy, end_xy):
    start_x = start_xy[0]
    start_y = start_xy[1]
    end_x = end_xy[0]
    end_y = end_xy[1]

    start_x_allows = [
        end_x - 1,
        end_x + 1.
    ]
    start_y_allows = [
        end_y - 1,
        end_y + 1,
    ]

    # 隣り合う点同士かどうかを判定
    if (start_x == end_x and start_y in start_y_allows) or (start_y == end_y and start_x in start_x_allows):
        # 隣り合っていたらTrueを戻す
        return True
    else:
        # 隣り合っていなかったら、エラー文を吐き出し、Falseを戻す
        print(Color.RED + '始点と終点は隣り合う点を指定してください' + Color.END)
        return False

# データを更新する


def update(cells, rows, cols, start_xy, end_xy, player, filled):
    if start_xy[0] == end_xy[0]:
        # 始点と終点のX座標が同じであるならば、cols配列を更新
        if cols[start_xy[0]][min(start_xy[1], end_xy[1])] > 0:
            # 既に選択されている場合は、再入力後、再更新する
            print(Color.RED + '既に選択されています。再度選択してください' + Color.END)
            start_xy, end_xy = getInput()
            update(cells, rows, cols, start_xy, end_xy, player, filled)
            return cells, rows, cols, start_xy, end_xy, player, filled
        else:
            cols = updateCols(cols, start_xy, end_xy, player)
    else:
        # そうでなければ、rows配列を更新
        if rows[start_xy[1]][min(start_xy[0], end_xy[0])] > 0:
            # 既に選択されている場合は、再入力後、再更新する
            print(Color.RED + '既に選択されています。再度選択してください' + Color.END)
            start_xy, end_xy = getInput()
            update(cells, rows, cols, start_xy, end_xy, player, filled)
            return cells, rows, cols, start_xy, end_xy, player, filled
        else:
            rows = updateRows(rows, start_xy, end_xy, player)

    #　cells配列を更新
    cells, filled = updateCells(cells, rows, cols, player)

    return cells, rows, cols, start_xy, end_xy, player, filled

# rows配列を更新する


def updateRows(rows, start_xy, end_xy, player):
    # start_xyとend_xyのY座標は同じであることが前提
    # そうでなかった場合は例外を発生させる
    if not start_xy[1] == end_xy[1]:
        raise Exception(Color.RED + '始点と終点のY座標は同じである必要があります。'+ Color.END)

    rows[start_xy[1]][min(start_xy[0], end_xy[0])] = player.number
    return rows


def updateCols(cols, start_xy, end_xy, player):
    # start_xyとend_xyのX座標は同じであることが前提
    # そうでなかった場合は例外を発生させる
    if not start_xy[0] == end_xy[0]:
        raise Exception(Color.RED + '始点と終点のX座標は同じである必要があります。' + Color.END)

    cols[start_xy[0]][min(start_xy[1], end_xy[1])] = player.number
    return cols


def updateCells(cells, rows, cols, player):
    filled = False
    # y: 0-3
    for y, fills_row in enumerate(cells):
        # x: 0-3
        for x, fill in enumerate(fills_row):
            if fill == 0 and rows[y][x] > 0 and rows[y+1][x] > 0 and cols[x][y] > 0 and cols[x+1][y] > 0:
                #　四方に線があるので、マスに現在のターンのプレイヤーの番号を設定する
                cells[y][x] = player.number
                player.count += 1
                filled = True
    return cells, filled


def isEnd(cells):
    return filledCells(cells)


def filledCells(cells):
    # cells配列内の値が全て0以外かどうか
    # すなわち、全てのマスが埋まっているかどうか
    for cell_row in cells:
        for cell in cell_row:
            if cell == 0:
                return False

    return True


def display(cells, rows, cols, players):
    # 水平線
    print(HR)

    for x, dot_row in enumerate(DOTS):
        for y, dot in enumerate(dot_row):
            if y == 0:
                # デザイン調整(左にパディング)
                print(PADDING_LEFT, end='')

            print(dot, end='')

            if y < len(dot_row) - 1:
                if rows[x][y] > 0:
                    print(players[rows[x][y] - 1].color + ROW_LINE + Color.END, end='')
                else:
                    print('　　', end='')

            if y >= len(dot_row) - 1:
                # 2回実行
                for j in range(2):
                    if j == 0:
                        #　改行
                        print('')

                    # デザイン調整(左にパディング)
                    print(PADDING_LEFT, end='')
                    # i:0-3
                    for i in range(len(cols)):
                        if x < len(DOTS) - 1:
                            if cols[i][x] > 0:
                                print(players[cols[i][x] - 1].color +
                                    COL_LINE + Color.END, end='')
                            else:
                                print('　　', end='')

                            if i < len(cols) - 1:
                                if cells[x][i] > 0:
                                    print(
                                        players[cells[x][i] - 1].bg_color + '　　' + Color.END, end='')

                                else:
                                    print('　　', end='')

                    if i >= len(cols) - 1:
                        print('')

    for j, player in enumerate(players):
        # 現在のスコアを表示
        print(player.color + player.name + '：' + str(player.count) + 'マス' + Color.END, end='')
        if j == 0:
            print(' / ', end='')
        if j >= len(players) - 1:
            print('')
            #　水平線
            print(HR)

def yes_no_input(ask, text_color = None):
    if text_color is not None:
        choice = input(text_color + ask + '[y/N]: ' + Color.END)
    else:
        choice = input(ask + '[y/N]: ')

    #小文字に変換
    choice = choice.lower()
    if choice in ['y', 'ye', 'yes']:
        return True
    else:
        return False

if __name__ == '__main__':
    main()
