import os
import webapp2
import jinja2
from Models import User, Post, Comment, make_secure_val,check_secure_val, blog_key, make_salt, make_pw_hash, valid_pw, valid_username, valid_password, valid_email
#This gets the directory that the HTML templates are stored in
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

#Instatiate the templating engine environment
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

#The jinja environment renders templates and passes them parameters which we can 
#manipulate using python if we choose the correct syntax in our html template
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Main Blog Handler
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