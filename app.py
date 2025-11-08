from flask import Flask, render_template, request
from gradio_client import Client

app = Flask(__name__)
client = Client("yeager07/multi-label-cs-article-classification")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/classify", methods=["GET", "POST"])
def index():
    labels = []
    input_text = ""
    
    if request.method == "POST":
        input_text = request.form.get("abstract", "").strip()
        
        if not input_text:
            labels = [{'label': 'Error: Please enter a valid abstract.', 'confidence': 0.0}]
        else:
            try:
                response = client.predict(
                    abstract=input_text,
                    api_name="/classify_subjects"
                )
                
                print("Response:", response)
                
                # Extract confidences from response
                confidences = response.get("confidences", [])
                
                # Take top 5 labels with confidence scores
                labels = [
                    {
                        'label': item['label'],
                        'confidence': item.get('confidence', 0.0) * 100
                    }
                    for item in confidences[:5]
                ]
                
            except Exception as e:
                print("Error:", e)
                labels = [{'label': 'Error: Unable to classify. Please try again.', 'confidence': 0.0}]
        
        return render_template("result.html", input_text=input_text, labels=labels)
    
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)