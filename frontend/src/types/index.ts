export type CRMStage = 'NEW' | 'ENRICHED' | 'CONTACTED' | 'IN_DISCUSSION' | 'WON' | 'LOST';

export interface SalesGap {
  code: string;
  title: string;
  description: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  pitch_angle: string;
  suggested_solution: string;
}

export interface Lead {
  id: number;
  place_id: string;
  name: string;
  category: string;
  city: string;
  address: string;
  latitude?: number;
  longitude?: number;
  phone: string;
  website: string;
  rating?: number;
  review_count: number;
  google_maps_url: string;

  // Contacts
  emails: string[];
  phones: string[];
  whatsapp: string;
  instagram: string;
  facebook: string;
  linkedin: string;
  twitter: string;
  youtube: string;

  // Audit
  has_website: boolean;
  has_ssl: boolean;
  meta_title: string;
  meta_description: string;

  // Sales Opportunity
  opportunity_score: number;
  gaps: SalesGap[];
  primary_gap: string;

  // CRM
  crm_stage: CRMStage;
  notes: string;
  last_contacted_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Stats {
  total_leads: number;
  with_email: number;
  with_phone: number;
  with_whatsapp: number;
  missing_website: number;
  high_opportunity: number;
  pipeline_stages: Record<CRMStage, number>;
}
