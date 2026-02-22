import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


DOCUMENT_PROMPTS = {
    "employment_contract": """You are an expert legal document drafter. Generate a professional Employment Contract with the following details:
- Employer: {employer_name}
- Employee: {employee_name}
- Job Title: {job_title}
- Start Date: {start_date}
- Salary: {salary}
- Work Location: {work_location}
- Additional Terms: {additional_terms}

Draft a complete, professional employment contract with all standard clauses including duties, compensation, benefits, confidentiality, termination, and governing law. Format it cleanly with clear section headers.""",

    "nda": """You are an expert legal document drafter. Generate a professional Non-Disclosure Agreement (NDA) with the following details:
- Disclosing Party: {party_one}
- Receiving Party: {party_two}
- Effective Date: {start_date}
- Purpose: {purpose}
- Duration: {duration}
- Additional Terms: {additional_terms}

Draft a complete, professional NDA with all standard clauses including definition of confidential information, obligations, exclusions, return of information, remedies, and governing law. Format it cleanly with clear section headers.""",

    "lease_agreement": """You are an expert legal document drafter. Generate a professional Residential Lease Agreement with the following details:
- Landlord: {party_one}
- Tenant: {party_two}
- Property Address: {property_address}
- Lease Start Date: {start_date}
- Lease Duration: {duration}
- Monthly Rent: {salary}
- Security Deposit: {security_deposit}
- Additional Terms: {additional_terms}

Draft a complete, professional lease agreement with all standard clauses including rent payment, security deposit, maintenance, utilities, entry rights, termination, and governing law. Format it cleanly with clear section headers.""",

    "service_agreement": """You are an expert legal document drafter. Generate a professional Service Agreement with the following details:
- Client: {party_one}
- Service Provider: {party_two}
- Services: {purpose}
- Start Date: {start_date}
- Duration: {duration}
- Payment: {salary}
- Additional Terms: {additional_terms}

Draft a complete, professional service agreement with all standard clauses including scope of work, payment terms, intellectual property, confidentiality, termination, and governing law. Format it cleanly with clear section headers.""",
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        if not client:
            return jsonify({"error": "GEMINI_API_KEY not found. Please set it in your .env file."}), 500

        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        doc_type = data.get("document_type", "")
        if doc_type not in DOCUMENT_PROMPTS:
            return jsonify({"error": "Invalid document type"}), 400

        # Build prompt from template
        prompt_template = DOCUMENT_PROMPTS[doc_type]
        prompt = prompt_template.format(
            employer_name=data.get("employer_name", ""),
            employee_name=data.get("employee_name", ""),
            party_one=data.get("party_one", data.get("employer_name", "")),
            party_two=data.get("party_two", data.get("employee_name", "")),
            job_title=data.get("job_title", ""),
            start_date=data.get("start_date", ""),
            salary=data.get("salary", ""),
            work_location=data.get("work_location", ""),
            purpose=data.get("purpose", ""),
            duration=data.get("duration", ""),
            property_address=data.get("property_address", ""),
            security_deposit=data.get("security_deposit", ""),
            additional_terms=data.get("additional_terms", "None"),
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if not response or not hasattr(response, "text") or not response.text:
            return jsonify({"error": "Failed to generate document. Please try again."}), 500

        document_text = response.text

        return jsonify({"success": True, "document": document_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)