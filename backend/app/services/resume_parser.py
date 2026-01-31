from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from ..models.resume import Resume
from ..core.llm_router import invoke_with_fallback, get_current_provider


prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are a precise resume parser that extracts structured data from raw resume text.
From the raw text (often noisy from PDF extraction), extract structured data into the Resume schema.

Rules:
- Clean typos, fix formatting (e.g., "AngualrJS" → "AngularJS", "RESTful" → "RESTful").
- Categorize skills logically (e.g., "Programming Languages", "Frameworks", "Cloud/DevOps", "Soft Skills").
- Infer education level: assign nfq_level 10 for PhD, 9 for Master's, 8 for Bachelor's.
- Keep bullets/achievements as-is but clean language.
- Output ONLY valid JSON matching the schema — no explanations.
"""),
    ("human", "Raw resume text:\n{raw_text}\n\nParse into structured Resume."),
])


def parse_resume(raw_text: str) -> Resume:
    """
    Parse resume using multi-LLM router with automatic fallback.
    """
    logger.info(f"Parsing resume with {get_current_provider()}...")

    result = invoke_with_fallback(
        prompt_template=prompt,
        input_data={"raw_text": raw_text},
        output_schema=Resume,
        temperature=0.1,
    )

    return result

# if __name__ == "__main__":
#     raw_resume_text = """YASH MODI
# +353 (89) 492-0341 ⋄ Cork, Ireland ⋄ yashmodi.ie@gmail.com ⋄ linkedin.com/in/yshmodi/
# PROFESSIONAL SUMMARY
# Graduate AI Engineer with hands-on experience in NLP, Deep Learning, Generative AI, and cloud-based deployment.
# Skilled in building and scaling AI models for automation, data-driven insights, and user experience enhancement.
# Experienced with LLM APIs (e.g., GPT) and MLOps concepts, with additional background in full-stack development
# for end-to-end product delivery.
# EDUCATION
# Master of Science in Artificial Intelligence, Munster Technological University 2025
# Relevant Coursework: Machine Learning & Deep Learning, Natural Language Processing (NLP), Decision Analytics,
# Big Data Processing, Software Agility.
# Bachelor of Technology in Information Technology, UKA Tarsadia University 2020 - 2024
# Relevant Coursework: Programming, Data Structures and Algorithms, Database Management Systems, Computer
# Networks, Operating Systems, Software Engineering.
# SKILLS
# Technical Skills Soft Skills AI Python, JavaScript, Spring Boot, AngularJS, Git, SQL, REST APIs, AWS, GCP
# Team Collaboration, Communication, Time Management, Critical Thinking, Leadership
# Machine Learning, NLP, LLMs (GPT APIs, Hugging Face), LangChain, Prompt Engineering
# EXPERIENCE
# Software Engineer Intern Yosa Technology Solutions Pvt. Ltd. Jan 2024 – Aug 2024
# Surat, IN
# • Developed and deployed a cloud-based HRMS portal using AngularJS and Spring Boot, resulting in a 40%
# improvement in HR process efficiency.
# • Led full-stack development for employee attendance and leave management modules, enhancing data accuracy
# and reducing manual HR workload by 60%.
# • Implemented RESTful APIs, integrated Firebase authentication, and optimized backend logic for real-time
# tracking and filtering of attendance logs.
# • Gained hands-on experience with DevOps concepts, server operations, and containerized deployment using
# Apache Tomcat, resulting in faster and more reliable application deployment.
# React Developer Intern Code Alchemy Pvt Ltd May 2023 – Jun 2023
# Surat, IN
# • Developed interactive web interfaces using ReactJS and Tailwind CSS, resulting in improved UI responsiveness
# and 30% faster page load times.
# • Collaborated on full-stack projects integrating Firebase for authentication and real-time data storage, enhancing
# backend scalability and performance.
# • Designed and developed a personalized vector art generator using ReactJS and Tailwind CSS, showcasing inter-
# active UI development, state management, and real-time rendering of SVG components.
# PROJECTS
# Master of Science in Artificial Intelligence, Munster Technological University May 2025
# Thesis: “Co-evolutionary Level Generation and Agent Development: A Hybrid GAN-RL Architecture
# for Ensuring Playable Game Content”
# Explored the integration of Generative Adversarial Networks (GANs) and Reinforcement Learning (RL) agents to
# create dynamic, procedurally generated game environments. Developed a conceptual co-evolutionary framework and
# implemented key components using TOAD-GAN and UC Berkeley’s Pac-Man AI project.
# Sentiment and Hate Analysis of Mpox Instagram Dataset Developed an NLP-based tool using Python,
# TensorFlow, and Scikit-learn to analyze sentiment and detect hate speech in Instagram posts during the Mpox
# outbreak. Achieved 85% accuracy in classifying user-generated content, providing actionable insights into public
# health responses. (Link)
# Streamlined HR Management: Cloud-Based HRMS Portal Built a cloud-based HR portal using AngularJS,
# Spring Boot, and AWS, enabling real-time employee attendance tracking and leave management. Improved HR
# process efficiency by 40% and reduced manual workload by 60% through optimized RESTful APIs and Firebase
# integration.
# Personalized Alpaca Vector Art Generator Created an interactive web app with ReactJS and Tailwind CSS
# for designing and downloading high-resolution alpaca vector art avatars. Enhanced user engagement with real-time
# customization, achieving 30% faster page load times and seamless SVG rendering. (Link)
# CERTIFICATIONS & TRAINING
# • Data Science Foundations – Level 1 (IBM)
# Gained hands-on experience with data exploration, visualization, and statistical analysis using Python and
# Jupyter Notebooks.
# Link
# • Introduction to Generative AI (Google Cloud Skills Boost)
# Learned foundational concepts of generative AI including text generation, image creation, and code synthesis.
# Link
# LEADERSHIP & VOLUNTEERING
# • Volunteered with the National Service Scheme (NSS) during undergraduate studies; participated in community
# outreach, environmental clean-up campaigns, and public health initiatives.
# • Certified Yoga Trainer; led group sessions and workshops promoting mental wellness, mindfulness, and physical
# health."""

# try:
#     parsed = parse_resume(raw_resume_text)
#     print("Parsed Resume (cleaned):")
#     print(parsed.model_dump_json(indent=2))

#     print("\nVisa Inference:")
#     print(parsed.visa_notes)
# except Exception as e:
#     print("Extraction failed:", e)
