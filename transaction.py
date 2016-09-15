from sqlalchemy import Column, BigInteger, Integer, String, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    name = Column(String)
    new_balance = Column(Integer)
    accountCurrency = Column(String)
    accountAmount = Column(Integer)
    localCurrency = Column(String)
    localAmount = Column(Integer)
    partnerName = Column(String)
    method = Column(String)
    description = Column(String)

    cardAcceptance = Column(String)

    date = Column(DateTime)

    transactionType = Column(Enum("EXPENSE", "INCOME"))

    def __repr__(self):
        return "<Transaction(%s),%d>" % (self.id, self.new_balance)

    def exists(self, session):
        from sqlalchemy import exists
        (exist,) = session.query(
            exists().where(Transaction.id == self.id))
        return exist[0]
