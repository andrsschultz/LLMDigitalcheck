import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

# Load environment variables from .env file
load_dotenv()

# Retrieve the OPENAI_API_KEY
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

#Initialize OpenAI API
openai = OpenAI(
    api_key=openai_api_key,  # Use environment variable for API key
    base_url="https://api.deepinfra.com/v1/openai",  # DeepInfra endpoint
)


# Define Digital Principles
principles = {
    "Digitale Kommunikation": [
        "technologieoffen",
        "Medienbrüche sind vermieden",
        "Analoge Schriftformerfordernisse sind vermieden",
        "Barrierefreiheit ist ermöglicht"
    ],
    "Wiederverwendung von Daten & Standards": [
        "Daten-Austauschverfahren sind geschaffen",
        "bestehende Standards wurden berücksichtigt",
        "Once-Only Gedanke wurde berücksichtigt"
    ],
    "Datenschutz & Informationssicherheit": [
        "Datenschutz-Expertise wurde konsultiert",
        "Datensparsamkeit ist berücksichtigt",
        "Informationssicherheit ist gewährleistet"
    ],
    "Klare Regelungen für eine digitale Ausführung": [
        "Verständlichkeit wurde getestet",
        "Chronologische Schritte sind klar",
        "Eindeutige Kriterien und Systematik",
        "Rechtsbegriffe sind harmonisiert"
    ],
    "Automatisierung": [
        "IT-Expertise wurde einbezogen",
        "Automatisierte Verfahren sind möglich",
        "Entscheidungsstrukturen sind eindeutig"
    ]
}

# Function to analyze a law text against principles using OpenAI
def analyze_text_with_llm(law_text, principles):

    all_checks = []
    for principle_group, checks in principles.items():
        all_checks.append(f"**{principle_group}:**")
        all_checks.extend([f"- {check}" for check in checks])
    checks_list = "\n".join(all_checks)

    prompt = (
    f"""
    Das folgende Dokument ist ein Gesetz: {law_text}\n\n
    "Der Digitalcheck unterstützt bei der Erarbeitung von digitaltauglichen Regelungsvorhaben.
    Beurteile, ob das Gesetz die Prinzipien unten erfüllt. Gib die Antwort zwingend in der folgenden JSON-Datenstruktur zurück:

    {{
      "Digitale Kommunikation": [
        {{
          "Prinzip": "technologieoffen",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Verbesserungsvorschlag": "string"
        }},
        ...
      ],
      "Wiederverwendung von Daten & Standards": [
        {{
          "Prinzip": "Daten-Austauschverfahren sind geschaffen",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Verbesserungsvorschlag": "string"
        }},
        ...
      ],
      ...
    }}

    Für jedes Prinzip:
    - `"Erfüllt"`: Gebe `true` zurück, wenn das Prinzip erfüllt ist, `false`, wenn es nicht erfüllt ist, oder `null`, wenn keine Aussage möglich ist.
    - `"Begründung"`: Erkläre prägnant, warum das Prinzip erfüllt oder nicht erfüllt ist. Zitiere die entsprechende Passage im Gesetz mit Absatz/Satz/Nummer usw.
    - `"Verbesserungsvorschlag"`: Mach einen kurzen Verbesserungsvorschlag. Wenn das Prinzip erfüllt ist oder kein Aussage möglich gebe `null` zurück."

    **Prinzipien:**
    {checks_list}
    """
    )

    try:
        response = openai.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",  # Specify the model to use
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as e:
        return f"Error occurred: {e}"

    reply = response.choices[0].message.content.strip()
    return reply

# Gradio interface function
def gradio_interface(law_text):
    # Analyze the law text
    result = analyze_text_with_llm(law_text, principles)
    return result

# Create Gradio interface
interface = gr.Interface(
    fn=gradio_interface,
    inputs=gr.Textbox(lines=20, placeholder="Gesetzestext einfügen..."),
    outputs=gr.Markdown(),
    title="Digitalcheck KI Analyse",
    description="Gesetzestext eingeben, um zu prüfen, ob er die definierten Prinzipien des Digitalchecks erfüllt.",
)

# Launch the Gradio app
if __name__ == "__main__":
    interface.launch(share=True)
