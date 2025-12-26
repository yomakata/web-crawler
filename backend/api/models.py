"""Data models and schemas for API"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
from datetime import datetime
import pytz
import uuid
import json
from pathlib import Path

# Thailand timezone
THAILAND_TZ = pytz.timezone('Asia/Bangkok')


def now_thailand():
    """Get current datetime in Thailand timezone"""
    return datetime.now(THAILAND_TZ)


@dataclass
class CrawlRequest:
    """Single URL crawl request"""
    url: str
    mode: str = 'content'
    formats: List[str] = field(default_factory=lambda: ['txt'])
    scope_class: Optional[str] = None
    scope_id: Optional[str] = None
    download_images: bool = False
    link_type: str = 'all'
    exclude_anchors: bool = False
    # Authentication parameters
    cookies: Optional[Dict[str, str]] = None
    auth_headers: Optional[Dict[str, str]] = None
    basic_auth_username: Optional[str] = None
    basic_auth_password: Optional[str] = None
    
    def validate(self) -> tuple:
        """Validate request parameters"""
        errors = []
        
        if not self.url:
            errors.append("URL is required")
        
        if self.mode not in ['content', 'link']:
            errors.append("Mode must be 'content' or 'link'")
        
        if self.mode == 'content':
            valid_formats = ['txt', 'md', 'html']
            if not all(fmt in valid_formats for fmt in self.formats):
                errors.append(f"Invalid formats for content mode. Valid: {valid_formats}")
        
        elif self.mode == 'link':
            valid_formats = ['txt', 'json']
            if not all(fmt in valid_formats for fmt in self.formats):
                errors.append(f"Invalid formats for link mode. Valid: {valid_formats}")
        
        if self.link_type not in ['all', 'internal', 'external']:
            errors.append("link_type must be 'all', 'internal', or 'external'")
        
        return len(errors) == 0, errors


@dataclass
class Job:
    """Crawling job"""
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = 'pending'  # pending, running, completed, failed
    created_at: datetime = field(default_factory=now_thailand)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_urls: int = 1
    completed_urls: int = 0
    failed_urls: int = 0
    results: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    crawl_type: str = 'single'  # 'single' or 'bulk'
    csv_filename: Optional[str] = None  # CSV filename for bulk crawls
    current_url: Optional[str] = None  # Currently processing URL
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'job_id': self.job_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_urls': self.total_urls,
            'completed_urls': self.completed_urls,
            'failed_urls': self.failed_urls,
            'progress': (self.completed_urls / self.total_urls * 100) if self.total_urls > 0 else 0,
            'results': self.results,
            'errors': self.errors,
            'crawl_type': self.crawl_type,
            'csv_filename': self.csv_filename,
            'current_url': self.current_url
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Job':
        """Create Job from dictionary"""
        # Parse datetime strings back to datetime objects
        if 'created_at' in data and isinstance(data['created_at'], str):
            dt = datetime.fromisoformat(data['created_at'])
            # If timezone-naive, localize to Thailand timezone
            if dt.tzinfo is None:
                dt = THAILAND_TZ.localize(dt)
            data['created_at'] = dt
        elif 'created_at' in data and isinstance(data['created_at'], datetime):
            # If it's already a datetime but timezone-naive, localize it
            if data['created_at'].tzinfo is None:
                data['created_at'] = THAILAND_TZ.localize(data['created_at'])
                
        if 'started_at' in data and data['started_at'] and isinstance(data['started_at'], str):
            dt = datetime.fromisoformat(data['started_at'])
            if dt.tzinfo is None:
                dt = THAILAND_TZ.localize(dt)
            data['started_at'] = dt
        elif 'started_at' in data and data['started_at'] and isinstance(data['started_at'], datetime):
            if data['started_at'].tzinfo is None:
                data['started_at'] = THAILAND_TZ.localize(data['started_at'])
                
        if 'completed_at' in data and data['completed_at'] and isinstance(data['completed_at'], str):
            dt = datetime.fromisoformat(data['completed_at'])
            if dt.tzinfo is None:
                dt = THAILAND_TZ.localize(dt)
            data['completed_at'] = dt
        elif 'completed_at' in data and data['completed_at'] and isinstance(data['completed_at'], datetime):
            if data['completed_at'].tzinfo is None:
                data['completed_at'] = THAILAND_TZ.localize(data['completed_at'])
        
        # Remove 'progress' if it exists (it's calculated, not stored)
        data.pop('progress', None)
        
        # Backwards compatibility: infer crawl_type from total_urls if not set
        if 'crawl_type' not in data or (data.get('crawl_type') == 'single' and data.get('total_urls', 1) > 1):
            data['crawl_type'] = 'bulk' if data.get('total_urls', 1) > 1 else 'single'
        
        # Fix status for old jobs: if all URLs failed but status is 'completed', change to 'failed'
        total_urls = data.get('total_urls', 1)
        failed_urls = data.get('failed_urls', 0)
        if data.get('status') == 'completed' and total_urls > 0 and failed_urls == total_urls:
            data['status'] = 'failed'
        
        # Backwards compatibility: add current_url if not present
        if 'current_url' not in data:
            data['current_url'] = None
        
        return cls(**data)
    
    def start(self):
        """Mark job as started"""
        self.status = 'running'
        self.started_at = now_thailand()
    
    def complete(self):
        """Mark job as completed or failed based on results"""
        # If all URLs failed, mark as failed instead of completed
        if self.total_urls > 0 and self.failed_urls == self.total_urls:
            self.status = 'failed'
        else:
            self.status = 'completed'
        self.completed_at = now_thailand()
    
    def fail(self, error: str):
        """Mark job as failed"""
        self.status = 'failed'
        self.completed_at = now_thailand()
        self.errors.append(error)
    
    def add_result(self, result: dict):
        """Add result to job"""
        self.results.append(result)
        if result.get('status') == 'success':
            self.completed_urls += 1
        else:
            self.failed_urls += 1
    
    def set_current_url(self, url: str):
        """Set currently processing URL"""
        self.current_url = url


class JobStore:
    """Persistent job storage with JSON file backend"""
    
    def __init__(self, storage_path: str = 'job_history.json'):
        self.storage_path = Path(storage_path)
        self.jobs: Dict[str, Job] = {}
        self._load()
    
    def _load(self):
        """Load job history from file"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for job_data in data:
                        job = Job.from_dict(job_data)
                        self.jobs[job.job_id] = job
                print(f"Loaded {len(self.jobs)} jobs from history file")
            except Exception as e:
                print(f"Error loading job history: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No job history file found, starting fresh")
    
    def _save(self):
        """Save job history to file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                data = [job.to_dict() for job in self.jobs.values()]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving job history: {e}")
            import traceback
            traceback.print_exc()
    
    def create_job(self, total_urls: int = 1, crawl_type: str = 'single', csv_filename: str = None) -> Job:
        """Create new job"""
        job = Job(total_urls=total_urls, crawl_type=crawl_type, csv_filename=csv_filename)
        self.jobs[job.job_id] = job
        self._save()
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_all_jobs(self, limit: int = 100) -> List[Job]:
        """Get all jobs (most recent first)"""
        sorted_jobs = sorted(
            self.jobs.values(),
            key=lambda j: j.created_at,
            reverse=True
        )
        return sorted_jobs[:limit]
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job"""
        if job_id in self.jobs:
            del self.jobs[job_id]
            self._save()
            return True
        return False
    
    def update_job(self, job: Job):
        """Update job and persist to disk"""
        if job.job_id in self.jobs:
            self.jobs[job.job_id] = job
            self._save()


