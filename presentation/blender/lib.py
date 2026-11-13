"""Procedural chess pieces, Monomakh's cap, materials and studio rig for Cycles renders."""
import bpy, bmesh, math, random
from mathutils import Vector

D = bpy.data


def reset(samples=128, w=1920, h=1080):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    c = sc.cycles
    c.device = 'CPU'; c.samples = samples; c.use_denoising = True; c.use_adaptive_sampling = True; c.adaptive_threshold = 0.02
    c.max_bounces = 6; c.glossy_bounces = 4; c.diffuse_bounces = 2; c.transmission_bounces = 4; c.caustics_reflective = False; c.caustics_refractive = False
    sc.render.resolution_x = w; sc.render.resolution_y = h; sc.render.threads_mode = 'AUTO'
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    wd = D.worlds.new('w'); sc.world = wd; wd.use_nodes = True
    wd.node_tree.nodes['Background'].inputs[0].default_value = (0.006, 0.003, 0.008, 1)
    return sc


# ---------- materials ----------
def principled(name, **kw):
    m = D.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    for k, v in kw.items(): b.inputs[k].default_value = v
    return m


def mats():
    M = {}
    M['gold'] = principled('gold', **{'Base Color': (1.0, 0.70, 0.27, 1), 'Metallic': 1.0, 'Roughness': 0.17})
    M['gold_r'] = principled('gold_r', **{'Base Color': (0.92, 0.50, 0.13, 1), 'Metallic': 1.0, 'Roughness': 0.3})
    mb = principled('marble', **{'Base Color': (0.86, 0.81, 0.72, 1), 'Roughness': 0.22, 'Subsurface Weight': 0.35, 'Subsurface Scale': 0.06, 'Coat Weight': 0.4, 'Coat Roughness': 0.1})
    nt = mb.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.2; nz.inputs['Detail'].default_value = 9; nz.inputs['Distortion'].default_value = 2.5
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.46; rp.color_ramp.elements[0].color = (0.86, 0.82, 0.74, 1); rp.color_ramp.elements[1].position = 0.60; rp.color_ramp.elements[1].color = (0.60, 0.54, 0.49, 1)
    e = rp.color_ramp.elements.new(0.53); e.color = (0.80, 0.75, 0.67, 1)
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    M['marble'] = mb
    M['obsidian'] = principled('obsidian', **{'Base Color': (0.012, 0.008, 0.014, 1), 'Roughness': 0.12, 'Coat Weight': 1.0})
    M['ruby'] = principled('ruby', **{'Base Color': (0.55, 0.0, 0.03, 1), 'Roughness': 0.03, 'Coat Weight': 1.0, 'Emission Color': (0.6, 0.0, 0.03, 1), 'Emission Strength': 0.25})
    M['emerald'] = principled('emerald', **{'Base Color': (0.0, 0.32, 0.12, 1), 'Roughness': 0.03, 'Coat Weight': 1.0, 'Emission Color': (0.0, 0.4, 0.15, 1), 'Emission Strength': 0.2})
    M['sapphire'] = principled('sapphire', **{'Base Color': (0.01, 0.06, 0.5, 1), 'Roughness': 0.03, 'Coat Weight': 1.0, 'Emission Color': (0.02, 0.1, 0.7, 1), 'Emission Strength': 0.2})
    M['pearl'] = principled('pearl', **{'Base Color': (0.92, 0.88, 0.82, 1), 'Roughness': 0.18, 'Coat Weight': 1.0, 'Subsurface Weight': 0.2, 'Subsurface Scale': 0.02})
    M['furbase'] = principled('furbase', **{'Base Color': (0.03, 0.015, 0.008, 1), 'Roughness': 0.9})
    hm = D.materials.new('hair'); hm.use_nodes = True; nt = hm.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    hb = nt.nodes.new('ShaderNodeBsdfHairPrincipled'); hb.parametrization = 'COLOR'
    hb.inputs['Color'].default_value = (0.16, 0.075, 0.03, 1); hb.inputs['Roughness'].default_value = 0.35
    nt.links.new(hb.outputs[0], [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0].inputs['Surface'])
    M['hair'] = hm
    # floor: glossy checker board
    f = principled('floor', **{'Roughness': 0.2, 'Coat Weight': 0.3, 'Coat Roughness': 0.15})
    nt = f.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); ch = nt.nodes.new('ShaderNodeTexChecker'); ch.inputs['Scale'].default_value = 1.0
    ch.inputs['Color1'].default_value = (0.10, 0.008, 0.02, 1); ch.inputs['Color2'].default_value = (0.008, 0.006, 0.010, 1)
    nt.links.new(tc.outputs['Object'], ch.inputs['Vector']); nt.links.new(ch.outputs['Color'], b.inputs['Base Color'])
    M['floor'] = f
    M['wall'] = principled('wall', **{'Base Color': (0.16, 0.012, 0.03, 1), 'Roughness': 0.9})
    return M


