# import requests
# from bs4 import BeautifulSoup
# import time
# import random
# import re
# from datetime import datetime,timedelta

# class JobScrapper:
#     """Job scraper for multiple platforms."""
#     def __init__(self):
#         self.headers={
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#         }
#         # Initialize platform-specific settings
#         self.platforms = {
#             "LinkedIn": {
#                 "search_url": "https://www.linkedin.com/jobs/search",
#                 "base_url": "https://www.linkedin.com"
#             },
#             "Indeed": {
#                 "search_url": "https://www.indeed.com/jobs",
#                 "base_url": "https://www.indeed.com"
#             },
#             "Glassdoor": {
#                 "search_url": "https://www.glassdoor.com/Job/jobs.htm",
#                 "base_url": "https://www.glassdoor.com"
#             },
#             "ZipRecruiter": {
#                 "search_url": "https://www.ziprecruiter.com/candidate/search",
#                 "base_url": "https://www.ziprecruiter.com"
#             },
#             "Monster": {
#                 "search_url": "https://www.monster.com/jobs/search",
#                 "base_url": "https://www.monster.com"
#             }
#         }
#     def verify_url(self,url):
#         """Verify that a URL is valid and reachable."""
#         try:
#             response=requests.head(url=url,timeout=5)
#             return response.status_code<400
#         except:
#             return False

#     def search_jobs(self,keywords,location,platform="Indeed",count=5):
#         """Search for jobs across selected platforms."""
#         if platform=="Linkedin":
#             return self.search_linkedin(keywords,location,count)
#         elif platform == "Indeed":
#             return self.search_indeed(keywords, location, count)
#         elif platform == "Glassdoor":
#             return self.search_glassdoor(keywords, location, count)
#         elif platform == "ZipRecruiter":
#             return self.search_ziprecruiter(keywords, location, count)
#         elif platform == "Monster":
#             return self.search_monster(keywords, location, count)
#         else:
#             print(f"Platform {platform} not supported.")
#             return []

#     def search_indeed(self,keywords,location,count=5):
#         """Search for jobs on Indeed with working URLs."""
#         try:
#             # Format search parameters correctly for Indeed
#             keyword_param=keywords.replace(" ","+")
#             location_param=location.replace(" ","+")

#             # Create search url
#             search_url=f"https://www.indeed.com/jobs?q={keyword_param}&l={location_param}&sort=date"
            
#             # Verify the search URL is valid
#             if not self.verify_url(search_url):
#                 search_url="https://www.indeed.com/"
#             # Create fallback job listings
#             jobs=[]
#             for i in range(min(count,5)):
#                 # Generate realistic fake job listings
#                 company_names = ["Acme Tech", "GlobalSystems", "InnoTech Solutions", "Digital Ventures", "TechCorp"]
#                 job_types = ["Full-time", "Contract", "Part-time", "Permanent", "Remote"]
                
#                 jobs.append({
#                     "title": f"{keywords} {['Specialist', 'Engineer', 'Manager', 'Developer', 'Analyst'][i % 5]}",
#                     "company": company_names[i % len(company_names)],
#                     "location": location,
#                     "description": f"We are looking for a talented {keywords} professional to join our team. This is a {job_types[i % len(job_types)]} position with competitive benefits.",
#                     "url": search_url,
#                     "apply_url": search_url,
#                     "date_posted": ["Today", "1 day ago", "2 days ago", "3 days ago", "5 days ago"][i % 5],
#                     "platform": "Indeed",
#                     "is_real_job": False
#                 })
#             return jobs
#         except Exception as e:
#             print(f"Indeed search error: {e}")
#             return []
        
#     def search_linkedin(self, keywords, location, count=5):
#         """Search for jobs on LinkedIn with working URLs."""
#         try:
#             # Format for LinkedIn search
#             keyword_param = keywords.replace(" ", "%20")
#             location_param = location.replace(" ", "%20")
            
#             # LinkedIn job search URL
#             search_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword_param}&location={location_param}&sortBy=DD"
            
#             # Verify the search URL is valid
#             if not self.verify_url(search_url):
#                 search_url = "https://www.linkedin.com/jobs/"
            
