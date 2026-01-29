import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from ..models.tailored_resume import TailoredResume

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1,
    max_output_tokens=4096,
)

structured_llm = llm.with_structured_output(TailoredResume, method="json_schema")

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert Irish tech recruiter helping non-EEA graduates tailor resumes for Critical Skills Employment Permit roles.
Target companies (e.g. Workday, Stripe, SIG, Accenture, HubSpot) value quantified impact, cloud/AI skills, full-stack exposure.

Given the parsed resume and target role/company, produce:
- Professional summary: concise, keyword-rich, highlight recent Irish Master's (Level 9) for Stamp 1G eligibility.
- 4–8 achievement bullets: start with strong action verbs, preserve/include metrics, weave in role-relevant keywords (e.g. Python, Machine Learning, AWS, LLMs, LangChain).
- Key skills: top 10–15, re-ranked and prioritized for the role.
- Cover letter note: brief, professional mention of visa eligibility (e.g. eligible for 24-month Stamp 1G) Ensure cover_letter_note is a complete 1-2 sentence..

2026 thresholds reminder (do NOT include in output unless explicitly asked):
- Graduate CSEP: €36,848
- Graduate GEP: €34,009

Output ONLY valid structured JSON — no extra text.
"""),
    ("human", """
Parsed resume: {parsed_resume}

Target role: {target_role}
Target company/context: {target_company} (Ireland)

