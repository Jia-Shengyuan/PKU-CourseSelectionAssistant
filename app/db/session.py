from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from scripts.load_config import load_semester

semester = load_semester()

SQLALCHEMY_DATABASE_URL = "sqlite:///./" + semester + ".db"  # 可换成 MySQL

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)