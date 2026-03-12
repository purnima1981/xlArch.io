"""
XlArch Reference Templates — Pre-built architecture patterns.
These are the gold standard. AI references these when generating.
"""

# ═══════════════════════════════════════════════════════════
#  TEMPLATE 1: NETWORK & CONNECTIVITY
# ═══════════════════════════════════════════════════════════

NETWORK_CONNECTIVITY = {
    "title": "Network & Connectivity Architecture",
    "layout": "nested",  # nested layers, not left-to-right
    "zones": ["external", "perimeter", "shared_vpc", "workload", "data", "hybrid"],
    "lanes": ["ingress", "internal", "egress"],
    "nodes": [
        # External
        {"id": "internet",        "icon": "users",           "label": "Internet",            "zone": "external",   "lane": "ingress",  "step": 1},
        {"id": "corp_network",    "icon": "vpn",             "label": "Corporate Network",   "zone": "external",   "lane": "egress",   "step": 1},
        {"id": "partner_api",     "icon": "client",          "label": "Partner APIs",        "zone": "external",   "lane": "internal"},

        # Perimeter
        {"id": "cloud_armor",     "icon": "firewall",        "label": "Cloud Armor / WAF",   "zone": "perimeter",  "lane": "ingress",  "step": 2},
        {"id": "ext_lb",          "icon": "load_balancing",  "label": "External LB (L7)",    "zone": "perimeter",  "lane": "ingress",  "step": 3},
        {"id": "cloud_cdn",       "icon": "cdn",             "label": "Cloud CDN",           "zone": "perimeter",  "lane": "ingress"},
        {"id": "cloud_dns",       "icon": "dns",             "label": "Cloud DNS",           "zone": "perimeter",  "lane": "internal"},

        # Shared VPC / Network Hub
        {"id": "shared_vpc",      "icon": "firewall",        "label": "Shared VPC Host",     "zone": "shared_vpc", "lane": "internal", "step": 4},
        {"id": "int_lb",          "icon": "load_balancing",  "label": "Internal LB (L4)",    "zone": "shared_vpc", "lane": "internal"},
        {"id": "vpc_sc",          "icon": "firewall",        "label": "VPC-SC Perimeter",    "zone": "shared_vpc", "lane": "ingress",  "step": 5},
        {"id": "nat_gw",          "icon": "dns",             "label": "Cloud NAT",           "zone": "shared_vpc", "lane": "egress"},

        # Workload Projects
        {"id": "gke_cluster",     "icon": "gke",             "label": "GKE (Workload)",      "zone": "workload",   "lane": "ingress",  "step": 6},
        {"id": "cloud_run_svc",   "icon": "cloud_run",       "label": "Cloud Run",           "zone": "workload",   "lane": "internal"},
        {"id": "compute_vms",     "icon": "compute_engine",  "label": "Compute VMs",         "zone": "workload",   "lane": "egress"},

        # Data Services (Private Access)
        {"id": "psc_bigquery",    "icon": "bigquery",        "label": "BigQuery (PSC)",      "zone": "data",       "lane": "internal", "step": 7},
        {"id": "psc_gcs",         "icon": "gcs",             "label": "GCS (PSC)",           "zone": "data",       "lane": "ingress"},
        {"id": "psc_cloudsql",    "icon": "cloudsql",        "label": "Cloud SQL (PSC)",     "zone": "data",       "lane": "egress"},
        {"id": "memorystore_psc", "icon": "memorystore",     "label": "Memorystore (PSC)",   "zone": "data",       "lane": "internal"},

        # Hybrid Connectivity
        {"id": "interconnect",    "icon": "vpn",             "label": "Dedicated Interconnect", "zone": "hybrid",  "lane": "egress",   "step": 8},
        {"id": "cloud_vpn",       "icon": "vpn",             "label": "Cloud VPN (HA)",      "zone": "hybrid",     "lane": "internal"},
        {"id": "cloud_router",    "icon": "dns",             "label": "Cloud Router (BGP)",  "zone": "hybrid",     "lane": "ingress"},
    ],
    "edges": [
        # Ingress path
        {"from": "internet",      "to": "cloud_armor"},
        {"from": "cloud_armor",   "to": "ext_lb"},
        {"from": "ext_lb",        "to": "cloud_cdn"},
        {"from": "ext_lb",        "to": "vpc_sc"},
        {"from": "vpc_sc",        "to": "gke_cluster"},
        {"from": "vpc_sc",        "to": "cloud_run_svc"},

        # Internal networking
        {"from": "cloud_dns",     "to": "shared_vpc"},
        {"from": "shared_vpc",    "to": "int_lb"},
        {"from": "int_lb",        "to": "cloud_run_svc"},
        {"from": "int_lb",        "to": "gke_cluster"},

        # Workload → Data (via PSC)
        {"from": "gke_cluster",   "to": "psc_bigquery"},
        {"from": "gke_cluster",   "to": "psc_gcs"},
        {"from": "cloud_run_svc", "to": "psc_cloudsql"},
        {"from": "cloud_run_svc", "to": "memorystore_psc"},

        # Egress / Hybrid
        {"from": "compute_vms",   "to": "nat_gw"},
        {"from": "nat_gw",        "to": "partner_api"},
        {"from": "shared_vpc",    "to": "interconnect"},
        {"from": "shared_vpc",    "to": "cloud_vpn"},
        {"from": "interconnect",  "to": "corp_network"},
        {"from": "cloud_vpn",     "to": "cloud_router"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "VPC Flow Logs"},
        {"icon": "firewall",     "label": "Firewall Rules"},
        {"icon": "dns",          "label": "Private DNS"},
        {"icon": "dataplex", "label": "Asset Inventory"},
    ],
    "bestPractices": [
        {"category": "NETWORK",     "tip": "Shared VPC for centralized network control across projects"},
        {"category": "NETWORK",     "tip": "VPC Service Controls for API-level perimeter around sensitive data"},
        {"category": "NETWORK",     "tip": "Private Service Connect (PSC) for all Google API access — no public endpoints"},
        {"category": "NETWORK",     "tip": "Dedicated Interconnect for hybrid with 99.99% SLA (dual attachments)"},
        {"category": "SECURITY",    "tip": "Cloud Armor WAF rules for OWASP Top 10 protection"},
        {"category": "SECURITY",    "tip": "Firewall policies at org level — deny-all default, allow specific"},
        {"category": "RELIABILITY", "tip": "HA Cloud VPN with dynamic routing via Cloud Router (BGP)"},
        {"category": "RELIABILITY", "tip": "Multi-region external LB with health checks and failover"},
        {"category": "COST",        "tip": "Cloud NAT only for egress that requires it — avoid over-provisioning"},
        {"category": "COMPLIANCE",  "tip": "VPC Flow Logs enabled on all subnets for audit trail"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 2: SECURITY & COMPLIANCE
# ═══════════════════════════════════════════════════════════

SECURITY_COMPLIANCE = {
    "title": "Security & Compliance Architecture",
    "layout": "nested",
    "zones": ["identity", "perimeter", "workload_security", "data_security", "detect_respond", "compliance"],
    "lanes": ["preventive", "detective", "corrective"],
    "nodes": [
        # Identity & Access
        {"id": "cloud_identity",  "icon": "users",          "label": "Cloud Identity",       "zone": "identity",           "lane": "preventive", "step": 1},
        {"id": "iam_policies",    "icon": "iam",            "label": "IAM Policies",         "zone": "identity",           "lane": "preventive", "step": 2},
        {"id": "workload_id",     "icon": "iam",            "label": "Workload Identity",    "zone": "identity",           "lane": "detective"},
        {"id": "org_policies",    "icon": "iam",            "label": "Org Policies",         "zone": "identity",           "lane": "corrective"},

        # Perimeter Security
        {"id": "cloud_armor_sec", "icon": "firewall",       "label": "Cloud Armor",          "zone": "perimeter",          "lane": "preventive", "step": 3},
        {"id": "vpc_sc_sec",      "icon": "firewall",       "label": "VPC-SC",               "zone": "perimeter",          "lane": "preventive", "step": 4},
        {"id": "binary_auth",     "icon": "firewall",       "label": "Binary Authorization", "zone": "perimeter",          "lane": "detective"},

        # Workload Security
        {"id": "gke_sec",         "icon": "gke",            "label": "GKE Security",         "zone": "workload_security",  "lane": "preventive", "step": 5},
        {"id": "secret_manager",  "icon": "kms",            "label": "Secret Manager",       "zone": "workload_security",  "lane": "preventive"},
        {"id": "container_scan",  "icon": "monitoring",     "label": "Container Scanning",   "zone": "workload_security",  "lane": "detective"},

        # Data Security
        {"id": "cmek",            "icon": "kms",            "label": "CMEK Encryption",      "zone": "data_security",      "lane": "preventive", "step": 6},
        {"id": "dlp",             "icon": "dataplex",   "label": "Cloud DLP",            "zone": "data_security",      "lane": "detective",  "step": 7},
        {"id": "dataplex_sec","icon": "dataplex",   "label": "Dataplex",         "zone": "data_security",      "lane": "detective"},
        {"id": "backup_vault",    "icon": "gcs",            "label": "Backup Vault",         "zone": "data_security",      "lane": "corrective"},

        # Detect & Respond
        {"id": "scc",             "icon": "monitoring",     "label": "Security Command Center", "zone": "detect_respond",  "lane": "detective",  "step": 8},
        {"id": "chronicle",       "icon": "logging",        "label": "Chronicle SIEM",       "zone": "detect_respond",     "lane": "detective"},
        {"id": "cloud_audit",     "icon": "logging",        "label": "Audit Logs",           "zone": "detect_respond",     "lane": "detective",  "step": 9},
        {"id": "alerting",        "icon": "monitoring",     "label": "Alert Policies",       "zone": "detect_respond",     "lane": "corrective"},

        # Compliance
        {"id": "assured_wl",      "icon": "iam",            "label": "Assured Workloads",    "zone": "compliance",         "lane": "preventive"},
        {"id": "access_transparency", "icon": "logging",    "label": "Access Transparency",  "zone": "compliance",         "lane": "detective"},
        {"id": "compliance_report", "icon": "dataplex", "label": "Compliance Reports",   "zone": "compliance",         "lane": "corrective"},
    ],
    "edges": [
        # Identity chain
        {"from": "cloud_identity",  "to": "iam_policies"},
        {"from": "iam_policies",    "to": "workload_id"},
        {"from": "iam_policies",    "to": "org_policies"},

        # Perimeter
        {"from": "cloud_armor_sec", "to": "vpc_sc_sec"},
        {"from": "vpc_sc_sec",      "to": "binary_auth"},

        # Identity → Workload
        {"from": "iam_policies",    "to": "gke_sec"},
        {"from": "workload_id",     "to": "gke_sec"},

        # Workload security
        {"from": "gke_sec",         "to": "secret_manager"},
        {"from": "gke_sec",         "to": "container_scan"},

        # Data security
        {"from": "gke_sec",         "to": "cmek"},
        {"from": "cmek",            "to": "dlp"},
        {"from": "dlp",             "to": "dataplex_sec"},
        {"from": "dataplex_sec","to": "backup_vault"},

        # Detection
        {"from": "container_scan",  "to": "scc"},
        {"from": "cloud_audit",     "to": "chronicle"},
        {"from": "scc",             "to": "alerting"},
        {"from": "chronicle",       "to": "alerting"},

        # Compliance
        {"from": "org_policies",    "to": "assured_wl"},
        {"from": "cloud_audit",     "to": "access_transparency"},
        {"from": "access_transparency", "to": "compliance_report"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "SCC"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "firewall",     "label": "VPC-SC"},
        {"icon": "dataplex", "label": "DLP"},
    ],
    "bestPractices": [
        {"category": "SECURITY",    "tip": "IAM least privilege — no primitive roles, use predefined or custom"},
        {"category": "SECURITY",    "tip": "Workload Identity Federation — no service account keys"},
        {"category": "SECURITY",    "tip": "CMEK on ALL data stores — BigQuery, GCS, Cloud SQL, Spanner"},
        {"category": "SECURITY",    "tip": "Binary Authorization — only signed container images in production"},
        {"category": "NETWORK",     "tip": "VPC Service Controls perimeter around all sensitive projects"},
        {"category": "COMPLIANCE",  "tip": "Organization policies enforced at folder level — uniform bucket access, public IP restrictions"},
        {"category": "COMPLIANCE",  "tip": "Cloud Audit Logs exported to centralized SIEM (Chronicle)"},
        {"category": "COMPLIANCE",  "tip": "Access Transparency logs for Google admin access visibility"},
        {"category": "RELIABILITY", "tip": "Automated backup to separate project with cross-region replication"},
        {"category": "COMPLIANCE",  "tip": "DLP scanning on all data ingestion pipelines for PII detection"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 3: DATA ANALYTICS (Enhanced pipeline)
# ═══════════════════════════════════════════════════════════

DATA_ANALYTICS = {
    "title": "Data Analytics Architecture",
    "layout": "pipeline",
    "zones": ["sources", "ingest", "process", "store", "analyze", "serve"],
    "lanes": ["streaming", "batch", "ml"],
    "nodes": [
        # Sources
        {"id": "web_app",         "icon": "cloud_run",    "label": "Web App",              "zone": "sources",  "lane": "streaming"},
        {"id": "mobile_events",   "icon": "functions",    "label": "Mobile Events",        "zone": "sources",  "lane": "streaming"},
        {"id": "app_db",          "icon": "cloudsql",     "label": "Application DB",       "zone": "sources",  "lane": "batch"},
        {"id": "partner_feeds",   "icon": "client",       "label": "Partner Feeds",        "zone": "sources",  "lane": "batch"},
        {"id": "iot_devices",     "icon": "client",       "label": "IoT Devices",          "zone": "sources",  "lane": "streaming"},

        # Ingest
        {"id": "pubsub",          "icon": "pubsub",       "label": "Pub/Sub",              "zone": "ingest",   "lane": "streaming", "step": 1},
        {"id": "composer",        "icon": "composer",      "label": "Cloud Composer",       "zone": "ingest",   "lane": "batch",     "step": 2},

        # Process
        {"id": "dataflow_stream", "icon": "dataflow",     "label": "Dataflow Streaming",   "zone": "process",  "lane": "streaming", "step": 3},
        {"id": "dataflow_batch",  "icon": "dataflow",     "label": "Dataflow Batch",       "zone": "process",  "lane": "batch",     "step": 4},
        {"id": "dataproc_spark",  "icon": "dataproc",     "label": "Dataproc Spark",       "zone": "process",  "lane": "batch"},

        # Store (Medallion)
        {"id": "gcs_bronze",      "icon": "gcs",          "label": "GCS Bronze (Raw)",     "zone": "store",    "lane": "streaming", "step": 5},
        {"id": "gcs_silver",      "icon": "gcs",          "label": "GCS Silver (Clean)",   "zone": "store",    "lane": "batch",     "step": 6},
        {"id": "bigtable_rt",     "icon": "bigtable",     "label": "Bigtable (Real-time)", "zone": "store",    "lane": "streaming"},
        {"id": "bq_gold",         "icon": "bigquery",     "label": "BigQuery Gold",        "zone": "store",    "lane": "batch",     "step": 7},

        # Analyze
        {"id": "bq_analytics",    "icon": "bigquery",     "label": "BQ Analytics",         "zone": "analyze",  "lane": "batch",     "step": 8},
        {"id": "vertex_ai",       "icon": "vertex_ai",    "label": "Vertex AI",            "zone": "analyze",  "lane": "ml",        "step": 9},
        {"id": "looker",          "icon": "looker",        "label": "Looker Studio",       "zone": "analyze",  "lane": "batch"},

        # Serve
        {"id": "memorystore_cache","icon": "memorystore", "label": "Memorystore",          "zone": "serve",    "lane": "streaming"},
        {"id": "api_endpoint",    "icon": "cloud_run",    "label": "API Endpoint",         "zone": "serve",    "lane": "batch"},
        {"id": "ml_endpoint",     "icon": "vertex_ai",    "label": "ML Endpoint",          "zone": "serve",    "lane": "ml"},
    ],
    "edges": [
        # Streaming path
        {"from": "web_app",         "to": "pubsub"},
        {"from": "mobile_events",   "to": "pubsub"},
        {"from": "iot_devices",     "to": "pubsub"},
        {"from": "pubsub",          "to": "dataflow_stream"},
        {"from": "dataflow_stream", "to": "gcs_bronze"},
        {"from": "dataflow_stream", "to": "bigtable_rt"},
        {"from": "bigtable_rt",     "to": "memorystore_cache"},

        # Batch path
        {"from": "app_db",          "to": "composer"},
        {"from": "partner_feeds",   "to": "composer"},
        {"from": "composer",        "to": "dataflow_batch"},
        {"from": "composer",        "to": "dataproc_spark"},
        {"from": "dataflow_batch",  "to": "gcs_silver"},
        {"from": "dataproc_spark",  "to": "gcs_silver"},
        {"from": "gcs_bronze",      "to": "gcs_silver"},
        {"from": "gcs_silver",      "to": "bq_gold"},

        # Analytics
        {"from": "bq_gold",         "to": "bq_analytics"},
        {"from": "bq_analytics",    "to": "looker"},
        {"from": "bq_analytics",    "to": "api_endpoint"},

        # ML path
        {"from": "bq_gold",         "to": "vertex_ai"},
        {"from": "vertex_ai",       "to": "ml_endpoint"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "firewall",     "label": "VPC-SC"},
        {"icon": "dns",          "label": "Private Connect"},
        {"icon": "dataplex", "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "SECURITY",     "tip": "CMEK encryption on BigQuery, GCS, Bigtable, and Cloud SQL"},
        {"category": "SECURITY",     "tip": "VPC-SC perimeter around all data projects"},
        {"category": "NETWORK",      "tip": "Private Service Connect for all Google API access"},
        {"category": "RELIABILITY",  "tip": "Pub/Sub dead-letter topics for failed message handling"},
        {"category": "RELIABILITY",  "tip": "Cloud Composer 2 in HA mode with auto-scaling workers"},
        {"category": "COST",         "tip": "Dataflow FlexRS for batch jobs — up to 40% savings"},
        {"category": "COST",         "tip": "BigQuery slot reservations for predictable costs"},
        {"category": "COST",         "tip": "GCS lifecycle rules — auto-transition to Nearline/Coldline"},
        {"category": "PERFORMANCE",  "tip": "BigQuery partitioned by date + clustered by high-cardinality columns"},
        {"category": "PERFORMANCE",  "tip": "Bigtable pre-split keys for even distribution"},
        {"category": "COMPLIANCE",   "tip": "Dataplex for metadata management and data lineage"},
        {"category": "COMPLIANCE",   "tip": "DLP scanning on ingestion for PII classification"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  TEMPLATE 4: REFERENCE PATTERNS
# ═══════════════════════════════════════════════════════════

MEDALLION_PATTERN = {
    "title": "Medallion Architecture (Bronze / Silver / Gold)",
    "layout": "pipeline",
    "zones": ["raw_sources", "bronze", "silver", "gold", "consumption"],
    "lanes": ["streaming", "batch", "ml"],
    "nodes": [
        {"id": "src_events",   "icon": "pubsub",     "label": "Event Streams",    "zone": "raw_sources", "lane": "streaming", "step": 1},
        {"id": "src_db",       "icon": "cloudsql",    "label": "Source DBs",       "zone": "raw_sources", "lane": "batch",     "step": 1},
        {"id": "src_api",      "icon": "client",      "label": "External APIs",    "zone": "raw_sources", "lane": "batch"},

        {"id": "bronze_gcs",   "icon": "gcs",         "label": "Bronze (Raw)",     "zone": "bronze",      "lane": "streaming", "step": 2},
        {"id": "bronze_bq",    "icon": "bigquery",    "label": "Bronze BQ (Raw)",  "zone": "bronze",      "lane": "batch",     "step": 2},

        {"id": "silver_gcs",   "icon": "gcs",         "label": "Silver (Clean)",   "zone": "silver",      "lane": "streaming", "step": 3},
        {"id": "silver_bq",    "icon": "bigquery",    "label": "Silver BQ",        "zone": "silver",      "lane": "batch",     "step": 3},
        {"id": "feature_store","icon": "bigtable",     "label": "Feature Store",    "zone": "silver",      "lane": "ml"},

        {"id": "gold_bq",      "icon": "bigquery",    "label": "Gold BQ (Curated)","zone": "gold",        "lane": "batch",     "step": 4},
        {"id": "gold_ml",      "icon": "vertex_ai",   "label": "ML Datasets",      "zone": "gold",        "lane": "ml",        "step": 4},

        {"id": "dashboards",   "icon": "looker",      "label": "Dashboards",       "zone": "consumption", "lane": "batch",     "step": 5},
        {"id": "ml_serving",   "icon": "vertex_ai",   "label": "ML Serving",       "zone": "consumption", "lane": "ml",        "step": 5},
        {"id": "api_serving",  "icon": "cloud_run",   "label": "API Layer",        "zone": "consumption", "lane": "streaming", "step": 5},
    ],
    "edges": [
        {"from": "src_events",  "to": "bronze_gcs"},
        {"from": "src_db",      "to": "bronze_bq"},
        {"from": "src_api",     "to": "bronze_bq"},
        {"from": "bronze_gcs",  "to": "silver_gcs"},
        {"from": "bronze_bq",   "to": "silver_bq"},
        {"from": "silver_gcs",  "to": "gold_bq"},
        {"from": "silver_bq",   "to": "gold_bq"},
        {"from": "silver_bq",   "to": "feature_store"},
        {"from": "gold_bq",     "to": "dashboards"},
        {"from": "gold_bq",     "to": "api_serving"},
        {"from": "feature_store","to": "gold_ml"},
        {"from": "gold_ml",     "to": "ml_serving"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "dataplex", "label": "Data Lineage"},
        {"icon": "firewall",     "label": "VPC-SC"},
    ],
    "bestPractices": [
        {"category": "SECURITY",     "tip": "Each medallion layer in separate dataset with distinct IAM"},
        {"category": "COST",         "tip": "Bronze in GCS Standard, Silver in Nearline, archive to Coldline"},
        {"category": "PERFORMANCE",  "tip": "Gold layer: materialized views for common query patterns"},
        {"category": "COMPLIANCE",   "tip": "Data lineage tracked via Dataplex for all transformations"},
        {"category": "RELIABILITY",  "tip": "Idempotent transforms — safe to re-run any Bronze → Silver job"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  ALL TEMPLATES INDEX
# ═══════════════════════════════════════════════════════════

TEMPLATES = {
    "network": {
        "name": "Network & Connectivity",
        "description": "VPC, subnets, PSC, interconnect, peering, WAF, load balancing",
        "data": NETWORK_CONNECTIVITY,
    },
    "security": {
        "name": "Security & Compliance",
        "description": "IAM, encryption, VPC-SC, DLP, SIEM, audit, compliance",
        "data": SECURITY_COMPLIANCE,
    },
    "data_analytics": {
        "name": "Data Analytics",
        "description": "Streaming + batch pipeline, medallion storage, ML, dashboards",
        "data": DATA_ANALYTICS,
    },
    "medallion": {
        "name": "Medallion Pattern",
        "description": "Bronze / Silver / Gold data lakehouse architecture",
        "data": MEDALLION_PATTERN,
    },
}
