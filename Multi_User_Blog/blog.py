from Models import User, Comment,Post
from Handlers import BlogHandler , Welcome, Signup, Register, Login, Logout, PostPage, NewPost, LikePost, EditPost, DeletePost, NewComment, DeleteComment, EditComment, BlogFront
import webapp2

#Map URLS to HTML handlers
#####################################################################################################################################
app = webapp2.WSGIApplication([('/', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+)/like', LikePost),
                               ('/blog/([0-9]+)/newcomment', NewComment),
                               ('/blog/([0-9]+)/update', EditPost),
                               ('/blog/([0-9]+)/delete', DeletePost),
                               ('/blog/([0-9]+)/([0-9]+)/update', EditComment),
                               ('/blog/([0-9]+)/([0-9]+)/delete', DeleteComment),                          
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True) 



