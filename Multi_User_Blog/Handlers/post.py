from bloghandler import BlogHandler, render_str
from google.appengine.ext import db
from Models import User, Post, Comment, make_secure_val,check_secure_val, blog_key, make_salt, make_pw_hash, valid_pw, valid_username, valid_password, valid_email
#Post Handlers
#####################################################################################################################################
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
            username = self.user.name
            p = Post(parent = blog_key(), subject = subject, content = content, created_by=username, num_likes=0, liked_by=[])
            p.put()
            self.redirect('/blog' )
        else:
            #If not render an error asking for the subject and content
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

#Handler for liking a post
class LikePost(BlogHandler):
    #Only logged in users can like posts
    def get(self,post_id):
        if not self.user:
            self.redirect('/register') 
        else:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            #get the post object from the db
            post = db.get(key)
            if post:
                if post.created_by == self.user.name:
                    message = 'You cannot like your own post!'
                    self.render('blog-error.html',message=message)
                else:
                    if self.user.name in post.liked_by:
                        message = 'You cannot like a post twice!'
                        self.render('blog-error.html',message=message)  
                    else:
                        #increment the number of likes by 1 and record the person who liked it
                        post.num_likes = post.num_likes + 1
                        post.liked_by.append(self.user.name)
                        post.put()
                        self.redirect('/blog/'+post_id)
            else:
                message = 'Post does not Exist!'
                self.render('blog-error.html',message=message) 


                

class EditPost(BlogHandler):
    def get(self,post_id):
        if not self.user:
            self.redirect('/register') 
        else:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            #get the post object from the db
            post = db.get(key)
            #if the user owns the post display the edit page
            if self.user.name == post.created_by:
                content = post.content
                subject = post.subject
                self.render('edit-post.html',subject=subject, content=content,post_id=post_id)
            else:
                #otherwise tell them they can't edit the post
                message = 'You cannot edit other user\'s posts'
                self.render('blog-error.html',message=message)                 


    def post(self,post_id):
            if not self.user:
                self.redirect('/register')
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            #get the post object from the db
            post = db.get(key) 
            #get the changes from the page
            subject = self.request.get('subject')
            content = self.request.get('content')
            post.subject = subject
            post.content = content
            #save the post in the db
            post.put()
            self.redirect('/blog')
             


class DeletePost(BlogHandler):
    def get(self,post_id):
            if not self.user:
                self.redirect('/register')        
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            #get the post object from the db
            post = db.get(key)
            #if the user owns the post delete it
            if self.user.name == post.created_by:
                post.delete()
                self.redirect('/blog')
            #otherwise tell them they can't delete the post
            else:
                message = 'You cannot delete other user\'s posts'
                self.render('blog-error.html',message=message)
                
