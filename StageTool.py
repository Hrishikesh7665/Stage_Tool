#Import Modules
from tkinter import filedialog, messagebox
from tkinter.font import BOLD, ITALIC
from click.decorators import command
from PIL import Image
from tkinter import *
import numpy as np
import webbrowser
import struct
import click
import wave
import math
import sys
import cv2
import os

#For Create Button ToolTip
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 160
        y = y + cy + self.widget.winfo_rooty() +24
        self.tipwindow = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=self.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

#Call This Function To Show Button ToolTip
def CreateToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

#Get Path Of Assestes Folder and convert \ to /
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    path_For =  os.path.join(base_path, "Assets", relative_path)
    path_BAk = path_For.replace(os.sep, '/')
    return path_BAk

#MainWindow Icon And Text Editor Icon
icon_1_path = resource_path("Mainicon.png")
icon_2_path = resource_path("Icon2.png")


#Create Main Window
mainWindow = Tk()

#Variables
carrier_Entry = StringVar(mainWindow)
output_Entry = StringVar(mainWindow)
TextFile_Entry =StringVar(mainWindow)
text_editor_data = StringVar(mainWindow)
CheckVar1 = IntVar (mainWindow)
CheckVar2 = IntVar (mainWindow)
filename = ""
output_filename = ""
text_Filename = ""

#don't changes values
num_lsb = 2
bytes_to_recover= 10

#Colours
Home_BACK_COL = "#d0ecfd"
ButtonColour_1 = "#90eebf"
ButtonColour_2 = "#f39797"
ButtonColour_3 = "#E66A82"
Banner_Colour_1 = "#fafad2"
Banner_Colour_2 = "#eee8aa"

mainWindow.configure(bg=Home_BACK_COL)





#Call this function to open tkinter widow in center
def center_window(name,w, h):
    ws = name.winfo_screenwidth()
    hs = name.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)  #change hs/2 to hs/4 to left window up
    name.geometry('%dx%d+%d+%d' % (w, h, x, y))
center_window(mainWindow,400, 400)
mainWindow.title("Stage Tool")
mainWindow.resizable(FALSE,FALSE)

#Main Backend Function Of Hide Image In Image And Extract Image From Image----------------------------
class Steganography(object):
    @staticmethod
    def __int_to_bin(rgb):
        r, g, b = rgb
        return ('{0:08b}'.format(r),
                '{0:08b}'.format(g),
                '{0:08b}'.format(b))

    @staticmethod
    def __bin_to_int(rgb):
        r, g, b = rgb
        return (int(r, 2),
                int(g, 2),
                int(b, 2))

    @staticmethod
    def __merge_rgb(rgb1, rgb2):
        r1, g1, b1 = rgb1
        r2, g2, b2 = rgb2
        rgb = (r1[:4] + r2[:4],g1[:4] + g2[:4],b1[:4] + b2[:4])
        return rgb

    @staticmethod
    def merge(img1, img2):
        # Check the images dimensions
        if img2.size[0] > img1.size[0] or img2.size[1] > img1.size[1]:
            raise ValueError('Image 2 should not be larger than Image 1!')

        # Get the pixel map of the two images
        pixel_map1 = img1.load()
        pixel_map2 = img2.load()

        # Create a new image that will be outputted
        new_image = Image.new(img1.mode, img1.size)
        pixels_new = new_image.load()

        for i in range(img1.size[0]):
            for j in range(img1.size[1]):
                rgb1 = Steganography.__int_to_bin(pixel_map1[i, j])

                # Use a black pixel as default
                rgb2 = Steganography.__int_to_bin((0, 0, 0))

                # Check if the pixel map position is valid for the second image
                if i < img2.size[0] and j < img2.size[1]:
                    rgb2 = Steganography.__int_to_bin(pixel_map2[i, j])

                # Merge the two pixels and convert it to a integer tuple
                rgb = Steganography.__merge_rgb(rgb1, rgb2)

                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

        return new_image

    @staticmethod
    def unmerged(img):

        # Load the pixel map
        pixel_map = img.load()

        # Create the new image and load the pixel map
        new_image = Image.new(img.mode, img.size)
        pixels_new = new_image.load()

        # Tuple used to store the image original size
        original_size = img.size

        for i in range(img.size[0]):
            for j in range(img.size[1]):
                # Get the RGB (as a string tuple) from the current pixel
                r, g, b = Steganography.__int_to_bin(pixel_map[i, j])

                # Extract the last 4 bits (corresponding to the hidden image)
                # Concatenate 4 zero bits because we are working with 8 bit
                rgb = (r[4:] + '0000',g[4:] + '0000',b[4:] + '0000')

                # Convert it to an integer tuple
                pixels_new[i, j] = Steganography.__bin_to_int(rgb)

                # If this is a 'valid' position, store it
                # as the last valid position
                if pixels_new[i, j] != (0, 0, 0):
                    original_size = (i + 1, j + 1)

        # Crop the image based on the 'valid' pixels
        new_image = new_image.crop((0, 0, original_size[0], original_size[1]))

        return new_image

#Call To Merge Image In Image
def merge(img1, img2, output):
    merged_image = Steganography.merge(Image.open(img1), Image.open(img2))
    merged_image.save(output)

#Call To Unmerged Image From Image
def unmerged(img, output):
    unmerged_image = Steganography.unmerged(Image.open(img))
    unmerged_image.save(output)

#Function Of Hinding And Extracting Image From Image End Here----------------------------


#Function To Hide Unhinge Text In Audio File (.wav).
# I failed to convert .mp3 to .wav so currently .wav is supported.

def prepare(sound_path):
    global sound, params, n_frames, n_samples, fmt, mask, smallest_byte
    sound = wave.open(sound_path, "r")

    params = sound.getparams()
    num_channels = sound.getnchannels()
    sample_width = sound.getsampwidth()
    n_frames = sound.getnframes()
    n_samples = n_frames * num_channels

    if (sample_width == 1):  # samples are unsigned 8-bit integers
        fmt = "{}B".format(n_samples)
        # Used to set the least significant num_lsb bits of an integer to zero
        mask = (1 << 8) - (1 << num_lsb)
        # The least possible value for a sample in the sound file is actually
        # zero, but we don't skip any samples for 8 bit depth wav files.
        smallest_byte = -(1 << 8)
    elif (sample_width == 2):  # samples are signed 16-bit integers
        fmt = "{}h".format(n_samples)
        # Used to set the least significant num_lsb bits of an integer to zero
        mask = (1 << 15) - (1 << num_lsb)
        # The least possible value for a sample in the sound file
        smallest_byte = -(1 << 15)
    else:
        # Python's wave module doesn't support higher sample widths
        raise ValueError("File has an unsupported bit-depth")

