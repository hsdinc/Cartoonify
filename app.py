from flask import Flask, render_template, request, send_file, after_this_request, Response, stream_with_context
from faceMorph import resizeImage, createTextFile, morph
import os

app = Flask(__name__)

# NUM_FRAMES is the number of frames to be created for the gif/mp4. Half of these frames will be the morph in reverse
NUM_FRAMES = 66
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

    return render_template('choosecartoon.html', filename = filename)

@app.route('/choosecartoon/<path:filename>', methods=['GET'])
def choosecartoon_start(filename):
    images = os.listdir(os.path.join(app.static_folder, "images"))
    return send_file(filename, as_attachment=True, mimetype='image/jpg')

@app.route('/choosecartoon/<path:filename>', methods=['POST'])
def choosecartoon(filename):
    cartoon = request.form['cartoon']
   
    f = os.path.basename(filename)
    videoname = f.split(".")[0] + cartoon.split(".")[0] + "morph.mp4"
    gifname = f.split(".")[0] + cartoon.split(".")[0] + "morph.gif"
    halfwayname = f.split(".")[0] + cartoon.split(".")[0] + "halfway.jpg"

    return render_template('loading.html', filename = f, cartoonname = cartoon, videoname = videoname, gifname = gifname, halfwayname = halfwayname)

@app.route('/load/<path:filename>/<path:cartoonname>')
def load(filename, cartoonname):
    return Response(morph(filename, cartoonname, NUM_FRAMES), mimetype= 'text/event-stream')

@app.route('/cartoonifyfinished/<path:videoname>/<path:gifname>/<path:halfwayname>')
def show_morph(videoname, gifname, halfwayname):
    videoname = os.path.join(MORPH_FOLDER, videoname)
    gifname = os.path.join(MORPH_FOLDER, gifname)
    halfwayname = os.path.join(MORPH_FOLDER, halfwayname)
    return render_template('cartoonify.html', videoname = videoname, gifname = gifname, halfwayname = halfwayname, init = True)

@app.route('/addpoints/<path:filename>', methods=['GET'])
def add_points_image(filename):
    return send_file(filename, as_attachment=True, mimetype='image/jpg')

@app.route('/cartoonify/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
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
    return send_file(filename, as_attachment=True)

@app.route('/cartoonify')
def tryagain(filename):
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
    return render_template('cartoonify.html', init=True)


if __name__ == '__main__':
    app.run(debug=True)
