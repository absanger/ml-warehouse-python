from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

Base = declarative_base()


class Test(Base):

    __tablename__ = "test"

    id = Column(Integer, primary_key=True)
    age = Column(Integer)


engine = create_engine("sqlite:///test_db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

# new_test = Test(name="Bob")
# session.add(new_test)
# session.commit()

print(type(session.query(Test).all()[0].age))
