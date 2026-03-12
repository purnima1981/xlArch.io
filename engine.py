"""
XlArch Engine — One architecture dict → canvas, PPTX, PNG.
All renderers share the same coordinate system.
"""

import os, base64, io, json, subprocess, tempfile
from pathlib import Path

ICON_DIR = Path(__file__).parent / "static" / "icons"

def get_icon_path(key):
    p = ICON_DIR / f"{key}.png"
    return str(p) if p.exists() else None

def get_all_icon_keys():
    return sorted([p.stem for p in ICON_DIR.glob("*.png")])

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
        {"id": "dataplex", "label": "Dataplex", "icon": "dataplex"},
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
        {"id": "redis", "label": "Redis", "icon": "redis"},
        {"id": "generic_db", "label": "Database", "icon": "generic_db"},
    ],
    "Messaging": [
        {"id": "kafka", "label": "Kafka", "icon": "kafka"},
        {"id": "rabbitmq", "label": "RabbitMQ", "icon": "rabbitmq"},
        {"id": "nats", "label": "NATS", "icon": "nats"},
    ],
    "AWS": [
        {"id": "aurora", "label": "Aurora", "icon": "aurora"},
        {"id": "dynamodb", "label": "DynamoDB", "icon": "dynamodb"},
        {"id": "redshift", "label": "Redshift", "icon": "redshift"},
        {"id": "rds", "label": "RDS", "icon": "rds"},
    ],
    "General": [
        {"id": "user", "label": "User", "icon": "user"},
        {"id": "users", "label": "Users", "icon": "users"},
        {"id": "client", "label": "Client App", "icon": "client"},
        {"id": "database", "label": "Database", "icon": "database"},
    ],
}

# ═══ SHARED LAYOUT CONSTANTS ═══
DEFAULT_ZONES = ["sources", "ingest", "process", "store", "analyze", "serve"]
DEFAULT_LANES = ["streaming", "batch", "ml"]

NW = 120     # node width
NH = 82      # node height
IS = 42      # icon size
ZG = 175     # zone gap
LG = 145     # lane gap
LP = 70      # left pad
TP = 90      # top pad
GOV_OFF = 15 # governance offset below last lane
ARROW_COLOR = "#9E9E9E"
LANE_COLORS = {"streaming": "#E8F4FD", "batch": "#EDF7ED", "ml": "#FFF3E0", "governance": "#F3E8FD",
    "user_identity": "#E8F4FD", "service_identity": "#EDF7ED", "secrets": "#FFF3E0",
    "primary": "#E8F4FD", "management": "#EDF7ED", "dns_routing": "#FFF3E0",
    "networking": "#E8F4FD", "identity": "#F3E8FD", "data_path": "#EDF7ED",
    "ingress": "#E8F4FD", "internal": "#EDF7ED", "egress": "#FFF3E0",
    "preventive": "#E8F4FD", "detective": "#EDF7ED", "corrective": "#FFF3E0",
}


def get_lane_gap(num_lanes):
    """Adaptive lane gap: fewer lanes = more space, many lanes = compact."""
    if num_lanes <= 4:
        return LG
    return max(100, LG - (num_lanes - 4) * 15)


def compute_layout(architecture):
    zones = architecture.get("zones", DEFAULT_ZONES)
    lanes = architecture.get("lanes", DEFAULT_LANES)
    nodes = architecture.get("nodes", [])

    # Adaptive gaps: fill available space
    # Target ~1100px wide canvas
    zone_gap = max(ZG, int(1000 / max(len(zones), 1)))
    lane_gap = LG if len(lanes) <= 4 else max(100, LG - (len(lanes) - 4) * 15)

    zone_x = {z: LP + i * zone_gap for i, z in enumerate(zones)}
    lane_y = {l: TP + i * lane_gap for i, l in enumerate(lanes)}

    cells = {}
    for n in nodes:
        key = f"{n.get('zone','')}-{n.get('lane','')}"
        cells.setdefault(key, []).append(n["id"])

    positions = {}
    for n in nodes:
        z, l = n.get("zone", ""), n.get("lane", "")
        key = f"{z}-{l}"
        siblings = cells.get(key, [n["id"]])
        idx = siblings.index(n["id"]) if n["id"] in siblings else 0
        positions[n["id"]] = {
            "x": zone_x.get(z, LP) + idx * (NW + 30),
            "y": lane_y.get(l, TP),
        }
    return positions, zone_gap, lane_gap


