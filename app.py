import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Retrieve the OPENAI_API_KEY
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

# Initialize OpenAI API
openai = OpenAI(
    api_key=openai_api_key,  # Use environment variable for API key
    base_url="https://api.deepinfra.com/v1/openai",  # DeepInfra endpoint (adjust if needed)
)

# Define Digitalcheck principles, cf. https://www.digitale-verwaltung.de/SharedDocs/downloads/Webs/DV/DE/digitalcheck-fuenf-prinzipien.pdf?__blob=publicationFile&v=5
# TBD: Improvements structure, information
principles = {
    "Digitale Kommunikation": [
        "Der Inhalt des Regelungsvorhabens ist technologieoffen.",
        "Medienbrüche sind vermieden.",
        "Analoge Schriftformerfordernisse und Nachweispflichten sind vermieden.",
        "Barrierefreiheit und deren Anforderungen sind ermöglicht."
    ],
    "Wiederverwendung von Daten & Standards": [
        "Bestehende Datenerfassungs- und Austauschverfahren, Register und weitere Quellen werden berücksichtigt und nicht erneut erfasst.",
        "Es besteht die Voraussetzung für die Verwendung bestehender relevanter Daten, Standards, Richtlinien und Komponenten.",
        "Barrierefreiheit und Anforderungen für Barrierefreiheit sind ermöglicht."
    ],
    "Datenschutz & Informationssicherheit": [
        "Der Erfüllungsaufwand berücksichtigt die für die Erfüllung der Vorgaben der Informationssicherheit notwendigen finanziellen und personellen Ressourcen.",
        "Es wurden Datenschutz-Expertise und IT-Sicherheitsexpertise konsultiert oder berücksichtigt",
        "(Gesetzliche) Anforderungen des Datenschutzes, insbesondere der Datensparsamkeit, und der Informationssicherheit sind berücksichtigt"
    ],
    "Klare Regelungen für eine digitale Ausführung": [
        "Die Regelungen wurden mit am Vollzug beteiligten Verwaltungen, Unternehmen, Organisationen oder Bürgerinnen und Bürgern auf Verständlichkeit getestet.",
        "Bei verfahrenstechnischen Anforderungen kann das Regelungsvorhaben in Aufgaben bzw. chronologische Schritte übersetzt werden.",
        "Klare Entscheidungsstrukturen liegen vor durch eindeutige Kriterien sowie kohärente und logische Systematik. Ausnahmen sind klar gekennzeichnet.",
        "Rechtsbegriffe sind harmonisiert. Alle Begriffe sind klar und eindeutig. Auslegungen verhindern eine einheitliche Umsetzung."
    ],
    "Automatisierung ermöglichen": [
        "IT-Expertise wurde bei der Erstellung einbezogen.",
        "Das Regelungsvorhaben schafft rechtliche Voraussetzungen für automatisierte und/oder antragslose Verfahren.",
        "Klare Entscheidungsstrukturen liegen vor; durch eindeutige Kriterien sowie kohärente und logische Systematik.",
        "Rechtsbegriffe sind harmonisiert. Alle Begriffe sind klar und eindeutig. Auslegungen verhindern die vollständige Automatisierung von Umsetzungsprozessen."
    ]
}

