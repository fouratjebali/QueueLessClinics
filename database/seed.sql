-- ============================================
-- QueueLess Clinic - Seed Data
-- Version: 1.0.0
-- Description: Test/demo data for development
-- ============================================

-- ============================================
-- CLINICS
-- ============================================

INSERT INTO clinics (id, name, slug, description, street, city, state, zip_code, country, phone, email, website, is_active)
VALUES
    (
        '550e8400-e29b-41d4-a716-446655440001',
        'Metro Care Clinic',
        'metro-care',
        'Providing quality healthcare services to our community for over 20 years. Specialized in family medicine, pediatrics, and preventive care.',
        '123 Main Street',
        'Tunis',
        'Tunis Governorate',
        '1000',
        'Tunisia',
        '+216 71 123 456',
        'contact@metrocare.tn',
        'https://metrocare.tn',
        TRUE
    ),
    (
        '550e8400-e29b-41d4-a716-446655440002',
        'Sfax Medical Center',
        'sfax-medical',
        'Modern medical facility offering comprehensive healthcare services. Open 24/7 for emergencies.',
        '456 Hospital Road',
        'Sfax',
        'Sfax Governorate',
        '3000',
        'Tunisia',
        '+216 74 987 654',
        'info@sfaxmedical.tn',
        'https://sfaxmedical.tn',
        TRUE
    ),
    (
        '550e8400-e29b-41d4-a716-446655440003',
        'Sousse Family Clinic',
        'sousse-family',
        'Family-oriented healthcare with a personal touch. Serving Sousse community since 2010.',
        '789 Beach Avenue',
        'Sousse',
        'Sousse Governorate',
        '4000',
        'Tunisia',
        '+216 73 456 789',
        'hello@soussefamily.tn',
        NULL,
        TRUE
    );

-- ============================================
-- CLINIC SETTINGS
-- ============================================

INSERT INTO clinic_settings (clinic_id, max_capacity, estimated_service_time, enable_sms, enable_email)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 60, 15, TRUE, TRUE),
    ('550e8400-e29b-41d4-a716-446655440002', 100, 20, TRUE, TRUE),
    ('550e8400-e29b-41d4-a716-446655440003', 40, 12, TRUE, FALSE);

-- ============================================
-- USERS (Password: 'Password123!' for all)
-- Hash generated with bcrypt, 10 rounds
-- ============================================

INSERT INTO users (id, clinic_id, email, password_hash, first_name, last_name, phone_number, role, is_active)
VALUES
    -- Admin
    (
        '650e8400-e29b-41d4-a716-446655440001',
        NULL,
        'admin@queueless.tn',
        '$2b$10$p0dY3m5gmToO9nvq2j7CuuyWqmLFB.PIwKLbwb30M1ZGg/pFYHg6S',
        'Ahmed',
        'Ben Ali',
        '+216 50 123 456',
        'ADMIN',
        TRUE
    ),
    -- Metro Care Staff
    (
        '650e8400-e29b-41d4-a716-446655440002',
        '550e8400-e29b-41d4-a716-446655440001',
        'dr.sarah@metrocare.tn',
        '$2b$10$p0dY3m5gmToO9nvq2j7CuuyWqmLFB.PIwKLbwb30M1ZGg/pFYHg6S',
        'Sarah',
        'Johnson',
        '+216 50 234 567',
        'DOCTOR',
        TRUE
    ),
    (
        '650e8400-e29b-41d4-a716-446655440003',
        '550e8400-e29b-41d4-a716-446655440001',
        'nurse.fatma@metrocare.tn',
        '$2b$10$p0dY3m5gmToO9nvq2j7CuuyWqmLFB.PIwKLbwb30M1ZGg/pFYHg6S',
        'Fatma',
        'Trabelsi',
        '+216 50 345 678',
        'NURSE',
        TRUE
    ),
    (
        '650e8400-e29b-41d4-a716-446655440004',
        '550e8400-e29b-41d4-a716-446655440001',
        'receptionist@metrocare.tn',
        '$2b$10$p0dY3m5gmToO9nvq2j7CuuyWqmLFB.PIwKLbwb30M1ZGg/pFYHg6S',
        'Amira',
        'Mansour',
        '+216 50 456 789',
        'RECEPTIONIST',
        TRUE
    ),
    -- Sfax Medical Staff
    (
        '650e8400-e29b-41d4-a716-446655440005',
        '550e8400-e29b-41d4-a716-446655440002',
        'dr.mohamed@sfaxmedical.tn',
        '$2b$10$p0dY3m5gmToO9nvq2j7CuuyWqmLFB.PIwKLbwb30M1ZGg/pFYHg6S',
        'Mohamed',
        'Bouazizi',
        '+216 51 123 456',
        'DOCTOR',
        TRUE
    ),
    (
        '650e8400-e29b-41d4-a716-446655440006',
        '550e8400-e29b-41d4-a716-446655440002',
        'staff@sfaxmedical.tn',
        '$2b$10$p0dY3m5gmToO9nvq2j7CuuyWqmLFB.PIwKLbwb30M1ZGg/pFYHg6S',
        'Leila',
        'Khelifi',
        '+216 51 234 567',
        'STAFF',
        TRUE
    ),
    -- Sousse Family Staff
    (
        '650e8400-e29b-41d4-a716-446655440007',
        '550e8400-e29b-41d4-a716-446655440003',
        'dr.ines@soussefamily.tn',
        '$2b$10$p0dY3m5gmToO9nvq2j7CuuyWqmLFB.PIwKLbwb30M1ZGg/pFYHg6S',
        'Ines',
        'Hamdi',
        '+216 52 123 456',
        'DOCTOR',
        TRUE
    );

