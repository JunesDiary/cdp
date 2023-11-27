import tkinter as tk
import json
from tkinter import ttk, filedialog
from tkinter import messagebox, simpledialog
import math
from prettytable import PrettyTable
from scipy import stats
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
%matplotlib qt

import os
import sys
sys.path.append(os.getcwd())

global filename_getdopplerbeam
global dopplergen_frame
global beam_anddoppler_holder
beam_anddoppler_holder = {}
from PIL import Image, ImageTk, ImageSequence


# Function to resize the image
def resize_image(image_path, width, height):
    original_image = Image.open(image_path)
    resized_image = original_image.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(resized_image)


def read_json_file(file_path):
    
    try:
        with open(file_path, 'r') as json_file:
            loaded_json_string = json_file.read()
            loaded_dict = json.loads(loaded_json_string)
            return loaded_dict
    except FileNotFoundError:
        display_error(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        display_error(f"Error: Unable to decode JSON from file {file_path}")
        return None

def addfor_beamload(result_dict, beamname):
    if beamname in beam_anddoppler_holder:
        return
    else:
        beam_anddoppler_holder[beamname] = result_dict
        return 
    
    

def uvwgen_plotter(scan):

    
    # U V W Generator Codes
    phi = 10 * ((math.pi)/180) #radians
    theta1 = 10 * ((math.pi)/180) #radians
    theta2 = 0 * ((math.pi)/180) #radians
    lamda = 5.660377358 #metres

    for key, value in beam_anddoppler_holder.items():
        if key.upper() == 'Zenith_X'.upper():
            east = value
        elif key.upper() == 'East'.upper():
            west = value    
        elif key.upper() == 'West'.upper():
            zenith = value 
        elif key.upper() == 'North'.upper():  # Corrected condition
            north = value
        elif key.upper() == 'South'.upper():  # Corrected condition
            south = value 

    eastvel = []
    westvel = []
    northvel = []
    southvel = []
    zenithvel = []
    
   
    length = min(len(east[scan]['dopp_freq']), len(west[scan]['dopp_freq']), len(zenith[scan]['dopp_freq']), len(north[scan]['dopp_freq']), len(south[scan]['dopp_freq']))

    for i in range(0,length):
        eastvel.append(-(east[scan]['dopp_freq'][i] * lamda)/2)
        westvel.append(-(west[scan]['dopp_freq'][i] * lamda)/2)
        northvel.append(-(north[scan]['dopp_freq'][i] * lamda)/2)
        southvel.append(-(south[scan]['dopp_freq'][i] * lamda)/2)
        zenithvel.append(-(zenith[scan]['dopp_freq'][i] * lamda)/2)

    vwind = []
    uwind = []
    wwind = []
    speed = []
    direction = []

    for i in range(0,length):

        u = (eastvel[i] - westvel[i])/(2*math.sin(phi))
        v = (northvel[i] - southvel[i])/(2*math.sin(phi))
        w = zenithvel[i]
        d = math.atan(v/u)

        vwind.append(v)
        uwind.append(u)
        wwind.append(w)
        direction.append(d)    


    # PLOTTING CODES    

    x1 = [] #u wind
    x2 = [] #v wind
    x3 = [] #w wind
    y1 = [] #u height
    y2 = [] #v height
    y3 = [] #w height

    lower = -40
    upper = 20
    for i in range(0, len(uwind)):
        if uwind[i]<upper and uwind[i]>lower:
            x1.append(uwind[i])
            y1.append(east[scan]['height'][i])

    for i in range(0, len(vwind)):
        if vwind[i]<upper and vwind[i]>lower:
            x2.append(vwind[i])
            y2.append(east[scan]['height'][i])

    for i in range(0, len(wwind)):
        if wwind[i]<upper and vwind[i]>lower:
            x3.append(wwind[i])
            y3.append(east[scan]['height'][i])

    w = 14
    p = 2
    x1_smooth = savgol_filter(savgol_filter(x1, w, p),w,p)
    x2_smooth = savgol_filter(savgol_filter(x2, w, p),w,p)
    x3_smooth = savgol_filter(savgol_filter(x3, w, p),w,p)

    # Create a figure with two subplots side by side
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(12, 5))

    # axes1
    ax1.plot(x1_smooth, y1, label='u', linestyle='-', color='blue', linewidth=2)
    #ax1.plot(x1, y, label='raw u', linestyle='--', color='black', linewidth=0.5)
    ax1.set_xlabel('Wind Velocity (m/s)')
    ax1.set_ylabel('Height (km)')
    ax1.set_title('Zonal')
    ax1.yaxis.set_major_locator(ticker.MaxNLocator(nbins=9))
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend()

    # axes2
    ax2.plot(x2_smooth, y2, label='v', linestyle='-', color='red', linewidth=2)
    #ax2.plot(x2, y, label='raw v', linestyle='--', color='black', linewidth=0.5)
    ax2.set_xlabel('Wind Velocity (m/s)')
    ax2.set_ylabel('Height (km)')
    ax2.set_title('Meridional')
    ax2.yaxis.set_major_locator(ticker.MaxNLocator(nbins=9))
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend()

    # axes3
    ax3.plot(x3_smooth, y3, label='w', linestyle='-', color='green', linewidth=2)
    #ax3.plot(x2, y, label='raw v', linestyle='--', color='black', linewidth=0.5)
    ax3.set_xlabel('Wind Velocity (m/s)')
    ax3.set_ylabel('Height (km)')
    ax3.set_title('Vertical')
    ax3.yaxis.set_major_locator(ticker.MaxNLocator(nbins=9))
    ax3.grid(True, linestyle='--', alpha=0.6)
    ax3.legend()


    # Adjust the spacing between subplots
    plt.tight_layout()
    return fig






