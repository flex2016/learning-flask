from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User, Place
from forms import SignupForm, LoginForm, AddressForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://pqtrpiiupjgvaw:a09995e2be6ef6d036e8a3bff8e8e4ec05b90b2615e9c45d324190345e6c2254@ec2-184-72-248-8.compute-1.amazonaws.com:5432/db94pmfe41nn0n'
#postgres://pqtrpiiupjgvaw:a09995e2be6ef6d036e8a3bff8e8e4ec05b90b2615e9c45d324190345e6c2254@ec2-184-72-248-8.compute-1.amazonaws.com:5432/db94pmfe41nn0n

#postgresql://postgres:flex@localhost/learningflask  to run locally
db.init_app(app)

app.secret_key = "development-key"




@app.route("/")
def index():
  return render_template("index.html")

@app.route("/about")
def about():
  return render_template("about.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
  if 'email' in session: #if user already logged in he can't access the signup page
    return redirect(url_for('home'))

  form = SignupForm()

  if request.method == "POST":
    if form.validate() == False:
      return render_template('signup.html', form=form)
    else:
      newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
      db.session.add(newuser)
      db.session.commit()

      session['email'] = newuser.email  #creates new session for the user
      return redirect(url_for('home'))

  elif request.method == "GET":
    return render_template('signup.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
  if 'email' in session: #if user already logged in he can't access the login page
    return redirect(url_for('home'))

  form = LoginForm()

  if request.method == "POST":
    if form.validate() == False:
      return render_template("login.html", form=form)
    else:
      email = form.email.data
      password = form.password.data

      user = User.query.filter_by(email=email).first() #check if user exist in database
      if user is not None and user.check_password(password):
        session['email'] = form.email.data
        return redirect(url_for('home'))
      else:
        return redirect(url_for('login'))

  elif request.method == 'GET':
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
  session.pop('email', None)
  return redirect(url_for('index'))

@app.route("/home", methods=["GET", "POST"])
def home():
  if 'email' not in session:
    return redirect(url_for('login'))

  form = AddressForm()

  places = []
  my_coordinates = (37.4221, -122.0844)

  if request.method == 'POST':
    if form.validate() == False:
      return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)
    else:
      # get the address
      address = form.address.data

      # query for places around it
      p = Place()
      my_coordinates = p.address_to_latlng(address)
      places = p.query(address)

      # return those results
      return render_template('home.html', form=form, my_coordinates=my_coordinates, places=places)

  elif request.method == 'GET':
    return render_template("home.html", form=form, my_coordinates=my_coordinates, places=places)

if __name__ == "__main__":
  app.run(debug=False)
