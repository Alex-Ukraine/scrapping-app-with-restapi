import os
import csv
import datetime
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)


def parse(company):
    # URL = 'https://query1.finance.yahoo.com/v7/finance/download/PD?period1=0&period2=1626480000&interval=1d&events=history&includeAdjustedClose=true'
    URL_BEFORE_COMPANY_NAME = 'https://query1.finance.yahoo.com/v7/finance/download/'
    URL_BEFORE_TIMESTAMP = '?period1=0&period2='
    URL_AFTER_TIMESTAMP = '&interval=1d&events=history&includeAdjustedClose=true'
    URL = URL_BEFORE_COMPANY_NAME + company + URL_BEFORE_TIMESTAMP + str(int(datetime.datetime.timestamp(datetime.datetime.now()))) + URL_AFTER_TIMESTAMP

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(URL, headers=HEADERS)
    response = csv.reader(response.iter_lines(decode_unicode=True), delimiter=',')
    headers = next(response)
    listy = []
    for row in response:
        dicty = {}
        for idx, value in enumerate(row):
            dicty.update({headers[idx]: value})
        listy.append(dicty)

    if not listy:
        return {"message": "no data for all time for this company"}, 200
    return listy


@app.route("/api", methods=["GET"])
def read_all():
    company = request.args.get('company')
    if company:
        return jsonify(parse(company)), 200
    else:
        return jsonify({'message': 'it is necessary to put company parameter in request'}), 404


if __name__ == "__main__":
    # port = int(os.environ.get('PORT'), 8000)
    app.run(debug=True, host='0.0.0.0')
