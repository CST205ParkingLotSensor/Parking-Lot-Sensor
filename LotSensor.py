from flask import Flask, render_template
import cv2
import numpy as np
import urllib
import urllib.request


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


# Define Cascade
casc_class = 'cascade.xml'
cascade = cv2.CascadeClassifier(casc_class)
if cascade.empty():
    print('WARNING: Cascade did not load')


# Define Class for a Lot
class Lot:
    """A class to define a parking lot"""

    def __init__(self, lotNum, maxCap, imageSrc):
        self.lotNum = lotNum
        self.maxCap = maxCap
        self.imageSrc = imageSrc
        self.updateOccup()

    def updateOccup(self):
        print("trying to get image")
        img = url_to_image(self.imageSrc)
        print("got img")
        cars = cascade.detectMultiScale(img, 1.1, 9)
        print("Found: " + str(len(cars)))
        self.currOccp = len(cars)


# Setup the desired Lots
Lots = [Lot(1, 20, "https://i.ytimg.com/vi/QPDTCtLComk/maxresdefault.jpg"),
        Lot(2, 200, "https://i.ytimg.com/vi/U7HRKjlXK-Y/maxresdefault.jpg")]

# create an instance of the Flask class
app = Flask(__name__)


# route() decorator binds a function to a URL
@app.route('/LotSensor')
def mainPage():
    return render_template('LotSensor.html', Lot_List=Lots)


@app.route('/LotSensor/<lot_num>')
def lot_info(lot_num):
    return render_template('LotInfo.html', Lot=Lots[int(lot_num) - 1])


if __name__ == "__main__":
    app.run(port=4996)