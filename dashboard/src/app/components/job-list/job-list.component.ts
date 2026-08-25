import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { Job, JobFilters, Stats } from '../../models/job.model';
import { JobService } from '../../services/job.service';

@Component({
  selector: 'app-job-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './job-list.component.html',
  styleUrl: './job-list.component.scss',
})
export class JobListComponent implements OnInit {
  jobs: Job[] = [];
  stats: Stats | null = null;

  filters: JobFilters = {
    min_score: 0,
    remote_only: false,
    limit: 50,
    offset: 0,
  };

  keyword = '';

  constructor(private jobService: JobService) {}

  ngOnInit(): void {
    this.loadStats();
    this.loadJobs();
  }

  loadJobs(): void {
    const f = { ...this.filters };
    if (this.keyword.trim()) f.keyword = this.keyword.trim();
    this.jobService.getJobs(f).subscribe(jobs => (this.jobs = jobs));
  }

  loadStats(): void {
    this.jobService.getStats().subscribe(stats => (this.stats = stats));
  }

  markSeen(job: Job): void {
    this.jobService.updateJob(job.id, { seen: true }).subscribe(updated => {
      const idx = this.jobs.findIndex(j => j.id === updated.id);
      if (idx !== -1) this.jobs[idx] = updated;
      this.loadStats();
    });
  }

  markApplied(job: Job): void {
    this.jobService.updateJob(job.id, { applied: true }).subscribe(updated => {
      const idx = this.jobs.findIndex(j => j.id === updated.id);
      if (idx !== -1) this.jobs[idx] = updated;
      this.loadStats();
    });
  }

  onFilterChange(): void {
    this.filters.offset = 0;
    this.loadJobs();
  }

  nextPage(): void {
    this.filters.offset = (this.filters.offset ?? 0) + (this.filters.limit ?? 50);
    this.loadJobs();
  }

  prevPage(): void {
    this.filters.offset = Math.max(0, (this.filters.offset ?? 0) - (this.filters.limit ?? 50));
    this.loadJobs();
  }
}
