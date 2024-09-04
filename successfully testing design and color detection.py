import tkinter as tk
from tkinter import Label
from tkinter import ttk
import customtkinter
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
from tkinter import messagebox
from pymodbus.client import ModbusTcpClient as mbc
import time
# Set up CustomTkinter
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("green")

frame_width = 1300
frame_height = 650

run1, run2, run3, run4 = False, False, False, False
run = True

class CameraApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Camera Feed")
        self.geometry(f"{frame_width}x{frame_height}")
        self.client = mbc('192.168.0.1', port=502)
        self.UNIT = 0x1  # rack, slot
        self.register_states = [0, 0, 0, 0]  # gửi tín hiệu 0 về 4 thanh ghi (0, 1, 2, 3)
        if self.client.connect():
            print('Connected to PLC')
            self.write_register(39, 1)   # nếu thanh ghi 39 nhận giá trị 1, bên tia portal kích 1 bit nhớ
        else:
            print('Failed to connect to PLC')
            self.write_register(39, 0)  
            exit()
        
        self.last_update_time = time.time()
        self.update_interval = 0.4  # Update interval in seconds
        # Initialize Modbus registers
        # Add a text label at the top
        label_height = (frame_height)/13  # Absolute height for the label in pixels
        rel_label_height = label_height / frame_height  # Calculate the relative height
        self.wel_label = customtkinter.CTkLabel(
            self, text="BẢO VỆ ĐỒ ÁN PHÂN LOẠI SP THEO MÀU SẮC", text_color="white", bg_color="black", 
            font=customtkinter.CTkFont(size=30, weight="bold")
        )
        self.wel_label.place(x=0, y=0, relwidth=1, relheight=rel_label_height)

        # Open the video capture
        self.cap = cv2.VideoCapture(0)
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) * 85 / 100)
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * 85 / 100)

        # Create the main video feed label
        self.available_height = frame_height - label_height
        self.video_label = Label(self, bg="black")
        self.video_label.place(x=0, y=label_height, 
                               relwidth=(self.width)/(frame_width), 
                               relheight=(self.height)/(frame_height))

        # Create the second frame on the right side
        self.second_label_width = frame_width - self.width
        self.second_label = customtkinter.CTkFrame(self)
        self.second_label.place(relx= self.width/frame_width, rely=label_height/frame_height, 
                                relwidth=(self.second_label_width)/(frame_width),
                                relheight=(self.height)/(frame_height))
        self.second_label.columnconfigure((0, 1, 2, 3), weight=1, uniform="a")
        self.second_label.rowconfigure((0, 1, 2, 3), weight=1, uniform="a")
        self.name_label = Label(self.second_label, bg="black")
        self.name_label.grid(row=0, column=3, columnspan=1, rowspan=2, sticky="nsew")
        self.width_for_image = (frame_width - self.width) * 1/4
        for i in range (7):
            self.name_label.rowconfigure(i, weight =1)
            self.name_label.columnconfigure(0, weight=1)
        self.name1 = customtkinter.CTkLabel(self.name_label, text= "TÊN NHÓM", text_color="yellow", 
                                            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.name1.grid(row=0, column = 0)
        self.name2 = customtkinter.CTkLabel(self.name_label, text="Trần Minh Quang", text_color="white", 
                                            font=customtkinter.CTkFont(size=15, weight="bold"))
        self.name2.grid(row=1, column=0)
        self.name3 = customtkinter.CTkLabel(self.name_label, text="Nguyễn Tiến Đạt", text_color="white",
                                            font=customtkinter.CTkFont(size=15, weight="bold"))
        self.name3.grid(row=2, column=0)
        self.name4 = customtkinter.CTkLabel(self.name_label, text="Lê Quý Đông", text_color="white", bg_color="black",
                                            font=customtkinter.CTkFont(size=15, weight="bold"))
        self.name4.grid(row=3, column=0)
        self.name5 = customtkinter.CTkLabel(self.name_label, text="Vũ Văn Long", text_color="white", bg_color="black",
                                            font=customtkinter.CTkFont(size=15, weight="bold"))
        self.name5.grid(row=4, column=0)
        self.name6 = customtkinter.CTkLabel(self.name_label, text="Ngô Văn Trung", text_color="white",
                                            font=customtkinter.CTkFont(size=15, weight="bold"))
        self.name6.grid(row=5, column=0)
        self.name7 = customtkinter.CTkLabel(self.name_label, text="GV: Ts Vũ Văn Tú", text_color="white", 
                                            font=customtkinter.CTkFont(size=15, weight="bold"))
        self.name7.grid(row=6, column=0)

        self.width_frame_for_color_and_status = (frame_width - self.width) * 3/4
        self.frame_for_color_and_status = customtkinter.CTkFrame(self.second_label)
        self.frame_for_color_and_status.place(x=0, y=0, relwidth = 0.75, relheight=1)

        self.frame_for_color_and_status.grid_rowconfigure((0, 1, 2, 3), weight=1, uniform="a")
        self.frame_for_color_and_status.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="a")
        # create frame for button 
        self.start = customtkinter.CTkButton(
            self.frame_for_color_and_status,
            text="Start Scada", 
            fg_color = "green",
            corner_radius = 50, 
            hover_color="gray", 
            command=self.on_clicked_button
            )
        self.start.grid(row=0, column=1)
        self.stop = customtkinter.CTkButton(
            self.frame_for_color_and_status,
            text="Stop Scada", 
            fg_color = "red",
            corner_radius = 50, 
            hover_color="gray", 
            command=self.clicked_stop
            )
        self.stop.grid(row=0, column=2)
        self.canvas_height = self.height/4
        self.canvas_width = self.width_frame_for_color_and_status * 3/5
        self.canvas = customtkinter.CTkCanvas(self.frame_for_color_and_status, width=self.canvas_width, height=self.canvas_height, bg = "black")
        self.canvas.grid(row=1, column=1, columnspan=2)
        self.label_height = 1/3 * self.canvas_height
        self.x1_circle1 = 1/5 * self.canvas_width
        self.x2_circle1 = 2/5 * self.canvas_width
        self.y2_circle1 = 2/3 * self.canvas_height
        self.circle1 = self.canvas.create_oval(self.x1_circle1,
                                               0,
                                                self.x2_circle1,
                                                 self.y2_circle1,
                                                   fill='gray', outline='yellow')
        self.canvas.create_text(3/10 * self.canvas_width, self.y2_circle1 + ((self.label_height)/2), text = "ĐÈN START", fill = "yellow")
        self.x1_circle2 = 5/10 * self.canvas_width
        self.x2_circle2 = 7/10 * self.canvas_width
        self.circle2 = self.canvas.create_oval(self.x1_circle2,
                                               0,
                                               self.x2_circle2,
                                                self.y2_circle1,
                                                 fill="gray", outline="yellow")
        self.canvas.create_text(6/10 * self.canvas_width, self.y2_circle1 + ((self.label_height)/2), text = "ĐÈN STOP", fill = "yellow")
        self.frame_color = customtkinter.CTkFrame(self.second_label)
        self.frame_color.grid(row = 2, column=0, rowspan = 2, columnspan=4, sticky = "nsew")
        self.frame_color.grid_rowconfigure((0, 1, 2 ,3, 4), weight=1, uniform="a")
        self.frame_color.grid_columnconfigure((0, 2, 3, 4, 5, 6), weight=1, uniform="a")
        self.frame_color.grid_columnconfigure(1, weight=2, uniform="a")
        self.status_text = customtkinter.CTkLabel(self.frame_color, text ="STATUS", text_color = "green", font=("Arial", 18))
        self.status_text.grid(row=0, column=1, sticky="s")
        self.enter_number = customtkinter.CTkLabel(self.frame_color, text ="NHẬP", text_color = "green", font=("Arial", 18))
        self.enter_number.grid(row=0, column=2, sticky="s")
        self.show_number = customtkinter.CTkLabel(self.frame_color, text="ĐẾM", text_color="green", font=("Arial", 18))
        self.show_number.grid(row=0, column=3, sticky="s")
        self.red_label = customtkinter.CTkLabel(self.frame_color, text="RED", text_color="black", bg_color="red", 
            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.red_label.grid(row =1, column = 0, columnspan =1, sticky="nsew")
        self.red_text = tk.Text(self.frame_color, width = int(self.canvas_width), height = int(self.height/200))
        self.red_text.grid(row=1, column=1, sticky="nsew")
        self.red_text.tag_configure("center", justify='center', foreground="red", font=("Helvetica", 12, "bold"))
        self.red_text.insert(tk.END, "By default, 2 objects will be in process")
        self.write_register(21, 2)
        self.red_text.tag_add("center", "1.0", "end")
        self.red_text.configure(state=tk.DISABLED)
        self.integer_var = tk.StringVar()
        
        self.red_enter = ttk.Entry(self.frame_color, textvariable=self.integer_var)
        self.red_enter.grid(row=1, column=2, sticky="nsew")
        self.red_enter.bind('<Return>', self.on_enter_red)
        self.red_show = tk.Text(self.frame_color, width = int(self.canvas_width), height = int(self.height/200))
        self.red_show.grid(row=1, column=3, sticky="nsew")
        self.red_show.tag_configure("center", justify='center', foreground="red", font=("Helvetica", 12, "bold"))
        self.red_show.insert(tk.END, "0")
        self.red_show.tag_add("center", "1.0", "end")
        self.red_show.configure(state="disabled")
        self.reset_red = customtkinter.CTkButton(self.frame_color, text="RESET RED", fg_color="gray", command=self.reset1)
        self.reset_red.grid(row=1, column=4, sticky="nsew")
        self.count=0
        self.trace_id = self.integer_var.trace_add('write', self.validate_integer_red)
        self.after(1000, self.update_red_show)  # Start the periodic update for red_show
        self.after(1000, self.check_storage_limit_red)
        self.yellow_label = customtkinter.CTkLabel(self.frame_color, text="YELLOW", text_color="black", bg_color="yellow", 
            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.yellow_label.grid(row =2, column = 0, columnspan =1, sticky="nsew")
        self.yellow_text = tk.Text(self.frame_color, width = int(self.canvas_width), height = int(self.height/200))
        self.yellow_text.grid(row=2, column=1, sticky="nsew")
        self.yellow_text.tag_configure("center", justify='center', foreground="#ABAE00", font=("Helvetica", 12, "bold"))
        self.yellow_text.insert(tk.END, "By default, 2 objects will be in process")
        self.write_register(24, 2)
        self.yellow_text.tag_add("center", "1.0", "end")
        self.yellow_text.configure(state=tk.DISABLED)
        self.integer_var2 = tk.StringVar()
        self.yellow_enter = ttk.Entry(self.frame_color, textvariable=self.integer_var2)
        self.yellow_enter.grid(row=2, column=2, sticky="nsew")
        self.yellow_enter.bind('<Return>', self.on_enter_yellow)
        self.trace_id2 = self.integer_var2.trace_add('write', self.validate_integer_yellow)
        self.yellow_show = tk.Text(self.frame_color, width = int(self.canvas_width), height = int(self.height/200))
        self.yellow_show.grid(row=2, column=3, sticky="nsew")
        self.yellow_show.tag_configure("center", justify='center', foreground="red", font=("Helvetica", 12, "bold"))
        self.yellow_show.insert(tk.END, "0")
        self.yellow_show.tag_add("center", "1.0", "end")
        self.yellow_show.configure(state="disabled")
        self.reset_yellow = customtkinter.CTkButton(self.frame_color, text="RESET YELLOW", fg_color="gray", command=self.reset2)
        self.reset_yellow.grid(row=2, column=4, sticky="nsew")
        self.after(1000, self.update_yellow_show)
        self.after(1000, self.check_storage_limit_yellow)
        self.blue_label = customtkinter.CTkLabel(self.frame_color, text="BLUE", text_color="black", bg_color="blue", 
            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.blue_label.grid(row =3, column = 0, columnspan =1, sticky="nsew")
        self.blue_text = tk.Text(self.frame_color, width = int(self.canvas_width), height = int(self.height/200))
        self.blue_text.grid(row=3, column=1, sticky="nsew")
        self.blue_text.tag_configure("center", justify='center', foreground="blue", font=("Helvetica", 12, "bold"))
        self.blue_text.insert(tk.END, "By default, 2 objects will be in process")
        self.write_register(27, 2)
        self.blue_text.tag_add("center", "1.0", "end")
        self.blue_text.configure(state=tk.DISABLED)
        self.integer_var3 = tk.StringVar()
        self.blue_enter = ttk.Entry(self.frame_color, textvariable=self.integer_var3)
        self.blue_enter.grid(row=3, column=2, sticky="nsew")
        self.blue_enter.bind('<Return>', self.on_enter_blue)
        self.trace_id3 = self.integer_var3.trace_add('write', self.validate_integer_blue)
        self.blue_show = tk.Text(self.frame_color, width = int(self.canvas_width), height = int(self.height/200))
        self.blue_show.grid(row=3, column=3, sticky="nsew")
        self.blue_show.tag_configure("center", justify='center', foreground="red", font=("Helvetica", 12, "bold"))
        self.blue_show.insert(tk.END, "0")
        self.blue_show.tag_add("center", "1.0", "end")
        self.blue_show.configure(state="disabled")
        self.reset_blue = customtkinter.CTkButton(self.frame_color, text="RESET BLUE", fg_color="gray", command=self.reset3)
        self.reset_blue.grid(row=3, column=4, sticky="nsew")
        self.after(1000, self.update_blue_show)
        self.after(1000, self.check_storage_limit_blue)
        self.purple_label = customtkinter.CTkLabel(self.frame_color, text="PURPLE", text_color="black", bg_color="purple", 
            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.purple_label.grid(row =4, column = 0, columnspan =1, sticky="nsew")
        self.purple_text = tk.Text(self.frame_color, width = int(self.canvas_width), height = int(self.height/200))
        self.purple_text.grid(row=4, column=1, sticky="nsew")
        self.purple_text.tag_configure("center", justify='center', foreground="purple", font=("Helvetica", 12, "bold"))
        self.purple_text.insert(tk.END, "By default, 2 objects will be in process")
        self.write_register(30, 2)
        self.purple_text.tag_add("center", "1.0", "end")
        self.purple_text.configure(state=tk.DISABLED)
        self.integer_var4 = tk.StringVar()
        self.purple_enter = ttk.Entry(self.frame_color, textvariable=self.integer_var4)
        self.purple_enter.grid(row=4, column=2, sticky="nsew")
        self.purple_enter.bind('<Return>', self.on_enter_purple)
        self.trace_id4 = self.integer_var4.trace_add('write', self.validate_integer_purple)
        self.purple_show = tk.Text(self.frame_color, width = int(self.canvas_width), height = int(self.height/200))
        self.purple_show.grid(row=4, column=3, sticky="nsew")
        self.purple_show.tag_configure("center", justify='center', foreground="red", font=("Helvetica", 12, "bold"))
        self.purple_show.insert(tk.END, "0")
        self.purple_show.tag_add("center", "1.0", "end")
        self.purple_show.configure(state="disabled")
        self.reset_purple = customtkinter.CTkButton(self.frame_color, text="RESET PURPLE", fg_color="gray", command=self.reset4)
        self.reset_purple.grid(row=4, column=4, sticky="nsew")
        self.after(1000, self.update_purple_show)
        self.after(1000, self.check_storage_limit_purple)
        self.current_path = os.path.dirname(os.path.realpath(__file__))
        self.bg_image = customtkinter.CTkImage(Image.open("logo_my_uni.jpg"),
                                               size=(self.width_for_image, self.width_for_image))
        self.bg_image_label = customtkinter.CTkLabel(self.frame_color, image=self.bg_image, bg_color= "black")
        self.bg_image_label.grid(row=0, column=5, rowspan=5, columnspan=2, sticky="s")

        # Create the third frame below the second frame
        self.third_frame_height = frame_height - self.height - label_height
        self.third_label = customtkinter.CTkFrame(self)
        self.third_label.place(x=0, rely=((self.height)+(label_height))/frame_height, 
                               relwidth=1, 
                               relheight=(self.third_frame_height)/(frame_height))
        self.third_frame1 = customtkinter.CTkFrame(self.third_label)
        self.third_frame1.place(x=0, y =0, relwidth = (self.width)/(frame_width), relheight = 1)
        self.canvas_light_height = self.third_frame_height
        self.canvas_light_width = (self.width) * 10/13
        self.canvas_light = customtkinter.CTkCanvas(self.third_frame1, width=self.canvas_light_width, height=self.canvas_light_height, bg="black")
        self.canvas_light.place(relx= ((self.width - self.canvas_light_width)/2) /self.width, 
                                y = 0, 
                                relwidth=(self.canvas_light_width)/(self.width), 
                                relheight = (self.canvas_light_height)/(self.third_frame_height))
        self.canvas_light.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")
        self.canvas_light.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight =1, uniform="a")
        self.light_text = customtkinter.CTkLabel(self.canvas_light, text = "HỆ THỐNG ĐÈN BÁO", text_color="white", 
                                            font=customtkinter.CTkFont(size=20, weight="bold"), bg_color="orange")
        self.light_text.grid(row =0, column =0, columnspan=6, sticky="n")
        self.frame_light1 = self.canvas_light_width / 3
        self.light1 = self.canvas_light.create_oval(1/4 * self.frame_light1, 
                                                    1/7 * self.canvas_light_height, 
                                                    3/4 * self.frame_light1, 
                                                    3/7 * self.canvas_light_height, fill="gray")
        self.canvas_light.create_text(1/2 * self.frame_light1, 1/16 * self.canvas_light_height + 3/7 * self.canvas_light_height, text="băng tải (Q0.0)",font=16, fill="white")
        self.light2 = self.canvas_light.create_oval(1/4 * self.frame_light1 + self.frame_light1, 
                                                    1/7 * self.canvas_light_height, 
                                                    3/4 * self.frame_light1 + self.frame_light1, 
                                                    3/7 * self.canvas_light_height, fill="gray")
        self.canvas_light.create_text(self.frame_light1 + 1/2 * self.frame_light1, 1/16 * self.canvas_light_height + 3/7 * self.canvas_light_height, text="van đẩy hàng (Q0.1)",font=16, fill="white")
        self.light3 = self.canvas_light.create_oval(1/4 * self.frame_light1 + 2 * self.frame_light1, 
                                                    1/7 * self.canvas_light_height, 
                                                    3/4 * self.frame_light1 + 2 * self.frame_light1, 
                                                    3/7 * self.canvas_light_height, fill="gray")
        self.canvas_light.create_text(2*self.frame_light1 + 1/2 * self.frame_light1, 1/16 * self.canvas_light_height + 3/7 * self.canvas_light_height, text="van xoay (Q0.2)",font=16, fill="white")
        self.light4 = self.canvas_light.create_oval(1/4 * self.frame_light1, 
                                                    4/7 * self.canvas_light_height, 
                                                    3/4 * self.frame_light1, 
                                                    6/7 * self.canvas_light_height, fill="gray")
        self.canvas_light.create_text(1/2 * self.frame_light1, 1/16 * self.canvas_light_height + 6/7 * self.canvas_light_height, text = "van ra vào (Q0.3)", font=16, fill="white")
        self.light5 = self.canvas_light.create_oval(1/4 * self.frame_light1 + self.frame_light1, 
                                                    4/7 * self.canvas_light_height, 
                                                    3/4 * self.frame_light1 + self.frame_light1, 
                                                    6/7 * self.canvas_light_height, fill="gray")
        self.canvas_light.create_text(self.frame_light1 + 1/2 * self.frame_light1, 1/16 * self.canvas_light_height + 6/7 * self.canvas_light_height, text="van lên xuống (Q0.4)",font=16, fill="white")
        self.light6 = self.canvas_light.create_oval(1/4 * self.frame_light1 + 2 * self.frame_light1, 
                                                    4/7 * self.canvas_light_height, 
                                                    3/4 * self.frame_light1 + 2 * self.frame_light1, 
                                                    6/7 * self.canvas_light_height, fill="gray")
        self.canvas_light.create_text(2*self.frame_light1 + 1/2 * self.frame_light1, 1/16 * self.canvas_light_height + 6/7 * self.canvas_light_height, text="van hút (Q0.5)",font=16, fill="white")
        self.light1_on, self.light2_on, self.light3_on, self.light4_on, self.light5_on, self.light6_on = False, False, False, False, False, False
        self.third_frame2 = customtkinter.CTkFrame(self.third_label)
        self.third_frame2.place(relx=(self.width)/frame_width, y=0, relwidth = (self.width_frame_for_color_and_status)/(frame_width), relheight=1)
        self.third_frame2.grid_rowconfigure((0, 1, 2), weight=1, uniform="a")
        self.third_frame2.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")
        self.switch = customtkinter.CTkSwitch(self.third_frame2, text = "MANUAL", command=self.switch_event)
        self.switch.grid(row=0, column=1)
        self.small_window = None
        
        self.canvas_auto_width= self.width_frame_for_color_and_status * 0.5
        self.canvas_auto_height = self.third_frame_height * 0.5
        self.light_auto_manual = customtkinter.CTkCanvas(self.third_frame2, bg="black")
        self.light_auto_manual.place(relx= (self.width_frame_for_color_and_status/4)/(self.width_frame_for_color_and_status),
                                     rely = 0.4, 
                                     relwidth = self.canvas_auto_width/self.width_frame_for_color_and_status, 
                                     relheight = self.canvas_auto_height/self.third_frame_height)
        self.light_for_auto = self.light_auto_manual.create_oval(1/8 * self.canvas_auto_width, 0, 3/8 * self.canvas_auto_width, 4/5 * self.canvas_auto_height)
        self.light_auto_manual.create_text(1/4 * self.canvas_auto_width, 4/5 * self.canvas_auto_height + 1/10 * self.canvas_auto_height, text="ĐÈN AUTO", fill="white")
        self.light_for_manual = self.light_auto_manual.create_oval(5/8 * self.canvas_auto_width, 0, 7/8 * self.canvas_auto_width, 4/5 * self.canvas_auto_height)
        self.light_auto_manual.create_text(3/4 * self.canvas_auto_width, 4/5 * self.canvas_auto_height + 1/10 * self.canvas_auto_height, text="ĐÈN MANUAL", fill="white")
        if self.small_window == None:
            self.light_auto_manual.itemconfig(self.light_for_auto, fill="green")
            self.light_auto_manual.itemconfig(self.light_for_manual, fill = "gray")
        self.third_frame3 = customtkinter.CTkFrame(self.third_label)
        self.third_frame3.place(relx=(self.width + self.width_frame_for_color_and_status)/frame_width, y = 0, relwidth = ((self.second_label_width)/4)/(frame_width), relheight=1)
        self.third_frame3.grid_rowconfigure((0, 1,2 ,3, 4,5), weight=1, uniform="a")
        self.appearance_mode_label = customtkinter.CTkLabel(self.third_frame3, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.third_frame3, values=["Dark", "light"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=1, column=0, rowspan =2, padx=20, pady=(10, 10))

        for i in range(4):
            self.write_register(i, 0)
        self.lower_red = np.array([0, 150, 150])
        self.upper_red = np.array([12, 255, 255])
        self.lower_yellow = np.array([18, 150, 150])
        self.upper_yellow = np.array([35, 255, 255])
        self.lower_blue = np.array([90, 120, 120])
        self.upper_blue = np.array([120, 255, 255])
        self.lower_purple = np.array([140, 80, 80])
        self.upper_purple = np.array([165, 255, 255])
        self.read_initial_state()
        self.video_loop()
        self.after(200, self.read_initial_state_light_1)
        self.after(200, self.read_initial_state_light_2)
        self.after(200, self.read_initial_state_light_3)
        self.after(200, self.read_initial_state_light_4)
        self.after(200, self.read_initial_state_light_5)
        self.after(200, self.read_initial_state_light_6)
    def write_register(self, register, value):   # self.write_register(10, 4) - integer
        response = self.client.write_register(register, value, unit=self.UNIT)  # ghi dữ liệu  
        if response.isError():
            print(f'Error writing to register {register}: {register}')
    def on_clicked_button(self):   # start button
        self.client.write_register(4, 1, unit=self.UNIT)
        self.client.write_register(5, 0, unit=self.UNIT)
        self.after(400, self.reset_registers_and_read_state)
    def clicked_stop(self):   # stop button
        self.client.write_register(4, 0, unit=self.UNIT)
        self.client.write_register(5, 1, unit=self.UNIT)
        self.after(400, self.reset_registers_and_read_state)
    def read_initial_state(self):    # read start and stop lights
        result1 = self.client.read_holding_registers(6, 1, unit=self.UNIT)
        result2 = self.client.read_holding_registers(7, 1, unit=self.UNIT)

        if result1.isError() or result2.isError():
            print('Failed to read from PLC')
        else:
            initial_state1 = result1.registers[0]
            initial_state2 = result2.registers[0]
            self.update_lights(initial_state1, initial_state2)
    def update_lights(self, state1, state2):
        if state1 == 1:
            self.canvas.itemconfig(self.circle1, fill="green")
        else:
            self.canvas.itemconfig(self.circle1, fill="gray")
        if state2 == 1:
            self.canvas.itemconfig(self.circle2, fill="red")
        else:
            self.canvas.itemconfig(self.circle2, fill="gray")
    def reset_registers_and_read_state(self):
        self.client.write_register(4, 0, unit=self.UNIT)
        self.client.write_register(5, 0, unit=self.UNIT)
        self.read_initial_state()
    def reset_every_button(self, i):
        self.client.write_register(i, 0, unit=self.UNIT)
    def reset1(self):
        self.write_register(17, 1)
        self.after(400, lambda: self.write_register(17, 0))
        self.write_register(21, 2)
        self.red_show.configure(state=tk.NORMAL)
        self.red_show.delete("1.0", tk.END)
        self.red_show.insert(tk.END, "0")
        self.red_show.tag_add("center", "1.0", "end")
        self.red_show.configure(state=tk.DISABLED)
        
        self.integer_var.trace_remove("write", self.trace_id)
        self.integer_var.set("")
        self.trace_id = self.integer_var.trace_add("write", self.validate_integer_red)
        self.update_status_red("By default, 2 objects will be in process")
    def read_register(self, register, count=1):
        result = self.client.read_holding_registers(register, count, unit=self.UNIT) 
        return result.registers
    def check_storage_limit_red(self):
        try:
            limit = int(self.integer_var.get())
        except ValueError:
            limit = 2

        storage_signal = self.read_register(23)[0]
        if storage_signal == 1:
            self.update_status_red("The storage is full")
        else:
            if limit > 2:
                self.update_status_red(f"You have entered {limit} so {limit} objects will be in process")
            else:
                self.update_status_red("By default, 2 objects will be in process") 
        self.after(1000, self.check_storage_limit_red)
    def update_red_show(self):
        read_value = self.read_register(22)[0]
        self.red_show.configure(state=tk.NORMAL)
        self.red_show.delete("1.0", tk.END)
        self.red_show.insert(tk.END, str(read_value))
        self.red_show.tag_add("center", "1.0", "end")
        self.red_show.configure(state=tk.DISABLED)
        self.after(1000, self.update_red_show)  # Continuously update red_show every second  
    def reset2(self):
        self.client.write_register(18, 1, unit=self.UNIT)
        self.after(400, lambda: self.write_register(18, 0))
        self.client.write_register(24, 2)
        self.yellow_show.configure(state=tk.NORMAL)
        self.yellow_show.delete("1.0", tk.END)
        self.yellow_show.insert(tk.END, "0")
        self.yellow_show.tag_add("center", "1.0", "end")
        self.yellow_show.configure(state=tk.DISABLED)
        self.integer_var2.trace_remove("write", self.trace_id2)
        self.integer_var2.set("")
        self.trace_id2 = self.integer_var2.trace_add("write", self.validate_integer_yellow)
        self.update_status_yellow("By default, 2 objects will be in process")
    def check_storage_limit_yellow(self):
        try:
            limit = int(self.integer_var2.get())
        except ValueError:
            limit = 2
        storage_signal2 = self.read_register(26)[0]
        if storage_signal2 ==1:
            self.update_status_yellow("The storage is full")
        else:
            if limit >2:
                self.update_status_yellow(f"You have entered {limit}")
            else:
                self.update_status_yellow("By default, 2 objects will be in process")
        self.after(1000, self.check_storage_limit_yellow)
    def reset3(self):
        self.client.write_register(19, 1, unit=self.UNIT)
        self.after(400, lambda: self.write_register(19, 0))
        self.write_register(27, 2)
        self.blue_show.configure(state=tk.NORMAL)
        self.blue_show.delete("1.0", tk.END)
        self.blue_show.insert(tk.END, "0")
        self.blue_show.tag_add("center", "1.0", "end")
        self.blue_show.configure(state=tk.DISABLED)
        self.integer_var3.trace_remove("write", self.trace_id3)
        self.integer_var3.set("")
        self.trace_id3 = self.integer_var3.trace_add("write", self.validate_integer_blue)
        self.update_status_blue("By default, 2 objects will be in process")
    def reset4(self):
        self.client.write_register(20, 1, unit=self.UNIT)
        self.after(400, lambda: self.write_register(20, 0))
        self.write_register(30, 2)
        self.purple_show.configure(state=tk.NORMAL)
        self.purple_show.delete("1.0", tk.END)
        self.purple_show.insert(tk.END, "0")
        self.purple_show.tag_add("center", "1.0", "end")
        self.purple_show.configure(state=tk.DISABLED)
        self.integer_var4.trace_remove("write", self.trace_id4)
        self.integer_var4.set("")
        self.trace_id4 = self.integer_var4.trace_add("write", self.validate_integer_purple)
        self.update_status_purple("By default, 2 objects will be in process")
    def validate_integer_red(self, *args):   # Update the status message based on the entered values
        value = self.integer_var.get()
        if value.isdigit() and int(value) > 2:   
            self.update_status_red(f"You have entered {value} so {value} objects will be in process")
            self.write_register(21, int(value))
        elif value.isdigit() and int(value) <= 2:
            self.update_status_red("By default, 2 objects will be in process")
            self.write_register(21, 2)
        else:
            self.update_status_red("Invalid Input")
    def on_enter_red(self, *args):    # Function is triggered when the user presses the enter key, only digits are allowed
        value = self.integer_var.get()
        if not value.isdigit():
            self.integer_var.set(''.join(filter(str.isdigit, value)))
    def update_status_red(self, message):
        self.red_text.configure(state=tk.NORMAL)
        self.red_text.delete("1.0", tk.END)
        self.red_text.insert(tk.END, message)
        self.red_text.tag_add("center", "1.0", "end")
        self.red_text.configure(state=tk.DISABLED)
    
    def on_enter_yellow(self, *args):
        value = self.integer_var2.get()
        if not value.isdigit():
            self.integer_var2.set(' '.join(filter(str.isdigit, value)))
    def validate_integer_yellow(self, *args):
        value = self.integer_var2.get()
        if value.isdigit() and int(value) > 2:
            self.update_status_yellow(f"You have entered {value}")
            self.write_register(24, int(value))
        elif value.isdigit() and int(value) <= 2:
            self.update_status_yellow("By default, 2 objects will be in process")
            self.write_register(24, 2)
        else:
            self.update_status_yellow("Invalid Input")

    def update_status_yellow(self, message):
        self.yellow_text.configure(state=tk.NORMAL)
        self.yellow_text.delete("1.0", tk.END)
        self.yellow_text.insert(tk.END, message)
        self.yellow_text.tag_add("center", "1.0", "end")
        self.yellow_text.configure(state=tk.DISABLED)
    def update_yellow_show(self):
        read_value2 = self.read_register(25)[0]
        self.yellow_show.configure(state=tk.NORMAL)
        self.yellow_show.delete("1.0", tk.END)
        self.yellow_show.insert(tk.END, str(read_value2))
        self.yellow_show.tag_add("center", "1.0", "end")
        self.yellow_show.configure(state=tk.DISABLED)
        self.after(1000, self.update_yellow_show)
    def on_enter_blue(self, *args):
        value = self.integer_var3.get()
        if not value.isdigit():
            self.integer_var3.set(' '.join(filter(str.isdigit, value)))
    def validate_integer_blue(self, *args):
        value = self.integer_var3.get()
        if value.isdigit() and int(value) > 2:
            self.update_status_blue(f"You have entered {value}")
            self.write_register(27, int(value))
        elif value.isdigit() and int(value) <= 2:
            self.update_status_blue("By default, 2 objects will be in process")
            self.write_register(27, 2)
        else:
            self.update_status_blue("Invalid Input")
    def update_status_blue(self, message):
        self.blue_text.configure(state=tk.NORMAL)
        self.blue_text.delete("1.0", tk.END)
        self.blue_text.insert(tk.END, message)
        self.blue_text.tag_add("center", "1.0", "end")
        self.blue_text.configure(state=tk.DISABLED)
    def check_storage_limit_blue(self):
        try:
            limit = int(self.integer_var3.get())
        except ValueError:
            limit = 2
        storage_signal3 = self.read_register(29)[0]
        if storage_signal3 == 1:
            self.update_status_blue("The storage is full")
        else:
            if limit > 2:
                self.update_status_blue(f"You have entered {limit}, so {limit} objects will be in process")
        self.after(1000, self.check_storage_limit_blue)
    def update_blue_show(self):
        read_value3 = self.read_register(28)[0]
        self.blue_show.configure(state=tk.NORMAL)
        self.blue_show.delete("1.0", tk.END)
        self.blue_show.insert(tk.END, str(read_value3))
        self.blue_show.tag_add("center", "1.0", "end")
        self.blue_show.configure(state=tk.DISABLED)
        self.after(1000, self.update_blue_show)
    def on_enter_purple(self, *args):
        value = self.integer_var4.get()
        if not value.isdigit():
            self.integer_var4.set(' '.join(filter(str.isdigit, value)))
    def validate_integer_purple(self, *args):
        value = self.integer_var4.get()
        if value.isdigit() and int(value) > 2:
            self.update_status_purple(f"You have entered {value}")
            self.write_register(30, int(value))
        elif value.isdigit() and int(value) <= 2:
            self.update_status_purple("By default, 2 objects will be in process")
            self.write_register(30, 2)
        else:
            self.update_status_purple("Invalid Input")
    def update_status_purple(self, message):
        self.purple_text.configure(state=tk.NORMAL)
        self.purple_text.delete("1.0", tk.END)
        self.purple_text.insert(tk.END, message)
        self.purple_text.tag_add("center", "1.0", "end")
        self.purple_text.configure(state=tk.DISABLED)
    def check_storage_limit_purple(self):
        try:
            limit = int(self.integer_var4.get())
        except ValueError:
            limit = 2
        storage_signal4 = self.read_register(32)[0]
        if storage_signal4 ==1:
            self.update_status_purple("The storage is full")
        else:
            if limit > 2:
                self.update_status_purple(f"You have entered {limit}, so {limit} will be in process")
            else:
                self.update_status_purple("By default, 2 objects will be in process")
        self.after(1000, self.check_storage_limit_purple)    
    def update_purple_show(self):
        read_value4 = self.read_register(31)[0]
        self.purple_show.configure(state = tk.NORMAL)
        self.purple_show.delete("1.0", tk.END)
        self.purple_show.insert(tk.END, str(read_value4))
        self.purple_show.tag_add("center", "1.0", "end")
        self.purple_show.configure(state=tk.DISABLED)
        self.after(1000, self.update_purple_show)
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        # Function to handle switch state change
    def switch_event(self):
        if self.switch.get() == 1:  # If switch is turned on
            self.open_small_window()
            self.light_auto_manual.itemconfig(self.light_for_auto, fill="gray")
            self.light_auto_manual.itemconfig(self.light_for_manual, fill="green")
            self.client.write_register(10, 1, unit=self.UNIT)
        else:
            if self.small_window:  # If the small window is open
                self.close_small_window()
                self.light_auto_manual.itemconfig(self.light_for_auto, fill="green")
                self.light_auto_manual.itemconfig(self.light_for_manual, fill = "gray")
                self.client.write_register(10, 0, unit=self.UNIT)

# Function to open the small window
    def open_small_window(self):
        self.small_window = customtkinter.CTkToplevel()
        self.small_window.geometry("500x300")
        self.small_window.title("WINDOW FOR MANUAL CONTROL")
        self.small_window.protocol("WM_DELETE_WINDOW", self.on_closing_small_window)
        self.small_window.attributes("-topmost", True)
        self.frame_inside_small_window = customtkinter.CTkFrame(self.small_window)
        self.frame_inside_small_window.pack(expand=True, fill="both")
        self.frame_inside_small_window.grid_rowconfigure(0, weight=1, uniform="a")
        self.frame_inside_small_window.grid_rowconfigure((1, 2), weight=2, uniform="a")
        self.frame_inside_small_window.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")
        self.title_small_window = customtkinter.CTkLabel(self.frame_inside_small_window, text="MANUAL CONTROL PANEL", bg_color= "orange", 
                                                         font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title_small_window.grid(row=0, column=0, columnspan=3)
        self.button1 = customtkinter.CTkButton(self.frame_inside_small_window,
            text="BĂNG TẢI (Q0.0)", 
            corner_radius = 50,  
            command=self.clicked_1)
        self.button1.grid(row =1, column=0)
        self.button2 = customtkinter.CTkButton(self.frame_inside_small_window,
            text="VAN ĐẨY(Q0.1)", 
            corner_radius = 50, 
            command=self.clicked_2)
        self.button2.grid(row =1, column=1)
        self.button3 = customtkinter.CTkButton(self.frame_inside_small_window,
            text="VAN XOAY(Q0.2)", 
            corner_radius = 50, 
            command=self.clicked_3)
        self.button3.grid(row =1, column=2)
        self.button4 = customtkinter.CTkButton(self.frame_inside_small_window,
            text="VAN RA VÀO(Q0.3)", 
            corner_radius = 50,  
            command=self.clicked_4)
        self.button4.grid(row =2, column=0)
        self.button5 = customtkinter.CTkButton(self.frame_inside_small_window,
            text="VAN LÊN XUỐNG(Q0.4)", 
            corner_radius = 50, 
            command=self.clicked_5)
        self.button5.grid(row =2, column=1)
        self.button6 = customtkinter.CTkButton(self.frame_inside_small_window,
            text="VAN HÚT (Q0.5)", 
            corner_radius = 50,  
            command=self.clicked_6)
        self.button6.grid(row =2, column=2)
    def clicked_1(self):
        self.light1_on = not self.light1_on
        if self.light1_on:
            print("manual - băng tải - ON")
            self.client.write_register(11, 1, unit=self.UNIT)
        else:
            print("manual - băng tải - OFF")
            self.client.write_register(11, 0, unit=self.UNIT)
    def clicked_2(self):
        self.light2_on = not self.light2_on
        if self.light2_on:
            print("manual - van đẩy - ON")
            self.client.write_register(12, 1, unit=self.UNIT)
        else:
            print("manual - van đẩy - OFF")
            self.client.write_register(12, 0, unit=self.UNIT)
    def clicked_3(self):
        self.light3_on = not self.light3_on
        if self.light3_on:
            print("manual - van xoay - ON")
            self.client.write_register(13, 1, unit=self.UNIT)
        else:
            print("manual - van xoay - OFF")
            self.client.write_register(13, 0, unit=self.UNIT)
    def clicked_4(self):
        self.light4_on = not self.light4_on
        if self.light4_on:
            print("manual - van ra vào - ON")
            self.client.write_register(14, 1, unit=self.UNIT)
        else:
            print("manual - van ra vào - OFF")
            self.client.write_register(14, 0, unit=self.UNIT)
    def clicked_5(self):
        self.light5_on = not self.light5_on
        if self.light5_on:
            print("manual - van kéo - ON")
            self.client.write_register(15, 1, unit=self.UNIT)
        else:
            print("manual - van kéo - OFF")
            self.client.write_register(15, 0, unit=self.UNIT)
    def clicked_6(self):
        self.light6_on = not self.light6_on
        if self.light6_on:
            print("manual - van hút - ON")
            self.client.write_register(16, 1, unit=self.UNIT)
        else:
            print("manual - van hút - OFF")
            self.client.write_register(16, 0, unit=self.UNIT)
    def read_initial_state_light_1(self):
        result_light_1 = self.read_register(33)[0]
        if result_light_1 == 1:
            self.canvas_light.itemconfig(self.light1, fill="green")
        else:
            self.canvas_light.itemconfig(self.light1, fill="gray")
        self.after(200, self.read_initial_state_light_1)
    def read_initial_state_light_2(self):
        result_light_2 = self.read_register(34)[0]
        if result_light_2 == 1:
            self.canvas_light.itemconfig(self.light2, fill="green")
        else:
            self.canvas_light.itemconfig(self.light2, fill="gray")
        self.after(200, self.read_initial_state_light_2)
    def read_initial_state_light_3(self):
        result_light_3 = self.read_register(35)[0]
        if result_light_3 == 1:
            self.canvas_light.itemconfig(self.light3, fill="green")
        else:
            self.canvas_light.itemconfig(self.light3, fill="gray")
        self.after(200, self.read_initial_state_light_3)
    def read_initial_state_light_4(self):
        result_light_4 = self.read_register(36)[0]
        if result_light_4 == 1:
            self.canvas_light.itemconfig(self.light4, fill="green")
        else:
            self.canvas_light.itemconfig(self.light4, fill="gray")
        self.after(200, self.read_initial_state_light_4)
    def read_initial_state_light_5(self):
        result_light_5 = self.read_register(37)[0]
        if result_light_5 == 1:
            self.canvas_light.itemconfig(self.light5, fill="green")
        else:
            self.canvas_light.itemconfig(self.light5, fill="gray")
        self.after(200, self.read_initial_state_light_5)
    def read_initial_state_light_6(self):
        result_light_6 = self.read_register(38)[0]
        if result_light_6 ==1:
            self.canvas_light.itemconfig(self.light6, fill="green")
        else:
            self.canvas_light.itemconfig(self.light6, fill="gray")
        self.after(200, self.read_initial_state_light_6)
    # Function to handle closing of small window
    def on_closing_small_window(self):
        response = messagebox.askyesno("Confirm", 
                                       "If you close, the manual mode will turn off and the auto mode will be on again, are you sure you wanna quit?", 
                                       parent=self.small_window)
        if response:
            self.small_window.destroy()
            self.switch.deselect()  # Turn off the switch
            self.light_auto_manual.itemconfig(self.light_for_auto, fill="green")
            self.light_auto_manual.itemconfig(self.light_for_manual, fill="gray")
            self.client.write_register(10, 0, unit=self.UNIT)
# Function to handle switch deselect event
    def close_small_window(self):
        if self.small_window:
            self.small_window.destroy()
            self.small_window = None


    def video_loop(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (self.width, self.height))
            self.fg_mask = self.background_subtractor.apply(frame)

            img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # Convert BGR image to HSV format

            masks = [
                (cv2.inRange(img, self.lower_red, self.upper_red), 0, "red Object"),
                (cv2.inRange(img, self.lower_yellow, self.upper_yellow), 1, "yellow Object"),
                (cv2.inRange(img, self.lower_blue, self.upper_blue), 2, "blue Object"),
                (cv2.inRange(img, self.lower_purple, self.upper_purple), 3, "purple Object")
            ]

            self.register_states = [0, 0, 0, 0]

            for mask, register, label in masks:
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for contour in contours:
                    if cv2.contourArea(contour) > 3000:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (76, 153, 0), 3)  # Draw rectangle
                        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        self.register_states[register] = 1
                        break

            if time.time() - self.last_update_time >= self.update_interval:
                for i in range(4):
                    self.write_register(i, self.register_states[i])
                self.last_update_time = time.time()
        
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.after(10, self.video_loop)  # Update the frame every 10 ms

    def __del__(self):
        # Release the video capture when the object is destroyed
        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    app = CameraApp()
    app.mainloop()