import random
import string
import os
from pymongo import MongoClient
import bcrypt
from flask import Flask, render_template, request, send_file, render_template, request, url_for, redirect, session
from pathlib import Path

app = Flask(__name__)
app.secret_key = "testing"


def MongoDB():
    db_uri = "mongodb+srv://eliauf23:93mheerdH5UqK6WO@cluster0.f5symzp.mongodb.net/websecurity?retryWrites=true&w=majority"
    client = MongoClient(db_uri)
    db = client.get_database('total_records')
    db_records = db.register
    return db_records


records = MongoDB()


@app.route("/", methods=['POST', 'GET'])
def index():
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('index.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('index.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            records.insert_one(user_input)
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            return render_template('logged_in.html', email=new_email)
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("logged_in"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            # encode the password and check match
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('logged_in'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)


@app.route('/logged_in')
def logged_in():
    if "email" in session:
        email = session["email"]
        return render_template('logged_in.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        return render_template("signout.html")
    else:
        return render_template('index.html')


def check_for_path_traversal(path):
    # convert encoding to utf-8
    path = path.encode('utf-8')
    # check if path is safe
    if b'../' in path or b'..' in path or b'./' in path:
        return True
    # check if path has null bytes
    if b'\x00' in path:
        return True


def is_safe_path(requested_file, user_id):
    safe_path = os.path.realpath(os.path.join("user_images", user_id))
    return os.path.commonprefix((os.path.realpath(requested_file), safe_path)) == safe_path


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    Anti-Brute: We write a catch-all function that generates a page of random size,
    thus preventing tools like dirb
    :return: the template with a random size and random error code
    """
    return render_template("random_200.html", path=path, random_text=random_string(random.randrange(3000, 8000))), random.randrange(200, 299, 1)


def random_string(n):
    return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=n)))


@app.route('/img', defaults={'file': ''}, methods=['GET'])
@app.route('/img/', defaults={'file': ''}, methods=['GET'])
def get_image(file):
    file = request.args.get('file')

    if file == '' or file is None:
        return 'No file given.'

    if check_for_path_traversal(file):
        return render_template("random_200.html", path='',
                               random_text=random_string(random.randrange(3000, 8000))), random.randrange(200, 299, 1)

    # check if filetype is allowed (for now we only allow text files)
    if not file.endswith('.txt'):
        return 'Unauthorized file type!'

    # get user from session
    if "email" in session:
        email = session.get("email", None)
        user = records.find_one({"email": email}) if email is not None else None
        if user is not None:
            user_id_str = str(user["_id"])
            path_str = os.path.join('user_images/', user_id_str, file)
            req_path = Path(path_str)
            if req_path.exists() and req_path.is_file() and os.access(path_str, os.R_OK) and is_safe_path(path_str,
                                                                                                          user_id_str):
                return send_file(req_path)
            else:
                return render_template("random_200.html", path='',
                                       random_text=random_string(random.randrange(3000, 8000))), random.randrange(200,
                                                                                                                  299,
                                                                                                                  1)
        else:
            return "Not authorized."


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
