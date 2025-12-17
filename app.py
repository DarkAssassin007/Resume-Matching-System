"""
Flask Web Application for Resume Matching System
Provides UI for uploading resumes, entering job descriptions, and viewing results
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
import time
from werkzeug.utils import secure_filename
from database import Database
from spark_processor import get_processor, stop_processor
import PyPDF2
import docx
import traceback
import atexit
import json
from config import Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx', 'zip'}

# Initialize database
db = Database()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(file_path, filename):
    """Extract text content from uploaded file"""
    ext = filename.rsplit('.', 1)[1].lower()
    
    try:
        if ext == 'txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        elif ext == 'pdf':
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                # Limit to first 10 pages to prevent hanging
                pages_to_read = min(10, len(pdf_reader.pages))
                for i in range(pages_to_read):
                    try:
                        text += pdf_reader.pages[i].extract_text() + "\n"
                    except Exception as page_error:
                        print(f"Warning: Could not extract text from page {i} of {filename}: {str(page_error)}")
                        continue
            return text
        
        elif ext == 'docx':
            doc = docx.Document(file_path)
            # Limit to first 100 paragraphs to prevent hanging
            paragraphs = doc.paragraphs[:100] if len(doc.paragraphs) > 100 else doc.paragraphs
            text = "\n".join([paragraph.text for paragraph in paragraphs])
            return text
        
        else:
            return ""
    except Exception as e:
        print(f"Error extracting text from {filename}: {str(e)}")
        return ""

@app.route('/')
def index():
    """Home page"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication - in production, use proper authentication
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    """Upload resume page"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            candidate_name = request.form.get('candidate_name', '').strip()
            
            if not candidate_name:
                flash('Please enter candidate name', 'error')
                return redirect(request.url)
            
            if 'resume_files' not in request.files:
                flash('No files uploaded', 'error')
                return redirect(request.url)
            
            files = request.files.getlist('resume_files')
            
            if not files or all(f.filename == '' for f in files):
                flash('No files selected', 'error')
                return redirect(request.url)
            
            # Ensure upload folder exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            uploaded_count = 0
            failed_files = []
            
            # Process each file
            for file in files:
                if file.filename == '':
                    continue
                    
                if file and allowed_file(file.filename):
                    try:
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        
                        # Handle duplicate filenames
                        counter = 1
                        base_name, ext = os.path.splitext(filename)
                        while os.path.exists(file_path):
                            new_name = f"{base_name}_{counter}{ext}"
                            file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
                            counter += 1
                        
                        # Save file with timeout
                        file.save(file_path)
                        
                        # Verify file was saved
                        if not os.path.exists(file_path):
                            failed_files.append(f"{filename} (Failed to save file)")
                            continue
                        
                        # Check if it's a zip file
                        if filename.lower().endswith('.zip'):
                            # Handle zip file upload
                            try:
                                import zipfile
                                
                                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                    # Validate zip file structure first
                                    zip_ref.testzip()
                                    
                                    # Get list of valid files first
                                    valid_files = []
                                    for zip_info in zip_ref.infolist():
                                        # Skip directories and __MACOSX files
                                        if zip_info.is_dir() or '__MACOSX' in zip_info.filename:
                                            continue
                                        
                                        # Skip files that are too large (more than 16MB each)
                                        if zip_info.file_size > 16 * 1024 * 1024:
                                            failed_files.append(f"{zip_info.filename} (File too large)")
                                            continue
                                        
                                        # Get file name
                                        inner_filename = os.path.basename(zip_info.filename)
                                        
                                        # Check if it's a supported file type
                                        if inner_filename and allowed_file(inner_filename):
                                            valid_files.append((zip_info, inner_filename))
                                        
                                        # Limit to 10 files max to prevent abuse
                                        if len(valid_files) >= 10:
                                            break
                                
                                # Process valid files
                                zip_uploaded_count = 0
                                for zip_info, inner_filename in valid_files:
                                    try:
                                        # Extract file to memory first
                                        with zip_ref.open(zip_info) as source:
                                            file_content = source.read()
                                        
                                        # Save to temporary location
                                        extracted_path = os.path.join(app.config['UPLOAD_FOLDER'], inner_filename)
                                        
                                        # Handle duplicate names
                                        counter = 1
                                        base_name, ext = os.path.splitext(inner_filename)
                                        while os.path.exists(extracted_path):
                                            new_name = f"{base_name}_{counter}{ext}"
                                            extracted_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
                                            counter += 1
                                        
                                        # Save file
                                        with open(extracted_path, 'wb') as target:
                                            target.write(file_content)
                                        
                                        # Extract text from file
                                        text_content = extract_text_from_file(extracted_path, inner_filename)
                                        
                                        if text_content and len(text_content.strip()) > 50:  # Minimum content check
                                            # Save to database
                                            resume_id = db.add_resume(f"{candidate_name}_{uploaded_count+zip_uploaded_count+1}", inner_filename, text_content)
                                            uploaded_count += 1
                                            zip_uploaded_count += 1
                                        else:
                                            failed_files.append(f"{inner_filename} (Insufficient content)")
                                        
                                        # Clean up temporary file immediately
                                        if os.path.exists(extracted_path):
                                            os.remove(extracted_path)
                                    except Exception as file_error:
                                        failed_files.append(f"{inner_filename} ({str(file_error)})")
                                
                                # Remove the zip file
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                
                                uploaded_count += zip_uploaded_count
                                
                            except zipfile.BadZipFile:
                                failed_files.append(f"{filename} (Invalid or corrupted zip file)")
                                # Clean up the invalid zip file
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                            except Exception as e:
                                failed_files.append(f"{filename} (Error processing zip: {str(e)})")
                                # Clean up the zip file
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                        else:
                            # Handle single file upload
                            # Extract text from file
                            file_content = extract_text_from_file(file_path, filename)
                            
                            if not file_content:
                                failed_files.append(f"{filename} (Could not extract text)")
                                # Clean up the file
                                if os.path.exists(file_path):
                                    os.remove(file_path)
                                continue
                            
                            # Save to database with timeout simulation
                            resume_id = db.add_resume(f"{candidate_name}_{uploaded_count+1}", filename, file_content)
                            uploaded_count += 1
                            
                            # Clean up the file immediately
                            if os.path.exists(file_path):
                                os.remove(file_path)
                    except Exception as file_save_error:
                        failed_files.append(f"{file.filename} (Failed to save: {str(file_save_error)})")
                else:
                    failed_files.append(f"{file.filename} (Invalid file type)")
            
            # Prepare success message
            if uploaded_count > 0:
                message = f'Successfully uploaded {uploaded_count} resume(s)!'
                if failed_files:
                    message += f' Failed to process: {", ".join(failed_files)}'
                flash(message, 'success')
            elif failed_files:
                flash(f'Failed to upload resumes: {", ".join(failed_files)}', 'error')
            else:
                flash('No valid resumes were uploaded.', 'warning')
            
            return redirect(url_for('upload_resume'))
        
        except Exception as e:
            flash(f'Error uploading resumes: {str(e)}', 'error')
            traceback.print_exc()
            return redirect(request.url)
    
    # GET request - show all resumes
    resumes = db.get_all_resumes()
    return render_template('upload_resume.html', resumes=resumes)

@app.route('/create_job', methods=['GET', 'POST'])
def create_job():
    """Create job description page"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            job_title = request.form.get('job_title', '').strip()
            description = request.form.get('description', '').strip()
            required_skills = request.form.get('required_skills', '').strip()
            
            if not job_title or not description or not required_skills:
                flash('All fields are required', 'error')
                return redirect(request.url)
            
            # Save to database
            job_id = db.add_job_description(job_title, description, required_skills)
            
            flash(f'Job description created successfully! ID: {job_id}', 'success')
            return redirect(url_for('create_job'))
        
        except Exception as e:
            flash(f'Error creating job description: {str(e)}', 'error')
            traceback.print_exc()
            return redirect(request.url)
    
    # GET request - show all jobs
    jobs = db.get_all_job_descriptions()
    return render_template('create_job.html', jobs=jobs)

