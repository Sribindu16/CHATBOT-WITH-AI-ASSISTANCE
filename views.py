from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import pymysql
from django.views.decorators.csrf import csrf_exempt
import os
import speech_recognition as sr
import subprocess
from numpy import dot
from numpy.linalg import norm
from django.core.files.storage import FileSystemStorage

global uname, questions, answers, vectorizer, tfidf
recognizer = sr.Recognizer()

def trainModel():
    global questions, answers, vectorizer, tfidf
    questions = []
    answers = []
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'AIChatbot',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * FROM faq")
        rows = cur.fetchall()
        for row in rows:
            questions.append(row[0].strip().lower())
            answers.append(row[1])
    vectorizer = TfidfVectorizer(use_idf=True, smooth_idf=False, norm=None, decode_error='replace')
    tfidf = vectorizer.fit_transform(questions).toarray()
    print(tfidf)
    print(tfidf.shape)

trainModel()

def Chatbot(request):
    if request.method == 'GET':
        return render(request, 'Chatbot.html', {})

@csrf_exempt
@csrf_exempt
@csrf_exempt
def record(request):
    if request.method == "POST":
        global answers, vectorizer, tfidf, questions, recognizer
        print("Enter")
        audio_data = request.FILES.get('data')
        fs = FileSystemStorage()

        # Delete previous record files if they exist
        if os.path.exists('ChatbotApp/static/record.wav'):
            os.remove('ChatbotApp/static/record.wav')
        if os.path.exists('ChatbotApp/static/record1.wav'):
            os.remove('ChatbotApp/static/record1.wav')

        # Save the uploaded audio file
        fs.save('ChatbotApp/static/record.wav', audio_data)

        # Correct path to ffmpeg.exe and the audio files
        ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"  # Make sure to include ffmpeg.exe
        input_audio_path = r"C:\Users\91817\OneDrive\Documents\Desktop\AIChatbot\ChatbotApp\static\record.wav"
        output_audio_path = r"C:\Users\91817\OneDrive\Documents\Desktop\AIChatbot\ChatbotApp\static\record1.wav"

        # Ensure the correct path is used in subprocess
        command = f'"{ffmpeg_path}" -i "{input_audio_path}" "{output_audio_path}"'

        try:
            # Run the ffmpeg command
            subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error with ffmpeg conversion: {e}")
            return HttpResponse("Error processing audio file.", content_type="text/plain")

        # Process the converted file using speech recognition
        with sr.WavFile(output_audio_path) as source:
            audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio)
        except Exception as ex:
            text = "unable to recognize"

        # Respond with chatbot's answer
        output = "unable to recognize"
        max_accuracy = 0
        index = -1
        recommend = []

        if text != "unable to recognize":
            query = text.strip().lower()
            testData = vectorizer.transform([query]).toarray()[0]
            for i in range(len(tfidf)):
                predict_score = dot(tfidf[i], testData) / (norm(tfidf[i]) * norm(testData))
                if predict_score > max_accuracy:
                    max_accuracy = predict_score
                    index = i
                    recommend.append(i)

        if index != -1:
            output = answers[index] + "#"
            for i in range(len(recommend)):
                if recommend[i] != index:
                    output += questions[recommend[i]]
                    break
        else:
            output = "Unable to recognize. Please Try Again"

        print(output)    
        return HttpResponse("Chatbot: " + output, content_type="text/plain")
    
def AddQuestion(request):
    if request.method == 'GET':
       return render(request, 'AddQuestion.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})
    
def AdminLogin(request):
    if request.method == 'GET':
        return render(request, 'AdminLogin.html', {})    

def AdminLoginAction(request):
    if request.method == 'POST':
        global userid
        user = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        if user == "admin" and password == "admin":
            context= {'data':'Welcome '+user}
            return render(request, 'AdminScreen.html', context)
        else:
            context= {'data':'Invalid Login'}
            return render(request, 'AdminLogin.html', context)

def UserLoginAction(request):
    if request.method == 'POST':
        global uname
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        index = 0
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'AIChatbot',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and password == row[1]:
                    uname = username
                    index = 1
                    break		
        if index == 1:
            context= {'data':'welcome '+username}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'UserLogin.html', context)


def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        status = "none"
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'AIChatbot',charset='utf8')
        with con:    
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username:
                    status = "Username already exists"
                    break
        if status == "none":
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'AIChatbot',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO register(username,password,contact,email,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                status = "Signup Process Completed. You can Login now"
        context= {'data': status}
        return render(request, 'Signup.html', context)

def AddQuestionAction(request):
    if request.method == 'POST':
        question = request.POST.get('t1', False)
        answer = request.POST.get('t2', False)
        status = "Error in adding question details"
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'AIChatbot',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "INSERT INTO faq(question, answer) VALUES('"+question+"','"+answer+"')"
        db_cursor.execute(student_sql_query)
        db_connection.commit()
        if db_cursor.rowcount == 1:
            status = "FAQ question added to database"
            trainModel()
        context= {'data': status}
        return render(request, 'AddQuestion.html', context)

def ViewUser(request):
    if request.method == 'GET':
        output = ''
        output+='<table border=1 align=center width=100%><tr><th><font size="" color="black">Username</th><th><font size="" color="black">Password</th><th><font size="" color="black">Contact No</th>'
        output+='<th><font size="" color="black">Email ID</th><th><font size="" color="black">Address</th></tr>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'AIChatbot',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from register")
            rows = cur.fetchall()
            output+='<tr>'
            for row in rows:
                output+='<td><font size="" color="black">'+row[0]+'</td><td><font size="" color="black">'+str(row[1])+'</td><td><font size="" color="black">'+row[2]+'</td><td><font size="" color="black">'+row[3]+'</td><td><font size="" color="black">'+row[4]+'</td></tr>'
        output+= "</table></br></br></br></br>"        
        context= {'data':output}
        return render(request, 'AdminScreen.html', context)    





    
