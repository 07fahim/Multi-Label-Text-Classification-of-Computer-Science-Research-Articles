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

    # Return dictionary of all subjects with probabilities
    return dict(zip(subjects, map(float, probs)))

# Gradio Interface
iface = gr.Interface(
    fn=classify_subjects,
    inputs=gr.Textbox(
        lines=6,
        placeholder="Enter research paper abstract here...",
        label="Research Abstract"
    ),
    outputs=gr.Label(num_top_classes=5),
    title="Computer Science Research Article Subject Classifier",
    description=(
        "This demo uses a SciBERT-based ONNX model to predict the top subject "
        "categories from computer science research paper abstracts."
    ),
    theme="gradio/soft",
    allow_flagging="never"
)

# Launch app
iface.launch(inline=False)

