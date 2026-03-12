"""
XlArch Renderer — ONE render function, multiple output adapters.
render() produces draw commands. Adapters translate to canvas JS or PPTX shapes.
"""

from engine import compute_layout, get_icon_path, get_all_icon_keys, NW, NH, IS, ZG, LG, LP, TP, GOV_OFF, LANE_COLORS, ARROW_COLOR

# ═══════════════════════════════════════════
#  DRAW COMMANDS — the universal language
# ═══════════════════════════════════════════
# Each command is a dict: {"type": "...", ...params}
# Types:
#   rect:  {x, y, w, h, fill, stroke, stroke_width, radius}
#   image: {x, y, w, h, src (icon key)}
#   text:  {x, y, w, text, size, color, bold, align}
#   line:  {x1, y1, x2, y2, color, width}
#   arrow: {points: [(x,y)...], color, width}  — polyline with arrowhead at end


def render(architecture):
    """Render architecture to a list of draw commands. Canvas + PPTX both consume this."""
    commands = []

    # ── Inject governance as real nodes in a "governance" lane
    arch = dict(architecture)
    gov = arch.get("governance", [])
    zones = list(arch.get("zones", []))
    lanes = list(arch.get("lanes", []))
    nodes = list(arch.get("nodes", []))
    edges = list(arch.get("edges", []))

    if gov and "governance" not in lanes:
        lanes.append("governance")
    
    for i, g in enumerate(gov):
        gid = f"gov_{g.get('icon', i)}"
        # Spread governance nodes across zones
        zone_idx = min(i, len(zones) - 1) if zones else 0
        zone = zones[zone_idx] if zones else "sources"
        nodes.append({
            "id": gid,
            "icon": g.get("icon", ""),
            "label": g.get("label", ""),
            "zone": zone,
            "lane": "governance",
        })

    arch["zones"] = zones
    arch["lanes"] = lanes
    arch["nodes"] = nodes
    arch["edges"] = edges

    positions, zone_gap, lane_gap = compute_layout(arch)
    title = arch.get("title", "")

    cw = LP + len(zones) * zone_gap + 60
    ch = TP + len(lanes) * lane_gap + 60

    # ── Title
    commands.append({"type": "text", "x": LP, "y": 15, "w": cw, "text": title,
                     "size": 14, "color": "#202124", "bold": True, "align": "left"})

    # ── Lane backgrounds
    for i, lane in enumerate(lanes):
        ly = TP + i * lane_gap - 18
        lw = len(zones) * zone_gap + 40
        lh = NH + 50
        fill = LANE_COLORS.get(lane, "#F5F5F5")
        commands.append({"type": "rect", "x": 25, "y": ly, "w": lw, "h": lh,
                        "fill": fill, "stroke": None, "stroke_width": 0, "radius": 8, "opacity": 0.3})

    # ── Zone labels
    for i, z in enumerate(zones):
        commands.append({"type": "text", "x": LP + i * zone_gap + 20, "y": 50, "w": NW,
                        "text": z.upper(), "size": 7, "color": "#BDBDBD", "bold": True, "align": "left"})

    # ── Edges (orthogonal)
    for e in edges:
        fp, tp = positions.get(e["from"]), positions.get(e["to"])
        if not fp or not tp:
            continue
        x1, y1 = fp["x"] + NW + 5, fp["y"] + NH / 2
        x2, y2 = tp["x"] - 5, tp["y"] + NH / 2

        if abs(y1 - y2) < 5:
            # Same lane — straight
            points = [(x1, y1), (x2, y2)]
        else:
            # Cross-lane — L-shape
            midX = (x1 + x2) / 2
            points = [(x1, y1), (midX, y1), (midX, y2), (x2, y2)]

        commands.append({"type": "arrow", "points": points,
                        "color": ARROW_COLOR, "width": 1,
                        "fromId": e["from"], "toId": e["to"]})

    # ── Nodes
    for n in nodes:
        p = positions.get(n["id"])
        if not p:
            continue
        x, y = p["x"], p["y"]
        nid = n["id"]

        # Card background
        commands.append({"type": "rect", "x": x, "y": y, "w": NW, "h": NH,
                        "fill": "#FFFFFF", "stroke": "#E0E4E8", "stroke_width": 0.5,
                        "radius": 10, "shadow": True, "nodeId": nid})

        # Icon
        commands.append({"type": "image", "x": x + (NW - IS) / 2, "y": y + 5,
                        "w": IS, "h": IS, "src": n.get("icon", ""), "nodeId": nid})

        # Label
        commands.append({"type": "text", "x": x, "y": y + NH - 14, "w": NW,
                        "text": n.get("label", ""), "size": 9, "color": "#3C4043",
                        "bold": False, "align": "center", "nodeId": nid})

        # Step badge
        if "step" in n:
            bx, by, bsz = x + NW - 14, y - 6, 20
            commands.append({"type": "rect", "x": bx, "y": by, "w": bsz, "h": 16,
                            "fill": "#4285F4", "stroke": None, "stroke_width": 0,
                            "radius": 4, "nodeId": nid})
            commands.append({"type": "text", "x": bx, "y": by + 1, "w": bsz,
                            "text": str(n["step"]), "size": 9, "color": "#FFFFFF",
                            "bold": True, "align": "center", "nodeId": nid})

    # Governance items are now regular nodes in "governance" lane
    # They render as cards with the same style — draggable, selectable, deletable

    return {"commands": commands, "width": cw, "height": ch, "positions": positions}


