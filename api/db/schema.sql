-- BBB Medical Report Database Schema
-- Medical report generation and analysis database schema

-- Patient information table
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Provider information table
CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    license_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Report table
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id VARCHAR(50) UNIQUE NOT NULL,
    patient_id INTEGER NOT NULL,
    provider_id INTEGER NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    title VARCHAR(200),
    content TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (provider_id) REFERENCES providers(id)
);

-- Symptom-ICD mapping table
CREATE TABLE IF NOT EXISTS symptom_icd (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom VARCHAR(200) NOT NULL,
    icd_code VARCHAR(20) NOT NULL,
    icd_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CPT code table
CREATE TABLE IF NOT EXISTS trigger_cpt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_condition VARCHAR(200) NOT NULL,
    cpt_code VARCHAR(20) NOT NULL,
    cpt_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fee information table
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cpt_code VARCHAR(20) NOT NULL,
    fee_amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    effective_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- EM rule table
CREATE TABLE IF NOT EXISTS em_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name VARCHAR(100) NOT NULL,
    rule_description TEXT,
    rule_condition TEXT,
    rule_action TEXT,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Report creation log table
CREATE TABLE IF NOT EXISTS report_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    user_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id)
);

-- Index creation
CREATE INDEX IF NOT EXISTS idx_patients_patient_id ON patients(patient_id);
CREATE INDEX IF NOT EXISTS idx_providers_provider_id ON providers(provider_id);
CREATE INDEX IF NOT EXISTS idx_reports_report_id ON reports(report_id);
CREATE INDEX IF NOT EXISTS idx_reports_patient_id ON reports(patient_id);
CREATE INDEX IF NOT EXISTS idx_reports_provider_id ON reports(provider_id);
CREATE INDEX IF NOT EXISTS idx_symptom_icd_symptom ON symptom_icd(symptom);
CREATE INDEX IF NOT EXISTS idx_symptom_icd_icd_code ON symptom_icd(icd_code);
CREATE INDEX IF NOT EXISTS idx_trigger_cpt_trigger ON trigger_cpt(trigger_condition);
CREATE INDEX IF NOT EXISTS idx_trigger_cpt_cpt_code ON trigger_cpt(cpt_code);
CREATE INDEX IF NOT EXISTS idx_fees_cpt_code ON fees(cpt_code);
CREATE INDEX IF NOT EXISTS idx_em_rules_active ON em_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_report_logs_report_id ON report_logs(report_id);
