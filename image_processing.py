from typing import Tuple

import cv2
import numpy as np
import matplotlib.pyplot as plt


blue_hue = 179
red_hue = 122
yellow_hue = 92


def debug_left_right_image(img: np.ndarray):
    """
    https://i0.wp.com/mediabiasfactcheck.com/wp-content/uploads/2016/12/extremeright021.png
    :param img:
    :return:
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    mask_blue = hsv_mask(img, blue_hue)
    mask_red = hsv_mask(img, red_hue)
    mask_yellow = hsv_mask(img, yellow_hue)
    result_blue = cv2.bitwise_and(img, img, mask=mask_blue)
    result_red = cv2.bitwise_and(img, img, mask=mask_red)
    result_yellow = cv2.bitwise_and(img, img, mask=mask_yellow)
    plt.subplot(2, 2, 1)
    plt.imshow(img)
    plt.subplot(2, 2, 2)
    plt.imshow(result_blue)
    plt.subplot(2, 2, 3)
    plt.imshow(result_red)
    plt.subplot(2, 2, 4)
    plt.imshow(result_yellow)
    plt.show()
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    print("blue", hsv_img[38, 34])
    print("red", hsv_img[38, 590])
    print("yellow", hsv_img[38, 574])


def hsv_mask(img: np.ndarray, hue):
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    light_colour = (hue - 10, 120, 120)
    dark_colour = (hue + 10, 255, 255)
    return cv2.inRange(hsv_img, light_colour, dark_colour)


def centroid(binary: np.ndarray) -> Tuple[int, int]:
    """
    Calculates the centroid of a single binary blob.
    :param binary:
    :return:
    """
    # calculate moments of binary image
    m = cv2.moments(binary)

    # calculate x,y coordinate of center
    c_x = int(m["m10"] / m["m00"])
    c_y = int(m["m01"] / m["m00"])

    return c_x, c_y


def left_most(binary: np.ndarray, reverse=False) -> Tuple[int, int]:
    """
    Gets the leftmost pixel in a binary image.
    :param binary:
    :param reverse:
    :return:
    """
    h, w = binary.shape

    for x in range(w):
        if reverse:
            x = w - x - 1
        for y in range(h):
            if binary[y, x] > 0:
                return x, y

    raise AttributeError('Image is black')


def right_most(binary: np.ndarray) -> Tuple[int, int]:
    """
    Gets the rightmost pixel in a binary image.
    :param binary:
    :return:
    """
    return left_most(binary, True)


def analyse_left_right_image(img: np.ndarray) -> int:
    """

    :param img: The image to analyse
    :return: The left right bias in the range [-50, 50]
    """
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    mask_blue = hsv_mask(img, blue_hue)
    mask_red = hsv_mask(img, red_hue)
    mask_yellow = hsv_mask(img, yellow_hue)
    x_centre, _ = centroid(mask_yellow)
    x_left, _ = left_most(mask_blue)
    x_right, _ = right_most(mask_red)

    value = x_centre - x_left
    domain = x_right - x_left
    bias = round(value / domain * 100) - 50
    return max(-50, min(bias, 50))
