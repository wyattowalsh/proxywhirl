"use client";

import { lazy, Suspense } from "react";
import Link from "next/link";
import { ArrowLeft, RefreshCw, AlertTriangle, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useProxyData } from "@/providers/ProxyDataProvider";

const AnalyticsDashboard = lazy(() =>
	import("@/components/analytics/AnalyticsDashboard").then((m) => ({
		default: m.AnalyticsDashboard,
	})),
);

function LoadingSkeleton() {
	return (
		<div className="space-y-8">
			<div className="grid gap-6 md:grid-cols-3">
				<Skeleton className="h-[300px]" />
				<Skeleton className="h-[300px]" />
				<Skeleton className="h-[300px]" />
			</div>
			<Skeleton className="h-[500px]" />
			<div className="grid gap-6 md:grid-cols-2">
				<Skeleton className="h-[400px]" />
				<Skeleton className="h-[400px]" />
			</div>
		</div>
	);
}

export function AnalyticsPage() {
	const {
		stats,
		statsLoading,
		statsError,
		refreshStats,
		richData,
		richLoading,
		richError,
		refreshRich,
	} = useProxyData();

	const isLoading = statsLoading || richLoading;
	const hasError = statsError || richError;
	const hasData = stats && richData?.proxies && richData.proxies.length > 0;

	const handleRefresh = () => {
		refreshStats();
		refreshRich();
	};

	return (
		<div className="space-y-8">
			{/* Header */}
			<div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
				<div className="flex items-center gap-4">
					<Button variant="ghost" size="icon" asChild>
						<Link href="/" aria-label="Back to home">
							<ArrowLeft className="h-5 w-5" aria-hidden="true" />
						</Link>
					</Button>
					<div>
						<h1 className="text-3xl font-bold tracking-tight flex items-center gap-3">
							<BarChart3 className="h-8 w-8 text-primary" aria-hidden="true" />
							Analytics Dashboard
						</h1>
						<p className="text-muted-foreground mt-1">
							Comprehensive proxy health, performance, and geographic insights
						</p>
					</div>
				</div>
				<Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
					<RefreshCw
						className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`}
						aria-hidden="true"
					/>
					Refresh Data
				</Button>
			</div>

			{/* Error state */}
			{hasError && !isLoading && (
				<section aria-labelledby="analytics-error-heading">
					<div className="rounded-lg border border-destructive/50 bg-destructive/5 p-6">
						<div className="flex items-start gap-4">
							<AlertTriangle className="h-6 w-6 text-destructive shrink-0 mt-0.5" aria-hidden="true" />
							<div className="flex-1">
								<h2 id="analytics-error-heading" className="font-semibold text-destructive">
									Failed to load data
								</h2>
								<p className="text-sm text-muted-foreground mt-1">
									{statsError || richError}
								</p>
								<Button
									variant="outline"
									size="sm"
									className="mt-3"
									onClick={handleRefresh}
								>
									<RefreshCw className="h-4 w-4 mr-2" aria-hidden="true" />
									Try Again
								</Button>
							</div>
						</div>
					</div>
				</section>
			)}

			{/* Loading state */}
			{isLoading && (
				<section aria-labelledby="analytics-loading-heading">
					<h2 id="analytics-loading-heading" className="sr-only">
						Loading analytics data
					</h2>
					<LoadingSkeleton />
				</section>
			)}

			{/* Main dashboard */}
			{!isLoading && hasData && (
				<section aria-labelledby="analytics-dashboard-heading">
					<h2 id="analytics-dashboard-heading" className="sr-only">
						Analytics charts and metrics
					</h2>
					<Suspense fallback={<LoadingSkeleton />}>
						<AnalyticsDashboard stats={stats} proxies={richData.proxies} />
					</Suspense>
				</section>
			)}

			{/* No data state */}
			{!isLoading && !hasError && !hasData && (
				<section aria-labelledby="analytics-empty-heading">
					<div className="rounded-lg border p-12 text-center">
						<BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" aria-hidden="true" />
						<h2 id="analytics-empty-heading" className="text-lg font-semibold">
							No Analytics Data
						</h2>
						<p className="text-muted-foreground mt-1">
							Proxy data is not available yet. Please check back later.
						</p>
						<Button variant="outline" className="mt-4" asChild>
							<Link href="/">Return Home</Link>
						</Button>
					</div>
				</section>
			)}
		</div>
	);
}