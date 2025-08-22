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
- Only files matching these patterns are included: docs/**/*.{md,markdown,mdx,rmd,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
docs/
  guidelines/
    plugin.md
    runner.md
  architecture.md
  plugins.md
  README-cn.md
  README.md
  source-maps.md
  syntax.md
  writing-a-plugin.md
```

# Files

## File: docs/guidelines/plugin.md
````markdown
# PostCSS Plugin Guidelines

A PostCSS plugin is a function that receives and, usually,
transforms a CSS AST from the PostCSS parser.

The rules below are *mandatory* for all PostCSS plugins.

See also [ClojureWerkz’s recommendations] for open source projects.

[ClojureWerkz’s recommendations]: http://blog.clojurewerkz.org/blog/2013/04/20/how-to-make-your-open-source-project-really-awesome/

**Table of Contents**

* [API](#1-api)
  * [1.1 Clear name with `postcss-` prefix](#11-clear-name-with-postcss--prefix)
  * [1.2. Do one thing, and do it well](#12-do-one-thing-and-do-it-well)
  * [1.3. Do not use mixins](#13-do-not-use-mixins)
  * [1.4. Keep `postcss` to `peerDependencies`](#14-keep-postcss-to-peerdependencies)
  * [1.5. Set `plugin.postcssPlugin` with plugin name](#15-set-pluginpostcssplugin-with-plugin-name)
* [Processing](#2-processing)
  * [2.1. Plugin must be tested](#21-plugin-must-be-tested)
  * [2.2. Use asynchronous methods whenever possible](#22-use-asynchronous-methods-whenever-possible)
  * [2.3. Use fast node’s scanning](#23-use-fast-nodes-scanning)
  * [2.4. Set `node.source` for new nodes](#24-set-nodesource-for-new-nodes)
  * [2.5. Use only the public PostCSS API](#25-use-only-the-public-postcss-api)
* [Dependencies](#3-dependencies)
  * [3.1. Use messages to specify dependencies](#31-use-messages-to-specify-dependencies)
* [Errors](#4-errors)
  * [4.1. Use `node.error` on CSS relevant errors](#41-use-nodeerror-on-css-relevant-errors)
  * [4.2. Use `result.warn` for warnings](#42-use-resultwarn-for-warnings)
*  [Documentation](#5-documentation)
  * [5.1. Document your plugin in English](#51-document-your-plugin-in-english)
  * [5.2. Include input and output examples](#52-include-input-and-output-examples)
  * [5.3. Maintain a changelog](#53-maintain-a-changelog)
  * [5.4. Include `postcss-plugin` keyword in `package.json`](#54-include-postcss-plugin-keyword-in-packagejson)

## 1. API

### 1.1 Clear name with `postcss-` prefix

The plugin’s purpose should be clear just by reading its name.
If you wrote a transpiler for CSS 4 Custom Media, `postcss-custom-media`
would be a good name. If you wrote a plugin to support mixins,
`postcss-mixins` would be a good name.

The prefix `postcss-` shows that the plugin is part of the PostCSS ecosystem.

This rule is not mandatory for plugins that can run as independent tools,
without the user necessarily knowing that it is powered by
PostCSS — for example, [RTLCSS] and [Autoprefixer].

[Autoprefixer]: https://github.com/postcss/autoprefixer
[RTLCSS]:       https://rtlcss.com/


### 1.2. Do one thing, and do it well

Do not create multitool plugins. Several small, one-purpose plugins bundled into
a plugin pack is usually a better solution.

For example, [`postcss-preset-env`] contains many small plugins,
one for each W3C specification. And [`cssnano`] contains a separate plugin
for each of its optimization.

[`postcss-preset-env`]: https://preset-env.cssdb.org/
[`cssnano`]:            https://github.com/cssnano/cssnano


### 1.3. Do not use mixins

Preprocessors libraries like Compass provide an API with mixins.

PostCSS plugins are different.
A plugin cannot be just a set of mixins for [`postcss-mixins`].

To achieve your goal, consider transforming valid CSS
or using custom at-rules and custom properties.

[`postcss-mixins`]: https://github.com/postcss/postcss-mixins


### 1.4. Keep `postcss` to `peerDependencies`

AST can be broken because of different `postcss` version in different plugins.
Different plugins could use a different node creators (like `postcss.decl()`).

```json
{
  "peerDependencies": {
    "postcss": "^8.0.0"
  }
}
```

It is better even not to import `postcss`.

```diff
- const { list, decl } = require('postcss')
  module.exports = opts => {
    postcssPlugin: 'postcss-name',
-   Once (root) {
+   Once (root, { list, decl }) {
      // Plugin code
    }
  }
  module.exports.postcss = true
```


### 1.5. Set `plugin.postcssPlugin` with plugin name

Plugin name will be used in error messages and warnings.

```js
module.exports = opts => {
  return {
    postcssPlugin: 'postcss-name',
    Once (root) {
      // Plugin code
    }
  }
}
module.exports.postcss = true
```


## 2. Processing

### 2.1. Plugin must be tested

A CI service like [Travis] is also recommended for testing code in
different environments. You should test in (at least) Node.js [active LTS](https://github.com/nodejs/LTS) and current stable version.

[Travis]: https://travis-ci.org/


### 2.2. Use asynchronous methods whenever possible

For example, use `fs.writeFile` instead of `fs.writeFileSync`:

```js
let { readFile } = require('fs').promises

module.exports = opts => {
  return {
    postcssPlugin: 'plugin-inline',
    async Decl (decl) {
      const imagePath = findImage(decl)
      if (imagePath) {
        let imageFile = await readFile(imagePath)
        decl.value = replaceUrl(decl.value, imageFile)
      }
    }
  }
}
module.exports.postcss = true
```

### 2.3. Use fast node’s scanning

Subscribing for specific node type is much faster, than calling `walk*` method:

```diff
  module.exports = {
    postcssPlugin: 'postcss-example',
-   Once (root) {
-     root.walkDecls(decl => {
-       // Slow
-     })
-   }
+   Declaration (decl) {
+     // Faster
+   }
  }
  module.exports.postcss = true
```

But you can make scanning even faster, if you know, what declaration’s property
or at-rule’s name do you need:

```diff
  module.exports = {
    postcssPlugin: 'postcss-example',
-   Declaration (decl) {
-     if (decl.prop === 'color') {
-       // Faster
-     }
-   }
+   Declaration: {
+     color: decl => {
+       // The fastest
+     }
+   }
  }
  module.exports.postcss = true
```


### 2.4. Set `node.source` for new nodes

Every node must have a relevant `source` so PostCSS can generate
an accurate source map.

So if you add a new declaration based on some existing declaration, you should
clone the existing declaration in order to save that original `source`.

```js
if (needPrefix(decl.prop)) {
  decl.cloneBefore({ prop: '-webkit-' + decl.prop })
}
```

You can also set `source` directly, copying from some existing node:

```js
if (decl.prop === 'animation') {
  const keyframe = createAnimationByName(decl.value)
  keyframes.source = decl.source
  decl.root().append(keyframes)
}
```


### 2.5. Use only the public PostCSS API

PostCSS plugins must not rely on undocumented properties or methods,
which may be subject to change in any minor release. The public API
is described in [API docs].

[API docs]: https://postcss.org/api/


## 3. Dependencies

### 3.1. Use messages to specify dependencies

If a plugin depends on another file, it should be specified by attaching
a `dependency` message to the `result`:

```js
result.messages.push({
  type: 'dependency',
  plugin: 'postcss-import',
  file: '/imported/file.css',
  parent: result.opts.from
})
```

Directory dependencies should be specified using the `dir-dependency` message
type. By default all files within the directory (recursively) are considered
dependencies. An optional `glob` property can be used to indicate that only
files matching a specific glob pattern should be considered.

```js
result.messages.push({
  type: 'dir-dependency',
  plugin: 'postcss-import',
  dir: '/imported',
  glob: '**/*.css', // optional
  parent: result.opts.from
})
```


## 4. Errors

### 4.1. Use `node.error` on CSS relevant errors

If you have an error because of input CSS (like an unknown name
in a mixin plugin) you should use `node.error` to create an error
that includes source position:

```js
if (typeof mixins[name] === 'undefined') {
  throw node.error('Unknown mixin ' + name)
}
```


### 4.2. Use `result.warn` for warnings

Do not print warnings with `console.log` or `console.warn`,
because some PostCSS runner may not allow console output.

```js
Declaration (decl, { result }) {
  if (outdated(decl.prop)) {
    result.warn(decl.prop + ' is outdated', { node: decl })
  }
}
```

If CSS input is a source of the warning, the plugin must set the `node` option.


## 5. Documentation

### 5.1. Document your plugin in English

PostCSS plugins must have their `README.md` wrote in English. Do not be afraid
of your English skills, as the open source community will fix your errors.

Of course, you are welcome to write documentation in other languages;
just name them appropriately (e.g. `README.ja.md`).


### 5.2. Include input and output examples

The plugin's `README.md` must contain example input and output CSS.
A clear example is the best way to describe how your plugin works.

The first section of the `README.md` is a good place to put examples.
See [postcss-opacity](https://github.com/iamvdo/postcss-opacity) for an example.

Of course, this guideline does not apply if your plugin does not
transform the CSS.


### 5.3. Maintain a changelog

PostCSS plugins must describe the changes of all their releases
in a separate file, such as `CHANGELOG.md`, `History.md`, or [GitHub Releases].
Visit [Keep A Changelog] for more information about how to write one of these.

Of course, you should be using [SemVer].

[Keep A Changelog]: https://keepachangelog.com/
[GitHub Releases]:  https://help.github.com/articles/creating-releases/
[SemVer]:           https://semver.org/


### 5.4. Include `postcss-plugin` keyword in `package.json`

PostCSS plugins written for npm must have the `postcss-plugin` keyword
in their `package.json`. This special keyword will be useful for feedback about
the PostCSS ecosystem.

For packages not published to npm, this is not mandatory, but is recommended
if the package format can contain keywords.
````

## File: docs/guidelines/runner.md
````markdown
# PostCSS Runner Guidelines

A PostCSS runner is a tool that processes CSS through a user-defined list
of plugins; for example, [`postcss-cli`] or [`gulp‑postcss`].
These rules are mandatory for any such runners.

For single-plugin tools, like [`gulp-autoprefixer`],
these rules are not mandatory but are highly recommended.

See also [ClojureWerkz’s recommendations] for open source projects.

[ClojureWerkz’s recommendations]: http://blog.clojurewerkz.org/blog/2013/04/20/how-to-make-your-open-source-project-really-awesome/
[`gulp-autoprefixer`]: https://github.com/sindresorhus/gulp-autoprefixer
[`gulp‑postcss`]:      https://github.com/w0rm/gulp-postcss
[`postcss-cli`]:       https://github.com/postcss/postcss-cli

**Table of Contents**

* [API](#1-api)
  * [1.1. Accept functions in plugin parameters](#11-accept-functions-in-plugin-parameters)
* [Processing](#21-set-from-and-to-processing-options)
  * [2.1. Set `from` and `to` processing options](#21-set-from-and-to-processing-options)
  * [2.2. Use only the asynchronous API](#22-use-only-the-asynchronous-api)
  * [2.3. Use only the public PostCSS API](#23-use-only-the-public-postcss-api)
  * [3.1. Rebuild when dependencies change](#31-rebuild-when-dependencies-change)
* [Output](#4-output)
  * [4.1. Don’t show JS stack for `CssSyntaxError`](#41-dont-show-js-stack-for-csssyntaxerror)
  * [4.2. Display `result.warnings()`](#42-display-resultwarnings)
  * [4.3. Allow the user to write source maps to different files](#43-allow-the-user-to-write-source-maps-to-different-files)
* [Documentation](#5-output)
  * [5.1. Document your runner in English](#51-document-your-runner-in-english)
  * [5.2. Maintain a changelog](#52-maintain-a-changelog)
  * [5.3. `postcss-runner` keyword in `package.json`](#53-postcss-runner-keyword-in-packagejson)
  * [5.4. Keep postcss to peerDependencies](#54-keep-postcss-to-peerdependencies)

## 1. API

### 1.1. Accept functions in plugin parameters

If your runner uses a config file, it must be written in JavaScript, so that
it can support plugins which accept a function, such as [`postcss-assets`]:

```js
module.exports = [
  require('postcss-assets')({
    cachebuster: function (file) {
      return fs.statSync(file).mtime.getTime().toString(16)
    }
  })
]
```

[`postcss-assets`]: https://github.com/borodean/postcss-assets


## 2. Processing

### 2.1. Set `from` and `to` processing options

To ensure that PostCSS generates source maps and displays better syntax errors,
runners must specify the `from` and `to` options. If your runner does not handle
writing to disk (for example, a gulp transform), you should set both options
to point to the same file:

```js
processor.process({ from: file.path, to: file.path })
```


### 2.2. Use only the asynchronous API

PostCSS runners must use only the asynchronous API.
The synchronous API is provided only for debugging, is slower,
and can’t work with asynchronous plugins.

```js
processor.process(opts).then(result => {
  // processing is finished
});
```


### 2.3. Use only the public PostCSS API

PostCSS runners must not rely on undocumented properties or methods,
which may be subject to change in any minor release. The public API
is described in [API docs].

[API docs]: https://postcss.org/api/


## 3. Dependencies

### 3.1. Rebuild when dependencies change

PostCSS plugins may declare file or directory dependencies by attaching
messages to the `result`. Runners should watch these and ensure that the
CSS is rebuilt when they change.

```js
for (let message of result.messages) {
  if (message.type === 'dependency') {
    watcher.addFile(message.file)
  } else if (message.type === 'dir-dependency' && message.glob) {
    watcher.addPattern(file.join(message.dir, message.glob))
  } else if (message.type === 'dir-dependency') {
    watcher.addPattern(file.join(message.dir, '**', '*'))
  }
}
```

Directories should be watched recursively by default, but `dir-dependency`
messages may contain an optional `glob` property indicating which files
within the directory are depended on (e.g. `**/*.css`). If `glob` is
specified then runners should only watch files matching the glob pattern,
where possible.


## 4. Output

### 4.1. Don’t show JS stack for `CssSyntaxError`

PostCSS runners must not show a stack trace for CSS syntax errors,
as the runner can be used by developers who are not familiar with JavaScript.
Instead, handle such errors gracefully:

```js
processor.process(opts).catch(error => {
  if (error.name === 'CssSyntaxError') {
    process.stderr.write(error.message + error.showSourceCode())
  } else {
    throw error
  }
})
```


### 4.2. Display `result.warnings()`

PostCSS runners must output warnings from `result.warnings()`:

```js
result.warnings().forEach(warn => {
  process.stderr.write(warn.toString())
})
```

See also [postcss-log-warnings] and [postcss-messages] plugins.

[postcss-log-warnings]: https://github.com/davidtheclark/postcss-log-warnings
[postcss-messages]:     https://github.com/postcss/postcss-messages


### 4.3. Allow the user to write source maps to different files

PostCSS by default will inline source maps in the generated file; however,
PostCSS runners must provide an option to save the source map in a different
file:

```js
if (result.map) {
  fs.writeFile(opts.to + '.map', result.map.toString())
}
```


## 5. Documentation

### 5.1. Document your runner in English

PostCSS runners must have their `README.md` written in English. Do not be afraid
of your English skills, as the open source community will fix your errors.

Of course, you are welcome to write documentation in other languages;
just name them appropriately (e.g. `README.ja.md`).


### 5.2. Maintain a changelog

PostCSS runners must describe changes of all releases in a separate file,
such as `ChangeLog.md`, `History.md`, or with [GitHub Releases].
Visit [Keep A Changelog] for more information on how to write one of these.

Of course, you should use [SemVer].

[Keep A Changelog]: https://keepachangelog.com/
[GitHub Releases]:  https://help.github.com/articles/creating-releases/
[SemVer]:           https://semver.org/


### 5.3. `postcss-runner` keyword in `package.json`

PostCSS runners written for npm must have the `postcss-runner` keyword
in their `package.json`. This special keyword will be useful for feedback about
the PostCSS ecosystem.

For packages not published to npm, this is not mandatory, but recommended
if the package format is allowed to contain keywords.


### 5.4. Keep `postcss` to `peerDependencies`

AST can be broken because of different `postcss` version in different plugins.
Different plugins could use a different node creators (like `postcss.decl()`).

```json
{
  "peerDependencies": {
    "postcss": "^8.0.0"
  }
}
```
````

## File: docs/architecture.md
````markdown
# PostCSS Architecture

General overview of the PostCSS architecture.
It can be useful for everyone who wishes to contribute to the core or develop a better understanding of the tool.

**Table of Contents**
  * [Overview](#overview)
  * [Workflow](#workflow)
  * [Core Structures](#core-structures)
  * [API Reference](#api-reference)


### Overview

> This section describes ideas lying behind PostCSS

Before diving deeper into the development of PostCSS let's briefly describe what is PostCSS and what is not.

**PostCSS**

- *is **NOT** a style preprocessor like `Sass` or `Less`.*

    It does not define a custom syntax and semantics, it's not actually a language.
    PostCSS works with CSS and can be easily integrated with the tools described above. That being said any valid CSS can be processed by PostCSS.

- *is a tool for CSS syntax transformations*

    It allows you to define custom CSS like syntax that could be understandable and transformed by plugins. That being said PostCSS is not strictly about CSS spec but about syntax definition manner of CSS. In such a way you can define custom syntax constructs like at-rule, that could be very helpful for tools build around PostCSS. PostCSS plays the role of a framework for building outstanding tools for CSS manipulations.

- *is a big player in CSS ecosystem*

    A Large amount of lovely tools like `Autoprefixer`, `Stylelint`, `CSSnano` were built on PostCSS ecosystem. There is a big chance that you already use it implicitly, just check your `node_modules` :smiley:


### Workflow

This is a high-level overview of the whole PostCSS workflow

<img width="300" src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/PostCSS_scheme.svg/512px-PostCSS_scheme.svg.png" alt="workflow">

As you can see from the diagram above, PostCSS architecture is pretty straightforward but some parts of it could be misunderstood.

You can see a part called *Parser*, this construct will be described in details later on, just for now think about it as a structure that can understand your CSS like syntax and create an object representation of it.

That being said, there are few ways to write a parser.

 - *Write a single file with string to AST transformation*

    This method is quite popular, for example, the [Rework analyzer](https://github.com/reworkcss/css/blob/master/lib/parse/index.js) was written in this style. But with a large code base, the code becomes hard to read and pretty slow.

 - *Split it into lexical analysis/parsing steps (source string → tokens → AST)*

    This is the way of how we do it in PostCSS and also the most popular one.
    A lot of parsers like [`@babel/parser` (parser behind Babel)](https://github.com/babel/babel/tree/master/packages/babel-parser), [`CSSTree`](https://github.com/csstree/csstree) were written in such way.
    The main reasons to separate tokenization from parsing steps are performance and abstracting complexity.

Let's think about why the second way is better for our needs.

First of all, because string to tokens step takes more time than parsing step. We operate on large source string and process it char by char, this is why it is very inefficient operation in terms of performance and we should perform it only once.

But from other side tokens to AST transformation is logically more complex so with such separation we could write very fast tokenizer (but from this comes sometimes hard to read code) and easy to read (but slow) parser.

Summing it up splitting into two steps improve performance and code readability.

So now let's look more closely on structures that play the main role in PostCSS workflow.


### Core Structures

 - #### Tokenizer [`lib/tokenize.js`](https://github.com/postcss/postcss/blob/main/lib/tokenize.js)

    Tokenizer (aka Lexer) plays important role in syntax analysis.

    It accepts CSS string and returns a list of tokens.

    Token is a simple structure that describes some part of syntax like `at-rule`, `comment` or `word`. It can also contain positional information for more descriptive errors.

    For example, if we consider following CSS

    ```css
    .className { color: #FFF; }
    ```

    corresponding tokens from PostCSS will be
    ```js
    [
        ["word", ".className", 1, 1, 1, 10]
        ["space", " "]
        ["{", "{", 1, 12]
        ["space", " "]
        ["word", "color", 1, 14, 1, 18]
        [":", ":", 1, 19]
        ["space", " "]
        ["word", "#FFF" , 1, 21, 1, 23]
        [";", ";", 1, 24]
        ["space", " "]
        ["}", "}", 1, 26]
    ]
    ```

    As you can see from the example above a single token represented as a list and also `space` token doesn't have positional information.

    Let's look more closely on single token like `word`. As it was said each token represented as a list and follow such pattern.

    ```js
    const token = [
         // represents token type
        'word',

        // represents matched word
        '.className',

        // This two numbers represent start position of token.
        // It is optional value as we saw in the example above,
        // tokens like `space` don't have such information.

        // Here the first number is line number and the second one is corresponding column.
        1, 1,

        // Next two numbers also optional and represent end position for multichar tokens like this one. Numbers follow same rule as was described above
        1, 10
    ]
    ```
   There are many patterns how tokenization could be done, PostCSS motto is performance and simplicity. Tokenization is a complex computing operation and takes a large amount of syntax analysis time ( ~90% ), that why PostCSS' Tokenizer looks dirty but it was optimized for speed. Any high-level constructs like classes could dramatically slow down tokenizer.

    PostCSS' Tokenizer uses some sort of streaming/chaining API where you expose [`nextToken()`](https://github.com/postcss/postcss/blob/main/lib/tokenize.js#L48-L308) method to Parser. In this manner, we provide a clean interface for Parser and reduce memory usage by storing only a few tokens and not the whole list of tokens.

- #### Parser [`lib/parse.js`](https://github.com/postcss/postcss/blob/main/lib/parse.js), [`lib/parser.js`](https://github.com/postcss/postcss/blob/main/lib/parser.js)

    Parser is the main structure responsible for [syntax analysis](https://en.wikipedia.org/wiki/Parsing) of incoming CSS. Parser produces a structure called [Abstract Syntax Tree (AST)](https://en.wikipedia.org/wiki/Abstract_syntax_tree) that could then be transformed by plugins later on.

    Parser works in common with Tokenizer and operates over tokens, not source string, as it would be a very inefficient operation.

    It uses mostly `nextToken` and `back` methods provided by Tokenizer for obtaining single or multiple tokens and then construct part of AST called `Node`.

    There are multiple Node types that PostCSS could produce but all of them inherit from base Node [class](https://github.com/postcss/postcss/blob/main/lib/node.js#L34).

- #### Processor [`lib/processor.js`](https://github.com/postcss/postcss/blob/main/lib/processor.js)

    Processor is a very plain structure that initializes plugins and runs syntax transformations

    It exposes only a few public API methods. Description of them could be found on [API](https://postcss.org/api/#processor)

- #### Stringifier [`lib/stringify.js`](https://github.com/postcss/postcss/blob/main/lib/stringify.js), [`lib/stringifier.js`](https://github.com/postcss/postcss/blob/main/lib/stringifier.js)

    Stringifier is a base class that translates modified AST to pure CSS string. Stringifier traverses AST starting from provided Node and generates a raw string representation of it calling corresponding methods.

    The most essential method is [`Stringifier.stringify`](https://github.com/postcss/postcss/blob/main/lib/stringifier.js#L25-L27)
    that accepts initial Node and semicolon indicator.
    You can learn more by checking [stringifier.js](https://github.com/postcss/postcss/blob/main/lib/stringifier.js)


### API Reference

More descriptive API documentation could be found [here](https://postcss.org/api/)
````

## File: docs/plugins.md
````markdown
# PostCSS Plugins

**Table of Contents**

* [Control](#control)
* [Packs](#packs)
* [Future CSS Syntax](#future-css-syntax)
* [Fallbacks](#fallbacks)
* [Language Extensions](#language-extensions)
* [Images and Fonts](#images-and-fonts)
* [Grids](#grids)
* [Optimizations](#optimizations)
* [Shortcuts](#shortcuts)
* [Others](#others)
* [Analysis](#analysis)
* [Reporters](#reporters)
* [Fun](#fun)

## Control

There are two ways to make PostCSS magic more explicit.

Limit a plugin's local stylesheet context using [`postcss-plugin-context`]:

```pcss
.css-example.is-test-for-css4-browsers {
  color: gray(255, 50%);
}
@context postcss-preset-env {
  .css-example.is-fallback-for-all-browsers {
    color: gray(255, 50%);
  }
}
```

Or enable plugins directly in CSS using [`postcss-use`]:

```pcss
@use autoprefixer(browsers: ['last 2 versions']);

:fullscreen a {
  display: flex;
}
```

[`postcss-plugin-context`]: https://github.com/postcss/postcss-plugin-context
[`postcss-use`]:            https://github.com/postcss/postcss-use


## Packs

* [`postcss-utilities`] includes the most commonly used mixins, shortcuts
  and helpers to use as `@util` rules.
* [`atcss`] contains plugins that transform your CSS according
  to special annotation comments.
* [`cssnano`] contains plugins that optimize CSS size for use in production.
* [`oldie`] contains plugins that transform your CSS
  for older Internet Explorer compatibility.
* [`rucksack`] contains plugins to speed up CSS development
  with new features and shortcuts.
* [`level4`] contains only plugins that let you write CSS4 without
  the IE9 fallbacks.
* [`short`] adds and extends numerous shorthand properties.
* [`stylelint`] contains plugins that lint your stylesheets.
* [`postcss-hamster`] for vertical rhythm, typography, modular scale functions.
* [`postcss-preset-env`] lets you convert modern CSS into something most
  browsers can understand, determining the polyfills you need based
  on your targeted browsers or runtime environments.
* [`postcss-ui-theme`] gives you syntax sugar and allows you to change theme.

[`postcss-preset-env`]: https://github.com/csstools/postcss-plugins/tree/main/plugin-packs/postcss-preset-env
[`postcss-utilities`]:  https://github.com/ismamz/postcss-utilities
[`postcss-hamster`]:    https://github.com/h0tc0d3/postcss-hamster
[`stylelint`]:          https://github.com/stylelint/stylelint
[`rucksack`]:           https://github.com/seaneking/rucksack
[`cssnano`]:            https://cssnano.github.io/cssnano/
[`level4`]:             https://github.com/stephenway/level4
[`oldie`]:              https://github.com/csstools/oldie
[`atcss`]:              https://github.com/morishitter/atcss
[`postcss-ui-theme`]:   https://github.com/cleverboy32/postcss-ui-theme


## Future CSS Syntax

* [`postcss-apply`] supports custom properties sets references.
* [`postcss-attribute-case-insensitive`] supports case insensitive attributes.
* [`postcss-bidirection`] generate left-to-right and right-to-left styles
  with single syntax.
* [`postcss-color-function`] supports functions to transform colors.
* [`postcss-color-gray`] supports the `gray()` function.
* [`postcss-color-hex-alpha`] supports `#rrggbbaa` and `#rgba` notation.
* [`postcss-color-hsl`]: transforms CSS Colors 4 `hsl()` to more compatible
  `hsl()` or `hsla()`.
* [`postcss-color-hwb`] transforms `hwb()` to widely compatible `rgb()`.
* [`postcss-color-image`] supports `image(<color>)` syntax
  allowing to use a solid color as an image.
* [`postcss-color-rebeccapurple`] supports the `rebeccapurple` color.
* [`postcss-color-rgb`]: transforms CSS Colors 4 `rgb()` to more compatible
  `rgb()` or `rgba()`.
* [`postcss-conic-gradient`] supports the `conic-gradient` background.
* [`postcss-custom-media`] supports custom aliases for media queries.
* [`postcss-custom-properties`] supports variables, using syntax from
  the W3C Custom Properties.
* [`postcss-custom-selectors`] adds custom aliases for selectors.
* [`postcss-extend`] supports spec-approximate `@extend` for rules
  and placeholders, recursively.
* [`postcss-font-format-keywords`] transforms keywords in `@font-face` rule’s
  `format()` function to widely supported strings.
* [`postcss-font-normalize`] to normalize font, especially `font-family`.
* [`postcss-font-variant`] transpiles human-readable `font-variant`
  to more widely supported CSS.
* [`postcss-font-family-system-ui`] transforms W3C CSS `font-family: system-ui`
  to a practical font list.
* [`postcss-font-display`] add `font-display` css rule.
* [`postcss-if-function`] transforms `if()` function for `media()` and
  `supports()` to `@media` and `@supports` queries.
* [`postcss-host`] makes the Shadow DOM’s `:host` selector work properly
  with pseudo-classes.
* [`postcss-initial`] supports `initial` keyword and `all: initial`
  to clean inherit styles.
* [`postcss-logical-properties`] transforms `start` and `end` properties
  to `left` and `right` depending on the writing direction of the document.
* [`postcss-media-minmax`] adds `<=` and `=>` statements to media queries.
* [`postcss-multi-value-display`] transforms `inline flex` and `block flow`
  to `inline-flex` and `block`
* [`postcss-pseudo-class-any-link`] adds `:any-link` pseudo-class.
* [`postcss-pseudo-is`] transforms `:is()` to more compatible CSS.
* [`postcss-selector-not`] transforms CSS4 `:not()` to CSS3 `:not()`.
* [`postcss-selector-matches`] transforms CSS4 `:matches()`
  to more compatible CSS.
* [`postcss-start-to-end`] lets you control your layout (LTR or RTL)
  through logical rather than direction / physical rules.
* [`postcss-subgrid`] provides a basic shim for the CSS `display: subgrid` spec.
* [`mq4-hover-shim`] supports the `@media (hover)` feature.

See also [`postcss-preset-env`] plugins pack to add future CSS syntax
by one line of code.


## Fallbacks

* [`postcss-auto-var-fallback`] adds var fallbacks by provided files of variables.
* [`postcss-color-rgba-fallback`] transforms `rgba()` to hexadecimal.
* [`postcss-disabled`] adds a `[disabled]` attribute and/or a `.disabled` class
  when the `:disabled` pseudo class is present.
* [`postcss-epub`] adds the `-epub-` prefix to relevant properties.
* [`postcss-esplit`] splits your CSS exceeding 4095 selectors for IE.
* [`postcss-fallback`] adds `fallback` function to avoid duplicate declarations.
* [`postcss-filter-gradient`] adds gradient filter for the old IE.
* [`postcss-flexibility`] adds `-js-` prefix for [`Flexibility polyfill`].
* [`postcss-gradient-transparency-fix`] transforms `transparent` values
  in gradients to support Safari's different color interpolation.
* [`postcss-hash-classname`] append hash string to your css class name.
* [`postcss-mqwidth-to-class`] converts min/max-width media queries to classes.
* [`postcss-opacity`] adds opacity filter for IE8.
* [`postcss-opacity-percentage`] transforms CSS4 percentage-based `opacity`
  values to float values.
* [`postcss-page-break`] adds `page-break-` fallback to `break-` properties.
* [`postcss-pseudoelements`] Convert `::` selectors into `:` selectors
  for IE 8 compatibility.
* [`postcss-redundant-color-vars`] adds custom property for certain border and
  box-shadow declarations to fix a known Safari bug
* [`postcss-replace-overflow-wrap`] replace `overflow-wrap` with `word-wrap`.
* [`postcss-round-subpixels`] plugin that rounds sub-pixel values
  to the nearest
  full pixel.
* [`postcss-unmq`] removes media queries while preserving desktop rules
  for IE≤8.
* [`postcss-vmin`] generates `vm` fallback for `vmin` unit in IE9.
* [`postcss-will-change`] inserts 3D hack before `will-change` property.
* [`autoprefixer`] adds vendor prefixes for you, using data from Can I Use.
* [`postcss-pie`] makes IE several of the most useful CSS3 decoration features.
* [`cssgrace`] provides various helpers and transpiles CSS 3 for IE
  and other old browsers.
* [`pixrem`] generates pixel fallbacks for `rem` units.
* [`postcss-fixie`] adds easy and painless IE hacks
* [`postcss-safe-area`] adds browser fallbacks for `safe-area-inset` `env`
  variables.
* [`webp-in-css`] to use WebP background images in CSS.
* [`postcss-clamp`] transform `clamp()` to combination of `min/max`
* [`postcss-spring-easing`] replaces `spring()` with a resulting `linear()`
  function and add a `--spring-duration` css variable.

See also [`oldie`] plugins pack.

[`Flexibility polyfill`]: https://github.com/10up/flexibility


## Language Extensions

* [`postcss-aspect-ratio`] fix an element's dimensions to an aspect ratio.
* [`postcss-atroot`] place rules directly at the root node.
* [`postcss-bem-fix`] adds at-rules for BEM and SUIT style classes.
* [`postcss-click`] allows to use the `:click` pseudo class and implement
  it in JavaScript.
* [`postcss-compact-mq`] provides compact syntax for media queries based
  on viewport width.
* [`postcss-conditionals`] adds `@if` statements.
* [`postcss-css-variables`] supports variables for selectors, and at-rules
  using W3C similar syntax.
* [`postcss-current-selector`] to get current selector in declaration.
* [`postcss-define-property`] to define properties shortcut.
* [`postcss-define-function`] to implement Sass `@function` directive.
* [`postcss-each`] adds `@each` statement.
* [`postcss-for`] adds `@for` loops.
* [`postcss-at-rules-variables`] adds support for custom properties in
  `@for`, `@each`, `@if`, etc.
* [`postcss-functions`] enables exposure of JavaScript functions.
* [`postcss-if-media`] inline or nest media queries within
  CSS rules & properties.
* [`postcss-inline-media`] inline multiple media queries into CSS property
  values.
* [`postcss-local-constants`] adds support for localized constants.
* [`postcss-map`] enables configuration maps.
* [`postcss-match`] adds `@match` for [Rust-style pattern matching].
* [`postcss-mixins`] enables mixins more powerful than Sass’,
  defined within stylesheets or in JS.
* [`postcss-media-variables`] adds support for `var()` and `calc()`
  in `@media` rules
* [`postcss-modular-scale`] adds a modular scale `ms()` function.
* [`postcss-namespace`] prefix a namespace to a selector.
* [`postcss-nested`] unwraps nested rules.
* [`postcss-nested-props`] unwraps nested properties.
* [`postcss-nested-vars`] supports nested Sass-style variables.
* [`postcss-pseudo-class-any-button`] adds `:any-button` pseudo-class
for targeting all button elements.
* [`postcss-pseudo-class-enter`] transforms `:enter` into `:hover` and `:focus`.
* [`postcss-quantity-queries`] enables quantity queries.
* [`postcss-ref`] refers properties from another rule.
* [`postcss-reverse-media`] reverse/Invert media query parameters.
* [`postcss-sassy-mixins`] enables mixins with Sass keywords.
* [`postcss-map-get`] adds the ability to use Sass like map function `map-get`.
* [`postcss-simple-extend`] lightweight extending of silent classes,
  like Sass’ `@extend`.
* [`postcss-simple-vars`] supports for Sass-style variables.
* [`postcss-strip-units`] strips units off of property values.
* [`postcss-vertical-rhythm`] adds a vertical rhythm unit
  based on `font-size` and `line-height`.
* [`postcss-vertical-rhythm-function`] adds a vertical rhythm `vr()` function
  that is unit agnostic and works in situations where the font-size cannot
  be calculated during build time.
* [`postcss-responsive-properties`] allows you to write responsive
  property values.
* [`postcss-text-remove-gap`] remove space before and after text strings, added
  by line-height and extra space in glyph itself.
* [`postcss-closest`] plugin to modify closest matching part of current
  selector.
* [`csstyle`] adds components workflow to your styles.
* [`postcss-percentage`] support Sass-like `percentage()` function.
* [`postcss-custom-css-units`] Define custom css units and convert them
  to CSS variables.
* [`postcss-easy-z`] lets you organize z-indices by declaring relations
  between them.
* [`@csstools/postcss-design-tokens`] lets you import and use design tokens
  from CSS.

[Rust-style pattern matching]: https://doc.rust-lang.org/book/match.html


## Colors

* [`postcss-ase-colors`] replaces color names with values read
  from an ASE palette file.
* [`postcss-brand-colors`] inserts company brand colors
  in the `brand-colors` module.
* [`postcss-color-alpha`] transforms `#hex.a`, `black(alpha)` and `white(alpha)`
  to `rgba()`.
* [`postcss-color-hcl`] transforms `hcl(H, C, L)` and `hcl(H, C, L, alpha)`
  to `#rgb` and `rgba()`.
* [`postcss-color-hexa`] transforms `hexa(hex, alpha)` into `rgba` format.
* [`postcss-color-mix`] mixes two colors together.
* [`postcss-color-palette`] transforms CSS 2 color keywords to a custom palette.
* [`postcss-color-pantone`] transforms pantone color to RGB.
* [`postcss-color-scale`] adds a color scale `cs()` function.
* [`postcss-color-short`] adds shorthand color declarations.
* [`postcss-color-yiq`] sets foreground colors using the YIQ color space.
* [`postcss-colorblind`] transforms colors using filters to simulate
  colorblindness.
* [`postcss-contrast`] checks background-color and gives either white or black.
* [`postcss-dark-theme-class`] to force dark or light theme by custom switcher.
* [`postcss-theme-colors`] add dark and light theme with color groups.
* [`postcss-hexrgba`] adds shorthand hex `rgba(hex, alpha)` method.
* [`postcss-rgb-plz`] converts 3 or 6 digit hex values to `rgb`.
* [`postcss-rgba-hex`] converts `rgba` values to `hex` analogues.
* [`postcss-shades-of-gray`] helps keeping grayscale colors consistent
  to a gray palette.
* [`colorguard`] helps maintain a consistent color palette.
* [`postcss-get-color`] get the prominent colors from an image.
* [`postcss-randomcolor`] supports function to use random color.


## Images and Fonts

* [`avif-in-css`] to use AVIF image format in CSS background.
* [`postcss-assets`] allows you to simplify URLs, insert image dimensions,
  and inline files.
* [`postcss-assets-rebase`] rebases assets from `url()`.
* [`postcss-at2x`] handles retina background images via use of `at-2x` keyword.
* [`postcss-background-image-auto-size`] generates CSS rules `width`
  and `height` for `background-image` automatically.
* [`postcss-border-9-patch`] generates 9-patch like border styles
  via a custom rule.
* [`postcss-cachebuster`] adds version parameter to images and fonts
* [`postcss-copy-assets`] copies assets referenced by relative `url()`s
  into a build directory.
* [`postcss-data-packer`] moves embedded Base64 data to a separate file.
* [`postcss-easysprites`] combine images to sprites, based on their
  image.png`#hash` and aspect ratio (`@2x`).
* [`postcss-icon-blender`] create custom SVG icon sets from over 80,000 free
  and open-source icons
* [`postcss-image-set`] adds `background-image` with first image
  for `image-set()`.
* [`postcss-image-inliner`] inlines local and remote images.
* [`postcss-instagram`] adds Instagram filters to `filter`.
* [`postcss-filter-tint`] adds tint filter to elements such as images.
* [`postcss-foft-classes`] adds guarding classes to blocks using web fonts
  for better font loading strategies.
* [`postcss-font-awesome`] adds an easy shortcut to font-awesome unicode codes
* [`postcss-font-grabber`] grabs remote fonts in `@font-face`,
  download them and update your CSS.
* [`postcss-font-pack`] simplifies font declarations and validates they match
  configured font packs.
* [`postcss-fontsize`] generates `rem` unit `font-size` and `line-height`
  with `px` fallbacks.
* [`postcss-fontpath`] adds font links for different browsers.
* [`postcss-fontsource-url`] rewrite Fontsource assets folder.
* [`postcss-lazyimagecss`] adds image width and height automatically.
* [`postcss-lazysprite`] generates sprites from the directory of images.
* [`postcss-placehold`] makes it easy to drop in placeholder images.
* [`postcss-resemble-image`] provides a gradient fallback for an image that
loosely resembles the original.
* [`postcss-resolve-urls`] resolves relative urls referenced in `url()`s
* [`postcss-responsive-images`] adds stylesheets for making
  your images responsive.
* [`postcss-sprites`] generates CSS sprites from stylesheets.
* [`postcss-svg`] insert inline SVG to CSS and allows to manage it colors.
* [`postcss-svg-fallback`] converts SVG in your CSS to PNG files for IE 8.
* [`postcss-svgo`] processes inline SVG through [SVGO].
* [`postcss-unicode-characters`] makes it easier to write `unicode-range`
  descriptors.
* [`postcss-url`] rebases or inlines `url()`s.
* [`postcss-urlrebase`] rebases `url()`s to a given root URL.
* [`postcss-urlrev`] adds MD5 hash strings to `url()`s.
* [`postcss-write-svg`] write inline SVGs in CSS.
* [`postcss-inline-svg`] inline SVG images and customize their styles.
* [`webpcss`] adds URLs for WebP images for browsers that support WebP.
* [`webp-in-css`] to use WebP image format in CSS background.

## Grids

* [`postcss-grid`] adds a semantic grid system.
* [`postcss-grid-kiss`] transforms ASCII-art grids into CSS Grid layout.
* [`postcss-grid-system`] creates grids based on a fixed column width.
* [`postcss-grid-fluid`] creates fluid grids.
* [`postcss-layout`] a plugin for some common CSS layout patterns
  and a Grid system.
* [`postcss-maze`] is a mobile first, semantic responsive grid
  to suit any design pattern.
* [`postcss-neat`] is a semantic and fluid grid framework.
* [`postcss-oldschool-grid`] is a grid system with wrapping columns
  and padding gutters.
* [`postcss-simple-grid`] create grid with one line.
* [`lost`] feature-rich `calc()` grid system by Jeet author.


## Optimizations

* [`postcss-calc`] reduces `calc()` to values
  (when expressions involve the same units).
* [`postcss-remove-nested-calc`] `calc(100vw - calc(20% - 10px))` to
  `calc(100vw - (20% - 10px))` for IE 11 compatibility.
* [`postcss-class-name-shortener`] shortens CSS class names to optimize
  website performance.
* [`postcss-combine-duplicated-selectors`] automatically join identical
  selectors.
* [`postcss-filter-mq`] Filter all matching or non-matching media queries.
* [`postcss-import`] inlines the stylesheets referred to by `@import` rules.
* [`postcss-nested-import`] inlines stylesheets referred to by `@import` rules
  inside nested rule blocks.
* [`postcss-partial-import`] inlines standard imports and Sass-like partials.
* [`postcss-reference`] emulates Less’s `@import`.
* [`postcss-remove-root`] removes all instances of `:root` from a stylesheet.
* [`postcss-single-charset`] ensures that there is one and only one
  `@charset` rule at the top of file.
* [`postcss-zindex`] rebases positive `z-index` values.
* [`postcss-unprefix`] Unprefixes vendor prefixes in legacy CSS.
* [`css-byebye`] removes the CSS rules that you don’t want.
* [`css-mqpacker`] joins matching CSS media queries into a single statement.
* [`stylehacks`] removes CSS hacks based on browser support.
* [`postcss-mq-optimize`] removes invalid media queries or its expressions.
* [`postcss-uncss`] removes unused CSS from your stylesheets.
* [`postcss-html-filter`] filters out CSS that does not apply to the HTML
  you provide.
* [`postcss-no-important`] delete declarations !important.
* [`postcss-deep-scopable`] unified deep scoped style for Vue.js.
* [`postcss-deadcss`] helps to find dead CSS in stylesheets.
* [`postcss-variable-compress`] minifies css variables and saves you space.

See also plugins in modular minifier [`cssnano`].

[SVGO]: https://github.com/svg/svgo


## Shortcuts

* [`postcss-alias`] creates shorter aliases for properties.
* [`postcss-alias-atrules`] creates shorter aliases for at-rules.
* [`postcss-all-link-colors`] insert colors for link-related pseudo-classes.
* [`postcss-border`] adds shorthand for width and color of all borders
  in `border` property.
* [`postcss-border-shortcut`] PostCSS plugin for assign default `border` type
  if not expressed.
* [`postcss-button`] creates buttons.
* [`postcss-center`] centers elements.
* [`postcss-circle`] inserts a circle with color.
* [`postcss-clearfix`] adds `fix` and `fix-legacy` properties to the `clear`
  declaration.
* [`postcss-crip`] shorthand properties for Crips that are too lazy to write.
* [`postcss-default-unit`] adds default unit to numeric CSS properties.
* [`postcss-easings`] replaces easing names from easings.net
  with `cubic-bezier()` functions.
* [`postcss-filter`] adds shorthand for black and white filter.
* [`postcss-focus`] adds `:focus` selector to every `:hover`.
* [`postcss-generate-preset`] allows quick generation of rules.
  Useful for creating repetitive utilities.
* [`postcss-hidden`] allows for easy ways to hide elements.
* [`postcss-input-style`] adds new pseudo-elements for cross-browser styling
  of inputs.
* [`postcss-nested-ancestors`] reference any parent/ancestor selector
  in nested CSS.
* [`postcss-parent-selector`] adds a parent selector to the beginning
  of all rules.
* [`postcss-position`] adds shorthand declarations for position attributes.
* [`postcss-property-lookup`] allows referencing property values without
  a variable.
* [`postcss-range-value`] range value with a max and min value between
  two screen sizes.
* [`postcss-responsive-type`] changes `font-size` depends on screen size.
* [`postcss-scrib`] define your own aliases/shortcuts for properties or values.
* [`postcss-short-font-size`] extends `font-size` to define line-height
  s a second value.
* [`postcss-short-position`] extends `position` to define edges
  as additional values.
* [`postcss-short-spacing`] extends `margin` and `padding` to allow
  or omitted edges.
* [`postcss-short-text`] adds a `text` shortcut property for several
  text-related properties.
* [`postcss-size`] adds a `size` shortcut that sets width and height
  with one declaration.
* [`postcss-speech-bubble`] adds speech bubbles of different kinds
  with just a couple of lines of CSS.
* [`postcss-transform-shortcut`] allows shorthand transform properties in CSS.
* [`postcss-triangle`] creates a triangle.
* [`postcss-typescale`] sets type based on a typographic scale.
* [`postcss-verthorz`] adds vertical and horizontal spacing declarations.
* [`font-magician`] generates all the `@font-face` rules needed in CSS.
* [`postcss-animation`] PostCSS plugin that adds `@keyframes` from animate.css.
* [`postcss-magic-animations`] PostCSS plugin that adds `@keyframes`
  from Magic Animations.


## Others

* [`postcss-add-root-selector`] intelligently wraps all rules
  in a custom selector.
* [`postcss-alter-property-value`] alters your CSS declarations
  from a rule based configuration.
* [`postcss-attribute-selector-prefix`] adds a prefix to attribute selectors
* [`postcss-auto-rem`] compiles pixel units to `rem` without configuration.
* [`postcss-autoreset`]  automatically adds reset styles.
* [`postcss-bem-to-js`] creates a JavaScript definition file for BEM-style CSS.
* [`postcss-bom`] adds a UTF-8 BOM to files.
* [`postcss-blurry-gradient-workaround`] fixes blurry CSS gradients
  with too many explicit end-stops.
* [`postcss-camelcaser`] transforms selectors to CamelCase.
* [`postcss-class-prefix`] adds a prefix/namespace to class selectors.
* [`postcss-classes-to-mixins`] converts classes to Sass, Less and Stylus mixins
* [`postcss-currency`] replaces name of currency with symbols.
* [`postcss-d-ts`] generates `.d.ts` declaration for TypeScript `import`
  from used CSS classes and ids
* [`postcss-eol`] replaces EOL of files.
* [`postcss-extract-value`] extracts values from css properties and puts them
  into variables.
* [`postcss-fakeid`] transforms `#foo` IDs to attribute selectors `[id="foo"]`.
* [`postcss-filter-stream`] blacklist files / folders that you don’t want
  to process with a PostCSS plugin.
* [`postcss-flexbox`] easy way to understand and start using CSS3 Flexbox.
* [`postcss-flexbox-reset`] resets Flexbox to avoid issues in responsive layouts.
* [`postcss-flexboxfixer`] unprefixes `-webkit-` only flexbox in legacy CSS.
* [`postcss-flexbugs-fixes`] fixes some of known [flexbox bugs].
* [`postcss-gradientfixer`] unprefixes `-webkit-` only gradients in legacy CSS.
* [`postcss-grid-reset`] resets CSS Grid to avoid issues in responsive layouts.
* [`postcss-hash`] replaces output file names with hash algorithms
  for cache busting.
* [`postcss-ie8`] strips out unsupported properties and media queries for IE8.
* [`postcss-increase-specificity`] increases the specificity of your selectors.
* [`postcss-inline-rtl`] converts your CSS to right-to-left,
  but inline (adding just what you need).
* [`postcss-join-transitions`] joins conflicting transition declarations.
* [`postcss-letter-tracking`] generates relative, Photoshop-compatible
  letter tracking for improved letter spacing.
* [`postcss-light-text`]  adds `-webkit-` antialiasing for light text.
* [`postcss-modules`]  allows to use CSS Modules everywhere.
* [`postcss-momentum-scrolling`] adding momentum style scrolling behavior
  (`-webkit-overflow-scrolling:touch`) for elements with overflow on iOS.
* [`postcss-mq-keyframes`] moves any animation keyframes in media queries
  to the end of the file.
* [`postcss-mq-last`] gives media query rules precedence by moving them
  to the end of the file.
* [`postcss-node-modules-replacer`] replaces path than includes `node_modules`
  to `~`.
* [`postcss-plugin-namespace`] add a css selector to all rules,
  so that CSS file don’t affect other element.
* [`postcss-prefix-hover`] adds a prefixed to any selector containing `:hover`.
* [`postcss-pseudo-content-insert`] adds `content: ''` to `:before` and `:after`
  if it is missing.
* [`postcss-pseudo-element-cases`] converts `.style::BEFORE`
  into `.style::before` and vice versa.
* [`postcss-pseudo-element-colons`] converts `.style:before`
  into `.style::before` and vice versa.
* [`postcss-pseudo-elements-content`] adds `content: ''` to `:before-c`
  and `:after-c`.
* [`postcss-pxtorem`] converts pixel units to `rem`.
* [`postcss-raw`] protects nodes inside `@raw` at-rules from being touched
  by other plugins.
* [`postcss-remove-prefixes`] removes vendor prefixes.
* [`postcss-rtlcss`] creates left-to-right and right-to-left rules
  in a single CSS file.
* [`postcss-safe-important`] adds `!important` to style declarations safely.
* [`postcss-sanitize`] remove properties and values using rules.
* [`postcss-scopify`] adds a user input scope to each selector.
* [`postcss-select`] select rules based off a selector list.
* [`postcss-selector-prefixer`] adds a prefix to css selectors.
* [`postcss-shorthand-expand`] expands shorthand properties.
* [`postcss-simple-trig`] calculate trigonometric functions: sin/cos/tan.
* [`postcss-sorting`] sort rules content with specified order.
* [`postcss-sort-media-queries`] combine and sort CSS media queries
  with mobile first or desktop first methods.
* [`postcss-style-guide`] generates a style guide automatically.
* [`css-declaration-sorter`] sorts CSS declarations fast and automatically
  in a certain order.
* [`perfectionist`] formats poorly written CSS and renders a “pretty” result.
* [`rtlcss`] mirrors styles for right-to-left locales.
* [`stylefmt`] modern CSS formatter that works well with `stylelint`.
* [`postcss-autocorrect`] corrects typos and notifies in the console.
* [`postcss-px-to-viewport`] generates viewport units
  (`vw`, `vh`, `vmin`, `vmax`) from `px` units.
* [`postcss-viewport-height-correction`] solves the popular problem when `100vh`
  doesn’t fit the mobile browser screen.
* [`postcss-unit-processor`] flexible processing of CSS units.
* [`postcss-rem-to-px`] converts `rem` values to `px` values.
* [`postcss-design-tokens`] provides a function to retrieve design tokens
  expressed in JS or JSON, within CSS.
* [`postcss-pixel-to-remvw`] converting px to both of rem and vw, also one of them
* [`postcss-easy-import`] inline `@import` rules content with extra features.
* [`postcss-plugin-ignore-file`] ignore file with a top-comment `/* @ignore */`.


[flexbox bugs]: https://github.com/philipwalton/flexbugs


## Analysis

* [`postcss-bem-linter`] lints CSS for conformance to SUIT CSS methodology.
* [`postcss-cssstats`] returns an object with CSS statistics.
* [`postcss-regexp-detect`] search for regexp in CSS declarations.
* [`css2modernizr`] creates a Modernizr config file
  that requires only the tests that your CSS uses.
* [`doiuse`] lints CSS for browser support, using data from Can I Use.
* [`immutable-css`] lints CSS for class mutations.
* [`list-selectors`] lists and categorizes the selectors used in your CSS,
  for code review.


## Reporters

* [`postcss-browser-reporter`] displays warning messages from other plugins
  right in your browser.
* [`postcss-forced-variables`] provides warnings and errors when specified
  properties don’t use variables.
* [`postcss-reporter`] logs warnings and other messages from other plugins
  in the console.


## Fun

* [`postcss-australian-stylesheets`] Australian Style Sheets.
* [`postcss-andalusian-stylesheets`] Andalusian Style Sheets.
* [`postcss-aze-stylesheets`] Azerbaijanian Style Sheets.
* [`postcss-canadian-stylesheets`] Canadian Style Sheets.
* [`postcss-chinese-stylesheets`] Chinese Style Sheets.
* [`postcss-czech-stylesheets`] Czech Style Sheets.
* [`postcss-german-stylesheets`] German Style Sheets.
* [`postcss-italian-stylesheets`] Italian Style Sheets.
* [`postcss-russian-stylesheets`] Russian Style Sheets.
* [`postcss-swedish-stylesheets`] Swedish Style Sheets.
* [`postcss-tatar-stylesheets`] Tatar Style Sheets
* [`postcss-trolling`] Trolling Style Sheets.
* [`postcss-lolcat-stylesheets`] Lolspeak Style Sheets.
* [`postcss-imperial`] adds CSS support for Imperial and US customary units
  of length.
* [`postcss-russian-units`] adds CSS support for russian units of length.
* [`postcss-pointer`] Replaces `pointer: cursor` with `cursor: pointer`.
* [`postcss-spiffing`] lets you use British English in your CSS.
* [`postcss-spanish-stylesheets`] Spanish Style Sheets.
* [`postcss-nope`] lets you write `nope` instead of `none`.
* [`postcss-glitch`] add glitch effect to your text.
* [`postcss-khaleesi`] translate CSS values and properties to
  `khaleesi meme` language.

[`postcss-background-image-auto-size`]:   https://github.com/JustClear/postcss-background-image-auto-size
[`postcss-letter-tracking`]:              https://github.com/letsjaam/postcss-letter-tracking
[`postcss-combine-duplicated-selectors`]: https://github.com/ChristianMurphy/postcss-combine-duplicated-selectors
[`postcss-attribute-case-insensitive`]:   https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-attribute-case-insensitive
[`postcss-alter-property-value`]:         https://github.com/kunukn/postcss-alter-property-value
[`postcss-attribute-selector-prefix`]:    https://github.com/GitScrum/postcss-attribute-selector-prefix
[`postcss-gradient-transparency-fix`]:    https://github.com/gilmoreorless/postcss-gradient-transparency-fix
[`postcss-vertical-rhythm-function`]:     https://github.com/F21/postcss-vertical-rhythm-function
[`postcss-pseudo-class-any-button`]:      https://github.com/andrepolischuk/postcss-pseudo-class-any-button
[`postcss-pseudo-elements-content`]:      https://github.com/omgovich/postcss-pseudo-elements-content
[`postcss-pseudo-element-cases`]:         https://github.com/timelsass/postcss-pseudo-element-cases
[`postcss-pseudo-element-colons`]:        https://github.com/timelsass/postcss-pseudo-element-colons
[`postcss-aze-stylesheets`]:              https://github.com/iskandarovBakshi/postcss-aze-stylesheets
[`postcss-andalusian-stylesheets`]:       https://github.com/bameda/postcss-andalusian-stylesheets
[`postcss-australian-stylesheets`]:       https://github.com/dp-lewis/postcss-australian-stylesheets
[`postcss-responsive-properties`]:        https://github.com/alexandr-solovyov/postcss-responsive-properties
[`postcss-pseudo-class-any-link`]:        https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-pseudo-class-any-link
[`postcss-pseudo-content-insert`]:        https://github.com/liquidlight/postcss-pseudo-content-insert
[`postcss-canadian-stylesheets`]:         https://github.com/chancancode/postcss-canadian-stylesheets
[`postcss-increase-specificity`]:         https://github.com/MadLittleMods/postcss-increase-specificity
[`postcss-chinese-stylesheets`]:          https://github.com/zhouwenbin/postcss-chinese-stylesheets
[`postcss-italian-stylesheets`]:          https://github.com/Pustur/postcss-italian-stylesheets
[`postcss-russian-stylesheets`]:          https://github.com/Semigradsky/postcss-russian-stylesheets
[`postcss-swedish-stylesheets`]:          https://github.com/johnie/postcss-swedish-stylesheets
[`postcss-color-rebeccapurple`]:          https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-color-rebeccapurple
[`postcss-auto-var-fallback`]:            https://github.com/Ch-Valentine/postcss-auto-var-fallback
[`postcss-color-rgba-fallback`]:          https://github.com/postcss/postcss-color-rgba-fallback
[`postcss-spanish-stylesheets`]:          https://github.com/ismamz/postcss-spanish-stylesheets
[`postcss-at-rules-variables`]:           https://github.com/GitScrum/postcss-at-rules-variables
[`postcss-discard-duplicates`]:           https://github.com/ben-eb/postcss-discard-duplicates
[`postcss-german-stylesheets`]:           https://github.com/timche/postcss-german-stylesheets
[`postcss-logical-properties`]:           https://github.com/ahmadalfy/postcss-logical-properties
[`postcss-bidirection`]:                  https://github.com/gasolin/postcss-bidirection
[`postcss-lolcat-stylesheets`]:           https://github.com/sandralundgren/postcss-lolcat-stylesheets
[`postcss-minify-font-weight`]:           https://github.com/ben-eb/postcss-minify-font-weight
[`postcss-pseudo-class-enter`]:           https://github.com/csstools/postcss-pseudo-class-enter
[`postcss-transform-shortcut`]:           https://github.com/csstools/postcss-transform-shortcut
[`postcss-unicode-characters`]:           https://github.com/ben-eb/postcss-unicode-characters
[`postcss-custom-properties`]:            https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-custom-properties
[`postcss-czech-stylesheets`]:            https://github.com/HoBi/postcss-czech-stylesheets
[`postcss-discard-font-face`]:            https://github.com/ben-eb/postcss-discard-font-face
[`postcss-responsive-images`]:            https://www.npmjs.com/package/postcss-responsive-images
[`postcss-selector-prefixer`]:            https://github.com/amaranter/postcss-selector-prefixer
[`postcss-tatar-stylesheets`]:            https://github.com/azat-io/postcss-tatar-stylesheets
[`postcss-browser-reporter`]:             https://github.com/postcss/postcss-browser-reporter
[`postcss-current-selector`]:             https://github.com/komlev/postcss-current-selector
[`postcss-custom-selectors`]:             https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-custom-selectors
[`postcss-discard-comments`]:             https://github.com/ben-eb/postcss-discard-comments
[`postcss-forced-variables`]:             https://github.com/alekhrycaiko/postcss-forced-variables
[`postcss-magic-animations`]:             https://github.com/nucliweb/postcss-magic-animations/
[`postcss-minify-selectors`]:             https://github.com/ben-eb/postcss-minify-selectors
[`postcss-mqwidth-to-class`]:             https://github.com/notacouch/postcss-mqwidth-to-class
[`postcss-quantity-queries`]:             https://github.com/pascalduez/postcss-quantity-queries
[`postcss-selector-matches`]:             https://github.com/postcss/postcss-selector-matches
[`postcss-shorthand-expand`]:             https://github.com/johnotander/postcss-shorthand-expand
[`postcss-dark-theme-class`]:             https://github.com/postcss/postcss-dark-theme-class
[`postcss-theme-colors`]:                 https://github.com/ambar/postcss-theme-colors
[`postcss-all-link-colors`]:              https://github.com/jedmao/postcss-all-link-colors
[`postcss-border-shortcut`]:              https://github.com/michelemazzucco/postcss-border-shortcut
[`postcss-color-hex-alpha`]:              https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-color-hex-alpha
[`postcss-define-property`]:              https://github.com/daleeidd/postcss-define-property
[`postcss-define-function`]:              https://github.com/titancat/postcss-define-function
[`postcss-filter-gradient`]:              https://github.com/yuezk/postcss-filter-gradient
[`postcss-generate-preset`]:              https://github.com/simonsmith/postcss-generate-preset
[`postcss-local-constants`]:              https://github.com/macropodhq/postcss-constants
[`postcss-media-variables`]:              https://github.com/WolfgangKluge/postcss-media-variables
[`postcss-page-break`]:                   https://github.com/shrpne/postcss-page-break
[`postcss-property-lookup`]:              https://github.com/simonsmith/postcss-property-lookup
[`postcss-remove-prefixes`]:              https://github.com/johnotander/postcss-remove-prefixes
[`postcss-replace-overflow-wrap`]:        https://github.com/MattDiMu/postcss-replace-overflow-wrap
[`postcss-range-value`]:                  https://github.com/soberwp/postcss-range-value
[`postcss-responsive-type`]:              https://github.com/seaneking/postcss-responsive-type
[`postcss-round-subpixels`]:              https://github.com/himynameisdave/postcss-round-subpixels
[`postcss-short-font-size`]:              https://github.com/csstools/postcss-short-font-size
[`postcss-vertical-rhythm`]:              https://github.com/markgoodyear/postcss-vertical-rhythm
[`postcss-border-9-patch`]:               https://github.com/teaualune/postcss-border-9-patch
[`postcss-color-function`]:               https://github.com/postcss/postcss-color-function
[`postcss-conic-gradient`]:               https://github.com/csstools/postcss-conic-gradient
[`postcss-convert-values`]:               https://github.com/ben-eb/postcss-convert-values
[`postcss-flexbugs-fixes`]:               https://github.com/luisrudge/postcss-flexbugs-fixes
[`postcss-font-format-keywords`]:         https://github.com/valtlai/postcss-font-format-keywords
[`postcss-font-normalize`]:               https://github.com/iahu/postcss-font-normalize
[`postcss-hash-classname`]:               https://github.com/ctxhou/postcss-hash-classname
[`postcss-oldschool-grid`]:               https://github.com/lordgiotto/postcss-oldschool-grid
[`postcss-partial-import`]:               https://github.com/csstools/postcss-partial-import
[`postcss-pseudoelements`]:               https://github.com/axa-ch/postcss-pseudoelements
[`postcss-resemble-image`]:               https://github.com/ben-eb/postcss-resemble-image
[`postcss-safe-important`]:               https://github.com/Crimx/postcss-safe-important
[`postcss-shades-of-gray`]:               https://github.com/laureanoarcanio/postcss-shades-of-gray
[`postcss-short-position`]:               https://github.com/csstools/postcss-short-position
[`postcss-single-charset`]:               https://github.com/hail2u/postcss-single-charset
[`css-declaration-sorter`]:               https://github.com/Siilwyn/css-declaration-sorter
[`postcss-alias-atrules`]:                https://github.com/maximkoretskiy/postcss-alias-atrules
[`postcss-assets-rebase`]:                https://github.com/devex-web-frontend/postcss-assets-rebase
[`postcss-color-palette`]:                https://github.com/zaim/postcss-color-palette
[`postcss-color-pantone`]:                https://github.com/longdog/postcss-color-pantone
[`postcss-css-variables`]:                https://github.com/MadLittleMods/postcss-css-variables
[`postcss-discard-empty`]:                https://github.com/ben-eb/postcss-discard-empty
[`postcss-extract-value`]:                https://github.com/lutien/postcss-extract-value
[`postcss-filter-stream`]:                https://www.npmjs.com/package/postcss-filter-stream
[`postcss-gradientfixer`]:                https://github.com/hallvors/postcss-gradientfixer
[`postcss-image-inliner`]:                https://github.com/bezoerb/postcss-image-inliner
[`postcss-modular-scale`]:                https://github.com/kristoferjoseph/postcss-modular-scale
[`postcss-normalize-url`]:                https://github.com/ben-eb/postcss-normalize-url
[`postcss-reduce-idents`]:                https://github.com/ben-eb/postcss-reduce-idents
[`postcss-regexp-detect`]:                https://github.com/devex-web-frontend/postcss-regexp-detect
[`postcss-reverse-media`]:                https://github.com/MadLittleMods/postcss-reverse-media
[`postcss-russian-units`]:                https://github.com/Semigradsky/postcss-russian-units
[`postcss-short-spacing`]:                https://github.com/csstools/postcss-short-spacing
[`postcss-simple-extend`]:                https://github.com/davidtheclark/postcss-simple-extend
[`postcss-speech-bubble`]:                https://github.com/archana-s/postcss-speech-bubble
[`postcss-aspect-ratio`]:                 https://github.com/arccoza/postcss-aspect-ratio
[`postcss-brand-colors`]:                 https://github.com/postcss/postcss-brand-colors
[`postcss-no-important`]:                 https://github.com/DUBANGARCIA/postcss-no-important
[`postcss-class-prefix`]:                 https://github.com/thompsongl/postcss-class-prefix
[`postcss-conditionals`]:                 https://github.com/andyjansson/postcss-conditionals
[`postcss-custom-media`]:                 https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-custom-media
[`postcss-default-unit`]:                 https://github.com/antyakushev/postcss-default-unit
[`postcss-flexboxfixer`]:                 https://github.com/hallvors/postcss-flexboxfixer
[`postcss-font-awesome`]:                 https://github.com/dan-gamble/postcss-font-awesome
[`postcss-font-variant`]:                 https://github.com/postcss/postcss-font-variant
[`postcss-lazyimagecss`]:                 https://github.com/Jeff2Ma/postcss-lazyimagecss
[`postcss-lazysprite`]:                   https://github.com/Jeff2Ma/postcss-lazysprite
[`postcss-media-minmax`]:                 https://github.com/postcss/postcss-media-minmax
[`postcss-merge-idents`]:                 https://github.com/ben-eb/postcss-merge-idents
[`postcss-mq-keyframes`]:                 https://github.com/TCotton/postcss-mq-keyframes
[`postcss-nested-props`]:                 https://github.com/jedmao/postcss-nested-props
[`postcss-sassy-mixins`]:                 https://github.com/andyjansson/postcss-sassy-mixins
[`postcss-selector-not`]:                 https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-selector-not
[`postcss-svg-fallback`]:                 https://github.com/justim/postcss-svg-fallback
[`postcss-cachebuster`]:                  https://github.com/glebmachine/postcss-cachebuster
[`postcss-color-alpha`]:                  https://github.com/avanes/postcss-color-alpha
[`postcss-color-scale`]:                  https://github.com/kristoferjoseph/postcss-color-scale
[`postcss-color-short`]:                  https://github.com/andrepolischuk/postcss-color-short
[`postcss-copy-assets`]:                  https://github.com/shutterstock/postcss-copy-assets
[`postcss-data-packer`]:                  https://github.com/Ser-Gen/postcss-data-packer
[`postcss-easysprites`]:                  https://github.com/glebmachine/postcss-easysprites
[`postcss-flexibility`]:                  https://github.com/7rulnik/postcss-flexibility
[`postcss-font-family`]:                  https://github.com/ben-eb/postcss-font-family
[`postcss-fontsize`]:                     https://github.com/richbachman/postcss-fontsize
[`postcss-fontsource-url`]:               https://github.com/mondeja/postcss-fontsource-url
[`postcss-grid-system`]:                  https://github.com/francoisromain/postcss-grid-system
[`postcss-input-style`]:                  https://github.com/seaneking/postcss-input-style
[`postcss-merge-rules`]:                  https://github.com/ben-eb/postcss-merge-rules
[`postcss-mq-optimize`]:                  https://github.com/panec/postcss-mq-optimize
[`postcss-nested-vars`]:                  https://github.com/jedmao/postcss-nested-vars
[`postcss-remove-root`]:                  https://github.com/cbracco/postcss-remove-root
[`postcss-simple-grid`]:                  https://github.com/admdh/postcss-simple-grid
[`postcss-simple-trig`]:                  https://github.com/Rplus/postcss-simple-trig
[`postcss-simple-vars`]:                  https://github.com/postcss/postcss-simple-vars
[`postcss-strip-units`]:                  https://github.com/whitneyit/postcss-strip-units
[`postcss-style-guide`]:                  https://github.com/morishitter/postcss-style-guide
[`postcss-will-change`]:                  https://github.com/postcss/postcss-will-change
[`postcss-randomcolor`]:                  https://github.com/alanev/postcss-randomcolor
[`postcss-filter-tint`]:                  https://github.com/alexlibby/postcss-filter-tint
[`postcss-ase-colors`]:                   https://github.com/dfernandez79/postcss-ase-colors
[`postcss-bem-linter`]:                   https://github.com/postcss/postcss-bem-linter
[`postcss-camelcaser`]:                   https://github.com/GMchris/postcss-camelcaser
[`postcss-color-gray`]:                   https://github.com/postcss/postcss-color-gray
[`postcss-color-hexa`]:                   https://github.com/nicksheffield/postcss-color-hexa
[`postcss-colorblind`]:                   https://github.com/btholt/postcss-colorblind
[`postcss-compact-mq`]:                   https://github.com/rominmx/postcss-compact-mq
[`postcss-grid-fluid`]:                   https://github.com/francoisromain/postcss-grid-fluid
[`postcss-inline-rtl`]:                   https://github.com/jakob101/postcss-inline-rtl
[`postcss-inline-svg`]:                   https://github.com/TrySound/postcss-inline-svg
[`postcss-short-text`]:                   https://github.com/csstools/postcss-short-text
[`postcss-animation`]:                    https://github.com/zhouwenbin/postcss-animation
[`postcss-autoreset`]:                    https://github.com/maximkoretskiy/postcss-autoreset
[`postcss-color-hcl`]:                    https://github.com/devgru/postcss-color-hcl
[`postcss-color-hwb`]:                    https://github.com/postcss/postcss-color-hwb
[`postcss-color-image`]:                  https://github.com/valtlai/postcss-color-image
[`postcss-color-mix`]:                    https://github.com/iamstarkov/postcss-color-mix
[`postcss-color-yiq`]:                    https://github.com/ben-eb/postcss-color-yiq
[`postcss-filter-mq`]:                    https://github.com/simeydotme/postcss-filter-mq
[`postcss-font-pack`]:                    https://github.com/jedmao/postcss-font-pack
[`postcss-functions`]:                    https://github.com/andyjansson/postcss-functions
[`postcss-get-color`]:                    https://github.com/ismamz/postcss-get-color
[`postcss-image-set`]:                    https://github.com/alex499/postcss-image-set
[`postcss-instagram`]:                    https://github.com/azat-io/postcss-instagram
[`postcss-namespace`]:                    https://github.com/totora0155/postcss-namespace
[`postcss-placehold`]:                    https://github.com/awayken/postcss-placehold
[`postcss-reference`]:                    https://github.com/dehuszar/postcss-reference
[`postcss-typescale`]:                    https://github.com/francoisromain/postcss-typescale
[`postcss-write-svg`]:                    https://github.com/csstools/postcss-write-svg
[`postcss-disabled`]:                     https://github.com/cocco3/postcss-disabled
[`postcss-clearfix`]:                     https://github.com/seaneking/postcss-clearfix
[`postcss-colormin`]:                     https://github.com/ben-eb/colormin
[`postcss-contrast`]:                     https://github.com/stephenway/postcss-contrast
[`postcss-cssstats`]:                     https://github.com/cssstats/postcss-cssstats
[`postcss-currency`]:                     https://github.com/talgautb/postcss-currency
[`postcss-fallback`]:                     https://github.com/MadLittleMods/postcss-fallback
[`postcss-fontpath`]:                     https://github.com/seaneking/postcss-fontpath
[`postcss-if-media`]:                     https://github.com/arccoza/postcss-if-media
[`postcss-imperial`]:                     https://github.com/cbas/postcss-imperial
[`postcss-position`]:                     https://github.com/seaneking/postcss-position
[`postcss-reporter`]:                     https://github.com/postcss/postcss-reporter
[`postcss-rgba-hex`]:                     https://github.com/XOP/postcss-rgba-hex
[`postcss-sanitize`]:                     https://github.com/eramdam/postcss-sanitize
[`postcss-spiffing`]:                     https://github.com/HashanP/postcss-spiffing
[`postcss-triangle`]:                     https://github.com/jedmao/postcss-triangle
[`postcss-trolling`]:                     https://github.com/juanfran/postcss-trolling
[`postcss-verthorz`]:                     https://github.com/davidhemphill/postcss-verthorz
[`pleeease-filters`]:                     https://github.com/iamvdo/pleeease-filters
[`postcss-easings`]:                      https://github.com/postcss/postcss-easings
[`postcss-flexbox`]:                      https://github.com/archana-s/postcss-flexbox
[`postcss-hexrgba`]:                      https://github.com/seaneking/postcss-hexrgba
[`postcss-initial`]:                      https://github.com/maximkoretskiy/postcss-initial
[`postcss-modules`]:                      https://github.com/outpunk/postcss-modules
[`postcss-opacity`]:                      https://github.com/iamvdo/postcss-opacity
[`postcss-opacity-percentage`]:           https://github.com/Dreamseer/postcss-opacity-percentage
[`postcss-pointer`]:                      https://github.com/markgoodyear/postcss-pointer
[`postcss-pxtorem`]:                      https://github.com/cuth/postcss-pxtorem
[`postcss-rgb-plz`]:                      https://github.com/himynameisdave/postcss-rgb-plz
[`postcss-map-get`]:                      https://github.com/GitScrum/postcss-map-get
[`postcss-scopify`]:                      https://github.com/pazams/postcss-scopify
[`postcss-sorting`]:                      https://github.com/hudochenkov/postcss-sorting
[`postcss-sprites`]:                      https://github.com/2createStudio/postcss-sprites
[`postcss-assets`]:                       https://github.com/borodean/postcss-assets
[`postcss-atroot`]:                       https://github.com/OEvgeny/postcss-atroot
[`postcss-border`]:                       https://github.com/andrepolischuk/postcss-border
[`postcss-button`]:                       https://github.com/francoisromain/postcss-button
[`postcss-center`]:                       https://github.com/jedmao/postcss-center
[`postcss-circle`]:                       https://github.com/jedmao/postcss-circle
[`postcss-esplit`]:                       https://github.com/vitaliyr/postcss-esplit
[`postcss-extend`]:                       https://github.com/travco/postcss-extend
[`postcss-fakeid`]:                       https://github.com/pathsofdesign/postcss-fakeid
[`postcss-filter`]:                       https://github.com/alanev/postcss-filter
[`postcss-hidden`]:                       https://github.com/lukelarsen/postcss-hidden
[`postcss-import`]:                       https://github.com/postcss/postcss-import
[`postcss-nested-import`]:                https://github.com/eriklharper/postcss-nested-import
[`postcss-layout`]:                       https://github.com/arccoza/postcss-layout
[`postcss-mixins`]:                       https://github.com/postcss/postcss-mixins
[`postcss-nested`]:                       https://github.com/postcss/postcss-nested
[`postcss-rtlcss`]:                       https://github.com/elchininet/postcss-rtlcss
[`postcss-select`]:                       https://github.com/johnotander/postcss-select
[`postcss-urlrebase`]:                    https://github.com/strarsis/postcss-urlrebase
[`postcss-urlrev`]:                       https://github.com/yuezk/postcss-urlrev
[`postcss-zindex`]:                       https://www.npmjs.com/package/postcss-zindex
[`list-selectors`]:                       https://github.com/davidtheclark/list-selectors
[`mq4-hover-shim`]:                       https://github.com/twbs/mq4-hover-shim
[`postcss-alias`]:                        https://github.com/seaneking/postcss-alias
[`postcss-apply`]:                        https://github.com/pascalduez/postcss-apply
[`postcss-focus`]:                        https://github.com/postcss/postcss-focus
[`postcss-match`]:                        https://github.com/rtsao/postcss-match
[`postcss-scrib`]:                        https://github.com/sneakertack/postcss-scrib
[`css2modernizr`]:                        https://github.com/vovanbo/css2modernizr
[`font-magician`]:                        https://github.com/csstools/postcss-font-magician
[`immutable-css`]:                        https://github.com/johno/immutable-css
[`perfectionist`]:                        https://github.com/ben-eb/perfectionist
[`postcss-uncss`]:                        https://github.com/RyanZim/postcss-uncss
[`postcss-click`]:                        https://github.com/ismamz/postcss-click
[`postcss-at2x`]:                         https://github.com/simonsmith/postcss-at2x
[`postcss-calc`]:                         https://github.com/postcss/postcss-calc
[`postcss-remove-nested-calc`]:           https://github.com/nico-jacobs/postcss-remove-nested-calc
[`postcss-crip`]:                         https://github.com/johnie/postcss-crip
[`postcss-each`]:                         https://github.com/outpunk/postcss-each
[`postcss-epub`]:                         https://github.com/Rycochet/postcss-epub
[`postcss-grid`]:                         https://github.com/andyjansson/postcss-grid
[`postcss-host`]:                         https://github.com/vitkarpov/postcss-host
[`postcss-maze`]:                         https://github.com/cathydutton/postcss-maze
[`postcss-neat`]:                         https://github.com/jo-asakura/postcss-neat
[`postcss-size`]:                         https://github.com/postcss/postcss-size
[`postcss-size-advanced`]:                https://github.com/jhpratt/postcss-size-advanced
[`postcss-svgo`]:                         https://www.npmjs.com/package/postcss-svgo
[`postcss-unmq`]:                         https://github.com/csstools/postcss-unmq
[`postcss-vmin`]:                         https://github.com/iamvdo/postcss-vmin
[`postcss-nope`]:                         https://github.com/dariopog/postcss-nope
[`autoprefixer`]:                         https://github.com/postcss/autoprefixer
[`css-mqpacker`]:                         https://github.com/hail2u/node-css-mqpacker
[`postcss-bem-fix`]:                      https://github.com/supermonkeyz/postcss-bem-fix
[`postcss-for`]:                          https://github.com/antyakushev/postcss-for
[`postcss-ie8`]:                          https://github.com/4wdmedia/postcss-ie8
[`postcss-map`]:                          https://github.com/pascalduez/postcss-map
[`postcss-raw`]:                          https://github.com/MadLittleMods/postcss-raw
[`postcss-svg`]:                          https://github.com/Pavliko/postcss-svg
[`postcss-url`]:                          https://github.com/postcss/postcss-url
[`webp-in-css`]:                          https://github.com/ai/webp-in-css
[`postcss-ref`]:                          https://github.com/morishitter/postcss-ref
[`colorguard`]:                           https://github.com/SlexAxton/css-colorguard
[`css-byebye`]:                           https://github.com/AoDev/css-byebye
[`stylehacks`]:                           https://www.npmjs.com/package/stylehacks
[`cssgrace`]:                             https://github.com/cssdream/cssgrace
[`stylefmt`]:                             https://github.com/morishitter/stylefmt
[`csstyle`]:                              https://github.com/geddski/csstyle
[`webpcss`]:                              https://github.com/lexich/webpcss
[`doiuse`]:                               https://github.com/anandthakker/doiuse
[`pixrem`]:                               https://github.com/robwierzbowski/node-pixrem
[`postcss-fixie`]:                        https://github.com/tivac/fixie
[`rtlcss`]:                               https://github.com/MohammadYounes/rtlcss
[`short`]:                                https://github.com/csstools/postcss-short
[`lost`]:                                 https://github.com/corysimmons/lost
[`postcss-text-remove-gap`]:              https://github.com/m18ru/postcss-text-remove-gap
[`postcss-closest`]:                      https://github.com/m18ru/postcss-closest
[`postcss-grid-kiss`]:                    https://github.com/sylvainpolletvillard/postcss-grid-kiss
[`postcss-unprefix`]:                     https://github.com/gucong3000/postcss-unprefix
[`postcss-pie`]:                          https://github.com/gucong3000/postcss-pie
[`postcss-color-hsl`]:                    https://github.com/dmarchena/postcss-color-hsl
[`postcss-color-rgb`]:                    https://github.com/dmarchena/postcss-color-rgb
[`postcss-parent-selector`]:              https://github.com/domwashburn/postcss-parent-selector
[`postcss-font-family-system-ui`]:        https://github.com/JLHwung/postcss-font-family-system-ui
[`postcss-percentage`]:                   https://github.com/creeperyang/postcss-percentage
[`postcss-start-to-end`]:                 https://github.com/sandrina-p/postcss-start-to-end
[`postcss-autocorrect`]:                  https://github.com/DimitrisNL/postcss-autocorrect
[`postcss-html-filter`]:                  https://github.com/mapbox/postcss-html-filter
[`postcss-hash`]:                         https://github.com/dacodekid/postcss-hash
[`postcss-light-text`]:                   https://github.com/jdsteinbach/postcss-light-text
[`postcss-bom`]:                          https://github.com/dichuvichkin/postcss-bom
[`postcss-eol`]:                          https://github.com/dichuvichkin/postcss-eol
[`postcss-node-modules-replacer`]:        https://github.com/dichuvichkin/postcss-node-modules-replacer
[`postcss-mq-last`]:                      https://github.com/JGJP/postcss-mq-last
[`postcss-bem-to-js`]:                    https://github.com/WebSeed/postcss-bem-to-js
[`postcss-foft-classes`]:                 https://github.com/zachleat/postcss-foft-classes
[`postcss-inline-media`]:                 https://github.com/dimitrinicolas/postcss-inline-media
[`postcss-nested-ancestors`]:             https://github.com/toomuchdesign/postcss-nested-ancestors
[`postcss-subgrid`]:                      https://github.com/seaneking/postcss-subgrid
[`postcss-join-transitions`]:             https://github.com/JGJP/postcss-join-transitions
[`postcss-font-display`]:                 https://github.com/dkrnl/postcss-font-display
[`postcss-if-function`]:                  https://github.com/mfranzke/css-if-polyfill/tree/main/packages/postcss-if-function
[`postcss-glitch`]:                       https://github.com/crftd/postcss-glitch
[`postcss-class-name-shortener`]:         https://github.com/mbrandau/postcss-class-name-shortener
[`postcss-plugin-namespace`]:             https://github.com/ymrdf/postcss-plugin-namespace
[`postcss-classes-to-mixins`]:            https://github.com/nrkno/postcss-classes-to-mixins
[`postcss-px-to-viewport`]:               https://github.com/evrone/postcss-px-to-viewport
[`postcss-font-grabber`]:                 https://github.com/AaronJan/postcss-font-grabber
[`postcss-redundant-color-vars`]:         https://github.com/caseyjacobson/postcss-redundant-color-vars
[`postcss-safe-area`]:                    https://github.com/plegner/postcss-safe-area
[`postcss-sort-media-queries`]:           https://github.com/solversgroup/postcss-sort-media-queries
[`postcss-momentum-scrolling`]:           https://github.com/solversgroup/postcss-momentum-scrolling
[`postcss-viewport-height-correction`]:   https://github.com/Faisal-Manzer/postcss-viewport-height-correction
[`postcss-clamp`]:                        https://github.com/polemius/postcss-clamp
[`postcss-pseudo-is`]:                    https://github.com/IlyaUpyackovich/postcss-pseudo-is
[`postcss-deep-scopable`]:                https://github.com/litt1e-p/postcss-deep-scopable
[`postcss-deadcss`]:                      https://github.com/DenyVeyten/postcss-deadcss
[`postcss-flexbox-reset`]:                https://github.com/AndrejGajdos/postcss-flexbox-reset
[`postcss-grid-reset`]:                   https://github.com/AndrejGajdos/postcss-grid-reset
[`webp-in-css`]:                          https://github.com/ai/webp-in-css
[`avif-in-css`]:                          https://github.com/nucliweb/avif-in-css
[`postcss-custom-css-units`]:             https://github.com/joe223/postcss-custom-css-units
[`postcss-khaleesi`]:                     https://github.com/Hugoer/postcss-khaleesi
[`postcss-blurry-gradient-workaround`]:   https://github.com/strarsis/postcss-blurry-gradient-workaround
[`postcss-d-ts`]:                         https://github.com/askirmas/postcss-d-ts
[`postcss-multi-value-display`]:          https://github.com/jake-low/postcss-multi-value-display
[`postcss-easy-z`]:                       https://github.com/CSSSR/postcss-easy-z
[`postcss-icon-blender`]:                 https://github.com/icon-blender/postcss-icon-blender
[`postcss-variable-compress`]:            https://github.com/navanshu/postcss-variable-compress
[`postcss-unit-processor`]:               https://github.com/hex-ci/postcss-unit-processor
[`postcss-rem-to-px`]:                    https://github.com/TheDutchCoder/postcss-rem-to-px
[`postcss-prefix-hover`]:                 https://github.com/larsmunkholm/postcss-prefix-hover
[`postcss-resolve-urls`]:                 https://github.com/bognarlaszlo/postcss-resolve-urls
[`postcss-design-tokens`]:                https://github.com/jptaranto/postcss-design-tokens
[`postcss-pixel-to-remvw`]:               https://github.com/ben-lau/postcss-pixel-to-remvw
[`@csstools/postcss-design-tokens`]:      https://github.com/csstools/postcss-plugins/tree/main/plugins/postcss-design-tokens
[`postcss-easy-import`]:                  https://github.com/TrySound/postcss-easy-import
[`postcss-spring-easing`]:                https://github.com/okikio/postcss-spring-easing
[`postcss-plugin-ignore-file`]:           https://github.com/RiadhAdrani/postcss-plugin-ignore-file
````

## File: docs/README-cn.md
````markdown
# PostCSS

<img align="right" width="95" height="95"
     alt="哲学家的石头 - PostCSS 的 logo"
     src="https://postcss.org/logo.svg">

PostCSS 是一个允许使用 JS 插件转换样式的工具。
这些插件可以检查（lint）你的 CSS，支持 CSS Variables 和 Mixins，
编译尚未被浏览器广泛支持的先进的 CSS 语法，内联图片，以及其它很多优秀的功能。

PostCSS 在工业界被广泛地应用，其中不乏很多有名的行业领导者，如：维基百科，Twitter，阿里巴巴，
JetBrains。PostCSS 的 [Autoprefixer] 插件是最流行的 CSS 处理工具之一。

PostCSS 接收一个 CSS 文件并提供了一个 API 来分析、修改它的规则（通过把 CSS 规则转换成一个[抽象语法树]的方式）。在这之后，这个 API 便可被许多[插件]利用来做有用的事情，比如寻错或自动添加 CSS vendor 前缀。

**Twitter 账号:** [@postcss](https://twitter.com/postcss)

如果需要 PostCSS 商业支持（如咨询，提升公司的前端文化，
PostCSS 插件），请联系 [Evil Martians](https://evilmartians.com/?utm_source=postcss)
邮箱 <surrender@evilmartians.com>。

[抽象语法树]:     https://zh.wikipedia.org/wiki/%E6%8A%BD%E8%B1%A1%E8%AA%9E%E6%B3%95%E6%A8%B9
[Autoprefixer]: https://github.com/postcss/autoprefixer
[插件]:          https://github.com/postcss/postcss/blob/main/README-cn.md#%E6%8F%92%E4%BB%B6

<a href="https://evilmartians.com/?utm_source=postcss">
  <img src="https://evilmartians.com/badges/sponsored-by-evil-martians.svg"
       alt="由 Evil Martians 赞助" width="236" height="54">
</a>

## 插件

截止到目前，PostCSS 有 200 多个插件。你可以在 [插件列表] 找到它们。
下方的列表是我们最喜欢的插件 - 它们很好地演示了我们可以用 PostCSS 做些什么。

如果你有任何新的想法，[开发 PostCSS 插件] 非常简单易上手。

[插件列表]: https://github.com/postcss/postcss/blob/main/docs/plugins.md

### 解决全局 CSS 的问题

* [`postcss-use`] 允许你在 CSS 里明确地设置 PostCSS 插件，并且只在当前文件执行它们。
* [`postcss-modules`] 和 [`react-css-modules`] 可以自动以组件为单位隔绝 CSS 选择器。
* [`postcss-autoreset`] 是全局样式重置的又一个选择，它更适用于分离的组件。
* [`postcss-initial`] 添加了 `all: initial` 的支持，重置了所有继承的样式。
* [`cq-prolyfill`] 添加了容器查询的支持，允许添加响应于父元素宽度的样式.

### 提前使用先进的 CSS 特性

* [`autoprefixer`] 添加了 vendor 浏览器前缀，它使用 Can I Use 上面的数据。
* [`postcss-preset-env`] 允许你使用未来的 CSS 特性。

### 更佳的 CSS 可读性

* [`postcss-sorting`] 给规则的内容以及@规则排序。
* [`postcss-utilities`] 囊括了最常用的简写方式和书写帮助。
* [`short`] 添加并拓展了大量的缩写属性。

### 图片和字体

* [`postcss-assets`] 可以插入图片尺寸和内联文件。
* [`postcss-sprites`] 能生成雪碧图。
* [`font-magician`] 生成所有在 CSS 里需要的 `@font-face` 规则。
* [`postcss-inline-svg`] 允许你内联 SVG 并定制它的样式。
* [`postcss-write-svg`] 允许你在 CSS 里写简单的 SVG。

### 提示器（Linters）

* [`stylelint`] 是一个模块化的样式提示器。
* [`stylefmt`] 是一个能根据 `stylelint` 规则自动优化 CSS 格式的工具。
* [`doiuse`] 提示 CSS 的浏览器支持性，使用的数据来自于 Can I Use。
* [`colorguard`] 帮助你保持一个始终如一的调色板。

### 其它

* [`postcss-rtl`] 在单个 CSS 文件里组合了两个方向（左到右，右到左）的样式。
* [`cssnano`] 是一个模块化的 CSS 压缩器。
* [`lost`] 是一个功能强大的 `calc()` 栅格系统。
* [`rtlcss`] 镜像翻转 CSS 样式，适用于 right-to-left 的应用场景。

[`postcss-inline-svg`]:         https://github.com/TrySound/postcss-inline-svg
[`postcss-preset-env`]:         https://github.com/jonathantneal/postcss-preset-env
[`react-css-modules`]:          https://github.com/gajus/react-css-modules
[`postcss-autoreset`]:          https://github.com/maximkoretskiy/postcss-autoreset
[`postcss-write-svg`]:          https://github.com/jonathantneal/postcss-write-svg
[`postcss-utilities`]:          https://github.com/ismamz/postcss-utilities
[`postcss-initial`]:            https://github.com/maximkoretskiy/postcss-initial
[`postcss-sprites`]:            https://github.com/2createStudio/postcss-sprites
[`postcss-modules`]:            https://github.com/outpunk/postcss-modules
[`postcss-sorting`]:            https://github.com/hudochenkov/postcss-sorting
[`postcss-assets`]:             https://github.com/assetsjs/postcss-assets
[开发 PostCSS 插件]:             https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md
[`font-magician`]:              https://github.com/jonathantneal/postcss-font-magician
[`autoprefixer`]:               https://github.com/postcss/autoprefixer
[`cq-prolyfill`]:               https://github.com/ausi/cq-prolyfill
[`postcss-rtl`]:                https://github.com/vkalinichev/postcss-rtl
[`postcss-use`]:                https://github.com/postcss/postcss-use
[`css-modules`]:                https://github.com/css-modules/css-modules
[`colorguard`]:                 https://github.com/SlexAxton/css-colorguard
[`stylelint`]:                  https://github.com/stylelint/stylelint
[`stylefmt`]:                   https://github.com/morishitter/stylefmt
[`cssnano`]:                    https://cssnano.github.io/cssnano/
[`doiuse`]:                     https://github.com/anandthakker/doiuse
[`rtlcss`]:                     https://github.com/MohammadYounes/rtlcss
[`short`]:                      https://github.com/jonathantneal/postcss-short
[`lost`]:                       https://github.com/peterramsing/lost

## 语法

PostCSS 可以转化样式到任意语法，不仅仅是 CSS。
如果还没有支持你最喜欢的语法，你可以编写一个解释器以及（或者）一个 stringifier 来拓展 PostCSS。

* [`sugarss`] 是一个以缩进为基础的语法，类似于 Sass 和 Stylus。
* [`postcss-syntax`] 通过文件扩展名自动切换语法。
* [`postcss-html`] 解析类 HTML 文件里`<style>`标签中的样式。
* [`postcss-markdown`] 解析 Markdown 文件里代码块中的样式。
* [`postcss-jsx`] 解析源文件里模板或对象字面量中的CSS。
* [`postcss-styled`] 解析源文件里模板字面量中的CSS。
* [`postcss-scss`] 允许你使用 SCSS *(但并没有将 SCSS 编译到 CSS)*。
* [`postcss-sass`] 允许你使用 Sass *(但并没有将 Sass 编译到 CSS)*。
* [`postcss-less`] 允许你使用 Less *(但并没有将 LESS 编译到 CSS)*。
* [`postcss-less-engine`] 允许你使用 Less *(并且使用真正的 Less.js 把 LESS 编译到 CSS)*。
* [`postcss-js`] 允许你在 JS 里编写样式，或者转换成 React 的内联样式／Radium／JSS。
* [`postcss-safe-parser`] 查找并修复 CSS 语法错误。
* [`midas`] 将 CSS 字符串转化成高亮的 HTML。

[`postcss-less-engine`]: https://github.com/Crunch/postcss-less
[`postcss-safe-parser`]: https://github.com/postcss/postcss-safe-parser
[`postcss-syntax`]:      https://github.com/gucong3000/postcss-syntax
[`postcss-html`]:        https://github.com/gucong3000/postcss-html
[`postcss-markdown`]:    https://github.com/gucong3000/postcss-markdown
[`postcss-jsx`]:         https://github.com/gucong3000/postcss-jsx
[`postcss-styled`]:      https://github.com/gucong3000/postcss-styled
[`postcss-scss`]:        https://github.com/postcss/postcss-scss
[`postcss-sass`]:        https://github.com/AleshaOleg/postcss-sass
[`postcss-less`]:        https://github.com/webschik/postcss-less
[`postcss-js`]:          https://github.com/postcss/postcss-js
[`sugarss`]:             https://github.com/postcss/sugarss
[`midas`]:               https://github.com/ben-eb/midas

## 文章

* [一些你对 PostCSS 可能产生的误解](http://julian.io/some-things-you-may-think-about-postcss-and-you-might-be-wrong)
* [PostCSS 究竟是什么，是做什么的](http://davidtheclark.com/its-time-for-everyone-to-learn-about-postcss)
* [PostCSS 指南](http://webdesign.tutsplus.com/series/postcss-deep-dive--cms-889)

你可以在 [awesome-postcss](https://github.com/jjaderg/awesome-postcss) 列表里找到更多优秀的文章和视频。

## 书籍

* Alex Libby, Packt 的 [网页设计之精通 PostCSS](https://www.packtpub.com/web-development/mastering-postcss-web-design) (2016年6月)

## 使用方法

你可以通过简单的两步便开始使用 PostCSS：

1. 在你的构建工具中查找并添加 PostCSS 拓展。
2. [选择插件]并将它们添加到你的 PostCSS 处理队列中。

[选择插件]: https://postcss.org/docs/postcss-plugins

### CSS-in-JS

同时使用 PostCSS 与 CSS-in-JS 的最好方式是 [`astroturf`](https://github.com/4Catalyzer/astroturf)，将它的 loader 添加到 `webpack.config.js` 中：

```js
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'postcss-loader'],
      },
      {
        test: /\.jsx?$/,
        use: ['babel-loader', 'astroturf/loader'],
      }
    ]
  }
}
```

然后创建 `postcss.config.js`：

```js
module.exports = {
  plugins: [
    require('autoprefixer'),
    require('postcss-nested')
  ]
}
```

### Parcel

[Parcel](https://parceljs.org/) 有内建的 PostCSS 支持，并已经使用 Autoprefixer 和 cssnano。如果你想更换插件，请在项目根目录中创建 `postcss.config.js`：

```js
module.exports = {
  plugins: [
    require('autoprefixer'),
    require('postcss-nested')
  ]
}
```

Parcel 甚至会自动地帮你安装这些插件。

> 请注意[第 1 版中存在的几个问题](https://github.com/parcel-bundler/parcel/labels/CSS%20Preprocessing)，第 2 版通过 [issue #2157](https://github.com/parcel-bundler/parcel/projects/5) 解决了这些问题。

### Webpack

在 `webpack.config.js` 里使用 [`postcss-loader`] :

```js
module.exports = {
  module: {
    rules: [
      {
        test: /\.css$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'style-loader',
          },
          {
            loader: 'css-loader',
            options: {
              importLoaders: 1,
            }
          },
          {
            loader: 'postcss-loader'
          }
        ]
      }
    ]
  }
}
```

然后创建 `postcss.config.js`:

```js
module.exports = {
  plugins: [
    require('autoprefixer'),
    require('postcss-nested')
  ]
}
```

[`postcss-loader`]: https://github.com/postcss/postcss-loader

### Gulp

使用 [`gulp-postcss`] 和 [`gulp-sourcemaps`].

```js
gulp.task('css', () => {
  const postcss    = require('gulp-postcss')
  const sourcemaps = require('gulp-sourcemaps')

  return gulp.src('src/**/*.css')
    .pipe( sourcemaps.init() )
    .pipe( postcss([ require('postcss-nested'), require('autoprefixer') ]) )
    .pipe( sourcemaps.write('.') )
    .pipe( gulp.dest('build/') )
})
```

[`gulp-sourcemaps`]: https://github.com/floridoo/gulp-sourcemaps
[`gulp-postcss`]:    https://github.com/postcss/gulp-postcss

### npm run / CLI

如果需要在你的命令行界面或 npm 脚本里使用 PostCSS，你可以使用 [`postcss-cli`]。

```sh
postcss --use autoprefixer -c options.json -o main.css css/*.css
```

[`postcss-cli`]: https://github.com/postcss/postcss-cli

### 浏览器

如果你想编译浏览器里的 CSS 字符串（例如像 CodePen 一样的在线编辑器），
只需使用 [Browserify] 或  [webpack]。它们会把 PostCSS 和插件文件打包进一个独立文件。

如果想要在 React 内联样式／JSS／Radium／其它 [CSS-in-JS] 里使用 PostCSS，
你可以用 [`postcss-js`] 然后转换样式对象。

```js
var postcss  = require('postcss-js')
var prefixer = postcss.sync([ require('autoprefixer') ])

prefixer({ display: 'flex' }) //=> { display: ['-webkit-box', '-webkit-flex', '-ms-flexbox', 'flex'] }
```

[`postcss-js`]: https://github.com/postcss/postcss-js
[Browserify]:   http://browserify.org/
[CSS-in-JS]:    https://github.com/MicheleBertoli/css-in-js
[webpack]:      https://webpack.github.io/

### 运行器

* **Grunt**: [`grunt-postcss`](https://github.com/nDmitry/grunt-postcss)
* **HTML**: [`posthtml-postcss`](https://github.com/posthtml/posthtml-postcss)
* **Stylus**: [`poststylus`](https://github.com/seaneking/poststylus)
* **Rollup**: [`rollup-plugin-postcss`](https://github.com/egoist/rollup-plugin-postcss)
* **Brunch**: [`postcss-brunch`](https://github.com/brunch/postcss-brunch)
* **Broccoli**: [`broccoli-postcss`](https://github.com/jeffjewiss/broccoli-postcss)
* **Meteor**: [`postcss`](https://atmospherejs.com/juliancwirko/postcss)
* **ENB**: [`enb-postcss`](https://github.com/awinogradov/enb-postcss)
* **Taskr**: [`taskr-postcss`](https://github.com/lukeed/taskr/tree/master/packages/postcss)
* **Start**: [`start-postcss`](https://github.com/start-runner/postcss)
* **Connect/Express**: [`postcss-middleware`](https://github.com/jedmao/postcss-middleware)

### JS API

对于其它的应用环境，你可以使用 JS API：

```js
const postcssNested = require('postcss-nested')
const autoprefixer = require('autoprefixer')
const postcss = require('postcss')
const fs = require('fs')

fs.readFile('src/app.css', (err, css) => {
  postcss([postcssNested, autoprefixer])
    .process(css, { from: 'src/app.css', to: 'dest/app.css' })
    .then(result => {
      fs.writeFile('dest/app.css', result.css)
      if ( result.map ) fs.writeFile('dest/app.css.map', result.map)
    })
})
```

阅读 [PostCSS API 文档] 获取更多有关 JS API 的信息.

所有的 PostCSS 运行器应当通过 [PostCSS 运行器指南]。

[PostCSS 运行器指南]: https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md
[PostCSS API 文档]:  https://postcss.org/api/

### 配置选项

绝大多数 PostCSS 运行器接受两个参数：

* 一个包含所需插件的数组
* 一个配置选项的对象

常见的选项：

* `syntax`: 一个提供了语法解释器和 stringifier 的对象。
* `parser`: 一个特殊的语法解释器（例如 [SCSS]）。
* `stringifier`: 一个特殊的语法 output 生成器（例如 [Midas]）。
* `map`: [source map 选项].
* `from`: input 文件名称（大多数运行器自动设置了这个）。
* `to`: output 文件名称（大多数运行器自动设置了这个）。

[source map 选项]: https://postcss.org/api/#sourcemapoptions
[Midas]:          https://github.com/ben-eb/midas
[SCSS]:           https://github.com/postcss/postcss-scss

### Atom

* [`language-postcss`] 添加了 PostCSS 和 [SugarSS] 代码高亮。
* [`source-preview-postcss`] 在一个独立窗口里实时预览生成的 CSS。

[SugarSS]: https://github.com/postcss/sugarss

### Sublime Text

* [`Syntax-highlighting-for-PostCSS`] 添加了 PostCSS 代码高亮。

[`Syntax-highlighting-for-PostCSS`]: https://github.com/hudochenkov/Syntax-highlighting-for-PostCSS
[`source-preview-postcss`]:          https://atom.io/packages/source-preview-postcss
[`language-postcss`]:                https://atom.io/packages/language-postcss

### Vim

* [`postcss.vim`] 添加了 PostCSS 代码高亮。

[`postcss.vim`]: https://github.com/stephenway/postcss.vim

### WebStorm

自 WebStorm 2016.3 开始，[提供了] 内建的 PostCSS 支持。

[提供了]: https://blog.jetbrains.com/webstorm/2016/08/webstorm-2016-3-early-access-preview/
````

## File: docs/README.md
````markdown
# Documentation

* [PostCSS Architecture](https://github.com/postcss/postcss/blob/main/docs/architecture.md#postcss-architecture)
  * [Overview](https://github.com/postcss/postcss/blob/main/docs/architecture.md#overview)
  * [Workflow](https://github.com/postcss/postcss/blob/main/docs/architecture.md#workflow)
  * [Core Structures](https://github.com/postcss/postcss/blob/main/docs/architecture.md#core-structures)
  * [API Reference](https://github.com/postcss/postcss/blob/main/docs/architecture.md#api-reference)
* [PostCSS Plugins](https://github.com/postcss/postcss/blob/main/docs/plugins.md#postcss-plugins)
  * [Control](https://github.com/postcss/postcss/blob/main/docs/plugins.md#control)
  * [Packs](https://github.com/postcss/postcss/blob/main/docs/plugins.md#packs)
  * [Future CSS Syntax](https://github.com/postcss/postcss/blob/main/docs/plugins.md#future-css-syntax)
  * [Fallbacks](https://github.com/postcss/postcss/blob/main/docs/plugins.md#fallbacks)
  * [Language Extensions](https://github.com/postcss/postcss/blob/main/docs/plugins.md#language-extensions)
  * [Colors](https://github.com/postcss/postcss/blob/main/docs/plugins.md#colors)
  * [Images and Fonts](https://github.com/postcss/postcss/blob/main/docs/plugins.md#images-and-fonts)
  * [Grids](https://github.com/postcss/postcss/blob/main/docs/plugins.md#grids)
  * [Optimizations](https://github.com/postcss/postcss/blob/main/docs/plugins.md#optimizations)
  * [Shortcuts](https://github.com/postcss/postcss/blob/main/docs/plugins.md#shortcuts)
  * [Others](https://github.com/postcss/postcss/blob/main/docs/plugins.md#others)
  * [Analysis](https://github.com/postcss/postcss/blob/main/docs/plugins.md#analysis)
  * [Reporters](https://github.com/postcss/postcss/blob/main/docs/plugins.md#reporters)
  * [Fun](https://github.com/postcss/postcss/blob/main/docs/plugins.md#fun)
* [PostCSS and Source Maps](https://github.com/postcss/postcss/blob/main/docs/source-maps.md#postcss-and-source-maps)

* [How to Write Custom Syntax](https://github.com/postcss/postcss/blob/main/docs/syntax.md#how-to-write-custom-syntax)
  * [Syntax](https://github.com/postcss/postcss/blob/main/docs/syntax.md#syntax)
  * [Parser](https://github.com/postcss/postcss/blob/main/docs/syntax.md#parser)
    * [Main Theory](https://github.com/postcss/postcss/blob/main/docs/syntax.md#main-theory)
    * [Performance](https://github.com/postcss/postcss/blob/main/docs/syntax.md#performance)
    * [Node Source](https://github.com/postcss/postcss/blob/main/docs/syntax.md#node-source)
    * [Raw Values](https://github.com/postcss/postcss/blob/main/docs/syntax.md#raw-values)
    * [Tests](https://github.com/postcss/postcss/blob/main/docs/syntax.md#tests)
   * [Stringifier](https://github.com/postcss/postcss/blob/main/docs/syntax.md#stringifier)
     * [Main Theory](https://github.com/postcss/postcss/blob/main/docs/syntax.md#main-theory-1)
     * [Builder Function](https://github.com/postcss/postcss/blob/main/docs/syntax.md#builder-function)
     * [Raw Values](https://github.com/postcss/postcss/blob/main/docs/syntax.md#raw-values-1)
     * [Tests](https://github.com/postcss/postcss/blob/main/docs/syntax.md#tests-1)
* [Writing a PostCSS Plugin](https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md#writing-a-postcss-plugin)
  * [Links](https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md#links)
  * [Step 1: Create an idea](https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md#step-1-create-an-idea)
  * [Step 2: Create a project](https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md#step-2-create-a-project)
  * [Step 3: Find nodes](https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md#step-3-find-nodes)
  * [Step 4: Change nodes](https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md#step-4-change-nodes)
  * [Step 5: Fight with frustration](https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md#step-5-fight-with-frustration)
  * [Step 6: Make it public](https://github.com/postcss/postcss/blob/main/docs/writing-a-plugin.md#step-6-make-it-public)

**Guidlines**
* [PostCSS Plugin Guidelines](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#postcss-plugin-guidelines)
  * [API](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#1-api)
    * [1.1 Clear name with `postcss-` prefix](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#11-clear-name-with-postcss--prefix)
    * [1.2. Do one thing, and do it well](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#12-do-one-thing-and-do-it-well)
    * [1.3. Do not use mixins](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#13-do-not-use-mixins)
    * [1.4. Keep `postcss` to `peerDependencies`](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#14-keep-postcss-to-peerdependencies)
    * [1.5. Set `plugin.postcssPlugin` with plugin name](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#15-set-pluginpostcssplugin-with-plugin-name)
  * [Processing](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#2-processing)
    * [2.1. Plugin must be tested](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#21-plugin-must-be-tested)
    * [2.2. Use asynchronous methods whenever possible](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#22-use-asynchronous-methods-whenever-possible)
    * [2.3. Use fast node’s scanning](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#23-use-fast-nodes-scanning)
    * [2.4. Set `node.source` for new nodes](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#24-set-nodesource-for-new-nodes)
    * [2.5. Use only the public PostCSS API](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#25-use-only-the-public-postcss-api)
  * [Dependencies](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#3-dependencies)
    * [3.1. Use messages to specify dependencies](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#31-use-messages-to-specify-dependencies)
  * [Errors](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#4-errors)
    * [4.1. Use `node.error` on CSS relevant errors](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#41-use-nodeerror-on-css-relevant-errors)
    * [4.2. Use `result.warn` for warnings](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#42-use-resultwarn-for-warnings)
  * [Documentation](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#5-documentation)
    * [5.1. Document your plugin in English](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#51-document-your-plugin-in-english)
    * [5.2. Include input and output examples](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#52-include-input-and-output-examples)
    * [5.3. Maintain a changelog](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#53-maintain-a-changelog)
    * [5.4. Include `postcss-plugin` keyword in `package.json`](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md#54-include-postcss-plugin-keyword-in-packagejson)

* [PostCSS Runner Guidelines](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#postcss-runner-guidelines)
  * [API](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#1-api)
    * [1.1. Accept functions in plugin parameters](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#11-accept-functions-in-plugin-parameters)
  * [Processing](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#21-set-from-and-to-processing-options)
    * [2.1. Set `from` and `to` processing options](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#21-set-from-and-to-processing-options)
    * [2.2. Use only the asynchronous API](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#22-use-only-the-asynchronous-api)
    * [2.3. Use only the public PostCSS API](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#23-use-only-the-public-postcss-api)
    * [3.1. Rebuild when dependencies change](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#31-rebuild-when-dependencies-change)
  * [Output](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#4-output)
    * [4.1. Don’t show JS stack for `CssSyntaxError`](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#41-dont-show-js-stack-for-csssyntaxerror)
    * [4.2. Display `result.warnings()`](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#42-display-resultwarnings)
    * [4.3. Allow the user to write source maps to different files](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#43-allow-the-user-to-write-source-maps-to-different-files)
  * [Documentation](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#5-documentation)
    * [5.1. Document your runner in English](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#51-document-your-runner-in-english)
    * [5.2. Maintain a changelog](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#52-maintain-a-changelog)
    * [5.3. `postcss-runner` keyword in `package.json`](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#53-postcss-runner-keyword-in-packagejson)
    * [5.4. Keep postcss to peerDependencies](https://github.com/postcss/postcss/blob/main/docs/guidelines/runner.md#54-keep-postcss-to-peerdependencies)
````

## File: docs/source-maps.md
````markdown
# PostCSS and Source Maps

See our **[source map API docs](https://postcss.org/api/#sourcemapoptions)**.
````

## File: docs/syntax.md
````markdown
# How to Write Custom Syntax

PostCSS can transform styles in any syntax, and is not limited to just CSS.
By writing a custom syntax, you can transform styles in any desired format.

Writing a custom syntax is much harder than writing a PostCSS plugin, but
it is an awesome adventure.

There are 3 types of PostCSS syntax packages:

* **Parser** to parse input string to node’s tree.
* **Stringifier** to generate output string by node’s tree.
* **Syntax** contains both parser and stringifier.

**Table of Contents**

* [Syntax](#syntax)
* [Parser](#parser)
  * [Main Theory](#main-theory)
  * [Performance](#performance)
  * [Node Source](#node-source)
  * [Raw Values](#raw-values)
  * [Tests](#tests)
* [Stringifier](#stringifier)
  * [Main Theory](#main-theory-1)
  * [Builder Function](#builder-function)
  * [Raw Values](#raw-values-1)
  * [Tests](#tests-1)

## Syntax

A good example of a custom syntax is [SCSS]. Some users may want to transform
SCSS sources with PostCSS plugins, for example if they need to add vendor
prefixes or change the property order. So this syntax should output SCSS from
an SCSS input.

The syntax API is a very simple plain object, with `parse` & `stringify`
functions:

```js
module.exports = {
  parse:     require('./parse'),
  stringify: require('./stringify')
}
```

[SCSS]: https://github.com/postcss/postcss-scss


## Parser

A good example of a parser is [Safe Parser], which parses malformed/broken CSS.
Because there is no point to generate broken output, this package only provides
a parser.

The parser API is a function which receives a string & returns a [`Root`]
or [`Document`] node. The second argument is a function which receives
an object with PostCSS options.

```js
const postcss = require('postcss')

module.exports = function parse (css, opts) {
  const root = postcss.root()
  // Add other nodes to root
  return root
}
```

For open source parser npm package must have `postcss` in `peerDependencies`,
not in direct `dependencies`.

[Safe Parser]: https://github.com/postcss/postcss-safe-parser
[`Root`]:      https://postcss.org/api/#root
[`Document`]:  https://postcss.org/api/#document


### Main Theory

There are many books about parsers; but do not worry because CSS syntax is
very easy, and so the parser will be much simpler than a programming language
parser.

The default PostCSS parser contains two steps:

1. [Tokenizer] which reads input string character by character and builds a
  tokens array. For example, it joins space symbols to a `['space', '\n  ']`
  token, and detects strings to a `['string', '"\"{"']` token.
2. [Parser] which reads the tokens array, creates node instances and
  builds a tree.

[Tokenizer]: https://github.com/postcss/postcss/blob/main/lib/tokenize.js
[Parser]:    https://github.com/postcss/postcss/blob/main/lib/parser.js


### Performance

Parsing input is often the most time consuming task in CSS processors. So it
is very important to have a fast parser.

The main rule of optimization is that there is no performance without a
benchmark. You can look at [PostCSS benchmarks] to build your own.

Of parsing tasks, the tokenize step will often take the most time, so its
performance should be prioritized. Unfortunately, classes, functions and
high level structures can slow down your tokenizer. Be ready to write dirty
code with repeated statements. This is why it is difficult to extend the
default [PostCSS tokenizer]; copy & paste will be a necessary evil.

Second optimization is using character codes instead of strings.

```js
// Slow
string[i] === '{'

// Fast
const OPEN_CURLY = 123 // `{'
string.charCodeAt(i) === OPEN_CURLY
```

Third optimization is “fast jumps”. If you find open quotes, you can find
next closing quote much faster by `indexOf`:

```js
// Simple jump
next = string.indexOf('"', currentPosition + 1)

// Jump by RegExp
regexp.lastIndex = currentPosion + 1
regexp.test(string)
next = regexp.lastIndex
```

The parser can be a well written class. There is no need in copy-paste and
hardcore optimization there. You can extend the default [PostCSS parser].

[PostCSS benchmarks]: https://github.com/postcss/benchmark
[PostCSS tokenizer]:  https://github.com/postcss/postcss/blob/main/lib/tokenize.js
[PostCSS parser]:     https://github.com/postcss/postcss/blob/main/lib/parser.js


### Node Source

Every node should have `source` property to generate correct source map.
This property contains `start` and `end` properties with `{ line, column }`,
and `input` property with an [`Input`] instance.

Your tokenizer should save the original position so that you can propagate
the values to the parser, to ensure that the source map is correctly updated.

[`Input`]: https://github.com/postcss/postcss/blob/main/lib/input.js


### Raw Values

A good PostCSS parser should provide all information (including spaces symbols)
to generate byte-to-byte equal output. It is not so difficult, but respectful
for user input and allow integration smoke tests.

A parser should save all additional symbols to `node.raws` object.
It is an open structure for you, you can add additional keys.
For example, [SCSS parser] saves comment types (`/* */` or `//`)
in `node.raws.inline`.