#             # Create fallback job listings
#             jobs = []
#             for i in range(min(count, 5)):
#                 # Generate realistic fake job listings
#                 company_names = ["Microsoft", "Amazon", "Google", "Apple", "Meta"]
#                 job_types = ["Full-time", "Contract", "Permanent", "Remote", "Hybrid"]
                
#                 jobs.append({
#                     "title": f"{keywords} {['Specialist', 'Engineer', 'Manager', 'Director', 'Lead'][i % 5]}",
#                     "company": company_names[i % len(company_names)],
#                     "location": location,
#                     "description": f"Join our team as a {keywords} professional. In this role, you will leverage your expertise to innovate and drive business impact.",
#                     "url": search_url,
#                     "apply_url": search_url,
#                     "date_posted": f"{random.randint(0, 2)} days ago",
#                     "platform": "LinkedIn",
#                     "is_real_job": False
#                 })
            
#             return jobs
#         except Exception as e:
#             print(f"LinkedIn search error: {e}")
#             return []
        

#     def search_glassdoor(self, keywords, location, count=5):
#         """Search for jobs on Glassdoor with working URLs."""
#         try:
#             # Format for Glassdoor search
#             keyword_formatted = keywords.replace(" ", "-").lower()
#             location_formatted = location.replace(" ", "-").lower()
            
#             # Real Glassdoor search URL
#             search_url = f"https://www.glassdoor.com/Job/{keyword_formatted}-jobs-SRCH_KO0,{len(keyword_formatted)}.htm"
            
#             # Verify the URL
#             if not self.verify_url(search_url):
#                 search_url = "https://www.glassdoor.com/Job/"
            
#             # Create fallback job listings
#             jobs = []
#             for i in range(min(count, 5)):
#                 # Generate realistic fake job listings
#                 company_names = ["Goldman Sachs", "JP Morgan", "Microsoft", "Amazon", "Google"]
#                 job_types = ["Full-time", "Contract", "Permanent", "Remote", "Hybrid"]
                
#                 jobs.append({
#                     "title": f"{keywords} {['Analyst', 'Consultant', 'Engineer', 'Director', 'Associate'][i % 5]}",
#                     "company": company_names[i % len(company_names)],
#                     "location": location,
#                     "description": f"We're seeking a talented {keywords} professional to join our team. You will work on challenging problems using cutting-edge technology.",
#                     "url": search_url,
#                     "apply_url": search_url,
#                     "date_posted": "Posted this week",
#                     "platform": "Glassdoor",
#                     "is_real_job": False
#                 })
            
#             return jobs
            
#         except Exception as e:
#             print(f"Glassdoor search error: {e}")
#             return []
        
#     def search_ziprecruiter(self, keywords, location, count=5):
#         """Search for jobs on ZipRecruiter with working URLs."""
#         try:
#             # Format for ZipRecruiter search
#             keyword_param = keywords.replace(" ", "+")
#             location_param = location.replace(" ", "+")
            
#             # Real ZipRecruiter search URL
#             search_url = f"https://www.ziprecruiter.com/candidate/search?search={keyword_param}&location={location_param}"
            
#             # Verify the search URL is valid
#             if not self.verify_url(search_url):
#                 search_url = "https://www.ziprecruiter.com/candidate/search"
            
#             # Create fallback job listings
#             jobs = []
#             for i in range(min(count, 5)):
#                 # Generate realistic fake job listings
#                 company_names = ["Johnson & Johnson", "Pfizer", "Apple", "Netflix", "Adobe"]
#                 job_types = ["Full-time", "Contract", "Part-time", "Remote", "Hybrid"]
                
#                 jobs.append({
#                     "title": f"{keywords} {['Specialist', 'Professional', 'Coordinator', 'Lead', 'Expert'][i % 5]}",
#                     "company": company_names[i % len(company_names)],
#                     "location": location,
#                     "description": f"Join our growing team as a {keywords} professional. In this role, you will utilize your expertise to drive innovation and excellence.",
#                     "url": search_url,
#                     "apply_url": search_url,
#                     "date_posted": "New",
#                     "platform": "ZipRecruiter",
#                     "is_real_job": False
#                 })
            
