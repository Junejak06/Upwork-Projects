import random # just to use it to pick a request header
import yfinance as yf # yahoo finance 
import requests # web requests handling
import pandas as pd # DataFrame  and read_html
from bs4 import BeautifulSoup as bs # for web scrapping
import datetime
import time


timespan = 300 #timespan for the equity beta calculation
market_risk_float = 0.08 # assume risky asset at 8% return
long_term_growth = 0.0 #assume asset at x% growth, will try to get from yahoo analysis
debt_return = 0.05 # long term debt return at 1% rate
tax_rate = 0.21 #year 2023

header = { 
'User-Agent'      : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
'Accept'          : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
'Accept-Language' : 'en-US,en;q=0.5',
'DNT'             : '1', # Do Not Track Request Header 
'Connection'      : 'close'
}
     
def _yfTicker(symbol):
    import requests
    apiBase = 'https://query2.finance.yahoo.com'

    def getCredentials(cookieUrl='https://fc.yahoo.com', crumbUrl=apiBase+'/v1/test/getcrumb'):
      cookie = requests.get(cookieUrl).cookies
      crumb = requests.get(url=crumbUrl, cookies=cookie, headers=header).text
      return {'cookie': cookie, 'crumb': crumb}
    
    def quote(symbols, credentials):
        url = apiBase + '/v7/finance/quote'
        params = {'symbols': symbols, 'crumb': credentials['crumb']}
        # if list of symbols like ['appl','tsla']
        # params = {'symbols': ','.join(symbols), 'crumb': credentials['crumb']}

        response = requests.get(url, params=params, cookies=credentials['cookie'], headers=header)
        # quotes = response.json()['quoteResponse']['result']
        quotes = response.json()['quoteResponse']['result'][0] #assume one symbol

        return quotes
    
    credentials = getCredentials()
    ticker_info={'info':quote(symbol,credentials)}

    return ticker_info['info']


