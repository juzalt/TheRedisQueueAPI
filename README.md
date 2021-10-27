# The Redis Queue API
###### [If you're looking for the original README checkout OLDREADME.md](OLDREADME.md)

----
The Redis Queue API allows users to send messages which will be stored in a queue. 
Later those messages can be counted and retrieved.

This README goes through the basics first, and further down below it details non-essential info & extra features directed at software engineers and those who are curious.

----

- [Getting Started](#getting-started)
  - [Pre-requisites](#pre-requisites)
  - [Setting up](#setting-up)
  - [Logging in](#logging-in)
- [Usage](#usage)
  - [Sending Messages](#sending-messages)
  - [Counting Messages](#counting-messages)
  - [Retrieving Messages](#retrieving-messages)
- [Through the looking glass // Details for nerds](#through-the-looking-glass)
  - [Extra Features](#extra-features)
    - [Automated Tests](#automated-tests)
    - [Logs](#logs)
    - [Monitoring](#monitoring)
    - [Healthcheck](#healthcheck)
    - [Slowlogs](#slowlogs)
  - [Digging deeper into the basics](#digging-deeper-into-the-basics)
    - [Login hash](#login-hash)
    - [Queue Pop Mechanism](#queue-pop-mechanism)
    - [Miscellaneous](#miscellaneous)

# Getting Started
## Pre-requisites

[Docker Engine](https://docs.docker.com/install/) --
[Docker Compose](https://docs.docker.com/compose/install/) --
[Bash](https://www.gnu.org/software/bash/) 


## Setting up
```
$ git clone git@github.com:irt-mercadolibre/challenge_redis_juzalt.git
$ cd challenge_redis_juzalt
$ docker-compose up
```
(Don't forget sudo on that last one if your system requires it.)

![Docker Compose Up gif](https://julianzaltron.now.sh/static/media/docker-compose-up.f270b20a.gif)

When the command line says...
> web_1    |  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)

...then we're ready to go. Leave that terminal the way it is and open up a new one located at the same directory.

## Logging in
```
$ ./login
```
Username:
> admin

Password:
> meliR0cks

(That's a capital R followed by a zero.)

![Login gif](https://julianzaltron.now.sh/static/media/login.89dd7ee5.gif)

# Usage
## Sending Messages
To send one or more messages first write them down in a file in which each line is a message.
```
$ vi helloworld.txt
```
> Hello world! This is my first message.  
Hi again, second message.  
Ok, third's a charm.  

Close the file and run the following:

```
$ ./push
$ helloworld.txt
```
![Push gif](https://julianzaltron.now.sh/static/media/push.1e944c41.gif)

Congrats on sending your first message(s)!

## Counting messages
To count the amount of messages stored in the queue, just type
```
$ ./count
```

  <img src="https://julianzaltron.now.sh/static/media/count.20bff265.png" alt="Image showing the count method in use." />

The value of "Count" is the amount of messages in the queue (In this case it's three)

## Retrieving messages
###### [The queue data type follows the FIFO method, so the first message sent will be the first retrieved. If you were looking to retrieve the most recent message, try a stack.](https://en.wikipedia.org/wiki/FIFO_(computing_and_electronics))

To retrieve the messages in the queue, just type
```
$ ./pop
```
You will be asked how many do you wish to receive. 

![Pop gif](https://julianzaltron.now.sh/static/media/pop.66c5f046.gif)

Any successfully retrieved messages will be logged at pop-log.txt in the program's root directory. (They are appended so don't worry about overwriting your pre-pop'd messages.)

You've completed the basics. Congrats! 
From now on we will talk about more advanced topics, or we'll be looking at the same ones at a lower level. 

# Through the looking glass
## Extra Features
### Automated Tests

Tests can be run by using Postman/Newman. There's no need to install anything, just run:
```
$ ./run-tests
```
![Tests gif](https://julianzaltron.now.sh/static/media/tests.99a77eb8.gif)

You will be asked for system root privileges, and don't forget authenticating yourself to the API before running them. 
In case you wanted to redefine, add or remove tests, a local version of them can be imported to Postman. You can find them at /tests/collections/Redis_Challenge.postman_collection.json and to run them use the following command:

```
$ sudo docker run --network host -t postman/newman:alpine run <COLLECTION-FILE> -r cli,json --reporter-json-export tests-output.json
```

As of February 2020, there's a bug when running this version of newman from a docker instance in which the reporters don't work well with json, but once it is fixed, the test results will be stored in tests-output.json and since we're pulling the image directly from Docker, there's no need to make any changes to our program.

### Logs
It's possible to log every command being processed by the API. 
First, activate the logs:
```
$ ./activate-logs
```

After that, run a command such as sending a message to the queue and it will appear in "logfile.txt" at the root directory. 
Logs have the following structure:

> < Timestamp > < Command Name > -- Response: < Result > 

In which "Result" is purposefully summarized on events in which logging the whole output would cause an unreadable logfile. 

Please be aware that the logs should only be used for debugging purposes and never in prod, since it causes the program to work at O(n) where n is the amount of logs being written.

To deactivate the logs, simply run:
```
./deactivate-logs
```

### Monitoring
Redis provides us with a healthy amount of data for monitoring our database.
To check it out run:
```
$ ./monitor
``` 

And choose the information you need:

* commandstats:

  It provides statistics based on the command type, including the number of calls, the total CPU time consumed by these commands, and the average CPU consumed per command execution.
  For each command type, the following line is added:

> cmdstat_XXX: calls=XXX,usec=XXX,usec_per_call=XXX

* memory: 

  It provides us with a lot of info regarding memory usage by Redis. 

* stats: 

  Provides us with general info such as total connections accepted by the server or the total number of commands processed by the server, among other things. 

[To check out the meaning of each section in regards to memory and stats, please click here.](https://redis.io/commands/info)

### Healthcheck
To check if our database is healthy and working as expected just type:
```
$ ./healthcheck
```
A "Health" key will be returned; if everything's OK then its value will be "Amazing". If it's not, it will be "Bad".

On the background this runs Redis's PING command. [You may wonder as I did if this is enough to perform a healthcheck. It surprisingly is, as it measures both latency and overall health. So why complicate things if simple is better, quicker and lighter?](https://www.inovex.de/blog/redis-cli/)

[Still not convinced? Then checkout this redis-py method that does exactly this.](https://redis-py.readthedocs.io/en/latest/_modules/redis/connection.html#Connection.check_health)

### Slowlogs
Redis offers us the possibility of logging those commands whose execution time exceeds a specified threshold. The default value is 10000 **micro**seconds.

To tell Redis to start logging these commands, simply run:
```
$ ./activate-slowlogs
```
To access this command, run
```
$ ./slowlogs
```

You will be presented with the following options

* get:
  This allows you to retrieve logged slow commands.
  You will be asked how many logs you want to retrieve, if you want them all, simply press enter again.

* length:
  This tells you how many slow commands have been logged.

* reset:
  This flushes all the slow logs. Useful for whenever you want a clean start to test the database on a new context.

![Slowlog gif](https://julianzaltron.now.sh/static/media/slowlog.f1674155.gif)

To deactivate the logs, run:
```
$ ./deactivate-slowlogs
```

## Digging deeper into the basics
### Login hash
Our authentication mechanism is a redesign of [Alessandro Molina's](https://www.vitoshacademy.com/hashing-passwords-in-python/) in order to fit our purposes and to keep it aligned with separation of concerns.

With this implementation, there's no harm in keeping the hash publicly available. This is because it was generated with lots of entropy by adding a salt to the first time the original password was hashed, and later concatenating that same salt to the resulting hash.
This protects us from rainbow tables since the valid hash falling in the hands of an attacker would be purposeless since it will not coincide with any stored hash of any chain.
Of course this also protects us from brute-force and dictionary attacks.

But how do we then use this hash to authenticate anyone?
Well, since we knew that the generated salt would always consist of 64chars, (This is because it's the result of an hexdigest of a sha256) we can take advantage of that by stripping the valid hash into two pieces: one corresponding to the salt and another to the hash of the original password concatenated with the same salt. (As in (salt + hash(plaintext + salt)))
Then the provided password (the one being authenticated) is hashed along with the same salt and checked against the valid hash (the one of the valid password).

If we had only used a general-purpose hash algorithm it would have been very easy to brute force. 
Another solution would have been using a tested and secure library that's already available in Flask: [werkzeug](https://techmonger.github.io/4/secure-passwords-werkzeug/)
But in this particular occasion I decided to re-invent the wheel to show that it could be done with native methods.
In a real-life scenario where time is of the essence, I would reccomend not following this path.

The program is still vulnerable to a MITM attack between the user and the API, and of course human error, but there's nothing I could code to prevent that.

### Queue Pop Mechanism
The Redis Queue API stores all messages in a List data type stored in Redis.
You may be wondering why would a list be used if it sounds like common sense to store messages in a string data type.

It was chosen this way because a list presents us with the opportunity of always running at O(1) when popping messages from the extremes (And since this is a queue, it will always work at that speed.) while keeping an orderly database.

If strings were to be used, then we would have to choose between storing each message in a new key, or appending each message to the only key used.

If the first path were chosen, then the database could grow enough to hold an enormous amount of strings, and Redis would not be the best choice for this since it runs in memory, but even if we were talking about another database system, I would prefer it if it weren't overflowing with key's everywhere.

If the second path were chosen, then the performance of the database would have suffered a downgrade to O(n) where n is the length of the returned string. [See GETRANGE](https://redis.io/commands/getrange)

<p align="center">
  <img src="https://camo.githubusercontent.com/874181d7b840a494fe94a11cc13c1fad5d372217/68747470733a2f2f6170656c6261756d2e66696c65732e776f726470726573732e636f6d2f323031312f31302f796161636f766170656c6261756d6269676f706c6f742e6a7067" alt="Cartesian graph showing speed comparison. Much superior. So fast. Wow. Many speed. -Doge.">
</p>

What's the only downside of using lists then? Well, you're limited to 2^(32) - 1 elements for each list. That's 4294967295 elements. If you got every chinese citizen to send a message, three times, one list would still be more than enough.

### Miscellaneous

* If you've been following this Readme and testing everything in your machine you probably already know by now, but if you haven't, then you might want to check the bash scripts that allow the program to be simple enough to run by just running the script that you want. I've implemented failsafe mechanisms as to not let the user misuse them. For example, in the login script the user is limited up to three tries before they are kicked out, this makes it harder for an attacker to take advantage of the script when performing a dictionary attack.

* Despite each script having its failsafe mechanism, I've also implemented this on the API.

* I've done the research and the program should work on a Mac as it does in Linux without the need of changing anything, but since I do not own a Mac, nor could I virtualize one there's no way I could test this.

* Upon establishing a connection to the API, the last session is always deauthenticated and the logs are deactivated. This allows us to not suffer any performance drawbacks if a user forgets the logs activated.

## Author
[Julian Zaltron](https://julianzaltron.now.sh)