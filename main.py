from datetime import datetime
import cpldata
import carpool_listing
import hashlib
import sendgrid

from flask import Flask, request, render_template, session, redirect

app = Flask(__name__)
app.secret_key = 'Lgݔ滾M3=L'


def log(msg):
    """Log a simple message."""
    # Look at: https://console.cloud.google.com/logs to see your logs.
    # Make sure you have "stdout" selected.
    print('main: %s' % msg)


@app.route('/')
@app.route('/index.htm')
@app.route('/index.html')
def index():
    user = get_user()
    if user:
        return redirect('/listings')
    else:
        return render_template('index.html', page_title='Home Page')


@app.route('/process', methods=['POST'])
def info():
    start_destination = request.form['start_destination']
    end_destination = request.form['end_destination']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    description = request.form['description']
    seats_available = request.form['seats_available']
    contact_info = request.form['contact_info']
    item_id = None
    if 'id' in request.form:
        item_id = request.form['id']
    # create and store listing in database
    listing = carpool_listing.CarPoolListing(item_id, start_destination, end_destination, start_date, end_date, description, seats_available, contact_info)
    cpldata.create_list_item(listing, get_user())
    return render_template('listcreated.html', page_title='Submission', user=get_user())


@app.route('/listings')
def listings():
    car_pool_listings = cpldata.get_listings()
    return render_template('listings.html', page_title='Listings', listings=car_pool_listings, user=get_user())

#
# Below is code for login and creating account
#


@app.route('/contact')
def contact():
    return render_template('contact.html', page_title='Contact Us', user=get_user())


@app.route('/contactsubmission', methods=['POST'])
def contactsubmission():
    name = request.form['fullname']
    info = request.form['email']
    comments = request.form['comments']
    sg = sendgrid.SendGridClient("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")
    message = sendgrid.Mail()

    message.add_to("carpoolemails@gmail.com")
    message.set_from("carpoolemails@gmail.com")
    message.set_subject("Contact Submission: " + name + " - " + info)
    message.set_html(comments)
    sg.send(message)
    return render_template('contactsuccess.html', page_title='Contact submission', user=get_user())


@app.route('/profile')
def profile():
    user = get_user()
    if user:
        about = cpldata.load_about_user(user)
        car_pool_listings = cpldata.get_user_listings(user)
    return render_template('profile.html', page_title='Profile', text=about, listings=car_pool_listings, user=get_user())


@app.route('/saveprofile', methods=['POST'])
def saveprofile():
    user = get_user()
    if user:
        about = request.form.get('profile')
        cpldata.save_about_user(user, about)
        return redirect('/profile')
    return 'Error you are not signed in'


@app.route('/user/<username>')
def user_page(username):
    about = cpldata.load_about_user(username)
    about_lines = about.splitlines()
    # listings = cpldata.load_listings(username)
    return render_template('profile.html', page_title='User Profile', user=username, lines=about_lines)


@app.route('/signout')
def signout():
    session['user'] = None
    return render_template('index.html', page_title='Home Page')


@app.route('/form')
def form():
    return render_template('form.html', page_title='Form Submission',user=get_user())


@app.route('/delete', methods=['POST'])
def delete():
    # retrieve the parameters from the request
    cpl_id = int(request.form['id'])
    try:
        log('deleting item for ID: %s' % cpl_id)
        cpldata.delete_list_item(cpl_id)
    except Exception as exc:
        log(str(exc))
    return redirect('/profile')


@app.route('/edit', methods=['POST'])
def edit():
    return render_template('editform.html', page_title='Edit Listing', user=get_user())


@app.route('/editsubmission', methods=['POST'])
def editsubmission():
    # retrieve the parameters from the request
    start_destination = request.form['start_destination']
    end_destination = request.form['end_destination']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    description = request.form['description']
    seats_available = request.form['seats_available']
    contact_info = request.form['contact_info']
    item_id = None
    if 'id' in request.form:
        item_id = request.form['id']
    try:
        if item_id:
            item = carpool_listing.CarPoolListing(item_id, start_destination, end_destination, start_date, end_date, description, seats_available, contact_info)
            log('saving list item for ID: %s' % item_id)
            cpldata.save_list_item(item)
        else:
            log('saving new list item')
            cpldata.create_list_item(carpool_listing.CarPoolListing(item_id, start_destination, end_destination, start_date, end_date, description, seats_available, contact_info))
    except Exception as exc:
        log(str(exc))
    return render_template('listings.html', page_title='Listings Edited', user=get_user())


@app.route('/about')
def about():
    return render_template('about.html', page_title='About Ride Share', user=get_user())


@app.route('/dologin', methods=['POST'])
def dologin():
    username = request.form.get('username')
    password = request.form.get('password')
    passwordhash = get_password_hash(password)
    user = cpldata.load_user(username, passwordhash)

    # Checks to see if the user is in the system already
    if user:
        session['user'] = user.username
        return redirect('/listings')
    else:
        error = 'Oops! We could not recognize your username and/or your password. Please try again.'
        return render_template('error.html', page_title='login', error=error)


@app.route('/make_account', methods=['POST'])
def make_account():
    username = request.form.get('username')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    email = request.form.get('email')
    user = carpool_listing.User(username, email)
    # validate username
    # validate email
    result = cpldata.user_exists_check(username)
    if(result is not None):
        error = 'ERROR: user already exists! Please choose a different username'
        return render_template('error.html', page_title='User Name Exists Error', error=error)

    passwordhash = get_password_hash(password1)
    cpldata.save_user(user, passwordhash)
    session['user'] = user.username
    return redirect('/listings')


def get_user():
    return session.get('user', None)


def get_password_hash(pw):
    encoded = pw.encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)