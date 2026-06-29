import "@/index.css";

import type { ReactNode } from "react";
import { RootProvider } from "fumadocs-ui/provider/next";
import { Toaster } from "sonner";

import { defaultMetadata } from "@/lib/metadata";

export const metadata = defaultMetadata;

export default function RootLayout({ children }: { children: ReactNode }) {
	return (
		<html lang="en" suppressHydrationWarning>
			<body className="min-h-[100dvh] bg-background text-foreground antialiased">
				<RootProvider
					theme={{
						attribute: "class",
						defaultTheme: "system",
						enableSystem: true,
						disableTransitionOnChange: true,
					}}
				>
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