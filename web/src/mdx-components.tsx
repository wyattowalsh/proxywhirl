import { Callout } from "fumadocs-ui/components/callout";
import { Tab, Tabs } from "fumadocs-ui/components/tabs";
import defaultMdxComponents from "fumadocs-ui/mdx";
import type { MDXComponents } from "mdx/types";

export function getMDXComponents(components?: MDXComponents): MDXComponents {
	return {
		...defaultMdxComponents,
		Callout,
		Tabs,
		Tab,
		...components,
	};
}

export const useMDXComponents = getMDXComponents;

export { Callout, Tab, Tabs };