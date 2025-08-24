import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';
import Icon from 'public/img/icon.svg';
import Image from 'next/image';
import { ThemeToggle } from '@/components/layout/theme-toggle';

/**
 * Shared layout configurations
 *
 * you can customise layouts individually from:
 * Home Layout: app/(home)/layout.tsx
 * Docs Layout: app/docs/layout.tsx
 */
export const baseOptions: BaseLayoutProps = {
	nav: {
		title: (
			<>
				<Image src={Icon} alt="proxwhirl project icon" width={36} height={36} />
				<span className="pw animated">proxywhirl</span>
			</>
		),
	},
	// see https://fumadocs.dev/docs/ui/navigation/links
	links: [
	],
	githubUrl: "https://github.com/wyattowalsh/proxywhirl",
	themeSwitch: {
		enabled: true,
		component: <ThemeToggle />,
		mode: 'light-dark-system'
	},
};
