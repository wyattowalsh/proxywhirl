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
  cli/
    add.md
    approve-builds.md
    audit.md
    bin.md
    cache-delete.md
    cache-list-registries.md
    cache-list.md
    cache-view.md
    cache.md
    cat-file.md
    cat-index.md
    config.md
    create.md
    dedupe.md
    deploy.md
    dlx.md
    doctor.md
    env.md
    exec.md
    fetch.md
    find-hash.md
    ignored-builds.md
    import.md
    init.md
    install-test.md
    install.md
    licenses.md
    link.md
    list.md
    outdated.md
    pack.md
    patch-commit.md
    patch-remove.md
    patch.md
    prune.md
    publish.md
    rebuild.md
    recursive.md
    remove.md
    root.md
    run.md
    self-update.md
    server.md
    setup.md
    start.md
    store.md
    test.md
    unlink.md
    update.md
    why.md
  settings/
    _catalogMode.mdx
    _cpuFlag.mdx
    _enablePrePostScripts.mdx
    _globalPnpmfile.mdx
    _ignorePnpmfile.mdx
    _libcFlag.mdx
    _osFlag.mdx
    _pnpmfile.mdx
    _scriptShell.mdx
    _shellEmulator.mdx
  aliases.md
  catalogs.md
  completion.md
  config-dependencies.md
  configuring.md
  continuous-integration.md
  docker.md
  errors.md
  faq.md
  feature-comparison.md
  filtering.md
  git_branch_lockfiles.md
  git.md
  how-peers-are-resolved.md
  installation.md
  limitations.md
  logos.md
  motivation.md
  only-allow-pnpm.md
  package_json.md
  pnpm-cli.md
  pnpm-vs-npm.md
  pnpm-workspace_yaml.md
  pnpmfile.md
  podman.md
  production.md
  scripts.md
  symlinked-node-modules-structure.md
  typescript.md
  uninstall.md
  using-changesets.md
  workspaces.md
```

# Files

## File: docs/cli/add.md
````markdown
---
id: add
title: "pnpm add <pkg>"
---

Installs a package and any packages that it depends on.
By default, any new package is installed as a production dependency.

## TL;DR

| Command                                | Meaning                            |
|----------------------------------------|------------------------------------|
| `pnpm add sax`                         | Save to `dependencies`             |
| `pnpm add -D sax`                      | Save to `devDependencies`          |
| `pnpm add -O sax`                      | Save to `optionalDependencies`     |
| `pnpm add -g sax `                     | Install package globally           |
| `pnpm add sax@next`                    | Install from the `next` tag        |
| `pnpm add sax@3.0.0`                   | Specify version `3.0.0`            |

## Supported package locations

### Install from npm registry

`pnpm add package-name` will install the latest version of `package-name` from
the [npm registry](https://www.npmjs.com/) by default.

If executed in a workspace, the command will first try to check whether other
projects in the workspace use the specified package. If so, the already used version range
will be installed.

You may also install packages by:

* tag: `pnpm add express@nightly`
* version: `pnpm add express@1.0.0`
* version range: `pnpm add express@2 react@">=0.1.0 <0.2.0"`

[the corresponding guide]: #install-from-remote-tarball

### Install from the JSR registry

Added in: v10.9.0

To install packages from the [JSR](https://jsr.io/) registry, use the `jsr:` protocol prefix:

```
pnpm add jsr:@hono/hono
pnpm add jsr:@hono/hono@4
pnpm add jsr:@hono/hono@latest
```

This works just like installing from npm, but tells pnpm to resolve the package through JSR instead.

### Install from the workspace

Note that when adding dependencies and working within a [workspace], packages
will be installed from the configured sources, depending on whether or not
[`link-workspace-packages`] is set, and use of the
[`workspace: range protocol`].

[workspace]: ../workspaces.md
[`link-workspace-packages`]: ../workspaces.md#link-workspace-packages
[`workspace: range protocol`]: ../workspaces.md#workspace-ranges-workspace

### Install from local file system

There are two ways to install from the local file system:

1. from a tarball file (`.tar`, `.tar.gz`, or `.tgz`)
2. from a directory

Examples:

```sh
pnpm add ./package.tar.gz
pnpm add ./some-directory
```

When you install from a directory, a symlink will be created in the current
project's `node_modules`, so it is the same as running `pnpm link`.

### Install from remote tarball

The argument must be a fetchable URL starting with "http://" or "https://".

Example:

```sh
pnpm add https://github.com/indexzero/forever/tarball/v0.5.6
```

### Install from Git repository

```sh
pnpm add <git remote url>
```

Installs the package from the hosted Git provider, cloning it with Git.

You may install packages from Git by:

* Latest commit from default branch:
```
pnpm add kevva/is-positive
```
* Git commit hash:
```
pnpm add kevva/is-positive#97edff6f525f192a3f83cea1944765f769ae2678
```
* Git branch:
```
pnpm add kevva/is-positive#master
```
* Git branch relative to refs:
```
pnpm add zkochan/is-negative#heads/canary
```
* Git tag:
```
pnpm add zkochan/is-negative#2.0.1
```
* V-prefixed Git tag:
```
pnpm add andreineculau/npm-publish-git#v0.0.7
```

#### Install from a Git repository using semver

You can specify version (range) to install using the `semver:` parameter. For example:

* Strict semver:
```
pnpm add zkochan/is-negative#semver:1.0.0
```
* V-prefixed strict semver:
```
pnpm add andreineculau/npm-publish-git#semver:v0.0.7
```
* Semver version range:
```
pnpm add kevva/is-positive#semver:^2.0.0
```
* V-prefixed semver version range:
```
pnpm add andreineculau/npm-publish-git#semver:<=v0.0.7
```

#### Install from a subdirectory of a Git repository

You may also install just a subdirectory from a Git-hosted monorepo using the `path:` parameter. For instance:

```
pnpm add RexSkz/test-git-subfolder-fetch#path:/packages/simple-react-app
```

#### Install from a Git repository via a full URL

If you want to be more explicit or are using alternative Git hosting, you might want to spell out full Git URL:

```
# git+ssh
pnpm add git+ssh://git@github.com:zkochan/is-negative.git#2.0.1

# https
pnpm add https://github.com/zkochan/is-negative.git#2.0.1
```

#### Install from a Git repository using hosting providers shorthand

You can use a protocol shorthand `[provider]:` for certain Git providers:

```
pnpm add github:zkochan/is-negative
pnpm add bitbucket:pnpmjs/git-resolver
pnpm add gitlab:pnpm/git-resolver
```

If `[provider]:` is omitted, it defaults to `github:`.

#### Install from a Git repository combining different parameters

It is possible to combine multiple parameters by separating them with `&`. This can be useful for forks of monorepos:

```
pnpm add RexSkz/test-git-subdir-fetch.git#beta\&path:/packages/simple-react-app
```

Installs from the `beta` branch and only the subdirectory at `/packages/simple-react-app`.

## Options

### --save-prod, -P

Install the specified packages as regular `dependencies`.

### --save-dev, -D

Install the specified packages as `devDependencies`.

### --save-optional, -O

Install the specified packages as `optionalDependencies`.

### --save-exact, -E

Saved dependencies will be configured with an exact version rather than using
pnpm's default semver range operator.

### --save-peer

Using `--save-peer` will add one or more packages to `peerDependencies` and
install them as dev dependencies.

### --save-catalog

Added in: v10.12.1

Save the new dependency to the default [catalog].

### --save-catalog-name &lt;catalog_name\>

Added in: v10.12.1

Save the new dependency to the specified [catalog].

[catalog]: catalogs.md

### --config

Added in: v10.8.0

Save the dependency to [configDependencies](config-dependencies.md).

### --ignore-workspace-root-check

Adding a new dependency to the root workspace package fails, unless the
`--ignore-workspace-root-check` or `-w` flag is used.

For instance, `pnpm add debug -w`.

### --global, -g

Install a package globally.

### --workspace

Only adds the new dependency if it is found in the workspace.


### --allow-build

Added in: v10.4.0

A list of package names that are allowed to run postinstall scripts during installation.

Example:

```
pnpm --allow-build=esbuild add my-bundler
```

This will run `esbuild`'s postinstall script and also add it to the `onlyBuiltDependencies` field of `pnpm-workspace.yaml`. So, `esbuild` will always be allowed to run its scripts in the future.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)

import CpuFlag from '../settings/_cpuFlag.mdx'

<CpuFlag />

import OsFlag from '../settings/_osFlag.mdx'

<OsFlag />

import LibcFlag from '../settings/_libcFlag.mdx'

<LibcFlag />
````

## File: docs/cli/approve-builds.md
````markdown
---
id: approve-builds
title: pnpm approve-builds
---

Added in: v10.1.0

Approve dependencies for running scripts during installation.

## Options

### --global, -g

Added in: v10.4.0

Approve dependencies of globally installed packages.
````

## File: docs/cli/audit.md
````markdown
---
id: audit
title: pnpm audit
---

Checks for known security issues with the installed packages.

If security issues are found, try to update your dependencies via `pnpm update`.
If a simple update does not fix all the issues, use [overrides] to force
versions that are not vulnerable. For instance, if `lodash@<2.1.0` is vulnerable,
use this overrides to force `lodash@^2.1.0`:

```yaml title="pnpm-workspace.yaml"
overrides:
  "lodash@<2.1.0": "^2.1.0"
```

Or alternatively, run `pnpm audit --fix`.

If you want to tolerate some vulnerabilities as they don't affect your project, you may use the [`auditConfig.ignoreCves`] setting.

[overrides]: ../settings.md#overrides
[`auditConfig.ignoreCves`]: ../settings.md#auditconfigignorecves

## Options

### --audit-level &lt;severity\>

* Type: **low**, **moderate**, **high**, **critical**
* Default: **low**

Only print advisories with severity greater than or equal to `<severity>`.

### --fix

Add overrides to the `package.json` file in order to force non-vulnerable versions of the dependencies.

### --json

Output audit report in JSON format.

### --dev, -D

Only audit dev dependencies.

### --prod, -P

Only audit production dependencies.

### --no-optional

Don't audit `optionalDependencies`.

### --ignore-registry-errors

If the registry responds with a non-200 status code, the process should exit with 0.
So the process will fail only if the registry actually successfully responds with found vulnerabilities.

### --ignore-unfixable

Added in: v10.11.0

Ignore all CVEs with no resolution.

### --ignore &lt;vulnerability\>

Added in: v10.11.0

Ignore a vulnerability by CVE.
````

## File: docs/cli/bin.md
````markdown
---
id: bin
title: pnpm bin
---

Prints the directory into which the executables of dependencies are linked.

## Options

### --global, -g

Prints the location of the globally installed executables.
````

## File: docs/cli/cache-delete.md
````markdown
---
id: cache-delete
title: pnpm cache delete
---

:::warning

This command is experimental

:::

Deletes metadata cache for the specified package(s). Supports patterns.
````

## File: docs/cli/cache-list-registries.md
````markdown
---
id: cache-list-registries
title: pnpm cache list-registries
---

:::warning

This command is experimental

:::

Lists all registries that have their metadata cache locally.
````

## File: docs/cli/cache-list.md
````markdown
---
id: cache-list
title: pnpm cache list
---

:::warning

This command is experimental

:::

Lists the available packages metadata cache. Supports filtering by glob.
````

## File: docs/cli/cache-view.md
````markdown
---
id: cache-view
title: pnpm cache view
---

:::warning

This command is experimental

:::

Views information from the specified package's cache.
````

## File: docs/cli/cache.md
````markdown
---
id: cache
title: pnpm cache
---

Commands:
* [cache list](/cli/cache-list.md)
* [cache list-registries](/cli/cache-list-registries.md)
* [cache delete](/cli/cache-delete.md)
* [cache view](/cli/cache-view.md)
````

## File: docs/cli/cat-file.md
````markdown
---
id: cat-file
title: "pnpm cat-file"
---

Prints the contents of a file based on the hash value stored in the index file. For example:

```
pnpm cat-file sha512-mvavhfVcEREI7d8dfvfvIkuBLnx7+rrkHHnPi8mpEDUlNpY4CUY+CvJ5mrrLl18iQYo1odFwBV7z/cOypG7xxQ==
```
````

## File: docs/cli/cat-index.md
````markdown
---
id: cat-index
title: "pnpm cat-index"
---

Prints the index file of a specific package from the store. The package is specified by its name and version:

```
pnpm cat-index <pkg name>@<pkg version>
```
````

## File: docs/cli/config.md
````markdown
---
id: config
title: pnpm config
---

Aliases: `c`

Manage the configuration files.

The configuration files are in `INI` (the global) and `YAML` (the local) formats.

The local configuration file is located in the root of the project and is named `pnpm-workspace.yaml`.

The global configuration file is located at one of the following locations:

* If the **$XDG_CONFIG_HOME** env variable is set, then **$XDG_CONFIG_HOME/pnpm/rc**
* On Windows: **~/AppData/Local/pnpm/config/rc**
* On macOS: **~/Library/Preferences/pnpm/rc**
* On Linux: **~/.config/pnpm/rc**

## Commands

### set &lt;key> &lt;value>

Set the config key to the value provided.

### get &lt;key>

Print the config value for the provided key.

### delete &lt;key>

Remove the config key from the config file.

### list

Show all the config settings.

## Options

### --global, -g

Set the configuration in the global config file.

### --location

When set to `project`, the `.npmrc` file at the nearest `package.json` will be used. If no `.npmrc` file is present in the directory, the setting will be written to a `pnpm-workspace.yaml` file.

When set to `global`, the performance is the same as setting the `--global` option.

### --json

Show all the config settings in JSON format.
````

## File: docs/cli/create.md
````markdown
---
id: create
title: "pnpm create"
---

Create a project from a `create-*` or `@foo/create-*` starter kit.

## Examples

```
pnpm create react-app my-app
```

## Options

### --allow-build

Added in: v10.2.0

A list of package names that are allowed to run postinstall scripts during installation.
````

## File: docs/cli/dedupe.md
````markdown
---
id: dedupe
title: "pnpm dedupe"
---

Perform an install removing older dependencies in the lockfile if a newer version can be used.

## Options

### `--check`

Check if running dedupe would result in changes without installing packages or editing the lockfile. Exits with a non-zero status code if changes are possible.
````

## File: docs/cli/deploy.md
````markdown
---
id: deploy
title: "pnpm deploy"
---

Deploy a package from a workspace. During deployment, the files of the deployed package are copied to the target directory. All dependencies of the deployed package, including dependencies from the workspace, are installed inside an isolated `node_modules` directory at the target directory. The target directory will contain a portable package that can be copied to a server and executed without additional steps.

:::note

By default, the deploy command only works with workspaces that have the `inject-workspace-packages` setting set to `true`. If you want to use deploy without "injected dependencies", use the `--legacy` flag or set `force-legacy-deploy` to `true`.

:::

Usage:

```
pnpm --filter=<deployed project name> deploy <target directory>
```

In case you build your project before deployment, also use the `--prod` option to skip `devDependencies` installation.

```
pnpm --filter=<deployed project name> --prod deploy <target directory>
```

Usage in a docker image. After building everything in your monorepo, do this in a second image that uses your monorepo base image as a build context or in an additional build stage:

```Dockerfile
# syntax=docker/dockerfile:1.4

FROM workspace as pruned
RUN pnpm --filter <your package name> --prod deploy pruned

FROM node:18-alpine
WORKDIR /app

ENV NODE_ENV=production

COPY --from=pruned /app/pruned .

ENTRYPOINT ["node", "index.js"]
```

## Options

### --dev, -D

Only `devDependencies` are installed.

### --no-optional

`optionalDependencies` are not installed.

### --prod, -P

Packages in `devDependencies` won't be installed.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)

### --legacy

Force legacy deploy implementation.

By default, `pnpm deploy` will try creating a dedicated lockfile from a shared lockfile for deployment. The `--legacy` flag disables this behavior and also allows using the deploy command without the `inject-workspace-packages=true` setting.

## Files included in the deployed project

By default, all the files of the project are copied during deployment but this can be modified in _one_ of the following ways which are resolved in order:

1. The project's `package.json` may contain a "files" field to list the files and directories that should be copied.
2. If there is an `.npmignore` file in the application directory then any files listed here are ignored.
3. If there is a `.gitignore` file in the application directory then any files listed here are ignored.
````

## File: docs/cli/dlx.md
````markdown
---
id: dlx
title: "pnpm dlx"
---

Aliases: `pnpx` is an alias for `pnpm dlx`

Fetches a package from the registry without installing it as a dependency, hotloads it, and runs whatever default command binary it exposes.

For example, to use `create-vue` anywhere to bootstrap a Vue project without
needing to install it under another project, you can run:

```
pnpm dlx create-vue my-app
```

This will fetch `create-vue` from the registry and run it with the given arguments.

You may also specify which exact version of the package you'd like to use:

```
pnpm dlx create-vue@next my-app
```

## Options

### --package &lt;name\>

The package to install before running the command.

Example:

```
pnpm --package=@pnpm/meta-updater dlx meta-updater --help
pnpm --package=@pnpm/meta-updater@0 dlx meta-updater --help
```

Multiple packages can be provided for installation:

```
pnpm --package=yo --package=generator-webapp dlx yo webapp --skip-install
```

### --allow-build

Added in: v10.2.0

A list of package names that are allowed to run postinstall scripts during installation.

Example:

```
pnpm --allow-build=esbuild my-bundler bundle
```

The actual packages executed by `dlx` are allowed to run postinstall scripts by default. So if in the above example `my-bundler` has to be built before execution, it will be built.

### --shell-mode, -c

Runs the command inside of a shell. Uses `/bin/sh` on UNIX and `\cmd.exe` on Windows.

Example: 

```
pnpm --package cowsay --package lolcatjs -c dlx 'echo "hi pnpm" | cowsay | lolcatjs'
```

### --silent, -s

Only the output of the executed command is printed.
````

## File: docs/cli/doctor.md
````markdown
---
id: doctor
title: "pnpm doctor"
---

Checks for known common issues with pnpm configuration.
````

## File: docs/cli/env.md
````markdown
---
id: env
title: "pnpm env <cmd>"
---

Manages the Node.js environment.

:::danger

`pnpm env` does not include the binaries for Corepack. If you want to use Corepack to install other package managers, you need to install it separately (e.g. `pnpm add -g corepack`).

:::

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/84-MzN_0Cng" title="The pnpm patch command demo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"></iframe>


## Commands

### use

Install and use the specified version of Node.js

Install the LTS version of Node.js:

```
pnpm env use --global lts
```

Install Node.js v16:

```
pnpm env use --global 16
```

Install a prerelease version of Node.js:

```
pnpm env use --global nightly
pnpm env use --global rc
pnpm env use --global 16.0.0-rc.0
pnpm env use --global rc/14
```

Install the latest version of Node.js:

```
pnpm env use --global latest
```

Install an LTS version of Node.js using its [codename]:

```
pnpm env use --global argon
```

[codename]: https://github.com/nodejs/Release/blob/main/CODENAMES.md

### add

Installs the specified version(s) of Node.js without activating them as the current version.

Example:

```
pnpm env add --global lts 18 20.0.1
```

### remove, rm

Removes the specified version(s) of Node.js.

Usage example:

```
pnpm env remove --global 14.0.0
pnpm env remove --global 14.0.0 16.2.3
```

### list, ls

List Node.js versions available locally or remotely.

Print locally installed versions:

```
pnpm env list
```

Print remotely available Node.js versions:

```
pnpm env list --remote
```

Print remotely available Node.js v16 versions:

```
pnpm env list --remote 16
```

## Options

### --global, -g

The changes are made systemwide.
````

## File: docs/cli/exec.md
````markdown
---
id: exec
title: pnpm exec
---

Execute a shell command in scope of a project.

`node_modules/.bin` is added to the `PATH`, so `pnpm exec` allows executing commands of dependencies.

## Examples

If you have Jest as a dependency of your project, there is no need to install Jest globally, just run it with `pnpm exec`:

```
pnpm exec jest
```

The `exec` part is actually optional when the command is not in conflict with a builtin pnpm command, so you may also just run:

```
pnpm jest
```

## Options

Any options for the `exec` command should be listed before the `exec` keyword.
Options listed after the `exec` keyword are passed to the executed command.

Good. pnpm will run recursively:

```
pnpm -r exec jest
```

Bad, pnpm will not run recursively but `jest` will be executed with the `-r` option:

```
pnpm exec jest -r
```

### --recursive, -r

Execute the shell command in every project of the workspace.

The name of the current package is available through the environment variable
`PNPM_PACKAGE_NAME`.

#### Examples

Prune `node_modules` installations for all packages:

```
pnpm -r exec rm -rf node_modules
```

View package information for all packages. This should be used with the `--shell-mode` (or `-c`) option for the environment variable to work.

```
pnpm -rc exec pnpm view \$PNPM_PACKAGE_NAME
```

### --no-reporter-hide-prefix

Do not hide prefix when running commands in parallel.

### --resume-from &lt;package_name\>

Resume execution from a particular project. This can be useful if you are working with a large workspace and you want to restart a build at a particular project without running through all of the projects that precede it in the build order.

### --parallel

Completely disregard concurrency and topological sorting, running a given script
immediately in all matching packages. This is the
preferred flag for long-running processes over many packages, for instance, a
lengthy build process.

### --shell-mode, -c

Runs the command inside of a shell. Uses `/bin/sh` on UNIX and `\cmd.exe` on Windows.

### --report-summary

[Read about this option in the run command docs](./run.md#--report-summary)

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)
````

## File: docs/cli/fetch.md
````markdown
---
id: fetch
title: pnpm fetch
---

Fetch packages from a lockfile into virtual store, package manifest is ignored.

## Usage scenario

This command is specifically designed to improve building a docker image.

You may have read the [official guide] to writing a Dockerfile for a Node.js
app, if you haven't read it yet, you may want to read it first.

From that guide, we learn to write an optimized Dockerfile for projects using
pnpm, which looks like

```Dockerfile
FROM node:20

