CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- DROP TABLES (in correct order due to foreign keys)
-- ============================================

DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS queue_events CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS queues CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS clinic_settings CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS clinics CASCADE;

-- ============================================
-- ENUMS
-- ============================================

-- User Roles
CREATE TYPE user_role AS ENUM (
    'ADMIN',
    'STAFF',
    'DOCTOR',
    'NURSE',
    'RECEPTIONIST'
);

-- Ticket Status
CREATE TYPE ticket_status AS ENUM (
    'WAITING',
    'CALLED',
    'SERVING',
    'COMPLETED',
    'CANCELLED',
    'NO_SHOW'
);

-- Ticket Priority
CREATE TYPE ticket_priority AS ENUM (
    'NORMAL',
    'HIGH',
    'URGENT'
);

-- Queue Event Type
CREATE TYPE queue_event_type AS ENUM (
    'QUEUE_OPENED',
    'QUEUE_CLOSED',
    'TICKET_CREATED',
    'TICKET_CALLED',
    'TICKET_SERVING',
    'TICKET_COMPLETED',
    'TICKET_CANCELLED',
    'TICKET_NO_SHOW',
    'TICKET_UPDATED'
);

-- Notification Type
CREATE TYPE notification_type AS ENUM (
    'SMS',
    'EMAIL',
    'PUSH'
);

-- Notification Status
CREATE TYPE notification_status AS ENUM (
    'PENDING',
    'SENT',
    'DELIVERED',
    'FAILED'
);

-- ============================================
-- TABLE: clinics
-- ============================================

CREATE TABLE clinics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    
    -- Address
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'Tunisia',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Contact
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    fax VARCHAR(20),
    
    -- Branding
    logo TEXT,
    primary_color VARCHAR(7) DEFAULT '#1e88e5',
    secondary_color VARCHAR(7) DEFAULT '#4caf50',
    cover_image TEXT,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_clinics_slug ON clinics(slug);
CREATE INDEX idx_clinics_is_active ON clinics(is_active);

-- ============================================
-- TABLE: clinic_settings
-- ============================================

CREATE TABLE clinic_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL UNIQUE REFERENCES clinics(id) ON DELETE CASCADE,
    
    -- Operating Hours (stored as JSON)
    operating_hours JSONB NOT NULL DEFAULT '{
        "monday": {"isOpen": true, "openTime": "08:00", "closeTime": "17:00"},
        "tuesday": {"isOpen": true, "openTime": "08:00", "closeTime": "17:00"},
        "wednesday": {"isOpen": true, "openTime": "08:00", "closeTime": "17:00"},
        "thursday": {"isOpen": true, "openTime": "08:00", "closeTime": "17:00"},
        "friday": {"isOpen": true, "openTime": "08:00", "closeTime": "17:00"},
        "saturday": {"isOpen": false, "openTime": "09:00", "closeTime": "13:00"},
        "sunday": {"isOpen": false, "openTime": "09:00", "closeTime": "13:00"}
    }'::jsonb,
    
    -- Queue Settings
    max_capacity INTEGER DEFAULT 50,
    allow_walkins BOOLEAN DEFAULT TRUE,
    allow_online_joining BOOLEAN DEFAULT TRUE,
    auto_call_next BOOLEAN DEFAULT FALSE,
    estimated_service_time INTEGER DEFAULT 15, -- minutes
    warning_threshold INTEGER DEFAULT 80, -- percentage
    closed_message TEXT,
    
    -- Notification Settings
    enable_sms BOOLEAN DEFAULT TRUE,
    enable_email BOOLEAN DEFAULT TRUE,
    reminder_before_minutes INTEGER DEFAULT 10,
    ready_notification BOOLEAN DEFAULT TRUE,
    missed_turn_notification BOOLEAN DEFAULT TRUE,
    
    -- Display Settings
    show_estimated_wait_time BOOLEAN DEFAULT TRUE,
    show_queue_position BOOLEAN DEFAULT TRUE,
    show_people_ahead BOOLEAN DEFAULT TRUE,
    display_languages TEXT[] DEFAULT ARRAY['en', 'fr'],
    custom_welcome_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index
CREATE INDEX idx_clinic_settings_clinic_id ON clinic_settings(clinic_id);

-- ============================================
-- TABLE: users
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID REFERENCES clinics(id) ON DELETE SET NULL,
    
    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Personal Info
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    avatar TEXT,
    
    -- Role & Permissions
    role user_role NOT NULL DEFAULT 'STAFF',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_clinic_id ON users(clinic_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================
-- TABLE: services
-- ============================================

CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    
    -- Service Info
    name VARCHAR(255) NOT NULL,
    description TEXT,
    estimated_duration INTEGER NOT NULL DEFAULT 15, -- minutes
    code VARCHAR(50), -- e.g., "CONS", "VACC", "LAB"
    
    -- Display
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_services_clinic_id ON services(clinic_id);
CREATE INDEX idx_services_is_active ON services(is_active);
CREATE INDEX idx_services_display_order ON services(clinic_id, display_order);

-- ============================================
-- TABLE: queues
-- ============================================

CREATE TABLE queues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    
    -- Queue Info
    date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    opened_at TIMESTAMP,
    closed_at TIMESTAMP,
    
    -- Statistics (updated in real-time)
    total_tickets INTEGER DEFAULT 0,
    waiting INTEGER DEFAULT 0,
    called INTEGER DEFAULT 0,
    serving INTEGER DEFAULT 0,
    completed INTEGER DEFAULT 0,
    cancelled INTEGER DEFAULT 0,
    no_show INTEGER DEFAULT 0,
    
    -- Average Times (in minutes)
    avg_wait_time DECIMAL(10, 2) DEFAULT 0,
    avg_service_time DECIMAL(10, 2) DEFAULT 0,
    current_wait_time INTEGER DEFAULT 0, -- estimated
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint: one queue per clinic per day
    CONSTRAINT unique_clinic_date UNIQUE (clinic_id, date)
);

