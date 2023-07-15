from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_login import current_user


# Create a Flask application instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://guard:Abinitio1968!@localhost:3306/justice_guarddb'
app.config['SECRET_KEY'] = 'my_secret_key_5050'


db = SQLAlchemy(app)


# Initialize LoginManager and configure it
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Define the User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


# Define the Report model
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    date_reported = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('reports', lazy=True))

    def __repr__(self):
        return f"<Report {self.title}>"


@app.route('/')
def landing():
    return render_template('landing.html')


# Define a route for the homepage ('/')
@app.route('/home')
def home():
    return render_template('home.html')


# Define the About route
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')
    

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # Process the contact form submission
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    
    # Add your logic here to handle the submitted data

    return "Thank you for contacting us!"


# Define the report creation route
@app.route('/create_report', methods=['GET', 'POST'])
@login_required
def create_report():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']

        # Create a new Report object
        report = Report(title=title, description=description, location=location, user=current_user)

        # Save the report to the database
        db.session.add(report)
        db.session.commit()

        return redirect(url_for('view_reports'))
    else:
        return render_template('create_report.html')




# Define the logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Define the login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password are valid
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # Login the user
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            # Invalid credentials, show an error message
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')


# Define the registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Create a new user
        new_user = User(username=username, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    else:
        return render_template('register.html')


# Create the database tables within the application context
with app.app_context():
    db.create_all()


    # Define the dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', current_user=current_user.username)


# Define the view reports route
@app.route('/view_reports')
@login_required
def view_reports():
    reports = Report.query.all()
    return render_template('view_reports.html', reports=reports)


@app.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    report = Report.query.get_or_404(report_id)

    # Check if the authenticated user is the owner of the report
    if report.user != current_user:
        flash('You are not authorized to delete this report.', 'danger')
        return redirect(url_for('view_reports'))

    # Delete the report from the database
    db.session.delete(report)
    db.session.commit()

    flash('Report deleted successfully.', 'success')
    return redirect(url_for('view_reports'))


# Run the Flask application in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)