WORKDIR /path/to/somewhere

RUN corepack enable pnpm && corepack install -g pnpm@latest-10

# Files required by pnpm install
COPY .npmrc package.json pnpm-lock.yaml pnpm-workspace.yaml .pnpmfile.cjs ./

# If you patched any package, include patches before install too
COPY patches patches

RUN pnpm install --frozen-lockfile --prod

# Bundle app source
COPY . .

EXPOSE 8080
CMD [ "node", "server.js" ]
```

As long as there are no changes to `.npmrc`, `package.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`,
`.pnpmfile.cjs`, docker build cache is still valid up to the layer of
`RUN pnpm install --frozen-lockfile --prod`, which cost most of the time
when building a docker image.

However, modification to `package.json` may happen much more frequently than
we expect, because it does not only contain dependencies, but may also
contain the version number, scripts, and arbitrary configuration for any other
tool.

It's also hard to maintain a Dockerfile that builds a monorepo project, it may
look like

```Dockerfile
FROM node:20

WORKDIR /path/to/somewhere

RUN corepack enable pnpm && corepack install -g pnpm@latest-10

# Files required by pnpm install
COPY .npmrc package.json pnpm-lock.yaml pnpm-workspace.yaml .pnpmfile.cjs ./

# If you patched any package, include patches before install too
COPY patches patches

# for each sub-package, we have to add one extra step to copy its manifest
# to the right place, as docker have no way to filter out only package.json with
# single instruction
COPY packages/foo/package.json packages/foo/
COPY packages/bar/package.json packages/bar/

RUN pnpm install --frozen-lockfile --prod

# Bundle app source
COPY . .

EXPOSE 8080
CMD [ "node", "server.js" ]

```
As you can see, the Dockerfile has to be updated when you add or remove
sub-packages.

`pnpm fetch` solves the above problem perfectly by providing the ability
to load packages into the virtual store using only information from a lockfile and a configuration file (`pnpm-workspace.yaml`).

```Dockerfile
FROM node:20

WORKDIR /path/to/somewhere

RUN corepack enable pnpm && corepack install -g pnpm@latest-10

# pnpm fetch does require only lockfile
COPY pnpm-lock.yaml pnpm-workspace.yaml ./

# If you patched any package, include patches before running pnpm fetch
COPY patches patches

RUN pnpm fetch --prod


ADD . ./
RUN pnpm install -r --offline --prod


EXPOSE 8080
CMD [ "node", "server.js" ]
```

It works for both simple and monorepo projects, `--offline` enforces
pnpm not to communicate with the package registry as all needed packages are
already present in the virtual store.

As long as the lockfile is not changed, the build cache is valid up to the
layer, so `RUN pnpm install -r --offline --prod`, will save you much
time.



## Options

### --dev, -D

Only development packages will be fetched

### --prod, -P

Development packages will not be fetched



[official guide]: https://github.com/nodejs/docker-node#readme
````

## File: docs/cli/find-hash.md
````markdown
---
id: find-hash
title: "pnpm find-hash"
---

:::warning

This command is experimental

:::

Lists the packages that include the file with the specified hash. For example:

```
pnpm find-hash sha512-mvavhfVcEREI7d8dfvfvIkuBLnx7+rrkHHnPi8mpEDUlNpY4CUY+CvJ5mrrLl18iQYo1odFwBV7z/cOypG7xxQ==
```
````

## File: docs/cli/ignored-builds.md
````markdown
---
id: ignored-builds
title: pnpm ignored-builds
---

Added in: v10.1.0

Print the list of packages with blocked build scripts.
````

## File: docs/cli/import.md
````markdown
---
id: import
title: pnpm import
---

`pnpm import` generates a `pnpm-lock.yaml` from another package manager's lockfile. Supported source files:
* `package-lock.json`
* `npm-shrinkwrap.json`
* `yarn.lock`

Note that if you have workspaces you wish to import dependencies for, they will need to be declared in a [pnpm-workspace.yaml](../pnpm-workspace_yaml.md) file beforehand.
````

## File: docs/cli/init.md
````markdown
---
id: init
title: "pnpm init"
---

Create a `package.json` file.
````

## File: docs/cli/install-test.md
````markdown
---
id: install-test
title: pnpm install-test
---

Aliases: `it`

Runs `pnpm install` followed immediately by `pnpm test`. It takes exactly the
same arguments as [`pnpm install`](./install.md).
````

## File: docs/cli/install.md
````markdown
---
id: install
title: pnpm install
---

Aliases: `i`

`pnpm install` is used to install all dependencies for a project.

In a CI environment, installation fails if a lockfile is present but needs an
update.

Inside a [workspace], `pnpm install` installs all dependencies in all the
projects. If you want to disable this behavior, set the `recursive-install`
setting to `false`.

![](/img/demos/pnpm-install.svg)

[workspace]: ../workspaces.md

## TL;DR

| Command                           | Meaning                             |
|-----------------------------------|-------------------------------------|
| `pnpm i --offline`                | Install offline from the store only |
| `pnpm i --frozen-lockfile`        | `pnpm-lock.yaml` is not updated     |
| `pnpm i --lockfile-only`          | Only `pnpm-lock.yaml` is updated    |

## Options for filtering dependencies

Without a lockfile, pnpm has to create one, and it must be consistent regardless of dependencies
filtering, so running `pnpm install --prod` on a directory without a lockfile would still resolve the
dev dependencies, and it would error if the resolution is unsuccessful. The only exception for this rule
are `link:` dependencies.

Without `--frozen-lockfile`, pnpm will check for outdated information from `file:` dependencies, so
running `pnpm install --prod` without `--frozen-lockfile` on an environment where the target of `file:`
has been removed would error.

### --prod, -P

* Default: **false**
* Type: **Boolean**

If `true`, pnpm will not install any package listed in `devDependencies` and will remove 
those insofar they were already installed.
If `false`, pnpm will install all packages listed in `devDependencies` and `dependencies`.

### --dev, -D

Only `devDependencies` are installed and `dependencies` are removed insofar they 
were already installed.

### --no-optional

`optionalDependencies` are not installed.

## Options

### --force

Force reinstall dependencies: refetch packages modified in store, recreate a lockfile and/or modules directory created by a non-compatible version of pnpm. Install all optionalDependencies even they don't satisfy the current environment(cpu, os, arch).

### --offline

* Default: **false**
* Type: **Boolean**

If `true`, pnpm will use only packages already available in the store.
If a package won't be found locally, the installation will fail.

### --prefer-offline

* Default: **false**
* Type: **Boolean**

If `true`, staleness checks for cached data will be bypassed, but missing data
will be requested from the server. To force full offline mode, use `--offline`.

### --no-lockfile

Don't read or generate a `pnpm-lock.yaml` file.

### --lockfile-only

* Default: **false**
* Type: **Boolean**

When used, only updates `pnpm-lock.yaml` and `package.json`. Nothing gets written to the `node_modules` directory.

### --fix-lockfile

Fix broken lockfile entries automatically.

### --frozen-lockfile

* Default:
  * For non-CI: **false**
  * For CI: **true**, if a lockfile is present
* Type: **Boolean**

If `true`, pnpm doesn't generate a lockfile and fails to install if the lockfile
is out of sync with the manifest / an update is needed or no lockfile is
present.

This setting is `true` by default in [CI environments]. The following code is used to detect CI environments:

```js title="https://github.com/watson/ci-info/blob/44e98cebcdf4403f162195fbcf90b1f69fc6e047/index.js#L54-L61"
exports.isCI = !!(
  env.CI || // Travis CI, CircleCI, Cirrus CI, GitLab CI, Appveyor, CodeShip, dsari
  env.CONTINUOUS_INTEGRATION || // Travis CI, Cirrus CI
  env.BUILD_NUMBER || // Jenkins, TeamCity
  env.RUN_ID || // TaskCluster, dsari
  exports.name ||
  false
)
```

[CI environments]: https://github.com/watson/ci-info#supported-ci-tools

### --merge-git-branch-lockfiles

Merge all git branch lockfiles.
[Read more about git branch lockfiles.](../git_branch_lockfiles)


### --reporter=&lt;name\>

* Default:
    * For TTY stdout: **default**
    * For non-TTY stdout: **append-only**
* Type: **default**, **append-only**, **ndjson**, **silent**

Allows you to choose the reporter that will log debug info to the terminal about
the installation progress.

* **silent** - no output is logged to the console, not even fatal errors
* **default** - the default reporter when the stdout is TTY
* **append-only** - the output is always appended to the end. No cursor manipulations are performed
* **ndjson** - the most verbose reporter. Prints all logs in [ndjson](https://github.com/ndjson/ndjson-spec) format

If you want to change what type of information is printed, use the [loglevel] setting.

[loglevel]: ../settings.md#loglevel

### --use-store-server

* Default: **false**
* Type: **Boolean**

:::danger

Deprecated feature

:::

Starts a store server in the background. The store server will keep running
after installation is done. To stop the store server, run `pnpm server stop`

### --shamefully-hoist

* Default: **false**
* Type: **Boolean**

Creates a flat `node_modules` structure, similar to that of `npm` or `yarn`.
**WARNING**: This is highly discouraged.

### --ignore-scripts

* Default: **false**
* Type: **Boolean**

Do not execute any scripts defined in the project `package.json` and its
dependencies.

### --filter &lt;package_selector>

[Read more about filtering.](../filtering.md)

### --resolution-only

Re-runs resolution: useful for printing out peer dependency issues.

import CpuFlag from '../settings/_cpuFlag.mdx'

<CpuFlag />

import OsFlag from '../settings/_osFlag.mdx'

<OsFlag />

import LibcFlag from '../settings/_libcFlag.mdx'

<LibcFlag />
````

## File: docs/cli/licenses.md
````markdown
---
id: licenses
title: pnpm licenses
---

## Commands

### list

Aliases: `ls`

List licenses for installed packages.

## Options

### --dev, -D

Check only "devDependencies".

### --json

Show information in JSON format.

### --long

Show more details (such as a link to the repo) are not displayed. To display the details, pass this option.

### --no-optional

Don't check packages from `optionalDependencies`.

### --prod, -P

Check only `dependencies` and `optionalDependencies`.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)
````

## File: docs/cli/link.md
````markdown
---
id: link
title: pnpm link
---

Aliases: `ln`

Makes the current local package accessible system-wide, or in another location.

```text
pnpm link <dir|pkg name>
pnpm link
```

## Options

### `pnpm link <dir>`

Links package from `<dir>` directory to `node_modules` of package from where you're executing this command.

> For example, if you are inside `~/projects/foo` and you execute `pnpm link ../bar`, then a link to `bar` will be created in `foo/node_modules/bar`.

### `pnpm link`

Links package from location where this command was executed to global `node_modules`, so it can be referred from another package with `pnpm link <pkg>`. Also if the package has a `bin` field, then the package's binaries become available system-wide.

### `pnpm link <pkg>`

Links the specified package (`<pkg>`) from global `node_modules` to the `node_modules` of package from where this command was executed.

## Use Cases

### Replace an installed package with a local version of it

Let's say you have a project that uses `foo` package. You want to make changes to `foo` and test them in your project. In this scenario, you can use `pnpm link` to link the local version of `foo` to your project.

```bash
cd ~/projects/foo
pnpm install # install dependencies of foo
pnpm link # link foo globally
cd ~/projects/my-project
pnpm link foo # link foo to my-project
```

You can also link a package from a directory to another directory, without using the global `node_modules` directory:

```bash
cd ~/projects/foo
pnpm install # install dependencies of foo
cd ~/projects/my-project
pnpm link ~/projects/foo # link foo to my-project
```

### Add a binary globally

If you are developing a package that has a binary, for example, a CLI tool, you can use `pnpm link` to make the binary available system-wide.
This is the same as using `pnpm install -g foo`, but it will use the local version of `foo` instead of downloading it from the registry.

Remember that the binary will be available only if the package has a `bin` field in its `package.json`.

```bash
cd ~/projects/foo
pnpm install # install dependencies of foo
pnpm link # link foo globally
```

## What's the difference between `pnpm link` and using the `file:` protocol?

When you use `pnpm link`, the linked package is symlinked from the source code. You can modify the source code of the linked package, and the changes will be reflected in your project. With this method pnpm will not install the dependencies of the linked package, you will have to install them manually in the source code. This may be useful when you have to use a specific package manager for the linked package, for example, if you want to use `npm` for the linked package, but pnpm for your project.

When you use the `file:` protocol in `dependencies`, the linked package is hard-linked to your project `node_modules`, you can modify the source code of the linked package, and the changes will be reflected in your project. With this method pnpm will also install the dependencies of the linked package, overriding the `node_modules` of the linked package.

:::info

When dealing with **peer dependencies** it is recommended to use the `file:` protocol. It better resolves the peer dependencies from the project dependencies, ensuring that the linked dependency correctly uses the versions of the dependencies specified in your main project, leading to more consistent and expected behaviors.

:::

| Feature                                      | `pnpm link`                                        | `file:` Protocol                                    |
|----------------------------------------------|----------------------------------------------------|-----------------------------------------------------|
| Symlink/Hard-link                            | Symlink                                            | Hard-link                                           |
| Reflects source code modifications           | Yes                                                | Yes                                                 |
| Installs dependencies of the linked package  | No (manual installation required)                  | Yes (overrides `node_modules` of the linked package)|
| Use different package manager for dependency | Possible (e.g., use `npm` for linked pkg)          | No, it will use pnpm                                |
````

## File: docs/cli/list.md
````markdown
---
id: list
title: pnpm list
---

Aliases: `ls`

This command will output all the versions of packages that are installed, as
well as their dependencies, in a tree-structure.

Positional arguments are `name-pattern@version-range` identifiers, which will
limit the results to only the packages named. For example,
`pnpm list "babel-*" "eslint-*" semver@5`.

## Options

### --recursive, -r

Perform command on every package in subdirectories or on every workspace
package, when executed inside a workspace.

### --json

Log output in JSON format.

### --long

Show extended information.

### --parseable

Outputs package directories in a parseable format instead of their tree view.

### --global, -g

List packages in the global install directory instead of in the current project.

### --depth &lt;number\>

Max display depth of the dependency tree.

`pnpm ls --depth 0` (default) will list direct dependencies only.
`pnpm ls --depth -1` will list projects only. Useful inside a workspace when
used with the `-r` option.
`pnpm ls --depth Infinity` will list all dependencies regardless of depth.

### --prod, -P

Display only the dependency graph for packages in `dependencies` and
`optionalDependencies`.

### --dev, -D

Display only the dependency graph for packages in `devDependencies`.

### --no-optional

Don't display packages from `optionalDependencies`.

### --only-projects

Display only dependencies that are also projects within the workspace.

### --exclude-peers

Exclude peer dependencies from the results (but dependencies of peer dependencies are not ignored).

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)
````

## File: docs/cli/outdated.md
````markdown
---
id: outdated
title: pnpm outdated
---

Checks for outdated packages. The check can be limited to a subset of the
installed packages by providing arguments (patterns are supported).

Examples:
```sh
pnpm outdated
pnpm outdated "*gulp-*" @babel/core
```

## Options

### --recursive, -r

Check for outdated dependencies in every package found in subdirectories, or in
every workspace package when executed inside a workspace.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)

### --global, -g

List outdated global packages.

### --long

Print details.

### --format &lt;format\>

* Default: **table**
* Type: **table**, **list**, **json**

Prints the outdated dependencies in the given format.

### --compatible

Prints only versions that satisfy specifications in `package.json`.

### --dev, -D

Checks only `devDependencies`.

### --prod, -P

Checks only `dependencies` and `optionalDependencies`.

### --no-optional

Doesn't check `optionalDependencies`.

### --sort-by

Specifies the order in which the output results are sorted. Currently only the value `name` is accepted.
````

## File: docs/cli/pack.md
````markdown
---
id: pack
title: pnpm pack
---

Create a tarball from a package.

## Options

### --recursive, -r

Added in: v10.11.0

Pack all packages from the workspace.

### --out &lt;path\>

Customizes the output path for the tarball. Use `%s` and `%v` to include the package name and version, e.g., `%s.tgz` or `some-dir/%s-%v.tgz`. By default, the tarball is saved in the current working directory with the name `<package-name>-<version>.tgz`.

### --pack-destination &lt;dir\>

Directory in which `pnpm pack` will save tarballs. The default is the current working directory.

### --pack-gzip-level &lt;level\>

Specifying custom compression level.

### --json

Log output in JSON format.

### --filter &lt;package_selector\>

Added in: v10.11.0

[Read more about filtering.](../filtering.md)

## Life Cycle Scripts

* `prepack`
* `prepare`
* `postpack`
````

## File: docs/cli/patch-commit.md
````markdown
---
id: patch-commit
title: "pnpm patch-commit <path>"
---

Generate a patch out of a directory and save it (inspired by a similar command in Yarn).

This command will compare the changes from `path` to the package it was supposed to patch, generate a patch file, save the a patch file to `patchesDir` (which can be customized by the `--patches-dir` option), and add an entry to [`patchedDependencies`].

Usage:

```sh
pnpm patch-commit <path>
```

* `path` is the path to a modified copy of the patch target package, it is usually a temporary directory generated by [`pnpm patch`](./patch).

## Options

### ---patches-dir &lt;patchesDir>

The generated patch file will be saved to this directory. By default, patches are saved to the `patches` directory in the root of the project.

[`patchedDependencies`]: ../settings.md#patcheddependencies
````

## File: docs/cli/patch-remove.md
````markdown
---
id: patch-remove
title: "pnpm patch-remove <pkg...>"
---

Remove existing patch files and settings in `patchedDependencies`.

```sh
pnpm patch-remove foo@1.0.0 bar@1.0.1
```
````

## File: docs/cli/patch.md
````markdown
---
id: patch
title: "pnpm patch <pkg>"
---

Prepare a package for patching (inspired by a similar command in Yarn).

This command will cause a package to be extracted in a temporary directory intended to be editable at will.

Once you're done with your changes, run `pnpm patch-commit <path>` (with `<path>` being the temporary directory you received) to generate a patchfile and register it into your top-level manifest via the [`patchedDependencies`] field.

Usage:

```
pnpm patch <pkg name>@<version>
```

[`patchedDependencies`]: ../settings.md#patcheddependencies

:::note

If you want to change the dependencies of a package, don't use patching to modify the `package.json` file of the package. For overriding dependencies, use [overrides] or a [package hook].

:::

[overrides]: ../settings.md#overrides
[package hook]: ../pnpmfile#hooksreadpackagepkg-context-pkg--promisepkg

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/0GjLqRGRbcY" title="The pnpm patch command demo" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"></iframe>

## Options

### --edit-dir &lt;dir>

The package that needs to be patched will be extracted to this directory.

### --ignore-existing

Ignore existing patch files when patching.
````

## File: docs/cli/prune.md
````markdown
---
id: prune
title: pnpm prune
---

Removes unnecessary packages.

## Options

### --prod

Remove the packages specified in `devDependencies`.

### --no-optional

Remove the packages specified in `optionalDependencies`.

:::warning

The prune command does not support recursive execution on a monorepo currently. To only install production-dependencies in a monorepo `node_modules` folders can be deleted and then re-installed with `pnpm install --prod`.

:::
````

## File: docs/cli/publish.md
````markdown
---
id: publish
title: pnpm publish
---

Publishes a package to the registry.

```sh
pnpm [-r] publish [<tarball|folder>] [--tag <tag>]
     [--access <public|restricted>] [options]
