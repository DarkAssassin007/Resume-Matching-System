"""
Quick script to check task execution status
"""
from database import Database

db = Database()

print("\n" + "="*60)
print("RESUME MATCHING SYSTEM - STATUS CHECK")
print("="*60 + "\n")

# Check resumes
resumes = db.get_all_resumes()
print(f"📄 RESUMES: {len(resumes)} uploaded")
for resume in resumes:
    print(f"   ✓ ID {resume['id']}: {resume['candidate_name']} ({resume['file_name']})")

print()

# Check job descriptions
jobs = db.get_all_job_descriptions()
print(f"💼 JOB DESCRIPTIONS: {len(jobs)} created")
for job in jobs:
    print(f"   ✓ ID {job['id']}: {job['job_title']}")

print()

# Check matching results
print("🎯 MATCHING RESULTS:")
if len(jobs) == 0:
    print("   ⚠ No jobs created yet")
else:
    for job in jobs:
        results = db.get_matching_results(job['id'])
        print(f"   Job '{job['job_title']}': {len(results)} matches")
        for result in results[:5]:  # Show top 5
            print(f"      - {result['candidate_name']}: {result['matching_score']:.1f}%")

print("\n" + "="*60 + "\n")
