"""
Script to trigger Spark initialization and check if Web UI starts
"""
import sys
import os
sys.path.insert(0, '.')

try:
    print("Importing Spark processor...")
    from spark_processor import get_processor
    print("Getting processor instance...")
    processor = get_processor()
    print("Processor initialized successfully!")
    
    # Check if we're using Spark or simple processor
    if hasattr(processor, 'spark'):
        print(f"Spark Version: {processor.spark.version}")
        
        # Try to do a simple operation to ensure Spark is working
        print("Testing basic Spark operation...")
        test_data = [{"name": "test", "value": 1}]
        df = processor.spark.createDataFrame(test_data)
        result = df.collect()
        print(f"Test operation result: {result}")
        
        print("Spark is working correctly!")
    else:
        print("Using simple matcher (no Spark)")
        # Test simple matcher
        test_resumes = [{"id": 1, "candidate_name": "John Doe", "file_content": "Python Java SQL"}]
        test_job = {"id": 1, "job_title": "Data Engineer", "description": "Looking for Python and SQL expert", "required_skills": "Python,SQL"}
        result = processor.match_resumes_to_job(test_resumes, test_job)
        print(f"Test operation result: {result}")
        print("Simple matcher is working correctly!")
    
    input("Press Enter to continue...")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()