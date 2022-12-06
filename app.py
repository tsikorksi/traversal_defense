import random
import string
import os

from flask import Flask, render_template, request

app = Flask(__name__)

safe_path = os.path.abspath('user_images')

def is_safe_path(requested_path):
    if os.path.commonprefix((os.path.realpath(requested_path), safe_path)) != safe_path:
      return false
    else:
      return true


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


@app.route('/img', defaults={'file': ''})
def get_image():
  file = request.args.get('file')
  if file == '':
    return 'No file given.'
  
  req_path = path.join(__dirname, '/user_images/', file)
  
  if (is_safe_path(req_path)):
    os.sendfile(
      path.join(__dirname, '/user_images/', file))
  else:
    return 'Unauthorized file path!'
    

if __name__ == '__main__':
	app.run()