#             return jobs
            
#         except Exception as e:
#             print(f"ZipRecruiter search error: {e}")
#             return []
    
#     def search_monster(self, keywords, location, count=5):
#         """Search for jobs on Monster with working URLs."""
#         try:
#             # Format for Monster search
#             keyword_param = keywords.replace(" ", "-")
#             location_param = location.replace(" ", "-")
            
#             # Monster job search URL
#             search_url = f"https://www.monster.com/jobs/search?q={keyword_param}&where={location_param}"
            
#             # Verify the search URL is valid
#             if not self.verify_url(search_url):
#                 search_url = "https://www.monster.com/jobs/search"
            
#             # Create fallback job listings
#             jobs = []
#             for i in range(min(count, 5)):
#                 # Generate realistic fake job listings
#                 company_names = ["IBM", "Oracle", "Intel", "Cisco", "SAP"]
#                 job_types = ["Full-time", "Contract", "Permanent", "Remote", "Hybrid"]
                
#                 jobs.append({
#                     "title": f"{keywords} {['Specialist', 'Consultant', 'Expert', 'Leader', 'Professional'][i % 5]}",
#                     "company": company_names[i % len(company_names)],
#                     "location": location,
#                     "description": f"We are seeking an experienced {keywords} professional for our growing team. This position offers competitive salary and benefits.",
#                     "url": search_url,
#                     "apply_url": search_url,
#                     "date_posted": f"{random.randint(1, 7)} days ago",
#                     "platform": "Monster",
#                     "is_real_job": False
#                 })
            
#             return jobs
            
#         except Exception as e:
#             print(f"Monster search error: {e}")
#             return []
            

            
import pandas as pd
from jobspy import scrape_jobs
import random
import requests
import time
from datetime import datetime, date


