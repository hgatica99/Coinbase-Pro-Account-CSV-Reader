import pandas as pd

class CSV_Reader():
    def __init__(self, csv_data=None):
        self.csv_data = csv_data

    # Set csv_data to what ever csv file the user uploads through a csv file path
    def set_file(self, csv_path):
        with open(csv_path, "r") as file:
            self.csv_data=pd.read_csv(file)

    # This returns a list of list of items, with same order id. The idea is that if they all share the same order id, they must be apart of the same transaction
    def get_transactions(self):
        # Won't run unless they run read_file
        # I kept getting an error when trying 'self.csv_data == None:'. Said it was too ambiguous
        if self.csv_data.empty:
            print("There is no data, please try running a.read_file()")
        else:
            transaction_groups=[] 
            data=self.csv_data
            y=len(data)-1
            x=0
            group_list=[data.loc[x]]
            while x<y:
                comparable=data.loc[x+1]
                first=data.loc[x]['order id']
                second=comparable['order id']

                if first!="Nan" and first==second:
                    group_list.append(comparable)
                    x+=1
                else:
                    transaction_groups.append(group_list)
                    group_list=[comparable]
                    x+=1     
            return transaction_groups
    
    # Scan each transaction and try separating them into groups of buys, sells, withdrawals, and deposits using my own algorythm. 
    def catergorize_transactions(self, transactions):
        final_dict={
            'buys': [],
            'sells': [],
            'withdrawals': [],
            'deposits': []
        }

        x=1

        for transaction in transactions:
            x+=1
            non_fee_usd_sum=0
            usd_fee=0
            non_fee_crypto_sum=0
            crypto_fee=0
            withdrawn_amount=0
            deposited_amount=0
            type=None
            unit=None
            unit_amount=None
            crypto_unit=''

            # Theoretically all items in a single transaction share the same date, trade it, and order id
            date=transaction[0]['time']
            trade_id=transaction[0]['trade id']
            order_id=transaction[0]['order id']

            # Since each transaction is a group of individual objects, we must iterate through each one and calculate the sum and unit type
            for item in transaction:
                type=item['type']
                unit=item['amount/balance unit']
                unit_amount=item['amount']
                # "match" seems to determine an order being filled. Negative USD and Positive Crypto signifies buying and vice versa
                if type=='match':
                    if unit=='USD':
                        non_fee_usd_sum+=unit_amount
                    else:
                        non_fee_crypto_sum+=unit_amount
                        crypto_unit=unit
                elif type=='fee':
                    if unit=='USD':
                        usd_fee+=unit_amount
                    else:
                        crypto_fee+=unit_amount
                        crypto_unit=unit
                elif type=='withdrawal':
                    withdrawn_amount+=unit_amount
                    transfer_id = item['transfer id']
                elif type=="deposit":
                    deposited_amount+=unit_amount
                    transfer_id = item['transfer id']

            usd_sum=non_fee_usd_sum+usd_fee
            crypto_sum=non_fee_crypto_sum+crypto_fee

            # Withdrawals/Deposits have transfer ids, but no trade or order id. 
            # Buys/Sells have no transfer id, but do have a trade and order id.
            if type=='withdrawal':
                final_dict['withdrawals'].append({
                    'trans num': x,
                    'date': date,
                    'unit withdrawn': unit,
                    'total': withdrawn_amount,
                    'transfer id': transfer_id
                    })
            elif type=='deposit':
                final_dict['deposits'].append({
                    'trans num': x,
                    'date': date,
                    'unit deposited': unit,
                    'total': deposited_amount,
                    'transfer id': transfer_id
                    })
            else:
                # It's assumed a negative USD sum is a buy, and positve a sell of cryptos since there seems to be no other indicator provided in the file
                if usd_sum<0:
                    final_dict['buys'].append({
                            'trans num': x,
                            'date': date,
                            'unit bought': crypto_unit,
                            'total bought': crypto_sum,
                            'unit sold': unit,
                            'cost': non_fee_usd_sum,
                            'fee': usd_fee,
                            'total sold': usd_sum,
                            'trade id': trade_id,
                            'order id': order_id
                            })
                elif usd_sum>0:
                    final_dict['sells'].append({
                            'trans num': x,
                            'date': date,
                            'unit bought': unit,
                            'total bought': usd_sum,
                            'unit sold': crypto_unit,
                            'cost': crypto_sum,
                            'fee': crypto_fee,
                            'total sold': crypto_sum,
                            'trade id': trade_id,
                            'order id': order_id
                        })
        return final_dict

    # Returns the total amount of a unit sold
    def get_total_unit_sold(self, transactions, symbol):
        unit_sum = 0
        for transaction in transactions:
            for item in transaction:
                if item['type'] == 'match' or item['type'] == 'fee':
                    # I assume if the amount is less than 0, it's because the unit is being sold and traded for another. Unit Net Loss
                    if item['amount/balance unit'] == symbol and item['amount']<0:
                        unit_sum += item['amount']
        # In the csv file, the numbers show negative if I'm selling the unit. I return a positive value instead since it's easier to understand. Sold = 5 not Sold = -5
        return unit_sum * -1
    
    # Returns the total amount of a unit bought
    def get_total_unit_bought(self, transactions, symbol):
        unit_sum = 0
        for transaction in transactions:
            for item in transaction:
                if item['type'] == 'match' or item['type'] == 'fee':
                    # I assume if the amount is greater than 0, it's because the unit is being bought. Unit Net Gain
                    if item['amount/balance unit'] == symbol and item['amount']>0:
                        unit_sum += item['amount']
        return unit_sum
    
    # For a majority of transactions, a fee will be charged. This will return all fees associated with the unit (symbol) provided
    def get_total_unit_fees(self, transactions, symbol):
        fee_sum = 0
        for transaction in transactions:
            for item in transaction:
                if item['type'] == 'fee' and item['amount/balance unit'] == symbol:
                    fee_sum+=item['amount']
        return fee_sum * -1

    def get_total_unit_withdrawn(self, transactions, symbol):
        withdrawn_sum = 0
        for transaction in transactions:
            for item in transaction:
                if item['type'] == 'withdrawal' and item['amount/balance unit'] == symbol:
                    withdrawn_sum += item['amount']
        return withdrawn_sum*-1

    def get_total_unit_deposited(self, transactions, symbol):
        deposit_sum = 0
        for transaction in transactions:
            for item in transaction:
                if item['type'] == 'deposit' and item['amount/balance unit'] == symbol:
                    deposit_sum += item['amount']
        return deposit_sum

    def get_all_symbols(self, transactions):
        symbol_list = []
        for transaction in transactions:
            for item in transaction:
                if item['amount/balance unit'] not in symbol_list:
                    symbol_list.append(item['amount/balance unit'])
        symbol_list.sort()
        return symbol_list
    
    # This will search for all the transactions provided that contain the symbol and return a dictionary of all matches separated by transaction type (buys, sells, withdrawals, deposits)
    def get_all_associated_trans(self, categorized_trans, symbol):
        final_dict = {
            'buys': [],
            'sells': [],
            'withdrawals': [],
            'deposits': []
        }

        for item in categorized_trans:
            for trans in categorized_trans[item]:
                if item == 'buys' or item =='sells':
                    if trans['unit bought'] == symbol or trans['unit sold'] == symbol:
                        final_dict[f'{item}'].append(trans)
                elif item == 'withdawals':
                    if trans['unit withdrawn'] == symbol:
                        final_dict[f'{item}'].append(trans)
                elif item == 'deposits':
                    if trans['unit deposited'] == symbol:
                        final_dict[f'{item}'].append(trans)
                
        return final_dict