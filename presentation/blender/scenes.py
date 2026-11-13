"""Usage: python3 scenes.py <scene|all> [preview]"""
import sys, os, json, math, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import lib as L

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'renders')
os.makedirs(OUT, exist_ok=True)
PREVIEW = len(sys.argv) > 2 and sys.argv[2] == 'preview'
LABELS = {}


def begin():
    sc = L.reset(samples=40 if PREVIEW else 96, w=800 if PREVIEW else 1920, h=450 if PREVIEW else 1080)
    M = L.mats(); L.cap_gold(M)
    return sc, M


def end(name, sc):
    sc.render.filepath = os.path.join(OUT, name + ('_p' if PREVIEW else '') + '.png')
    t = time.time(); bpy.ops.render.render(write_still=True); print(f'## {name} rendered in {time.time() - t:.0f}s', flush=True)


def test():
    sc, M = begin(); L.stage(M)
    L.monomakh(M, loc=(-2.6, 0, 0), scale=1.5, rot=(0, 0, .4))
    for i, (fn, m) in enumerate([(L.king, 'gold'), (L.queen, 'marble'), (L.bishop, 'marble'), (L.rook, 'marble'), (L.pawn, 'marble'), (L.king, 'obsidian')]):
        fn(M[m], loc=(-1 + i * 1.0, 0, 0))
    L.camera((1.2, -9.5, 2.0), (0.8, 0, .9), lens=60, fstop=4)
    end('test', sc)


def s1():  # title: Monomakh's cap
    sc, M = begin(); L.stage(M, center=(0, 0, 0))
    L.monomakh(M, loc=(0, 0, 0), scale=1.75, rot=(0, 0, .35))
    L.pawn(M['marble'], loc=(-2, 3, 0)); L.pawn(M['marble'], loc=(2, 4, 0)); L.rook(M['marble'], loc=(-3, 6, 0)); L.bishop(M['marble'], loc=(3, 7, 0)); L.pawn(M['marble'], loc=(-5, 8, 0))
    L.camera((0.3, -9, 2.0), (0, 0, 1.2), lens=60, fstop=1.6, focus=(0, -0.9, 1.2), shift_x=-.235)
    end('s1', sc)


def s2():  # king with estates around
    sc, M = begin(); L.stage(M)
    L.king(M['gold'], loc=(0, 0, 0), scale=1.25)
    for (fn, x, y) in [(L.queen, -1, 1), (L.bishop, 1, 1), (L.rook, 2, 0), (L.rook, -2, 0), (L.bishop, -2, 2), (L.pawn, -1, -1), (L.pawn, 1, -1), (L.pawn, 2, -2), (L.pawn, 0, -2), (L.pawn, 3, 1), (L.queen, 2, 3), (L.pawn, 0, 3)]:
        fn(M['marble'], loc=(x, y, 0))
    L.camera((0.4, -11, 2.7), (0.3, 0, 1.15), lens=56, fstop=1.6, focus=(0, 0, 1.3), shift_x=-.2)
    end('s2', sc)


def s3():  # macro
    sc, M = begin(); L.stage(M, key=.8)
    L.king(M['gold'], loc=(0, 0, 0)); L.queen(M['marble'], loc=(1, 1, 0)); L.bishop(M['marble'], loc=(-1, 2, 0)); L.rook(M['marble'], loc=(2, 3, 0)); L.pawn(M['marble'], loc=(1, -1, 0)); L.pawn(M['marble'], loc=(-1, 0, 0))
    L.camera((0.5, -5.6, 1.8), (0, 0, 1.72), lens=85, fstop=1.4, focus=(0, 0, 1.7), shift_x=-.27)
    end('s3', sc)


def s4():  # five kings in a row
    sc, M = begin(); L.stage(M, center=(0, 0, 0))
    lab = []
    for i in range(5):
        x = -4 + i * 2; ru = i == 4; s = 1.0 + i * 0.06 + (0.22 if ru else 0)
        L.king(M['gold' if ru else 'marble'], loc=(x, 0, 0), scale=s); lab.append((x, s))
        L.pawn(M['marble'], loc=(x - 1, 2, 0))
    cam = L.camera((0, -16, 2.6), (0, 0, 2.0), lens=55, fstop=2.8, focus=(0, 0, 1.2))
    LABELS['s4'] = [{'top': L.project(cam, (x, 0, 2.3 * s)), 'base': L.project(cam, (x, -0.75, 0))} for x, s in lab]
    end('s4', sc)


