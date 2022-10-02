#Matheus - DSC220800031

# Import library pandas, RegEx
from io import StringIO
from msilib.schema import File
from string import whitespace
from unittest import TextTestResult
import pandas as pd
import re

# Import library main Flask class and request object
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

#Import database
import sqlite3

#Connect database
db = sqlite3.connect('db_Gold.db', check_same_thread=False)
db.text_factory = bytes
mycursor = db.cursor()

#Create the flask app
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'Text Cleansing for Binar Gold Challenge Data Science Bootcamp'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Text Cleansing by Matheus Wicaksono Jahja - DSC220800031'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,             
                  config=swagger_config)


#Function text cleansing
def text_cleansing(teks):
    #Cleansing emoticon
    teks = re.sub(r"[^\x00-\x7F]+",'', teks)
    #Cleansing punctuation
    teks = re.sub(r"[^a-zA-Z0-9\s]+",'', teks)
    #Cleansing website link
    teks = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ', teks)
    #Cleansing enter paragraph
    teks = re.sub('\n',' ', teks)
    teks = re.sub('  +',' ', teks)
    return teks

def database_txt(input1, input2):
    conn = sqlite3.connect("db_Gold.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS TextBersihBersih (input varchar(255), result varchar(255))""")
    cursor.execute("INSERT INTO TextBersihBersih (input, result) VALUES ('" + input1 + "', '" + input2 + "')")
    conn.commit()
    cursor.close()
    conn.close()
    print("Data Saved to sqlite3")

def database_csv(data) :
    conn = sqlite3.connect("db_Gold.db")
    cursor = conn.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS TextBersihBersih (input varchar(255), result varchar(255))""")

    data.to_sql('TextBersihBersih', conn, if_exist='append', index = False)
    print("Data File Saved to sqlite3")

#Endpoint for text input processing
@swag_from('docs/text-processing.yaml', methods=['GET'])
@app.route('/text-processing', methods=['GET'])

#define text processing function
def text_processing():
    raw_text = request.args.get('raw_text')
    input1 = raw_text
    input2 = text_cleansing(raw_text)
    database_txt(input1, input2)

    #Json response for successful message
    json_response = {
         'status_code': 200,
         'description': "Result from text cleansing",
         'input': input1,
         'output': input2
     }

    response_data = jsonify(json_response)
    return response_data

#Endpoint route for file processing
@swag_from('docs/file-processing.yaml', methods=['POST'])
@app.route('/file-processing', methods=['POST'])
#Define file processing function
def file_processing():
    # file = request.files['uploadfile']
    # df = pd.read_csv(file, names=['textinput'], header = None)
    # df['textresult'] = df.apply(lambda row: process(row[0]), axis=1)
    # database_csv(df)
    
    if "file" in request.files:
      file = request.files['file']
      # Save temporary file in server
      file.save("dataRaw.csv")
      df = pd.read_csv("dataRaw.csv",header=None)
      text = df.values.tolist()
      clean_text = []

      for i in text:
        clean_text.append(text_cleansing(i[0]))

      #df['TextBersihBersih'] = df.apply(lambda row : clean_text(row['input1'],row['input2']), axis = 1)
      #df.to_sql('TextBersihBersih',conn, if_exists='append',index = False)
        
      # Json response for successful request
    json_response = {
              'status_code': 200,
              'description': "Result from clean file",
              'data': clean_text
          }

    response_data = jsonify(json_response)
    return response_data
    
if __name__ == '__main__':
    # run app in debug mode on port 4000
    app.run(host='0.0.0.0',debug=True, port=4000)