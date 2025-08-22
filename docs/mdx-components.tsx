import defaultMdxComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import * as TabsComponents from "fumadocs-ui/components/tabs";
import { Mermaid } from "@/components/mdx/mermaid";
import { ImageZoom } from 'fumadocs-ui/components/image-zoom';
import * as Python from 'fumadocs-python/components';

// use this function to get MDX components, you will need it for rendering MDX
export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    ...TabsComponents,
    Mermaid,
    img: (props) => <ImageZoom {...(props as any)} />,
    ...Python,
    ...components,
  };
}