-- ============================================
-- SERVICES
-- ============================================

-- Metro Care Services
INSERT INTO services (id, clinic_id, name, description, estimated_duration, code, display_order, is_active)
VALUES
    (
        '750e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        'General Consultation',
        'Regular check-up and consultation with our doctors',
        15,
        'CONS',
        1,
        TRUE
    ),
    (
        '750e8400-e29b-41d4-a716-446655440002',
        '550e8400-e29b-41d4-a716-446655440001',
        'Vaccination',
        'Immunization and vaccination services',
        10,
        'VACC',
        2,
        TRUE
    ),
    (
        '750e8400-e29b-41d4-a716-446655440003',
        '550e8400-e29b-41d4-a716-446655440001',
        'Lab Work',
        'Blood tests and laboratory services',
        20,
        'LAB',
        3,
        TRUE
    ),
    (
        '750e8400-e29b-41d4-a716-446655440004',
        '550e8400-e29b-41d4-a716-446655440001',
        'Prescription Renewal',
        'Renew existing prescriptions',
        5,
        'PRESC',
        4,
        TRUE
    );

-- Sfax Medical Services
INSERT INTO services (id, clinic_id, name, description, estimated_duration, code, display_order, is_active)
VALUES
    (
        '750e8400-e29b-41d4-a716-446655440005',
        '550e8400-e29b-41d4-a716-446655440002',
        'Emergency Care',
        '24/7 emergency medical services',
        30,
        'EMRG',
        1,
        TRUE
    ),
    (
        '750e8400-e29b-41d4-a716-446655440006',
        '550e8400-e29b-41d4-a716-446655440002',
        'Consultation',
        'Medical consultation with specialists',
        20,
        'CONS',
        2,
        TRUE
    ),
    (
        '750e8400-e29b-41d4-a716-446655440007',
        '550e8400-e29b-41d4-a716-446655440002',
        'X-Ray',
        'Radiology and imaging services',
        15,
        'XRAY',
        3,
        TRUE
    );

-- Sousse Family Services
INSERT INTO services (id, clinic_id, name, description, estimated_duration, code, display_order, is_active)
VALUES
    (
        '750e8400-e29b-41d4-a716-446655440008',
        '550e8400-e29b-41d4-a716-446655440003',
        'Family Medicine',
        'Comprehensive family healthcare',
        15,
        'FAM',
        1,
        TRUE
    ),
    (
        '750e8400-e29b-41d4-a716-446655440009',
        '550e8400-e29b-41d4-a716-446655440003',
        'Pediatrics',
        'Child healthcare and development monitoring',
        12,
        'PED',
        2,
        TRUE
    );

