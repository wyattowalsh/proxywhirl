This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: apps/docs/content/docs/**/*.{md,markdown,mdx,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
apps/
  docs/
    content/
      docs/
        cli/
          index.mdx
        headless/
          components/
            breadcrumb.mdx
            index.mdx
            link.mdx
            sidebar.mdx
            toc.mdx
          content-collections/
            index.mdx
          mdx/
            headings.mdx
            index.mdx
            install.mdx
            rehype-code.mdx
            remark-admonition.mdx
            remark-image.mdx
            remark-ts2js.mdx
            structure.mdx
          search/
            algolia.mdx
            index.mdx
            orama-cloud.mdx
            orama.mdx
            trieve.mdx
          utils/
            find-neighbour.mdx
            get-toc.mdx
            git-last-edit.mdx
            index.mdx
          custom-source.mdx
          index.mdx
          internationalization.mdx
          page-conventions.mdx
          page-tree.mdx
          source-api.mdx
        mdx/
          async.mdx
          collections.mdx
          global.mdx
          include.mdx
          index.mdx
          last-modified.mdx
          mdx.mdx
          page.mdx
          performance.mdx
          plugin.mdx
        openapi/
          index.mdx
        ui/
          (integrations)/
            openapi/
              configurations.mdx
              index.mdx
              media-adapters.mdx
              proxy.mdx
            feedback.mdx
            llms.mdx
            open-graph.mdx
            python.mdx
            rss.mdx
            typescript.mdx
          components/
            accordion.mdx
            auto-type-table.mdx
            banner.mdx
            dynamic-codeblock.mdx
            files.mdx
            github-info.mdx
            image-zoom.mdx
            index.mdx
            inline-toc.mdx
            steps.mdx
            tabs.mdx
            type-table.mdx
          layouts/
            docs.mdx
            home-layout.mdx
            notebook.mdx
            page.mdx
            root-provider.mdx
          markdown/
            index.mdx
            math.mdx
            mermaid.mdx
            twoslash.mdx
          mdx/
            codeblock.mdx
            index.mdx
          navigation/
            index.mdx
            links.mdx
            sidebar.mdx
          search/
            .shared.mdx
            .tag-filter.mdx
            algolia.mdx
            index.mdx
            orama-cloud.mdx
            orama.mdx
          comparisons.mdx
          customisation.mdx
          index.mdx
          internationalization.mdx
          manual-installation.mdx
          page-conventions.mdx
          static-export.mdx
          theme.mdx
          versioning.mdx
          what-is-fumadocs.mdx
```

# Files

## File: apps/docs/content/docs/cli/index.mdx
`````
---
title: User Guide
description: The CLI tool that automates setups and installs components.
---

## Installation

Initialize a config for CLI:

```package-install
npx @fumadocs/cli
```

You can change the output paths of components in the config.

### Components

Select and install components.

```package-install
npx @fumadocs/cli add
```

You can pass component names directly.

```package-install
npx @fumadocs/cli add banner files
```

#### How the magic works?

The CLI fetches the latest version of component from the GitHub repository of Fumadocs.
When you install a component, it is guaranteed to be up-to-date.

In addition, it also transforms import paths.
Make sure to use the latest version of CLI

> This is highly inspired by Shadcn UI.

### Customise

A simple way to customise Fumadocs layouts.

```package-install
npx @fumadocs/cli customise
```

### Tree

Generate files tree for Fumadocs UI `Files` component, using the `tree` command from your terminal.

```package-install
npx @fumadocs/cli tree ./my-dir ./output.tsx
```

You can output MDX files too:

```package-install
npx @fumadocs/cli tree ./my-dir ./output.mdx
```

See help for further details:

```package-install
npx @fumadocs/cli tree -h
```

#### Example Output

```tsx title="output.tsx"
import { File, Folder, Files } from 'fumadocs-ui/components/files';

export default (
  <Files>
    <Folder name="app">
      <File name="layout.tsx" />
      <File name="page.tsx" />
      <File name="global.css" />
    </Folder>
    <Folder name="components">
      <File name="button.tsx" />
      <File name="tabs.tsx" />
      <File name="dialog.tsx" />
    </Folder>
    <File name="package.json" />
  </Files>
);
```
`````

## File: apps/docs/content/docs/headless/components/breadcrumb.mdx
`````
---
title: Breadcrumb
description: The navigation component at the top of the screen
---

A hook for implementing Breadcrumb in your documentation. It returns breadcrumb items for a page based on the given page tree.

> If present, the index page of a folder will be used as the item.

## Usage

It exports a `useBreadcrumb` hook:

```ts twoslash
declare const tree: any;
// ---cut---
import { usePathname } from 'next/navigation';
import { useBreadcrumb } from 'fumadocs-core/breadcrumb';

const pathname = usePathname();
const items = useBreadcrumb(pathname, tree);
//    ^?
```

### Example

A styled example.

```tsx
'use client';
import { usePathname } from 'next/navigation';
import { useBreadcrumb } from 'fumadocs-core/breadcrumb';
import type { PageTree } from 'fumadocs-core/server';
import { Fragment } from 'react';
import { ChevronRight } from 'lucide-react';
import Link from 'next/link';

export function Breadcrumb({ tree }: { tree: PageTree.Root }) {
  const pathname = usePathname();
  const items = useBreadcrumb(pathname, tree);

  if (items.length === 0) return null;

  return (
    <div className="-mb-3 flex flex-row items-center gap-1 text-sm font-medium text-fd-muted-foreground">
      {items.map((item, i) => (
        <Fragment key={i}>
          {i !== 0 && (
            <ChevronRight className="size-4 shrink-0 rtl:rotate-180" />
          )}
          {item.url ? (
            <Link
              href={item.url}
              className="truncate hover:text-fd-accent-foreground"
            >
              {item.name}
            </Link>
          ) : (
            <span className="truncate">{item.name}</span>
          )}
        </Fragment>
      ))}
    </div>
  );
}
```

You can use it by passing the page tree via `tree` prop in a server component.

### Breadcrumb Item

<AutoTypeTable path="./content/docs/headless/props.ts" name="BreadcrumbItem" />
`````

## File: apps/docs/content/docs/headless/components/index.mdx
`````
---
title: Components
index: true
description: Blocks for your docs
---
`````

## File: apps/docs/content/docs/headless/components/link.mdx
`````
---
title: Link
description: A Link component that handles external links
---

A component that wraps `next/link` and automatically handles external links in the document.
When an external URL is detected, it uses `<a>` instead of the Next.js Link
Component. The `rel` property is automatically generated.

## Usage

Usage is the same as using `<a>`.

```mdx
import Link from 'fumadocs-core/link';

<Link href="/docs/components">Click Me</Link>
```

### External

You can force a URL to be external by passing an `external` prop.

### Dynamic hrefs

Dynamic hrefs are no longer supported in Next.js App Router. You can enable
dynamic hrefs by importing `dynamic-link` instead.

```mdx
import { DynamicLink } from 'fumadocs-core/dynamic-link';

<DynamicLink href="/[lang]/components">Click Me</DynamicLink>
```
`````

## File: apps/docs/content/docs/headless/components/sidebar.mdx
`````
---
title: Sidebar
description: The navigation bar at the side of the viewport
---

A sidebar component which handles device resizing and removes scroll bar
automatically.

## Usage

```tsx
import * as Base from 'fumadocs-core/sidebar';

return (
  <Base.SidebarProvider>
    <Base.SidebarTrigger />
    <Base.SidebarList />
  </Base.SidebarProvider>
);
```

### Sidebar Provider

<AutoTypeTable
  path="./content/docs/headless/props.ts"
  name="SidebarProviderProps"
/>

### Sidebar Trigger

Opens the sidebar on click.

<AutoTypeTable
  path="./content/docs/headless/props.ts"
  name="SidebarTriggerProps"
/>

### Sidebar List

| Data Attribute | Values        | Description     |
| -------------- | ------------- | --------------- |
| `data-open`    | `true, false` | Is sidebar open |

<AutoTypeTable
  path="./content/docs/headless/props.ts"
  type="SidebarContentProps"
/>
`````

## File: apps/docs/content/docs/headless/components/toc.mdx
`````
---
title: TOC
description: Table of Contents
---

A Table of Contents with active anchor observer and auto scroll.

## Usage

```tsx
import * as Base from 'fumadocs-core/toc';

return (
  <Base.AnchorProvider>
    <Base.ScrollProvider>
      <Base.TOCItem />
      <Base.TOCItem />
    </Base.ScrollProvider>
  </Base.AnchorProvider>
);
```

### Anchor Provider

Watches for the active anchor using the Intersection Observer API.

<AutoTypeTable
  path="./content/docs/headless/props.ts"
  name="AnchorProviderProps"
/>

### Scroll Provider

Scrolls the scroll container to the active anchor.

<AutoTypeTable
  path="./content/docs/headless/props.ts"
  name="ScrollProviderProps"
/>

### TOC Item

An anchor item for jumping to the target anchor.

| Data Attribute | Values        | Description          |
| -------------- | ------------- | -------------------- |
| `data-active`  | `true, false` | Is the anchor active |

## Example

<include>./toc-example.tsx</include>
`````

## File: apps/docs/content/docs/headless/content-collections/index.mdx
`````
---
title: Content Collections
description: Use Content Collections for Fumadocs
---

[Content Collections](https://www.content-collections.dev) is a library that transforms your content into type-safe data collections.

## Setup

Install the required packages.

```package-install
@fumadocs/content-collections @content-collections/core @content-collections/mdx @content-collections/next
```

After the installation, add a path alias for the generated collections to the `tsconfig.json`.

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"],
      "content-collections": ["./.content-collections/generated"]
    }
  }
}
```

In the Next.js configuration file, apply the plugin.

```js title="next.config.mjs"
import { withContentCollections } from '@content-collections/next';

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
};

export default withContentCollections(config);
```

To integrate with Fumadocs, add the following to your `content-collections.ts`.

<include cwd meta='title="content-collections.ts"'>
  ../../examples/content-collections/content-collections.ts
</include>

And pass it to Source API.

<include cwd meta='title="lib/source.ts"'>
  ../../examples/content-collections/lib/source.ts
</include>

Done! You can access the pages and generated page tree from Source API.

```ts
import { getPage } from '@/lib/source';

const page = getPage(slugs);

// MDX output
page?.data.body;

// Table of contents
page?.data.toc;

// Structured Data, for Search API
page?.data.structuredData;
```

### MDX Options

You can customise MDX options in the `transformMDX` function.

```ts
import { defineCollection } from '@content-collections/core';
import { transformMDX } from '@fumadocs/content-collections/configuration';

const docs = defineCollection({
  transform: (document, context) =>
    transformMDX(document, context, {
      // options here
    }),
});
```

### Import Components

To use components from other packages like Fumadocs UI, pass them to your `<MDXContent />` component.

```tsx
import { MDXContent } from '@content-collections/mdx/react';
import { getMDXComponents } from '@/mdx-components';

<MDXContent code="..." components={getMDXComponents()} />;
```

You can also import them in MDX Files, but it is not recommended.

<Callout title='Deep Dive: Why?'>
    Content Collections uses `mdx-bundler` to bundle MDX files.

    To support importing a package from node modules, Fumadocs added a default value to the `cwd` option of MDX Bundler.
    It works good, but we still **do not** recommend importing components in MDX files.

    Reasons:

    - It requires esbuild to bundle these components, while it should be done by the Next.js bundler (for features of Server Components)
    - You can refactor the import path of components without changing your MDX files.
    - With Remote Sources, it doesn't make sense to add an import in MDX files.

</Callout>
`````

## File: apps/docs/content/docs/headless/mdx/headings.mdx
`````
---
title: Headings
description: Process headings from your document
---

## Remark Heading

Applies ids to headings.

```ts title="MDX Compiler"
import { compile } from '@mdx-js/mdx';
import { remarkHeading } from 'fumadocs-core/mdx-plugins';

await compile('...', {
  remarkPlugins: [remarkHeading],
});
```

> This plugin is included by default on Fumadocs MDX.

### Extract TOC

By default, it extracts the headings (table of contents) of a document to `vfile.data.toc`.
You can disable it with:

```ts
import { remarkHeading } from 'fumadocs-core/mdx-plugins';

