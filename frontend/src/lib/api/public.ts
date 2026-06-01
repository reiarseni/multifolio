export interface PublicProjectImage {
  id: string;
  image_url: string;
  caption: string | null;
}

export interface PublicProject {
  id: string;
  title: string;
  description: string | null;
  cover_image_url: string | null;
  markdown_content: string | null;
  github_url: string | null;
  live_url: string | null;
  images: PublicProjectImage[];
}

export interface PublicExperience {
  id: string;
  company: string;
  position: string;
  description: string | null;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  location: string | null;
}

export interface PublicEducation {
  id: string;
  institution: string;
  degree: string;
  field: string | null;
  description: string | null;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
}

export interface PublicSkill {
  id: string;
  name: string;
  category: string | null;
  level: string | null;
  is_transversal: boolean;
}

export interface PublicCertification {
  id: string;
  name: string;
  issuer: string;
  issue_date: string | null;
  credential_url: string | null;
}

export interface PublicFacetResponse {
  slug: string;
  title: string | null;
  bio: string | null;
  meta_title: string | null;
  meta_description: string | null;
  pdf_template: string;
  full_name: string;
  email: string;
  phone: string | null;
  photo_url: string | null;
  website: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  experiences: PublicExperience[];
  educations: PublicEducation[];
  skills: PublicSkill[];
  certifications: PublicCertification[];
  projects: PublicProject[];
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const publicApi = {
  getFacet: (slug: string) =>
    fetch(`${BASE_URL}/${slug}`).then((res) => {
      if (!res.ok) throw new Error("Not found");
      return res.json() as Promise<PublicFacetResponse>;
    }),
};
