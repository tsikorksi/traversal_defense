import random
import string
import os

from flask import Flask, render_template, request, send_file

app = Flask(__name__)

safe_path = os.path.realpath('placeholder.txt')

def is_safe_path(requested_file):
    if os.path.commonprefix((os.path.realpath(requested_file), safe_path)) != safe_path:
      return False
    else:
      return True


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


@app.route('/img', defaults={'file': ''}, methods=['GET'])
@app.route('/img/', defaults={'file': ''}, methods=['GET'])
def get_image(file):
  file = request.args.get('file')
  
  if file == '' or file is None:
    return 'No file given.'

  req_path = os.path.join('user_images/', file)
  
  if (is_safe_path(file)):
    return send_file(req_path)
  else:
    return 'Unauthorized file path!'
    

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(debug=True, host='0.0.0.0', port=port)