-- ============================================
-- QUEUES (Today's queues)
-- ============================================

INSERT INTO queues (id, clinic_id, date, is_active, opened_at, total_tickets, waiting, called, serving, completed, cancelled, no_show, avg_wait_time, avg_service_time, current_wait_time)
VALUES
    (
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001', -- Metro Care
        CURRENT_DATE,
        TRUE,
        CURRENT_TIMESTAMP - INTERVAL '4 hours',
        15,
        5,
        1,
        1,
        7,
        1,
        0,
        18.5,
        14.2,
        25
    ),
    (
        '850e8400-e29b-41d4-a716-446655440002',
        '550e8400-e29b-41d4-a716-446655440002', -- Sfax Medical
        CURRENT_DATE,
        TRUE,
        CURRENT_TIMESTAMP - INTERVAL '6 hours',
        28,
        8,
        2,
        2,
        15,
        1,
        0,
        22.3,
        18.7,
        30
    ),
    (
        '850e8400-e29b-41d4-a716-446655440003',
        '550e8400-e29b-41d4-a716-446655440003', -- Sousse Family
        CURRENT_DATE,
        TRUE,
        CURRENT_TIMESTAMP - INTERVAL '3 hours',
        10,
        3,
        1,
        1,
        5,
        0,
        0,
        15.0,
        12.5,
        18
    );

-- ============================================
-- TICKETS (Current patients in queue)
-- ============================================

-- Metro Care Tickets
INSERT INTO tickets (id, queue_id, clinic_id, service_id, ticket_number, patient_name, patient_phone, patient_email, status, priority, position, estimated_wait_time, is_walkin, joined_at, called_at, serving_started_at, completed_at, called_by, served_by, notes)
VALUES
    -- Completed tickets
    (
        '950e8400-e29b-41d4-a716-446655440001',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440001',
        'A001',
        'Ali Ben Salah',
        '+216 98 111 222',
        'ali.salah@email.tn',
        'COMPLETED',
        'NORMAL',
        1,
        0,
        FALSE,
        CURRENT_TIMESTAMP - INTERVAL '3 hours 45 minutes',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 30 minutes',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 25 minutes',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 10 minutes',
        '650e8400-e29b-41d4-a716-446655440002',
        '650e8400-e29b-41d4-a716-446655440002',
        'Regular check-up'
    ),
    (
        '950e8400-e29b-41d4-a716-446655440002',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440002',
        'A002',
        'Sarra Mejri',
        '+216 98 222 333',
        NULL,
        'COMPLETED',
        'NORMAL',
        2,
        0,
        FALSE,
        CURRENT_TIMESTAMP - INTERVAL '3 hours 30 minutes',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 15 minutes',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 10 minutes',
        CURRENT_TIMESTAMP - INTERVAL '3 hours',
        '650e8400-e29b-41d4-a716-446655440003',
        '650e8400-e29b-41d4-a716-446655440003',
        'Flu vaccine'
    ),
    -- Currently serving
    (
        '950e8400-e29b-41d4-a716-446655440003',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440001',
        'A003',
        'Karim Toumi',
        '+216 98 333 444',
        'karim.t@email.tn',
        'SERVING',
        'NORMAL',
        3,
        0,
        FALSE,
        CURRENT_TIMESTAMP - INTERVAL '2 hours 45 minutes',
        CURRENT_TIMESTAMP - INTERVAL '15 minutes',
        CURRENT_TIMESTAMP - INTERVAL '10 minutes',
        NULL,
        '650e8400-e29b-41d4-a716-446655440002',
        '650e8400-e29b-41d4-a716-446655440002',
        NULL
    ),
    -- Called (waiting for patient)
    (
        '950e8400-e29b-41d4-a716-446655440004',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440003',
        'A004',
        'Yasmine Gharbi',
        '+216 98 444 555',
        NULL,
        'CALLED',
        'HIGH',
        4,
        5,
        FALSE,
        CURRENT_TIMESTAMP - INTERVAL '2 hours 30 minutes',
        CURRENT_TIMESTAMP - INTERVAL '2 minutes',
        NULL,
        NULL,
        '650e8400-e29b-41d4-a716-446655440004',
        NULL,
        'Lab work - fasting blood test'
    ),
    -- Waiting
    (
        '950e8400-e29b-41d4-a716-446655440005',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440001',
        'A005',
        'Mehdi Bouguerra',
        '+216 98 555 666',
        'mehdi.b@email.tn',
        'WAITING',
        'NORMAL',
        5,
        15,
        TRUE,
        CURRENT_TIMESTAMP - INTERVAL '1 hour 30 minutes',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        'Walk-in patient'
    ),
    (
        '950e8400-e29b-41d4-a716-446655440006',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440004',
        'A006',
        'Nadia Hammouda',
        '+216 98 666 777',
        NULL,
        'WAITING',
        'NORMAL',
        6,
        20,
        FALSE,
        CURRENT_TIMESTAMP - INTERVAL '1 hour 15 minutes',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        '950e8400-e29b-41d4-a716-446655440007',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440001',
        'A007',
        'Omar Dridi',
        '+216 98 777 888',
        'omar.dridi@email.tn',
        'WAITING',
        'URGENT',
        7,
        25,
        FALSE,
        CURRENT_TIMESTAMP - INTERVAL '45 minutes',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        'Urgent - chest pain'
    ),
    (
        '950e8400-e29b-41d4-a716-446655440008',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440002',
        'A008',
        'Rim Belhaj',
        '+216 98 888 999',
        NULL,
        'WAITING',
        'NORMAL',
        8,
        30,
        FALSE,
        CURRENT_TIMESTAMP - INTERVAL '30 minutes',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL
    ),
    -- Cancelled
    (
        '950e8400-e29b-41d4-a716-446655440009',
        '850e8400-e29b-41d4-a716-446655440001',
        '550e8400-e29b-41d4-a716-446655440001',
        '750e8400-e29b-41d4-a716-446655440001',
        'A009',
        'Hichem Jebali',
        '+216 98 999 000',
        'hichem.j@email.tn',
        'CANCELLED',
        'NORMAL',
        9,
        0,
        FALSE,
        CURRENT_TIMESTAMP - INTERVAL '2 hours',
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        'Patient cancelled - emergency'
    );

-- Sfax Medical Tickets (fewer details for brevity)
INSERT INTO tickets (queue_id, clinic_id, service_id, ticket_number, patient_name, patient_phone, status, priority, position, estimated_wait_time, is_walkin, joined_at)
VALUES
    ('850e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', '750e8400-e29b-41d4-a716-446655440006', 'B001', 'Ahmed Mansouri', '+216 97 111 222', 'WAITING', 'NORMAL', 1, 30, FALSE, CURRENT_TIMESTAMP - INTERVAL '2 hours'),
    ('850e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', '750e8400-e29b-41d4-a716-446655440007', 'B002', 'Samia Zouari', '+216 97 222 333', 'WAITING', 'NORMAL', 2, 35, FALSE, CURRENT_TIMESTAMP - INTERVAL '1 hour 45 minutes'),
    ('850e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', '750e8400-e29b-41d4-a716-446655440005', 'B003', 'Rami Belkacem', '+216 97 333 444', 'SERVING', 'URGENT', 3, 0, TRUE, CURRENT_TIMESTAMP - INTERVAL '1 hour 30 minutes');

-- Sousse Family Tickets
INSERT INTO tickets (queue_id, clinic_id, service_id, ticket_number, patient_name, patient_phone, status, priority, position, estimated_wait_time, is_walkin, joined_at)
VALUES
    ('850e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', '750e8400-e29b-41d4-a716-446655440008', 'C001', 'Leila Khiari', '+216 96 111 222', 'WAITING', 'NORMAL', 1, 18, FALSE, CURRENT_TIMESTAMP - INTERVAL '1 hour'),
    ('850e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', '750e8400-e29b-41d4-a716-446655440009', 'C002', 'Youssef Maaloul', '+216 96 222 333', 'CALLED', 'NORMAL', 2, 5, FALSE, CURRENT_TIMESTAMP - INTERVAL '45 minutes');

-- ============================================
-- QUEUE EVENTS (Recent activity log)
-- ============================================

INSERT INTO queue_events (queue_id, ticket_id, event_type, user_id, user_name, metadata, timestamp)
VALUES
    (
        '850e8400-e29b-41d4-a716-446655440001',
        NULL,
        'QUEUE_OPENED',
        '650e8400-e29b-41d4-a716-446655440002',
        'Sarah Johnson',
        '{"message": "Queue opened for the day"}'::jsonb,
        CURRENT_TIMESTAMP - INTERVAL '4 hours'
    ),
    (
        '850e8400-e29b-41d4-a716-446655440001',
        '950e8400-e29b-41d4-a716-446655440001',
        'TICKET_CREATED',
        NULL,
        'System',
        '{"ticket_number": "A001", "patient_name": "Ali Ben Salah"}'::jsonb,
        CURRENT_TIMESTAMP - INTERVAL '3 hours 45 minutes'
    ),
    (
        '850e8400-e29b-41d4-a716-446655440001',
        '950e8400-e29b-41d4-a716-446655440001',
        'TICKET_CALLED',
        '650e8400-e29b-41d4-a716-446655440002',
        'Sarah Johnson',
        '{"ticket_number": "A001"}'::jsonb,
        CURRENT_TIMESTAMP - INTERVAL '3 hours 30 minutes'
    ),
    (
        '850e8400-e29b-41d4-a716-446655440001',
        '950e8400-e29b-41d4-a716-446655440001',
        'TICKET_SERVING',
        '650e8400-e29b-41d4-a716-446655440002',
        'Sarah Johnson',
        '{"ticket_number": "A001"}'::jsonb,
        CURRENT_TIMESTAMP - INTERVAL '3 hours 25 minutes'
    ),
    (
        '850e8400-e29b-41d4-a716-446655440001',
        '950e8400-e29b-41d4-a716-446655440001',
        'TICKET_COMPLETED',
        '650e8400-e29b-41d4-a716-446655440002',
        'Sarah Johnson',
        '{"ticket_number": "A001", "service_time": 15}'::jsonb,
        CURRENT_TIMESTAMP - INTERVAL '3 hours 10 minutes'
    ),
    (
        '850e8400-e29b-41d4-a716-446655440001',
        '950e8400-e29b-41d4-a716-446655440003',
        'TICKET_CALLED',
        '650e8400-e29b-41d4-a716-446655440002',
        'Sarah Johnson',
        '{"ticket_number": "A003"}'::jsonb,
        CURRENT_TIMESTAMP - INTERVAL '15 minutes'
    ),
    (
        '850e8400-e29b-41d4-a716-446655440001',
        '950e8400-e29b-41d4-a716-446655440004',
        'TICKET_CALLED',
        '650e8400-e29b-41d4-a716-446655440004',
        'Amira Mansour',
        '{"ticket_number": "A004"}'::jsonb,
        CURRENT_TIMESTAMP - INTERVAL '2 minutes'
    );

-- ============================================
-- NOTIFICATIONS (Sent notifications)
-- ============================================

INSERT INTO notifications (ticket_id, type, recipient, subject, message, status, sent_at, delivered_at)
VALUES
    (
        '950e8400-e29b-41d4-a716-446655440001',
        'SMS',
        '+216 98 111 222',
        NULL,
        'Your ticket A001 has been created. Your position: 1. Estimated wait: 15 minutes.',
        'DELIVERED',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 45 minutes',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 44 minutes'
    ),
    (
        '950e8400-e29b-41d4-a716-446655440001',
        'SMS',
        '+216 98 111 222',
        NULL,
        'Your turn! Please proceed to the counter. Ticket: A001',
        'DELIVERED',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 30 minutes',
        CURRENT_TIMESTAMP - INTERVAL '3 hours 29 minutes'
    ),
    (
        '950e8400-e29b-41d4-a716-446655440005',
        'SMS',
        '+216 98 555 666',
        NULL,
        'Your ticket A005 has been created. Your position: 5. Estimated wait: 45 minutes.',
        'DELIVERED',
        CURRENT_TIMESTAMP - INTERVAL '1 hour 30 minutes',
        CURRENT_TIMESTAMP - INTERVAL '1 hour 29 minutes'
    ),
    (
        '950e8400-e29b-41d4-a716-446655440007',
        'EMAIL',
        'omar.dridi@email.tn',
        'Your QueueLess Ticket - A007',
        'Dear Omar Dridi, your ticket A007 has been created. You are currently position 7 in the queue. Estimated wait time: 45 minutes. We will notify you when it''s your turn.',
        'SENT',
        CURRENT_TIMESTAMP - INTERVAL '45 minutes',
        NULL
    );

-- ============================================
-- SUCCESS MESSAGE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Seed Data Inserted Successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Clinics: 3';
    RAISE NOTICE 'Users: 7 (Password: Password123!)';
    RAISE NOTICE 'Services: 9';
    RAISE NOTICE 'Active Queues: 3';
    RAISE NOTICE 'Tickets: ~25';
    RAISE NOTICE 'Events: 7';
    RAISE NOTICE 'Notifications: 4';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Login Credentials:';
    RAISE NOTICE 'Admin: admin@queueless.tn / Password123!';
    RAISE NOTICE 'Doctor: dr.sarah@metrocare.tn / Password123!';
    RAISE NOTICE 'Nurse: nurse.fatma@metrocare.tn / Password123!';
    RAISE NOTICE '========================================';
END $$;