class JobScrapper:
    def __init__(self):
        self.platform_map = {
            "LinkedIn": "linkedin",
            "Indeed": "indeed",
            "Glassdoor": "glassdoor",
            "ZipRecruiter": "zip_recruiter",
            "Naukri": "naukri"
        }

        self.job_type_map={
            "Full-time": "fulltime",
            "Part-time": "parttime",
            "Internship":"internship",
            "Contract": "contract"
        }


    def relative_date(self,value):
        """
        Convert date/datetime/string to 'X days ago'
        """
        if not value:
            return "N/A"

        # If already relative text
        if isinstance(value, str) and "day" in value.lower():
            return value

        try:
            # Handle datetime / date
            if isinstance(value, (datetime, date)):
                posted_date = value.date() if isinstance(value, datetime) else value
            else:
                # Handle string date
                posted_date = datetime.strptime(str(value), "%Y-%m-%d").date()

            delta_days = (date.today() - posted_date).days

            if delta_days <= 0:
                return "Today"
            elif delta_days == 1:
                return "1 day ago"
            else:
                return f"{delta_days} days ago"

        except Exception:
            return "N/A"
    
    def search_jobs(self, keywords,search_term, location, platform=["LinkedIn"],count=5,days_ago=2 ,force_fake=False,job_type="Fulltime"):
        
        """Tier 1: Real Scraper (JobSpy) or Skip to Fake."""
        if force_fake:
            return self.get_platform_specific_fake_jobs(keywords, location, platform[0], count=1)

        try:
            flag=False
            print(" ")
            print("===========================================================================================================================")
            print(" ")
            print(keywords,"=>",type(keywords))
            print(search_term,"=>",type(search_term))
            print(location,"=>",type(location))
            print(platform,"=>",type(platform))
            print(count,"=>",type(count))
            print(days_ago,"=>",type(days_ago))
            print(job_type,"=>",type(job_type))
            print(" ")
            print("===========================================================================================================================")

            # site_key = list({
            #                     self.platform_map.get(p, "indeed")
            #                     for p in platform
            #                 })
            site_key = [self.platform_map.get(p,p.lower()) for p in platform]
            total_hours = int(days_ago) * 24
            # 2. Optimized Human-like Delay (Faster but safe)
            time.sleep(3.0)
            keywords+=f" in {location}"
            keywords+=f", within {days_ago} days"
            if location=="Remote":
                flag=True

            print(f"Scraping {site_key} for the last {total_hours} hours for {keywords}...")
            
            job_type_arg=self.job_type_map.get(job_type,job_type.lower())


            print(" ")
            print("===========================================================================================================================")
            print(" ")
            print(keywords,"=>",type(keywords))
            print(search_term,"=>",type(search_term))
            print(location,"=>",type(location))
            print(platform,"=>",type(platform))
            print(count,"=>",type(count))
            print(days_ago,"=>",type(days_ago))
            print(job_type,"=>",type(job_type))
            print(site_key,"=>",type(site_key))
            print(total_hours,"=>",type(total_hours))
            print(job_type_arg,"=>",type(job_type_arg))
            print(" ")
            print("===========================================================================================================================")

            # site_key = list({

            jobs_df = scrape_jobs(
                site_name=site_key,
                search_term=search_term,
                google_search_term=keywords,
                location=location,
                results_wanted=count,
                hours_old=total_hours,
                verbose=2,
                country_indeed="India",
                is_remote=flag,
                job_type=job_type_arg  
            )
            # if not jobs_df.empty:
            #     return self._format_dataframe(jobs_df, platform)
            if jobs_df is not None and not jobs_df.empty:
                # We no longer pass platform[0] here
                raw_jobs = self._format_dataframe(jobs_df)
                print("Scraping finished.")
                
                # # --- DEDUPLICATION ---
                # unique_jobs = []
                # seen_keys = set()
                # for job in raw_jobs:
                #     fingerprint = f"{job['title'].lower()}|{job['company'].lower()}".strip()
                    
                #     if fingerprint not in seen_keys:
                #         seen_keys.add(fingerprint)
                #         unique_jobs.append(job)
                
                return raw_jobs
        except Exception as e:
            print(f"JobSpy Error for {platform}: {e}")
        
        return None # Signal Agent to try SerpAPI

    def get_platform_specific_fake_jobs(self, keywords, location, platform, count=1):
        """Tier 3: Platform-Specific Emergency Safety Net."""
        print(f"Generating platform-specific safety-net for {platform}...")
        
        # Configuration for specific platform 'vibes'
        configs = {
            "LinkedIn": {
                "companies": ["Microsoft", "Google", "Meta", "Apple", "Amazon"],
                "roles": ["Lead", "Director", "Senior Manager", "Principal"],
                "url": "https://www.linkedin.com/jobs"
            },
            "Indeed": {
                "companies": ["Acme Tech", "Global Systems", "InnoTech", "Digital Ventures"],
                "roles": ["Specialist", "Engineer", "Analyst", "Developer"],
                "url": "https://www.indeed.com"
            },
            "Glassdoor": {
                "companies": ["Goldman Sachs", "JP Morgan", "Stripe", "Airbnb"],
                "roles": ["Consultant", "Associate", "Engineer", "Lead"],
                "url": "https://www.glassdoor.com"
            },
            "ZipRecruiter": {
                "companies": ["Pfizer", "Netflix", "Adobe", "Salesforce"],
                "roles": ["Coordinator", "Expert", "Professional", "Lead"],
                "url": "https://www.ziprecruiter.com"
            }
        }

        # Fallback to general if platform not in list
        cfg = configs.get(platform, {
            "companies": ["Tech Corp", "Solutions Ltd"],
            "roles": ["Professional"],
            "url": "https://www.google.com/search?q=jobs"
        })

        jobs = []
        for i in range(count):
            role_suffix = cfg["roles"][i % len(cfg["roles"])]
            jobs.append({
                "title": f"{keywords} {role_suffix}",
                "company": cfg["companies"][i % len(cfg["companies"])],
                "location": location,
                "description": f"Join {cfg['companies'][i % len(cfg['companies'])]} as a {keywords} expert. Competitive salary and benefits.",
                "url": cfg["url"],
                "apply_url": cfg["url"],
                "date_posted": f"{random.randint(1, 4)} days ago",
                "platform": platform,
                "job_type": "Full-time",
                "is_real_job": False 
            })
        return jobs

    # def _format_dataframe(self, df, platform):
    #     return [{
    #         "title": row.get("title", "N/A"),
    #         "company": row.get("company", "N/A"),
    #         "location": row.get("location", "N/A"),
    #         "description": row.get("description", ""),
    #         "url": row.get("job_url", ""),
    #         "apply_url": row.get("job_url_direct") or row.get("job_url", ""),
    #         "date_posted": str(row.get("date_posted", "Recent")),
    #         "job_type": row.get("job_type", "N/A"),
    #         "platform": platform,
    #         "is_real_job": True
    #     } for _, row in df.iterrows()]

    def _format_dataframe(self, df):
        """Simple formatter that uses the platform JobSpy actually found."""
        if df is None or df.empty:
            return []
        
        formatted_list = []
        for _, row in df.iterrows():
            # Get the actual site name from the scraper result (e.g., 'linkedin')
            raw_site = row.get("site", "unknown") 
            
            formatted_list.append({
                "title": row.get("title", "N/A"),
                "company": row.get("company", "N/A"),
                "location": row.get("location", "N/A"),
                "description": row.get("description", ""),
                "url": row.get("job_url", ""),
                "apply_url": row.get("job_url_direct") or row.get("job_url", ""),
                "date_posted": str(self.relative_date(row.get("date_posted",None))),
                "job_type": row.get("job_type", "N/A"),
                "platform": str(raw_site).capitalize(), # Labeled by source
                "is_real_job": True
            })
        return formatted_list



