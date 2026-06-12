import { notFound } from "next/navigation";
import type { Metadata } from "next";
import { publicApi } from "@/lib/api/public";
import { ThemeProvider } from "@/components/cv/ThemeProvider";
import { layoutRegistry } from "@/components/cv/layouts";
import { SingleColumnLayout } from "@/components/cv/layouts/SingleColumnLayout";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    const data = await publicApi.getFacet(slug);
    return {
      title: data.meta_title || `${data.full_name}${data.title ? ` - ${data.title}` : ""}`,
      description: data.meta_description || data.bio || undefined,
    };
  } catch {
    return { title: "Página no encontrada" };
  }
}

export default async function PublicFacetPage({ params }: Props) {
  const { slug } = await params;

  let data;
  try {
    data = await publicApi.getFacet(slug);
  } catch {
    notFound();
  }

  const Layout = layoutRegistry[data.web_layout] ?? SingleColumnLayout;

  return (
    <ThemeProvider tokens={data.theme_tokens ?? {}}>
      <Layout data={data} />
    </ThemeProvider>
  );
}
