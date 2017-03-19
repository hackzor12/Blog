from google.appengine.ext import db
import os
import webapp2
import jinja2
from comment import Comment 
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

#Post Object 
##################################################################################################################################### 
#Defines the Post object using the db model
#Renders the content of the post to the page
def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

class Post(db.Model):
    #instance level attributes of a post
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    created_by = db.TextProperty(required=True)
    num_likes = db.IntegerProperty(required=True)
    liked_by = db.ListProperty(str,required=True)

    #rendes a provides post object into html
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

    @classmethod
    def by_id(cls, post_id):
        return User.get_by_id(uid, parent = users_key())

    @property
    def comments(self):
        return Comment.all().filter( "post = ", str(self.key().id())) 