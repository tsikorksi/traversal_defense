import random
import string
import os

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
	return 'Hello World!'


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	"""
	Anti-Brute: We write a catch-all function that generates a page of random size,
	thus preventing tools like dirb
	:return: the template with a random size and random error code
	"""
	return render_template("random_200.html", path=path,
							                 random_text=random_string(random.randrange(3000, 8000))), random.randrange(200, 299, 1)


def random_string(n):
	return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=n)))


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(debug=True, host='0.0.0.0', port=port)
