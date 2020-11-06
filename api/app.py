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
from bson.objectid import ObjectId
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

@app.route('/api/v1/marketplace/open', methods=["GET"])
def marktplace_open():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    mydoc = mycol.find({"active": "1"})
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace/profil/edit', methods=["POST"])
def profilUpdate():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["marketplace"]
    content = json.loads(request.get_json())
    ObjId = content['id']
    x = mycol.update_one(
        { "_id" : ObjectId(ObjId) },
        { "$set": {
            'email': content['email'] }
        } )
    profilExtrasUpdate(content)
    return jsonify({"result":"ok"}), 201

@app.route('/api/v1/marketplace/profile/extras/<id>', methods=["GET"])
def profileExtras(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["profile"]
    mydoc = mycol.find({"userid": id})
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace/profile/users', methods=["GET"])
def profileUser():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["profile"]
    mydoc = mycol.find()
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

def profilExtrasUpdate(content):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["profile"]
    # print ("Test: " + content['id'])
    ObjId = content['id']
    x = mycol.update_one(
        { "userid" : ObjId },
        { "$set": {
            'name': content['name'] }
        },upsert=True )
    return jsonify({"result":"ok"}), 201

@app.route('/api/v1/marketplace/<id>', methods=["GET"])
def marktplace(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    # s = "\"seller\": " + id
    # mydoc = mycol.aggregate( [ { "$match" : { "seller" : id } }, { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description", "active":"$active"} } ] )
    mydoc = mycol.aggregate( [ { "$match" : { "_id" : ObjectId(id) } }, { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description", "active":"$active"} } ] )
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace/my/<id>', methods=["GET"])
def marktplace_my(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    # s = "\"seller\": " + id
    mydoc = mycol.aggregate( [ { "$match" : { "seller" : id } }, { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description", "active":"$active"} } ] )
    # mydoc = mycol.aggregate( [ { "$match" : { "_id" : ObjectId(id) } }, { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description", "active":"$active"} } ] )
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200


@app.route('/api/v1/marketplace/myone/<id>', methods=["GET"])
def marktplace_myoffer(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    # s = "\"seller\": " + id
    # mydoc = mycol.aggregate( [ { "$match" : { "seller" : id } }, { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description", "active":"$active"} } ] )
    mydoc = mycol.aggregate( [ { "$match" : { "_id" : ObjectId(id) } }, { "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description", "active":"$active"} } ] )
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200


@app.route('/api/v1/marketplace/active', methods=["GET"])
def marktplace_aktive():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    mydoc = mycol.aggregate([ { "$match" : { "active" : "1" } },{ "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description", "active":"$active"} } ] )
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace/categoryactive/<id>', methods=["GET"])
def category_aktive(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    mydoc = mycol.aggregate([ { "$match" : { "active" : "1", "category": id } },{ "$project": {"id": {"$toString": '$_id' }, "title": "$title", "seller": "$seller", "price": "$price", "type": "$type", "category": "$category", "type": "$type", "image": "$image", "description": "$description", "active":"$active"} } ] )
    list_cur = list(mydoc)
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

# /api/v1/marketplace/offer/edit
@app.route('/api/v1/marketplace/offer/edit', methods=["POST"])
def offerUpdate():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    content = json.loads(request.get_json())
    ObjId = content['id']
    x = mycol.update(
        { "_id" : ObjectId(ObjId) },
        { "$set": {
            'title': content['title'],
            'description': content['description'],
            'price': content['price'],
            'category': content['category'],
            'type': content['type'],
            'seller': content['seller'],
            'active': content['active'],
            'image': content['image']
           }
        } )
    return jsonify({"result":"ok"}), 201


@app.route('/api/v1/markplace/<id>', methods=["GET"])
def marktplaceById(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marktplace"]
    mycol = mydb["offer"]
    s = "\"_id\": ObjectId('" + id + "')"
    mydoc = mycol.aggregate([
      { "$match": { s } },
    ])
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace/<id>', methods=["GET"])
def marktplaceOffer(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["offers"]
    mydoc = mycol.find({"_id": ObjectId(id) })
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace/categories', methods=["GET"])
def marktplaceCategories():
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["categories"]
    mydoc = mycol.aggregate([ { "$project": {"id": {"$toString": '$_id' }, "active": "$active", "name": "$name" } } ] )
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

@app.route('/api/v1/marketplace/categories/<id>', methods=["GET"])
def marktplaceCategoriesId(id):
    myclient = pymongo.MongoClient("mongodb://mongo:27017/")
    mydb = myclient["marketplace"]
    mycol = mydb["categories"]
    mydoc = mycol.find({"_id": ObjectId(id)})
    list_cur = list(mydoc)
    cat_name = list_cur[0]["name"]
    json_data = dumps(list_cur, indent = 2, default=str)
    return cat_name, 200

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
    list_cur = list(mydoc)
    json_data = dumps(list_cur, indent = 2, default=str)
    return json_data, 200

def p_debug(str):
    app.logger.info("Debug: ", str)
    return

def to_pretty_json(value):
    return json.dumps(value, sort_keys=false,
                      indent=4, separators=(',', ': '))

app.jinja_env.filters['tojson_pretty'] = to_pretty_json

if __name__ == "__main__":
  app.run(debug=True,host='0.0.0.0', port=4006)