Tailor the resume now.
""")
])

chain = prompt | structured_llm

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def tailor_resume(parsed_resume: dict, target_role: str, target_company: str = "") -> TailoredResume:
    """
    Tailor resume using Gemini structured output.
    Input: dict from parsed_resume (not Resume object).
    """
    result = chain.invoke({
        "parsed_resume": parsed_resume,
        "target_role": target_role,
        "target_company": target_company
    })
    return result


def calculate_match_score(resume_skills: list, tailored_skills: list) -> float:
    """Calculate skill alignment score 0-100."""
    if not resume_skills or not tailored_skills:
        return 50.0

    resume_skill_items = set()
    for skill_cat in resume_skills:
        if isinstance(skill_cat, dict):
            resume_skill_items.update(skill_cat.get("items", []))

    matched = sum(1 for skill in tailored_skills if skill in resume_skill_items)
    return min(100.0, (matched / len(tailored_skills)) * 100) if tailored_skills else 50.0


def generate_visa_advice(education: list) -> str:
    """Generate visa eligibility advice based on NFQ education level."""
    if not education:
        return "Review education details to determine visa eligibility."

    max_nfq = max(
        [edu.get("nfq_level", 0) for edu in education if isinstance(edu, dict)],
        default=0,
    )

    if max_nfq >= 9:
        return (
            "Eligible for 24-month Stamp 1G as a Master's degree holder (NFQ Level 9). "
            "CSEP threshold: €40,904 general | €36,848 recent grads."
        )
    if max_nfq == 8:
        return (
            "Eligible for 12-month Stamp 1G as a Bachelor's degree holder (NFQ Level 8). "
            "A Master's (NFQ 9) extends Stamp 1G to 24 months."
        )
    return "Verify education credentials. Minimum NFQ Level 8 is required for Stamp 1G."

# ────────────────────────────────────────────────
# Standalone Test (run: python -m backend.app.services.resume_tailor)
# ────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        # Paste ONLY the "parsed_resume" inner dict (not the wrapper with "status")
        parsed_data = {
            "name": "YASH MODI",
            "contact": {
            "phone": "+353 (89) 492-0341",
            "email": "yashmodi.ie@gmail.com",
            "linkedin": "linkedin.com/in/yshmodi/",
            "location": "Cork, Ireland"
            },
            "summary": "Graduate AI Engineer with hands-on experience in NLP, Deep Learning, Generative AI, and cloud-based deployment. Skilled in building and scaling AI models for automation, data-driven insights, and user experience enhancement. Experienced with LLM APIs (e.g., GPT) and MLOps concepts, with additional background in full-stack development for end-to-end product delivery.",
            "education": [
            {
                "degree": "Master of Science",
                "field": "Artificial Intelligence",
                "institution": "Munster Technological University",
                "year": "2025",
                "nfq_level": 9
            },
            {
                "degree": "Bachelor of Technology",
                "field": "Information Technology",
                "institution": "UKA Tarsadia University",
                "year": "2024",
                "nfq_level": 8
            }
            ],
            "experience": [
            {
                "title": "Software Engineer Intern",
                "company": "Yosa Technology Solutions Pvt. Ltd.",
                "dates": "Jan 2024 – Aug 2024",
                "bullets": [
                "Developed and deployed a cloud-based HRMS portal using AngularJS and Spring Boot, resulting in a 40% improvement in HR process efficiency.",
                "Led full-stack development for employee attendance and leave management modules, enhancing data accuracy and reducing manual HR workload by 60%.",
                "Implemented RESTful APIs, integrated Firebase authentication, and optimized backend logic for real-time tracking and filtering of attendance logs.",
                "Gained hands-on experience with DevOps concepts, server operations, and containerized deployment using Apache Tomcat, resulting in faster and more reliable application deployment."
                ]
            },
            {
                "title": "React Developer Intern",
                "company": "Code Alchemy Pvt Ltd",
                "dates": "May 2023 – Jun 2023",
                "bullets": [
                "Developed interactive web interfaces using ReactJS and Tailwind CSS, resulting in improved UI responsiveness and 30% faster page load times.",
                "Collaborated on full-stack projects integrating Firebase for authentication and real-time data storage, enhancing backend scalability and performance.",
                "Designed and developed a personalized vector art generator using ReactJS and Tailwind CSS, showcasing interactive UI development, state management, and real-time rendering of SVG components."
                ]
            }
            ],
            "skills": [
            {
                "name": "Programming Languages & Frameworks",
                "items": [
                "Python",
                "JavaScript",
                "Spring Boot",
                "AngularJS",
                "ReactJS",
                "LangChain",
                "TensorFlow",
                "Scikit-learn"
                ]
            },
            {
                "name": "AI/ML",
                "items": [
                "Machine Learning",
                "Deep Learning",
                "Natural Language Processing (NLP)",
                "Generative AI",
                "LLMs (GPT APIs, Hugging Face)",
                "Prompt Engineering"
                ]
            },
            {
                "name": "Cloud & DevOps",
                "items": [
                "AWS",
                "GCP",
                "Git",
                "Apache Tomcat",
                "Firebase"
                ]
            },
            {
                "name": "Databases & APIs",
                "items": [
                "SQL",
                "REST APIs",
                "Database Management Systems"
                ]
            },
            {
                "name": "Soft Skills",
                "items": [
                "Team Collaboration",
                "Communication",
                "Time Management",
                "Critical Thinking",
                "Leadership"
                ]
            }
            ],
            "projects": [
            {
                "title": "Co-evolutionary Level Generation and Agent Development: A Hybrid GAN-RL Architecture for Ensuring Playable Game Content",
                "description": "Explored the integration of Generative Adversarial Networks (GANs) and Reinforcement Learning (RL) agents to create dynamic, procedurally generated game environments. Developed a conceptual co-evolutionary framework and implemented key components using TOAD-GAN and UC Berkeley’s Pac-Man AI project.",
                "tech": [
                "GANs",
                "Reinforcement Learning (RL)",
                "TOAD-GAN",
                "Pac-Man AI"
                ]
            },
            {
                "title": "Sentiment and Hate Analysis of Mpox Instagram Dataset",
                "description": "Developed an NLP-based tool using Python, TensorFlow, and Scikit-learn to analyze sentiment and detect hate speech in Instagram posts during the Mpox outbreak. Achieved 85% accuracy in classifying user-generated content, providing actionable insights into public health responses.",
                "tech": [
                "Python",
                "TensorFlow",
                "Scikit-learn",
                "NLP"
                ]
            },
            {
                "title": "Streamlined HR Management: Cloud-Based HRMS Portal",
                "description": "Built a cloud-based HR portal using AngularJS, Spring Boot, and AWS, enabling real-time employee attendance tracking and leave management. Improved HR process efficiency by 40% and reduced manual workload by 60% through optimized RESTful APIs and Firebase integration.",
                "tech": [
                "AngularJS",
                "Spring Boot",
                "AWS",
                "RESTful APIs",
                "Firebase"
                ]
            },
            {
                "title": "Personalized Alpaca Vector Art Generator",
                "description": "Created an interactive web app with ReactJS and Tailwind CSS for designing and downloading high-resolution alpaca vector art avatars. Enhanced user engagement with real-time customization, achieving 30% faster page load times and seamless SVG rendering.",
                "tech": [
                "ReactJS",
                "Tailwind CSS",
                "SVG"
                ]
            }
            ],
            "certifications": [
            {
                "name": "Data Science Foundations – Level 1",
                "issuer": "IBM"
            },
            {
                "name": "Introduction to Generative AI",
                "issuer": "Google Cloud Skills Boost"
            }
            ],
            "visa_notes": {
                "stamp_1g_months": 24
            }
        }

        tailored = tailor_resume(
            parsed_resume=parsed_data,
            target_role="AI Engineer",
            target_company="Stripe Ireland"
        )

        print("Tailored Professional Summary:\n", tailored.professional_summary)
        print("\nAchievement Bullets:")
        for bullet in tailored.achievement_bullets:
            print(f"- {bullet}")
        print("\nKey Skills:", ", ".join(tailored.key_skills))
        print("\nCover Letter Visa Note:", tailored.cover_letter_note)

    except Exception as e:
        print(f"Error during tailoring test: {e}")
