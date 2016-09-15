import time
import typing
from transaction import Transaction
import requests
from bs4 import BeautifulSoup
import json
import os
import datetime


class ErsteAdapter():
    def __init__(self):
        self.login()

    def login(self):
        session = requests.session()
        login = session.get(
            "https://netbank.erstebank.hu/daui/UI/Login?realm=/netbank&service=NetbankService").text
        souped = BeautifulSoup(login, "html.parser")

        sun_query_param = souped.find("input", {"name": "SunQueryParamsString"})["value"]
        payload = {
            "IDToken1": os.environ["ERSTE_USERNAME"],
            "IDToken2": os.environ["ERSTE_PASSWORD"],
            "SunQueryParamsString": sun_query_param,
            "encoded": "false",
            "gx_charset": "UTF-8"
        }

        self.headers = {"Accept": "*/*", "Content-Type": "application/json"}
        session.post("https://netbank.erstebank.hu/daui/UI/Login", data=payload)
        session.post("https://netbank.erstebank.hu/netbankgui-war//app/netbank/login/ssoLogin",
                     headers=self.headers, data='{"header":{"conversationScopeId":2},"data":{"data":{}}}')
        init = session.post("https://netbank.erstebank.hu/netbankgui-war/app/init/init.do").text
        self.token = json.loads(init)["header"]["token"]
        print(self.token)
        self.session = session

    def get_latest_transactions(self) -> typing.List[Transaction]:
        transpotter_payload = {
            "header": {"token": self.token, "conversationScopeId": 1},
            "data": {"": {"start": 0, "limit": 6}}
        }

        transpotter_response = self.session.post(
            "https://netbank.erstebank.hu/netbankgui-war/app/welcome/transactionspotter.query.get",
            headers=self.headers, data=json.dumps(transpotter_payload)).text
        try:
            js_transactions = json.loads(transpotter_response)
        except json.decoder.JSONDecodeError:
            # Erste return a login page when the login token times out...
            self.login()
            return self.get_latest_transactions()
        print(js_transactions)

        parsed_transactions = []
        for tran in js_transactions["data"]:
            t = Transaction(
                id=str(tran["transactionId"]),
                name=str(tran["accountNumber"]),
                description=tran["transactionMethod"],
                cardAcceptance=tran["cardAcceptance"],
                localCurrency=tran["localCurrency"],
                localAmount=tran["localCurrencyAmount"],
                accountCurrency=tran["accountCurrency"],
                accountAmount=tran["accountCurrencyAmount"],
                new_balance=tran["actualBalance"],
                transactionType=tran["transactionType"],
                date=datetime.datetime.now()
            )
            parsed_transactions.append(t)

        return parsed_transactions
