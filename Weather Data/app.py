# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify
import numpy as np


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Homepage"""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"The api above should look like /api/v1.0/start-date <br/>"
        f"The date has to be in the format Year-Month-Day<br/>"
        f"Example: 2016-08-23<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"The api above should look like /api/v1.0/start-date/end-date<br/>"
        f"The date has to be in the format Year-Month-Day<br/>"
        f"Example: 2016-08-23/2016-09-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    most_recent = dt.date(2017, 8, 23)

    start_date = (most_recent - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    prcp_scores = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date > start_date).all()

    session.close()

    prcp_list = []
    for date, prcp in prcp_scores:
        prcp_dict = {}
        prcp_dict["date"] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_data = session.query(measurement.station).distinct().all()

    session.close()

    station_list = list(np.ravel(station_data))

    return jsonify(station_list)
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    most_recent = dt.date(2017, 8, 23)

    start_date = (most_recent - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    active_station = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).first()

    tobs = session.query(measurement.date, measurement.tobs).\
    filter(measurement.station == active_station[0]).\
    filter(measurement.date > start_date).all()

    session.close()

    tobs_list = []
    for date, tob in tobs:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tob"] = tob
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    temps = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= start).\
        group_by(measurement.date).all()

    session.close()

    temps_list = []
    for date, tmin, tmax, tavg in temps:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["tmin"] = tmin
        temps_dict["tmax"] = tmax
        temps_dict["tavg"] = tavg
        temps_list.append(temps_dict)

    return jsonify(temps_list)

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    session = Session(engine)

    temps = session.query(measurement.date, func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
    filter(measurement.date >= start, measurement.date <= end).\
    group_by(measurement.date).all()

    session.close()

    temps_list = []
    for date, tmin, tmax, tavg in temps:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["tmin"] = tmin
        temps_dict["tmax"] = tmax
        temps_dict["tavg"] = tavg
        temps_list.append(temps_dict)

    return jsonify(temps_list)

if __name__ == "__main__":
    app.run(debug=True)
