export interface Clinic {
  id: string;
  name: string;
  slug: string;
  description?: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  latitude?: number;
  longitude?: number;
  phone: string;
  email: string;
  website?: string;
  fax?: string;
  logo?: string;
  primary_color?: string;
  secondary_color?: string;
  cover_image?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  settings?: any;
}

export interface Service {
  id: string;
  clinic: string;
  name: string;
  description?: string;
  estimated_duration: number;
  code?: string;
  display_order: number;
  is_active: boolean;
}

export interface Queue {
  id: string;
  clinic: string;
  date: string;
  is_active: boolean;
  opened_at?: string;
  closed_at?: string;
  total_tickets: number;
  waiting: number;
  called: number;
  serving: number;
  completed: number;
  cancelled: number;
  no_show: number;
  avg_wait_time: number;
  avg_service_time: number;
  current_wait_time: number;
}

export interface Ticket {
  id: string;
  queue: string;
  clinic: string;
  service?: string;
  ticket_number: string;
  patient_name: string;
  patient_phone: string;
  patient_email?: string;
  status: string;
  priority: string;
  position: number;
  estimated_wait_time: number;
  is_walkin: boolean;
  joined_at: string;
  called_at?: string;
  serving_started_at?: string;
  completed_at?: string;
  cancelled_at?: string;
  called_by?: string;
  served_by?: string;
  notes?: string;
  clinic_name?: string;
  service_name?: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  role: string;
  clinic?: string;
  clinic_name?: string;
  is_active: boolean;
  is_staff?: boolean;
  full_name?: string;
}

export interface StaffClinicContext {
  clinic: Clinic;
  settings: any;
  permissions: {
    can_edit_settings: boolean;
    can_manage_services: boolean;
    role: string;
  };
}

export interface StaffClinicKpis {
  date: string;
  waiting: number;
  avg_wait: number;
  completed: number;
  no_show: number;
}

export interface PublicStats {
  total_patients: number;
  partner_clinics: number;
  open_queues: number;
  in_queue: number;
  serving_now: number;
  next_available_time: string;
}

export interface AdminOverview {
  from: string;
  to: string;
  total_clinics: number;
  active_clinics: number;
  tickets_today: number;
  tickets_week: number;
  tickets_month: number;
  total_tickets: number;
  total_queues: number;
  total_users: number;
  active_users: number;
  total_services: number;
  avg_wait_time: number;
  no_show_rate: number;
  notifications_total: number;
  notifications_delivery_rate: number;
  status_counts: Array<{ status: string; total: number }>;
  priority_counts: Array<{ priority: string; total: number }>;
  system_status: {
    api: string;
    db: string;
    websocket: string;
  };
  top_clinics: Array<{ name: string; total: number }>;
}

export interface AdminAuditLog {
  id: string;
  actor: string | null;
  actor_name?: string;
  actor_email?: string;
  clinic: string | null;
  clinic_name?: string;
  action_type: string;
  entity_type: string;
  entity_id?: string;
  before_data?: any;
  after_data?: any;
  metadata?: any;
  created_at: string;
}

export interface AdminSystemSettings {
  id: string;
  twilio_config: any;
  smtp_config: any;
  sms_template: string;
  email_template: string;
  default_queue_rules: any;
  maintenance_mode: boolean;
  maintenance_banner: string;
  data_retention_days: number;
  allowed_countries: string[];
  allowed_phone_formats: string[];
}
