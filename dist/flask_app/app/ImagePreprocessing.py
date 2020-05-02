# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 11:20:09 2020
@author: Donovan
"""
import cv2
#conda install -c conda-forge opencv=3.4.1
#3-Clause BSD License

import os
import csv
import numpy as np
from skimage.io import imread, imshow
import matplotlib.pyplot as plt
from skimage.color import rgb2hsv

#conda install -c anaconda scikit-image
#BSD 3-Clause

class ImagePreprocessing:
    """@package ImagePreprocessing
This class extracts a number of features from the images and saves them in a CSV
to be used by the machine learning class.

"""
    def __init__(self):
        import cv2
        #conda install -c conda-forge opencv=3.4.1
        #3-Clause BSD License

        import os
        import csv
        import numpy as np
        from skimage.io import imread, imshow
        import matplotlib.pyplot as plt
        from skimage.color import rgb2hsv
        
      
 
    def getAdvancedFeatures(self, imageIn):
        """
        Returns a tuple of advanced features.

        Parameters
        ----------
        imageIn : Image
            The image to process.

        Returns
        -------
        returnValues : tuple
            numbers.

        """
        lowRed = 165
        highRed = 240
        lowGreen = 160
        highGreen = 200
        lowBlue = 135
        highBlue = 240
        
        rgb_img = imageIn
        red = rgb_img[:, :, 0]
        hsv_img = rgb2hsv(rgb_img)
        hue_img = hsv_img[:, :, 0]
        sat_img = hsv_img[:, :, 1]
        value_img = hsv_img[:, :, 2]
        
        #saturation mask to isolate foreground
        satMask = (sat_img > .11) | (value_img > .3)
        #hue and value mask to remove additional brown from background
        mask = (hue_img > .14) | (value_img > .48)
        #healthy corn mask to remove healthy corn, leaving only blighted pixels
        nonBlightMask = hue_img < .14
        #get foreground
        rawForeground = np.zeros_like(rgb_img)
        rawForeground[mask] = rgb_img[mask]
        #reduce brown in background
        foreground = np.zeros_like(rgb_img)
        foreground[satMask] = rawForeground[satMask]
        #get blighted pixels from foreground
        blightedPixels = np.zeros_like(rgb_img)
        blightedPixels[nonBlightMask] = foreground[nonBlightMask]
        #combine into one band
        blightedHSV = np.bitwise_or(blightedPixels[:,:,0], blightedPixels[:,:,1])
        blightedHSV = np.bitwise_or(blightedHSV, blightedPixels[:,:,2])
        
        red = rgb_img[:, :, 0]
        green = rgb_img[:, :, 1]
        blue = rgb_img [:, :, 2]
        binary_green = lowGreen < green
        binary_blue = lowBlue < blue
        binary_red = lowRed < red 
        RGB_Blights = np.bitwise_and(binary_red, binary_green)
        #'brown' pixels within each RGB threshold
        RGB_Blights = np.bitwise_and(RGB_Blights, binary_blue)
        HSV_and_RGB = np.bitwise_and(RGB_Blights, blightedHSV)
        #get features
        numForegroundPixels = np.count_nonzero(foreground)
        numBlightedHSVPixels = np.count_nonzero(blightedHSV)
        blightedHSVRatio = numBlightedHSVPixels / numForegroundPixels
        num_RGB_blightedPixels = np.count_nonzero(RGB_Blights)
        blightedRGBRatio = num_RGB_blightedPixels / numForegroundPixels 
        numBlightedBothPixels = np.count_nonzero(HSV_and_RGB)
        blightedBothRatio = numBlightedBothPixels / numForegroundPixels  
        returnValues = (numForegroundPixels, numBlightedHSVPixels, blightedHSVRatio, num_RGB_blightedPixels,
                        blightedRGBRatio, numBlightedBothPixels, blightedBothRatio)
       
        return returnValues
    
    def avgGray(self, image):
        grayscaleArray = np.reshape(image, -1)
        gray_mean = np.mean(grayscaleArray)
        return gray_mean
    
    def avgRed(self, image):
        red = image[0:4000, 0:6000, 0]
        red = np.reshape(red, -1)
        red_mean = np.mean(red)
        return red_mean
    
    def avgGreen(self, image):
        green = image[0:4000, 0:6000, 1]
        green = np.reshape(green, -1)
        green_mean = np.mean(green)
        return green_mean
    
    def avgBlue(self, image):
        blue = image [0:4000, 0:6000, 2]
        blue = np.reshape(blue, -1)
        blue_mean = np.mean(blue)
        return blue_mean
        
    def numBrownRed(self, image):
        red = image[0:4000, 0:6000, 0]
        red = np.reshape(red, -1)
        num_brown_red, bin_edges = np.histogram(red, bins=1, range=(180, 250))
        return num_brown_red[0]
    
    def numBrownGreen(self, image):
        green = image[0:4000, 0:6000, 1]
        green = np.reshape(green, -1)
        num_brown_green, bin_edges = np.histogram(green, bins=1, range=(160, 200))
        return num_brown_green[0]
    
    def numBrownBlue(self, image):
        blue = image [0:4000, 0:6000, 2]
        blue = np.reshape(blue, -1)
        num_brown_blue, bin_edges = np.histogram(blue, bins=1, range=(150, 240))
        return num_brown_blue[0]
    
    def FdHuMoments(self, image):
        """
        Extracts Hu moments feature from an image
        Parameters
        ----------
        
        image : imread
            The image used for feature extraction
        Returns
        -------
        Feature : Float Array
            The Hu moments in the image.
        Reference
        ---------
        https://gogul.dev/software/image-classification-python
        """
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        feature = cv2.HuMoments(cv2.moments(image)).flatten()
        return feature
    
    def FdHaralick(self, image):
        import mahotas
        #
        #MIT License
        """
        Extracts Haralick texture feature from an image
        Parameters
        ----------
        
        image : imread
            The image used for feature extraction
        Returns
        -------
        Feature : Float Array
            The Haralick texture in the image.
        Reference
        ---------
        https://gogul.dev/software/image-classification-python
        """
        # convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # compute the haralick texture feature vector
        haralick = mahotas.features.haralick(gray).mean(axis=0)
        # return the result
        return haralick
    
    def FdHistogram(self, image, mask=None, bins = 8):
        """
        Extracts color histogram feature from an image
        Parameters
        ----------
        
        image : imread
            The image used for feature extraction
        Returns
        -------
        Feature : Float Array
            The color histogram in the image.
        Reference
        ---------
        https://gogul.dev/software/image-classification-python
        """
        # convert the image to HSV color-space
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # compute the color histogram
        hist  = cv2.calcHist([image], [0, 1, 2], None, [bins, bins, bins], [0, 256, 0, 256, 0, 256])
        # normalize the histogram
        cv2.normalize(hist, hist)
        # return the histogram
        return hist.flatten()
    
    import numpy as np
    def ImageProcessing(self, folder_name):
        def allFilesInDir(dir_name, label):
            csvOut = []
            counter = 0
            for root, dirs, files in os.walk(os.path.abspath(dir_name)):
                for file in files:
    
                    image = imread(os.path.join(root, file), as_gray=True)
                    import matplotlib.pyplot as plt
            
                    gray_mean = self.avgGray(image)
    
                    image = imread(os.path.join(root, file))
                    red_mean = self.avgRed(image)
                    green_mean = self.avgGreen(image)
                    blue_mean = self.avgBlue(image)
                    num_brown_red = self.numBrownRed(image)
                    num_brown_green = self.numBrownGreen(image)
                    num_brown_blue = self.numBrownBlue(image)
                    advanced_features = self.getAdvancedFeatures(image)
                    
                    image = cv2.imread(os.path.join(root, file))
                    fv_hu_moments = self.FdHuMoments(image)
                    fv_haralick = self.FdHaralick(image)
    #                fv_histrogram = FdHistogram(image)
    
                    feature_vector = np.hstack([file, fv_hu_moments[0], fv_haralick[0], fv_haralick[3], fv_haralick[7], fv_haralick[8], gray_mean, green_mean, 
                                                num_brown_red, advanced_features[0], 
                                                advanced_features[1],  advanced_features[2],  advanced_features[3],
                                                 advanced_features[4],  advanced_features[5],  advanced_features[6], label])
                    
                    csvOut.append(feature_vector)
                    counter += 1
                    print(counter)
            return csvOut
        
        #Please update these column labels if you add features in order to help with feature selection.
        columnLabels = ('fileName','fvhu', 'fvha1', 'fvha4', 'fvha8','fvha9',
                       'gray_mean',  'green_mean',  'num_brown_red', 'numForegroundPxls', 'blightedHSV_pxls', 'blightedHSV_ratio', 
                        'numRGB_blightedPxls', 'blightedRGBRatio', 'RGB_and_HSV_blighted', 'RGB_and_HSV_both_ratio', 'label')
        
        blighted_features = allFilesInDir('images/blighted', 'B')
        healthy_features = allFilesInDir('images/healthy', 'H')
        csvfile = open('csvOut.csv','w', newline = '')
        obj = csv.writer(csvfile)
        #Uncomment to add column labels
        #obj.writerow(columnLabels)
        obj.writerows(blighted_features)
        obj.writerows(healthy_features)
    
#Main
folder_name = '../images/'



processor = ImagePreprocessing()
processor.ImageProcessing(folder_name)