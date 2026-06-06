import "@/index.css";

import type { Metadata } from "next";
import type { ReactNode } from "react";
import { RootProvider } from "fumadocs-ui/provider/next";
import { Toaster } from "sonner";

export const metadata: Metadata = {
	title: {
		default: "ProxyWhirl",
		template: "%s | ProxyWhirl",
	},
	description:
		"Production-grade proxy rotation for Python with live proxy lists and canonical docs.",
	icons: {
		icon: [{ url: "/favicon.svg", type: "image/svg+xml" }],
		shortcut: ["/favicon.svg"],
	},
};

export default function RootLayout({ children }: { children: ReactNode }) {
	return (
		<html lang="en" suppressHydrationWarning>
			<body className="min-h-[100dvh] bg-background text-foreground antialiased">
				<RootProvider>
					{children}
					<Toaster
						position="bottom-right"
						toastOptions={{
							className: "border bg-background text-foreground",
						}}
					/>
				</RootProvider>
			</body>
		</html>
	);
}
