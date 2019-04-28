from flask import Flask, render_template, request, send_file, after_this_request, Response, stream_with_context, url_for, send_from_directory
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
    """ Brings user to homepage"""
    return render_template('home.html')

@app.route('/about')
def about():
    """ Brings user to about page"""
    return render_template('about.html')

@app.route('/cartoonify')
def cartoonify(filename = None):
    """ Brings user to first part of cartoonify process (uploading their image)"""
    return render_template('cartoonify.html')

@app.route('/addpoints', methods=['POST'])
def upload_image():
    """ Saves an uploaded image in the uploads folder, resizes it, and redirects
    user to the addpoints page."""
    try:
        image = request.files['image']

        # Check file extension and return error page if not .jpg or .png
        extension = image.filename.split(".")[-1]
        if extension != "png" and extension != "jpg":
            return render_template('error.html')

        f = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(f)
        resizeImage(f)
        
        return render_template('addpoints.html', filename=f)

    except:
        return render_template('error.html')

@app.route('/addpoints/<path:filename>', methods=['POST'])
def add_points(filename):
    """ Parses extra points provided by user and creates a text file representing the
    facial keypoints of their uploaded image (plus the extra points they added). Redirects
    the user to the choosecartoon page."""
    try:
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

    except:
        return render_template('error.html')

@app.route('/choosecartoon/<path:filename>', methods=['POST'])
def choosecartoon(filename):
    """ Takes in a user's cartoon choice and redirects them to the loading screen
    for their morph."""
    try:
        cartoon = request.form['cartoon']
    
        f = os.path.basename(filename)
        videoname = f.split(".")[0] + cartoon.split(".")[0] + "morph.mp4"
        gifname = f.split(".")[0] + cartoon.split(".")[0] + "morph.gif"
        halfwayname = f.split(".")[0] + cartoon.split(".")[0] + "halfway.jpg"
        quartername = f.split(".")[0] + cartoon.split(".")[0] + "quarter.jpg"
        threequartername = f.split(".")[0] + cartoon.split(".")[0] + "threequarter.jpg"

        return render_template('loading.html', filename = f, cartoonname = cartoon, videoname = videoname, 
            gifname = gifname, halfwayname = halfwayname, quartername = quartername, threequartername = threequartername)

    except:
        return render_template('error.html')

@app.route('/load/<path:filename>/<path:cartoonname>')
def load(filename, cartoonname):
    """ Runs the morph/gif writing process and returns information about how the morph
    in an HTML response to be parsed in loading.html"""
    return Response(morph(filename, cartoonname, NUM_FRAMES), mimetype= 'text/event-stream')

@app.route('/cartoonifyfinished/<path:videoname>/<path:gifname>/<path:halfwayname>/<path:quartername>/<path:threequartername>')
def show_morph(videoname, gifname, halfwayname, quartername, threequartername):
    """ Redirects user to the final stage of the cartoonify page, in which they can 
    view and download their morph as a gif or mp4, or the quarter, halfway, and 
    three-quarters stages of the moprh as jpgs"""
    try:
        videoname = os.path.join(MORPH_FOLDER, videoname)
        gifname = os.path.join(MORPH_FOLDER, gifname)
        halfwayname = os.path.join(MORPH_FOLDER, halfwayname)
        quartername = os.path.join(MORPH_FOLDER, quartername)
        threequartername = os.path.join(MORPH_FOLDER, threequartername)
        return render_template('cartoonify.html', videoname = videoname, gifname = gifname, 
            halfwayname = halfwayname, quartername = quartername, threequartername = threequartername, init = True)

    except:
        return render_template('error.html')

@app.route('/addpoints/<path:filename>', methods=['GET'])
def add_points_image(filename):
    """ Serves the image the user uploaded to the addpoints page"""
    return send_file(filename, as_attachment=True, mimetype='image/jpg')

@app.route('/cartoonify/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    """ Serves one of the downloadable files at the final stage of 
    the cartoonify page"""
    return send_file(filename, as_attachment=True)

@app.route('/cartoonify')
def tryagain():
    """ Reroutes user back to the starting cartoonify page from the
    final cartoonify page."""
    return render_template('cartoonify.html', init=False)

if __name__ == '__main__':
    app.run(debug=True)
