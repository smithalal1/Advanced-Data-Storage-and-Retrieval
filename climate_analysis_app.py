"cells": [
  {
  "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import datetime as dt\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import datetime as dt\n",
    "import sqlalchemy\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func\n",
    "from flask import Flask, jsonify"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "engine = create_engine(\"sqlite:///hawaii.sqlite\")\n",
    "Base = automap_base()\n",
    "Base.prepare(engine, reflect=True)\n",
    "Station = Base.classes.station\n",
    "Measurements = Base.classes.measurement\n",
    "session = Session(engine)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "app = Flask(__name__)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/\")\n",
    "#Apparently, defining the Flask app in the same cell as the routes causes Jupyter Notebook to violently spazz, hence the separation...\n",
    "def welcome():\n",
    "    \"\"\"List all available api routes.\"\"\"\n",
    "    return (\n",
    "        f\"Available Routes:<br/>\"\n",
    "        f\"<br/>\"\n",
    "        f\"/api/v1.0/precipitation<br/>\"\n",
    "        f\"- List of prior year rain totals from all stations<br/>\"\n",
    "        f\"<br/>\"\n",
    "        f\"/api/v1.0/stations<br/>\"\n",
    "        f\"- List of Station numbers and names<br/>\"\n",
    "        f\"<br/>\"\n",
    "        f\"/api/v1.0/tobs<br/>\"\n",
    "        f\"- List of prior year temperatures from all stations<br/>\"\n",
    "        f\"<br/>\"\n",
    "        f\"/api/v1.0/start<br/>\"\n",
    "        f\"- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX temperature for all dates greater than and equal to the start date<br/>\"\n",
    "        f\"<br/>\"\n",
    "        f\"/api/v1.0/start/end<br/>\"\n",
    "        f\"- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX temperature for dates between the start and end date inclusive<br/>\"\n",
    "\n",
    "    )"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/precipitation\", endpoint = \"func1\")\n",
    "\n",
    "def precipitation():\n",
    "    \"\"\"Return a list of rain fall for prior year\"\"\"\n",
    "    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)\n",
    "    rain = session.query(Measurement.date, Measurement.prcp).\\\n",
    "        filter(Measurement.date > last_year).\\\n",
    "        order_by(Measurement.date).all()\n",
    "\n",
    "# Create a list of dicts with `date` and `prcp` as the keys and values\n",
    "    rain_totals = []\n",
    "    for result in rain:\n",
    "        row = {}\n",
    "        row[\"date\"] = rain[0]\n",
    "        row[\"prcp\"] = rain[1]\n",
    "        rain_totals.append(row)\n",
    "\n",
    "    return jsonify(rain_totals)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/stations\")\n",
    "def stations():\n",
    "    stations_query = session.query(Station.name, Station.station)\n",
    "    stations = pd.read_sql(stations_query.statement, stations_query.session.bind)\n",
    "    return jsonify(stations.to_dict())"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/tobs\")\n",
    "def tobs():\n",
    "    \"\"\"Return a list of temperatures for prior year\"\"\"\n",
    "#    * Query for the dates and temperature observations from the last year.\n",
    "#           * Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.\n",
    "#           * Return the json representation of your dictionary.\n",
    "    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)\n",
    "    temperature = session.query(Measurement.date, Measurement.tobs).\\\n",
    "        filter(Measurement.date > last_year).\\\n",
    "        order_by(Measurement.date).all()\n",
    "\n",
    "# Create a list of dicts with `date` and `tobs` as the keys and values\n",
    "    temperature_totals = []\n",
    "    for result in temperature:\n",
    "        row = {}\n",
    "        row[\"date\"] = temperature[0]\n",
    "        row[\"tobs\"] = temperature[1]\n",
    "        temperature_totals.append(row)\n",
    "\n",
    "    return jsonify(temperature_totals)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>\")\n",
    "def trip1(start):\n",
    "\n",
    " # go back one year from start date and go to end of data for Min/Avg/Max temp   \n",
    "    start_date= dt.datetime.strptime(start, '%Y-%m-%d')\n",
    "    last_year = dt.timedelta(days=365)\n",
    "    start = start_date-last_year\n",
    "    end =  dt.date(2017, 8, 23)\n",
    "    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\\\n",
    "        filter(Measurement.date >= start).filter(Measurement.date <= end).all()\n",
    "    trip = list(np.ravel(trip_data))\n",
        return jsonify(trip)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [],
   "source": [
    "@app.route(\"/api/v1.0/<start>/<end>\")\n",
    "def trip2(start,end):\n",
    "\n",
    "  # go back one year from start/end date and get Min/Avg/Max temp     \n",
    "    start_date= dt.datetime.strptime(start, '%Y-%m-%d')\n",
    "    end_date= dt.datetime.strptime(end,'%Y-%m-%d')\n",
    "    last_year = dt.timedelta(days=365)\n",
    "    start = start_date-last_year\n",
    "    end = end_date-last_year\n",
    "    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\\\n",
    "        filter(Measurement.date >= start).filter(Measurement.date <= end).all()\n",
    "    trip = list(np.ravel(trip_data))\n",
    "    return jsonify(trip)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "metadata": {},
   "outputs": [
    {
     "ename": "UnsupportedOperation",
     "evalue": "not writable",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mUnsupportedOperation\u001b[0m                      Traceback (most recent call last)",
      "\u001b[1;32m<ipython-input-24-1fa6c4e94fd5>\u001b[0m in \u001b[0;36m<module>\u001b[1;34m()\u001b[0m\n\u001b[0;32m      1\u001b[0m \u001b[1;32mif\u001b[0m \u001b[0m__name__\u001b[0m \u001b[1;33m==\u001b[0m \u001b[1;34m'__main__'\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m      2\u001b[0m     \u001b[0mapp\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mdebug\u001b[0m\u001b[1;33m=\u001b[0m\u001b[1;32mTrue\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m----> 3\u001b[1;33m     \u001b[0mapp\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mrun\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m",
      "\u001b[1;32m~\\Anaconda3\\lib\\site-packages\\flask\\app.py\u001b[0m in \u001b[0;36mrun\u001b[1;34m(self, host, port, debug, load_dotenv, **options)\u001b[0m\n\u001b[0;32m    936\u001b[0m         \u001b[0moptions\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0msetdefault\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m'threaded'\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;32mTrue\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    937\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 938\u001b[1;33m         \u001b[0mcli\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mshow_server_banner\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0menv\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mdebug\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mname\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;32mFalse\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m    939\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    940\u001b[0m         \u001b[1;32mfrom\u001b[0m \u001b[0mwerkzeug\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mserving\u001b[0m \u001b[1;32mimport\u001b[0m \u001b[0mrun_simple\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32m~\\Anaconda3\\lib\\site-packages\\flask\\cli.py\u001b[0m in \u001b[0;36mshow_server_banner\u001b[1;34m(env, debug, app_import_path, eager_loading)\u001b[0m\n\u001b[0;32m    627\u001b[0m             \u001b[0mmessage\u001b[0m \u001b[1;33m+=\u001b[0m \u001b[1;34m' (lazy loading)'\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    628\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 629\u001b[1;33m         \u001b[0mclick\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mecho\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mmessage\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m    630\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    631\u001b[0m     \u001b[0mclick\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mecho\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m' * Environment: {0}'\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mformat\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0menv\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32m~\\Anaconda3\\lib\\site-packages\\click\\utils.py\u001b[0m in \u001b[0;36mecho\u001b[1;34m(message, file, nl, err, color)\u001b[0m\n\u001b[0;32m    257\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    258\u001b[0m     \u001b[1;32mif\u001b[0m \u001b[0mmessage\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m--> 259\u001b[1;33m         \u001b[0mfile\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mwrite\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mmessage\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m    260\u001b[0m     \u001b[0mfile\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mflush\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m    261\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;31mUnsupportedOperation\u001b[0m: not writable"
     ]
    }
   ],
   "source": [
    "if __name__ == '__main__':\n",
    "    app.debug=True\n",
    "    app.run()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}




































# dependencies
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Database 
engine = create_engine(create_engine(f'sqlite:///{database_path}',
session = Session(engine)
Base = automap_base()
Base.prepare(engine, reflect=True)

# variables for bases
measurement = Base.classes.measurement
station = Base.classes.station

# make a flask app for everything to come
app = Flask(__name__)

# main page routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Precipitation and Temperature Information API.<br/>"
        f"Here are the available API calls:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start date<br/>"
        f"/api/v1.0/start date/end date<br/>"
    )

# precip API call
@app.route("/api/v1.0/precipitation")
def precipitation():
    last12 = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precip_query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= last12).all()
    precip = {date: prcp for date, prcp in precip_query}

    return jsonify(precip)

# station API call
@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(station.station, station.name).all()
    station = list(np.ravel(station_query))

    return jsonify(station)

# temperature API call
@app.route("/api/v1.0/tobs")
def temperature():
    last12 = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp = session.query(measurement.date, measurement.tobs).filter(measurement.date >= last12).all()
    tobs = list(np.ravel(temp))

    return jsonify(tobs)

# start date API call
@app.route("/api/v1.0/start")
def temp_start(start):
    start_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    temp = list(np.ravel(start_query))

    return jsonify(temp)

# date range API call
@app.route("/api/v1.0/start/end")
def temp_date_range(start, end):
    start_end_query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).all()
    temp =list(np.ravel(start_end_query))

    return jsonify(temp)

if __name__ == "__main__":
    app.run(debug=True)