# import random
# import time
# from hashlib import sha1
# from jobspy import scrape_jobs

# def safe_str(value):
#         if value is None:
#             return ""
#         if isinstance(value, float):
#             return ""
#         return str(value)

# class JobScrapper:
#     def __init__(self):
#         self.platform_map = {
#             "LinkedIn": "linkedin",
#             "Indeed": "indeed",
#             "Glassdoor": "glassdoor",
#             "ZipRecruiter": "zip_recruiter",
#             "Naukri": "naukri"
#         }

#     def search_jobs(
#         self,
#         keywords,
#         location,
#         platform=["Indeed"],
#         count=5,
#         days_ago=7,
#         force_fake=False
#     ):
#         """
#         Tier 1: Real scraping via JobSpy
#         Tier 3: Platform-specific fake fallback
#         """

#         if force_fake:
#             return self.get_platform_specific_fake_jobs(
#                 keywords, location, platform[0], count
#             )

#         try:
#             # --- PLATFORM NORMALIZATION (DO NOT CHANGE INPUT) ---
#             site_keys = list(dict.fromkeys(self.platform_map.get(p, "indeed") for p in platform))


#             total_hours = int(days_ago) * 24

#             # Human-like delay
#             time.sleep(random.uniform(2.0, 4.0))

#             print(f"Scraping platforms={site_keys} for last {total_hours} hours")

#             # --- OVERFETCH TO AVOID DUPLICATES ---
#             jobs_df = scrape_jobs(
#                 site_name=site_keys,
#                 search_term=keywords,
#                 location=location,
#                 results_wanted=max(count * 2, 10),   # IMPORTANT
#                 hours_old=total_hours,
#                 verbose=2,
#                 country_indeed="India"
#             )

#             if jobs_df is None or jobs_df.empty:
#                 return None

#             raw_jobs = self._format_dataframe(jobs_df)

#             # --- STRONG DEDUPLICATION ---
#             deduped_jobs = self._deduplicate_jobs(raw_jobs)

#             # --- PLATFORM BALANCING ---
#             balanced_jobs = self._balance_by_platform(
#                 deduped_jobs,
#                 max_per_platform=count
#             )

#             return balanced_jobs

#         except Exception as e:
#             print(f"JobSpy Error for {platform}: {e}")
#             return None  # Signal Agent to fallback

#     # ------------------------------------------------------------------

#     def _deduplicate_jobs(self, jobs):
#         seen = set()
#         unique = []

