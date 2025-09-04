-- 샘플 데이터 삽입 SQL
-- 테이블 생성 후 실행하세요

-- 1. 샘플 환자 데이터
INSERT INTO patients (name, birth_date, gender, phone, address, medical_history, emergency_contact, insurance) VALUES
('김민수', '1985-03-15', '남', '010-1234-5678', '서울시 강남구 역삼동 123-45', '어깨 탈구 병력', '010-1234-5679', '건강보험'),
('이영희', '1990-07-22', '여', '010-2345-6789', '서울시 서초구 서초동 234-56', '무릎 인대 손상', '010-2345-6790', '건강보험'),
('박철수', '1978-11-08', '남', '010-3456-7890', '경기도 성남시 분당구 정자동 345-67', '허리디스크 수술 이력', '010-3456-7891', '의료급여'),
('최수진', '1995-05-30', '여', '010-4567-8901', '서울시 송파구 잠실동 456-78', '목 디스크', '010-4567-8902', '건강보험'),
('정대호', '1982-12-03', '남', '010-5678-9012', '인천시 남동구 구월동 567-89', '발목 골절 병력', '010-5678-9013', '산재보험');

-- 2. 샘플 의료진 데이터
INSERT INTO doctors (name, specialty, license_num, phone, email, work_hours, experience_years, education) VALUES
('김재현', '물리치료', 'PT-2018-001', '010-1111-2222', 'kim.jaehyun@hospital.com', '09:00-18:00', 6, '연세대학교 물리치료학과'),
('박소영', '정형외과', 'MD-2015-045', '010-2222-3333', 'park.soyoung@hospital.com', '08:00-17:00', 9, '서울대학교 의과대학'),
('이동훈', '재활의학과', 'MD-2017-023', '010-3333-4444', 'lee.donghoon@hospital.com', '10:00-19:00', 7, '고려대학교 의과대학'),
('최민정', '도수치료', 'PT-2019-012', '010-4444-5555', 'choi.minjeong@hospital.com', '09:00-18:00', 5, '경희대학교 물리치료학과'),
('정우성', '스포츠의학', 'MD-2016-078', '010-5555-6666', 'jung.woosung@hospital.com', '14:00-22:00', 8, '성균관대학교 의과대학');

-- 3. 샘플 예약 데이터
INSERT INTO appointments (patient_id, doctor_id, date, time, status, treatment_type, notes) VALUES
(1, 1, '2024-07-28', '09:00', '예약완료', '물리치료', '어깨 재활 치료'),
(2, 2, '2024-07-28', '10:30', '진료완료', '초진', '무릎 통증 검사'),
(3, 3, '2024-07-28', '14:00', '예약완료', '재진', '허리 재활 상담'),
(4, 1, '2024-07-29', '09:30', '예약완료', '물리치료', '목 디스크 치료'),
(5, 4, '2024-07-29', '11:00', '예약완료', '도수치료', '발목 관절 가동술');

-- 4. 샘플 진료 기록 데이터
INSERT INTO medical_records (appointment_id, patient_id, doctor_id, chief_complaint, diagnosis, treatment, prescription, next_visit) VALUES
(2, 2, 2, '무릎 부종 및 보행 시 통증', '무릎 관절염 초기', '관절 내 히알루론산 주사', '연골 보호제 30일분', '2024-07-31'),
(1, 1, 1, '어깨 통증 및 운동 제한', '어깨 충돌증후군', '초음파 치료 및 운동 요법', '소염진통제 7일분', '2024-08-01');

-- 5. 샘플 SMS 로그 데이터
INSERT INTO sms_log (recipient, message, status, message_type) VALUES
('010-1234-5678', '[병원] 김민수님 오늘 09:00 물리치료 예약을 확인해주세요.', '발송완료', '예약확인'),
('010-2345-6789', '[병원] 이영희님 진료가 완료되었습니다.', '발송완료', '치료완료'),
('010-3456-7890', '[병원] 박철수님 오늘 14:00 재활의학과 예약을 확인해주세요.', '발송완료', '예약확인');

-- 6. 샘플 대기 시간 데이터
INSERT INTO waiting_times (appointment_id, patient_name, doctor_name, scheduled_time, estimated_wait_minutes, current_status) VALUES
(1, '김민수', '김재현', '09:00', 15, '대기중'),
(3, '박철수', '이동훈', '14:00', 8, '대기중'),
(4, '최수진', '김재현', '09:30', 25, '대기중');

-- 7. 샘플 의료진 스케줄 데이터
INSERT INTO doctor_schedules (doctor_id, doctor_name, date, start_time, end_time, max_patients, current_patients, status, notes) VALUES
(1, '김재현', '2024-07-28', '09:00', '18:00', 12, 3, '정상', '물리치료실 A'),
(2, '박소영', '2024-07-28', '08:00', '17:00', 10, 2, '정상', '진료실 1'),
(3, '이동훈', '2024-07-28', '10:00', '19:00', 8, 1, '정상', '재활의학과');

-- 데이터 삽입 완료 확인
SELECT 'Sample data inserted successfully!' as message;