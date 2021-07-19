Python Test Task 

Extract financial data from web site finance.yahoo.com  by a given company for the whole period.

Step 1. Find the company page on the web site. By site search or in any other way.
Step 2. Go to ‘Historical data’ tab on the company page.
Step 3. Choose the max period and get data.
Step 4. Download data via link ‘Download Data’
Step 5. Save data from file to database.

Test List of Companies:
PD ZUO PINS ZM PVTL DOCU CLDR RUN

Please note: 
everything should be executed automatically by the application you implement.

Step 6. Need to create a REST service, which returns JSON with the saved data. Add an opportunity to extract data for the exact company.

Docker is recommended to be used.
The task should be implemented without using Selenium.
Do not use Yahoo Finance library. Please use plain requests to access the data.

**************************************************************
Decision to store data like disk csvfile taken because yahoo not provide downloading data only per 1 LAST!!! day. 
We cannot fetch last part of data.

User could only see last record only if he downloaded csv for certain company for all times.
