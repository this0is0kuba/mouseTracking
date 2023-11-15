import tkinter as tk
from .parameters import Parameters, State
from .editor import process_image
from .editor import find_magic_points
import os
import re
import pickle


class PaintGUI:

    def __init__(self):

        # root parts:
        self.header = None
        self.entry = None
        self.header_label = None
        self.footer_label = None

        # main parts:
        self.root = tk.Tk()
        self.set_header()

        self.cnv = tk.Canvas(self.root, width=Parameters.WIDTH, height=Parameters.HEIGHT, bg="white")
        self.set_canvas()

        self.set_footer()

        # image info
        self.index = 0
        self.info_about_photo = []  # [(x, y, index) ]
        self.image_size = {"top": Parameters.HEIGHT, "bottom": -1, "left": Parameters.WIDTH, "right": -1}

        # other auxiliary parts:
        self.state = State.SETTING_CLASS_NAME
        self.symbol_name = None
        self.images = []
        self.previous_event = None

        create_directory(Parameters.DIRECTORY)

    def set_header(self):

        self.root.title("Creator of symbols")
        self.root.geometry(str(Parameters.WIDTH + 10) + "x" + str(Parameters.HEIGHT + 110))
        self.root.bind('<Control-s>', self.save_data)
        self.root.bind('<Command-s>', self.save_data)

        self.header = tk.Frame(self.root)
        self.header.columnconfigure(0, weight=1)

        self.header_label = tk.Label(self.header, text="Symbol Class: ", font=("Arial", 18))
        self.header_label.configure(padx=10, pady=10)
        self.header_label.grid(row=0, column=0)

        self.entry = tk.Entry(self.header, font=("Arial", 18))
        self.entry.grid(row=0, column=1)
        self.entry.bind('<Return>', self.on_enter_entry)
        self.entry.bind('<Button-1>', self.on_click_entry)

        self.header.pack()

    def set_canvas(self):

        self.cnv.pack()
        self.cnv.bind("<B1-Motion>", self.paint_circle)
        self.cnv.bind("<ButtonRelease-1>", self.add_img)

    def set_footer(self):

        self.footer_label = tk.Label(self.root, text="Your image will be saved to:  ", font=("Arial", 18))
        self.footer_label.configure(pady=10)
        self.footer_label.pack()

    def paint_circle(self, event):

        if self.state == State.PAINING:

            r = Parameters.RADIUS
            x, y = event.x, event.y

            if not self.if_brush_on_canvas(x, y, r):
                return

            self.change_image_size(x, y)

            if self.previous_event is not None:
                self.interpolation(x, y, r)

            self.cnv.create_oval(x - r, y - r, x + r, y + r, fill='black')

            self.info_about_photo.append((x, y, self.index))

            self.index += 1
            self.previous_event = event

    def interpolation(self, x, y, r):

        x_prev = self.previous_event.x
        y_prev = self.previous_event.y

        points = find_magic_points(x, y, x_prev, y_prev, r)

        if points is not None:
            self.cnv.create_polygon(points)

    def on_enter_entry(self, event):

        symbol_name = self.entry.get().strip()
        symbol_name = re.sub("[\s+]", "", symbol_name)

        if symbol_name != "" and self.entry["state"] == "normal":
            self.set_values(symbol_name)

        elif symbol_name == "" and self.entry["state"] == "normal":
            print("provide appropriate file name!")

        else:
            print("nothing")

    def set_values(self, symbol_name):

        if self.state == State.PAINING:
            self.save_data(None)

        self.entry["state"] = "disabled"
        self.symbol_name = symbol_name
        self.state = State.PAINING

        path = os.path.join(Parameters.DIRECTORY, symbol_name + ".pkl")
        self.footer_label.configure(text="Your image will be saved to: " + path)

    def change_image_size(self, x, y):

        if y < self.image_size["top"]:
            self.image_size["top"] = y

        if y > self.image_size["bottom"]:
            self.image_size["bottom"] = y

        if x < self.image_size["left"]:
            self.image_size["left"] = x

        if x > self.image_size["right"]:
            self.image_size["right"] = x

    def restart_image_size(self):

        self.image_size["top"] = Parameters.HEIGHT
        self.image_size["bottom"] = 0
        self.image_size["left"] = Parameters.WIDTH
        self.image_size["right"] = 0

    def on_click_entry(self, event):

        if self.entry["state"] == "disabled":
            self.entry["state"] = "normal"

    def add_img(self, event):

        if self.state == State.PAINING:

            if not self.image_exits():

                print("You create blank image. It will not be added")
                return

            np_img = process_image(self.info_about_photo, self.image_size)

            self.images.append(np_img)

            self.cnv.delete("all")
            self.index = 0
            self.info_about_photo = []
            self.previous_event = None
            self.restart_image_size()
            print("image has been added")

        else:
            print("Set The Symbol CLass!")

    def image_exits(self):

        if len(self.info_about_photo) > 0:
            return True

        return False

    def if_brush_on_canvas(self, x, y, r):

        if 0 <= x - r and x + r <= Parameters.WIDTH - 1 and 0 <= y - r and y + r < Parameters.HEIGHT - 1:
            return True

        return False

    def save_data(self, event):

        if self.state == State.PAINING:

            path = os.path.join(Parameters.DIRECTORY, self.symbol_name + ".pkl")

            try:
                with open(path, "rb") as f:
                    loaded_images = pickle.load(f)

            except FileNotFoundError:
                loaded_images = []

            images_to_save = loaded_images + self.images

            print("your data has been saved")

            with open(path, "wb") as f:
                pickle.dump(images_to_save, f)

    def start(self):
        self.root.mainloop()


def create_directory(directory):

    if directory and not os.path.exists(directory):
        os.makedirs(directory)
