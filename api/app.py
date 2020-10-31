from flask import render_template, request, session, redirect, url_for
from flask_jsonpify import jsonify
from flask import Flask, flash, redirect, render_template, request, session, abort, current_app
from flask_restful import Resource, Api
from flask_cors import CORS
import sys
import json
import os,fnmatch
import logging
import requests
import time
import re
import natsort
import pymongo
from bson.json_util import dumps, loads
from datetime import datetime
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/v1/status', methods=["GET"])
def apistatus():
    return jsonify({"status":"ok"})

@app.route('/api/v1/klopapier', methods=["GET"])
def klopapier():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["klopapier"]
    mycol = mydb["borbeck"]
    mydoc = mycol.find().sort("date")
    list_cur = list(mydoc)
    json_data = dumps({"cases": list_cur}, indent = 2)
    return json_data

@app.route('/api/v1/klopapier/<date>/<val>', methods=["POST"])
def klopapieradd(date,val):
    darf = request.headers.get('darfschein')
    if str(darf) == str(os.environ.get("SEC")):
        myclient = pymongo.MongoClient("mongodb://mongo:27017/")
        mydb = myclient["klopapier"]
        mycol = mydb["borbeck"]
        mydict = { "date": date, "val": val }
        x = mycol.insert_one(mydict)
        return jsonify({"result":"ok"})
    else:
        return jsonify({"result":"no allowed"}), 403

