# 2023 Dividend Aristocrats

## Visualizations

This report covers stock market data for companies that were dividend aristocrats in 2023 and includes 25 years of historical dividend payment data ranging from January 4, 1999 to December 29, 2023. [Nasdaq defines dividend aristocrats](https://www.nasdaq.com/stocks/investing-lists/dividend-aristocrats) as “companies that are part of the S&P 500 and have increased their dividends in each of the past 25 years.”

There are four visualizations. A pie chart shows the amount of dividends paid out over the 25 years with each slice representing a sector such as Industrials, Consumer Defensive, and Healthcare among others.

![pie_chart](https://github.com/mkennedm/2023_dividend_aristocrats/assets/8769212/c071c283-6b60-4a35-9979-b87ca9b937e1)

A scatter chart has one point for each stock on a graph where the Y-axis represents the last dividend amount and the X-axis represents the 2023 closing price.

![scatter_chart](https://github.com/mkennedm/2023_dividend_aristocrats/assets/8769212/40da3299-d28d-470f-84e0-6a5dac0ed45c)

A line chart shows the dividend payment amount over time from 1999-2023 for all dividend aristocrats.

![line_chart](https://github.com/mkennedm/2023_dividend_aristocrats/assets/8769212/dd462778-8e17-4fe0-8959-ad971bb926e1)

A matrix has information on every stock including the dividend yield, estimated next ex-dividend date, estimated dividend amount, and DRIP. DRIP is short for Dividend Reinvestment Plan. The value here is how much you would have if you invested $10,000 in the stock on January 4, 1999 and kept reinvesting dividend payments until December 29, 2023.

![matrix](https://github.com/mkennedm/2023_dividend_aristocrats/assets/8769212/4b4a80c6-c68e-4752-a832-f0aa16d70973)


## Data Collection
### 25 Year History
The 25 Year History table which contains the Ex-dividend Date and Dividend amount for each stock going back to 1999 was populated with data from Yahoo Finance. The data for Aflac Incorporated (AFL) for example can be found at https://finance.yahoo.com/quote/AFL/history?period1=915408000&period2=1703808000&interval=capitalGain%7Cdiv%7Csplit&filter=div&frequency=1d&includeAdjustedClose=true The same data for any other stock can be found by replacing “AFL” in the URL with another stock symbol.

Importantly, the Ex-dividend date is not the date the dividends are paid to investors.  [According to Investopedia](https://www.investopedia.com/terms/e/ex-dividend.asp) it “refers to the period after which a stock is traded without a right to its next dividend payment.” The actual pay date may be several weeks after the Ex-dividend date.

It’s also possible to get historical dividend data with Python using a few different APIs. I tested out [Tiingo](https://www.tiingo.com/) and have committed the code in get_stock_data.py. The store_dividend_data function reads in a text file with a list of stock symbols. For each symbol it searches Tiingo for data going back to January 4, 1999. Then it makes a row for each day of activity that includes a dividend. This code was only written as an exercise to see what was possible. None of the data in this project came from the Tiingo API.

The list of dividend aristocrats, acquired from [Hedge Fellow](https://hedgefollow.com/dividend-aristocrats.php) in December 2023 is stored in stocks.txt and includes 67 stock symbols. Some of these stocks made their first dividend payment after 1999. These would be SJM (2000), ABBV (2013), AMCR (2014), and KVUE (2023).

KVUE is a spinoff of JNJ which has been paying dividends since at least 1999. ABBV is a spinoff of ABT which has been paying dividends since at least 1999.
### Estimated Future Payments
The Estimated Future Payments table was populated with data from the [Dividend.com](https://www.dividend.com/) page for each stock. The rows for KVUE, LIN, and EXPD, don’t have estimates because Dividend.com did not provide them at the time the data was collected. Here’s criteria they use to determine when to give estimates

> ### Payout Estimation Logic
> Estimates are provided for securities with at least 5 consecutive payouts, special dividends not included. For ETFs and Mutual Funds, return of capital and capital gains distributions are not included.
> * If the last five payouts show limited variability, we estimate future payouts equal to the most recent one.
> * If the last five payouts show variability and are all growing, we estimate future payouts by applying the average growth rate to the most recent payout.
> * If the last five payouts show variability and are not all growing, we estimate future payouts by applying the lowest growth rate (negative growth rates included) to the most recent payment.

### Stock Details
The Stock Details table was uploaded with 4 columns: Symbol, Name, Sector, and DRIP. The Name column  (column B in the Google Sheet) was populated using a Google Finance function in Google Sheets.

`=GOOGLEFINANCE(A2, "name")`

A2 in the function above is a cell containing a Symbol and was updated for each row.

The Sector column came from Yahoo Finance.

The DRIP value came from searching each stock on [Dividend Channel](https://www.dividendchannel.com/drip-returns-calculator/) January 4, 1999, and December 29, 2023 as start and end dates.

The remaining columns in the table were computed with DAX and will be explained in the Data Modeling section.
### Stock Prices
The Stock Prices table was created using a Google Finance function in Google Sheets. Cells in the 2023 Closing Price column (column B in the Google Sheet) followed this format.

`=INDEX(GOOGLEFINANCE(A2,"price","12/29/2023"),2,2)`

A2 in the function above is a cell containing a Symbol and was updated for each row.

## Data Modeling
### Date
I created the Date table because I knew I would be handling dates in the 25 Year History table,  the Estimated Future Payments table and the Stock Details table. I used the DAX formula below to create the Date table.

```
Date =
VAR MinDate =  MIN ( '25 Year History'[Ex-dividend Date] )
VAR MaxDate = MAX ( 'Estimated Future Payments'[Estimated Next Ex-dividend Date] )
RETURN
ADDCOLUMNS (
    FILTER (
        CALENDARAUTO( ),
        AND (  [Date]  >= MinDate, [Date] <= MaxDate )
    ),
    "Calendar Year", "CY " & YEAR ( [Date] ),
    "Month Name", FORMAT ( [Date], "mmmm" ),
    "Month Number", MONTH ( [Date] )
)
```

### Stock Details
The Stock Details table has 4 columns that were computed with DAX.

Last Dividend Date contains the last dividend date that can be found in the 25 Year History table for each stock.

```
Last Dividend Date =
CALCULATE(
    MAXX(
        RELATEDTABLE('25 Year History'),
        '25 Year History'[Ex-dividend Date]
    ),
    ALLEXCEPT(
        'Stock Details',
        'Stock Details'[Symbol]
    )
)
```

Last Dividend Amount provides the related dividend amount for the Last Dividend Date.

```
Last Dividend Amount = CALCULATE( FIRSTNONBLANK('25 Year History'[Dividend],1),
    FILTER('25 Year History',
        '25 Year History'[Symbol] = 'Stock Details'[Symbol] &&
        'Stock Details'[Last Dividend Date] = '25 Year History'[Ex-dividend Date]))
```


2023 Total is the sum of the dividend payments for each stock within 2023.


```
2023 Total =
CALCULATE(
    SUMX(
        RELATEDTABLE('25 Year History'),
        '25 Year History'[Dividend]
    ),
    YEAR('25 Year History'[Ex-dividend Date]) = 2023
)
```


Dividend Yield is the 2023 Total as a percentage of the 2023 closing stock price.


```
Dividend Yield =
DIVIDE(
    [2023 Total],
    RELATED('Stock Prices'[2023 Closing Price])
)
```
### Relationships

| Table 1               	| Table 1 Column Name         	| Cardinality | Table 2               	| Table 2 Column Name |
|---------------------------|---------------------------------|-------------|---------------------------|---------------------|
| 25 Year History       	| Ex-dividend Date            	| Many to one | Date                  	| Date            	|
| 25 Year History       	| Symbol                      	| Many to one | Stock Details         	| Symbol          	|
| Estimated Future Payments | Estimated Next Ex-dividend Date | Many to one | Date                  	| Date            	|
| Stock Details         	| Symbol                      	| One to one  | Estimated Future Payments | Symbol          	|
| Stock Details         	| Symbol                      	| One to one  | Stock Prices          	| Symbol          	|
| Stock Details         	| Last Dividend Date          	| Many to one | Date                  	| Date            	|
