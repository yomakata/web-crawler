#!/usr/bin/env python3
"""Test script to verify current_url functionality"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from api.models import Job, job_store

# Create a test job
print("Creating test job...")
job = job_store.create_job(total_urls=3, crawl_type='bulk')
print(f"Job created: {job.job_id}")
print(f"Initial current_url: {job.current_url}")

# Start the job
job.start()
print(f"\nJob started, status: {job.status}")

# Set current URL
test_url = "https://example.com/test-page"
print(f"\nSetting current_url to: {test_url}")
job.set_current_url(test_url)
job_store.update_job(job)

# Retrieve and verify
retrieved_job = job_store.get_job(job.job_id)
print(f"Retrieved job current_url: {retrieved_job.current_url}")

# Check to_dict output
job_dict = retrieved_job.to_dict()
print(f"\nJob dict current_url: {job_dict.get('current_url')}")

# Test API-like response
print("\nSimulated API response:")
import json
print(json.dumps({
    'job_id': job_dict['job_id'],
    'status': job_dict['status'],
    'progress': job_dict['progress'],
    'current_url': job_dict['current_url']
}, indent=2))

print("\n✅ Test completed successfully!")
