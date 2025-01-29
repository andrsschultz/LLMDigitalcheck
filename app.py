import os
import json
from dotenv import load_dotenv
from openai import OpenAI

import helper

# Load environment variables from .env file
load_dotenv()

# Retrieve OPENAI_API_KEY and/or DEEPINFRA_API_KEY
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
deepinfra_api_key = os.getenv("DEEPINFRA_API_KEY")
if not deepinfra_api_key:
    raise ValueError("DEEPINFRA_API_KEY environment variable is not set.")

# Initialize OpenAI and DeepInfra API client
openaiClient = OpenAI(
    api_key=openai_api_key,  
)
deepinfraClient = OpenAI(
    api_key=deepinfra_api_key,  # Use environment variable for API key
    base_url="https://api.deepinfra.com/v1/openai",
)

# Available models configuration
# Note: Some models may output truncated output due to max token limitation
# Note: Some models may not conform to JSON response format, see below 
availableModels = {
    "openai": ["chatgpt-4o-latest", "gpt-4o-mini", "o1-mini", "o1-preview", "o1"],
    "deepinfra": ["meta-llama/Llama-3.3-70B-Instruct", "meta-llama/Meta-Llama-3.1-8B-Instruct", "deepseek-ai/DeepSeek-R1", "deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "deepseek-ai/DeepSeek-V3"]
}

# Select model for analysis
selectedModel =  "chatgpt-4o-latest"  # Can be changed to any model listed in availableModels

# STEP 1 ANALYZING LAW

def analyze_text_with_llm(law_text):

    prompt = (
    f"""
    Analysiere das am Ende gegebene Gesetz darauf, ob es folgende Prinzipien des Digitalchecks einhält: {helper.digital_check_prinzipien}\n\n
    
    Beurteile, ob das Gesetz die Prinzipien unten erfüllt. Gib die Antwort zwingend entsprechend der folgenden JSON-Datenstruktur zurück:

      "prinzipien": [
        {{
          "prinzip": "Digitale Kommunikation sicherstellen",
          "verstoss": true,
          "begruendung": "Die Vorschrift verlangt eine schriftliche Anzeige, ohne eine digitale Alternative vorzusehen. Dies führt zu Medienbrüchen und verhindert eine vollständig digitale Kommunikation.",
          "zitierte_passagen": [
            "§ 30 (1) [...] dem für die Verwaltung der Erbschaftsteuer zuständigen Finanzamt schriftlich anzuzeigen.",
            "§ 30 (5) [...] der Vermögensübergang dem nach § 35 Absatz 4 zuständigen Finanzamt schriftlich anzuzeigen."
          ],
          "verbesserungsvorschlag": "Eine Einreichungsmöglichkeit in elektronischer Form oder Textform ermöglichen."
        }},
        {{
          "prinzip": "Wiederverwendung von Daten & Standards ermöglichen",
          "verstoss": true,
          "begruendung": "Bestehende Register (z. B. Grundbuch, Melderegister, Steuer-ID) werden nicht genutzt. Betroffene müssen Informationen erneut eingeben, obwohl sie bereits in anderen Behörden vorliegen.",
          "zitierte_passagen": [
            "§ 30 (4) Die Anzeige soll folgende Angaben enthalten: 1. Vorname und Familienname, Identifikationsnummer (§ 139b der Abgabenordnung), Beruf, Wohnung des Erblassers oder Schenkers und des Erwerbers;",
            "§ 30 (4) 3. Gegenstand und Wert des Erwerbs;"
          ],
          "verbesserungsvorschlag": "Soweit die Daten den Behörden bereits vorliegen, die Notwendigkeit einer erneuten Datenübermittlung streichen. Die Behörde könnte dabei auf Steuer-ID und andere Register zugreifen, um diese Daten zu erlangen."
        }},
        {{
          "prinzip": "Datenschutz & Informationssicherheit gewährleisten",
          "verstoss": true,
          "begruendung": "Es gibt keine expliziten Vorgaben zur sicheren Verarbeitung und Speicherung der personenbezogenen Daten. Datenschutz und IT-Sicherheit sind nicht berücksichtigt.",
          "zitierte_passagen": [
            "§ 30 (4) Die Anzeige soll folgende Angaben enthalten: 1. Vorname und Familienname, Identifikationsnummer (§ 139b der Abgabenordnung), Beruf, Wohnung des Erblassers oder Schenkers und des Erwerbers;"
          ],
          "verbesserungsvorschlag": "Datensparsamkeit durch Minimaldatenerhebung sicherstellen."
        }},
        {{
          "prinzip": "Klare Regelungen für eine digitale Ausführung finden",
          "verstoss": true,
          "begruendung": "Die Regelung enthält keine spezifischen Anforderungen für eine digitale Prozessgestaltung. Es fehlen klare Schritte für eine digitale Anzeige und Harmonisierung der Begriffe.",
          "zitierte_passagen": [
            "§ 30 (4) Die Anzeige soll folgende Angaben enthalten: [...]"
          ],
          "verbesserungsvorschlag": "Klare Verfahrensschritte für ein digitales Meldesystem definieren, z. B. durch eine Online-Plattform mit strukturierten Eingabefeldern und Validierungsmöglichkeiten."
        }},
        {{
          "prinzip": "Automatisierung ermöglichen",
          "verstoss": true,
          "begruendung": "Die Vorschrift verlangt eine manuelle Anzeige und ermöglicht keine automatisierten oder antragslosen Verfahren. Es gibt keine rechtlichen Voraussetzungen für eine automatisierte Verarbeitung der Daten.",
          "zitierte_passagen": [
            "§ 30 (1) Jeder der Erbschaftsteuer unterliegende Erwerb [...] ist schriftlich anzuzeigen.",
            "§ 30 (5) [...] schriftlich anzuzeigen."
          ],
          "verbesserungsvorschlag": "Rechtliche Grundlagen für eine automatisierte Bearbeitung schaffen, z. B. durch standardisierte digitale Schnittstellen, automatische Registerabfragen und vorbefüllte Online-Formulare."
        }}
      ]
    

    Für jedes Prinzip:
    - `"Erfüllt"`: Gebe `true` zurück, wenn das Prinzip erfüllt ist, `false`, wenn es nicht erfüllt ist, oder `null`, wenn keine Aussage möglich ist.
    - `"Begründung"`: Erkläre prägnant, warum das Prinzip erfüllt oder nicht erfüllt ist. Zitiere die entsprechende Passagen im Gesetz mit Absatz/Satz/Nummer usw.
    - `"Zitat"`: Zitiere die entsprechenden Passagen des Gesetzestextes im Wortlaut, für die das Prinzip nicht erfüllt ist. Wenn das Prinzip erfüllt ist oder keine Aussage möglich ist, gebe `null` zurück.
    - `"Änderungsvorschlag"`: Wie würdest du den Gesetzestext ändern, um das Prinzip zu berücksichtigen? Wenn das Prinzip erfüllt ist oder keine Aussage möglich ist, gebe `null` zurück.

    Das Gesetz lautet: {law_text}
    """
    )

    try:
        # Select the appropriate client and model based on selectedModel
        if selectedModel in availableModels["openai"]:
            client = openaiClient
        elif selectedModel in availableModels["deepinfra"]:
            client = deepinfraClient
        else:
            raise ValueError(f"Selected model {selectedModel} not found in available models")

        response = client.chat.completions.create(
            model=selectedModel,
            messages=[{"role": "user", "content": prompt}],
            #Comment line below if selected model does not allow for response formatting
            response_format={ "type": "json_object" }
        )
        print("\nToken Usage:")
        print(f"Input tokens: {response.usage.prompt_tokens}")
        print(f"Output tokens: {response.usage.completion_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")
    except Exception as e:
        return f"Error occurred: {e}"

    reply = response.choices[0].message.content.strip()
    return reply

# STEP 2 AMENDING LAW

def generate_amended_law(law_text, input_response):
    
    prompt = f"""
    Als erfahrener Rechtsexperte, überarbeite bitte den am Ende gegebenen Gesetzestext unter Berücksichtigung der im folgenden JSON enthaltenen Änderungsvorschlägen: {input_response}\n\n
    
    Das Gesetz lautet: {law_text}

    Gib den überarbeiteten Gesetzestext in seiner Gesamtheit zurück. Markiere geänderte oder neue Passagen durch [[ ]] Klammern.
    """    
    try:
        # Select the appropriate client and model based on selectedModel
        if selectedModel in availableModels["openai"]:
            client = openaiClient
        elif selectedModel in availableModels["deepinfra"]:
            client = deepinfraClient
        else:
            raise ValueError(f"Selected model {selectedModel} not found in available models")

        response = client.chat.completions.create(
            model=selectedModel,
            messages=[{"role": "user", "content": prompt}]
        )
        
        print("\nToken Usage for Law Amendment:")
        print(f"Input tokens: {response.usage.prompt_tokens}")
        print(f"Output tokens: {response.usage.completion_tokens}")
        print(f"Total tokens: {response.usage.total_tokens}")
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating amended law: {e}"

if __name__ == "__main__":
    print("Enter the law text (type 'END' on a new line and press enter to finish):")
    # Initialize an empty list to collect lines of input
    law_text_lines = []

    # Collect input until the user types 'END'
    while True:
        line = input()
        if line.strip().upper() == "END":  # End the input if the user types 'END'
            break
        law_text_lines.append(line)

    # Join all lines into a single string
    law_text = "\n".join(law_text_lines)

    if not law_text: 
        print("No law text entered. Using sample law (§30 ErbStG) for analysis.")
        law_text = helper.sample_law
    else: 
        print("Law text entered:")
        print(law_text)

    # The rest of the script follows as before
    print("Analyzing law started ...")
    result = analyze_text_with_llm(law_text)
    if result:
        print("Analyzing law completed. Response:")
        print(result)
        # STEP 2, see above
        amended_law = generate_amended_law(law_text, result)
        if amended_law: 
            print("Amending law completed. Amended law text:")
            print(amended_law)