export default {
  remarkPlugins: [[remarkHeading, { generateToc: false }]],
};
```

### Custom Ids [#custom-heading-id]

You can customise the heading id with `[#slug]`.

```md
# heading [#slug]
```

### Output

An array of `TOCItemType`.

<AutoTypeTable path="./content/docs/headless/props.ts" name="TOCItemType" />

## Rehype TOC

Exports table of contents (an array of `TOCItemType`), it allows JSX nodes which is not possible with a Remark plugin.

> It requires MDX.js.

### Usage

```ts
import { rehypeToc } from 'fumadocs-core/mdx-plugins';

export default {
  rehypePlugins: [rehypeToc],
};
```

### Output

For a Markdown document:

```md
## Hello `code`
```

An export will be created:

```jsx
export const toc = [
  {
    title: (
      <>
        Hello <code>code</code>
      </>
    ),
    depth: 2,
    url: '#hello-code',
  },
];
```
`````

## File: apps/docs/content/docs/headless/mdx/index.mdx
`````
---
title: MDX Plugins
index: true
description: Useful remark & rehype plugins for your docs.
---
`````

## File: apps/docs/content/docs/headless/mdx/install.mdx
`````
---
title: Package Install
description: Generate code blocks for installing packages
---

## Usage

```package-install
fumadocs-docgen
```

Add the remark plugin.

```ts title="source.config.ts" tab="Fumadocs MDX"
import { remarkInstall } from 'fumadocs-docgen';
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkInstall],
  },
});
```

```ts tab="MDX Compiler"
import { compile } from '@mdx-js/mdx';
import { remarkInstall } from 'fumadocs-docgen';

await compile('...', {
  remarkPlugins: [remarkInstall],
});
```

Define the required components.

```tsx title="mdx-components.tsx (Fumadocs UI)"
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';
import defaultComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    Tab,
    Tabs,
    ...components,
  };
}
```

| Component |                                    |
| --------- | ---------------------------------- |
| Tabs      | Accepts an array of item (`items`) |
| Tab       | Accepts the name of item (`value`) |

Create code blocks with `package-install` as language.

````mdx
```package-install
my-package
```

```package-install
npm i my-package -D
```
````

### Output

The following structure should be generated by the plugin.

```mdx
<Tabs items={['npm', 'pnpm', 'yarn', 'bun']}>
  <Tab value="npm">...</Tab>
  <Tab value="pnpm">...</Tab>
  <Tab value="yarn">...</Tab>
  <Tab value="bun">...</Tab>
</Tabs>
```

```package-install
my-package
```

## Options

### Persistent

When using with Fumadocs UI, you can enable persistence with the `persist` option.

```ts title="source.config.ts" tab="Fumadocs MDX"
import { remarkInstall } from 'fumadocs-docgen';
import { defineConfig } from 'fumadocs-mdx/config';

const remarkInstallOptions = {
  persist: {
    id: 'some-id',
  },
};

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [[remarkInstall, remarkInstallOptions]],
  },
});
```

```ts tab="MDX Compiler"
import { compile } from '@mdx-js/mdx';
import { remarkInstall } from 'fumadocs-docgen';

const remarkInstallOptions = {
  persist: {
    id: 'some-id',
  },
};

await compile('...', {
  remarkPlugins: [[remarkInstall, remarkInstallOptions]],
});
```

This will instead generate:

```mdx
<Tabs groupId="some-id" persist items={[...]}>
  ...
</Tabs>
```
`````

## File: apps/docs/content/docs/headless/mdx/rehype-code.mdx
`````
---
title: Rehype Code
description: Code syntax highlighter
---

A wrapper of [Shiki](https://shiki.style), the built-in syntax highlighter.

## Usage

Add the rehype plugin.

```ts title="MDX Compiler"
import { compile } from '@mdx-js/mdx';
import { rehypeCode } from 'fumadocs-core/mdx-plugins';

await compile('...', {
  rehypePlugins: [rehypeCode],
});
```

> This plugin is included by default on Fumadocs MDX.

### Output

A codeblock wrapped in `<pre />` element.

```html
<pre>
<code>...</code>
</pre>
```

### Meta

It parses the `title` meta string, and adds it to the `pre` element as an attribute.

````mdx
```js title="Title"
console.log('Hello');
```
````

You may filter the meta string before processing it with the `filterMetaString` option.

### Inline Code

`console.log("hello world"){:js}` works.

See https://shiki.style/packages/rehype#inline-code.

### Icon

Adds an icon according to the language of the codeblock.
It outputs HTML, you might need to render it with React `dangerouslySetInnerHTML`.

```jsx
<pre icon="<svg />">...</pre>
```

Disable or customise icons with the `icon` option.

### More Options

See [Shiki](https://shiki.style).
`````

## File: apps/docs/content/docs/headless/mdx/remark-admonition.mdx
`````
---
title: Remark Admonition
description: Use Admonition in Fumadocs
---

In Docusaurus, there's an [Admonition syntax](https://docusaurus.io/docs/markdown-features/admonitions).

For people migrating from Docusaurus, you can enable this remark plugin to support the Admonition syntax.

## Usage

```ts title="source.config.ts" tab="Fumadocs MDX"
import { remarkAdmonition } from 'fumadocs-core/mdx-plugins';
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkAdmonition],
  },
});
```

```ts tab="MDX Compiler"
import { compile } from '@mdx-js/mdx';
import { remarkAdmonition } from 'fumadocs-core/mdx-plugins';

await compile('...', {
  remarkPlugins: [remarkAdmonition],
});
```

### Input

```md
:::warning
Hello World
:::
```

### Output

```mdx
<Callout type='warn'>

Hello World

</Callout>
```

### When to use

We highly recommend using the JSX syntax of MDX instead.
It's more flexible, some editors support IntelliSense in MDX files.

```mdx
<Callout type='warn'>

Hello World

</Callout>
```
`````

## File: apps/docs/content/docs/headless/mdx/remark-image.mdx
`````
---
title: Remark Image
description: Make images compatible with Next.js Image Optimization
---

## Usage

Add it to your Remark plugins.

```ts title="MDX Compiler"
import { compile } from '@mdx-js/mdx';
import { remarkImage } from 'fumadocs-core/mdx-plugins';

await compile('...', {
  remarkPlugins: [remarkImage],
});
```

> This plugin is included by default on Fumadocs MDX.

Supported:

- Local Images
- External URLs
- Next.js static imports

### How It Works

It transforms your `![image](/test.png)` into Next.js Image usage, and add required props like `width` and `height`.

By default, it uses **static imports** to import local images, which supports the `placeholder` option of Next.js Image.
Next.js can handle image imports with its built-in image loader.

Otherwise, it uses the file system or an HTTP request to download the image and obtain its size.

### Options

<AutoTypeTable
  path="./content/docs/headless/props.ts"
  name="RemarkImageOptions"
/>

### Example: With Imports

```mdx
![Hello](/hello.png)
![Test](https://example.com/image.png)
```

Yields:

```mdx
import HelloImage from './public/hello.png';

<img alt="Hello" src={HelloImage} />
<img
  alt="Test"
  src="https://example.com/image.png"
  width="1980"
  height="1080"
/>
```

Where `./public/hello.png` points to the image in public directory.

### Example: Without Imports

You can disable Next.js static imports on local images.

```ts
import { remarkImage } from 'fumadocs-core/mdx-plugins';

export default {
  remarkPlugins: [[remarkImage, { useImport: false }]],
};
```

```mdx
![Hello](/hello.png)
![Test](https://example.com/image.png)
```

Yields:

```mdx
<img alt="Hello" src="/hello.png" width="1980" height="1080" />
<img
  alt="Test"
  src="https://example.com/image.png"
  width="1980"
  height="1080"
/>
```

### Example: Relative Paths

When `useImport` is enabled, you can reference local images using relative paths.

```mdx
![Hello](./hello.png)
```

Be careful that using it with `useImport` disabled **doesn't work**.
Next.js will not add the image to public assets unless you have imported it in code.
For images in public directory, you can just reference them without relative paths.

### Example: Public Directory

Customise the path of public directory

```ts
import { remarkImage } from 'fumadocs-core/mdx-plugins';
import path from 'node:path';

export default {
  remarkPlugins: [
    remarkImage,
    {
      publicDir: path.join(process.cwd(), 'dir'),
    },
  ],
};
```

You can pass a URL too.

```ts
import { remarkImage } from 'fumadocs-core/mdx-plugins';

export default {
  remarkPlugins: [
    remarkImage,
    {
      publicDir: 'http://localhost:3000/images',
    },
  ],
};
```
`````

## File: apps/docs/content/docs/headless/mdx/remark-ts2js.mdx
`````
---
title: Remark TS to JS
description: A remark plugin to transform TypeScript codeblocks into two tabs of codeblock with its JavaScript variant.
---

## Usage

Install dependencies:

```package-install
fumadocs-docgen oxc-transform
```

Add `oxc-transform` to `serverExternalPackages` in `next.config.mjs`:

```js title="next.config.mjs"
import { createMDX } from 'fumadocs-mdx/next';

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
  serverExternalPackages: ['oxc-transform'],
};

const withMDX = createMDX();

export default withMDX(config);
```

Add the remark plugin:

```ts title="source.config.ts" tab="Fumadocs MDX"
import { remarkTypeScriptToJavaScript } from 'fumadocs-docgen/remark-ts2js';
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkTypeScriptToJavaScript],
  },
});
```

```ts tab="MDX Compiler"
import { remarkTypeScriptToJavaScript } from 'fumadocs-docgen/remark-ts2js';
import { compile } from '@mdx-js/mdx';

await compile('...', {
  remarkPlugins: [remarkTypeScriptToJavaScript],
});
```

Finally, make sure to define the required MDX components: `Tabs` and `Tab`.

```tsx title="mdx-components.tsx (Fumadocs UI)"
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';
import defaultComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    Tab,
    Tabs,
    ...components,
  };
}
```

You can now enable it on TypeScript/TSX codeblocks, like:

````md
```tsx ts2js
import { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return <div>{children}</div>;
}
```
````

```tsx ts2js
import { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return <div>{children}</div>;
}
```
`````

## File: apps/docs/content/docs/headless/mdx/structure.mdx
`````
---
title: Remark Structure
description: Extract information from your documents, useful for implementing document search
---

## Usage

Add it as a remark plugin.

```ts title="MDX Compiler"
import { compile } from '@mdx-js/mdx';
import { remarkStructure } from 'fumadocs-core/mdx-plugins';

const vfile = await compile('...', {
  remarkPlugins: [remarkStructure],
});
```

> This plugin is included by default on Fumadocs MDX.

Extracted information could be found in `vfile.data.structuredData`, you may
write your own plugin to convert it into a MDX export.

### Options

<AutoTypeTable
  path="./content/docs/headless/props.ts"
  name="StructureOptions"
/>

### Output

A list of headings and contents. Paragraphs will be extracted to the `contents`
array, each item contains a `heading` prop indicating the heading of paragraph.

<Callout title="Note">A heading can have multiple paragraphs.</Callout>

#### Heading

| Prop      |                                      |
| --------- | ------------------------------------ |
| `id`      | unique identifier or slug of heading |
| `content` | Text content                         |

#### Content

| Prop      |                                 |
| --------- | ------------------------------- |
| `heading` | Heading of paragraph (nullable) |
| `content` | Text content                    |

## As a Function

Accepts MDX/markdown content and return structurized data.

```ts
import { structure } from 'fumadocs-core/mdx-plugins';

structure(page.body.raw);
```

<Callout title="Tip" className="mt-4">
If you have custom remark plugins enabled, such as
`remark-math`, you have to pass these plugins to the function. This avoids unreadable content on paragraphs.

```ts
import { structure } from 'fumadocs-core/mdx-plugins';
import remarkMath from 'remark-math';

structure(page.body.raw, [remarkMath]);
```

</Callout>

### Parameters

| Parameter       |                        |
| --------------- | ---------------------- |
| `content`       | MDX/markdown content   |
| `remarkPlugins` | List of remark plugins |
| `options`       | Custom options         |
`````

## File: apps/docs/content/docs/headless/search/algolia.mdx
`````
---
title: Algolia Search
description: Integrate Algolia Search with Fumadocs
---

<Callout title="Notice">
  If you're using Algolia's free tier, you have to [display their logo on your
  search dialog](https://algolia.com/policies/free-services-terms).
</Callout>

## Introduction

The Algolia Integration automatically configures Algolia Search for document search.

It creates a record for **each paragraph** in your document, it is also recommended by Algolia.

Each record contains searchable attributes:

| Attribute | Description           |
| --------- | --------------------- |
| `title`   | Page Title            |
| `section` | Heading ID (nullable) |
| `content` | Paragraph content     |

The `section` field only exists in paragraphs under a heading. Headings and
paragraphs are indexed as an individual record, grouped by their page ID.

Notice that it expects the `url` property of a page to be unique, you shouldn't have two pages with the same
url.

## Setup

Install dependencies:

```package-install
algoliasearch
```

### Sign up on Algolia

Sign up and obtain the app id and API keys for your search. Store these
credentials in environment variables.

### Sync Search Indexes

Export the search indexes from Next.js using a route handler, this way we can access the search indexes after production build:

```ts title="app/static.json/route.ts"
import { NextResponse } from 'next/server';
import { type DocumentRecord } from 'fumadocs-core/search/algolia';
import { source } from '@/lib/source';

export const revalidate = false;

export function GET() {
  const results: DocumentRecord[] = [];

  for (const page of source.getPages()) {
    results.push({
      _id: page.url,
      structured: page.data.structuredData,
      url: page.url,
      title: page.data.title,
      description: page.data.description,
    });
  }

  return NextResponse.json(results);
}
```

Make a script to sync search indexes:

<include lang="js" meta='title="update-index.mjs"'>
  ./sync-algolia.mjs
</include>

The `sync` function will update the index settings and sync search indexes.

Now run the script after build:

```json title="package.json"
{
  "scripts": {
    "build": "next build && node ./update-index.mjs"
  }
}
```

### Workflow

You may make it a script and manually sync with `node ./update-index.mjs`, or
integrate it with your CI/CD pipeline.

<Callout type="warn" title="Typescript Usage">
  If you are running the script with [TSX](https://github.com/privatenumber/tsx)
  or other similar Typescript executors, ensure to name it `.mts` for best ESM
  compatibility.
</Callout>

### Search UI

You can consider different options for implementing the UI:

- Using [Fumadocs UI search dialog](/docs/ui/search/algolia).
- Build your own using the built-in search client hook:

  ```ts twoslash
  import { liteClient } from 'algoliasearch/lite';
  import { useDocsSearch } from 'fumadocs-core/search/client';

  const client = liteClient('id', 'key');

  const { search, setSearch, query } = useDocsSearch({
    type: 'algolia',
    indexName: 'document',
    client,
  });
  ```

- Use their official clients directly.

## Options

### Tag Filter

To configure tag filtering, add a `tag` value to indexes.

```js
import { sync } from 'fumadocs-core/search/algolia';

void sync(client, {
  indexName: 'document',
  documents: records.map((index) => ({
    ...index,
    tag: 'value', // [!code ++]
  })),
});
```

And update your search client:

- **Fumadocs UI**: Enable [Tag Filter](/docs/ui/search/algolia#tag-filter) on Search UI.
- **Search Client**: You can add the tag filter like:

  ```ts
  import { useDocsSearch } from 'fumadocs-core/search/client';

  const { search, setSearch, query } = useDocsSearch({
    tag: '<your tag value>',
    // ...
  });
  ```

The `tag` field is an attribute for faceting. You can also use the filter `tag:value` on Algolia search clients.
`````

## File: apps/docs/content/docs/headless/search/index.mdx
`````
---
title: Search
description: Configure Search in Fumadocs
icon: Search
index: true
---
`````

## File: apps/docs/content/docs/headless/search/orama-cloud.mdx
`````
---
title: Orama Cloud
description: Integrate with Orama Cloud
---

To begin, create an account on Orama Cloud.

## REST API

REST API integration requires your docs to upload the indexes.

1. Create a new REST API index from Dashboard.
2. Use the following schema:

   ```json
   {
     "id": "string",
     "title": "string",
     "url": "string",
     "tag": "string",
     "page_id": "string",
     "section": "string",
     "section_id": "string",
     "content": "string"
   }
   ```

3. Then, using the private API key and index ID from dashboard, create a script to sync search indexes.

   <include cwd meta='title="sync-index.mjs"' lang="js">
     ../../examples/next-mdx/scripts/sync-orama-cloud.mjs
   </include>

4. Create a route handler in your Next.js app to export search indexes.

   <include cwd meta='title="app/static.json/route.ts"'>
     ../../examples/next-mdx/app/static.json/orama-cloud.ts
   </include>

5. Run the script after `next build`.

### Search Client

To search documents on the client side, consider:

- Using [Fumadocs UI search dialog](/docs/ui/search/orama-cloud).
- Custom search UI using the built-in hook of Fumadocs:

  ```ts
  import { useDocsSearch } from 'fumadocs-core/search/client';
  import { OramaClient } from '@oramacloud/client';

  const client = new OramaClient();

  const { search, setSearch, query } = useDocsSearch({
    type: 'orama-cloud',
    client,
    params: {
      // search params
    },
  });
  ```

- Use their search client directly.

## Web Crawler

1. Create a Crawler index from dashboard, and configure it correctly with the "Documentation" preset.
2. Copy the public API key and index ID from dashboard

### Search Client

Same as REST API integration, but make sure to set `index` to `crawler`.

```ts
import { useDocsSearch } from 'fumadocs-core/search/client';
import { OramaClient } from '@oramacloud/client';

const client = new OramaClient({
  endpoint: '<endpoint_url>',
  api_key: '<api_key>',
});

const { search, setSearch, query } = useDocsSearch({
  type: 'orama-cloud',
  index: 'crawler',
  client,
  params: {
    // optional search params
  },
});
```

It's same for Fumadocs UI.
`````

## File: apps/docs/content/docs/headless/search/orama.mdx
`````
---
title: Built-in Search
description: Built-in document search of Fumadocs
---

Fumadocs supports document search with Orama, It is the default but also the recommended option since it can be self-hosted and totally free.

## Search Server

You can create the search route handler from the source object, or search indexes.

<Accordions>

    <Accordion title='From Source'>

Create a route handler from source object.

<include cwd meta='title="app/api/search/route.ts"'>
  ../../examples/next-mdx/app/api/search/route.ts
</include>

    </Accordion>
    <Accordion title="From Search Indexes">

Pass search indexes to the function.

<Tabs items={['Structured Data', 'Raw Content']}>

    <Tab>

        Each index needs a `structuredData` field.
        Usually, it is provided by your content source (e.g. Fumadocs MDX). You can also extract it from Markdown/MDX document using the [Remark Structure](/docs/headless/mdx/structure) plugin.

        <include cwd meta='title="app/api/search/route.ts"'>
            ../../examples/next-mdx/app/api/search/route-full.ts
        </include>

    </Tab>

    <Tab>

Index with the raw content of document (unrecommended).

```ts title="app/api/search/route.ts"
import { allDocs } from 'content-collections';
import { createSearchAPI } from 'fumadocs-core/search/server';

export const { GET } = createSearchAPI('simple', {
  indexes: allDocs.map((docs) => ({
    title: docs.title,
    content: docs.content, // Raw Content
    url: docs.url,
  })),
});
```

    </Tab>

</Tabs>

    </Accordion>

</Accordions>

## Search Client

You can search documents using:

- **Fumadocs UI**: Supported out-of-the-box, see [Search UI](/docs/ui/search/orama) for details.
- **Search Client**:

```ts twoslash
import { useDocsSearch } from 'fumadocs-core/search/client';

const client = useDocsSearch({
  type: 'fetch',
});
```

<auto-type-table type='Extract<import("fumadocs-core/search/client").Client, { type: "fetch" }>' />

## Configurations

### Tag Filter

Support filtering results by tag, it's useful for implementing multi-docs similar to this documentation.

<include meta='title="app/api/search/route.ts"' cwd>
  ../../examples/next-mdx/app/api/search/route-tag.ts
</include>

and update your search client:

- **Fumadocs UI**: Configure [Tag Filter](/docs/ui/search/orama#tag-filter) on Search UI.
- **Search Client**: pass a tag to the hook.

```ts
import { useDocsSearch } from 'fumadocs-core/search/client';

// Pass `tag` in your custom search dialog
const client = useDocsSearch({
  type: 'fetch',
  tag: '<value>',
});
```

### Internationalization

```ts title="lib/source.ts" tab="createFromSource"
import { i18n } from '@/lib/i18n';
import { loader } from 'fumadocs-core/source';

// You only need i18n option on source object.
export const source = loader({
  i18n, // [!code highlight]
});
```

<include cwd meta='title="app/api/search/route.ts" tab="createI18nSearchAPI"'>
  ../../examples/i18n/app/api/search/route-full.ts
</include>

and update your search clients:

- **Fumadocs UI**: No changes needed, Fumadocs UI handles this when you have i18n configured correctly.
- **Search Client**:
  Add `locale` to the search client, this will only allow pages with specified locale to be searchable by the user.

```ts
import { useDocsSearch } from 'fumadocs-core/search/client';

const { search, setSearch, query } = useDocsSearch({
  type: 'fetch',
  locale: 'cn',
});
```

### Special Languages

If your language is not on the Orama [Supported Languages](https://docs.orama.com/open-source/supported-languages#officially-supported-languages) list, you have to configure them manually:

<Accordions>

    <Accordion title='Fetch mode'>

        <include cwd meta='title="app/api/search/route.ts" tab="With I18n"'>
            ../../examples/i18n/app/api/search/route.ts
        </include>

```ts title="app/api/search/route.ts" tab="Without I18n"
import { source } from '@/lib/source';
import { createFromSource } from 'fumadocs-core/search/server';
import { createTokenizer } from '@orama/tokenizers/mandarin';

// example for Mandarin
export const { GET } = createFromSource(source, {
  components: {
    tokenizer: createTokenizer(),
  },
  search: {
    threshold: 0,
    tolerance: 0,
  },
});
```

    </Accordion>
    <Accordion title='Static mode'>

You can customise it in the client-side `initOrama()` function.

```tsx
import { useDocsSearch } from 'fumadocs-core/search/client';
import { createTokenizer } from '@orama/tokenizers/mandarin';

function initOrama(locale?: string) {
  return create({
    schema: { _: 'string' },
    components: {
      // for users with i18n enabled, you can pass it conditionally based on `locale`
      tokenizer: locale === 'cn' ? createTokenizer() : undefined,
      // or if all documents are written in Chinese
      tokenizer: createTokenizer(),
    },
  });
}

function Search() {
  const client = useDocsSearch({
    type: 'static',
    initOrama,
  });
  // ...
}
```

    </Accordion>

</Accordions>

### Static Export

To work with Next.js static export, use `staticGET` from search server.

```ts title="app/api/search/route.ts"
import { source } from '@/lib/source';
import { createFromSource } from 'fumadocs-core/search/server';

// it should be cached forever
export const revalidate = false;

// [!code highlight]
export const { staticGET: GET } = createFromSource(source);
```

> `staticGET` is also available on `createSearchAPI`.

and update your search clients:

- **Fumadocs UI**: use [static client](/docs/ui/search/orama#static) on Search UI.

- **Search Client**: use `static` instead of `fetch`.

  ```ts
  import { useDocsSearch } from 'fumadocs-core/search/client';

  const client = useDocsSearch({
    type: 'static',
  });
  ```

  <AutoTypeTable type='Extract<import("fumadocs-core/search/client").Client, { type: "static" }>' />

<Callout type='warn' title="Be Careful">

    Static Search requires clients to download the exported search indexes.
    For large docs sites, it can be expensive.

    You should use cloud solutions like Orama Cloud or Algolia for these cases.

</Callout>

## Headless

You can host the search server on other backend such as Express and Elysia.

```ts
import { initAdvancedSearch } from 'fumadocs-core/search/server';

const server = initAdvancedSearch({
  // you still have to pass indexes
});

server.search('query', {
  // you can specify `locale` and `tag` here
});
```
`````

## File: apps/docs/content/docs/headless/search/trieve.mdx
`````
---
title: Trieve Search
description: Integrate Trieve Search with Fumadocs
---

> This is a community maintained integration.

## Introduction

The Trieve Integration automatically configures Trieve Search for site search.

By default, it creates a chunk for **each paragraph** in your document, it is
officially recommended by Trieve.

## Setup

### Install Dependencies

```package-install
trieve-ts-sdk trieve-fumadocs-adapter
```

### Sign up on Trieve

Sign up and create a dataset. Then obtain 2 API keys where one has only read access and the other has admin access to create and delete chunks.
Store these credentials in environment variables.

<Callout title="Notice">
  One API Key should have only read access for the public facing search and the
  other should have admin access to create and delete chunks.
</Callout>

### Sync Dataset

You can export the search indexes from Next.js using a route handler:

```ts title="app/static.json/route.ts"
import { NextResponse } from 'next/server';
import { source } from '@/lib/source';
import { type TrieveDocument } from 'trieve-fumadocs-adapter/search/sync';

export const revalidate = false;

export function GET() {
  const results: TrieveDocument[] = [];

  for (const page of source.getPages()) {
    results.push({
      _id: page.url,
      structured: page.data.structuredData,
      url: page.url,
      title: page.data.title,
      description: page.data.description,
    });
  }

  return NextResponse.json(results);
}
```

Create a script, the `sync` function will sync search indexes.

```js title="update-index.mjs"
import * as fs from 'node:fs';
import { sync } from 'trieve-fumadocs-adapter/search/sync';
import { TrieveSDK } from 'trieve-ts-sdk';

const content = fs.readFileSync('.next/server/app/static.json.body');

// now you can pass it to `sync`
/** @type {import('trieve-fumadocs-adapter/search/sync').TrieveDocument[]} **/
const records = JSON.parse(content.toString());

const client = new TrieveSDK({
  apiKey: 'adminApiKey',
  datasetId: 'datasetId',
});

sync(client, records);
```

Make sure to run the script after build:

```json title="package.json"
{
  "scripts": {
    "build": "next build && node ./update-index.mjs"
  }
}
```

### Workflow

You may manually sync with `node ./update-index.mjs`, or
integrate it with your CI/CD pipeline.

<Callout type="info" title="Typescript Usage">
  You can use Bun or other JavaScript runtimes that supports TypeScript and ESM.
</Callout>

### Search UI

You can use their `SearchDialog` component:

```tsx title="components/search.tsx"
'use client';
import type { SharedProps } from 'fumadocs-ui/components/dialog/search';
import SearchDialog from 'trieve-fumadocs-adapter/components/dialog/search';
import { TrieveSDK } from 'trieve-ts-sdk';

const trieveClient = new TrieveSDK({
  apiKey: 'readOnlyApiKey',
  datasetId: 'datasetId',
});

export default function CustomSearchDialog(props: SharedProps) {
  return <SearchDialog trieveClient={trieveClient} {...props} />;
}
```

1. Replace `apiKey` and `datasetId` with your desired values.

2. Replace the default search dialog with your new one.

### Search Client

Add the `useTrieveSearch` hook:

```ts
import { TrieveSDK } from 'trieve-ts-sdk';
import { useTrieveSearch } from 'trieve-fumadocs-adapter/search/trieve';

const client = new TrieveSDK({
  apiKey: 'readOnlyApiKey',
  datasetId: 'datasetId',
});

const { search, setSearch, query } = useTrieveSearch(client);
```

## Options

### Tag Filter

To configure tag filtering, add a `tag` value to indexes.

```js
import { sync } from 'trieve-fumadocs-adapter/search/sync';
import { TrieveSDK } from 'trieve-ts-sdk';

const client = new TrieveSDK({
  apiKey: 'adminApiKey',
  datasetId: 'datasetId',
});

const documents = records.map((index) => ({
  ...index,
  tag: 'value', // [!code highlight]
}));

sync(client, documents);
```

#### Search UI

Enable Tag Filter.

```tsx title="components/search.tsx"
import SearchDialog from 'trieve-fumadocs-adapter/components/dialog/search';

<SearchDialog
  defaultTag="value"
  tags={[
    {
      name: 'Tag Name',
      value: 'value',
    },
  ]}
/>;
```

#### Search Client

The `tag_set` field is an attribute for filtering. To filter indexes by tag, use the filter on Trieve search clients.

```json
{
  "must": [
    {
      "field": "tag_set",
      "match": ["value"]
    }
  ]
}
```

Or with `useTrieveSearch` hook:

```ts
import { TrieveSDK } from 'trieve-ts-sdk';
import { useTrieveSearch } from 'trieve-fumadocs-adapter/search/trieve';

const client = new TrieveSDK({
  apiKey: 'readOnlyApiKey',
  datasetId: 'datasetId',
});

const { search, setSearch, query } = useTrieveSearch(
  client,
  undefined,
  '<your tag value>',
);
```
`````

## File: apps/docs/content/docs/headless/utils/find-neighbour.mdx
`````
---
title: Find Neighbours
description: Find the neighbours of a page from the page tree
---

Find the neighbours of a page from the page tree, it returns the next and
previous page of a given page. It is useful for implementing a footer.

## Usage

It requires a page tree and the url of page.

```ts
import { findNeighbour } from 'fumadocs-core/server';
import { pageTree } from '@/lib/source';

const neighbours = findNeighbour(pageTree, '/url/to/page');
```

| Parameter | Type       | Description     |
| --------- | ---------- | --------------- |
| tree      | `PageTree` | The page tree   |
| url       | `string`   | The url of page |
`````

## File: apps/docs/content/docs/headless/utils/get-toc.mdx
`````
---
title: Get TOC
description: Parse Table of contents from markdown/mdx content
---

Parse Table of contents from markdown/mdx content.

> [You can use the remark plugin directly](/docs/headless/mdx/headings)

## Usage

Note: If you're using a CMS, you should use the API provided by the CMS instead.

```ts
import { getTableOfContents } from 'fumadocs-core/server';

const toc = getTableOfContents('## markdown content');
```

### Output

An array of [`TOCItemType`](/docs/headless/mdx/headings#output) is returned.
`````

## File: apps/docs/content/docs/headless/utils/git-last-edit.mdx
`````
---
title: Last Modified Time
description: Get the last edit time of a file in Github repository
---

## Usage

Pass your repository name, and the path to file.

```ts
import { getGithubLastEdit } from 'fumadocs-core/server';

const time = await getGithubLastEdit({
  owner: 'fuma-nama',
  repo: 'fumadocs',
  // example: "content/docs/index.mdx"
  path: `content/docs/${page.path}`,
});
```

### Github Token

Notice that you may easily reach the rate limit in development mode. Hence, you
should pass a Github token for a higher rate limit.

Learn more about
[Authenticating to the REST API](https://docs.github.com/en/rest/overview/authenticating-to-the-rest-api).

```ts
import { getGithubLastEdit } from 'fumadocs-core/server'

 const time = await getGithubLastEdit({
    ...,
    token: `Bearer ${process.env.GIT_TOKEN}`
  })
```

Also, you can skip this in development mode if you don't need that
functionality.

```ts
process.env.NODE_ENV === 'development'? null : getGithubLastEdit(...)
```
`````

## File: apps/docs/content/docs/headless/utils/index.mdx
`````
---
title: Utilities
index: true
description: Utilities to provide extra functionality to your docs
---
`````

## File: apps/docs/content/docs/headless/custom-source.mdx
`````
---
title: Custom Source
description: Build your own content source
---

## Introduction

**Fumadocs is very flexible.** You can integrate with any content source, even without an official adapter.

> This guide assumes you are experienced with Next.js App Router.

### Examples

You can see examples to use Fumadocs with a CMS, which allows a nice experience on publishing content, and real-time update without re-building the app.

- [BaseHub](https://github.com/fuma-nama/fumadocs-basehub)
- [Sanity](https://github.com/fuma-nama/fumadocs-sanity)

For a custom content source implementation, you will need:

### Page Tree

You can either hardcode the page tree, or write some code to generate one.
See [Definitions of Page Tree](/docs/headless/page-tree).

Pass your Page Tree to `DocsLayout` (usually in a `layout.tsx`).

```tsx title="layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      nav={{ title: 'Example Docs' }}
      tree={
        {
          /// your own tree
        }
      }
    >
      {children}
    </DocsLayout>
  );
}
```

The page tree is like a smarter "sidebar items", they will be referenced everywhere in the UI for navigation elements, such as the page footer.

### Docs Page

Same as a normal Next.js app, the code of your docs page is located in `[[...slug]]/page.tsx`.

#### SSG

Define the [`generateStaticParams`](https://nextjs.org/docs/app/api-reference/functions/generate-static-params) function.
It should return a list of parameters (`params`) to populate the `[[...slug]]` catch-all route.

#### Body

In the main body of page, find the corresponding page according to the slug and render its content inside the `DocsPage` component.

You also need table of contents, which can be generated with your own implementation, or using the [`getTableOfContents`](/docs/headless/utils/get-toc) utility (Markdown/MDX only).

```tsx
import { DocsPage, DocsBody } from 'fumadocs-ui/page';
import { getPage } from './my-content-source';
import { notFound } from 'next/navigation';

export default function Page({ params }: { params: { slug?: string[] } }) {
  const page = getPage(params.slug);
  if (!page) notFound();

  return (
    <DocsPage toc={page.tableOfContents}>
      <DocsBody>{page.render()}</DocsBody>
    </DocsPage>
  );
}
```

#### Metadata

Next.js offers a Metadata API for SEO, you can configure it with `generateMetadata` (similar as the code above).

### Document Search

This can be difficult considering your content may not be necessarily Markdown/MDX.
For Markdown and MDX, the built-in [Search API](/docs/headless/search/orama) is adequate for most use cases.
Otherwise, you will have to bring your own implementation.

We recommend 3rd party solutions like Algolia Search. They are more flexible than the built-in Search API, and is easier to integrate with remote sources.
Fumadocs offers a simple [Algolia Search Adapter](/docs/headless/search/algolia), which includes a search client to integrate with Fumadocs UI.

## MDX Remote

Fumadocs offers the **MDX Remote** package, it is a helper to integrate Markdown-based content sources with Fumadocs.
You can think it as a `next-mdx-remote` with built-in plugins for Fumadocs.

### Setup

```package-install
@fumadocs/mdx-remote
```

The main feature it offers is the MDX Compiler, it can compile MDX content to JSX nodes.
Since it doesn't use a bundler, there's some limitations:

- No imports and exports in MDX files.

It's compatible with Server Components. For example:

```tsx
import { compileMDX } from '@fumadocs/mdx-remote';
import { getPage } from './my-content-source';
import { DocsBody, DocsPage } from 'fumadocs-ui/page';
import { getMDXComponents } from '@/mdx-components';

export default async function Page({
  params,
}: {
  params: { slug?: string[] };
}) {
  const page = getPage(params.slug);
  const compiled = await compileMDX({
    source: page.content,
  });

  const MdxContent = compiled.body;

  return (
    <DocsPage toc={compiled.toc}>
      <DocsBody>
        <MdxContent components={getMDXComponents()} />
      </DocsBody>
    </DocsPage>
  );
}
```

#### Images

On some platforms like Vercel, the original `public` folder (including static assets like images) will be removed after `next build`.
`compileMDX` might no longer be able to access local images in `public`.

When referencing images, make sure to use a URL.
`````

## File: apps/docs/content/docs/headless/index.mdx
`````
---
title: Introduction
description: Getting started with core library
icon: Album
---

## What is this?

Fumadocs Core offers server-side functions and headless components to build docs on any React.js frameworks like Next.js.

- Search (built-in: Orama, Algolia Search)
- Breadcrumb, Sidebar, TOC Components
- Remark/Rehype Plugins
- Additional utilities

<Callout title="Tip">

    It can be used without Fumadocs UI, in other words, it's headless.

    For beginners and normal usages, use [Fumadocs UI](/docs/ui).

</Callout>

## Installation

No other dependencies required.

```package-install
fumadocs-core
```

For some components, a framework provider is needed:

```tsx tab="Next.js"
import type { ReactNode } from 'react';
import { NextProvider } from 'fumadocs-core/framework/next';

export function RootLayout({ children }: { children: ReactNode }) {
  // or if you're using Fumadocs UI, use `<RootProvider />`
  return <NextProvider>{children}</NextProvider>;
}
```

```tsx tab="React Router"
import type { ReactNode } from 'react';
import { ReactRouterProvider } from 'fumadocs-core/framework/react-router';

export function Root({ children }: { children: ReactNode }) {
  return <ReactRouterProvider>{children}</ReactRouterProvider>;
}
```

```tsx tab="Tanstack Start/Router"
import type { ReactNode } from 'react';
import { TanstackProvider } from 'fumadocs-core/framework/tanstack';

export function Root({ children }: { children: ReactNode }) {
  return <TanstackProvider>{children}</TanstackProvider>;
}
```

It offers simple document searching as well as components for building a
good docs.

<Cards>

<Card
  title="Breadcrumb"
  href="/docs/headless/components/breadcrumb"
  description="The navigation component at the top of screen"
/>

<Card
  title="TOC"
  href="/docs/headless/components/toc"
  description="A Table of Contents with active anchor observer"
/>

<Card
  title="Sidebar"
  href="/docs/headless/components/sidebar"
  description="The navigation bar at aside of viewport"
/>

<Card
  title="Search"
  href="/docs/headless/search"
  description="Implement document searching"
/>

</Cards>
`````

## File: apps/docs/content/docs/headless/internationalization.mdx
`````
---
title: Internationalization
description: Support multiple languages in your documentation
---

## Introduction

Fumadocs core provides necessary middleware and options for i18n support.

You can define a config to share between utilities.

<include cwd meta='title="lib/i18n.ts"'>
  ../../examples/i18n/lib/i18n.ts
</include>

### Hide Locale Prefix

To hide the locale prefix (e.g. `/en/page` -> `/page`), use the `hideLocale` option.

```ts
import type { I18nConfig } from 'fumadocs-core/i18n';

export const i18n: I18nConfig = {
  defaultLanguage: 'en',
  languages: ['en', 'cn'],
  hideLocale: 'default-locale',
};
```

| Mode             | Description                                        |
| ---------------- | -------------------------------------------------- |
| `always`         | Always hide the prefix, detect locale from cookies |
| `default-locale` | Only hide the default locale                       |
| `never`          | Never hide the prefix (default)                    |

<Callout type='warn' title={<>Using <code>always</code></>}>

On `always` mode, locale is stored as a cookie (set by the middleware), which isn't optimal for static sites.

This may cause undesired cache problems, and need to pay extra attention on SEO to ensure search engines can index your pages correctly.

</Callout>

### Middleware

Redirects users to appropriate locale, it can be customised from `i18n.ts`.

<include cwd meta='title="middleware.ts"'>
  ../../examples/i18n/middleware.ts
</include>

> When `hideLocale` is enabled, it uses `NextResponse.rewrite` to hide locale prefixes.
`````

## File: apps/docs/content/docs/headless/page-conventions.mdx
`````
---
title: Routing
description: A shared convention for organizing your documents
---

<Callout title='Before reading'>

    This guide only applies for content sources that uses `loader()` API, such as Fumadocs MDX.

</Callout>

## Overview

While Next.js handles routing, Fumadocs generates **page slugs** and **sidebar items** (page tree) from your content directory using [`loader()`](/docs/headless/source-api).

You can define folders and pages similar to the file-system based routing of Next.js.

<Files>
  <Folder name="content/docs (content directory)" defaultOpen>
    <File name="index.mdx" />
    <File name="getting-started.mdx" />
  </Folder>
</Files>

## File

A [MDX](https://mdxjs.com) or Markdown file, you can customise its frontmatter.

```mdx
---
title: My Page
description: Best document ever
icon: HomeIcon
full: true
---

## Learn More
```

| name          | description                                        |
| ------------- | -------------------------------------------------- |
| `title`       | The title of page                                  |
| `description` | The description of page                            |
| `icon`        | The name of icon, see [Icons](#icons)              |
| `full`        | Fill all available space on the page (Fumadocs UI) |

<Callout title='Fumadocs MDX'>

    You can use the [`schema`](/docs/mdx/collections#schema-1) option to add frontmatter properties.

</Callout>

### Slugs

The slugs of a page are generated from its file path.

| path (relative to content folder) | slugs             |
| --------------------------------- | ----------------- |
| `./dir/page.mdx`                  | `['dir', 'page']` |
| `./dir/index.mdx`                 | `['dir']`         |

## Folder

Organize multiple pages, you can create a [Meta file](#meta) to customise folders.

### Folder Group

By default, putting a file into folder will change its slugs.
You can wrap the folder name in parentheses to avoid impacting the slugs of child files.

| path (relative to content folder) | slugs      |
| --------------------------------- | ---------- |
| `./(group-name)/page.mdx`         | `['page']` |

## Meta

Customise folders by creating a `meta.json` file in the folder.

```json title="meta.json"
{
  "title": "Display Name",
  "icon": "MyIcon",
  "pages": ["index", "getting-started"],
  "defaultOpen": true
}
```

| name          | description                           |
| ------------- | ------------------------------------- |
| `title`       | Display name                          |
| `icon`        | The name of icon, see [Icons](#icons) |
| `pages`       | Folder items (see below)              |
| `defaultOpen` | Open the folder by default            |

### Pages

By default, folder items are sorted alphabetically.

You can add or control the order of items using `pages`, items are not included unless they are listed inside.

```json title="meta.json"
{
  "title": "Name of Folder",
  "pages": ["guide", "components", "---My Separator---", "./nested/page"]
}
```

<Files>
  <File name="meta.json" />
  <File name="guide.mdx" />
  <File name="components.mdx" />
  <File name="nested/page.mdx" />
</Files>

#### Rest

Add a `...` item to include remaining pages (sorted alphabetically), or `z...a` for descending order.

```json title="meta.json"
{
  "pages": ["guide", "..."]
}
```

You can add `!name` to prevent an item from being included.

```json title="meta.json"
{
  "pages": ["guide", "...", "!components"]
}
```

#### Extract

You can extract the items from a folder with `...folder_name`.

```json title="meta.json"
{
  "pages": ["guide", "...nested"]
}
```

#### Link

Use the syntax `[Text](url)` to insert links, or `[Icon][Text](url)` to add icon.

```json title="meta.json"
{
  "pages": [
    "[Vercel](https://vercel.com)",
    "[Triangle][Vercel](https://vercel.com)"
  ]
}
```

## Icons

Since Fumadocs doesn't include an icon library, you have to convert the icon names to JSX elements in runtime, and render it as a component.

You can add an [`icon` handler](/docs/headless/source-api#icons) to `loader()`.

## Root Folder

Marks the folder as a root folder, only items in the opened root folder will be considered.

```json title="meta.json"
{
  "title": "Name of Folder",
  "description": "The description of root folder (optional)",
  "root": true
}
```

For example, when you are opening a root folder `framework`, the other folders (e.g. `headless`) are not shown on the sidebar and other navigation elements.

<Files>
  <Folder name="framework" defaultOpen>
    <File name="index.mdx" />
    <File
      name="current-page.mdx"
      className="!text-fd-primary !bg-fd-primary/10"
    />
    <File name="other-pages.mdx" />
  </Folder>
  <Folder name="headless (hidden)" className="opacity-50" disabled defaultOpen>
    <File name="my-page.mdx" />
  </Folder>
</Files>

<Callout title='Fumadocs UI'>

    Fumadocs UI renders root folders as [Sidebar Tabs](/docs/ui/navigation/sidebar#sidebar-tabs), which allows user to switch between them.

</Callout>

## Internationalization

<include>../../shared/page-conventions.i18n.mdx</include>
`````

## File: apps/docs/content/docs/headless/page-tree.mdx
`````
---
title: Page Tree
description: The structure of page tree.
---

Page tree is a tree structure that describes all navigation links, with other items like separator and folders.

It will be sent to the client and being referenced in navigation elements including the sidebar and breadcrumb.
Hence, you shouldn't store any sensitive or large data in page tree.

<Callout title="Note">

By design, page tree only contains necessary information of all pages and folders.

Unserializable data such as functions can't be passed to page tree.

</Callout>

## Conventions

The type definitions of page tree, for people who want to hardcode/generate it.
You can also import the type from Fumadocs.

```ts
import type { PageTree } from 'fumadocs-core/server';

const tree: PageTree.Root = {
  // props
};
```

Certain nodes contain a `$ref` property, they are internal and not used when hardcoding it.

### Root

The initial root of page trees.

<AutoTypeTable path="./content/docs/headless/props.ts" name="PageTreeRoot" />

### Page

```json
{
  "type": "page",
  "name": "Quick Start",
  "url": "/docs"
}
```

> External urls are also supported

<AutoTypeTable path="./content/docs/headless/props.ts" name="PageTreeItem" />

### Folder

```json
{
    "type": "folder",
    "name": "Guide",
    "index": {
        "type": "page",
        ...
    }
    "children": [
        ...
    ]
}
```

<AutoTypeTable path="./content/docs/headless/props.ts" name="PageTreeFolder" />

### Separator

A label between items.

```json
{
  "type": "separator",
  "name": "Components"
}
```

<AutoTypeTable
  path="./content/docs/headless/props.ts"
  name="PageTreeSeparator"
/>

## Icons

Icon is a `ReactElement`, supported by pages and folders.
`````

## File: apps/docs/content/docs/headless/source-api.mdx
`````
---
title: loader()
description: Turn a content source into a unified interface
---

## Usage

`loader()` provides an interface for Fumadocs to integrate with file-system based content sources.

### What it does?

- Generate page trees based on file system.
- Assign URL and slugs to each page.
- Output useful utilities to interact with content.

It doesn't rely on the real file system (zero `node:fs` usage), a virtual storage is also allowed.

You can use it with built-in content sources like Fumadocs MDX.

```ts
import { loader } from 'fumadocs-core/source';
import { docs } from '@/.source';

export const source = loader({
  source: docs.toFumadocsSource(),
});
```

### URL

You can override the base URL, or specify a function to generate URL for each page.

```ts
import { loader } from 'fumadocs-core/source';

loader({
  baseUrl: '/docs',
  // or you can customise it with function
  url(slugs, locale) {
    if (locale) return '/' + [locale, 'docs', ...slugs].join('/');
    return '/' + ['docs', ...slugs].join('/');
  },
});
```

### Icons

Load the [icon](/docs/headless/page-conventions#icons) property specified by pages and meta files.

```ts
import { loader } from 'fumadocs-core/source';
import { icons } from 'lucide-react';
import { createElement } from 'react';

loader({
  icon(icon) {
    if (!icon) {
      // You may set a default icon
      return;
    }

    if (icon in icons) return createElement(icons[icon as keyof typeof icons]);
  },
});
```

### I18n

Pass the `i18n` config to loader.

```ts title="lib/source.ts"
import { i18n } from '@/lib/i18n';
import { loader } from 'fumadocs-core/source';

export const source = loader({
  i18n, // [!code highlight]
});
```

With i18n enabled, loader will generate a page tree for every locale.

When looking for a page, it fallbacks to default locale if the page doesn't exist for specified locale.

## Output

The loader outputs a source object.

### Get Page

Get page with slugs.

```ts
import { source } from '@/lib/source';

source.getPage(['slug', 'of', 'page']);

// with i18n
source.getPage(['slug', 'of', 'page'], 'locale');
```

### Get Pages

Get a list of page available for locale.

```ts
import { source } from '@/lib/source';

// from default locale
source.getPages();

// for a specific locale
source.getPages('locale');
```

### Page Tree

```ts
import { source } from '@/lib/source';

// without i18n
source.pageTree;

// with i18n
source.pageTree['locale'];
```

### Get from Node

The page tree nodes contain references to their original file path.
You can find their original page or meta file from the tree nodes.

```ts
import { source } from '@/lib/source';

source.getNodePage(pageNode);
source.getNodeMeta(folderNode);
```

### Params

A function to generate output for Next.js `generateStaticParams`.
The generated parameter names will be `slug: string[]` and `lang: string` (i18n only).

```ts title="app/[[...slug]]/page.tsx"
import { source } from '@/lib/source';

export function generateStaticParams() {
  return source.generateParams();
}
```

### Language Entries

Get available languages and its pages.

```ts
import { source } from '@/lib/source';

// language -> pages
const entries = source.getLanguages();
```

## Deep Dive

As mentioned, Source API doesn't rely on real file systems.
During the process, your input source files will be parsed and form a virtual storage to avoid inconsistent behaviour between different OS.

### Transformer

To perform virtual file-system operations before processing, you can add a transformer.

```ts
import { loader } from 'fumadocs-core/source';

loader({
  transformers: [
    ({ storage }) => {
      storage.makeDir();
    },
  ],
});
```

### Page Tree

The page tree is generated from your file system, some unnecessary information (e.g. unused frontmatter properties) will be filtered.

You can customise it using the `pageTree` option, such as attaching custom properties to nodes, or customising the display name of pages.

```tsx
import React from 'react';
import { loader } from 'fumadocs-core/source';

loader({
  pageTree: {
    attachFile(node, file) {
      // you can access its file information
      console.log(file?.data);
      // JSX nodes are allowed
      node.name = <>Some JSX Nodes here</>;

      return node;
    },
  },
});
```

### Custom Source

To plug your own content source, create a `Source` object.

It includes a `files` property which is an array of virtual files.
Each virtual file must contain its file path and corresponding data.
You can check type definitions for more info.

Since Source API doesn't rely on file system, file paths cannot be absolute or relative (for example, `./file.mdx` and `D://content/file.mdx` are not allowed).
Instead, pass the file paths like `file.mdx` and `content/file.mdx`.

```ts
import { Source } from 'fumadocs-core/source';

export function createMySource(): Source<{
  metaData: { title: string; pages: string[] }; // Your custom type
  pageData: { title: string; description: string }; // Your custom type
}> {
  return {
    files: [],
  };
}
```
`````

## File: apps/docs/content/docs/mdx/async.mdx
`````
---
title: Async Mode
description: Runtime compilation of content files.
---

## Introduction

By default, all Markdown and MDX files need to be pre-compiled first. The same constraint also applies to the development server.

This may result in longer dev server start times for large docs sites. You can enable Async Mode on `doc` collections to improve this.

### Setup

Install required dependencies.

```package-install
@fumadocs/mdx-remote shiki
```

Enable Async Mode.

```ts tab="Docs Collection"
import { defineDocs } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: 'content/docs',
  docs: {
    async: true,
  },
});
```

```ts tab="Doc Collection"
import { defineCollections } from 'fumadocs-mdx/config';

export const doc = defineCollections({
  type: 'doc',
  dir: 'content/docs',
  async: true,
});
```

### Usage

Async Mode allows on-demand compilation of Markdown and MDX content by moving the compilation process from build time to Next.js runtime.

However, you need to invoke the `load()` async function to load and compile content.

For example:

```tsx title="lib/source.ts"
import { loader } from 'fumadocs-core/source';
import { docs } from '@/.source';

export const source = loader({
  baseUrl: '/docs',
  source: docs.toFumadocsSource(),
});
```

```tsx title="page.tsx"
import { source } from '@/lib/source';
import { getMDXComponents } from '@/mdx-components';

const page = source.getPage(['...']);

if (page) {
  // frontmatter properties are available
  console.log(page.data);

  // Markdown content requires await
  const { body: MdxContent, toc } = await page.data.load();

  console.log(toc);

  return <MdxContent components={getMDXComponents()} />;
}
```

When using Async Mode, we highly recommend to use third-party services to implement search, which usually have better capability to handle massive amount of content to index.

### Constraints

It comes with some limitations on MDX features.

- No import/export allowed in MDX files. For MDX components, pass them from the `components` prop instead.
- Images must be referenced with URL (e.g. `/images/test.png`). Don't use **file paths** like `./image.png`. You should locate your images in the `public` folder and reference them with URLs.
`````

## File: apps/docs/content/docs/mdx/collections.mdx
`````
---
title: Collections
description: Collection of content data for your app
---

## Define Collections

Define a collection to parse a certain set of files.

```ts
import { defineCollections } from 'fumadocs-mdx/config';
import { z } from 'zod';

export const blog = defineCollections({
  type: 'doc',
  dir: './content/blog',
  schema: z.object({
    // schema
  }),
  // other options
});
```

### `type`

The accepted type of collection.

```ts
import { defineCollections } from 'fumadocs-mdx/config';

// only scan for json/yaml files
export const metaFiles = defineCollections({
  type: 'meta',
  // options
});
```

- `type: meta`

  Accept JSON/YAML files, available options:

  <AutoTypeTable path="./content/docs/mdx/props.ts" name="MetaCollection" />

- `type: doc`

  Markdown/MDX documents, available options:

  <AutoTypeTable path="./content/docs/mdx/props.ts" name="DocCollection" />

### `dir`

Directories to scan for input files.

### `schema`

The schema to validate file data (frontmatter on `doc` type, content on `meta` type).

```ts
import { defineCollections } from 'fumadocs-mdx/config';
import { z } from 'zod';

export const blog = defineCollections({
  type: 'doc',
  dir: './content/blog',
  schema: z.object({
    name: z.string(),
  }),
});
```

> [Standard Schema](https://standardschema.dev) compatible libraries, including Zod, are supported.

Note that the validation is done at build time, hence the output must be serializable.
You can also pass a function that receives the transform context.

```ts
import { defineCollections } from 'fumadocs-mdx/config';
import { z } from 'zod';

export const blog = defineCollections({
  type: 'doc',
  dir: './content/blog',
  schema: (ctx) => {
    return z.object({
      name: z.string(),
      testPath: z.string().default(
        // original file path
        ctx.path,
      ),
    });
  },
});
```

### `mdxOptions`

Customise MDX options at the collection level.

```ts title="source.config.ts"
import { defineCollections, getDefaultMDXOptions } from 'fumadocs-mdx/config';

export const blog = defineCollections({
  type: 'doc',
  mdxOptions: {
    // mdx options
  },
});
```

By design, this will remove all default settings applied by your global config and Fumadocs MDX.
You have full control over MDX options.

You can use `getDefaultMDXOptions` to apply default configurations, it accepts the [extended MDX Options](/docs/mdx/mdx#extended).

```ts title="source.config.ts"
import { defineCollections, getDefaultMDXOptions } from 'fumadocs-mdx/config';

export const blog = defineCollections({
  type: 'doc',
  mdxOptions: getDefaultMDXOptions({
    // extended mdx options
  }),
});
```

> This API is only available on `doc` type.

## Define Docs

Define a collection for Fumadocs.

```ts
import { defineDocs } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: '/my/content/dir',
  docs: {
    // optional, options of `doc` collection
  },
  meta: {
    // optional, options of `meta` collection
  },
});
```

### `dir`

Instead of per collection, you should customise `dir` from `defineDocs`:

```ts
import { defineDocs } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: 'my/content/dir',
});
```

### `schema`

You can extend the default Zod schema of `docs` and `meta`.

```ts
import { frontmatterSchema, metaSchema, defineDocs } from 'fumadocs-mdx/config';
import { z } from 'zod';

export const docs = defineDocs({
  docs: {
    schema: frontmatterSchema.extend({
      index: z.boolean().default(false),
    }),
  },
  meta: {
    schema: metaSchema.extend({
      // other props
    }),
  },
});
```
`````

## File: apps/docs/content/docs/mdx/global.mdx
`````
---
title: Global Options
description: Customise Fumadocs MDX
---

## Global Options

Shared options of Fumadocs MDX.

```ts title="source.config.ts"
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  // global options
});
```

<AutoTypeTable path="./content/docs/mdx/props.ts" name="GlobalConfig" />

### MDX Options

Customise the MDX processor options for MDX files.

```ts title="source.config.ts"
import { defineConfig } from 'fumadocs-mdx/config';
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkMath],
    // When order matters
    rehypePlugins: (v) => [rehypeKatex, ...v],
  },
});
```

Some default options are applied by Fumadocs MDX, see [Extended MDX Options](/docs/mdx/mdx#extended) for available options.
`````

## File: apps/docs/content/docs/mdx/include.mdx
`````
---
title: Include
description: Reuse content from other files.
---

## Usage

### Markdown

Specify the target Markdown file path in the `<include>` tag (relative to the Markdown file itself).

```mdx title="page.mdx"
<include>./another.mdx</include>
```

This will display the content from the target file (e.g. `another.mdx`).

### CodeBlock

For other types of files, it will become a codeblock:

```mdx title="page.mdx"
<include>./script.ts</include>

<include lang="tsx" meta='title="lib.ts"'>
  ./script.ts
</include>
```

### `cwd`

Resolve relative paths from cwd instead of the Markdown file:

```mdx
<include cwd lang="tsx" meta='title="lib.ts"'>
  ./script.ts
</include>
```
`````

## File: apps/docs/content/docs/mdx/index.mdx
`````
---
title: Introduction
description: What is Fumadocs MDX?
icon: Album
---

Fumadocs MDX is the official content source of Fumadocs.

It provides the tool for Next.js to transform content into type-safe data, similar to Content Collections.
This library is made for Next.js, you can use it to handle blog and other contents.

## Getting Started

Set up Fumadocs MDX for your Next.js application.

```package-install
fumadocs-mdx @types/mdx
```

Add the plugin to your `next.config.mjs` file.

```js
import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
};

export default withMDX(config);
```

<Callout title="ESM Only" type='warn' className="mt-4">

    The Next.js config must be a `.mjs` file since Fumadocs is ESM-only.

</Callout>

### Defining Collections

**Collection** refers to a collection containing a certain type of files. You can define collections by creating a `source.config.ts` file.

Fumadocs MDX transforms collections into arrays of type-safe data, accessible in your app. Available collections:

<Tabs items={["doc", "meta", 'docs']}>

    <Tab value='doc'>

Compile Markdown & MDX files into a React Server Component, with useful properties like **Table of Contents**.

```ts title="source.config.ts"
import { defineCollections } from 'fumadocs-mdx/config';

export const test = defineCollections({
  type: 'doc',
  dir: 'content/docs',
});
```

    </Tab>

    <Tab value='meta'>

Transform YAML/JSON files into an array of data.

```ts title="source.config.ts"
import { defineCollections } from 'fumadocs-mdx/config';

export const test = defineCollections({
  type: 'meta',
  dir: 'content/docs',
});
```

    </Tab>
    <Tab value='docs'>

Combination of `meta` and `doc` collections, which is needed for Fumadocs.

```ts title="source.config.ts"
import { defineDocs } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: 'content/docs',
  docs: {
    // options for `doc` collection
  },
  meta: {
    // options for `meta` collection
  },
});
```

    </Tab>

</Tabs>

For example, a `doc` collection will transform the `.md` and `.mdx` files:

<Files>
  <Folder name="folder" defaultOpen>
    <File name="ui.md" />
  </Folder>
  <File name="hello.md" />
  <File name="index.mdx" />
  <File
    name="meta.json"
    className="opacity-50 cursor-not-allowed"
    aria-disabled
  />
</Files>

### Output Folder

A `.source` folder is generated in the root directory when you run `next dev` or `next build`. It contains all output data and types, you should add it to `.gitignore`.

The `fumadocs-mdx` command also generates types for `.source` folder. Add it as a post install script to ensure types are generated when initializing the project.

```json title="package.json"
{
  "scripts": {
    "postinstall": "fumadocs-mdx"
  }
}
```

### Accessing Collections

**Collection Output** is the generated data of a collection. It can have a different type/shape depending on the collection type and schema.

You can access the collection output from `.source` folder with its original name:

```ts tab="source.config.ts"
import { defineDocs } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: 'content/docs',
  docs: {
    // options for `doc` collection
  },
  meta: {
    // options for `meta` collection
  },
});
```

```ts tab="Usage"
import { docs } from '@/.source';

console.log(docs);
```

> Make sure you are importing from `.source` rather than `source.config.ts`. We will import it with `@/.source` import alias in this guide.

## Integrate with Fumadocs

Create a `docs` collection and use the `toFumadocsSource()` function of its output.

```ts title="lib/source.ts"
import { docs } from '@/.source';
import { loader } from 'fumadocs-core/source';

export const source = loader({
  baseUrl: '/docs',
  source: docs.toFumadocsSource(),
});
```

> You can do the same for multiple `docs` collections.

Generally, you'll interact with the collection through [`loader()`](/docs/headless/source-api#output).

```tsx
import { source } from '@/lib/source';

const page = source.getPage(['slugs']);

if (page) {
  // access page data [!code highlight]
  console.log(page.data);

  // frontmatter properties are also inside [!code highlight]
  console.log(page.data.title);
}
```

To render the page, use `page.data.body` as a component.

```tsx
import { getMDXComponents } from '@/mdx-components';

const MDX = page.data.body;

// set your MDX components with `components` prop
return <MDX components={getMDXComponents()} />;
```

## FAQ

### Built-in Properties

These properties are exported from MDX files by default.

| Property         | Description                                     |
| ---------------- | ----------------------------------------------- |
| `frontmatter`    | Frontmatter                                     |
| `toc`            | Table of Contents                               |
| `structuredData` | Structured Data, useful for implementing search |

### Customise Frontmatter

Use the [`schema`](/docs/mdx/collections#schema-1) option to pass a validation schema to validate frontmatter and define its output properties.

### MDX Plugins

For other customisation needs such as Syntax Highlighting, see [MDX Options](/docs/mdx/mdx).
`````

## File: apps/docs/content/docs/mdx/last-modified.mdx
`````
---
title: Last Modified Time
description: Output the last modified time of a document
---

## Usage

This feature is not enabled by default, you can enable this from the config file. Note that it only supports Git as version control.
Please ensure you have Git installed on your machine, and **the repository is not shallow cloned**, as it relies on your local Git history.

```ts title="source.config.ts"
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  lastModifiedTime: 'git', // [!code highlight]
});
```

### Access the Property

After doing this, a `lastModified` number will be exported for each document. You can convert it to a JavaScript Date object.

```ts
import { source } from '@/lib/source';

const page = source.getPage(['...']);

console.log(new Date(page.data.lastModified));
// or with async mode:
const { lastModified } = await page.data.load();
console.log(new Date(lastModified));
```
`````

## File: apps/docs/content/docs/mdx/mdx.mdx
`````
---
title: MDX Options
description: Configure MDX processor for Fumadocs MDX
---

## Customising MDX Processor

Fumadocs MDX uses [MDX Compiler](https://mdxjs.com/packages/mdx) to compile MDX files into JavaScript files.

You can customise it on [Global Config](/docs/mdx/global#mdx-options) or [Collection Config](/docs/mdx/collections#mdxoptions).

## Extended MDX Options [#extended]

Fumadocs MDX will apply some default MDX options, to make features like **syntax highlighting** work out of the box.

To allow overriding the defaults, Fumadocs MDX's `mdxOptions` option accepts **Extended MDX Options** on top of [`ProcessorOptions`](https://mdxjs.com/packages/mdx/#processoroptions).
Additional options below:

### Remark Plugins

These plugins are applied by default:

- [Remark Image](/docs/headless/mdx/remark-image) - Handle images
- [Remark Heading](/docs/headless/mdx/headings) - Extract table of contents
- [Remark Structure](/docs/headless/mdx/structure) - Generate search indexes
- Remark Exports - Exports the output generated by remark plugins above

Add other remark plugins with:

```ts tab="Global Config"
import { defineConfig } from 'fumadocs-mdx/config';
import { myPlugin } from './remark-plugin';

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [myPlugin],
    // You can also pass a function to control the order of remark plugins.
    remarkPlugins: (v) => [myPlugin, ...v],
  },
});
```

```ts tab="Collection Config"
import { defineCollections, getDefaultMDXOptions } from 'fumadocs-mdx/config';
import { myPlugin } from './remark-plugin';

export const blog = defineCollections({
  type: 'doc',
  mdxOptions: getDefaultMDXOptions({
    remarkPlugins: [myPlugin],
    // You can also pass a function to control the order of remark plugins.
    remarkPlugins: (v) => [myPlugin, ...v],
  }),
});
```

### Rehype Plugins

These plugins are applied by default:

- [Rehype Code](/docs/headless/mdx/rehype-code) - Syntax highlighting

Same as remark plugins, you can pass an array or a function to add other rehype plugins.

```ts tab="Global Config"
import { defineConfig } from 'fumadocs-mdx/config';
import { myPlugin } from './rehype-plugin';

export default defineConfig({
  mdxOptions: {
    rehypePlugins: (v) => [myPlugin, ...v],
  },
});
```

```ts tab="Collection Config"
import { defineCollections, getDefaultMDXOptions } from 'fumadocs-mdx/config';
import { myPlugin } from './rehype-plugin';

export const blog = defineCollections({
  type: 'doc',
  mdxOptions: getDefaultMDXOptions({
    rehypePlugins: (v) => [myPlugin, ...v],
  }),
});
```

### Customise Built-in Plugins

Customise the options of built-in plugins like:

```ts tab="Global Config"
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    rehypeCodeOptions: {
      // options
    },
    remarkImageOptions: {
      // options
    },
    remarkHeadingOptions: {
      // options
    },
  },
});
```

```ts tab="Collection Config"
import { defineCollections, getDefaultMDXOptions } from 'fumadocs-mdx/config';

export const blog = defineCollections({
  type: 'doc',
  mdxOptions: getDefaultMDXOptions({
    rehypeCodeOptions: {
      // options
    },
    remarkImageOptions: {
      // options
    },
    remarkHeadingOptions: {
      // options
    },
  }),
});
```

### Export Properties from `vfile.data`

Some remark plugins store their output in `vfile.data` (compile-time memory) which cannot be accessed from your code.
Fumadocs MDX applies a remark plugin that turns `vfile.data` properties into ESM exports, so you can access these properties when importing the MDX file.

You can define additional properties to be exported.

```ts tab="Global Config"
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    valueToExport: ['dataName'],
  },
});
```

```ts tab="Collection Config"
import { defineCollections, getDefaultMDXOptions } from 'fumadocs-mdx/config';

export const blog = defineCollections({
  type: 'doc',
  mdxOptions: getDefaultMDXOptions({
    valueToExport: ['dataName'],
  }),
});
```

By default, it includes:

- `toc` for the Remark Heading plugin
- `structuredData` for the Remark Structure Plugin
- `frontmatter` for the frontmatter of MDX (using `gray-matter`)
`````

## File: apps/docs/content/docs/mdx/page.mdx
`````
---
title: Use as Page
description: Use MDX file as a page
---

## Setup

You can use `page.mdx` instead of `page.tsx` for creating a new page under the app directory.

However, it doesn't have MDX components by default, so you have to provide them:

```tsx title="mdx-components.tsx"
import defaultMdxComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents, // for Fumadocs UI
    ...components,
  };
}

// export a `useMDXComponents()` that returns MDX components
export const useMDXComponents = getMDXComponents; // [!code ++]
```

```ts title="source.config.ts"
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    // Path to import your `mdx-components.tsx` above. [!code ++]
    providerImportSource: '@/mdx-components',
  },
});
```

### Usage

```mdx title="app/test/page.mdx"
{/* this will enable Typography styles of Fumadocs UI */}
export { withArticle as default } from 'fumadocs-ui/page';

## Hello World
```
`````

## File: apps/docs/content/docs/mdx/performance.mdx
`````
---
title: Performance
description: The performance of Fumadocs MDX
icon: Rocket
---

## Overview

Fumadocs MDX is a bundler plugin, in other words, it has a higher performance bottleneck.
With bundlers like Webpack and Turbopack, it is enough for large docs sites with nearly 500+ MDX files, which is sufficient for almost all use cases.

Since Fumadocs MDX works with your bundler, you can import any files including client components in your MDX files.
This allows high flexibility and ensures everything is optimized by default.

### Image Optimization

Fumadocs MDX resolves images into static imports with [Remark Image](/docs/headless/mdx/remark-image).
Therefore, your images will be optimized automatically by the Next.js Image API.

```mdx
![Hello](./hello.png)

or in public folder

![Hello](/hello.png)
```

Yields:

```mdx
import HelloImage from './hello.png';

<img alt="Hello" src={HelloImage} />
```

![Banner](/banner.png)

## Caveats

Although Fumadocs MDX can handle nearly 500+ files, it could be slow and inefficient.
A huge amount of MDX files can cause extremely high memory usage during build and development mode.

This is because of:

- Bundlers do a lot of work under the hood to bundle MDX and JavaScript files and optimize performance.
- Bundlers are not supposed to compile hundreds of MDX files.

### Solutions

The main solution is to make the compilation on-demand, such that content is only loaded when it's being requested.

#### Remote Source

Remote sources don't need to pre-compile MDX files, it can compile them on-demand with SSG which can **highly increase your build speed.**
However, you cannot use import in MDX files anymore.

See [Custom Source](/docs/headless/custom-source) for configuring remote sources.

#### Async Mode

See [Async Mode](/docs/mdx/async).
`````

## File: apps/docs/content/docs/mdx/plugin.mdx
`````
---
title: Next.js Loader
description: Customise the Next.js loader
---

## Plugin Options

Fumadocs MDX offers loaders and a Fumadocs [Source API](/docs/headless/source-api) adapter for integration with Fumadocs.
You can configure the plugin by passing options to `createMDX` in `next.config.mjs`.

### Config Path

Customise the config file path.

```ts
import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX({
  configPath: './my-config.ts',
});
```

### Development Server

When running in development mode (`next dev`), a file watcher starts to monitor for changes.
It automatically re-generates the index file in `.source` folder, ensuring Next.js hot reload is working properly.
`````

## File: apps/docs/content/docs/openapi/index.mdx
`````
---
title: Scalar Example
description: View the Scalar Galaxy example OpenAPI schema.
index: true
---
`````

## File: apps/docs/content/docs/ui/(integrations)/openapi/configurations.mdx
`````
---
title: Configurations
description: Customise Fumadocs OpenAPI
---

## File Generator

Pass options to the `generateFiles` function.

### Input

An array of input files.
Allowed:

- File Paths
- External URLs
- Wildcard

```ts
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  input: ['./unkey.json'],
});
```

### Output

The output directory.

```ts
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  output: '/content/docs',
});
```

### Per

Customise how the page is generated, default to `operation`.

> Operation in OpenAPI schema refers to an API endpoint with specific method like `/api/weather:GET`.

| mode      |                             | output                                |
| --------- | --------------------------- | ------------------------------------- |
| tag       | operations with same tag    | `{tag_name}.mdx`                      |
| file      | operations in schema schema | `{file_name}.mdx`                     |
| operation | each operation              | `{operationId ?? endpoint_path}.mdx`) |

```ts
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  per: 'tag',
});
```

### Group By

In `operation` mode, you can group output files with folders.

| value | output                                                 |
| ----- | ------------------------------------------------------ |
| tag   | `{tag}/{operationId ?? endpoint_path}.mdx`             |
| route | `{endpoint_path}/{method}.mdx` (ignores `name` option) |
| none  | `{operationId ?? endpoint_path}.mdx` (default)         |

```ts
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  per: 'operation',
  groupBy: 'tag',
});
```

### Name

A function that controls the output path of MDX pages.

```ts
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  name: (output, document) => {
    if (output.type === 'operation') {
      const operation = document.paths![output.item.path]![output.item.method]!;
      // operation object
      console.log(operation);

      return 'my-dir/filename';
    }

    const hook = document.webhooks![output.item.name][output.item.method]!;
    // webhook object
    console.log(hook);
    return 'my-dir/filename';
  },
});
```

### Frontmatter

Customise the frontmatter of MDX files.

By default, it includes:

| property      | description                                      |
| ------------- | ------------------------------------------------ |
| `title`       | Page title                                       |
| `description` | Page description                                 |
| `full`        | Always true, added for Fumadocs UI               |
| `method`      | Available method of operation (`operation` mode) |
| `route`       | Route of operation (`operation` mode)            |

```ts
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  input: ['./petstore.yaml'],
  output: './content/docs',
  frontmatter: (title, description) => ({
    myProperty: 'hello',
  }),
});
```

### Add Generated Comment

Add a comment to the top of generated files indicating they are auto-generated.

```ts
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  input: ['./petstore.yaml'],
  output: './content/docs',
  // Add default comment
  addGeneratedComment: true,

  // Or provide a custom comment
  addGeneratedComment: 'Custom auto-generated comment',

  // Or disable comments
  addGeneratedComment: false,
});
```

### Tag Display Name

Adding `x-displayName` to OpenAPI Schema can control the display name of your tags.

```yaml title="openapi.yaml"
tags:
  - name: test
    description: this is a tag.
    x-displayName: My Test Name
```

## OpenAPI Server

The server to render pages.

### Generate Code Samples

Generate custom code samples for each API endpoint. Make sure to install the types package to give you type-safety when customising it:

```package-install
openapi-types -D
```

```ts
import { createOpenAPI } from 'fumadocs-openapi/server';

export const openapi = createOpenAPI({
  generateCodeSamples(endpoint) {
    return [
      {
        lang: 'js',
        label: 'JavaScript SDK',
        source: "console.log('hello')",
      },
    ];
  },
});
```

In addition, you can also specify code samples via OpenAPI schema.

```yaml
paths:
  /plants:
    get:
      x-codeSamples:
        - lang: js
          label: JavaScript SDK
          source: |
            const planter = require('planter');
            planter.list({ unwatered: true });
```

#### Disable Code Sample

You can disable the code sample for a specific language, for example, to disable cURL:

```ts
import { createOpenAPI } from 'fumadocs-openapi/server';

export const openapi = createOpenAPI({
  generateCodeSamples(endpoint) {
    return [
      {
        lang: 'curl',
        label: 'cURL',
        source: false,
      },
    ];
  },
});
```

### Renderer

Customise components in the page.

```ts
import { createOpenAPI } from 'fumadocs-openapi/server';

export const openapi = createOpenAPI({
  renderer: {
    Root(props) {
      // your own (server) component
    },
  },
});
```

## Advanced

### Using API Page

> This is not a public API, use it carefully.

To use the `APIPage` component in your MDX files:

```mdx
---
title: Delete Api
full: true
---

<APIPage
  document="./unkey.json"
  operations={[{ path: '/v1/apis.deleteApi', method: 'post' }]}
  hasHead={false}
/>
```

Unlike using the `generateFiles()` function, this supports revalidation of the OpenAPI schema if given an URL.

| Prop         | Description                               |
| ------------ | ----------------------------------------- |
| `document`   | OpenAPI Schema                            |
| `operations` | Operations (API endpoints) to be rendered |
| `hasHead`    | Enable to render the heading of operation |
`````

## File: apps/docs/content/docs/ui/(integrations)/openapi/index.mdx
`````
---
title: OpenAPI
description: Generating docs for OpenAPI schema
---

## Manual Setup

Install the required packages.

```package-install
fumadocs-openapi shiki
```

### Generate Styles

Please note that you must have Tailwind CSS v4 configured.

```css title="Tailwind CSS"
@import 'tailwindcss';
@import 'fumadocs-ui/css/neutral.css';
@import 'fumadocs-ui/css/preset.css';
/* [!code ++] */
@import 'fumadocs-openapi/css/preset.css';
```

### Configure Pages

Create an OpenAPI instance on the server. Fumadocs OpenAPI renders the pages on server-side.

```ts title="lib/source.ts"
import { createOpenAPI, attachFile } from 'fumadocs-openapi/server';
import { loader } from 'fumadocs-core/source';

export const source = loader({
  pageTree: {
    // [!code ++] adds a badge to each page item in page tree
    attachFile,
  },
});

// [!code ++]
export const openapi = createOpenAPI();
```

Add `APIPage` to your MDX Components, so that you can use it in MDX files.

```tsx title="mdx-components.tsx"
import defaultComponents from 'fumadocs-ui/mdx';
import { APIPage } from 'fumadocs-openapi/ui';
import { openapi } from '@/lib/source';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    APIPage: (props) => <APIPage {...openapi.getAPIPageProps(props)} />,
    ...components,
  };
}
```

> It is a React Server Component.

### Generate Files

You can generate MDX files directly from your OpenAPI schema.

Create a script:

```js title="scripts/generate-docs.mjs"
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  // the OpenAPI schema, you can also give it an external URL.
  input: ['./unkey.json'],
  output: './content/docs',
  // we recommend to enable it
  // make sure your endpoint description doesn't break MDX syntax.
  includeDescription: true,
});
```

> Only OpenAPI 3.0 and 3.1 are supported.

Generate docs with the script:

```bash
node ./scripts/generate-docs.mjs
```

## Features

The official OpenAPI integration supports:

- Basic API endpoint information
- Interactive API playground
- Example code to send request (in different programming languages)
- Response samples and TypeScript definitions
- Request parameters and body generated from schemas

### Demo

[View demo](/docs/openapi).
`````

## File: apps/docs/content/docs/ui/(integrations)/openapi/media-adapters.mdx
`````
---
title: Media Adapters
description: Support other media types
---

## Overview

A media adapter in Fumadocs handle:

- Encode: convert form data into `fetch()` body with corresponding media type.
- Example: generate code example based on different programming language/tool.

Put your media adapters in a separate file with `use client` directive.

```ts title="lib/media-adapters.ts" twoslash
'use client';

import type { MediaAdapter } from 'fumadocs-openapi';

export const myAdapter: MediaAdapter = {
  encode(data) {
    return JSON.stringify(data.body);
  },
  // returns code that inits a `body` variable, used for request body
  generateExample(data, ctx) {
    if (ctx.lang === 'js') {
      return `const body = "hello world"`;
    }

    if (ctx.lang === 'python') {
      return `body = "hello world"`;
    }

    if (ctx.lang === 'go' && 'addImport' in ctx) {
      ctx.addImport('strings');

      return `body := strings.NewReader("hello world")`;
    }
  },
};
```

```ts title="lib/source.ts"
import { createOpenAPI } from 'fumadocs-openapi/server';
import { myAdapter } from './media-adapters';

export const openapi = createOpenAPI({
  proxyUrl: '/api/proxy',
  mediaAdapters: {
    // [!code ++] override the default adapter of `application/json`
    'application/json': myAdapter,
  },
});
```
`````

## File: apps/docs/content/docs/ui/(integrations)/openapi/proxy.mdx
`````
---
title: Creating Proxy
description: Avoid CORS problem
---

## Introduction

A proxy server is useful for executing HTTP (`fetch`) requests, as it doesn't have CORS constraints like on the browser.
We can use it for executing HTTP requests on the OpenAPI playground, when the target API endpoints do not have CORS configured correctly.

<Callout type="warn" title="Warning">
  Do not use this on unreliable sites and API endpoints, the proxy server will
  forward all received headers & body, including HTTP-only `Cookies` and
  `Authorization` header.
</Callout>

### Setup

Create a route handler for proxy server.

```ts title="/api/proxy/route.ts"
import { openapi } from '@/lib/source';

export const { GET, HEAD, PUT, POST, PATCH, DELETE } = openapi.createProxy({
  // optional, we recommend to set a list of allowed origins for proxied requests
  allowedOrigins: ['https://example.com'],
});
```

> Follow the [Getting Started](/docs/ui/openapi) guide if `openapi` server is not yet configured.

And enable the proxy from `createOpenAPI`.

```ts title="lib/source.ts"
import { createOpenAPI } from 'fumadocs-openapi/server';

export const openapi = createOpenAPI({
  proxyUrl: '/api/proxy', // [!code ++]
});
```
`````

## File: apps/docs/content/docs/ui/(integrations)/feedback.mdx
`````
---
title: Feedback
description: Receive feedback from your users
---

## Overview

Feedback is crucial for knowing what your reader thinks, and help you to further improve documentation content.

## Installation

Add dependencies:

```package-install
class-variance-authority lucide-react
```

Copy the component:

<include cwd meta='title="components/rate.tsx"'>
  ./components/rate.tsx
</include>

The `@/lib/cn` import specifier may be different for your project, change it to import your `cn()` function if needed. (e.g. like `@/lib/utils`)

### How to Use

Now add the `<Rate />` component to your docs page:

```tsx
import { DocsPage } from 'fumadocs-ui/page';
import { Rate } from '@/components/rate';
import posthog from 'posthog-js';

export default async function Page() {
  return (
    <DocsPage toc={toc} full={page.data.full}>
      {/* at the bottom of page */}
      <Rate
        onRateAction={async (url, feedback) => {
          'use server';

          await posthog.capture('on_rate_docs', feedback);
        }}
      />
    </DocsPage>
  );
}
```

On above example, it reports user feedback by capturing a `on_rate_docs` event on PostHog.

You can specify your own server action to `onRateAction`, and report the feedback to different destinations like database, or GitHub Discussions via their API.

### Linking to GitHub Discussion

To report your feedback to GitHub Discussion, make a custom `onRateAction`.

You can copy this example as a starting point:

<include cwd meta="lib/github.ts">
  ./lib/github.ts
</include>

- Create your own GitHub App and obtain its app ID and private key.
- Fill required environment variables.
- Replace constants like `owner`, `repo`, and `DocsCategory`.
`````

## File: apps/docs/content/docs/ui/(integrations)/llms.mdx
`````
---
title: LLM
description: Output docs content for large language models.
---

## Overview

It's simple in Fumadocs to make your docs site more AI-friendly.

First, make a `getLLMText` function that converts pages into static MDX content:

<include>./get-llm-text.ts</include>

> Modify it to include other remark plugins.

### `llms.txt`

A version of docs for AIs to read.

<include meta='title="app/llms.txt/route.ts"'>./llms.txt.ts</include>

### `*.mdx`

Allow people to append `.mdx` to a page to get its Markdown/MDX content.

Make a route handler to return page content.

<include meta='title="app/llms.mdx/[[...slug]]/route.ts"'>
  ./llms.mdx.ts
</include>

And redirect users to that route.

```ts title="next.config.ts"
import type { NextConfig } from 'next';

const config: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/docs/:path*.mdx',
        destination: '/llms.mdx/:path*',
      },
    ];
  },
};
```
`````

## File: apps/docs/content/docs/ui/(integrations)/open-graph.mdx
`````
---
title: Metadata
description: Usage with Next.js Metadata API
---

## Introduction

Next.js provides an useful set of utilities, allowing a flexible experience with Fumadocs.
Fumadocs uses the Next.js Metadata API for SEO.

Make sure to read their [Metadata section](https://nextjs.org/docs/app/building-your-application/optimizing/metadata) for the fundamentals of Metadata API.

## Open Graph Image

For docs pages, Fumadocs has a built-in metadata image generator.

You will need a route handler to get started.

<include cwd meta='title="app/docs-og/[...slug]/route.tsx"'>
  ../../examples/next-mdx/app/docs-og/[...slug]/route.tsx
</include>

> We need to append `image.png` to the end of slugs so that we can access it via `/docs-og/my-page/image.png`.

In your docs page, add the image to metadata.

```tsx title="app/docs/[[...slug]]/page.tsx"
import { notFound } from 'next/navigation';
import { source } from '@/lib/source';

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug?: string[] }>;
}) {
  const { slug = [] } = await params;
  const page = source.getPage(slug);
  if (!page) notFound();

  const image = ['/docs-og', ...slug, 'image.png'].join('/');
  return {
    title: page.data.title,
    description: page.data.description,
    openGraph: {
      images: image,
    },
    twitter: {
      card: 'summary_large_image',
      images: image,
    },
  };
}
```

### Font

You can also customise the font, options for Satori are also available on the built-in generator.

```ts
import { generateOGImage } from 'fumadocs-ui/og';

generateOGImage({
  fonts: [
    {
      name: 'Roboto',
      // Use `fs` (Node.js only) or `fetch` to read the font as Buffer/ArrayBuffer and provide `data` here.
      data: robotoArrayBuffer,
      weight: 400,
      style: 'normal',
    },
  ],
});
```
`````

## File: apps/docs/content/docs/ui/(integrations)/python.mdx
`````
---
title: Python
description: Generate docs from Python
---

<Callout type="warn" title="Experiemntal">
  Support for Python docgen is still experimental, please use it in caution.
</Callout>

## Setup

```package-install
fumadocs-python shiki
```

### Generate Docs

Install the Python command first, we need it to collect docs from your Python package.

```bash
pip install ./node_modules/fumadocs-python
```

Generate the docs as a JSON:

```bash
fumapy-generate your-package-name
# for example
fumapy-generate httpx
```

Use the following script to convert JSON into MDX:

```js title="scripts/generate-docs.mjs"
import { rimraf } from 'rimraf';
import * as Python from 'fumadocs-python';
import * as fs from 'node:fs/promises';

// output JSON file path
const jsonPath = './httpx.json';

async function generate() {
  const out = 'content/docs/(api)';
  // clean previous output
  await rimraf(out);

  const content = JSON.parse((await fs.readFile(jsonPath)).toString());
  const converted = Python.convert(content, {
    baseUrl: '/docs',
  });

  await Python.write(converted, {
    outDir: out,
  });
}

void generate();
```

<Callout type="warn" title="Be careful">
  While most docgens use Markdown or reStructuredText, Fumadocs uses **MDX**.
  Make sure your doc is valid in MDX syntax before running.
</Callout>

### MDX Components

Add the components.

```tsx
import defaultMdxComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import * as Python from 'fumadocs-python/components';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    ...Python,
    ...components,
  };
}
```

Add styles:

```css title="Tailwind CSS"
@import 'tailwindcss';
@import 'fumadocs-ui/css/neutral.css';
@import 'fumadocs-ui/css/preset.css';
/* [!code ++] */
@import 'fumadocs-python/preset.css';
```
`````

## File: apps/docs/content/docs/ui/(integrations)/rss.mdx
`````
---
title: RSS
description: Generate a RSS feed for your docs/blog.
---

## Overview

You can implement the feed using a route handler like:

```ts title="app/rss.xml/route.ts"
import { Feed } from 'feed';
import { source } from '@/lib/source';
import { NextResponse } from 'next/server';

export const revalidate = false;

const baseUrl = 'https://fumadocs.dev';

export function GET() {
  const feed = new Feed({
    title: 'Fumadocs Blog',
    id: `${baseUrl}/blog`,
    link: `${baseUrl}/blog`,
    language: 'en',

    image: `${baseUrl}/banner.png`,
    favicon: `${baseUrl}/icon.png`,
    copyright: 'All rights reserved 2025, Fuma Nama',
  });

  for (const page of source.getPages().sort((a, b) => {
    return new Date(b.data.date).getTime() - new Date(a.data.date).getTime();
  })) {
    feed.addItem({
      id: page.url,
      title: page.data.title,
      description: page.data.description,
      link: `${baseUrl}${page.url}`,
      date: new Date(page.data.date),

      author: [
        {
          name: 'Fuma',
        },
      ],
    });
  }

  return new NextResponse(feed.rss2());
}
```

You can add an alternates object to the metadata object with your feed’s title and URL.

```ts title="app/layout.tsx"
import type { Metadata } from 'next';

export const metadata: Metadata = {
  alternates: {
    types: {
      'application/rss+xml': [
        {
          title: 'Fumadocs Blog',
          url: 'https://fumadocs.dev/blog/index.xml',
        },
      ],
    },
  },
};
```
`````

## File: apps/docs/content/docs/ui/(integrations)/typescript.mdx
`````
---
title: Typescript
description: Generate docs from Typescript definitions
---

## Usage

```package-install
fumadocs-typescript
```

### UI Integration

It comes with the `AutoTypeTable` component. Learn more about [Auto Type Table](/docs/ui/components/auto-type-table).

### MDX Integration

You can use it as a remark plugin:

```ts title="source.config.ts" tab="Fumadocs MDX"
import { remarkAutoTypeTable, createGenerator } from 'fumadocs-typescript';
import { defineConfig } from 'fumadocs-mdx/config';

const generator = createGenerator();

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [[remarkAutoTypeTable, { generator }]],
  },
});
```

```ts tab="MDX Compiler"
import { remarkAutoTypeTable, createGenerator } from 'fumadocs-typescript';
import { compile } from '@mdx-js/mdx';

const generator = createGenerator();

await compile('...', {
  remarkPlugins: [[remarkAutoTypeTable, { generator }]],
});
```

It gives you a `auto-type-table` component.

You can use it like [Auto Type Table](/docs/ui/components/auto-type-table), but with additional rules:

- The value of attributes must be string.
- `path` accepts a path relative to the MDX file itself.
- You also need to add [`TypeTable`](/docs/ui/components/type-table) to MDX components.

```ts title="path/to/file.ts"
export interface MyInterface {
  name: string;
}
```

```mdx title="page.mdx"
<auto-type-table path="./path/to/file.ts" name="MyInterface" />
```

## Annotations

### Hide

Hide a field by adding `@internal` tsdoc tag.

```ts
interface MyInterface {
  /**
   * @internal
   */
  cache: number;
}
```

### Specify Type Name

You can specify the name of a type with the `@remarks` tsdoc tag.

```ts
interface MyInterface {
  /**
   * @remarks `timestamp` Returned by API. // [!code highlight]
   */
  time: number;
}
```

This will make the type of `time` property to be shown as `timestamp`.
`````

## File: apps/docs/content/docs/ui/components/accordion.mdx
`````
---
title: Accordion
description: Add Accordions to your documentation
preview: accordion
---

## Usage

Based on
[Radix UI Accordion](https://www.radix-ui.com/primitives/docs/components/accordion), useful for FAQ sections.

```mdx
import { Accordion, Accordions } from 'fumadocs-ui/components/accordion';

<Accordions type="single">
  <Accordion title="My Title">My Content</Accordion>
</Accordions>
```

### Accordions

<AutoTypeTable path="./content/docs/ui/props.ts" name="AccordionsProps" />

### Accordion

<AutoTypeTable path="./content/docs/ui/props.ts" name="AccordionProps" />

### Linking to Accordion

You can specify an `id` for accordion. The accordion will automatically open when the user is navigating to the page with the specified `id` in hash parameter.

```mdx
<Accordions>
<Accordion title="My Title" id="my-title">

My Content

</Accordion>
</Accordions>
```

> The value of accordion is same as title by default. When an id presents, it will be used as the value instead.
`````

## File: apps/docs/content/docs/ui/components/auto-type-table.mdx
`````
---
title: Auto Type Table
description: Auto-generated type table
---

<Wrapper>

<div className="bg-fd-background p-4 rounded-xl">

<AutoTypeTable name="AutoTypeTableExample" type={`export interface AutoTypeTableExample {
    /**
     * Markdown syntax like links, \`code\` are supported.
     *
     * See https://fumadocs.vercel.app/docs/ui/components/type-table
     */
    name: string;

    /**
    * We love Shiki.
    *
    * \`\`\`ts
    * console.log("Hello World, powered by Shiki");
    * \`\`\`
    */
    options: Partial<{ a: unknown }>;

}`} />

</div>

</Wrapper>

It generates a table for your docs based on TypeScript definitions.

## Usage

```package-install
fumadocs-typescript
```

Initialize the TypeScript compiler and add it as a MDX component.

```tsx title="mdx-components.tsx"
import defaultComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import { createGenerator } from 'fumadocs-typescript';
import { AutoTypeTable } from 'fumadocs-typescript/ui';

const generator = createGenerator();

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    AutoTypeTable: (props) => (
      <AutoTypeTable {...props} generator={generator} />
    ),
    ...components,
  };
}
```

### From File

It accepts a `path` prop that points to a typescript file, and `name` for the exported type name.

```ts title="path/to/file.ts"
export interface MyInterface {
  name: string;
}
```

```mdx
<AutoTypeTable path="./path/to/file.ts" name="MyInterface" />
```

The path is relative to your project directory (`cwd`), because `AutoTypeTable` is a React Server Component, it cannot access build-time information like MDX file path.

<Callout title="Server Component only" type="warn">

You cannot use this in a client component.

</Callout>

### From Type

You can specify the type to generate, without an actual TypeScript file.

```mdx
import { AutoTypeTable } from 'fumadocs-typescript/ui';

<AutoTypeTable type="{ hello: string }" />
```

When a `path` is given, it shares the same context as the TypeScript file.

```ts title="file.ts"
export type A = { hello: string };
```

```mdx
<AutoTypeTable path="file.ts" type="A & { world: string }" />
```

When `type` has multiple lines, the export statement and `name` prop are required.

```mdx
<AutoTypeTable
  path="file.ts"
  name="B"
  type={`
import { ReactNode } from "react"
export type B = ReactNode | { world: string }
`}
/>
```

### Functions

Notice that only object type is allowed. For functions, you should wrap them into an object instead.

```ts
export interface MyInterface {
  myFn: (input: string) => void;
}
```

### References

<auto-type-table path="../props.ts" name="AutoTypeTableProps" />

### File System

It relies on the file system, hence, the page referencing this component must be built in **build time**. Rendering the component on serverless runtime may cause problems.

### Deep Dive

Under the hood, it uses the [Typescript Compiler API](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API) to extract type information.
Your `tsconfig.json` file in the current working directory will be loaded.

To change the compiler settings, pass a `options` prop to the component.

Learn more about [Typescript Docs Generation](/docs/ui/typescript).
`````

## File: apps/docs/content/docs/ui/components/banner.mdx
`````
---
title: Banner
description: Add a banner to your site
preview: banner
---

## Usage

Put the element at the top of your root layout, you can use it for displaying announcements.

```tsx
import { Banner } from 'fumadocs-ui/components/banner';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <html lang="en">
      <body>
        <Banner>Hello World</Banner>
        {children}
      </body>
    </html>
  );
}
```

### Variant

Change the default variant.

```tsx
import { Banner } from 'fumadocs-ui/components/banner';

<Banner variant="rainbow">Hello World</Banner>;
```

### Change Layout

By default, the banner uses a `style` tag to modify Fumadocs layouts (e.g. reduce the sidebar height).
You can disable it with:

```tsx
import { Banner } from 'fumadocs-ui/components/banner';

<Banner changeLayout={false}>Hello World</Banner>;
```

### Close

To allow users to close the banner, give the banner an ID.

```tsx
import { Banner } from 'fumadocs-ui/components/banner';

<Banner id="hello-world">Hello World</Banner>;
```

The state will be automatically persisted.
`````

## File: apps/docs/content/docs/ui/components/dynamic-codeblock.mdx
`````
---
title: Code Block (Dynamic)
description: A codeblock that also highlights code
preview: dynamicCodeBlock
---

## Usage

### Client Component

```tsx
import { DynamicCodeBlock } from 'fumadocs-ui/components/dynamic-codeblock';

<DynamicCodeBlock lang="ts" code='console.log("Hello World")' />;
```

Unlike the MDX [`CodeBlock`](/docs/ui/mdx/codeblock) component, this is a client component that can be used without MDX.
It highlights the code with Shiki and use the default component to render it.

Features:

- Can be pre-rendered on server
- load languages and themes on browser lazily

#### Options

```tsx
import { DynamicCodeBlock } from 'fumadocs-ui/components/dynamic-codeblock';

<DynamicCodeBlock
  lang="ts"
  code='console.log("Hello World")'
  options={{
    themes: {
      light: 'github-light',
      dark: 'github-dark',
    },
    components: {
      // override components (e.g. `pre` and `code`)
    },
    // other Shiki options
  }}
/>;
```

### Server Component

For a server component equivalent, you can use the built-in utility from core:

<include>./server-codeblock.tsx</include>
`````

## File: apps/docs/content/docs/ui/components/files.mdx
`````
---
title: Files
description: Display file structure in your documentation
preview: 'files'
---

## Usage

Wrap file components in `Files`.

```mdx
import { File, Folder, Files } from 'fumadocs-ui/components/files';

<Files>
  <Folder name="app" defaultOpen>
    <File name="layout.tsx" />
    <File name="page.tsx" />
    <File name="global.css" />
  </Folder>
  <Folder name="components">
    <File name="button.tsx" />
    <File name="tabs.tsx" />
    <File name="dialog.tsx" />
  </Folder>
  <File name="package.json" />
</Files>
```

### File

<AutoTypeTable path="./content/docs/ui/props.ts" name="FileProps" />

### Folder

<AutoTypeTable path="./content/docs/ui/props.ts" name="FolderProps" />
`````

## File: apps/docs/content/docs/ui/components/github-info.mdx
`````
---
title: GitHub Info
description: Display your GitHub repository information
preview: githubInfo
---

## Usage

```tsx
import { GithubInfo } from 'fumadocs-ui/components/github-info';

<GithubInfo
  owner="fuma-nama"
  repo="fumadocs"
  // your own GitHub access token (optional)
  token={process.env.GITHUB_TOKEN}
/>;
```

It's recommended to add it to your docs layout with `links` option:

```tsx title="app/docs/layout.tsx"
import { DocsLayout, type DocsLayoutProps } from 'fumadocs-ui/layouts/notebook';
import type { ReactNode } from 'react';
import { baseOptions } from '@/app/layout.config';
import { source } from '@/lib/source';
import { GithubInfo } from 'fumadocs-ui/components/github-info';

const docsOptions: DocsLayoutProps = {
  ...baseOptions,
  tree: source.pageTree,
  links: [
    {
      type: 'custom',
      children: (
        <GithubInfo owner="fuma-nama" repo="fumadocs" className="lg:-mx-2" />
      ),
    },
  ],
};

export default function Layout({ children }: { children: ReactNode }) {
  return <DocsLayout {...docsOptions}>{children}</DocsLayout>;
}
```
`````

## File: apps/docs/content/docs/ui/components/image-zoom.mdx
`````
---
title: Zoomable Image
description: Allow zoom-in images in your documentation
preview: zoomImage
---

## Usage

Replace `img` with `ImageZoom` in your MDX components.

```tsx title="mdx-components.tsx"
import { ImageZoom } from 'fumadocs-ui/components/image-zoom';
import defaultComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    img: (props) => <ImageZoom {...(props as any)} />,
    ...components,
  };
}
```

Now image zoom will be automatically enabled on all images.

```mdx
![Test](/banner.png)
```

### Image Optimization

A default [`sizes` property](https://nextjs.org/docs/app/api-reference/components/image#sizes) will be defined for Next.js `<Image />` component if not specified.
`````

## File: apps/docs/content/docs/ui/components/index.mdx
`````
---
title: Components
description: Additional components to improve your docs
index: true
---
`````

## File: apps/docs/content/docs/ui/components/inline-toc.mdx
`````
---
title: Inline TOC
description: Add Inline TOC into your documentation
preview: inlineTOC
---

## Usage

Pass TOC items to the component.

```mdx
import { InlineTOC } from 'fumadocs-ui/components/inline-toc';

<InlineTOC items={toc} />
```

### Use in Pages

You can add inline TOC into every page.

```tsx
<DocsPage>
  ...
  <InlineTOC items={toc} />
  ...
</DocsPage>
```

## Reference

<AutoTypeTable path="./content/docs/ui/props.ts" name="InlineTOCProps" />
`````

## File: apps/docs/content/docs/ui/components/steps.mdx
`````
---
title: Steps
description: Adding steps to your docs
preview: steps
---

## Usage

Put your steps into the `Steps` container.

```mdx
import { Step, Steps } from 'fumadocs-ui/components/steps';

<Steps>
<Step>

### Hello World

</Step>

<Step>

### Hello World

</Step>
</Steps>
```

> We recommend using Tailwind CSS utility classes directly on Tailwind CSS projects.

### Without imports

You can use the Tailwind CSS utilities without importing it.

```mdx
<div className="fd-steps">
  <div className="fd-step" />
</div>
```

It supports adding step styles to only headings with arbitrary variants.

```mdx
<div className='fd-steps [&_h3]:fd-step'>

### Hello World

</div>
```

<div className='fd-steps [&_h3]:fd-step'>

### Hello World

You no longer need to use the step component anymore.

</div>
`````

## File: apps/docs/content/docs/ui/components/tabs.mdx
`````
---
title: Tabs
description:
  A Tabs component built with Radix UI, with additional features such as
  persistent and shared value.
preview: tabs
---

## Usage

Add MDX components.

```tsx title="mdx-components.tsx"
import defaultMdxComponents from 'fumadocs-ui/mdx';
import * as TabsComponents from 'fumadocs-ui/components/tabs';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    ...TabsComponents, // [!code ++]
    ...components,
  };
}
```

And use it like:

```mdx
<Tabs items={['Javascript', 'Rust']}>
  <Tab value="Javascript">Javascript is weird</Tab>
  <Tab value="Rust">Rust is fast</Tab>
</Tabs>
```

<Tabs items={['Javascript', 'Rust']}>
  <Tab value="Javascript">Javascript is weird</Tab>
  <Tab value="Rust">Rust is fast</Tab>
</Tabs>

### Without `value`

Without a `value`, it detects from the children index. Note that it might cause errors on re-renders, it's not encouraged if the tabs might change.

```mdx
import { Tab, Tabs } from 'fumadocs-ui/components/tabs';

<Tabs items={['Javascript', 'Rust']}>
  <Tab>Javascript is weird</Tab>
  <Tab>Rust is fast</Tab>
</Tabs>
```

<Tabs items={['Javascript', 'Rust']}>
  <Tab>Javascript is weird</Tab>
  <Tab>Rust is fast</Tab>
</Tabs>

### Shared Value

By passing an `groupId` property, you can share a value across all tabs with the same
id.

```mdx
<Tabs groupId="language" items={['Javascript', 'Rust']}>
  <Tab value="Javascript">Javascript is weird</Tab>
  <Tab value="Rust">Rust is fast</Tab>
</Tabs>
```

### Persistent

You can enable persistent by passing a `persist` property. The value will be
stored in `localStorage`, with its id as the key.

```mdx
<Tabs groupId="language" items={['Javascript', 'Rust']} persist>
  <Tab value="Javascript">Javascript is weird</Tab>
  <Tab value="Rust">Rust is fast</Tab>
</Tabs>
```

> Persistent only works if you have passed an `id`.

### Default Value

Set a default value by passing `defaultIndex`.

```mdx
<Tabs items={['Javascript', 'Rust']} defaultIndex={1}>
  <Tab value="Javascript">Javascript is weird</Tab>
  <Tab value="Rust">Rust is fast</Tab>
</Tabs>
```

### Link to Tab

Use HTML `id` attribute to link to a specific tab.

```mdx
<Tabs items={['Javascript', 'Rust', 'C++']}>
  <Tab value="Javascript">Javascript is weird</Tab>
  <Tab value="Rust">Rust is fast</Tab>
  <Tab id="tab-cpp" value="C++">
    `Hello World`
  </Tab>
</Tabs>
```

You can add the hash `#tab-cpp` to your URL and reload, the C++ tab will be activated.

<Tabs items={['Javascript', 'Rust', 'C++']}>
  <Tab value="Javascript">Javascript is weird</Tab>
  <Tab value="Rust">Rust is fast</Tab>
  <Tab id="tab-cpp" value="C++">
    `Hello World`
  </Tab>
</Tabs>

Additionally, the `updateAnchor` property can be set to `true` in the `Tabs` component
to automatically update the URL hash whenever time a new tab is selected:

```mdx
<Tabs items={['Javascript', 'Rust', 'C++']} updateAnchor>
  <Tab id="tab-js" value="Javascript">
    Javascript is weird
  </Tab>
  <Tab id="tab-rs" value="Rust">
    Rust is fast
  </Tab>
  <Tab id="tab-cpp" value="C++">
    `Hello World`
  </Tab>
</Tabs>
```

<UrlBar />

<Tabs items={['Hello', 'World']} updateAnchor>
  <Tab id="tab-hello" value="Hello">
    Hello!
  </Tab>
  <Tab id="tab-world" value="World">
    World!
  </Tab>
</Tabs>

## Advanced Usage

Use it in the Radix UI primitive way, see [Radix UI](https://radix-ui.com/primitives/docs/components/tabs) for more details.

```mdx
<Tabs defaultValue="npm">
  <TabsList>
    <TabsTrigger value="npm">
      <NpmIcon />
      npm
    </TabsTrigger>
  </TabsList>
  <TabsContent value="npm">Hello World</TabsContent>
</Tabs>
```

<Tabs defaultValue="npm">
  <TabsList>
    <TabsTrigger value="npm">
      <svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <title>npm</title>
        <path
          fill="currentColor"
          d="M1.763 0C.786 0 0 .786 0 1.763v20.474C0 23.214.786 24 1.763 24h20.474c.977 0 1.763-.786 1.763-1.763V1.763C24 .786 23.214 0 22.237 0zM5.13 5.323l13.837.019-.009 13.836h-3.464l.01-10.382h-3.456L12.04 19.17H5.113z"
        />
      </svg>
      npm
    </TabsTrigger>
  </TabsList>
  <TabsContent value="npm">Hello World</TabsContent>
</Tabs>
`````

## File: apps/docs/content/docs/ui/components/type-table.mdx
`````
---
title: Type Table
description: A table for documenting types
preview: typeTable
---

## Usage

It accepts a `type` property.

```mdx
import { TypeTable } from 'fumadocs-ui/components/type-table';

<TypeTable
  type={{
    percentage: {
      description:
        'The percentage of scroll position to display the roll button',
      type: 'number',
      default: 0.2,
    },
  }}
/>
```

## References

### Type Table

<AutoTypeTable path="./content/docs/ui/props.ts" name="TypeTableProps" />

### Object Type

<AutoTypeTable path="./content/docs/ui/props.ts" name="ObjectTypeProps" />
`````

## File: apps/docs/content/docs/ui/layouts/docs.mdx
`````
---
title: Docs Layout
description: The layout of documentation
---

The layout of documentation pages, it includes a sidebar and mobile-only navbar.

> It is a server component, you should not reference it in a client component.

## Usage

Pass your page tree to the component.

```tsx title="layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { baseOptions } from '@/app/layout.config';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout {...baseOptions} tree={tree}>
      {children}
    </DocsLayout>
  );
}
```

<AutoTypeTable
  path="./content/docs/ui/props.ts"
  type="Omit<DocsLayoutProps, 'children' | 'disableThemeSwitch'>"
/>

## Sidebar

```tsx title="layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/docs';

<DocsLayout
  sidebar={{
    enabled: true,
    // replace the default sidebar
    // component:
  }}
/>;
```

> See [Sidebar Links](/docs/ui/navigation/sidebar) for customising sidebar items.

<AutoTypeTable path="./content/docs/ui/props.ts" name="SidebarProps" />

## Nav

A mobile-only navbar, we recommend to customise it from `baseOptions`.

<div className='max-w-[460px] mx-auto'>

![Docs Nav](/docs/docs-nav.png)

</div>

```tsx
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  githubUrl: 'https://github.com/fuma-nama/fumadocs',
  nav: {
    title: 'My App',
  },
};
```

<AutoTypeTable
  path="./content/docs/ui/props.ts"
  type="Omit<NavbarProps, 'children'>"
/>

### Transparent Mode

To make the navbar background transparent, you can configure transparent mode.

```tsx
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  nav: {
    transparentMode: 'top',
  },
};
```

| Mode     | Description                              |
| -------- | ---------------------------------------- |
| `always` | Always use a transparent background      |
| `top`    | When at the top of page                  |
| `none`   | Disable transparent background (default) |

### Replace Navbar

To replace the navbar in Docs Layout, set `nav.component` to your own component.

```tsx title="layout.tsx"
import { baseOptions } from '@/app/layout.config';
import { DocsLayout } from 'fumadocs-ui/layouts/notebook';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      {...baseOptions}
      nav={{
        component: <CustomNavbar />,
      }}
    >
      {children}
    </DocsLayout>
  );
}
```

Fumadocs uses **CSS Variables** to share the size of layout components, and fit each layout component into appropriate position.

You need to override `--fd-nav-height` to the exact height of your custom navbar, this can be done with a CSS stylesheet (e.g. in `global.css`):

```css
:root {
  --fd-nav-height: 80px !important;
}
```

## Advanced

### Disable Prefetching

By default, it uses the Next.js Link component with prefetch enabled.
When the link component appears into the browser viewport, the content (RSC payload) will be prefetched.

On Vercel, this may cause a high usage of serverless functions and Data Cache.
It can also hit the limits of some other hosting platforms.

You can disable prefetching to reduce the amount of RSC requests.

```tsx
import { DocsLayout } from 'fumadocs-ui/layouts/docs';

<DocsLayout sidebar={{ prefetch: false }} />;
```
`````

## File: apps/docs/content/docs/ui/layouts/home-layout.mdx
`````
---
title: Home Layout
description: Shared layout for other pages
---

## Usage

Add a navbar and search dialog across other pages.

```tsx title="/app/(home)/layout.tsx"
import { HomeLayout } from 'fumadocs-ui/layouts/home';
import { baseOptions } from '@/app/layout.config';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return <HomeLayout {...baseOptions}>{children}</HomeLayout>;
}
```

Create a [Route Group](https://nextjs.org/docs/app/building-your-application/routing/route-groups) to share the same layout across multiple pages.

<Files>
  <Folder name="(home)" defaultOpen>
    <File name="page.tsx" />
    <File name="layout.tsx" />
  </Folder>
  <Folder name="/docs">
    <Folder name={'[[..slugs]]'}>
      <File name="page.tsx" />
    </Folder>
    <File name="layout.tsx" />
  </Folder>
</Files>

We recommend to customise it from [`baseOptions`](/docs/ui/navigation/links).
`````

## File: apps/docs/content/docs/ui/layouts/notebook.mdx
`````
---
title: Notebook
description: A more compact version of Docs Layout
---

![Notebook](/docs/notebook.png)

## Usage

Enable the notebook layout with `fumadocs-ui/layouts/notebook`, it's a more compact layout than the default one.

```tsx title="layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/notebook'; // [!code highlight]
import { baseOptions } from '@/app/layout.config';
import { source } from '@/lib/source';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout {...baseOptions} tree={source.pageTree}>
      {children}
    </DocsLayout>
  );
}
```

## Configurations

The options are inherited from [Docs Layout](/docs/ui/layouts/docs), with minor differences:

- sidebar/navbar cannot be replaced, Notebook layout is more opinionated than the default one.
- additional options (see below).

### Tab Mode

Configure the style of sidebar tabs.

![Notebook](/docs/notebook-tab-mode.png)

```tsx title="layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/notebook';
import { baseOptions } from '@/app/layout.config';
import { source } from '@/lib/source';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      {...baseOptions}
      tabMode="navbar" // [!code ++]
      tree={source.pageTree}
    >
      {children}
    </DocsLayout>
  );
}
```

### Nav Mode

Configure the style of navbar.

![Notebook](/docs/notebook-nav-mode.png)

```tsx title="layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/notebook';
import { baseOptions } from '@/app/layout.config';
import { source } from '@/lib/source';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      {...baseOptions}
      nav={{ ...baseOptions.nav, mode: 'top' }} // [!code ++]
      tree={source.pageTree}
    >
      {children}
    </DocsLayout>
  );
}
```
`````

## File: apps/docs/content/docs/ui/layouts/page.mdx
`````
---
title: Docs Page
description: A page in your documentation
---

Page is the base element of a documentation, it includes Table of contents,
Footer, and Breadcrumb.

## Usage

```tsx title="page.tsx"
import {
  DocsPage,
  DocsDescription,
  DocsTitle,
  DocsBody,
} from 'fumadocs-ui/page';

<DocsPage>
  <DocsTitle>title</DocsTitle>
  <DocsDescription>description</DocsDescription>
  <DocsBody>
    <h2>This heading looks good!</h2>
    It applies the Typography styles, wrap your content here.
  </DocsBody>
</DocsPage>;
```

<Callout type='info' title='Good to know'>

Instead of rendering the title with `DocsTitle` in `page.tsx`, you can put the title into MDX file.
This will render the title in the MDX body.

</Callout>

### Edit on GitHub

You can also add your own component.

```tsx
import { DocsBody } from 'fumadocs-ui/page';

<DocsBody>
  <a
    href={`https://github.com/fuma-nama/fumadocs/blob/main/content/docs/${page.path}`}
    rel="noreferrer noopener"
    target="_blank"
    className="w-fit border rounded-xl p-2 font-medium text-sm text-fd-secondary-foreground bg-fd-secondary transition-colors hover:text-fd-accent-foreground hover:bg-fd-accent"
  >
    Edit on GitHub
  </a>
</DocsBody>;
```

## Configurations

### Full Mode

To extend the page to fill up all available space, pass `full` to the page component.
This will force TOC to be shown as a popover.

```tsx
import { DocsPage } from 'fumadocs-ui/page';

<DocsPage full>...</DocsPage>;
```

### Table of Contents

An overview of all the headings in your article, it requires an array of headings.

For Markdown and MDX documents, You can obtain it using the
[TOC Utility](/docs/headless/utils/get-toc). Content sources like Fumadocs MDX offer this out-of-the-box.

```tsx
import { DocsPage } from 'fumadocs-ui/page';

<DocsPage toc={headings}>...</DocsPage>;
```

You can customise or disable it with the `tableOfContent` option, or with `tableOfContentPopover` on smaller devices.

```tsx
import { DocsPage } from 'fumadocs-ui/page';

<DocsPage tableOfContent={options} tableOfContentPopover={options}>
  ...
</DocsPage>;
```

<AutoTypeTable path="./content/docs/ui/props.ts" name="TOCProps" />

#### Style

You can choose another style for TOC, like `clerk` inspired by https://clerk.com:

```tsx
import { DocsPage } from 'fumadocs-ui/page';

<DocsPage
  tableOfContent={{
    style: 'clerk',
  }}
>
  ...
</DocsPage>;
```

### Last Updated Time

Display last updated time of the page.

```tsx
import { DocsPage } from 'fumadocs-ui/page';

<DocsPage lastUpdate={new Date(lastModifiedTime)} />;
```

Since you might use different version controls (e.g. Github) or CMS like Sanity, Fumadocs UI doesn't display the last updated time by
default.

<Tabs items={['Fumadocs MDX', 'GitHub API']}>

    <Tab>

You can enable [`lastModifiedTime`](/docs/mdx/last-modified).

```tsx
import { DocsPage } from 'fumadocs-ui/page';
import { source } from '@/lib/source';
const page = source.getPage(['...']);

<DocsPage lastUpdate={new Date(page.data.lastModified)} />;
```

    </Tab>

    <Tab>

For Github hosted documents, you can use
the [`getGithubLastEdit`](/docs/headless/utils/git-last-edit) utility.

```tsx
import { DocsPage } from 'fumadocs-ui/page';
import { getGithubLastEdit } from 'fumadocs-core/server';

const time = await getGithubLastEdit({
  owner: 'fuma-nama',
  repo: 'fumadocs',
  path: `content/docs/${page.path}`,
});

<DocsPage lastUpdate={new Date(time)} />;
```

    </Tab>

</Tabs>

### Footer

Footer is a navigation element that has two buttons to jump to the next and previous pages. When not specified, it shows the neighbour pages found from page tree.

Customise the footer with the `footer` option.

```tsx
import { DocsPage, DocsBody } from 'fumadocs-ui/page';

<DocsPage footer={options}>
  <DocsBody>...</DocsBody>
</DocsPage>;
```

<AutoTypeTable path="./content/docs/ui/props.ts" name="FooterProps" />

### Breadcrumb

A navigation element, shown only when user is navigating in folders.

<AutoTypeTable path="./content/docs/ui/props.ts" name="BreadcrumbProps" />
`````

## File: apps/docs/content/docs/ui/layouts/root-provider.mdx
`````
---
title: Root Provider
description: The context provider of Fumadocs UI.
---

The context provider of all the components, including `next-themes` and context
for search dialog. It should be located at the root layout.

## Usage

```jsx
import { RootProvider } from 'fumadocs-ui/provider';

export default function Layout({ children }) {
  return (
    <html lang="en">
      <body>
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}
```

### Search Dialog

Customize or disable the search dialog with `search` option.

```jsx
<RootProvider
  search={{
    enabled: false,
  }}
>
  {children}
</RootProvider>
```

Learn more from [Search](/docs/ui/search).

### Theme Provider

Fumadocs supports light/dark modes with [`next-themes`](https://github.com/pacocoursey/next-themes).
Customise or disable it with `theme` option.

```jsx
<RootProvider
  theme={{
    enabled: false,
  }}
>
  {children}
</RootProvider>
```
`````

## File: apps/docs/content/docs/ui/markdown/index.mdx
`````
---
title: Markdown
description: How to write documents
---

## Introduction

Fumadocs provides many useful extensions to MDX, a markup language. Here is a brief introduction to the default MDX syntax of Fumadocs.

> MDX is not the only supported format of Fumadocs. In fact, you can use any renderers such as `next-mdx-remote` or CMS.

## MDX

We recommend MDX, a superset of Markdown with JSX syntax.
It allows you to import components, and use them in the document, or even writing JavaScript.

See:

- [MDX Syntax](https://mdxjs.com/docs/what-is-mdx/#mdx-syntax).
- GFM (GitHub Flavored Markdown) is also supported, see [GFM Specification](https://github.github.com/gfm).

```mdx
---
title: This is a document
---

import { Component } from './component';

<Component name="Hello" />

# Heading

## Heading

### Heading

#### Heading

Hello World, **Bold**, _Italic_, ~~Hidden~~

1. First
2. Second
3. Third

- Item 1
- Item 2

> Quote here

![alt](/image.png)

| Table | Description |
| ----- | ----------- |
| Hello | World       |
```

Images are automatically optimized for `next/image`.

### Auto Links

Internal links use the `next/link` component to allow prefetching and avoid hard-reload.

External links will get the default `rel="noreferrer noopener" target="_blank"` attributes for security.

```mdx
[My Link](https://github.github.com/gfm)

This also works: https://github.github.com/gfm.
```

### Cards

Useful for adding links.

```mdx
import { HomeIcon } from 'lucide-react';

<Cards>
  <Card
    href="https://nextjs.org/docs/app/building-your-application/data-fetching/fetching-caching-and-revalidating"
    title="Fetching, Caching, and Revalidating"
  >
    Learn more about caching in Next.js
  </Card>
  <Card title="href is optional">Learn more about `fetch` in Next.js.</Card>
  <Card icon={<HomeIcon />} href="/" title="Home">
    You can include icons too.
  </Card>
</Cards>
```

<Cards>
  <Card
    href="https://nextjs.org/docs/app/building-your-application/data-fetching/fetching-caching-and-revalidating"
    title="Fetching, Caching, and Revalidating"
  >
    Learn more about caching in Next.js
  </Card>
  <Card title="href is optional">Learn more about `fetch` in Next.js.</Card>
  <Card icon={<HomeIcon />} href="/" title="Home">
    You can include icons too.
  </Card>
</Cards>

#### "Further Reading" Section

You can do something like:

```tsx title="page.tsx"
import { getPageTreePeers } from 'fumadocs-core/server';
import { source } from '@/lib/source';

<Cards>
  {getPageTreePeers(source.pageTree, '/docs/my-page').map((peer) => (
    <Card key={peer.url} title={peer.name} href={peer.url}>
      {peer.description}
    </Card>
  ))}
</Cards>;
```

This will show the other pages in the same folder as cards.

<DocsCategory url="/docs/ui/navigation" />

### Callouts

Useful for adding tips/warnings, it is included by default. You can specify the type of callout:

- `info` (default)
- `warn`/`warning`
- `error`
- `success`

```mdx
<Callout>Hello World</Callout>

<Callout title="Title">Hello World</Callout>

<Callout title="Title" type="error">
  Hello World
</Callout>
```

<Callout>Hello World</Callout>

<Callout title="Title" type="warn">
  Hello World
</Callout>

<Callout title="Title" type="error">
  Hello World
</Callout>

### Headings

An anchor is automatically applied to each heading, it sanitizes invalid characters like spaces. (e.g. `Hello World` to `hello-world`)

```md
# Hello `World`
```

#### TOC Settings

The table of contents (TOC) will be generated based on headings, you can also customise the effects of headings:

```md
# Heading [!toc]

This heading will be hidden from TOC.

# Another Heading [toc]

This heading will **only** be visible in TOC, you can use it to add additional TOC items.
Like headings rendered in a React component:

<MyComp />
```

#### Custom Anchor

You can add `[#slug]` to customise heading anchors.

```md
# heading [#my-heading-id]
```

You can also chain it with TOC settings like:

```md
# heading [toc] [#my-heading-id]
```

To link people to a specific heading, add the heading id to hash fragment: `/page#my-heading-id`.

### Codeblock

Syntax Highlighting is supported by default using [Rehype Code](/docs/headless/mdx/rehype-code).

````mdx
```js
console.log('Hello World');
```

```js title="My Title"
console.log('Hello World');
```
````

#### Line Numbers

Show line numbers, it also works with Twoslash and other transformers.

````mdx tab="Input"
```ts twoslash lineNumbers
const a = 'Hello World';
//    ^?
console.log(a); // [!code highlight]
```
````

```ts twoslash lineNumbers tab="Output"
const a = 'Hello World';
//    ^?
console.log(a); // [!code highlight]
```

You can set the initial value of line numbers.

````mdx tab="Input"
```js lineNumbers=4
function main() {
  console.log('starts from 4');

  return 0;
}
```
````

```js lineNumbers=4 tab="Output"
function main() {
  console.log('starts from 4');

  return 0;
}
```

#### Shiki Transformers

We support some of the [Shiki Transformers](https://shiki.style/packages/transformers), allowing you to highlight/style specific lines.

````md tab="Input"
```tsx
// highlight a line
<div>Hello World</div> // [\!code highlight]

// highlight a word
// [\!code word:Fumadocs]
<div>Fumadocs</div>

// diff styles
console.log('hewwo'); // [\!code --]
console.log('hello'); // [\!code ++]

// focus
return new ResizeObserver(() => {}) // [\!code focus]
```
````

```tsx tab="Output"
// highlight a line
<div>Hello World</div> // [!code highlight]

// highlight a word
// [!code word:Fumadocs]
<div>Fumadocs</div>

// diff styles:
console.log('hewwo'); // [!code --]
console.log('hello'); // [!code ++]

// focus
return new ResizeObserver(() => {}) // [!code focus]
```

#### Tab Groups

Make sure to add MDX components first:

```tsx title="mdx-components.tsx"
import defaultMdxComponents from 'fumadocs-ui/mdx';
import * as TabsComponents from 'fumadocs-ui/components/tabs';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    ...TabsComponents, // [!code ++]
    ...components,
  };
}
```

````mdx
```ts tab="Tab 1"
console.log('A');
```

```ts tab="Tab 2"
console.log('B');
```
````

```ts tab="Tab 1"
console.log('A');
```

```ts tab="Tab 2"
console.log('B');
```

### Include

> This is only available on **Fumadocs MDX**.

Reference another file (can also be a Markdown/MDX document).
Specify the target file path in `<include>` tag (relative to the MDX file itself).

```mdx title="page.mdx"
<include>./another.mdx</include>
```

See [other usages](/docs/mdx/include).

## Additional Features

You may be interested:

<DocsCategory />

### Package Install

Generate commands for installing packages via package managers.

````md tab="Input"
```package-install
npm i next -D
```
````

```package-install tab="Output"
npm i next -D
```

To enable, see [Remark Install](/docs/headless/mdx/install).

### Tab Groups with MDX

You can use MDX inside tab values too, enable it the remark plugin:

```ts tab="Fumadocs MDX" title="source.config.ts"
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    remarkCodeTabOptions: {
      parseMdx: true, // [!code ++]
    },
  },
});
```

```ts tab="MDX Compiler"
import { compile } from '@mdx-js/mdx';
import { remarkCodeTab } from 'fumadocs-core/mdx-plugins';

await compile('...', {
  remarkPlugins: [
    [
      remarkCodeTab,
      {
        parseMdx: true, // [!code ++]
      },
    ],
  ],
});
```

````mdx
```ts tab="<Building /> Tab 1"
console.log('A');
```

```ts tab="<Rocket /> Tab 2"
console.log('B');
```
````

```ts tab="<Building /> Tab 1"
console.log('A');
```

```ts tab="<Rocket /> Tab 2"
console.log('B');
```
`````

## File: apps/docs/content/docs/ui/markdown/math.mdx
`````
---
title: Math
description: Writing math equations in Markdown/MDX.
---

## Getting Started

```package-install
remark-math rehype-katex katex
```

### Add Plugins

Add the required remark/rehype plugins, the code might be vary depending on your content source.

```ts title="source.config.ts" tab="Fumadocs MDX"
import rehypeKatex from 'rehype-katex';
import remarkMath from 'remark-math';
import { defineConfig } from 'fumadocs-mdx/config';

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkMath],
    // Place it at first, it should be executed before the syntax highlighter
    rehypePlugins: (v) => [rehypeKatex, ...v],
  },
});
```

### Add Stylesheet

Add the following to root layout to make it looks great:

```tsx title="layout.tsx"
import 'katex/dist/katex.css';
```

### Done

Type some TeX expression in your documents, like the Pythagoras theorem:

````mdx
Inline: $$c = \pm\sqrt{a^2 + b^2}$$

```math
c = \pm\sqrt{a^2 + b^2}
```
````

Inline: $$c = \pm\sqrt{a^2 + b^2}$$

```math
c = \pm\sqrt{a^2 + b^2}
```

Taylor Expansion (expressing holomorphic function $$f(x)$$ in power series):

```math
\displaystyle {\begin{aligned}T_{f}(z)&=\sum _{k=0}^{\infty }{\frac {(z-c)^{k}}{2\pi i}}\int _{\gamma }{\frac {f(w)}{(w-c)^{k+1}}}\,dw\\&={\frac {1}{2\pi i}}\int _{\gamma }{\frac {f(w)}{w-c}}\sum _{k=0}^{\infty }\left({\frac {z-c}{w-c}}\right)^{k}\,dw\\&={\frac {1}{2\pi i}}\int _{\gamma }{\frac {f(w)}{w-c}}\left({\frac {1}{1-{\frac {z-c}{w-c}}}}\right)\,dw\\&={\frac {1}{2\pi i}}\int _{\gamma }{\frac {f(w)}{w-z}}\,dw=f(z),\end{aligned}}
```

<Callout title="Tip">

    You can actually copy equations on Wikipedia, they will be converted into a KaTeX string when you paste it.

```math
\displaystyle S[{\boldsymbol {q}}]=\int _{a}^{b}L(t,{\boldsymbol {q}}(t),{\dot {\boldsymbol {q}}}(t))\,dt.
```

</Callout>
`````

## File: apps/docs/content/docs/ui/markdown/mermaid.mdx
`````
---
title: Mermaid
description: Rendering diagrams in your docs
---

Fumadocs doesn't have a built-in Mermaid wrapper provided, we recommend using `mermaid` directly.

## Setup

Install the required dependencies, `next-themes` is used with Fumadocs to manage the light/dark mode.

```package-install
mermaid next-themes
```

Create the Mermaid component:

<include cwd meta='title="components/mdx/mermaid.tsx"'>
  ./components/mdx/mermaid.tsx
</include>

> This is originally inspired by [remark-mermaid](https://github.com/the-guild-org/docs/blob/main/packages/remark-mermaid/src/mermaid.tsx).

Add the component as a MDX component:

```tsx title="mdx-components.tsx"
import defaultMdxComponents from 'fumadocs-ui/mdx';
import { Mermaid } from '@/components/mdx/mermaid';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    Mermaid,
    ...components,
  };
}
```

## Usage

Use it in MDX files.

```mdx
<Mermaid
  chart="
graph TD;
subgraph AA [Consumers]
A[Mobile app];
B[Web app];
C[Node.js client];
end
subgraph BB [Services]
E[REST API];
F[GraphQL API];
G[SOAP API];
end
Z[GraphQL API];
A --> Z;
B --> Z;
C --> Z;
Z --> E;
Z --> F;
Z --> G;"
/>
```

<Tabs items={['Diagram', 'User Journey']}>

    <Tab>
    <Mermaid
        chart="

graph TD;
subgraph AA [Consumers]
A[Mobile app];
B[Web app];
C[Node.js client];
end
subgraph BB [Services]
E[REST API];
F[GraphQL API];
G[SOAP API];
end
Z[GraphQL API];
A --> Z;
B --> Z;
C --> Z;
Z --> E;
Z --> F;
Z --> G;"
/>

</Tab>

    <Tab>
        <Mermaid
            chart="

journey
title My working day
section Go to work
Make tea: 5: Me
Go upstairs: 3: Me
Do work: 1: Me, Cat
section Go home
Go downstairs: 5: Me
Sit down: 5: Me
"
/>

    </Tab>

</Tabs>
`````

## File: apps/docs/content/docs/ui/markdown/twoslash.mdx
`````
---
title: Twoslash
description: Use Typescript Twoslash in your docs
---

## Usage

Thanks to the Twoslash integration of [Shiki](https://github.com/shikijs/shiki), the default code syntax highlighter, it is as simple as adding a transformer.

```package-install
fumadocs-twoslash twoslash
```

Update your `serverExternalPackages` in Next.js config:

```js
import { createMDX } from 'fumadocs-mdx/next';

const config = {
  reactStrictMode: true,
  serverExternalPackages: ['typescript', 'twoslash'],
};

const withMDX = createMDX();

export default withMDX(config);
```

Add to your Shiki transformers.

```ts twoslash title="source.config.ts (Fumadocs MDX)"
import { defineConfig } from 'fumadocs-mdx/config';
import { transformerTwoslash } from 'fumadocs-twoslash';
import { rehypeCodeDefaultOptions } from 'fumadocs-core/mdx-plugins';

export default defineConfig({
  mdxOptions: {
    rehypeCodeOptions: {
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
      transformers: [
        ...(rehypeCodeDefaultOptions.transformers ?? []),
        transformerTwoslash(),
      ],
    },
  },
});
```

Add styles, Tailwind CSS v4 is required.

```css title="Tailwind CSS"
@import 'fumadocs-twoslash/twoslash.css';
```

Add MDX components.

```tsx title="mdx-components.tsx"
import * as Twoslash from 'fumadocs-twoslash/ui';
import defaultComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    ...Twoslash,
    ...components,
  };
}
```

Now you can add `twoslash` meta string to codeblocks.

````md
```ts twoslash
console.log('Hello World');
```
````

### Example

Learn more about [Twoslash notations](https://twoslash.netlify.app/refs/notations).

```ts twoslash title="Test" lineNumbers
type Player = {
  /**
   * The player name
   * @default 'user'
   */
  name: string;
};

// ---cut---
// @noErrors
console.g;
//       ^|

const player: Player = { name: 'Hello World' };
//    ^?
```

```ts twoslash
const a = '123';

console.log(a);
//      ^^^
```

```ts twoslash
import { generateFiles } from 'fumadocs-openapi';

void generateFiles({
  input: ['./museum.yaml'],
  output: './content/docs/ui',
});
```

```ts twoslash
// @errors: 2588
const a = '123';

a = 132;
```

## Cache

You can enable filesystem cache with `typesCache` option:

```ts twoslash title="source.config.ts"
import { transformerTwoslash } from 'fumadocs-twoslash';
import { createFileSystemTypesCache } from 'fumadocs-twoslash/cache-fs';

transformerTwoslash({
  typesCache: createFileSystemTypesCache(),
});
```
`````

## File: apps/docs/content/docs/ui/mdx/codeblock.mdx
`````
---
title: Code Block
description: Displaying Shiki highlighted code blocks
---

<Wrapper>
<div className="bg-fd-background rounded-lg prose-no-margin">

```js title="config.js"
import createMDX from 'fumadocs-mdx/config';

const withMDX = createMDX();

// [!code word:config]
/** @type {import('next').NextConfig} */
const config = {
  // [!code highlight]
  reactStrictMode: true, // [!code highlight]
}; // [!code highlight]

export default withMDX(config);
```

</div>
</Wrapper>

This is a MDX component to be used with [Rehype Code](/docs/headless/mdx/rehype-code) to display highlighted codeblocks.

Supported features:

- Copy button
- Custom titles and icons

> If you're looking for an equivalent with runtime syntax highlighting, see [Dynamic Code Block](/docs/ui/components/dynamic-codeblock).

## Usage

Wrap the pre element in `<CodeBlock />`, which acts as the wrapper of code block.

```tsx title="mdx-components.tsx"
import defaultComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';
import { CodeBlock, Pre } from 'fumadocs-ui/components/codeblock';

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultComponents,
    // HTML `ref` attribute conflicts with `forwardRef`
    pre: ({ ref: _ref, ...props }) => (
      <CodeBlock {...props}>
        <Pre>{props.children}</Pre> {/* [!code highlight] */}
      </CodeBlock>
    ),
    ...components,
  };
}
```

See [Markdown](/docs/ui/markdown#codeblock) for usages.

### Keep Background

Use the background color generated by Shiki.

```tsx
import { Pre, CodeBlock } from 'fumadocs-ui/components/codeblock';

<CodeBlock keepBackground {...props}>
  <Pre>{props.children}</Pre>
</CodeBlock>;
```

### Icons

Specify a custom icon by passing an `icon` prop to `CodeBlock` component.

By default, the icon will be injected by the custom Shiki transformer.

```js title="config.js"
console.log('js');
```
`````

## File: apps/docs/content/docs/ui/mdx/index.mdx
`````
---
title: MDX
description: Default MDX Components
---

## Usage

The default MDX components include Cards, Callouts, Code Blocks and Headings.

```ts
import defaultMdxComponents from 'fumadocs-ui/mdx';
```

### Relative Link

To support links with relative file path in `href`, override the default `a` component with:

```tsx title="app/docs/[[...slug]]/page.tsx"
import { createRelativeLink } from 'fumadocs-ui/mdx';
import { source } from '@/lib/source';
import { getMDXComponents } from '@/mdx-components';

const page = source.getPage(['...']);

return (
  <MdxContent
    components={getMDXComponents({
      // override the `a` tag
      a: createRelativeLink(source, page),
    })}
  />
);
```

```mdx
[My Link](./file.mdx)
```

[Example: `../(integrations)/open-graph.mdx`](<../(integrations)/open-graph.mdx>)

<Callout type="warn">Server Component only.</Callout>
`````

## File: apps/docs/content/docs/ui/navigation/index.mdx
`````
---
title: Navigation
description: Configure navigation in your Fumadocs app.
index: true
---
`````

## File: apps/docs/content/docs/ui/navigation/links.mdx
`````
---
title: Layout Links
description: Customise the shared navigation links on all layouts.
---

## Overview

Fumadocs allows adding additional links to your layouts with a `links` prop, like linking to your "showcase" page.

<div className="not-prose grid gap-2 *:border max-sm:*:last:hidden sm:grid-cols-[2fr_1fr]">

<>![Nav](/docs/nav-layout-home.png)</>

<>![Nav](/docs/nav-layout-docs.png)</>

</div>

```tsx tab="Shared Options" title="app/layout.config.tsx"
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  links: [], // [!code highlight]
  // other options
};
```

```tsx tab="Docs Layout" title="app/docs/layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { baseOptions } from '@/app/layout.config';
import { source } from '@/lib/source';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      {...baseOptions}
      tree={source.pageTree}
      links={[]} // [!code highlight]
    >
      {children}
    </DocsLayout>
  );
}
```

```tsx tab="Home Layout" title="app/(home)/layout.tsx"
import { HomeLayout } from 'fumadocs-ui/layouts/home';
import { baseOptions } from '@/app/layout.config';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <HomeLayout
      {...baseOptions}
      links={[]} // [!code highlight]
    >
      {children}
    </HomeLayout>
  );
}
```

You can see all supported items below:

### Link Item

A link to navigate to a URL/href, can be external.

```tsx title="app/layout.config.tsx"
import { BookIcon } from 'lucide-react';
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  links: [
    {
      icon: <BookIcon />,
      text: 'Blog',
      url: '/blog',
      // secondary items will be displayed differently on navbar
      secondary: false,
    },
  ],
};
```

#### Active Mode

The conditions to be marked as active.

| Mode         | Description                                                 |
| ------------ | ----------------------------------------------------------- |
| `url`        | When browsing the specified url                             |
| `nested-url` | When browsing the url and its child pages like `/blog/post` |
| `none`       | Never be active                                             |

```tsx title="app/layout.config.tsx"
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  links: [
    {
      text: 'Blog',
      url: '/blog',
      active: 'nested-url',
    },
  ],
};
```

### Icon Item

Same as link item, but is shown as an icon button.
Icon items are secondary by default.

```tsx title="app/layout.config.tsx"
import { BookIcon } from 'lucide-react';
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  links: [
    {
      type: 'icon',
      label: 'Visit Blog', // `aria-label`
      icon: <BookIcon />,
      text: 'Blog',
      url: '/blog',
    },
  ],
};
```

### Custom Item

Display a custom component.

```tsx title="app/layout.config.tsx"
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  links: [
    {
      type: 'custom',
      children: <Button variant="primary">Login</Button>,
      secondary: true,
    },
  ],
};
```

### GitHub URL

There's also a shortcut for adding GitHub repository link item.

```tsx twoslash title="app/layout.config.tsx"
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  githubUrl: 'https://github.com',
};
```

### Normal Menu

A menu containing multiple link items.

```tsx title="app/layout.config.tsx"
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export const baseOptions: BaseLayoutProps = {
  links: [
    {
      type: 'menu',
      text: 'Guide',
      items: [
        {
          text: 'Getting Started',
          description: 'Learn to use Fumadocs',
          url: '/docs',
        },
      ],
    },
  ],
};
```

### Navigation Menu

In Home Layout, you can add navigation menu (fully animated) to the navbar.

![Nav](/docs/nav-layout-menu.png)

```tsx title="app/(home)/layout.tsx"
import { baseOptions } from '@/app/layout.config';
import type { ReactNode } from 'react';
import { HomeLayout } from 'fumadocs-ui/layouts/home';
import {
  NavbarMenu,
  NavbarMenuContent,
  NavbarMenuLink,
  NavbarMenuTrigger,
} from 'fumadocs-ui/layouts/home/navbar';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <HomeLayout
      {...baseOptions}
      links={[
        {
          type: 'custom',
          // only displayed on navbar, not mobile menu
          on: 'nav',
          children: (
            <NavbarMenu>
              <NavbarMenuTrigger>Documentation</NavbarMenuTrigger>
              <NavbarMenuContent>
                <NavbarMenuLink href="/docs">Hello World</NavbarMenuLink>
              </NavbarMenuContent>
            </NavbarMenu>
          ),
        },
        // other items
      ]}
    >
      {children}
    </HomeLayout>
  );
}
```
`````

## File: apps/docs/content/docs/ui/navigation/sidebar.mdx
`````
---
title: Sidebar Links
description: Customise sidebar navigation links on Docs Layout.
---

## Overview

<div className='flex justify-center items-center *:max-w-[200px] bg-gradient-to-br from-fd-primary/10 rounded-xl border'>

    ![Sidebar](/docs/sidebar.png)

</div>

Sidebar items are rendered from the page tree you passed to `<DocsLayout />`.

For `source.pageTree`, it generates the tree from your file structure, you can see [Routing](/docs/ui/page-conventions) for available patterns.

```tsx title="layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { source } from '@/lib/source';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={source.pageTree}
      // other props
    >
      {children}
    </DocsLayout>
  );
}
```

You may hardcode it too:

```tsx title="layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={{
        name: 'docs',
        children: [],
      }}
      // other props
    >
      {children}
    </DocsLayout>
  );
}
```

### Sidebar Tabs

Tabs are folders with tab-like behaviours, only the content of opened tab will be visible.

Fumadocs provide a dropdown component to switch between tabs, it will be hidden unless one of its items is active.

<div className='flex justify-center items-center *:max-w-[360px] bg-gradient-to-br from-fd-primary/10 rounded-xl border'>

    ![Sidebar Tabs](/docs/sidebar-tabs.png)

</div>

You can add items by marking folders as [Root Folders](/docs/ui/page-conventions#root-folder), create a `meta.json` file in the folder:

```json title="content/docs/my-folder/meta.json"
{
  "title": "Name of Folder",
  "description": "The description of root folder (optional)",
  "root": true
}
```

Or specify them explicitly:

```tsx title="/app/docs/layout.tsx"
import { DocsLayout } from 'fumadocs-ui/layouts/docs';

<DocsLayout
  sidebar={{
    tabs: [
      {
        title: 'Components',
        description: 'Hello World!',
        // active for `/docs/components` and sub routes like `/docs/components/button`
        url: '/docs/components',

        // optionally, you can specify a set of urls which activates the item
        // urls: new Set(['/docs/test', '/docs/components']),
      },
    ],
  }}
/>;
```

Set it to `false` to disable:

```tsx
import { DocsLayout } from 'fumadocs-ui/layouts/docs';

<DocsLayout sidebar={{ tabs: false }} />;
```

<Callout title="Want further customisations?">

You can specify a `banner` to the [Docs Layout](/docs/ui/layouts/docs) component.

```tsx
import { DocsLayout, type DocsLayoutProps } from 'fumadocs-ui/layouts/docs';
import type { ReactNode } from 'react';
import { baseOptions } from '@/app/layout.config';
import { source } from '@/lib/source';

const docsOptions: DocsLayoutProps = {
  ...baseOptions,
  tree: source.pageTree,
  sidebar: {
    banner: <div>Hello World</div>,
  },
};

export default function Layout({ children }: { children: ReactNode }) {
  return <DocsLayout {...docsOptions}>{children}</DocsLayout>;
}
```

</Callout>

#### Decoration

Change the icon/styles of tabs.

```tsx
import { DocsLayout } from 'fumadocs-ui/layouts/docs';

<DocsLayout
  sidebar={{
    tabs: {
      transform: (option, node) => ({
        ...option,
        icon: <MyIcon />,
      }),
    },
  }}
/>;
```
`````

## File: apps/docs/content/docs/ui/search/.shared.mdx
`````
### Replace Search Dialog

To use your own search dialog, make a client-side `<RootProvider />` wrapper, and replace the original root provider with it.

```tsx tab="provider.tsx"
'use client';
import { RootProvider } from 'fumadocs-ui/provider';
// your custom dialog [!code highlight]
import SearchDialog from '@/components/search';
import type { ReactNode } from 'react';

export function Provider({ children }: { children: ReactNode }) {
  return (
    <RootProvider
      search={{
        SearchDialog,
      }}
    >
      {children}
    </RootProvider>
  );
}
```

```tsx tab="app/layout.tsx"
import { Provider } from './provider';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        {/* [!code ++] */}
        <Provider>{children}</Provider>
      </body>
    </html>
  );
}
```
`````

## File: apps/docs/content/docs/ui/search/.tag-filter.mdx
`````
```tsx
'use client';

import {
  SearchDialog,
  SearchDialogContent,
  SearchDialogFooter,
  SearchDialogOverlay,
  type SharedProps,
  TagsList,
  TagsListItem,
} from 'fumadocs-ui/components/dialog/search';
import { useState } from 'react';
import { useDocsSearch } from 'fumadocs-core/search/client';

export default function CustomSearchDialog(props: SharedProps) {
  // [!code ++]
  const [tag, setTag] = useState<string | undefined>();
  const { search, setSearch, query } = useDocsSearch({
    tag, // [!code ++]
  });

  return (
    <SearchDialog>
      <SearchDialogOverlay />
      <SearchDialogContent>
        ...
        <SearchDialogFooter className="flex flex-row">
          {/* [!code ++:3] */}
          <TagsList tag={tag} onTagChange={setTag}>
            <TagsListItem value="my-value">My Value</TagsListItem>
          </TagsList>
        </SearchDialogFooter>
      </SearchDialogContent>
    </SearchDialog>
  );
}
```
`````

## File: apps/docs/content/docs/ui/search/algolia.mdx
`````
---
title: Algolia
description: Using Algolia with Fumadocs UI.
---

## Overview

For the setup guide, see [Integrate Algolia Search](/docs/headless/search/algolia).

While generally we recommend building your own search with their client-side
SDK, you can also plug the built-in dialog interface.

## Setup

Create a search dialog, replace `appId`, `apiKey` and `indexName` with your desired values.

<include meta='title="components/search.tsx"'>./algolia.tsx</include>

<Callout title="Note" className='mt-4'>

    `useDocsSearch()` doesn't use instant search (their official
    Javascript client).

</Callout>

<include>.shared.mdx</include>

### Tag Filter

Optionally, you can add UI for filtering results by tags. Configure [Tag Filter](/docs/headless/search/algolia#tag-filter) on search server and add the following:

<include>.tag-filter.mdx</include>
`````

## File: apps/docs/content/docs/ui/search/index.mdx
`````
---
title: Search
description: Implement document search in your docs
---

## Search UI

You can customise some configurations from root provider.

For example, to disable search UI:

```tsx title="app/layout.tsx"
import { RootProvider } from 'fumadocs-ui/provider';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>
        <RootProvider
          search={{
            enabled: false, // [!code ++]
          }}
        >
          {children}
        </RootProvider>
      </body>
    </html>
  );
}
```

For further customisations, you can see [Search Client](#search-client).

### Hot Keys

Customise the hot keys to trigger search dialog, by default it's <kbd>⌘</kbd> <kbd>K</kbd> or <kbd>Ctrl</kbd> <kbd>K</kbd>.

```tsx
import { RootProvider } from 'fumadocs-ui/provider';

<RootProvider
  search={{
    hotKey: [
      {
        display: 'K',
        key: 'k', // key code, or a function determining whether the key is pressed
      },
    ],
  }}
>
  {children}
</RootProvider>;
```

## Search Client

You can choose & configure the search client according to your search engine, it defaults to Orama search.

<DocsCategory />

### Community Integrations

A list of integrations maintained by community.

- [Trieve Search](/docs/headless/search/trieve)
`````

## File: apps/docs/content/docs/ui/search/orama-cloud.mdx
`````
---
title: Orama Cloud
description: Using Orama Cloud with Fumadocs UI.
---

## Setup

For the setup guide, see [Integrate Orama Cloud](/docs/headless/search/orama-cloud).

Create a search dialog, replace `endpoint` and `api_key` with your desired values.

<include meta='title="components/search.tsx"'>orama-cloud.tsx</include>

<include>.shared.mdx</include>
`````

## File: apps/docs/content/docs/ui/search/orama.mdx
`````
---
title: Orama (default)
description: The default search engine powered by Orama.
---

## Overview

Fumadocs configures [Orama search engine](/docs/headless/search/orama) out-of-the-box.

It works through a API endpoint (route handler), or a statically cached file for Next.js apps using Static Export.

## Setup

Create a search dialog.

<Tabs items={['fetch (default)', 'static']}>

    <Tab>

The UI has been configured by default, you can also re-create it for further customisations:

<include meta='title="components/search.tsx"'>fetch.tsx</include>

    </Tab>

    <Tab id='static'>

For Static Export, you can configure [static mode](/docs/headless/search/orama#static-export) on search server, and use the `static` client:

```package-install
@orama/orama
```

<include meta='title="components/search.tsx"'>./static.tsx</include>

    </Tab>

</Tabs>

<include>.shared.mdx</include>

### Tag Filter

Optionally, you can add UI for filtering results by tags. Configure [Tag Filter](/docs/headless/search/orama#tag-filter) on search server and add the following:

<include>.tag-filter.mdx</include>
`````

## File: apps/docs/content/docs/ui/comparisons.mdx
`````
---
title: Comparisons
description: How is Fumadocs different from other existing frameworks?
icon: GitCompareArrows
---

## Nextra

Fumadocs is highly inspired by Nextra. For example, the Routing Conventions. That is why
`meta.json` also exists in Fumadocs.

Nextra is more opinionated than Fumadocs. Fumadocs is accelerated by App Router. As a result, It provides many server-side functions, and you have to
configure things manually compared to simply editing a configuration file.

Fumadocs works great if you want more control over everything, such as
adding it to an existing codebase or implementing advanced routing.

### Feature Table

| Feature             | Fumadocs     | Nextra                    |
| ------------------- | ------------ | ------------------------- |
| Static Generation   | Yes          | Yes                       |
| Cached              | Yes          | Yes                       |
| Light/Dark Mode     | Yes          | Yes                       |
| Syntax Highlighting | Yes          | Yes                       |
| Table of Contents   | Yes          | Yes                       |
| Full-text Search    | Yes          | Yes                       |
| i18n                | Yes          | Yes                       |
| Last Git Edit Time  | Yes          | Yes                       |
| Page Icons          | Yes          | Yes, via `_meta.js` files |
| RSC                 | Yes          | Yes                       |
| Remote Source       | Yes          | Yes                       |
| SEO                 | Via Metadata | Yes                       |
| Built-in Components | Yes          | Yes                       |
| RTL Layout          | Yes          | Yes                       |

### Additional Features

Features supported via 3rd party libraries like [TypeDoc](https://typedoc.org) will not be listed here.

| Feature                    | Fumadocs | Nextra |
| -------------------------- | -------- | ------ |
| OpenAPI Integration        | Yes      | No     |
| TypeScript Docs Generation | Yes      | No     |
| TypeScript Twoslash        | Yes      | Yes    |

## Mintlify

Mintlify is a documentation service, as compared to Fumadocs, it offers a free tier but isn't completely free and open source.

Fumadocs is not as powerful as Mintlify, for example, the OpenAPI integration of Mintlify.
As the creator of Fumadocs, I wouldn't recommend switching to Fumadocs from Mintlify if you're satisfied with the current way you build docs.
However, I believe Fumadocs is a suitable tool for all Next.js developers who want to have elegant docs.

## Docusaurus

Docusaurus is a powerful framework based on React.js. It offers many cool
features with plugins and custom themes.

### Better DX

Since Fumadocs is built on the top of Next.js, you'll have to start the Next.js dev
server every time to review changes, and initial boilerplate code is relatively more
compared to Docusaurus.

For a simple docs, Docusaurus might be a better choice if you don't need any Next.js specific functionality.

However, when you want to use Next.js, or seek extra customizability like tuning default UI components, Fumadocs could be a better choice.

### Plugins

You can easily achieve many things with plugins, their ecosystem is indeed larger and maintained by many contributors.

In comparison, the flexibility of Fumadocs allows you to implement them on your own, it may take longer to tune it to your satisfaction.
`````

## File: apps/docs/content/docs/ui/customisation.mdx
`````
---
title: Overview
description: An overview of Fumadocs UI
---

## Architecture

<UiOverview />

|               |                                                         |
| ------------- | ------------------------------------------------------- |
| **Sidebar**   | Display site title and navigation elements.             |
| **Page Tree** | Passed by you, mainly rendered as the items of sidebar. |
| **Docs Page** | All content of the page.                                |
| **TOC**       | Navigation within the article.                          |

## Customisation

### Layouts

You can use the exposed options of different layouts:

<Cards>
  <Card title="Docs Layout" href="/docs/ui/layouts/docs">
    Layout for docs
  </Card>
  <Card title="Docs Page" href="/docs/ui/layouts/page">
    Layout for docs content
  </Card>
  <Card title="Notebook Layout" href="/docs/ui/layouts/notebook">
    A more compact version of Docs Layout
  </Card>
  <Card title="Home Layout" href="/docs/ui/layouts/home-layout">
    Layout for other pages
  </Card>
</Cards>

### Components

Fumadocs UI also offers styled components for interactive examples to enhance your docs, you can customise them with exposed props like `style` and `className`.

See [Components](/docs/ui/components).

### Design System

Since the design system is built on Tailwind CSS, you can customise it [with CSS Variables](/docs/ui/theme#colors).

### CLI

Fumadocs CLI is a tool that installs components to your codebase, similar to Shadcn UI.

```package-install
npx @fumadocs/cli
```

Use it to install Fumadocs UI components:

```package-install
npx @fumadocs/cli add
```

Or customise layouts:

```package-install
npx @fumadocs/cli customise
```
`````

## File: apps/docs/content/docs/ui/index.mdx
`````
---
title: Quick Start
description: Getting Started with Fumadocs
icon: Album
---

## Introduction

Fumadocs <span className='text-fd-muted-foreground text-sm'>(Foo-ma docs)</span> is a **documentation framework** based on Next.js, designed to be fast, flexible,
and composes seamlessly into Next.js App Router.

Fumadocs has different parts:

<Cards>

<Card icon={<CpuIcon className="text-purple-300" />} title='Fumadocs Core'>

Handles most of the logic, including document search, content source adapters, and Markdown extensions.

</Card>

<Card icon={<PanelsTopLeft className="text-blue-300" />} title='Fumadocs UI'>

The default theme of Fumadocs offers a beautiful look for documentation sites and interactive components.

</Card>

<Card icon={<Database />} title='Content Source'>

The source of your content, can be a CMS or local data layers like [Fumadocs MDX](/docs/mdx) (the official content source).

</Card>

<Card icon={<Terminal />} title='Fumadocs CLI'>

A command line tool to install UI components and automate things, useful for customizing layouts.

</Card>

</Cards>

<Callout title="Want to learn more?">
  Read our in-depth [What is Fumadocs](/docs/ui/what-is-fumadocs) introduction.
</Callout>

### Terminology

**Markdown/MDX:** Markdown is a markup language for creating formatted text. Fumadocs supports Markdown and MDX (superset of Markdown) out-of-the-box.

Although not required, some basic knowledge of Next.js App Router would be useful for further customisations.

## Automatic Installation

A minimum version of Node.js 18 required, note that Node.js 23.1 might have problems with Next.js production build.

<Tabs groupId='package-manager' persist items={['npm', 'pnpm', 'yarn', 'bun']} label='Initialize Fumadocs'>

```bash tab="npm"
npm create fumadocs-app
```

```bash tab="pnpm"
pnpm create fumadocs-app
```

```bash tab="yarn"
yarn create fumadocs-app
```

```bash tab="bun"
bun create fumadocs-app
```

</Tabs>

It will ask you:

- the React.js framework to use (the docs is only written for Next.js).
- the content source to use.

A new fumadocs app should be initialized. Now you can start hacking!

<Callout title='From Existing Codebase?'>

    You can follow the [Manual Installation](/docs/ui/manual-installation) guide to get started.

</Callout>

### Enjoy!

Create your first MDX file in the docs folder.

```mdx title="content/docs/index.mdx"
---
title: Hello World
---

## Yo what's up
```

Run the app in development mode and see http://localhost:3000/docs.

```package-install
npm run dev
```

## FAQ

Some common questions you may encounter.

<Accordions>
    <Accordion id='change-base-url' title="How to change the base route of /docs?">

You can change the base route of docs (e.g. from `/docs/page` to `/info/page`).
Since Fumadocs uses Next.js App Router, you can simply rename the route:

<Files>
  <Folder name="app/docs" defaultOpen className="opacity-50" disabled>
    <File name="layout.tsx" />
  </Folder>
  <Folder name="app/info" defaultOpen>
    <File name="layout.tsx" />
  </Folder>
</Files>

And tell Fumadocs to use the new route in `source.ts`:

```ts title="lib/source.ts"
import { loader } from 'fumadocs-core/source';

export const source = loader({
  baseUrl: '/info',
  // other options
});
```

    </Accordion>
    <Accordion id='dynamic-route' title="It uses Dynamic Route, will it be poor in performance?">

Next.js turns dynamic route into static routes when `generateStaticParams` is configured.
Hence, it is as fast as static pages.

You can enable Static Exports on Next.js to get a static build output. (Notice that Route Handler doesn't work with static export, you have to configure static search)

    </Accordion>
    <Accordion id='custom-layout-docs-page' title='How to create a page in /docs without docs layout?'>

Same as managing layouts in Next.js App Router, remove the original MDX file from content directory (`/content/docs`).
This ensures duplicated pages will not cause errors.

Now, You can add the page to another route group, which isn't a descendant of docs layout.

For example, to replace `/docs/test`:

<Files>
  <File name="(home)/docs/test/page.tsx" />
  <Folder name="docs">
    <File name="layout.tsx" />
    <File name="[[...slug]]/page.tsx" />
  </Folder>
</Files>

For `/docs`, you need to change the catch-all route to be non-optional:

<Files>
  <File name="(home)/docs/page.tsx" />
  <Folder name="docs" defaultOpen>
    <File name="layout.tsx" />
    <File name="[...slug]/page.tsx" />
  </Folder>
</Files>

    </Accordion>

    <Accordion id='multi-docs' title="How to implement multi-docs?">
        We recommend to use [Sidebar Tabs](/docs/ui/navigation/sidebar#sidebar-tabs).
    </Accordion>

</Accordions>

## Learn More

New to here? Don't worry, we are welcome for your questions.

If you find anything confusing, please give your feedback on [Github Discussion](https://github.com/fuma-nama/fumadocs/discussions)!

### Writing Content

For authoring docs, make sure to read:

<Cards>
  <Card href="/docs/ui/markdown" title="Markdown">
    Fumadocs has some additional features for authoring content.
  </Card>
  <Card href="/docs/ui/navigation" title="Navigation">
    Learn how to customise navigation links and sidebar items.
  </Card>
  <Card href="/docs/ui/page-conventions" title="Routing">
    Learn how to organise content.
  </Card>
  <Card
    href="/docs/ui/components"
    title="Components"
    description="See all available components to enhance your docs"
  />
</Cards>

### Special Needs

<Cards>
  <Card
    href="/docs/ui/static-export"
    title="Configure Static Export"
    description="Learn how to enable static export on your docs"
  />
  <Card
    href="/docs/ui/internationalization"
    title="Internationalization"
    description="Learn how to enable i18n"
  />
  <Card
    href="/docs/ui/theme"
    title="Color Themes"
    description="Add themes to Fumadocs UI"
  />
  <Card
    href="/docs/ui/customisation"
    title="Customise UI"
    description="A detailed guide on how to customise UI"
  />
</Cards>
`````

## File: apps/docs/content/docs/ui/internationalization.mdx
`````
---
title: Internationalization
description: Support multiple languages in your documentation
---

## Overview

For Next.js apps, you'll have to configure i18n routing on both Next.js and Fumadocs.

Fumadocs is not a full-powered i18n library, it's up to you when implementing i18n for Next.js part.
You can also use other libraries with Fumadocs like [next-intl](https://github.com/amannn/next-intl).

[Learn more about i18n in Next.js](https://nextjs.org/docs/app/building-your-application/routing/internationalization).

## Setup

Define the i18n configurations in a file, we will import it with `@/ilb/i18n` in this guide.

<include cwd meta='title="lib/i18n.ts"'>
  ../../examples/i18n/lib/i18n.ts
</include>

> See [customisable options](/docs/headless/internationalization).

Pass it to the source loader.

```ts title="lib/source.ts"
import { i18n } from '@/lib/i18n';
import { loader } from 'fumadocs-core/source';

export const source = loader({
  i18n, // [!code ++]
  // other options
});
```

### Middleware

Create a middleware that redirects users to appropriate locale.

<include cwd meta='title="middleware.ts"'>
  ../../examples/i18n/middleware.ts
</include>

<Callout title="Custom Middleware">

    The default middleware is optional, you can instead use your own middleware or the one provided by i18n libraries.

    When using custom middleware, make sure the locale is correctly passed to Fumadocs.
    You may also want to [customise page URLs](/docs/headless/source-api#url) from `loader()`.

</Callout>

### Routing

Create a `/app/[lang]` folder, and move all files (e.g. `page.tsx`, `layout.tsx`) from `/app` to the folder.

Provide UI translations and other config to `<RootProvider />`.
Note that only English translations are provided by default.

```tsx title="app/[lang]/layout.tsx"
import { RootProvider } from 'fumadocs-ui/provider';
import type { Translations } from 'fumadocs-ui/i18n';

// translations
const cn: Partial<Translations> = {
  search: 'Translated Content',
};

// available languages that will be displayed on UI
// make sure `locale` is consistent with your i18n config
const locales = [
  {
    name: 'English',
    locale: 'en',
  },
  {
    name: 'Chinese',
    locale: 'cn',
  },
];

export default async function RootLayout({
  params,
  children,
}: {
  params: Promise<{ lang: string }>;
  children: React.ReactNode;
}) {
  const lang = (await params).lang;

  return (
    <html lang={lang}>
      <body>
        <RootProvider
          i18n={{
            locale: lang, // [!code ++]
            locales, // [!code ++]
            translations: { cn }[lang], // [!code ++]
          }}
        >
          {children}
        </RootProvider>
      </body>
    </html>
  );
}
```

### Pass Locale

Pass the locale to Fumadocs in your pages and layouts.

```tsx title="app/layout.config.tsx" tab="Shared Options"
import { i18n } from '@/lib/i18n';
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

// Make `baseOptions` a function: [!code highlight]
export function baseOptions(locale: string): BaseLayoutProps {
  return {
    i18n, // [!code ++]
    // different props based on `locale`
  };
}
```

```tsx title="/app/[lang]/(home)/layout.tsx" tab="Home Layout"
import type { ReactNode } from 'react';
import { HomeLayout } from 'fumadocs-ui/layouts/home';
import { baseOptions } from '@/app/layout.config';

export default async function Layout({
  params,
  children,
}: {
  params: Promise<{ lang: string }>;
  children: ReactNode;
}) {
  const { lang } = await params;

  return <HomeLayout {...baseOptions(lang)}>{children}</HomeLayout>; // [!code highlight]
}
```

```tsx title="/app/[lang]/docs/layout.tsx" tab="Docs Layout"
import type { ReactNode } from 'react';
import { source } from '@/lib/source';
import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import { baseOptions } from '@/app/layout.config';

export default async function Layout({
  params,
  children,
}: {
  params: Promise<{ lang: string }>;
  children: ReactNode;
}) {
  const { lang } = await params;

  return (
    // [!code highlight]
    <DocsLayout {...baseOptions(lang)} tree={source.pageTree[lang]}>
      {children}
    </DocsLayout>
  );
}
```

```ts title="page.tsx" tab="Docs Page"
import { source } from '@/lib/source';

export default async function Page({
  params,
}: {
  params: Promise<{ lang: string; slug?: string[] }>;
}) {
  const { slug, lang } = await params;
  // get page
  source.getPage(slug); // [!code --]
  source.getPage(slug, lang); // [!code ++]

  // get pages
  source.getPages(); // [!code --]
  source.getPages(lang); // [!code ++]
}
```

<Callout title={<>Using another name for <code>lang</code> dynamic segment?</>}>

If you're using another name like `app/[locale]`, you also need to update `generateStaticParams()` in docs page:

```tsx
export function generateStaticParams() {
  return source.generateParams(); // [!code --]
  return source.generateParams('slug', 'locale'); // [!code ++] new param name
}
```

</Callout>

### Search

Configure i18n on your search solution.

- **Built-in Search (Orama):**
  For [Supported Languages](https://docs.orama.com/open-source/supported-languages#officially-supported-languages), no further changes are needed.

  Otherwise, additional config is required (e.g. Chinese & Japanese). See [Special Languages](/docs/headless/search/orama#special-languages).

- **Cloud Solutions (e.g. Algolia):**
  They usually have official support for multilingual.

## Writing Documents

<include>../../shared/page-conventions.i18n.mdx</include>

## Navigation

Fumadocs only handles navigation for its own layouts (e.g. sidebar).
For other places, you can use the `useParams` hook to get the locale from url, and attend it to `href`.

```tsx
import Link from 'next/link';
import { useParams } from 'next/navigation';

const { lang } = useParams();

return <Link href={`/${lang}/another-page`}>This is a link</Link>;
```

In addition, the [`fumadocs-core/dynamic-link`](/docs/headless/components/link#dynamic-hrefs) component supports dynamic hrefs, you can use it to attend the locale prefix.
It is useful for Markdown/MDX content.

```mdx title="content.mdx"
import { DynamicLink } from 'fumadocs-core/dynamic-link';

<DynamicLink href="/[lang]/another-page">This is a link</DynamicLink>
```
`````

## File: apps/docs/content/docs/ui/manual-installation.mdx
`````
---
title: Manual Installation
description: Add Fumadocs to existing projects.
---

Before continuing, make sure:

- Next.js 15 and Tailwind CSS 4 are configured.

## Getting Started

```package-install
fumadocs-ui fumadocs-core
```

### MDX Components

<include cwd meta='title="mdx-components.tsx"'>
  ../../examples/next-mdx/mdx-components.tsx
</include>

### Content Source

Fumadocs supports different content sources, including Fumadocs MDX and [Content Collections](/docs/headless/content-collections).

Fumadocs MDX is our official content source, you can configure it with:

```package-install
fumadocs-mdx @types/mdx
```

```js tab="next.config.mjs"
import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
};

export default withMDX(config);
```

```ts tab="source.config.ts"
import { defineDocs } from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: 'content/docs',
});
```

```json tab="package.json"
{
  "scripts": {
    "postinstall": "fumadocs-mdx" // [!code ++]
  }
}
```

Finally, to access your content:

```ts title="lib/source.ts"
// .source folder will be generated when you run `next dev`
import { docs } from '@/.source';
import { loader } from 'fumadocs-core/source';

export const source = loader({
  baseUrl: '/docs',
  source: docs.toFumadocsSource(),
});
```

### Root Layout

Wrap the entire application inside [Root Provider](/docs/ui/layouts/root-provider), and add required styles to `body`.

```tsx title="app/layout.tsx"
import { RootProvider } from 'fumadocs-ui/provider';
import type { ReactNode } from 'react';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        // you can use Tailwind CSS too
        style={{
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
        }}
      >
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}
```

### Styles

Add the following Tailwind CSS styles to `global.css`.

```css title="global.css"
@import 'tailwindcss';
@import 'fumadocs-ui/css/neutral.css';
@import 'fumadocs-ui/css/preset.css';
```

> It doesn't come with a default font, you may choose one from `next/font`.

### Layout

Create a `app/layout.config.tsx` file to put the shared options for our layouts.

<include cwd meta='title="app/layout.config.tsx"'>
  ../../examples/next-mdx/app/layout.config.tsx
</include>

Create a folder `/app/docs` for our docs, and give it a proper layout.

<include cwd meta='title="app/docs/layout.tsx"'>
  ../../examples/next-mdx/app/docs/layout.tsx
</include>

> `pageTree` refers to Page Tree, it should be provided by your content source.

### Page

Create a catch-all route `/app/docs/[[...slug]]` for docs pages.

In the page, wrap your content in the [Page](/docs/ui/layouts/page) component.

<Tabs groupId='content-source' items={['Fumadocs MDX', 'Content Collections']}>

    <include cwd meta='title="app/docs/[[...slug]]/page.tsx" tab="Fumadocs MDX"'>../../examples/next-mdx/app/docs/[[...slug]]/page.tsx</include>

    <include cwd meta='title="app/docs/[[...slug]]/page.tsx" tab="Content Collections"'>../../examples/content-collections/app/docs/[[...slug]]/page.tsx</include>

</Tabs>

### Search

Use the default document search based on Orama.

<include cwd meta='title="app/api/search/route.ts"'>
  ../../examples/next-mdx/app/api/search/route.ts
</include>

Learn more about [Document Search](/docs/headless/search).

### Done

You can start the dev server and create MDX files.

```mdx title="content/docs/index.mdx"
---
title: Hello World
---

## Introduction

I love Anime.
```

## Deploying

It should work out-of-the-box with Vercel & Netlify.

### Cloudflare

Use https://opennext.js.org/cloudflare, Fumadocs doesn't work on Edge runtime.

### Docker Deployment

If you want to deploy your Fumadocs app using Docker with **Fumadocs MDX configured**, make sure to add the `source.config.ts` file to the `WORKDIR` in the Dockerfile.
The following snippet is taken from the official [Next.js Dockerfile Example](https://github.com/vercel/next.js/blob/canary/examples/with-docker/Dockerfile):

```zsh title="Dockerfile"
# syntax=docker.io/docker/dockerfile:1

FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
# Check https://github.com/nodejs/docker-node/tree/b4117f9333da4138b03a546ec926ef50a31506c3#nodealpine to understand why libc6-compat might be needed.
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager [!code highlight]
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* .npmrc* source.config.ts ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi


# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Next.js collects completely anonymous telemetry data about general usage.
# Learn more here: https://nextjs.org/telemetry
# Uncomment the following line in case you want to disable telemetry during the build.
# ENV NEXT_TELEMETRY_DISABLED=1

RUN \
  if [ -f yarn.lock ]; then yarn run build; \
  elif [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm run build; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
# Uncomment the following line in case you want to disable telemetry during runtime.
# ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000

# server.js is created by next build from the standalone output
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output
ENV HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
```

This ensures Fumadocs MDX can access your configuration file during builds.
`````

## File: apps/docs/content/docs/ui/page-conventions.mdx
`````
---
title: Routing
description: A shared convention for organizing your documents
---

<include>../headless/page-conventions.mdx</include>
`````

## File: apps/docs/content/docs/ui/static-export.mdx
`````
---
title: Static Export
description: Enable static export with Fumadocs
---

## Overview

Fumadocs is fully compatible with Next.js static export, allowing you to export the app as a static HTML site without a Node.js server.

```js title="next.config.mjs"
/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  output: 'export',

  // Optional: Change links `/me` -> `/me/` and emit `/me.html` -> `/me/index.html`
  // trailingSlash: true,

  // Optional: Prevent automatic `/me` -> `/me/`, instead preserve `href`
  // skipTrailingSlashRedirect: true,
};
```

See [Next.js docs](https://nextjs.org/docs/app/guides/static-exports) for limitations and details.

## Search

### Cloud Solutions

Since the search functionality is powered by remote servers, static export works without configuration.

### Built-in Search

Learn how to [enable static mode](/docs/ui/search/orama#static) on search client.

This enables the route handler to be statically cached into a single file, and search will be computed on browser instead.
`````

## File: apps/docs/content/docs/ui/theme.mdx
`````
---
title: Themes
description: Add Theme to Fumadocs UI
---

## Usage

Only Tailwind CSS v4 is supported, the preset will also include source to Fumadocs UI itself:

```css title="Tailwind CSS"
@import 'tailwindcss';
@import 'fumadocs-ui/css/neutral.css';
@import 'fumadocs-ui/css/preset.css';
```

### Preflight Changes

By using the Tailwind CSS plugin, or the pre-built stylesheet, your default border, text and background
colors will be changed.

### Light/Dark Modes

Fumadocs supports light/dark modes with [`next-themes`](https://github.com/pacocoursey/next-themes), it is included in Root Provider.

See [Root Provider](/docs/ui/layouts/root-provider#theme-provider) to learn more.

### RTL Layout

RTL (Right-to-left) layout is supported.

To enable RTL, set the `dir` prop to `rtl` in body and root provider (required for Radix UI).

```tsx
import { RootProvider } from 'fumadocs-ui/provider';
import type { ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body dir="rtl">
        <RootProvider dir="rtl">{children}</RootProvider>
      </body>
    </html>
  );
}
```

### Layout Width

Customise the max width of docs layout with CSS Variables.

```css
:root {
  --fd-layout-width: 1400px;
}
```

<WidthTrigger />

## Tailwind CSS Preset

Fumadocs UI adds its own colors, animations, and utilities with Tailwind CSS preset.

### Colors

It comes with many themes out-of-the-box, you can pick one you prefer.

```css
@import 'fumadocs-ui/css/<theme>.css';
@import 'fumadocs-ui/css/preset.css';
```

<Tabs items={['neutral', 'black', 'vitepress', 'dusk', 'catppuccin', 'ocean', 'purple']}>

    <Tab value='neutral'>

![Neutral](/themes/neutral.png)

    </Tab>

    <Tab value='black'>

![Black](/themes/black.png)

    </Tab>

    <Tab value='vitepress'>

![Vitepress](/themes/vitepress.png)

    </Tab>

    <Tab value='dusk'>

![Dusk](/themes/dusk.png)

    </Tab>

    <Tab value='Catppuccin'>

![Catppuccin](/themes/catppuccin.png)

    </Tab>

    <Tab value='ocean'>

![Ocean](/themes/ocean.png)

    </Tab>

    <Tab value='purple'>

![Purple](/themes/purple.png)

    </Tab>

</Tabs>

The design system was inspired by [Shadcn UI](https://ui.shadcn.com), you can also customize the colors using CSS variables.

```css title="global.css"
:root {
  --color-fd-background: hsl(0, 0%, 100%);
}

.dark {
  --color-fd-background: hsl(0, 0%, 0%);
}
```

For Shadcn UI, you can use the `shadcn` preset instead.
It uses colors from your Shadcn UI theme.

```css
@import 'tailwindcss';
@import 'fumadocs-ui/css/shadcn.css';
@import 'fumadocs-ui/css/preset.css';
```

### Typography

We have a built-in plugin forked from [Tailwind CSS Typography](https://tailwindcss.com/docs/typography-plugin).

The plugin adds a `prose` class and variants to customise it.

```tsx
<div className="prose">
  <h1>Good Heading</h1>
</div>
```

> The plugin works with and only with Fumadocs UI's MDX components, it may conflict with `@tailwindcss/typography`.
> If you need to use `@tailwindcss/typography` over the default plugin, [set a class name option](https://github.com/tailwindlabs/tailwindcss-typography/blob/main/README.md#changing-the-default-class-name) to avoid conflicts.
`````

## File: apps/docs/content/docs/ui/versioning.mdx
`````
---
title: Versioning
description: Implementing multi-version in your docs.
---

## Overview

It's common for developer tool related docs to version their docs, such as different docs for v1 and v2 of the same tool.

Fumadocs provide the primitives for you to implement versioning on your own way.

## Partial Versioning

When versioning only applies to part of your docs, You can separate them by folders.

For example:

<Files>
  <Folder name="java-sdk" defaultOpen>
    <Folder name="v1" defaultOpen>
      <File name="getting-started.mdx" />
    </Folder>
    <Folder name="v2" defaultOpen>
      <File name="getting-started.mdx" />
    </Folder>
  </Folder>
</Files>

<Callout title="Good to Know">
  You may want to group them with tabs rather than folders [using Sidebar
  Tabs](/docs/ui/navigation/sidebar#sidebar-tabs).
</Callout>

## Full Versioning

Sometimes you want to version the entire website, such as https://v14.fumadocs.dev (Fumadocs v14) and https://fumadocs.dev (Latest Fumadocs).

You can create a Git branch for a version of docs (call it `v2` for example), and deploy it as a separate app on another subdomain like `v2.my-site.com`.

Optionally, you can link to the other versions from your docs.
This design allows some advantages over partial versioning:

- Easy maintenance: Old docs/branches won't be affected when you iterate or upgrade dependencies.
- Better consistency: Not just the docs itself, your landing page (and other pages) will also be versioned.
`````

## File: apps/docs/content/docs/ui/what-is-fumadocs.mdx
`````
---
title: What is Fumadocs
description: Introducing Fumadocs, a docs framework that you can break.
icon: CircleHelp
---

Fumadocs was created because I wanted a more customisable experience for building docs, to be a docs framework that is not opinionated, **a "framework" that you can break**.

## Philosophy

**Less Abstraction:** Fumadocs expects you to write code and cooperate with the rest of your software.
While most frameworks are configured with a configuration file, they usually lack flexibility when you hope to tune its details.
You can’t control how they render the page nor the internal logic. Fumadocs shows you how the app works, instead of a single configuration file.

**Next.js Fundamentals:** It gives you the utilities and a good-looking UI.
You are still using features of Next.js App Router, like **Static Site Generation**. There is nothing new for Next.js developers, so you can use it with confidence.

**Opinionated on UI:** The only thing Fumadocs UI (the default theme) offers is **User Interface**. The UI is opinionated for bringing better mobile responsiveness and user experience.
Instead, we use a much more flexible approach inspired by Shadcn UI — [Fumadocs CLI](/docs/cli), so we can iterate our design quick, and welcome for more feedback about the UI.

## Why Fumadocs

Fumadocs is designed with flexibility in mind.

You can use `fumadocs-core` as a headless UI library and bring your own styles.
Fumadocs MDX is also a useful library to handle MDX content in Next.js. It also includes:

- Many built-in components.
- Typescript Twoslash, OpenAPI, and Math (KaTeX) integrations.
- Fast and optimized by default, natively built on App Router.
- Tight integration with Next.js, you can add it to an existing Next.js project easily.

You can read [Comparisons](/docs/ui/comparisons) if you're interested.

### Documentation

Fumadocs focuses on **authoring experience**, it provides a beautiful theme and many docs automation tools.

It helps you to iterate your codebase faster while never leaving your docs behind.
You can take this site as an example of docs site built with Fumadocs.

### Blog sites

Since Next.js is already a powerful framework, most features can be implemented with **just Next.js**.

Fumadocs provides additional tooling for Next.js, including syntax highlighting, document search, and a default theme (Fumadocs UI).
It helps you to avoid reinventing the wheels.

## When to use Fumadocs

For most of the web applications, vanilla React.js is no longer enough.
Nowadays, we also wish to have a blog, a showcase page, a FAQ page, etc. With a
fancy UI that's breathtaking, in these cases, Fumadocs can help you build the
docs easier, with less boilerplate.

Fumadocs is maintained by Fuma and many contributors, with care on the maintainability of codebase.
While we don't aim to offer every functionality people wanted, we're more focused on making basic features perfect and well-maintained.
You can also help Fumadocs to be more useful by contributing!
`````
