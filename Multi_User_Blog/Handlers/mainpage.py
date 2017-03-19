import os
import webapp2
import jinja2
from Models import User, Post, Comment, make_secure_val,check_secure_val, blog_key, make_salt, make_pw_hash, valid_pw, valid_username, valid_password, valid_email
from bloghandler import BlogHandler

class BlogFront(BlogHandler):
	#gets all posts and renders them in the body of the page
    def get(self):
		if not self.user:
			self.redirect('/login')
		else:
		#gets all posts and renders them in the body of the page
			posts = greetings = Post.all().order('-created')
			self.render('front.html', posts = posts)
