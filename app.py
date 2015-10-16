"""
AUTHOR: Ian Garrett
PROJECT: proj3-ajax
COURSE: CIS399
"""

import flask
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify # For AJAX transactions

import json
import logging
import math
import datetime

# Date handling 
import arrow # Replacement for datetime, based on moment.js
import datetime # But we still need time
from dateutil import tz  # For interpreting local times

# Our own module
# import acp_limits


###
# Globals
###
app = flask.Flask(__name__)
import CONFIG

import uuid
app.secret_key = str(uuid.uuid4())
app.debug=CONFIG.DEBUG
app.logger.setLevel(logging.DEBUG)


###
# Pages
###

@app.route("/")
@app.route("/index")
@app.route("/calc")
def index():
  app.logger.debug("Main page entry")
  return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    flask.session['linkback'] =  flask.url_for("index")
    return flask.render_template('page_not_found.html'), 404


###############
#
# AJAX request handlers 
#   These return JSON, rather than rendering pages. 
#
###############
@app.route("/_calc_times")


#QUESTIONS:
#-Do we need to make default text under mile entry disappear when user so much as
# clicks the box? if so, any tips?
#-How much is "somewhat larger than 200km"? What is the range we are going for?
#-Do we need things to auto update when we change the date?
#-Do we need cap on shortest possible?
#-How should I check if date is valid? seems like I'll have to do it in python then send back a function


def calc_times():
  """
  Calculates open/close times from miles, using rules 
  described at http://www.rusa.org/octime_alg.html.
  Expects one URL-encoded argument, the number of miles. 
  """
  # Grab things you need from javascript using request.args.get('miles', 0, type=int), 
  app.logger.debug("Got a JSON request");
  kmiles = request.args.get('miles', 0, type=int)
  raceDist = request.args.get('RaceDistance', 0, type=int)
  date = request.args.get('date', 0, type=str)
  time = request.args.get('time', 0, type=str)
  inputUnit = request.args.get('inputUnit', 0, type=str)

  #convert units if necessary
  if inputUnit == "miles":
    kmiles *= 1.609344
  
  #set default time to 00:00
  if len(time)==0:
    time = '00:00'

  warningList = ();

  #check if date given is valid, if not return appropriate error message to user
  try:
    testDate = date.split("/")
    try:
      newDate = datetime.datetime(int(testDate[0]),int(testDate[1]),int(testDate[2]))
    except IndexError:
      return jsonify(dateError="yes", badDate=date)
  except ValueError:
    return jsonify(dateError="yes", badDate=date)

  #check if time given is valid, if not return appropriate error message to user
  try:
    currentStart = arrow.get(str(date)+' '+time,'YYYY/MM/DD HH:mm')
  except ValueError:
    return jsonify(timeError="yes", badTime=time)

  #process special cases in which kmiles is greater than or equal to race distance
  raceDistList = (200,300,400,600,1000)

  startAdditive = 0
  endAdditive = 0
  for dist in raceDistList:
    if raceDist == dist:
      if kmiles >= raceDist:
        kmiles = raceDist
        #Add extra minutes
        if dist==200 or dist==1000:
          endAdditive = 10
        elif dist==400:
          endAdditive = 20

  #Create arrays to contain min and max speeds
  minSpeeds = [15,11.428,13.333]
  maxSpeeds = [34,32,30,28,26]


  #Select min and max speeds based on miles (should we display these for the user?
  if kmiles in range(0,200):
    minSpeed = minSpeeds[0]
    maxSpeed = maxSpeeds[0]

  elif kmiles in range(200,400):
    minSpeed = minSpeeds[0]
    maxSpeed = maxSpeeds[1]

  elif kmiles in range(400,600):
    minSpeed = minSpeeds[0]
    maxSpeed = maxSpeeds[2]

  elif kmiles in range(600,1000):
    minSpeed = minSpeeds[1]
    maxSpeed = maxSpeeds[3]

  elif kmiles in range(1000,1300):
    minSpeed = minSpeeds[2]
    maxSpeed = maxSpeeds[4]

  #find way to split up distance and assign speed to each one
  
  #find prebuilt times to add when distances go past rements

  #end times
  endOneTime = 600/15
  endTwoTime = 400/11.482
  endThreeTime = 300/13.333

  #start times
  startOneTime = 200/34
  startTwoTime = 200/32
  startThreeTime = 200/30
  startFourTime = 400/28
  startFiveTime = 300/26

  

  if kmiles < 200:
    endTime = kmiles/minSpeed
    startTime = kmiles/maxSpeed

  elif kmiles in range(200,400):
    endTime = kmiles/minSpeed
    startTime = startOneTime+((kmiles-200)/maxSpeed)

  elif kmiles in range(400,600):
    endTime = kmiles/minSpeed
    startTime = startOneTime+startTwoTime+((kmiles-400)/maxSpeed)

  elif kmiles in range(600,1000):
    endTime = endOneTime+((kmiles-600)/minSpeed)
    startTime = startOneTime+startTwoTime+startThreeTime+((kmiles-600)/maxSpeed)

  elif kmiles in range(1000,1300):
    endTime = endOneTime+endTwoTime+((kmiles-1000)/minSpeed)
    startTime = startOneTime+startTwoTime+startThreeTime+startFourTime+((kmiles-1000)/maxSpeed)

  elif kmiles >= 1300:
    endTime = endOneTime+endTwoTime+endThreeTime+((kmiles-1300)/minSpeed)
    startTime = startOneTime+startTwoTime+startThreeTime+startFourTime+startFiveTime+((kmiles-600)/maxSpeed)


  #process times into hh:mm
  endTimepair = math.modf(endTime)
  startTimepair = math.modf(startTime)

  endaddhours = int(endTimepair[1])
  endaddminutes = round(endTimepair[0]*60)

  startaddhours = int(startTimepair[1])
  startaddminutes = round(startTimepair[0]*60)

  #determine what to add to the current date as far as days, hours, and minutes go
  if (endaddhours-24) < 0:
    endaddDays = 0
  else:
    endaddDays = endaddhours//24
    endaddhours = endaddhours%24

  if (startaddhours-24) < 0:
    startaddDays = 0
  else:
    startaddDays = startaddhours//24
    startaddhours = startaddhours%24

  #modify dates
  endTime = (currentStart.replace(days=endaddDays ,hours=endaddhours, minutes=endaddminutes+endAdditive)).format("YYYY/MM/DD HH:mm")
  startTime = (currentStart.replace(days=startaddDays ,hours=startaddhours, minutes=startaddminutes)).format("YYYY/MM/DD HH:mm")

  return jsonify(openTime=startTime,closeTime=endTime)


if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT)

    
