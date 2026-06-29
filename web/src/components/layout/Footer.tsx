import Link from "next/link";

import { proxyListLinks, siteNavLinks } from "@/lib/site-nav";

export function Footer() {
	const footerNavLinks = siteNavLinks.filter(
		(link) => link.label === "Docs" || link.label === "Analytics",
	);

	return (
		<footer className="border-t py-6 md:py-0">
			<div className="container flex flex-col gap-4 py-4 md:py-6">
				<div className="flex flex-col items-center justify-between gap-4 md:flex-row">
					<p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
						Built with{" "}
						<a
							href="https://github.com/wyattowalsh/proxywhirl"
							target="_blank"
							rel="noopener noreferrer"
							className="font-medium underline underline-offset-4"
						>
							ProxyWhirl
						</a>
						. Proxy lists updated every 6 hours.
					</p>
					<nav
						aria-label="Footer navigation"
						className="flex flex-wrap items-center justify-center gap-4 text-sm text-muted-foreground"
					>
						{footerNavLinks.map((link) => (
							<Link
								key={link.href}
								href={link.href}
								className="transition-colors hover:text-foreground"
							>
								{link.label}
							</Link>
						))}
					</nav>
				</div>
				<nav
					aria-label="Proxy list downloads"
					className="flex flex-wrap items-center justify-center gap-4 text-sm text-muted-foreground md:justify-start"
				>
					{proxyListLinks.map((link) => (
						<a
							key={link.href}
							href={link.href}
							className="transition-colors hover:text-foreground"
						>
							{link.label}
						</a>
					))}
				</nav>
				<p className="text-center text-sm text-muted-foreground md:text-right">
					Free and open source.
				</p>
			</div>
		</footer>
	);
}