#         for job in jobs:
#             key_raw = (
#                 f"{safe_str(job.get('title')).lower()}|"
#                 f"{safe_str(job.get('company')).lower()}|"
#                 f"{safe_str(job.get('location')).lower()}|"
#                 f"{safe_str(job.get('apply_url'))}"
#             )

#             fingerprint = sha1(key_raw.encode()).hexdigest()

#             if fingerprint not in seen:
#                 seen.add(fingerprint)
#                 unique.append(job)

#         return unique

#     # ------------------------------------------------------------------

#     def _balance_by_platform(self, jobs, max_per_platform=5):
#         """
#         Prevent Indeed-only domination.
#         """
#         platform_buckets = {}
#         balanced = []

#         for job in jobs:
#             platform = job.get("platform", "Unknown")
#             platform_buckets.setdefault(platform, []).append(job)

#         for platform, items in platform_buckets.items():
#             balanced.extend(items[:max_per_platform])

#         return balanced

#     # ------------------------------------------------------------------
    


#     def _format_dataframe(self, df):
#         formatted = []

#         for _, row in df.iterrows():
#             raw_site = safe_str(row.get("site")) or "indeed"

#             formatted.append({
#                 "title": safe_str(row.get("title")) or "N/A",
#                 "company": safe_str(row.get("company")) or "N/A",
#                 "location": safe_str(row.get("location")) or "N/A",
#                 "description": safe_str(row.get("description")),
#                 "url": safe_str(row.get("job_url")),
#                 "apply_url": safe_str(row.get("job_url_direct")) or safe_str(row.get("job_url")),
#                 "date_posted": safe_str(row.get("date_posted")) or "Recent",
#                 "job_type": safe_str(row.get("job_type")) or "N/A",
#                 "platform": raw_site.capitalize(),
#                 "is_real_job": True
#             })

#         return formatted


#     # ------------------------------------------------------------------

#     def get_platform_specific_fake_jobs(self, keywords, location, platform, count=1):
#         """
#         Safety net – unchanged logic
#         """
#         print(f"Generating platform-specific safety-net for {platform}...")

#         configs = {
#             "LinkedIn": {
#                 "companies": ["Microsoft", "Google", "Meta", "Apple", "Amazon"],
#                 "roles": ["Lead", "Director", "Senior Manager", "Principal"],
#                 "url": "https://www.linkedin.com/jobs"
#             },
#             "Indeed": {
#                 "companies": ["Acme Tech", "Global Systems", "InnoTech", "Digital Ventures"],
#                 "roles": ["Specialist", "Engineer", "Analyst", "Developer"],
#                 "url": "https://www.indeed.com"
#             },
#             "Glassdoor": {
#                 "companies": ["Goldman Sachs", "JP Morgan", "Stripe", "Airbnb"],
#                 "roles": ["Consultant", "Associate", "Engineer", "Lead"],
#                 "url": "https://www.glassdoor.com"
#             },
#             "ZipRecruiter": {
#                 "companies": ["Pfizer", "Netflix", "Adobe", "Salesforce"],
#                 "roles": ["Coordinator", "Expert", "Professional", "Lead"],
#                 "url": "https://www.ziprecruiter.com"
#             }
#         }

#         cfg = configs.get(platform, {
#             "companies": ["Tech Corp", "Solutions Ltd"],
#             "roles": ["Professional"],
#             "url": "https://www.google.com/search?q=jobs"
#         })

#         jobs = []
#         for i in range(count):
#             jobs.append({
#                 "title": f"{keywords} {cfg['roles'][i % len(cfg['roles'])]}",
#                 "company": cfg["companies"][i % len(cfg["companies"])],
#                 "location": location,
#                 "description": f"Join {cfg['companies'][i % len(cfg['companies'])]} as a {keywords} expert.",
#                 "url": cfg["url"],
#                 "apply_url": cfg["url"],
#                 "date_posted": f"{random.randint(1,4)} days ago",
#                 "platform": platform,
#                 "job_type": "Full-time",
#                 "is_real_job": False
#             })

#         return jobs


# # job_scrapper.py
# import random
# import time
# from hashlib import sha1
# from urllib.parse import urlparse
# from playwright.sync_api import sync_playwright
# from playwright_stealth import Stealth


