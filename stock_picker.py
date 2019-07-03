import argparse
import csv 
import datetime 
import difflib
import statistics

# can create a date_config...as of now only one format
date_config = '%d-%b-%Y'

def get_data(csv_file_path):
    """Get the data from the csv file path
    Note:
        Assumes delimeter in the csvfile is a space
    """
    stock_data = {}
    with open(csv_file_path, 'r') as csvfile: 
        csvreader = csv.reader(csvfile, delimiter=' ')
        next(csvreader) # skip the header..assuming header is present in all the csv files
        for row in csvreader:
            stock, date, price = row
            stock = stock.strip() # handle extra spaces
            date = date.strip()
            price = price.strip()
            if stock in stock_data:
                stock_data[stock].append([date, price])
            else:
                stock_data[stock] = [[date, price]]
            
    return  stock_data

def get_buy_sell_date(stock_data):
    """Give out the buy and sell date of the stock along with its price to get max profit
    """
    assert (len(stock_data) >= 2)

    max_profit = stock_data[1][1] - stock_data[0][1]
    min_price = stock_data[0][1]
    sell_data = stock_data[1]
    buy_data = stock_data[0]
    min_buy_data = stock_data[0]

    # find the max profit ...
    for i in range(1, len(stock_data)):
        if (stock_data[i][1] - min_price > max_profit):
            max_profit = stock_data[i][1] - min_price
            sell_data = stock_data[i]
            min_buy_data = buy_data
        if min_price < stock_data[i][1]:
            min_price = stock_data[i][1]
            buy_data = stock_data[i]

    return (max_profit*100, sell_data, min_buy_data) # profit for 100 shares

def get_metrics(stock_data, start_date, end_date):
    """Process the stocks from the stock data and give metrics.
    Arguments:
        stock_data: The stock_data from the csvfile data.
        start_data: The start_date
        end_date: The end_date
    Returns:
        Mean
        Std-Deviation
        Buy-Date
        Sell-Date
        Profit (after buying 100 shares)
    """
    # convert the date string to dateobjects
    stock_data_modified = [[datetime.datetime.strptime(date_text, date_config), price] for date_text,price in stock_data]
    start_date = datetime.datetime.strptime(start_date, date_config)
    end_date = datetime.datetime.strptime(end_date, date_config)
    
    # sort the data according to the dates
    stock_data_sorted = sorted(stock_data_modified, key=lambda x: x[0])

    # fill-in the missing values using the previous date...assuming ...no startdate will have empty price
    for  i,ele in enumerate(stock_data_sorted):
        _, price = ele
        if not price:
            stock_data_sorted[i][1] = stock_data_sorted[i-1][1]

    # get the data that is there in between the start_date and end_date
    stock_data_range = [ele for ele in stock_data_modified if start_date < ele[0] < end_date]

    # convert the price to float ..once and for all...
    stock_data_range = [[ele[0], float(ele[1])] for ele in stock_data_range]

    if stock_data_range and len(stock_data_range) >= 2:
        # find the buy and sell date
        profit, sell_data, buy_data = get_buy_sell_date(stock_data_range)
        # find out the profit

        # give out the average
        mean = statistics.mean([ele[1] for ele in stock_data_range])
        # give out the sd
        sd = statistics.stdev([ele[1] for ele in stock_data_range]) 

        buy_date = buy_data[0]
        sell_date =  sell_data[0]
        return mean, sd, buy_date, sell_date, profit
    else:
        return 

def check_format(date_text, format):
    """Returns whether the date input is in the required format or not"""
    try: 
        datetime.datetime.strptime(date_text, date_config) 
        return True
    except ValueError:
        return False 
    return False

def get_the_nearest_match(stock_name, stock_names_csv):
    closest_matches = difflib.get_close_matches(stock_name, stock_names_csv)
    if closest_matches:
        return  closest_matches[0]
    else:
        return ""

def process():
    """The stock analysis process.
    """
    # get the stock data in the required format
    all_stock_data = get_data(csv_file_path)
    
    stock_name = input("Welcome Agent! Which stock you need to process?:- ")
    
    stock_name = stock_name.strip() # remove unwanted spaces and things
    stock_names_csv = all_stock_data.keys() 

    proceed_further = False
    while not proceed_further:
        if stock_name not in stock_names_csv:
            probable_stock = get_the_nearest_match(stock_name, stock_names_csv) # get the nearest match of the given stock
            if probable_stock:
                response = input(f"Oops! Do you mean {probable_stock} (y or n) :- ")
                # handle cases for yes or no inputs
                while response.strip().lower() not in ["y", "n"]:
                    response = input(f"please input (y or n) :- ")
                if response == 'y':
                    stock_name = probable_stock
                    proceed_further = True
                else:
                    stock_name = input("Please enter which stock to process:- ")
            else:
                stock_name = input("Stock not exists!! Please enter which stock to process:- ")
        else:
            proceed_further = True

    # handle the start date and end data
    start_date = input("From which date you want to start?(DD-MMM-YYYY):- ")
    while not check_format(start_date, date_config):
        start_date = input("Oops! please put in the correct date or format (DD-MMM-YYYY):- ")

    end_date = input("Till which date you want to analyze:- ")
    while not check_format(end_date, date_config):
        end_date = input("Oops! please put in the correct date format (DD-MMM-YYYY):- ")

    stock_data = all_stock_data[stock_name]

    # give out the metrics
    metrics = get_metrics(stock_data, start_date, end_date)
    if metrics:
        mean, sd, buy_date, sell_date, profit = metrics
        print (f"Here is your result:- \nmean: {mean}\nStd: {sd}\nBuy date: {buy_date:%d-%b-%Y}\nSell date: {sell_date:%d-%b-%Y}\nProfit: {profit}")
    else:
        print ("Sorry more than 2 stocks doesnot exists in the given date range! Please try again")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process stocks and return insights.')
    parser.add_argument('input_file_path', metavar='csv_file_path', type=str,
                        help='Path to the csv file')
    args = parser.parse_args()
    csv_file_path = (args.input_file_path)
    process()
    