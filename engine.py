"""
XlArch Engine — Architecture definition, layout, icon loading.
One Python dict → canvas, PPTX, PNG.
"""

import os, base64, io, json
from pathlib import Path

# ═══════════════════════════════════════════
#  ICON LOADER
# ═══════════════════════════════════════════

ICON_DIR = Path(__file__).parent / "static" / "icons"

def get_icon_path(key):
    """Get filesystem path to an icon PNG."""
    p = ICON_DIR / f"{key}.png"
    return str(p) if p.exists() else None

def get_icon_b64(key):
    """Get icon as base64 string."""
    p = ICON_DIR / f"{key}.png"
    if not p.exists():
        return None
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_all_icon_keys():
    """List all available icon keys."""
    return [p.stem for p in ICON_DIR.glob("*.png")]

def get_icon_url(key):
    """Get web URL for an icon."""
    return f"/static/icons/{key}.png"


# ═══════════════════════════════════════════
#  SERVICE CATALOG
# ═══════════════════════════════════════════

CATALOG = {
    "GCP Compute": [
        {"id": "cloud_run", "label": "Cloud Run", "icon": "cloud_run"},
        {"id": "functions", "label": "Cloud Functions", "icon": "functions"},
        {"id": "gke", "label": "GKE", "icon": "gke"},
        {"id": "compute_engine", "label": "Compute Engine", "icon": "compute_engine"},
    ],
    "GCP Analytics": [
        {"id": "bigquery", "label": "BigQuery", "icon": "bigquery"},
        {"id": "dataflow", "label": "Dataflow", "icon": "dataflow"},
        {"id": "pubsub", "label": "Pub/Sub", "icon": "pubsub"},
        {"id": "composer", "label": "Composer", "icon": "composer"},
        {"id": "looker", "label": "Looker", "icon": "looker"},
        {"id": "dataproc", "label": "Dataproc", "icon": "dataproc"},
        {"id": "data_catalog", "label": "Data Catalog", "icon": "data_catalog"},
    ],
    "GCP Storage & DB": [
        {"id": "gcs", "label": "Cloud Storage", "icon": "gcs"},
        {"id": "bigtable", "label": "Bigtable", "icon": "bigtable"},
        {"id": "memorystore", "label": "Memorystore", "icon": "memorystore"},
        {"id": "spanner", "label": "Spanner", "icon": "spanner"},
        {"id": "firestore", "label": "Firestore", "icon": "firestore"},
        {"id": "cloudsql", "label": "Cloud SQL", "icon": "cloudsql"},
    ],
    "GCP AI / ML": [
        {"id": "vertex_ai", "label": "Vertex AI", "icon": "vertex_ai"},
        {"id": "automl", "label": "AutoML", "icon": "automl"},
        {"id": "tpu", "label": "Cloud TPU", "icon": "tpu"},
    ],
    "GCP Security & Ops": [
        {"id": "iam", "label": "Cloud IAM", "icon": "iam"},
        {"id": "kms", "label": "Cloud KMS", "icon": "kms"},
        {"id": "monitoring", "label": "Monitoring", "icon": "monitoring"},
        {"id": "logging", "label": "Logging", "icon": "logging"},
    ],
    "GCP Network": [
        {"id": "load_balancing", "label": "Load Balancing", "icon": "load_balancing"},
        {"id": "cdn", "label": "Cloud CDN", "icon": "cdn"},
        {"id": "dns", "label": "Cloud DNS", "icon": "dns"},
    ],
    "Databases": [
        {"id": "postgresql", "label": "PostgreSQL", "icon": "postgresql"},
        {"id": "mysql", "label": "MySQL", "icon": "mysql"},
        {"id": "oracle", "label": "Oracle", "icon": "oracle"},
        {"id": "mssql", "label": "SQL Server", "icon": "mssql"},
        {"id": "mongodb", "label": "MongoDB", "icon": "mongodb"},
        {"id": "cassandra", "label": "Cassandra", "icon": "cassandra"},
        {"id": "neo4j", "label": "Neo4j", "icon": "neo4j"},
        {"id": "redis", "label": "Redis", "icon": "redis"},
        {"id": "generic_db", "label": "Database", "icon": "generic_db"},
    ],
    "Messaging": [
        {"id": "kafka", "label": "Kafka", "icon": "kafka"},
        {"id": "rabbitmq", "label": "RabbitMQ", "icon": "rabbitmq"},
        {"id": "activemq", "label": "ActiveMQ", "icon": "activemq"},
        {"id": "nats", "label": "NATS", "icon": "nats"},
    ],
    "AWS": [
        {"id": "aurora", "label": "Aurora", "icon": "aurora"},
        {"id": "dynamodb", "label": "DynamoDB", "icon": "dynamodb"},
        {"id": "redshift", "label": "Redshift", "icon": "redshift"},
        {"id": "elasticache", "label": "ElastiCache", "icon": "elasticache"},
        {"id": "rds", "label": "RDS", "icon": "rds"},
    ],
    "General": [
        {"id": "user", "label": "User", "icon": "user"},
        {"id": "users", "label": "Users", "icon": "users"},
        {"id": "client", "label": "Client App", "icon": "client"},
        {"id": "firewall", "label": "Firewall", "icon": "firewall"},
        {"id": "database", "label": "Database", "icon": "database"},
    ],
}


