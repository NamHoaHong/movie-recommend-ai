from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

chat_history = []

def create_model():
    """Create the model for the movie generator."""
    create_model_cmd = ["ollama", "create", "generator", "-f", "./Modelfile"]
    try:
        subprocess.run(create_model_cmd, check=True)  # Remove stdout and stderr
    except subprocess.CalledProcessError as e:
        print(f"Error creating the model: {e}")  # Print error output


def run_ollama_model(user_input):
    """Run the generator model and maintain chat history."""
    global chat_history
    run_model_cmd = ["ollama", "run", "generator"]

    chat_history.append(f"User: {user_input}")
    prompt = "\n".join(chat_history)

    try:
        # Running the command without capturing stdout/stderr
        process = subprocess.run(run_model_cmd, input=prompt, text=True, capture_output=True)

        if process.returncode != 0:
            print(f"Error running the model: {process.stderr.strip()}")
            return None

        model_response = process.stdout.strip()
        print("Model Response:", model_response)
        chat_history.append(f"Generator: {model_response}")
        return model_response.strip()

    except subprocess.CalledProcessError as e:
        print(f"Error running the model: {e}")
        return None


@app.route('/', methods=['GET', 'POST'])
def home():
    create_model()
    if request.method == 'POST':
        user_input = request.form['user_input']
        response = run_ollama_model(user_input)

        # Return JSON response for AJAX
        return jsonify({"response": response, "chat_history": chat_history})

    return render_template('index.html', chat_history=chat_history)

if __name__ == '__main__':
    create_model()  # Create model when starting the app
    app.run(debug=True)
