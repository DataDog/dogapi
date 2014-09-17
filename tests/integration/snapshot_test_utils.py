from PIL import Image
import io
import urllib


def read_image_as_raster(img_url):
    """ Reads image data from URL in raster format."""
    try:
        img = urllib.urlopen(img_url)
        image_file = io.BytesIO(img.read())
        img = Image.open(image_file)
        w, h = img.size
        pixels = img.load()
        return [pixels[x, y] for x in range(w) for y in xrange(h)]
    except Exception:  # Return empty array if image is not found or is corrupt
        return []


def assert_not_blank(snapshot_url):
    """ Asserts image is not blank"""
    pixels = read_image_as_raster(snapshot_url)
    assert len(pixels) > 0, "Image should not be empty"
    assert len(set(pixels)) > 1, "Image should have at least 2 colors"


def assert_has_no_events(snapshot_url):
    """ Asserts snapshot has no events"""
    pixels = read_image_as_raster(snapshot_url)
    for color in set(pixels):
        r, g, b, a = color  # red, green, blue, alpha
        assert not (r == 255 and g == 230 and b == 230),\
            "Snapshot should not have events"