import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db


#This gets the directory that the HTML templates are stored in
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

#Instatiate the templating engine environment
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

#The jinja environment renders templates and passes them parameters which we can 
#manipulate using python if we choose the correct syntax in our html template
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


#This is our 'private key used to validate cookies'
secret = 'supersecretsecret'

#Cookie Validation
####################################################################################################################################

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

#Blog Handler
#####################################################################################################################################
#The main blog handler class, other page handler inherit from this guy
class BlogHandler(webapp2.RequestHandler):
	#This allows us to write input and html directly to the page
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    #Jinja uses an environment to dynamically render html templates, this adds the user as a parameter
    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    #This adds the kw arguments we want to pass to jinja
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #This gets the secure cookie described in the function above and sets it for the user
    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    #Retrieve the cookie, return it and an indication of its authenticity
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    #Once the user logs in set the cookie so it can be used to verify if the user is genuine as they move from page to page
    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    #Clear the users cookie 
    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    #Overrides the __init__ function of webapp2 request handler and gets the user id from the secure cookie, 
    #Remember nothing is returned if the user is invalid
    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
#####################################################################################################################################

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

#User Object / Login/Registration/Logout Handlers
#####################################################################################################################################

#db is a google app extension that represents a database object we can interact with the database through

 
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

#User Validation
#####################################################################################################################################
#Compiled regex expressions used to validate registration input
#Functions that use the compiled regex to validate each registration input

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASS_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)

#Registration/Login/Logout HTML Handlers
#####################################################################################################################################

#Signup inherits from Bloghandler, renders the register page
class Signup(BlogHandler):
    def get(self):
        self.render("register.html")


    def post(self):
    	#Set the value of the username, password and email to what the user entered into the form
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        #Build the params to pass back to the form in case the user inputs fields with errors
        params = dict(username = self.username,
                      email = self.email)

        #Validate the user input
        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        #If there is an error render the register page with it
        if have_error:
            self.render('register.html', **params)
        else:
            self.done()


#Register inherits from signup, renders the registration page
class Register(Signup):
	#After the signup is complete check to see if the user is a duplicate
    def done(self):
        u = User.by_name(self.username)
        if u:
        	#if the user is a dupe, tell the user and render the registration page again
            msg = 'That user already exists.'
            self.render('register.html', error_username = msg)
        else:
        	#If the user is valid then build a user object with the given parameters
            u = User.register(self.username, self.password, self.email)
            #Save the user in the db
            u.put()

            #Set the users cookie data
            self.login(u)
            #Send the user to the welcome page
            self.redirect('/?username=' + self.username)

#Inherits from Bloghandler 
class Login(BlogHandler):
    def get(self):
    	#renders the login page
        self.render('login.html')

    def post(self):
    	#Set the username and password to the user input
        username = self.request.get('username')
        password = self.request.get('password')

        #Set the users cookie, and retrieve the user object
        u = User.login(username, password)

        #If the user object is null it means the validation failed
        if u:
        	#Set the users cookie data
            self.login(u)
            #Send the user to the welcome page
            self.redirect('/?username=' + username)
        else:
        	#Tell the user they made a mistake and render the login page again
            msg = 'Invalid login'
            self.render('login.html', error = msg)

#Inherits from Bloghandler 
class Logout(BlogHandler):
    def get(self):
    	#Clear the users cookie
        self.logout()
        #Redirect user to registration page
        self.redirect('/signup')

#Wecome page
#####################################################################################################################################
class Welcome(BlogHandler):
	#When a user succesfully logs in or registers, render a page that welcomes them using their username
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
        	#if the username does not exist redirect the user to the registration page
            self.redirect('/signup')

#Blog stuff
#####################################################################################################################################

#Returns the PK of a user given their username
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

#Defines the Post object using the db model
class Post(db.Model):
	#instance level attributes of a post
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    created_by = db.TextProperty(required=True)
    num_likes = db.IntegerProperty(required=True)
    liked_by = db.ListProperty(str)

    #rendes a provides post object into html
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

#Main page of the blog
class BlogFront(BlogHandler):
	#gets all posts and renders them in the body of the page
    def get(self):
		if not self.user:
			self.redirect('/login')
		else:
		#gets all posts and renders them in the body of the page
			posts = greetings = Post.all().order('-created')
			self.render('front.html', posts = posts)

#Page for a particular post 
class PostPage(BlogHandler):
    def get(self, post_id):
		if not self.user:
			self.redirect('/login')
		else:
			#Gets a post object's PK given post_id and FK which is the user's PK
			key = db.Key.from_path('Post', int(post_id), parent=blog_key())
			#get the post object from the db
			post = db.get(key)

			#if not found show an error on the screen
			if not post:
			    self.error(404)
			    return

			#render the post page for a specific post
			self.render("permalink.html", post = post)
    def post(self,post_id):
    	key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        #get the post object from the db
        post = db.get(key)


#Page for creating a new blog post
class NewPost(BlogHandler):
	#Make sure the user is authentic 
    def get(self):
		if not self.user:
			self.redirect('/register')
		else:
			self.render("newpost.html")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        #If the user inputed a subject and contect
        if subject and content:
        	#Create the post object and save it in the db
            p = Post(parent = blog_key(), subject = subject, content = content, created_by=self.username, num_likes=0, liked_by=[])
            p.put()
            self.redirect('/blog' )
        else:
        	#If not render an error asking for the subject and content
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class LikePost(BlogHandler):
	def get(self):
		if not self.user:
			self.redirect('/register')
		else:
			key = db.Key.from_path('Post',int('post_id'),parent=blog_key())
			p = db.get(key)
			post_owner = p.created_by
			post_liker = self.username

			if post_owner == post_liker:
				self.error(404)
				return
			else:
				p.num_likes =p.num_likes + 1
				p.put()
				self.redirect()





#Map URLS to HTML handlers
#####################################################################################################################################
app = webapp2.WSGIApplication([('/', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+)/like)', LikePost),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)