# ---------- geometry helpers ----------
def catmull(p0, p1, p2, p3, n):
    out = []
    for i in range(n):
        t = i / n; t2 = t * t; t3 = t2 * t
        out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    return out


def profile(pts, n=8):
    """pts: (r, z, 'c'|'s'). Corners split smooth runs."""
    runs, cur = [], [pts[0]]
    for p in pts[1:]:
        cur.append(p)
        if p[2] == 'c': runs.append(cur); cur = [p]
    if len(cur) > 1: runs.append(cur)
    out = []
    for run in runs:
        q = [(p[0], p[1]) for p in run]
        if len(q) == 2: out += [q[0]]
        else:
            e = [q[0]] + q + [q[-1]]
            for i in range(1, len(e) - 2): out += catmull(e[i - 1], e[i], e[i + 1], e[i + 2], n)
    out.append((pts[-1][0], pts[-1][1]))
    return [(max(r, 0.0), z) for r, z in out]


def finish(ob, mat, bevel=0.006, smooth=True):
    me = ob.data
    if smooth:
        for p in me.polygons: p.use_smooth = True
    me.materials.append(mat)
    if bevel:
        bv = ob.modifiers.new('bv', 'BEVEL'); bv.width = bevel; bv.segments = 3; bv.limit_method = 'ANGLE'; bv.angle_limit = math.radians(28)
        wn = ob.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.keep_sharp = False
    return ob


def lathe(name, pts, mat, segs=96, bevel=0.006, n=8):
    prof = profile(pts, n)
    bm = bmesh.new(); rings = []
    for r, z in prof:
        if r < 1e-5: rings.append([bm.verts.new((0, 0, z))])
        else: rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / segs), r * math.sin(2 * math.pi * i / segs), z)) for i in range(segs)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1: continue
        for i in range(segs):
            j = (i + 1) % segs
            try:
                if len(a) == 1: bm.faces.new((a[0], b[i], b[j]))
                elif len(b) == 1: bm.faces.new((a[i], a[j], b[0]))
                else: bm.faces.new((a[i], a[j], b[j], b[i]))
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = D.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = D.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    return finish(ob, mat, bevel)


def prim(kind, mat, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), bevel=0.0, **kw):
    getattr(bpy.ops.mesh, 'primitive_' + kind + '_add')(location=loc, rotation=rot, **kw)
    ob = bpy.context.object; ob.scale = scale
    return finish(ob, mat, bevel, smooth=kind != 'cube')


