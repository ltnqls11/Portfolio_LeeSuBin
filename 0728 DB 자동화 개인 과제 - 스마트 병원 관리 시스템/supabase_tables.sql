-- 병원 관리 시스템 테이블 생성 SQL
-- Supabase SQL Editor에서 실행하세요

-- 1. 환자 테이블
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    birth_date DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT,
    medical_history TEXT,
    emergency_contact VARCHAR(20),
    insurance VARCHAR(50),
    registration_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 의료진 테이블
CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    license_num VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    work_hours VARCHAR(50),
    experience_years INTEGER,
    education TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. 예약 테이블
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    time TIME NOT NULL,
    status VARCHAR(50) DEFAULT '예약완료',
    treatment_type VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. 진료 기록 테이블
CREATE TABLE IF NOT EXISTS medical_records (
    id SERIAL PRIMARY KEY,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    chief_complaint TEXT,
    diagnosis TEXT,
    treatment TEXT,
    prescription TEXT,
    next_visit DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. SMS 로그 테이블
CREATE TABLE IF NOT EXISTS sms_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    recipient VARCHAR(20),
    message TEXT,
    status VARCHAR(20) DEFAULT '발송완료',
    message_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. 대기 시간 테이블
CREATE TABLE IF NOT EXISTS waiting_times (
    id SERIAL PRIMARY KEY,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE CASCADE,
    patient_name VARCHAR(100),
    doctor_name VARCHAR(100),
    scheduled_time TIME,
    estimated_wait_minutes INTEGER,
    current_status VARCHAR(50) DEFAULT '대기중',
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. 의료진 스케줄 테이블
CREATE TABLE IF NOT EXISTS doctor_schedules (
    id SERIAL PRIMARY KEY,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    doctor_name VARCHAR(100),
    date DATE,
    start_time TIME,
    end_time TIME,
    max_patients INTEGER DEFAULT 10,
    current_patients INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT '정상',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성 (성능 향상)
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(date);
CREATE INDEX IF NOT EXISTS idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_patient_id ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_sms_log_timestamp ON sms_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_waiting_times_status ON waiting_times(current_status);

-- Row Level Security (RLS) 활성화 (선택사항)
-- ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE medical_records ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE sms_log ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE waiting_times ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE doctor_schedules ENABLE ROW LEVEL SECURITY;

-- 테이블 생성 완료 확인
SELECT 'Tables created successfully!' as message;