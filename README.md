# Painite Pendulum

Full-colour Python 3 neon wrecking-bob arcade for [ElbowOS](https://x.com/ElbowOS).

Pump a copper pendulum and smash jade ore for combo points. Magenta slag spikes break the streak. This is an original arcade — not a ROM, not an emulator.

## Play

```bash
pip install -r requirements.txt
python3 painite_pendulum.py --play
```

A / Left pumps left. D / Right pumps right. R restarts.

## Record a 9:16 reel

```bash
python3 painite_pendulum.py --record
```

Writes a 1080x1920 h264 clip (15s @ 30fps, yuv420p, CRF 20, +faststart) with title, score, and `x.com/ElbowOS` burned into the frames. Headless recording uses `SDL_VIDEODRIVER=dummy`.

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/1y-4lxvQJFBOJZQldoLEfk92hLiPTI8OZ/view