# ═══════════════════════════════════════════
#  LAYOUT ENGINE
# ═══════════════════════════════════════════

DEFAULT_ZONES = ["sources", "ingest", "process", "store", "analyze", "serve"]
DEFAULT_LANES = ["streaming", "batch", "ml"]

DEFAULT_STYLE = {
    "icon_size": 48,
    "node_w": 130,
    "node_h": 88,
    "zone_gap": 180,
    "lane_gap": 160,
    "left_pad": 60,
    "top_pad": 80,
    "arrow_color": "#b0b8c1",
    "arrow_width": 1.5,
    "lane_colors": {
        "streaming": "#EBF5FB",
        "batch": "#F0F9E8",
        "ml": "#FDF2E9",
    },
}


def compute_layout(architecture):
    """Compute x,y positions for all nodes based on zone/lane."""
    zones = architecture.get("zones", DEFAULT_ZONES)
    lanes = architecture.get("lanes", DEFAULT_LANES)
    style = architecture.get("style", DEFAULT_STYLE)
    nodes = architecture.get("nodes", [])

    zg = style.get("zone_gap", 180)
    lg = style.get("lane_gap", 160)
    lp = style.get("left_pad", 60)
    tp = style.get("top_pad", 80)
    nw = style.get("node_w", 130)

    zone_x = {z: lp + i * zg for i, z in enumerate(zones)}
    lane_y = {l: tp + i * lg for i, l in enumerate(lanes)}

    # Count nodes per cell to spread duplicates
    cells = {}
    for n in nodes:
        key = f"{n.get('zone','')}-{n.get('lane','')}"
        cells.setdefault(key, []).append(n["id"])

    positions = {}
    for n in nodes:
        z = n.get("zone", "")
        l = n.get("lane", "")
        key = f"{z}-{l}"
        siblings = cells.get(key, [n["id"]])
        idx = siblings.index(n["id"]) if n["id"] in siblings else 0
        bx = zone_x.get(z, lp)
        by = lane_y.get(l, tp)
        positions[n["id"]] = {
            "x": bx + idx * (nw + 20),
            "y": by,
        }

    return positions


def new_architecture(title="Untitled"):
    """Create a blank architecture."""
    return {
        "title": title,
        "zones": list(DEFAULT_ZONES),
        "lanes": list(DEFAULT_LANES),
        "style": dict(DEFAULT_STYLE),
        "nodes": [],
        "edges": [],
        "governance": [],
        "bestPractices": [],
    }


# ═══════════════════════════════════════════
#  AI PROMPT
# ═══════════════════════════════════════════

SYSTEM_PROMPT = """You are XlArch, an expert system architect. Generate architecture as a Python dict.

OUTPUT ONLY A VALID PYTHON DICT LITERAL. No markdown, no backticks, no explanation, no imports.
Start with { and end with }

Available icon IDs: """ + ", ".join(get_all_icon_keys()) + """

ZONES (left-to-right columns): sources, ingest, process, store, analyze, serve
LANES (top-to-bottom rows): streaming, batch, ml

OUTPUT FORMAT:
{
    "title": "Architecture title",
    "zones": ["sources", "ingest", "process", "store", "analyze", "serve"],
    "lanes": ["streaming", "batch", "ml"],
    "nodes": [
        {"id": "unique_id", "icon": "bigquery", "label": "BigQuery", "zone": "store", "lane": "batch", "step": 5},
    ],
    "edges": [
        {"from": "node_id_1", "to": "node_id_2"},
    ],
    "governance": [
        {"icon": "iam", "label": "Cloud IAM"},
    ],
    "bestPractices": [
        {"category": "SECURITY", "tip": "Enable CMEK encryption"},
    ],
}

RULES:
- 8-18 nodes depending on complexity
- Number steps 1-N to show processing order
- Always include governance: at minimum IAM and monitoring
- Include best practices for reliability, security, cost, performance
- Use real icon IDs from the available list
- Place each node in exactly one zone and one lane
- Edges show data flow direction (from → to)
"""


