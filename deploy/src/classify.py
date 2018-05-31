from keras.models import load_model
from vectorize import vectorize
import numpy as np

model = load_model('is_it_anime.h5')

def classify(data):
    vect_input = np.asarray([vectorize(data, scale_size=512)]) / 256
    results = model.predict(vect_input)[0]
    return [float(x) for x in results]
