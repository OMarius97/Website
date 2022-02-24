from flask import Flask, render_template, request, session, redirect

import random
import mysql.connector
from mysql.connector import Error
import smtplib, ssl



# Connection to Database
def connection_db(user, password, host, name):
    connection = None
    try:
        connection = mysql.connector.connect(
            user = user,
            passwd = password,
            host = host,
            database = name
        )
        print ('connection to MySql db succesful')

    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


conn = connection_db('xxxx', 'xxxx', 'xxxx','xxxx')

# Execute the query
cursor = conn.cursor()

# Flask
app = Flask(__name__)
app.secret_key ='Marius1997!'



port = 587
smtp_server = "smtp.gmail.com"
sender_email = "xxx"
receiver_email = "xxxx"
password = "xxx"


# Home page

@app.route('/', methods=['GET', 'POST'])
def homepage():
    user = session.get('user', None)

    return render_template('index.html', user = user)


# User login and register

@app.route('/register', methods = ['GET', 'POST'])
def register():

    error = None

    if request.method == 'POST' and 'nickname' and 'email' and 'password' and 'cpassword' in request.form:
        nickname = request.form.get('nickname')
        mail = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        data = (nickname, mail, password)

        if cpassword != password:
            error = 'Password'
        else:
            cursor.execute(f"SELECT USER_ID FROM User WHERE USER_NICKNAME = '{nickname}';")
            try:
                for row in cursor:
                    nickname_check = row
                if bool(nickname_check) == True:
                    error = 'Nickname'
            except:
                cursor.execute(f"SELECT USER_ID FROM User WHERE USER_MAIL = '{mail}';")
                try:
                    for row in cursor:
                        mail_check = row
                    if bool(mail_check) == True:
                        error = 'Mail'
                except:
                    insert = "INSERT INTO User (USER_NICKNAME, USER_MAIL, USER_PASSWORD) VALUES (%s, %s, %s);"
                    cursor.execute(insert, data)
                    conn.commit()

    return render_template('register.html', error = error)


@app.route('/login', methods = ['GET', 'POST'])
def login():

    user =''
    session['user'] = user

    if request.method == 'POST' and 'password' in request.form:

        email = request.form.get('email')
        password = request.form.get('password')

        cursor.execute(f"""SELECT USER_NICKNAME FROM User
                            WHERE USER_MAIL = '{email}'
                            AND USER_PASSWORD = '{password}';""")
        try:
            for row in cursor:
                nick = row
            if bool(nick) == True:
                for element in nick:
                    user = element
                    session['user'] = user
                    return redirect('/')
        except:
            user = 'empty'

    return render_template('login.html', user = user)


# Contact Page

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    user = session.get('user', None)
    confirmation = ''

    if request.method == 'POST' and 'email' in request.form:
        title = request.form.get('title')
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')

        if bool(email) == False or bool(subject) == False or bool(name) == False:
            confirmation = 'no'

        else:

            message = f'sender {email} Title {title} name {name} Message {subject}'

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls(context=context)
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message)

            confirmation = 'yes'
    return render_template('contact.html', confirmation=confirmation, user = user)


# Menu

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    user = session.get('user', None)

    return render_template('menu.html', user = user)


#Guess The Number game

@app.route('/difficulty1', methods=['GET', 'POST'])
def g1dif():
    user = session.get('user', None)
    diff = []
    nrmax = 0
    if 'easy' in request.form:
        diff.append('Easy')
        nrmax = 5
        solution = random.randint(1, nrmax)
        session['solution'] = solution
    elif 'normal' in request.form:
        diff.append('Normal')
        nrmax = 10
        solution = random.randint(1, nrmax)
        session['solution'] = solution
    elif 'impossible' in request.form:
        diff.append('Impossible')
        nrmax = 15
        solution = random.randint(1, nrmax)
        session['solution'] = solution

    session['nrmax'] = nrmax

    return render_template('difficulties.html', diff=diff, user = user)

@app.route('/Guess-the-number', methods=['GET', 'POST'])
def guess_the_number():
    user = session.get('user', None)
    life = 3
    solution = session.get('solution', None)
    result = ()
    hint = ''

    def possibilities(counter, guess, life=life):
        if guess == solution:
            hint = 'Congratulation you win, Well done'
        elif guess >= solution:
            life = life - counter
            hint = 'Too high try again'
        elif guess <= solution:
            life = life - counter
            hint = 'Too low try again'
        return life, hint

    if 'guess1' in request.form:
        guess1 = int(request.form.get('guess1'))
        result = possibilities(counter=1, guess=guess1)

    if 'guess2' in request.form:
        guess2 = int(request.form.get('guess2'))

        result = possibilities(counter=2, guess=guess2)

    if 'guess3' in request.form:
        guess3 = int(request.form.get('guess3'))
        if guess3 == solution:
            hint = 'Congratulation you win, Well done'

        else:
            life = life - 3
            hint = f'Aaah sorry you lose, the corect answer was {solution}'

    if result:
        life = result[0]
        hint = result[1]
    else:
        pass

    print(life)
    print(hint)

    return render_template('guess_the_number.html', solution=solution, life=life, hint=hint, user=user)

# Memorize Game

