import { Suspense } from "react";
import { Layout } from "@/components/layout/Layout";
import { Skeleton } from "@/components/ui/skeleton";
import { Home } from "@/screens/Home";

export default function Page() {
	return (
		<Layout>
			<Suspense fallback={<Skeleton className="h-[500px]" />}>
				<Home />
			</Suspense>
		</Layout>
	);
}
