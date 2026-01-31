from jobspy import scrape_jobs
from typing import List, Dict
import json
from datetime import datetime, timezone
from ..core.cache import redis

def search_jobs(
        search_term: str,
        location: str,
        days_old: int,
        max_results: int,
        sources: List[str],
        force_refresh: bool = False
) -> List[Dict]:
    """
    100% user-controlled job search.
    All parameters are required and come from frontend.
    Cache key is unique per exact combination of parameters.
    """
    if not search_term.strip():
        raise ValueError("search term is required")
    if not location.strip():
        raise ValueError("location is required")
    if days_old < 1 or days_old > 90:
        raise ValueError("days_old must be between 1 and 90")
    if max_results < 5 or max_results > 50:
        raise ValueError("max_results must be between 5 and 50")
    if not sources:
        raise ValueError("sources list is required (e.g. ['linkedin', indeed'])")

    cache_key = f"jobs:{search_term}:{location}:{days_old}:{max_results}:{','.join(sorted(sources))}"

    cached = redis.get(cache_key)
    if cached and not force_refresh:
        return json.loads(cached)

    try:
        jobs_df = scrape_jobs(
            site_name=sources,
            search_term=search_term,
            location=location,
            results_wanted=max_results,
            hours_old=days_old * 24,
            linkedin_fetch_description=True
        )

        if jobs_df.empty:
            return []

        jobs = jobs_df.to_dict("records")

        normalized = []
        for job in jobs:
            normalized.append({
                "id": f"{job.get('site','unknown')}_{job.get('job_id', hash(job.get('title', '')))}",
                "title": job.get("title","N/A"),
                "company": job.get("company", "N/A"),
                "location": job.get("location","N/A"),
                "posted": str(job.get("date_posted", "Recent")),
                "description": job.get("description", ""),
                "url": job.get("job_url", ""),
                "source": job.get("site", "unknown"),
                "salary": job.get("salary", None),
                "search_params": {
                    "term": search_term,
                    "location": location,
                    "days_old": days_old,
                    "max_results": max_results,
                    "sources": sources
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

        redis.set(cache_key, json.dumps(normalized), ex=7200) # 2 hours TTL

        return normalized

    except Exception as e:
        print(f"Job search failed: {str(e)}")
        return []
