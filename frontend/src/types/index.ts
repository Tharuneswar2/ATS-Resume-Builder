export interface BasicInfoLinks {
  linkedin?: string;
  github?: string;
  portfolio?: string;
  shortlist_live?: string;
  debugignore_docs?: string;
  other_links?: Record<string, string>;
}

export interface BasicInfo {
  name: string;
  title: string;
  email: string;
  phone?: string;
  location?: string;
  links: BasicInfoLinks;
}

export interface ProfessionalSummary {
  experience_years: number;
  core_identity: string;
  domains: string[];
  key_strengths: string[];
  target_company_alignment: string[];
}

export interface Skills {
  programming: string[];
  ml_ai: string[];
  backend: string[];
  distributed_systems: string[];
  databases: string[];
  data_processing: string[];
  computer_vision: string[];
  cloud_devops: string[];
  developer_tooling: string[];
  tools: string[];
  automation: string[];
  software_engineering: string[];
  extra_categories?: Record<string, string[]>;
}

export interface ImpactItem {
  area: string;
  achievement: string;
  method: string;
}

export interface Experience {
  company: string;
  role: string;
  type?: string;
  responsibilities: string[];
  impact: ImpactItem[];
  tech_stack: string[];
  faang_alignment: string[];
}

export interface OpenSourceProjectLinks {
  documentation?: string;
  github?: string;
}

export interface OpenSourceProject {
  name: string;
  type: string;
  links: OpenSourceProjectLinks;
  highlights: string[];
  core_engineering_concepts: string[];
  tech_stack: string[];
  target_company_alignment: string[];
}

export interface Project {
  name: string;
  category: string[];
  live_link?: string;
  github_link?: string;
  highlights: string[];
  tech_stack: string[];
  faang_alignment: string[];
}

export interface Education {
  degree: string;
  institution: string;
  status?: string;
  duration?: string;
}

export interface Certification {
  name: string;
  provider: string;
}

export interface AchievementBankItem {
  tags: string[];
  text: string;
}

export interface Preferences {
  target_roles: string[];
  work_type: string[];
  industries: string[];
  target_companies: string[];
}

export interface WritingStyle {
  tone: string;
  style: string;
  rules: string[];
}

export interface Profile {
  _id?: string;
  basic_info: BasicInfo;
  professional_summary: ProfessionalSummary;
  skills: Skills;
  experience: Experience[];
  open_source_projects: OpenSourceProject[];
  projects: Project[];
  education: Education[];
  certifications: Certification[];
  awards: string[];
  achievement_bank: AchievementBankItem[];
  preferences: Preferences;
  writing_style: WritingStyle;
}

export interface JDAnalysis {
  role: string;
  company?: string;
  required_skills: string[];
  preferred_skills: string[];
  keywords: string[];
  years_of_experience?: number;
  responsibilities: string[];
}

export interface JDScore {
  overall_match: number;
  matched_keywords: string[];
  missing_keywords: string[];
}
