from bloghandler import BlogHandler
from google.appengine.ext import db
from Models import User, Post, Comment, make_secure_val,check_secure_val, blog_key, make_salt, make_pw_hash, valid_pw, valid_username, valid_password, valid_email
#Comment Handlers
#####################################################################################################################################
class NewComment(BlogHandler):
    #Make sure the user is authentic 
    def get(self,post_id):
        if not self.user:
            self.redirect('/register') 
        else:
            self.render('new-comment.html')
    def post(self,post_id):
        if not self.user:
            self.redirect('/blog')
        #Get the associated post        
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        content = self.request.get('content')
        #if the post does not exist we cannot add a comment to it
        if post and content:
            #save the comment with the id of the post it is associated with
            c = Comment(post=post_id,content=content, author=self.user.name)
            c.put()
            self.redirect('/blog/' + post_id)
        else:
            error = "content please!"
            self.render("new-comment.html", content=content, error=error,post_id=post_id)   

class DeleteComment(BlogHandler):
    def get(self, post_id, comment_id):
        #User must be logged in
        if not self.user:
            self.redirect('/register') 
        else: 
            #Get the associated post        
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            #If the post does not exist we cannot delete the comment
            if post:
                comment = None
                #See if the comment we are trying to delete belongs to the post
                for c in post.comments:
                    if comment_id == str(c.key().id()):
                        comment = c
                #If the comment exists we can delete it
                if comment != None:
                    #If the comment is owned by the user we can delete it
                    if comment.author == self.user.name:
                        comment.delete()
                        self.redirect('/blog/' + post_id)
                    else:
                        message = 'You cannot delete comments that other\'s made'
                        self.render('blog-error.html',message=message)
                else:
                    message = 'Invalid Comment!'
                    self.render('blog-error.html',message=message) 
            else:
                message = 'Invalid Post!'
                self.render('blog-error.html',message=message)                 

class EditComment(BlogHandler):
    def get(self,post_id,comment_id):
        #User must be logged in
        if not self.user:
            self.redirect('/register') 
        else: 
            #Get the associated post        
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            #The post must exist for us to be able to edit the comment
            if post:
                comment = None
                #See if the comment we are trying to delete belongs to the post
                for c in post.comments:
                    if comment_id == str(c.key().id()):
                        comment = c
                #If we find a post and the user is the author render the edit page
                if comment != None:
                    if comment.author == self.user.name:
                        content = comment.content
                        self.render('edit-comment.html',content=content,post_id=post_id)
                    else:
                        message = 'You cannot edit comments that other\'s made'
                        self.render('blog-error.html',message=message) 
                else:
                    message = 'Invalid Comment!'
                    self.render('blog-error.html',message=message) 
            else:
                message = 'Invalid Post!'
                self.render('blog-error.html',message=message)                                 
    def post(self,post_id,comment_id):
            if not self.user:
                self.redirect('/register')
            else:
                #Get the associated post        
                key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                post = db.get(key)
                if post:
                    comment = None
                    #See if the comment we are trying to delete belongs to the post
                    for c in post.comments:
                        if comment_id == str(c.key().id()):
                            comment = c
                    if comment != None:
                        if comment.author == self.user.name:
                            #get the changes from the page
                            content = self.request.get('content')
                            comment.content = content
                            #save the post in the db
                            comment.put()
                            self.redirect('/blog/'+post_id)
                        else:
                            message = 'You cannot edit the posts of others!'
                            self.render('blog-error.html',message=message)  
                    else:
                        message = 'Invalid Comment!'
                        self.render('blog-error.html',message=message) 
                else:
                    message = 'Invalid Post!'
                    self.render('blog-error.html',message=message)   
