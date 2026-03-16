from flask import Flask, render_template,request,redirect,url_for # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
from dotenv import load_dotenv

import os

app = Flask(__name__)
title = "TODO sample application with Flask and MongoDB"
heading = "TODO Reminder with Flask and MongoDB"
# get uri form .env file if not resolve to localhost
load_dotenv()
mongo_uri = os.environ.get("MONGO_URI")

#mongo_uri = os.environ.get("MONGO_URI")
if mongo_uri:
    print(f"Using MongoDB URI from environment: {mongo_uri}")
else:
    print(f"Environment variable MONGO_URI not set. Using default: {mongo_uri}")

client = MongoClient(mongo_uri)

# Test connection
try:
    client.admin.command("ping")
    print("MongoDB connection successful!")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
#mongo_uri = os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017")
#client = MongoClient(mongo_uri)

db = client.mymongodb    #Select the database
todos = db.todo #Select the collection name

def redirect_url():
    return request.args.get('next') or \
           request.referrer or \
           url_for('index')

@app.route("/list")
def lists ():
        #Display the all Tasks
        todos_l = todos.find()
        a1="active"
        return render_template('index.html',a1=a1,todos=todos_l,t=title,h=heading)

@app.route("/")
@app.route("/uncompleted")
def tasks ():
        #Display the Uncompleted Tasks
        todos_l = todos.find({"done":"no"})
        a2="active"
        return render_template('index.html',a2=a2,todos=todos_l,t=title,h=heading)


@app.route("/completed")
def completed ():
        #Display the Completed Tasks
        todos_l = todos.find({"done":"yes"})
        a3="active"
        return render_template('index.html',a3=a3,todos=todos_l,t=title,h=heading)

@app.route("/done")
def done():
        #Done-or-not ICON
        id=request.values.get("_id")
        task=todos.find_one({"_id":ObjectId(id)})  # use find_one instead of find
        if task:  # check if task exists
            if(task["done"]=="yes"):
                    todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"no"}})  # use update_one
            else:
                    todos.update_one({"_id":ObjectId(id)}, {"$set": {"done":"yes"}})  # use update_one
        redir=redirect_url()

        return redirect(redir)

@app.route("/action", methods=['POST'])
def action ():
        #Adding a Task
        name=request.values.get("name")
        desc=request.values.get("desc")
        date=request.values.get("date")
        pr=request.values.get("pr")
        todos.insert_one({ "name":name, "desc":desc, "date":date, "pr":pr, "done":"no"})
        return redirect("/list")

@app.route("/update")
def update ():
	id=request.values.get("_id")
	task=todos.find({"_id":ObjectId(id)})
	return render_template('update.html',tasks=task,h=heading,t=title)

@app.route("/remove")
def remove():
        #Deleting a Task with various references
        key=request.values.get("_id")
        todos.delete_one({"_id":ObjectId(key)})  # use delete_one instead of remove
        return redirect("/")

@app.route("/action3", methods=['POST'])
def action3 ():
        #Updating a Task with various references
        name=request.values.get("name")
        desc=request.values.get("desc")
        date=request.values.get("date")
        pr=request.values.get("pr")
        id=request.values.get("_id")
        todos.update_one({"_id":ObjectId(id)}, {'$set':{ "name":name, "desc":desc, "date":date, "pr":pr }})
        return redirect("/")

@app.route("/search", methods=['GET'])
def search():
        #Searching a Task with various references

        key=request.values.get("key")
        refer=request.values.get("refer")
        if(key=="_id"):
                todos_l = todos.find({refer:ObjectId(key)})
        else:
                todos_l = todos.find({refer:key})
        return render_template('searchlist.html',todos=todos_l,t=title,h=heading)

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
