import gradio as gr
import onnxruntime as rt
from transformers import AutoTokenizer
import torch, json

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")

# Load encoded subject dictionary
with open("subject_types_encoded.json", "r") as fp:
    encode_subject_types = json.load(fp)

subjects = list(encode_subject_types.keys())

# Load ONNX model
inf_session = rt.InferenceSession("Scientific Articles-classifier-quantized.onnx")
input_name = inf_session.get_inputs()[0].name
output_name = inf_session.get_outputs()[0].name

# Prediction function
def classify_subjects(abstract: str):
    inputs = tokenizer(
        abstract,
        padding="max_length",
        truncation=True,
        max_length=512,
        return_tensors="np"
    )
    logits = inf_session.run([output_name], {input_name: inputs["input_ids"]})[0]
    logits = torch.FloatTensor(logits)
    probs = torch.sigmoid(logits)[0]
    return dict(zip(subjects, map(float, probs)))

# Gradio Interface
label = gr.Label(num_top_classes=10)
iface = gr.Interface(
    fn=classify_subjects,
    inputs=gr.Textbox(lines=5, placeholder="Enter research paper abstract here..."),
    outputs=label,
    title="Multi-Label Classification of Computer Science Research Articles",
    description="Predict multiple subject categories from computer science research paper abstracts."
)

iface.launch()
