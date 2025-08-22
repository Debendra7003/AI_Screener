import PyPDF2
from docx import Document
import re
from typing import Dict, List
import json


class ResumeParserService:
    """Service for parsing PDF and DOCX resume files"""
    
    def parse_resume(self, file_path: str, file_type: str) -> Dict:
        """Parse resume file and extract structured data"""
        
        try:
            if file_type.lower() == 'pdf':
                text = self._extract_pdf_text(file_path)
            elif file_type.lower() in ['docx', 'doc']:
                text = self._extract_docx_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            return self._parse_resume_text(text)
            
        except Exception as e:
            print(f"Error parsing resume: {e}")
            return self._get_empty_resume_data()
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
        return text
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
        return text
    
    def _parse_resume_text(self, text: str) -> Dict:
        """Parse resume text and extract structured information"""
        
        parsed_data = {
            'skills': self._extract_skills(text),
            'experience_years': self._extract_experience_years(text),
            'education': self._extract_education(text),
            'work_experience': self._extract_work_experience(text),
            'summary': self._extract_summary(text)
        }
        
        return parsed_data
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        skills = []
        
        # Common technical skills patterns
        skill_patterns = [
            r'(?i)skills?[:\s]*([^\n]+)',
            r'(?i)technologies?[:\s]*([^\n]+)',
            r'(?i)programming languages?[:\s]*([^\n]+)',
            r'(?i)technical skills?[:\s]*([^\n]+)'
        ]
        
        # Common skills to look for
        common_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'aws', 'docker', 'kubernetes', 'git', 'agile', 'scrum', 'html', 'css',
            'angular', 'vue.js', 'django', 'flask', 'spring', 'mysql', 'postgresql',
            'redis', 'elasticsearch', 'jenkins', 'ci/cd', 'microservices', 'rest api'
        ]
        
        text_lower = text.lower()
        
        # Extract from skill sections
        for pattern in skill_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                # Split by common delimiters
                skill_items = re.split(r'[,;|•\n]', match)
                for item in skill_items:
                    item = item.strip()
                    if len(item) > 1 and len(item) < 30:
                        skills.append(item)
        
        # Look for common skills in the entire text
        for skill in common_skills:
            if skill in text_lower:
                skills.append(skill.title())
        
        # Remove duplicates and return
        return list(set(skills))
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience from resume"""
        
        # Patterns to find experience mentions
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience[:\s]*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*in\s*(?:software|development|programming)',
        ]
        
        years = []
        text_lower = text.lower()
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years.append(int(match))
                except ValueError:
                    continue
        
        # Return the maximum years found, or 0 if none
        return max(years) if years else 0
    
    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        
        # Look for degree patterns
        degree_patterns = [
            r'(?i)(bachelor|master|phd|doctorate|b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?)\s*(?:of\s*)?(?:science\s*)?(?:in\s*)?([^\n,]+)',
            r'(?i)(degree)\s*in\s*([^\n,]+)',
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                education.append({
                    'degree': match[0].strip(),
                    'field': match[1].strip() if len(match) > 1 else '',
                    'institution': ''  # Could be enhanced to extract institution
                })
        
        return education
    
    def _extract_work_experience(self, text: str) -> List[Dict]:
        """Extract work experience information"""
        experience = []
        
        # Look for job title patterns
        title_patterns = [
            r'(?i)(software engineer|developer|programmer|analyst|manager|lead|senior|junior)\s*[^\n]*',
            r'(?i)(intern|internship)\s*[^\n]*',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join(match)
                
                experience.append({
                    'title': match.strip(),
                    'company': '',  # Could be enhanced
                    'duration': '',  # Could be enhanced
                    'description': ''
                })
        
        return experience[:5]  # Limit to 5 entries
    
    def _extract_summary(self, text: str) -> str:
        """Extract or generate a summary from resume"""
        
        # Look for summary/objective sections
        summary_patterns = [
            r'(?i)(?:summary|objective|profile)[:\s]*([^\n]+(?:\n[^\n]+)*?)(?:\n\s*\n|\n[A-Z])',
            r'(?i)(?:about me|personal statement)[:\s]*([^\n]+(?:\n[^\n]+)*?)(?:\n\s*\n|\n[A-Z])',
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                summary = match.group(1).strip()
                if len(summary) > 50:  # Only return if substantial
                    return summary
        
        # If no summary found, create a basic one from first few lines
        lines = text.split('\n')[:5]
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if non_empty_lines:
            return ' '.join(non_empty_lines[:2])
        
        return "No summary available"
    
    def _get_empty_resume_data(self) -> Dict:
        """Return empty resume data structure"""
        return {
            'skills': [],
            'experience_years': 0,
            'education': [],
            'work_experience': [],
            'summary': ''
        }
