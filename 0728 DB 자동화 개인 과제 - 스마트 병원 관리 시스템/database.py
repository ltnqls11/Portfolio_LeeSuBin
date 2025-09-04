from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

# 환자 테이블
class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    birth_date = Column(Date)
    gender = Column(String)

# 의사 테이블
class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    specialty = Column(String)

# 예약 테이블
class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    date = Column(Date)
    time = Column(Time)
    status = Column(String)

    patient = relationship("Patient")
    doctor = relationship("Doctor")

# DB 연결
engine = create_engine('sqlite:///hospital.db')
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
