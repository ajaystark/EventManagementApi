import logging
from flask import Flask,render_template,request,json,Response,jsonify,redirect,send_file
from flask_mysqldb import MySQL
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime

file_handler= logging.FileHandler('Server.log')

app = Flask(__name__,template_folder="templates",static_folder='static')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO) 


load_dotenv(find_dotenv())
DB_NAME=os.getenv("DB_NAME")
DB_USERNAME=os.getenv("DB_USERNAME")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOST=os.getenv("DB_HOST")

app.config['MYSQL_HOST'] = DB_HOST
app.config['MYSQL_USER'] = DB_USERNAME
app.config['MYSQL_PASSWORD'] = DB_PASSWORD
app.config['MYSQL_DB'] = DB_NAME
mysql = MySQL(app)


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status':404,
        'message':'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp

@app.route("/createEvent",methods=['POST'])
def createEvent():
    if request.method=="POST":
        try:
            if len(request.form)!=0:
                data=request.form
            else:
                data=request.json
            
            app.logger.info('Data Received {}'.format(data))

            try:
                title=data['title'],
                description=data['description'],
                image=request.files['image'],
                date=data['date'],
                location=data['location'],
                allowed_attendees=data['allowed_attendees'],
                waitlist=data['waitlist'],
                startTime=data['startTime'],
                endTime=data['endTime']
            except Exception as ee:
                
                app.logger.info('Error occured in createEvent : Missing Parameters')

                return {
                    'code':2,
                    'Msg':'MissingParameters'
                }
            print(title)
            filename=image[0].filename+'_'+title

            print(filename)
            cursor=mysql.connection.cursor()
            
            q='''INSERT INTO event (title, description, image, date, location, allowed_attendees, waitlist, startTime, endTime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);'''

            cursor.execute(q,(title, description, filename, date, location, allowed_attendees, waitlist, startTime, endTime))
            

            image[0].save(os.path.join('images', filename))

            mysql.connection.commit()
            
            app.logger.info('Event {} Added Successfully'.format(title))

            return {
                'code':1,
                'Msg':'Added Successfully'
            }
        except Exception as e:
            app.logger.info('Error occured in createEvent {}'.format(e))
            return {
                'code':0,
                'Msg':'SomethingWentWrong'
            }
    else:
        return {
            'code':0,
            'Msg':'InvalidRequest'
        }

        
@app.route("/DeleteEvent",methods=['POST'])
def DeleteEvent():
    if request.method=="POST":
        try:
            if len(request.form)!=0:
                data=request.form
            else:
                data=request.json

            try:
                title=data['title']

            except Exception as ee:
                
                app.logger.info('Error occured in DeleteEvent : Missing Parameters')

                return {
                    'code':2,
                    'Msg':'MissingParameters'
                }

            app.logger.info('Title Received {}'.format(title))

            cursor=mysql.connection.cursor()

            q='''select id from event where title='{}';'''.format(title)
            cursor.execute(q)
            record=cursor.fetchone()

            if record!=None:
                q='''DELETE FROM `event` WHERE (`id` = %s);'''
                cursor.execute(q,(record))
                mysql.connection.commit()
            else:
                return {
                    'code':3,
                    'Msg':'TitleNotFound'
                }
            app.logger.info('{} deleted'.format(title))
            return {
                'code':1,
                'Msg':'Deleted Successfully'
            }

        except Exception as e:
            app.logger.info('Error occured in DeleteEvent {}'.format(e))
            return {
                'code':0,
                'Msg':'SomethingWentWrong'
            }
    else:
        return {
            'code':0,
            'Msg':'InvalidRequest'
        }

@app.route("/createUser",methods=['POST'])
def createUser():
    if request.method=="POST":
        try:
            if len(request.form)!=0:
                data=request.form
            else:
                data=request.json

            try:
                app.logger.info('Data Received {}'.format(data))

                name=data['name']
                email=data['email']

            except Exception as ee:
                
                app.logger.info('Error occured in createUser : Missing Parameters')

                return {
                    'code':2,
                    'Msg':'MissingParameters'
                }

            cursor=mysql.connection.cursor()            
            q='''INSERT INTO `user` (`name`, `email`) VALUES (%s, %s);'''
            cursor.execute(q,(name,email))
            mysql.connection.commit()

            app.logger.info('{} added '.format(name))

            return {
                'code':1,
                'Msg':'User Added Successfully'
            }

        except Exception as e:
            app.logger.info('Error occured in createUser {}'.format(e))
            return {
                'code':0,
                'Msg':'SomethingWentWrong'
            }
    else:
        return {
            'code':0,
            'Msg':'InvalidRequest'
        }
@app.route("/DeleteUser",methods=['POST'])
def DeleteUser():
    if request.method=="POST":
        try:
            if len(request.form)!=0:
                data=request.form
            else:
                data=request.json

            try:
                email=data['email']

            except Exception as ee:
                
                app.logger.info('Error occured in DeleteUser : Missing Parameters')

                return {
                    'code':2,
                    'Msg':'MissingParameters'
                }

            app.logger.info('email Received {}'.format(email))

            cursor=mysql.connection.cursor()

            q='''select id from user where email='{}';'''.format(email)
            cursor.execute(q)
            record=cursor.fetchone()

            if record!=None:
                q='''DELETE FROM `user` WHERE (`id` = %s);'''
                cursor.execute(q,(record))
                mysql.connection.commit()
            else:
                return {
                    'code':3,
                    'Msg':'UserNotFound'
                }
            app.logger.info('{} deleted'.format(email))
            return {
                'code':1,
                'Msg':'Deleted Successfully'
            }

        except Exception as e:
            app.logger.info('Error occured in DeleteUser {}'.format(e))
            return {
                'code':0,
                'Msg':'SomethingWentWrong'
            }
    else:
        return {
            'code':0,
            'Msg':'InvalidRequest'
        }

@app.route("/getUpcomingEvents",methods=['GET'])
def getUpcomingEvents():
    try:
        currentTime=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor=mysql.connection.cursor()

        q='''select title,description,date,location,image from event where date>'{}';'''.format(currentTime)

        cursor.execute(q)
        records=cursor.fetchall()

        data=[]

        for r in records:
            data.append({
                'title':r[0],
                'description':r[1],
                'date':r[2],
                'location':r[3],
                'imageUrl':'/getImage?name='+r[4]
            })

        return {
            'code':1,
            'data':data
        }
    except Exception as e:
        app.logger.info('Error occured in getUpcomingEvents {}'.format(e))
        return {
            'code':0,
            'Msg':'SomethingWentWrong'
        }
        
@app.route("/getImage",methods=['GET'])
def getImage():
    try:
        
        cursor=mysql.connection.cursor()
        name=request.args.get('name')

        return send_file('images/'+name)

    except Exception as e:
        app.logger.info('Error occured in getImage {}'.format(e))
        return {
            'code':0,
            'Msg':'SomethingWentWrong'
        }
if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0")