"use client";

import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { siteNavLinks } from "@/lib/site-nav";
import { BarChart3, BookOpen, Github, Menu, Moon, Sun } from "lucide-react";
import Link from "next/link";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

function ProxyWhirlLogo({ className }: { className?: string }) {
	return (
		<svg viewBox="0 0 100 100" className={className} aria-hidden="true">
			<defs>
				<linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
					<stop offset="0%" stopColor="#06b6d4" />
					<stop offset="50%" stopColor="#3b82f6" />
					<stop offset="100%" stopColor="#8b5cf6" />
				</linearGradient>
			</defs>
			<circle
				cx="50"
				cy="50"
				r="44"
				fill="none"
				stroke="url(#logoGradient)"
				strokeWidth="6"
				strokeLinecap="round"
				strokeDasharray="60 30"
			/>
			<g fill="url(#logoGradient)">
				<path d="M50 18 L58 30 L52 30 L52 42 L48 42 L48 30 L42 30 Z" />
				<path d="M82 50 L70 58 L70 52 L58 52 L58 48 L70 48 L70 42 Z" />
				<path d="M50 82 L42 70 L48 70 L48 58 L52 58 L52 70 L58 70 Z" />
				<path d="M18 50 L30 42 L30 48 L42 48 L42 52 L30 52 L30 58 Z" />
			</g>
			<circle cx="50" cy="50" r="8" fill="url(#logoGradient)" />
		</svg>
	);
}

const navIcons = {
	Docs: BookOpen,
	Analytics: BarChart3,
	GitHub: Github,
} as const;

function NavIcon({
	label,
	className = "h-4 w-4",
}: {
	label: string;
	className?: string;
}) {
	const Icon = navIcons[label as keyof typeof navIcons];
	if (!Icon) return null;
	return <Icon className={className} aria-hidden="true" />;
}

export function Header() {
	const { resolvedTheme, setTheme } = useTheme();
	const [mounted, setMounted] = useState(false);

	useEffect(() => {
		setMounted(true);
	}, []);

	const isDark = resolvedTheme === "dark";

	const toggleTheme = () => {
		setTheme(isDark ? "light" : "dark");
	};

	const primaryNavLinks = siteNavLinks.filter(
		(link) => link.label !== "Home" && link.label !== "GitHub",
	);

	return (
		<header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
			<div className="container flex h-14 items-center">
				<Link href="/" className="mr-6 flex items-center space-x-2">
					<ProxyWhirlLogo className="h-7 w-7" />
					<span className="font-bold text-foreground">ProxyWhirl</span>
				</Link>

				<nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
					{primaryNavLinks.map((link) => (
						<Link
							key={link.href}
							href={link.href}
							className="flex items-center gap-1 text-foreground/60 transition-colors hover:text-foreground/80"
						>
							<NavIcon label={link.label} />
							{link.label}
						</Link>
					))}
				</nav>

				<div className="flex flex-1 items-center justify-end space-x-2">
					<Button
						variant="ghost"
						size="icon"
						onClick={toggleTheme}
						aria-label="Toggle theme"
					>
						{mounted && isDark ? (
							<Sun className="h-5 w-5" aria-hidden="true" />
						) : (
							<Moon className="h-5 w-5" aria-hidden="true" />
						)}
					</Button>
					<Button
						variant="ghost"
						size="icon"
						asChild
						className="hidden md:flex"
					>
						<a
							href={
								siteNavLinks.find((link) => link.label === "GitHub")?.href ??
								"https://github.com/wyattowalsh/proxywhirl"
							}
							target="_blank"
							rel="noopener noreferrer"
						>
							<Github className="h-5 w-5" aria-hidden="true" />
							<span className="sr-only">GitHub</span>
						</a>
					</Button>

					<div className="md:hidden">
						<DropdownMenu>
							<DropdownMenuTrigger asChild>
								<Button variant="ghost" size="icon" aria-label="Toggle menu">
									<Menu className="h-5 w-5" aria-hidden="true" />
								</Button>
							</DropdownMenuTrigger>
							<DropdownMenuContent align="end">
								{siteNavLinks
									.filter((link) => link.label !== "Home")
									.map((link) => (
										<DropdownMenuItem key={link.href} asChild>
											{link.external ? (
												<a
													href={link.href}
													target="_blank"
													rel="noopener noreferrer"
													className="flex cursor-pointer items-center"
												>
													<NavIcon
														label={link.label}
														className="mr-2 h-4 w-4"
													/>
													{link.label}
												</a>
											) : (
												<Link
													href={link.href}
													className="flex cursor-pointer items-center"
												>
													<NavIcon
														label={link.label}
														className="mr-2 h-4 w-4"
													/>
													{link.label}
												</Link>
											)}
										</DropdownMenuItem>
									))}
							</DropdownMenuContent>
						</DropdownMenu>
					</div>
				</div>
			</div>
		</header>
	);
}