from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from ..models.tailored_resume import TailoredResume
from ..core.llm_router import invoke_with_fallback, get_current_provider


prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an expert tech recruiter helping candidates tailor resumes for specific job applications.

Given the parsed resume and job description, produce:
- Professional summary: concise, keyword-rich, tailored to the specific role and company. Highlight relevant experience and skills.
- 5-7 achievement bullets: start with strong action verbs, preserve metrics from original resume, weave in keywords from the JD.
- Key skills: top 10-15, re-ranked and prioritized based on the job requirements.

Focus ONLY on skills, experience, and achievements. No visa, work authorization, or immigration mentions.

Output ONLY valid structured JSON — no extra text.
"""),
    ("human", """
Parsed resume: {parsed_resume}

Job Description:
{jd_text}

Target role: {target_role}
Target company: {target_company}

Tailor the resume to match this job.
""")
])


def tailor_resume(
    parsed_resume: dict,
    target_role: str,
    target_company: str = "",
    jd_text: str = ""
) -> TailoredResume:
    """
    Tailor resume using multi-LLM router with automatic fallback.
    Pure skill-focused tailoring - no visa/authorization logic.
    """
    logger.info(f"Tailoring resume with {get_current_provider()}...")

    result = invoke_with_fallback(
        prompt_template=prompt,
        input_data={
            "parsed_resume": parsed_resume,
            "jd_text": jd_text or "No specific job description provided. Tailor for the target role generically.",
            "target_role": target_role,
            "target_company": target_company
        },
        output_schema=TailoredResume,
        temperature=0.1,
    )

    return result


def calculate_match_score(resume_skills: list, tailored_skills: list) -> float:
    """
    Calculate skill alignment score 0-100 using fuzzy substring matching.
    Handles cases like 'AWS (API Gateway, Lambda)' matching 'AWS'.
    """
    if not resume_skills or not tailored_skills:
        return 50.0

    # Flatten resume skills to lowercase for matching
    resume_skill_items = set()
    for skill_cat in resume_skills:
        if isinstance(skill_cat, dict):
            for item in skill_cat.get("items", []):
                resume_skill_items.add(item.lower().strip())

    matched = 0
    for tailored_skill in tailored_skills:
        tailored_lower = tailored_skill.lower().strip()
        # Check exact match OR if any resume skill is contained in tailored skill
        for resume_skill in resume_skill_items:
            if resume_skill in tailored_lower or tailored_lower in resume_skill:
                matched += 1
                break

    return min(100.0, (matched / len(tailored_skills)) * 100) if tailored_skills else 50.0


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
