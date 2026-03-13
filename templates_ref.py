"""
XlArch Reference Templates — Enterprise-grade architecture patterns.

RULES:
  - ONE node per zone+lane cell. No crowding.
  - Each lane tells ONE story, reads left to right.
  - Cross-lane edges show dependencies.
  - Governance = reusable security pattern (same everywhere).
"""

# ═══════════════════════════════════════════════════════════
#  1. IDENTITY & SECRETS
# ═══════════════════════════════════════════════════════════

IDENTITY_SECRETS = {
    "title": "Identity & Secrets Management",
    "zones": ["corporate", "boundary", "cloud_iam", "workload"],
    "lanes": ["user_identity", "service_identity", "secrets", "enforcement"],
    "nodes": [
        {"id": "ad",             "icon": "users",          "label": "Active Directory",   "zone": "corporate",  "lane": "user_identity",    "step": 1},
        {"id": "gcds",           "icon": "iam",            "label": "GCDS Sync",          "zone": "boundary",   "lane": "user_identity",    "step": 2},
        {"id": "cloud_id",       "icon": "iam",            "label": "Cloud Identity",     "zone": "cloud_iam",  "lane": "user_identity",    "step": 3},
        {"id": "iam_roles",      "icon": "iam",            "label": "IAM Roles",          "zone": "workload",   "lane": "user_identity",    "step": 4},

        {"id": "onprem_app",     "icon": "compute_engine", "label": "On-Prem App",        "zone": "corporate",  "lane": "service_identity", "step": 1},
        {"id": "wif",            "icon": "iam",            "label": "WI Federation",      "zone": "boundary",   "lane": "service_identity", "step": 2},
        {"id": "gcp_sa",         "icon": "iam",            "label": "GCP Service Acct",   "zone": "cloud_iam",  "lane": "service_identity", "step": 3},
        {"id": "token",          "icon": "kms",            "label": "Short-Lived Token",  "zone": "workload",   "lane": "service_identity", "step": 4},

        {"id": "cyberark",       "icon": "kms",            "label": "CyberArk Vault",     "zone": "corporate",  "lane": "secrets",          "step": 1},
        {"id": "ccp_api",        "icon": "vpn",            "label": "CCP API Sync",       "zone": "boundary",   "lane": "secrets",          "step": 2},
        {"id": "secret_mgr",     "icon": "kms",            "label": "Secret Manager",     "zone": "cloud_iam",  "lane": "secrets",          "step": 3},
        {"id": "secret_inject",  "icon": "gke",            "label": "Workload Inject",    "zone": "workload",   "lane": "secrets",          "step": 4},

        {"id": "ad_groups",      "icon": "users",          "label": "AD Groups",          "zone": "corporate",  "lane": "enforcement"},
        {"id": "domain_restrict","icon": "firewall",       "label": "Domain Restrict",    "zone": "boundary",   "lane": "enforcement"},
        {"id": "sa_key_disable", "icon": "firewall",       "label": "SA Key Disabled",    "zone": "cloud_iam",  "lane": "enforcement"},
        {"id": "cond_iam",       "icon": "firewall",       "label": "Conditional IAM",    "zone": "workload",   "lane": "enforcement"},
    ],
    "edges": [
        {"from": "ad",              "to": "gcds"},
        {"from": "gcds",            "to": "cloud_id"},
        {"from": "cloud_id",        "to": "iam_roles"},
        {"from": "onprem_app",      "to": "wif"},
        {"from": "wif",             "to": "gcp_sa"},
        {"from": "gcp_sa",          "to": "token"},
        {"from": "cyberark",        "to": "ccp_api"},
        {"from": "ccp_api",         "to": "secret_mgr"},
        {"from": "secret_mgr",      "to": "secret_inject"},
        {"from": "ad_groups",       "to": "domain_restrict"},
        {"from": "domain_restrict", "to": "sa_key_disable"},
        {"from": "sa_key_disable",  "to": "cond_iam"},
        {"from": "cloud_id",        "to": "gcp_sa"},
        {"from": "iam_roles",       "to": "token"},
        {"from": "token",           "to": "secret_inject"},
        {"from": "sa_key_disable",  "to": "gcp_sa"},
    ],
    "governance": [
        {"icon": "iam", "label": "IAM"}, {"icon": "kms", "label": "KMS / CMEK"},
        {"icon": "monitoring", "label": "Monitoring"}, {"icon": "logging", "label": "Audit Logs"},
        {"icon": "firewall", "label": "VPC-SC"}, {"icon": "dataplex", "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "IDENTITY",   "tip": "GCDS syncs AD → Cloud Identity. One-way, never reverse."},
        {"category": "IDENTITY",   "tip": "WIF replaces SA keys. Zero exported credentials."},
        {"category": "SECURITY",   "tip": "Org policy: iam.disableServiceAccountKeyCreation everywhere."},
        {"category": "COMPLIANCE", "tip": "Conditional IAM: restrict by device posture, IP, time."},
    ],
}

ONPREM_TO_GCP = {
    "title": "On-Prem to GCP Connectivity",
    "zones": ["on_prem", "how", "gcp"],
    "lanes": ["identity", "secrets", "database", "compute", "messaging", "monitoring"],
    "nodes": [
        {"id": "ad",           "icon": "users",          "label": "Active Directory",  "zone": "on_prem", "lane": "identity",   "step": 1},
        {"id": "gcds",         "icon": "iam",            "label": "GCDS Sync",         "zone": "how",     "lane": "identity",   "step": 2},
        {"id": "cloud_iam",    "icon": "iam",            "label": "Cloud IAM",         "zone": "gcp",     "lane": "identity",   "step": 3},
        {"id": "cyberark",     "icon": "kms",            "label": "CyberArk Vault",    "zone": "on_prem", "lane": "secrets",    "step": 1},
        {"id": "vault_api",    "icon": "vpn",            "label": "CCP API Sync",      "zone": "how",     "lane": "secrets",    "step": 2},
        {"id": "secret_mgr",   "icon": "kms",            "label": "Secret Manager",    "zone": "gcp",     "lane": "secrets",    "step": 3},
        {"id": "oracle",       "icon": "oracle",         "label": "Oracle DB",         "zone": "on_prem", "lane": "database",   "step": 1},
        {"id": "interconnect", "icon": "vpn",            "label": "Interconnect",      "zone": "how",     "lane": "database",   "step": 2},
        {"id": "bigquery",     "icon": "bigquery",       "label": "BigQuery",          "zone": "gcp",     "lane": "database",   "step": 3},
        {"id": "vmware",       "icon": "compute_engine", "label": "VMware / VMs",      "zone": "on_prem", "lane": "compute",    "step": 1},
        {"id": "ha_vpn",       "icon": "vpn",            "label": "HA Cloud VPN",      "zone": "how",     "lane": "compute",    "step": 2},
        {"id": "gke",          "icon": "gke",            "label": "GKE",               "zone": "gcp",     "lane": "compute",    "step": 3},
        {"id": "kafka",        "icon": "kafka",          "label": "Kafka",             "zone": "on_prem", "lane": "messaging",  "step": 1},
        {"id": "kafka_connect","icon": "vpn",            "label": "Kafka Connect",     "zone": "how",     "lane": "messaging",  "step": 2},
        {"id": "pubsub",       "icon": "pubsub",         "label": "Pub/Sub",           "zone": "gcp",     "lane": "messaging",  "step": 3},
        {"id": "splunk",       "icon": "monitoring",     "label": "Splunk",            "zone": "on_prem", "lane": "monitoring", "step": 1},
        {"id": "log_api",      "icon": "vpn",            "label": "Log Export API",    "zone": "how",     "lane": "monitoring", "step": 2},
        {"id": "cloud_mon",    "icon": "monitoring",     "label": "Cloud Monitoring",  "zone": "gcp",     "lane": "monitoring", "step": 3},
    ],
    "edges": [
        {"from": "ad",         "to": "gcds"},        {"from": "gcds",       "to": "cloud_iam"},
        {"from": "cyberark",   "to": "vault_api"},   {"from": "vault_api",  "to": "secret_mgr"},
        {"from": "oracle",     "to": "interconnect"},{"from": "interconnect","to": "bigquery"},
        {"from": "vmware",     "to": "ha_vpn"},      {"from": "ha_vpn",     "to": "gke"},
        {"from": "kafka",      "to": "kafka_connect"},{"from": "kafka_connect","to": "pubsub"},
        {"from": "splunk",     "to": "log_api"},     {"from": "log_api",    "to": "cloud_mon"},
    ],
    "governance": [
        {"icon": "iam", "label": "IAM"}, {"icon": "kms", "label": "KMS / CMEK"},
        {"icon": "monitoring", "label": "Monitoring"}, {"icon": "logging", "label": "Audit Logs"},
        {"icon": "firewall", "label": "VPC-SC"}, {"icon": "dns", "label": "Private DNS"},
    ],
    "bestPractices": [
        {"category": "NETWORK", "tip": "Dedicated Interconnect for database replication"},
        {"category": "NETWORK", "tip": "HA Cloud VPN as backup or for smaller sites"},
        {"category": "SECURITY","tip": "VPC-SC perimeter around all GCP projects"},
    ],
}

AWS_TO_GCP = {
    "title": "AWS to GCP Multi-Cloud",
    "zones": ["aws", "connectivity", "gcp_network", "gcp_workload"],
    "lanes": ["networking", "identity", "data"],
    "nodes": [
        {"id": "aws_vpc",   "icon": "firewall", "label": "AWS VPC",          "zone": "aws",          "lane": "networking", "step": 1},
        {"id": "tgw",       "icon": "dns",      "label": "Transit Gateway",  "zone": "connectivity", "lane": "networking", "step": 2},
        {"id": "gcp_vpc",   "icon": "firewall", "label": "GCP Shared VPC",   "zone": "gcp_network",  "lane": "networking", "step": 3},
        {"id": "gke",       "icon": "gke",      "label": "GKE Cluster",      "zone": "gcp_workload", "lane": "networking", "step": 4},
        {"id": "aws_iam",   "icon": "iam",      "label": "AWS IAM",          "zone": "aws",          "lane": "identity",   "step": 1},
        {"id": "wif",       "icon": "iam",      "label": "WI Federation",    "zone": "connectivity", "lane": "identity",   "step": 2},
        {"id": "cross_iam", "icon": "iam",      "label": "Cross-Cloud IAM",  "zone": "gcp_network",  "lane": "identity",   "step": 3},
        {"id": "anthos",    "icon": "gke",      "label": "Anthos Fleet",     "zone": "gcp_workload", "lane": "identity",   "step": 4},
        {"id": "s3",        "icon": "gcs",      "label": "S3 Buckets",       "zone": "aws",          "lane": "data",       "step": 1},
        {"id": "ha_vpn",    "icon": "vpn",      "label": "HA VPN (IPSec)",   "zone": "connectivity", "lane": "data",       "step": 2},
        {"id": "vpc_sc",    "icon": "firewall", "label": "VPC-SC Perimeter", "zone": "gcp_network",  "lane": "data",       "step": 3},
        {"id": "bq_omni",   "icon": "bigquery", "label": "BigQuery Omni",    "zone": "gcp_workload", "lane": "data",       "step": 4},
    ],
    "edges": [
        {"from": "aws_vpc",  "to": "tgw"},       {"from": "tgw",      "to": "gcp_vpc"},   {"from": "gcp_vpc", "to": "gke"},
        {"from": "aws_iam",  "to": "wif"},        {"from": "wif",      "to": "cross_iam"}, {"from": "cross_iam","to": "anthos"},
        {"from": "s3",       "to": "ha_vpn"},     {"from": "ha_vpn",   "to": "vpc_sc"},    {"from": "vpc_sc",  "to": "bq_omni"},
        {"from": "gcp_vpc",  "to": "vpc_sc"},     {"from": "cross_iam","to": "gke"},
    ],
    "governance": [
        {"icon": "iam", "label": "IAM"}, {"icon": "kms", "label": "KMS / CMEK"},
        {"icon": "monitoring", "label": "Monitoring"}, {"icon": "logging", "label": "Audit Logs"},
        {"icon": "firewall", "label": "VPC-SC"}, {"icon": "dataplex", "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "NETWORK",  "tip": "Transit Gateway + Partner Interconnect for dedicated bandwidth"},
        {"category": "SECURITY", "tip": "WIF — AWS IAM roles → GCP SA, no keys"},
        {"category": "COST",     "tip": "BigQuery Omni to query S3 in-place — avoid data copy"},
    ],
}

AZURE_TO_GCP = {
    "title": "Azure to GCP Multi-Cloud",
    "zones": ["azure", "connectivity", "gcp_network", "gcp_workload"],
    "lanes": ["networking", "identity", "data"],
    "nodes": [
        {"id": "azure_vnet",    "icon": "firewall", "label": "Azure VNet",       "zone": "azure",        "lane": "networking", "step": 1},
        {"id": "express_route", "icon": "vpn",      "label": "ExpressRoute",     "zone": "connectivity", "lane": "networking", "step": 2},
        {"id": "gcp_vpc",       "icon": "firewall", "label": "GCP Shared VPC",   "zone": "gcp_network",  "lane": "networking", "step": 3},
        {"id": "gke",           "icon": "gke",      "label": "GKE Cluster",      "zone": "gcp_workload", "lane": "networking", "step": 4},
        {"id": "entra_id",      "icon": "users",    "label": "Entra ID",         "zone": "azure",        "lane": "identity",   "step": 1},
        {"id": "saml_fed",      "icon": "iam",      "label": "SAML Federation",  "zone": "connectivity", "lane": "identity",   "step": 2},
        {"id": "cloud_id",      "icon": "iam",      "label": "Cloud Identity",   "zone": "gcp_network",  "lane": "identity",   "step": 3},
        {"id": "anthos",        "icon": "gke",      "label": "Anthos Fleet",     "zone": "gcp_workload", "lane": "identity",   "step": 4},
        {"id": "blob",          "icon": "gcs",      "label": "Blob Storage",     "zone": "azure",        "lane": "data",       "step": 1},
        {"id": "ha_vpn",        "icon": "vpn",      "label": "HA VPN",           "zone": "connectivity", "lane": "data",       "step": 2},
        {"id": "vpc_sc",        "icon": "firewall", "label": "VPC-SC Perimeter", "zone": "gcp_network",  "lane": "data",       "step": 3},
        {"id": "bq_omni",       "icon": "bigquery", "label": "BigQuery Omni",    "zone": "gcp_workload", "lane": "data",       "step": 4},
    ],
    "edges": [
        {"from": "azure_vnet",   "to": "express_route"}, {"from": "express_route","to": "gcp_vpc"},   {"from": "gcp_vpc", "to": "gke"},
        {"from": "entra_id",     "to": "saml_fed"},      {"from": "saml_fed",     "to": "cloud_id"},  {"from": "cloud_id","to": "anthos"},
        {"from": "blob",         "to": "ha_vpn"},        {"from": "ha_vpn",       "to": "vpc_sc"},    {"from": "vpc_sc",  "to": "bq_omni"},
        {"from": "gcp_vpc",      "to": "vpc_sc"},        {"from": "cloud_id",     "to": "gke"},
    ],
    "governance": [
        {"icon": "iam", "label": "IAM"}, {"icon": "kms", "label": "KMS / CMEK"},
        {"icon": "monitoring", "label": "Monitoring"}, {"icon": "logging", "label": "Audit Logs"},
        {"icon": "firewall", "label": "VPC-SC"}, {"icon": "dataplex", "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "NETWORK",  "tip": "ExpressRoute to Partner Interconnect via shared peering"},
        {"category": "SECURITY", "tip": "Entra ID → SAML Federation for cross-cloud SSO"},
        {"category": "COST",     "tip": "BigQuery Omni for in-place queries on Blob Storage"},
    ],
}

LANDING_ZONE = {
    "title": "GCP Landing Zone",
    "zones": ["org_level", "shared_infra", "security", "workloads"],
    "lanes": ["governance", "networking", "compute"],
    "nodes": [
        {"id": "org_node",      "icon": "iam",        "label": "GCP Org Node",      "zone": "org_level",    "lane": "governance", "step": 1},
        {"id": "host_project",  "icon": "firewall",   "label": "VPC Host Project",  "zone": "shared_infra", "lane": "governance", "step": 2},
        {"id": "sec_project",   "icon": "kms",        "label": "Security Project",  "zone": "security",     "lane": "governance", "step": 3},
        {"id": "ops_dashboard", "icon": "monitoring",  "label": "Ops Dashboard",     "zone": "workloads",    "lane": "governance", "step": 4},
        {"id": "org_policies",  "icon": "firewall",   "label": "Org Policies",      "zone": "org_level",    "lane": "networking"},
        {"id": "hub_vpc",       "icon": "firewall",   "label": "Hub VPC",           "zone": "shared_infra", "lane": "networking", "step": 2},
        {"id": "scc",           "icon": "monitoring",  "label": "SCC Premium",       "zone": "security",     "lane": "networking"},
        {"id": "svc_vpc",       "icon": "firewall",   "label": "Service VPC",       "zone": "workloads",    "lane": "networking"},
        {"id": "billing",       "icon": "generic_db",  "label": "Billing Account",   "zone": "org_level",    "lane": "compute"},
        {"id": "log_sink",      "icon": "logging",    "label": "Central Log Sink",  "zone": "shared_infra", "lane": "compute"},
        {"id": "kms_project",   "icon": "kms",        "label": "KMS Key Rings",     "zone": "security",     "lane": "compute"},
        {"id": "prod_project",  "icon": "gke",        "label": "Prod Project",      "zone": "workloads",    "lane": "compute", "step": 4},
    ],
    "edges": [
        {"from": "org_node",     "to": "host_project"}, {"from": "host_project","to": "sec_project"}, {"from": "sec_project", "to": "ops_dashboard"},
        {"from": "org_policies", "to": "hub_vpc"},       {"from": "hub_vpc",     "to": "scc"},          {"from": "scc",         "to": "svc_vpc"},
        {"from": "billing",      "to": "log_sink"},      {"from": "log_sink",    "to": "kms_project"},  {"from": "kms_project", "to": "prod_project"},
        {"from": "org_node",     "to": "org_policies"},  {"from": "host_project","to": "hub_vpc"},
        {"from": "svc_vpc",      "to": "prod_project"},  {"from": "sec_project", "to": "kms_project"},
    ],
    "governance": [
        {"icon": "iam", "label": "IAM"}, {"icon": "kms", "label": "KMS / CMEK"},
        {"icon": "monitoring", "label": "Monitoring"}, {"icon": "logging", "label": "Audit Logs"},
        {"icon": "firewall", "label": "VPC-SC"}, {"icon": "dataplex", "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "GOVERNANCE", "tip": "Org policies at org level — cascades to all folders/projects"},
        {"category": "NETWORK",    "tip": "Hub-and-spoke VPC: host project owns network"},
        {"category": "SECURITY",   "tip": "Dedicated security project for KMS, SCC, audit sinks"},
    ],
}

DATA_ANALYTICS = {
    "title": "Data Analytics Architecture",
    "zones": ["sources", "ingest", "process", "store", "analyze", "serve"],
    "lanes": ["streaming", "batch", "ml"],
    "nodes": [
        {"id": "web_app",         "icon": "client",      "label": "Web App",          "zone": "sources",  "lane": "streaming", "step": 1},
        {"id": "pubsub",          "icon": "pubsub",      "label": "Pub/Sub",          "zone": "ingest",   "lane": "streaming", "step": 2},
        {"id": "dataflow_stream", "icon": "dataflow",    "label": "Dataflow Stream",  "zone": "process",  "lane": "streaming", "step": 3},
        {"id": "gcs_bronze",      "icon": "gcs",         "label": "GCS Bronze",       "zone": "store",    "lane": "streaming", "step": 4},
        {"id": "bigtable",        "icon": "bigtable",    "label": "Bigtable (RT)",    "zone": "analyze",  "lane": "streaming", "step": 5},
        {"id": "memorystore",     "icon": "memorystore", "label": "Memorystore",      "zone": "serve",    "lane": "streaming", "step": 6},

        {"id": "app_db",          "icon": "database",    "label": "Application DB",   "zone": "sources",  "lane": "batch"},
        {"id": "composer",        "icon": "composer",    "label": "Cloud Composer",   "zone": "ingest",   "lane": "batch",     "step": 2},
        {"id": "dataflow_batch",  "icon": "dataflow",    "label": "Dataflow Batch",   "zone": "process",  "lane": "batch",     "step": 4},
        {"id": "gcs_silver",      "icon": "gcs",         "label": "GCS Silver",       "zone": "store",    "lane": "batch",     "step": 6},
        {"id": "bq_analytics",    "icon": "bigquery",    "label": "BQ Analytics",     "zone": "analyze",  "lane": "batch",     "step": 8},
        {"id": "api_endpoint",    "icon": "cloud_run",   "label": "API Endpoint",     "zone": "serve",    "lane": "batch"},

        {"id": "vertex",          "icon": "vertex_ai",   "label": "Vertex AI",        "zone": "analyze",  "lane": "ml",        "step": 9},
        {"id": "ml_endpoint",     "icon": "vertex_ai",   "label": "ML Endpoint",      "zone": "serve",    "lane": "ml"},
    ],
    "edges": [
        {"from": "web_app",        "to": "pubsub"},        {"from": "pubsub",         "to": "dataflow_stream"},
        {"from": "dataflow_stream","to": "gcs_bronze"},    {"from": "gcs_bronze",     "to": "bigtable"},
        {"from": "bigtable",       "to": "memorystore"},
        {"from": "app_db",         "to": "composer"},       {"from": "composer",       "to": "dataflow_batch"},
        {"from": "dataflow_batch", "to": "gcs_silver"},    {"from": "gcs_silver",     "to": "bq_analytics"},
        {"from": "bq_analytics",   "to": "api_endpoint"},
        {"from": "gcs_bronze",     "to": "gcs_silver"},
        {"from": "bq_analytics",   "to": "vertex"},        {"from": "vertex",         "to": "ml_endpoint"},
    ],
    "governance": [
        {"icon": "iam", "label": "IAM"}, {"icon": "kms", "label": "KMS / CMEK"},
        {"icon": "monitoring", "label": "Monitoring"}, {"icon": "logging", "label": "Audit Logs"},
        {"icon": "firewall", "label": "VPC-SC"}, {"icon": "dns", "label": "Private Connect"},
        {"icon": "dataplex", "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "DATA",        "tip": "Medallion: Bronze (raw) → Silver (cleansed) → Gold (business)"},
        {"category": "PERFORMANCE", "tip": "Bigtable for sub-10ms reads, Memorystore for sub-1ms cache"},
        {"category": "SECURITY",    "tip": "CMEK on all storage — separate keys per tier"},
    ],
}

TEMPLATES = {
    "identity":       {"name": "Identity & Secrets",  "description": "AD → Cloud Identity → IAM → WIF", "data": IDENTITY_SECRETS},
    "onprem_gcp":     {"name": "On-Prem to GCP",      "description": "Tool-by-tool connectivity",        "data": ONPREM_TO_GCP},
    "aws_gcp":        {"name": "AWS to GCP",           "description": "Multi-cloud networking + identity","data": AWS_TO_GCP},
    "azure_gcp":      {"name": "Azure to GCP",         "description": "Entra ID, ExpressRoute, BQ Omni", "data": AZURE_TO_GCP},
    "landing_zone":   {"name": "GCP Landing Zone",     "description": "Org, projects, networking, IAM",  "data": LANDING_ZONE},
    "data_analytics": {"name": "Data Analytics",       "description": "Streaming + batch + ML pipeline", "data": DATA_ANALYTICS},
}

# Diagnostics Agentic
DIAGNOSTICS_AGENTIC = {
    "title": "Diagnostics Agentic Platform",
    "zones": ["input", "orchestrate", "process", "connect", "store"],
    "lanes": ["experience", "control", "agents", "protocols", "intelligence", "data"],
    "nodes": [
        {"id": "physician_portal", "icon": "users",      "label": "Physician Portal", "zone": "input",       "lane": "experience", "step": 1},
        {"id": "patient_portal",   "icon": "client",     "label": "Patient Portal",   "zone": "orchestrate", "lane": "experience", "step": 2},
        {"id": "lab_dashboard",    "icon": "monitoring",  "label": "Lab Tech UI",      "zone": "process",     "lane": "experience", "step": 3},
        {"id": "master_agent",     "icon": "iam",        "label": "Master Agent",     "zone": "orchestrate", "lane": "control",    "step": 4},
        {"id": "guardrails",       "icon": "firewall",   "label": "Guardrails",       "zone": "connect",     "lane": "control",    "step": 5},
        {"id": "test_agent",       "icon": "monitoring",  "label": "Test Agent",       "zone": "input",       "lane": "agents"},
        {"id": "specimen_agent",   "icon": "gcs",        "label": "Specimen Agent",   "zone": "orchestrate", "lane": "agents"},
        {"id": "results_agent",    "icon": "bigquery",   "label": "Results Agent",    "zone": "process",     "lane": "agents"},
        {"id": "ai_companion",     "icon": "vertex_ai",  "label": "AI Companion",     "zone": "connect",     "lane": "agents"},
        {"id": "billing_agent",    "icon": "generic_db",  "label": "Billing Agent",    "zone": "store",       "lane": "agents"},
        {"id": "mcp_lis",          "icon": "pubsub",     "label": "MCP (LIS/EHR)",    "zone": "input",       "lane": "protocols"},
        {"id": "a2a",              "icon": "dataflow",   "label": "A2A Protocol",     "zone": "process",     "lane": "protocols"},
        {"id": "fhir_hl7",         "icon": "dns",        "label": "FHIR / HL7",       "zone": "store",       "lane": "protocols"},
        {"id": "llm_gateway",      "icon": "cloud_run",  "label": "LLM Gateway",      "zone": "input",       "lane": "intelligence"},
        {"id": "test_compendium",  "icon": "bigtable",   "label": "Test Compendium",  "zone": "orchestrate", "lane": "intelligence"},
        {"id": "rag_pipeline",     "icon": "dataflow",   "label": "RAG Pipeline",     "zone": "process",     "lane": "intelligence"},
        {"id": "vector_db",        "icon": "spanner",    "label": "Vector DB",        "zone": "connect",     "lane": "intelligence"},
        {"id": "lis",              "icon": "database",   "label": "LIS",              "zone": "input",       "lane": "data"},
        {"id": "ehr_epic",         "icon": "client",     "label": "EHR / EPIC",       "zone": "orchestrate", "lane": "data"},
        {"id": "bq",               "icon": "bigquery",   "label": "BigQuery",         "zone": "process",     "lane": "data"},
        {"id": "gcs_store",        "icon": "gcs",        "label": "GCS",              "zone": "connect",     "lane": "data"},
        {"id": "salesforce",       "icon": "client",     "label": "Salesforce",       "zone": "store",       "lane": "data"},
    ],
    "edges": [
        {"from": "physician_portal","to": "master_agent"}, {"from": "patient_portal","to": "master_agent"},
        {"from": "lab_dashboard",   "to": "master_agent"}, {"from": "master_agent",  "to": "guardrails"},
        {"from": "guardrails",      "to": "test_agent"},   {"from": "guardrails",    "to": "specimen_agent"},
        {"from": "guardrails",      "to": "results_agent"},{"from": "guardrails",    "to": "ai_companion"},
        {"from": "guardrails",      "to": "billing_agent"},
        {"from": "test_agent",      "to": "mcp_lis"},      {"from": "results_agent", "to": "a2a"},
        {"from": "billing_agent",   "to": "fhir_hl7"},
        {"from": "ai_companion",    "to": "llm_gateway"},  {"from": "test_agent",    "to": "test_compendium"},
        {"from": "results_agent",   "to": "rag_pipeline"}, {"from": "rag_pipeline",  "to": "vector_db"},
        {"from": "mcp_lis",         "to": "lis"},           {"from": "mcp_lis",       "to": "ehr_epic"},
        {"from": "fhir_hl7",        "to": "salesforce"},
        {"from": "test_compendium", "to": "bq"},            {"from": "vector_db",     "to": "gcs_store"},
    ],
    "governance": [
        {"icon": "iam", "label": "IAM"}, {"icon": "kms", "label": "HIPAA / CLIA"},
        {"icon": "monitoring", "label": "Monitoring"}, {"icon": "logging", "label": "Audit Trail"},
        {"icon": "firewall", "label": "PHI Encrypt"}, {"icon": "dns", "label": "VPC-SC"},
    ],
    "bestPractices": [
        {"category": "SECURITY",   "tip": "All PHI encrypted at rest (CMEK) and in transit (mTLS)"},
        {"category": "COMPLIANCE", "tip": "Every agent decision logged to immutable audit trail"},
        {"category": "GUARDRAILS", "tip": "Critical lab values trigger mandatory human-in-the-loop"},
    ],
}
TEMPLATES["diagnostics_agentic"] = {"name": "Diagnostics Agentic Platform", "description": "Healthcare diagnostics agents", "data": DIAGNOSTICS_AGENTIC}


# ═══════════════════════════════════════════════════════════
#  CONNECTIVITY PATTERN — The Complete Foundation
#
#  Everything linked. Identity creates SAs. SAs get tokens.
#  Tokens + secrets = workload authenticates. Network carries
#  the traffic. Enforcement controls it all. Observability
#  watches every step.
#
#  THIS is the pattern. Every architecture rides on it.
# ═══════════════════════════════════════════════════════════

CONNECTIVITY_PATTERN = {
    "title": "Connectivity Pattern",
    "zones": ["corporate", "boundary", "gcp_control", "workload"],
    "lanes": ["identity", "service_acct", "secrets", "network", "enforcement", "observability"],
    "nodes": [
        # IDENTITY: How humans prove who they are
        {"id": "ad",             "icon": "users",          "label": "Active Directory",  "zone": "corporate",   "lane": "identity",      "step": 1},
        {"id": "entra",          "icon": "users",          "label": "Entra ID",          "zone": "boundary",    "lane": "identity",      "step": 2},
        {"id": "cloud_id",       "icon": "iam",            "label": "Cloud Identity",    "zone": "gcp_control", "lane": "identity",      "step": 3},
        {"id": "iam_roles",      "icon": "iam",            "label": "IAM Roles",         "zone": "workload",    "lane": "identity",      "step": 4},

        # SERVICE ACCOUNTS: How apps authenticate (no keys)
        {"id": "onprem_app",     "icon": "compute_engine", "label": "On-Prem App",       "zone": "corporate",   "lane": "service_acct",  "step": 1},
        {"id": "wif",            "icon": "iam",            "label": "WI Federation",     "zone": "boundary",    "lane": "service_acct",  "step": 2},
        {"id": "gcp_sa",         "icon": "iam",            "label": "GCP Service Acct",  "zone": "gcp_control", "lane": "service_acct",  "step": 3},
        {"id": "token",          "icon": "kms",            "label": "Short-Lived Token", "zone": "workload",    "lane": "service_acct",  "step": 4},

        # SECRETS: How credentials flow and rotate
        {"id": "cyberark",       "icon": "kms",            "label": "CyberArk Vault",    "zone": "corporate",   "lane": "secrets",       "step": 1},
        {"id": "ccp_sync",       "icon": "vpn",            "label": "CCP API Sync",      "zone": "boundary",    "lane": "secrets",       "step": 2},
        {"id": "secret_mgr",     "icon": "kms",            "label": "Secret Manager",    "zone": "gcp_control", "lane": "secrets",       "step": 3},
        {"id": "inject",         "icon": "gke",            "label": "Workload Inject",   "zone": "workload",    "lane": "secrets",       "step": 4},

        # NETWORK: The physical path — no public internet
        {"id": "corp_lan",       "icon": "client",         "label": "Corp Network",      "zone": "corporate",   "lane": "network",       "step": 1},
        {"id": "interconnect",   "icon": "vpn",            "label": "Interconnect",      "zone": "boundary",    "lane": "network",       "step": 2},
        {"id": "shared_vpc",     "icon": "firewall",       "label": "Shared VPC",        "zone": "gcp_control", "lane": "network",       "step": 3},
        {"id": "psc",            "icon": "dns",            "label": "PSC Endpoint",      "zone": "workload",    "lane": "network",       "step": 4},

        # ENFORCEMENT: Guardrails that prevent misconfiguration
        {"id": "ad_groups",      "icon": "users",          "label": "AD Groups",         "zone": "corporate",   "lane": "enforcement"},
        {"id": "domain_restrict","icon": "firewall",       "label": "Domain Restrict",   "zone": "boundary",    "lane": "enforcement"},
        {"id": "vpc_sc",         "icon": "firewall",       "label": "VPC-SC Perimeter",  "zone": "gcp_control", "lane": "enforcement"},
        {"id": "cond_iam",       "icon": "firewall",       "label": "Conditional IAM",   "zone": "workload",    "lane": "enforcement"},

        # OBSERVABILITY: How you know it's working
        {"id": "siem",           "icon": "monitoring",     "label": "SIEM / Splunk",     "zone": "corporate",   "lane": "observability"},
        {"id": "audit_log",      "icon": "logging",        "label": "Audit Events",      "zone": "boundary",    "lane": "observability"},
        {"id": "cloud_logging",  "icon": "logging",        "label": "Cloud Logging",     "zone": "gcp_control", "lane": "observability"},
        {"id": "alerts",         "icon": "monitoring",     "label": "Monitoring/Alerts",  "zone": "workload",    "lane": "observability"},
    ],
    "edges": [
        # ── Horizontal: each lane's own chain
        # Identity
        {"from": "ad",             "to": "entra"},
        {"from": "entra",          "to": "cloud_id"},
        {"from": "cloud_id",       "to": "iam_roles"},
        # Service accounts
        {"from": "onprem_app",     "to": "wif"},
        {"from": "wif",            "to": "gcp_sa"},
        {"from": "gcp_sa",         "to": "token"},
        # Secrets
        {"from": "cyberark",       "to": "ccp_sync"},
        {"from": "ccp_sync",       "to": "secret_mgr"},
        {"from": "secret_mgr",     "to": "inject"},
        # Network
        {"from": "corp_lan",       "to": "interconnect"},
        {"from": "interconnect",   "to": "shared_vpc"},
        {"from": "shared_vpc",     "to": "psc"},
        # Enforcement
        {"from": "ad_groups",      "to": "domain_restrict"},
        {"from": "domain_restrict","to": "vpc_sc"},
        {"from": "vpc_sc",         "to": "cond_iam"},
        # Observability
        {"from": "siem",           "to": "audit_log"},
        {"from": "audit_log",      "to": "cloud_logging"},
        {"from": "cloud_logging",  "to": "alerts"},

        # ── Cross-lane: HOW THEY LINK
        # Identity creates service accounts
        {"from": "cloud_id",       "to": "gcp_sa"},
        # IAM roles authorize the token
        {"from": "iam_roles",      "to": "token"},
        # Token + secret = workload can authenticate
        {"from": "token",          "to": "inject"},
        # Workload reaches resource via network
        {"from": "inject",         "to": "psc"},
        # Enforcement controls network
        {"from": "vpc_sc",         "to": "shared_vpc"},
        # Enforcement controls SA
        {"from": "cond_iam",       "to": "token"},
        # Observability watches identity
        {"from": "cloud_id",       "to": "cloud_logging"},
        # Observability watches network
        {"from": "shared_vpc",     "to": "cloud_logging"},
        # Observability watches secrets
        {"from": "secret_mgr",     "to": "cloud_logging"},
    ],
    "governance": [],
    "bestPractices": [
        {"category": "IDENTITY",      "tip": "AD → Entra ID → Cloud Identity. One-way sync. Never manage users in GCP directly."},
        {"category": "SERVICE_ACCT",   "tip": "Workload Identity Federation replaces SA keys. Zero exported credentials."},
        {"category": "SECRETS",        "tip": "CyberArk → Secret Manager via CCP API. Auto-rotate every 90 days."},
        {"category": "NETWORK",        "tip": "Dedicated Interconnect + PSC. No public IPs, no public endpoints."},
        {"category": "ENFORCEMENT",    "tip": "VPC-SC perimeter. Domain restriction. SA key creation disabled org-wide."},
        {"category": "OBSERVABILITY",  "tip": "Every IAM change, every secret access, every network flow → Cloud Logging → Alerts."},
    ],
}

TEMPLATES["connectivity"] = {
    "name": "Connectivity Pattern",
    "description": "The complete foundation — identity, SA, secrets, network, enforcement, observability — all linked",
    "data": CONNECTIVITY_PATTERN,
}
