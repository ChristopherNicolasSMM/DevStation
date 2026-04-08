"""
Base database models and session management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional

from core.config import Config

# Create metadata with naming convention for constraints
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

Base = declarative_base(metadata=metadata)


class DatabaseManager:
    """Manages database connections and sessions"""
    
    _instance: Optional['DatabaseManager'] = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database connection"""
        config = Config()
        database_url = config.database_url
        
        from sqlalchemy import create_engine
        self._engine = create_engine(
            database_url,
            echo=config.get("database.echo", False),
            pool_size=config.get("database.pool_size", 5),
            max_overflow=config.get("database.max_overflow", 10)
        )
        
        self._session_factory = sessionmaker(bind=self._engine)
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self._engine)
    
    def drop_all_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(self._engine)
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self._session_factory()
    
    @property
    def engine(self):
        return self._engine


# Global database manager instance
db_manager = DatabaseManager()