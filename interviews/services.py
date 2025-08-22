import google.generativeai as genai
from django.conf import settings
from typing import List, Dict
import re
import json


class AIService:
    """Service for AI-powered question generation and scoring"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # self.model = genai.GenerativeModel('gemini-pro')
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        # self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_questions_from_jd(self, job_description: str, num_questions: int = 6) -> List[Dict]:
        """Generate interview questions based on job description"""
        
        prompt = f"""
        Based on the following job description, generate {num_questions} relevant interview questions.
        
        Job Description:
        {job_description}
        
        Please generate questions that:
        1. Test technical skills mentioned in the JD
        2. Assess problem-solving abilities
        3. Evaluate communication skills
        4. Check cultural fit
        5. Verify experience claims
        
        Return the response as a JSON array with this format:
        [
            {{
                "question": "Your question here",
                "difficulty": "easy|medium|hard",
                "expected_keywords": ["keyword1", "keyword2"],
                "category": "technical|behavioral|experience"
            }}
        ]
        """
        
        try:
            system_prompt = "You are an expert HR interviewer. Generate relevant, professional interview questions."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1500,
                )
            )
            
            content = response.text
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                questions_data = json.loads(json_match.group())
                return questions_data
            else:
                # Fallback questions if AI fails
                return self._get_fallback_questions()
                
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._get_fallback_questions()
    
    def score_answer(self, question: str, answer_transcript: str, expected_keywords: List[str]) -> Dict:
        """Score an interview answer using AI"""
        
        prompt = f"""
        Question: {question}
        Answer: {answer_transcript}
        Expected Keywords: {', '.join(expected_keywords)}
        
        Please score this interview answer on a scale of 0-10 and provide feedback.
        Consider:
        1. Relevance to the question (0-3 points)
        2. Technical accuracy (0-3 points)
        3. Communication clarity (0-2 points)
        4. Use of expected keywords (0-2 points)
        
        Return response as JSON:
        {{
            "score": 7.5,
            "feedback": "Detailed feedback here",
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"]
        }}
        """
        
        try:
            system_prompt = "You are an expert technical interviewer. Provide fair and constructive scoring."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )
            
            content = response.text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"score": 5.0, "feedback": "Unable to process answer", "strengths": [], "improvements": []}
                
        except Exception as e:
            print(f"Error scoring answer: {e}")
            return {"score": 5.0, "feedback": "Scoring unavailable", "strengths": [], "improvements": []}
    
    def generate_final_recommendation(self, interview_data: Dict) -> str:
        """Generate final hiring recommendation based on interview performance"""
        
        prompt = f"""
        Based on the following interview performance data, provide a hiring recommendation:
        
        Candidate: {interview_data.get('candidate_name', 'Unknown')}
        Total Score: {interview_data.get('total_score', 0)}/10
        Individual Scores: {interview_data.get('individual_scores', [])}
        
        Questions and Answers:
        {interview_data.get('qa_summary', '')}
        
        Please provide:
        1. Overall recommendation (Hire/Maybe/Reject)
        2. Key strengths
        3. Areas of concern
        4. Suggested next steps
        
        Keep it professional and constructive.
        """
        
        try:
            system_prompt = "You are an experienced hiring manager providing final interview recommendations."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=800,
                )
            )
            
            return response.text
            
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return "Unable to generate recommendation due to technical issues."
    
    def _get_fallback_questions(self) -> List[Dict]:
        """Fallback questions when AI generation fails"""
        return [
            {
                "question": "Tell me about your experience with the technologies mentioned in this role.",
                "difficulty": "medium",
                "expected_keywords": ["experience", "technology", "projects"],
                "category": "technical"
            },
            {
                "question": "Describe a challenging problem you solved in your previous role.",
                "difficulty": "medium", 
                "expected_keywords": ["problem", "solution", "challenge"],
                "category": "behavioral"
            },
            {
                "question": "How do you stay updated with the latest industry trends?",
                "difficulty": "easy",
                "expected_keywords": ["learning", "trends", "development"],
                "category": "behavioral"
            },
            {
                "question": "Walk me through your approach to debugging a complex issue.",
                "difficulty": "hard",
                "expected_keywords": ["debugging", "systematic", "tools"],
                "category": "technical"
            },
            {
                "question": "How do you handle working under tight deadlines?",
                "difficulty": "medium",
                "expected_keywords": ["deadlines", "pressure", "prioritization"],
                "category": "behavioral"
            },
            {
                "question": "What interests you most about this position and our company?",
                "difficulty": "easy",
                "expected_keywords": ["interest", "company", "role"],
                "category": "behavioral"
            }
        ]
