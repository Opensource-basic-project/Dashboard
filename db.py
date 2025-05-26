from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///legislation.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# DB 테이블 구조 정의 
class LegislationNotice(Base):  #진행중 입법예고 
    __tablename__ = "legislation_notices"

    id = Column(Integer, primary_key=True, index=True)
    bill_name = Column(String)
    proposer = Column(String)
    bill_id = Column(String)
    noti_ed_dt = Column(String)
    link_url = Column(String)
    curr_committee = Column(String)
    announce_dt = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)
