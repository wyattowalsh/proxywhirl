import type { ReactNode } from "react";
import { Header } from "./Header";
import { Footer } from "./Footer";

export function Layout({ children }: { children: ReactNode }) {
	return (
		<div className="relative min-h-screen flex flex-col">
			<Header />
			<main className="flex-1 container py-6">{children}</main>
			<Footer />
		</div>
	);
}
