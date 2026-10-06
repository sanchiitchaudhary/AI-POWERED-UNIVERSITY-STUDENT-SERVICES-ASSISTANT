"""Database session and engine setup."""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

DEFAULT_DB_PATH = Path("data/student_services.db")


def get_engine(db_path: Path | str | None = None):
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    
    if isinstance(db_path, str) and not db_path.startswith("sqlite"):
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{path.resolve()}"
    elif isinstance(db_path, Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{db_path.resolve()}"
    else:
        url = str(db_path)

    return create_engine(url, echo=False)


def get_session_factory(db_path: Path | str | None = None):
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