def calc_intrinsic_value(symbol):
    
    income_statement_url=f'https://finance.yahoo.com/quote/{symbol}/financials?p={symbol}'
    balance_sheet_url=f'https://finance.yahoo.com/quote/{symbol}/balance-sheet?p={symbol}'
    market_cap_url = f'https://finance.yahoo.com/quote/{symbol}?p={symbol}'
    analyse_url = f'https://finance.yahoo.com/quote/{symbol}/analysis?p={symbol}'
    statistics_url = f'https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}'
    
    tickerinfo=_yfTicker(symbol)#,day_begin='1-1-2022', day_end='31-12-2022',interval='1d')
        
    y_Beta=tickerinfo.get('beta')
    y_previousClose=yf.Ticker(symbol).history(period="1d", interval='1d')['Close'].iloc[0]
    
    
    Next5YearPAGrowthRate=0

    try:

        r = requests.get(analyse_url,headers=header)
        page = pd.read_html(r.text)
        for i,p in enumerate(page):
            try:
                df= p[p['Growth Estimates'].str.contains('Next 5 Years \(per annum\)')]
                Next5YearPAGrowthRate  = float(p.loc[4,symbol.upper()].replace('%',''))              
                break
            except Exception as e:
                continue
    except Exception as e:
        print ('Cannot get Analysis view of growth rate. Assume 0 (error:%s)'%(str(e)))
        return  0, y_previousClose

    long_term_growth=((float(Next5YearPAGrowthRate+100)/100)**(1/5)-1) # Next 5 Years (per annum) prediction by analyst

    
    retry=3
    income_statement_header=None
    for i in range(retry): # retry if not getting info
        try:
            income_statement_html = requests.get(income_statement_url,headers=header)
            income_statement_soup = bs(income_statement_html.text, 'html.parser')
            income_statement_table = income_statement_soup.find('div', class_='M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)')
            income_statement_header = income_statement_table.find('div', class_='D(tbr) C($primaryColor)')
            break # if no error then skip retry
        except AttributeError as e:
            print(i,':retry getting income staemeent from ',income_statement_url)
            time.sleep(1)
        except Exception as e:
            print ('Error getting income statement:',str(e))

        
    header_lst = [] 
    try:
        if income_statement_header is None:
            return  -1, y_previousClose

        for i in income_statement_header.find_all('div'):
            if len(i) != 0:
               header_lst.append(i.text)
        header_lst = header_lst[::-1]
        del header_lst[len(header_lst)-1]
        header_lst.insert(0,'Breakdown')
        income_statement_df = pd.DataFrame(columns = header_lst)
    except Exception as e:
        print ('Error getting income_statement_header:', e)
        return  0, y_previousClose
    
    revenue_row = income_statement_table.find('div', class_='D(tbr) fi-row Bgc($hoverBgColor):h')
    revenue_lst = [] 
    for i in revenue_row.find_all('div', attrs={'data-test':'fin-col'}):
        i = i.text
        i = i.replace(",","")
        revenue_lst.append(int(i)*1000)
    revenue_lst = revenue_lst[::-1]
    revenue_lst.insert(0,'Total Revenue')
        
    income_statement_df.loc[0] = revenue_lst
        
    retry=5
    EBIT_row=None
    
    for i in range(retry): # retry if not getting info
        try:        
            EBIT_row = income_statement_table.find('div', attrs={'title':'EBIT'}).parent.parent
            break
        except AttributeError as e:
            print ('Attribute Error getting EBIT from income statement:',str(e))
            time.sleep(1)
        except Exception as e:
            print ('Error getting income statement:',str(e))

    if EBIT_row is None:
        return  0, y_previousClose
    
    EBIT_lst = [] 
    for i in EBIT_row.find_all('div', attrs={'data-test':'fin-col'}):
        i = i.text
        i = i.replace(",","")
        if i=='-':
            i=0
        EBIT_lst.append(int(i)*1000)
    EBIT_lst = EBIT_lst[::-1]
    EBIT_lst.insert(0,'EBIT')
    income_statement_df.loc[1] = EBIT_lst
    
    income_statement_df = income_statement_df.drop('ttm', axis=1)
    
     
   
    latest_rev = income_statement_df.iloc[0,len(income_statement_df.columns)-1]
    earliest_rev = income_statement_df.iloc[0,1]
    rev_CAGR = (latest_rev/earliest_rev)**(float(1/(len(income_statement_df.columns)-1)))-1
    
    EBIT_margin_lst = []
    for year in range(1,len(income_statement_df.columns)):
        EBIT_margin = income_statement_df.iloc[1,year]/income_statement_df.iloc[0,year]
        EBIT_margin_lst.append(EBIT_margin)
    avg_EBIT_margin = sum(EBIT_margin_lst)/len(EBIT_margin_lst)
    
    len_EBIT_available=len(EBIT_lst)
    forecast_df = pd.DataFrame(columns=['Year ' + str(i) for i in range(1,len_EBIT_available+1)]) # 7)]) 
    
    rev_forecast_lst = []
    for i in range(1,len_EBIT_available+1): #7):
        if i != len_EBIT_available-1: #6:
            rev_forecast = latest_rev*(1+rev_CAGR)**i
        else:
            rev_forecast = latest_rev*(1+rev_CAGR)**(i-1)*(1+long_term_growth)
        rev_forecast_lst.append(int(rev_forecast))
    forecast_df.loc[0] = rev_forecast_lst
    
    def applyposneg(num):
        if float(num)<0:
            return -1
        return 1
    
    EBIT_forecast_lst = []
    EBIT_lst.append(0) # TEST: add 0 to last year just to make +ve/-ve sign for forecasted EBIT
    
    for i in range(0,len_EBIT_available):
        EBIT_forecast = rev_forecast_lst[i]*abs(avg_EBIT_margin)*applyposneg(EBIT_lst[i+1])
        EBIT_forecast_lst.append(int(EBIT_forecast))
    forecast_df.loc[1] = EBIT_forecast_lst
    
   
      
    current_date = datetime.date.today()
    past_date = current_date-datetime.timedelta(days=timespan)
    
    #CBOE Interest Rate 10 Year T No
    risk_free_rate_float=(yf.Ticker('^TNX').history(period='5d',
                                 interval='1d')['Close'].iloc[-1])/100

    price_information_df = pd.DataFrame(columns=['Stock Prices', 'Market Prices'])

    price_information_df['Stock Prices']=yf.Ticker(symbol).history(start=past_date, 
                                                        end=current_date,
                                                        interval='1d')['Close']#.reset_index()

    # S&P 500 as Market growth reference
    price_information_df['Market Prices']=yf.Ticker('^GSPC').history(start=past_date, 
                                                        end=current_date,
                                                        interval='1d')['Close']#.reset_index()
    
    returns_information_df = pd.DataFrame(columns =['Stock Returns', 'Market Returns'])
    
   
    stock_return_lst = []
    for i in range(1,len(price_information_df)):
        open_price = price_information_df.iloc[i-1,0]
        close_price = price_information_df.iloc[i,0]
        stock_return = (close_price-open_price)/open_price
        stock_return_lst.append(stock_return)
    returns_information_df['Stock Returns'] = stock_return_lst
    
    market_return_lst = []
    for i in range(1,len(price_information_df)):
        open_price = price_information_df.iloc[i-1,1]
        close_price = price_information_df.iloc[i,1]
        market_return = (close_price-open_price)/open_price
        market_return_lst.append(market_return)
    returns_information_df['Market Returns'] = market_return_lst
    
    covariance_df = returns_information_df.cov()
    covariance_float = covariance_df.iloc[1,0]
    variance_df = returns_information_df.var()
    market_variance_float = variance_df.iloc[1]
    
    equity_beta = covariance_float/market_variance_float
    
    market_risk_premium = market_risk_float - risk_free_rate_float
    
    if y_Beta is None or True:
        beta = equity_beta #use calculated Beta
    else:
        beta = y_Beta #use Yahoo Beta if exists
        
    equity_return = risk_free_rate_float+ beta *(market_risk_premium)

    retry=3
    with requests.Session() as s:
        for i in range(retry): # retry if not getting info
            try:
                balance_sheet_html = s.get(balance_sheet_url,headers=header, timeout=20)
            except Exception as e:
                print ('Error getting balance sheet,retrying:',balance_sheet_html.status_code)
    balance_sheet_soup = bs(balance_sheet_html.text, 'html.parser')
    
    balance_sheet_table = balance_sheet_soup.find('div', class_='D(tbrg)')
    
    net_debt_lst = []
    
    net_debt_row = balance_sheet_table.find('div', attrs={'title':'Total Debt'}).parent.parent
    for value in net_debt_row.find_all('div'):
        value = value.text
        value = value.replace(',','')
        net_debt_lst.append(value)
        
    net_debt_int = int(net_debt_lst[3])*1000 #skip the first two columns which is text and start with 3 which is current period value

    market_cap_html = requests.get(market_cap_url,headers=header)

    market_cap_soup = bs(market_cap_html.text, 'html.parser')
    market_cap_int = 0
    
    market_cap_row = market_cap_soup.find('td', attrs={'data-test':'MARKET_CAP-value'})
    market_cap_str = market_cap_row.text
    market_cap_lst = market_cap_str.split('.')
    
    if market_cap_str[len(market_cap_str)-1] == 'T':
        market_cap_length = len(market_cap_lst[1])-1
        market_cap_lst[1] = market_cap_lst[1].replace('T',(12-market_cap_length)*'0')
        market_cap_int = int(''.join(market_cap_lst))
    
    if market_cap_str[len(market_cap_str)-1] == 'B':
        market_cap_length = len(market_cap_lst[1])-1
        market_cap_lst[1] = market_cap_lst[1].replace('B',(9-market_cap_length)*'0')
        market_cap_int = int(''.join(market_cap_lst))
    
    company_value = market_cap_int + net_debt_int
    WACC = market_cap_int/company_value * equity_return + net_debt_int/company_value * debt_return * (1-tax_rate)
    
    
    
    discounted_EBIT_lst = []
    
    
    for year in range(0,5):
        discounted_EBIT = forecast_df.iloc[1,year]/(1+WACC)**(year+1)
        discounted_EBIT_lst.append(int(discounted_EBIT))

    terminal_value = forecast_df.iloc[1,len_EBIT_available-1]/(WACC-long_term_growth) # len_EBIT_available = 5 used to be
    PV_terminal_value = int(terminal_value/((1+WACC)**len_EBIT_available)) #5))

    try:

        r = requests.get(statistics_url,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        
        page = pd.read_html(r.text)
        y_enterprise_value = 0
        y_total_cash_value = 0
        for i,p in enumerate(page):
            try:
                df= p[p[0].str.contains('Enterprise Value')]

                if not df.empty:
                    #p.index(0).filter(regex='^Enterprise Value ')
                    y_enterprise_value_str=df[1].iloc[0]
                    y_stat_Enterprise_Value = y_enterprise_value_str.split('.') #split 123.4B into 1234 and 4B
                    # print (df, 'y_enterprise_value=',y_enterprise_value, ' vs ticker.info = ',numerize.numerize(y_enterpriseValue))

                    if y_enterprise_value_str[-1] == 'T':
                        if len(y_stat_Enterprise_Value)==1: # no decimal
                            y_stat_Enterprise_Value[0]=y_stat_Enterprise_Value[0].replace('T',12*'0')
                        else:
                            y_stat_Enterprise_Value_len = len(y_stat_Enterprise_Value[1])-1
                            y_stat_Enterprise_Value[1] = y_stat_Enterprise_Value[1].replace('T',(12-y_stat_Enterprise_Value_len)*'0')
                        y_enterprise_value = float(''.join(y_stat_Enterprise_Value))
                    
                    if y_enterprise_value_str[-1] == 'B':
                        if len(y_stat_Enterprise_Value)==1: # no decimal
                            y_stat_Enterprise_Value[0]=y_stat_Enterprise_Value[0].replace('B',9*'0')
                        else:
                            y_stat_Enterprise_Value_len = len(y_stat_Enterprise_Value[1])-1
                            y_stat_Enterprise_Value[1] = y_stat_Enterprise_Value[1].replace('B',(9-y_stat_Enterprise_Value_len)*'0')
                        y_enterprise_value = float(''.join(y_stat_Enterprise_Value))
                    break
                else:
                    print (p)
            except Exception as e:
                print ('Waring: error occurs during y_enterprise_value extraction:',str(e),'page#',i,'\n',p)
                continue

        for i,p in enumerate(page):
            try:

                df= p[p[0].str.contains('Total Cash')]
                if not df.empty:

                    y_total_cash_value_str=df[1].iloc[0]
                    y_stat_Total_Cash = y_total_cash_value_str.split('.') #split 123.4B into 1234 and 4B
                    
                    if y_total_cash_value_str[-1] == 'T':
                        if len(y_stat_Total_Cash)==1: # no decimal
                            y_stat_Total_Cash[0]=y_stat_Total_Cash[0].replace('T',12*'0')
                        else:
                            y_stat_Total_Cash_len = len(y_stat_Total_Cash[1])-1
                            y_stat_Total_Cash[1] = y_stat_Total_Cash[1].replace('T',(12-y_stat_Total_Cash_len)*'0')
                        y_total_cash_value = float(''.join(y_stat_Total_Cash))
                    
                    if y_total_cash_value_str[-1] == 'B':
                        if len(y_stat_Total_Cash)==1: # no decimal
                            y_stat_Total_Cash[0]=y_stat_Total_Cash[0].replace('B',9*'0')
                        else:
                            y_stat_Total_Cash_len = len(y_stat_Total_Cash[1])-1
                            y_stat_Total_Cash[1] = y_stat_Total_Cash[1].replace('B',(9-y_stat_Total_Cash_len)*'0')
                        y_total_cash_value = float(''.join(y_stat_Total_Cash))
                    
                    break
            except Exception as e:
                print ('Waring: error during y_stat_Total_Cash extraction:',str(e))
                continue
    except Exception as e:
        print ('Cannot get EV / TC from yahoo statistisc: %s)'%(str(e)))

 
    if y_enterprise_value: # if Yahoo enterprise_value exists, use it
        enterprise_value = y_enterprise_value
    else:
        enterprise_value = sum(discounted_EBIT_lst)+PV_terminal_value-y_total_cash_value

    equity_value = enterprise_value-net_debt_int+y_total_cash_value

    share_outstanding = balance_sheet_table.find('div', attrs={'title':'Share Issued'}).parent.parent
    share_outstanding_lst = []
    for value in share_outstanding.find_all('div'):
        value = value.text
        value = value.replace(',','')
        share_outstanding_lst.append(value)
    
    # working backward to get the expected share price 
    share_outstanding_int = int(share_outstanding_lst[3])*1000
    equity_intrinsic_value = equity_value/share_outstanding_int
    
    overundervalue_pct=round(((y_previousClose-equity_intrinsic_value)/y_previousClose)*100,2)
    
    return round(equity_intrinsic_value, 3), y_previousClose, discounted_EBIT_lst, terminal_value, enterprise_value, WACC, len_EBIT_available

def read_html_table(source):
    user_agents = [ 
     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
     'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 
     'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148', 
     'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36' 
    ] 
    user_agent = random.choice(user_agents) 
    
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 '}     

    res = requests.get(source,headers=header, timeout=20)

    if res.status_code != 200: 
        res = requests.get(source,headers=header, timeout=20) #try 1 more time
        return None, res.status_code, res.text
    
    soup = bs(res.content, "html.parser")

    if 'Select All' in res.text:
        for tag in soup.find_all("span", {'class':'Fz(0)'}): #remove those select checkboxes if any
            tag.replaceWith('')

    table = soup.find_all('table') # it should give us a table of tickers
    
    if len(table)==0:
        print ('something very wrong gtting ',symbol)
        return None, res.status_code, res.text
    df = pd.read_html(str(table))[0]          
    return df['Symbol']

input_csv_path = '/Users/kunaljuneja/Upwork/nasdaq_forecasts.csv'
output_csv_path = 'updated_sp500_forecasts.csv'

# Read the nasdaq_forecasts.csv file
df = pd.read_csv(input_csv_path)

# Create empty lists to store the calculated values
intrinsic_values = []
previous_closes = []
discounted_EBIT_lsts = []
terminal_values = []
enterprise_values = []
WACCs = []
len_EBIT_availables = []
fcf_values_lists = []  # List to store FCF values for each symbol

# Loop through the symbols and calculate values
for symbol in df['Symbol']:
    try:
        intrinsic_value, previous_close, discounted_EBIT_lst, terminal_value, enterprise_value, WACC, len_EBIT_available = calc_intrinsic_value(symbol)
        
        # Append the calculated values to the respective lists
        intrinsic_values.append(intrinsic_value)
        previous_closes.append(previous_close)
        discounted_EBIT_lsts.append(discounted_EBIT_lst)
        terminal_values.append(terminal_value)
        enterprise_values.append(enterprise_value)
        WACCs.append(WACC)
        len_EBIT_availables.append(len_EBIT_available)
        
        # Calculate FCF values if discounted_EBIT_lst is not None
        if discounted_EBIT_lst is not None:
            fcf_values = [
                discounted_EBIT_lst[0],
                discounted_EBIT_lst[1],
                discounted_EBIT_lst[2],
                discounted_EBIT_lst[3],
                terminal_value
            ]
            fcf_values_lists.append(fcf_values)
        else:
            fcf_values_lists.append(None)
        
        # Print the intrinsic value for the symbol
        print(f"Symbol: {symbol}, Intrinsic Value: {intrinsic_value}")
        
    except Exception as e:
        # Handle exceptions when web scraping fails
        print(f"Error calculating values for symbol {symbol}: {str(e)}")
        
        # Append None values for the failed symbol
        intrinsic_values.append(None)
        previous_closes.append(None)
        discounted_EBIT_lsts.append(None)
        terminal_values.append(None)
        enterprise_values.append(None)
        WACCs.append(None)
        len_EBIT_availables.append(None)
        fcf_values_lists.append(None)

# Add the calculated values as new columns to the DataFrame
df['Intrinsic Value'] = intrinsic_values
df['Previous Close'] = previous_closes
df['Discounted EBIT'] = discounted_EBIT_lsts
df['Terminal Value'] = terminal_values
df['Enterprise Value'] = enterprise_values
df['WACC'] = WACCs
df['Len EBIT Available'] = len_EBIT_availables

# Add FCF columns to the DataFrame
df['FCF Year 1'] = [fcf[0] if fcf is not None else None for fcf in fcf_values_lists]
df['FCF Year 2'] = [fcf[1] if fcf is not None else None for fcf in fcf_values_lists]
df['FCF Year 3'] = [fcf[2] if fcf is not None else None for fcf in fcf_values_lists]
df['FCF Year 4'] = [fcf[3] if fcf is not None else None for fcf in fcf_values_lists]
df['FCF Year 5'] = [fcf[4] if fcf is not None else None for fcf in fcf_values_lists]

# Save the updated DataFrame to a new CSV file
df.to_csv(output_csv_path, index=False)