@app.route('/match_resumes/<int:job_id>')
def match_resumes(job_id):
    """Match all resumes to a specific job"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get job description
        job = db.get_job_by_id(job_id)
        if not job:
            flash('Job description not found', 'error')
            return redirect(url_for('create_job'))
        
        # Get all resumes
        resumes = db.get_all_resumes()
        
        if not resumes:
            flash('No resumes available for matching', 'warning')
            return redirect(url_for('create_job'))
        
        # Initialize monitoring variables
        start_time = time.time()
        resume_count = len(resumes)
        
        # Try Spark processor first, fallback to simple matcher
        try:
            # Get Spark processor
            processor = get_processor()
            matching_results = processor.match_resumes_to_job(resumes, job)
            method_used = "PySpark (TF-IDF)"
            flash('Using advanced PySpark matching with TF-IDF algorithm.', 'info')
            
            # Add basic monitoring info
            processing_time = time.time() - start_time
            flash(f'Matching completed in {processing_time:.2f} seconds for {resume_count} resumes.', 'info')
        except Exception as spark_error:
            # Fallback to simple matcher (no Spark required)
            print(f"Spark matching failed, using simple matcher: {spark_error}")
            try:
                from simple_matcher import get_simple_processor
                processor = get_simple_processor()
                matching_results = processor.match_resumes_to_job(resumes, job)
                method_used = "Scikit-learn (TF-IDF)"
                flash('Using simplified matching (Spark unavailable due to compatibility issues). The application will still work correctly with slightly reduced performance.', 'warning')
                
                # Add basic monitoring info
                processing_time = time.time() - start_time
                flash(f'Matching completed in {processing_time:.2f} seconds for {resume_count} resumes.', 'info')
            except Exception as simple_error:
                print(f"Simple matching also failed: {simple_error}")
                flash(f'Error: Both Spark and simple matching failed. Please check the logs.', 'error')
                return redirect(url_for('create_job'))
        
        # Clear previous results for this job
        db.clear_matching_results(job_id)
        
        # Save results to database
        for result in matching_results:
            db.add_matching_result(
                resume_id=result['resume_id'],
                job_id=job_id,
                matching_score=result['matching_score'],
                matched_skills=result['matched_skills_str']
            )
        
        flash(f'Successfully matched {len(matching_results)} resumes using {method_used}!', 'success')
        return redirect(url_for('view_results', job_id=job_id))
    
    except Exception as e:
        flash(f'Error matching resumes: {str(e)}', 'error')
        traceback.print_exc()
        return redirect(url_for('create_job'))

@app.route('/results/<int:job_id>')
def view_results(job_id):
    """View matching results for a job"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        job = db.get_job_by_id(job_id)
        if not job:
            flash('Job description not found', 'error')
            return redirect(url_for('create_job'))
        
        results = db.get_matching_results(job_id, limit=50)
        
        # Get Spark Web UI URL (if available)
        try:
            processor = get_processor()
            spark_ui_url = processor.get_spark_ui_url()
        except Exception as e:
            # Fallback if Spark processor is not available
            spark_ui_url = 'http://localhost:4040'
        
        return render_template('results.html', job=job, results=results, spark_ui_url=spark_ui_url)
    
    except Exception as e:
        flash(f'Error viewing results: {str(e)}', 'error')
        traceback.print_exc()
        return redirect(url_for('create_job'))

