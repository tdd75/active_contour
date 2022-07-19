import argparse
from imageio import imread
import random

import cv2
import numpy as np

import matplotlib.pyplot as plt
import morphsnakes as ms
from pprint import pprint
from skimage.filters import gaussian
from skimage.segmentation import active_contour as active_contour_sklearn

import warnings

# warnings.filter("ignore")

from feature_aggregation import BagOfWords, LLC, FisherVectors, Vlad


FOLDER_OUTPUT = './output'
drawing = False


# def click_and_crop(event, x, y, flags, param):
#     global refPt, cropping, drawing

#     def draw():
#         global image
#         cv2.circle(image, tuple(refPt[-1]), 3, (0, 255, 0), -1)
#         # image[refPt[-1]] = np.array([0,255,0])
#         cv2.imshow(window_name, image)

#     press_and_hold = 1

#     if not press_and_hold:
#         if event == cv2.EVENT_LBUTTONDOWN:
#             # refPt.append(np.array([x, y]))
#             pass

#         # check to see if the left mouse button was released
#         elif event == cv2.EVENT_LBUTTONUP:
#             refPt.append(np.array([x, y]))
#             cropping = False
#             draw()

#     else:
#         if event == cv2.EVENT_LBUTTONDOWN:
#             drawing = True
#             refPt.append(np.array([x, y]))
#             draw()
#         elif event == cv2.EVENT_MOUSEMOVE:
#             if drawing == True:
#                 refPt.append(np.array([x, y]))
#                 draw()

#         elif event == cv2.EVENT_LBUTTONUP:
#             drawing = False


def visual_callback_2d(input_file, background, fig=None):

    # Prepare the visual environment.
    if fig is None:
        fig = plt.figure()
    fig.clf()
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.imshow(background, cmap=plt.cm.gray)

    ax2 = fig.add_subplot(1, 2, 2)
    ax_u = ax2.imshow(np.zeros_like(background), vmin=0, vmax=1)
    plt.pause(0.001)

    def callback(levelset):

        if ax1.collections:
            del ax1.collections[0]
        ax1.contour(levelset, [0.5], colors='r')
        ax_u.set_data(levelset)
        fig.canvas.draw()
        plt.pause(0.001)

        plt.savefig(
            "contour_images/contour_{0}.png".format(input_file.split(".")[0].split("/")[-1]))

    return callback


def rgb2gray(img):
    return 0.2989 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]


refPt = []
image = []
# # construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="Path to the image")
# ap.add_argument("-t", "--transform",
#                 help="Do you want resizing?", action="store_true")
# ap.add_argument("-r", "--resize", help="Resizes the image into a x b x 3",
#                 type=int, nargs=2, default=[256, 256])
# args = vars(ap.parse_args())


def active_contour(input_file, output_file, image_size, argument, is_transform, is_morph):
    GRAY_IMAGE_SIZE = (256, 256)

    global image
    global refPt
    refPt = []

    print(input_file)
    print('start')

    # load the image, clone it, and setup the mouse callback function
    image = cv2.imread(input_file)
    if is_transform:
        image = cv2.resize(image, image_size)
    window_name = 'image_' + str(random.randint(1, 100000))

    def click_and_crop(event, x, y, flags, param):
        global refPt, cropping, drawing

        def draw():
            global image
            cv2.circle(image, tuple(refPt[-1]), 3, (0, 255, 0), -1)
            # image[refPt[-1]] = np.array([0,255,0])
            cv2.imshow(window_name, image)

        press_and_hold = 1

        if not press_and_hold:
            if event == cv2.EVENT_LBUTTONDOWN:
                # refPt.append(np.array([x, y]))
                pass

            # check to see if the left mouse button was released
            elif event == cv2.EVENT_LBUTTONUP:
                refPt.append(np.array([x, y]))
                cropping = False
                draw()

        else:
            if event == cv2.EVENT_LBUTTONDOWN:
                drawing = True
                refPt.append(np.array([x, y]))
                draw()
            elif event == cv2.EVENT_MOUSEMOVE:
                if drawing == True:
                    refPt.append(np.array([x, y]))
                    draw()

            elif event == cv2.EVENT_LBUTTONUP:
                drawing = False

    clone = image.copy()

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_and_crop)

    final_level_set = []
    while True:
        # display the image and wait for a keypress
        cv2.imshow(window_name, image)
        key = cv2.waitKey(1) & 0xFF

        # if the 'q' key is pressed, quit current window
        if key == ord('q'):
            cv2.destroyAllWindows()
            break

        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            image = clone.copy()

        # if the 'c' key is pressed, start drawing
        elif key == ord("c"):
            cv2.destroyAllWindows()
            input_image = imread(input_file)

            if is_transform:
                input_image = cv2.resize(input_image, image_size)

            if is_morph:
                imgcolor = input_image / 255.0
                img = rgb2gray(imgcolor)

                gimg = ms.inverse_gaussian_gradient(img, alpha=1000, sigma=2)

                init_ls = np.zeros(img.shape, dtype=np.int8)
                cv2.fillPoly(init_ls, np.array(
                    [np.array(refPt, dtype=np.int32)], dtype=np.int32), 255)

                # Callback for visual plotting
                callback = visual_callback_2d(input_file, imgcolor)

                # MorphGAC.
                # final_level_set = ms.morphological_geodesic_active_contour(gimg, iterations=10000,
                #                                                         init_level_set=init_ls,
                #                                                         smoothing=3, threshold=0.4,
                #                                                         balloon=-1, iter_callback=callback)
                final_level_set = ms.morphological_geodesic_active_contour(gimg,
                                                                           init_level_set=init_ls,
                                                                           iter_callback=callback,
                                                                           **argument)
            else:
                img = rgb2gray(input_image)

                init = np.array(refPt).reshape(len(refPt), 2)[:, ::-1]

                final_level_set = active_contour_sklearn(gaussian(img, 5, preserve_range=False),
                                                         init, **argument)

                init_ls = np.zeros(img.shape, dtype=np.int8)

                cv2.fillPoly(init_ls, np.array(
                    [np.array(final_level_set[:, ::-1], dtype=np.int32)], dtype=np.int32), 255)

                visual_callback_2d(
                    input_file, input_image / 255)(init_ls)

            plt.close('all')

            plt.imsave(output_file, init_ls)

            print('save')

            # np.set_printoptions(threshold='nan')

            ###
            # mask = np.array(final_level_set, dtype=np.uint8) * 255

            # cv2.imshow("Final Mask", final_level_set * 255.)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            # input_image = imread(input_file)

            # if is_transform:
            #     input_image = cv2.resize(input_image, image_size)
            print('test')

            # cv_image = cv2.cvtColor(
            #     np.array(input_image, dtype=np.uint8), cv2.COLOR_RGB2BGR)

            # src_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            # mask_out = cv2.subtract(src_mask, np.array(cv_image, dtype=np.uint8))
            # cropped_image = cv2.subtract(src_mask, mask_out)

            break
    print('done')
    cv2.destroyAllWindows()

    return final_level_set
