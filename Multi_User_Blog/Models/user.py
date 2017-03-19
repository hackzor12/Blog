from google.appengine.ext import db
from functions import make_secure_val, check_secure_val, blog_key, make_salt, make_pw_hash, valid_pw, valid_username, valid_password, valid_email
#User Object 
#####################################################################################################################################
def users_key(group = 'default'):
    return db.Key.from_path('users', group)
#The user object which inherits the database model 
class User(db.Model):
	#class attributes that represent fields in the db

	#name is the id the user signed up with, the user id for us
    name = db.StringProperty(required = True)

    #password hash is a tuple with the salt in the 
    #0th position and the password + salt hashed using sha256
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

	#A class methethod, the first parameter passed to a class method is always an instance of the class
	#This defines a means of interacting with the database without directly making calls in our html handlers

	#Return the user object when given the id of that user
    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

	#return the user object when give the name of that user     
    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

   	#returns a user object with instance level variables set to the input so it can be saved after a user succesfully registers
    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)
    #retrieves the user object given the name and insures the provided password is correct then returns the user object
    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u
