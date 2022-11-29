import random
import string

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
	:param path:
	:return:
	"""
	return render_template("random_200.html", random_text=random_string(200))


def random_string(n):
	return str(''.join(random.choices(string.ascii_uppercase + string.digits, k=n)))


if __name__ == '__main__':
	app.run()
