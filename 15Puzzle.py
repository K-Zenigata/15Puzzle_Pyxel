import math
import pyxel


class Vector2i:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Puzzle:

    WINDOW_W = 64
    WINDOW_H = 64
    ROWS = 4
    COLS = 4
    PANEL_SIZE = 16
    SHUFFLE_VOLUME = 2000

    # アニメーションの速さ
    ANIME_SPEED = 2

    def __init__(self):
        # 画像が小さくても、windowのサイズの値を小さくすれば、拡大される。
        # 64 でも、640 でも、実際に表示されるwindowの大きさは変わらない。
        pyxel.init(self.WINDOW_W, self.WINDOW_H, title="15 Puzzle")
        pyxel.load("assets/puzzle.pyxres")

        # マウスポインターの表示
        pyxel.mouse(True)

        # 盤面 4x4と番兵を入れて、6x6に。-1で初期化
        self.grid = [[-1 for _ in range(6)] for _ in range(6)]

        # クリック地点の座標
        self.mouse_x = 0
        self.mouse_y = 0

        self.shuffle = False

        # アニメーション用 **************
        self.animation = False
        self.directionList = []  # 移動の道筋の座標を入れる
        self.list_count = 0
        self.target_pos = Vector2i(0, 0)  # 移動先のポジション
        # ******************************

        self.compleat = False
        self.end_music = False

        self.init()
        self.shuffleNumbers()

        pyxel.run(self.update, self.draw)

    def init(self):
        # 番兵以外の場所に、1 ~ 16 の数値を入れる
        n = 1
        for y in range(self.ROWS):
            for x in range(self.COLS):
                # print(n)
                self.grid[y + 1][x + 1] = n

                # 16 の時は、0 を入れる (白いパネル用)
                n = 0 if n == 15 else n + 1

    # 移動アニメーション用の道筋の座標を取得
    def movingMakePath(self, x, y, dx, dy):

        # 古い座標の配列を消去
        self.directionList.clear()

        # アニメーションの速度、1コマの移動量(速さ x 方向)
        move = Vector2i(dx * self.ANIME_SPEED, dy * self.ANIME_SPEED)

        # click した場所、アニメーションのスタート地点
        anime_pos = Vector2i(x * self.PANEL_SIZE, y * self.PANEL_SIZE)

        # 道筋の数
        vol = self.PANEL_SIZE / self.ANIME_SPEED

        for i in range(int(vol)):
            # click した場所に、1コマの移動量が加算せれていく
            anime_pos.x += move.x
            anime_pos.y += move.y

            # anime_pos をそのままappendしたらダメ
            # Vector2i で取り直さないと、配列に全部同じ値が入る
            # anime_pos は、クラスのインスタンスなので、たぶん参照扱い
            temp = Vector2i(anime_pos.x, anime_pos.y)

            # 道筋の座標をどんどん入れていく
            self.directionList.append(temp)

    # キー入力からの、update
    def updateBoard(self, x, y):
        dx = 0
        dy = 0

        if self.grid[y + 1][x] == 0:
            # 下が空白パネルなら
            dx = 0
            dy = 1
        elif self.grid[y][x + 1] == 0:
            # 右隣が空白パネルなら
            dx = 1
            dy = 0
        elif self.grid[y][x - 1] == 0:
            # 左隣が空白パネルなら
            dx = -1
            dy = 0
        elif self.grid[y - 1][x] == 0:
            # 上が空白パネルなら
            dx = 0
            dy = -1
        else:  # 周りに空白パネルが無いなら
            return

        # クリックされたパネルの番号を退避
        n = self.grid[y][x]

        # クリックした場所に空白パネルを配置
        self.grid[y][x] = 0

        # 空白パネルがあった場所に、クリックパネルを配置
        self.grid[y + dy][x + dx] = n

        # シャッフル中は、アニメーションいらないので、ここでreturn
        if not self.shuffle:
            return

        # アニメーション用
        click = Vector2i(x - 1, y - 1)

        # 移動先のポジション
        self.target_pos.x = click.x + dx
        self.target_pos.y = click.y + dy

        self.animation = True

        # クリック サウンド
        # ここに置く理由は、アニメーションが確実に行われるから
        # 移動しないパネルで、鳴ったらダメだから
        pyxel.play(0, 0)

        # 情報を渡して、アニメーションの道筋を作ってもらう
        self.movingMakePath(click.x, click.y, dx, dy)

    # 盤面をシャッフル
    def shuffleNumbers(self):

        for i in range(self.SHUFFLE_VOLUME):
            x = pyxel.rndi(1, 4)
            y = pyxel.rndi(1, 4)

            self.updateBoard(x, y)

        self.shuffle = True

    # ゲームクリア判定
    def checkCompleat(self):
        n = 1

        for y in range(1, 5):
            for x in range(1, 5):

                # 白いパネル
                if n == 16:
                    n = 0

                # 1つでも違っていたら return
                if n != self.grid[y][x]:
                    return False

                n += 1

        # 1 ~ 15 0 と並んでいれば
        return True

    # 移動アニメーション
    def drawAnimation(self, x, y, n):

        # blt(ここにx, ここにy, このimgを, 画像のここからx, 画像のここからy, 画像の幅w, 画像の高さh, 色?)

        # blt(x,  y, img, u,  v, w, h, [colkey])
        px = x * self.PANEL_SIZE
        py = y * self.PANEL_SIZE
        img = 0
        u = n * self.PANEL_SIZE
        v = 0
        w = self.PANEL_SIZE
        h = self.PANEL_SIZE

        # クリックしたパネルの順番が来たら
        if y == self.target_pos.y and x == self.target_pos.x:

            # 白いパネルは、ここで同時に描画する。
            # 白いパネルは、アニメーションしないので、windowの背景を白にして、誤魔化している。
            pyxel.blt(px, py, img, 0, v, w, h)

            # 道筋の座標を取り出していく
            px = self.directionList[self.list_count].x
            py = self.directionList[self.list_count].y

            # 描画
            pyxel.blt(px, py, img, u, v, w, h)

            self.list_count += 1

            # アニメーションが終了したのかどうか
            if self.list_count == len(self.directionList):
                self.animation = False
                self.list_count = 0

        else:  # クリックしたパネル以外の描画

            # 白いパネルは描画しない (0 = 白いパネル)
            if n:
                pyxel.blt(px, py, img, u, v, w, h)

    # 盤面の描画
    def drawBoard(self):
        for y in range(self.ROWS):
            for x in range(self.COLS):

                n = self.grid[y + 1][x + 1]

                if self.animation:

                    # アニメーション中は、こちらの関数に描画をゆだねる
                    self.drawAnimation(x, y, n)
                else:
                    # blt(x,  y, img, u,  v, w, h, [colkey])
                    px = x * self.PANEL_SIZE
                    py = y * self.PANEL_SIZE
                    img = 0
                    u = n * self.PANEL_SIZE
                    v = 0
                    w = self.PANEL_SIZE
                    h = self.PANEL_SIZE

                    pyxel.blt(px, py, img, u, v, w, h)

    # text の描画
    def drawText(self):

        # text(x, y, str, clr)
        pyxel.text(3, 3, "Clear!", 10)

        # 白いパネルを黒いパネルに変えているだけ、気分の問題
        pyxel.blt(48, 48, 0, 0, 16, 16, 16)

    # クリック イベント
    def mouseButtonPressed(self):

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and not self.animation and not self.compleat:

            # クリック地点の座標
            self.mouse_x = pyxel.mouse_x
            self.mouse_y = pyxel.mouse_y

            # 座標を、1 ~ 4 の数値に変換
            x = math.floor(self.mouse_x / self.PANEL_SIZE)
            y = math.floor(self.mouse_y / self.PANEL_SIZE)

            # 番兵を考慮して、+ 1
            self.updateBoard(x + 1, y + 1)

    # update
    def update(self):

        # ゲームクリアなら
        if self.compleat:
            return

        self.mouseButtonPressed()

    # draw
    def draw(self):

        # 背景色 cls(色番号)
        pyxel.cls(7)

        self.compleat = self.checkCompleat()
        self.drawBoard()

        # ゲームクリアなら text を描画
        if self.compleat and not self.animation:
            self.drawText()

            # ゲームクリアの音楽は、フラグで制御しないと、おかしくなる
            if not self.end_music:
                pyxel.play(0, 1)
                self.end_music = True


Puzzle()
