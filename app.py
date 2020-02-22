from flask import Flask, jsonify, request
import tabula
import pandas as pd

app = Flask(__name__)

def csv_result(tables):
    return [ table.to_csv() for table in tables ]

def json_result(tables):
    return 'tables', tables 

formaters = { 'csv': csv_result, 'json': json_result }

def excel_result(tables):
    with pd.ExcelWriter('result.xlsx') as writer:
        for table in tables:
            table.to_excel(writer)
        return writer

formaters = { 'csv': csv_result, 'json': json_result, 'excel': excel_result }

@app.route('/', methods=['POST', 'GET'])
def handle():
    urls = request.args.get('urls')
    pages = request.args.get('pages')
    formats = request.args.get('formats')
    formats = [ format for format in formats if format in formaters ]
    if not len(formats):
        formats = ['csv']

    tables=[]
    if urls and pages:
        for url in urls:
            tables += tabula.read_pdf(url, pages=pages)
    if not tables:
        return 'No matching tables found'

    if request.method=='GET':
        return csv_result(tables)
    
    return jsonify({ ( format, formaters[format](tables)) for format in formats })

