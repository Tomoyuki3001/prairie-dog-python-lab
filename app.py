import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()


def generate_audit_with_gemini(combined_text):
    system_instruction = """
    You are a Senior Technical Career Coach and Lead Recruiter at a FAANG company.
    Your goal is to audit a candidate's Resume against a Job Description (JD).

    CRITICAL REQUIREMENTS:
    1. MATCH SCORE: Provide a score from 0-100% based on technical alignment.
    2. GAP ANALYSIS: List the top 3-5 technical skills or tools mentioned in the JD that are missing from the resume.
    3. BULLET POINT SURGERY: Pick 2 weak bullet points from the resume and rewrite them to be "Action-Oriented" and "Result-Driven" (using the STAR method).
    4. CULTURAL FIT: Mention one specific 'soft skill' the JD emphasizes that the candidate should highlight.

    Tone: Professional, direct, and encouraging but honest.

    FORMATTING:
    - Use *bold* for the headers.
    - Use > blockquotes for the Pro-Tips.
    - Use `code blocks` for any technical terms or commands.
    """

    user_prompt = f"""
    Analyze the following text and identify the JD and Resume parts:\n\n{combined_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[user_prompt],
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )

    return response.text


def generate_interview_questions_with_gemini(combined_text):
    system_instruction = """
    You are a Senior Technical Career Coach and Lead Recruiter at a FAANG company.
    Your goal is to generate interview questions for a candidate based on a Job Description (JD).

    CRITICAL REQUIREMENTS:
    1. GENERATE 3-5 INTERVIEW QUESTIONS: Create a list of 3-5 interview questions that are relevant to the JD.
    2. CULTURAL FIT: Mention one specific 'soft skill' the JD emphasizes that the candidate should highlight.

    Tone: Professional, direct, and encouraging but honest.
    """

    user_prompt = f"""
    Generate 3 interview questions for the following JD:\n\n{combined_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[user_prompt],
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )

    return response.text