@app.route('/difficulty2', methods=['GET', 'POST'])
def g2dif():
    user = session.get('user', None)
    diff = []
    nrmax = 0
    listlevel = []
    if 'easy' in request.form:
        diff.append('Easy')
        nrmax = 5
        session['nrmax'] = nrmax
    elif 'normal' in request.form:
        diff.append('Normal')
        nrmax = 10
        session['nrmax'] = nrmax
    elif 'impossible' in request.form:
        diff.append('Impossible')
        nrmax = 15
        session['nrmax'] = nrmax

    for level in range(nrmax - 4, nrmax + 1):
        number = []
        for i in range(0, level):
            number.append(random.randint(1, 9))
        listlevel.append(number)

    session['listlevel'] = listlevel
    session['level'] = 0

    return render_template('difficultiesmemory.html', diff=diff, user = user)


@app.route('/Memorize', methods=['GET', 'POST'])
def memorize():
    user = session.get('user', None)
    listlevel = session.get('listlevel')
    nrmax = session.get('nrmax')
    seconds = nrmax // 2
    answer = []
    level = session.get('level')

    if request.method == 'POST' and 'answer' in request.form:
        for i in request.form.get('answer'):
            answer.append(int(i))

        if answer == listlevel[level]:
            level = level + 1
            session['level'] = level
        else:
            level = -1
            session['level'] = level

    return render_template('memorize.html', listlevel=listlevel, seconds=seconds, level=level, user = user)


# Phonebook

# Homepage
@app.route('/phonebook', methods=['GET', 'POST'])
def phonebook():
    user = session.get('user', None)
    return render_template('phonebook.html', user = user)


# Add contact Page
@app.route('/add', methods=['GET', 'POST'])
def add():
    user = session.get('user', None)
    data = ''

    cursor.execute(f"SELECT USER_ID FROM User WHERE USER_NICKNAME = '{user}';")
    for row in cursor:
        for element in row:
            userid = element

    if request.method == 'POST' and 'name' in request.form:
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        nickname = request.form.get('nickname')
        company = request.form.get('company')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        birthday = request.form.get('birthday')
        data = (userid, name, lastname, nickname, company, phone, email, address, birthday)

        insert = ("""INSERT INTO Contact (USER_ID,CONTACT_NAME, CONTACT_LASTNAME, CONTACT_NICKNAME, CONTACT_COMPANY,
                     CONTACT_PHONE, CONTACT_EMAIL, CONTACT_ADDRESS, CONTACT_BIRTHDAY)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""")

        cursor.execute(insert, data)
        conn.commit()

    return render_template('add.html', data=data, user = user)

#Search Contact Page
@app.route('/search', methods=['GET', 'POST'])
def search():
    user = session.get('user', None)
    search_by = []
    result = []

    cursor.execute(f"SELECT USER_ID FROM User WHERE USER_NICKNAME = '{user}';")
    for row in cursor:
        for element in row:
            userid = element

    if request.method == 'POST' and 'name' or 'lastname' or 'phone' in request.form:
        name = request.form.get('name')
        lastname = request.form.get('lastname')
        phone = request.form.get('phone')
        search_by = [name, lastname, phone]
        contact = ['CONTACT_NAME', 'CONTACT_LASTNAME', 'CONTACT_PHONE']

    for element in search_by:
        if element:
            cursor.execute(f"""SELECT CONTACT_NAME, CONTACT_LASTNAME, CONTACT_NICKNAME, CONTACT_COMPANY, CONTACT_PHONE,
                               CONTACT_EMAIL, CONTACT_ADDRESS, CONTACT_BIRTHDAY FROM Contact
                               WHERE {contact[search_by.index(element)]} LIKE '%{element}%'
                               AND USER_ID = {userid}""")
            for row in cursor:
                result.append(row)

    return render_template('search.html', result=result, user = user)


#Delete Contact Page
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    user = session.get('user', None)
    search_by = []
    result = []
    confirm = False

    cursor.execute(f"SELECT USER_ID FROM User WHERE USER_NICKNAME = '{user}';")
    for row in cursor:
        for element in row:
            userid = element

    if request.method == 'POST' and 'name' in request.form:
        name = request.form.get('name')
        phone = request.form.get('phone')
        search_by = [name, phone]
        contact = ['CONTACT_NAME', 'CONTACT_PHONE']

    for element in search_by:
        if element:
            cursor.execute(f"""SELECT CONTACT_NAME, CONTACT_LASTNAME, CONTACT_NICKNAME, CONTACT_COMPANY, CONTACT_PHONE,
                               CONTACT_EMAIL, CONTACT_ADDRESS, CONTACT_BIRTHDAY FROM Contact
                               WHERE {contact[search_by.index(element)]} LIKE '%{element}%'
                               AND USER_ID = {userid}""")

            for row in cursor:
                result.append(row)


    if request.method == 'POST' and 'name_confirm' and 'phone_confirm' in request.form:
        name_confirm = request.form.get('name_confirm')
        phone_confirm = request.form.get('phone_confirm')

        cursor.execute(f"""DELETE FROM Contact
                           WHERE CONTACT_NAME = '{name_confirm}'
                           AND CONTACT_PHONE = '{phone_confirm}'
                           AND USER_ID = {userid};""")
        conn.commit()
        confirm = True


    return render_template('delete.html', result=result, confirm=confirm, user=user)
