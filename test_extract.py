#!/usr/bin/env python3
"""
Test LinkedIn job extraction
"""

import sys
sys.path.insert(0, '.')

from deep_web_reader import extract_linkedin_jobs

# Sample HTML mimicking LinkedIn job search results
SAMPLE_HTML = '''
<!DOCTYPE html>
<html>
<body>
    <div class="job-search-card">
        <a class="base-card__full-link" href="/jobs/view/1234567890">Link</a>
        <div class="base-search-card__title">Senior Software Engineer</div>
        <div class="base-search-card__subtitle">Google</div>
        <div class="job-search-card__listdate">1 day ago</div>
    </div>
    <div class="job-card-container">
        <a href="https://www.linkedin.com/jobs/view/9876543210"></a>
        <h3 class="job-card-list__title">Data Scientist</h3>
        <span class="job-card-container__company-name">Facebook</span>
        <time class="job-card-container__listed-time">2 days ago</time>
    </div>
    <li class="jobs-search-results__list-item">
        <a class="job-card-container__link" href="/jobs/view/5555555555"></a>
        <div class="base-search-card__title">Product Manager</div>
        <div class="base-search-card__subtitle">Microsoft</div>
        <div class="job-search-card__listdate">3 days ago</div>
    </li>
</body>
</html>
'''

def main():
    print("Testing extract_linkedin_jobs...")
    result = extract_linkedin_jobs(SAMPLE_HTML)
    print("Result:")
    print(result)
    print("\n" + "="*60)
    
    # Check if expected jobs are found
    expected_companies = ["Google", "Facebook", "Microsoft"]
    expected_titles = ["Senior Software Engineer", "Data Scientist", "Product Manager"]
    
    for company in expected_companies:
        if company in result:
            print(f"✓ Found company: {company}")
        else:
            print(f"✗ Missing company: {company}")
    
    for title in expected_titles:
        if title in result:
            print(f"✓ Found title: {title}")
        else:
            print(f"✗ Missing title: {title}")
    
    # Check for links
    if "/jobs/view/1234567890" in result or "linkedin.com/jobs/view/1234567890" in result:
        print("✓ Found job link 1")
    else:
        print("✗ Missing job link 1")
    
    if "linkedin.com/jobs/view/9876543210" in result:
        print("✓ Found job link 2")
    else:
        print("✗ Missing job link 2")
    
    if "/jobs/view/5555555555" in result or "linkedin.com/jobs/view/5555555555" in result:
        print("✓ Found job link 3")
    else:
        print("✗ Missing job link 3")

if __name__ == "__main__":
    main()