# ═══════════════════════════════════════════
#  PPTX RENDERER
# ═══════════════════════════════════════════

def render_pptx(architecture, output_path):
    """Render architecture dict to an editable PPTX file."""
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE

    positions = compute_layout(architecture)
    style = architecture.get("style", DEFAULT_STYLE)
    S = 0.012  # canvas units → inches

    prs = Presentation()
    prs.slide_width = Inches(13.3)
    prs.slide_height = Inches(7.5)
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    def rgb(h):
        h = h.lstrip("#")
        return RGBColor(int(h[:2],16), int(h[2:4],16), int(h[4:],16))

    # Title
    tx = slide.shapes.add_textbox(Inches(0.3), Inches(0.1), Inches(8), Inches(0.4))
    p = tx.text_frame.paragraphs[0]
    p.text = architecture.get("title", "Architecture")
    p.font.size = Pt(16); p.font.bold = True; p.font.color.rgb = rgb("#202124")

    icon_s = style.get("icon_size", 48) * S
    nw = style.get("node_w", 130) * S
    nh = style.get("node_h", 88) * S

    # Nodes
    for n in architecture.get("nodes", []):
        pos = positions.get(n["id"])
        if not pos:
            continue
        px = pos["x"] * S + 0.5
        py = pos["y"] * S + 0.3

        # Icon
        icon_path = get_icon_path(n.get("icon", ""))
        if icon_path:
            ix = px + (nw - icon_s) / 2
            slide.shapes.add_picture(icon_path, Inches(ix), Inches(py), Inches(icon_s), Inches(icon_s))

        # Label
        tx = slide.shapes.add_textbox(Inches(px - 0.1), Inches(py + icon_s + 0.02), Inches(nw + 0.2), Inches(0.3))
        tf = tx.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = n.get("label", "")
        p.font.size = Pt(7); p.font.color.rgb = rgb("#3C4043")
        p.alignment = PP_ALIGN.CENTER

        # Step badge
        if "step" in n:
            sz = 0.2
            shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                Inches(px + nw - 0.05), Inches(py - 0.05), Inches(sz), Inches(sz))
            shape.fill.solid()
            shape.fill.fore_color.rgb = rgb("#4285F4")
            shape.line.fill.background()
            p = shape.text_frame.paragraphs[0]
            p.text = str(n["step"])
            p.font.size = Pt(8); p.font.color.rgb = RGBColor(255,255,255)
            p.font.bold = True; p.alignment = PP_ALIGN.CENTER

    # Edges
    for e in architecture.get("edges", []):
        fp = positions.get(e["from"])
        tp = positions.get(e["to"])
        if not fp or not tp:
            continue
        x1 = (fp["x"] + style.get("node_w", 130)) * S + 0.5
        y1 = (fp["y"] + style.get("node_h", 88) / 2) * S + 0.3
        x2 = tp["x"] * S + 0.5
        y2 = (tp["y"] + style.get("node_h", 88) / 2) * S + 0.3
        conn = slide.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
        conn.line.color.rgb = rgb("#9E9E9E")
        conn.line.width = Pt(0.75)

    # Governance bar
    gov_y = 6.0
    for i, g in enumerate(architecture.get("governance", [])):
        gx = 0.5 + i * 2.0
        icon_path = get_icon_path(g.get("icon", ""))
        if icon_path:
            slide.shapes.add_picture(icon_path, Inches(gx), Inches(gov_y), Inches(0.4), Inches(0.4))
        tx = slide.shapes.add_textbox(Inches(gx - 0.15), Inches(gov_y + 0.42), Inches(0.7), Inches(0.2))
        p = tx.text_frame.paragraphs[0]
        p.text = g.get("label", ""); p.font.size = Pt(6)
        p.font.color.rgb = rgb("#5F6368"); p.alignment = PP_ALIGN.CENTER

    prs.save(output_path)
    return output_path


# ═══════════════════════════════════════════
#  PNG RENDERER (via diagrams library)
# ═══════════════════════════════════════════

