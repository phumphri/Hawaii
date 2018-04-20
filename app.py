"""
## Step 4 - Climate App

Now that you have completed your initial analysis, design a Flask api based on the queries that you have just developed.

* Use FLASK to create your routes.

### Routes

* `/api/v1.0/precipitation`

  * Query for the dates and temperature observations from the last year.

  * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.

  * Return the json representation of your dictionary.

* `/api/v1.0/stations`

  * Return a json list of stations from the dataset.

* `/api/v1.0/tobs`

  * Return a json list of Temperature Observations (tobs) for the previous year

* `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

  * Return a json list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

  * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

  * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

"""
# Import dependencies.
from flask import Flask, jsonify
from datetime import datetime
import pandas as pd
import numpy as np

# Import Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy import and_

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Print all of the classes mapped to the Base
print(Base.classes.keys())

# Assign the Measurement class to a variable called `Measurement`
Measurement = Base.classes.measurement

# Create a session
session = Session(engine)


# Dependency injection.
app = Flask(__name__)

# Test data.
hello_dict = {"Hello": "World!"}

# Home page.
@app.route("/")
def normal():

    s = '<!DOCTYPE html>'
    s += '<html>'
    s += '    <head>'
    s += '        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'
    s += '        <title>Homework 11:  Hawaiian Weather</title>'
    s += '        <link rel="stylesheet" type="text/css" href="viterbi.css"/>'
    s += '        <link rel="shortcut icon" href="https://www.usc.edu/favicon.ico"/>'
    s += '    </head>'
    s += '    <body>'
    s += '        <table>'
    s += '            <tr>'
    s += '                <td>'
    s += '                    <img '
    s += '                        src="data:image/png;base64,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" '
    s += '                        height="175px">  '
    s += ' '                     
    s += '                   '
    s += '                </td>'
    s += '                <td>'
    s += '                    <h1>Hawaii Weather</h1>'
    s += '                    <h3>Organization:  USC Viterbi Data Analytics Bootcamp</h3>'
    s += '                    <h3>Author:  Patrick Humphries</h3>'
    s += '                </td>'
    s += '            </tr>'
    s += ' '            
    s += '            <tr>'
    s += '                <td>'
    s += '                    <p><h2>'
    s += '                        The folloing APIs provide weather data for Hawaii: <br/> <code>'
    s += '                        /api/v1.0/precipitation <br/> '
    s += '                        /api/v1.0/stations <br/> '
    s += '                        /api/v1.0/tobs <br/> '
    s += '                        /api/v1.0/&lt;start date YYYY-MM-DD&gt; <br/> '
    s += '                        /api/v1.0/&lt;start date YYYY-MM-DD&gt;/&lt;end date YYYY-MM-DD&gt; <br/></code></h2> '
    s += '                </td>'
    s += '            </tr>'
    s += '        </table>'
    s += '    </body>'
    s += '</html>'

    return(s)

@app.route("/api/v1.0/precipitation")
def get_precipitation():
    """
    Query for the dates and temperature observations from the last year.
    Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
    Return the json representation of your dictionary
    """
    current_year = int(datetime.today().strftime("%Y"))
    previous_year = current_year - 1
    previous_year_str = str(previous_year)

    rs = session \
        .query(func.substr(Measurement.date, 1, 7), func.sum(Measurement.prcp)) \
        .filter(func.substr(Measurement.date, 1, 4) == previous_year_str) \
        .group_by(func.substr(Measurement.date, 1, 7)) \
        .all()

    precipitation_dict = {}

    for entry in rs:
        precipitation_dict[entry[0]] = entry[1]

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def get_stations():
    """
    Return a json list of stations from the dataset.
    """

    rs = session \
        .query(func.distinct(Measurement.station)) \
        .all()

    stations_list = []

    for entry in rs:
        stations_list.append(entry[0])

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def get_temperatures():
    """
    Return a json list of Temperature Observations (tobs) for the previous year
    """
    current_year = int(datetime.today().strftime("%Y"))
    previous_year = current_year - 1
    previous_year_str = str(previous_year)

    rs = session \
        .query(Measurement.date, Measurement.tobs) \
        .filter(func.substr(Measurement.date, 1, 4) == previous_year_str) \
        .all()

    return jsonify(rs)


@app.route("/api/v1.0/<min_date_str>")
def get_temperatures_from_start(min_date_str):
    """
    Return a json list of the minimum temperature, the average temperature, and
    the max temperature for a given start or start-end range.

    When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all 
    dates greater than and equal to the start date.
    """
    rs = session \
        .query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
        .filter(Measurement.date >= min_date_str) \
        .all()

    tobs_list = rs[0]

    return jsonify(tobs_list)


@app.route("/api/v1.0/<min_date_str>/<max_date_str>")
def get_temperatures_in_range(min_date_str, max_date_str):
    """
    Return a json list of the minimum temperature, the average temperature, and
    the max temperature for a given start or start-end range.

    When given the start and the end date, calculate the `TMIN`, `TAVG`, and 
    `TMAX` for dates between the start and end date inclusive.
    """
    rs = session \
        .query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)) \
        .filter(and_(Measurement.date >= min_date_str),(Measurement.date <= max_date_str)) \
        .all()

    tobs_list = rs[0]

    return jsonify(tobs_list)

if __name__ == "__main__":
    app.run(debug=True)
