from fastapi import APIRouter, Query, HTTPException
from typing import List
import json
from ...services.job_service import search_jobs
from ...core.cache import redis

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/search")
async def search_jobs_endpoint(
    search_term: str = Query(..., min_length=3, description="Required: job keywords (e.g. 'Junior AI Engineer')"),
    location: str = Query(..., min_length=2, description="Required: location (e.g. 'Cork, Ireland', 'Remote Europe')"),
    days_old: int = Query(..., ge=1, le=90, description="Required: max age of postings in days"),
    max_results: int = Query(..., ge=5, le=50, description="Required: number of results (5-50)"),
    sources: str = Query(..., description="Required: comma-separated sources (e.g. 'linkedin,indeed,glassdoor')"),
    force_refresh: bool = Query(False, description="Force fresh scrape (ignores cache)")
):
    """
    Search for jobs using JobSpy across multiple platforms.
    Returns list of jobs with id, title, company, description, url.
    """
    if not search_term.strip() or not location.strip() or not sources.strip():
        raise HTTPException(400, "search_term, location, and sources are required")

    source_list = [s.strip() for s in sources.split(",") if s.strip()]
    if not source_list:
        raise HTTPException(400, "At least one source is required")

    jobs = search_jobs(
        search_term=search_term,
        location=location,
        days_old=days_old,
        max_results=max_results,
        sources=source_list,
        force_refresh=force_refresh
    )

    return {
        "status": "success",
        "count": len(jobs),
        "search_params": {
            "term": search_term,
            "location": location,
            "days_old": days_old,
            "max_results": max_results,
            "sources": source_list
        },
        "jobs": jobs
    }


@router.get("/{job_id}")
async def get_job_by_id(job_id: str):
    """
    Fetch a single job by ID from cache.
    Use this after /search to get full job details for tailoring.
    """
    if not redis:
        raise HTTPException(503, "Cache unavailable. Run /search first and use job from response.")

    # Scan all jobs:* keys in Redis
    for key in redis.scan_iter("jobs:*"):
        cached = redis.get(key)
        if cached:
            jobs = json.loads(cached)
            for job in jobs:
                if job.get("id") == job_id:
                    return {"status": "success", "job": job}

    raise HTTPException(404, f"Job '{job_id}' not found in cache. Run /search first.")
