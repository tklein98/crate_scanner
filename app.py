from flask import Flask, request, render_template
from crate_scanner.scrapers.price_scraper import get_price
from crate_scanner.scrapers.reviews_scraper import get_top3_reviews
import os
from tensorflow.keras.models import Model
from tensorflow.keras.applications import VGG16
import numpy as np
from crate_scanner.albuminfo import matched_album

# Creating basemodel for vectorization
vgg16 = VGG16(weights='imagenet', include_top=True, pooling='max', input_shape=(224, 224, 3))
basemodel = Model(inputs=vgg16.input, outputs=vgg16.get_layer('fc2').output)

TEMPLATE_DIR = os.path.abspath('templates')
STATIC_DIR = os.path.abspath('static')

# loading images database
full_vectors = np.load('crate_scanner/data/full_array.npy', allow_pickle=True)

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result/', methods=['GET'])
def display_result():
    url = request.args.get("url")

    # run model 1:artist, 2:album, 3:artist+album, 4: album_id, 5: album_cover
    album_info = matched_album(url, basemodel, full_vectors)

    # run model: retrieve album, artist and cover
    artist = album_info[1].lower()
    album = album_info[2].lower()
    cover_url = album_info[5]

    # add spotify widget
    album_id = album_info[4]

    # get price
    price = get_price(artist, album)

    # get reviews
    reviews = get_top3_reviews(artist, album)

    # get album recommendations

    #render template, and add variables to be passed to frontend as arguments
    return render_template('result.html', artist=artist, album=album, album_id=album_id, price=price, reviews=reviews, url=url, cover_url=cover_url)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
