import { Suspense } from "react";
import { Layout } from "@/components/layout/Layout";
import { Skeleton } from "@/components/ui/skeleton";
import { AnalyticsPage } from "@/screens/AnalyticsPage";
import { createPageMetadata } from "@/lib/metadata";

export const metadata = createPageMetadata({
	title: "Analytics",
	description: "ProxyWhirl proxy health, performance, and geography analytics.",
	path: "/analytics",
});

export default function Page() {
	return (
		<Layout>
			<Suspense fallback={<Skeleton className="h-[500px]" />}>
				<AnalyticsPage />
			</Suspense>
		</Layout>
	);
}
