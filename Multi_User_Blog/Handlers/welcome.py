from bloghandler import BlogHandler
from Models import User, Post, Comment, make_secure_val,check_secure_val, blog_key, make_salt, make_pw_hash, valid_pw, valid_username, valid_password, valid_email
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