@app.route('/spark_ui')
def spark_ui_redirect():
    """Redirect to Spark Web UI"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        processor = get_processor()
        return redirect(processor.get_spark_ui_url())
    except Exception as e:
        # Fallback if Spark processor is not available
        flash('Spark Web UI is not available at the moment.', 'warning')
        return redirect(url_for('index'))

@app.route('/spark_monitor')
def spark_monitor():
    """Integrated system monitoring dashboard with database and Spark metrics"""
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get database statistics
        all_resumes = db.get_all_resumes()
        all_jobs = db.get_all_job_descriptions()
        
        # Calculate matching statistics
        total_matches = 0
        jobs_with_results = 0
        for job in all_jobs:
            results = db.get_matching_results(job['id'], limit=1000)
            if results:
                total_matches += len(results)
                jobs_with_results += 1
        
        avg_matches = round(total_matches / jobs_with_results, 1) if jobs_with_results > 0 else 0
        
        # Get database file size
        import os
        db_path = 'data/resume_matching.db'
        db_size = "N/A"
        if os.path.exists(db_path):
            size_bytes = os.path.getsize(db_path)
            if size_bytes < 1024:
                db_size = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                db_size = f"{size_bytes / 1024:.2f} KB"
            else:
                db_size = f"{size_bytes / (1024 * 1024):.2f} MB"
        
        db_stats = {
            'total_resumes': len(all_resumes),
            'total_jobs': len(all_jobs),
            'total_matches': total_matches,
            'jobs_with_results': jobs_with_results,
            'avg_matches': avg_matches,
            'db_size': db_size
        }
        
        # Try to get Spark status
        try:
            processor = get_processor()
            spark_status = {
                'session_active': True,
                'version': processor.spark.version,
                'app_name': processor.spark.sparkContext.appName,
                'master': processor.spark.sparkContext.master,
                'cores': processor.spark.sparkContext.defaultParallelism,
                'default_parallelism': processor.spark.sparkContext.defaultParallelism,
                'driver_memory': processor.spark.sparkContext.getConf().get('spark.driver.memory', '2g'),
                'executor_memory': processor.spark.sparkContext.getConf().get('spark.executor.memory', 'N/A')
            }
            spark_ui_url = processor.get_spark_ui_url()
        except Exception as e:
            # Provide enhanced fallback information
            import psutil
            import os
            
            # Get system information as a fallback
            cpu_count = psutil.cpu_count()
            memory_info = psutil.virtual_memory()
            
            spark_status = {
                'session_active': False,
                'version': 'N/A (Using fallback processing)',
                'app_name': 'ResumeMatchingSystem',
                'master': 'local[*]',
                'cores': cpu_count if cpu_count else 0,
                'default_parallelism': cpu_count if cpu_count else 0,
                'driver_memory': f"{memory_info.total / (1024**3):.1f}GB",
                'executor_memory': 'N/A (Fallback mode)'
            }
            spark_ui_url = 'http://localhost:4040'
        
        # Get recent jobs from database
        recent_jobs = []
        for job in all_jobs[:10]:  # Last 10 jobs
            results = db.get_matching_results(job['id'], limit=1)
            recent_jobs.append({
                'id': job['id'],
                'job_title': job['job_title'],
                'resume_count': len(db.get_matching_results(job['id'], limit=1000)),
                'created_at': job['created_at']
            })
        
        return render_template('spark_monitor.html', 
                             db_stats=db_stats,
                             spark_status=spark_status,
                             spark_ui_url=spark_ui_url,
                             recent_jobs=recent_jobs)
    
    except Exception as e:
        flash(f'Error loading monitoring dashboard: {str(e)}. Spark monitoring features are unavailable due to compatibility issues, but the application will still work correctly.', 'warning')
        traceback.print_exc()
        return redirect(url_for('index'))

@app.route('/api/resumes')
def api_resumes():
    """API endpoint to get all resumes"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    resumes = db.get_all_resumes()
    return jsonify(resumes)

