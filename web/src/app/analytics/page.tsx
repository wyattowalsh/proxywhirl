import { Suspense } from "react";
import { Layout } from "@/components/layout/Layout";
import { Skeleton } from "@/components/ui/skeleton";
import { AnalyticsPage } from "@/screens/AnalyticsPage";

export const metadata = {
	title: "Analytics",
	description: "ProxyWhirl proxy health, performance, and geography analytics.",
};

export default function Page() {
	return (
		<Layout>
			<Suspense fallback={<Skeleton className="h-[500px]" />}>
				<AnalyticsPage />
			</Suspense>
		</Layout>
	);
}
