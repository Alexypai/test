from flask import Flask, render_template, request, redirect, url_for,session, abort,flash
import sqlite3
import os

#Variable corresponding to the database of the application
db_local = 'BDD_python_project.db'

app = Flask(__name__)

norepeat = []

app.secret_key = os.urandom(12)

#Application Login Page
@app.route('/', methods = ['GET', 'POST'])
def log():
    session['logged_in'] = True
    if request.method == 'GET':
        return render_template('Pages/login.html')
    else:
        log_user = (
            request.form['Login']
        )
        password_user = (
            request.form['Password']
        )
        connexion(log_user, password_user)
        v = connexion(log_user, password_user)
    if v == True:
        return render_template("Pages/Index.html")
    else:
        msgn = msgE()
        return render_template('Pages/login.html',msgn = msgn)

def msgE():
    msgV = "Mauvais User name ou Password !"
    return msgV

def msgF():
    msgV = "Utilisateur créé !"
    return msgV

def connexion(log_user, password_user):
    connect = sqlite3.connect(db_local)
    c = connect.cursor()
    c.execute("SELECT login, password FROM logs WHERE login=? AND password=?",(log_user,password_user))
    id = c.fetchall()
    if not id:
        validation = False
    else:
        id2 = id[0]
        idu = id2[0]
        idp = id2[1]
        connect.close()
        #Verification of user input data
        if ((password_user == idp) and (log_user == idu)):
            validation = True
        else:
            validation = False
    return(validation)

