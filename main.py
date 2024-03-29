#importing all the required libraries
import email
import pandas as pd
import pickle
import requests
from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb  import MySQL
import MySQLdb.cursors
import secrets
import re
import random  
from flask_mail import Mail, Message  # Use Flask-




app = Flask(__name__)


#importing the model 
similarity = pickle.load(open(r'similarity.pkl', 'rb'))
movies = pickle.load(open(r'movie_list.pkl','rb'))
movie_list = movies['title'].values


#MYSQL configuration
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'movie'



mysql =MySQL(app)



# Function to fetch the movie poster path based on the provided movie ID
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path



#The function takes a movie title as input, finds similar movies based on a precomputed similarity matrix, and returns a list of recommended movie names along with their poster paths.
def recommend(movie):
    # Assume movies and similarity are loaded from pickle files
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:10]:
        # fetch the movie poster
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters



@app.route('/', methods=['GET', 'POST'])
def login():
        
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password =  request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
        accounts = cursor.fetchone()
        
        if accounts:
            # Valid username and password
            session['username'] = username  # Store username in session
            return redirect(url_for('home'))  # Redirect to the index route

        else:
            # Incorrect username/password
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg=msg)



#homepage when the user  logs in the website 
@app.route('/home')
def home():
    if not is_user_logged_in():
        return redirect(url_for('login'))  # Redirect to login if not logged in
    else:
    # Replace this with your actual logic to get the logged-in user's username
        username = session.get('username', None)
    return render_template("home.html",user_authenticated=is_user_authenticated(), username=username)

        
 #user logs out       
        
@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('email', None)
	return redirect(url_for('login'))
    
    
   
    
#user Registration 

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    email=''
    username =''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    
    return render_template('register.html', msg = msg)  






@app.route('/recover', methods=['GET', 'POST'])
def recover():
    msg = ''
    email = ''
    username = ''
    if request.method == 'POST':
        email = request.form.get('email')

        # Check if the email exists in your user database (in this case, the 'movies' table)
        
    return render_template('recover.html')

def send_reset_email(email, token):
    # Implement your email sending logic here
    # Example: Use Flask-Mail or any other email library
    pass





    
def is_user_logged_in():
    return 'username' in session

def is_user_authenticated():
    #  if 'username' is in the session
    return 'username' in session




@app.route('/index', methods=['GET', 'POST'])
def index():
    if not is_user_logged_in():
        return redirect(url_for('login'))  # Redirect to login if not logged in
    else:
    # Replace this with your actual logic to get the logged-in user's username
        username = session.get('username', None)


        recommended_movie_names = []
        recommended_movie_posters = []
    if request.method == 'POST':
        selected_movie = request.form['movie']
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
        return render_template('recommendations.html', movie_names=recommended_movie_names, movie_posters=recommended_movie_posters,user_authenticated=is_user_authenticated(), username=username)
    return render_template('index.html', movie_list=movie_list,user_authenticated=is_user_authenticated(), username=username)




if __name__ == '__main__':
    app.run(debug=True)
    