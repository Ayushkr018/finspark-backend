import uuid
from datetime import datetime
from typing import Dict, List

# ── Adapter Registry ──────────────────────────────────────────────────────────
ADAPTERS: Dict[str, dict] = {
    "cibil-v3": {
        "id": "cibil-v3",
        "name": "CIBIL Credit Bureau",
        "category": "Credit Bureau",
        "version": "v3",
        "versions": ["v1", "v2", "v3"],
        "status": "active",
        "description": "TransUnion CIBIL score and report integration for Indian lending",
        "endpoints": [
            {"method": "POST", "path": "/inquiry", "description": "Credit inquiry"},
            {"method": "GET",  "path": "/report/{id}", "description": "Fetch report"},
        ],
        "required_fields": ["pan_number", "dob", "consent_flag"],
        "optional_fields": ["mobile", "email", "address"],
        "auth_type": "API_KEY",
        "sla_ms": 800,
        "icon": "🏦",
    },
    "experian-v2": {
        "id": "experian-v2",
        "name": "Experian Bureau",
        "category": "Credit Bureau",
        "version": "v2",
        "versions": ["v1", "v2"],
        "status": "active",
        "description": "Experian credit score and FOIR calculation",
        "endpoints": [
            {"method": "POST", "path": "/score",  "description": "Get credit score"},
            {"method": "POST", "path": "/report", "description": "Detailed credit report"},
        ],
        "required_fields": ["pan_number", "full_name", "dob"],
        "optional_fields": ["aadhaar_last4", "mobile"],
        "auth_type": "OAUTH2",
        "sla_ms": 1200,
        "icon": "📊",
    },
    "karza-kyc-v2": {
        "id": "karza-kyc-v2",
        "name": "Karza KYC",
        "category": "KYC",
        "version": "v2",
        "versions": ["v1", "v2"],
        "status": "active",
        "description": "Aadhaar, PAN, GST, and bank account verification",
        "endpoints": [
            {"method": "POST", "path": "/aadhaar/verify",  "description": "Aadhaar OTP verification"},
            {"method": "POST", "path": "/pan/verify",      "description": "PAN verification"},
            {"method": "POST", "path": "/bank/verify",     "description": "Bank account penny-drop"},
        ],
        "required_fields": ["aadhaar_number", "pan_number", "mobile"],
        "optional_fields": ["consent_text", "ip_address"],
        "auth_type": "API_KEY",
        "sla_ms": 500,
        "icon": "🔐",
    },
    "gst-suvidha-v1": {
        "id": "gst-suvidha-v1",
        "name": "GST Suvidha Provider",
        "category": "GST",
        "version": "v1",
        "versions": ["v1"],
        "status": "active",
        "description": "GST return filing history and turnover extraction",
        "endpoints": [
            {"method": "GET",  "path": "/returns/{gstin}",  "description": "Fetch GST returns"},
            {"method": "POST", "path": "/turnover/compute", "description": "Compute annual turnover"},
        ],
        "required_fields": ["gstin", "financial_year"],
        "optional_fields": ["return_type"],
        "auth_type": "API_KEY",
        "sla_ms": 1500,
        "icon": "🧾",
    },
    "razorpay-pg-v2": {
        "id": "razorpay-pg-v2",
        "name": "Razorpay Payment Gateway",
        "category": "Payment Gateway",
        "version": "v2",
        "versions": ["v1", "v2"],
        "status": "active",
        "description": "EMI disbursement, repayment collection, and refund processing",
        "endpoints": [
            {"method": "POST", "path": "/orders",         "description": "Create payment order"},
            {"method": "POST", "path": "/disbursements",  "description": "Disburse loan amount"},
            {"method": "POST", "path": "/refunds",        "description": "Process refund"},
        ],
        "required_fields": ["amount", "currency", "account_number", "ifsc"],
        "optional_fields": ["description", "notes", "webhook_url"],
        "auth_type": "BASIC_AUTH",
        "sla_ms": 300,
        "icon": "💳",
    },
    "seon-fraud-v3": {
        "id": "seon-fraud-v3",
        "name": "SEON Fraud Engine",
        "category": "Fraud Detection",
        "version": "v3",
        "versions": ["v1", "v2", "v3"],
        "status": "active",
        "description": "Real-time fraud scoring using device fingerprint, email, and phone intelligence",
        "endpoints": [
            {"method": "POST", "path": "/fraud/score",    "description": "Real-time fraud score"},
            {"method": "POST", "path": "/device/check",  "description": "Device fingerprint check"},
        ],
        "required_fields": ["email", "mobile", "ip_address"],
        "optional_fields": ["device_id", "user_agent", "session_id"],
        "auth_type": "API_KEY",
        "sla_ms": 200,
        "icon": "🛡️",
    },
    "finvu-aa-v2": {
        "id": "finvu-aa-v2",
        "name": "Finvu Account Aggregator",
        "category": "Open Banking",
        "version": "v2",
        "versions": ["v1", "v2"],
        "status": "active",
        "description": "RBI Account Aggregator for fetching bank statements and financial data",
        "endpoints": [
            {"method": "POST", "path": "/consent/create", "description": "Create consent request"},
            {"method": "GET",  "path": "/data/fetch",     "description": "Fetch consented financial data"},
        ],
        "required_fields": ["mobile", "fip_id", "date_range"],
        "optional_fields": ["account_type", "consent_purpose"],
        "auth_type": "OAUTH2",
        "sla_ms": 2000,
        "icon": "🏛️",
    },
}

# ── Configurations (populated at runtime) ─────────────────────────────────────
CONFIGURATIONS: Dict[str, dict] = {}

# ── Audit Logs (populated at runtime) ─────────────────────────────────────────
AUDIT_LOGS: List[dict] = []

# ── Tenants ────────────────────────────────────────────────────────────────────
TENANTS = {
    "tenant-001": {"name": "Bajaj Finserv",   "env": "production"},
    "tenant-002": {"name": "HDFC Credila",    "env": "staging"},
    "tenant-003": {"name": "Lendingkart",     "env": "sandbox"},
}

def add_audit_log(action: str, entity: str, entity_id: str, tenant_id: str, details: dict = {}):
    AUDIT_LOGS.append({
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "entity": entity,
        "entity_id": entity_id,
        "tenant_id": tenant_id,
        "details": details,
    })
