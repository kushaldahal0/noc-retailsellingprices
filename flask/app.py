from flask import Flask, render_template
from bs4 import BeautifulSoup
import requests as req
import pandas as pd
from matplotlib import pyplot as plt
import datetime

app = Flask(__name__)
def webpage(url):
    return req.get(url)


def plot(df, imgname):

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(24,18))
    x = df['effective Date']

    #contains full datas
    yidx = df.columns[1:]

    #contains column names
    ycs = df[yidx]
    for yid in yidx:
        if (yid not in ['LPG', 'ATF (DF)','kerosene']):
            if (yid == 'diesel'):
                ax1.plot(x, ycs[yid], label='diesel and kerosene')
            else:
                ax1.plot(x, ycs[yid], label=yid)

            for i, val in enumerate(ycs[yid]):
                ax1.annotate(f'{val:.2f}', (x.iloc[i], val), textcoords='offset points', xytext=(0, 10), ha='center')
    ax1.legend()
    ax1.set(title=df.name, xlabel=x.name, ylabel="Prices")

    ax2.plot(x, ycs['LPG'], label='LPG')
    ax2.plot(x, ycs['ATF (DF)'], label='ATF (DF)')
    for yid in ['LPG', 'ATF (DF)']:
        for i, val in enumerate(ycs[yid]):
            ax2.annotate(f'{val:.2f}', (x.iloc[i], val), textcoords='offset points', xytext=(0, 10), ha='center')
    ax2.set(title=df.name, xlabel=x.name, ylabel="Prices")
    ax2.legend()
    fig1 = plt.gcf()
    # plt.show()

    fig1.savefig('static/images/rs.png', bbox_inches='tight',transparent=True)

def table(web):
    S = BeautifulSoup(web.content, 'html.parser')
    return S.find_all('table')[-1]


def th_list(table):
    hs = table.find_all('th')
    return [h.text for h in hs]


def rows_data(table):
    rows = table.find_all('tr')[1:]
    rowsr = [row.text for row in rows]
    row_values = []
    dates = []
    for entry in rowsr:
        # Remove leading and trailing whitespace
        entry = entry.strip()

        # Split the entry into lines
        lines = entry.split('\n')

        # Extract the date information
        date_info = lines[0].strip()

        # Extract and clean the numerical values
        values = [line.strip() for line in lines[3:] if line.strip().replace(".", "", 1).isdigit()]

        dates.append(date_info)
        row_values.append(values)
    return dates, row_values


def create_df(h, d, rd, name):
    df = pd.DataFrame(columns=h)
    df.name = name + ' price in Kathmandu, Pokhara, Dipayal'
    all = h
    all.remove('effective Date')
    for i in range(len(rd)):
        l = len(df)
        df.loc[l, 'effective Date'] = d[len(rd) - 1 - i]
        df.loc[l, all] = rd[len(rd) - 1 - i]
    df[all] = df[all].apply(pd.to_numeric, errors='coerce')
    return df


def retail():
    # Requesting for the website
    urlr = 'https://noc.org.np/retailprice'
    webr = webpage(urlr)
    retail = table(webr)
    headr = th_list(retail)
    headr.remove('effective Time')
    date, rdr = rows_data(retail)
    dfretail = create_df(headr, date, rdr, 'Retail Selling')
    dtable = dfretail
    dateu = datetime.date.today()
    plot(dfretail, 'rs')
    return dtable,dateu


@app.route("/")
def index():
    return "/prices for the NOC prices"

@app.route("/home")
def home():
    table,dateup = retail()
    return render_template('index.html',date = dateup, table=table.to_html(classes='data table-auto text-slate-900 dark:text-white', header=True, index=False))

@app.route("/2021")
def hello():
    # retail()
    return '<h1>This is warm hello from flask!</h1>'

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