# Global job store instance
job_store = JobStore()


@dataclass
class SavedJob:
    """Saved job configuration for reuse"""
    saved_job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ''
    description: str = ''
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Job configuration
    input_method: str = 'single'  # 'single' or 'bulk'
    mode: str = 'content'
    url: Optional[str] = None
    csv_filename: Optional[str] = None
    csv_content: Optional[str] = None  # Store CSV file content for bulk jobs
    formats: List[str] = field(default_factory=lambda: ['txt'])
    scope_class: Optional[str] = None
    scope_id: Optional[str] = None
    download_images: bool = False
    link_type: str = 'all'
    combine_results: bool = False

    # Authentication configuration
    auth_method: Optional[str] = None  # 'cookies', 'headers', 'basic'
    cookies: Optional[str] = None
    auth_headers: Optional[str] = None
    basic_auth_username: Optional[str] = None
    basic_auth_password: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat() if self.created_at else None
        data['updated_at'] = self.updated_at.isoformat() if self.updated_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SavedJob':
        """Create from dictionary"""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and isinstance(data['updated_at'], str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class SavedJobStore:
    """Persistent storage for saved jobs"""
    
    def __init__(self, storage_path: str = 'saved_jobs.json'):
        self.storage_path = Path(storage_path)
        self.jobs: Dict[str, SavedJob] = {}
        self._load()
    
    def _load(self):
        """Load saved jobs from file"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for job_data in data:
                        job = SavedJob.from_dict(job_data)
                        self.jobs[job.saved_job_id] = job
                print(f"Loaded {len(self.jobs)} jobs from {self.storage_path}")
            except Exception as e:
                print(f"Error loading saved jobs from {self.storage_path}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"No saved jobs file found at {self.storage_path}, starting fresh")
    
    def _save(self):
        """Save jobs to file"""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                data = [job.to_dict() for job in self.jobs.values()]
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Successfully saved {len(self.jobs)} jobs to {self.storage_path}")
        except Exception as e:
            print(f"Error saving jobs to {self.storage_path}: {e}")
            import traceback
            traceback.print_exc()
    
    def create_job(self, job_data: dict) -> SavedJob:
        """Create new saved job"""
        print(f"Creating new saved job with data: {job_data.get('name', 'unnamed')}")
        job = SavedJob(**job_data)
        self.jobs[job.saved_job_id] = job
        print(f"Job created with ID: {job.saved_job_id}, total jobs: {len(self.jobs)}")
        self._save()
        return job
    
    def update_job(self, saved_job_id: str, job_data: dict) -> Optional[SavedJob]:
        """Update existing saved job"""
        if saved_job_id in self.jobs:
            job = self.jobs[saved_job_id]
            # Update fields
            for key, value in job_data.items():
                if hasattr(job, key) and key not in ['saved_job_id', 'created_at']:
                    setattr(job, key, value)
            job.updated_at = datetime.now()
            self._save()
            return job
        return None
    
    def get_job(self, saved_job_id: str) -> Optional[SavedJob]:
        """Get saved job by ID"""
        return self.jobs.get(saved_job_id)
    
    def get_all_jobs(self) -> List[SavedJob]:
        """Get all saved jobs (most recent first)"""
        return sorted(
            self.jobs.values(),
            key=lambda j: j.updated_at,
            reverse=True
        )
    
    def find_by_name(self, name: str) -> Optional[SavedJob]:
        """Find saved job by name (case-insensitive)"""
        name_lower = name.lower().strip()
        for job in self.jobs.values():
            if job.name.lower().strip() == name_lower:
                return job
        return None
    
    def delete_job(self, saved_job_id: str) -> bool:
        """Delete saved job"""
        if saved_job_id in self.jobs:
            del self.jobs[saved_job_id]
            self._save()
            return True
        return False


# Global saved job store instance
saved_job_store = SavedJobStore()
