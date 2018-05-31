from PIL import Image

def vectorize(img_file, cache=None, scale_size=None):
    """ Coordinator for vectorization """

    # If we've saved the image, no point in recomputing
    if cache and img_file in cache and False:
        return cache[img_file]

    # Load PIL with the image
    img = Image.open(img_file)

    # If given a scale, format the image to that scale
    if scale_size:
        vec = scale(img, scale_size)

    # Otherwise assume it's good
    else:
        vec = get_pixels(img)

    # If we have a cache and it missed, add it
    if cache:
        cache[img_file] = vec

    return vec

def get_pixels(image):
    """ Takes a PIL image object, and returns a 3d vector """
    vec_flat = list(image.convert('RGB').getdata())
    # vec_flat = [(r/256, g/256, b/256) for r, g, b in vec_flat]
    width, height = image.size
    return [vec_flat[i * width:(i + 1) * width] for i in range(height)]


def scale(img, size):
    """ scale to size, then pad to square """

    width, height = img.size

    # We don't want to distort in the scaling, so we'll be resizing both width and height by the same value
    if width > height:
        resize_factor = size / width
    else:
        resize_factor = size / height

    # Resize the image to the computed size, and carry it as a vector
    img_vect = get_pixels(
        img.resize(
            (
                int(width * resize_factor),
                int(height * resize_factor)
            )
        )
    )

    # We'll be fixing this if it's not square
    height, width = len(img_vect), len(img_vect[0])

    # If we're taller than we are wide, then pad the width by inserting into each row
    if size > width:
        diff = size - width
        pre = int(diff/2)  # Calculated so that the image is centered
        post = int((diff+1)/2)
        for idx, row in enumerate(img_vect):
            img_vect[idx] = [(0, 0, 0)]*pre + row + [(0, 0, 0)]*post

    # If wider than we are tall, pad with extra rows
    if size > height:
        diff = size - height
        pre = int(diff/2)
        post = int((diff+1)/2)
        img_vect[0:0] = [[(0, 0, 0)]*size] * pre
        img_vect.extend([[(0, 0, 0)]*size] * post)

    return img_vect