@app.route('/api/jobs')
def api_jobs():
    """API endpoint to get all job descriptions"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    jobs = db.get_all_job_descriptions()
    return jsonify(jobs)

@app.route('/api/results/<int:job_id>')
def api_results(job_id):
    """API endpoint to get matching results"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    results = db.get_matching_results(job_id)
    return jsonify(results)

@app.route('/api/upload_resumes', methods=['POST'])
def api_upload_resumes():
    """API endpoint for uploading resumes with progress tracking"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        candidate_name = request.form.get('candidate_name', '').strip()
        
        if not candidate_name:
            return jsonify({'error': 'Please enter candidate name'}), 400
        
        if 'resume_files' not in request.files:
            return jsonify({'error': 'No files uploaded'}), 400
        
        files = request.files.getlist('resume_files')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        total_files = len(files)
        processed_files = 0
        uploaded_count = 0
        failed_files = []
        
        # Process each file
        for i, file in enumerate(files):
            if file.filename == '':
                continue
                
            if file and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    # Handle duplicate filenames
                    counter = 1
                    base_name, ext = os.path.splitext(filename)
                    while os.path.exists(file_path):
                        new_name = f"{base_name}_{counter}{ext}"
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
                        counter += 1
                    
                    # Save file with timeout
                    file.save(file_path)
                    
                    # Verify file was saved
                    if not os.path.exists(file_path):
                        failed_files.append(f"{filename} (Failed to save file)")
                        continue
                    
                    # Check if it's a zip file
                    if filename.lower().endswith('.zip'):
                        # Handle zip file upload
                        try:
                            import zipfile
                            
                            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                # Validate zip file structure first
                                zip_ref.testzip()
                                
                                # Get list of valid files first
                                valid_files = []
                                for zip_info in zip_ref.infolist():
                                    # Skip directories and __MACOSX files
                                    if zip_info.is_dir() or '__MACOSX' in zip_info.filename:
                                        continue
                                    
                                    # Skip files that are too large (more than 16MB each)
                                    if zip_info.file_size > 16 * 1024 * 1024:
                                        failed_files.append(f"{zip_info.filename} (File too large)")
                                        continue
                                    
                                    # Get file name
                                    inner_filename = os.path.basename(zip_info.filename)
                                    
                                    # Check if it's a supported file type
                                    if inner_filename and allowed_file(inner_filename):
                                        valid_files.append((zip_info, inner_filename))
                                    
                                    # Limit to 10 files max to prevent abuse
                                    if len(valid_files) >= 10:
                                        break
                            
                            # Process valid files
                            zip_uploaded_count = 0
                            for zip_info, inner_filename in valid_files:
                                try:
                                    # Extract file to memory first
                                    with zip_ref.open(zip_info) as source:
                                        file_content = source.read()
                                    
                                    # Save to temporary location
                                    extracted_path = os.path.join(app.config['UPLOAD_FOLDER'], inner_filename)
                                    
                                    # Handle duplicate names
                                    counter = 1
                                    base_name, ext = os.path.splitext(inner_filename)
                                    while os.path.exists(extracted_path):
                                        new_name = f"{base_name}_{counter}{ext}"
                                        extracted_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)
                                        counter += 1
                                    
                                    # Save file
                                    with open(extracted_path, 'wb') as target:
                                        target.write(file_content)
                                    
                                    # Extract text from file
                                    text_content = extract_text_from_file(extracted_path, inner_filename)
                                    
                                    if text_content and len(text_content.strip()) > 50:  # Minimum content check
                                        # Save to database
                                        resume_id = db.add_resume(f"{candidate_name}_{uploaded_count+zip_uploaded_count+1}", inner_filename, text_content)
                                        uploaded_count += 1
                                        zip_uploaded_count += 1
                                    else:
                                        failed_files.append(f"{inner_filename} (Insufficient content)")
                                    
                                    # Clean up temporary file immediately
                                    if os.path.exists(extracted_path):
                                        os.remove(extracted_path)
                                except Exception as file_error:
                                    failed_files.append(f"{inner_filename} ({str(file_error)})")
                            
                            # Remove the zip file
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            
                            uploaded_count += zip_uploaded_count
                            
                        except zipfile.BadZipFile:
                            failed_files.append(f"{filename} (Invalid or corrupted zip file)")
                            # Clean up the invalid zip file
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except Exception as e:
                            failed_files.append(f"{filename} (Error processing zip: {str(e)})")
                            # Clean up the zip file
                            if os.path.exists(file_path):
                                os.remove(file_path)
                    else:
                        # Handle single file upload
                        # Extract text from file
                        file_content = extract_text_from_file(file_path, filename)
                        
                        if not file_content:
                            failed_files.append(f"{filename} (Could not extract text)")
                            # Clean up the file
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            continue
                        
                        # Save to database with timeout simulation
                        resume_id = db.add_resume(f"{candidate_name}_{uploaded_count+1}", filename, file_content)
                        uploaded_count += 1
                        
                        # Clean up the file immediately
                        if os.path.exists(file_path):
                            os.remove(file_path)
                    
                    # Update progress
                    processed_files = i + 1
                except Exception as file_save_error:
                    failed_files.append(f"{file.filename} (Failed to save: {str(file_save_error)})")
            else:
                failed_files.append(f"{file.filename} (Invalid file type)")
        
        # Prepare success message
        result = {
            'uploaded_count': uploaded_count,
            'total_files': total_files,
            'processed_files': processed_files,
            'failed_files': failed_files,
            'message': f'Successfully uploaded {uploaded_count} resume(s)!'
        }
        
        if failed_files:
            result['message'] += f' Failed to process: {", ".join(failed_files)}'
        
        return jsonify(result)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Error uploading resumes: {str(e)}'}), 500

@app.route('/api/delete_resume/<int:resume_id>', methods=['DELETE'])
def api_delete_resume(resume_id):
    """API endpoint for deleting a resume"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Delete resume from database
        success = db.delete_resume(resume_id)
        
        if success:
            return jsonify({'message': f'Resume ID {resume_id} deleted successfully'}), 200
        else:
            return jsonify({'error': f'Resume ID {resume_id} not found'}), 404
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Error deleting resume: {str(e)}'}), 500

# Cleanup on shutdown
@atexit.register
def cleanup():
    """Stop Spark processor on application shutdown"""
    stop_processor()

if __name__ == '__main__':
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("\n" + "="*60)
    print("Resume Matching System")
    print("="*60)
    print(f"Web Application: http://localhost:5000")
    print(f"Spark Web UI: http://localhost:4040")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