def render_png(architecture, output_path):
    """Render architecture dict to PNG using diagrams library."""
    # Build a temporary Python script and execute it
    nodes = architecture.get("nodes", [])
    edges = architecture.get("edges", [])
    title = architecture.get("title", "Architecture")

    # Map icon keys to diagrams library imports
    DIAGRAMS_MAP = {
        "bigquery": ("diagrams.gcp.analytics", "BigQuery"),
        "dataflow": ("diagrams.gcp.analytics", "Dataflow"),
        "pubsub": ("diagrams.gcp.analytics", "PubSub"),
        "composer": ("diagrams.gcp.analytics", "Composer"),
        "looker": ("diagrams.gcp.analytics", "Looker"),
        "data_catalog": ("diagrams.gcp.analytics", "DataCatalog"),
        "dataproc": ("diagrams.gcp.analytics", "Dataproc"),
        "gcs": ("diagrams.gcp.storage", "GCS"),
        "bigtable": ("diagrams.gcp.database", "BigTable"),
        "memorystore": ("diagrams.gcp.database", "Memorystore"),
        "spanner": ("diagrams.gcp.database", "Spanner"),
        "firestore": ("diagrams.gcp.database", "Firestore"),
        "cloudsql": ("diagrams.gcp.database", "SQL"),
        "vertex_ai": ("diagrams.gcp.ml", "VertexAI"),
        "automl": ("diagrams.gcp.ml", "AutoML"),
        "tpu": ("diagrams.gcp.ml", "TPU"),
        "cloud_run": ("diagrams.gcp.compute", "CloudRun"),
        "functions": ("diagrams.gcp.compute", "Functions"),
        "gke": ("diagrams.gcp.compute", "GKE"),
        "compute_engine": ("diagrams.gcp.compute", "ComputeEngine"),
        "iam": ("diagrams.gcp.security", "Iam"),
        "kms": ("diagrams.gcp.security", "KMS"),
        "monitoring": ("diagrams.gcp.operations", "Monitoring"),
        "logging": ("diagrams.gcp.operations", "Logging"),
        "load_balancing": ("diagrams.gcp.network", "LoadBalancing"),
        "cdn": ("diagrams.gcp.network", "CDN"),
        "dns": ("diagrams.gcp.network", "DNS"),
        "kafka": ("diagrams.onprem.queue", "Kafka"),
        "rabbitmq": ("diagrams.onprem.queue", "RabbitMQ"),
        "postgresql": ("diagrams.onprem.database", "PostgreSQL"),
        "mysql": ("diagrams.onprem.database", "MySQL"),
        "oracle": ("diagrams.onprem.database", "Oracle"),
        "mssql": ("diagrams.onprem.database", "Mssql"),
        "mongodb": ("diagrams.onprem.database", "MongoDB"),
        "cassandra": ("diagrams.onprem.database", "Cassandra"),
        "redis": ("diagrams.onprem.inmemory", "Redis"),
    }

    # Collect needed imports
    imports = set()
    node_map = {}
    for n in nodes:
        icon = n.get("icon", "")
        if icon in DIAGRAMS_MAP:
            mod, cls = DIAGRAMS_MAP[icon]
            imports.add(f"from {mod} import {cls}")
            node_map[n["id"]] = (cls, n.get("label", n["id"]))

    if not node_map:
        return None

    # Build script
    lines = [
        "from diagrams import Diagram, Edge",
        *sorted(imports),
        "",
        f'with Diagram("{title}", filename="{output_path}", show=False, direction="LR",',
        '             graph_attr={"splines": "ortho", "nodesep": "0.6", "ranksep": "0.9", "bgcolor": "#FFFFFF"}):',
    ]

    # Declare nodes
    for nid, (cls, label) in node_map.items():
        safe_id = nid.replace("-", "_")
        lines.append(f'    {safe_id} = {cls}("{label}")')

    # Declare edges
    for e in edges:
        f_id = e["from"].replace("-", "_")
        t_id = e["to"].replace("-", "_")
        if f_id in [nid.replace("-","_") for nid in node_map] and t_id in [nid.replace("-","_") for nid in node_map]:
            lines.append(f'    {f_id} >> {t_id}')

    script = "\n".join(lines)

    import tempfile, subprocess
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(["python3", script_path], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return f"{output_path}.png"
    except Exception:
        pass
    finally:
        os.unlink(script_path)

    return None