```

When publishing a package inside a [workspace](../workspaces.md), the LICENSE file
from the root of the workspace is packed with the package (unless the package
has a license of its own).

You may override some fields before publish, using the
[publishConfig] field in `package.json`.
You also can use the [`publishConfig.directory`](../package_json.md#publishconfigdirectory) to customize the published subdirectory (usually using third party build tools).

When running this command recursively (`pnpm -r publish`), pnpm will publish all
the packages that have versions not yet published to the registry.

[publishConfig]: ../package_json.md#publishconfig

## Options

### --recursive, -r

Publish all packages from the workspace.

### --json

Show information in JSON format.

### --tag &lt;tag\>

Publishes the package with the given tag. By default, `pnpm publish` updates
the `latest` tag.

For example:

```sh
# inside the foo package directory
pnpm publish --tag next
# in a project where you want to use the next version of foo
pnpm add foo@next
```

### --access &lt;public|restricted\>

Tells the registry whether the published package should be public or restricted.

### --no-git-checks

Don't check if current branch is your publish branch, clean, and up-to-date with remote.

### --publish-branch &lt;branch\>

* Default: **master** and **main**
* Types: **String**

The primary branch of the repository which is used for publishing the latest
changes.

### --force

Try to publish packages even if their current version is already found in the
registry.

### --report-summary

Save the list of published packages to `pnpm-publish-summary.json`. Useful when some other tooling is used to report the list of published packages.

An example of a `pnpm-publish-summary.json` file:

```json
{
  "publishedPackages": [
    {
      "name": "foo",
      "version": "1.0.0"
    },
    {
      "name": "bar",
      "version": "2.0.0"
    }
  ]
}
```

### --dry-run

Does everything a publish would do except actually publishing to the registry.

### --otp

When publishing packages that require two-factor authentication, this option can specify a one-time password.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)

## Configuration

You can also set `gitChecks`, `publishBranch` options in the `pnpm-workspace.yaml` file.

For example:

```yaml title="pnpm-workspace.yaml"
gitChecks: false
publishBranch: production
```

## Life Cycle Scripts

* `prepublishOnly`
* `prepublish`
* `prepack`
* `prepare`
* `postpack`
* `publish`
* `postpublish`
````

## File: docs/cli/rebuild.md
````markdown
---
id: rebuild
title: pnpm rebuild
---

Aliases: `rb`

Rebuild a package.

## Options

### --recursive, -r

This command runs the **pnpm rebuild** command in every package of the monorepo.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)
````

## File: docs/cli/recursive.md
````markdown
---
id: recursive
title: pnpm -r, --recursive
---

Aliases: `m`, `multi`, `recursive`, `<command> -r`

Runs a command in every project of a workspace, when used with the following commands:

* `install`
* `list`
* `outdated`
* `publish`
* `pack`
* `rebuild`
* `remove`
* `unlink`
* `update`
* `why`

Runs a command in every project of a workspace, excluding the root project,
when used with the following commands:

* `exec`
* `run`
* `test`
* `add`

If you want the root project be included even when running scripts, set the [includeWorkspaceRoot] setting to `true`.

Usage example:

```
pnpm -r publish
```

## Options

### --link-workspace-packages

* Default: **false**
* Type: **true, false, deep**

Link locally available packages in workspaces of a monorepo into `node_modules`
instead of re-downloading them from the registry. This emulates functionality
similar to `yarn workspaces`.

When this is set to deep, local packages can also be linked to subdependencies.

Be advised that it is encouraged instead to use [`pnpm-workspace.yaml`] for this setting, to
enforce the same behaviour in all environments. This option exists solely so you
may override that if necessary.

[`pnpm-workspace.yaml`]: ../settings.md#linkWorkspacePackages

### --workspace-concurrency

* Default: **4**
* Type: **Number**

Set the maximum number of tasks to run simultaneously. For unlimited concurrency
use `Infinity`.

You can set the `workspace-concurrency` as `<= 0` and it will use amount of cores of the host as: `max(1, (number of cores) - abs(workspace-concurrency))`

### --[no-]bail

* Default: **true**
* Type: **Boolean**

If true, stops when a task throws an error.

This config does not affect the exit code.
Even if `--no-bail` is used, all tasks will finish but if any of the tasks fail,
the command will exit with a non-zero code.

Example (run tests in every package, continue if tests fail in one of them):
```sh
pnpm -r --no-bail test
```

### --[no-]sort

* Default: **true**
* Type: **Boolean**

When `true`, packages are sorted topologically (dependencies before dependents).
Pass `--no-sort` to disable.

Example:
```sh
pnpm -r --no-sort test
```

### --reverse

* Default: **false**
* Type: **boolean**

When `true`, the order of packages is reversed.

```
pnpm -r --reverse run clean
```

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)

[includeWorkspaceRoot]: ../settings.md#includeWorkspaceRoot
````

## File: docs/cli/remove.md
````markdown
---
id: remove
title: pnpm remove
---

Aliases: `rm`, `uninstall`, `un`

Removes packages from `node_modules` and from the project's `package.json`.

## Options

### --recursive, -r

When used inside a [workspace](../workspaces.md), removes a dependency (or
dependencies) from every workspace package.

When used not inside a workspace, removes a dependency (or dependencies) from
every package found in subdirectories.

### --global, -g

Remove a global package.

### --save-dev, -D

Only remove the dependency from `devDependencies`.

### --save-optional, -O

Only remove the dependency from `optionalDependencies`.

### --save-prod, -P

Only remove the dependency from `dependencies`.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)
````

## File: docs/cli/root.md
````markdown
---
id: root
title: pnpm root
---

Prints the effective modules directory.

## Options

### --global, -g

The global package's modules directory is printed.
````

## File: docs/cli/run.md
````markdown
---
id: run
title: pnpm run
---

Aliases: `run-script`

Runs a script defined in the package's manifest file.

## Examples

Let's say you have a `watch` script configured in your `package.json`, like so:

```json
"scripts": {
    "watch": "webpack --watch"
}
```

You can now run that script by using `pnpm run watch`! Simple, right?
Another thing to note for those that like to save keystrokes and time is that
all scripts get aliased in as pnpm commands, so ultimately `pnpm watch` is just
shorthand for `pnpm run watch` (ONLY for scripts that do not share the same name
as already existing pnpm commands).

## Running multiple scripts

You may run multiple scripts at the same time by using a regex instead of the script name.

```sh
pnpm run "/<regex>/"
```

Run all scripts that start with `watch:`:

```sh
pnpm run "/^watch:.*/"
```

## Details

In addition to the shell’s pre-existing `PATH`, `pnpm run` includes
`node_modules/.bin` in the `PATH` provided to `scripts`. This means that so
long as you have a package installed, you can use it in a script like a regular
command. For example, if you have `eslint` installed, you can write up a script
like so:

```json
"lint": "eslint src --fix"
```

And even though `eslint` is not installed globally in your shell, it will run.

For workspaces, `<workspace root>/node_modules/.bin` is also added
to the `PATH`, so if a tool is installed in the workspace root, it may be called
in any workspace package's `scripts`.

## Environment

There are some environment variables that pnpm automatically creates for the executed scripts.
These environment variables may be used to get contextual information about the running process.

These are the environment variables created by pnpm:

* **npm_command** - contains the name of the executed command. If the executed command is `pnpm run`, then the value of this variable will be "run-script".

## Options

Any options for the `run` command should be listed before the script's name.
Options listed after the script's name are passed to the executed script.

All these will run pnpm CLI with the `--silent` option:

```sh
pnpm run --silent watch
pnpm --silent run watch
pnpm --silent watch
```

Any arguments after the command's name are added to the executed script.
So if `watch` runs `webpack --watch`, then this command:

```sh
pnpm run watch --no-color
```

will run:

```sh
webpack --watch --no-color
```

### --recursive, -r

This runs an arbitrary command from each package's "scripts" object.
If a package doesn't have the command, it is skipped.
If none of the packages have the command, the command fails.

### --if-present

You can use the `--if-present` flag to avoid exiting with a non-zero exit code
when the script is undefined. This lets you run potentially undefined scripts
without breaking the execution chain.

### --parallel

Completely disregard concurrency and topological sorting, running a given script
immediately in all matching packages with prefixed streaming output. This is the
preferred flag for long-running processes over many packages, for instance, a
lengthy build process.

### --stream

Stream output from child processes immediately, prefixed with the originating
package directory. This allows output from different packages to be interleaved.

### --aggregate-output

Aggregate output from child processes that are run in parallel, and only print output when the child process is finished. It makes reading large logs after running `pnpm -r <command>` with `--parallel` or with `--workspace-concurrency=<number>` much easier (especially on CI). Only `--reporter=append-only` is supported.

### --resume-from &lt;package_name\>

Resume execution from a particular project. This can be useful if you are working with a large workspace and you want to restart a build at a particular project without running through all of the projects that precede it in the build order.

### --report-summary

Record the result of the scripts executions into a `pnpm-exec-summary.json` file.

An example of a `pnpm-exec-summary.json` file:

```json
{
  "executionStatus": {
    "/Users/zoltan/src/pnpm/pnpm/cli/command": {
      "status": "passed",
      "duration": 1861.143042
    },
    "/Users/zoltan/src/pnpm/pnpm/cli/common-cli-options-help": {
      "status": "passed",
      "duration": 1865.914958
    }
  }
```

Possible values of `status` are: 'passed', 'queued', 'running'.

### --reporter-hide-prefix

Hide workspace prefix from output from child processes that are run in parallel, and only print the raw output. This can be useful if you are running on CI and the output must be in a specific format without any prefixes (e.g. [GitHub Actions annotations](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-error-message)). Only `--reporter=append-only` is supported.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)

## pnpm-workspace.yaml settings

import EnablePrePostScripts from '../settings/_enablePrePostScripts.mdx'

<EnablePrePostScripts />

import ScriptShell from '../settings/_scriptShell.mdx'

<ScriptShell />

import ShellEmulator from '../settings/_shellEmulator.mdx'

<ShellEmulator />
````

## File: docs/cli/self-update.md
````markdown
---
id: self-update
title: pnpm self-update
---

Updates pnpm to the latest version or the one specified.

Usage examples:

```
pnpm self-update
pnpm self-update 10
pnpm self-update next-10
pnpm self-update 10.6.5
```
````

## File: docs/cli/server.md
````markdown
---
id: server
title: pnpm server
---

:::danger

Deprecated feature

:::

Manage a store server.

## Commands

### pnpm server start

Starts a server that performs all interactions with the store.
Other commands will delegate any store-related tasks to this server.

### pnpm server stop

Stops the store server.

### pnpm server status

Prints information about the running server.

## Options

### --background

* Default: **false**
* Type: **Boolean**

Runs the server in the background, similar to daemonizing on UNIX systems.

### --network-concurrency

* Default: **null**
* Type: **Number**

The maximum number of network requests to process simultaneously.

### --protocol

* Default: **auto**
* Type: **auto**, **tcp**, **ipc**

The communication protocol used by the server.
When this is set to `auto`, IPC is used on all systems except for Windows,
which uses TCP.

### --port

* Default: **5813**
* Type: **port number**

The port number to use when TCP is used for communication.
If a port is specified and the protocol is set to `auto`, regardless of system
type, the protocol is automatically set to use TCP.

### --store-dir

* Default: **&lt;home\>/.pnpm-store**
* Type: **Path**

The directory to use for the content addressable store.

### --[no-]lock

* Default: **false**
* Type: **Boolean**

Set whether to make the package store immutable to external processes while
the server is running or not.

### --ignore-stop-requests

* Default: **false**
* Type: **Boolean**

Prevents you from stopping the server using `pnpm server stop`.

### --ignore-upload-requests

* Default: **false**
* Type: **Boolean**

Prevents creating a new side effect cache during install.
````

## File: docs/cli/setup.md
````markdown
---
id: setup
title: pnpm setup
---

This command is used by the standalone installation scripts of pnpm. For instance, in [https://get.pnpm.io/install.sh].

Setup does the following actions:

* creates a home directory for the pnpm CLI
* adds the pnpm home directory to the `PATH` by updating the shell configuration file
* copies the pnpm executable to the pnpm home directory

[https://get.pnpm.io/install.sh]: https://get.pnpm.io/install.sh
````

## File: docs/cli/start.md
````markdown
---
id: start
title: pnpm start
---

Aliases: `run start`

Runs an arbitrary command specified in the package's `start` property of its
`scripts` object. If no `start` property is specified on the `scripts` object,
it will attempt to run `node server.js` as a default, failing if neither are
present.

The intended usage of the property is to specify a command that starts your
program.
````

## File: docs/cli/store.md
````markdown
---
id: store
title: pnpm store
---

Managing the package store.

## Commands

### status

Checks for modified packages in the store.

Returns exit code 0 if the content of the package is the same as it was at the
time of unpacking.

### add

Functionally equivalent to [`pnpm add`], except this adds new packages to the
store directly without modifying any projects or files outside of the store.

[`pnpm add`]: ./add.md

### prune

Removes _unreferenced packages_ from the store.

Unreferenced packages are packages that are not used by any projects on the
system. Packages can become unreferenced after most installation operations, for
instance when dependencies are made redundant.

For example, during `pnpm install`, package `foo@1.0.0` is updated to
`foo@1.0.1`. pnpm will keep `foo@1.0.0` in the store, as it does not
automatically remove packages. If package `foo@1.0.0` is not used by any other
project on the system, it becomes unreferenced. Running `pnpm store prune` would
remove `foo@1.0.0` from the store.

Running `pnpm store prune` is not harmful and has no side effects on your
projects. If future installations require removed packages, pnpm will download
them again.

It is best practice to run `pnpm store prune` occasionally to clean up the
store, but not too frequently. Sometimes, unreferenced packages become required
again. This could occur when switching branches and installing older
dependencies, in which case pnpm would need to re-download all removed packages,
briefly slowing down the installation process.

Please note that this command is prohibited when a [store server] is running.

[store server]: ./server.md

### path

Returns the path to the active store directory.
````

## File: docs/cli/test.md
````markdown
---
id: test
title: pnpm test
---

Aliases: `run test`, `t`, `tst`

Runs an arbitrary command specified in the package's `test` property of its
`scripts` object. 

The intended usage of the property is to specify a command that runs unit or
integration testing for your program.
````

## File: docs/cli/unlink.md
````markdown
---
id: unlink
title: pnpm unlink
---

Unlinks a system-wide package (inverse of [`pnpm link`](./link.md)).

If called without arguments, all linked dependencies will be unlinked inside the
current project.

This is similar to `yarn unlink`, except pnpm re-installs the dependency after
removing the external link.

:::info

If you want to remove a link made with `pnpm link --global <package>`, you should use `pnpm uninstall --global <package>`. 
`pnpm unlink` only removes the links in your current directory.

:::

## Options

### --recursive, -r

Unlink in every package found in subdirectories or in every workspace package,
when executed inside a [workspace](../workspaces.md).

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)
````

## File: docs/cli/update.md
````markdown
---
id: update
title: pnpm update
---

Aliases: `up`, `upgrade`

`pnpm update` updates packages to their latest version based on the specified
range.

When used without arguments, updates all dependencies.

## TL;DR

| Command              | Meaning                                                                  |
|----------------------|--------------------------------------------------------------------------|
|`pnpm up`             | Updates all dependencies, adhering to ranges specified in `package.json` |
|`pnpm up --latest`    | Updates all dependencies to their latest versions                        |
|`pnpm up foo@2`       | Updates `foo` to the latest version on v2                                |
|`pnpm up "@babel/*"` | Updates all dependencies under the `@babel` scope                        |

## Selecting dependencies with patterns

You can use patterns to update specific dependencies.

Update all `babel` packages:

```sh
pnpm update "@babel/*"
```

Update all dependencies, except `webpack`:

```sh
pnpm update "\!webpack"
```

Patterns may also be combined, so the next command will update all `babel` packages, except `core`:

```sh
pnpm update "@babel/*" "\!@babel/core"
```

## Options

### --recursive, -r

Concurrently runs update in all subdirectories with a `package.json` (excluding
node_modules).

Usage examples:

```sh
pnpm --recursive update
# updates all packages up to 100 subdirectories in depth
pnpm --recursive update --depth 100
# update typescript to the latest version in every package
pnpm --recursive update typescript@latest
```

### --latest, -L

Update the dependencies to their latest stable version as determined by their `latest` tags (potentially upgrading the packages across major versions) as long as the version range specified in `package.json` is lower than the `latest` tag (i.e. it will not downgrade prereleases).

### --global, -g

Update global packages.

### --workspace

Tries to link all packages from the workspace. Versions are updated to match the
versions of packages inside the workspace.

If specific packages are updated, the command will fail if any of the updated
dependencies are not found inside the workspace. For instance, the following
command fails if `express` is not a workspace package:

```sh
pnpm up -r --workspace express
```

### --prod, -P

Only update packages in `dependencies` and `optionalDependencies`.

### --dev, -D

Only update packages in `devDependencies`.

### --no-optional

Don't update packages in `optionalDependencies`.

### --interactive, -i

Show outdated dependencies and select which ones to update.

### --no-save

Don't update the ranges in `package.json`.

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)
````

## File: docs/cli/why.md
````markdown
---
id: why
title: pnpm why
---

Shows all packages that depend on the specified package.

:::caution

If the Dependencies Tree has more than 10 results (end leaves), the output will be truncated to 10 end leaves.

This makes the output more readable and avoids memory issues.

:::

## Options

### --recursive, -r

Show the dependency tree for the specified package on every package in
subdirectories or on every workspace package when executed inside a workspace.

### --json

Show information in JSON format.

### --long

Show verbose output.

### --parseable

Show parseable output instead of tree view.

### --global, -g

List packages in the global install directory instead of in the current project.

### --prod, -P

Only display the dependency tree for packages in `dependencies`.

### --dev, -D

Only display the dependency tree for packages in `devDependencies`.

### --depth &lt;number\>

Display only dependencies within a specific depth.

### --only-projects

Display only dependencies that are also projects within the workspace.

### --exclude-peers

Exclude peer dependencies from the results (but dependencies of peer dependencies are not ignored).

### --filter &lt;package_selector\>

[Read more about filtering.](../filtering.md)
````

## File: docs/settings/_catalogMode.mdx
````
### catalogMode

Added in: v10.12.1

* Default: **manual**
* Type: **manual**, **strict**, **prefer**

Controlls if and how dependencies are added to the default catalog, when running `pnpm add`. There are three modes:

- **strict** - only allows dependency versions from the catalog. Adding a dependency outside the catalog's version range will cause an error.
- **prefer** - prefers catalog versions, but will fall back to direct dependencies if no compatible version is found.
- **manual** (default) - does not automatically add dependencies to the catalog.
````

## File: docs/settings/_cpuFlag.mdx
````
### --cpu=&lt;name\>

Added in: v10.14.0

Override CPU architecture of native modules to install. Acceptable values are same as `cpu` field of `package.json`, which comes from `process.arch`.
````

## File: docs/settings/_enablePrePostScripts.mdx
````
### enablePrePostScripts

* Default: **true**
* Type: **Boolean**

When `true`, pnpm will run any pre/post scripts automatically. So running `pnpm foo`
will be like running `pnpm prefoo && pnpm foo && pnpm postfoo`.
````

## File: docs/settings/_globalPnpmfile.mdx
````
### globalPnpmfile

* Default: **null**
* Type: **path**
* Example: **~/.pnpm/global_pnpmfile.cjs**

The location of a global pnpmfile. A global pnpmfile is used by all projects
during installation.

:::note

It is recommended to use local pnpmfiles. Only use a global pnpmfile
if you use pnpm on projects that don't use pnpm as the primary package manager.

:::
````

## File: docs/settings/_ignorePnpmfile.mdx
````
### ignorePnpmfile

* Default: **false**
* Type: **Boolean**

`.pnpmfile.cjs` will be ignored. Useful together with `--ignore-scripts` when you
want to make sure that no script gets executed during install.
````

## File: docs/settings/_libcFlag.mdx
````
### --libc=&lt;name\>

Added in: v10.14.0

Override libc of native modules to install. Acceptable values are same as `libc` field of `package.json`.
````

## File: docs/settings/_osFlag.mdx
````
### --os=&lt;name\>

Added in: v10.14.0

Override OS of native modules to install. Acceptable values are same as `os` field of `package.json`, which comes from `process.platform`.
````

## File: docs/settings/_pnpmfile.mdx
````
### pnpmfile

* Default: **['.pnpmfile.cjs']**
* Type: **path[]**
* Example: **['.pnpm/.pnpmfile.cjs']**

The location of the local pnpmfile(s).
````

## File: docs/settings/_scriptShell.mdx
````
### scriptShell

* Default: **null**
* Type: **path**

The shell to use for scripts run with the `pnpm run` command.

For instance, to force usage of Git Bash on Windows:

```
pnpm config set scriptShell "C:\\Program Files\\git\\bin\\bash.exe"
```
````

## File: docs/settings/_shellEmulator.mdx
````
### shellEmulator

* Default: **false**
* Type: **Boolean**

When `true`, pnpm will use a JavaScript implementation of a [bash-like shell] to
execute scripts.

This option simplifies cross-platform scripting. For instance, by default, the
next script will fail on non-POSIX-compliant systems:

```json
"scripts": {
  "test": "NODE_ENV=test node test.js"
}
```

But if the `shellEmulator` setting is set to `true`, it will work on all
platforms.

[bash-like shell]: https://www.npmjs.com/package/@yarnpkg/shell
````

## File: docs/aliases.md
````markdown
---
id: aliases
title: Aliases
---

Aliases let you install packages with custom names.

Let's assume you use `lodash` all over your project. There is a bug in `lodash`
that breaks your project. You have a fix but `lodash` won't merge it. Normally
you would either install `lodash` from your fork directly (as a git-hosted
dependency) or publish it with a different name. If you use the second solution
you have to replace all the requires in your project with the new dependency
name (`require('lodash')` => `require('awesome-lodash')`). With aliases, you
have a third option.

Publish a new package called `awesome-lodash` and install it using `lodash` as
its alias:

```
pnpm add lodash@npm:awesome-lodash
```

No changes in code are needed. All the requires of `lodash` will now resolve to
`awesome-lodash`.

Sometimes you'll want to use two different versions of a package in your
project. Easy:

```sh
pnpm add lodash1@npm:lodash@1
pnpm add lodash2@npm:lodash@2
```

Now you can require the first version of lodash via `require('lodash1')` and the
second via `require('lodash2')`.

This gets even more powerful when combined with hooks. Maybe you want to replace
`lodash` with `awesome-lodash` in all the packages in `node_modules`. You can
easily achieve that with the following `.pnpmfile.cjs`:

```js
function readPackage(pkg) {
  if (pkg.dependencies && pkg.dependencies.lodash) {
    pkg.dependencies.lodash = 'npm:awesome-lodash@^1.0.0'
  }
  return pkg
}

module.exports = {
  hooks: {
    readPackage
  }
}
```
````

## File: docs/catalogs.md
````markdown
---
id: catalogs
title: Catalogs
---

"_Catalogs_" are a [workspace feature](./workspaces.md) for defining dependency version ranges as reusable constants. Constants defined in catalogs can later be referenced in `package.json` files.

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/PuRUk4mV2jc" title="pnpm Catalogs — A New Tool to Manage Dependencies in monorepos" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"></iframe>

## The Catalog Protocol (`catalog:`)

Once a catalog is defined in `pnpm-workspace.yaml`,

```yaml title="pnpm-workspace.yaml"
packages:
  - packages/*

# Define a catalog of version ranges.
catalog:
  react: ^18.3.1
  redux: ^5.0.1
```

The `catalog:` protocol can be used instead of the version range itself.

```json title="packages/example-app/package.json"
{
  "name": "@example/app",
  "dependencies": {
    "react": "catalog:",
    "redux": "catalog:"
  }
}
```

This is equivalent to writing a version range (e.g. `^18.3.1`) directly.

```json title="packages/example-app/package.json"
{
  "name": "@example/app",
  "dependencies": {
    "react": "^18.3.1",
    "redux": "^5.0.1"
  }
}
```

You may use the `catalog:` protocol in the next fields:

* `package.json`:
  * `dependencies`
  * `devDependencies`
  * `peerDependencies`
  * `optionalDependencies`
* `pnpm-workspace.yaml`
    * `overrides`

The `catalog:` protocol allows an optional name after the colon (ex: `catalog:name`) to specify which catalog should be used. When a name is omitted, the default catalog is used.

Depending on the scenario, the `catalog:` protocol offers a few [advantages](#advantages) compared to writing version ranges directly that are detailed next.

## Advantages

In a workspace (i.e. monorepo or multi-package repo) it's common for the same dependency to be used by many packages. Catalogs reduce duplication when authoring `package.json` files and provide a few benefits in doing so:

- **Maintain unique versions** — It's usually desirable to have only one version of a dependency in a workspace. Catalogs make this easier to maintain. Duplicated dependencies can conflict at runtime and cause bugs. Duplicates also increase size when using a bundler.
- **Easier upgrades** — When upgrading a dependency, only the catalog entry in `pnpm-workspace.yaml` needs to be edited rather than all `package.json` files using that dependency. This saves time — only one line needs to be changed instead of many.
- **Fewer merge conflicts** — Since `package.json` files do not need to be edited when upgrading a dependency, git merge conflicts no longer happen in these files.

## Defining Catalogs

Catalogs are defined in the `pnpm-workspace.yaml` file. There are two ways to define catalogs.

1. Using the (singular) `catalog` field to create a catalog named `default`.
2. Using the (plural) `catalogs` field to create arbitrarily named catalogs.

:::tip

If you have an existing workspace that you want to migrate to using catalogs, you can use the following [codemod](https://go.codemod.com/pnpm-catalog):

```
pnpx codemod pnpm/catalog
```

:::

### Default Catalog

The top-level `catalog` field allows users to define a catalog named `default`.

```yaml title="pnpm-workspace.yaml"
catalog:
  react: ^18.2.0
  react-dom: ^18.2.0
```

These version ranges can be referenced through `catalog:default`. For the default catalog only, a special `catalog:` shorthand can also be used. Think of `catalog:` as a shorthand that expands to `catalog:default`.

### Named Catalogs

Multiple catalogs with arbitrarily chosen names can be configured under the `catalogs` key.

```yaml title="pnpm-workspace.yaml"
catalogs:
  # Can be referenced through "catalog:react17"
  react17:
    react: ^17.0.2
    react-dom: ^17.0.2

  # Can be referenced through "catalog:react18"
  react18:
    react: ^18.2.0
    react-dom: ^18.2.0
```

A default catalog can be defined alongside multiple named catalogs. This might be useful in a large multi-package repo that's migrating to a newer version of a dependency piecemeal.

```yaml title="pnpm-workspace.yaml"
catalog:
  react: ^16.14.0
  react-dom: ^16.14.0

catalogs:
  # Can be referenced through "catalog:react17"
  react17:
    react: ^17.0.2
    react-dom: ^17.0.2

  # Can be referenced through "catalog:react18"
  react18:
    react: ^18.2.0
    react-dom: ^18.2.0
```

## Publishing

The `catalog:` protocol is removed when running `pnpm publish` or `pnpm pack`. This is similar to the [`workspace:` protocol](./workspaces.md#workspace-protocol-workspace), which is [also replaced on publish](./workspaces.md#publishing-workspace-packages).

For example,

```json title="packages/example-components/package.json"
{
  "name": "@example/components",
  "dependencies": {
    "react": "catalog:react18",
  }
}
```

Will become the following on publish.

```json title="packages/example-components/package.json"
{
  "name": "@example/components",
  "dependencies": {
    "react": "^18.3.1",
  }
}
```

The `catalog:` protocol replacement process allows the `@example/components` package to be used by other workspaces or package managers.

## Settings

import CatalogMode from './settings/_catalogMode.mdx'

<CatalogMode />
````

## File: docs/completion.md
````markdown
---
id: completion
title: Command line tab-completion
---

:::info

Completion for pnpm v9+ is incompatible with completion for older pnpm versions.
If you have already installed pnpm completion for a version older than v9, you must uninstall it first to ensure that completion for v9+ works properly.
You can do this by removing the section of code that contains `__tabtab` in your dot files.

:::

Unlike other popular package managers, which usually require plugins, pnpm
supports command line tab-completion for Bash, Zsh, Fish, and similar shells.

To setup autocompletion for Bash, run:

```text
pnpm completion bash > ~/completion-for-pnpm.bash
echo 'source ~/completion-for-pnpm.bash' >> ~/.bashrc
```

To setup autocompletion for Fish, run:

```text
pnpm completion fish > ~/.config/fish/completions/pnpm.fish
```

## g-plane/pnpm-shell-completion

[pnpm-shell-completion] is a shell plugin maintained by Pig Fang on Github.

Features:

- Provide completion for `pnpm --filter <package>`.
- Provide completion for `pnpm remove` command, even in workspace's packages (by specifying `--filter` option).
- Provide completion for scripts in `package.json`.

[pnpm-shell-completion]: https://github.com/g-plane/pnpm-shell-completion
````

## File: docs/config-dependencies.md
````markdown
---
id: config-dependencies
title: Config Dependencies
---

Config dependencies allow you to share and centralize configuration files, settings, and hooks across multiple projects. They are installed before all regular dependencies ("dependencies", "devDependencies", "optionalDependencies"), making them ideal for setting up custom hooks, patches, and catalog entries.

Config dependencies help you keep all the hooks, settings, patches, overrides, catalogs, rules in a single place and use them across multiple repositories.

If your config dependency is named following the `pnpm-plugin-*` pattern, pnpm will automatically load the `pnpmfile.cjs` from its root.

## How to Add a Config Dependency

Config dependencies are defined in your `pnpm-workspace.yaml` and must be installed using an exact version and an integrity checksum.

Example:

```yaml title="pnpm-workspace.yaml"
configDependencies:
  my-configs: "1.0.0+sha512-30iZtAPgz+LTIYoeivqYo853f02jBYSd5uGnGpkFV0M3xOt9aN73erkgYAmZU43x4VfqcnLxW9Kpg3R5LC4YYw=="
```

**Important:**

* Config dependencies **cannot** have their own dependencies.
* Config dependencies **cannot** define lifecycle scripts (like `preinstall`, `postinstall`, etc.).

## Usage

### Loading an Allow List of Built Dependencies

You can load a list of package names that are allowed to be built, using the [`onlyBuiltDependenciesFile`] setting.

Example `allow.json` file inside a config dependency ([@pnpm/trusted-deps]):

```json title="allow.json"
[
  "@airbnb/node-memwatch",
  "@apollo/protobufjs",
  ...
]
```

Your workspace configuration:

```yaml title="pnpm-workspace.yaml"
configDependencies:
  '@pnpm/trusted-deps': 0.1.0+sha512-IERT0uXPBnSZGsCmoSuPzYNWhXWWnKkuc9q78KzLdmDWJhnrmvc7N4qaHJmaNKIusdCH2riO3iE34Osohj6n8w==
onlyBuiltDependenciesFile: node_modules/.pnpm-config/@pnpm/trusted-deps/allow.json
```

[@pnpm/trusted-deps]: https://github.com/pnpm/trusted-deps
[`onlyBuiltDependenciesFile`]: settings.md#onlybuiltdependenciesfile

### Installing Dependencies Used in Hooks

Config dependencies are installed **before** hooks from your [`.pnpmfile.cjs`] are loaded, allowing you to import logic from config packages.

Example:

```js title=".pnpmfile.cjs"
const { readPackage } = require('.pnpm-config/my-hooks')

module.exports = {
  hooks: {
    readPackage
  }
}
```

[`.pnpmfile.cjs`]: ./pnpmfile.md

### Updating pnpm Settings Dynamically

Using the [`updateConfig`] hook, you can dynamically update pnpm’s settings using config dependencies.

For example, the following `pnpmfile` adds a new [catalog] entry to pnpm's configuration:

```js title="my-catalogs/pnpmfile.cjs"
module.exports = {
  hooks: {
    updateConfig (config) {
      config.catalogs.default ??= {}
      config.catalogs.default['is-odd'] = '1.0.0'
      return config
    }
  }
}
```

Install and load it:

```yaml title="pnpm-workspace.yaml"
configDependencies:
  my-catalogs: "1.0.0+sha512-30iZtAPgz+LTIYoeivqYo853f02jBYSd5uGnGpkFV0M3xOt9aN73erkgYAmZU43x4VfqcnLxW9Kpg3R5LC4YYw=="
pnpmfile: "node_modules/.pnpm-config/my-catalogs/pnpmfile.cjs"
```

Then you can run:

```
pnpm add is-odd@catalog:
```

This will install `is-odd@1.0.0` and add the following to your `package.json`:

```json
{
  "dependencies": {
    "is-odd": "catalog:"
  }
}
```

This makes it easy to maintain and share centralized configuration and dependency versions across projects.

[`updateConfig`]: ./pnpmfile.md#hooksupdateconfigconfig-config--promiseconfig
[catalog]: ./catalogs.md

### Loading Patch Files

You can reference [patch files] stored inside config dependencies.

Example:

```yaml title="pnpm-workspace.yaml"
configDependencies:
  my-patches: "1.0.0+sha512-30iZtAPgz+LTIYoeivqYo853f02jBYSd5uGnGpkFV0M3xOt9aN73erkgYAmZU43x4VfqcnLxW9Kpg3R5LC4YYw=="
patchedDependencies:
  react: "node_modules/.pnpm-config/my-patches/react.patch"
```

[patch files]: ./cli/patch.md
````

## File: docs/configuring.md
````markdown
---
id: configuring
title: Configuring
---

pnpm uses [npm's configuration] formats. Hence, you should set configuration
the same way you would for npm. For example,

```
pnpm config set store-dir /path/to/.pnpm-store
```

If no store is configured, then pnpm will automatically create a store on the
same drive. If you need pnpm to work across multiple hard drives or filesystems,
please read [the FAQ].

Furthermore, pnpm uses the same configuration that npm uses for doing
installations. If you have a private registry and npm is configured to work with
it, pnpm should be able to authorize requests as well, with no additional
configuration.

In addition to those options, pnpm also allows you to use all parameters that
are flags (for example `--filter` or `--workspace-concurrency`) as options:

```
workspace-concurrency = 1
filter = @my-scope/*
```

See the [`config` command] for more information.

[npm's configuration]: https://docs.npmjs.com/misc/config
[the FAQ]: ./faq.md#does-pnpm-work-across-multiple-drives-or-filesystems
[`config` command]: ./cli/config.md
````

## File: docs/continuous-integration.md
````markdown
---
id: continuous-integration
title: Continuous Integration
---

pnpm can easily be used in various continuous integration systems.

:::note

In all the provided configuration files the store is cached. However, this is not required, and it is not guaranteed that caching the store will make installation faster. So feel free to not cache the pnpm store in your job.

:::

## AppVeyor

On [AppVeyor], you can use pnpm for installing your dependencies by adding this
to your `appveyor.yml`:

```yaml title="appveyor.yml"
install:
  - ps: Install-Product node $env:nodejs_version
  - npm install --global corepack@latest
  - corepack enable
  - corepack prepare pnpm@latest-10 --activate
  - pnpm install
```

[AppVeyor]: https://www.appveyor.com

## Azure Pipelines

On Azure Pipelines, you can use pnpm for installing and caching your dependencies by adding this to your `azure-pipelines.yml`:

```yaml title="azure-pipelines.yml"
variables:
  pnpm_config_cache: $(Pipeline.Workspace)/.pnpm-store

steps:
  - task: Cache@2
    inputs:
      key: 'pnpm | "$(Agent.OS)" | pnpm-lock.yaml'
      path: $(pnpm_config_cache)
    displayName: Cache pnpm

  - script: |
      npm install --global corepack@latest
      corepack enable
      corepack prepare pnpm@latest-10 --activate
      pnpm config set store-dir $(pnpm_config_cache)
    displayName: "Setup pnpm"

  - script: |
      pnpm install
      pnpm run build
    displayName: "pnpm install and build"
```

## Bitbucket Pipelines

You can use pnpm for installing and caching your dependencies:

```yaml title=".bitbucket-pipelines.yml"
definitions:
  caches:
    pnpm: $BITBUCKET_CLONE_DIR/.pnpm-store

pipelines:
  pull-requests:
    "**":
      - step:
          name: Build and test
          image: node:18.17.1
          script:
            - npm install --global corepack@latest
            - corepack enable
            - corepack prepare pnpm@latest-10 --activate
            - pnpm install
            - pnpm run build # Replace with your build/test…etc. commands
          caches:
            - pnpm
```

## CircleCI

On CircleCI, you can use pnpm for installing and caching your dependencies by adding this to your `.circleci/config.yml`:

```yaml title=".circleci/config.yml"
version: 2.1

jobs:
  build: # this can be any name you choose
    docker:
      - image: node:18
    resource_class: large
    parallelism: 10

    steps:
      - checkout
      - restore_cache:
          name: Restore pnpm Package Cache
          keys:
            - pnpm-packages-{{ checksum "pnpm-lock.yaml" }}
      - run:
          name: Install pnpm package manager
          command: |
            npm install --global corepack@latest
            corepack enable
            corepack prepare pnpm@latest-10 --activate
            pnpm config set store-dir .pnpm-store
      - run:
          name: Install Dependencies
          command: |
            pnpm install
      - save_cache:
          name: Save pnpm Package Cache
          key: pnpm-packages-{{ checksum "pnpm-lock.yaml" }}
          paths:
            - .pnpm-store
```

## GitHub Actions

On GitHub Actions, you can use pnpm for installing and caching your dependencies
like so (belongs in `.github/workflows/NAME.yml`):

```yaml title=".github/workflows/NAME.yml"
name: pnpm Example Workflow
on:
  push:

jobs:
  build:
    runs-on: ubuntu-22.04
    strategy:
      matrix:
        node-version: [20]
    steps:
      - uses: actions/checkout@v4
      - name: Install pnpm
        uses: pnpm/action-setup@v4
        with:
          version: 10
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: "pnpm"
      - name: Install dependencies
        run: pnpm install
```

## GitLab CI

On GitLab, you can use pnpm for installing and caching your dependencies
like so (belongs in `.gitlab-ci.yml`):

```yaml title=".gitlab-ci.yml"
stages:
  - build

build:
  stage: build
  image: node:18.17.1
  before_script:
    - npm install --global corepack@latest
    - corepack enable
    - corepack prepare pnpm@latest-10 --activate
    - pnpm config set store-dir .pnpm-store
  script:
    - pnpm install # install dependencies
  cache:
    key:
      files:
        - pnpm-lock.yaml
    paths:
      - .pnpm-store
```

## Jenkins

You can use pnpm for installing and caching your dependencies:

```title="Jenkinsfile"
pipeline {
    agent {
        docker {
            image 'node:lts-bullseye-slim'
            args '-p 3000:3000'
        }
    }
    stages {
        stage('Build') {
            steps {
                sh 'npm install --global corepack@latest'
                sh 'corepack enable'
                sh 'corepack prepare pnpm@latest-10 --activate'
                sh 'pnpm install'
            }
        }
    }
}
```

## Semaphore

On [Semaphore], you can use pnpm for installing and caching your dependencies by
adding this to your `.semaphore/semaphore.yml` file:

```yaml title=".semaphore/semaphore.yml"
version: v1.0
name: Semaphore CI pnpm example
agent:
  machine:
    type: e1-standard-2
    os_image: ubuntu1804
blocks:
  - name: Install dependencies
    task:
      jobs:
        - name: pnpm install
          commands:
            - npm install --global corepack@latest
            - corepack enable
            - corepack prepare pnpm@latest-10 --activate
            - checkout
            - cache restore node-$(checksum pnpm-lock.yaml)
            - pnpm install
            - cache store node-$(checksum pnpm-lock.yaml) $(pnpm store path)
```

[Semaphore]: https://semaphoreci.com

## Travis

On [Travis CI], you can use pnpm for installing your dependencies by adding this
to your `.travis.yml` file:

```yaml title=".travis.yml"
cache:
  npm: false
  directories:
    - "~/.pnpm-store"
before_install:
  - npm install --global corepack@latest
  - corepack enable
  - corepack prepare pnpm@latest-10 --activate
  - pnpm config set store-dir ~/.pnpm-store
install:
  - pnpm install
```

[Travis CI]: https://travis-ci.org
````

## File: docs/docker.md
````markdown
---
id: docker
title: Working with Docker
---

:::note

It is impossible to create reflinks or hardlinks between a Docker container and the host filesystem during build time.
The next best thing you can do is using BuildKit cache mount to share cache between builds. Alternatively, you may use
[podman] because it can mount Btrfs volumes during build time.

:::

[podman]: ./podman.md

## Minimizing Docker image size and build time

* Use a small image, e.g. `node:XX-slim`.
* Leverage multi-stage if possible and makes sense.
* Leverage BuildKit cache mounts.

### Example 1: Build a bundle in a Docker container

Since `devDependencies` is only necessary for building the bundle, `pnpm install --prod` will be a separate stage
from `pnpm install` and `pnpm run build`, allowing the final stage to copy only necessary files from the earlier
stages, minimizing the size of the final image.

```text title=".dockerignore"
node_modules
.git
.gitignore
*.md
dist
```

```dockerfile title="Dockerfile"
FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable
COPY . /app
WORKDIR /app

FROM base AS prod-deps
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --prod --frozen-lockfile

FROM base AS build
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
RUN pnpm run build

FROM base
COPY --from=prod-deps /app/node_modules /app/node_modules
COPY --from=build /app/dist /app/dist
EXPOSE 8000
CMD [ "pnpm", "start" ]
```

### Example 2: Build multiple Docker images in a monorepo

Assuming you have a monorepo with 3 packages: app1, app2, and common; app1 and app2 depend on common but not each other.

You want to save only necessary dependencies for each package, `pnpm deploy` should help you with copying only necessary files and packages.

```text title="Structure of the monorepo"
./
├── Dockerfile
├── .dockerignore
├── .gitignore
├── packages/
│   ├── app1/
│   │   ├── dist/
│   │   ├── package.json
│   │   ├── src/
│   │   └── tsconfig.json
│   ├── app2/
│   │   ├── dist/
│   │   ├── package.json
│   │   ├── src/
│   │   └── tsconfig.json
│   └── common/
│       ├── dist/
│       ├── package.json
│       ├── src/
│       └── tsconfig.json
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
└── tsconfig.json
```

```yaml title="pnpm-workspace.yaml"
packages:
  - 'packages/*'
syncInjectedDepsAfterScripts:
- build
injectWorkspacePackages: true
```

```text title=".dockerignore"
node_modules
.git
.gitignore
*.md
dist
```

```dockerfile title="Dockerfile"
FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

FROM base AS build
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
RUN pnpm run -r build
RUN pnpm deploy --filter=app1 --prod /prod/app1
RUN pnpm deploy --filter=app2 --prod /prod/app2

FROM base AS app1
COPY --from=build /prod/app1 /prod/app1
WORKDIR /prod/app1
EXPOSE 8000
CMD [ "pnpm", "start" ]

FROM base AS app2
COPY --from=build /prod/app2 /prod/app2
WORKDIR /prod/app2
EXPOSE 8001
CMD [ "pnpm", "start" ]
```

Run the following commands to build images for app1 and app2:

```sh
docker build . --target app1 --tag app1:latest
docker build . --target app2 --tag app2:latest
```

### Example 3: Build on CI/CD

On CI or CD environments, the BuildKit cache mounts might not be available, because the VM or container is ephemeral and only normal docker cache will work.

So an alternative is to use a typical Dockerfile with layers that are built incrementally, for this scenario, `pnpm fetch` is the best option, as it only needs the `pnpm-lock.yaml` file and the layer cache will only be lost when you change the dependencies.

```dockerfile title="Dockerfile"
FROM node:20-slim AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

FROM base AS prod

COPY pnpm-lock.yaml /app
WORKDIR /app
RUN pnpm fetch --prod

COPY . /app
RUN pnpm run build

FROM base
COPY --from=prod /app/node_modules /app/node_modules
COPY --from=prod /app/dist /app/dist
EXPOSE 8000
CMD [ "pnpm", "start" ]
```
````

## File: docs/errors.md
````markdown
---
id: errors
title: Error Codes
---

## ERR_PNPM_UNEXPECTED_STORE

A modules directory is present and is linked to a different store directory.

If you changed the store directory intentionally, run `pnpm install` and pnpm will reinstall the dependencies using the new store.

## ERR_PNPM_NO_MATCHING_VERSION_INSIDE_WORKSPACE

A project has a workspace dependency that does not exist in the workspace.

For instance, package `foo` has `bar@1.0.0` in the `dependencies`:

```json
{
  "name": "foo",
  "version": "1.0.0",
  "dependencies": {
    "bar": "workspace:1.0.0"
  }
}
```

However, there is only `bar@2.0.0` in the workspace, so `pnpm install` will fail.

To fix this error, all dependencies that use the [workspace protocol] should be updated to use versions of packages that are present in the workspace. This can be done either manually or using the `pnpm -r update` command.

[workspace protocol]: ./workspaces.md#workspace-protocol-workspace

## ERR_PNPM_PEER_DEP_ISSUES

`pnpm install` will fail if the project has unresolved peer dependencies or the peer dependencies are not matching the wanted ranges. To fix this, install the missing peer dependencies.

You may also selectively ignore these errors using the [peerDependencyRules.ignoreMissing] and [peerDependencyRules.allowedVersions] settings.

[peerDependencyRules.ignoreMissing]: settings#peerdependencyrulesignoremissing
[peerDependencyRules.allowedVersions]: settings#peerdependencyrulesallowedversions

## ERR_PNPM_OUTDATED_LOCKFILE

This error happens when installation cannot be performed without changes to the lockfile. This might happen in a CI environment if someone has changed a `package.json` file in the repository without running `pnpm install` afterwards. Or someone forgot to commit the changes to the lockfile.

To fix this error, just run `pnpm install` and commit the changes to the lockfile.

## ERR\_PNPM\_TARBALL\_INTEGRITY

This error indicates that the downloaded package's tarball did not match the expected integrity checksum.

If you use the npm registry (`registry.npmjs.org`), then this probably means that the integrity in your lockfile is incorrect.
This might happen if a lockfile had badly resolved merge conflicts.

If you use a registry that allows to override existing versions of a package, then it might mean that in your local metadata cache you have the integrity checksum of an older version of the package. In this case, you should run `pnpm store prune`. This command will remove your local metadata cache. Then you can retry the command that failed.

But also be careful and verify that the package is downloaded from the right URL. The URL should be printed in the error message.

## ERR_PNPM_MISMATCHED_RELEASE_CHANNEL

The config field `use-node-version` defines a release channel different from version suffix.

For example:
* `rc/20.0.0` defines an `rc` channel but the version is that of a stable release.
* `release/20.0.0-rc.0` defines a `release` channel but the version is that of an RC release.

To fix this error, either remove the release channel prefix or correct the version suffix.

Note that it is not allowed to specify node versions like `lts/Jod`.
The correct syntax for stable release is strictly X.Y.Z or release/X.Y.Z.

## ERR_PNPM_INVALID_NODE_VERSION

The value of config field `use-node-version` has an invalid syntax.

Below are the valid forms of `use-node-version`:
* Stable release:
  * `X.Y.Z` (`X`, `Y`, `Z` are integers)
  * `release/X.Y.Z` (`X`, `Y`, `Z` are integers)
* RC release:
  * `X.Y.Z-rc.W` (`X`, `Y`, `Z`, `W` are integers)
  * `rc/X.Y.Z-rc.W` (`X`, `Y`, `Z`, `W` are integers)
````

## File: docs/faq.md
````markdown
---
id: faq
title: Frequently Asked Questions
---

## Why does my `node_modules` folder use disk space if packages are stored in a global store?

pnpm creates [hard links] from the global store to the project's `node_modules`
folders. Hard links point to the same place on the disk where the original
files are. So, for example, if you have `foo` in your project as a dependency
and it occupies 1MB of space, then it will look like it occupies 1MB of space in
the project's `node_modules` folder and the same amount of space in the global
store. However, that 1MB is *the same space* on the disk addressed from two
different locations. So in total `foo` occupies 1MB, not 2MB.

[hard links]: https://en.wikipedia.org/wiki/Hard_link

For more on this subject:

* [Why do hard links seem to take the same space as the originals?](https://unix.stackexchange.com/questions/88423/why-do-hard-links-seem-to-take-the-same-space-as-the-originals)
* [A thread from the pnpm chat room](https://gist.github.com/zkochan/106cfef49f8476b753a9cbbf9c65aff1)
* [An issue in the pnpm repo](https://github.com/pnpm/pnpm/issues/794)

## Does it work on Windows?

Short answer: Yes.
Long answer: Using symbolic linking on Windows is problematic to say the least,
however, pnpm has a workaround. For Windows, we use [junctions] instead.

[junctions]: https://docs.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions

## But the nested `node_modules` approach is incompatible with Windows?

Early versions of npm had issues because of nesting all `node_modules` (see
[this issue]). However, pnpm does not create deep folders, it stores all packages
flatly and uses symbolic links to create the dependency tree structure.

[this issue]: https://github.com/nodejs/node-v0.x-archive/issues/6960

## What about circular symlinks?

Although pnpm uses linking to put dependencies into `node_modules` folders,
circular symlinks are avoided because parent packages are placed into the same
`node_modules` folder in which their dependencies are. So `foo`'s dependencies
are not in `foo/node_modules`, but `foo` is in `node_modules` together with its
own dependencies.

## Why have hard links at all? Why not symlink directly to the global store?

One package can have different sets of dependencies on one machine.

In project **A** `foo@1.0.0` can have a dependency resolved to `bar@1.0.0`, but
in project **B** the same dependency of `foo` might resolve to `bar@1.1.0`; so,
pnpm hard links `foo@1.0.0` to every project where it is used, in order to
create different sets of dependencies for it.

Direct symlinking to the global store would work with Node's
`--preserve-symlinks` flag, however, that approach comes with a plethora of its
own issues, so we decided to stick with hard links. For more details about why
this decision was made, see [this issue][eps-issue].

[eps-issue]: https://github.com/nodejs/node-eps/issues/46

## Does pnpm work across different subvolumes in one Btrfs partition?

While Btrfs does not allow cross-device hardlinks between different subvolumes in a single partition, it does permit reflinks. As a result, pnpm utilizes reflinks to share data between these subvolumes.

## Does pnpm work across multiple drives or filesystems?

The package store should be on the same drive and filesystem as installations,
otherwise packages will be copied, not linked. This is due to a limitation in
how hard linking works, in that a file on one filesystem cannot address a
location in another. See [Issue #712] for more details.

pnpm functions differently in the 2 cases below:

[Issue #712]: https://github.com/pnpm/pnpm/issues/712

### Store path is specified

If the store path is specified via [the store config](configuring.md), then copying
occurs between the store and any projects that are on a different disk.

If you run `pnpm install` on disk `A`, then the pnpm store must be on disk `A`.
If the pnpm store is located on disk `B`, then all required packages will be
directly copied to the project location instead of being linked. This severely
inhibits the storage and performance benefits of pnpm.

### Store path is NOT specified

If the store path is not set, then multiple stores are created (one per drive or
filesystem).

If installation is run on disk `A`, the store will be created on `A`
`.pnpm-store` under the filesystem root.  If later the installation is run on
disk `B`, an independent store will be created on `B` at `.pnpm-store`. The
projects would still maintain the benefits of pnpm, but each drive may have
redundant packages.

## What does `pnpm` stand for?

`pnpm` stands for `performant npm`.
[@rstacruz](https://github.com/rstacruz/) came up with the name.

## `pnpm` does not work with &lt;YOUR-PROJECT-HERE>?

In most cases it means that one of the dependencies require packages not
declared in `package.json`. It is a common mistake caused by flat
`node_modules`. If this happens, this is an error in the dependency and the
dependency should be fixed. That might take time though, so pnpm supports
workarounds to make the buggy packages work.

### Solution 1

In case there are issues, you can use the [`nodeLinker: hoisted`] setting.
This creates a flat `node_modules` structure similar to the one created by `npm`.

[`nodeLinker: hoisted`]: settings#nodeLinker

### Solution 2

In the following example, a dependency does **not** have the `iterall` module in
its own list of deps.

The easiest solution to resolve missing dependencies of the buggy packages is to
**add `iterall` as a dependency to our project's `package.json`**.

You can do so, by installing it via `pnpm add iterall`, and will be
automatically added to your project's `package.json`.

```json
  "dependencies": {
    ...
    "iterall": "^1.2.2",
    ...
  }
```

### Solution 3

One of the solutions is to use [hooks](pnpmfile.md#hooks) for adding the missing
dependencies to the package's `package.json`.

An example was [Webpack Dashboard] which wasn't working with `pnpm`. It has
since been resolved such that it works with `pnpm` now.

It used to throw an error:

```console
Error: Cannot find module 'babel-traverse'
  at /node_modules/inspectpack@2.2.3/node_modules/inspectpack/lib/actions/parse
```

The problem was that `babel-traverse` was used in `inspectpack` which
was used by `webpack-dashboard`, but `babel-traverse` wasn't specified in
`inspectpack`'s `package.json`. It still worked with `npm` and `yarn` because
they create flat `node_modules`.

The solution was to create a `.pnpmfile.cjs` with the following contents:

```js
module.exports = {
  hooks: {
    readPackage: (pkg) => {
      if (pkg.name === "inspectpack") {
        pkg.dependencies['babel-traverse'] = '^6.26.0';
      }
      return pkg;
    }
  }
};
```

After creating a `.pnpmfile.cjs`, delete `pnpm-lock.yaml` only - there is no need
to delete `node_modules`, as pnpm hooks only affect module resolution. Then,
rebuild the dependencies & it should be working.

[Webpack Dashboard]: https://github.com/pnpm/pnpm/issues/1043
````

## File: docs/feature-comparison.md
````markdown
---
id: feature-comparison
title: Feature Comparison
---

| Feature                          |pnpm              |Yarn              |npm               | Notes |
| ---                              |:--:              |:--:              |:--:              | ---   |
| [Workspace support]              |:white_check_mark:|:white_check_mark:|:white_check_mark:|
| Isolated `node_modules`          |:white_check_mark:|:white_check_mark:|:white_check_mark:| Default in pnpm. |
| [Hoisted `node_modules`]         |:white_check_mark:|:white_check_mark:|:white_check_mark:| Default in npm. |
| Plug'n'Play                      |:white_check_mark:|:white_check_mark:|:x:               | Default in Yarn. |
| [Autoinstalling peers]           |:white_check_mark:|:x:               |:white_check_mark:|
| Zero-Installs                    |:x:               |:white_check_mark:|:x:               |
| [Patching dependencies]          |:white_check_mark:|:white_check_mark:|:x:               |
| [Managing Node.js versions]      |:white_check_mark:|:x:               |:x:               |
| [Managing versions of itself]    |:white_check_mark:|:white_check_mark:|:x:               |
| Has a lockfile                   |:white_check_mark:|:white_check_mark:|:white_check_mark:| `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`. |
| [Overrides support]              |:white_check_mark:|:white_check_mark:|:white_check_mark:| Known as "resolutions" in Yarn. |
| Content-addressable storage      |:white_check_mark:|:white_check_mark:|:x:               | Yarn uses a CAS when `nodeLinker` is set to `pnpm`. |
| [Dynamic package execution]      |:white_check_mark:|:white_check_mark:|:white_check_mark:| `pnpm dlx`, `yarn dlx`, `npx`. |
| [Side-effects cache]             |:white_check_mark:|:x:               |:x:               |
| [Catalogs]                       |:white_check_mark:|:x:               |:x:               |
| [Config dependencies]            |:white_check_mark:|:x:               |:x:               |
| [JSR registry support]           |:white_check_mark:|:white_check_mark:|:x:               |
| [Auto-install before script run] |:white_check_mark:|:x:               |:x:               | In Yarn, Plug'n'Play ensures dependencies are always up to date. |
| [Hooks]                          |:white_check_mark:|:white_check_mark:|:x:               |
| [Listing licenses]               |:white_check_mark:|:white_check_mark:|:x:               | pnpm supports it via `pnpm licenses list`. Yarn has a plugin for it. |

[Auto-install before script run]: ./settings.md#verifydepsbeforerun
[Autoinstalling peers]: ./settings.md#autoinstallpeers
[Catalogs]: ./catalogs.md
[Config dependencies]: ./config-dependencies.md
[Dynamic package execution]: ./cli/dlx.md
[Hoisted `node_modules`]: ./settings.md#nodelinker
[JSR registry support]: ./cli/add.md#install-from-the-jsr-registry
[Listing licenses]: ./cli/licenses.md
[Managing Node.js versions]: ./cli/env.md
[Managing versions of itself]: ./settings.md#managepackagemanagerversions
[Overrides support]: ./settings.md#overrides
[Patching dependencies]: ./cli/patch.md
[Side-effects cache]: ./settings.md#sideeffectscache
[Workspace support]: ./workspaces.md
[hooks]: ./pnpmfile.md

**Note:** To keep the comparison concise, we include only features likely to be used frequently.
````

## File: docs/filtering.md
````markdown
---
id: filtering
title: Filtering
---

Filtering allows you to restrict commands to specific subsets of packages.

pnpm supports a rich selector syntax for picking packages by name or by
relation.

Selectors may be specified via the `--filter` (or `-F`) flag:

```sh
pnpm --filter <package_selector> <command>
```

## Matching

### --filter &lt;package_name>

To select an exact package, just specify its name (`@scope/pkg`) or use a
pattern to select a set of packages (`@scope/*`).

Examples:

```sh
pnpm --filter "@babel/core" test
pnpm --filter "@babel/*" test
pnpm --filter "*core" test
```

Specifying the scope of the package is optional, so `--filter=core` will pick `@babel/core` if `core` is not found.
However, if the workspace has multiple packages with the same name (for instance, `@babel/core` and `@types/core`),
then filtering without scope will pick nothing.

### --filter &lt;package_name>...

To select a package and its dependencies (direct and non-direct), suffix the
package name with an ellipsis: `<package_name>...`. For instance, the next
command will run tests of `foo` and all of its dependencies:

```sh
pnpm --filter foo... test
```

You may use a pattern to select a set of root packages:

```sh
pnpm --filter "@babel/preset-*..." test
```

### --filter &lt;package_name>^...

To ONLY select the dependencies of a package (both direct and non-direct),
suffix the name with the aforementioned ellipsis preceded by a chevron. For
instance, the next command will run tests for all of `foo`'s
dependencies:

```sh
pnpm --filter "foo^..." test
```

### --filter ...&lt;package_name>

To select a package and its dependent packages (direct and non-direct), prefix
the package name with an ellipsis: `...<package_name>`. For instance, this will
run the tests of `foo` and all packages dependent on it:

```sh
pnpm --filter ...foo test
```

### --filter "...^&lt;package_name>"

To ONLY select a package's dependents (both direct and non-direct), prefix the
package name with an ellipsis followed by a chevron. For instance, this will
run tests for all packages dependent on `foo`:

```text
pnpm --filter "...^foo" test
```

### --filter `./<glob>`, --filter `{<glob>}`

A glob pattern relative to the current working directory matching projects.

```sh
pnpm --filter "./packages/**" <cmd>
```

Includes all projects that are under the specified directory.

It may be used with the ellipsis and chevron operators to select
dependents/dependencies as well:

```sh
pnpm --filter ...{<directory>} <cmd>
pnpm --filter {<directory>}... <cmd>
pnpm --filter ...{<directory>}... <cmd>
```

It may also be combined with `[<since>]`. For instance, to select all changed
projects inside a directory:

```sh
pnpm --filter "{packages/**}[origin/master]" <cmd>
pnpm --filter "...{packages/**}[origin/master]" <cmd>
pnpm --filter "{packages/**}[origin/master]..." <cmd>
pnpm --filter "...{packages/**}[origin/master]..." <cmd>
```

Or you may select all packages from a directory with names matching the given
pattern:

```text
pnpm --filter "@babel/*{components/**}" <cmd>
pnpm --filter "@babel/*{components/**}[origin/master]" <cmd>
pnpm --filter "...@babel/*{components/**}[origin/master]" <cmd>
```

### --filter "[&lt;since>]"

Selects all the packages changed since the specified commit/branch. May be
suffixed or prefixed with `...` to include dependencies/dependents.

For example, the next command will run tests in all changed packages since
`master` and on any dependent packages:

```sh
pnpm --filter "...[origin/master]" test
```

### --fail-if-no-match

Use this flag if you want the CLI to fail if no packages have matched the filters.

## Excluding

Any of the filter selectors may work as exclusion operators when they have a
leading "!". In zsh (and possibly other shells), "!" should be escaped: `\!`.

For instance, this will run a command in all projects except for `foo`:

```sh
pnpm --filter=!foo <cmd>
```

And this will run a command in all projects that are not under the `lib`
directory:

```sh
pnpm --filter=!./lib <cmd>
```

## Multiplicity

When packages are filtered, every package is taken that matches at least one of
the selectors. You can use as many filters as you want:

```sh
pnpm --filter ...foo --filter bar --filter baz... test
```

## --filter-prod &lt;filtering_pattern>

Acts the same a `--filter` but omits `devDependencies` when selecting dependency projects
from the workspace.

## --test-pattern &lt;glob>

`test-pattern` allows detecting whether the modified files are related to tests.
If they are, the dependent packages of such modified packages are not included.

This option is useful with the "changed since" filter. For instance, the next
command will run tests in all changed packages, and if the changes are in the
source code of the package, tests will run in the dependent packages as well:

```sh
pnpm --filter="...[origin/master]" --test-pattern="test/*" test
```

## --changed-files-ignore-pattern &lt;glob>

Allows to ignore changed files by glob patterns when filtering for changed projects since the specified commit/branch.

Usage example:

```sh
pnpm --filter="...[origin/master]" --changed-files-ignore-pattern="**/README.md" run build
```
````

## File: docs/git_branch_lockfiles.md
````markdown
---
id: git_branch_lockfiles
title: Git Branch Lockfiles
---

Git branch lockfiles allows you to totally avoid lockfile merge conflicts and solve it later.

## Use git branch lockfiles

You can turn on this feature by configuring the `pnpm-workspace.yaml` file.

```yaml
gitBranchLockfile: true
```

By doing this, lockfile name will be generated based on the current branch name.

For instance, the current branch name is `feature-1`. Then, the generated lockfile name will
be `pnpm-lock.feature-1.yaml`. You can commit it to the Git, and merge all git branch lockfiles later.

```
- <project_folder>
|- pnpm-lock.yaml
|- pnpm-lock.feature-1.yaml
|- pnpm-lock.<branch_name>.yaml
```

:::note

`feature/1` is special in that the `/` is automatically converted to `!`, so the corresponding
lockfile name would be `pnpm-lock.feature!1.yaml`.

:::

## Merge git branch lockfiles

### `pnpm install --merge-git-branch-lockfiles`

To merge all git branch lockfiles, just specify `--merge-git-branch-lockfiles` to `pnpm install` command.

After that, all git branch lockfiles will be merged into one `pnpm-lock.yaml`


### Branch Matching

pnpm allows you to specify `--merge-git-branch-lockfiles` by matching the current branch name.

For instance, by the following setting in `pnpm-workspace.yaml` file, `pnpm install` will merge all git branch lockfiles when 
running in the `main` branch and the branch name starts with `release`.

```yaml
mergeGitBranchLockfilesBranchPattern:
- main
- release*
```
````

## File: docs/git.md
````markdown
---
id: git
title: Working with Git
---

## Lockfiles

You should always commit the lockfile (`pnpm-lock.yaml`). This is for a
multitude of reasons, the primary of which being:
- it enables faster installation for CI and production environments, due to
being able to skip package resolution
- it enforces consistent installations and resolution between development,
testing, and production environments, meaning the packages used in testing
and production will be exactly the same as when you developed your project

### Merge conflicts

pnpm can automatically resolve merge conflicts in `pnpm-lock.yaml`.
If you have conflicts, just run `pnpm install` and commit the changes.

Be warned, however. It is advised that you review the changes prior to
staging a commit, because we cannot guarantee that pnpm will choose the correct
head - it instead builds with the most updated of lockfiles, which is ideal in
most cases.
````

## File: docs/how-peers-are-resolved.md
````markdown
---
id: how-peers-are-resolved
title: How peers are resolved
---

One of the best features of pnpm is that in one project, a specific version of a
package will always have one set of dependencies. There is one exception from
this rule, though - packages with [peer dependencies].

[peer dependencies]: https://docs.npmjs.com/cli/v10/configuring-npm/package-json#peerdependencies

Peer dependencies are resolved from dependencies installed higher in the
dependency graph, since they share the same version as their parent. That means
that if `foo@1.0.0` has two peers (`bar@^1` and `baz@^1`) then it might have
multiple different sets of dependencies in the same project.

```text
- foo-parent-1
  - bar@1.0.0
  - baz@1.0.0
  - foo@1.0.0
- foo-parent-2
  - bar@1.0.0
  - baz@1.1.0
  - foo@1.0.0
```

In the example above, `foo@1.0.0` is installed for `foo-parent-1` and
`foo-parent-2`. Both packages have `bar` and `baz` as well, but they depend on
different versions of `baz`. As a result, `foo@1.0.0` has two different sets of
dependencies: one with `baz@1.0.0` and the other one with `baz@1.1.0`. To
support these use cases, pnpm has to hard link `foo@1.0.0` as many times as
there are different dependency sets.

Normally, if a package does not have peer dependencies, it is hard linked to a
`node_modules` folder next to symlinks of its dependencies, like so:

```text
node_modules
└── .pnpm
    ├── foo@1.0.0
    │   └── node_modules
    │       ├── foo
    │       ├── qux   -> ../../qux@1.0.0/node_modules/qux
    │       └── plugh -> ../../plugh@1.0.0/node_modules/plugh
    ├── qux@1.0.0
    ├── plugh@1.0.0
```

However, if `foo` has peer dependencies, there may be multiple sets of
dependencies for it, so we create different sets for different peer dependency
resolutions:

```text
node_modules
└── .pnpm
    ├── foo@1.0.0_bar@1.0.0+baz@1.0.0
    │   └── node_modules
    │       ├── foo
    │       ├── bar   -> ../../bar@1.0.0/node_modules/bar
    │       ├── baz   -> ../../baz@1.0.0/node_modules/baz
    │       ├── qux   -> ../../qux@1.0.0/node_modules/qux
    │       └── plugh -> ../../plugh@1.0.0/node_modules/plugh
    ├── foo@1.0.0_bar@1.0.0+baz@1.1.0
    │   └── node_modules
    │       ├── foo
    │       ├── bar   -> ../../bar@1.0.0/node_modules/bar
    │       ├── baz   -> ../../baz@1.1.0/node_modules/baz
    │       ├── qux   -> ../../qux@1.0.0/node_modules/qux
    │       └── plugh -> ../../plugh@1.0.0/node_modules/plugh
    ├── bar@1.0.0
    ├── baz@1.0.0
    ├── baz@1.1.0
    ├── qux@1.0.0
    ├── plugh@1.0.0
```

We create symlinks either to the `foo` that is inside
`foo@1.0.0_bar@1.0.0+baz@1.0.0` or to the one in
`foo@1.0.0_bar@1.0.0+baz@1.1.0`.
As a consequence, the Node.js module resolver will find the correct peers.

*If a package has no peer dependencies but has dependencies with peers that are
resolved higher in the graph*, then that transitive package can appear in the
project with different sets of dependencies. For instance, there's package
`a@1.0.0` with a single dependency `b@1.0.0`. `b@1.0.0` has a peer dependency
`c@^1`. `a@1.0.0` will never resolve the peers of `b@1.0.0`, so it becomes
dependent from the peers of `b@1.0.0` as well.

Here's how that structure will look in `node_modules`. In this example,
`a@1.0.0` will need to appear twice in the project's `node_modules` - resolved
once with `c@1.0.0` and again with `c@1.1.0`.

```text
node_modules
└── .pnpm
    ├── a@1.0.0_c@1.0.0
    │   └── node_modules
    │       ├── a
    │       └── b -> ../../b@1.0.0_c@1.0.0/node_modules/b
    ├── a@1.0.0_c@1.1.0
    │   └── node_modules
    │       ├── a
    │       └── b -> ../../b@1.0.0_c@1.1.0/node_modules/b
    ├── b@1.0.0_c@1.0.0
    │   └── node_modules
    │       ├── b
    │       └── c -> ../../c@1.0.0/node_modules/c
    ├── b@1.0.0_c@1.1.0
    │   └── node_modules
    │       ├── b
    │       └── c -> ../../c@1.1.0/node_modules/c
    ├── c@1.0.0
    ├── c@1.1.0
```
````

## File: docs/installation.md
````markdown
---
id: installation
title: Installation
---

## Prerequisites

If you don't use the standalone script or `@pnpm/exe` to install pnpm, then you need to have Node.js (at least v18.12) to be installed on your system.

## Using a standalone script

You may install pnpm even if you don't have Node.js installed, using the following scripts.

### On Windows

:::warning

Sometimes, Windows Defender may block our executable if you install pnpm this way.

Due to this issue, we currently recommend installing pnpm using [npm](#using-npm) or [Corepack](#using-corepack) on Windows.

:::

Using PowerShell:

```powershell
Invoke-WebRequest https://get.pnpm.io/install.ps1 -UseBasicParsing | Invoke-Expression
```

### On POSIX systems

```sh
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

If you don't have curl installed, you would like to use wget:

```sh
wget -qO- https://get.pnpm.io/install.sh | sh -
```

:::tip

You may use the [pnpm env] command then to install Node.js.

:::

### In a Docker container

```sh
# bash
wget -qO- https://get.pnpm.io/install.sh | ENV="$HOME/.bashrc" SHELL="$(which bash)" bash -
# sh
wget -qO- https://get.pnpm.io/install.sh | ENV="$HOME/.shrc" SHELL="$(which sh)" sh -
# dash
wget -qO- https://get.pnpm.io/install.sh | ENV="$HOME/.dashrc" SHELL="$(which dash)" dash -
```

### Installing a specific version

Prior to running the install script, you may optionally set an env variable `PNPM_VERSION` to install a specific version of pnpm:

```sh
curl -fsSL https://get.pnpm.io/install.sh | env PNPM_VERSION=<version> sh -
```

## Using Corepack

Due to an issue with [outdated signatures in Corepack](https://github.com/nodejs/corepack/issues/612), Corepack should be updated to its latest version first:

```
npm install --global corepack@latest
```

Since v16.13, Node.js is shipping [Corepack](https://nodejs.org/api/corepack.html) for managing package managers. This is an experimental feature, so you need to enable it by running:

:::info

If you have installed Node.js with `pnpm env` Corepack won't be installed on your system, you will need to install it separately. See [#4029](https://github.com/pnpm/pnpm/issues/4029).

:::

```
corepack enable pnpm
```

This will automatically install pnpm on your system.

You can pin the version of pnpm used on your project using the following command:

```
corepack use pnpm@latest-10
```

This will add a `"packageManager"` field in your local `package.json` which will instruct Corepack to always use a specific version on that project. This can be useful if you want reproducability, as all developers who are using Corepack will use the same version as you. When a new version of pnpm is released, you can re-run the above command.

## Using other package managers

### Using npm

We provide two packages of pnpm CLI, `pnpm` and `@pnpm/exe`.

- [`pnpm`](https://www.npmjs.com/package/pnpm) is an ordinary version of pnpm, which needs Node.js to run.
- [`@pnpm/exe`](https://www.npmjs.com/package/@pnpm/exe) is packaged with Node.js into an executable, so it may be used on a system with no Node.js installed.


```sh
npm install -g pnpm@latest-10
```

or

```sh
npm install -g @pnpm/exe@latest-10
```

### Using Homebrew

If you have the package manager installed, you can install pnpm using the following command:

```
brew install pnpm
```

### Using winget

If you have winget installed, you can install pnpm using the following command:

```
winget install -e --id pnpm.pnpm
```

### Using Scoop

If you have Scoop installed, you can install pnpm using the following command:

```
scoop install nodejs-lts pnpm
```

### Using Choco

If you have Chocolatey installed, you can install pnpm using the following command:

```
choco install pnpm
```

### Using Volta

If you have Volta installed, you can install pnpm using the following command:

```
volta install pnpm
```

:::tip

Do you wanna use pnpm on CI servers? See: [Continuous Integration](./continuous-integration.md).

:::

## Compatibility

Here is a list of past pnpm versions with respective Node.js version support.

| Node.js    | pnpm 8 | pnpm 9 | pnpm 10 |
|------------|--------|--------|---------|
| Node.js 14 | ❌     | ❌     | ❌      |
| Node.js 16 | ✔️      | ❌     | ❌      |
| Node.js 18 | ✔️      | ✔️      | ✔️       |
| Node.js 20 | ✔️      | ✔️      | ✔️       |
| Node.js 22 | ✔️      | ✔️      | ✔️       |

## Troubleshooting

If pnpm is broken and you cannot fix it by reinstalling, you might need to remove it manually from the PATH.

Let's assume you have the following error when running `pnpm install`:

```
C:\src>pnpm install
internal/modules/cjs/loader.js:883
  throw err;
  ^



Error: Cannot find module 'C:\Users\Bence\AppData\Roaming\npm\pnpm-global\4\node_modules\pnpm\bin\pnpm.js'
←[90m    at Function.Module._resolveFilename (internal/modules/cjs/loader.js:880:15)←[39m
←[90m    at Function.Module._load (internal/modules/cjs/loader.js:725:27)←[39m
←[90m    at Function.executeUserEntryPoint [as runMain] (internal/modules/run_main.js:72:12)←[39m
←[90m    at internal/main/run_main_module.js:17:47←[39m {
  code: ←[32m'MODULE_NOT_FOUND'←[39m,
  requireStack: []
}
```

First, try to find the location of pnpm by running: `which pnpm`. If you're on Windows, run `where.exe pnpm.*`.
You'll get the location of the pnpm command, for instance:

```
$ which pnpm
/c/Program Files/nodejs/pnpm
```

Now that you know where the pnpm CLI is, open that directory and remove any pnpm-related files (`pnpm.cmd`, `pnpx.cmd`, `pnpm`, etc).
Once done, install pnpm again and it should work as expected.

## Using a shorter alias

`pnpm` might be hard to type, so you may use a shorter alias like `pn` instead. 

#### Adding a permanent alias on POSIX systems

Just put the following line to your `.bashrc`, `.zshrc`, or `config.fish`:

```
alias pn=pnpm
```

#### Adding a permanent alias in Powershell (Windows):

In a Powershell window with admin rights, execute:

```
notepad $profile.AllUsersAllHosts
```

In the `profile.ps1` file that opens, put:

```
set-alias -name pn -value pnpm
```

Save the file and close the window. You may need to close any open Powershell window in order for the alias to take effect.

## Updating pnpm

To update pnpm, run the [`self-update`] command:

```
pnpm self-update
```

[`self-update`]: ./cli/self-update.md

## Uninstalling pnpm

If you need to remove the pnpm CLI from your system and any files it has written to your disk, see [Uninstalling pnpm].

[Uninstalling pnpm]: ./uninstall.md
[pnpm env]: ./cli/env.md
````

## File: docs/limitations.md
````markdown
---
id: limitations
title: Limitations
---

1. `npm-shrinkwrap.json` and `package-lock.json` are ignored. Unlike pnpm, npm
can install the same `name@version` multiple times and with different sets of
dependencies. npm's lockfile is designed to reflect the flat `node_modules`
layout, however, as pnpm creates an isolated layout by default, it cannot respect
npm's lockfile format. See [pnpm import] if you wish to convert a lockfile to
pnpm's format, though.
1. Binstubs (files in `node_modules/.bin`) are always shell files, not
symlinks to JS files. The shell files are created to help pluggable CLI apps
in finding their plugins in the unusual `node_modules` structure. This is very
rarely an issue and if you expect the file to be a JS file, reference the
original file directly instead, as described in [#736].

Got an idea for workarounds for these issues?
[Share them.](https://github.com/pnpm/pnpm/issues/new)

[pnpm import]: cli/import.md
[#736]: https://github.com/pnpm/pnpm/issues/736
````

## File: docs/logos.md
````markdown
---
id: logos
title: Logos
---

## Standard logo

**SVG:**

![](/img/logos/pnpm-standard.svg)

**PNG:**

![](/img/logos/pnpm-standard.png)

## Standard logo with no text

**SVG:**

![](/img/logos/pnpm-standard-no-text.svg)

**PNG:**

![](/img/logos/pnpm-standard-no-text.png)

## Standard light logo

**SVG:**

> ![](/img/logos/pnpm-light.svg)

**PNG:**

> ![](/img/logos/pnpm-light.png)

## Standard light logo with no text

**SVG:**

> ![](/img/logos/pnpm-light-no-text.svg)

**PNG:**

> ![](/img/logos/pnpm-light-no-text.png)
````

## File: docs/motivation.md
````markdown
---
id: motivation
title: Motivation
---

## Saving disk space

![An illustration of the pnpm content-addressable store. On the illustration there are two projects with node_modules. The files in the node_modules directories are hard links to the same files in the content-addressable store.](/img/pnpm-store.svg)

When using npm, if you have 100 projects using a dependency, you will
have 100 copies of that dependency saved on disk. With pnpm, the dependency will be
stored in a content-addressable store, so:

1. If you depend on different versions of the dependency, only the files that
differ are added to the store. For instance, if it has 100 files, and a new
version has a change in only one of those files, `pnpm update` will only add 1
new file to the store, instead of cloning the entire dependency just for the
singular change.
1. All the files are saved in a single place on the disk. When packages are
installed, their files are hard-linked from that single place, consuming no
additional disk space. This allows you to share dependencies of the same version
across projects.

As a result, you save a lot of space on your disk proportional to the number of
projects and dependencies, and you have a lot faster installations!

## Boosting installation speed

pnpm performs installation in three stages:

1. Dependency resolution. All required dependencies are identified and fetched to the store.
1. Directory structure calculation. The `node_modules` directory structure is calculated based on the dependencies.
1. Linking dependencies. All remaining dependencies are fetched and hard linked from the store to `node_modules`.

![An illustration of the pnpm install process. Packages are resolved, fetched, and hard linked as soon as possible.](/img/installation-stages-of-pnpm.svg)

This approach is significantly faster than the traditional three-stage installation process of resolving, fetching, and writing all dependencies to `node_modules`.

![An illustration of how package managers like Yarn Classic or npm install dependencies.](/img/installation-stages-of-other-pms.svg)

## Creating a non-flat node_modules directory

When installing dependencies with npm or Yarn Classic, all packages are hoisted to the root of the
modules directory. As a result, source code has access to dependencies that are
not added as dependencies to the project.

By default, pnpm uses symlinks to add only the direct dependencies of the project into the root of the modules directory.

![An illustration of a node_modules directory created by pnpm. Packages in the root node_modules are symlinks to directories inside the node_modules/.pnpm directory](/img/isolated-node-modules.svg)

If you'd like more details about the unique `node_modules` structure that pnpm
creates and why it works fine with the Node.js ecosystem, read:
- [Flat node_modules is not the only way](/blog/2020/05/27/flat-node-modules-is-not-the-only-way)
- [Symlinked node_modules structure](symlinked-node-modules-structure.md)

:::tip

If your tooling doesn't work well with symlinks, you may still use pnpm and set the [nodeLinker](settings#nodeLinker) setting to `hoisted`. This will instruct pnpm to create a node_modules directory that is similar to those created by npm and Yarn Classic.

:::
````

## File: docs/only-allow-pnpm.md
````markdown
---
id: only-allow-pnpm
title: Only allow pnpm
---

When you use pnpm on a project, you don't want others to accidentally run
`npm install` or `yarn`. To prevent devs from using other package managers,
you can add the following `preinstall` script to your `package.json`:

```json
{
	"scripts": {
		"preinstall": "npx only-allow pnpm"
	}
}
```

Now, whenever someone runs `npm install` or `yarn`, they'll get an
error instead and installation will not proceed.

If you use npm v7, use `npx -y` instead.
````

## File: docs/package_json.md
````markdown
---
id: package_json
title: package.json
---

The manifest file of a package. It contains all the package's metadata,
including dependencies, title, author, et cetera. This is a standard preserved
across all major Node.js package managers, including pnpm.

In addition to the traditional `package.json` format, pnpm also supports `package.json5` (via [json5]) and `package.yaml` (via [js-yaml]).

[json5]: https://www.npmjs.com/package/json5
[js-yaml]: https://www.npmjs.com/package/@zkochan/js-yaml

## engines

You can specify the version of Node and pnpm that your software works on:

```json
{
    "engines": {
        "node": ">=10",
        "pnpm": ">=3"
    }
}
```

During local development, pnpm will always fail with an error message
if its version does not match the one specified in the `engines` field.

Unless the user has set the `engineStrict` config flag (see [settings]), this
field is advisory only and will only produce warnings when your package is
installed as a dependency.

[settings]: ./settings.md#enginestrict

## devEngines.runtime

Added in: v10.14

Allows to specify one or more JavaScript runtime engines used by the project. Supported runtimes are Node.js, Deno, and Bun.

For instance, here is how to add `node@^24.4.0` to your dependencies:

```json
{
  "devEngines": {
    "runtime": {
      "name": "node",
      "version": "^24.4.0",
      "onFail": "download"
    }
  }
}
```

You can also add multiple runtimes to the same `package.json`:

```json
{
  "devEngines": {
    "runtime": [
      {
        "name": "node",
        "version": "^24.4.0",
        "onFail": "download"
      },
      {
        "name": "deno",
        "version": "^2.4.3",
        "onFail": "download"
      }
    ]
  }
}
```

How it works:

1. `pnpm install` resolves your specified range to the latest matching runtime version.
1. The exact version (and checksum) is saved in the lockfile.
1. Scripts use the local runtime, ensuring consistency across environments.

## dependenciesMeta

Additional meta information used for dependencies declared inside `dependencies`, `optionalDependencies`, and `devDependencies`.

### dependenciesMeta.*.injected

If this is set to `true` for a dependency that is a local workspace package, that package will be installed by creating a hard linked copy in the virtual store (`node_modules/.pnpm`).

If this is set to `false` or not set, then the dependency will instead be installed by creating a `node_modules` symlink that points to the package's source directory in the workspace.  This is the default, as it is faster and ensures that any modifications to the dependency will be immediately visible to its consumers.

For example, suppose the following `package.json` is a local workspace package:

```json
{
  "name": "card",
  "dependencies": {
    "button": "workspace:1.0.0"
  }
}
```

The `button` dependency will normally be installed by creating a symlink in the `node_modules` directory of `card`, pointing to the development directory for `button`.

But what if `button` specifies `react` in its `peerDependencies`? If all projects in the monorepo use the same version of `react`, then there is no problem. But what if `button` is required by `card` that uses `react@16` and `form` that uses `react@17`? Normally you'd have to choose a single version of `react` and specify it using `devDependencies` of `button`. Symlinking does not provide a way for the `react` peer dependency to be satisfied differently by different consumers such as `card` and `form`.

The `injected` field solves this problem by installing a hard linked copies of `button` in the virtual store. To accomplish this, the `package.json` of `card` could be configured as follows:

```json
{
  "name": "card",
  "dependencies": {
    "button": "workspace:1.0.0",
    "react": "16"
  },
  "dependenciesMeta": {
    "button": {
      "injected": true
    }
  }
}
```

Whereas the `package.json` of `form` could be configured as follows:

```json
{
  "name": "form",
  "dependencies": {
    "button": "workspace:1.0.0",
    "react": "17"
  },
  "dependenciesMeta": {
    "button": {
      "injected": true
    }
  }
}
```

With these changes, we say that `button` is an "injected dependency" of `card` and `form`.  When `button` imports `react`, it will resolve to `react@16` in the context of `card`, but resolve to `react@17` in the context of `form`.

Because injected dependencies produce copies of their workspace source directory, these copies must be updated somehow whenever the code is modified; otherwise, the new state will not be reflected for consumers. When building multiple projects with a command such as `pnpm --recursive run build`, this update must occur after each injected package is rebuilt but before its consumers are rebuilt. For simple use cases, it can be accomplished by invoking `pnpm install` again, perhaps using a `package.json` lifecycle script such as `"prepare": "pnpm run build"` to rebuild that one project.  Third party tools such as [pnpm-sync](https://www.npmjs.com/package/pnpm-sync-lib) and [pnpm-sync-dependencies-meta-injected](https://www.npmjs.com/package/pnpm-sync-dependencies-meta-injected) provide a more robust and efficient solution for updating injected dependencies, as well as watch mode support.

## peerDependenciesMeta

This field lists some extra information related to the dependencies listed in
the `peerDependencies` field.

### peerDependenciesMeta.*.optional

If this is set to true, the selected peer dependency will be marked as optional
by the package manager. Therefore, the consumer omitting it will no longer be
reported as an error.

For example:
```json
{
    "peerDependencies": {
        "foo": "1"
    },
    "peerDependenciesMeta": {
        "foo": {
            "optional": true
        },
        "bar": {
            "optional": true
        }
    }
}
```

Note that even though `bar` was not specified in `peerDependencies`, it is
marked as optional. pnpm will therefore assume that any version of bar is fine.
However, `foo` is optional, but only to the required version specification.

## publishConfig

It is possible to override some fields in the manifest before the package is
packed.
The following fields may be overridden:

* [`bin`](https://github.com/stereobooster/package.json#bin)
* [`main`](https://github.com/stereobooster/package.json#main)
* [`exports`](https://nodejs.org/api/esm.html#esm_package_exports)
* [`types` or `typings`](https://github.com/stereobooster/package.json#types)
* [`module`](https://github.com/stereobooster/package.json#module)
* [`browser`](https://github.com/stereobooster/package.json#browser)
* [`esnext`](https://github.com/stereobooster/package.json#esnext)
* [`es2015`](https://github.com/stereobooster/package.json#es2015)
* [`unpkg`](https://github.com/stereobooster/package.json#unpkg-1)
* [`umd:main`](https://github.com/stereobooster/package.json#microbundle)
* [`typesVersions`](https://www.typescriptlang.org/docs/handbook/declaration-files/publishing.html#version-selection-with-typesversions)
* cpu
* os

To override a field, add the publish version of the field to `publishConfig`.

For instance, the following `package.json`:

```json
{
    "name": "foo",
    "version": "1.0.0",
    "main": "src/index.ts",
    "publishConfig": {
        "main": "lib/index.js",
        "typings": "lib/index.d.ts"
    }
}
```

Will be published as:

```json
{
    "name": "foo",
    "version": "1.0.0",
    "main": "lib/index.js",
    "typings": "lib/index.d.ts"
}
```

### publishConfig.executableFiles

By default, for portability reasons, no files except those listed in the bin field will be marked as executable in the resulting package archive. The `executableFiles` field lets you declare additional files that must have the executable flag (+x) set even if they aren't directly accessible through the bin field.

```json
{
  "publishConfig": {
    "executableFiles": [
      "./dist/shim.js"
    ]
  }
}
```

### publishConfig.directory

You also can use the field `publishConfig.directory` to customize the published subdirectory relative to the current `package.json`.

It is expected to have a modified version of the current package in the specified directory (usually using third party build tools).

> In this example the `"dist"` folder must contain a `package.json`

```json
{
  "name": "foo",
  "version": "1.0.0",
  "publishConfig": {
    "directory": "dist"
  }
}
```

### publishConfig.linkDirectory

* Default: **true**
* Type: **Boolean**

When set to `true`, the project will be symlinked from the `publishConfig.directory` location during local development.

For example:

```json
{
  "name": "foo",
  "version": "1.0.0",
  "publishConfig": {
    "directory": "dist",
    "linkDirectory": true
  }
}
```
````

## File: docs/pnpm-cli.md
````markdown
---
id: pnpm-cli
title: pnpm CLI
---

## Differences vs npm

Unlike npm, pnpm validates all options. For example, `pnpm install --target_arch x64` will
fail as `--target_arch` is not a valid option for `pnpm install`.

However, some dependencies may use the `npm_config_` environment variable, which
is populated from the CLI options. In this case, you have the following options:

1. explicitly set the env variable: `npm_config_target_arch=x64 pnpm install`
1. force the unknown option with `--config.`: `pnpm install --config.target_arch=x64`

## Options

### -C &lt;path\>, --dir &lt;path\>

Run as if pnpm was started in `<path>` instead of the current working directory.

### -w, --workspace-root

Run as if pnpm was started in the root of the [workspace](./workspaces.md)
instead of the current working directory.

## Commands

For more information, see the documentation for individual CLI commands. Here is
a list of handy npm equivalents to get you started:

| npm command     | pnpm equivalent    |
|-----------------|--------------------|
| `npm install`   | [`pnpm install`]   |
| `npm i <pkg>`   | [`pnpm add <pkg>`] |
| `npm run <cmd>` | [`pnpm <cmd>`]     |

When an unknown command is used, pnpm will search for a script with the given name,
so `pnpm run lint` is the same as `pnpm lint`. If there is no script with the specified name,
then pnpm will execute the command as a shell script, so you can do things like `pnpm eslint` (see [`pnpm exec`]).

[`pnpm install`]: ./cli/install.md
[`pnpm add <pkg>`]: ./cli/add.md
[`pnpm <cmd>`]: ./cli/run.md
[`pnpm exec`]: ./cli/exec.md

## Environment variables

Some environment variables that are not pnpm related might change the behaviour of pnpm:

* [`CI`](./cli/install.md#--frozen-lockfile)

These environment variables may influence what directories pnpm will use for storing global information:

* `XDG_CACHE_HOME`
* `XDG_CONFIG_HOME`
* `XDG_DATA_HOME`
* `XDG_STATE_HOME`

You can search the docs to find the settings that leverage these environment variables.
````

## File: docs/pnpm-vs-npm.md
````markdown
---
id: pnpm-vs-npm
title: pnpm vs npm
---

## npm's flat tree

npm maintains a [flattened dependency tree] as of version 3. This leads to less
disk space bloat, with a messy `node_modules` directory as a side effect.

On the other hand, pnpm manages `node_modules` by using hard linking and
symbolic linking to a global on-disk content-addressable store. This lets you get the benefits of far less disk space usage, while also keeping your
`node_modules` clean. There is documentation on the [store layout] if you wish
to learn more.

The good thing about pnpm's proper `node_modules` structure is that it
"[helps to avoid silly bugs]" by making it impossible to use modules that are not
specified in the project's `package.json`.

[flattened dependency tree]: https://github.com/npm/npm/issues/6912
[store layout]: symlinked-node-modules-structure
[helps to avoid silly bugs]: https://www.kochan.io/nodejs/pnpms-strictness-helps-to-avoid-silly-bugs.html

## Installation

pnpm does not allow installation of packages without saving them to
`package.json`. If no parameters are passed to `pnpm add`, packages are saved as
regular dependencies. Like with npm, `--save-dev` and `--save-optional` can be
used to install packages as dev or optional dependencies.

As a consequence of this limitation, projects won't have any extraneous packages
when they use pnpm unless they remove a dependency and leave it orphaned. That's
why pnpm's implementation of the [prune command] does not allow you to specify
packages to prune - it ALWAYS removes all extraneous and orphaned packages.

[prune command]: cli/prune

## Directory dependencies

Directory dependencies start with the `file:` prefix and point to a directory in
the filesystem. Like npm, pnpm symlinks those dependencies. Unlike npm, pnpm
does not perform installation for the file dependencies.

This means that if you have a package called `foo` (`<root>/foo`) that has
`bar@file:../bar` as a dependency, pnpm won't perform installation for
`<root>/bar` when you run `pnpm install` on `foo`.

If you need to run installations in several packages at the same time, for
instance in the case of a monorepo, you should look at the documentation for
[`pnpm -r`].

[`pnpm -r`]: cli/recursive
````

## File: docs/pnpm-workspace_yaml.md
````markdown
---
id: pnpm-workspace_yaml
title: pnpm-workspace.yaml
---

`pnpm-workspace.yaml` defines the root of the [workspace] and enables you to
include / exclude directories from the workspace. By default, all packages of
all subdirectories are included.

For example:

```yaml title="pnpm-workspace.yaml"
packages:
  # specify a package in a direct subdir of the root
  - 'my-app'
  # all packages in direct subdirs of packages/
  - 'packages/*'
  # all packages in subdirs of components/
  - 'components/**'
  # exclude packages that are inside test directories
  - '!**/test/**'
```

The root package is always included, even when custom location wildcards are
used.

Catalogs are also defined in the `pnpm-workspace.yaml` file. See [_Catalogs_](./catalogs.md) for details.

```yaml title="pnpm-workspace.yaml"
packages:
  - 'packages/*'

catalog:
  chalk: ^4.1.2

catalogs:
  react16:
    react: ^16.7.0
    react-dom: ^16.7.0
  react17:
    react: ^17.10.0
    react-dom: ^17.10.0
```

[workspace]: workspaces.md
````

## File: docs/pnpmfile.md
````markdown
---
id: pnpmfile
title: .pnpmfile.cjs
---

pnpm lets you hook directly into the installation process via special functions
(hooks). Hooks can be declared in a file called `.pnpmfile.cjs`.

By default, `.pnpmfile.cjs` should be located in the same directory as the
lockfile. For instance, in a [workspace](workspaces.md) with a shared lockfile,
`.pnpmfile.cjs` should be in the root of the monorepo.

## Hooks

### TL;DR

| Hook Function                                         | Process                                                    | Uses                                               |
|-------------------------------------------------------|------------------------------------------------------------|----------------------------------------------------|
| `hooks.readPackage(pkg, context): pkg`                | Called after pnpm parses the dependency's package manifest | Allows you to mutate a dependency's `package.json` |
| `hooks.afterAllResolved(lockfile, context): lockfile` | Called after the dependencies have been resolved.          | Allows you to mutate the lockfile.                 |

### `hooks.readPackage(pkg, context): pkg | Promise<pkg>`

Allows you to mutate a dependency's `package.json` after parsing and prior to
resolution. These mutations are not saved to the filesystem, however, they will
affect what gets resolved in the lockfile and therefore what gets installed.

Note that you will need to delete the `pnpm-lock.yaml` if you have already
resolved the dependency you want to modify.

:::tip

If you need changes to `package.json` saved to the filesystem, you need to use the [`pnpm patch`] command and patch the `package.json` file.
This might be useful if you want to remove the `bin` field of a dependency for instance.

:::

#### Arguments

* `pkg` - The manifest of the package. Either the response from the registry or
the `package.json` content.
* `context` - Context object for the step. Method `#log(msg)` allows you to use
a debug log for the step.

#### Usage

Example `.pnpmfile.cjs` (changes the dependencies of a dependency):

```js
function readPackage(pkg, context) {
  // Override the manifest of foo@1.x after downloading it from the registry
  if (pkg.name === 'foo' && pkg.version.startsWith('1.')) {
    // Replace bar@x.x.x with bar@2.0.0
    pkg.dependencies = {
      ...pkg.dependencies,
      bar: '^2.0.0'
    }
    context.log('bar@1 => bar@2 in dependencies of foo')
  }
  
  // This will change any packages using baz@x.x.x to use baz@1.2.3
  if (pkg.dependencies.baz) {
    pkg.dependencies.baz = '1.2.3';
  }
  
  return pkg
}

module.exports = {
  hooks: {
    readPackage
  }
}
```

#### Known limitations

Removing the `scripts` field from a dependency's manifest via `readPackage` will
not prevent pnpm from building the dependency. When building a dependency, pnpm
reads the `package.json` of the package from the package's archive, which is not
affected by the hook. In order to ignore a package's build, use the
[neverBuiltDependencies](settings.md#neverbuiltdependencies) field.

### `hooks.updateConfig(config): config | Promise<config>`

Added in: v10.8.0

Allows you to modify the configuration settings used by pnpm. This hook is most useful when paired with [configDependencies](config-dependencies), allowing you to share and reuse settings across different Git repositories.

For example, [@pnpm/plugin-better-defaults](https://github.com/pnpm/plugin-better-defaults) uses the `updateConfig` hook to apply a curated set of recommended settings.

#### Usage example

```js title=".pnpmfile.cjs"
module.exports = {
  hooks: {
    updateConfig (config) {
      return Object.assign(config, {
        enablePrePostScripts: false,
        optimisticRepeatInstall: true,
        resolutionMode: 'lowest-direct',
        verifyDepsBeforeRun: 'install',
      })
    }
  }
}
```

### `hooks.afterAllResolved(lockfile, context): lockfile | Promise<lockfile>`

Allows you to mutate the lockfile output before it is serialized.

#### Arguments

* `lockfile` - The lockfile resolutions object that is serialized to
`pnpm-lock.yaml`.
* `context` - Context object for the step. Method `#log(msg)` allows you to use
a debug log for the step.

#### Usage example

```js title=".pnpmfile.cjs"
function afterAllResolved(lockfile, context) {
  // ...
  return lockfile
}

module.exports = {
  hooks: {
    afterAllResolved
  }
}
```

#### Known Limitations

There are none - anything that can be done with the lockfile can be modified via
this function, and you can even extend the lockfile's functionality.

### `hooks.preResolution(options): Promise<void>`

This hook is executed after reading and parsing the lockfiles of the project, but before resolving dependencies. It allows modifications to the lockfile objects.

#### Arguments

* `options.existsCurrentLockfile` - A boolean that is true if the lockfile at `node_modules/.pnpm/lock.yaml` exists.
* `options.currentLockfile` - The lockfile object from `node_modules/.pnpm/lock.yaml`.
* `options.existsNonEmptyWantedLockfile` - A boolean that is true if the lockfile at `pnpm-lock.yaml` exists.
* `options.wantedLockfile` - The lockfile object from `pnpm-lock.yaml`.
* `options.lockfileDir` - The directory where the wanted lockfile is found.
* `options.storeDir` - The location of the store directory.
* `options.registries` - A map of scopes to registry URLs.

### `hooks.importPackage(destinationDir, options): Promise<string | undefined>`

This hook allows to change how packages are written to `node_modules`. The return value is optional and states what method was used for importing the dependency, e.g.: clone, hardlink.

#### Arguments

* `destinationDir` - The destination directory where the package should be written.
* `options.disableRelinkLocalDirDeps`
* `options.filesMap`
* `options.force`
* `options.resolvedFrom`
* `options.keepModulesDir`

### `hooks.fetchers`

This hook allows to override the fetchers that are used for different types of dependencies. It is an object that may have the following fields:

* `localTarball`
* `remoteTarball`
* `gitHostedTarball`
* `directory`
* `git`

## Related Configuration

import IgnorePnpmfile from './settings/_ignorePnpmfile.mdx'

<IgnorePnpmfile />

import Pnpmfile from './settings/_pnpmfile.mdx'

<Pnpmfile />

import GlobalPnpmfile from './settings/_globalPnpmfile.mdx'

<GlobalPnpmfile />

[`pnpm patch`]: ./cli/patch.md
````

## File: docs/podman.md
````markdown
---
id: podman
title: Working with Podman
---

## Sharing Files Between a Container and the Host Btrfs Filesystem

:::note

This method only works on copy-on-write filesystems supported by Podman, such as Btrfs. For other filesystems, like Ext4, pnpm will copy the files instead.

:::

Podman support copy-on-write filesystems like Btrfs. With Btrfs, container runtimes create actual Btrfs subvolumes for their mounted volumes. pnpm can leverage this behavior to reflink the files between different mounted volumes.

To share files between the host and the container, mount the store directory and the `node_modules` directory from the host to the container. This allows pnpm inside the container to naturally reuse the files from the host as reflinks.

Below is an example container setup for demonstration:

```dockerfile title="Dockerfile"
FROM node:20-slim

# corepack is an experimental feature in Node.js v20 which allows
# installing and managing versions of pnpm, npm, yarn
RUN corepack enable

VOLUME [ "/pnpm-store", "/app/node_modules" ]
RUN pnpm config --global set store-dir /pnpm-store

# You may need to copy more files than just package.json in your code
COPY package.json /app/package.json

WORKDIR /app
RUN pnpm install
RUN pnpm run build
```

Run the following command to build the podman image:

```sh
podman build . --tag my-podman-image:latest -v "$HOME/.local/share/pnpm/store:/pnpm-store" -v "$(pwd)/node_modules:/app/node_modules"
```
````

## File: docs/production.md
````markdown
---
id: production
title: Production
---

There are two ways to bootstrap your package in a production environment with
pnpm. One of these is to commit the lockfile. Then, in your production
environment, run `pnpm install` - this will build the dependency tree using the
lockfile, meaning the dependency versions will be consistent with how they were
when the lockfile was committed. This is the most effective way (and the one we
recommend) to ensure your dependency tree persists across environments.

The other method is to commit the lockfile AND copy the package store to your
production environment (you can change where with the [store location option]).
Then, you can run `pnpm install --offline` and pnpm will use the packages from
the global store, so it will not make any requests to the registry. This is
recommended **ONLY** for environments where external access to the registry is
unavailable for whatever reason.

[store location option]: settings#storeDir
````

## File: docs/scripts.md
````markdown
---
id: scripts
title: Scripts
---

How pnpm handles the `scripts` field of `package.json`.

## Lifecycle Scripts

### `pnpm:devPreinstall`

Runs only on local `pnpm install`.

Runs before any dependency is installed.

This script is executed only when set in the root project's `package.json`.
````

## File: docs/symlinked-node-modules-structure.md
````markdown
---
id: symlinked-node-modules-structure
title: Symlinked `node_modules` structure
---

:::info

This article only describes how pnpm's `node_modules` are structured when
there are no packages with peer dependencies. For the more complex scenario of
dependencies with peers, see [how peers are resolved](how-peers-are-resolved.md).

:::

pnpm's `node_modules` layout uses symbolic links to create a nested structure of
dependencies.

Every file of every package inside `node_modules` is a hard link to the
content-addressable store. Let's say you install `foo@1.0.0` that depends on
`bar@1.0.0`. pnpm will hard link both packages to `node_modules` like this:

```text
node_modules
└── .pnpm
    ├── bar@1.0.0
    │   └── node_modules
    │       └── bar
    │           ├── index.js     -> <store>/001
    │           └── package.json -> <store>/002
    └── foo@1.0.0
        └── node_modules
            └── foo
                ├── index.js     -> <store>/003
                └── package.json -> <store>/004
```

These are the only "real" files in `node_modules`. Once all the packages are
hard linked to `node_modules`, symbolic links are created to build the nested
dependency graph structure.

As you might have noticed, both packages are hard linked into a subfolder inside
a `node_modules` folder (`foo@1.0.0/node_modules/foo`). This is needed to:

1. **allow packages to import themselves.** `foo` should be able to
`require('foo/package.json')` or `import * as package from "foo/package.json"`.
2. **avoid circular symlinks.** Dependencies of packages are placed in the same
folder in which the dependent packages are. For Node.js it doesn't make a
difference whether dependencies are inside the package's `node_modules` or in
any other `node_modules` in the parent directories.

The next stage of installation is symlinking dependencies. `bar` is going to be
symlinked to the `foo@1.0.0/node_modules` folder:

```text
node_modules
└── .pnpm
    ├── bar@1.0.0
    │   └── node_modules
    │       └── bar -> <store>
    └── foo@1.0.0
        └── node_modules
            ├── foo -> <store>
            └── bar -> ../../bar@1.0.0/node_modules/bar
```

Next, direct dependencies are handled. `foo` is going to be symlinked into the
root `node_modules` folder because `foo` is a dependency of the project:

```text
node_modules
├── foo -> ./.pnpm/foo@1.0.0/node_modules/foo
└── .pnpm
    ├── bar@1.0.0
    │   └── node_modules
    │       └── bar -> <store>
    └── foo@1.0.0
        └── node_modules
            ├── foo -> <store>
            └── bar -> ../../bar@1.0.0/node_modules/bar
```

This is a very simple example. However, the layout will maintain this structure
regardless of the number of dependencies and the depth of the dependency graph.

Let's add `qar@2.0.0` as a dependency of `bar` and `foo`. This is how the new
structure will look:

```text
node_modules
├── foo -> ./.pnpm/foo@1.0.0/node_modules/foo
└── .pnpm
    ├── bar@1.0.0
    │   └── node_modules
    │       ├── bar -> <store>
    │       └── qar -> ../../qar@2.0.0/node_modules/qar
    ├── foo@1.0.0
    │   └── node_modules
    │       ├── foo -> <store>
    │       ├── bar -> ../../bar@1.0.0/node_modules/bar
    │       └── qar -> ../../qar@2.0.0/node_modules/qar
    └── qar@2.0.0
        └── node_modules
            └── qar -> <store>
```

As you may see, even though the graph is deeper now (`foo > bar > qar`), the
directory depth in the file system is still the same.

This layout might look weird at first glance, but it is completely compatible
with Node's module resolution algorithm! When resolving modules, Node ignores
symlinks, so when `bar` is required from `foo@1.0.0/node_modules/foo/index.js`,
Node does not use `bar` at `foo@1.0.0/node_modules/bar`, but instead, `bar` is
resolved to its real location (`bar@1.0.0/node_modules/bar`). As a consequence,
`bar` can also resolve its dependencies which are in `bar@1.0.0/node_modules`.

A great bonus of this layout is that only packages that are really in the
dependencies are accessible. With a flattened `node_modules` structure, all
hoisted packages are accessible. To read more about why this is an advantage,
see "[pnpm's strictness helps to avoid silly bugs][bugs]"

Unfortunately, many packages in the ecosystem are broken — they use dependencies that are not listed in their `package.json`. To minimize the number of issues new users encounter, pnpm hoists all dependencies by default into `node_modules/.pnpm/node_modules`. To disable this hoisting, set [hoist] to `false`.

[hoist]: settings.md#hoist

[bugs]: https://www.kochan.io/nodejs/pnpms-strictness-helps-to-avoid-silly-bugs.html
````

## File: docs/typescript.md
````markdown
---
id: typescript
title: Working with TypeScript
---

pnpm should work well with TypeScript out of the box most of the time.

## Do not preserve symlinks

You should not use TypeScript with [`preserveSymlinks`](https://www.typescriptlang.org/tsconfig/#preserveSymlinks) set to `true`. TypeScript will not be able to resolve the type dependencies correctly in the linked `node_modules`. If you do need to preserve symlinks for some reason, then you should set pnpm's `nodeLinker` setting to `hoisted`.

## Workspace usage

You might sometimes have issues if you have different versions of a `@types/` dependency in a workspace. These issues happen when a package requires these types without having the type dependency in dependencies. For instance, if you have `antd` in your dependencies, which relies on `@types/react`, you might get a compilation error if there are multiple versions of `@types/react` in your workspace. This is actually an issue on `antd`'s end because it should've added `@types/react` to `peerDependencies`. Luckily, you can fix this by extending `antd` with the missing peer dependency. You can do this either by adding this to your `pnpm-workspace.yaml`:

```yaml
packageExtensions:
  antd:
    peerDependencies:
      '@types/react': '*'
```

Alternatively, you can install a config dependency that we created to deal with these issues [`@pnpm/plugin-types-fixer`]. Run:

```sh
pnpm add @pnpm/plugin-types-fixer --config
```

[`@pnpm/plugin-types-fixer`]: https://github.com/pnpm/plugin-types-fixer
````

## File: docs/uninstall.md
````markdown
---
id: uninstall
title: Uninstalling pnpm
---

## Removing the globally installed packages

Before removing the pnpm CLI, it might make sense to remove all global packages that were installed by pnpm.

To list all the global packages, run `pnpm ls -g`. There are two ways to remove the global packages:

1. Run `pnpm rm -g <pkg>...` with each global package listed.
2. Run `pnpm root -g` to find the location of the global directory and remove it manually.

## Removing the pnpm CLI

If you used the standalone script to install pnpm, then you should be able to uninstall the pnpm CLI by removing the pnpm home directory:

```
rm -rf "$PNPM_HOME"
```

You might also want to clean the `PNPM_HOME` env variable in your shell configuration file (`$HOME/.bashrc`, `$HOME/.zshrc` or `$HOME/.config/fish/config.fish`).

If you used npm to install pnpm, then you should use npm to uninstall pnpm:

```
npm rm -g pnpm
```

## Removing the global content-addressable store

```
rm -rf "$(pnpm store path)"
```

If you used pnpm in non-primary disks, then you must run the above command in every disk, where pnpm was used.
pnpm creates one store per disk.
````

## File: docs/using-changesets.md
````markdown
---
id: using-changesets
title: Using Changesets with pnpm
---

:::note

At the time of writing this documentation, the latest pnpm version was
v10.4.1. The latest [Changesets](https://github.com/changesets/changesets) version was v2.28.0.

:::

## Setup

To setup changesets on a pnpm workspace, install changesets as a dev dependency
in the root of the workspace:

```sh
pnpm add -Dw @changesets/cli
```

Then run changesets' init command to generate a changesets config:

```sh
pnpm changeset init
```

## Adding new changesets

To generate a new changeset, run `pnpm changeset` in the root of the repository.
The generated markdown files in the `.changeset` directory should be committed
to the repository.

## Releasing changes

1. Run `pnpm changeset version`. This will bump the versions of the packages
   previously specified with `pnpm changeset` (and any dependents of those) and
   update the changelog files.
2. Run `pnpm install`. This will update the lockfile and rebuild packages.
3. Commit the changes.
4. Run `pnpm publish -r`. This command will publish all packages that have
   bumped versions not yet present in the registry.

## Integration with GitHub Actions

To automate the process, you can use `changeset version` with GitHub actions. The action will detect when changeset files arrive in the `main` branch, and then open a new PR listing all the packages with bumped versions. The PR will automatically update itself every time a new changeset file arrives in `main`. Once merged the packages will be updated, and if the `publish` input has been specified on the action they will  be published using the given command.

### Add a publish script

Add a new script called `ci:publish` which executes `pnpm publish -r`. This will publish to the registry once the PR created by `changeset version` has been merged. If the package is public and scoped, adding `--access=public` may be necessary to prevent npm rejecting the publish.

**package.json**
```json
{
   "scripts": {
      "ci:publish": "pnpm publish -r"
   },
   ...
}
```

### Add the workflow

Add a new workflow at `.github/workflows/changesets.yml`. This workflow will create a new branch and PR, so Actions should be given **read and write** permissions in the repo settings (`github.com/<repo-owner>/<repo-name>/settings/actions`). If including the `publish` input on the `changesets/action` step, the repo should also include an auth token for npm as a repository secret named `NPM_TOKEN`.

**.github/workflows/changesets.yml**
```yaml
name: Changesets

on:
  push:
    branches:
      - main

env:
  CI: true

jobs:
  version:
    timeout-minutes: 15
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code repository
        uses: actions/checkout@v4

      - name: Setup pnpm
        uses: pnpm/action-setup@v4

      - name: Setup node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'pnpm'
      
      - name: Install dependencies
        run: pnpm install
      
      - name: Create and publish versions
        uses: changesets/action@v1
        with:
          commit: "chore: update versions"
          title: "chore: update versions"
          publish: pnpm ci:publish
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

More info and documentation regarding the changesets action can be found
[here](https://github.com/changesets/action).
````

## File: docs/workspaces.md
````markdown
---
id: workspaces
title: Workspace
---

pnpm has built-in support for monorepositories (AKA multi-package repositories,
multi-project repositories, or monolithic repositories). You can create a
workspace to unite multiple projects inside a single repository.

A workspace must have a [`pnpm-workspace.yaml`] file in its
root.

[`pnpm-workspace.yaml`]: pnpm-workspace_yaml.md

:::tip

If you are looking into monorepo management, you might also want to look into [Bit].
Bit uses pnpm under the hood but automates a lot of the things that are currently done manually in a traditional workspace managed by pnpm/npm/Yarn. There's an article about `bit install` that talks about it: [Painless Monorepo Dependency Management with Bit].

:::

[Bit]: https://bit.dev/?utm_source=pnpm&utm_medium=workspace_page
[Painless Monorepo Dependency Management with Bit]: https://bit.dev/blog/painless-monorepo-dependency-management-with-bit-l4f9fzyw?utm_source=pnpm&utm_medium=workspace_page

## Workspace protocol (workspace:)

If [linkWorkspacePackages] is set to `true`, pnpm will link packages from the workspace if the available packages
match the declared ranges. For instance, `foo@1.0.0` is linked into `bar` if
`bar` has `"foo": "^1.0.0"` in its dependencies and `foo@1.0.0` is in the workspace. However, if `bar` has
`"foo": "2.0.0"` in dependencies and `foo@2.0.0` is not in the workspace,
`foo@2.0.0` will be installed from the registry. This behavior introduces some
uncertainty.

Luckily, pnpm supports the `workspace:` protocol. When
this protocol is used, pnpm will refuse to resolve to anything other than a
local workspace package. So, if you set `"foo": "workspace:2.0.0"`, this time
installation will fail because `"foo@2.0.0"` isn't present in the workspace.

This protocol is especially useful when the [linkWorkspacePackages] option is
set to `false`. In that case, pnpm will only link packages from the workspace if
the `workspace:` protocol is used.

[linkWorkspacePackages]: settings.md#linkWorkspacePackages

### Referencing workspace packages through aliases

Let's say you have a package in the workspace named `foo`. Usually, you would
reference it as `"foo": "workspace:*"`.

If you want to use a different alias, the following syntax will work too:
`"bar": "workspace:foo@*"`.

Before publish, aliases are converted to regular aliased dependencies. The above
example will become: `"bar": "npm:foo@1.0.0"`.


### Referencing workspace packages through their relative path

In a workspace with 2 packages:

```
+ packages
	+ foo
	+ bar
```

`bar` may have `foo` in its dependencies declared as
`"foo": "workspace:../foo"`. Before publishing, these specs are converted to
regular version specs supported by all package managers.

### Publishing workspace packages

When a workspace package is packed into an archive (whether it's through
`pnpm pack` or one of the publish commands like `pnpm publish`), we dynamically
replace any `workspace:` dependency by:

* The corresponding version in the target workspace (if you use `workspace:*`, `workspace:~`, or `workspace:^`)
* The associated semver range (for any other range type)

So for example, if we have `foo`, `bar`, `qar`, `zoo` in the workspace and they all are at version `1.5.0`, the following:

```json
{
	"dependencies": {
		"foo": "workspace:*",
		"bar": "workspace:~",
		"qar": "workspace:^",
		"zoo": "workspace:^1.5.0"
	}
}
```

Will be transformed into:

```json
{
	"dependencies": {
		"foo": "1.5.0",
		"bar": "~1.5.0",
		"qar": "^1.5.0",
		"zoo": "^1.5.0"
	}
}
```

This feature allows you to depend on your local workspace packages while still
being able to publish the resulting packages to the remote registry without
needing intermediary publish steps - your consumers will be able to use your
published workspaces as any other package, still benefitting from the guarantees
semver offers.

## Release workflow

Versioning packages inside a workspace is a complex task and pnpm currently does
not provide a built-in solution for it. However, there are 2 well tested tools
that handle versioning and support pnpm:
- [changesets](https://github.com/changesets/changesets)
- [Rush](https://rushjs.io)

For how to set up a repository using Rush, read [this page][rush-setup].

For using Changesets with pnpm, read [this guide][changesets-guide].

[rush-setup]: https://rushjs.io/pages/maintainer/setup_new_repo
[changesets-guide]: using-changesets.md

## Troubleshooting

pnpm cannot guarantee that scripts will be run in topological order if there are cycles between workspace dependencies. If pnpm detects cyclic dependencies during installation, it will produce a warning. If pnpm is able to find out which dependencies are causing the cycles, it will display them too.

If you see the message `There are cyclic workspace dependencies`, please inspect workspace dependencies declared in `dependencies`, `optionalDependencies` and `devDependencies`.

## Usage examples

Here are a few of the most popular open source projects that use the workspace feature of pnpm:

| Project | Stars | Migration date | Migration commit |
| --      | --    | --             | --               |
| [Next.js](https://github.com/vercel/next.js) | ![](https://img.shields.io/github/stars/vercel/next.js) | 2022-05-29 | [`f7b81316aea4fc9962e5e54981a6d559004231aa`](https://github.com/vercel/next.js/commit/f7b81316aea4fc9962e5e54981a6d559004231aa) |
| [n8n](https://github.com/n8n-io/n8n) | ![](https://img.shields.io/github/stars/n8n-io/n8n) | 2022-11-09 | [`736777385c54d5b20174c9c1fda38bb31fbf14b4`](https://github.com/n8n-io/n8n/commit/736777385c54d5b20174c9c1fda38bb31fbf14b4) |
| [Material UI](https://github.com/mui/material-ui) | ![](https://img.shields.io/github/stars/mui/material-ui) | 2024-01-03 | [`a1263e3e5ef8d840252b4857f85b33caa99f471d`](https://github.com/mui/material-ui/commit/a1263e3e5ef8d840252b4857f85b33caa99f471d) |
| [Vite](https://github.com/vitejs/vite) | ![](https://img.shields.io/github/stars/vitejs/vite) | 2021-09-26 | [`3e1cce01d01493d33e50966d0d0fd39a86d229f9`](https://github.com/vitejs/vite/commit/3e1cce01d01493d33e50966d0d0fd39a86d229f9) |
| [Nuxt](https://github.com/nuxt/nuxt) | ![](https://img.shields.io/github/stars/nuxt/nuxt) | 2022-10-17 | [`74a90c566c936164018c086030c7de65b26a5cb6`](https://github.com/nuxt/nuxt/commit/74a90c566c936164018c086030c7de65b26a5cb6) |
| [Vue](https://github.com/vuejs/core) | ![](https://img.shields.io/github/stars/vuejs/core) | 2021-10-09 | [`61c5fbd3e35152f5f32e95bf04d3ee083414cecb`](https://github.com/vuejs/core/commit/61c5fbd3e35152f5f32e95bf04d3ee083414cecb) |
| [Astro](https://github.com/withastro/astro) | ![](https://img.shields.io/github/stars/withastro/astro) | 2022-03-08 | [`240d88aefe66c7d73b9c713c5da42ae789c011ce`](https://github.com/withastro/astro/commit/240d88aefe66c7d73b9c713c5da42ae789c011ce) |
| [Prisma](https://github.com/prisma/prisma) | ![](https://img.shields.io/github/stars/prisma/prisma) | 2021-09-21 | [`c4c83e788aa16d61bae7a6d00adc8a58b3789a06`](https://github.com/prisma/prisma/commit/c4c83e788aa16d61bae7a6d00adc8a58b3789a06) |
| [Novu](https://github.com/novuhq/novu) | ![](https://img.shields.io/github/stars/novuhq/novu) | 2021-12-23 | [`f2ea61f7d7ac7e12db4c9e70767082841ed98b2b`](https://github.com/novuhq/novu/commit/f2ea61f7d7ac7e12db4c9e70767082841ed98b2b) |
| [Slidev](https://github.com/slidevjs/slidev) | ![](https://img.shields.io/github/stars/slidevjs/slidev) | 2021-04-12 | [`d6783323eb1ab1fc612577eb63579c8f7bc99c3a`](https://github.com/slidevjs/slidev/commit/d6783323eb1ab1fc612577eb63579c8f7bc99c3a) |
| [Turborepo](https://github.com/vercel/turborepo) | ![](https://img.shields.io/github/stars/vercel/turborepo) | 2022-03-02 | [`fd171519ec02a69c9afafc1bc5d9d1b481fba721`](https://github.com/vercel/turborepo/commit/fd171519ec02a69c9afafc1bc5d9d1b481fba721) |
| [Quasar Framework](https://github.com/quasarframework/quasar) | ![](https://img.shields.io/github/stars/quasarframework/quasar) | 2024-03-13 | [`7f8e550bb7b6ab639ce423d02008e7f5e61cbf55`](https://github.com/quasarframework/quasar/commit/7f8e550bb7b6ab639ce423d02008e7f5e61cbf55) |
| [Element Plus](https://github.com/element-plus/element-plus) | ![](https://img.shields.io/github/stars/element-plus/element-plus) | 2021-09-23 | [`f9e192535ff74d1443f1d9e0c5394fad10428629`](https://github.com/element-plus/element-plus/commit/f9e192535ff74d1443f1d9e0c5394fad10428629) |
| [NextAuth.js](https://github.com/nextauthjs/next-auth) | ![](https://img.shields.io/github/stars/nextauthjs/next-auth) | 2022-05-03 | [`4f29d39521451e859dbdb83179756b372e3dd7aa`](https://github.com/nextauthjs/next-auth/commit/4f29d39521451e859dbdb83179756b372e3dd7aa) |
| [Ember.js](https://github.com/emberjs/ember.js) | ![](https://img.shields.io/github/stars/emberjs/ember.js) | 2023-10-18 | [`b6b05da662497183434136fb0148e1dec544db04`](https://github.com/emberjs/ember.js/commit/b6b05da662497183434136fb0148e1dec544db04) |
| [Qwik](https://github.com/BuilderIO/qwik) | ![](https://img.shields.io/github/stars/BuilderIO/qwik) | 2022-11-14 | [`021b12f58cca657e0a008119bc711405513e1ee9`](https://github.com/BuilderIO/qwik/commit/021b12f58cca657e0a008119bc711405513e1ee9) |
| [VueUse](https://github.com/vueuse/vueuse) | ![](https://img.shields.io/github/stars/vueuse/vueuse) | 2021-09-25 | [`826351ba1d9c514e34426c85f3d69fb9875c7dd9`](https://github.com/vueuse/vueuse/commit/826351ba1d9c514e34426c85f3d69fb9875c7dd9) |
| [SvelteKit](https://github.com/sveltejs/kit) | ![](https://img.shields.io/github/stars/sveltejs/kit) | 2021-09-26 | [`b164420ab26fa04fd0fbe0ac05431f36a89ef193`](https://github.com/sveltejs/kit/commit/b164420ab26fa04fd0fbe0ac05431f36a89ef193) |
| [Verdaccio](https://github.com/verdaccio/verdaccio) | ![](https://img.shields.io/github/stars/verdaccio/verdaccio) | 2021-09-21 | [`9dbf73e955fcb70b0a623c5ab89649b95146c744`](https://github.com/verdaccio/verdaccio/commit/9dbf73e955fcb70b0a623c5ab89649b95146c744) |
| [Vercel](https://github.com/vercel/vercel) | ![](https://img.shields.io/github/stars/vercel/vercel) | 2023-01-12 | [`9c768b98b71cfc72e8638bf5172be88c39e8fa69`](https://github.com/vercel/vercel/commit/9c768b98b71cfc72e8638bf5172be88c39e8fa69) |
| [Vitest](https://github.com/vitest-dev/vitest) | ![](https://img.shields.io/github/stars/vitest-dev/vitest) | 2021-12-13 | [`d6ff0ccb819716713f5eab5c046861f4d8e4f988`](https://github.com/vitest-dev/vitest/commit/d6ff0ccb819716713f5eab5c046861f4d8e4f988) |
| [Cycle.js](https://github.com/cyclejs/cyclejs) | ![](https://img.shields.io/github/stars/cyclejs/cyclejs) | 2021-09-21 | [`f2187ab6688368edb904b649bd371a658f6a8637`](https://github.com/cyclejs/cyclejs/commit/f2187ab6688368edb904b649bd371a658f6a8637) |
| [Milkdown](https://github.com/Saul-Mirone/milkdown) | ![](https://img.shields.io/github/stars/Saul-Mirone/milkdown) | 2021-09-26 | [`4b2e1dd6125bc2198fd1b851c4f00eda70e9b913`](https://github.com/Saul-Mirone/milkdown/commit/4b2e1dd6125bc2198fd1b851c4f00eda70e9b913) |
| [Nhost](https://github.com/nhost/nhost) | ![](https://img.shields.io/github/stars/nhost/nhost) | 2022-02-07 | [`10a1799a1fef2f558f737de3bb6cadda2b50e58f`](https://github.com/nhost/nhost/commit/10a1799a1fef2f558f737de3bb6cadda2b50e58f) |
| [Logto](https://github.com/logto-io/logto) | ![](https://img.shields.io/github/stars/logto-io/logto) | 2021-07-29 | [`0b002e07850c8e6d09b35d22fab56d3e99d77043`](https://github.com/logto-io/logto/commit/0b002e07850c8e6d09b35d22fab56d3e99d77043) |
| [Rollup plugins](https://github.com/rollup/plugins) | ![](https://img.shields.io/github/stars/rollup/plugins) | 2021-09-21 | [`53fb18c0c2852598200c547a0b1d745d15b5b487`](https://github.com/rollup/plugins/commit/53fb18c0c2852598200c547a0b1d745d15b5b487) |
| [icestark](https://github.com/ice-lab/icestark) | ![](https://img.shields.io/github/stars/ice-lab/icestark) | 2021-12-16 | [`4862326a8de53d02f617e7b1986774fd7540fccd`](https://github.com/ice-lab/icestark/commit/4862326a8de53d02f617e7b1986774fd7540fccd) |
| [ByteMD](https://github.com/bytedance/bytemd) | ![](https://img.shields.io/github/stars/bytedance/bytemd) | 2021-02-18 | [`36ef25f1ea1cd0b08752df5f8c832302017bb7fb`](https://github.com/bytedance/bytemd/commit/36ef25f1ea1cd0b08752df5f8c832302017bb7fb) |
| [Stimulus Components](https://github.com/stimulus-components/stimulus-components) | ![](https://img.shields.io/github/stars/stimulus-components/stimulus-components) | 2024-10-26 | [`8e100d5b2c02ad5bf0b965822880a60f543f5ec3`](https://github.com/stimulus-components/stimulus-components/commit/8e100d5b2c02ad5bf0b965822880a60f543f5ec3) |
| [Serenity/JS](https://github.com/serenity-js/serenity-js) | ![](https://img.shields.io/github/stars/serenity-js/serenity-js) | 2025-01-01 | [`43dbe6f440d8dd81811da303e542381a17d06b4d`](https://github.com/serenity-js/serenity-js/commit/43dbe6f440d8dd81811da303e542381a17d06b4d) |
| [kysely](https://github.com/kysely-org/kysely) | ![](https://img.shields.io/github/stars/kysely-org/kysely) | 2025-07-29 | [`5ac19105ddb17af310c67e004c11fa3345454b66`](https://github.com/kysely-org/kysely/commit/5ac19105ddb17af310c67e004c11fa3345454b66) |
````
