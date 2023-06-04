from sqlalchemy import create_engine, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, sessionmaker


# DB_URL = 'sqlite:///todo.sqlite3'
DB_URL = 'postgresql+psycopg2://postgres:test1234!@localhost:5432/TodoApplicationDatabase'

engine = create_engine(DB_URL)


class Base(DeclarativeBase):
    pass


class Todo(Base):
    __tablename__ = 'todos'
    id = mapped_column(Integer, primary_key=True, index=True)
    title = mapped_column(String)
    description = mapped_column(String)
    priority = mapped_column(Integer)
    complete = mapped_column(Boolean, default=False)
    owner_id = mapped_column(Integer, ForeignKey('users.id'))


class User(Base):
    __tablename__ = 'users'
    id = mapped_column(Integer, primary_key=True, index=True)
    email = mapped_column(String, unique=True)
    username = mapped_column(String, unique=True)
    firstname = mapped_column(String)
    lastname = mapped_column(String)
    hashed_password = mapped_column(String)
    is_active = mapped_column(Boolean, default=True)
    role = mapped_column(String)


Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)
