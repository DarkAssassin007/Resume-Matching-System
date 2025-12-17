"""
PySpark Resume Matching Processor
Uses TF-IDF and cosine similarity to match resumes with job descriptions
"""

from pyspark.sql import SparkSession
from pyspark.ml.feature import HashingTF, IDF, Tokenizer, StopWordsRemover
from pyspark.sql.functions import col, udf, explode, array, lit
from pyspark.sql.types import FloatType, StringType, ArrayType
import numpy as np
from typing import List, Dict, Tuple
import re
import sys

class ResumeMatchingProcessor:
    def __init__(self, app_name: str = "ResumeMatchingSystem"):
        """Initialize Spark session with Web UI enabled"""
        try:
            # Create a minimal Spark session first to test compatibility
            print("Initializing minimal Spark session...")
            
            # Try multiple initialization approaches for compatibility
            try:
                # Approach 1: Simple initialization
                self.spark = SparkSession.builder \
                    .appName(app_name) \
                    .master("local[2]") \
                    .getOrCreate()
            except Exception as init_error:
                print(f"First initialization attempt failed: {init_error}")
                try:
                    # Approach 2: With compatibility configs
                    self.spark = SparkSession.builder \
                        .appName(app_name) \
                        .master("local[2]") \
                        .config("spark.sql.adaptive.enabled", "false") \
                        .config("spark.sql.execution.arrow.pyspark.enabled", "false") \
                        .getOrCreate()
                except Exception as init_error2:
                    print(f"Second initialization attempt failed: {init_error2}")
                    # Approach 3: Minimal initialization
                    self.spark = SparkSession.builder \
                        .appName(app_name) \
                        .master("local") \
                        .config("spark.driver.host", "localhost") \
                        .config("spark.driver.bindAddress", "127.0.0.1") \
                        .getOrCreate()
            
            # Set log level to reduce verbosity
            self.spark.sparkContext.setLogLevel("WARN")
            
            print(f"Spark Version: {self.spark.version}")
            print("Spark session initialized successfully!")
        except Exception as e:
            print(f"Failed to initialize Spark session: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Spark initialization failed: {e}")
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text data"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and digits
        text = re.sub(r'[^a-z\s]', ' ', text)
        # Remove extra whitespace
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
    
    def calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2:
            return 0.0
        
        vec1_array = np.array(vec1)
        vec2_array = np.array(vec2)
        
        dot_product = np.dot(vec1_array, vec2_array)
        norm1 = np.linalg.norm(vec1_array)
        norm2 = np.linalg.norm(vec2_array)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def match_resumes_to_job(self, resumes: List[Dict], job_description: Dict) -> List[Dict]:
        """
        Match multiple resumes to a single job description using TF-IDF
        
        Args:
            resumes: List of resume dictionaries with 'id', 'candidate_name', 'file_content'
            job_description: Dictionary with 'id', 'job_title', 'description', 'required_skills'
        
        Returns:
            List of matching results sorted by score
        """
        try:
            if not resumes:
                return []
            
            # Parse required skills
            required_skills = [s.strip() for s in job_description['required_skills'].split(',')]
            
            # Prepare data for Spark DataFrame
            resume_data = []
            for resume in resumes:
                preprocessed_content = self.preprocess_text(resume['file_content'])
                resume_data.append({
                    'resume_id': resume['id'],
                    'candidate_name': resume['candidate_name'],
                    'content': preprocessed_content,
                    'original_content': resume['file_content']
                })
            
            # Add job description to the data
            job_content = self.preprocess_text(
                job_description['description'] + ' ' + job_description['required_skills']
            )
            
            all_data = resume_data + [{
                'resume_id': -1,  # Special ID for job description
                'candidate_name': 'JOB_DESCRIPTION',
                'content': job_content,
                'original_content': job_description['description']
            }]
            
            # Create Spark DataFrame
            df = self.spark.createDataFrame(all_data)
            
            # Tokenization
            tokenizer = Tokenizer(inputCol="content", outputCol="words")
            words_df = tokenizer.transform(df)
            
            # Remove stop words
            remover = StopWordsRemover(inputCol="words", outputCol="filtered_words")
            filtered_df = remover.transform(words_df)
            
            # TF (Term Frequency)
            hashing_tf = HashingTF(inputCol="filtered_words", outputCol="raw_features", numFeatures=1000)
            tf_df = hashing_tf.transform(filtered_df)
            
            # IDF (Inverse Document Frequency)
            idf = IDF(inputCol="raw_features", outputCol="features")
            idf_model = idf.fit(tf_df)
            tfidf_df = idf_model.transform(tf_df)
            
            # Collect results
            results = tfidf_df.select('resume_id', 'candidate_name', 'features', 'original_content').collect()
            
            # Find job description vector
            job_vector = None
            for row in results:
                if row['resume_id'] == -1:
                    job_vector = row['features'].toArray().tolist()
                    break
            
            if job_vector is None:
                return []
            
            # Calculate similarity scores
            matching_results = []
            for row in results:
                if row['resume_id'] == -1:  # Skip job description itself
                    continue
                
                resume_vector = row['features'].toArray().tolist()
                similarity_score = self.calculate_cosine_similarity(resume_vector, job_vector)
                
                # Extract matched skills
                matched_skills = self.extract_skills(row['original_content'], required_skills)
                
                # Calculate weighted score (70% TF-IDF similarity + 30% skill match)
                skill_match_score = len(matched_skills) / len(required_skills) if required_skills else 0
                final_score = (similarity_score * 0.7) + (skill_match_score * 0.3)
                
                matching_results.append({
                    'resume_id': row['resume_id'],
                    'candidate_name': row['candidate_name'],
                    'matching_score': round(final_score * 100, 2),  # Convert to percentage
                    'tfidf_score': round(similarity_score * 100, 2),
                    'skill_match_score': round(skill_match_score * 100, 2),
                    'matched_skills': matched_skills,
                    'matched_skills_str': ', '.join(matched_skills) if matched_skills else 'None'
                })
            
            # Sort by matching score (descending)
            matching_results.sort(key=lambda x: x['matching_score'], reverse=True)
            
            return matching_results
            
        except Exception as e:
            print(f"Error in Spark matching: {e}")
            raise RuntimeError(f"Spark matching failed: {e}")
    
    def get_spark_ui_url(self) -> str:
        """Get Spark Web UI URL"""
        return "http://localhost:4040"
    
    def stop(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            print("Spark session stopped")

# Singleton instance
_processor_instance = None
_simple_processor_instance = None

# Import simple matcher for fallback
try:
    from simple_matcher import get_simple_processor
    SIMPLE_MATCHER_AVAILABLE = True
except ImportError:
    SIMPLE_MATCHER_AVAILABLE = False

def get_processor():
    """Get or create processor instance (fallback to simple matcher if Spark fails)"""
    global _processor_instance, _simple_processor_instance
    
    # Try to get Spark processor first
    if _processor_instance is None:
        try:
            _processor_instance = ResumeMatchingProcessor()
            print("Using Spark-based processor")
            return _processor_instance
        except Exception as e:
            print(f"Failed to create Spark processor: {e}")
            print("Falling back to simple matcher...")
    elif _processor_instance is not None:
        print("Using existing Spark-based processor")
        return _processor_instance
    
    # Fall back to simple matcher
    if _simple_processor_instance is None:
        if SIMPLE_MATCHER_AVAILABLE:
            try:
                _simple_processor_instance = get_simple_processor()
                print("Using simple matcher as fallback")
                return _simple_processor_instance
            except Exception as e:
                print(f"Failed to create simple processor: {e}")
                raise RuntimeError("Could not initialize either Spark or simple processor")
        else:
            raise RuntimeError("Could not initialize Spark processor and simple matcher not available")
    else:
        print("Using existing simple processor")
        return _simple_processor_instance

def stop_processor():
    """Stop the processor instance"""
    global _processor_instance
    if _processor_instance:
        try:
            _processor_instance.stop()
        except Exception as e:
            print(f"Error stopping processor: {e}")
        _processor_instance = None