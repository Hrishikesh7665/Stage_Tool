[![](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![](https://img.shields.io/badge/Supported%20OS-Windows-blue)](https://www.microsoft.com/en-in/software-download/windows10)


# Stage Tool
A Simple GUI Based Steganography (LSB-Method) Tool For Hide-Unhide (Encode-Decode) Text From Image & Audio File. Also, Hide Image Behind An Image & Extract It.

**Made In Python(3.9.5) With Tkinter GUI**

## Usage

1. Hide Text or Text File Behind Any Simple Image (.jpg, .jpeg., .png). 
2. Hide Text or Text File Behind Audio (.wav).
3. Hide A Secret Image Behind Another Simple Image (.jpg, .jpeg., .png).
4. Extract Text or Text File From Image (.png). 
5. Extract Text or Text File From Audio (.wav). 
6. Extract The Secret Image From Carrier Image (.png).


## Features 

1. Simple & Clean UI.
2. Inbuilt Text Editor For Writing Text Or Preview Text After Extracting.
3. Easy To Use.


## Requirements

- opencv-python
- pillow
- click
- numpy
- wave


## Installation

- Download Repository

`Direct Download Zip` [Click Here](https://codeload.github.com/Hrishikesh7665/Stage_Tool/zip/refs/heads/main)

- Or

- Clone Repository

```
git clone https://github.com/Hrishikesh7665/Stage_Tool.git
```

- Install Required Modules

```
pip install opencv-python
```
```
pip install pillow
```
```
pip install click
```
```
pip install numpy
```
```
pip install wave
```

- Or

```
pip install -r requirements.txt
```

- Run

```
python "StageTool.py"
```



## Documentation

What Is Steganography
=====================

Steganography is the technique of hiding secret data within an ordinary, non-secret, file or message in order to avoid detection. Here we mainly use Image and Audio steganography.
			The image steganography is the process in which we hide the data within an image so that there will not be any perceived visible change in the original image. The conventional image steganography algorithm is LSB embedding algorithm.


Least Significant Bit (LSB)
===========================

I used the most basic method which is the least significant bit. A colour pixel is composed of red, green and blue, encoded on one byte. The idea is to store information in the first bit of every pixel's RGB component. In the worst case, the decimal value is different by one which is not visible to the human eye. In practice, if you don't have space to store all of your data in the first bit of every pixel you should start using the second bit, and so on. You have to keep in mind that the more your store data in an image. Store less data in a single image to avoid detection.

How It Works
------------

Hide text or text data behind in an image function in this program is based on OpenCV to hide data in images. It uses the first bit of every pixel, and every colour of an image. The code is quite simple to understand; If every first bit has been used, the module starts using the second bit, so the larger the data, the more the image is altered.
