Alex Or PJ?
===========

This is the application that hosts the Alex or PJ functionality on the web. This
README documents how to get things up and running.

# Development
In order to get the application to run, there are a couple of steps.

## Virtual env
As per usual, you need to create a virtual environment and install dependencies.  I'm
not going to cover that here.

## Env Vars
The app needs a number of env vars to be passed to it in order to function. It's set up
to grab these from a `.env` file in the root directory.  Create this file and add entries
to it for

```
SECRET_KEY=<key>
TWITTER_CONSUMER_TOKEN=<token> #from the twitter app
TWITTER_CONSUMER_SECRET=<secret> #from the twitter app
```

## Running the app
To run the application, execute the following command in the root directory.

```
env FLASK_APP=src/app.py flask run
```

## Testing
Run the test suite with
```
pytest src
```