# def safe_str(value):
#     if value is None or isinstance(value, float):
#         return ""
#     return str(value)


# class JobScrapper:

#     def __init__(self):
#         print("[INIT] JobScrapper initialized")

#     # ==========================================================
#     # MAIN ENTRY
#     # ==========================================================
#     def search_jobs(
#         self,
#         keywords,
#         location,
#         platform=["Indeed"],  # <- list from Streamlit multiselect
#         count=5,
#         days_ago=7,
#         force_fake=False
#     ):

#         print(f"\n[SEARCH] keywords='{keywords}', location='{location}', "
#               f"platform={platform}, count={count}, days_ago={days_ago}")

#         if force_fake:
#             print("[MODE] Forced fake job generation")
#             return self.get_platform_specific_fake_jobs(
#                 keywords, location, platform[0], count
#             )

#         try:
#             jobs = self._scrape_google_jobs(
#                 keywords=keywords,
#                 location=location,
#                 platforms=platform,
#                 max_jobs=count * 2,
#                 days_ago=days_ago
#             )

#             if not jobs:
#                 print("[WARN] No jobs scraped from Google")
#                 return None

#             print(f"[INFO] Raw jobs scraped: {len(jobs)}")

#             deduped = self._deduplicate_jobs(jobs)
#             print(f"[INFO] Jobs after deduplication: {len(deduped)}")

#             balanced = self._balance_by_platform(deduped, count)
#             print(f"[INFO] Jobs after platform balancing: {len(balanced)}")

#             return balanced[:count]

#         except Exception as e:
#             print("[ERROR] search_jobs failed:", repr(e))
#             return None

#     # ==========================================================
#     # GOOGLE JOBS SCRAPER
#     # ==========================================================
#     def _scrape_google_jobs(
#         self,
#         keywords,
#         location,
#         platforms,
#         max_jobs,
#         days_ago
#     ):

#         query = f"{keywords} jobs {location}"
#         search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

#         print(f"[SCRAPER] Google search URL: {search_url}")
#         print(f"[SCRAPER] Platforms selected: {platforms}")
#         print(f"[SCRAPER] Max jobs to fetch: {max_jobs}")

#         results = []

#         with sync_playwright() as p:
#             print("[BROWSER] Launching Playwright Chromium")
#             browser = p.chromium.launch(
#                 headless=False,  # True=background, False=see browser
#                 args=["--disable-blink-features=AutomationControlled"]
#             )

#             context = browser.new_context(
#                 viewport={"width": 1366, "height": 768},
#                 locale="en-US",
#                 user_agent=(
#                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                     "AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/120.0.0.0 Safari/537.36"
#                 ),
#                 java_script_enabled=True,
#                 bypass_csp=True,
#                 ignore_https_errors=True
#             )

#             print("[BROWSER] New isolated browser context created (SAFE)")
#             page = context.new_page()

#             # ✅ STEALTH
#             stealth = Stealth()
#             stealth.apply_stealth_sync(page)
#             print("[STEALTH] Stealth mode applied")

#             print("[NAVIGATE] Opening Google search page")
#             page.goto(search_url, timeout=60000)
#             time.sleep(random.uniform(2, 3))

#             print("[ACTION] Attempting to click Jobs tab")
#             try:
#                 page.click("a:has-text('Jobs'), div[jsname='tUj3bd'] a", timeout=5000)
#                 print("[OK] Jobs tab clicked")
#                 time.sleep(2)
#             except Exception as e:
#                 print("[WARN] Jobs tab not clickable, continuing without tab:", repr(e))

#             print("[WAIT] Waiting for job cards to load")
#             try:
#                 page.wait_for_selector("div.gws-plugins-horizon-jobs__li", timeout=15000)
#                 print("[OK] Job cards detected")
#             except Exception as e:
#                 print("[ERROR] Job cards not found:", repr(e))
#                 browser.close()
#                 return []

#             cards = page.locator("div.gws-plugins-horizon-jobs__li")
#             card_count = min(cards.count(), max_jobs)
#             print(f"[SCRAPER] Job cards found: {cards.count()}")
#             print(f"[SCRAPER] Processing top {card_count} jobs")