#Create a new user
@app.route('/createUser', methods = ['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('Pages/nouvelUtilisateur.html')
    else:
        new_log_user = (
            request.form['newLogin']
        )
        new_password_user = (
            request.form['newPassword']
        )
        newUser(new_log_user, new_password_user)
        msgb = msgE()
        return render_template('Pages/login.html',msgb = msgb)

def newUser(new_log_user,new_password_user):
    connect = sqlite3.connect(db_local)
    c = connect.cursor()
    c.execute("INSERT INTO logs (login, password) VALUES (?,?)",(new_log_user,new_password_user))
    connect.commit()
    connect.close()

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return render_template('Pages/login.html')

#Application index with setting the id_project variable to zero when a user has finished creating a team
@app.route('/Index')
def index():
    id_Project = None
    print(id_Project)
    return render_template('Pages/Index.html')

@app.route('/Annuaire')
def Annuaire():
    return render_template('Pages/Annuaire.html')

#returns the team creation page where the user must enter the project name
@app.route('/Crea', methods = ['GET','POST'])
def Crea():
    if request.method == 'GET':
        return render_template('Pages/Création_equipe.html')
    else:
        new_team = (
            request.form['team_name']
        )
        insert_team(new_team)
        return redirect(url_for('choice'))

#Function allowing the addition of the named project in the team creation page and assigning an id to this new project
def insert_team(new_team):
    connect = sqlite3.connect(db_local)
    c = connect.cursor()
    sql_team_write = 'INSERT INTO PROJECTS (PROJECTS_name) VALUES (?)'
    c.execute(sql_team_write,[new_team])
    connect.commit()
    c2 = connect.cursor()
    c2.execute("SELECT PROJECTS_ID FROM PROJECTS WHERE PROJECTS_name=?",(new_team,))
    x = c2.fetchone()
    global id_Project
    id_Project = x[0]
    connect.close()

#Display of the choice page when the user has validated the name of the team
#Thanks to this page the user can adds members to the team previously created
#Whenever an employee has been added to a team the page will regenerate,
#To leave this page, click on the end creation of a team that returns to the application index.
@app.route('/choice', methods = ['GET','POST'])
def choice():
    if request.method == 'GET':
        return render_template('Pages/choice.html')
    else:
        time_user = (
            request.form['TIME']
        )
        role_user = (
            request.form['ROLES']
        )
        insert_user(id_Project,time_user, role_user)
        msgv = msgA()
        return render_template('Pages/choice.html',msgv=msgv)

#Function allowing the addition of an employee with the most available time in the team previously created, according to the role chosit by the user
#When added, this function inserts in the USERS_BY_PROJECT table: the employee id with the most time available, the project id previously created and the time it was assigned to it
def insert_user(id_Project,time_user, role_user):
    connect = sqlite3.connect(db_local)
    c = connect.cursor()
    c.execute("SELECT USERS_BY_PROJECT.USERS_ID FROM (RESPONSIBILITIES INNER JOIN (USERS INNER JOIN (SELECT USERS_BY_PROJECT.USERS_ID, Sum(USERS_BY_PROJECT.TIME) AS SBU FROM USERS LEFT JOIN USERS_BY_PROJECT ON USERS.USERS_ID = USERS_BY_PROJECT.USERS_ID GROUP BY USERS_BY_PROJECT.USERS_ID, USERS.TAUX_HORAIRE)  AS SU ON USERS.USERS_ID = SU.USERS_ID) ON RESPONSIBILITIES.Responsibilities_ID = USERS.Responsibilities_ID) LEFT JOIN USERS_BY_PROJECT ON USERS.USERS_ID = USERS_BY_PROJECT.USERS_ID GROUP BY USERS_BY_PROJECT.USERS_ID, [USERS].[TAUX_HORAIRE]-SU.SBU, RESPONSIBILITIES.Responsibilities_Name HAVING (((RESPONSIBILITIES.Responsibilities_Name)=?)) ORDER BY [USERS].[TAUX_HORAIRE]-SU.SBU DESC;",(role_user,))
    x = c.fetchall()
    x2 = x[0]
    user_select = x2[0]
    c2 = connect.cursor()
    c2.execute("INSERT INTO USERS_BY_PROJECT (TIME,USERS_ID,PROJECTS_ID) VALUES (?,?,?)",(time_user,user_select,id_Project))
    connect.commit()
    connect.close()

def msgA():
    msgV = "Employé Ajouté ! Vous pouvez continuer ou valide votre equipe en cliquant sur fin création d'equipe"
    return msgV

def msgD():
    msgV = "Equipe supprimé ! Vous pouvez continuer ou utilisé le menu ci dessus pour d'autres fonctionnalités"
    return msgV


#view all current projects and users linked to the different projects
@app.route('/Equipe')    
def Equipe():
    Equipe = query_equipe()
    Users = query_users()
    return render_template('Pages/Equipe_cree.html',Equipe=Equipe,Users=Users)

#Select all data from the PROJETCS tables
def query_equipe():
    connect = sqlite3.connect(db_local)
    c = connect.cursor()
    c.execute("SELECT * FROM PROJECTS WHERE PROJECTS_ID > 3")
    Users = c.fetchall()
    connect.close()
    return Users

#Selects all data from the USERS table
def query_users():
    connect = sqlite3.connect(db_local)
    c = connect.cursor()
    c.execute("SELECT USERS_BY_PROJECT.USERS_ID,USERS.USERS_NAME,USERS_BY_PROJECT.PROJECTS_ID,PROJECTS.PROJECTS_name,USERS_BY_PROJECT.TIME FROM PROJECTS INNER JOIN (USERS INNER JOIN USERS_BY_PROJECT ON USERS.USERS_ID = USERS_BY_PROJECT.USERS_ID) ON PROJECTS.PROJECTS_ID =  USERS_BY_PROJECT.PROJECTS_ID ")
    Equipe = c.fetchall()
    connect.close()
    return Equipe


#Allows the user to delete a project according to the project id
@app.route('/Delete', methods = ['GET','POST'])
def Delete():
    if request.method == 'GET':
        return render_template('Pages/Delete.html')
    else:
        team_id = (
            request.form['id']
        )
        if (team_id == "3"):
            msg = "Impossible de suprrimé cette valeur"
            return render_template('Pages/Delete.html',msg=msg)
        else:
            delete_team(team_id)
            msg = msgD()
            return render_template('Pages/Delete.html',msg=msg)

#Allows the deletion of a project in the PROJECT table
def delete_team(team_id):
    connect = sqlite3.connect(db_local)
    c = connect.cursor()
    c.execute("DELETE FROM PROJECTS WHERE PROJECTS_ID = ?",(team_id,))
    connect.commit()
    c.execute("DELETE FROM USERS_BY_PROJECT WHERE PROJECTS_ID = ?",(team_id,))
    connect.commit()
    connect.close()

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=4000)
