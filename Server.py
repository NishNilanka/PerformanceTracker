from flask import Flask, render_template, request, url_for, redirect
import pandas as pd

app = Flask(__name__)
stf = pd.read_excel("Book1.xlsx", index_col=None, na_values=['NA'],
                    usecols="C,U:XFD")  # only import C column and U to XDF columns
stf.columns = stf.columns.str.replace(' ', '')
print("Hi")

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/day')
def day():
    return render_template("day.html")


@app.route('/range')
def range():
    return render_template("home.html")


@app.route('/officer')
def officer():
    return render_template("home.html")

@app.route('/selectDate', methods=['GET', 'POST'])
def selectDate():
    if request.method == 'POST':
        startDate = request.form.get('Start_Date', None)
        EndDate = request.form.get('End_Date', None)
        return render_template("day.html", selected_date=EndDate)

if __name__ =='__main__':
    app.run()