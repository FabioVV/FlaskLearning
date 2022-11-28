from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

app = Flask(__name__)
app.secret_key = "Supersecretkey"







if __name__ == "__main__":
    app.run("0.0.0.0", port=5002, debug=True)