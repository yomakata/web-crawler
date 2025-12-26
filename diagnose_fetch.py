"""
Diagnostic tool to check what HTML is actually being fetched
This helps debug why scoped elements aren't being found
"""
import sys
sys.path.insert(0, 'backend')

from crawler.fetcher import WebFetcher
from crawler.parser import ContentParser
from bs4 import BeautifulSoup

# The URL from your test
test_url = "https://intranet.dtgo.com/Whats-New/News/2025/12/06-Dont-Miss-MQDC-Special-Year-End-Offer"
target_class = "content-section"

print("=" * 80)
print("HTML FETCH DIAGNOSTIC TOOL")
print("=" * 80)
print(f"\nTarget URL: {test_url}")
print(f"Looking for class: '{target_class}'")
print("\n" + "-" * 80)

try:
    # Fetch the page
    print("\n1. Fetching page...")
    fetcher = WebFetcher()
    response = fetcher.fetch(test_url)
    print(f"   ✓ Status: {response.status_code}")
    print(f"   ✓ Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    print(f"   ✓ Content-Length: {len(response.text)} characters")
    
    # Parse HTML
    print("\n2. Parsing HTML...")
    parser = ContentParser(response.text, test_url)
    print(f"   ✓ Parsed with BeautifulSoup (lxml)")
    
    # Check for JavaScript frameworks
    print("\n3. Checking for JavaScript frameworks...")
    scripts = parser.soup.find_all('script')
    print(f"   Found {len(scripts)} script tags")
    
    js_indicators = ['React', 'Vue', 'Angular', 'botframework', 'webchat', 'app.bundle', 'vendor.bundle']
    found_frameworks = []
    for indicator in js_indicators:
        if any(indicator in str(script) for script in scripts):
            found_frameworks.append(indicator)
    
    if found_frameworks:
        print(f"   ⚠ JavaScript frameworks detected: {', '.join(found_frameworks)}")
        print("   ⚠ This page may render content dynamically!")
    else:
        print("   ✓ No obvious JavaScript frameworks detected")
    
    # Look for the target class
    print(f"\n4. Searching for class='{target_class}'...")
    
    # Method 1: find()
    element1 = parser.soup.find(class_=target_class)
    print(f"   Method 1 (find): {'✓ FOUND' if element1 else '✗ NOT FOUND'}")
    
    # Method 2: attrs with lambda
    element2 = parser.soup.find(attrs={"class": lambda x: x and target_class in x.split()})
    print(f"   Method 2 (attrs): {'✓ FOUND' if element2 else '✗ NOT FOUND'}")
    
    # Method 3: CSS selector
    element3 = parser.soup.select_one(f".{target_class}")
    print(f"   Method 3 (select): {'✓ FOUND' if element3 else '✗ NOT FOUND'}")
    
    # List all available classes
    print("\n5. All classes found in HTML:")
    all_classes = set()
    for tag in parser.soup.find_all(class_=True):
        classes = tag.get('class', [])
        if isinstance(classes, list):
            all_classes.update(classes)
        else:
            all_classes.add(classes)
    
    sorted_classes = sorted(list(all_classes))
    print(f"   Total unique classes: {len(sorted_classes)}")
    
    # Check if target class is in the list
    if target_class in sorted_classes:
        print(f"   ✓ '{target_class}' IS in the list!")
    else:
        print(f"   ✗ '{target_class}' is NOT in the list")
    
    print("\n   First 30 classes:")
    for i, cls in enumerate(sorted_classes[:30], 1):
        marker = "  👉" if cls == target_class else "    "
        print(f"{marker} {i}. {cls}")
    
    if len(sorted_classes) > 30:
        print(f"   ... and {len(sorted_classes) - 30} more classes")
    
    # Check for div with "content" in the name
    print("\n6. Looking for similar class names...")
    similar = [cls for cls in sorted_classes if 'content' in cls.lower()]
    if similar:
        print(f"   Classes containing 'content': {', '.join(similar)}")
    else:
        print("   No classes containing 'content' found")
    
    # Sample the HTML structure
    print("\n7. HTML Structure Sample (first 2000 chars):")
    print("-" * 80)
    print(response.text[:2000])
    print("-" * 80)
    
    # Check body content
    body = parser.soup.find('body')
    if body:
        print("\n8. Body tag analysis:")
        print(f"   Body has {len(list(body.descendants))} descendant elements")
        print(f"   Body classes: {body.get('class', [])}")
    
    print("\n" + "=" * 80)
    print("DIAGNOSIS COMPLETE")
    print("=" * 80)
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