The default parser cleans CSS values from comments and spaces.
It saves the original value with comments to `node.raws.value.raw` and uses it,
if the node value was not changed.

[SCSS parser]: https://github.com/postcss/postcss-scss


### Tests

Of course, all parsers in the PostCSS ecosystem must have tests.

If your parser just extends CSS syntax (like [SCSS] or [Safe Parser]),
you can use the [PostCSS Parser Tests]. It contains unit & integration tests.

[PostCSS Parser Tests]: https://github.com/postcss/postcss-parser-tests


## Stringifier

A style guide generator is a good example of a stringifier. It generates output
HTML which contains CSS components. For this use case, a parser isn't necessary,
so the package should just contain a stringifier.

The Stringifier API is little bit more complicated, than the parser API.
PostCSS generates a source map, so a stringifier can’t just return a string.
It must link every substring with its source node.

A Stringifier is a function which receives [`Root`] or [`Document`] node and builder callback.
Then it calls builder with every node’s string and node instance.

```js
module.exports = function stringify (root, builder) {
  // Some magic
  const string = decl.prop + ':' + decl.value + ';'
  builder(string, decl)
  // Some science
};
```


### Main Theory

PostCSS [default stringifier] is just a class with a method for each node type
and many methods to detect raw properties.

In most cases it will be enough just to extend this class,
like in [SCSS stringifier].

