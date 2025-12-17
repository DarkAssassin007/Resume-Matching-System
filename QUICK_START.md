# Quick Start Guide - Resume Matching System

## ⚡ Fast Setup (5 Minutes)

### 1. Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install -r requirements.txt
```

### 2. Verify Java Installation

Spark requires Java. Check if installed:

```powershell
java -version
```

If not installed:
- Download Java JDK 8 or 11 from: https://www.oracle.com/java/technologies/downloads/
- Or use OpenJDK: https://adoptium.net/

### 3. Start the Application

```powershell
python app.py
```

You should see:
```
============================================================
Resume Matching System
============================================================
Web Application: http://localhost:5000
Spark Web UI: http://localhost:4040
============================================================
```

### 4. Access the Application

Open your browser and go to:
- **Main Application**: http://localhost:5000
- **Spark Monitoring**: http://localhost:4040 (available after first job runs)

## 🎯 Quick Demo

### Step 1: Upload Sample Resumes

1. Go to **Upload Resume** page
2. Upload the sample resumes from `data/` folder:
   - `sample_resume_1.txt` (John Doe - Senior Software Engineer)
   - `sample_resume_2.txt` (Sarah Johnson - Data Scientist)
   - `sample_resume_3.txt` (Michael Chen - Full Stack Developer)

### Step 2: Create a Job Description

1. Go to **Create Job** page
2. Fill in the form:
   - **Job Title**: Senior Python Developer
   - **Description**: 
     ```
     We are seeking an experienced Python developer to join our team. 
     The ideal candidate will have strong experience in web development, 
     cloud technologies, and machine learning. You will be responsible 
     for building scalable applications and APIs.
     ```
   - **Required Skills**: Python, Django, Flask, AWS, Docker, Machine Learning

3. Click **Create Job Description**

### Step 3: Run Matching

1. In the job list, click **Match Resumes**
2. Wait a few seconds for processing
3. View the ranked results!

### Step 4: Monitor Spark Jobs

1. Click **Spark Web UI** in the navigation
2. See the TF-IDF job execution details
3. Explore stages, tasks, and performance metrics

## 📊 Expected Results

For the sample data above, you should see:
1. **John Doe**: ~75-85% match (has Python, AWS, Docker, ML experience)
2. **Sarah Johnson**: ~70-80% match (strong ML and Python, some AWS)
3. **Michael Chen**: ~50-60% match (has Python, but focused on frontend)

## 🔧 Troubleshooting

### Port Already in Use

If port 5000 or 4040 is already in use:

**Change Flask port** in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
```

**Change Spark UI port** in `spark_processor.py`:
```python
.config("spark.ui.port", "4041")
```

### Python Package Errors

Update pip and reinstall:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Java Not Found

Set JAVA_HOME environment variable:
```powershell
$env:JAVA_HOME = "C:\Program Files\Java\jdk-11"
```

Replace path with your Java installation directory.

## 📝 Next Steps

1. **Try Different Job Descriptions**: Create jobs for different roles
2. **Upload Real Resumes**: Test with actual resume files (PDF/DOCX)
3. **Experiment with Skills**: See how skill matching affects scores
4. **Monitor Performance**: Use Spark UI to understand processing
5. **Customize Scoring**: Modify weights in `spark_processor.py`

## 🎓 Understanding the System

### File Flow
```
Upload Resume → Extract Text → Save to SQLite
Create Job → Save to Database
Match Resumes → Load from DB → PySpark Processing → TF-IDF → Results
```

### Matching Algorithm
1. Text preprocessing (lowercase, remove special chars)
2. Tokenization (split into words)
3. Stop words removal
4. TF-IDF vectorization
5. Cosine similarity calculation
6. Skill matching
7. Weighted scoring (70% TF-IDF + 30% skills)

### Database Tables
- `resumes`: Stores candidate information and resume text
- `job_descriptions`: Stores job details and required skills
- `matching_results`: Stores computed matching scores

## 🚀 Advanced Usage

### Batch Processing

Upload multiple resumes at once using the API:

```python
import requests

files = ['resume1.pdf', 'resume2.pdf', 'resume3.pdf']
for file in files:
    with open(file, 'rb') as f:
        requests.post('http://localhost:5000/upload_resume', 
                     files={'resume_file': f},
                     data={'candidate_name': file.split('.')[0]})
```

### Custom TF-IDF Parameters

Edit `spark_processor.py` to customize:

```python
# Change number of features
hashing_tf = HashingTF(inputCol="filtered_words", 
                       outputCol="raw_features", 
                       numFeatures=2000)  # Default: 1000
```

### Export Results

Results can be accessed via API:

```python
import requests
import pandas as pd

response = requests.get('http://localhost:5000/api/results/1')
results = response.json()
df = pd.DataFrame(results)
df.to_csv('matching_results.csv', index=False)
```

## 📧 Support

For issues or questions:
1. Check the main README.md
2. Review Spark logs in console
3. Check Spark Web UI for job failures
4. Verify database in `data/resume_matching.db`

---

**Happy Matching! 🎯**
