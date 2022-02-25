import csv
from csv_reader import CSV_Reader
import pprint

## OBSERVATIONS ##

## When comparing the data from the csv_reader.csv_data.loc to the coinbase pro csv file, items do get rounded, i.e: amount(0.00000) and balance(0.000000) from a quick glance.
## Its beyond the tenths place but since this is to help with taxes, please be aware of this slight difference
## I haven't checked if everything is rounded the same but I assume so.

pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)

# EXAMPLE USES PROVIDED BELOW
# Numbers are not rounded to retain exact info as close as possible for tax purposes

CSV_PATH = 'USER COINBASE PRO ACCOUNT CSV PATH'

# Creating the reading object
csv_reader = CSV_Reader()

# If you don't initiate the object with a path, or just want to update the path, then you can set_file
csv_reader.set_file(csv_path=CSV_PATH)

# Find all transactions. Every function moving forward will read and analyze this object
transactions = csv_reader.get_transactions()

# This will scan through all transactions and return a nesteded dictionary of transactions divided by buys, sells, withdrawals, and deposits
catergorized_trans = csv_reader.catergorize_transactions(transactions=transactions)
btc_sold = csv_reader.get_total_unit_sold(transactions=transactions, symbol='BTC')
btc_bought = csv_reader.get_total_unit_bought(transactions=transactions, symbol='BTC')

# If I'm selling USD, that usually means I'm buying crypto
usd_sold = csv_reader.get_total_unit_sold(transactions=transactions, symbol='USD')

# If I'm buying USD, that usually means I'm selling crypto
usd_bought = csv_reader.get_total_unit_bought(transactions=transactions, symbol='USD')

# Fees usually associated with buying cryptos via USD
usd_fees = csv_reader.get_total_unit_fees(transactions=transactions, symbol='USD')

# How much USD I deposited in 2021
usd_deposited = csv_reader.get_total_unit_deposited(transactions=transactions, symbol='USD')

# How much USD I withdrew in 2021
usd_withdrawn = csv_reader.get_total_unit_withdrawn(transactions=transactions, symbol='USD')

# This will return a list of strings of all unique symbols within the csv file in alphabetical order
symbol_list = csv_reader.get_all_symbols(transactions=transactions)

# This will return a dictionary of transacrtions that include the symbol BTC
associated_btc_trans = csv_reader.get_all_associated_trans(categorized_trans=catergorized_trans, symbol='BTC')

print(usd_bought)
print(usd_sold)
print(usd_fees)
print(usd_withdrawn)
print(usd_deposited)
print(symbol_list)
pp.pprint(associated_btc_trans)