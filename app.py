import os
from openai import OpenAI

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

# Function to analyze a law text against a principle using OpenAI
def analyze_text_with_llm(law_text, principles):
    # Fetch API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API key not found! Please set the OPENAI_API_KEY environment variable.")
    
    client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
    )   

    results = {}

    for principle, checks in principles.items():
        principle_results = []
        for check in checks:
            # Construct the prompt
            prompt = (
                f"""
                Bei dem folgenden Dokument handelt es sich um ein Gesetz:  {law_text}\n\n
                "Der Digitalcheck unterstützt bei der Erarbeitung von digitaltauglichen Regelungsvorhaben für eine einfache und nutzerorientierte digitale Umsetzung.
                Erfüllt der Text folgendes Prinzip aus dem Digitalcheck: '{check}'?
                Stelle dar, ob das Prinzip erfüllt ist und begründe deine Entscheidung prägnant. Mache einen kurzen Änderungsvorschlag. Wenn du keine Information geben kannst, antworte mit "Das weiß ich nicht".
                """
            )

            print(prompt)

            # Query the OpenAI API
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )

            print("Check Prinzip: " + check)

            # Parse the response
            reply = response.choices[0].message.content.strip()
            principle_results.append({"check": check, "response": reply})

        results[principle] = principle_results

    return results

# Example usage
if __name__ == "__main__":
    # Input law text
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
Fußnote

(+++ § 30: Zur Anwendung vgl. §§ 13 u. 37 +++)
    """

    # Analyze the text
    analysis_results = analyze_text_with_llm(law_text, principles)

    # Output results
    for principle, checks in analysis_results.items():
        print(f"Principle: {principle}")
        for check in checks:
            print(f"  - Check: {check['check']}")
            print(f"    Response: {check['response']}")
        print()