# STEP 1 ANALYZING LAW

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
    Beurteile, ob das Gesetz die Prinzipien unten erfüllt. Gib die Antwort zwingend entsprechend der folgenden JSON-Datenstruktur zurück:

    {{
      "Digitale Kommunikation": [
        {{
          "Prinzip": "Der Inhalt des Regelungsvorhabens ist technologieoffen.",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Zitat": "string"/null,
          "Änderungsvorschlag": "string"
        }}
      ],
      "Wiederverwendung von Daten & Standards": [
        {{
          "Bestehende Datenerfassungs- und Austauschverfahren, Register und weitere Quellen werden berücksichtigt und nicht erneut erfasst.",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Zitat": "string"/null,
          "Änderungsvorschlag": "string"
        }}
      ],
      "Datenschutz & Informationssicherheit": [
        {{
          "Prinzip": "(Gesetzliche) Anforderungen des Datenschutzes, insbesondere der Datensparsamkeit, und der Informationssicherheit sind berücksichtigt",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Zitat": "string"/null,
          "Änderungsvorschlag": "string"
        }}
      ],
      "Klare Regelungen für eine digitale Ausführung": [
        {{
          "Klare Entscheidungsstrukturen liegen vor durch eindeutige Kriterien sowie kohärente und logische Systematik. Ausnahmen sind klar gekennzeichnet.",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Zitat": "string"/null,
          "Änderungsvorschlag": "string"
        }}
      ],
      "Automatisierung": [
        {{
          "Das Regelungsvorhaben schafft rechtliche Voraussetzungen für automatisierte und/oder antragslose Verfahren.",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Zitat": "string"/null,
          "Änderungsvorschlag": "string"
        }}
      ]
    }}

    Für jedes Prinzip:
    - `"Erfüllt"`: Gebe `true` zurück, wenn das Prinzip erfüllt ist, `false`, wenn es nicht erfüllt ist, oder `null`, wenn keine Aussage möglich ist.
    - `"Begründung"`: Erkläre prägnant, warum das Prinzip erfüllt oder nicht erfüllt ist. Zitiere die entsprechende Passage im Gesetz mit Absatz/Satz/Nummer usw.
    - `"Zitat"`: Zitiere den entsprechenden Worlaut im Gesetzestext, wenn das Prinzip nicht erfüllt ist. Wenn das Prinzip erfüllt ist oder kein Aussage möglich gebe `null` zurück."
    - `"Änderungsvorschlag"`: Wie würdest du den Gesetzestext ändern um das Prinzip zu berücksichtigen? Wenn das Prinzip erfüllt ist oder kein Aussage möglich gebe `null` zurück."

    **Prinzipien:**
    {checks_list}
    """
    )

    try:
        response = openai.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",  # Adjust model if needed
            messages=[{"role": "user", "content": prompt}],
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

# STEP 2 PARSING JSON
def parse_json(result):
    try:
        # Parse the JSON response
        result_json = json.loads(result)
        
        # Extract improvement suggestions only for items where Erfüllt is false
        improvement_suggestions = []
        
        for category, items in result_json.items():
            for item in items:
                if item.get("Erfüllt") == False and item.get("Änderungsvorschlag") is not None and item["Änderungsvorschlag"] != "null":
                    improvement_suggestions.append({
                        "category": category,
                        "principle": item["Prinzip"],
                        "zitat": item["Zitat"],
                        "suggestion": item["Änderungsvorschlag"]
                    })

        print("\nImprovement Suggestions for unfulfilled principles:")
        for suggestion in improvement_suggestions:
            print(f"\nCategory: {suggestion['category']}")
            print(f"Principle: {suggestion['principle']}")
            print(f"Zitat: {suggestion['zitat']}")
            print(f"Suggestion: {suggestion['suggestion']}")
            
        return improvement_suggestions

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return None
    except Exception as e:
        print(f"Error processing results: {e}")
        return None


# STEP 3 AMENDING LAW

def generate_amended_law(law_text, improvement_suggestions):
    """
    Generate an amended version of the law text based on improvement suggestions.
    
    Args:
        law_text (str): The original law text
        improvement_suggestions (list): List of dictionaries containing improvement suggestions
    
    Returns:
        str: The LLM response containing the amended law text
    """
    # Format suggestions for the prompt
    formatted_suggestions = []
    for suggestion in improvement_suggestions:
        formatted_suggestions.append(
            f"'{suggestion['suggestion']}"
        )
    
    suggestions_text = "\n".join(formatted_suggestions)
    
    prompt = f"""
    Als erfahrener Rechtsexperte, überarbeite bitte den folgenden Gesetzestext unter Berücksichtigung der Änderungsvorschläge für die digitale Transformation. 
    
    Ursprünglicher Gesetzestext:
    {law_text}

    Zu berücksichtigende Änderungsvorschläge:
    {suggestions_text}

    Gib den überarbeiteten Gesetzestext in seiner Gesamtheit zurück. Markiere geänderte oder neue Passagen durch [[ ]] Klammern.
    """

    print(prompt)
    
    try:
        response = openai.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
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

    print("Law text entered:")
    print(law_text)

    # The rest of the script follows as before
    print("Analyzing law started ...")
    result = analyze_text_with_llm(law_text, principles)
    if result:
        print("Analyzing law completed.")
        print(result)
         # STEP 2, see above
        print("Parsing returned JSON started ...")
        improvement_suggestions = parse_json(result)
        print("Parsing returned JSON completed")
        print(improvement_suggestions)
        if improvement_suggestions:
            print("Amending law started ...")
             # STEP 3, see above
            amended_law = generate_amended_law(law_text, improvement_suggestions)
            if amended_law: 
                print("Amending law completed. Amended law text:")
                print(amended_law)
