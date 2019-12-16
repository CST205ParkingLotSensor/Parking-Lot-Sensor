from flask import Flask, render_template, request
import cv2
import numpy as np
import urllib
import urllib.request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired

LotChoice = []
# function to download images from web and convert to grayscale
def url_to_image(url):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_GRAYSCALE)

    # return the image
    return image

def build_choice_list():
    result = []
    for i in range(len(Lots)):
        tup = (str(i), Lots[i].lotName)
        result.append(tup)
    print(result)
    return result

# Define Cascade
casc_class = 'cascade.xml'
cascade = cv2.CascadeClassifier(casc_class)
if cascade.empty():
    print('WARNING: Cascade did not load')


# Define Classes
class Lot:
    """A class to define a parking lot"""

    def __init__(self, lotName, maxCap, imageSrc):
        self.lotName = lotName
        self.maxCap = maxCap
        self.imageSrc = imageSrc
        self.updateOccup()

    def updateOccup(self):
        img = url_to_image(self.imageSrc)
        cars = cascade.detectMultiScale(img, 1.1, 9)
        self.currOccp = len(cars)

# Setup the desired Lots
Lots = [Lot("A", 20, "https://i.ytimg.com/vi/QPDTCtLComk/maxresdefault.jpg"),
        Lot("B", 200, "https://i.ytimg.com/vi/U7HRKjlXK-Y/maxresdefault.jpg")]


class Config(FlaskForm):
    removeList = SelectField()
    lot_name = StringField('Lot Name')
    lot_max = IntegerField('Lot Max Capacity')
    lot_src = StringField('Lot Image Source')


# create an instance of the Flask class
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sensor-lot'



# route() decorator binds a function to a URL
@app.route('/LotSensor')
def mainPage():
    return render_template('LotSensor.html', Lot_List=Lots)


@app.route('/LotSensor/<lot_name>')
def lot_info(lot_name):
    for lot in Lots:
        if lot.lotName == lot_name:
            return render_template('LotInfo.html', Lot=lot)
    return render_template('Error.html')

@app.route('/LotSensor/Config', methods=['GET','POST'])
def config():
    form = Config()
    form.removeList.choices = build_choice_list()
    if form.validate_on_submit():
        if form.lot_name.data == "" or int(form.lot_max.data) <= 0 or form.lot_src.data == "":
            print("removing")
            Lots.pop(int(form.removeList.data)-1)
        else:
            print("adding")
            Lots.append(Lot(form.lot_name.data, form.lot_max.data, form.lot_src.data))

    return render_template('Config.html', Lot_List=Lots, form = form)

if __name__ == "__main__":
    app.run(port=4996)