def canvas_bounds(architecture):
    zones = architecture.get("zones", DEFAULT_ZONES)
    lanes = architecture.get("lanes", DEFAULT_LANES)
    zone_gap = max(ZG, int(1000 / max(len(zones), 1)))
    lane_gap = LG if len(lanes) <= 4 else max(100, LG - (len(lanes) - 4) * 15)
    return LP + len(zones) * zone_gap + 60, TP + len(lanes) * lane_gap + GOV_OFF + 130


def new_architecture(title="Untitled"):
    return {
        "title": title,
        "zones": list(DEFAULT_ZONES),
        "lanes": list(DEFAULT_LANES),
        "nodes": [], "edges": [], "governance": [], "bestPractices": [],
    }


# ═══ SYSTEM PROMPT ═══
SYSTEM_PROMPT = """You are XlArch, an expert system architect. Generate architecture as a Python dict.

OUTPUT ONLY A VALID PYTHON DICT LITERAL. No markdown, no backticks, no explanation.
Start with { and end with }

Available icon IDs: """ + ", ".join(get_all_icon_keys()) + """

ZONES (left-to-right): sources, ingest, process, store, analyze, serve
LANES (top-to-bottom): streaming, batch, ml

FORMAT:
{
    "title": "Title",
    "zones": ["sources", "ingest", "process", "store", "analyze", "serve"],
    "lanes": ["streaming", "batch", "ml"],
    "nodes": [
        {"id": "unique_id", "icon": "bigquery", "label": "BigQuery", "zone": "store", "lane": "batch", "step": 5},
    ],
    "edges": [
        {"from": "id1", "to": "id2"},
    ],
    "governance": [
        {"icon": "iam", "label": "IAM"},
        {"icon": "kms", "label": "KMS / CMEK"},
        {"icon": "monitoring", "label": "Monitoring"},
        {"icon": "logging", "label": "Audit Logs"},
        {"icon": "firewall", "label": "VPC-SC"},
        {"icon": "dns", "label": "Private Connect"},
        {"icon": "dataplex", "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "SECURITY", "tip": "..."},
    ],
}

═══════════════════════════════════════
NON-NEGOTIABLE — EVERY architecture MUST include these in governance:
═══════════════════════════════════════

1. IDENTITY & ACCESS
   - Cloud IAM (icon: iam) — least privilege, service accounts, Workload Identity
   - Authentication & Authorization flow must be shown or referenced

2. ENCRYPTION
   - Cloud KMS (icon: kms) — CMEK for all data at rest
   - TLS/mTLS for all data in transit

3. NETWORK SECURITY
   - VPC Service Controls / blast radius isolation (icon: firewall)
   - Private connectivity — Private Service Connect, VPC peering, no public endpoints (icon: dns)
   - Interconnect for hybrid connectivity if applicable

4. OBSERVABILITY
   - Cloud Monitoring (icon: monitoring) — metrics, dashboards, SLOs
   - Cloud Logging (icon: logging) — audit logs, access transparency, log sinks
   - Alerting policies on all critical services

5. DATA GOVERNANCE
   - Dataplex (icon: dataplex) — metadata, lineage, classification
   - DLP for PII detection where applicable

ALL of the above MUST appear in the "governance" array. Never skip them.
GOVERNANCE LABELS MUST BE SHORT — max 15 characters. Use: "IAM", "KMS / CMEK", "Monitoring", "Audit Logs", "VPC-SC", "Private Connect", "Dataplex". Never long descriptions.

═══════════════════════════════════════
ARCHITECTURE RULES:
═══════════════════════════════════════

- 10-18 nodes in the main architecture
- Number steps 1-N in data flow order
- Every edge represents a real data flow — show HOW data moves
- Use only icon IDs from the available list
- Each node in exactly one zone and one lane
- Connect logically: sources → ingest → process → store → analyze → serve
- Show cross-lane connections where data flows between streaming/batch/ml paths

BEST PRACTICES — include 6-10 across these categories:
- SECURITY: IAM least privilege, CMEK, VPC-SC, no public endpoints, service account keys rotation
- NETWORK: Private Service Connect, dedicated interconnect, firewall rules, DNS peering
- RELIABILITY: multi-region, auto-scaling, dead letter queues, retry policies, HA configurations
- COST: committed use discounts, autoscaling to zero, lifecycle policies, slot reservations
- PERFORMANCE: caching, partitioning, pre-splitting, streaming engine, connection pooling
- COMPLIANCE: audit logging, access transparency, data residency, retention policies
"""