# ═══════════════════════════════════════════
#  ADAPTER: PPTX
# ═══════════════════════════════════════════

def commands_to_pptx(render_result, output_path):
    """Translate draw commands to python-pptx shapes."""
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE

    commands = render_result["commands"]
    cw, ch = render_result["width"], render_result["height"]

    # Scale to fit slide
    SLIDE_W, SLIDE_H = 13.3, 7.5
    margin = 0.35
    scale = min((SLIDE_W - 2 * margin) / cw, (SLIDE_H - 2 * margin) / ch)

    def sx(x): return margin + x * scale
    def sy(y): return margin + y * scale
    def sw(v): return v * scale

    def rgb(h):
        h = h.lstrip("#")
        return RGBColor(int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16))

    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    for cmd in commands:
        t = cmd["type"]

        if t == "rect":
            shape = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE if cmd.get("radius", 0) > 0 else MSO_SHAPE.RECTANGLE,
                Inches(sx(cmd["x"])), Inches(sy(cmd["y"])),
                Inches(sw(cmd["w"])), Inches(sw(cmd["h"])))
            shape.fill.solid()
            shape.fill.fore_color.rgb = rgb(cmd["fill"])
            if cmd.get("stroke"):
                shape.line.color.rgb = rgb(cmd["stroke"])
                shape.line.width = Pt(cmd.get("stroke_width", 0.5))
            else:
                shape.line.fill.background()
            if cmd.get("shadow") is not True:
                shape.shadow.inherit = False

        elif t == "image":
            ipath = get_icon_path(cmd["src"])
            if ipath:
                try:
                    slide.shapes.add_picture(ipath,
                        Inches(sx(cmd["x"])), Inches(sy(cmd["y"])),
                        Inches(sw(cmd["w"])), Inches(sw(cmd["h"])))
                except:
                    pass

        elif t == "text":
            tx = slide.shapes.add_textbox(
                Inches(sx(cmd["x"])), Inches(sy(cmd["y"])),
                Inches(sw(cmd["w"])), Inches(0.25))
            tf = tx.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = cmd["text"]
            p.font.size = Pt(cmd.get("size", 7))
            p.font.color.rgb = rgb(cmd.get("color", "#3C4043"))
            p.font.bold = cmd.get("bold", False)
            align_map = {"center": PP_ALIGN.CENTER, "left": PP_ALIGN.LEFT, "right": PP_ALIGN.RIGHT}
            p.alignment = align_map.get(cmd.get("align", "center"), PP_ALIGN.CENTER)

        elif t == "arrow":
            pts = cmd["points"]
            color = rgb(cmd.get("color", "#9E9E9E"))
            width = Pt(cmd.get("width", 0.75))
            # Draw each segment
            for j in range(len(pts) - 1):
                x1, y1 = pts[j]
                x2, y2 = pts[j + 1]
                conn = slide.shapes.add_connector(1,
                    Inches(sx(x1)), Inches(sy(y1)),
                    Inches(sx(x2)), Inches(sy(y2)))
                conn.line.color.rgb = color
                conn.line.width = width

    prs.save(output_path)
    return output_path


# ═══════════════════════════════════════════
#  ADAPTER: CANVAS JS
# ═══════════════════════════════════════════

def commands_to_canvas_js(render_result):
    """Translate draw commands to JavaScript that draws on an HTML canvas."""
    import json
    return json.dumps(render_result["commands"])
