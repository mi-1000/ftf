import spacy
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from mysql.connector import Error, connect
from unidecode import unidecode

from ipa.ipa_ancient import phoneticize
from translation.translate import translate

load_dotenv()

app = Flask(__name__)

nlp = spacy.load("fr_core_news_md") # Load the French model # TODO Uncomment when debugging is done

@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        data = request.get_json(cache=True)
        word = data.get("word")
        if word:
            date = get_date((unidecode(word)))
        else:
            date = None
        return jsonify({"date": date})
    else:
        return render_template("index.html")


@app.route("/ipa", methods=["POST"])
def ipa():
    data = request.get_json(cache=True)
    text = data.get("text")
    lang = data.get("lang")
    period = data.get("period")
    try:
        ipa = phoneticize(text, lang, period)
        return jsonify({"ipa": ipa})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/pos", methods=["POST"])
def pos_tagging():
    # Get text from request
    data = request.get_json(cache=True)
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Missing key 'test' in request body."})

    # Handle text with loaded model
    doc = nlp(text)
    result = [{"text": token.text, "pos": token.pos_} for token in doc]

    return jsonify(result)

@app.route("/translation", methods=["POST"])
async def translate_text():
    data = request.get_json(cache=True)
    text = data.get("text")
    source_lang = data.get("source")
    target_lang = data.get("target")
    try:
        translation = await translate(source_lang, target_lang, text)
        return jsonify({"translation": translation})
    except Exception as e:
        return jsonify({"error": str(e)})

def get_date(
    word: str,
    db_config: dict = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    },
):
    try: # TODO Implement connection pool
        connection = connect(**db_config)

        if not connection.is_connected():
            raise Exception("Connection failed.")
        print("Successfully connected.")

        cursor = connection.cursor(buffered=True)

        query = "SELECT `date` FROM `etymology` WHERE `word` = %s"
        cursor.execute(query, (word,))
        result = cursor.fetchone()
        if result[0]: # Extract date from result set
            return result[0]
        return None

    except Error as e:
        print(f"SQL Error: {e}")
        return None
    except Exception as e:
        print(f"Error while retrieving date: {e}")
        return None
    finally:
        # Close resources
        if "cursor" in locals() and cursor:
            cursor.close()
        if "connection" in locals() and connection.is_connected():
            connection.close()
            print("Connection closed.")


if __name__ == "__main__":
    app.run(debug=True)