@app.route("/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Corona API"
    return jsonify(swag)

@app.route('/api/v1/corona/<table>/<name>/<val>', methods=["POST"])
def probesadd(table,name,val):
    darf = request.headers.get('darfschein')
    if str(darf) == str(os.environ.get("SEC")):
        myclient = pymongo.MongoClient("mongodb://mongo:27017/")
        mydb = myclient["corona"]
        mycol = mydb[table]
        mydict = { "name": name, "val": val }
        x = mycol.insert_one(mydict)
        return jsonify({"result":"ok"}), 201
    else:
        return jsonify({"result":"no allowed"}), 403

@app.route('/api/v1/corona/<table>', methods=["GET"])
def probes(table):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["corona"]
    mycol = mydb[table]
    mydoc = mycol.find().sort("name")
    # mydoc = mycol.aggregate({$skip: 30}, {"$sort": {"average.name": 1}})
    list_cur = list(mydoc)
    json_data = dumps({"cases": list_cur,"version": "1.0"}, indent = 2)
    return json_data, 200

@app.route('/api/v1/corona/<table>/month/<month>', methods=["GET"])
def probesByMonth(table,month):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["corona"]
    mycol = mydb[table]
    mydoc = mycol.find({"name": { "$regex": u"2020-"+month } }).sort("name")
    # mydoc = mycol.aggregate({$skip: 30}, {"$sort": {"average.name": 1}})
    list_cur = list(mydoc)
    json_data = dumps({"cases": list_cur,"version": "1.0"}, indent = 2)
    return json_data, 200

@app.route('/api/v1/corona/<table>/<name>/<val>', methods=["PUT"])
def update_data(table,name,val):
    darf = request.headers.get('darfschein')
    if str(darf) == str(os.environ.get("SEC")):
        myclient = pymongo.MongoClient("mongodb://mongo:27017/")
        mydb = myclient["corona"]
        mycol = mydb[table]
        mydict = { "name": name, "val": val }
        x = mycol.update({"name": name}, mydict)
        return jsonify({"result":"ok"}), 200
    else:
        return jsonify({"result":"no allowed"}), 403

@app.route('/api/v1/corona/<table>/<name>/<val>', methods=["DELETE"])
def delete_data(table,name,val):
    darf = request.headers.get('darfschein')
    if str(darf) == str(os.environ.get("SEC")):
        myclient = pymongo.MongoClient("mongodb://mongo:27017/")
        mydb = myclient["corona"]
        mycol = mydb[table]
        mydict = { "name": name, "val": val }
        x = mycol.remove(mydict)
        return jsonify({"result":"ok"}), 202
    else:
        return jsonify({"result":"no allowed"}), 403

@app.route('/api/v1/corona/config/<name>/<val>', methods=["POST"])
def add_config(name,val):
    darf = request.headers.get('darfschein')
    if str(darf) == str(os.environ.get("SEC")):
        myclient = pymongo.MongoClient("mongodb://mongo:27017/")
        mydb = myclient["corona"]
        mycol = mydb["config"]
        mydict = { "name": name, "val": val }
        x = mycol.insert_one(mydict)
        return jsonify({"result":"ok"}), 201
    else:
        return jsonify({"result":"no allowed"}), 403

@app.route('/api/v1/corona/config/<name>/<val>', methods=["PUT"])
def update_config(name,val):
    darf = request.headers.get('darfschein')
    if str(darf) == str(os.environ.get("SEC")):
        myclient = pymongo.MongoClient("mongodb://mongo:27017/")
        mydb = myclient["corona"]
        mycol = mydb["config"]
        mydict = { "name": name, "val": val }
        x = mycol.update({"name": name}, mydict, upsert=True )
        return jsonify({"result":"ok"}), 200
    else:
        return jsonify({"result":"no allowed"}), 403

@app.route('/api/v1/corona/config/<str>', methods=["DELETE"])
def del_coronaconfig(str):
    darf = request.headers.get('darfschein')
    if str(darf) == str(os.environ.get("SEC")):
        myclient = pymongo.MongoClient("mongodb://mongo:27017/")
        mydb = myclient.corona
        mydb.config.remove({"name":str})
        return "Delete: " + str , 200
    else:
        return jsonify({"result":"no allowed"}), 403

@app.route('/api/v1/corona/config/<str>', methods=["GET"])
def get_coronaconfig(str):
    print ("string: " + str)
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient.corona
    list_cur = mydb.config.find({"name":str})
    for car in list_cur:
        print('{0} {1}'.format(car['name'], car['val']))
        retval = car['val']
    return retval, 200

@app.route('/api/v1/domains/get/<key>/<value>', methods=["GET"])
def get_domains(key,value):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient.corona
    mydoc = mydb.domains.find({key: { "$regex": u""+value } } )
    list_cur = list(mydoc)
    json_data = dumps({"cases": list_cur}, indent = 2)
    return json_data, 200

# offer / wandet
# @app.route('/api/v1/markplace/<table>', methods=["GET"])
@app.route('/api/v1/marketplace', methods=["GET"])
def marktplace():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    # mydoc = mycol.find(id: '$_id').sort("updatetime", -1)
    mydoc = mycol.aggregate([ { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description" } } ] )
    # mydoc = mycol.aggregate({$skip: 30}, {"$sort": {"average.name": 1}})
    list_cur = list(mydoc)
    # json_data = dumps({"products": list_cur,"version": "1.0"}, indent = 2)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace', methods=["POST"])
def addItem():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    content = request.get_json()
    x = mycol.insert(  json.loads(content) )
    return jsonify({"result":"ok"}), 201

@app.route('/api/v1/markplace/<id>', methods=["GET"])
def marktplaceById(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marktplace"]
    mycol = mydb["offer"]
    s = "\"_id\": ObjectId('" + id + "')"
    mydoc = mycol.aggregate([
      { "$match": { s } },
      # { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description" } }
    ])
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace/uploads/<seller>/<filename>', methods=["GET"])
def save_upload(seller,filename):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["uploads"]
    mydict = { "seller": seller, "filename": filename }
    x = mycol.insert_one(mydict)
    return jsonify({"result":"ok - "}), 200

@app.route('/api/v1/marketplace/uploads/<seller>', methods=["GET"])
def getUploadBySeller(seller):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["uploads"]
    mydoc = mycol.find({"seller": seller})
    # mydoc = mycol.aggregate([ { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description" } } ] )
    list_cur = list(mydoc)
    # json_data = dumps({"products": list_cur,"version": "1.0"}, indent = 2)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

# GET full Article list
@app.route('/api/v1/articles', methods = ["GET"])
def index():
    import os, fnmatch
    master_dictionary = {}
    listOfMetaFiles = os.listdir('meta/')
    listOfMetaFiles = natsort.natsorted(listOfMetaFiles,reverse=True)
    listOfMetaFiles = sorted(listOfMetaFiles)
    pattern = "*.json"
    for metaentry in listOfMetaFiles:
        if fnmatch.fnmatch(metaentry, pattern):
            filename = metaentry.replace(".json", "")
            print ("Filename:", filename)
            master_dictionary[filename] = read_meta_edit(filename)
    app.logger.info("Debug: ", master_dictionary)
    return json.dumps(master_dictionary)

# GET Article by ID
@app.route('/api/v1/articles/<id>', methods = ['GET'])
def getJsonHandler(id):
    content = read_data(id)
    return json.dumps(content)

# PUT Update Artcile
@app.route('/api/v1/articles/<id>', methods = ['PUT'])
def postJsonHandler(id):
    print (request.is_json)
    content = request.get_json()
    print (content)
    write_data(id,content)
    return jsonify({"result":"ok"})

# POST New Article
@app.route("/api/v1/articles", methods=["POST"])
def newarticle():
    callback = request.form.get('callback')
    dateTimeObj = datetime.now()
    id = dateTimeObj.strftime("%Y-%m-%d-%H-%M-%S-%f")
    write_data(id,"")
    write_new_meta(id)
    return redirect("http://"+callback+"/admin/editor.html/"+id);

# GET Metadata by ID
@app.route("/api/v1/metadata/<id>", methods=["GET"])
def meta_edit(id):
    content = read_meta_edit(id)
    return json.dumps(content)

# PUT Update Metadata
@app.route('/api/v1/metadata', methods=['PUT'])
def savemetadata():
    print (request.is_json)
    content = request.get_json()
    metadata = {}
    for a_dict in content:
        if a_dict['name'] != 'callback':
            metadata[a_dict['name']] = a_dict['value']
        if a_dict['name'] == 'id':
            id = a_dict['value']
    print ("metadata: ", metadata, " ID: ", id, file=sys.stderr)
    write_meta(id,metadata)
    return jsonify({"result":"ok"})

# GET full Page list
@app.route('/api/v1/pages', methods = ["GET"])
def pages():
    import os, fnmatch
    master_dictionary = {}
    listOfMetaFiles = os.listdir('pages/')
    listOfMetaFiles = natsort.natsorted(listOfMetaFiles,reverse=True)
    listOfMetaFiles = sorted(listOfMetaFiles)
    pattern = "*.json"
    for metaentry in listOfMetaFiles:
        if fnmatch.fnmatch(metaentry, pattern):
            filename = metaentry.replace(".json", "")
            print ("Filename:", filename)
            master_dictionary[filename] = read_page_data(filename)
    app.logger.info("Debug: ", master_dictionary)
    return json.dumps(master_dictionary)

# POST New Page
@app.route("/api/v1/pages", methods=["POST"])
def newpages():
    callback = request.form.get('callback')
    dateTimeObj = datetime.now()
    id = dateTimeObj.strftime("%Y-%m-%d-%H-%M-%S-%f")
    write_new_page(id)
    return jsonify({"result": id})

# GET Page by ID
@app.route('/api/v1/pages/<id>', methods = ['GET'])
def getPageById(id):
    content = read_page(id)
    return json.dumps(content)

# PUT Update Page
@app.route('/api/v1/pages', methods=['PUT'])
def udpatePageData():
    content = request.get_json()
    print ("content: ", content, file=sys.stderr)
    metadata = {}
    childs = []
    for a_dict in content:
        name = a_dict['name']
        value = a_dict['value']
        if "childs" in name:
            print ("Name: ", name, " Value: ", value, file=sys.stderr)
            childs.append(value)
        else:
            print ("Name: ", name, " Value: ", value, file=sys.stderr)
            metadata[name] = value
        if name == 'id':
            id = value
    metadata['childs'] = childs
    print ("MetaData: ", metadata, file=sys.stderr)
    write_page_data(id,metadata)
    # return json.dumps(metadata)
    return jsonify({"result":"ok"})

# GET Page by Name
@app.route('/api/v1/rewrite/<path:u_path>')
def rewrite(u_path):
    name = u_path
    print ("name: ", name, file=sys.stderr)
    id = pageIdByName(name)
    return jsonify({"id": id})

def pageIdByName(name):
    master_dictionary = {}
    listOfMetaFiles = os.listdir('pages/')
    listOfMetaFiles = natsort.natsorted(listOfMetaFiles,reverse=True)
    listOfMetaFiles = sorted(listOfMetaFiles)
    pattern = "*.json"
    for metaentry in listOfMetaFiles:
        if fnmatch.fnmatch(metaentry, pattern):
            filename = metaentry.replace(".json", "")
            print ("Filename:", filename, file=sys.stderr)
            metaData = read_page_data(filename)
            print ("MetaData: ", json.dumps(metaData), file=sys.stderr)
            if name in metaData['url']:
                app.logger.info("Debug: ", name)
                return metaData['id']
    app.logger.info("Debug: ", master_dictionary)
    return name

# GET Article by ID
@app.route('/api/v1/menu/<id>', methods = ['GET'])
def getMenu(id):
    content = read_menu(id)
    return json.dumps(content)

# PUT Update Artcile
@app.route('/api/v1/menu/<id>', methods = ['PUT'])
def editMenu(id):
    print (request.is_json)
    content = request.get_json()
    metadata = {}
    for a_dict in content:
        if a_dict['name'] != 'callback':
            metadata[a_dict['name']] = a_dict['value']
        if a_dict['name'] == 'id':
            id = a_dict['value']
    print ("metadata: ", metadata, " ID: ", id, file=sys.stderr)
    write_menu(id,metadata)
    return jsonify({"result":"ok"})

    # print (request.is_json)
    # content = request.get_json()
    # print (content)
    # write_menu(id,content)
    # return jsonify({"result":"ok"})

# POST New Article
# @app.route("/api/v1/menu", methods=["POST"])
# def newMenu():
#     callback = request.form.get('callback')
#     dateTimeObj = datetime.now()
#     id = dateTimeObj.strftime("%Y-%m-%d-%H-%M-%S-%f")
#     write_data(id,"")
#     write_new_meta(id)
#     return redirect("http://"+callback+"/admin/editor.html/"+id);


def p_debug(str):
    app.logger.info("Debug: ", str)
    return

def to_pretty_json(value):
    return json.dumps(value, sort_keys=false,
                      indent=4, separators=(',', ': '))

def write_new_page(id):
    page_data = {}
    page_data = {"id": id, "type": "page", "title": id, "author": "Authorname" , "url": "/" + id, "childs": ()}
    write_page(id,page_data);

def write_page(id,data):
    with open("pages/" + id + ".json", "w") as data_file:
        json.dump(data, data_file, indent=4, sort_keys=True)

def read_page_data(id):
    return json.loads(open('pages/' + id + '.json','r').read())

def read_page(id):
    return json.loads(open('pages/' + id + '.json','r').read())

def write_page_data(id,data):
    print ("id: " + id)
    with open("pages/"+id+".json", "w") as data_file:
        json.dump(data, data_file, indent=4, sort_keys=True)

def write_new_meta(id):
    meta_data = {}
    meta_data = {"id": id, "type": "draft", "title": id, "author": "Authorname" }
    write_meta(id,meta_data);

def read_meta_edit(id):
    return json.loads(open('meta/' + id + '.json','r').read())

def write_meta(id,data):
    with open("meta/" + id + ".json", "w") as data_file:
        json.dump(data, data_file, indent=4, sort_keys=True)

def read_data(id):
    return json.loads(open('data/' + id + '.json','r').read())

def write_data(id,data):
    print ("id: " + id)
    with open("data/"+id+".json", "w") as data_file:
        json.dump(data, data_file, indent=4, sort_keys=True)

def read_menu(id):
    return json.loads(open('meta/' + id + '.menu','r').read())

def write_menu(id,data):
    print ("id: " + id)
    with open("meta/"+id+".menu", "w") as data_file:
        json.dump(data, data_file, indent=4, sort_keys=True)

def save_articles(articles, filepath):
    with open(filepath, "w") as f:
        json.dump(articles, f, indent=4)
    return None

app.jinja_env.filters['tojson_pretty'] = to_pretty_json

if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0', port=4006)
