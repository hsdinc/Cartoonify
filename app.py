from flask import Flask, render_template, request, send_file, after_this_request, Response, stream_with_context
from faceMorph import resizeImage, createTextFile, morph
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('uploads')
MORPH_FOLDER = os.path.basename('facemorph')
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

@app.route('/addpoints', methods=['POST'])
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
    f = os.path.basename(filename)
    createTextFile(f, extraPoints)
    gifname = os.path.join(MORPH_FOLDER, f.split(".")[0] + "morph.gif")

    return render_template('loading.html', filename = f, gifname = gifname)
    #return render_template('cartoonify.html', filename = f, init = True)

@app.route('/load/<path:filename>')
def load(filename):
    return Response(morph(filename), mimetype= 'text/event-stream')

@app.route('/cartoonifyfinished/<path:filename>')
def show_morph(filename):
    return render_template('cartoonify.html', filename = filename, init = True)

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
