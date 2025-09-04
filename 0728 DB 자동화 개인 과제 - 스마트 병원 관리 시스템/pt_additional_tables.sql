-- 물리치료 특화 추가 테이블들
-- Supabase SQL Editor에서 실행하세요

-- 1. 물리치료 평가 테이블
CREATE TABLE IF NOT EXISTS pt_assessments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE CASCADE,
    
    -- ROM 데이터 (JSON 형태로 저장)
    rom_data JSONB,
    
    -- MMT 데이터 (JSON 형태로 저장)
    mmt_data JSONB,
    
    -- 통증 및 기능 점수
    pain_score INTEGER CHECK (pain_score >= 0 AND pain_score <= 10),
    functional_score INTEGER CHECK (functional_score >= 0 AND functional_score <= 100),
    
    -- 평가 소견
    assessment_notes TEXT,
    
    -- 평가 날짜
    assessment_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 운동처방 테이블
CREATE TABLE IF NOT EXISTS exercise_prescriptions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    
    -- 진단 및 치료 단계
    diagnosis VARCHAR(100),
    treatment_phase VARCHAR(50),
    
    -- 처방된 운동들 (JSON 배열)
    prescribed_exercises JSONB,
    
    -- 운동 강도
    sets INTEGER,
    reps INTEGER,
    frequency VARCHAR(50),
    
    -- 처방 기간
    duration_weeks INTEGER,
    
    -- 특별 지시사항
    special_instructions TEXT,
    
    -- 처방 날짜
    prescription_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. 물리적 인자 치료 기록 테이블
CREATE TABLE IF NOT EXISTS physical_agent_treatments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE CASCADE,
    
    -- 치료 정보
    agent_type VARCHAR(50),
    agent_method VARCHAR(100),
    intensity VARCHAR(50),
    duration_minutes INTEGER,
    body_part VARCHAR(100),
    
    -- 환자 반응
    patient_response TEXT,
    
    -- 치료 날짜
    treatment_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. 홈 프로그램 테이블
CREATE TABLE IF NOT EXISTS home_programs (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
    
    -- 프로그램 정보
    program_type VARCHAR(50),
    program_content JSONB,
    frequency VARCHAR(50),
    duration_weeks INTEGER,
    
    -- 특별 지시사항
    special_notes TEXT,
    
    -- 프로그램 시작일
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    
    -- 상태 (진행중, 완료, 중단)
    status VARCHAR(20) DEFAULT '진행중',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. 치료 진행도 추적 테이블
CREATE TABLE IF NOT EXISTS treatment_progress (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    
    -- 측정 날짜
    measurement_date DATE DEFAULT CURRENT_DATE,
    
    -- 진행도 데이터
    pain_score INTEGER CHECK (pain_score >= 0 AND pain_score <= 10),
    rom_data JSONB,
    functional_score INTEGER CHECK (functional_score >= 0 AND functional_score <= 100),
    
    -- 기타 측정값
    additional_measurements JSONB,
    
    -- 메모
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_pt_assessments_patient_id ON pt_assessments(patient_id);
CREATE INDEX IF NOT EXISTS idx_pt_assessments_date ON pt_assessments(assessment_date);
CREATE INDEX IF NOT EXISTS idx_exercise_prescriptions_patient_id ON exercise_prescriptions(patient_id);
CREATE INDEX IF NOT EXISTS idx_physical_agent_treatments_patient_id ON physical_agent_treatments(patient_id);
CREATE INDEX IF NOT EXISTS idx_home_programs_patient_id ON home_programs(patient_id);
CREATE INDEX IF NOT EXISTS idx_treatment_progress_patient_id ON treatment_progress(patient_id);
CREATE INDEX IF NOT EXISTS idx_treatment_progress_date ON treatment_progress(measurement_date);

-- 완료 메시지
SELECT 'Physical Therapy specialized tables created successfully!' as message;