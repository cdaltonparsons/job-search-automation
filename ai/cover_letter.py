import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

COVER_LETTER_SYSTEM = """You are an expert career coach helping a frontend/full-stack engineer (Angular, TypeScript)
write targeted cover letters. Write concisely and authentically — no fluff, no clichés.
Match the tone of the company (startup = casual, enterprise = professional).
Structure: 3 paragraphs — why this role, what you bring, what excites you about the company."""

GAP_ANALYSIS_SYSTEM = """You are a resume analyst. Be direct and specific.
Identify what skills or experience the job requires that the resume lacks or undersells.
Format as a short bullet list. Be honest — this helps the candidate prepare."""


def generate_cover_letter(resume: str, job_title: str, company: str, job_description: str) -> str:
    """Stream a tailored cover letter to stdout. The resume is prompt-cached across calls."""
    print(f"\n--- Cover Letter: {job_title} at {company} ---\n")

    full_text = ""
    with client.messages.stream(
        model="claude-opus-5",
        max_tokens=1024,
        system=COVER_LETTER_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"My resume:\n\n{resume}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Write a cover letter for this role:\n\n"
                            f"Title: {job_title}\nCompany: {company}\n\n"
                            f"Job Description:\n{job_description[:3000]}"
                        ),
                    },
                ],
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text

    print()
    return full_text


def analyze_gap(resume: str, job_title: str, job_description: str) -> str:
    """Identify gaps between the resume and job requirements. Resume is prompt-cached."""
    print(f"\n--- Gap Analysis: {job_title} ---\n")

    full_text = ""
    with client.messages.stream(
        model="claude-opus-5",
        max_tokens=512,
        system=GAP_ANALYSIS_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"My resume:\n\n{resume}",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": (
                            f"Job: {job_title}\n\n"
                            f"Description:\n{job_description[:3000]}\n\n"
                            "What does this role require that my resume lacks or undersells?"
                        ),
                    },
                ],
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_text += text

    print()
    return full_text
