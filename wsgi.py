import csv
import datetime
import requests
import redis
from flask import Flask, request, jsonify

app = Flask(__name__)


def parse(company, place):
    # we get csv file by downloading from web or from local directory which already saved like cache
    file_name = 'csv_files/'+company + datetime.datetime.now().strftime("%d-%b-%Y") + '.csv'

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
        response = csv.reader(response.iter_lines(decode_unicode=True), delimiter=',')
        with open(file_name, 'wb') as csv_file:
            csv_file.write(url_content)
    else: # if we choose to get data from directory on server
        csv_file = open(file_name, 'r')
        response = csv.reader(csv_file, delimiter=',')

    headers = next(response)
    listy = []
    for row in response:
        dicty = {}
        for idx, value in enumerate(row):
            dicty.update({headers[idx]: value})
        dicty.update({'company': company})
        listy.append(dicty)

    csv_file.close()

    if not listy:
        return {"message": "no data for all time for this company"}, 200
    return listy


@app.route("/api", methods=["GET"])
def read_all():
    # we use redis db to store pairs {company: date} where date is date last downloaded csv from web for certain company
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    company = request.args.get('company')
    if company:
        company_date = redis_client.get(company)
        if not company_date or (company_date.decode("utf-8") != datetime.datetime.now().strftime("%d-%b-%Y")):
            company_data = parse(company, place='url')
            redis_client.set(company, datetime.datetime.now().strftime("%d-%b-%Y"))
        else:
            company_data = parse(company, place='local')
        return jsonify(company_data), 200
    else:
        return jsonify({'message': 'it is necessary to put company parameter in request'}), 404


if __name__ == "__main__":
    # port = int(os.environ.get('PORT'), 8000)
    app.run(debug=True, host='0.0.0.0')
