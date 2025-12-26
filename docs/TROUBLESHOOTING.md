# Common Issues & Solutions

## Docker Issues

### ❌ Error: "unable to prepare context: path frontend not found"

**Problem:** The original docker-compose.yml referenced a frontend that doesn't exist yet.

**Solution:** This has been fixed! The frontend service is now commented out in docker-compose.yml.

```bash
# Simply run again:
docker-compose up -d
```

### ❌ Error: "port is already allocated"

**Problem:** Port 5000 or 6379 is already in use.

**Solution:**
```bash
# Option 1: Stop the conflicting service
docker ps
docker stop <container-id>

# Option 2: Change port in .env file
# Edit .env and change BACKEND_PORT=5000 to another port like 8000
BACKEND_PORT=8000

# Then restart
docker-compose down
docker-compose up -d
```

### ❌ Error: "Cannot connect to Docker daemon"

**Problem:** Docker is not running.

**Solution:**
- **Windows:** Start Docker Desktop
- **Linux:** `sudo systemctl start docker`
- **Mac:** Start Docker Desktop

### ❌ Services won't start / crash immediately

**Problem:** Configuration or dependency issues.

**Solution:**
```bash
# Check logs
docker-compose logs backend

# Rebuild from scratch
docker-compose down
docker-compose up --build

# If still failing, check .env file exists
ls -la .env
```

## Python/Backend Issues

### ❌ ModuleNotFoundError

**Problem:** Dependencies not installed.

**Solution:**
```bash
cd backend
pip install -r requirements.txt

# If using virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Permission denied when writing files

**Problem:** Output directory doesn't exist or lacks permissions.

**Solution:**
```bash
# Create output directory
mkdir -p output
chmod 755 output

# Or specify different directory
python main.py --url https://example.com --output /path/to/writable/dir
```

### ❌ Import errors (cannot import 'api', 'crawler', etc.)

**Problem:** Running from wrong directory or PYTHONPATH issue.

**Solution:**
```bash
# Always run from backend directory
cd /c/Projects/web-crawler/backend

# Then run commands
python main.py --url https://example.com
python -m flask --app api.app run
```

### ❌ Flask app won't start

**Problem:** Port already in use or configuration issue.

**Solution:**
```bash
# Use different port
python -m flask --app api.app run --port 8000

# Or kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

## Network/Crawling Issues

### ❌ Timeout errors when crawling

**Problem:** Website is slow or blocking requests.

**Solution:**
```bash
# Increase timeout
python main.py --url https://example.com --timeout 60

# Or edit .env
DEFAULT_TIMEOUT=60
```

### ❌ "Invalid URL" error

**Problem:** URL format is incorrect.

**Solution:**
```bash
# Make sure URL includes http:// or https://
# Wrong:
python main.py --url example.com

# Correct:
python main.py --url https://example.com
```

### ❌ 403 Forbidden or 429 Too Many Requests

**Problem:** Website is blocking or rate-limiting your requests.

**Solution:**
```bash
# Set a custom user agent in .env
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Add delays between requests (for bulk operations)
# This is not built-in yet, but you can modify csv_processor.py to add time.sleep()
```

### ❌ Images not downloading

**Problem:** Image URLs are invalid or inaccessible.

**Solution:**
- Check extraction_details.json for image download errors
- Some sites use JavaScript to load images (not supported yet)
- Increase IMAGE_TIMEOUT in .env

## CSV/Bulk Processing Issues

### ❌ "CSV must contain a 'url' column"

**Problem:** CSV file doesn't have the required 'url' column.

**Solution:**
```csv
# Make sure first row has 'url' header
url,mode,format
https://example.com,content,txt
```

### ❌ "Too many URLs" error

**Problem:** CSV has more URLs than allowed limit.

**Solution:**
```bash
# Split into multiple CSV files
# Or increase limit in .env
MAX_URLS_PER_CSV=2000
```

### ❌ Some URLs fail in bulk mode

**Problem:** Individual URLs may have issues (invalid, timeout, etc.)

**Solution:**
- Check bulk_results.csv for details
- Failed URLs will be logged but won't stop the whole process
- Re-run failed URLs individually to see specific errors

## Output Issues

### ❌ Files not found after crawling

**Problem:** Output directory is different than expected.

**Solution:**
```bash
# Check where files were saved (shown in CLI output)
# Or specify output directory explicitly
python main.py --url https://example.com --output ./my-output

# Files are in: output/<domain>_<timestamp>/
ls output/
```

### ❌ Metadata files are missing

**Problem:** Crawl may have partially failed.

**Solution:**
- Check CLI output for errors
- Look for extraction_details.json and extraction_summary.txt
- Re-run the crawl

### ❌ HTML/Markdown looks wrong

**Problem:** Complex pages may not convert perfectly.

**Solution:**
- Try different format (txt instead of md)
- Use scope_class to target specific content
- Some formatting may be lost in conversion

## API Issues

### ❌ CORS errors in browser

**Problem:** Frontend trying to access API from different origin.

**Solution:**
```bash
# Add your frontend URL to .env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Then restart API
docker-compose restart backend
```

### ❌ "Job not found" error

**Problem:** Job ID is invalid or job was deleted.

**Solution:**
- Jobs are stored in memory and lost on restart
- Get fresh job ID from /api/history
- Use Docker volumes to persist (requires database setup)

### ❌ File download returns 404

**Problem:** File doesn't exist or wrong path.

**Solution:**
- Check job results to see actual filenames
- Files are in output folders, make sure they weren't deleted
- Use correct job_id and filename in download URL

## Testing Issues

### ❌ pytest command not found

**Problem:** pytest not installed or not in PATH.

**Solution:**
```bash
pip install pytest
# Or
pip install -r requirements.txt
```

### ❌ Tests failing

**Problem:** Dependencies or environment issues.

**Solution:**
```bash
# Make sure you're in backend directory
cd backend

# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest -v

# If still failing, run setup test
python test_setup.py
```

## General Tips

### 🔍 Debugging

```bash
# Run with verbose output
python main.py --url https://example.com --output ./test -v

# Check logs
# API logs:
docker-compose logs -f backend

# Check extraction details
cat output/<folder>/extraction_details.json | python -m json.tool
```

### 🧪 Quick Tests

```bash
# Test a simple page
python main.py --url https://example.com

# Test API
curl http://localhost:5000/health

# Verify setup
python test_setup.py
```

### 📚 Getting More Help

1. Read GETTING_STARTED.md for detailed setup
2. Check DOCKER_FIX.md for Docker-specific issues
3. Review extraction_details.json for crawl errors
4. Check API response messages for specific error details

## Still Having Issues?

1. **Run diagnostics:**
   ```bash
   cd backend
   python test_setup.py
   ```

2. **Check versions:**
   ```bash
   python --version  # Should be 3.10+
   docker --version  # Should be 20.10+
   docker-compose --version  # Should be 2.0+
   ```

3. **Start fresh:**
   ```bash
   # Remove virtual environment
   rm -rf backend/venv
   
   # Recreate
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. **Review logs carefully** - error messages usually tell you exactly what's wrong!
