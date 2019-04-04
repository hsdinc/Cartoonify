from flask import Flask, render_template, request, send_file, after_this_request
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
        return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/cartoonify')
def cartoonify(filename = None):
    return render_template('cartoonify.html')


@app.route('/cartoonify', methods=['POST'])
def upload_image():
    file = request.files['image']
    f = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(f)
    return render_template('cartoonify.html', filename=f, init=True)


@app.route('/cartoonify/<path:filename>', methods=['GET', 'POST'])
def download_image(filename):
    file_handle = open(filename, 'r')
    @after_this_request
    def remove_file(response):
        try:
                print(filename)
                os.remove(filename)
                file_handle.close()
        except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
        return response
    return send_file(filename, as_attachment=True, mimetype='image/jpg')

@app.route('/cartoonify')
def tryagain(filename):
    file_handle = open(filename, 'r')
    @after_this_request
    def remove_file(response):
        try:
            os.remove(filename)
            file_handle.close()
        except Exception as error:
            app.logger.error("Error removing or closing downloaded file handle", error)
        return response
    return render_template('cartoonify.html', init=True)


if __name__ == '__main__':
    app.run(debug=True)