[default stringifier]: https://github.com/postcss/postcss/blob/main/lib/stringifier.js
[SCSS stringifier]:    https://github.com/postcss/postcss-scss/blob/main/lib/scss-stringifier.js


### Builder Function

A builder function will be passed to `stringify` function as second argument.
For example, the default PostCSS stringifier class saves it
to `this.builder` property.

Builder receives output substring and source node to append this substring
to the final output.

Some nodes contain other nodes in the middle. For example, a rule has a `{`
at the beginning, many declarations inside and a closing `}`.

For these cases, you should pass a third argument to builder function:
`'start'` or `'end'` string:

```js
this.builder(rule.selector + '{', rule, 'start')
// Stringify declarations inside
this.builder('}', rule, 'end')
```


### Raw Values

A good PostCSS custom syntax saves all symbols and provide byte-to-byte equal
output if there were no changes.

This is why every node has `node.raws` object to store space symbol, etc.

All data related to source code and not CSS structure, should be in `Node#raws`. For instance, `postcss-scss` keep in `Comment#raws.inline` boolean marker of inline comment (`// comment` instead of `/* comment */`).

Be careful, because sometimes these raw properties will not be present; some
nodes may be built manually, or may lose their indentation when they are moved
to another parent node.

This is why the default stringifier has a `raw()` method to autodetect raw
properties by other nodes. For example, it will look at other nodes to detect
indent size and then multiply it with the current node depth.