def box(mat, size, loc, bevel=0.008, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object; ob.scale = size
    bpy.ops.object.transform_apply(scale=True)
    return finish(ob, mat, bevel, smooth=True)


def arc_block(mat, r0, r1, z0, z1, a0, a1, n=10):
    bm = bmesh.new(); L = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n; c, s = math.cos(a), math.sin(a)
        L.append([bm.verts.new((r * c, r * s, z)) for r, z in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for a, b in zip(L, L[1:]):
        for k in range(4): bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
    bm.faces.new(L[0]); bm.faces.new(L[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = D.meshes.new('arc'); bm.to_mesh(me); bm.free()
    ob = D.objects.new('arc', me); bpy.context.scene.collection.objects.link(ob)
    return finish(ob, mat, 0.006)


def group(name, children, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    e = D.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    for c in children: c.parent = e
    e.location = loc; e.rotation_euler = rot; e.scale = (scale,) * 3
    return e


# ---------- chess pieces ----------
def foot(k=1.0):
    return [(0, 0, 'c'), (.400 * k, 0, 'c'), (.412 * k, .035, 's'), (.400 * k, .075, 'c'), (.365 * k, .085, 'c'), (.365 * k, .115, 'c'),
            (.385 * k, .125, 's'), (.395 * k, .160, 's'), (.375 * k, .198, 'c'), (.315 * k, .21, 'c')]


def collar(r, z, w=1.0):
    return [(r + .10 * w, z, 'c'), (r + .118 * w, z + .028, 's'), (r + .10 * w, z + .056, 'c'), (r + .035, z + .066, 'c'), (r + .035, z + .09, 'c'),
            (r + .075 * w, z + .098, 'c'), (r + .088 * w, z + .12, 's'), (r + .075 * w, z + .142, 'c'), (r + .02, z + .152, 'c')]


def king(mat, **kw):
    p = foot() + [(.30, .24, 's'), (.215, .40, 's'), (.160, .66, 's'), (.132, .98, 's'), (.128, 1.22, 's'), (.142, 1.33, 'c')] + collar(.142, 1.34) + \
        [(.158, 1.52, 's'), (.185, 1.66, 's'), (.245, 1.80, 'c'), (.262, 1.815, 's'), (.262, 1.845, 's'), (.245, 1.86, 'c'), (.19, 1.885, 's'), (.10, 1.925, 's'), (.05, 1.94, 'c'), (.05, 1.97, 'c'), (0, 1.97, 'c')]
    body = lathe('king', p, mat)
    c1 = box(mat, (.062, .062, .30), (0, 0, 2.11)); c2 = box(mat, (.20, .062, .062), (0, 0, 2.15))
    return group('king', [body, c1, c2], **kw)


def queen(mat, **kw):
    p = foot(.96) + [(.29, .24, 's'), (.205, .40, 's'), (.150, .64, 's'), (.124, .92, 's'), (.120, 1.10, 's'), (.134, 1.20, 'c')] + collar(.134, 1.21) + \
        [(.150, 1.38, 's'), (.175, 1.50, 's'), (.235, 1.63, 'c'), (.245, 1.66, 'c'), (.20, 1.66, 'c'), (.17, 1.63, 's'), (.12, 1.70, 's'), (.05, 1.745, 's'), (0, 1.75, 'c')]
    body = lathe('queen', p, mat); ch = [body]
    for i in range(9):
        a = 2 * math.pi * i / 9; ch.append(prim('uv_sphere', mat, (.225 * math.cos(a), .225 * math.sin(a), 1.675), radius=.038, segments=24, ring_count=12))
    ch.append(prim('uv_sphere', mat, (0, 0, 1.79), radius=.058, segments=32, ring_count=16))
    return group('queen', ch, **kw)


def bishop(mat, **kw):
    p = foot(.9) + [(.27, .23, 's'), (.19, .37, 's'), (.138, .58, 's'), (.116, .82, 's'), (.114, .95, 's'), (.126, 1.03, 'c')] + collar(.126, 1.04, .9) + \
        [(.135, 1.21, 's'), (.178, 1.31, 's'), (.172, 1.44, 's'), (.105, 1.58, 's'), (.045, 1.655, 'c'), (.04, 1.67, 'c'), (0, 1.67, 'c')]
    body = lathe('bishop', p, mat)
    cut = box(mat, (.5, .035, .22), (.11, 0, 1.50), bevel=0, rot=(0, math.radians(-38), 0)); cut.hide_render = True; cut.display_type = 'WIRE'
    bo = body.modifiers.new('slit', 'BOOLEAN'); bo.object = cut; bo.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = body; bpy.ops.object.modifier_move_to_index(modifier='slit', index=0)
    ball = prim('uv_sphere', mat, (0, 0, 1.715), radius=.055, segments=32, ring_count=16)
    return group('bishop', [body, cut, ball], **kw)


def rook(mat, **kw):
    p = foot(.92) + [(.285, .235, 's'), (.235, .36, 's'), (.205, .60, 's'), (.200, .86, 'c'), (.285, .90, 'c'), (.30, .925, 's'), (.30, 1.10, 'c'), (.225, 1.10, 'c'), (.225, 1.04, 'c'), (0, 1.04, 'c')]
    body = lathe('rook', p, mat); ch = [body]
    for i in range(6):
        a = 2 * math.pi * i / 6; ch.append(arc_block(mat, .225, .30, 1.09, 1.21, a - .33, a + .33))
    return group('rook', ch, **kw)


def pawn(mat, **kw):
    p = foot(.78) + [(.235, .225, 's'), (.155, .35, 's'), (.108, .55, 's'), (.098, .66, 'c'), (.185, .675, 'c'), (.20, .70, 's'), (.185, .725, 'c'), (.105, .735, 'c')]
    R, cz = .158, .875
    for i in range(0, 17):
        a = math.radians(-62 + i * (152 / 16)); p.append((R * math.cos(a), cz + R * math.sin(a), 's'))
    p.append((0, cz + R, 'c'))
    return group('pawn', [lathe('pawn', p, mat, n=4)], **kw)


# ---------- Monomakh's cap ----------
def monomakh(M, fur=True, **kw):
    ch = []
    dome = lathe('dome', [(0, .10, 'c'), (.56, .10, 'c'), (.585, .22, 's'), (.565, .42, 's'), (.48, .62, 's'), (.33, .77, 's'), (.16, .86, 's'), (.075, .885, 'c'), (0, .885, 'c')], M['cap_gold'], bevel=0, n=10)
    ch.append(dome)
    for i in range(8):  # ribs between plates
        a = 2 * math.pi * i / 8 + math.pi / 8
        rib = lathe('rib', [(0, 0, 'c'), (.012, 0, 'c'), (.012, 1, 'c'), (0, 1, 'c')], M['gold'], segs=8, bevel=0)
        cu = D.curves.new('ribc', 'CURVE'); cu.dimensions = '3D'; sp = cu.splines.new('NURBS')
        pts = [(.59, .2), (.572, .42), (.487, .625), (.336, .777), (.165, .868), (.08, .892)]
        sp.points.add(len(pts) - 1)
        for pt, (r, z) in zip(sp.points, pts): pt.co = (r * math.cos(a), r * math.sin(a), z, 1)
        sp.use_endpoint_u = True; cu.bevel_depth = .011; cu.bevel_resolution = 4
        co = D.objects.new('ribc', cu); bpy.context.scene.collection.objects.link(co); co.data.materials.append(M['gold'])
        D.objects.remove(rib); ch.append(co)
    gems = [M['ruby'], M['emerald'], M['sapphire']]
    for i in range(8):  # stones in bezels + pearls
        a = 2 * math.pi * i / 8
        for (r, z, s, tilt) in ((.578, .40, .062, 80), (.455, .665, .045, 55)):
            n = Vector((math.cos(a), math.sin(a), 0)); pos = (r * n.x, r * n.y, z)
            rot = (0, math.radians(tilt), a)
            g = prim('uv_sphere', gems[(i + (0 if tilt == 80 else 1)) % 3], pos, (s, s * 1.3, s * .5) if False else (s * .55, s, s * 1.25), rot=(0, 0, a), radius=1, segments=32, ring_count=16)
            bz = prim('torus', M['gold'], pos, (1, 1, 1), rot=rot, major_radius=s * 1.05, minor_radius=s * .22, major_segments=32, minor_segments=10)
            bz.scale = (1.25, 1, 1) ; ch += [g, bz]
            for dz in (-1, 1):
                ch.append(prim('uv_sphere', M['pearl'], ((r - (.02 if dz > 0 else -.005)) * n.x + .0, (r - (.02 if dz > 0 else -.005)) * n.y, z + dz * s * 2.1), radius=s * .42, segments=24, ring_count=12))
    # finial + cross
    ch.append(lathe('fin', [(0, .88, 'c'), (.11, .88, 'c'), (.125, .895, 's'), (.11, .91, 'c'), (.06, .92, 's'), (.045, .95, 's'), (.10, 1.0, 's'), (.115, 1.06, 's'), (.07, 1.12, 's'), (.03, 1.145, 'c'), (0, 1.145, 'c')], M['gold'], segs=48, bevel=.003))
    for i in range(4):
        a = math.pi / 4 + i * math.pi / 2; ch.append(prim('uv_sphere', M['pearl'], (.125 * math.cos(a), .125 * math.sin(a), 1.05), radius=.032, segments=20, ring_count=10))
    ch.append(box(M['gold'], (.036, .036, .30), (0, 0, 1.29), bevel=.004)); ch.append(box(M['gold'], (.19, .036, .036), (0, 0, 1.33), bevel=.004))
    for x, z in ((-.11, 1.33), (.11, 1.33), (0, 1.455)): ch.append(prim('uv_sphere', M['pearl'], (x, 0, z), radius=.03, segments=20, ring_count=10))
    # fur trim
    bpy.ops.mesh.primitive_torus_add(location=(0, 0, .13), major_radius=.60, minor_radius=.165, major_segments=96, minor_segments=32)
    t = bpy.context.object; t.scale = (1, 1, .92); bpy.ops.object.transform_apply(scale=True)
    for p_ in t.data.polygons: p_.use_smooth = True
    t.data.materials.append(M['furbase']); t.data.materials.append(M['hair'])
    if fur:
        md = t.modifiers.new('fur', 'PARTICLE_SYSTEM'); ps = md.particle_system.settings
        ps.type = 'HAIR'; ps.count = 9000; ps.hair_length = .13; ps.hair_step = 5; ps.material = 2
        ps.child_type = 'INTERPOLATED'; ps.rendered_child_count = 14; ps.child_length = 1.0; ps.clump_factor = .35; ps.clump_shape = .2
        ps.roughness_1 = .04; ps.roughness_1_size = .6; ps.roughness_endpoint = .06; ps.roughness_2 = .02
        ps.root_radius = 1.0; ps.tip_radius = 0.1; ps.radius_scale = .0035
        ps.normal_factor = .05; ps.tangent_factor = 0.0; ps.factor_random = .02; ps.length_random = .4
        ps.effector_weights.gravity = 0
    ch.append(t)
    return group('cap', ch, **kw)


def cap_gold(M):
    """Gold with fine filigree bump for the cap plates."""
    m = principled('cap_gold', **{'Base Color': (1.0, 0.68, 0.25, 1), 'Metallic': 1.0, 'Roughness': 0.24})
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); v = nt.nodes.new('ShaderNodeTexVoronoi'); v.feature = 'DISTANCE_TO_EDGE'; v.inputs['Scale'].default_value = 38
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[1].position = 0.12
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.55; bp.inputs['Distance'].default_value = 0.01; bp.invert = True
    nt.links.new(tc.outputs['Object'], v.inputs['Vector']); nt.links.new(v.outputs['Distance'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    M['cap_gold'] = m


# ---------- stage ----------
def area(name, loc, target, size, power, color=(1, 1, 1), size_y=None, spread=None):
    l = D.lights.new(name, 'AREA'); l.energy = power; l.color = color; l.size = size
    if size_y: l.shape = 'RECTANGLE'; l.size_y = size_y
    if spread: l.spread = math.radians(spread)
    o = D.objects.new(name, l); bpy.context.scene.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o


def stage(M, center=(0, 0, 0), key=1.0, rim=1.0, floor=True, wall=True, offset=(0.5, 0.5)):
    cx, cy, cz = center
    if floor:
        bpy.ops.mesh.primitive_plane_add(size=120, location=(offset[0], offset[1], 0)); f = bpy.context.object; f.data.materials.append(M['floor'])
    if wall:
        bpy.ops.mesh.primitive_plane_add(size=140, location=(0, 34, 20), rotation=(math.radians(90), 0, 0)); w = bpy.context.object; w.data.materials.append(M['wall'])
        s = D.lights.new('wallspot', 'SPOT'); s.energy = 9000 * rim; s.color = (1.0, 0.18, 0.28); s.spot_size = math.radians(70); s.spot_blend = 1.0
        so = D.objects.new('wallspot', s); bpy.context.scene.collection.objects.link(so); so.location = (cx + 3, 6, 5)
        so.rotation_euler = (Vector((cx + 4, 34, 7)) - Vector(so.location)).to_track_quat('-Z', 'Y').to_euler()
    lights = [area('key', (cx - 5, cy - 6, 7.5), (cx, cy, 1.0), 12, 1700 * key, (1.0, 0.90, 0.76)),
              area('strip', (cx + 6, cy - 2.5, 3.2), (cx, cy, 1.2), 1.5, 800 * key, (1.0, 0.95, 0.9), size_y=7),
              area('top', (cx, cy + 1, 9), (cx, cy, 0), 10, 400 * key, (1.0, 0.86, 0.7)),
              area('rimR', (cx + 4.5, cy + 6, 4.5), (cx, cy, 1.3), 3, 1100 * rim, (1.0, 0.22, 0.30)),
              area('rimL', (cx - 5.5, cy + 5, 3.5), (cx, cy, 1.3), 3, 700 * rim, (1.0, 0.62, 0.25))]
    lights.append(area('sheen', (cx, cy + 22, 4.5), (cx, cy, 1), 16, 2600 * rim, (1.0, 0.42, 0.38), size_y=4))
    if floor:
        ex = D.collections.new('nofloor'); ex.objects.link(f); ex.collection_objects[0].light_linking.link_state = 'EXCLUDE'
        for l in lights: l.light_linking.receiver_collection = ex
        fill = area('floorfill', (cx - 7, cy - 26, 10), (cx, cy, 0), 14, 11000 * key, (1.0, 0.9, 0.8))
        inc = D.collections.new('onlyfloor'); inc.objects.link(f); fill.light_linking.receiver_collection = inc


def camera(loc, target, lens=70, fstop=1.2, focus=None, shift_x=0.0, shift_y=0.0):
    c = D.cameras.new('cam'); c.lens = lens; c.sensor_width = 36; c.shift_x = shift_x; c.shift_y = shift_y
    o = D.objects.new('cam', c); bpy.context.scene.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    c.dof.use_dof = True; c.dof.aperture_fstop = fstop; c.dof.focus_distance = (Vector(focus or target) - Vector(loc)).length
    bpy.context.scene.camera = o
    return o


def project(cam, p):
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    v = world_to_camera_view(bpy.context.scene, cam, Vector(p))
    return [round(v.x * 1920, 1), round((1 - v.y) * 1080, 1)]


def topple(ob, loc, yaw, r):
    """Lay a piece on its side; r ≈ its base radius."""
    ob.rotation_euler = (0, math.radians(90), yaw); ob.location = (loc[0], loc[1], r)
