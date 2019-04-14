from flask import Flask, render_template, request, send_file, after_this_request
from faceMorph import resizeImage, createTextFile, morph
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
    image = request.files['image']
    f = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(f)
    resizeImage(f)

    return render_template('addpoints.html', filename=f)

@app.route('/addpoints/<path:filename>', methods=['POST'])
def add_points(filename):
    # Find extra points from form
    extraPoints = []
    extraPoints += [(int(request.form['leftearX']), int(request.form['leftearY']))]
    extraPoints += [(int(request.form['neckX']), int(request.form['neckY']))]
    extraPoints += [(int(request.form['rightshoulderX']), int(request.form['rightshoulderY']))]
    extraPoints += [(int(request.form['leftshoulderX']), int(request.form['leftshoulderY']))]

    # Create a text file representing the points to be used for the uploaded picture and morph
    createTextFile(os.path.basename(filename), extraPoints)
    #f = morph(os.path.basename(filename))

    return Response(morph(os.path.basename(filename)), "text/http")
    #return render_template('cartoonify.html', filename = f, init = True)

@app.route('/addpoints/<path:filename>', methods=['GET'])
def add_points_image(filename):
    return send_file(filename, as_attachment=True, mimetype='image/jpg')

@app.route('/cartoonify/<path:filename>', methods=['GET', 'POST'])
def download_image(filename):
    #file_handle = open(filename, 'r')
    #text_file_handle = open(filename + ".txt", 'r')
    #@after_this_request
    #def remove_file(response):
    #    try:
    #        os.remove(filename)
    #        os.remove(filename + ".txt")
    #        file_handle.close()
    #        text_file_handle.close()
    #    except Exception as error:
    #        app.logger.error("Error removing or closing downloaded file handle" + str(error))
    #    return response
    return send_file(filename, as_attachment=True, mimetype='image/gif')

@app.route('/cartoonify')
def tryagain(filename):
    file_handle = open(filename, 'r')
    text_file_handle = open(filename + ".txt", 'r')
    @after_this_request
    def remove_file(response):
        try:
            os.remove(filename)
            os.remove(filename + ".txt")
            file_handle.close()
            text_file_handle.close()
        except Exception as error:
            app.logger.error("Error removing or closing downloaded file handle" + str(error))
        return response
    return render_template('cartoonify.html', init=True)


if __name__ == '__main__':
    app.run(debug=True)
