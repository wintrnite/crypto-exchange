# Crypto exchange

### Description:
Get current exchange rates (**get request**)

    curl *running_server*

Add new cryptocurrency (**post request**, forms: **crypto_name**, **sell_price**, **buy_price**)

    curl -X POST -F crypto_name=*your_crypto_name* -F sell_price=*crypto_sell_price* -F buy_price=*crypto_buy_price* *running_server*/add

Register new user (**post request**, forms: **user_name**)
    
    curl -X POST -F user_name=*your_name* *running_server*/register

Get user balance (**get request**)

    curl *running_server*/*user_name*/balance

Get user portfolio (**get request**)

    curl *running_server*/*user_name*/portfolio

Buy cryptocurrency (**post request**, forms: **crypto_name**, **count**, **price**)

    curl -X POST -F crypto_name=*buying_crypto_name* -F count=*buying_count* -F price=*expected_price* *running_server*/*user_name*/buy

Sell cryptocurrency (**post request**, forms: **crypto_name**, **count**, **price**)

    curl -X POST -F crypto_name=*selling_crypto_name* -F count=*selling_count* -F price=*expected_price* *running_server*/*user_name*/sell

Show user operations history (**get request**, args (*required*): **limit**, **page**)
     
     curl *running_server*/*user_name*/history?limit=*page_operations_count*&offset=*number_of_page*
___

### Create venv:
    make venv

### Run tests:
    make test

### Run linters:
    make lint

### Run formatters:
    make format

### Run app:
    make up

App logs in **app.logs**

App data base in  **app.db**
