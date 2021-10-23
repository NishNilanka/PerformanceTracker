import tkinter as tk
from csv import writer
from datetime import date
from datetime import datetime

import numpy as np
import pandas as pd
import tkcalendar as tkc
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tabulate import tabulate

stf = pd.read_excel("Book1.xlsx", index_col=None, na_values=['NA'],
                    usecols="C,U:XFD")  # only import C column and U to XDF columns
stf.columns = stf.columns.str.replace(' ', '')


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()

    def clearFrame(self):
        # destroy all widgets from frame
        for widget in self.winfo_children():
            widget.destroy()

        # this will clear frame and frame will be empty
        # if you want to hide the empty panel then
        self.pack_forget()


class Page1(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        super().clearFrame()
        self.label = tk.Label(self, text="Day performance")
        self.label.pack(side="top", fill="both", expand=True)

    def load_elements(self):
        self.clearFrame()
        self.btn_save = tk.Button(text='Save', width=10, command=self.apend_to_excel).pack(side="left")
        self.btn_ER = tk.Button(text='ER', width=10, command=self.ER_fun).pack(side="left")
        self.btn_Dya_Percentage = tk.Button(text='Day Percentage', width=15, command=self.percentage).pack(side="left")
        self.btn_chrt = tk.Button(text='Chart', width=10, command=self.plot).pack(side="left")
        self.lbl_bt = tk.Label(text='Select the date :', fg='red', font=('Times New Roman', 12, 'bold')).pack(side="top", fill="both", expand=True)
        self.cal = tkc.Calendar(selectmode='day', year=2021, month=9, day=15)
        self.cal.pack(side="top", fill="both", expand=True)
        self.btn_show = tk.Button(text='Ok', command=self.Show_date).pack(side="left")


    def plot(self):
        self.percentage()
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

        # Creating Canvas
        canv = FigureCanvasTkAgg(fig, master=win)
        canv.draw()

        get_widz = canv.get_tk_widget()
        get_widz.pack()

        win.mainloop()
        # plt.show()

    def ER_fun(self):
        global ER_count
        ER_count = stf['ER'].value_counts()
        ER_count = ER_count.to_frame().reset_index().rename(columns={'index': 'ER_L', 'ER': 'Total'}).sort_values(
            "ER_L")
        ER_count = ER_count.reset_index()
        del ER_count["index"]
        text_line = tabulate(ER_count, headers='keys', tablefmt='psql')
        tk.Label(text=text_line).pack(side="top", fill="both", expand=True)

    def calculation(self):
        self.Show_date()
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

    def createlist(self):
        self.calculation()
        self.ER_fun()
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

    def tot_abs(self):
        self.createlist()
        missing_list = ER_count[
            ~ER_count['ER_L'].isin(tot_absents['ER'])]  # to find the missing rows compire to ER_count and tot_absents
        missing_list = missing_list.rename(
            columns={'ER_L': 'ER', 'Total': 'Day_count'})  # change the column names equalt to tot_absents column names
        missing_list['Day_count'] = 0  # Every missing value absenties count = 0
        global new_tot_absents
        new_tot_absents = tot_absents.append(missing_list,
                                             ignore_index=True)  # add to missnig values to tot_absent dataframe
        new_tot_absents = new_tot_absents.sort_values("ER").reset_index()
        del new_tot_absents["index"]

    def percentage(self):
        self.tot_abs()
        conditions = [(ER_count['ER_L'] == new_tot_absents['ER'])]
        choices = [(new_tot_absents['Day_count'] / ER_count['Total']) * 100]
        new_tot_absents['Percentage'] = np.select(conditions, choices,
                                                  default=(new_tot_absents['Day_count'] / ER_count['Total']) * 100)
        text_line3 = tabulate(new_tot_absents, headers='keys', tablefmt='psql')
        tk.Label(text=text_line3).pack(side="top", fill="both", expand=True)

        new_tot_absents_transpose = new_tot_absents.T
        global tot_absents_transpose
        tot_absents_transpose = new_tot_absents_transpose.drop(['Day_count'], axis=0)
        tot_absents_transpose['Date'] = dt_start
        first_column = tot_absents_transpose.pop('Date')
        tot_absents_transpose.insert(0, 'Date', first_column)

    def apend_to_excel(self):
        self.percentage()
        dt = tot_absents_transpose
        with open('performance.csv', 'a', newline='') as file:
            writer_object = writer(file)
            writer_object.writerow(dt)
            file.close()

    def ER_fun(self):
        global ER_count
        ER_count = stf['ER'].value_counts()
        ER_count = ER_count.to_frame().reset_index().rename(columns={'index': 'ER_L', 'ER': 'Total'}).sort_values(
            "ER_L")
        ER_count = ER_count.reset_index()
        del ER_count["index"]
        text_line = tabulate(ER_count, headers='keys', tablefmt='psql')
        tk.Label(text=text_line).pack(side="top", fill="both", expand=True)

    # date picker
    def Show_date(self):
        u_input = self.cal.get_date()
        global dt_start
        dt_start = datetime.strptime(u_input, '%m/%d/%y').date()  # convert input date such as 2021-09-23
        text_line = "selected date is :", dt_start
        tk.Label(text=text_line, font=('Times New Roman', 10, 'bold'), fg='Blue').pack(side="top", fill="both", expand=True)


class Page2(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        super().clearFrame()
        label = tk.Label(self, text="Range of days performance")
        label.pack(side="top", fill="both", expand=True)


class Page3(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)
        super().clearFrame()
        label = tk.Label(self, text="performance by officer")
        label.pack(side="top", fill="both", expand=True)


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.p1 = Page1(self)
        self.p2 = Page2(self)
        self.p3 = Page3(self)

        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        self.p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.p2.place(in_=container, x=0, y=0, relwidth=1, relheight=1)
        self.p3.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(buttonframe, text="Day", command=self.p1.load_elements)
        b2 = tk.Button(buttonframe, text="Range", command=self.p1.pack_forget)
        b3 = tk.Button(buttonframe, text="Officer", command=self.p3.lift)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")

        self.p1.show()




if __name__ == "__main__":
    root = tk.Tk()
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("850x650+200+200")
    root.title('performance tracker')
    root.mainloop()
