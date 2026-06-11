import type { PublicFacetResponse } from "@/lib/api/public";
import { CVHeader } from "@/components/cv/CVHeader";
import { CVExperience } from "@/components/cv/CVExperience";
import { CVEducation } from "@/components/cv/CVEducation";
import { CVSkills } from "@/components/cv/CVSkills";
import { CVProjects } from "@/components/cv/CVProjects";

export function SingleColumnLayout({ data }: { data: PublicFacetResponse }) {
  return (
    <div
      className="max-w-3xl mx-auto p-6"
      style={{ backgroundColor: "var(--color-background, white)", fontFamily: "var(--font-body, inherit)" }}
    >
      <CVHeader data={data} />
      <CVExperience items={data.experiences} />
      <CVEducation items={data.educations} />
      <CVSkills items={data.skills} />
      <CVProjects items={data.projects} />
    </div>
  );
}
