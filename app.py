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

# Define Digitalcheck principles
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
    Beurteile, ob das Gesetz die Prinzipien unten erfüllt. Gib die Antwort zwingend in der folgenden JSON-Datenstruktur zurück:

    {{
      "Digitale Kommunikation": [
        {{
          "Prinzip": "technologieoffen",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Verbesserungsvorschlag": "string"
        }}
      ],
      "Wiederverwendung von Daten & Standards": [
        {{
          "Prinzip": "Daten-Austauschverfahren sind geschaffen",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Verbesserungsvorschlag": "string"
        }}
      ],
      "Datenschutz & Informationssicherheit": [
        {{
          "Prinzip": "Datenschutz-Expertise wurde konsultiert",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Verbesserungsvorschlag": "string"
        }}
      ],
      "Klare Regelungen für eine digitale Ausführung": [
        {{
          "Prinzip": "Verständlichkeit wurde getestet",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Verbesserungsvorschlag": "string"
        }}
      ],
      "Automatisierung": [
        {{
          "Prinzip": "IT-Expertise wurde einbezogen",
          "Erfüllt": true/false/null,
          "Begründung": "string",
          "Verbesserungsvorschlag": "string"
        }}
      ]
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
        
        # Extract improvement suggestions
        improvement_suggestions = []
        
        for category, items in result_json.items():
            for item in items:
                if item.get("Verbesserungsvorschlag") is not None and item["Verbesserungsvorschlag"] != "null":
                    improvement_suggestions.append({
                        "category": category,
                        "principle": item["Prinzip"],
                        "suggestion": item["Verbesserungsvorschlag"]
                    })

        """
        print("\nImprovement Suggestions:")
        for suggestion in improvement_suggestions:
            print(f"\nCategory: {suggestion['category']}")
            print(f"Principle: {suggestion['principle']}")
            print(f"Suggestion: {suggestion['suggestion']}")
        """
            
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
            #TBD: avoid redudancies when prompting; maybe pass along corresponding categories and principles?
            f"{suggestion['suggestion']}"
        )
    
    suggestions_text = "\n".join(formatted_suggestions)
    
    #TBD: Improve prompt structure
    prompt = f"""
    Als erfahrener Rechtsexperte, überarbeite bitte den folgenden Gesetzestext unter Berücksichtigung der Verbesserungsvorschläge für die digitale Transformation. 
    Beachte dabei:
    - Behalte die juristische Sprache und Struktur bei
    - Füge neue Absätze ein, wo nötig
    - Ergänze oder modifiziere bestehende Absätze
    - Stelle sicher, dass die Änderungen die digitale Transformation unterstützen
    - Behalte die ursprüngliche Nummerierung bei, füge bei Bedarf Unterpunkte hinzu

    Ursprünglicher Gesetzestext:
    {law_text}

    Zu berücksichtigende Verbesserungsvorschläge:
    {suggestions_text}

    Gib den überarbeiteten Gesetzestext in seiner Gesamtheit zurück. Markiere geänderte oder neue Passagen durch [[ ]] Klammern.
    """

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