#             for i in range(card_count):
#                 print(f"[JOB] Processing card {i + 1}")
#                 card = cards.nth(i)

#                 def txt(sel):
#                     try:
#                         return card.locator(sel).inner_text(timeout=1500)
#                     except:
#                         return ""

#                 title = txt("h2")
#                 company = txt(".vNEEBe")
#                 job_location = txt(".Qk80Jf")
#                 date_posted = txt(".LL4CDc") or "Recent"

#                 try:
#                     link = card.locator("a").first.get_attribute("href")
#                 except:
#                     link = ""

#                 # ✅ Platform detection
#                 job_platform = self._extract_platform(link)

#                 # ✅ Filter using Streamlit multiselect
#                 if job_platform not in platforms:
#                     print(f"[SKIP] Job skipped: platform '{job_platform}' not selected")
#                     continue

#                 if not self._within_days(date_posted, days_ago):
#                     print(f"[SKIP] Job skipped: older than {days_ago} days")
#                     continue

#                 results.append({
#                     "title": title or "N/A",
#                     "company": company or "N/A",
#                     "location": job_location or location,
#                     "description": "",
#                     "url": link,
#                     "apply_url": link,
#                     "date_posted": date_posted,
#                     "job_type": "N/A",
#                     "platform": job_platform,
#                     "is_real_job": True
#                 })

#                 print(f"[ADD] {title} | {company} | {job_platform}")

#             print("[BROWSER] Closing browser")
#             browser.close()

#         print(f"[DONE] Total jobs collected: {len(results)}")
#         return results

#     # ==========================================================
#     # HELPERS
#     # ==========================================================
#     def _extract_platform(self, url):
#         if not url:
#             return "Unknown"
#         domain = urlparse(url).netloc.lower()
#         if "linkedin" in domain:
#             return "LinkedIn"
#         elif "indeed" in domain:
#             return "Indeed"
#         elif "glassdoor" in domain:
#             return "Glassdoor"
#         elif "ziprecruiter" in domain:
#             return "ZipRecruiter"
#         elif "naukri" in domain:
#             return "Naukri"
#         return domain.split(".")[0]

#     def _within_days(self, text, days):
#         try:
#             n = int(text.split()[0])
#             return n <= days
#         except:
#             return True

#     def _deduplicate_jobs(self, jobs):
#         print("[DEDUP] Running deduplication")
#         seen = set()
#         unique = []

#         for job in jobs:
#             key = (
#                 f"{safe_str(job['title']).lower()}|"
#                 f"{safe_str(job['company']).lower()}|"
#                 f"{safe_str(job['location']).lower()}|"
#                 f"{safe_str(job['apply_url'])}"
#             )

#             fp = sha1(key.encode()).hexdigest()
#             if fp not in seen:
#                 seen.add(fp)
#                 unique.append(job)

#         return unique

#     def _balance_by_platform(self, jobs, max_per_platform):
#         print("[BALANCE] Balancing jobs by platform")
#         buckets = {}
#         balanced = []

#         for job in jobs:
#             p = job.get("platform", "Unknown")
#             buckets.setdefault(p, []).append(job)

#         for p, items in buckets.items():
#             balanced.extend(items[:max_per_platform])

#         return balanced

#     # ==========================================================
#     # FAKE FALLBACK
#     # ==========================================================
#     def get_platform_specific_fake_jobs(self, keywords, location, platform, count=1):
#         print(f"[FAKE] Generating fake jobs for {platform}")
#         jobs = []
#         for i in range(count):
#             jobs.append({
#                 "title": f"{keywords} Specialist",
#                 "company": "Demo Corp",
#                 "location": location,
#                 "description": f"Demo job for {keywords}",
#                 "url": "https://www.google.com/search?q=jobs",
#                 "apply_url": "https://www.google.com/search?q=jobs",
#                 "date_posted": f"{random.randint(1,3)} days ago",
#                 "platform": platform,
#                 "job_type": "Full-time",
#                 "is_real_job": False
#             })
#         return jobs
