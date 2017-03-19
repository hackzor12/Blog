from google.appengine.ext import db
#Comment Object 
#####################################################################################################################################
#This is a comment object that has the PK of a post as its FK
class Comment(db.Model):
    post = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    author = db.StringProperty(required=True)