-- Indexes
CREATE INDEX idx_queues_clinic_id ON queues(clinic_id);
CREATE INDEX idx_queues_date ON queues(date);
CREATE INDEX idx_queues_is_active ON queues(is_active);
CREATE INDEX idx_queues_clinic_date ON queues(clinic_id, date);

-- ============================================
-- TABLE: tickets
-- ============================================

CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    queue_id UUID NOT NULL REFERENCES queues(id) ON DELETE CASCADE,
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(id) ON DELETE SET NULL,
    
    -- Ticket Info
    ticket_number VARCHAR(10) NOT NULL, -- e.g., "A001", "B042"
    
    -- Patient Info
    patient_name VARCHAR(255) NOT NULL,
    patient_phone VARCHAR(20) NOT NULL,
    patient_email VARCHAR(255),
    
    -- Status & Priority
    status ticket_status DEFAULT 'WAITING',
    priority ticket_priority DEFAULT 'NORMAL',
    position INTEGER NOT NULL,
    estimated_wait_time INTEGER DEFAULT 0, -- minutes
    
    -- Type
    is_walkin BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    called_at TIMESTAMP,
    serving_started_at TIMESTAMP,
    completed_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Staff Info
    called_by UUID REFERENCES users(id) ON DELETE SET NULL,
    served_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Additional Info
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tickets_queue_id ON tickets(queue_id);
CREATE INDEX idx_tickets_clinic_id ON tickets(clinic_id);
CREATE INDEX idx_tickets_ticket_number ON tickets(ticket_number);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_patient_phone ON tickets(patient_phone);
CREATE INDEX idx_tickets_position ON tickets(queue_id, position);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);

-- ============================================
-- TABLE: queue_events
-- ============================================

CREATE TABLE queue_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    queue_id UUID NOT NULL REFERENCES queues(id) ON DELETE CASCADE,
    ticket_id UUID REFERENCES tickets(id) ON DELETE SET NULL,
    
    -- Event Info
    event_type queue_event_type NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    user_name VARCHAR(255), -- Denormalized for history
    
    -- Metadata (stored as JSON for flexibility)
    metadata JSONB,
    
    -- Timestamp
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_queue_events_queue_id ON queue_events(queue_id);
CREATE INDEX idx_queue_events_ticket_id ON queue_events(ticket_id);
CREATE INDEX idx_queue_events_timestamp ON queue_events(timestamp);
CREATE INDEX idx_queue_events_event_type ON queue_events(event_type);

-- ============================================
-- TABLE: notifications
-- ============================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
    
    -- Notification Info
    type notification_type NOT NULL,
    recipient VARCHAR(255) NOT NULL, -- phone or email
    subject VARCHAR(255),
    message TEXT NOT NULL,
    
    -- Status
    status notification_status DEFAULT 'PENDING',
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notifications_ticket_id ON notifications(ticket_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_sent_at ON notifications(sent_at);

-- ============================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_clinics_updated_at BEFORE UPDATE ON clinics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clinic_settings_updated_at BEFORE UPDATE ON clinic_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON services
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_queues_updated_at BEFORE UPDATE ON queues
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS (Optional but useful)
-- ============================================

-- View: Active queues with statistics
CREATE OR REPLACE VIEW v_active_queues AS
SELECT 
    q.*,
    c.name as clinic_name,
    c.slug as clinic_slug
FROM queues q
JOIN clinics c ON q.clinic_id = c.id
WHERE q.is_active = TRUE;

-- View: Current tickets summary
CREATE OR REPLACE VIEW v_tickets_summary AS
SELECT 
    t.id,
    t.ticket_number,
    t.patient_name,
    t.patient_phone,
    t.status,
    t.priority,
    t.position,
    t.estimated_wait_time,
    t.is_walkin,
    t.joined_at,
    c.name as clinic_name,
    s.name as service_name,
    s.estimated_duration as service_duration,
    q.date as queue_date,
    u1.first_name || ' ' || u1.last_name as called_by_name,
    u2.first_name || ' ' || u2.last_name as served_by_name
FROM tickets t
JOIN queues q ON t.queue_id = q.id
JOIN clinics c ON t.clinic_id = c.id
LEFT JOIN services s ON t.service_id = s.id
LEFT JOIN users u1 ON t.called_by = u1.id
LEFT JOIN users u2 ON t.served_by = u2.id;

-- ============================================
-- COMMENTS (Documentation)
-- ============================================

COMMENT ON TABLE clinics IS 'Healthcare clinics/facilities information';
COMMENT ON TABLE clinic_settings IS 'Configuration and preferences for each clinic';
COMMENT ON TABLE users IS 'Staff and administrative users';
COMMENT ON TABLE services IS 'Medical services offered by clinics';
COMMENT ON TABLE queues IS 'Daily queues for each clinic';
COMMENT ON TABLE tickets IS 'Individual patient tickets in queues';
COMMENT ON TABLE queue_events IS 'Audit log of all queue and ticket events';
COMMENT ON TABLE notifications IS 'SMS, Email, and Push notifications sent to patients';

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'QueueLess Clinic Schema Created Successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables created: 8';
    RAISE NOTICE 'Enums created: 5';
    RAISE NOTICE 'Views created: 2';
    RAISE NOTICE 'Ready for seed data!';
    RAISE NOTICE '========================================';
END $$;