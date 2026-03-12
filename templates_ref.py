"""
XlArch Reference Templates — Enterprise-grade architecture patterns.
Real flows, real enterprise tools, proper propagation paths.
"""

# ═══════════════════════════════════════════════════════════
#  1. IDENTITY & SECRETS FLOW
#  AD → Cloud Identity → IAM → Workload Identity
#  CyberArk → Secret Manager → Workloads
# ═══════════════════════════════════════════════════════════

IDENTITY_SECRETS = {
    "title": "Identity & Secrets Management",
    "layout": "pipeline",
    "zones": ["corporate", "identity_sync", "cloud_iam", "secrets_mgmt", "workload_auth", "runtime"],
    "lanes": ["user_identity", "service_identity", "secrets"],
    "nodes": [
        # Corporate (source of truth)
        {"id": "active_dir",      "icon": "users",          "label": "Active Directory",     "zone": "corporate",      "lane": "user_identity",    "step": 1},
        {"id": "ad_groups",       "icon": "users",          "label": "AD Security Groups",   "zone": "corporate",      "lane": "service_identity"},
        {"id": "cyberark",        "icon": "kms",            "label": "CyberArk Vault",       "zone": "corporate",      "lane": "secrets",          "step": 1},

        # Identity Sync
        {"id": "gcds",            "icon": "iam",            "label": "GCDS (Dir Sync)",      "zone": "identity_sync",  "lane": "user_identity",    "step": 2},
        {"id": "cloud_identity",  "icon": "iam",            "label": "Cloud Identity",       "zone": "identity_sync",  "lane": "user_identity",    "step": 3},
        {"id": "saml_sso",        "icon": "iam",            "label": "SAML / SSO",           "zone": "identity_sync",  "lane": "service_identity", "step": 2},

        # Cloud IAM
        {"id": "org_policies",    "icon": "iam",            "label": "Org Policies",         "zone": "cloud_iam",      "lane": "user_identity",    "step": 4},
        {"id": "iam_roles",       "icon": "iam",            "label": "IAM Custom Roles",     "zone": "cloud_iam",      "lane": "user_identity"},
        {"id": "iam_conditions",  "icon": "iam",            "label": "IAM Conditions",       "zone": "cloud_iam",      "lane": "service_identity"},
        {"id": "svc_accounts",    "icon": "iam",            "label": "Service Accounts",     "zone": "cloud_iam",      "lane": "service_identity", "step": 4},

        # Secrets Management
        {"id": "secret_mgr",     "icon": "kms",            "label": "Secret Manager",       "zone": "secrets_mgmt",   "lane": "secrets",          "step": 3},
        {"id": "kms_keys",       "icon": "kms",            "label": "Cloud KMS",            "zone": "secrets_mgmt",   "lane": "secrets",          "step": 4},
        {"id": "cert_authority",  "icon": "kms",            "label": "CA Service (mTLS)",    "zone": "secrets_mgmt",   "lane": "service_identity"},

        # Workload Auth
        {"id": "wl_identity",     "icon": "iam",            "label": "Workload Identity",    "zone": "workload_auth",  "lane": "service_identity", "step": 5},
        {"id": "wl_federation",   "icon": "iam",            "label": "WI Federation",        "zone": "workload_auth",  "lane": "user_identity",    "step": 5},
        {"id": "secret_inject",   "icon": "kms",            "label": "Secret Injection",     "zone": "workload_auth",  "lane": "secrets",          "step": 5},

        # Runtime
        {"id": "gke_pods",        "icon": "gke",            "label": "GKE Pods",             "zone": "runtime",        "lane": "service_identity", "step": 6},
        {"id": "cloud_run_svc",   "icon": "cloud_run",      "label": "Cloud Run",            "zone": "runtime",        "lane": "user_identity",    "step": 6},
        {"id": "data_services",   "icon": "bigquery",       "label": "Data Services",        "zone": "runtime",        "lane": "secrets",          "step": 6},
    ],
    "edges": [
        # User identity flow
        {"from": "active_dir",     "to": "gcds"},
        {"from": "gcds",           "to": "cloud_identity"},
        {"from": "cloud_identity", "to": "org_policies"},
        {"from": "org_policies",   "to": "iam_roles"},
        {"from": "iam_roles",      "to": "wl_federation"},
        {"from": "wl_federation",  "to": "cloud_run_svc"},

        # Service identity flow
        {"from": "ad_groups",      "to": "saml_sso"},
        {"from": "saml_sso",       "to": "iam_conditions"},
        {"from": "iam_conditions", "to": "svc_accounts"},
        {"from": "svc_accounts",   "to": "wl_identity"},
        {"from": "cert_authority", "to": "wl_identity"},
        {"from": "wl_identity",    "to": "gke_pods"},

        # Secrets flow
        {"from": "cyberark",       "to": "secret_mgr"},
        {"from": "secret_mgr",     "to": "kms_keys"},
        {"from": "kms_keys",       "to": "secret_inject"},
        {"from": "secret_inject",  "to": "gke_pods"},
        {"from": "secret_inject",  "to": "data_services"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "firewall",     "label": "VPC-SC"},
        {"icon": "dataplex",     "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "SECURITY",    "tip": "GCDS sync — one-way from AD to Cloud Identity, never reverse"},
        {"category": "SECURITY",    "tip": "No service account keys — use Workload Identity Federation only"},
        {"category": "SECURITY",    "tip": "CyberArk secrets synced to Secret Manager via CCP/REST API"},
        {"category": "SECURITY",    "tip": "IAM Conditions: restrict by IP, device, time for sensitive roles"},
        {"category": "SECURITY",    "tip": "Certificate Authority Service for mTLS between all services"},
        {"category": "NETWORK",     "tip": "SAML/SSO via Cloud Identity — enforce MFA for all users"},
        {"category": "COMPLIANCE",  "tip": "Org policies: disable SA key creation, enforce uniform bucket access"},
        {"category": "COMPLIANCE",  "tip": "Admin audit logs exported to SIEM for all IAM changes"},
        {"category": "RELIABILITY", "tip": "Secret rotation automated — 90-day max for all credentials"},
        {"category": "COST",        "tip": "Custom roles over predefined — least privilege reduces blast radius"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  2. ON-PREM TO GCP — How On-Prem Tools Connect to GCP
# ═══════════════════════════════════════════════════════════

ONPREM_TO_GCP = {
    "title": "On-Prem to GCP Connectivity",
    "layout": "pipeline",
    "zones": ["on_prem", "how", "gcp"],
    "lanes": ["identity", "secrets", "database", "compute", "messaging", "monitoring"],
    "nodes": [
        # Identity
        {"id": "ad",              "icon": "users",          "label": "Active Directory",     "zone": "on_prem", "lane": "identity",   "step": 1},
        {"id": "gcds",            "icon": "iam",            "label": "GCDS Sync",            "zone": "how",     "lane": "identity",   "step": 2},
        {"id": "cloud_iam",       "icon": "iam",            "label": "Cloud IAM",            "zone": "gcp",     "lane": "identity",   "step": 3},

        # Secrets
        {"id": "cyberark",        "icon": "kms",            "label": "CyberArk Vault",       "zone": "on_prem", "lane": "secrets",    "step": 1},
        {"id": "vault_api",       "icon": "vpn",            "label": "CCP API / Sync",       "zone": "how",     "lane": "secrets",    "step": 2},
        {"id": "secret_mgr",      "icon": "kms",            "label": "Secret Manager",       "zone": "gcp",     "lane": "secrets",    "step": 3},

        # Database
        {"id": "oracle",          "icon": "oracle",         "label": "Oracle DB",            "zone": "on_prem", "lane": "database",   "step": 1},
        {"id": "interconnect",    "icon": "vpn",            "label": "Interconnect / DMS",   "zone": "how",     "lane": "database",   "step": 2},
        {"id": "bigquery",        "icon": "bigquery",       "label": "BigQuery",             "zone": "gcp",     "lane": "database",   "step": 3},

        # Compute
        {"id": "vmware",          "icon": "compute_engine", "label": "VMware / VMs",         "zone": "on_prem", "lane": "compute",    "step": 1},
        {"id": "ha_vpn",          "icon": "vpn",            "label": "HA Cloud VPN",         "zone": "how",     "lane": "compute",    "step": 2},
        {"id": "gke",             "icon": "gke",            "label": "GKE",                  "zone": "gcp",     "lane": "compute",    "step": 3},

        # Messaging
        {"id": "kafka",           "icon": "kafka",          "label": "Kafka",                "zone": "on_prem", "lane": "messaging",  "step": 1},
        {"id": "kafka_connect",   "icon": "vpn",            "label": "Kafka Connect",        "zone": "how",     "lane": "messaging",  "step": 2},
        {"id": "pubsub",          "icon": "pubsub",         "label": "Pub/Sub",              "zone": "gcp",     "lane": "messaging",  "step": 3},

        # Monitoring
        {"id": "splunk",          "icon": "monitoring",     "label": "Splunk",               "zone": "on_prem", "lane": "monitoring", "step": 1},
        {"id": "log_api",         "icon": "vpn",            "label": "Log Export API",       "zone": "how",     "lane": "monitoring", "step": 2},
        {"id": "cloud_mon",       "icon": "monitoring",     "label": "Cloud Monitoring",     "zone": "gcp",     "lane": "monitoring", "step": 3},
    ],
    "edges": [
        {"from": "ad",         "to": "gcds"},
        {"from": "gcds",       "to": "cloud_iam"},
        {"from": "cyberark",   "to": "vault_api"},
        {"from": "vault_api",  "to": "secret_mgr"},
        {"from": "oracle",     "to": "interconnect"},
        {"from": "interconnect","to": "bigquery"},
        {"from": "vmware",     "to": "ha_vpn"},
        {"from": "ha_vpn",     "to": "gke"},
        {"from": "kafka",      "to": "kafka_connect"},
        {"from": "kafka_connect","to": "pubsub"},
        {"from": "splunk",     "to": "log_api"},
        {"from": "log_api",    "to": "cloud_mon"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "firewall",     "label": "VPC-SC"},
        {"icon": "dns",          "label": "Private DNS"},
    ],
    "bestPractices": [
        {"category": "IDENTITY",    "tip": "GCDS syncs AD groups to Cloud Identity — never manage users in GCP directly"},
        {"category": "SECRETS",     "tip": "CyberArk CCP API syncs credentials to Secret Manager — keys never exported"},
        {"category": "NETWORK",     "tip": "Dedicated Interconnect for database replication (Oracle → BigQuery via DMS)"},
        {"category": "NETWORK",     "tip": "HA Cloud VPN as backup or for smaller sites"},
        {"category": "NETWORK",     "tip": "Private Service Connect — BigQuery, GCS, Cloud SQL accessed privately"},
        {"category": "DATA",        "tip": "Database Migration Service for continuous Oracle → Cloud SQL replication"},
        {"category": "MESSAGING",   "tip": "Kafka Connect with Pub/Sub sink connector — mirror topics to GCP"},
        {"category": "SECURITY",    "tip": "VPC-SC perimeter around all GCP projects — blast radius containment"},
        {"category": "COMPLIANCE",  "tip": "Cloud Logging exported back to Splunk for unified SIEM"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  3. AWS TO GCP (Multi-Cloud)
# ═══════════════════════════════════════════════════════════

AWS_TO_GCP = {
    "title": "AWS to GCP Multi-Cloud Connectivity",
    "layout": "pipeline",
    "zones": ["aws_env", "connectivity", "identity_bridge", "gcp_network", "gcp_workloads", "shared_data"],
    "lanes": ["networking", "identity", "data_path"],
    "nodes": [
        # AWS Environment
        {"id": "aws_vpc",         "icon": "firewall",        "label": "AWS VPC",              "zone": "aws_env",        "lane": "networking",    "step": 1},
        {"id": "aws_iam",         "icon": "iam",             "label": "AWS IAM",              "zone": "aws_env",        "lane": "identity",      "step": 1},
        {"id": "aws_s3",          "icon": "gcs",             "label": "S3 Buckets",           "zone": "aws_env",        "lane": "data_path"},
        {"id": "aws_eks",         "icon": "gke",             "label": "EKS Clusters",         "zone": "aws_env",        "lane": "networking"},

        # Connectivity
        {"id": "aws_tgw",         "icon": "dns",             "label": "Transit Gateway",      "zone": "connectivity",   "lane": "networking",    "step": 2},
        {"id": "partner_ic",      "icon": "vpn",             "label": "Partner Interconnect",  "zone": "connectivity",  "lane": "networking",    "step": 3},
        {"id": "ha_vpn",          "icon": "vpn",             "label": "HA VPN (IPSec)",       "zone": "connectivity",   "lane": "data_path",     "step": 2},

        # Identity Bridge
        {"id": "wi_federation",   "icon": "iam",             "label": "WI Federation",        "zone": "identity_bridge","lane": "identity",      "step": 4},
        {"id": "sts_token",       "icon": "kms",             "label": "STS Token Exchange",   "zone": "identity_bridge","lane": "identity"},
        {"id": "cross_org_iam",   "icon": "iam",             "label": "Cross-Cloud IAM",      "zone": "identity_bridge","lane": "identity"},

        # GCP Network
        {"id": "gcp_vpc",         "icon": "firewall",        "label": "GCP Shared VPC",       "zone": "gcp_network",    "lane": "networking",    "step": 5},
        {"id": "cloud_router_mc", "icon": "dns",             "label": "Cloud Router",         "zone": "gcp_network",    "lane": "networking"},
        {"id": "vpc_sc_mc",       "icon": "firewall",        "label": "VPC-SC Perimeter",     "zone": "gcp_network",    "lane": "data_path",     "step": 5},

        # GCP Workloads
        {"id": "gke_multi",       "icon": "gke",             "label": "GKE (Multi-Cloud)",    "zone": "gcp_workloads",  "lane": "networking",    "step": 6},
        {"id": "anthos",          "icon": "gke",             "label": "Anthos Fleet",         "zone": "gcp_workloads",  "lane": "identity"},

        # Shared Data
        {"id": "bq_omni",         "icon": "bigquery",        "label": "BigQuery Omni",        "zone": "shared_data",    "lane": "data_path",     "step": 7},
        {"id": "gcs_transfer",    "icon": "gcs",             "label": "Storage Transfer",     "zone": "shared_data",    "lane": "data_path"},
        {"id": "dataflow_cross",  "icon": "dataflow",        "label": "Cross-Cloud ETL",      "zone": "shared_data",    "lane": "networking",    "step": 7},
    ],
    "edges": [
        # Network path
        {"from": "aws_vpc",        "to": "aws_tgw"},
        {"from": "aws_tgw",        "to": "partner_ic"},
        {"from": "partner_ic",     "to": "gcp_vpc"},
        {"from": "gcp_vpc",        "to": "cloud_router_mc"},
        {"from": "gcp_vpc",        "to": "gke_multi"},
        {"from": "aws_eks",        "to": "anthos"},

        # Identity
        {"from": "aws_iam",        "to": "wi_federation"},
        {"from": "wi_federation",  "to": "sts_token"},
        {"from": "sts_token",      "to": "cross_org_iam"},
        {"from": "cross_org_iam",  "to": "anthos"},

        # Data
        {"from": "aws_s3",         "to": "ha_vpn"},
        {"from": "ha_vpn",         "to": "vpc_sc_mc"},
        {"from": "vpc_sc_mc",      "to": "bq_omni"},
        {"from": "aws_s3",         "to": "gcs_transfer"},
        {"from": "gke_multi",      "to": "dataflow_cross"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "firewall",     "label": "VPC-SC"},
        {"icon": "dataplex",     "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "NETWORK",     "tip": "Partner Interconnect when direct peering not available — 10 Gbps"},
        {"category": "NETWORK",     "tip": "HA VPN with BGP as backup to Interconnect — auto-failover"},
        {"category": "SECURITY",    "tip": "Workload Identity Federation — AWS IAM roles → GCP SA, no keys"},
        {"category": "SECURITY",    "tip": "VPC-SC around all cross-cloud data access points"},
        {"category": "SECURITY",    "tip": "STS token exchange for short-lived cross-cloud credentials"},
        {"category": "RELIABILITY", "tip": "Anthos Fleet for unified management across EKS and GKE"},
        {"category": "COST",        "tip": "BigQuery Omni to query S3 in-place — avoid data copy costs"},
        {"category": "COMPLIANCE",  "tip": "Audit logs from both clouds into centralized SIEM"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  4. AZURE TO GCP
# ═══════════════════════════════════════════════════════════

AZURE_TO_GCP = {
    "title": "Azure to GCP Multi-Cloud Connectivity",
    "layout": "pipeline",
    "zones": ["azure_env", "connectivity", "identity_bridge", "gcp_network", "gcp_workloads", "shared_data"],
    "lanes": ["networking", "identity", "data_path"],
    "nodes": [
        # Azure
        {"id": "azure_vnet",      "icon": "firewall",        "label": "Azure VNet",           "zone": "azure_env",      "lane": "networking",    "step": 1},
        {"id": "azure_ad",        "icon": "users",           "label": "Azure AD (Entra ID)",  "zone": "azure_env",      "lane": "identity",      "step": 1},
        {"id": "azure_blob",      "icon": "gcs",             "label": "Blob Storage",         "zone": "azure_env",      "lane": "data_path"},
        {"id": "azure_aks",       "icon": "gke",             "label": "AKS Clusters",         "zone": "azure_env",      "lane": "networking"},

        # Connectivity
        {"id": "express_route",   "icon": "vpn",             "label": "ExpressRoute",         "zone": "connectivity",   "lane": "networking",    "step": 2},
        {"id": "partner_ic_az",   "icon": "vpn",             "label": "Partner Interconnect",  "zone": "connectivity",  "lane": "networking",    "step": 3},
        {"id": "ha_vpn_az",       "icon": "vpn",             "label": "HA VPN",               "zone": "connectivity",   "lane": "data_path",     "step": 2},

        # Identity Bridge
        {"id": "aad_federation",  "icon": "iam",             "label": "AAD → WI Fed",         "zone": "identity_bridge","lane": "identity",      "step": 4},
        {"id": "saml_bridge",     "icon": "iam",             "label": "SAML Federation",      "zone": "identity_bridge","lane": "identity"},
        {"id": "gcds_azure",      "icon": "iam",             "label": "GCDS (Azure AD)",      "zone": "identity_bridge","lane": "identity"},

        # GCP Network
        {"id": "gcp_vpc_az",      "icon": "firewall",        "label": "GCP Shared VPC",       "zone": "gcp_network",    "lane": "networking",    "step": 5},
        {"id": "cloud_router_az", "icon": "dns",             "label": "Cloud Router",         "zone": "gcp_network",    "lane": "networking"},
        {"id": "vpc_sc_az",       "icon": "firewall",        "label": "VPC-SC Perimeter",     "zone": "gcp_network",    "lane": "data_path",     "step": 5},

        # GCP Workloads
        {"id": "gke_az",          "icon": "gke",             "label": "GKE Cluster",          "zone": "gcp_workloads",  "lane": "networking",    "step": 6},
        {"id": "anthos_az",       "icon": "gke",             "label": "Anthos Fleet",         "zone": "gcp_workloads",  "lane": "identity"},

        # Shared Data
        {"id": "bq_omni_az",      "icon": "bigquery",        "label": "BigQuery Omni",        "zone": "shared_data",    "lane": "data_path",     "step": 7},
        {"id": "storage_transfer","icon": "gcs",             "label": "Storage Transfer",     "zone": "shared_data",    "lane": "data_path"},
    ],
    "edges": [
        {"from": "azure_vnet",     "to": "express_route"},
        {"from": "express_route",  "to": "partner_ic_az"},
        {"from": "partner_ic_az",  "to": "gcp_vpc_az"},
        {"from": "gcp_vpc_az",     "to": "cloud_router_az"},
        {"from": "gcp_vpc_az",     "to": "gke_az"},
        {"from": "azure_aks",      "to": "anthos_az"},

        {"from": "azure_ad",       "to": "aad_federation"},
        {"from": "aad_federation", "to": "saml_bridge"},
        {"from": "saml_bridge",    "to": "gcds_azure"},
        {"from": "gcds_azure",     "to": "anthos_az"},

        {"from": "azure_blob",     "to": "ha_vpn_az"},
        {"from": "ha_vpn_az",      "to": "vpc_sc_az"},
        {"from": "vpc_sc_az",      "to": "bq_omni_az"},
        {"from": "azure_blob",     "to": "storage_transfer"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "firewall",     "label": "VPC-SC"},
        {"icon": "dataplex",     "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "NETWORK",     "tip": "ExpressRoute to Partner Interconnect via shared peering provider"},
        {"category": "SECURITY",    "tip": "Azure AD → Workload Identity Federation for cross-cloud auth"},
        {"category": "SECURITY",    "tip": "SAML federation for user SSO across Azure and GCP consoles"},
        {"category": "COST",        "tip": "BigQuery Omni for in-place queries on Azure Blob Storage"},
        {"category": "RELIABILITY", "tip": "HA VPN as backup path to ExpressRoute/Interconnect"},
        {"category": "COMPLIANCE",  "tip": "Unified audit logging from both clouds into single SIEM"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  5. GCP LANDING ZONE
#  Org → Folders → Projects → Networking → IAM
# ═══════════════════════════════════════════════════════════

LANDING_ZONE = {
    "title": "GCP Enterprise Landing Zone",
    "layout": "pipeline",
    "zones": ["org_level", "folder_structure", "shared_infra", "security_proj", "workload_proj", "operations"],
    "lanes": ["governance", "networking", "workloads"],
    "nodes": [
        # Org Level
        {"id": "org_node",        "icon": "iam",             "label": "GCP Org Node",         "zone": "org_level",       "lane": "governance",   "step": 1},
        {"id": "billing_acct",    "icon": "monitoring",      "label": "Billing Account",      "zone": "org_level",       "lane": "workloads"},
        {"id": "org_policies_lz", "icon": "iam",             "label": "Org Policies",         "zone": "org_level",       "lane": "governance",   "step": 2},

        # Folder Structure
        {"id": "folder_shared",   "icon": "iam",             "label": "Shared/ Folder",       "zone": "folder_structure","lane": "networking",    "step": 3},
        {"id": "folder_prod",     "icon": "iam",             "label": "Production/ Folder",   "zone": "folder_structure","lane": "workloads",     "step": 3},
        {"id": "folder_dev",      "icon": "iam",             "label": "Dev/ Folder",          "zone": "folder_structure","lane": "governance"},

        # Shared Infrastructure
        {"id": "host_project",    "icon": "firewall",        "label": "VPC Host Project",     "zone": "shared_infra",    "lane": "networking",    "step": 4},
        {"id": "hub_vpc",         "icon": "firewall",        "label": "Hub VPC",              "zone": "shared_infra",    "lane": "networking"},
        {"id": "log_sink",        "icon": "logging",         "label": "Central Log Sink",     "zone": "shared_infra",    "lane": "governance",    "step": 4},

        # Security Project
        {"id": "sec_project",     "icon": "kms",             "label": "Security Project",     "zone": "security_proj",   "lane": "governance",    "step": 5},
        {"id": "kms_project",     "icon": "kms",             "label": "KMS Key Rings",        "zone": "security_proj",   "lane": "governance"},
        {"id": "scc_project",     "icon": "monitoring",      "label": "SCC Premium",          "zone": "security_proj",   "lane": "networking",    "step": 5},

        # Workload Projects
        {"id": "prod_project",    "icon": "gke",             "label": "Prod Project",         "zone": "workload_proj",   "lane": "workloads",     "step": 6},
        {"id": "data_project",    "icon": "bigquery",        "label": "Data Project",         "zone": "workload_proj",   "lane": "workloads"},
        {"id": "ml_project",      "icon": "vertex_ai",       "label": "ML Project",           "zone": "workload_proj",   "lane": "workloads"},
        {"id": "svc_project_net", "icon": "firewall",        "label": "Service Project VPC",  "zone": "workload_proj",   "lane": "networking",    "step": 6},

        # Operations
        {"id": "monitoring_proj", "icon": "monitoring",      "label": "Monitoring Hub",       "zone": "operations",      "lane": "governance",    "step": 7},
        {"id": "alerting",        "icon": "monitoring",      "label": "Alert Policies",       "zone": "operations",      "lane": "networking"},
        {"id": "dashboard",       "icon": "looker",          "label": "Ops Dashboard",        "zone": "operations",      "lane": "workloads",     "step": 7},
    ],
    "edges": [
        # Governance flow
        {"from": "org_node",        "to": "org_policies_lz"},
        {"from": "org_policies_lz", "to": "folder_dev"},
        {"from": "org_policies_lz", "to": "folder_shared"},
        {"from": "folder_dev",      "to": "log_sink"},
        {"from": "log_sink",        "to": "sec_project"},
        {"from": "sec_project",     "to": "kms_project"},
        {"from": "sec_project",     "to": "monitoring_proj"},

        # Networking flow
        {"from": "folder_shared",   "to": "host_project"},
        {"from": "host_project",    "to": "hub_vpc"},
        {"from": "hub_vpc",         "to": "scc_project"},
        {"from": "scc_project",     "to": "svc_project_net"},
        {"from": "svc_project_net", "to": "alerting"},

        # Workload flow
        {"from": "billing_acct",    "to": "folder_prod"},
        {"from": "folder_prod",     "to": "prod_project"},
        {"from": "folder_prod",     "to": "data_project"},
        {"from": "folder_prod",     "to": "ml_project"},
        {"from": "prod_project",    "to": "dashboard"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "SCC Premium"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "firewall",     "label": "Org Policies"},
        {"icon": "dataplex",     "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "SECURITY",    "tip": "Org policies enforced at top — uniform bucket access, disable SA keys"},
        {"category": "SECURITY",    "tip": "Separate security project for KMS, SCC — restricted admin access"},
        {"category": "NETWORK",     "tip": "Shared VPC host project owns all networking — service projects consume"},
        {"category": "NETWORK",     "tip": "Hub-and-spoke VPC topology for network segmentation"},
        {"category": "COMPLIANCE",  "tip": "Central log sink: all audit logs → BigQuery in logging project"},
        {"category": "COMPLIANCE",  "tip": "SCC Premium for vulnerability scanning and threat detection"},
        {"category": "COST",        "tip": "Billing alerts per project folder — budget caps on non-prod"},
        {"category": "RELIABILITY", "tip": "Separate projects per environment — blast radius isolation"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  6. DATA ANALYTICS (Enhanced)
# ═══════════════════════════════════════════════════════════

DATA_ANALYTICS = {
    "title": "Data Analytics Architecture",
    "layout": "pipeline",
    "zones": ["sources", "ingest", "process", "store", "analyze", "serve"],
    "lanes": ["streaming", "batch", "ml"],
    "nodes": [
        {"id": "web_app",         "icon": "cloud_run",    "label": "Web App",              "zone": "sources",  "lane": "streaming"},
        {"id": "mobile_events",   "icon": "functions",    "label": "Mobile Events",        "zone": "sources",  "lane": "streaming"},
        {"id": "app_db",          "icon": "cloudsql",     "label": "Application DB",       "zone": "sources",  "lane": "batch"},
        {"id": "partner_feeds",   "icon": "client",       "label": "Partner Feeds",        "zone": "sources",  "lane": "batch"},

        {"id": "pubsub",          "icon": "pubsub",       "label": "Pub/Sub",              "zone": "ingest",   "lane": "streaming", "step": 1},
        {"id": "composer",        "icon": "composer",      "label": "Cloud Composer",       "zone": "ingest",   "lane": "batch",     "step": 2},

        {"id": "dataflow_stream", "icon": "dataflow",     "label": "Dataflow Streaming",   "zone": "process",  "lane": "streaming", "step": 3},
        {"id": "dataflow_batch",  "icon": "dataflow",     "label": "Dataflow Batch",       "zone": "process",  "lane": "batch",     "step": 4},
        {"id": "dataproc_spark",  "icon": "dataproc",     "label": "Dataproc Spark",       "zone": "process",  "lane": "batch"},

        {"id": "gcs_bronze",      "icon": "gcs",          "label": "GCS Bronze",           "zone": "store",    "lane": "streaming", "step": 5},
        {"id": "gcs_silver",      "icon": "gcs",          "label": "GCS Silver",           "zone": "store",    "lane": "batch",     "step": 6},
        {"id": "bigtable_rt",     "icon": "bigtable",     "label": "Bigtable (RT)",        "zone": "store",    "lane": "streaming"},
        {"id": "bq_gold",         "icon": "bigquery",     "label": "BigQuery Gold",        "zone": "store",    "lane": "batch",     "step": 7},

        {"id": "bq_analytics",    "icon": "bigquery",     "label": "BQ Analytics",         "zone": "analyze",  "lane": "batch",     "step": 8},
        {"id": "vertex_ai",       "icon": "vertex_ai",    "label": "Vertex AI",            "zone": "analyze",  "lane": "ml",        "step": 9},
        {"id": "looker",          "icon": "looker",        "label": "Looker Studio",       "zone": "analyze",  "lane": "batch"},

        {"id": "cache",           "icon": "memorystore",  "label": "Memorystore",          "zone": "serve",    "lane": "streaming"},
        {"id": "api_ep",          "icon": "cloud_run",    "label": "API Endpoint",         "zone": "serve",    "lane": "batch"},
        {"id": "ml_ep",           "icon": "vertex_ai",    "label": "ML Endpoint",          "zone": "serve",    "lane": "ml"},
    ],
    "edges": [
        {"from": "web_app",         "to": "pubsub"},
        {"from": "mobile_events",   "to": "pubsub"},
        {"from": "pubsub",          "to": "dataflow_stream"},
        {"from": "dataflow_stream", "to": "gcs_bronze"},
        {"from": "dataflow_stream", "to": "bigtable_rt"},
        {"from": "bigtable_rt",     "to": "cache"},

        {"from": "app_db",          "to": "composer"},
        {"from": "partner_feeds",   "to": "composer"},
        {"from": "composer",        "to": "dataflow_batch"},
        {"from": "composer",        "to": "dataproc_spark"},
        {"from": "dataflow_batch",  "to": "gcs_silver"},
        {"from": "gcs_bronze",      "to": "gcs_silver"},
        {"from": "gcs_silver",      "to": "bq_gold"},

        {"from": "bq_gold",         "to": "bq_analytics"},
        {"from": "bq_analytics",    "to": "looker"},
        {"from": "bq_analytics",    "to": "api_ep"},
        {"from": "bq_gold",         "to": "vertex_ai"},
        {"from": "vertex_ai",       "to": "ml_ep"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "KMS / CMEK"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "Audit Logs"},
        {"icon": "firewall",     "label": "VPC-SC"},
        {"icon": "dns",          "label": "Private Connect"},
        {"icon": "dataplex",     "label": "Dataplex"},
    ],
    "bestPractices": [
        {"category": "SECURITY",     "tip": "CMEK encryption on BigQuery, GCS, Bigtable, Cloud SQL"},
        {"category": "SECURITY",     "tip": "VPC-SC perimeter around all data projects"},
        {"category": "NETWORK",      "tip": "Private Service Connect for all Google API access"},
        {"category": "RELIABILITY",  "tip": "Pub/Sub dead-letter topics for failed messages"},
        {"category": "RELIABILITY",  "tip": "Cloud Composer 2 in HA mode with auto-scaling"},
        {"category": "COST",         "tip": "Dataflow FlexRS for batch — up to 40% savings"},
        {"category": "COST",         "tip": "GCS lifecycle rules — Bronze to Nearline after 30 days"},
        {"category": "PERFORMANCE",  "tip": "BigQuery partitioned + clustered tables"},
        {"category": "COMPLIANCE",   "tip": "Dataplex for metadata, lineage, and data quality"},
    ],
}


# ═══════════════════════════════════════════════════════════
#  ALL TEMPLATES INDEX
# ═══════════════════════════════════════════════════════════

TEMPLATES = {
    "identity": {
        "name": "Identity & Secrets",
        "description": "AD → Cloud Identity → IAM → Workload Identity, CyberArk → Secret Manager",
        "data": IDENTITY_SECRETS,
    },
    "onprem_gcp": {
        "name": "On-Prem to GCP",
        "description": "Interconnect, VPN, Shared VPC, DNS, PSC — enterprise hybrid connectivity",
        "data": ONPREM_TO_GCP,
    },
    "aws_gcp": {
        "name": "AWS to GCP",
        "description": "Multi-cloud connectivity, identity federation, BigQuery Omni, Anthos",
        "data": AWS_TO_GCP,
    },
    "azure_gcp": {
        "name": "Azure to GCP",
        "description": "ExpressRoute, AAD federation, cross-cloud data access",
        "data": AZURE_TO_GCP,
    },
    "landing_zone": {
        "name": "GCP Landing Zone",
        "description": "Org, folders, projects, networking, IAM — enterprise foundation",
        "data": LANDING_ZONE,
    },
    "data_analytics": {
        "name": "Data Analytics",
        "description": "Streaming + batch pipeline, medallion storage, ML, dashboards",
        "data": DATA_ANALYTICS,
    },
}


# ═══════════════════════════════════════════════════════════
#  HEALTHCARE DIAGNOSTICS — Unified Agentic Platform
# ═══════════════════════════════════════════════════════════

DIAGNOSTICS_AGENTIC = {
    "title": "Diagnostics Agentic Platform",
    "layout": "layered",
    "zones": ["input", "orchestrate", "process", "connect", "store", "govern"],
    "lanes": ["experience", "control", "agents", "protocols", "intelligence", "data"],
    "nodes": [
        # ── EXPERIENCE: Who uses it
        {"id": "physician_portal",  "icon": "users",       "label": "Physician Portal",  "zone": "input",       "lane": "experience", "step": 1},
        {"id": "patient_portal",    "icon": "client",      "label": "Patient Portal",    "zone": "orchestrate", "lane": "experience", "step": 2},
        {"id": "lab_dashboard",     "icon": "monitoring",   "label": "Lab Tech UI",       "zone": "process",     "lane": "experience", "step": 3},

        # ── CONTROL: Master Agent + Guardrails
        {"id": "master_agent",      "icon": "iam",         "label": "Master Agent",      "zone": "orchestrate", "lane": "control",    "step": 4},
        {"id": "guardrails",        "icon": "firewall",    "label": "Guardrails",        "zone": "connect",     "lane": "control",    "step": 5},

        # ── AGENTS: Specialists
        {"id": "test_agent",        "icon": "monitoring",  "label": "Test Agent",        "zone": "input",       "lane": "agents"},
        {"id": "specimen_agent",    "icon": "gcs",         "label": "Specimen Agent",    "zone": "orchestrate", "lane": "agents"},
        {"id": "results_agent",     "icon": "bigquery",    "label": "Results Agent",     "zone": "process",     "lane": "agents"},
        {"id": "ai_companion",      "icon": "vertex_ai",   "label": "AI Companion",      "zone": "connect",     "lane": "agents"},
        {"id": "billing_agent",     "icon": "generic_db",  "label": "Billing Agent",     "zone": "store",       "lane": "agents"},
        {"id": "compliance_agent",  "icon": "kms",         "label": "Compliance Agent",  "zone": "govern",      "lane": "agents"},

        # ── PROTOCOLS: How agents talk
        {"id": "mcp_lis",           "icon": "pubsub",      "label": "MCP (LIS/EHR)",     "zone": "input",       "lane": "protocols"},
        {"id": "a2a",               "icon": "dataflow",    "label": "A2A Protocol",      "zone": "process",     "lane": "protocols"},
        {"id": "fhir_hl7",          "icon": "dns",         "label": "FHIR / HL7",        "zone": "store",       "lane": "protocols"},

        # ── INTELLIGENCE: Brains
        {"id": "llm_gateway",       "icon": "cloud_run",   "label": "LLM Gateway",       "zone": "input",       "lane": "intelligence"},
        {"id": "test_compendium",   "icon": "bigtable",    "label": "Test Compendium",   "zone": "orchestrate", "lane": "intelligence"},
        {"id": "rag_pipeline",      "icon": "dataflow",    "label": "RAG Pipeline",      "zone": "process",     "lane": "intelligence"},
        {"id": "vector_db",         "icon": "spanner",     "label": "Vector DB",         "zone": "connect",     "lane": "intelligence"},

        # ── DATA: Sources
        {"id": "lis",               "icon": "database",    "label": "LIS",               "zone": "input",       "lane": "data"},
        {"id": "ehr_epic",          "icon": "client",      "label": "EHR / EPIC",        "zone": "orchestrate", "lane": "data"},
        {"id": "bq",               "icon": "bigquery",    "label": "BigQuery",          "zone": "process",     "lane": "data"},
        {"id": "gcs_store",        "icon": "gcs",         "label": "GCS",               "zone": "connect",     "lane": "data"},
        {"id": "salesforce",        "icon": "client",      "label": "Salesforce",        "zone": "store",       "lane": "data"},
        {"id": "sharepoint",        "icon": "client",      "label": "SharePoint",        "zone": "govern",      "lane": "data"},
    ],
    "edges": [
        # Experience → Master Agent
        {"from": "physician_portal", "to": "master_agent"},
        {"from": "patient_portal",   "to": "master_agent"},
        {"from": "lab_dashboard",    "to": "master_agent"},

        # Master Agent → Guardrails → Agents
        {"from": "master_agent",     "to": "guardrails"},
        {"from": "guardrails",       "to": "test_agent"},
        {"from": "guardrails",       "to": "specimen_agent"},
        {"from": "guardrails",       "to": "results_agent"},
        {"from": "guardrails",       "to": "ai_companion"},
        {"from": "guardrails",       "to": "billing_agent"},
        {"from": "guardrails",       "to": "compliance_agent"},

        # Agent-to-Agent via A2A
        {"from": "test_agent",       "to": "a2a"},
        {"from": "specimen_agent",   "to": "a2a"},
        {"from": "results_agent",    "to": "a2a"},
        {"from": "billing_agent",    "to": "a2a"},

        # Agents → MCP (external systems)
        {"from": "test_agent",       "to": "mcp_lis"},
        {"from": "specimen_agent",   "to": "mcp_lis"},
        {"from": "results_agent",    "to": "fhir_hl7"},
        {"from": "billing_agent",    "to": "fhir_hl7"},

        # Agents → Intelligence
        {"from": "ai_companion",     "to": "llm_gateway"},
        {"from": "test_agent",       "to": "test_compendium"},
        {"from": "results_agent",    "to": "rag_pipeline"},
        {"from": "compliance_agent", "to": "rag_pipeline"},
        {"from": "rag_pipeline",     "to": "vector_db"},
        {"from": "llm_gateway",      "to": "rag_pipeline"},

        # MCP / Protocols → Data
        {"from": "mcp_lis",          "to": "lis"},
        {"from": "mcp_lis",          "to": "ehr_epic"},
        {"from": "fhir_hl7",        "to": "ehr_epic"},
        {"from": "fhir_hl7",        "to": "salesforce"},

        # Intelligence → Data
        {"from": "test_compendium",  "to": "bq"},
        {"from": "vector_db",        "to": "gcs_store"},
        {"from": "rag_pipeline",     "to": "bq"},
    ],
    "governance": [
        {"icon": "iam",          "label": "IAM"},
        {"icon": "kms",          "label": "HIPAA / CLIA"},
        {"icon": "monitoring",   "label": "Monitoring"},
        {"icon": "logging",      "label": "Audit Trail"},
        {"icon": "firewall",     "label": "PHI Encrypt"},
        {"icon": "dns",          "label": "VPC-SC"},
    ],
    "bestPractices": [
        {"category": "SECURITY",    "tip": "All PHI encrypted at rest (CMEK) and in transit (mTLS)"},
        {"category": "COMPLIANCE",  "tip": "Every agent decision logged to immutable audit trail"},
        {"category": "COMPLIANCE",  "tip": "HIPAA BAA in place for all cloud services processing PHI"},
        {"category": "COMPLIANCE",  "tip": "CLIA/CAP compliance checks automated via Compliance Agent"},
        {"category": "GUARDRAILS",  "tip": "PHI/PII detection on all inputs and outputs"},
        {"category": "GUARDRAILS",  "tip": "Critical lab values trigger mandatory human-in-the-loop"},
        {"category": "RELIABILITY", "tip": "Master Agent escalates to human when confidence < threshold"},
        {"category": "RELIABILITY", "tip": "A2A protocol ensures agent handoffs are tracked end-to-end"},
    ],
}

# Update TEMPLATES index
TEMPLATES["diagnostics_agentic"] = {
    "name": "Diagnostics Agentic Platform",
    "description": "Healthcare diagnostics — Master Agent, Guardrails, Specialist Agents, MCP, A2A",
    "data": DIAGNOSTICS_AGENTIC,
}
