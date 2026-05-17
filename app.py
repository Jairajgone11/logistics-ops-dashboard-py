from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Logistics Ops Dashboard</h1>
    <p>Deployment successful 🚀</p>
    <p>GitHub repo connected to Vercel.</p>
    """