#Call the function to hide text in audio
def hide_data(sound_path, file_path, output_path):
    global sound, params, n_frames, n_samples, fmt, mask, smallest_byte
    prepare(sound_path)
    # We can hide up to num_lsb bits in each sample of the sound file
    max_bytes_to_hide = (n_samples * num_lsb) // 8
    filesize = os.stat(file_path).st_size

    if (filesize > max_bytes_to_hide):
        required_LSBs = math.ceil(filesize * 8 / n_samples)
        raise ValueError("Input file too large to hide, "
                         "requires {} LSBs, using {}"
                         .format(required_LSBs, num_lsb))


    # Put all the samples from the sound file into a list
    raw_data = list(struct.unpack(fmt, sound.readframes(n_frames)))
    sound.close()

    input_data = memoryview(open(file_path, "rb").read())

    # The number of bits we've processed from the input file
    data_index = 0
    sound_index = 0

    # values will hold the altered sound data
    values = []
    buffer = 0
    buffer_length = 0
    done = False

    while(not done):
        while (buffer_length < num_lsb and data_index // 8 < len(input_data)):
            # If we don't have enough data in the buffer, add the
            # rest of the next byte from the file to it.
            buffer += (input_data[data_index // 8] >> (data_index % 8)
                        ) << buffer_length
            bits_added = 8 - (data_index % 8)
            buffer_length += bits_added
            data_index += bits_added

        # Retrieve the next num_lsb bits from the buffer for use later
        current_data = buffer % (1 << num_lsb)
        buffer >>= num_lsb
        buffer_length -= num_lsb

        while (sound_index < len(raw_data) and raw_data[sound_index] == smallest_byte):
            # If the next sample from the sound file is the smallest possible
            # value, we skip it. Changing the LSB of such a value could cause
            # an overflow and drastically change the sample in the output.
            values.append(struct.pack(fmt[-1], raw_data[sound_index]))
            sound_index += 1

        if (sound_index < len(raw_data)):
            current_sample = raw_data[sound_index]
            sound_index += 1

            sign = 1
            if (current_sample < 0):
                # We alter the LSBs of the absolute value of the sample to
                # avoid problems with two's complement. This also avoids
                # changing a sample to the smallest possible value, which we
                # would skip when attempting to recover data.
                current_sample = -current_sample
                sign = -1

            # Bitwise AND with mask turns the num_lsb least significant bits
            # of current_sample to zero. Bitwise OR with current_data replaces
            # these least significant bits with the next num_lsb bits of data.
            altered_sample = sign * ((current_sample & mask) | current_data)

            values.append(struct.pack(fmt[-1], altered_sample))

        if (data_index // 8 >= len(input_data) and buffer_length <= 0):
            done = True

    while(sound_index < len(raw_data)):
        # At this point, there's no more data to hide. So we append the rest of
        # the samples from the original sound file.
        values.append(struct.pack(fmt[-1], raw_data[sound_index]))
        sound_index += 1

    sound_steg = wave.open(output_path, "w")
    sound_steg.setparams(params)
    sound_steg.writeframes(b"".join(values))
    sound_steg.close()


#Call the function to recover text from audio
def recover_data(sound_path, output_path):
    # Recover data from the file at sound_path to the file at output_path
    global sound, n_frames, n_samples, fmt, smallest_byte,bytes_to_recover
    prepare(sound_path)

    # Put all the samples from the sound file into a list
    raw_data = list(struct.unpack(fmt, sound.readframes(n_frames)))
    # Used to extract the least significant num_lsb bits of an integer
    mask = (1 << num_lsb) - 1
    output_file = open(output_path, "wb+")

    data = bytearray()
    sound_index = 0
    buffer = 0
    buffer_length = 0
    sound.close()

    while (bytes_to_recover > 0):

        next_sample = raw_data[sound_index]
        if (next_sample != smallest_byte):
            # Since we skipped samples with the minimum possible value when
            # hiding data, we do the same here.
            buffer += (abs(next_sample) & mask) << buffer_length
            buffer_length += num_lsb
        sound_index += 1

        while (buffer_length >= 8 and bytes_to_recover > 0):
            # If we have more than a byte in the buffer, add it to data
            # and decrement the number of bytes left to recover.
            current_data = buffer % (1 << 8)
            buffer >>= 8
            buffer_length -= 8
            data += struct.pack('1B', current_data)
            bytes_to_recover -= 1

    output_file.write(bytes(data))
    output_file.close()
#Function To Hide Unhinge Text In Audio File Is End Here--------------------

#Function to hide unhidden text in image file
#convert output file in png format

class SteganographyException(Exception):
    pass


class LSBSteg():
    def __init__(self, im):
        self.image = im
        self.height, self.width, self.nbchannels = im.shape
        self.size = self.width * self.height

        self.maskONEValues = [1,2,4,8,16,32,64,128]
        #Mask used to put one ex:1->00000001, 2->00000010 .. associated with OR bitwise
        self.maskONE = self.maskONEValues.pop(0) #Will be used to do bitwise operations

        self.maskZEROValues = [254,253,251,247,239,223,191,127]
        #Mak used to put zero ex:254->11111110, 253->11111101 .. associated with AND bitwise
        self.maskZERO = self.maskZEROValues.pop(0)

        self.curwidth = 0  # Current width position
        self.curheight = 0 # Current height position
        self.curchan = 0   # Current channel position

    def put_binary_value(self, bits): #Put the bits in the image
        for c in bits:
            val = list(self.image[self.curheight,self.curwidth]) #Get the pixel value as a list
            if int(c) == 1:
                val[self.curchan] = int(val[self.curchan]) | self.maskONE #OR with maskONE
            else:
                val[self.curchan] = int(val[self.curchan]) & self.maskZERO #AND with maskZERO

            self.image[self.curheight,self.curwidth] = tuple(val)
            self.next_slot() #Move "cursor" to the next space

    def next_slot(self):#Move to the next slot were information can be taken or put
        if self.curchan == self.nbchannels-1: #Next Space is the following channel
            self.curchan = 0
            if self.curwidth == self.width-1: #Or the first channel of the next pixel of the same line
                self.curwidth = 0
                if self.curheight == self.height-1:#Or the first channel of the first pixel of the next line
                    self.curheight = 0
                    if self.maskONE == 128: #Mask 1000000, so the last mask
                        raise SteganographyException("No available slot remaining (image filled)")
                    else: #Or instead of using the first bit start using the second and so on..
                        self.maskONE = self.maskONEValues.pop(0)
                        self.maskZERO = self.maskZEROValues.pop(0)
                else:
                    self.curheight +=1
            else:
                self.curwidth +=1
        else:
            self.curchan +=1

    def read_bit(self): #Read a single bit int the image
        val = self.image[self.curheight,self.curwidth][self.curchan]
        val = int(val) & self.maskONE
        self.next_slot()
        if val > 0:
            return "1"
        else:
            return "0"

    def read_byte(self):
        return self.read_bits(8)

    def read_bits(self, nb): #Read the given number of bits
        bits = ""
        for i in range(nb):
            bits += self.read_bit()
        return bits

    def byteValue(self, val):
        return self.binary_value(val, 8)

    def binary_value(self, val, bitsize): #Return the binary value of an int as a byte
        binval = bin(val)[2:]
        if len(binval) > bitsize:
            raise SteganographyException("binary value larger than the expected size")
        while len(binval) < bitsize:
            binval = "0"+binval
        return binval


    def encode_text(self, txt):
        l = len(txt)
        binl = self.binary_value(l, 16) #Length coded on 2 bytes so the text size can be up to 65536 bytes long
        self.put_binary_value(binl) #Put text length coded on 4 bytes
        for char in txt: #And put all the chars
            c = ord(char)
            self.put_binary_value(self.byteValue(c))
        return self.image

    #Call the function to Un-hide text from image
    def decode_text(self):
        ls = self.read_bits(16) #Read the text size in bytes
        l = int(ls,2)
        i = 0
        unhideTxt = ""
        while i < l: #Read all bytes of the text
            tmp = self.read_byte() #So one byte
            i += 1
            unhideTxt += chr(int(tmp,2)) #Every chars concatenated to str
        return unhideTxt

    #Call the function to hide text in image
    def encode_image(self, imtohide):
        w = imtohide.width
        h = imtohide.height
        if self.width*self.height*self.nbchannels < w*h*imtohide.channels:
            raise SteganographyException("Carrier image not big enough to hold all the datas to steganography")
        binw = self.binary_value(w, 16) #Width coded on to byte so width up to 65536
        binh = self.binary_value(h, 16)
        self.put_binary_value(binw) #Put width
        self.put_binary_value(binh) #Put height
        for h in range(imtohide.height): #Iterate the hole image to put every pixel values
            for w in range(imtohide.width):
                for chan in range(imtohide.channels):
                    val = imtohide[h,w][chan]
                    self.put_binary_value(self.byteValue(int(val)))
        return self.image


    def decode_image(self):
        width = int(self.read_bits(16),2) #Read 16bits and convert it in int
        height = int(self.read_bits(16),2)
        unhideimg = np.zeros((width,height, 3), np.uint8) #Create an image in which we will put all the pixels read
        for h in range(height):
            for w in range(width):
                for chan in range(unhideimg.channels):
                    val = list(unhideimg[h,w])
                    val[chan] = int(self.read_byte(),2) #Read the value
                    unhideimg[h,w] = tuple(val)
        return unhideimg

    def encode_binary(self, data):
        l = len(data)
        if self.width*self.height*self.nbchannels < l+64:
            raise SteganographyException("Carrier image not big enough to hold all the datas to steganography")
        self.put_binary_value(self.binary_value(l, 64))
        for byte in data:
            byte = byte if isinstance(byte, int) else ord(byte) # Compat py2/py3
            self.put_binary_value(self.byteValue(byte))
        return self.image

    def decode_binary(self):
        l = int(self.read_bits(64), 2)
        output = b""
        for i in range(l):
            output += bytearray([int(self.read_byte(),2)])
        return output

#Function to hide unhidden text in image file is end here------------------------------
#Backend PART IS END HERE ----------------------------------------------------------------------




#UI Part Start---------------------------------------------------------------
#After Click TextButton On Encode screen
def click_EncodeScreen_Text():
    global filename, output_filename, text_Filename
    #Input File Chouser
    def choose_Input_file():
        global filename
        filename = filedialog.askopenfilename(title = "Select Carrier Image",filetypes = (("jpg files","*.jpg"),("jpeg files","*.jpeg"),("png files","*.png")))
        filename_con = filename.replace('/', '\\')
        carrier_Entry.set(filename_con)
        EncodeFrame_EntryBox1.xview_moveto(1)
        if EncodeFrame_EntryBox1.get() != "":
            EncodeFrame_Button2.config(state=NORMAL)
            EncodeFrame_Button1.config(text="Change")
        else:
            EncodeFrame_Button2.config(state=DISABLED)
            EncodeFrame_Button1.config(text="Select")
            carrier_Entry.set("")
            EncodeFrame_Button5.config(state=DISABLED)

    #Output File Chouser
    def choose_Output_file():
        global output_filename
        foldername = filedialog.askdirectory(title = "Select Output Folder")
        Org_filename = os.path.basename(filename)
        Org_filename = os.path.splitext(Org_filename)[0]
        if foldername != "":
            output_filename = foldername+"/"+Org_filename+"_Encoded.png"
        foldername_con = output_filename.replace('/', '\\')
        output_Entry.set(foldername_con)
        EncodeFrame_EntryBox2.xview_moveto(1)
        if EncodeFrame_EntryBox2.get() != "":
            C1.config(state=NORMAL)
            C2.config(state=NORMAL)
            EncodeFrame_Button2.config(text="Change")
        else:
            C1.config(state=DISABLED)
            C2.config(state=DISABLED)
            EncodeFrame_Button2.config(text="Select")
            output_Entry.set("")
            EncodeFrame_Button5.config(state=DISABLED)


    def main_Text_encode():
        global filename,output_filename,text_Filename
        if EncodeFrame_Button5['text'] == "Encode":
            if CheckVar1.get() == 1:
                try:
                    EncodeFrame_Button5.config(state=DISABLED,text="Reset",bg=ButtonColour_1)
                    EncodeFrame_Button4.config(state=DISABLED)
                    in_img = cv2.imread(filename)
                    steg = LSBSteg(in_img)
                    data = open(text_Filename, "rb").read()
                    res = steg.encode_binary(data)
                    cv2.imwrite(output_filename, res)
                    messagebox.showinfo("Operation Successful","Task Compleat")
                except:
                    messagebox.showerror("Error!!","An Unexpected Error Occurred\nPlease Try Again :-(")
                    EncodeFrame_Button5.config(text="Encode",state=NORMAL,bg=ButtonColour_1)
                    EncodeFrame_Button4.config(state=NORMAL)

            elif CheckVar2.get()  == 1:
                try:
                    EncodeFrame_Button5.config(state=DISABLED,text="Reset",bg=ButtonColour_1)
                    EncodeFrame_Button4.config(state=DISABLED)
                    in_img = cv2.imread(filename)
                    steg = LSBSteg(in_img)
                    data =text_editor_data.get()
                    res = steg.encode_binary(data)
                    cv2.imwrite(output_filename, res)
                    messagebox.showinfo("Operation Successful","Task Compleat")
                except:
                    messagebox.showerror("Error!!","An Unexpected Error Occurred\nPlease Try Again :-(")
                    EncodeFrame_Button5.config(text="Encode",state=NORMAL,bg=ButtonColour_1)
                    EncodeFrame_Button4.config(state=NORMAL)
            EncodeFrame_Button5.config(state=NORMAL)
            EncodeFrame_Button4.config(state=NORMAL)

        elif EncodeFrame_Button5['text'] == "Reset":
            EncodeFrame_Button5.config(text="Encode",bg=ButtonColour_1)
            carrier_Entry.set("")
            output_Entry.set("")
            TextFile_Entry.set("")
            text_editor_data.set("")
            filename = ""
            output_filename = ""
            text_Filename = ""
            CheckVar1.set(0)
            CheckVar2.set(0)
            click_EncodeScreen_Text()

    def back_Btn_Fun():
        global filename,output_filename,text_Filename
        carrier_Entry.set("")
        output_Entry.set("")
        TextFile_Entry.set("")
        text_editor_data.set("")
        filename = ""
        output_filename = ""
        text_Filename = ""
        CheckVar1.set(0)
        CheckVar2.set(0)
        show_EncodeScreen()

    #Show Text File Selection Option
    def select_Text(value):
        global text_Filename
        #Text File Chouser
        def choose_Text_file():
            global text_Filename
            text_Filename = filedialog.askopenfilename(title = "Select Text File",filetypes = (('text files', '*.txt'),))
            filename_con = text_Filename.replace('/', '\\')
            TextFile_Entry.set(filename_con)
            EncodeFrame_EntryBox3.xview_moveto(1)
            if EncodeFrame_EntryBox3.get() != "":
                EncodeFrame_Button5.config(state=NORMAL)
                EncodeFrame_Button3.config(text="Change")
            else:
                EncodeFrame_Button5.config(state=DISABLED)
                EncodeFrame_Button3.config(text="Select")
                TextFile_Entry.set("")


        def get_Editor_Data():
            mainWindow.withdraw()
            def open_file():
                filepath = filedialog.askopenfilename(
                    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
                )
                if not filepath:
                    return
                txt_edit.delete(1.0, END)
                with open(filepath, "r") as input_file:
                    text = input_file.read()
                    txt_edit.insert(END, text)
                window.title(f"Text Editor - {filepath}")

            def save_OK():
                global data
                data = txt_edit.get(1.0, "end-1c")
                window.destroy()
                if data !="":
                    EncodeFrame_Button5.config(state=NORMAL)
                    text_editor_data.set(data)
                else:
                    EncodeFrame_Button5.config(state=DISABLED)
                mainWindow.deiconify()


            def clear_fun():
                txt_edit.delete("1.0","end")

            def cancel_fun():
                window.destroy()
                EncodeFrame_Button5.config(state=DISABLED)
                text_editor_data.set("")
                mainWindow.deiconify()

            def destroy_TOplevel():
                window.destroy()
                mainWindow.deiconify()

            window = Toplevel()
            window.title("Text Editor")
            window.rowconfigure(0, minsize=600, weight=1)
            window.columnconfigure(1, minsize=600, weight=1)
            center_window(window,600, 600)
            txt_edit = Text(window)
            fr_buttons = Frame(window, relief=RAISED, bd=2)
            btn_open = Button(fr_buttons, text="Open", command=open_file)
            btn_save = Button(fr_buttons, text="Ok", command=save_OK)
            btn_clear = Button(fr_buttons, text="Clear", command=clear_fun)
            btn_cancel = Button(fr_buttons, text="Cancel", command=cancel_fun)

            btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            btn_save.grid(row=1, column=0, sticky="ew", padx=5)
            btn_clear.grid(row=2, column=0, sticky="ew", padx=5,pady=5)
            btn_cancel.grid(row=3, column=0, sticky="ew", padx=5)



            fr_buttons.grid(row=0, column=0, sticky="ns")
            txt_edit.grid(row=0, column=1, sticky="nsew")

            if text_editor_data!="":
                txt_edit.insert(END, text_editor_data.get())

            window.tk.call('wm', 'iconphoto', window._w, PhotoImage(file=icon_2_path))
            window.protocol("WM_DELETE_WINDOW", destroy_TOplevel)

        if value == 1:
            if CheckVar1.get() == 1:
                C2.config(state=DISABLED)
                CheckVar2.set(0)
                TextEncodeFrame6.place(x=0,y=245)
                TextEncodeFrame_7.place(x=0,y=280)
                Label(TextEncodeFrame6,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
                Label(TextEncodeFrame6,text="Select Text File",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

                Label(TextEncodeFrame_7,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

                xscrollbar3 = Scrollbar(TextEncodeFrame_7, orient=HORIZONTAL)
                xscrollbar3.pack(side=BOTTOM,fill=BOTH)

                EncodeFrame_EntryBox3 = Entry(TextEncodeFrame_7,cursor='',textvariable=TextFile_Entry,font=("century",13),xscrollcommand=xscrollbar3.set,width=33,state=DISABLED)
                EncodeFrame_EntryBox3.pack(side=LEFT)

                xscrollbar3.config(command=EncodeFrame_EntryBox3.xview)

                Label(TextEncodeFrame_7,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
                EncodeFrame_Button3 = Button(TextEncodeFrame_7,text="Select",font=("arial",12),width=6,height=1,command=choose_Text_file)
                EncodeFrame_Button3.pack(side=RIGHT)


            elif CheckVar1.get() == 0:
                C2.config(state=NORMAL)
                CheckVar2.set(0)
                for i in TextEncodeFrame6.winfo_children():
                    i.destroy()
                for i in TextEncodeFrame_7.winfo_children():
                    i.destroy()
                TextEncodeFrame6.config(bg=Home_BACK_COL)
                TextEncodeFrame_7.config(bg=Home_BACK_COL)
                EncodeFrame_Button5.config(state=DISABLED)
                TextFile_Entry.set("")
                text_editor_data.set("")


        elif value == 2:
            if CheckVar2.get() == 1:
                C1.config(state=DISABLED)
                CheckVar1.set(0)
                TextEncodeFrame6.place(x=70,y=245)
                TextEncodeFrame_7.place(x=130,y=295)
                Label(TextEncodeFrame6,text="Please Open Text Editor And\nEnter Your Text",font=("Lucida Fax",13),bg=Home_BACK_COL).pack()
                Button(TextEncodeFrame_7,text="Open Text Editor",font=("arial",12),command=get_Editor_Data).pack()

            elif CheckVar2.get() == 0:
                C1.config(state=NORMAL)
                CheckVar1.set(0)
                for i in TextEncodeFrame6.winfo_children():
                    i.destroy()
                for i in TextEncodeFrame_7.winfo_children():
                    i.destroy()
                TextEncodeFrame6.config(bg=Home_BACK_COL)
                TextEncodeFrame_7.config(bg=Home_BACK_COL)
                EncodeFrame_Button5.config(state=DISABLED)
                TextFile_Entry.set("")
                text_editor_data.set("")

    for i in mainWindow.winfo_children():
        i.destroy()
    TextEncodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",1),bg=Home_BACK_COL).pack()

    TextEncodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    TextEncodeFrame.pack(side=TOP,anchor=W)
    Label(TextEncodeFrame,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(TextEncodeFrame,text="Carrier Image",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    TextEncodeFrame_2 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(TextEncodeFrame_2,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar = Scrollbar(TextEncodeFrame_2, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar.pack(side=BOTTOM,fill=BOTH)

    EncodeFrame_EntryBox1 = Entry(TextEncodeFrame_2,cursor='',textvariable=carrier_Entry,font=("century",13),xscrollcommand=xscrollbar.set,width=33,state=DISABLED)
    EncodeFrame_EntryBox1.pack(side=LEFT)

    xscrollbar.config(command=EncodeFrame_EntryBox1.xview)

    Label(TextEncodeFrame_2,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button1 = Button(TextEncodeFrame_2,text="Select",font=("arial",12),width=6,height=1,command=choose_Input_file)
    EncodeFrame_Button1.pack(side=RIGHT)

    TextEncodeFrame_2.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack()

    TextEncodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",1),bg=Home_BACK_COL).pack()

    TextEncodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    TextEncodeFrame3.pack(side=TOP,anchor=W)
    Label(TextEncodeFrame3,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(TextEncodeFrame3,text="Output Image",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    TextEncodeFrame_4 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(TextEncodeFrame_4,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar2 = Scrollbar(TextEncodeFrame_4, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar2.pack(side=BOTTOM,fill=BOTH)

    EncodeFrame_EntryBox2 = Entry(TextEncodeFrame_4,cursor='',font=("century",13),width=33,textvariable=output_Entry,xscrollcommand=xscrollbar2.set,state=DISABLED)
    EncodeFrame_EntryBox2.pack(side=LEFT)
    xscrollbar2.config(command=EncodeFrame_EntryBox2.xview)

    Label(TextEncodeFrame_4,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button2 = Button(TextEncodeFrame_4,text="Select",font=("arial",12),width=6,height=1,command=choose_Output_file,state=DISABLED)
    EncodeFrame_Button2.pack(side=RIGHT)

    TextEncodeFrame_4.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",4),bg=Home_BACK_COL).pack()

    TextEncodeFrame_5 = Frame(mainWindow,bg=Home_BACK_COL)

    C1 = Checkbutton(TextEncodeFrame_5,bg=Home_BACK_COL,activebackground=Home_BACK_COL,state=DISABLED, text = "Select A Text File",font=("Lucida Bright",13) ,command=lambda:select_Text(1),variable = CheckVar1,onvalue = 1, offvalue = 0,width=15)
    C1.pack(side=LEFT)
    C2 = Checkbutton(TextEncodeFrame_5,bg=Home_BACK_COL,activebackground=Home_BACK_COL,state=DISABLED, text = "Enter Text Manually",font=("Lucida Bright",13),command=lambda:select_Text(2), variable = CheckVar2,onvalue = 1, offvalue = 0,width=15)
    C2.pack(side=RIGHT)
    TextEncodeFrame_5.pack()

    Label(mainWindow,text="  ",font=("arial",50),bg=Home_BACK_COL).pack()
    TextEncodeFrame6 = Frame(mainWindow)
    #TextEncodeFrame6.place()#pack(side=TOP,anchor=W)
    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()
    TextEncodeFrame_7 = Frame(mainWindow,bg=Home_BACK_COL)

    #pack(side=TOP,anchor=W)


    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()
    TextEncodeFrame_8 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack(side=BOTTOM)
    TextEncodeFrame_8.pack(side=BOTTOM)

    EncodeFrame_Button4 = Button(TextEncodeFrame_8,text="Back",font=("Lucida Bright",14,BOLD,ITALIC),width=12,bg=ButtonColour_2,command=back_Btn_Fun)
    EncodeFrame_Button4.pack(side=LEFT)
    Label(TextEncodeFrame_8,text="      ",font=("arial",10),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button5 = Button(TextEncodeFrame_8,text="Encode",font=("Lucida Bright",14,BOLD,ITALIC),width=12,state=DISABLED,bg=ButtonColour_1,command=main_Text_encode)
    EncodeFrame_Button5.pack(side=LEFT)


def click_Audio_Encode_Screen():
    global filename, output_filename, text_Filename
    #Input File Chouser
    def choose_Input_file():
        global filename
        filename = filedialog.askopenfilename(title = "Select Carrier Audio",filetypes = (("Audio files","*.wav"),))
        filename_con = filename.replace('/', '\\')
        carrier_Entry.set(filename_con)
        EncodeFrame_EntryBox1.xview_moveto(1)
        if EncodeFrame_EntryBox1.get() != "":
            EncodeFrame_Button2.config(state=NORMAL)
            EncodeFrame_Button1.config(text="Change")
        else:
            EncodeFrame_Button2.config(state=DISABLED)
            EncodeFrame_Button1.config(text="Select")
            carrier_Entry.set("")
            EncodeFrame_Button5.config(state=DISABLED)

    #Output File Chouser
    def choose_Output_file():
        global output_filename
        foldername = filedialog.askdirectory(title = "Select Output Folder")
        Org_filename = os.path.basename(filename)
        Org_filename = os.path.splitext(Org_filename)[0]
        if foldername != "":
            output_filename = foldername+"/"+Org_filename+"_Encoded.wav"
        foldername_con = output_filename.replace('/', '\\')
        output_Entry.set(foldername_con)
        EncodeFrame_EntryBox2.xview_moveto(1)
        if EncodeFrame_EntryBox2.get() != "":
            C1.config(state=NORMAL)
            C2.config(state=NORMAL)
            EncodeFrame_Button2.config(text="Change")
        else:
            C1.config(state=DISABLED)
            C2.config(state=DISABLED)
            EncodeFrame_Button2.config(text="Select")
            output_Entry.set("")
            EncodeFrame_Button5.config(state=DISABLED)


    def main_Text_encode():
        global filename,output_filename,text_Filename
        if EncodeFrame_Button5['text'] == "Encode":
            if CheckVar1.get() == 1:
                try:
                    EncodeFrame_Button5.config(state=DISABLED,text="Reset",bg=ButtonColour_1)
                    EncodeFrame_Button4.config(state=DISABLED)
                    hide_data(filename, text_Filename, output_filename)
                    messagebox.showinfo("Operation Successful","Task Compleat")
                except:
                    messagebox.showerror("Error!!","An Unexpected Error Occurred\nPlease Try Again :-(")
                    EncodeFrame_Button5.config(text="Encode",state=NORMAL,bg=ButtonColour_1)
                    EncodeFrame_Button4.config(state=NORMAL)

            elif CheckVar2.get()  == 1:
                try:
                    EncodeFrame_Button5.config(state=DISABLED,text="Reset",bg=ButtonColour_1)
                    EncodeFrame_Button4.config(state=DISABLED)
                    data =text_editor_data.get()
                    f = open("demofile.txt", "w")
                    f.write(data)
                    f.close()
                    hide_data(filename, "demofile.txt", output_filename)
                    messagebox.showinfo("Operation Successful","Task Compleat")
                    os.remove("demofile.txt")
                except :
                    messagebox.showerror("Error!!","An Unexpected Error Occurred\nPlease Try Again :-(")
                    EncodeFrame_Button5.config(text="Encode",state=NORMAL,bg=ButtonColour_1)
                    EncodeFrame_Button4.config(state=NORMAL)
            EncodeFrame_Button5.config(state=NORMAL)
            EncodeFrame_Button4.config(state=NORMAL)

        elif EncodeFrame_Button5['text'] == "Reset":
            EncodeFrame_Button5.config(text="Encode",bg=ButtonColour_1)
            carrier_Entry.set("")
            output_Entry.set("")
            TextFile_Entry.set("")
            text_editor_data.set("")
            filename = ""
            output_filename = ""
            text_Filename = ""
            CheckVar1.set(0)
            CheckVar2.set(0)
            click_Audio_Encode_Screen()

    def back_Btn_Fun():
        global filename,output_filename,text_Filename
        carrier_Entry.set("")
        output_Entry.set("")
        TextFile_Entry.set("")
        text_editor_data.set("")
        filename = ""
        output_filename = ""
        text_Filename = ""
        CheckVar1.set(0)
        CheckVar2.set(0)
        show_EncodeScreen()

    #Show Text File Selection Option
    def select_Text(value):
        global text_Filename
        #Text File Chouser
        def choose_Text_file():
            global text_Filename
            text_Filename = filedialog.askopenfilename(title = "Select Text File",filetypes = (('text files', '*.txt'),))
            filename_con = text_Filename.replace('/', '\\')
            TextFile_Entry.set(filename_con)
            EncodeFrame_EntryBox3.xview_moveto(1)
            if EncodeFrame_EntryBox3.get() != "":
                EncodeFrame_Button5.config(state=NORMAL)
                EncodeFrame_Button3.config(text="Change")
            else:
                EncodeFrame_Button5.config(state=DISABLED)
                EncodeFrame_Button3.config(text="Select")
                TextFile_Entry.set("")


        def get_Editor_Data():
            mainWindow.withdraw()
            def open_file():
                filepath = filedialog.askopenfilename(
                    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
                )
                if not filepath:
                    return
                txt_edit.delete(1.0, END)
                with open(filepath, "r") as input_file:
                    text = input_file.read()
                    txt_edit.insert(END, text)
                window.title(f"Text Editor - {filepath}")

            def save_OK():
                global data
                data = txt_edit.get(1.0, "end-1c")
                window.destroy()
                if data !="":
                    EncodeFrame_Button5.config(state=NORMAL)
                    text_editor_data.set(data)
                else:
                    EncodeFrame_Button5.config(state=DISABLED)
                mainWindow.deiconify()


            def clear_fun():
                txt_edit.delete("1.0","end")

            def cancel_fun():
                window.destroy()
                EncodeFrame_Button5.config(state=DISABLED)
                text_editor_data.set("")
                mainWindow.deiconify()

            def destroy_TOplevel():
                window.destroy()
                mainWindow.deiconify()

            window = Toplevel()
            window.title("Text Editor")
            window.rowconfigure(0, minsize=600, weight=1)
            window.columnconfigure(1, minsize=600, weight=1)
            center_window(window,600, 600)

            txt_edit = Text(window)
            fr_buttons = Frame(window, relief=RAISED, bd=2)
            btn_open = Button(fr_buttons, text="Open", command=open_file)
            btn_save = Button(fr_buttons, text="Ok", command=save_OK)
            btn_clear = Button(fr_buttons, text="Clear", command=clear_fun)
            btn_cancel = Button(fr_buttons, text="Cancel", command=cancel_fun)

            btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
            btn_save.grid(row=1, column=0, sticky="ew", padx=5)
            btn_clear.grid(row=2, column=0, sticky="ew", padx=5,pady=5)
            btn_cancel.grid(row=3, column=0, sticky="ew", padx=5)



            fr_buttons.grid(row=0, column=0, sticky="ns")
            txt_edit.grid(row=0, column=1, sticky="nsew")

            if text_editor_data!="":
                txt_edit.insert(END, text_editor_data.get())

            window.tk.call('wm', 'iconphoto', window._w, PhotoImage(file=icon_2_path))
            window.protocol("WM_DELETE_WINDOW", destroy_TOplevel)

        if value == 1:
            if CheckVar1.get() == 1:
                C2.config(state=DISABLED)
                CheckVar2.set(0)
                AudioEncodeFrame6.place(x=0,y=245)
                AudioEncodeFrame_7.place(x=0,y=280)
                Label(AudioEncodeFrame6,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
                Label(AudioEncodeFrame6,text="Select Text File",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

                Label(AudioEncodeFrame_7,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

                xscrollbar3 = Scrollbar(AudioEncodeFrame_7, orient=HORIZONTAL,bg=Home_BACK_COL)
                xscrollbar3.pack(side=BOTTOM,fill=BOTH)

                EncodeFrame_EntryBox3 = Entry(AudioEncodeFrame_7,cursor='',textvariable=TextFile_Entry,font=("century",13),xscrollcommand=xscrollbar3.set,width=33,state=DISABLED)
                EncodeFrame_EntryBox3.pack(side=LEFT)

                xscrollbar3.config(command=EncodeFrame_EntryBox3.xview)

                Label(AudioEncodeFrame_7,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
                EncodeFrame_Button3 = Button(AudioEncodeFrame_7,text="Select",font=("arial",12),width=6,height=1,command=choose_Text_file)
                EncodeFrame_Button3.pack(side=RIGHT)


            elif CheckVar1.get() == 0:
                C2.config(state=NORMAL)
                CheckVar2.set(0)
                for i in AudioEncodeFrame6.winfo_children():
                    i.destroy()
                for i in AudioEncodeFrame_7.winfo_children():
                    i.destroy()
                EncodeFrame_Button5.config(state=DISABLED)
                TextFile_Entry.set("")
                text_editor_data.set("")
                AudioEncodeFrame_7.config(bg=Home_BACK_COL)
                AudioEncodeFrame6.config(bg=Home_BACK_COL)

        elif value == 2:
            if CheckVar2.get() == 1:
                C1.config(state=DISABLED)
                CheckVar1.set(0)
                AudioEncodeFrame6.place(x=70,y=245)
                AudioEncodeFrame_7.place(x=130,y=295)
                Label(AudioEncodeFrame6,text="Please Open Text Editor And\nEnter Your Text",font=("Lucida Fax",13),bg=Home_BACK_COL).pack()
                Button(AudioEncodeFrame_7,text="Open Text Editor",font=("arial",12),command=get_Editor_Data).pack()

            elif CheckVar2.get() == 0:
                C1.config(state=NORMAL)
                CheckVar1.set(0)
                for i in AudioEncodeFrame6.winfo_children():
                    i.destroy()
                for i in AudioEncodeFrame_7.winfo_children():
                    i.destroy()
                EncodeFrame_Button5.config(state=DISABLED)
                TextFile_Entry.set("")
                text_editor_data.set("")
                AudioEncodeFrame_7.config(bg=Home_BACK_COL)
                AudioEncodeFrame6.config(bg=Home_BACK_COL)

    for i in mainWindow.winfo_children():
        i.destroy()
    AudioEncodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",1),bg=Home_BACK_COL).pack()

    AudioEncodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    AudioEncodeFrame.pack(side=TOP,anchor=W)
    Label(AudioEncodeFrame,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(AudioEncodeFrame,text="Carrier Audio",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    AudioEncodeFrame_2 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(AudioEncodeFrame_2,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar = Scrollbar(AudioEncodeFrame_2, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar.pack(side=BOTTOM,fill=BOTH)

    EncodeFrame_EntryBox1 = Entry(AudioEncodeFrame_2,cursor='',textvariable=carrier_Entry,font=("century",13),xscrollcommand=xscrollbar.set,width=33,state=DISABLED)
    EncodeFrame_EntryBox1.pack(side=LEFT)

    xscrollbar.config(command=EncodeFrame_EntryBox1.xview)

    Label(AudioEncodeFrame_2,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button1 = Button(AudioEncodeFrame_2,text="Select",font=("arial",12),width=6,height=1,command=choose_Input_file)
    EncodeFrame_Button1.pack(side=RIGHT)

    AudioEncodeFrame_2.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack()

    AudioEncodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",1),bg=Home_BACK_COL).pack()

    AudioEncodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    AudioEncodeFrame3.pack(side=TOP,anchor=W)
    Label(AudioEncodeFrame3,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(AudioEncodeFrame3,text="Output Audio",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    AudioEncodeFrame_4 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(AudioEncodeFrame_4,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar2 = Scrollbar(AudioEncodeFrame_4, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar2.pack(side=BOTTOM,fill=BOTH)

    EncodeFrame_EntryBox2 = Entry(AudioEncodeFrame_4,cursor='',font=("century",13),width=33,textvariable=output_Entry,xscrollcommand=xscrollbar2.set,state=DISABLED)
    EncodeFrame_EntryBox2.pack(side=LEFT)
    xscrollbar2.config(command=EncodeFrame_EntryBox2.xview)

    Label(AudioEncodeFrame_4,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button2 = Button(AudioEncodeFrame_4,text="Select",font=("arial",12),width=6,height=1,command=choose_Output_file,state=DISABLED)
    EncodeFrame_Button2.pack(side=RIGHT)

    AudioEncodeFrame_4.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",4),bg=Home_BACK_COL).pack()

    AudioEncodeFrame_5 = Frame(mainWindow,bg=Home_BACK_COL)

    C1 = Checkbutton(AudioEncodeFrame_5,activebackground=Home_BACK_COL,bg=Home_BACK_COL,state=DISABLED, text = "Select A Text File",font=("Lucida Bright",13) ,command=lambda:select_Text(1),variable = CheckVar1,onvalue = 1, offvalue = 0,width=15)
    C1.pack(side=LEFT)
    C2 = Checkbutton(AudioEncodeFrame_5,activebackground=Home_BACK_COL,bg=Home_BACK_COL,state=DISABLED, text = "Enter Text Manually",font=("Lucida Bright",13),command=lambda:select_Text(2), variable = CheckVar2,onvalue = 1, offvalue = 0,width=15)
    C2.pack(side=RIGHT)
    AudioEncodeFrame_5.pack()

    Label(mainWindow,text="  ",font=("arial",50),bg=Home_BACK_COL).pack()
    AudioEncodeFrame6 = Frame(mainWindow,bg=Home_BACK_COL)
    #AudioEncodeFrame6.place()#pack(side=TOP,anchor=W)
    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()
    AudioEncodeFrame_7 = Frame(mainWindow)

    #pack(side=TOP,anchor=W)


    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()
    AudioEncodeFrame_8 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack(side=BOTTOM)
    AudioEncodeFrame_8.pack(side=BOTTOM)

    EncodeFrame_Button4 = Button(AudioEncodeFrame_8,text="Back",font=("Lucida Bright",14,BOLD,ITALIC),width=12,bg=ButtonColour_2,command=back_Btn_Fun)
    EncodeFrame_Button4.pack(side=LEFT)
    Label(AudioEncodeFrame_8,text="      ",font=("arial",10),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button5 = Button(AudioEncodeFrame_8,text="Encode",font=("Lucida Bright",14,BOLD,ITALIC),width=12,state=DISABLED,bg=ButtonColour_1,command=main_Text_encode)
    EncodeFrame_Button5.pack(side=LEFT)


def click_Image_Encode_Screen():
    global filename, output_filename, text_Filename
    #Input File Chouser
    def choose_Input_file():
        global filename
        filename = filedialog.askopenfilename(title = "Select Carrier Image",filetypes = (("jpg files","*.jpg"),("jpeg files","*.jpeg"),("png files","*.png")))
        filename_con = filename.replace('/', '\\')
        carrier_Entry.set(filename_con)
        EncodeFrame_EntryBox1.xview_moveto(1)
        if EncodeFrame_EntryBox1.get() != "":
            EncodeFrame_Button2.config(state=NORMAL)
            EncodeFrame_Button1.config(text="Change")
        else:
            EncodeFrame_Button2.config(state=DISABLED)
            EncodeFrame_Button1.config(text="Select")
            EncodeFrame_Button3.config(state=DISABLED)
            EncodeFrame_Button5.config(state=DISABLED)
            carrier_Entry.set("")
    #Output File Chouser
    def choose_Output_file():
        global output_filename
        foldername = filedialog.askdirectory(title = "Select Output Folder")
        Org_filename = os.path.basename(filename)
        Org_filename = os.path.splitext(Org_filename)[0]
        if foldername != "":
            output_filename = foldername+"/"+Org_filename+"_Encoded.png"
        foldername_con = output_filename.replace('/', '\\')
        output_Entry.set(foldername_con)
        EncodeFrame_EntryBox2.xview_moveto(1)
        if EncodeFrame_EntryBox2.get() != "":
            EncodeFrame_Button2.config(text="Change")
            EncodeFrame_Button3.config(state=NORMAL)
        else:
            EncodeFrame_Button2.config(text="Select")
            EncodeFrame_Button3.config(state=DISABLED)
            EncodeFrame_Button5.config(state=DISABLED)
            output_Entry.set("")

    #Audio File Chouser
    def choose_IN_Image__file():
        global text_Filename
        text_Filename = filedialog.askopenfilename(title = "Select Image File",filetypes = (("jpg files","*.jpg"),("jpeg files","*.jpeg"),("png files","*.png")))
        filename_con = text_Filename.replace('/', '\\')
        TextFile_Entry.set(filename_con)
        EncodeFrame_EntryBox3.xview_moveto(1)
        if EncodeFrame_EntryBox3.get() != "":
            EncodeFrame_Button3.config(text="Change")
            EncodeFrame_Button5.config(state=NORMAL)
        else:
            EncodeFrame_Button3.config(text="Select")
            EncodeFrame_Button5.config(state=DISABLED)
            TextFile_Entry.set("")

    def main_Image_encode():
        global filename,output_filename,text_Filename
        if EncodeFrame_Button5['text'] == "Encode":
            try:
                EncodeFrame_Button5.config(state=DISABLED,text="Reset",bg=ButtonColour_1)
                EncodeFrame_Button4.config(state=DISABLED)
                merge(filename, text_Filename, output_filename)
                messagebox.showinfo("Operation Successful","Task Compleat")
            except:
                messagebox.showerror("Error!!","An Unexpected Error Occurred\nPlease Try Again :-(")
                EncodeFrame_Button5.config(text="Encode",state=NORMAL,bg=ButtonColour_1)
                EncodeFrame_Button4.config(state=NORMAL)
            EncodeFrame_Button5.config(state=NORMAL)
            EncodeFrame_Button4.config(state=NORMAL)
        elif EncodeFrame_Button5['text'] == "Reset":
            EncodeFrame_Button5.config(text="Encode",bg=ButtonColour_1)
            carrier_Entry.set("")
            output_Entry.set("")
            TextFile_Entry.set("")
            text_editor_data.set("")
            filename = ""
            output_filename = ""
            text_Filename = ""
            CheckVar1.set(0)
            CheckVar2.set(0)
            click_Image_Encode_Screen()

    def back_Btn_Fun():
        global filename,output_filename,text_Filename
        carrier_Entry.set("")
        output_Entry.set("")
        TextFile_Entry.set("")
        text_editor_data.set("")
        filename = ""
        output_filename = ""
        text_Filename = ""
        CheckVar1.set(0)
        CheckVar2.set(0)
        show_EncodeScreen()


    for i in mainWindow.winfo_children():
        i.destroy()
    ImageEncodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",10),bg=Home_BACK_COL).pack()

    ImageEncodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    ImageEncodeFrame.pack(side=TOP,anchor=W)
    Label(ImageEncodeFrame,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(ImageEncodeFrame,text="Carrier Image",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    ImageEncodeFrame_2 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(ImageEncodeFrame_2,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar = Scrollbar(ImageEncodeFrame_2, orient=HORIZONTAL)
    xscrollbar.pack(side=BOTTOM,fill=BOTH)

    EncodeFrame_EntryBox1 = Entry(ImageEncodeFrame_2,cursor='',textvariable=carrier_Entry,font=("century",13),xscrollcommand=xscrollbar.set,width=33,state=DISABLED)
    EncodeFrame_EntryBox1.pack(side=LEFT)

    xscrollbar.config(command=EncodeFrame_EntryBox1.xview,bg=Home_BACK_COL)

    Label(ImageEncodeFrame_2,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button1 = Button(ImageEncodeFrame_2,text="Select",font=("arial",12),width=6,height=1,command=choose_Input_file)
    EncodeFrame_Button1.pack(side=RIGHT)

    ImageEncodeFrame_2.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack()

    ImageEncodeFrame3 = Frame(mainWindow)
    Label(mainWindow,text=" ",font=("arial",8),bg=Home_BACK_COL).pack()

    ImageEncodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    ImageEncodeFrame3.pack(side=TOP,anchor=W)
    Label(ImageEncodeFrame3,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(ImageEncodeFrame3,text="Output Image",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    ImageEncodeFrame_4 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(ImageEncodeFrame_4,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar2 = Scrollbar(ImageEncodeFrame_4, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar2.pack(side=BOTTOM,fill=BOTH)

    EncodeFrame_EntryBox2 = Entry(ImageEncodeFrame_4,cursor='',font=("century",13),width=33,textvariable=output_Entry,xscrollcommand=xscrollbar2.set,state=DISABLED)
    EncodeFrame_EntryBox2.pack(side=LEFT)
    xscrollbar2.config(command=EncodeFrame_EntryBox2.xview)

    Label(ImageEncodeFrame_4,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button2 = Button(ImageEncodeFrame_4,text="Select",font=("arial",12),width=6,height=1,state=DISABLED,command=choose_Output_file)
    EncodeFrame_Button2.pack(side=RIGHT)

    ImageEncodeFrame_4.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",10),bg=Home_BACK_COL).pack()

    ImageEncodeFrame_5 = Frame(mainWindow,bg=Home_BACK_COL)
    ImageEncodeFrame_6 = Frame(mainWindow,bg=Home_BACK_COL)


    Label(ImageEncodeFrame_5,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(ImageEncodeFrame_5,text="Hidden Image File",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(ImageEncodeFrame_6,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar3 = Scrollbar(ImageEncodeFrame_6, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar3.pack(side=BOTTOM,fill=BOTH)

    EncodeFrame_EntryBox3 = Entry(ImageEncodeFrame_6,cursor='',textvariable=TextFile_Entry,font=("century",13),xscrollcommand=xscrollbar3.set,width=33,state=DISABLED)
    EncodeFrame_EntryBox3.pack(side=LEFT)

    xscrollbar3.config(command=EncodeFrame_EntryBox3.xview)

    Label(ImageEncodeFrame_6,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button3 = Button(ImageEncodeFrame_6,text="Select",font=("arial",12),width=6,height=1,state=DISABLED,command=choose_IN_Image__file)
    EncodeFrame_Button3.pack(side=RIGHT)

    ImageEncodeFrame_5.pack(side=TOP,anchor=W)
    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack()
    ImageEncodeFrame_6.pack(side=TOP,anchor=W)

    ImageEncodeFrame_7 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack(side=BOTTOM)
    ImageEncodeFrame_7.pack(side=BOTTOM)

    EncodeFrame_Button4 = Button(ImageEncodeFrame_7,text="Back",font=("Lucida Bright",14,BOLD,ITALIC),width=12,bg=ButtonColour_2,command=back_Btn_Fun)
    EncodeFrame_Button4.pack(side=LEFT)
    Label(ImageEncodeFrame_7,text="      ",font=("arial",10),bg=Home_BACK_COL).pack(side=LEFT)
    EncodeFrame_Button5 = Button(ImageEncodeFrame_7,text="Encode",font=("Lucida Bright",14,BOLD,ITALIC),width=12,state=DISABLED,bg=ButtonColour_1,command=main_Image_encode)
    EncodeFrame_Button5.pack(side=LEFT)


def click_DecodeScreen_Text():
    global filename, output_filename, text_Filename
    #Input File Chouser
    def choose_Input_file():
        global filename
        filename = filedialog.askopenfilename(title = "Select Encoded Image",filetypes = (("png files","*.png"),))
        filename_con = filename.replace('/', '\\')
        carrier_Entry.set(filename_con)
        DecodeFrame_EntryBox1.xview_moveto(1)
        if DecodeFrame_EntryBox1.get() != "":
            DecodeFrame_Button2.config(state=NORMAL)
            DecodeFrame_Button1.config(text="Change")
        else:
            DecodeFrame_Button2.config(state=DISABLED)
            DecodeFrame_Button1.config(text="Select")
            carrier_Entry.set("")
            DecodeFrame_Button5.config(state=DISABLED)

    #Output File Chouser
    def choose_Output_file():
        global output_filename
        foldername = filedialog.askdirectory(title = "Select Output Folder")
        Org_filename = os.path.basename(filename)
        Org_filename = os.path.splitext(Org_filename)[0]
        if foldername != "":
            output_filename = foldername+"/"+Org_filename+"_Decoded.txt"
        foldername_con = output_filename.replace('/', '\\')
        output_Entry.set(foldername_con)
        DecodeFrame_EntryBox2.xview_moveto(1)
        if DecodeFrame_EntryBox2.get() != "":
            DecodeFrame_Button2.config(text="Change")
            DecodeFrame_Button5.config(state=NORMAL)
        else:
            DecodeFrame_Button2.config(text="Select")
            output_Entry.set("")
            DecodeFrame_Button5.config(state=DISABLED)


    def main_Text_Decode():
        global filename,output_filename,text_Filename
        if DecodeFrame_Button5['text'] == "Decode":
            try:
                DecodeFrame_Button5.config(state=DISABLED,text="Reset",bg=ButtonColour_1)
                DecodeFrame_Button4.config(state=DISABLED)
                in_img = cv2.imread(filename)
                steg = LSBSteg(in_img)
                raw = steg.decode_binary()
                with open(output_filename, "wb") as f:
                    f.write(raw)
                messagebox.showinfo("Operation Successful","Task Compleat")
                DecodeFrame_Button3.config(state=NORMAL)
                raw = raw.decode("utf-8")
                text_editor_data.set(raw)
            except:
                messagebox.showerror("Error!!","An Unexpected Error Occurred\nPlease Try Again :-(")
                DecodeFrame_Button5.config(text="Decode",state=NORMAL,bg=ButtonColour_1)
                DecodeFrame_Button4.config(state=NORMAL)

            DecodeFrame_Button5.config(state=NORMAL)
            DecodeFrame_Button4.config(state=NORMAL)

        elif DecodeFrame_Button5['text'] == "Reset":
            DecodeFrame_Button5.config(text="Decode",bg=ButtonColour_1)
            carrier_Entry.set("")
            output_Entry.set("")
            TextFile_Entry.set("")
            text_editor_data.set("")
            filename = ""
            output_filename = ""
            text_Filename = ""
            CheckVar1.set(0)
            CheckVar2.set(0)
            click_DecodeScreen_Text()


    def preview_In_text_editor():
        mainWindow.withdraw()
        def save_file():
            filepath = filedialog.asksaveasfilename(
                defaultextension="txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            )
            if not filepath:
                return
            with open(filepath, "w") as output_file:
                text = txt_edit.get(1.0, END)
                output_file.write(text)
            window.title(f"Text Editor - {filepath}")

        def text_edit():
            txt_edit.config(state=NORMAL)
            txt_edit.focus()
            txt_edit.see(END)
            txt_edit.focus_set()

        def close_Editor():
            window.destroy()
            mainWindow.deiconify()

        window = Toplevel()
        window.title("Text Editor")
        window.rowconfigure(0, minsize=600, weight=1)
        window.columnconfigure(1, minsize=600, weight=1)
        center_window(window,600, 600)

        txt_edit = Text(window)
        fr_buttons = Frame(window, relief=RAISED, bd=2)
        btn_save = Button(fr_buttons, text="Save As...", command=save_file)
        btn_Edit = Button(fr_buttons, text="Editing Mode",command=text_edit)
        btn_close = Button(fr_buttons, text="Close", command=close_Editor)


        btn_save.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_Edit.grid(row=1, column=0, sticky="ew", padx=5)
        btn_close.grid(row=2, column=0, sticky="ew", padx=5, pady=5)


        fr_buttons.grid(row=0, column=0, sticky="ns")
        txt_edit.grid(row=0, column=1, sticky="nsew")

        txt_edit.insert(END,text_editor_data.get())
        txt_edit.config(state=DISABLED)

        window.tk.call('wm', 'iconphoto', window._w, PhotoImage(file=icon_2_path))
        window.protocol("WM_DELETE_WINDOW", close_Editor)
        window.mainloop()

    def back_Btn_Fun():
        global filename,output_filename,text_Filename
        carrier_Entry.set("")
        output_Entry.set("")
        TextFile_Entry.set("")
        text_editor_data.set("")
        filename = ""
        output_filename = ""
        text_Filename = ""
        CheckVar1.set(0)
        CheckVar2.set(0)
        show_DecodeScreen()


    for i in mainWindow.winfo_children():
        i.destroy()
    TextDecodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",12),bg=Home_BACK_COL).pack()

    TextDecodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    TextDecodeFrame.pack(side=TOP,anchor=W)
    Label(TextDecodeFrame,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(TextDecodeFrame,text="Encoded Image",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    TextDecodeFrame_2 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(TextDecodeFrame_2,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar = Scrollbar(TextDecodeFrame_2, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar.pack(side=BOTTOM,fill=BOTH)

    DecodeFrame_EntryBox1 = Entry(TextDecodeFrame_2,cursor='',textvariable=carrier_Entry,font=("century",13),xscrollcommand=xscrollbar.set,width=33,state=DISABLED)
    DecodeFrame_EntryBox1.pack(side=LEFT)

    xscrollbar.config(command=DecodeFrame_EntryBox1.xview)

    Label(TextDecodeFrame_2,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button1 = Button(TextDecodeFrame_2,text="Select",font=("arial",12),width=6,height=1,command=choose_Input_file)
    DecodeFrame_Button1.pack(side=RIGHT)

    TextDecodeFrame_2.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack()

    TextDecodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",1),bg=Home_BACK_COL).pack()

    TextDecodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    TextDecodeFrame3.pack(side=TOP,anchor=W)
    Label(TextDecodeFrame3,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(TextDecodeFrame3,text="Output Folder",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    TextDecodeFrame_4 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(TextDecodeFrame_4,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar2 = Scrollbar(TextDecodeFrame_4, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar2.pack(side=BOTTOM,fill=BOTH)

    DecodeFrame_EntryBox2 = Entry(TextDecodeFrame_4,cursor='',font=("century",13),width=33,textvariable=output_Entry,xscrollcommand=xscrollbar2.set,state=DISABLED)
    DecodeFrame_EntryBox2.pack(side=LEFT)
    xscrollbar2.config(command=DecodeFrame_EntryBox2.xview)

    Label(TextDecodeFrame_4,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button2 = Button(TextDecodeFrame_4,text="Select",font=("arial",12),width=6,height=1,command=choose_Output_file,state=DISABLED)
    DecodeFrame_Button2.pack(side=RIGHT)

    TextDecodeFrame_4.pack(side=TOP,anchor=W)

    TextDecodeFrame_5 = Frame(mainWindow,bg=Home_BACK_COL)
    TextDecodeFrame_5.place(x=90,y=230)
    TextDecodeFrame_6 = Frame(mainWindow,bg=Home_BACK_COL)
    TextDecodeFrame_6.place(x=130,y=280)
    Label(TextDecodeFrame_5,text="Preview Decoded Text In\nText Editor",font=("Lucida Fax",13),bg=Home_BACK_COL).pack()
    DecodeFrame_Button3 = Button(TextDecodeFrame_6,text="Open Text Editor",font=("arial",12),command=preview_In_text_editor,state=DISABLED)
    DecodeFrame_Button3.pack()

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()
    TextDecodeFrame_8 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack(side=BOTTOM)
    TextDecodeFrame_8.pack(side=BOTTOM)

    DecodeFrame_Button4 = Button(TextDecodeFrame_8,text="Back",font=("Lucida Bright",14,BOLD,ITALIC),width=12,bg=ButtonColour_2,command=back_Btn_Fun)
    DecodeFrame_Button4.pack(side=LEFT)
    Label(TextDecodeFrame_8,text="      ",font=("arial",10),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button5 = Button(TextDecodeFrame_8,text="Decode",font=("Lucida Bright",14,BOLD,ITALIC),width=12,state=DISABLED,bg=ButtonColour_1,command=main_Text_Decode)
    DecodeFrame_Button5.pack(side=LEFT)

def click_DecodeScreen_Audio():
    global filename, output_filename, text_Filename
    #Input File Chouser
    def choose_Input_file():
        global filename
        filename = filedialog.askopenfilename(title = "Select Encoded Audio",filetypes = (("wav files","*.wav"),))
        filename_con = filename.replace('/', '\\')
        carrier_Entry.set(filename_con)
        DecodeFrame_EntryBox1.xview_moveto(1)
        if DecodeFrame_EntryBox1.get() != "":
            DecodeFrame_Button2.config(state=NORMAL)
            DecodeFrame_Button1.config(text="Change")
        else:
            DecodeFrame_Button2.config(state=DISABLED)
            DecodeFrame_Button1.config(text="Select")
            carrier_Entry.set("")
            DecodeFrame_Button5.config(state=DISABLED)

    #Output File Chouser
    def choose_Output_file():
        global output_filename
        foldername = filedialog.askdirectory(title = "Select Output Folder")
        Org_filename = os.path.basename(filename)
        Org_filename = os.path.splitext(Org_filename)[0]
        if foldername != "":
            output_filename = foldername+"/"+Org_filename+"_Decoded.txt"
        foldername_con = output_filename.replace('/', '\\')
        output_Entry.set(foldername_con)
        DecodeFrame_EntryBox2.xview_moveto(1)
        if DecodeFrame_EntryBox2.get() != "":
            DecodeFrame_Button2.config(text="Change")
            DecodeFrame_Button5.config(state=NORMAL)
        else:
            DecodeFrame_Button2.config(text="Select")
            output_Entry.set("")
            DecodeFrame_Button5.config(state=DISABLED)


    def main_Text_Decode():
        global filename,output_filename,text_Filename
        if DecodeFrame_Button5['text'] == "Decode":
            try:
                DecodeFrame_Button5.config(state=DISABLED,text="Reset",bg=ButtonColour_1)
                DecodeFrame_Button4.config(state=DISABLED)
                recover_data(filename,output_filename)
                f = open(output_filename, "r")
                raw = f.read()
                f.close()
                messagebox.showinfo("Operation Successful","Task Compleat")
                text_editor_data.set(raw)
                DecodeFrame_Button3.config(state=NORMAL)
            except:
                messagebox.showerror("Error!!","An Unexpected Error Occurred\nPlease Try Again :-(")
                DecodeFrame_Button5.config(text="Decode",state=NORMAL,bg=ButtonColour_1)
                DecodeFrame_Button4.config(state=NORMAL)

            DecodeFrame_Button5.config(state=NORMAL)
            DecodeFrame_Button4.config(state=NORMAL)

        elif DecodeFrame_Button5['text'] == "Reset":
            DecodeFrame_Button5.config(text="Decode",bg=ButtonColour_1)
            carrier_Entry.set("")
            output_Entry.set("")
            TextFile_Entry.set("")
            text_editor_data.set("")
            filename = ""
            output_filename = ""
            text_Filename = ""
            CheckVar1.set(0)
            CheckVar2.set(0)
            click_DecodeScreen_Audio()


    def preview_In_text_editor():
        mainWindow.withdraw()
        def save_file():
            filepath = filedialog.asksaveasfilename(
                defaultextension="txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            )
            if not filepath:
                return
            with open(filepath, "w") as output_file:
                text = txt_edit.get(1.0, END)
                output_file.write(text)
            window.title(f"Text Editor - {filepath}")

        def text_edit():
            txt_edit.config(state=NORMAL)
            txt_edit.focus()
            txt_edit.see(END)
            txt_edit.focus_set()

        def close_Editor():
            window.destroy()
            mainWindow.deiconify()

        window = Toplevel()
        window.title("Text Editor")
        window.rowconfigure(0, minsize=600, weight=1)
        window.columnconfigure(1, minsize=600, weight=1)
        center_window(window,600, 600)

        txt_edit = Text(window)
        fr_buttons = Frame(window, relief=RAISED, bd=2)
        btn_save = Button(fr_buttons, text="Save As...", command=save_file)
        btn_Edit = Button(fr_buttons, text="Editing Mode",command=text_edit)
        btn_close = Button(fr_buttons, text="Close", command=close_Editor)


        btn_save.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_Edit.grid(row=1, column=0, sticky="ew", padx=5)
        btn_close.grid(row=2, column=0, sticky="ew", padx=5, pady=5)


        fr_buttons.grid(row=0, column=0, sticky="ns")
        txt_edit.grid(row=0, column=1, sticky="nsew")

        txt_edit.insert(END,text_editor_data.get())
        txt_edit.config(state=DISABLED)

        window.tk.call('wm', 'iconphoto', window._w, PhotoImage(file=icon_2_path))
        window.protocol("WM_DELETE_WINDOW", close_Editor)
        window.mainloop()

    def back_Btn_Fun():
        global filename,output_filename,text_Filename
        carrier_Entry.set("")
        output_Entry.set("")
        TextFile_Entry.set("")
        text_editor_data.set("")
        filename = ""
        output_filename = ""
        text_Filename = ""
        CheckVar1.set(0)
        CheckVar2.set(0)
        show_DecodeScreen()


    for i in mainWindow.winfo_children():
        i.destroy()
    AudioDecodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",12),bg=Home_BACK_COL).pack()

    AudioDecodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    AudioDecodeFrame.pack(side=TOP,anchor=W)
    Label(AudioDecodeFrame,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(AudioDecodeFrame,text="Encoded Audio",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    AudioDecodeFrame_2 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(AudioDecodeFrame_2,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar = Scrollbar(AudioDecodeFrame_2, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar.pack(side=BOTTOM,fill=BOTH)

    DecodeFrame_EntryBox1 = Entry(AudioDecodeFrame_2,cursor='',textvariable=carrier_Entry,font=("century",13),xscrollcommand=xscrollbar.set,width=33,state=DISABLED)
    DecodeFrame_EntryBox1.pack(side=LEFT)

    xscrollbar.config(command=DecodeFrame_EntryBox1.xview)

    Label(AudioDecodeFrame_2,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button1 = Button(AudioDecodeFrame_2,text="Select",font=("arial",12),width=6,height=1,command=choose_Input_file)
    DecodeFrame_Button1.pack(side=RIGHT)

    AudioDecodeFrame_2.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack()

    AudioDecodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",1),bg=Home_BACK_COL).pack()

    AudioDecodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    AudioDecodeFrame3.pack(side=TOP,anchor=W)
    Label(AudioDecodeFrame3,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(AudioDecodeFrame3,text="Output Folder",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    AudioDecodeFrame_4 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(AudioDecodeFrame_4,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar2 = Scrollbar(AudioDecodeFrame_4, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar2.pack(side=BOTTOM,fill=BOTH)

    DecodeFrame_EntryBox2 = Entry(AudioDecodeFrame_4,cursor='',font=("century",13),width=33,textvariable=output_Entry,xscrollcommand=xscrollbar2.set,state=DISABLED)
    DecodeFrame_EntryBox2.pack(side=LEFT)
    xscrollbar2.config(command=DecodeFrame_EntryBox2.xview)

    Label(AudioDecodeFrame_4,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button2 = Button(AudioDecodeFrame_4,text="Select",font=("arial",12),width=6,height=1,command=choose_Output_file,state=DISABLED)
    DecodeFrame_Button2.pack(side=RIGHT)

    AudioDecodeFrame_4.pack(side=TOP,anchor=W)

    AudioDecodeFrame_5 = Frame(mainWindow,bg=Home_BACK_COL)
    AudioDecodeFrame_5.place(x=90,y=230)
    AudioDecodeFrame_6 = Frame(mainWindow,bg=Home_BACK_COL)
    AudioDecodeFrame_6.place(x=130,y=280)
    Label(AudioDecodeFrame_5,text="Preview Decoded Text In\nText Editor",font=("Lucida Fax",13),bg=Home_BACK_COL).pack()
    DecodeFrame_Button3 = Button(AudioDecodeFrame_6,text="Open Text Editor",font=("arial",12),command=preview_In_text_editor,state=DISABLED)
    DecodeFrame_Button3.pack()

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()
    AudioDecodeFrame_8 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack(side=BOTTOM)
    AudioDecodeFrame_8.pack(side=BOTTOM)

    DecodeFrame_Button4 = Button(AudioDecodeFrame_8,text="Back",font=("Lucida Bright",14,BOLD,ITALIC),width=12,bg=ButtonColour_2,command=back_Btn_Fun)
    DecodeFrame_Button4.pack(side=LEFT)
    Label(AudioDecodeFrame_8,text="      ",font=("arial",10),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button5 = Button(AudioDecodeFrame_8,text="Decode",font=("Lucida Bright",14,BOLD,ITALIC),width=12,state=DISABLED,bg=ButtonColour_1,command=main_Text_Decode)
    DecodeFrame_Button5.pack(side=LEFT)

def click_DecodeScreen_Image():
    global filename, output_filename, text_Filename
    #Input File Chouser
    def choose_Input_file():
        global filename
        filename = filedialog.askopenfilename(title = "Select Encoded Image",filetypes = (("png files","*.png"),))
        filename_con = filename.replace('/', '\\')
        carrier_Entry.set(filename_con)
        DecodeFrame_EntryBox1.xview_moveto(1)
        if DecodeFrame_EntryBox1.get() != "":
            DecodeFrame_Button2.config(state=NORMAL)
            DecodeFrame_Button1.config(text="Change")
        else:
            DecodeFrame_Button2.config(state=DISABLED)
            DecodeFrame_Button1.config(text="Select")
            carrier_Entry.set("")
            DecodeFrame_Button5.config(state=DISABLED)

    #Output File Chouser
    def choose_Output_file():
        global output_filename
        foldername = filedialog.askdirectory(title = "Select Output Folder")
        Org_filename = os.path.basename(filename)
        Org_filename = os.path.splitext(Org_filename)[0]
        if foldername != "":
            output_filename = foldername+"/"+Org_filename+"_Decoded.png"
        foldername_con = output_filename.replace('/', '\\')
        output_Entry.set(foldername_con)
        DecodeFrame_EntryBox2.xview_moveto(1)
        if DecodeFrame_EntryBox2.get() != "":
            DecodeFrame_Button2.config(text="Change")
            DecodeFrame_Button5.config(state=NORMAL)
        else:
            DecodeFrame_Button2.config(text="Select")
            output_Entry.set("")
            DecodeFrame_Button5.config(state=DISABLED)


    def main_Text_Decode():
        global filename,output_filename,text_Filename
        if DecodeFrame_Button5['text'] == "Decode":
            try:
                DecodeFrame_Button5.config(state=DISABLED,text="Reset",bg=ButtonColour_1)
                DecodeFrame_Button4.config(state=DISABLED)
                unmerged(filename, output_filename)
                messagebox.showinfo("Operation Successful","Task Compleat")
                DecodeFrame_Button3.config(state=NORMAL)
            except Exception as E:
                print(E)
                messagebox.showerror("Error!!","An Unexpected Error Occurred\nPlease Try Again :-(")
                DecodeFrame_Button5.config(text="Decode",state=NORMAL,bg=ButtonColour_1)
                DecodeFrame_Button4.config(state=NORMAL)

            DecodeFrame_Button5.config(state=NORMAL)
            DecodeFrame_Button4.config(state=NORMAL)

        elif DecodeFrame_Button5['text'] == "Reset":
            DecodeFrame_Button5.config(text="Decode",bg=ButtonColour_1)
            carrier_Entry.set("")
            output_Entry.set("")
            TextFile_Entry.set("")
            text_editor_data.set("")
            filename = ""
            output_filename = ""
            text_Filename = ""
            CheckVar1.set(0)
            CheckVar2.set(0)
            click_DecodeScreen_Image()

    def preview_Image():
        image = Image.open(output_filename)
        image.show()

    def back_Btn_Fun():
        global filename,output_filename,text_Filename
        carrier_Entry.set("")
        output_Entry.set("")
        TextFile_Entry.set("")
        text_editor_data.set("")
        filename = ""
        output_filename = ""
        text_Filename = ""
        CheckVar1.set(0)
        CheckVar2.set(0)
        show_DecodeScreen()


    for i in mainWindow.winfo_children():
        i.destroy()
    ImageDecodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",12),bg=Home_BACK_COL).pack()

    ImageDecodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    ImageDecodeFrame.pack(side=TOP,anchor=W)
    Label(ImageDecodeFrame,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(ImageDecodeFrame,text="Encoded Image",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    ImageDecodeFrame_2 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(ImageDecodeFrame_2,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar = Scrollbar(ImageDecodeFrame_2, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar.pack(side=BOTTOM,fill=BOTH)

    DecodeFrame_EntryBox1 = Entry(ImageDecodeFrame_2,cursor='',textvariable=carrier_Entry,font=("century",13),xscrollcommand=xscrollbar.set,width=33,state=DISABLED)
    DecodeFrame_EntryBox1.pack(side=LEFT)

    xscrollbar.config(command=DecodeFrame_EntryBox1.xview)

    Label(ImageDecodeFrame_2,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button1 = Button(ImageDecodeFrame_2,text="Select",font=("arial",12),width=6,height=1,command=choose_Input_file)
    DecodeFrame_Button1.pack(side=RIGHT)

    ImageDecodeFrame_2.pack(side=TOP,anchor=W)

    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack()

    ImageDecodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text=" ",font=("arial",1),bg=Home_BACK_COL).pack()

    ImageDecodeFrame3 = Frame(mainWindow,bg=Home_BACK_COL)
    ImageDecodeFrame3.pack(side=TOP,anchor=W)
    Label(ImageDecodeFrame3,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    Label(ImageDecodeFrame3,text="Output Folder",font=("Calisto MT",14,BOLD),relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2).pack(side=LEFT)

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()

    ImageDecodeFrame_4 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(ImageDecodeFrame_4,text="    ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)

    xscrollbar2 = Scrollbar(ImageDecodeFrame_4, orient=HORIZONTAL,bg=Home_BACK_COL)
    xscrollbar2.pack(side=BOTTOM,fill=BOTH)

    DecodeFrame_EntryBox2 = Entry(ImageDecodeFrame_4,cursor='',font=("century",13),width=33,textvariable=output_Entry,xscrollcommand=xscrollbar2.set,state=DISABLED)
    DecodeFrame_EntryBox2.pack(side=LEFT)
    xscrollbar2.config(command=DecodeFrame_EntryBox2.xview)

    Label(ImageDecodeFrame_4,text="      ",font=("arial",4),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button2 = Button(ImageDecodeFrame_4,text="Select",font=("arial",12),width=6,height=1,command=choose_Output_file,state=DISABLED)
    DecodeFrame_Button2.pack(side=RIGHT)

    ImageDecodeFrame_4.pack(side=TOP,anchor=W)

    ImageDecodeFrame_5 = Frame(mainWindow,bg=Home_BACK_COL)
    ImageDecodeFrame_5.place(x=60,y=230)
    ImageDecodeFrame_6 = Frame(mainWindow,bg=Home_BACK_COL)
    ImageDecodeFrame_6.place(x=110,y=280)
    Label(ImageDecodeFrame_5,text="Preview Image In Your Default\nImage Viewer",font=("Lucida Fax",13),bg=Home_BACK_COL).pack()
    DecodeFrame_Button3 = Button(ImageDecodeFrame_6,text="Open In Image Viewer",font=("arial",12),command=preview_Image,state=DISABLED)
    DecodeFrame_Button3.pack()

    Label(mainWindow,text="  ",font=("arial",1),bg=Home_BACK_COL).pack()
    ImageDecodeFrame_8 = Frame(mainWindow,bg=Home_BACK_COL)
    Label(mainWindow,text="  ",font=("arial",2),bg=Home_BACK_COL).pack(side=BOTTOM)
    ImageDecodeFrame_8.pack(side=BOTTOM)

    DecodeFrame_Button4 = Button(ImageDecodeFrame_8,text="Back",font=("Lucida Bright",14,BOLD,ITALIC),width=12,bg=ButtonColour_2,command=back_Btn_Fun)
    DecodeFrame_Button4.pack(side=LEFT)
    Label(ImageDecodeFrame_8,text="      ",font=("arial",10),bg=Home_BACK_COL).pack(side=LEFT)
    DecodeFrame_Button5 = Button(ImageDecodeFrame_8,text="Decode",font=("Lucida Bright",14,BOLD,ITALIC),width=12,state=DISABLED,bg=ButtonColour_1,command=main_Text_Decode)
    DecodeFrame_Button5.pack(side=LEFT)


def show_About():

    def HomeBtn_on_enter(e):
        HomeBtn.config(foreground= "Blue")
    def HomeBtn_on_leave(e):
        HomeBtn.config(foreground= "Black")

    def GITBtn_on_enter(e):
        GITBtn.config(foreground= "Red")
    def GITBtn_on_leave(e):
        GITBtn.config(foreground= "Blue")

    for i in mainWindow.winfo_children():
        i.destroy()
    AboutFrame = Frame(mainWindow,bg=Home_BACK_COL)
    About_banner_Frame = Frame(mainWindow,bd=5,relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2)

    Label(mainWindow,text=" ",font=("arial",2),bg=Home_BACK_COL).pack()
    About_Banner = Label(About_banner_Frame,text=" Stage Tool ",font=("elephant",35,ITALIC,UNDERLINE),bg=Banner_Colour_1)
    About_Banner.pack()
    Label(About_banner_Frame,text=" ",font=("arial",2),bg=Banner_Colour_1).pack()
    About_Description = Label(About_banner_Frame,text="A Steganography Tool That Allow\nUser To Hide Text & Text File\nBehind An Image & An Audio\nFile, It Also Allow You To Hide\nAn Image Behind An Image File.\nIt Use Least Significant Bit\n(LSB) Method To Hide Data\nBehind An Image Or Audio File.",font=("Lucida Calligraphy",14,ITALIC),bg=Banner_Colour_1)
    About_Description.pack()
    Label(About_banner_Frame,text=" ",font=("Lucida Calligraphy",4,ITALIC),bg=Banner_Colour_1).pack()
    About_Description2 = Label(About_banner_Frame,text=" Developed By ",font=("Lucida Calligraphy",14,ITALIC,UNDERLINE),bg=Banner_Colour_1)
    About_Description2.pack()
    About_Description3 = Label(About_banner_Frame,text="~Hrishikesh Patra  ",font=("Lucida Calligraphy",14),bg=Banner_Colour_1)
    About_Description3.pack()
    About_banner_Frame.pack()

    Label(AboutFrame,text="  ",background=Home_BACK_COL).pack(side=LEFT)
    HomeBtn = Button(AboutFrame,text="Back To Home",font=("Copperplate Gothic Bold",10),borderwidth=0, relief=SUNKEN,background=Home_BACK_COL,activebackground=Home_BACK_COL,command=show_HomeScreen)
    HomeBtn.pack(side=LEFT)
    HomeBtn.bind('<Enter>', HomeBtn_on_enter)
    HomeBtn.bind('<Leave>', HomeBtn_on_leave)
    Label(AboutFrame,text="                                                  ",background=Home_BACK_COL).pack(side=LEFT)
    GITBtn = Button(AboutFrame,text="Hrishikesh Patra",font=("Javanese Text",10,ITALIC),borderwidth=0, relief=SUNKEN,background=Home_BACK_COL,fg="blue",activebackground=Home_BACK_COL,command=lambda:(webbrowser.open('https://github.com/Hrishikesh7665')))
    GITBtn.pack(side=RIGHT)
    GITBtn.bind('<Enter>', GITBtn_on_enter)
    GITBtn.bind('<Leave>', GITBtn_on_leave)
    AboutFrame.pack(side=LEFT)

#After Click Encodebutton from home screen
def show_EncodeScreen():
    for i in mainWindow.winfo_children():
        i.destroy()
    EncodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    encode_banner_Frame = Frame(mainWindow,bd=5,relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2)

    Label(mainWindow,text=" ",font=("arial",2),bg=Home_BACK_COL).pack()

    Label(encode_banner_Frame,text=" ",font=("elephant",1,ITALIC),bg=Banner_Colour_1).pack()
    Encode_Banner = Label(encode_banner_Frame,text=" Encode ",font=("elephant",35,ITALIC,UNDERLINE),bg=Banner_Colour_1)
    Encode_Banner.pack()
    Label(encode_banner_Frame,text=" ",font=("arial",2),bg=Banner_Colour_1).pack()
    encode_Description = Label(encode_banner_Frame,text="Hide Text Text-File In Image\n& Audio File Also Image In Image",font=("Lucida Calligraphy",14,ITALIC),bg=Banner_Colour_1)
    encode_Description.pack()
    encode_banner_Frame.pack()

    Label(EncodeFrame,text=" ",font=("arial",8),bg=Home_BACK_COL).pack()
    Text_button = Button(EncodeFrame,text="Text/Text File",font=("Lucida Bright",14,BOLD,ITALIC),width=12,command=click_EncodeScreen_Text,bg=ButtonColour_1)
    Text_button.pack()
    CreateToolTip(Text_button, text = "Encode Text Or Text File\nBehind An Image File")
    Label(EncodeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    Audio_button = Button(EncodeFrame,text="Audio",font=("Lucida Bright",14,BOLD,ITALIC),width=12,command=click_Audio_Encode_Screen,bg=ButtonColour_1)
    Audio_button.pack()
    CreateToolTip(Audio_button, text = "Encode Text Or Text File\nBehind An Audio File")
    Label(EncodeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    Image_button = Button(EncodeFrame,text="Image",font=("Lucida Bright",14,BOLD,ITALIC),width=12,command=click_Image_Encode_Screen,bg=ButtonColour_1)
    Image_button.pack()
    CreateToolTip(Image_button, text = "Encode An Image File\nBehind An Image File")
    Label(EncodeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    Back_button = Button(EncodeFrame,text="Back",font=("Lucida Bright",14,BOLD,ITALIC),width=12,command=show_HomeScreen,bg=ButtonColour_2)
    Back_button.pack()
    CreateToolTip(Back_button, text = "Back To Home Screen")

    EncodeFrame.pack()


def show_DecodeScreen():
    for i in mainWindow.winfo_children():
        i.destroy()
    DecodeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    Decode_banner_Frame = Frame(mainWindow,bd=5,relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2)

    Label(mainWindow,text=" ",font=("arial",2),bg=Home_BACK_COL).pack()

    Label(Decode_banner_Frame,text=" ",font=("elephant",1,ITALIC),bg=Banner_Colour_1).pack()
    Decode_Banner = Label(Decode_banner_Frame,text=" Decode ",font=("elephant",35,ITALIC,UNDERLINE),bg=Banner_Colour_1)
    Decode_Banner.pack()
    Label(Decode_banner_Frame,text=" ",font=("arial",2),bg=Banner_Colour_1).pack()
    Decode_Description = Label(Decode_banner_Frame,text="Extract Text From Image & Audio\nFile Also Image From Image",font=("Lucida Calligraphy",14,ITALIC),bg=Banner_Colour_1)
    Decode_Description.pack()
    Decode_banner_Frame.pack()

    Label(DecodeFrame,text=" ",font=("arial",8),bg=Home_BACK_COL).pack()
    Text_button = Button(DecodeFrame,text="Text/Text File",font=("Lucida Bright",14,BOLD,ITALIC),width=12,command=click_DecodeScreen_Text,bg=ButtonColour_1)
    Text_button.pack()
    CreateToolTip(Text_button, text = "Extract Text or Text Document\nFrom Image File")
    Label(DecodeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    Audio_button = Button(DecodeFrame,text="Audio",font=("Lucida Bright",14,BOLD,ITALIC),width=12,command=click_DecodeScreen_Audio,bg=ButtonColour_1)
    Audio_button.pack()
    CreateToolTip(Audio_button, text = "Extract Text or Text Document\nFrom Audio File")
    Label(DecodeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    Image_button = Button(DecodeFrame,text="Image",font=("Lucida Bright",14,BOLD,ITALIC),width=12,command=click_DecodeScreen_Image,bg=ButtonColour_1)
    Image_button.pack()
    CreateToolTip(Image_button, text = "Extract Encoded Image\nFrom Image File")
    Label(DecodeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    Back_button = Button(DecodeFrame,text="Back",font=("Lucida Bright",14,BOLD,ITALIC),width=12,command=show_HomeScreen,bg=ButtonColour_2)
    Back_button.pack()
    CreateToolTip(Back_button, text = "Back To Home Screen")

    DecodeFrame.pack()


def exit_CON():
    a = messagebox.askquestion("Exit!!","Are You Sure ??")
    if a == "yes":
        mainWindow.destroy()

#Home screen
def show_HomeScreen():
    for i in mainWindow.winfo_children():
        i.destroy()
    homeFrame = Frame(mainWindow,bg=Home_BACK_COL)
    home_banner_Frame = Frame(mainWindow,bd=5,relief=RAISED,bg=Banner_Colour_1,highlightthickness=3,highlightbackground=Banner_Colour_2)

    Label(mainWindow,text=" ",font=("arial",2),bg=Home_BACK_COL).pack()

    Label(home_banner_Frame,text=" ",font=("elephant",1,ITALIC),bg=Banner_Colour_1).pack()
    Home_Banner = Label(home_banner_Frame,text=" Stage Tool ",font=("elephant",35,ITALIC,UNDERLINE),bg=Banner_Colour_1)
    Home_Banner.pack()
    Label(home_banner_Frame,text=" ",font=("arial",2),bg=Banner_Colour_1).pack()
    Home_Description = Label(home_banner_Frame,text="Hide Un-hide Text Text-File In Image\n& Audio File Also Image In Image",font=("Lucida Calligraphy",13,ITALIC),bg=Banner_Colour_1)
    Home_Description.pack()
    home_banner_Frame.pack()


    Label(homeFrame,text=" ",font=("arial",8),bg=Home_BACK_COL).pack()
    Encode_button = Button(homeFrame,text="Encode",font=("Lucida Bright",14,BOLD,ITALIC),width=11,bg=ButtonColour_1,command=show_EncodeScreen)
    Encode_button.pack()
    Label(homeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    Decode_button = Button(homeFrame,text="Decode",font=("Lucida Bright",14,BOLD,ITALIC),width=11,bg=ButtonColour_1,command=show_DecodeScreen)
    Decode_button.pack()
    Label(homeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    About_button = Button(homeFrame,text="About",font=("Lucida Bright",14,BOLD,ITALIC),width=11,bg=ButtonColour_1,command=show_About)
    About_button.pack()
    Label(homeFrame,text=" ",font=("arial",4),bg=Home_BACK_COL).pack()
    Exit_button = Button(homeFrame,text="Exit",font=("Lucida Bright",14,BOLD,ITALIC),width=11,bg=ButtonColour_2,command=exit_CON)
    Exit_button.pack()
    homeFrame.pack()


mainWindow.protocol("WM_DELETE_WINDOW", exit_CON)
mainWindow.tk.call('wm', 'iconphoto', mainWindow._w, PhotoImage(file=icon_1_path))
#UI PART END HERE----------------------------------------------------------------


#CAll THE MAIN Function--------
if __name__ == "__main__":
    show_HomeScreen()
    mainWindow.mainloop()