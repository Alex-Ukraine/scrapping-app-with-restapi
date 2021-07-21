import csv
import datetime
import requests
import redis
from flask import Flask, request, jsonify

app = Flask(__name__)


def parse(company, place, redis_client):
    # we get csv file by downloading from web or from local directory which already saved like cache
    data_key = company + datetime.datetime.now().strftime("%d-%b-%Y") + '.csv'

    if place == 'url': # if we choose to download data from web and store like file
        URL_BEFORE_COMPANY_NAME = 'https://query1.finance.yahoo.com/v7/finance/download/'
        URL_BEFORE_TIMESTAMP = '?period1=0&period2='
        URL_AFTER_TIMESTAMP = '&interval=1d&events=history&includeAdjustedClose=true'
        URL = URL_BEFORE_COMPANY_NAME + company + URL_BEFORE_TIMESTAMP + \
              str(int(datetime.datetime.timestamp(datetime.datetime.now()))) + URL_AFTER_TIMESTAMP

        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(URL, headers=HEADERS)
        url_content = response.content
        redis_client.set(data_key, url_content)
        response = csv.reader(response.iter_lines(decode_unicode=True), delimiter=',')

    elif place == 'db':
        response = redis_client.get(data_key)
        if not response:
            return {"message": "no data in DB for this company"}
        response = response.decode('utf-8')
        response = csv.reader(response.split('\n'), delimiter=',')

    headers = next(response)
    listy = []
    for row in response:
        dicty = {}
        for idx, value in enumerate(row):
            dicty.update({headers[idx]: value})
        # dicty.update({'company': company})
        listy.append(dicty)

    if not listy:
        return {"message": "no data in web storage or local storage for all time for this company"}
    return listy


@app.route("/api", methods=["GET"])
def read_all():
    # we use redis db to store pairs {company: date} where date is date last downloaded csv from web for certain company
    REDIS_URL = 'localhost'
    REDIS_URL = 'redis://:pf4ed8e4a5661b6c41a7c173ae6e17e67276b324404fac1af04b4f8d151ebbb23@ec2-3-248-238-125.eu-west-1.compute.amazonaws.com:21910'
    #redis_client = redis.Redis(host=REDIS_URL, port=6379, db=0)
    redis_client = redis.Redis(host=REDIS_URL)
    company_param = request.args.get('company')
    source_param = request.args.get('source')
    if company_param:
        if source_param != 'db':
            company_date = redis_client.get(company_param)
            if not company_date or (company_date.decode("utf-8") != datetime.datetime.now().strftime("%d-%b-%Y")):
                company_data = parse(company_param, place='url', redis_client=redis_client)
                redis_client.set(company_param, datetime.datetime.now().strftime("%d-%b-%Y"))
            else:
                company_data = parse(company_param, place='db', redis_client=redis_client)
            return jsonify(company_data), 200
        elif source_param == 'db':
            return jsonify(parse(company_param, place='db', redis_client=redis_client)), 200
    else:
        return jsonify({'message': 'it is necessary to put company parameter in request'}), 404


if __name__ == "__main__":
    # port = int(os.environ.get('PORT'), 8000)
    app.run(debug=False, host='0.0.0.0')
