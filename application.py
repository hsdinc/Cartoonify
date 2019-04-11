from flask import Flask, render_template, request, send_file, after_this_request
from faceMorph import morph
import os

application = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('uploads')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@application.route('/')
def index():
        return render_template('home.html')


@application.route('/about')
def about():
    return render_template('about.html')


@application.route('/cartoonify')
def cartoonify(filename = None):
    return render_template('cartoonify.html')


@application.route('/cartoonify', methods=['POST'])
def upload_image():
    image = request.files['image']
    f = os.path.join(application.config['UPLOAD_FOLDER'], image.filename)
    image.save(f)
    f = morph(image.filename)
    return render_template('cartoonify.html', filename=f, init=True)


@application.route('/cartoonify/<path:filename>', methods=['GET', 'POST'])
def download_image(filename):
    file_handle = open(filename, 'r')
    @after_this_request
    def remove_file(response):
        try:
            print(filename)
            os.remove(filename)
            file_handle.close()
        except Exception as error:
            application.logger.error("Error removing or closing downloaded file handle", error)
        return response
    return send_file(filename, as_attachment=True, mimetype='image/jpg')

@application.route('/cartoonify')
def tryagain(filename):
    file_handle = open(filename, 'r')
    @after_this_request
    def remove_file(response):
        try:
            os.remove(filename)
            file_handle.close()
        except Exception as error:
            application.logger.error("Error removing or closing downloaded file handle", error)
        return response
    return render_template('cartoonify.html', init=True)


if __name__ == '__main__':
    application.run(debug=True)