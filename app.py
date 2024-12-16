from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from gtts import gTTS
import os
from translations import translate_genz_word, suggest_closest_word

app = Flask(__name__, template_folder='SYSTEM')  # Set template folder to 'SYSTEM'
app.secret_key = 'your_secret_key'  # Required for session management

# Ensure 'static' directory exists
if not os.path.exists('static'):
    os.makedirs('static')

# Path to save the audio file
AUDIO_FILE_PATH = 'static/translation.mp3'

@app.route('/')
def index():
    # Check if the user is logged in (via session)
    if session.get('logged_in'):
        return render_template('index.html')  # Show index.html from the 'SYSTEM' folder if logged in
    else:
        return render_template('loginandsignup.html')  # Show loginandsignup.html if not logged in

@app.route('/login', methods=['POST'])
def login():
    try:
        # Retrieve login credentials from the form
        email = request.form.get('email')
        password = request.form.get('password')

        # Dummy check for login credentials (use real validation in production)
        if email == "test@example.com" and password == "password123":
            session['logged_in'] = True  # Set the session flag for logged-in user
            return redirect(url_for('index'))

        # If login fails, show error
        return render_template('loginandsignup.html', error="Invalid credentials")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        # Retrieve signup information
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Simple check if passwords match
        if password != confirm_password:
            return render_template('loginandsignup.html', error="Passwords do not match")

        # Add the user to the database or perform signup logic here
        # For now, we are just redirecting to index page as if the user was successfully signed up
        session['logged_in'] = True  # Automatically log in after signup
        return redirect(url_for('index'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logout')
def logout():
    # Log the user out by clearing the session
    session.pop('logged_in', None)
    return redirect(url_for('index'))  # Redirect to login page

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        genz_word = data.get('word', '').strip()
        language = data.get('language', 'en')

        if not genz_word:
            return jsonify({"translation": "Input is empty", "audio_url": "", "suggestion": ""}), 400

        # Call the translation function from translations.py
        translation = translate_genz_word(genz_word, language)
        suggestion = ""

        # If translation is not found, get a suggestion
        if translation == "Translation not found.":
            suggestion = suggest_closest_word(genz_word)

        # If translation is found, generate speech using gTTS
        audio_url = ""
        if translation != "Translation not found.":
            # Language setting for gTTS (default to 'en' if not 'tl')
            tts_lang = 'tl' if language == 'tl' else 'en'
            tts = gTTS(text=translation, lang=tts_lang)

            # Save the audio file in the 'static' directory
            tts.save(AUDIO_FILE_PATH)
            audio_url = f"{AUDIO_FILE_PATH}?t={os.path.getmtime(AUDIO_FILE_PATH)}"  # Prevent caching

        return jsonify({
            "translation": translation,
            "audio_url": audio_url,
            "suggestion": suggestion
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