# PPTX rendering moved to renderer.py — single render, multiple outputs

# ═══ PNG RENDERER ═══

def render_png(architecture, output_path):
    nodes = architecture.get("nodes", [])
    edges = architecture.get("edges", [])
    title = architecture.get("title", "Architecture")

    DMAP = {
        "bigquery":("diagrams.gcp.analytics","BigQuery"), "dataflow":("diagrams.gcp.analytics","Dataflow"),
        "pubsub":("diagrams.gcp.analytics","PubSub"), "composer":("diagrams.gcp.analytics","Composer"),
        "looker":("diagrams.gcp.analytics","Looker"), "dataproc":("diagrams.gcp.analytics","Dataproc"),
        "gcs":("diagrams.gcp.storage","GCS"), "bigtable":("diagrams.gcp.database","BigTable"),
        "memorystore":("diagrams.gcp.database","Memorystore"), "spanner":("diagrams.gcp.database","Spanner"),
        "firestore":("diagrams.gcp.database","Firestore"), "cloudsql":("diagrams.gcp.database","SQL"),
        "vertex_ai":("diagrams.gcp.ml","VertexAI"), "cloud_run":("diagrams.gcp.compute","CloudRun"),
        "functions":("diagrams.gcp.compute","Functions"), "gke":("diagrams.gcp.compute","GKE"),
        "compute_engine":("diagrams.gcp.compute","ComputeEngine"),
        "iam":("diagrams.gcp.security","Iam"), "kms":("diagrams.gcp.security","KMS"),
        "monitoring":("diagrams.gcp.operations","Monitoring"), "logging":("diagrams.gcp.operations","Logging"),
        "kafka":("diagrams.onprem.queue","Kafka"), "rabbitmq":("diagrams.onprem.queue","RabbitMQ"),
        "postgresql":("diagrams.onprem.database","PostgreSQL"), "mysql":("diagrams.onprem.database","MySQL"),
        "oracle":("diagrams.onprem.database","Oracle"), "mssql":("diagrams.onprem.database","Mssql"),
        "mongodb":("diagrams.onprem.database","MongoDB"), "redis":("diagrams.onprem.inmemory","Redis"),
    }

    imports, nmap = set(), {}
    for n in nodes:
        if n.get("icon","") in DMAP:
            mod, cls = DMAP[n["icon"]]
            imports.add(f"from {mod} import {cls}")
            nmap[n["id"]] = (cls, n.get("label", n["id"]))

    if not nmap: return None

    lines = ["from diagrams import Diagram, Edge", *sorted(imports), "",
        f'with Diagram("{title}", filename="{output_path}", show=False, direction="LR",',
        '             graph_attr={"splines":"ortho","nodesep":"0.6","ranksep":"0.9","bgcolor":"#FFFFFF"}):']
    for nid, (cls, label) in nmap.items():
        s = nid.replace("-","_").replace(" ","_")
        lines.append(f'    {s} = {cls}("{label}")')
    valid = {nid.replace("-","_").replace(" ","_") for nid in nmap}
    for e in edges:
        f, t = e["from"].replace("-","_").replace(" ","_"), e["to"].replace("-","_").replace(" ","_")
        if f in valid and t in valid: lines.append(f'    {f} >> {t}')

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("\n".join(lines)); sp = f.name
    try:
        r = subprocess.run(["python3", sp], capture_output=True, text=True, timeout=30)
        if r.returncode == 0: return f"{output_path}.png"
    except: pass
    finally: os.unlink(sp)
    return None
