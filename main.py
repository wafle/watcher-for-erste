import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import erste_adapter
import transaction
import gmail
import os


def create_mail_title(t: transaction.Transaction):
    return "Erste: {amount} {currency} - {cardAcceptance} {description}".format(
        amount=t.localAmount,
        currency=t.localCurrency,
        cardAcceptance=t.cardAcceptance,
        description=t.description)


def create_mail_body(t: transaction.Transaction):
    return "New balance: {balance} {currency}.".format(
        balance=t.new_balance, currency=t.localCurrency)


def get_script_dir():
    import os, sys
    return os.path.dirname(os.path.realpath(sys.argv[0]))


engine = create_engine('sqlite:///{script_dir}/erste.db'.format(script_dir=get_script_dir()))
transaction.Base.metadata.create_all(engine)
SQLSession = sessionmaker(bind=engine)

erste = erste_adapter.ErsteAdapter()


def loop():
    transactions = erste.get_latest_transactions()
    s = SQLSession()
    for t in transactions:
        if not t.exists(s):
            s.add(t)
            s.commit()
            title = create_mail_title(t)
            body = create_mail_body(t)
            gmail.send_mail(os.environ["GMAIL_ADDRESS"], title, body)
    s.close()


while True:
    loop()
    time.sleep(60)
