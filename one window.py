# from tkinter import *
# import tkcalendar
# from datetime import timedelta
#
# root = Tk()
#
# def date_range(start, stop):
#     global dates  # If you want to use this outside of functions
#
#     dates = []
#     diff = (stop - start).days
#     for i in range(diff + 1):
#         day = start + timedelta(days=i)
#         dates.append(day)
#     if dates:
#         print(dates)  # Print it, or even make it global to access it outside this
#     else:
#         print('Make sure the end date is later than start date')
#
#
# date1 = tkcalendar.DateEntry(root)
# date1.pack(padx=10, pady=10)
#
# date2 = tkcalendar.DateEntry(root)
# date2.pack(padx=10, pady=10)
#
# Button(root, text='Selected date range is : \n    ', command=lambda: date_range(date1.get_date(), date2.get_date())).pack()
#
# root.mainloop()






import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 100000)       #change the display defult values
pd.set_option('display.max_columns', 100000)

#import data
stf = pd.read_excel("Book1.xlsx", index_col=None, na_values=['NA'], usecols="C,U:XFD")  # only import C column and U to XDF columns
stf.columns = stf.columns.str.replace(' ', '')  # Remove all the spaces in column names
# print(stf.columns)

#calculate employess head count owned by ER officer
ER_count = stf['ER'].value_counts()
ER_count = ER_count.to_frame().reset_index().rename(columns={'index': 'ER_L', 'ER': 'Total'}).sort_values("ER_L")
ER_count = ER_count.reset_index()
del ER_count["index"]
#print("\nTotal number of employees owned by the officer :\n", ER_count)


#ask the range of dates
today = pd.to_datetime("today")  # take time and date
today = pd.to_datetime(today).date()  # only select date

default = str(today)  # Convert to string format to today value
u_input = input("Input start date ex(2021-10-01) : ")
u_input2 = input("Input end date ex(2021-10-01) : ")


if not u_input:
    u_input = default  # if user does not enter any date, get today as user date
    if not u_input2:
        u_input2 = default
try:
    dt_start = datetime.strptime(u_input, '%Y-%m-%d').date()  # user date format is inccorect, rice as error.
    dt_start2 = datetime.strptime(u_input2, '%Y-%m-%d').date()

except ValueError:
    print("Incorrect format")
    exit()

#calculation of dates
from datetime import date

d0 = date(2021, 9, 1)  # minimum date of data have
d1 = dt_start  # take the user wont date
d2 = dt_start2

days_from_start = (d1 -d0)              #how many days to start from 2021-9-1
days_from_end = (d2-d0)                 #how many days to ends from 2021-9-1

days_from_start = days_from_start.days
days_from_end = days_from_end.days
difference = days_from_end - days_from_start

#print('difference between start and end : ', difference)
#print("days from start : ", days_from_start)
#print("days from end : ", days_from_end)

select_column_list = []
for i in range(difference+1):
    select_column_list.append(days_from_start +1 + i)

dict = {}

# col_num = 1 + days_from_start

#take the colum names in original data set
for j in select_column_list:
    col_num = j
    Day_count = (stf.iloc[:, col_num]).value_counts()
    #print('Day_count \n', Day_count)
    col_name = stf.columns[col_num]

    need = stf[['ER', col_name]]  # select only ER and needed columns
    group = need.groupby(['ER', col_name])  # only group by ER and needed columns
    take_count = group.size().reset_index(name='Count')  # take count of the grouped two columns
    # print("\nThe total number of absences of the officer \n", take_count)

    ER = (take_count.loc[:, "ER"])  # to call only ER column
    ER = list(set(ER))  # Take the unique values and convert to list

    all_absenteeism_reasons = (take_count.loc[:, col_name])
    all_absenteeism_reasons = list(set(all_absenteeism_reasons))

    absenteeism_reason = list()
    for i in all_absenteeism_reasons:
        if i == 'Health' or i == 'Informed - Other Reasons' or i == 'Long Absent' or i == 'Unauthorized' or i == 'Authorized':
            absenteeism_reason.append(i)
    # Create wonted list
    selected_list = (take_count.loc[(take_count['ER'].isin(ER)) & (take_count[col_name].isin(absenteeism_reason))])
    # print("\nComplete list of absences affecting the officer's performance: \n", selected_list)
    tot_absents = (selected_list.groupby('ER')['Count'].sum().reset_index(name='Day_count')).sort_values("ER")
    # print("total absents is", col_name, " :\n", (tot_absents))

    # equality = ER_count['ER_L'].equals(tot_absents['ER'])
    missing_list = ER_count[~ER_count['ER_L'].isin(tot_absents['ER'])]  # to find the missing rows compire to ER_count and tot_absents
    missing_list = missing_list.rename(columns={'ER_L': 'ER', 'Total': 'Day_count'})  # change the column names equalt to tot_absents column names
    missing_list['Day_count'] = 0  # Every missing value absenties count = 0
    new_tot_absents = tot_absents.append(missing_list, ignore_index=True)  # add to missnig values to tot_absent dataframe
    new_tot_absents = new_tot_absents.sort_values("ER").reset_index()
    del new_tot_absents["index"]
    #print("new total absents ",  col_name, ": \n", new_tot_absents)

    # total absents of ER
    # print("\n The total value of absenteeism in a day, according to the officer : \n", tot_absents)

    conditions = [(ER_count['ER_L'] == new_tot_absents['ER'])]
    choices = [(new_tot_absents['Day_count'] / ER_count['Total']) * 100]
    new_tot_absents['Percentage'] = np.select(conditions, choices, default=(new_tot_absents['Day_count'] / ER_count['Total']) * 100)

    del new_tot_absents["Day_count"]            # delete day count column


    dict[j] = new_tot_absents.set_index('ER').T.to_dict('list')         # convert to new total absents dataframe to dictionary
    # print('\nPercentage of absenteeism according to the officer of', col_name, ': \n', new_tot_absents)


new = pd.DataFrame.from_dict(dict)                      # convert dictionary to dataframe
braket_remove = new.applymap(lambda x : x[0])                   # remove all the squre brackets in dataframe


#print("\nbefore delete colums\n\n ", new)

avarages_days = braket_remove.drop(braket_remove.std()[(braket_remove.std() == 0)].index, axis=1)       #removing holidays
length_columns = len(avarages_days.columns)         #take the length of columns

avarages_days["sum"] = avarages_days.sum(axis=1)            # To take the sum of rows
avarages_days["Average"] = avarages_days['sum']/length_columns                  #Take the average column
print(avarages_days)

avarages_days = avarages_days.reset_index()
avarages_days = avarages_days.rename(columns={'index': 'ER'})
final_average_list = avarages_days[["ER", "Average"]]               #only get ER and average columns

print(avarages_days)
print(final_average_list)

plt.barh(avarages_days['ER'], avarages_days['Average'])
plt.title('Percentage of Absenteeism from %s to %s' % (d1, d2))
plt.xlabel('Percentage')
plt.axvline(x=4.5, color='r', linestyle='-')
plt.show()