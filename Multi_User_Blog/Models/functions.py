import hmac
import re
import random
import hashlib
from string import letters
from google.appengine.ext import db
#Cookie Validation
####################################################################################################################################
#This is our 'private key used to validate cookies'
secret = 'supersecretsecret'

#This function returns username | hash of (username+private key)
#We can compare this to the cookie to see if a post is performed by a genuine user
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

#If the username provided by the cookie and the hash following the pipe 
#equates to what we expected return the username otherwise return nothing
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

#Returns the PK of a user given their username
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

#Password Validation
#####################################################################################################################################

#This function returns 5 random letters 
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

#This function makes a password hash by mixing the 5 random letters created above or passed in to the function
#with the username and password and hashing it using sha256 
def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

#This function splits the salt from the password hash that it recieves then it uses the name and password to 
#create the hash and compare it to the hash passed in, this protects from rainbow table attacks
def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

#User Validation
#####################################################################################################################################
#Compiled regex expressions used to validate registration input
#Functions that use the compiled regex to validate each registration input

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASS_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)