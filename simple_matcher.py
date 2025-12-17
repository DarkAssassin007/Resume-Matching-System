"""
Simplified Resume Matching (No Spark Required)
Uses TF-IDF with scikit-learn instead of PySpark
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict

class SimpleResumeMatchingProcessor:
    """Simple matching without Spark dependency"""
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text data"""
        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_skills(self, text: str, skill_list: List[str]) -> List[str]:
        """Extract matched skills from text"""
        text_lower = text.lower()
        matched_skills = []
        for skill in skill_list:
            if skill.lower() in text_lower:
                matched_skills.append(skill)
        return matched_skills
    
    def match_resumes_to_job(self, resumes: List[Dict], job_description: Dict) -> List[Dict]:
        """
        Match resumes to job using scikit-learn TF-IDF
        
        Args:
            resumes: List of resume dictionaries
            job_description: Job description dictionary
        
        Returns:
            List of matching results sorted by score
        """
        if not resumes:
            return []
        
        # Parse required skills
        required_skills = [s.strip() for s in job_description['required_skills'].split(',')]
        
        # Prepare documents
        documents = []
        resume_data = []
        
        for resume in resumes:
            preprocessed = self.preprocess_text(resume['file_content'])
            documents.append(preprocessed)
            resume_data.append({
                'resume_id': resume['id'],
                'candidate_name': resume['candidate_name'],
                'original_content': resume['file_content']
            })
        
        # Add job description
        job_content = self.preprocess_text(
            job_description['description'] + ' ' + job_description['required_skills']
        )
        documents.append(job_content)
        
        # Calculate TF-IDF
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Get job vector (last document)
        job_vector = tfidf_matrix[-1]
        
        # Calculate similarities
        matching_results = []
        for idx, resume in enumerate(resume_data):
            resume_vector = tfidf_matrix[idx]
            
            # Cosine similarity
            similarity = cosine_similarity(resume_vector, job_vector)[0][0]
            
            # Extract matched skills
            matched_skills = self.extract_skills(resume['original_content'], required_skills)
            
            # Calculate weighted score (70% TF-IDF + 30% skills)
            skill_match_score = len(matched_skills) / len(required_skills) if required_skills else 0
            final_score = (similarity * 0.7) + (skill_match_score * 0.3)
            
            matching_results.append({
                'resume_id': resume['resume_id'],
                'candidate_name': resume['candidate_name'],
                'matching_score': round(final_score * 100, 2),
                'tfidf_score': round(similarity * 100, 2),
                'skill_match_score': round(skill_match_score * 100, 2),
                'matched_skills': matched_skills,
                'matched_skills_str': ', '.join(matched_skills) if matched_skills else 'None'
            })
        
        # Sort by matching score
        matching_results.sort(key=lambda x: x['matching_score'], reverse=True)
        
        return matching_results

def get_simple_processor():
    """Get simple processor instance"""
    return SimpleResumeMatchingProcessor()
