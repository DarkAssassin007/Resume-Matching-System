"""
Add 10 sample resumes to the database
"""
from database import Database

# Initialize database
db = Database()

# Sample resumes with diverse skill sets
sample_resumes = [
    {
        "name": "John Smith",
        "filename": "john_smith_resume.pdf",
        "content": """
John Smith
Senior Software Engineer

SUMMARY:
Experienced software engineer with 8+ years in full-stack development. Expert in Python, Java, and cloud technologies.

SKILLS:
- Programming: Python, Java, JavaScript, C++
- Frameworks: Django, Flask, Spring Boot, React
- Cloud: AWS, Azure, Docker, Kubernetes
- Database: PostgreSQL, MySQL, MongoDB
- Tools: Git, Jenkins, JIRA, Agile/Scrum

EXPERIENCE:
Senior Software Engineer at Tech Corp (2019-Present)
- Developed microservices architecture using Python and Docker
- Implemented CI/CD pipelines with Jenkins
- Led team of 5 developers in agile environment

Software Engineer at StartupXYZ (2016-2019)
- Built RESTful APIs using Flask and Django
- Designed database schemas for high-traffic applications
- Worked with AWS services (EC2, S3, Lambda)

EDUCATION:
Bachelor of Science in Computer Science
University of Technology, 2016
"""
    },
    {
        "name": "Sarah Johnson",
        "filename": "sarah_johnson_resume.pdf",
        "content": """
Sarah Johnson
Data Scientist & ML Engineer

PROFESSIONAL SUMMARY:
Data scientist with 6+ years experience in machine learning, data analysis, and AI solutions.

TECHNICAL SKILLS:
- Languages: Python, R, SQL, Scala
- ML/AI: TensorFlow, PyTorch, Scikit-learn, Keras
- Big Data: Apache Spark, Hadoop, Hive
- Cloud: AWS SageMaker, Google Cloud AI
- Data Viz: Tableau, Power BI, Matplotlib, Seaborn

WORK HISTORY:
Lead Data Scientist - AI Solutions Inc (2021-Present)
- Developed predictive models with 95% accuracy using TensorFlow
- Built recommendation systems using collaborative filtering
- Processed large datasets with PySpark and Hadoop

Data Analyst - Data Corp (2018-2021)
- Created dashboards and reports using Tableau
- Performed statistical analysis using Python and R
- Optimized SQL queries for performance

EDUCATION:
Master of Science in Data Science
Tech University, 2018

CERTIFICATIONS:
- AWS Certified Machine Learning Specialty
- Google Professional Data Engineer
"""
    },
    {
        "name": "Michael Chen",
        "filename": "michael_chen_resume.pdf",
        "content": """
Michael Chen
Full Stack Developer

ABOUT ME:
Passionate full-stack developer specializing in modern web technologies and mobile development.

CORE COMPETENCIES:
- Frontend: React, Vue.js, Angular, TypeScript, HTML5, CSS3
- Backend: Node.js, Express, Python, Django
- Mobile: React Native, Flutter
- Database: MongoDB, PostgreSQL, Redis
- DevOps: Docker, Kubernetes, AWS, CI/CD

PROFESSIONAL EXPERIENCE:
Full Stack Developer - WebTech Solutions (2020-Present)
- Developed responsive web applications using React and Node.js
- Built RESTful APIs with Express.js and MongoDB
- Implemented authentication using JWT and OAuth

Junior Developer - StartupHub (2018-2020)
- Created mobile apps using React Native
- Worked with PostgreSQL and Redis for data management
- Participated in code reviews and agile sprints

EDUCATION:
BS in Software Engineering, 2018
State University

PROJECTS:
- E-commerce Platform: React, Node.js, MongoDB
- Task Management App: Vue.js, Express, PostgreSQL
"""
    },
    {
        "name": "Emily Rodriguez",
        "filename": "emily_rodriguez_resume.pdf",
        "content": """
Emily Rodriguez
DevOps Engineer

PROFILE:
DevOps engineer with expertise in cloud infrastructure, automation, and continuous integration/deployment.

SKILLS:
- Cloud Platforms: AWS, Azure, Google Cloud Platform
- Containers: Docker, Kubernetes, Helm
- IaC: Terraform, Ansible, CloudFormation
- CI/CD: Jenkins, GitLab CI, GitHub Actions
- Monitoring: Prometheus, Grafana, ELK Stack
- Scripting: Python, Bash, PowerShell

EMPLOYMENT:
Senior DevOps Engineer - CloudTech Inc (2020-Present)
- Managed AWS infrastructure using Terraform
- Implemented Kubernetes clusters for microservices
- Set up monitoring with Prometheus and Grafana
- Reduced deployment time by 70% with automated pipelines

DevOps Engineer - Tech Startup (2017-2020)
- Built CI/CD pipelines with Jenkins and Docker
- Automated server provisioning with Ansible
- Migrated legacy applications to cloud

EDUCATION:
Bachelor of Engineering in Information Technology, 2017

CERTIFICATIONS:
- AWS Certified Solutions Architect
- Certified Kubernetes Administrator (CKA)
- HashiCorp Certified: Terraform Associate
"""
    },
    {
        "name": "David Williams",
        "filename": "david_williams_resume.pdf",
        "content": """
David Williams
Backend Developer

OBJECTIVE:
Skilled backend developer focused on building scalable APIs and distributed systems.

TECHNICAL EXPERTISE:
- Languages: Java, Python, Go, Kotlin
- Frameworks: Spring Boot, Django, FastAPI
- Databases: MySQL, PostgreSQL, Cassandra, DynamoDB
- Messaging: Kafka, RabbitMQ, Redis
- Testing: JUnit, pytest, Mockito

EXPERIENCE:
Backend Developer - Enterprise Solutions (2019-Present)
- Designed RESTful APIs serving 1M+ requests/day
- Implemented event-driven architecture using Kafka
- Optimized database queries reducing response time by 60%

Software Developer - FinTech Corp (2017-2019)
- Developed payment processing systems using Java Spring
- Worked with microservices architecture
- Implemented security best practices

ACADEMIC BACKGROUND:
Computer Science Degree, 2017
Technical Institute

ACHIEVEMENTS:
- Reduced API latency by 40%
- Implemented caching strategies with Redis
- Led migration from monolith to microservices
"""
    },
    {
        "name": "Jessica Martinez",
        "filename": "jessica_martinez_resume.pdf",
        "content": """
Jessica Martinez
Frontend Developer & UI/UX Designer

SUMMARY:
Creative frontend developer with strong design skills and passion for user experience.

SKILLS:
- Frontend: React, Vue.js, Next.js, TypeScript
- Design: Figma, Adobe XD, Sketch, Photoshop
- Styling: CSS3, SASS, Tailwind CSS, Material-UI
- Animation: GSAP, Framer Motion
- Testing: Jest, React Testing Library, Cypress

WORK EXPERIENCE:
Senior Frontend Developer - Design Studio (2020-Present)
- Created responsive websites using React and Next.js
- Designed user interfaces in Figma
- Improved website performance by 50%
- Implemented accessibility standards (WCAG 2.1)

Frontend Developer - Creative Agency (2018-2020)
- Built interactive web applications with Vue.js
- Collaborated with designers on UI/UX
- Used Tailwind CSS for rapid prototyping

EDUCATION:
BA in Digital Media Design, 2018

PORTFOLIO:
www.jessicamartinez-portfolio.com
"""
    },
    {
        "name": "Robert Brown",
        "filename": "robert_brown_resume.pdf",
        "content": """
Robert Brown
Cloud Architect

PROFESSIONAL SUMMARY:
Certified cloud architect with 10+ years designing and implementing enterprise cloud solutions.

EXPERTISE:
- Cloud: AWS, Azure, Google Cloud, Multi-cloud
- Architecture: Microservices, Serverless, Event-driven
- Security: IAM, VPC, Security Groups, Encryption
- Networking: Load Balancers, CDN, VPN
- Cost Optimization: Reserved Instances, Auto-scaling

CAREER HISTORY:
Cloud Architect - Global Tech Corp (2021-Present)
- Designed multi-cloud architecture for enterprise clients
- Reduced cloud costs by 35% through optimization
- Led migration of 50+ applications to cloud
- Implemented disaster recovery solutions

Solutions Architect - Cloud Services Inc (2018-2021)
- Architected serverless applications on AWS Lambda
- Designed secure VPC configurations
- Conducted cloud readiness assessments

Senior Engineer - IT Consulting (2014-2018)
- Managed on-premise to cloud migrations
- Implemented hybrid cloud solutions

EDUCATION:
Master's in Information Systems, 2014

CERTIFICATIONS:
- AWS Certified Solutions Architect Professional
- Azure Solutions Architect Expert
- Google Cloud Professional Architect
"""
    },
    {
        "name": "Amanda Taylor",
        "filename": "amanda_taylor_resume.pdf",
        "content": """
Amanda Taylor
QA Automation Engineer

PROFILE:
Quality assurance engineer specializing in test automation and continuous testing.

TECHNICAL SKILLS:
- Automation: Selenium, Cypress, Playwright, Appium
- Languages: Python, JavaScript, Java
- Frameworks: pytest, TestNG, JUnit, Mocha
- CI/CD: Jenkins, CircleCI, GitHub Actions
- API Testing: Postman, REST Assured
- Performance: JMeter, LoadRunner

PROFESSIONAL BACKGROUND:
Senior QA Engineer - Software Solutions (2020-Present)
- Developed automated test suites using Selenium and Python
- Implemented CI/CD testing pipelines
- Reduced testing time by 80% through automation
- Performed API testing with Postman and REST Assured

QA Engineer - Tech Products Inc (2017-2020)
- Created test plans and test cases
- Performed manual and automated testing
- Worked in agile environment with daily standups

EDUCATION:
BS in Computer Engineering, 2017

TOOLS & TECHNOLOGIES:
Git, JIRA, TestRail, Selenium Grid, Docker
"""
    },
    {
        "name": "James Anderson",
        "filename": "james_anderson_resume.pdf",
        "content": """
James Anderson
Mobile Application Developer

ABOUT:
Mobile developer with 7+ years building iOS and Android applications.

SKILLS:
- Mobile: React Native, Flutter, Swift, Kotlin
- iOS: SwiftUI, UIKit, CoreData, XCode
- Android: Jetpack Compose, MVVM, Android Studio
- Backend: Firebase, Node.js, GraphQL
- Tools: Git, Fastlane, TestFlight

EXPERIENCE:
Lead Mobile Developer - AppTech Studios (2021-Present)
- Developed cross-platform apps using React Native
- Published 10+ apps on App Store and Google Play
- Implemented in-app purchases and push notifications
- Managed team of 3 mobile developers

Mobile Developer - Digital Agency (2018-2021)
- Built native iOS apps using Swift
- Created Android apps with Kotlin
- Integrated third-party APIs and SDKs

Junior Developer - Mobile Solutions (2016-2018)
- Developed mobile UIs and features
- Fixed bugs and improved app performance

EDUCATION:
Computer Science Degree, 2016

ACHIEVEMENTS:
- Apps downloaded 500K+ times
- 4.5+ star rating on app stores
- Featured app on Google Play
"""
    },
    {
        "name": "Lisa Thompson",
        "filename": "lisa_thompson_resume.pdf",
        "content": """
Lisa Thompson
Security Engineer

SUMMARY:
Cybersecurity professional with expertise in application security, penetration testing, and security architecture.

COMPETENCIES:
- Security: OWASP Top 10, Penetration Testing, Vulnerability Assessment
- Tools: Burp Suite, Metasploit, Nmap, Wireshark
- Compliance: GDPR, HIPAA, PCI-DSS, ISO 27001
- Cloud Security: AWS Security, Azure Security Center
- Programming: Python, Bash, PowerShell
- SIEM: Splunk, ELK Stack

WORK HISTORY:
Senior Security Engineer - CyberSec Corp (2020-Present)
- Conducted security assessments and penetration testing
- Implemented security best practices in CI/CD pipelines
- Developed security automation scripts using Python
- Responded to security incidents and breaches

Security Analyst - InfoSec Solutions (2017-2020)
- Performed vulnerability scanning and remediation
- Monitored security events using SIEM tools
- Conducted security training for development teams

EDUCATION:
MS in Cybersecurity, 2017
Bachelor's in Information Technology, 2015

CERTIFICATIONS:
- Certified Ethical Hacker (CEH)
- Offensive Security Certified Professional (OSCP)
- CISSP (Certified Information Systems Security Professional)
- CompTIA Security+
"""
    }
]

def add_resumes():
    """Add sample resumes to database"""
    print("\n" + "="*60)
    print("ADDING SAMPLE RESUMES TO DATABASE")
    print("="*60 + "\n")
    
    added_count = 0
    
    for resume in sample_resumes:
        try:
            resume_id = db.add_resume(
                candidate_name=resume['name'],
                file_name=resume['filename'],
                file_content=resume['content']
            )
            print(f"✓ Added: {resume['name']} (ID: {resume_id})")
            added_count += 1
        except Exception as e:
            print(f"✗ Failed to add {resume['name']}: {str(e)}")
    
    print("\n" + "="*60)
    print(f"COMPLETED: {added_count}/{len(sample_resumes)} resumes added")
    print("="*60 + "\n")
    
    # Display summary
    all_resumes = db.get_all_resumes()
    print(f"Total resumes in database: {len(all_resumes)}\n")
    
    print("Resume List:")
    for idx, resume in enumerate(all_resumes, 1):
        print(f"{idx}. {resume['candidate_name']} ({resume['file_name']})")

if __name__ == "__main__":
    add_resumes()