def s5():  # composition of the Zemsky Sobor
    sc, M = begin(); L.stage(M, center=(-2, 0, 0))
    L.box(M['obsidian'], (1.6, 1.6, .7), (-2.5, 3.5, .35), bevel=.03); L.box(M['gold'], (1.25, 1.25, .12), (-2.5, 3.5, .76), bevel=.02)
    L.king(M['gold'], loc=(-2.5, 3.5, .82), scale=1.25)
    L.queen(M['marble'], loc=(-5, 0, 0)); L.queen(M['marble'], loc=(-5.9, 1, 0), scale=.94)
    L.bishop(M['marble'], loc=(-2.5, 0, 0)); L.bishop(M['marble'], loc=(-3.4, .9, 0), scale=.95)
    L.rook(M['marble'], loc=(0, 0, 0)); L.pawn(M['marble'], loc=(.9, -.9, 0)); L.pawn(M['marble'], loc=(-.6, -1, 0)); L.pawn(M['marble'], loc=(1.1, .8, 0))
    cam = L.camera((-2.4, -15, 3.2), (-2.4, 0.5, 1.95), lens=50, fstop=2.8, focus=(-2.5, 0, 1), shift_x=.17)
    LABELS['s5'] = {'duma': L.project(cam, (-5.2, -1.0, 0)), 'sobor': L.project(cam, (-2.7, -1.0, 0)), 'zem': L.project(cam, (.3, -1.7, 0)), 'tsar': L.project(cam, (-2.5, 3.5, 3.95))}
    end('s5', sc)


def s6():  # timeline bars
    sc, M = begin(); L.stage(M, center=(0, 0, 0), offset=(0, 0.5))
    hs = [0.9, 1.25, 1.75, 2.7, 2.2, 1.1, 0.28]; lab = []
    random.seed(4)
    for i, h in enumerate(hs):
        x = -4.8 + i * 1.6; last = i == 6
        L.box(M['marble' if last else ('gold' if i == 3 else 'gold_r')], (1.0, 1.0, h), (x, 0, h / 2), bevel=.03, rot=(0, 0, .12 if last else 0))
        if last:
            for k in range(9): L.box(M['marble'], (random.uniform(.1, .28),) * 3, (x + random.uniform(-.7, .7), random.uniform(-1.3, -.6), .08), bevel=.01, rot=(random.random(), random.random(), random.random()))
        lab.append((x, h))
    L.king(M['gold'], loc=(-4.8 + 3 * 1.6, 0, 2.7), scale=.62)
    L.pawn(M['marble'], loc=(-4.8 + 6 * 1.6 + .1, .1, .28), scale=.6)
    cam = L.camera((0, -15, 3.0), (0, 0, 2.0), lens=47, fstop=4, focus=(0, 0, 1.2))
    LABELS['s6'] = [{'top': L.project(cam, (x, -.5, h + (1.45 if i == 3 else 0.72 if i == 6 else 0))), 'base': L.project(cam, (x, -1.1, 0))} for i, (x, h) in enumerate(lab)]
    end('s6', sc)


def s7():  # fallen estates, king stands
    sc, M = begin(); L.stage(M, key=.75, rim=1.3)
    L.king(M['gold'], loc=(0, 0, 0), scale=1.2)
    random.seed(11)
    for fn, x, y, yaw, r in [(L.queen, 1.6, -.6, .5, .39), (L.bishop, -1.5, -1.0, 2.6, .37), (L.rook, 1.2, 1.4, -1.0, .37), (L.pawn, -.9, -2.0, 1.3, .32), (L.pawn, 2.6, -1.9, -2.2, .32), (L.pawn, -2.3, .6, .2, .32), (L.bishop, 3.1, .9, 2.0, .37), (L.pawn, .5, -2.6, 2.9, .32)]:
        L.topple(fn(M['marble']), (x, y), yaw, r)
    L.camera((0.6, -9.5, 1.8), (0.4, 0, 1.2), lens=55, fstop=1.4, focus=(0, 0, 1.3), shift_x=-.2)
    end('s7', sc)


def s10():  # lone king
    sc, M = begin(); L.stage(M, key=.9, rim=1.4)
    L.king(M['gold'], loc=(0, 0, 0), scale=1.05)
    L.topple(L.pawn(M['marble']), (-1.5, -1.0), 2.4, .32)
    L.camera((0.3, -7.6, 1.2), (0, 0, 1.22), lens=60, fstop=1.4, focus=(0, 0, 1.5), shift_x=-.25)
    end('s10', sc)


def cut(name, fn, mat):  # transparent cut-outs
    sc, M = begin(); sc.render.film_transparent = True; L.stage(M, floor=False, wall=False)
    sc.render.resolution_x = 300 if PREVIEW else 900; sc.render.resolution_y = 450 if PREVIEW else 1350
    fn(M[mat]); L.camera((0, -9, 1.6), (0, 0, 1.12), lens=110, fstop=16)
    end(name, sc)


ALL = {'test': test, 's1': s1, 's2': s2, 's3': s3, 's4': s4, 's5': s5, 's6': s6, 's7': s7, 's10': s10,
       'cut_gold': lambda: cut('cut_gold', L.king, 'gold'), 'cut_marble': lambda: cut('cut_marble', L.king, 'marble')}
which = sys.argv[1].split(',') if sys.argv[1] != 'all' else [k for k in ALL if k != 'test']
for k in which: ALL[k]()
if LABELS:
    p = os.path.join(OUT, 'labels.json'); old = json.load(open(p)) if os.path.exists(p) else {}
    old.update(LABELS); json.dump(old, open(p, 'w'))
