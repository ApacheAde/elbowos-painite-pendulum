"""Painite Pendulum — neon wrecking-bob arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get(
    "ELBOWOS_MP4",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "PAINITE_PENDULUM_ElbowOS.mp4"),
)
PIVX, PIVY, L = 540, 300, 820
WINE, INK = (22, 8, 28), (8, 2, 12)
COPPER, GOLD = (255, 140, 58), (255, 214, 108)
JADE, MAG = (72, 255, 176), (255, 64, 128)
CREAM, SLAG = (255, 236, 214), (90, 70, 84)
random.seed(11)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        pygame.display.set_caption("Painite Pendulum")
        self.font = pygame.font.Font(None, 92)
        self.mid = pygame.font.Font(None, 54)
        self.small = pygame.font.Font(None, 40)
        self.reset()

    def reset(self):
        self.ang, self.omg = -0.35, 0.0
        self.score, self.combo, self.lives = 0, 0, 3
        self.shake, self.flash = 0.0, 0
        self.parts, self.pops = [], []
        self.gems = []
        for i in range(9):
            self.spawn(i)

    def spawn(self, slot):
        a = -1.05 + slot * (2.1 / 8)
        r = L - 30 + (slot % 3) * 46
        kind = "slag" if slot % 5 == 4 else "ore"
        self.gems.append({"a": a, "r": r, "kind": kind, "pulse": random.random() * 6})

    def bob(self):
        return PIVX + math.sin(self.ang) * L, PIVY + math.cos(self.ang) * L

    def step(self, left, right):
        torque = (-0.0024 if left else 0) + (0.0024 if right else 0)
        self.omg = (self.omg + torque) * 0.991
        self.ang += self.omg
        if self.ang > 1.22:
            self.ang, self.omg = 1.22, -abs(self.omg) * 0.45
        if self.ang < -1.22:
            self.ang, self.omg = -1.22, abs(self.omg) * 0.45
        bx, by = self.bob()
        for g in self.gems:
            gx = PIVX + math.sin(g["a"]) * g["r"]
            gy = PIVY + math.cos(g["a"]) * g["r"]
            if (bx - gx) ** 2 + (by - gy) ** 2 < 78 ** 2:
                self.hit(g, gx, gy)
                g["a"] = random.uniform(-1.05, 1.05)
                g["r"] = random.choice((L - 20, L + 20, L + 70))
                g["kind"] = "slag" if random.random() < 0.22 else "ore"
        self.parts = [p for p in self.parts if p[4] > 0]
        for p in self.parts:
            p[0] += p[2]; p[1] += p[3]; p[3] += 0.35; p[4] -= 1
        self.pops = [(x, y, t, n, c) for x, y, t, n, c in self.pops if t > 0]
        self.pops = [(x, y - 2, t - 1, n, c) for x, y, t, n, c in self.pops]
        self.shake = max(0, self.shake - 1)
        self.flash = max(0, self.flash - 1)

    def hit(self, g, x, y):
        if g["kind"] == "slag":
            self.combo = 0
            self.lives = max(0, self.lives - 1)
            self.score = max(0, self.score - 25)
            self.flash, self.shake = 8, 14
            col = MAG
            if self.lives == 0:
                self.lives = 3
        else:
            self.combo += 1
            gain = 10 * self.combo
            self.score += gain
            self.shake = 6
            col = GOLD if self.combo > 2 else JADE
            self.pops.append([x, y - 20, 28, f"+{gain}", col])
        for _ in range(16):
            a = random.random() * math.tau
            sp = random.uniform(2, 9)
            self.parts.append([x, y, math.cos(a) * sp, math.sin(a) * sp, random.randint(12, 26), col])

    def auto(self):
        best, bd = None, 1e9
        for g in self.gems:
            if g["kind"] == "slag":
                continue
            d = abs(g["a"] - self.ang) + abs(g["r"] - L) / 400
            if d < bd:
                bd, best = d, g
        if not best:
            return False, False
        want = best["a"]
        if self.ang < want - 0.04:
            return False, True
        if self.ang > want + 0.04:
            return True, False
        return False, False

    def draw(self, surf):
        surf.fill(INK)
        for i, col in enumerate(((40, 12, 36), (70, 22, 28), (28, 10, 32))):
            pygame.draw.circle(surf, col, (PIVX, PIVY + 200), 780 - i * 160)
        ox = int(random.randint(-4, 4) * (self.shake > 0))
        oy = int(random.randint(-3, 3) * (self.shake > 0))
        pygame.draw.circle(surf, COPPER, (PIVX, PIVY), 18)
        bx, by = self.bob()
        pygame.draw.line(surf, (180, 120, 70), (PIVX, PIVY), (bx + ox, by + oy), 8)
        for t in range(1, 8):
            k = t / 8
            pygame.draw.circle(surf, GOLD, (int(PIVX + (bx - PIVX) * k) + ox, int(PIVY + (by - PIVY) * k) + oy), 5)
        for g in self.gems:
            gx = int(PIVX + math.sin(g["a"]) * g["r"]) + ox
            gy = int(PIVY + math.cos(g["a"]) * g["r"]) + oy
            g["pulse"] += 0.15
            rad = 28 + int(3 * math.sin(g["pulse"]))
            if g["kind"] == "slag":
                pygame.draw.circle(surf, SLAG, (gx, gy), rad)
                for k in range(6):
                    a = g["pulse"] + k * 1.05
                    pygame.draw.line(surf, MAG, (gx, gy), (gx + int(math.cos(a) * 40), gy + int(math.sin(a) * 40)), 4)
            else:
                col = JADE if int(g["pulse"]) % 2 == 0 else GOLD
                pts = [(gx + int(math.cos(g["pulse"] + k) * rad), gy + int(math.sin(g["pulse"] + k) * rad)) for k in (0, 2.1, 4.2)]
                pygame.draw.polygon(surf, col, pts)
                pygame.draw.polygon(surf, CREAM, pts, 3)
        pygame.draw.circle(surf, COPPER, (int(bx) + ox, int(by) + oy), 46)
        pygame.draw.circle(surf, GOLD, (int(bx) + ox, int(by) + oy), 28)
        pygame.draw.circle(surf, CREAM, (int(bx) - 8 + ox, int(by) - 8 + oy), 10)
        for p in self.parts:
            pygame.draw.circle(surf, p[5], (int(p[0]), int(p[1])), max(2, p[4] // 6))
        if self.flash:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((255, 40, 80, 70))
            surf.blit(veil, (0, 0))
        title = self.font.render("PAINITE PENDULUM", True, GOLD)
        surf.blit(title, title.get_rect(center=(W // 2, 110)))
        sc = self.mid.render(f"SCORE  {self.score}", True, CREAM)
        surf.blit(sc, sc.get_rect(center=(W // 2, 190)))
        combo = self.small.render(f"COMBO x{self.combo}    LIVES {self.lives}", True, JADE)
        surf.blit(combo, combo.get_rect(center=(W // 2, 1760)))
        tag = self.mid.render("x.com/ElbowOS", True, COPPER)
        surf.blit(tag, tag.get_rect(center=(W // 2, 1840)))
        for x, y, t, n, c in self.pops:
            lab = self.small.render(n, True, c)
            surf.blit(lab, lab.get_rect(center=(int(x), int(y))))

    def record(self):
        os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for i in range(frames):
                left, right = self.auto()
                if i % 18 < 7 and not left and not right:
                    left, right = self.ang < 0, self.ang >= 0
                self.step(left, right)
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            keys = pygame.key.get_pressed()
            left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            self.step(left, right)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()
        pygame.quit()

if __name__ == "__main__":
    main()
