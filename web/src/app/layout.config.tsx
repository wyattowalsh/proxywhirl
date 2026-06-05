import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";
import Image from "next/image";

function Logo() {
	return (
		<Image
			src="/favicon.svg"
			alt=""
			width={28}
			height={28}
			className="h-7 w-7"
			aria-hidden="true"
			unoptimized
		/>
	);
}

export const baseOptions: BaseLayoutProps = {
	nav: {
		url: "/docs",
		title: (
			<span className="flex items-center gap-2 font-semibold">
				<Logo />
				ProxyWhirl Docs
			</span>
		),
	},
	links: [
		{ text: "Home", url: "/" },
		{ text: "Analytics", url: "/analytics" },
		{
			text: "GitHub",
			url: "https://github.com/wyattowalsh/proxywhirl",
			external: true,
		},
	],
};
