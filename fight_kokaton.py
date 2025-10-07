import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.img = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """
    def __init__(self, bird:"Bird"):
         """
         ビーム画像Surfaceを生成する
         引数 bird：ビームを放つこうかとん（Birdインスタンス）
         """
         self.img = pg.image.load(f"fig/beam.png")
         self.rct = self.img.get_rect()
         self.rct.centery = bird.rct.centery
         self.rct.left = bird.rct.right
         self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)

class Score:
    """
    スコアに関するクラス
    """
    def __init__(self):
        """
        スコアクラスのコンストラクタ
        スコア表示の座標、初期状態の設定を行う
        """
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.score = 0
        self.img = self.fonto.render("スコア:" + str(self.score), 0, (0,0,255))
        self.img_rct = self.img.get_rect()
        self.img_rct.center = (100, HEIGHT - 50)
    def update(self,screen : pg.Surface):
        """
        引数 Surface型の表示用のスクリーン
        現在のスコアに更新する
        """
        self.img = self.img = self.fonto.render("スコア:" + str(self.score), 0, (0,0,255))
        screen.blit(self.img,self.img_rct)

class Explosion:
    """
    爆発の演出に関するクラス
    """
    def __init__(self,bomb : pg.Rect):
        """
        Explosionクラスのコンストラクタ
        引数 爆発演出を行いたい爆弾のRect型
        爆発演出の時間、画像、座標の設定
        """
        self.life = 60
        self.img = pg.image.load(f"fig/explosion.gif")
        self.img_f = pg.transform.flip(self.img, True, True)
        self.rct = self.img.get_rect()
        self.rct.center = bomb.center
    def update(self, screen: pg.Surface):
        """
        引数 表示したい画面のSurface型
        表示時間のカウントを進める
        時間によって爆発画像の切り替えを行う
        """
        self.life -= 1
        if self.life > 0 :
            if self.life % 10 == 0:
                screen.blit(self.img, self.rct)
            else:
                screen.blit(self.img_f, self.rct)

def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((300, 200))
    # bomb = Bomb((255,0,0),10) 
    bombs = [Bomb((255, 0, 0), 10) for i in range(NUM_OF_BOMBS)]
    beams = []
    explosions = []
    # beam = None # ゲーム初期化時にはビームは存在しない
    score = Score()
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # スペースキー押下でBeamクラスのインスタンス生成
                beams.append(Beam(bird))
        screen.blit(bg_img, [0, 0])

        for bomb in bombs: 
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Game Over", True, (255, 0, 0))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                time.sleep(1)
                return

        for i, bomb in enumerate(bombs):
            for id,beam in enumerate(beams):
                if beam.rct.colliderect(bomb.rct):
                    # ビームと爆弾の衝突判定
                    explosions.append(Explosion(bombs[i].rct))
                    beams[id], bombs[i] = None, None
                    bird.change_img(6,screen)
                    score.score += 1
                    beams = [beam for beam in beams if beam is not None]
        
        bombs = [bomb for bomb in bombs if bomb is not None]
        explosions = [explosion for explosion in explosions if explosion.life > 0]

        for id,beam in enumerate(beams):
            if check_bound(beam.rct) != (True, True):
                beams[id] = None
        beams = [beam for beam in beams if beam is not None]

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for beam in beams:
            beam.update(screen)
        for bomb in bombs: 
            bomb.update(screen)
        for explosion in explosions: 
            explosion.update(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
