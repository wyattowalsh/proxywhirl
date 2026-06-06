import type { ReactNode } from "react";
import { Header } from "./Header";
import { Footer } from "./Footer";

export function Layout({ children }: { children: ReactNode }) {
	return (
		<div className="relative flex min-h-[100dvh] flex-col">
			<a
				href="#main-content"
				className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[60] focus:rounded-md focus:bg-background focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:shadow"
			>
				Skip to content
			</a>
			<Header />
			<main id="main-content" className="container flex-1 py-6">
				{children}
			</main>
			<Footer />
		</div>
	);
}
