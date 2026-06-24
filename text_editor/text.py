from tkinter import *
import tkinter.filedialog
from tkinter import colorchooser

#Saves the text to file
def saveas():
    global text
    t = text.get('1.0', 'end-1c')
    savelocation=tkinter.filedialog.asksaveasfilename()
    file1=open(savelocation, 'w+')
    file1.write(t)
    file1.close()

#Different Fonts available
def FontHelvetica():
    global text
    text.config(font='Helvetica')
def FontCourier():
    global text
    text.config(font='Courier')
def FontTimes():
    global text
    text.config(font='Times')

# Allows user to pick color
def pick_color():
    selected_color = colorchooser.askcolor(title="Select a color")
    
    if selected_color[1]:
        text.config(fg=selected_color[1])
        print(f"RGB: {selected_color[0]}")
        print(f"Hex: {selected_color[1]}")
    
#Initializing page
root = Tk("Text Editor")
text = Text(root)
text.grid()

# Color changing button
color_btn = Button(root, text="Change Color", command=pick_color)
color_btn.grid()

#Font Menu
font=Menubutton(root, text='Font')
font.grid()
font_menu = Menu(font, tearoff=0)
font['menu'] = font_menu
helvetica=IntVar()
courier=IntVar()
times=IntVar()

#Adding buttons for each of the fonts
font_menu.add_checkbutton(label='Helvetica', variable=helvetica, command=FontHelvetica)

font_menu.add_checkbutton(label='Courier', 
variable=courier, 
command=FontCourier)

font_menu.add_checkbutton(label='Times New Roman', variable=times, 
command=FontTimes)

# The save button
button=Button(root, text="Save your beautiful work!", command=saveas)
button.grid()

root.mainloop()