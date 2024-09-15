from flask import Flask, session, make_response, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

from prompts.config import prompts

load_dotenv()

from openai import OpenAI
import os
import json

API_KEY = os.environ['OPEN_AI_API_KEY']

DB_URI = os.environ['DB_URI']

app = Flask(__name__, template_folder='templates')

env_config = os.getenv("PROD_APP_SETTINGS", "config.DevelopmentConfig")
app.config.from_object(env_config)

app.secret_key = 'your api key'

client = OpenAI(api_key=API_KEY)
mongo_client = MongoClient(DB_URI, connect=False)

db = mongo_client.get_database('situations')
user_situations_collection = db.get_collection('situation')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        text = request.form['text']
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
        {"role": "system", "content": f"""
            {prompts['initial_profile']}
            It will be Key/Value pairs, each field can be string,boolean, lists. if there is a nested object, flat it to root level. Lists should 
            not contain any nested json.
            Only return the JSON object (strictly json easy to parse in code).
            keep all the facts and features at root level, avoid unnecessary nesting.
            
            FORMAT = JSON
            """},
        {"role": "user", "content": text},
        
        ]
    )
    result = json.loads(response.choices[0].message.content)
    insert_doc = result.copy()

    user_situations_collection.insert_one(insert_doc)
    
    session['text'] = text
    session['initial_profile'] = result
    session['inserted_id'] = str(insert_doc['_id'])
    
    return redirect(url_for('show_profile'))



@app.route('/show_profile', methods=['GET', 'POST'])
def show_profile():
    text = session.get('text', '')
    initial_profile = session.get('initial_profile', {})
    
    if request.method == 'GET':    
        return render_template('initial.profile.html', text=text, initial_profile=initial_profile)
    
    if request.method == 'POST':
        pass
    

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    if request.method == 'POST':
        text  = ''
        for k, v in request.form.items():
            text += f'{k}: {v}\n'
        user_profile = dict(request.form)
        
        user_situation =  request.form['additional_information']
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
        {"role": "system", "content": f"""
            {prompts['generate_questions']}
            User described the following situation: {user_situation} 
            Now return all the list of questions in JSON format.
            """ + """
            FORMAT = JSON
            {
                "questions": [
                    "question1 ...",
                    "questions2 ..",
                    "questions3 ..",
                    "questions4 ..",
                    "questions5 .."
                ]
            }
            The response content is strictly json only, don't append or present anything.
            """},
        {"role": "user", "content": text},
        
        ]
    )
    session.pop('text', None)
    session.pop('initial_profile', None)
    
    session['updated_profile'] = user_profile
    
    result = json.loads(response.choices[0].message.content)
    questions = list(result['questions'])
    return render_template('questions.html', questions=questions, user_profile=user_profile)


@app.route('/update_profile', methods=['POST'])
def update_profile():
    if request.method == 'POST':
        text  = ''
        for k, v in request.form.items():
            text += f'{k}: {v}\n'
        if not session.get('updated_profile'):
            return make_response('user profile missing', 400)
        
        user_profile = session['updated_profile']
        user_profile['user_situation'] = user_profile['additional_information']
        user_profile.pop('additional_information', '')
        
        inserted_id = session.get('inserted_id')
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
        {"role": "system", "content": f"""
            You are the social analyst. 
            You are working for a consulting business that helps people to make decisions in complex life situations. 
            User profile: {user_profile}
            Questions answered by the user are given = {text}
            Now based on these answers, find the missing fields in user profile based on the question answered by the user.
            It will be Key/Value pairs, each field can be string,boolean, lists. if there is a nested object, flat it to root level. Lists should 
            not contain any nested json.
            Only return the JSON object (strictly json easy to parse in code).
            
            FORMAT = JSON
            """},
        {"role": "user", "content": text},
        
        ]
    )
    result = json.loads(response.choices[0].message.content)
    result = dict(result)
    result.update(dict(user_profile))
    
    user_situations_collection.find_one_and_update({ '_id': ObjectId(inserted_id) }, {'$set': result})
    
    session.pop('text', None)
    session.pop('inserted_id', None)
    session.pop('initial_profile', None)
    session.pop('updated_profile', None)    
    
    
    response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
        {"role": "system", "content": f"""
            You are the social analyst. 
            You are working for a consulting business that helps people to make decisions in complex life situations. 
            User profile: {result}
            Now based on this profile, provide a list of strategies to resolve a user’s situation. 
            First, include four strategies that likely will work. Second, include four strategies that typically lead to failures.
            Suggest maximum five products or services that may help to resolve a given user’s situation. Use simple language and brief sentences. Generate output in plain text, not markup. : {user_profile['user_situation']}
            """},
        {"role": "user", "content": text},
        
        ]
    )
    return render_template('suggestions.html', user_profile=dict(result), suggestions=[response.choices[0].message.content])
