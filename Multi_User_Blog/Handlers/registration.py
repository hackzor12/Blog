from bloghandler import BlogHandler
from Models import User, Post, Comment, make_secure_val,check_secure_val, blog_key, make_salt, make_pw_hash, valid_pw, valid_username, valid_password, valid_email
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