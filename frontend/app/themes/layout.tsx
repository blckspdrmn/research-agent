import { fetchThemes } from "@/lib/api/themes";
import { ResearchWatcher } from "./_components/ResearchWatcher";

export default async function ThemesLayout({
  children,
}: LayoutProps<"/themes">) {
  const themes = await fetchThemes();

  return (
    <>
      <ResearchWatcher themes={themes} />
      {children}
    </>
  );
}
