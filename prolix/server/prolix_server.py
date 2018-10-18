from flask import Flask

app=Flask("prolix_server")


@app.route("/")
def hello():
    return "ProlixServer says hello warmly"