### Tests

A stringifier must have tests too.

You can use unit and integration test cases from [PostCSS Parser Tests].
Just compare input CSS with CSS after your parser and stringifier.

[PostCSS Parser Tests]: https://github.com/postcss/postcss-parser-tests
````

## File: docs/writing-a-plugin.md
````markdown
# Writing a PostCSS Plugin

**Table of Contents**

* [Links](#links)
* [Step 1: Create an idea](#step-1-create-an-idea)
* [Step 2: Create a project](#step-2-create-a-project)
* [Step 3: Find nodes](#step-3-find-nodes)
* [Step 4: Change nodes](#step-4-change-nodes)
* [Step 5: Fight with frustration](#step-5-fight-with-frustration)
* [Step 6: Make it public](#step-6-make-it-public)

## Links

Documentation:

* [Plugin Boilerplate](https://github.com/postcss/postcss-plugin-boilerplate)
* [Plugin Guidelines](https://github.com/postcss/postcss/blob/main/docs/guidelines/plugin.md)
* [PostCSS API](https://postcss.org/api/)
* [AST playground](https://astexplorer.net/#/2uBU1BLuJ1)

Support:

* [Ask questions](https://github.com/orgs/postcss/discussions)
* [PostCSS twitter](https://twitter.com/postcss) with latest updates.


## Step 1: Create an idea

There are many fields where writing new PostCSS plugin will help your work:

* **Compatibility fixes:** if you always forget to add hack
  for browser compatibility, you can create PostCSS plugin to automatically
  insert this hack for you. [`postcss-flexbugs-fixes`] and [`postcss-100vh-fix`]
  are good examples.
* **Automate routine operations:** let’s computer do routine operations, free
  yourself for creative tasks. For instance, PostCSS with [RTLCSS] can
  automatically convert a design to right-to-left languages (like Arabic
  or Hebrew) or with [postcss-dark-theme-class`] can insert media
  queries for dark/light theme switcher.
* **Preventing popular mistakes:** “if an error happened twice,
  it will happen again.” PostCSS plugin can check your source code for popular
  mistakes and save your time for unnecessary debugging. The best way to do it
  is to [write new Stylelint plugin] (Stylelint uses PostCSS inside).
* **Increasing code maintainability:** [CSS Modules] or [`postcss-autoreset`]
  are great example how PostCSS can increase code maintainability by isolation.
* **Polyfills:** we already have a lot polyfills for CSS drafts
  in [`postcss-preset-env`]. If you find a new draft, you can add a new plugin
  and send it to this preset.
* **New CSS syntax:** we recommend avoiding adding new syntax to CSS.
  If you want to add a new feature, it is always better to write a CSS draft
  proposal, send it to [CSSWG] and then implement polyfill.
  [`postcss-easing-gradients`] with [this proposal] is a good example.
  However, there are a lot of cases when you can’t send a proposal.
  For instance, browser’s parser performance limited CSSWG nested syntax a lot
  and you may want to have non-official Sass-like syntax from [`postcss-nested].

[`postcss-easing-gradients`]: https://github.com/larsenwork/postcss-easing-gradients
[write new Stylelint plugin]: https://stylelint.io/developer-guide/plugins
[postcss-dark-theme-class`]: https://github.com/postcss/postcss-dark-theme-class
[`postcss-flexbugs-fixes`]: https://github.com/luisrudge/postcss-flexbugs-fixes
[`postcss-preset-env`]: https://github.com/csstools/postcss-preset-env
[`postcss-autoreset`]: https://github.com/maximkoretskiy/postcss-autoreset
[`postcss-100vh-fix`]: https://github.com/postcss/postcss-100vh-fix
[`postcss-nested]: https://github.com/postcss/postcss-nested
[this proposal]: https://github.com/w3c/csswg-drafts/issues/1332
[CSS Modules]: https://github.com/css-modules/css-modules
[RTLCSS]: https://rtlcss.com/
[CSSWG]: https://github.com/w3c/csswg-drafts


## Step 2: Create a project

There are two ways to write a plugin:

* Create a **private** plugin. Use this way only if the plugin is related
  to specific things of projects. For instance, you want to automate a specific
  task for your unique UI library.
* Publish a **public** plugin. It is always the recommended way. Remember that
  private front-end systems, even in Google, often became unmaintained.
  On the other hand, many popular plugins were created during the work
  on a closed source project.

For private plugin:
1. Create a new file in `postcss/` folder with the name of your plugin.
2. Copy [plugin template] from our boilerplate.

For public plugins:
1. Use the guide in [PostCSS plugin boilerplate] to create a plugin directory.
2. Create a repository on GitHub or GitLab.
3. Publish your code there.

```js
module.exports = (opts = {}) => {
  // Plugin creator to check options or prepare shared state
  return {
    postcssPlugin: 'PLUGIN NAME'
    // Plugin listeners
  }
}
module.exports.postcss = true
```

[PostCSS plugin boilerplate]: https://github.com/postcss/postcss-plugin-boilerplate/
[plugin template]: https://github.com/postcss/postcss-plugin-boilerplate/blob/main/template/index.t.js


## Step 3: Find nodes

Most of the PostCSS plugins do two things:
1. Find something in CSS (for instance, `will-change` property).
2. Change found elements (for instance, insert `transform: translateZ(0)` before
   `will-change` as a polyfill for old browsers).

PostCSS parses CSS to the tree of nodes (we call it AST). This tree may content:
* [`Root`]: node of the top of the tree, which represent CSS file.
* [`AtRule`]: statements begin with `@` like `@charset "UTF-8"`
  or `@media (screen) {}`.
* [`Rule`]: selector with declaration inside. For instance `input, button {}`.
* [`Declaration`]: key-value pair like `color: black`;
* [`Comment`]: stand-alone comment. Comments inside selectors, at-rule
  parameters and values are stored in node’s `raws` property.

You can use [AST Explorer](https://astexplorer.net/#/2uBU1BLuJ1) to learn
how PostCSS convert different CSS to AST.

[`Root`]: https://postcss.org/api/#root
[`AtRule`]: https://postcss.org/api/#atrule
[`Rule`]: https://postcss.org/api/#rule
[`Declaration`]: https://postcss.org/api/#declaration
[`Comment`]: https://postcss.org/api/#comment

You can find all nodes with specific types by adding method to plugin object:

```js
module.exports = (opts = {}) => {
  return {
    postcssPlugin: 'PLUGIN NAME',
    Once (root) {
      // Calls once per file, since every file has single Root
    },
    Declaration (decl) {
      // All declaration nodes
    }
  }
}
module.exports.postcss = true
```

Here is the full list of [plugin’s events](https://postcss.org/api/#plugin).

If you need declaration or at-rule with specific names,
you can use quick search:

```js
    Declaration: {
      color: decl => {
        // All `color` declarations
      }
      '*': decl => {
        // All declarations
      }
    },
    AtRule: {
      media: atRule => {
        // All @media at-rules
      }
    }
```

For other cases, you can use regular expressions or specific parsers:

* [Selector parser](https://github.com/postcss/postcss-selector-parser)
* [Value parser](https://github.com/TrySound/postcss-value-parser)
* [Dimension parser](https://github.com/jedmao/parse-css-dimension)
  for `number`, `length` and `percentage`.
* [Media query parser](https://github.com/dryoma/postcss-media-query-parser)
* [Font parser](https://github.com/jedmao/parse-css-font)
* [Sides parser](https://github.com/jedmao/parse-css-sides)
  for `margin`, `padding` and `border` properties.

Other tools to analyze AST:

* [Property resolver](https://github.com/jedmao/postcss-resolve-prop)
* [Function resolver](https://github.com/andyjansson/postcss-functions)
* [Font helpers](https://github.com/jedmao/postcss-font-helpers)
* [Margin helpers](https://github.com/jedmao/postcss-margin-helpers)

Don’t forget that regular expression and parsers are heavy tasks. You can use
`String#includes()` quick test before check node with heavy tool:

```js
if (decl.value.includes('gradient(')) {
  let value = valueParser(decl.value)
  …
}
```

There two types or listeners: enter and exit. `Once`, `Root`, `AtRule`,
and `Rule` will be called before processing children. `OnceExit`, `RootExit`,
`AtRuleExit`, and `RuleExit` after processing all children inside node.

You may want to re-use some data between listeners. You can do with
runtime-defined listeners:

```js
module.exports = (opts = {}) => {
  return {
    postcssPlugin: 'vars-collector',
    prepare (result) {
      const variables = {}
      return {
        Declaration (node) {
          if (node.variable) {
            variables[node.prop] = node.value
          }
        },
        OnceExit () {
          console.log(variables)
        }
      }
    }
  }
}
```

You can use `prepare()` to generate listeners dynamically. For instance,
to use [Browserslist] to get declaration properties.

[Browserslist]: https://github.com/browserslist/browserslist


## Step 4: Change nodes

When you find the right nodes, you will need to change them or to insert/delete
other nodes around.

PostCSS node has a DOM-like API to transform AST. Check out our [API docs].
Nodes has methods to travel around (like [`Node#next`] or [`Node#parent`]),
look to children (like [`Container#some`]), remove a node
or add a new node inside.

Plugin’s methods will receive node creators in second argument:

```js
    Declaration (node, { Rule }) {
      let newRule = new Rule({ selector: 'a', source: node.source })
      node.root().append(newRule)
      newRule.append(node)
    }
```

If you added new nodes, it is important to copy [`Node#source`] to generate
correct source maps.

Plugins will re-visit all nodes, which you changed or added. If you will change
any children, plugin will re-visit parent as well. Only `Once` and
`OnceExit` will not be called again.

```js
const plugin = () => {
  return {
    postcssPlugin: 'to-red',
    Rule (rule) {
      console.log(rule.toString())
    },
    Declaration (decl) {
      console.log(decl.toString())
      decl.value = 'red'
    }
  }
}
plugin.postcss = true

await postcss([plugin]).process('a { color: black }', { from })
// => a { color: black }
// => color: black
// => a { color: red }
// => color: red
```

Since visitors will re-visit node on any changes, just adding children will
cause an infinite loop. To prevent it, you need to check
that you already processed this node:

```js
    Declaration: {
      'will-change': decl => {
        if (decl.parent.some(decl => decl.prop === 'transform')) {
          decl.cloneBefore({ prop: 'transform', value: 'translate3d(0, 0, 0)' })
        }
      }
    }
```

You can also use `Symbol` to mark processed nodes:

```js
const processed = Symbol('processed')

const plugin = () => {
  return {
    postcssPlugin: 'example',
    Rule (rule) {
      if (!rule[processed]) {
        process(rule)
        rule[processed] = true
      }
    }
  }
}
plugin.postcss = true
```

Second argument also have `result` object to add warnings:

```js
    Declaration: {
      bad: (decl, { result }) {
        decl.warn(result, 'Deprecated property bad')
      }
    }
```

If your plugin depends on another file, you can attach a message to `result`
to signify to runners (webpack, Gulp etc.) that they should rebuild the CSS
when this file changes:

```js
    AtRule: {
      import: (atRule, { result }) {
        const importedFile = parseImport(atRule)
        result.messages.push({
          type: 'dependency',
          plugin: 'postcss-import',
          file: importedFile,
          parent: result.opts.from
        })
      }
    }
```

If the dependency is a directory you should use the `dir-dependency`
message type instead:

```js
result.messages.push({
  type: 'dir-dependency',
  plugin: 'postcss-import',
  dir: importedDir,
  parent: result.opts.from
})
```

If you find an syntax error (for instance, undefined custom property),
you can throw a special error:

```js
if (!variables[name]) {
  throw decl.error(`Unknown variable ${name}`, { word: name })
}
```

[`Container#some`]: https://postcss.org/api/#container-some
[`Node#source`]: https://postcss.org/api/#node-source
[`Node#parent`]: https://postcss.org/api/#node-parent
[`Node#next`]: https://postcss.org/api/#node-next
[API docs]: https://postcss.org/api/


## Step 5: Fight with frustration

> I hate programming<br />
> I hate programming<br />
> I hate programming<br />
> It works!<br />
> I love programming

You will have bugs and a minimum of 10 minutes in debugging even a simple plugin.
You may found that simple origin idea will not work in real-world and you need
to change everything.

Don’t worry. Every bug is findable, and finding another solution may make your
plugin even better.

Start from writing tests. Plugin boilerplate has a test template
in `index.test.js`. Call `npx jest` to test your plugin.

Use Node.js debugger in your text editor or just `console.log`
to debug the code.

PostCSS community can help you since we are all experiencing the same problems.
Don’t afraid to ask in [special channel](https://github.com/orgs/postcss/discussions).


## Step 6: Make it public

When your plugin is ready, call `npx clean-publish` in your repository.
[`clean-publish`] is a tool to remove development configs from the npm package.
We added this tool to our plugin boilerplate.

Write a tweet about your new plugin (even if it is a small one) with
[`@postcss`] mention. Or tell about your plugin in [our chat].
We will help you with marketing.

[Add your new plugin] to PostCSS plugin catalog.

[Add your new plugin]: https://github.com/himynameisdave/postcss-plugins#submitting-a-new-plugin
[`clean-publish`]: https://github.com/shashkovdanil/clean-publish/
[`@postcss`]: https://twitter.com/postcss
````
