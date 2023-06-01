from flask import Flask, render_template, request, jsonify, send_file, make_response
from io import open
import os
import io
from io import BytesIO
from PIL import Image, ImageDraw
import pathlib
import random
import pickle
from datetime import date
import ntpath
import base64
import glob
import json
import requests
import mysql.connector
import redis
from apig_sdk import signer


app = Flask(__name__, template_folder='.', static_folder='staticFiles')
ALLOWED_EXTENSIONS = {'jpg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET','POST'])
def skin_cancer():
    if request.method == 'POST':
        # Get the file from the form
        file = request.files['image-input']
        if file and allowed_file(file.filename):
            # Mysql connection
            mydb = mysql.connector.connect(host="10.0.2.21", user="root", password="DATABASEPASSWORD", database="doga-project")
            mycursor = mydb.cursor()
            today = date.today()
            
            # Save the file to a temporary location
            url = "MODELART END-POINT URL"
            ak = "YOUR ACCESS KEY"
            sk = "YOUR SECRET KEY"
            method = 'POST'
            headers = {"x-sdk-content-sha256": "UNSIGNED-PAYLOAD"}
            request2 = signer.HttpRequest(method, url, headers)

            sig = signer.Signer()
            sig.Key = ak
            sig.Secret = sk
            sig.Sign(request2)
            files = {'images': file}
            resp = requests.request(request2.method, request2.scheme + "://" + request2.host + request2.uri, headers=request2.headers, files=files)
            print(resp.text)
            doga = json.loads(resp.text)
            
            sql = "INSERT INTO results (Date,Result) VALUES (%s, %s)"
            val = (str(today),str(doga))
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
            print(mycursor.rowcount, "record inserted.")
            mydb.close()
            return render_template('index.html', rest = doga["predicted_label"])
        else:
            return render_template('index.html')
            ##return json.stringify(predict)
    
    if request.method == 'GET':
        rest = ""
        return render_template('index.html', rest = rest)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
