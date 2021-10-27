## # LIBRARIES # ##
import redis
from flask import Flask, request, jsonify, abort
import hashlib
import binascii
import sys
import os
import time
import logging

## # GLOBAL VARIABLES # ##
r = redis.Redis(host='redis', port=6379)
app = Flask(__name__)
encoding = 'utf-8'
VALID_USERNAME = 'admin'
VALID_PASSW_HASH = "0c7e7a307606695350137f71319614899bf793e726b263cdec47ca91f93466a1023d92d3121f04e203873723077bc9a97c36da169989687392b72ef426574ae163d1d02a32a44534b7a2ef466a0cf4925ae4c7a25f49d877552b038ee43e6f27"


## # MAIN FUNCTIONS # ##
class InitializeRedis():
    def __init__(self):
        r.set('auth', 'false')
        r.set('logsStatus', 'deactivated')
        r.set('slowlogStatus', 'deactivated')
InitializeRedis()

def checkLogin():
    if str(r.get('auth')) != 'b\'true\'':
        abort(401)


def hashPassword(password, salt):
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                password.encode('utf-8'), 
                                salt.encode('ascii'),
                                100000)
    pwdhash = binascii.hexlify(pwdhash)
    return pwdhash 

def verifyPassword(storedPassword, providedPassword):
    salt, storedPassword = stripPassword(storedPassword)
    pwdhash = hashPassword(providedPassword, salt).decode('ascii')
    return pwdhash == storedPassword

def stripPassword(storedPassword):
    salt = storedPassword[:64]
    storedPassword = storedPassword[64:]
    return salt, storedPassword


@app.route('/api/queue/auth', methods=['POST'])
def auth():
    if str(r.get('auth')) == 'b\'true\'':
        return "You're already logged in.\n"
    username = request.json.get('username')
    providedPassword = request.json.get('password')
    if bool(username) is False or bool(providedPassword) is False:
        return "\nPlease fill in both fields.\n", 400
    if verifyPassword(VALID_PASSW_HASH, providedPassword) is False or username != VALID_USERNAME:
        return "\nPlease check your username and password, and try again.\n", 401
    r.set('auth', 'true')
    logRecent('Auth', 'logged in.')
    return "Access Granted.\n", 200


@app.route('/api/queue/push', methods=['POST'])
def push():
    checkLogin()
    if not request.json or not 'msg' in request.json:
        abort(400)
    message = request.json['msg']
    r.rpush('chat', message)
    logRecent('Push', str(message))
    return jsonify({'status': 'ok'}), 201

@app.route('/api/queue/pop', methods=['POST'])
def pop():
    checkLogin()
    emptyListMessage = "The chat is empty! Try writing something into it by sending a POST method to /api/queue/push with the \"msg\" key :) \n"
    msgBytes = r.lpop('chat')
    if msgBytes is None:
        return emptyListMessage

    msgStr = msgBytes.decode(encoding)
    logRecent('Pop', str(msgStr))
    appendToFile(msgStr, "pop-log.txt")
    return jsonify({'status': 'ok', 'message': msgStr}), 200

@app.route('/api/queue/count', methods=['GET'])
def count():    
    checkLogin()
    count = r.llen('chat')
    logRecent('Count', str(count))
    return jsonify({'status': 'ok', 'count': count}), 200


## # MONITORING # ##
@app.route('/api/queue/healthcheck', methods=['GET'])
def healthCheck():    
    checkLogin()
    healthy = r.ping()
    logRecent('Healthcheck', str(healthy))
    if healthy is True:
        return jsonify({'status': 'ok', 'Health': 'Amazing'}), 200
    return jsonify({'status': 'ok', 'Health': 'Bad'}), 200

@app.route('/api/queue/metrics', methods=['PUT'])
def info():    
    checkLogin()
    command = request.json.get('command')
    logRecent('Metrics', command)
    metrics = None # Used in the methods below. Clears var upon mult calls. If this ever stops being a switch, delete this line.
    def commandstats():
        metrics = r.info('commandstats')
        return metrics
    def memory():
        metrics = r.info('memory')
        return metrics
    def stats():
        metrics = r.info('stats')
        return metrics 
    def selectCommand(command):
        switcher = {
            'commandstats': commandstats,
            'memory': memory,
            'stats': stats
        }
        func = switcher.get(command, "Valid commands are: commandstats, memory, stats\n")
        if func == "Valid commands are: commandstats, memory, stats\n":
            return func
        return func()
    result = selectCommand(command)
    statuscode = 400 if result == "Valid commands are: commandstats, memory, stats\n" else 200
    return result, statuscode


## # LOGGING # ##
def appendToFile(data, fileName):
   file = open(fileName, "a")
   dataStr = str(data)
   appendLog = dataStr[3:-2] + '\n'
   appendPop = dataStr + '\n'
   file.write(appendLog) if fileName != "pop-log.txt" else file.write(appendPop)
   file.close()

def logRecent(location, info):
    if str(r.get('logsStatus')) == "b'activated'":
        message = time.asctime() + ' ' + location + ' -- Response: ' + info
        r.lpush('logs', message)
        message = None
        logs = r.lrange('logs', 0, -1)
        appendToFile(logs, "logfile.txt")
        r.delete('logs')
        logs = None

@app.route('/api/queue/control_logs', methods=['POST'])
def changeLogsStatus():
    checkLogin()
    if not request.json or not 'status' in request.json:
        abort(400)
    status = request.json.get('status')
    if str(status) != 'activated' and str(status) != 'deactivated':
        return "You have to indicate if you would like the logs \'activated\' or \'deactivated\'", 400
    r.set('logsStatus', status)
    return "The logs have been {0} \n".format(status), 200

@app.route('/api/queue/slowlog', methods=['PUT'])
def slowlog():    
    checkLogin()
    command = request.json.get('command')
    logRecent('Slowlog', command)
    amountOfMessages = request.json.get('amount')
    def get(amountOfMessages =0):
        messages = None
        messages = r.slowlog_get(amountOfMessages)
        return messages
    def length():
        length = None
        length = r.slowlog_len()
        return length
    def reset():
        r.slowlog_reset()
        return "Slowlog was flushed." 
    def selectCommand(command, amountOfMessages =0):
        switcher = {
            'get': get,
            'length': length,
            'reset': reset
        }
        func = switcher.get(command, "Valid commands are: get, length, reset\n")
        if func == "Valid commands are: get, length, reset\n":
            return func
        return func()
    result = selectCommand(command, amountOfMessages)
    result = 'empty' if str(result) == '[]' else result
    statuscode = 400 if result == "Valid commands are: get, length, reset\n" else 200
    return jsonify({'status': 'ok', 'result': result}), statuscode

@app.route('/api/queue/set_slowlog', methods=['PUT'])
def setSlowlog():
    checkLogin()
    change = request.json.get('change')
    logRecent('Set Slowlog', change)
    if change == 'activate':
        r.set('slowlogStatus', 'activated')
        return jsonify({'status': 'ok', 'result': 'slowlog activated'}), 200
    r.set('slowlogStatus', 'deactivated')
    return jsonify({'status': 'ok', 'result': 'slowlog deactivated'}), 200

if __name__ == '__main__':
    app.run(debug=True)
