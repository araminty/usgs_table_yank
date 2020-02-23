from flask import Flask, jsonify, request
import tabula
import pandas as pd
import pickle
from os.path import isfile

app = Flask(__name__)

def csv_result(tables):
    return jsonify(dict(enumerate([ table.to_csv() for table in tables ])))

# def excel_result(tables):
#     with pd.ExcelWriter('result.xlsx') as writer:
#         for table in tables:
#             table.to_excel(writer)
#         return writer

# formaters = { 'csv': csv_result, 'excel': excel_result }

files = {}
if isfile('files_index.pkl'):
    with open('files_index.pkl', 'rb') as file_index:
        files = pickle.load(file_index)

@app.route('/', methods=['POST', 'GET'])
def handle():
    url = request.args.get('url')
    pages = request.args.get('pages')
    # format = request.args.get('format')
    print('url', url, 'pages', pages, 'formats', format)

    if url in files:
        print('loading cached file...')
        pdf = files[url]
        print('done')
    else:
        print('downloading remote file...')
        pdf = tabula.file_util.localize_file(url)[0]
        print('done')
        if pdf:
            files[url]=pdf
            with open('files_index.pkl', 'wb+') as file_index:
                pickle.dump(files, file_index)

    # if not format or format not in formaters:
    #     format = 'csv'


    int_check = lambda i: int(i) if type(i)==str and i.isdigit() else i if type(i)==int else None

    if pages:
        if pages=="all":
            pass
        else:
            if type(pages)!=list:
                pages = [ pages ]
            pages = [ int_check(page) for page in pages ]
    if not pages:
        pages = "all"

    tables= tabula.read_pdf(pdf, pages=pages)

    if not tables:
        return 'No matching tables found'

    return csv_result(tables)

