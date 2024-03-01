from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/rate', methods=['GET'])
def rate():
  url = "http://service-a:8888"
  # url = "http://34.49.136.69"
  r = requests.get(url)
  return r.text

# Handle all 404s
@app.errorhandler(404)
def error(e):
  return "nothing here"

if __name__ == "__main__":
  app.run(port=5000, host='0.0.0.0')