import os
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
        )
    except Exception as e:
        return f"Error occurred: {e}"

    reply = response.choices[0].message.content.strip()
    return reply

if __name__ == "__main__":
    # Replace this with your actual law text
    law_text = """
    Erbschaftsteuer- und Schenkungsteuergesetz (ErbStG)
§ 30 Anzeige des Erwerbs

(1) Jeder der Erbschaftsteuer unterliegende Erwerb (§ 1) ist vom Erwerber, bei einer Zweckzuwendung vom Beschwerten binnen einer Frist von drei Monaten nach erlangter Kenntnis von dem Anfall oder von dem Eintritt der Verpflichtung dem für die Verwaltung der Erbschaftsteuer zuständigen Finanzamt schriftlich anzuzeigen.
(2) Erfolgt der steuerpflichtige Erwerb durch ein Rechtsgeschäft unter Lebenden, ist zur Anzeige auch derjenige verpflichtet, aus dessen Vermögen der Erwerb stammt.
(3) Einer Anzeige bedarf es nicht, wenn der Erwerb auf einer von einem deutschen Gericht, einem deutschen Notar oder einem deutschen Konsul eröffneten Verfügung von Todes wegen beruht und sich aus der Verfügung das Verhältnis des Erwerbers zum Erblasser unzweifelhaft ergibt; das gilt nicht, wenn zum Erwerb Grundbesitz, Betriebsvermögen, Anteile an Kapitalgesellschaften, die nicht der Anzeigepflicht nach § 33 unterliegen, oder Auslandsvermögen gehört. Einer Anzeige bedarf es auch nicht, wenn eine Schenkung unter Lebenden oder eine Zweckzuwendung gerichtlich oder notariell beurkundet ist.
(4) Die Anzeige soll folgende Angaben enthalten:
1.
Vorname und Familienname, Identifikationsnummer (§ 139b der Abgabenordnung), Beruf, Wohnung des Erblassers oder Schenkers und des Erwerbers;
2.
Todestag und Sterbeort des Erblassers oder Zeitpunkt der Ausführung der Schenkung;
3.
Gegenstand und Wert des Erwerbs;
4.
Rechtsgrund des Erwerbs wie gesetzliche Erbfolge, Vermächtnis, Ausstattung;
5.
persönliches Verhältnis des Erwerbers zum Erblasser oder zum Schenker wie Verwandtschaft, Schwägerschaft, Dienstverhältnis;
6.
frühere Zuwendungen des Erblassers oder Schenkers an den Erwerber nach Art, Wert und Zeitpunkt der einzelnen Zuwendung.
(5) In den Fällen des § 1 Absatz 1 Nummer 4 ist von der Stiftung oder dem Verein binnen einer Frist von drei Monaten nach dem Zeitpunkt des ersten Übergangs von Vermögen auf die Stiftung oder auf den Verein der Vermögensübergang dem nach § 35 Absatz 4 zuständigen Finanzamt schriftlich anzuzeigen. Die Anzeige soll folgende Angaben enthalten:
1.
Name, Ort der Geschäftsleitung und des Sitzes der Stiftung oder des Vereins,
2.
Name und Anschrift des gesetzlichen Vertreters der Stiftung oder des Vereins,
3.
Zweck der Stiftung oder des Vereins,
4.
Zeitpunkt des ersten Vermögensübergangs auf die Stiftung oder den Verein,
5.
Wert und Zusammensetzung des Vermögens.
    """
    result = analyze_text_with_llm(law_text, principles)
    print(result)
