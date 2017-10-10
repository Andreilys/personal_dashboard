#!/usr/bin/env python
import mintapi
import time
import sys
from datetime import date, timedelta
import datetime
import os
try:
    from .personal_info import *
except:
    from personal_info import *
#The mint class is used to interact with the mint web scraper.
# After intitializing a Mint object you'll be able to get your weekly and daily spend
class Mint:
    def __init__(self):
        self.week_list = []
        self.today = None
        self.get_weeks()
        self.mint = None
        self.mint_trans = self.get_transactions()



    #The get_weeks function is a helper function which returns the past 7 days
    # in the Month-Day format matching the mint web scraper format
    def get_weeks(self):
        for i in range(7):
            the_date = date.today() - timedelta(i)
            now = the_date.strftime("%c").split(' ')
            now = list(filter(None, now))
            formatted_date = now[1] + " " + now[2]
            self.week_list.append(formatted_date)
        self.today = self.week_list[0]
        return self.week_list


    # The login method will keep executing until it successfully logs in by restarting
    # the script
    def login(self):
        result = None
        while result is None:
            try:
                # This contains my email/login and cookie information to login
                self.mint = mintapi.Mint(MINT_DETAILS[0], MINT_DETAILS[1], MINT_DETAILS[2], MINT_DETAILS[3])
                print("Sleeping")
                time.sleep(600)
                print("finished sleeping")
                result = True
            except Exception as e:
                print(e)
                os.execv(sys.executable, ['python'] + sys.argv)


    #The get_transactions method will keep running until it successfully executes
    def get_transactions(self):
        self.login()
        result = None
        while result is None:
            try:
                self.mint_trans = self.mint.get_transactions_json(include_investment=False, skip_duplicates=False)
                result = True
            except Exception as e:
                os.execv(sys.executable, ['python'] + sys.argv)
        return self.mint_trans


    def get_weekly_spend(self):
        mint_trans = self.mint_trans
        amount_spent_weekly = 0
        for i in range(100):
            transaction_date = mint_trans[i]["odate"]
            if transaction_date in self.week_list and mint_trans[i]["isSpending"] and not mint_trans[i]["isTransfer"] or mint_trans[i]["category"] == "Income":
                transaction = mint_trans[i]["amount"]
                amount_spent_weekly += float(transaction[1:])
            elif mint_trans[i]["isTransfer"] or mint_trans[i]["category"] == "Income":
                pass
            else:
                break
        return round(amount_spent_weekly, 2)


    def get_daily_spend(self):
        mint_trans = self.mint_trans
        amount_spent_daily = 0
        for i in range(100):
            transaction_date = mint_trans[i]["odate"]
            if mint_trans[i]["isTransfer"] or mint_trans[i]["category"] == "Income":
                pass
            elif transaction_date == self.today and not mint_trans[i]["isTransfer"] or mint_trans[i]["category"] == "Income":
                transaction = mint_trans[i]["amount"]
                amount_spent_daily += float(transaction[1:])
            else:
                break
        return round(amount_spent_daily, 2)

mint = Mint()
print(mint.get_daily_spend())
print(mint.get_weekly_spend())
