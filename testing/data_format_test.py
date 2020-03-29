import unittest
from PIL import Image

# function to read in a jpg image and convert it into a numpy array
def readJPGFile(filename):
    # read in the image and convert it to grayscale
    img = Image.open(filename).convert('L')
    # return the numpy array of the image
    return np.asarray(img).reshape(160,300,1)

class LoadDataTest(unittest.TestCase):
    # test that the shape of the image is as expected
    def read_image_test():
        img = readJPGFile('../forms/ABET_SCANS_Result/no/no_0001_a0.jpg')
        self.assertTrue(img.shape == (160,300,1))

if __name__ == '__main__':
    unittest.main()