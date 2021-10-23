'''coded by Luchina kaluarachchi'''

import tkinter as tk
import tkcalendar as tkc
from csv import writer
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import date
from tabulate import tabulate
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


window = tk.Tk()
window.title('performance tracker')
window.geometry('850x650+200+200')              #window size
frm_data = tk.Frame(window)

window.rowconfigure(4, {'minsize': 30})
window.columnconfigure(9, {'minsize': 30})

stf = pd.read_excel("Book1.xlsx", index_col=None, na_values=['NA'], usecols="C,U:XFD")     # only import C column and U to XDF columns
stf.columns = stf.columns.str.replace(' ', '')                              # Remove all the spaces in column names

def ER_fun():
    global ER_count
    ER_count = stf['ER'].value_counts()
    ER_count = ER_count.to_frame().reset_index().rename(columns={'index': 'ER_L', 'ER': 'Total'}).sort_values("ER_L")
    ER_count = ER_count.reset_index()
    del ER_count["index"]
    text_line = tabulate(ER_count, headers='keys', tablefmt='psql')
    tk.Label(text=text_line).grid(row=2, column=6)

#date picker
def Show_date():
    u_input = cal.get_date()
    global dt_start
    dt_start = datetime.strptime(u_input, '%m/%d/%y').date()                   #convert input date such as 2021-09-23
    text_line = "selected date is :", dt_start
    tk.Label(text=text_line, font=('Times New Roman', 10, 'bold'), fg='Blue').grid(row=4, column=1)

lbl_bt = tk.Label(text='Select the date :', fg='red', font=('Times New Roman', 12, 'bold')).grid(row=0, column=0)
cal = tkc.Calendar(selectmode='day', year=2021, month=9, day=15)
cal.grid(row=1, column=1, sticky='E')
btn_show = tk.Button(text='Ok', command=Show_date).grid(row=2, column=1)

def calculation():
    Show_date()
    d0 = date(2021, 9, 1)  # minimum date of data have
    d1 = dt_start  # take the user wont date
    days_from = d1 - d0  # how many days from minimum date
    days_from = days_from.days
    col_num = 1 + days_from
    Day_count = (stf.iloc[:, col_num]).value_counts()
    global col_name
    col_name = stf.columns[col_num]

    need = stf[['ER', col_name]]  # select only ER and needed columns
    group = need.groupby(['ER', col_name])  # only group by ER and needed columns
    global take_count
    take_count = group.size().reset_index(name='Count')  # take count of the grouped two columns
def createlist():
    calculation()
    ER_fun()
    ER = (take_count.loc[:, "ER"])  # to call only ER column
    ER = list(set(ER))  # Take the unique values and convert to list

    all_absenteeism_reasons = (take_count.loc[:, col_name])
    all_absenteeism_reasons = list(set(all_absenteeism_reasons))

    absenteeism_reason = list()
    for i in all_absenteeism_reasons:
        if i == 'Health' or i == 'Informed - Other Reasons' or i == 'Long Absent' or i == 'Unauthorized' or i == 'Authorized':
            absenteeism_reason.append(i)

    selected_list = (take_count.loc[(take_count['ER'].isin(ER)) & (take_count[col_name].isin(absenteeism_reason))])
    global tot_absents
    tot_absents = (selected_list.groupby('ER')['Count'].sum().reset_index(name='Day_count')).sort_values("ER")

def tot_abs():
    createlist()
    missing_list = ER_count[~ER_count['ER_L'].isin(tot_absents['ER'])]  # to find the missing rows compire to ER_count and tot_absents
    missing_list = missing_list.rename(columns={'ER_L': 'ER', 'Total': 'Day_count'})  # change the column names equalt to tot_absents column names
    missing_list['Day_count'] = 0  # Every missing value absenties count = 0
    global new_tot_absents
    new_tot_absents = tot_absents.append(missing_list, ignore_index=True)  # add to missnig values to tot_absent dataframe
    new_tot_absents = new_tot_absents.sort_values("ER").reset_index()
    del new_tot_absents["index"]

def percentage():
    tot_abs()
    conditions = [(ER_count['ER_L'] == new_tot_absents['ER'])]
    choices = [(new_tot_absents['Day_count'] / ER_count['Total']) * 100]
    new_tot_absents['Percentage'] = np.select(conditions, choices, default=(new_tot_absents['Day_count'] / ER_count['Total']) * 100)
    # print('\nPercentage of absenteeism according to the officer of', dt_start, ': \n', new_tot_absents)

    text_line3 = tabulate(new_tot_absents, headers='keys', tablefmt='psql')
    tk.Label(text=text_line3).grid(row=1, column=6)

    new_tot_absents_transpose = new_tot_absents.T
    global tot_absents_transpose
    tot_absents_transpose = new_tot_absents_transpose.drop(['Day_count'], axis=0)
    tot_absents_transpose['Date'] = dt_start
    first_column = tot_absents_transpose.pop('Date')
    tot_absents_transpose.insert(0, 'Date', first_column)
    #print(tot_absents_transpose)

from matplotlib.figure import Figure

def plot():
    percentage()
    win = tk.Tk()
    win.title('performance')
    win.geometry('800x450+200+200')

    # Creating Figure.
    fig = Figure(figsize=(9, 7), dpi=100)

    y = new_tot_absents['Percentage']
    x = new_tot_absents['ER']

    # Plotting the graph inside the Figure
    a = fig.add_subplot(111)
    a.barh(x, y)
    a.set_xlabel("Percentage")
    a.set_ylabel("ER officer")
    a.set_title("Percentage of absenteeism according to the officer")
    a.axvline(x=4.5, color='r', linestyle='-')

    #a.legend(labale="")
    #a.grid()

    # Creating Canvas
    canv = FigureCanvasTkAgg(fig, master=win)
    canv.draw()

    get_widz = canv.get_tk_widget()
    get_widz.pack()

    win.mainloop()
    #plt.show()

def apend_to_excel():
    percentage()
    # tot_absents_transpose.to_excel('./Performance.xlsx', 'a', index=False, header=False)

    dt = tot_absents_transpose
    with open('performance.csv', 'a', newline='') as file:
        writer_object = writer(file)
        writer_object.writerow(dt)
        file.close()

today = pd.to_datetime("today")                 #take time and date
today = pd.to_datetime(today).date()             #only select date

def close():
 window.destroy()

#shuld correct this code
def clear():
    for ele in window.winfo_children():
        ele.destroy()

#buttons
frm_but = tk.Frame(window)
btn_save = tk.Button(text='Save', width=10, command=apend_to_excel).grid(row=0, column=5, pady=10)
#btn_clear = tk.Button(text='Clear', width=10, command=clear).grid(row=0, column=6, pady=10)
btn_ER = tk.Button(text='ER', width=10, command=ER_fun).grid(row=0, column=7, pady=10)
btn_Dya_Percentage = tk.Button(text='Day Percentage', width=15, command=percentage).grid(row=0, column=6, pady=10)
#btn_close = tk.Button(text='Close', width=10, command=close).grid(row=0, column=9, pady=10)
btn_chrt = tk.Button(text='Chart', width=10, command=plot).grid(row=0, column=4, pady=10)

window.mainloop()