from flask import Flask, render_template, request
from gradio_client import Client
import concurrent.futures
import hashlib

app = Flask(__name__)
client = Client("yeager07/multi-label-cs-article-classification")

# Simple in-memory cache for recent predictions
cache = {}
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

def classify_abstract(text):
    """Safely call Gradio API."""
    try:
        response = client.predict(
            abstract=text,
            api_name="/classify_subjects"
        )
        return response
    except Exception as e:
        print("Gradio API Error:", e)
        return {"confidences": [], "label": "Error"}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/classify", methods=["GET", "POST"])
def classify():
    labels = []
    input_text = ""

    if request.method == "POST":
        input_text = request.form.get("abstract", "").strip()

        if not input_text:
            labels = [{'label': 'Error: Please enter a valid abstract.', 'confidence': 0.0}]
        else:
            # Cache key based on text hash
            text_hash = hashlib.md5(input_text.encode()).hexdigest()

            if text_hash in cache:
                print("Cache hit")
                response = cache[text_hash]
            else:
                print("Cache miss — calling model")
                future = executor.submit(classify_abstract, input_text)
                try:
                    response = future.result(timeout=10)
                    cache[text_hash] = response
                except concurrent.futures.TimeoutError:
                    labels = [{'label': 'Error: Timeout. Please try again later.', 'confidence': 0.0}]
                    return render_template("result.html", input_text=input_text, labels=labels)

            confidences = response.get("confidences", [])
            labels = []
            for item in confidences[:5]:
                conf = item.get("confidence", 0.0)
                # Convert to percentage only once
                if 0 <= conf <= 1:
                    conf *= 100
                labels.append({
                    "label": item.get("label", "Unknown"),
                    "confidence": round(conf, 2)
                })

        return render_template("result.html", input_text=input_text, labels=labels)

    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