#functions called by tkinter appd
def get_beam_names(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()

    beampos = []

    for line in lines:
        words = (line.strip()).split(' ')
        if 'Position' in words:
            if words[-1] not in beampos:
                beampos.append(words[-1])

    return beampos


def expinforeader(filename):
    file = open(filename, 'r')
    lines = file.readlines()
    file.close()

    count = 0
    datatransfer = False
    expinfo = {}

    for line in lines:
        count = count + 1

        words = (line.strip()).split(' ')
        if 'HEADER' in words:
            datatransfer = True

        if datatransfer:
            if 'Date' in words:
                expinfo['date'] = words[-1]
            elif 'Time' in words:
                expinfo['time'] = words[-1]
            elif 'bins:' in words:
                expinfo['bins'] = words[-1]
            elif 'FFT' in words:
                expinfo['fft'] = words[-1]
            elif 'coherent' and 'integs:' in words:
                expinfo['noofcoh'] = words[-1]
            elif 'incoh.integs'  in words:
                expinfo['noofincoh'] = words[-1]
            elif 'IPP' in words:
                expinfo['ipp'] = words[-1]
            elif 'Pulse' in words:
                expinfo['pulse'] = words[-1]
            elif 'Beams:' in words:
                expinfo['noofbeams'] = words[-1]    
            elif 'Reciever' in words:
                expinfo['receiver'] = words[-1]                
            elif 'Comments:' in words:
                datatransfer = False
                break
                
    return expinfo


def getdopplerfrombeam(readbeam, filename):

    
    file = open(filename, 'r') #input
    lines = file.readlines()
    file.close()
    #readbeam = 'West'
    
    scan = 0
    temp = []
    total_power = []
    mean_dopp_freq = []
    spec_width = []
    temp_fft = []
    height = []
    freqbins = []

    main_readings = {}
    readings = {}

    targetbeam = False
    firsttime = True
    readpower_out = False
    readpower_in = False
    allow = False
    beampos = get_beam_names(filename)
    
    #information for moment calculation
    ipp = int(expinforeader(filename)['ipp']) #must be in milliseconds !!!
    totalbins = int(expinforeader(filename)['fft'])

    for i in range(0,totalbins):
        freqbins.append((((i+1)-(totalbins/2))* 1000000 )/(ipp * totalbins*totalbins))
    
    #print(beamposdict)
    for line in lines:

        words = (line.strip()).split(' ')

        if 'HEADER' in words:
            readpower_out = False
            readpower_in = False


        #beam chooser
        elif 'Position' in words:
            if words[-1] in beampos and words[-1] == readbeam:
                targetbeam = True
                if mean_dopp_freq != []:
                    #print('transfer')
                    readings['totalpower'] = total_power
                    readings['dopp_freq'] = mean_dopp_freq
                    readings['width'] = spec_width


                    try:
                        readings['height'] = height
                        #print(scan, words[-1])
                    except:
                        None
                    #print(readings)
                    main_readings[int(scan)] = readings

                    readings = {}
                    mean_dopp_freq = []
                    spec_width = []
                    height = []

                readpower_in = True
            else:
                targetbeam = False

        #read scan cycle number for storing purposes
        elif 'cycle:' in words and targetbeam:            
            scan = words[-1]

        elif 'Height' in words and targetbeam:
            readpower_out = True
            height.append(words[-1])

        elif readpower_out:
            if readpower_in:
                if temp_fft != [] and words[0] == '' :
                    #print('compute')
                    if temp_fft[0] == '':
                        temp_fft = temp_fft[1:]
                    
                    #noise estimation and elimination
                    noisethreshold = estimatenoise(temp_fft, totalbins)
                    temp_fft = [x - noisethreshold for x in temp_fft]
                    
                    #zeroth moment
                    total_power.append(sum(temp_fft))
                    
                    #first moment calculation
                    freq_power_product = 0
                    for i in range(0,len(temp_fft)):
                        freq_power_product = freq_power_product + (freqbins[i] * temp_fft[i])                     
                    mean_dopp_freq.append(freq_power_product / sum(temp_fft))
                    
                    #second moment calculation
                    freqsquared_power_product = 0
                    for i in range(0,len(temp_fft)):
                        freqsquared_power_product = freqsquared_power_product + (((freqbins[i] - (freq_power_product / sum(temp_fft)))**2) * temp_fft[i])                     
                    spec_width.append(freqsquared_power_product / sum(temp_fft))
                              
                    temp_fft = []

                else:
                    #print(words[0])
                    try:
                        temp_fft.append(float(words[0]))
                    except:
                        temp_fft.append(words[0])

    #for transfering the last datas calculated as there is no HEADER word at last.                    
    readings['totalpower'] = total_power
    readings['dopp_freq'] = mean_dopp_freq
    readings['width'] = spec_width


    try:
        readings['height'] = height
        #print(scan, words[-1])
    except:
        None
    #print(readings)
    main_readings[int(scan)] = readings

    readings = {}
    mean_dopp_freq = []
    spec_width = []
    height = []


    return main_readings
    #------------------------------------------------------------------------------------



    
#local functions
def estimatenoise(a, fft):
    a.sort()
    pn = 0
    rn = []

    for n in range(1,fft+1):
        for i in range(0,n):
            pn = pn + (a[i] / (fft + i))

        qn = 0
        for i in range(0,fft):
            qn = qn + ((a[i] ** 2) / (n+1))
        qn = qn - (pn**2)

        if qn>0:
            rn.append((pn**2)/(qn*(n+1)))
        else:
            rn.append('None')

    for i in range(1,len(rn)+1):
        if rn[i-1] == 'None':
            continue
        else:
            if rn[i-1] > 1:
                return a[i-1]
    
    return a[0]









# ----------------------------------------------------------------------
def button_click(button_text):
    if button_text == "Beam names":
           
        filename = filedialog.askopenfilename(title="Select an ASCII Spectral File", filetypes=[("All Files", "*.*")])
        if filename:
            beams_names = get_beam_names(filename)
            result = f"Filename: {filename}\nNumber of Beams: {len(beams_names)}\nBeam names: {' '.join(beams_names)}\n"
            warning = "\nWarning: Please note that the beam names are as per read from the file and may not mean literally. Kindly consult with the technical team at CU-ST Radar for clarifications on actual beam angles for each beam position mentioned here"
            display_result(result)
            display_warning(warning)
    
        else:
            error = f"Error: No file selected"
            display_error(error)
            
    elif button_text == 'Read Experiment Details':

            
        filename = filedialog.askopenfilename(title="Select an ASCII Spectral File", filetypes=[("All Files", "*.*")])
        if filename:
            result = expinforeader(filename)
            table = PrettyTable(['Label', 'Value'])
            for key, value in result.items():
                table.add_row([key, value])
                
            display_result(str(table))
            
    
        else:
            error = f"Error: No file selected"
            display_error(error)
        
    elif button_text == 'Generate Doppler of Beam':
           
        beamdoppler()
    
    elif button_text == 'Read JSON and Load':
        if len(beam_anddoppler_holder) == 5:
            error = f"Error: Maximum of 5 loaded"
            display_error(error)            
        else:    
            filename = filedialog.askopenfilename(title="Select a JSON File", filetypes=[("JSON", "*.json*")])
            if filename:
                loaded_dict = read_json_file(filename)
                display_result(loaded_dict)
                initial_value = os.path.splitext(os.path.basename(filename))[0]
                beamname = simpledialog.askstring(".", f"Enter Beam Name:", initialvalue=os.path.basename(initial_value))
                addfor_beamload(loaded_dict, beamname)

            else:
                error = f"Error: No file selected"
                display_error(error)
            
    elif button_text == 'Beam Loader':
        # Check if the frame already contains widgets
        if beamloader_frame.winfo_children():
            for widget in beamloader_frame.winfo_children():
                widget.destroy()    


        
        # Add Labels and Text widgets dynamically to uvwgen_frame
        column_headings = ['Beam', 'Status']
        for col, heading_text in enumerate(column_headings):
            heading_label = tk.Label(beamloader_frame, text=heading_text, font=("Helvetica", 12, "bold"))
            heading_label.grid(row=0, column=col, padx=5, pady=5, sticky='w')
    
        for row, (label_text, _) in enumerate(beam_anddoppler_holder.items(), start=1):
            label = tk.Label(beamloader_frame, text=f"{label_text}:")
            label.grid(row=row, column=0, padx=5, pady=5, sticky='w')

            value_textbox = tk.Text(beamloader_frame, wrap=tk.WORD, height=1, width=30, state=tk.NORMAL)
            value_textbox.insert(tk.END, "Loaded")  # Insert the corresponding value
            value_textbox.config(state=tk.DISABLED)
            value_textbox.grid(row=row, column=1, padx=5, pady=5, sticky='w')

        # If there are less than 5 items, add empty Text widgets for the remaining rows
        for row in range(len(beam_anddoppler_holder) + 1, 6):
            label = tk.Label(beamloader_frame, text=f"Beam {row}:")
            label.grid(row=row, column=0, padx=5, pady=5, sticky='w')

            value_textbox = tk.Text(beamloader_frame, wrap=tk.WORD, height=1, width=30, state=tk.NORMAL)
            value_textbox.insert(tk.END, "Not loaded")  # Insert an empty string
            value_textbox.config(state=tk.DISABLED)
            value_textbox.grid(row=row, column=1, padx=5, pady=5, sticky='w')        
    
    elif button_text == 'Plot UVW':
        
        if len(beam_anddoppler_holder) == 5:
            options = len(beam_anddoppler_holder[next(iter(beam_anddoppler_holder))])
            scancycle = simpledialog.askstring(".", f"Enter Scan cycle (1 to {options}) to plot:")
            fig = uvwgen_plotter(scancycle)
            
            # Create a FigureCanvasTkAgg, which can embed Matplotlib figures in Tkinter
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            # Create a button to close the window
            close_button = ttk.Button(root, text="Close", command=root.destroy)
            close_button.pack(side=tk.BOTTOM)


        else:
            error = f"Error: Load 5 beams to use this function"
            display_error(error)
    else:
        error = f"Error: Not yet available! Work in progress. Thank you for your patience"
        display_error(error)
        
        
# Function to handle button clicks in the result pane for Button 3
def beamdoppler():
    global filename_getdopplerbeam
    filename_getdopplerbeam = None  
    # Ask the user a question    
    if len(beam_anddoppler_holder) == 5:
        loadbeam = False
    else:
        answer = messagebox.askquestion("Question", "Do you want to load JSON file for UVW Gen after the processing?")
        if answer == "yes":
            display_warning('Status: The doppler beam will be loaded')
            loadbeam = True
        else:
            display_warning('Status: The doppler beam will not be loaded')
            loadbeam = False
    
    # Check if the frame already contains widgets
    if dopplergen_bottom_leftframe.winfo_children():
        for widget in dopplergen_bottom_leftframe.winfo_children():
            widget.destroy()
        
    
    # If the frame is empty, create new widgets    
    # Function to handle file selection
    def choose_file():
        global filename_getdopplerbeam
        filename_getdopplerbeam = filedialog.askopenfilename(title="Select an ASCII Spectral File", filetypes=[("All Files", "*.*")])
        
        if filename_getdopplerbeam:
            file_label.config(text=f"Chosen File: {filename_getdopplerbeam}")
        else:
            error = f"Error: No file selected"
            display_error(error)
            filename_getdopplerbeam = None
        
    # Function to handle processing of entered text and filename
    def process_data():
        
        if filename_getdopplerbeam != None:
            beamname = text_input.get("1.0", "end-1c")  # Get the text from the text input widget
            result_dict = getdopplerfrombeam(beamname, filename_getdopplerbeam)
            
            if loadbeam == True: 
                addfor_beamload(result_dict, beamname)

            # Ask the user for the save location
            save_directory = filedialog.askdirectory()

            # Check if the user canceled the operation
            if not save_directory:
                return

            # Construct the full path for the JSON file
            json_file_path = tk.filedialog.asksaveasfilename(
                defaultextension=".json", filetypes=[("JSON files", "*.json")],
                initialdir=save_directory, initialfile="output.json"
            )

            # Construct the full path for the text file
            #text_file_path = tk.filedialog.asksaveasfilename(
            #    defaultextension=".txt", filetypes=[("Text files", "*.txt")],
            #    initialdir=save_directory, initialfile="output.txt"
           # )

            # Check if the user canceled the operation
            if not json_file_path : #or not text_file_path
                return

            # Save the dictionary to a JSON file


            # Save the dictionary to the chosen JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(result_dict, json_file)
            display_warning(f"Status: Dictionary saved to JSON file: {json_file_path}")
            # Save the dictionary to the chosen text file
            #with open(text_file_path, 'w') as text_file:
            #    text_file.write(str(result_dict))

            # Optionally, provide feedback to the user
            #print(f"Dictionary saved to JSON file: {json_file_path}")
            #print(f"Dictionary saved to text file: {text_file_path}")
    # Add a heading to the bottom left pane
    dopplergen_heading = tk.Label(dopplergen_bottom_leftframe, text="Doppler File Read", font=("Helvetica", 14, "bold"), bg="white")
    dopplergen_heading.pack(side=tk.TOP, padx=5, pady=(3, 3))
    
    # Create a "Choose a File" button
    choose_file_button = tk.Button(dopplergen_bottom_leftframe, text="Select an ASCII Spectral File", command=choose_file)
    choose_file_button.pack(pady=2)
    
    #print(filename_getdopplerbeam)

    # Create a label to display the chosen file
    file_label = tk.Label(dopplergen_bottom_leftframe, text="Chosen File: None")
    file_label.pack(pady=2)
    

    # Create a text input widget
    text_heading = tk.Label(dopplergen_bottom_leftframe, text="Write Beam name to extract", font=("Helvetica", 10), bg="white")
    text_heading.pack(pady=2)
    text_input = tk.Text(dopplergen_bottom_leftframe, wrap=tk.WORD, height=2, width=10)
    text_input.pack(pady=2)

    # Create a button to process the entered text and filename
    process_button = tk.Button(dopplergen_bottom_leftframe, text="Extract Doppler from Beam", command=process_data)
    process_button.pack(pady=2)
    
def clear_warning_text():
    bottom_pane_text.config(state=tk.NORMAL)  # Allow modifications
    bottom_pane_text.delete(1.0, tk.END)  # Clear existing text
    bottom_pane_text.config(state=tk.DISABLED)  # Disable further modifications


# Function to display result in the top pane using Text widget
def display_result(result):
    top_pane_text.config(state=tk.NORMAL)  # Allow modifications
    top_pane_text.delete(1.0, tk.END)  # Clear existing text
    top_pane_text.insert(tk.END, result)
    top_pane_text.config(state=tk.DISABLED)  # Disable further modifications

# Function to display warning in the bottom pane using Text widget
def display_warning(warning):
    bottom_pane_text.config(state=tk.NORMAL)  # Allow modifications and set text color to orange
    bottom_pane_text.insert(tk.END, "\n" + warning)
    #bottom_pane_text.insert(tk.END, "\n" + warning, ("darkorange",))  # Insert text at the end with a newline
    #bottom_pane_text.tag_configure("darkorange", foreground="FF8C00")  # Configure a tag for the orange color
    bottom_pane_text.config(state=tk.DISABLED)  # Disable further modifications

def display_error(error):
    bottom_pane_text.config(state=tk.NORMAL)  # Allow modifications
    bottom_pane_text.insert(tk.END, "\n" + error, ("red",))
    bottom_pane_text.tag_configure("red", foreground="red")  # Configure a tag for the orange color
    bottom_pane_text.config(state=tk.DISABLED)  # Disable further modifications






    
#-----------------------------------------------------------------------------------------



# Create the main window with a specified size
root = tk.Tk()






root.title("CU-ST Radar Data Processor")
root.geometry("1200x800")  # Set the initial size to 1200x800 pixels
root.iconbitmap("app_icon.ico")

# Create a style to configure the tabs
style = ttk.Style()
style.configure("TNotebook.Tab", padding=[20, 5], font=("Helvetica", 12), borderwidth=3)  # Set the font size for the tabs

# Create a notebook (tabs container)
notebook = ttk.Notebook(root, width=1200, height=800)  # Adjust the size of the notebook

#------------------------------------------------------------
# Create Tab 1
tab1 = ttk.Frame(notebook)
tab1_icon = resize_image("active.png", 20, 20)
notebook.add(tab1, text="Active Mode", image=tab1_icon, compound=tk.LEFT)

# Create PanedWindow for left and right panes
paned_window = tk.PanedWindow(tab1, orient=tk.HORIZONTAL)
paned_window.pack(expand=True, fill="both")

# Create Left Pane with a light grey color
left_pane = tk.Frame(paned_window, bg="lightgrey", width=250)  # Increased width to 250
paned_window.add(left_pane)



# Create top pane in the left pane
top_leftpane = tk.PanedWindow(left_pane, orient=tk.VERTICAL, bg="white")

# Create a label for the heading
functions_heading = tk.Label(left_pane, text="Functions", font=("Helvetica", 16, "bold"), bg="#ecf0f1")
functions_heading.pack(fill="x", padx=5, pady=(5, 5))

# Create individual buttons in the left pane
style = ttk.Style()
style.configure("TButton", padding=(10, 5, 10, 5), font='Helvetica 12 bold', background='#4CAF50', foreground='black')

read_experiment_details = ttk.Button(top_leftpane, text="Read Experiment Details", command=lambda: button_click("Read Experiment Details"))
read_experiment_details.pack(fill="x", padx=0, pady=0)

button_beam_names = ttk.Button(top_leftpane, text="Get Beam names", command=lambda: button_click("Beam names"))
button_beam_names.pack(fill="x", padx=0, pady=0)

beamdopplergen = ttk.Button(top_leftpane, text="Generate Doppler of Beam", command=lambda: button_click("Generate Doppler of Beam"))
beamdopplergen.pack(fill="x", padx=0, pady=0)

read_json_load = ttk.Button(top_leftpane, text="Read JSON and Load Beam", command=lambda: button_click("Read JSON and Load"))
read_json_load.pack(fill="x", padx=0, pady=0)

beamloader = ttk.Button(top_leftpane, text="Refresh Beams", command=lambda: button_click("Beam Loader"))
beamloader.pack(fill="x", padx=0, pady=0)

plotuvw = ttk.Button(top_leftpane, text="Plot UVW", command=lambda: button_click("Plot UVW"))
plotuvw.pack(fill="x", padx=0, pady=0)

# Pack top_leftpane in the left_pane
top_leftpane.pack(fill="both", expand=True)

# Create bottom pane in the left pane for dopplergen_frame
dopplergen_bottom_leftframe = tk.Frame(left_pane, bg="white")
# Pack dopplergen_bottom_leftframe in the left_pane
dopplergen_bottom_leftframe.pack(fill="both", expand=True)

# Create bottom pane in the left pane for dopplergen_frame
beamloader_frame = tk.Frame(left_pane, bg="white")
# Pack dopplergen_bottom_leftframe in the left_pane
beamloader_frame.pack(fill="both", expand=True)


# Create Right Pane with a PanedWindow to divide into top and bottom panes
right_pane = tk.Frame(paned_window, bg="white")
paned_window.add(right_pane)


# Top Pane in the Right Pane
top_pane = tk.Frame(right_pane)
top_pane_text = tk.Text(top_pane, wrap=tk.WORD, state=tk.DISABLED)
top_pane_text.pack(fill="both", expand=True)
top_pane.pack(fill="both", expand=True)

# Thin Bottom Pane in the Right Pane
bottom_pane = tk.Frame(right_pane)
bottom_pane_text = tk.Text(bottom_pane, wrap=tk.WORD, state=tk.DISABLED, height = 0.1)  # Set the height to make it thinner
bottom_pane_text.pack(fill="both", expand=True)
bottom_pane.pack(fill="both", expand=True)

# Add a heading to the bottom pane
warning_heading = tk.Label(bottom_pane, text="Warnings/Errors", font=("Helvetica", 10, "bold"))
warning_heading.pack(side=tk.TOP, padx=5)

# Clear Text button in the warning pane
clear_warning_button = tk.Button(bottom_pane, text="Clear Text", command=clear_warning_text)
clear_warning_button.pack(side=tk.BOTTOM, pady=5)
#------------------------------------------------------------

#------------------------------------------------------------
# Create Tab 2
tab2 = ttk.Frame(notebook)
tab2_icon = resize_image("passive.png", 20, 20)
notebook.add(tab2, text="Passive Mode", image=tab2_icon, compound=tk.LEFT)

# Create content for Tab 2
label2 = tk.Label(tab2, text="Content for Passive Mode")
label2.pack(padx=20, pady=20)
#------------------------------------------------------------


#------------------------------------------------------------
# Create Tab 3
tab3 = ttk.Frame(notebook)
tab3_icon = resize_image("tools.png", 20, 20)
notebook.add(tab3, text="Tools", image=tab3_icon, compound=tk.LEFT)

# Create content for Tab 2
label3 = tk.Label(tab3, text="Content for Tools Mode")
label3.pack(padx=20, pady=20)

#azimuth off zenith calculator
#

#------------------------------------------------------------

#------------------------------------------------------------
# Create Tab 4
tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Credits", compound=tk.LEFT)

# Create content for Tab 2
label4 = tk.Label(tab4, text="Created and Maintained by: Arjun Ghosh \n Contact: arjunghosh@ieee.org \n\n\n Last Update: 10:30 AM IST, 26 Nov 2023")
label4.pack(padx=100, pady=20)
#------------------------------------------------------------
# Pack the notebook to make it visible
notebook.pack(expand=True, fill="both")

# Start the application
root.mainloop()