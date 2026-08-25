import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Job, JobFilters, JobUpdate, Stats } from '../models/job.model';

const API = 'http://localhost:8000/api';

@Injectable({ providedIn: 'root' })
export class JobService {
  constructor(private http: HttpClient) {}

  getJobs(filters: JobFilters = {}): Observable<Job[]> {
    let params = new HttpParams();
    if (filters.keyword)     params = params.set('keyword', filters.keyword);
    if (filters.min_score)   params = params.set('min_score', filters.min_score);
    if (filters.remote_only) params = params.set('remote_only', filters.remote_only);
    if (filters.seen != null) params = params.set('seen', filters.seen);
    if (filters.applied != null) params = params.set('applied', filters.applied);
    if (filters.limit)       params = params.set('limit', filters.limit);
    if (filters.offset)      params = params.set('offset', filters.offset ?? 0);
    return this.http.get<Job[]>(`${API}/jobs`, { params });
  }

  getJob(id: string): Observable<Job> {
    return this.http.get<Job>(`${API}/jobs/${id}`);
  }

  updateJob(id: string, update: JobUpdate): Observable<Job> {
    return this.http.patch<Job>(`${API}/jobs/${id}`, update);
  }

  getStats(): Observable<Stats> {
    return this.http.get<Stats>(`${API}/stats`);
  }
}
