"""
Add sample job descriptions to the database
"""
from database import Database
from config import Config

# Initialize database
db = Database()

# Sample job descriptions
sample_jobs = [
    {
        "title": "Senior Python Developer",
        "description": """
We are seeking an experienced Python developer to join our backend team. 
The ideal candidate will have strong experience in web development, cloud technologies, 
and machine learning. You will be responsible for building scalable applications and APIs.

Responsibilities:
- Design and develop RESTful APIs using Flask or Django
- Work with AWS services for cloud deployment
- Implement CI/CD pipelines and DevOps practices
- Collaborate with frontend developers and data scientists
- Write clean, maintainable, and well-documented code
        """,
        "skills": "Python, Django, Flask, AWS, Docker, PostgreSQL, REST API, Git, Machine Learning"
    },
    {
        "title": "Full Stack JavaScript Developer",
        "description": """
Looking for a talented full-stack developer proficient in modern JavaScript frameworks.
You will work on both frontend and backend systems, creating responsive web applications.

Requirements:
- Build user interfaces with React or Vue.js
- Develop backend services with Node.js and Express
- Design and optimize database schemas
- Implement authentication and authorization
- Work in an agile development environment
        """,
        "skills": "JavaScript, React, Vue.js, Node.js, Express, MongoDB, TypeScript, HTML5, CSS3, Git"
    },
    {
        "title": "DevOps Engineer",
        "description": """
We need a DevOps engineer to manage our cloud infrastructure and automate deployment processes.
Experience with containerization and orchestration is essential.

Key Responsibilities:
- Manage AWS/Azure infrastructure using Infrastructure as Code
- Implement and maintain Kubernetes clusters
- Build CI/CD pipelines with Jenkins or GitLab
- Monitor system performance and troubleshoot issues
- Ensure security best practices
        """,
        "skills": "AWS, Azure, Kubernetes, Docker, Terraform, Jenkins, Python, Bash, Monitoring, CI/CD"
    },
    {
        "title": "Data Scientist",
        "description": """
Join our AI team as a data scientist to develop machine learning models and analyze large datasets.
You will work on exciting projects involving predictive analytics and recommendation systems.

What you'll do:
- Build and train ML models using Python
- Process big data with Apache Spark
- Create data visualizations and dashboards
- Deploy models to production environments
- Collaborate with engineering teams
        """,
        "skills": "Python, Machine Learning, TensorFlow, PyTorch, Spark, SQL, Pandas, Scikit-learn, AWS, Statistics"
    },
    {
        "title": "Mobile App Developer",
        "description": """
Seeking a mobile developer to create cross-platform applications for iOS and Android.
Experience with React Native or Flutter is highly valued.

Duties:
- Develop mobile applications using React Native or Flutter
- Integrate with RESTful APIs and third-party services
- Optimize app performance and user experience
- Test and debug applications
- Publish apps to App Store and Google Play
        """,
        "skills": "React Native, Flutter, Swift, Kotlin, iOS, Android, JavaScript, Firebase, Git, Mobile Development"
    }
]

def add_jobs():
    """Add sample job descriptions to database"""
    print("\n" + "="*60)
    print("ADDING SAMPLE JOB DESCRIPTIONS TO DATABASE")
    print("="*60 + "\n")
    
    added_count = 0
    
    for job in sample_jobs:
        try:
            job_id = db.add_job_description(
                job_title=job['title'],
                description=job['description'],
                required_skills=job['skills']
            )
            print(f"✓ Added: {job['title']} (ID: {job_id})")
            added_count += 1
        except Exception as e:
            print(f"✗ Failed to add {job['title']}: {str(e)}")
    
    print("\n" + "="*60)
    print(f"COMPLETED: {added_count}/{len(sample_jobs)} jobs added")
    print("="*60 + "\n")
    
    # Display summary
    all_jobs = db.get_all_job_descriptions()
    print(f"Total jobs in database: {len(all_jobs)}\n")
    
    print("Job List:")
    for idx, job in enumerate(all_jobs, 1):
        skills_preview = job['required_skills'][:50] + "..." if len(job['required_skills']) > 50 else job['required_skills']
        print(f"{idx}. {job['job_title']}")
        print(f"   Skills: {skills_preview}\n")

if __name__ == "__main__":
    add_jobs()
