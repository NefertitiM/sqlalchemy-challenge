# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

climateapp = Flask(__name__)
#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create a session
Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup & Routes
#################################################

@app.route('/')
def home():
    routes = {
        "/api/v1.0/precipitation": "Returns precipitation data for the last 12 months",
        "/api/v1.0/stations": "Returns a list of stations",
        "/api/v1.0/tobs": "Returns temperature observations for the last 12 months",
        "/api/v1.0/<start>": "Returns temperature statistics from a start date",
        "/api/v1.0/<start>/<end>": "Returns temperature statistics between start and end dates"
    }
    return jsonify(routes)

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year before the most recent date
    rec_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    rec_date = datetime.strptime(rec_date, '%Y-%m-%d')
    start_date = rec_date - timedelta(days=365)

    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= rec_date).all()

    # Convert results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query all stations
    results = session.query(Station.station, Station.name).all()
    stations_list = [{"station": station, "name": name} for station, name in results]
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year before the most recent date
    rec_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    rec_date = datetime.strptime(rec_date, '%Y-%m-%d')
    start_date = rec_date - timedelta(days=365)

    # Query temperature observations
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= rec_date).all()

    # Convert results to a list
    tobs_list = [tobs for (tobs,) in results]
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def stats(start, end=None):
    # Define the date range
    start_date = datetime.strptime(start, '%Y-%m-%d')
    if end:
        end_date = datetime.strptime(end, '%Y-%m-%d')
    else:
        end_date = datetime.now()

    # Query the temperature statistics
    results = session.query(
        func.min(Measurement.tobs).label('TMIN'),
        func.avg(Measurement.tobs).label('TAVG'),
        func.max(Measurement.tobs).label('TMAX')
    ).filter(Measurement.date >= start_date).\
     filter(Measurement.date <= end_date).all()

    # Convert results to a dictionary
    stats_dict = {
        "TMIN": results[0].TMIN,
        "TAVG": results[0].TAVG,
        "TMAX": results[0].TMAX
    }

    return jsonify(stats_dict)

if __name__ == '__main__':
    app.run(debug=True)