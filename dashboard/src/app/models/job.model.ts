export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  url: string;
  source: string;
  posted_date: string;
  description: string;
  salary: string | null;
  remote: 0 | 1;
  seen: 0 | 1;
  applied: 0 | 1;
  notes: string | null;
  relevance_score: number | null;
}

export interface JobFilters {
  keyword?: string;
  min_score?: number;
  remote_only?: boolean;
  seen?: boolean;
  applied?: boolean;
  limit?: number;
  offset?: number;
}

export interface Stats {
  total: number;
  unseen: number;
  applied: number;
  avg_score: number | null;
}

export interface JobUpdate {
  seen?: boolean;
  applied?: boolean;
  notes?: string;
}
