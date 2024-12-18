import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

# Load environment variables from .env file
load_dotenv()

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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "API key not found! Please set the OPENAI_API_KEY environment variable."
    
    client = OpenAI(api_key=api_key)

    all_checks = []
    for principle_group, checks in principles.items():
        all_checks.append(f"**{principle_group}:**")
        all_checks.extend([f"- {check}" for check in checks])
    checks_list = "\n".join(all_checks)

    prompt = (
        f"""
        Das folgende Dokument ist ein Gesetz: {law_text}\n\n
        "Der Digitalcheck unterstützt bei der Erarbeitung von digitaltauglichen Regelungsvorhaben.
        Beurteile, ob das Gesetz die Prinzipien unten erfüllt. Für jedes Prinzip: Gib an, ob es erfüllt ist, begründe deine Antwort kurz und mache einen Verbesserungsvorschlag.

        **Prinzipien:**
        {checks_list}

        Wenn du keine Aussage treffen kannst, antworte mit 'Das weiß ich nicht'.
        """
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            timeout=30
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
    inputs=gr.Textbox(lines=20, placeholder="Fügen Sie hier den Gesetzestext ein..."),
    outputs=gr.Markdown(),
    title="Digitalcheck Analyzer",
    description="Geben Sie einen Gesetzestext ein, und der Digitalcheck wird prüfen, ob er die definierten Prinzipien erfüllt.",
)

# Launch the Gradio app
if __name__ == "__main__":
    interface.launch(share=True)
