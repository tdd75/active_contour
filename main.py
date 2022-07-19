from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd
from tkinter import Menu
from tkinter import ttk
from tkinter.ttk import *
import numpy as np
import random
import csv
import time
import math
import os

from active_contour import active_contour


class GeneralUserInterface:
    def __init__(self, title, w, h):
        self.window = Tk()
        self.window.title(title)
        self.window.geometry('{0}x{1}'.format(w, h))

    def block_entry(self, nameTab, label, row, column, isVertical=0, placeholder=''):
        """
        generate normal type (label: entry)
        isVertical : int (1 <=> vertical)
        """
        Label(nameTab, text=label).grid(
            column=column, row=row, sticky=W, pady=5)
        entry = Entry(nameTab)

        if isVertical == 1:
            entry.grid(column=column, row=row + 1, sticky=W)
        else:
            entry.grid(column=column + 1, row=row, sticky=W)
        entry.insert(END, placeholder)

        return entry

    def block_combo(self, name_tab, label, row, column, values, default_position=0):
        """
        generate combo type (label: combo)
        isVertical : int (1 <=> vertical)
        """

        Label(name_tab, text=label).grid(column=column, row=row)
        combo = Combobox(name_tab)
        combo['values'] = values
        combo.current(default_position)
        combo.grid(column=column + 1, row=row)

        return combo

    def block_select_file(self):
        filetypes = (
            ('image files', '*.jpg'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes
        )

        # messagebox.showinfo(
        #     title='Selected File',
        #     message=filename
        # )

        return filename


class GUI(GeneralUserInterface):
    def __init__(self, title, w, h):
        super().__init__(title, w, h)

        self.tab_control = ttk.Notebook(self.window)

        tab1 = ttk.Frame(self.tab_control)
        tab2 = ttk.Frame(self.tab_control)

        self.tab_control.add(tab1, text='Snake')
        self.tab_control.add(tab2, text='Morphological Snakes')

        # self.menu = Menu(tab2)
        # new_item = Menu(self.menu)
        # new_item.add_command(label='runBall', command=self.get_contour)
        # new_item.add_command(label='option2')
        # self.menu.add_cascade(label='Run', menu=new_item)
        # self.window.config(menu=self.menu)

        # tab 1
        self.set_size_x_tab1 = self.block_entry(
            tab1, 'Set Size x:', 6, 1, placeholder=768)
        self.set_size_y_tab1 = self.block_entry(
            tab1, 'Set Size y:', 5, 1, placeholder=768)
        self.set_alpha_tab1 = self.block_entry(
            tab1, 'Set Alpha:', 2, 1, placeholder=0.01)
        self.set_beta_tab1 = self.block_entry(
            tab1, 'Set Beta:', 3, 1, placeholder=0.1)
        self.set_gamma_tab1 = self.block_entry(
            tab1, 'Set Gamma:', 4, 1, placeholder=0.01)

        # Check button
        self.check_transform_tab1 = BooleanVar(value=True)
        self.check = Checkbutton(tab1, text='Transform: ', var=self.check_transform_tab1).grid(
            column=3, row=0, sticky=W, padx=5)
        # self.check.select()

        # Button
        Button(tab1, text='run', command=self.get_countour_snake).grid(
            row=0, column=7,)

        # tab2
        self.set_size_x = self.block_entry(
            tab2, 'Set Size x:', 6, 1, placeholder=768)
        self.set_size_y = self.block_entry(
            tab2, 'Set Size y:', 5, 1, placeholder=768)
        self.set_iteration = self.block_entry(
            tab2, 'Set Iteration:', 1, 1, placeholder=10000)
        self.set_smooth = self.block_entry(
            tab2, 'Set Smooth:', 2, 1, placeholder=3)
        self.set_threshold = self.block_entry(
            tab2, 'Set Threshold:', 3, 1, placeholder=0.4)
        self.set_balloon = self.block_entry(
            tab2, 'Set Balloon:', 4, 1, placeholder=-1)

        # Check button
        self.check_transform = BooleanVar(value=True)
        self.check = Checkbutton(tab2, text='Transform: ', var=self.check_transform).grid(
            column=3, row=0, sticky=W, padx=5)
        # self.check.select()

        # Button
        Button(tab2, text='run', command=self.get_contour).grid(
            row=0, column=7,)
        # open button
        # self.open_button = Button(tab2, text='Open a File', command=self.block_select_file).grid(row=10, column=1)

        self.tab_control.pack(expand=1, fill='both')

    def get_contour(self):
        # open file
        filetypes = (
            ('image files', '*.jpg'),
            ('image files', '*.jpeg'),
            ('All files', '*.*')
        )

        input_file = fd.askopenfilename(
            title='Open a file',
            initialdir='.\data',
            filetypes=filetypes
        )

        # file infor
        size_x = int(self.set_size_x.get())
        size_y = int(self.set_size_y.get())
        image_size = (size_x, size_y)

        # output_format = self.combo_output_format.get()
        is_transform = self.check_transform.get()

        # algorithm argument
        iteration = int(self.set_iteration.get())
        smooth = int(self.set_smooth.get())
        threshold = float(self.set_threshold.get())
        balloon = float(self.set_balloon.get())

        argument = {
            'iterations': iteration,
            'smoothing': smooth,
            'threshold': threshold,
            'balloon': balloon
        }

        print(argument)

        output_folder = './output_images'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        input_name_file = input_file.split('/')[-1].split('.')[0]
        output_file_name = output_folder + f'/{input_name_file}'
        output_file = output_file_name + '_output.png'

        img = active_contour(input_file=input_file,
                             output_file=output_file,
                             image_size=image_size,
                             argument=argument,
                             is_transform=is_transform, is_morph=True)

        # if output_format == 'COCO':
        #     print('COCO')
        # elif output_format == 'json':
        #     print(1)
        # elif output_format == 'csv':
        #     # img_array = (img.flatten())

        #     # img_array  = img_array.reshape(-1, 1).T
        #     # np.savetxt(f'{output_file_name}.csv', img_array, delimiter=',')
        #     pass

        print('done active contour')
        messagebox.showinfo(title='active contour', message='done')
        return

    def get_countour_snake(self):
        filetypes = (
            ('image files', '*.jpg'),
            ('image files', '*.jpeg'),
            ('All files', '*.*')
        )

        input_file = fd.askopenfilename(
            title='Open a file',
            initialdir='.\data',
            filetypes=filetypes
        )

        # file infor
        size_x_tab1 = int(self.set_size_x.get())
        size_y_tab1 = int(self.set_size_y.get())
        image_size = (size_x_tab1, size_y_tab1)

        # output_format = self.combo_output_format.get()
        is_transform = self.check_transform_tab1.get()

        # algorithm argument
        alpha = float(self.set_alpha_tab1.get())
        beta = float(self.set_beta_tab1.get())
        gamma = float(self.set_gamma_tab1.get())

        argument = {
            'alpha': alpha,
            'beta': beta,
            'gamma': gamma,
        }

        output_folder = './output_images'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        input_name_file = input_file.split('/')[-1].split('.')[0]
        output_file_name = output_folder + f'/{input_name_file}'
        output_file = output_file_name + '_output.png'

        img = active_contour(input_file,
                             output_file,
                             image_size,
                             argument,
                             is_transform, False)

        # if output_format == 'COCO':

        print('done snake')
        messagebox.showinfo(title='snake', message='done')
        return


if __name__ == '__main__':
    gui = GUI('Controller', 500, 400)
    gui.window.mainloop()
