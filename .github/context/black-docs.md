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
  contributing/
    gauging_changes.md
    index.md
    issue_triage.md
    release_process.md
    the_basics.md
  guides/
    index.md
    introducing_black_to_your_project.md
    using_black_with_other_tools.md
  integrations/
    editors.md
    github_actions.md
    index.md
    source_version_control.md
  the_black_code_style/
    current_style.md
    future_style.md
    index.md
  usage_and_configuration/
    black_as_a_server.md
    black_docker_image.md
    file_collection_and_discovery.md
    index.md
    the_basics.md
  authors.md
  change_log.md
  faq.md
  getting_started.md
  index.md
  license.md
  requirements.txt
```

# Files

## File: docs/contributing/gauging_changes.md
````markdown
# Gauging changes

A lot of the time, your change will affect formatting and/or performance. Quantifying
these changes is hard, so we have tooling to help make it easier.

It's recommended you evaluate the quantifiable changes your _Black_ formatting
modification causes before submitting a PR. Think about if the change seems disruptive
enough to cause frustration to projects that are already "black formatted".

## diff-shades

diff-shades is a tool that runs _Black_ across a list of open-source projects recording
the results. The main highlight feature of diff-shades is being able to compare two
revisions of _Black_. This is incredibly useful as it allows us to see what exact
changes will occur, say merging a certain PR.

For more information, please see the [diff-shades documentation][diff-shades].

### CI integration

diff-shades is also the tool behind the "diff-shades results comparing ..." /
"diff-shades reports zero changes ..." comments on PRs. The project has a GitHub Actions
workflow that analyzes and compares two revisions of _Black_ according to these rules:

|                       | Baseline revision       | Target revision              |
| --------------------- | ----------------------- | ---------------------------- |
| On PRs                | latest commit on `main` | PR commit with `main` merged |
| On pushes (main only) | latest PyPI version     | the pushed commit            |

For pushes to main, there's only one analysis job named `preview-changes` where the
preview style is used for all projects.

For PRs they get one more analysis job: `assert-no-changes`. It's similar to
`preview-changes` but runs with the stable code style. It will fail if changes were
made. This makes sure code won't be reformatted again and again within the same year in
accordance to Black's stability policy.

Additionally for PRs, a PR comment will be posted embedding a summary of the preview
changes and links to further information. If there's a pre-existing diff-shades comment,
it'll be updated instead the next time the workflow is triggered on the same PR.

```{note}
The `preview-changes` job will only fail intentionally if while analyzing a file failed to
format. Otherwise a failure indicates a bug in the workflow.
```

The workflow uploads several artifacts upon completion:

- The raw analyses (.json)
- HTML diffs (.html)
- `.pr-comment.json` (if triggered by a PR)

The last one is downloaded by the `diff-shades-comment` workflow and shouldn't be
downloaded locally. The HTML diffs come in handy for push-based where there's no PR to
post a comment. And the analyses exist just in case you want to do further analysis
using the collected data locally.

[diff-shades]: https://github.com/ichard26/diff-shades#readme
````

## File: docs/contributing/index.md
````markdown
# Contributing

```{toctree}
---
hidden:
---

the_basics
gauging_changes
issue_triage
release_process
```

Welcome! Happy to see you willing to make the project better. Have you read the entire
[user documentation](https://black.readthedocs.io/en/latest/) yet?

```{rubric} Bird's eye view

```

In terms of inspiration, _Black_ is about as configurable as _gofmt_ (which is to say,
not very). This is deliberate. _Black_ aims to provide a consistent style and take away
opportunities for arguing about style.

Bug reports and fixes are always welcome! Please follow the
[issue templates on GitHub](https://github.com/psf/black/issues/new/choose) for best
results.

Before you suggest a new feature or configuration knob, ask yourself why you want it. If
it enables better integration with some workflow, fixes an inconsistency, speeds things
up, and so on - go for it! On the other hand, if your answer is "because I don't like a
particular formatting" then you're not ready to embrace _Black_ yet. Such changes are
unlikely to get accepted. You can still try but prepare to be disappointed.

```{rubric} Contents

```

This section covers the following topics:

- {doc}`the_basics`
- {doc}`gauging_changes`
- {doc}`release_process`

For an overview on contributing to the _Black_, please checkout {doc}`the_basics`.
````

## File: docs/contributing/issue_triage.md
````markdown
# Issue triage

Currently, _Black_ uses the issue tracker for bugs, feature requests, proposed style
modifications, and general user support. Each of these issues have to be triaged so they
can be eventually be resolved somehow. This document outlines the triaging process and
also the current guidelines and recommendations.

```{tip}
If you're looking for a way to contribute without submitting patches, this might be
the area for you. Since _Black_ is a popular project, its issue tracker is quite busy
and always needs more attention than is available. While triage isn't the most
glamorous or technically challenging form of contribution, it's still important.
For example, we would love to know whether that old bug report is still reproducible!

You can get easily started by reading over this document and then responding to issues.

If you contribute enough and have stayed for a long enough time, you may even be
given Triage permissions!
```

## The basics

_Black_ gets a whole bunch of different issues, they range from bug reports to user
support issues. To triage is to identify, organize, and kickstart the issue's journey
through its lifecycle to resolution.

More specifically, to triage an issue means to:

- identify what type and categories the issue falls under
- confirm bugs
- ask questions / for further information if necessary
- link related issues
- provide the first initial feedback / support

Note that triage is typically the first response to an issue, so don't fret if the issue
doesn't make much progress after initial triage. The main goal of triaging to prepare
the issue for future more specific development or discussion, so _eventually_ it will be
resolved.

The lifecycle of a bug report or user support issue typically goes something like this:

1. _the issue is waiting for triage_
2. **identified** - has been marked with a type label and other relevant labels, more
   details or a functional reproduction may be still needed (and therefore should be
   marked with `S: needs repro` or `S: awaiting response`)
3. **confirmed** - the issue can reproduced and necessary details have been provided
4. **discussion** - initial triage has been done and now the general details on how the
   issue should be best resolved are being hashed out
5. **awaiting fix** - no further discussion on the issue is necessary and a resolving PR
   is the next step
6. **closed** - the issue has been resolved, reasons include:
   - the issue couldn't be reproduced
   - the issue has been fixed
   - duplicate of another pre-existing issue or is invalid

For enhancement, documentation, and style issues, the lifecycle looks very similar but
the details are different:

1. _the issue is waiting for triage_
2. **identified** - has been marked with a type label and other relevant labels
3. **discussion** - the merits of the suggested changes are currently being discussed, a
   PR would be acceptable but would be at significant risk of being rejected
4. **accepted & awaiting PR** - it's been determined the suggested changes are OK and a
   PR would be welcomed (`S: accepted`)
5. **closed**: - the issue has been resolved, reasons include:
   - the suggested changes were implemented
   - it was rejected (due to technical concerns, ethos conflicts, etc.)
   - duplicate of a pre-existing issue or is invalid

**Note**: documentation issues don't use the `S: accepted` label currently since they're
less likely to be rejected.

## Labelling

We use labels to organize, track progress, and help effectively divvy up work.

Our labels are divided up into several groups identified by their prefix:

- **T - Type**: the general flavor of issue / PR
- **C - Category**: areas of concerns, ranges from bug types to project maintenance
- **F - Formatting Area**: like C but for formatting specifically
- **S - Status**: what stage of resolution is this issue currently in?
- **R - Resolution**: how / why was the issue / PR resolved?

We also have a few standalone labels:

- **`good first issue`**: issues that are beginner-friendly (and will show up in GitHub
  banners for first-time visitors to the repository)
- **`help wanted`**: complex issues that need and are looking for a fair bit of work as
  to progress (will also show up in various GitHub pages)
- **`skip news`**: for PRs that are trivial and don't need a CHANGELOG entry (and skips
  the CHANGELOG entry check)

```{note}
We do use labels for PRs, in particular the `skip news` label, but we aren't that
rigorous about it. Just follow your judgement on what labels make sense for the
specific PR (if any even make sense).
```

## Projects

For more general and broad goals we use projects to track work. Some may be longterm
projects with no true end (e.g. the "Amazing documentation" project) while others may be
more focused and have a definite end (like the "Getting to beta" project).

```{note}
To modify GitHub Projects you need the [Write repository permission level or higher](https://docs.github.com/en/organizations/managing-access-to-your-organizations-repositories/repository-permission-levels-for-an-organization#repository-access-for-each-permission-level).
```

## Closing issues

Closing an issue signifies the issue has reached the end of its life, so closing issues
should be taken with care. The following is the general recommendation for each type of
issue. Note that these are only guidelines and if your judgement says something else
it's totally cool to go with it instead.

For most issues, closing the issue manually or automatically after a resolving PR is
ideal. For bug reports specifically, if the bug has already been fixed, try to check in
with the issue opener that their specific case has been resolved before closing. Note
that we close issues as soon as they're fixed in the `main` branch. This doesn't
necessarily mean they've been released yet.

Design and enhancement issues should be also closed when it's clear the proposed change
won't be implemented, whether that has been determined after a lot of discussion or just
simply goes against _Black_'s ethos. If such an issue turns heated, closing and locking
is acceptable if it's severe enough (although checking in with the core team is probably
a good idea).

User support issues are best closed by the author or when it's clear the issue has been
resolved in some sort of manner.

Duplicates and invalid issues should always be closed since they serve no purpose and
add noise to an already busy issue tracker. Although be careful to make sure it's truly
a duplicate and not just very similar before labelling and closing an issue as
duplicate.

## Common reports

Some issues are frequently opened, like issues about _Black_ formatted code causing E203
messages. Even though these issues are probably heavily duplicated, they still require
triage sucking up valuable time from other things (although they usually skip most of
their lifecycle since they're closed on triage).

Here's some of the most common issues and also pre-made responses you can use:

### "The trailing comma isn't being removed by Black!"

```text
Black used to remove the trailing comma if the expression fits in a single line, but this was changed by #826 and #1288. Now a trailing comma tells Black to always explode the expression. This change was made mostly for the cases where you _know_ a collection or whatever will grow in the future. Having it always exploded as one element per line reduces diff noise when adding elements. Before the "magic trailing comma" feature, you couldn't anticipate a collection's growth reliably since collections that fitted in one line were ruthlessly collapsed regardless of your intentions. One of Black's goals is reducing diff noise, so this was a good pragmatic change.

So no, this is not a bug, but an intended feature. Anyway, [here's the documentation](https://github.com/psf/black/blob/master/docs/the_black_code_style.md#the-magic-trailing-comma) on the "magic trailing comma", including the ability to skip this functionality with the `--skip-magic-trailing-comma` option. Hopefully that helps solve the possible confusion.
```

### "Black formatted code is violating Flake8's E203!"

```text
Hi,

This is expected behaviour, please see the documentation regarding this case (emphasis
mine):

> PEP 8 recommends to treat : in slices as a binary operator with the lowest priority, and to leave an equal amount of space on either side, **except if a parameter is omitted (e.g. ham[1 + 1 :])**. It recommends no spaces around : operators for “simple expressions” (ham[lower:upper]), and **extra space for “complex expressions” (ham[lower : upper + offset])**. **Black treats anything more than variable names as “complex” (ham[lower : upper + 1]).** It also states that for extended slices, both : operators have to have the same amount of spacing, except if a parameter is omitted (ham[1 + 1 ::]). Black enforces these rules consistently.

> This behaviour may raise E203 whitespace before ':' warnings in style guide enforcement tools like Flake8. **Since E203 is not PEP 8 compliant, you should tell Flake8 to ignore these warnings**.

https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#slices

Have a good day!
```
````

## File: docs/contributing/release_process.md
````markdown
# Release process

_Black_ has had a lot of work done into standardizing and automating its release
process. This document sets out to explain how everything works and how to release
_Black_ using said automation.

## Release cadence

**We aim to release whatever is on `main` every 1-2 months.** This ensures merged
improvements and bugfixes are shipped to users reasonably quickly, while not massively
fracturing the user-base with too many versions. This also keeps the workload on
maintainers consistent and predictable.

If there's not much new on `main` to justify a release, it's acceptable to skip a
month's release. Ideally January releases should not be skipped because as per our
[stability policy](labels/stability-policy), the first release in a new calendar year
may make changes to the _stable_ style. While the policy applies to the first release
(instead of only January releases), confining changes to the stable style to January
will keep things predictable (and nicer) for users.

Unless there is a serious regression or bug that requires immediate patching, **there
should not be more than one release per month**. While version numbers are cheap,
releases require a maintainer to both commit to do the actual cutting of a release, but
also to be able to deal with the potential fallout post-release. Releasing more
frequently than monthly nets rapidly diminishing returns.

## Cutting a release

**You must have `write` permissions for the _Black_ repository to cut a release.**

The 10,000 foot view of the release process is that you prepare a release PR and then
publish a [GitHub Release]. This triggers [release automation](#release-workflows) that
builds all release artifacts and publishes them to the various platforms we publish to.

We now have a `scripts/release.py` script to help with cutting the release PRs.

- `python3 scripts/release.py --help` is your friend.
  - `release.py` has only been tested in Python 3.12 (so get with the times :D)

To cut a release:

1. Determine the release's version number
   - **_Black_ follows the [CalVer] versioning standard using the `YY.M.N` format**
     - So unless there already has been a release during this month, `N` should be `0`
   - Example: the first release in January, 2022 → `22.1.0`
   - `release.py` will calculate this and log to stderr for you copy paste pleasure
1. File a PR editing `CHANGES.md` and the docs to version the latest changes
   - Run `python3 scripts/release.py [--debug]` to generate most changes
1. If `release.py` fail manually edit; otherwise, yay, skip this step!
   1. Replace the `## Unreleased` header with the version number
   1. Remove any empty sections for the current release
   1. (_optional_) Read through and copy-edit the changelog (eg. by moving entries,
      fixing typos, or rephrasing entries)
   1. Double-check that no changelog entries since the last release were put in the
      wrong section (e.g., run `git diff <last release> CHANGES.md`)
   1. Update references to the latest version in
      {doc}`/integrations/source_version_control` and
      {doc}`/usage_and_configuration/the_basics`
   - Example PR: [GH-3139]
1. Once the release PR is merged, wait until all CI passes
   - If CI does not pass, **stop** and investigate the failure(s) as generally we'd want
     to fix failing CI before cutting a release
1. [Draft a new GitHub Release][new-release]
   1. Click `Choose a tag` and type in the version number, then select the
      `Create new tag: YY.M.N on publish` option that appears
   1. Verify that the new tag targets the `main` branch
   1. You can leave the release title blank, GitHub will default to the tag name
   1. Copy and paste the _raw changelog Markdown_ for the current release into the
      description box
1. Publish the GitHub Release, triggering [release automation](#release-workflows) that
   will handle the rest
1. Once CI is done add + commit (git push - No review) a new empty template for the next
   release to CHANGES.md _(Template is able to be copy pasted from release.py should we
   fail)_
   1. `python3 scripts/release.py --add-changes-template|-a [--debug]`
   1. Should that fail, please return to copy + paste
1. At this point, you're basically done. It's good practice to go and [watch and verify
   that all the release workflows pass][black-actions], although you will receive a
   GitHub notification should something fail.
   - If something fails, don't panic. Please go read the respective workflow's logs and
     configuration file to reverse-engineer your way to a fix/solution.

Congratulations! You've successfully cut a new release of _Black_. Go and stand up and
take a break, you deserve it.

```{important}
Once the release artifacts reach PyPI, you may see new issues being filed indicating
regressions. While regressions are not great, they don't automatically mean a hotfix
release is warranted. Unless the regressions are serious and impact many users, a hotfix
release is probably unnecessary.

In the end, use your best judgement and ask other maintainers for their thoughts.
```

## Release workflows

All of _Black_'s release automation uses [GitHub Actions]. All workflows are therefore
configured using YAML files in the `.github/workflows` directory of the _Black_
repository.

They are triggered by the publication of a [GitHub Release].

Below are descriptions of our release workflows.

### Publish to PyPI

This is our main workflow. It builds an [sdist] and [wheels] to upload to PyPI where the
vast majority of users will download Black from. It's divided into three job groups:

#### sdist + pure wheel

This single job builds the sdist and pure Python wheel (i.e., a wheel that only contains
Python code) using [build] and then uploads them to PyPI using [twine]. These artifacts
are general-purpose and can be used on basically any platform supported by Python.

#### mypyc wheels (…)

We use [mypyc] to compile _Black_ into a CPython C extension for significantly improved
performance. Wheels built with mypyc are platform and Python version specific.
[Supported platforms are documented in the FAQ](labels/mypyc-support).

These matrix jobs use [cibuildwheel] which handles the complicated task of building C
extensions for many environments for us. Since building these wheels is slow, there are
multiple mypyc wheels jobs (hence the term "matrix") that build for a specific platform
(as noted in the job name in parentheses).

Like the previous job group, the built wheels are uploaded to PyPI using [twine].

#### Update stable branch

So this job doesn't _really_ belong here, but updating the `stable` branch after the
other PyPI jobs pass (they must pass for this job to start) makes the most sense. This
saves us from remembering to update the branch sometime after cutting the release.

- _Currently this workflow uses an API token associated with @ambv's PyPI account_

### Publish executables

This workflow builds native executables for multiple platforms using [PyInstaller]. This
allows people to download the executable for their platform and run _Black_ without a
[Python runtime](https://wiki.python.org/moin/PythonImplementations) installed.

The created binaries are stored on the associated GitHub Release for download over _IPv4
only_ (GitHub still does not have IPv6 access 😢).

### docker

This workflow uses the QEMU powered `buildx` feature of Docker to upload an `arm64` and
`amd64`/`x86_64` build of the official _Black_ Docker image™.

- _Currently this workflow uses an API Token associated with @cooperlees account_

```{note}
This also runs on each push to `main`.
```

[black-actions]: https://github.com/psf/black/actions
[build]: https://pypa-build.readthedocs.io/
[calver]: https://calver.org
[cibuildwheel]: https://cibuildwheel.readthedocs.io/
[gh-3139]: https://github.com/psf/black/pull/3139
[github actions]: https://github.com/features/actions
[github release]: https://github.com/psf/black/releases
[new-release]: https://github.com/psf/black/releases/new
[mypyc]: https://mypyc.readthedocs.io/
[mypyc-platform-support]:
  /faq.html#what-is-compiled-yes-no-all-about-in-the-version-output
[pyinstaller]: https://www.pyinstaller.org/
[sdist]:
  https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist
[twine]: https://github.com/features/actions
[wheels]: https://packaging.python.org/en/latest/glossary/#term-Wheel
````

## File: docs/contributing/the_basics.md
````markdown
# The basics

An overview on contributing to the _Black_ project.

## Technicalities

Development on the latest version of Python is preferred. You can use any operating
system.

First clone the _Black_ repository:

```console
$ git clone https://github.com/psf/black.git
$ cd black
```

Then install development dependencies inside a virtual environment of your choice, for
example:

```console
$ python3 -m venv .venv
$ source .venv/bin/activate # activation for linux and mac
$ .venv\Scripts\activate # activation for windows

(.venv)$ pip install -r test_requirements.txt
(.venv)$ pip install -e ".[d]"
(.venv)$ pre-commit install
```

Before submitting pull requests, run lints and tests with the following commands from
the root of the black repo:

```console
# Linting
(.venv)$ pre-commit run -a

# Unit tests
(.venv)$ tox -e py

# Optional Fuzz testing
(.venv)$ tox -e fuzz

# Format Black itself
(.venv)$ tox -e run_self
```

### Development

Further examples of invoking the tests

```console
# Run all of the above mentioned, in parallel
(.venv)$ tox --parallel=auto

# Run tests on a specific python version
(.venv)$ tox -e py39

# Run an individual test
(.venv)$ pytest -k <test name>

# Pass arguments to pytest
(.venv)$ tox -e py -- --no-cov

# Print full tree diff, see documentation below
(.venv)$ tox -e py -- --print-full-tree

# Disable diff printing, see documentation below
(.venv)$ tox -e py -- --print-tree-diff=False
```

### Testing

All aspects of the _Black_ style should be tested. Normally, tests should be created as
files in the `tests/data/cases` directory. These files consist of up to three parts:

- A line that starts with `# flags: ` followed by a set of command-line options. For
  example, if the line is `# flags: --preview --skip-magic-trailing-comma`, the test
  case will be run with preview mode on and the magic trailing comma off. The options
  accepted are mostly a subset of those of _Black_ itself, except for the
  `--minimum-version=` flag, which should be used when testing a grammar feature that
  works only in newer versions of Python. This flag ensures that we don't try to
  validate the AST on older versions and tests that we autodetect the Python version
  correctly when the feature is used. For the exact flags accepted, see the function
  `get_flags_parser` in `tests/util.py`. If this line is omitted, the default options
  are used.
- A block of Python code used as input for the formatter.
- The line `# output`, followed by the output of _Black_ when run on the previous block.
  If this is omitted, the test asserts that _Black_ will leave the input code unchanged.

_Black_ has two pytest command-line options affecting test files in `tests/data/` that
are split into an input part, and an output part, separated by a line with`# output`.
These can be passed to `pytest` through `tox`, or directly into pytest if not using
`tox`.

#### `--print-full-tree`

Upon a failing test, print the full concrete syntax tree (CST) as it is after processing
the input ("actual"), and the tree that's yielded after parsing the output ("expected").
Note that a test can fail with different output with the same CST. This used to be the
default, but now defaults to `False`.

#### `--print-tree-diff`

Upon a failing test, print the diff of the trees as described above. This is the
default. To turn it off pass `--print-tree-diff=False`.

### News / Changelog Requirement

`Black` has CI that will check for an entry corresponding to your PR in `CHANGES.md`. If
you feel this PR does not require a changelog entry please state that in a comment and a
maintainer can add a `skip news` label to make the CI pass. Otherwise, please ensure you
have a line in the following format added below the appropriate header:

```md
- `Black` is now more awesome (#X)
```

<!---
The Next PR Number link uses HTML because of a bug in MyST-Parser that double-escapes the ampersand, causing the query parameters to not be processed.
MyST-Parser issue: https://github.com/executablebooks/MyST-Parser/issues/760
MyST-Parser stalled fix PR: https://github.com/executablebooks/MyST-Parser/pull/929
-->

Note that X should be your PR number, not issue number! To workout X, please use
<a href="https://ichard26.github.io/next-pr-number/?owner=psf&name=black">Next PR
Number</a>. This is not perfect but saves a lot of release overhead as now the releaser
does not need to go back and workout what to add to the `CHANGES.md` for each release.

### Style Changes

If a change would affect the advertised code style, please modify the documentation (The
_Black_ code style) to reflect that change. Patches that fix unintended bugs in
formatting don't need to be mentioned separately though. If the change is implemented
with the `--preview` flag, please include the change in the future style document
instead and write the changelog entry under the dedicated "Preview style" heading.

### Docs Testing

If you make changes to docs, you can test they still build locally too.

```console
(.venv)$ pip install -r docs/requirements.txt
(.venv)$ pip install -e ".[d]"
(.venv)$ sphinx-build -a -b html -W docs/ docs/_build/
```

## Hygiene

If you're fixing a bug, add a test. Run it first to confirm it fails, then fix the bug,
and run the test again to confirm it's really fixed.

If adding a new feature, add a test. In fact, always add a test. If adding a large
feature, please first open an issue to discuss it beforehand.

## Finally

Thanks again for your interest in improving the project! You're taking action when most
people decide to sit and watch.
````

## File: docs/guides/index.md
````markdown
# Guides

```{toctree}
---
hidden:
---

introducing_black_to_your_project
using_black_with_other_tools
```

Wondering how to do something specific? You've found the right place! Listed below are
topic specific guides available:

- {doc}`introducing_black_to_your_project`
- {doc}`using_black_with_other_tools`
````

## File: docs/guides/introducing_black_to_your_project.md
````markdown
# Introducing _Black_ to your project

```{note}
This guide is incomplete. Contributions are welcomed and would be deeply
appreciated!
```

## Avoiding ruining git blame

A long-standing argument against moving to automated code formatters like _Black_ is
that the migration will clutter up the output of `git blame`. This was a valid argument,
but since Git version 2.23, Git natively supports
[ignoring revisions in blame](https://git-scm.com/docs/git-blame#Documentation/git-blame.txt---ignore-revltrevgt)
with the `--ignore-rev` option. You can also pass a file listing the revisions to ignore
using the `--ignore-revs-file` option. The changes made by the revision will be ignored
when assigning blame. Lines modified by an ignored revision will be blamed on the
previous revision that modified those lines.

So when migrating your project's code style to _Black_, reformat everything and commit
the changes (preferably in one massive commit). Then put the full 40 characters commit
identifier(s) into a file usually called `.git-blame-ignore-revs` at the root of your
project directory.

```text
# Migrate code style to Black
5b4ab991dede475d393e9d69ec388fd6bd949699
```

Afterwards, you can pass that file to `git blame` and see clean and meaningful blame
information.

```console
$ git blame important.py --ignore-revs-file .git-blame-ignore-revs
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 1) def very_important_function(text, file):
abdfd8b0 (Alice Doe  2019-09-23 11:39:32 -0400 2)     text = text.lstrip()
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 3)     with open(file, "r+") as f:
7a1ae265 (John Smith 2019-04-15 15:55:13 -0400 4)         f.write(formatted)
```

You can even configure `git` to automatically ignore revisions listed in a file on every
call to `git blame`.

```console
$ git config blame.ignoreRevsFile .git-blame-ignore-revs
```

**The one caveat is that some online Git-repositories like GitLab do not yet support
ignoring revisions using their native blame UI.** So blame information will be cluttered
with a reformatting commit on those platforms. (If you'd like this feature, there's an
open issue for [GitLab](https://gitlab.com/gitlab-org/gitlab/-/issues/31423)).
[GitHub supports `.git-blame-ignore-revs`](https://docs.github.com/en/repositories/working-with-files/using-files/viewing-a-file#ignore-commits-in-the-blame-view)
by default in blame views however.
````

## File: docs/guides/using_black_with_other_tools.md
````markdown
# Using _Black_ with other tools

## Black compatible configurations

All of Black's changes are harmless (or at least, they should be), but a few do conflict
against other tools. It is not uncommon to be using other tools alongside _Black_ like
linters and type checkers. Some of them need a bit of tweaking to resolve the conflicts.
Listed below are _Black_ compatible configurations in various formats for the common
tools out there.

**Please note** that _Black_ only supports the TOML file format for its configuration
(e.g. `pyproject.toml`). The provided examples are to only configure their corresponding
tools, using **their** supported file formats.

Compatible configuration files can be
[found here](https://github.com/psf/black/blob/main/docs/compatible_configs/).

### isort

[isort](https://pypi.org/p/isort/) helps to sort and format imports in your Python code.
_Black_ also formats imports, but in a different way from isort's defaults which leads
to conflicting changes.

#### Profile

Since version 5.0.0, isort supports
[profiles](https://pycqa.github.io/isort/docs/configuration/profiles.html) to allow easy
interoperability with common code styles. You can set the black profile in any of the
[config files](https://pycqa.github.io/isort/docs/configuration/config_files.html)
supported by isort. Below, an example for `pyproject.toml`:

```toml
[tool.isort]
profile = "black"
```

#### Custom Configuration

If you're using an isort version that is older than 5.0.0 or you have some custom
configuration for _Black_, you can tweak your isort configuration to make it compatible
with _Black_. Below, an example for `.isort.cfg`:

```
multi_line_output = 3
include_trailing_comma = True
force_grid_wrap = 0
use_parentheses = True
ensure_newline_before_comments = True
line_length = 88
```

#### Why those options above?

_Black_ wraps imports that surpass `line-length` by moving identifiers onto separate
lines and by adding a trailing comma after each. A more detailed explanation of this
behaviour can be
[found here](../the_black_code_style/current_style.md#how-black-wraps-lines).

isort's default mode of wrapping imports that extend past the `line_length` limit is
"Grid".

```py3
from third_party import (lib1, lib2, lib3,
                         lib4, lib5, ...)
```

This style is incompatible with _Black_, but isort can be configured to use a different
wrapping mode called "Vertical Hanging Indent" which looks like this:

```py3
from third_party import (
    lib1,
    lib2,
    lib3,
    lib4,
)
```

This style is _Black_ compatible and can be achieved by `multi-line-output = 3`. Also,
as mentioned above, when wrapping long imports _Black_ puts a trailing comma and uses
parentheses. isort should follow the same behaviour and passing the options
`include_trailing_comma = True` and `use_parentheses = True` configures that.

The option `force_grid_wrap = 0` is just to tell isort to only wrap imports that surpass
the `line_length` limit.

Finally, isort should be told to wrap imports when they surpass _Black_'s default limit
of 88 characters via `line_length = 88` as well as
`ensure_newline_before_comments = True` to ensure spacing import sections with comments
works the same as with _Black_.

**Please note** `ensure_newline_before_comments = True` only works since isort >= 5 but
does not break older versions so you can keep it if you are running previous versions.

#### Formats

<details>
<summary>.isort.cfg</summary>

```ini
[settings]
profile = black
```

</details>

<details>
<summary>setup.cfg</summary>

```ini
[isort]
profile = black
```

</details>

<details>
<summary>pyproject.toml</summary>

```toml
[tool.isort]
profile = 'black'
```

</details>

<details>
<summary>.editorconfig</summary>

```ini
[*.py]
profile = black
```

</details>

### pycodestyle

[pycodestyle](https://pycodestyle.pycqa.org/) is a code linter. It warns you of syntax
errors, possible bugs, stylistic errors, etc. For the most part, pycodestyle follows
[PEP 8](https://www.python.org/dev/peps/pep-0008/) when warning about stylistic errors.
There are a few deviations that cause incompatibilities with _Black_.

#### Configuration

```
max-line-length = 88
ignore = E203,E701
```

(labels/why-pycodestyle-warnings)=

#### Why those options above?

##### `max-line-length`

As with isort, pycodestyle should be configured to allow lines up to the length limit of
`88`, _Black_'s default.

##### `E203`

In some cases, as determined by PEP 8, _Black_ will enforce an equal amount of
whitespace around slice operators. Due to this, pycodestyle will raise
`E203 whitespace before ':'` warnings. Since this warning is not PEP 8 compliant, it
should be disabled.

##### `E701` / `E704`

_Black_ will collapse implementations of classes and functions consisting solely of `..`
to a single line. This matches how such examples are formatted in PEP 8. It remains true
that in all other cases Black will prevent multiple statements on the same line, in
accordance with PEP 8 generally discouraging this.

However, `pycodestyle` does not mirror this logic and may raise
`E701 multiple statements on one line (colon)` in this situation. Its
disabled-by-default `E704 multiple statements on one line (def)` rule may also raise
warnings and should not be enabled.

##### `W503`

When breaking a line, _Black_ will break it before a binary operator. This is compliant
with PEP 8 as of
[April 2016](https://github.com/python/peps/commit/c59c4376ad233a62ca4b3a6060c81368bd21e85b#diff-64ec08cc46db7540f18f2af46037f599).
There's a disabled-by-default warning in Flake8 which goes against this PEP 8
recommendation called `W503 line break before binary operator`. It should not be enabled
in your configuration. You can use its counterpart
`W504 line break after binary operator` instead.

#### Formats

<details>
<summary>setup.cfg, .pycodestyle, tox.ini</summary>

```ini
[pycodestyle]
max-line-length = 88
ignore = E203,E701
```

</details>

### Flake8

[Flake8](https://pypi.org/p/flake8/) is a wrapper around multiple linters, including
pycodestyle. As such, it has many of the same issues.

#### Bugbear

It's recommended to use [the Bugbear plugin](https://github.com/PyCQA/flake8-bugbear)
and enable
[its B950 check](https://github.com/PyCQA/flake8-bugbear#opinionated-warnings#:~:text=you%20expect%20it.-,B950,-%3A%20Line%20too%20long)
instead of using Flake8's E501, because it aligns with
[Black's 10% rule](labels/line-length).

Install Bugbear and use the following config:

```
[flake8]
max-line-length = 80
extend-select = B950
extend-ignore = E203,E501,E701
```

#### Minimal Configuration

In cases where you can't or don't want to install Bugbear, you can use this minimally
compatible config:

```
[flake8]
max-line-length = 88
extend-ignore = E203,E701
```

#### Why those options above?

See [the pycodestyle section](labels/why-pycodestyle-warnings) above.

#### Formats

<details>
<summary>.flake8, setup.cfg, tox.ini</summary>

```ini
[flake8]
max-line-length = 88
extend-ignore = E203,E701
```

</details>

### Pylint

[Pylint](https://pypi.org/p/pylint/) is also a code linter like Flake8. It has many of
the same checks as Flake8 and more. It particularly has more formatting checks regarding
style conventions like variable naming.

#### Configuration

```
max-line-length = 88
```

#### Why those options above?

Pylint should be configured to only complain about lines that surpass `88` characters
via `max-line-length = 88`.

If using `pylint<2.6.0`, also disable `C0326` and `C0330` as these are incompatible with
_Black_ formatting and have since been removed.

#### Formats

<details>
<summary>pylintrc</summary>

```ini
[format]
max-line-length = 88
```

</details>

<details>
<summary>setup.cfg</summary>

```cfg
[pylint]
max-line-length = 88
```

</details>

<details>
<summary>pyproject.toml</summary>

```toml
[tool.pylint.format]
max-line-length = "88"
```

</details>
````

## File: docs/integrations/editors.md
````markdown
# Editor integration

## Emacs

Options include the following:

- [wbolster/emacs-python-black](https://github.com/wbolster/emacs-python-black)
- [proofit404/blacken](https://github.com/pythonic-emacs/blacken)
- [Elpy](https://github.com/jorgenschaefer/elpy).

## PyCharm/IntelliJ IDEA

There are several different ways you can use _Black_ from PyCharm:

1. Using the built-in _Black_ integration (PyCharm 2023.2 and later). This option is the
   simplest to set up.
1. As local server using the BlackConnect plugin. This option formats the fastest. It
   spins up {doc}`Black's HTTP server </usage_and_configuration/black_as_a_server>`, to
   avoid the startup cost on subsequent formats.
1. As external tool.
1. As file watcher.

### Built-in _Black_ integration

1. Install `black`.

   ```console
   $ pip install black
   ```

1. Go to `Preferences or Settings -> Tools -> Black` and configure _Black_ to your
   liking.

### As local server

1. Install _Black_ with the `d` extra.

   ```console
   $ pip install 'black[d]'
   ```

1. Install
   [BlackConnect IntelliJ IDEs plugin](https://plugins.jetbrains.com/plugin/14321-blackconnect).

1. Open plugin configuration in PyCharm/IntelliJ IDEA

   On macOS:

   `PyCharm -> Preferences -> Tools -> BlackConnect`

   On Windows / Linux / BSD:

   `File -> Settings -> Tools -> BlackConnect`

1. In `Local Instance (shared between projects)` section:
   1. Check `Start local blackd instance when plugin loads`.
   1. Press the `Detect` button near `Path` input. The plugin should detect the `blackd`
      executable.

1. In `Trigger Settings` section check `Trigger on code reformat` to enable code
   reformatting with _Black_.

1. Format the currently opened file by selecting `Code -> Reformat Code` or using a
   shortcut.

1. Optionally, to run _Black_ on every file save:
   - In `Trigger Settings` section of plugin configuration check
     `Trigger when saving changed files`.

### As external tool

1. Install `black`.

   ```console
   $ pip install black
   ```

1. Locate your `black` installation folder.

   On macOS / Linux / BSD:

   ```console
   $ which black
   /usr/local/bin/black  # possible location
   ```

   On Windows:

   ```console
   $ where black
   %LocalAppData%\Programs\Python\Python36-32\Scripts\black.exe  # possible location
   ```

   Note that if you are using a virtual environment detected by PyCharm, this is an
   unneeded step. In this case the path to `black` is `$PyInterpreterDirectory$/black`.

1. Open External tools in PyCharm/IntelliJ IDEA

   On macOS:

   `PyCharm -> Preferences -> Tools -> External Tools`

   On Windows / Linux / BSD:

   `File -> Settings -> Tools -> External Tools`

1. Click the + icon to add a new external tool with the following values:
   - Name: Black
   - Description: Black is the uncompromising Python code formatter.
   - Program: \<install_location_from_step_2>
   - Arguments: `"$FilePath$"`

1. Format the currently opened file by selecting `Tools -> External Tools -> black`.
   - Alternatively, you can set a keyboard shortcut by navigating to
     `Preferences or Settings -> Keymap -> External Tools -> External Tools - Black`.

### As file watcher

1. Install `black`.

   ```console
   $ pip install black
   ```

1. Locate your `black` installation folder.

   On macOS / Linux / BSD:

   ```console
   $ which black
   /usr/local/bin/black  # possible location
   ```

   On Windows:

   ```console
   $ where black
   %LocalAppData%\Programs\Python\Python36-32\Scripts\black.exe  # possible location
   ```

   Note that if you are using a virtual environment detected by PyCharm, this is an
   unneeded step. In this case the path to `black` is `$PyInterpreterDirectory$/black`.

1. Make sure you have the
   [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) plugin
   installed.
1. Go to `Preferences or Settings -> Tools -> File Watchers` and click `+` to add a new
   watcher:
   - Name: Black
   - File type: Python
   - Scope: Project Files
   - Program: \<install_location_from_step_2>
   - Arguments: `$FilePath$`
   - Output paths to refresh: `$FilePath$`
   - Working directory: `$ProjectFileDir$`

- In Advanced Options
  - Uncheck "Auto-save edited files to trigger the watcher"
  - Uncheck "Trigger the watcher on external changes"

## Wing IDE

Wing IDE supports `black` via **Preference Settings** for system wide settings and
**Project Properties** for per-project or workspace specific settings, as explained in
the Wing documentation on
[Auto-Reformatting](https://wingware.com/doc/edit/auto-reformatting). The detailed
procedure is:

### Prerequistes

- Wing IDE version 8.0+

- Install `black`.

  ```console
  $ pip install black
  ```

- Make sure it runs from the command line, e.g.

  ```console
  $ black --help
  ```

### Preference Settings

If you want Wing IDE to always reformat with `black` for every project, follow these
steps:

1. In menubar navigate to `Edit -> Preferences -> Editor -> Reformatting`.

1. Set **Auto-Reformat** from `disable` (default) to `Line after edit` or
   `Whole files before save`.

1. Set **Reformatter** from `PEP8` (default) to `Black`.

### Project Properties

If you want to just reformat for a specific project and not intervene with Wing IDE
global setting, follow these steps:

1. In menubar navigate to `Project -> Project Properties -> Options`.

1. Set **Auto-Reformat** from `Use Preferences setting` (default) to `Line after edit`
   or `Whole files before save`.

1. Set **Reformatter** from `Use Preferences setting` (default) to `Black`.

## Vim

### Official plugin

Commands and shortcuts:

- `:Black` to format the entire file (ranges not supported);
  - you can optionally pass `target_version=<version>` with the same values as in the
    command line.
- `:BlackUpgrade` to upgrade _Black_ inside the virtualenv;
- `:BlackVersion` to get the current version of _Black_ in use.

Configuration:

- `g:black_fast` (defaults to `0`)
- `g:black_linelength` (defaults to `88`)
- `g:black_skip_string_normalization` (defaults to `0`)
- `g:black_skip_magic_trailing_comma` (defaults to `0`)
- `g:black_virtualenv` (defaults to `~/.vim/black` or `~/.local/share/nvim/black`)
- `g:black_use_virtualenv` (defaults to `1`)
- `g:black_target_version` (defaults to `""`)
- `g:black_quiet` (defaults to `0`)
- `g:black_preview` (defaults to `0`)

#### Installation

This plugin **requires Vim 7.0+ built with Python 3.9+ support**. It needs Python 3.9 to
be able to run _Black_ inside the Vim process which is much faster than calling an
external command.

##### `vim-plug`

To install with [vim-plug](https://github.com/junegunn/vim-plug):

_Black_'s `stable` branch tracks official version updates, and can be used to simply
follow the most recent stable version.

```
Plug 'psf/black', { 'branch': 'stable' }
```

Another option which is a bit more explicit and offers more control is to use
`vim-plug`'s `tag` option with a shell wildcard. This will resolve to the latest tag
which matches the given pattern.

The following matches all stable versions (see the
[Release Process](../contributing/release_process.md) section for documentation of
version scheme used by Black):

```
Plug 'psf/black', { 'tag': '*.*.*' }
```

and the following demonstrates pinning to a specific year's stable style (2022 in this
case):

```
Plug 'psf/black', { 'tag': '22.*.*' }
```

##### Vundle

or with [Vundle](https://github.com/VundleVim/Vundle.vim):

```
Plugin 'psf/black'
```

and execute the following in a terminal:

```console
$ cd ~/.vim/bundle/black
$ git checkout origin/stable -b stable
```

##### Arch Linux

On Arch Linux, the plugin is shipped with the
[`python-black`](https://archlinux.org/packages/extra/any/python-black/) package, so you
can start using it in Vim after install with no additional setup.

##### Vim 8 Native Plugin Management

or you can copy the plugin files from
[plugin/black.vim](https://github.com/psf/black/blob/stable/plugin/black.vim) and
[autoload/black.vim](https://github.com/psf/black/blob/stable/autoload/black.vim).

```
mkdir -p ~/.vim/pack/python/start/black/plugin
mkdir -p ~/.vim/pack/python/start/black/autoload
curl https://raw.githubusercontent.com/psf/black/stable/plugin/black.vim -o ~/.vim/pack/python/start/black/plugin/black.vim
curl https://raw.githubusercontent.com/psf/black/stable/autoload/black.vim -o ~/.vim/pack/python/start/black/autoload/black.vim
```

Let me know if this requires any changes to work with Vim 8's builtin `packadd`, or
Pathogen, and so on.

#### Usage

On first run, the plugin creates its own virtualenv using the right Python version and
automatically installs _Black_. You can upgrade it later by calling `:BlackUpgrade` and
restarting Vim.

If you need to do anything special to make your virtualenv work and install _Black_ (for
example you want to run a version from main), create a virtualenv manually and point
`g:black_virtualenv` to it. The plugin will use it.

If you would prefer to use the system installation of _Black_ rather than a virtualenv,
then add this to your vimrc:

```
let g:black_use_virtualenv = 0
```

Note that the `:BlackUpgrade` command is only usable and useful with a virtualenv, so
when the virtualenv is not in use, `:BlackUpgrade` is disabled. If you need to upgrade
the system installation of _Black_, then use your system package manager or pip--
whatever tool you used to install _Black_ originally.

To run _Black_ on save, add the following lines to `.vimrc` or `init.vim`:

```
augroup black_on_save
  autocmd!
  autocmd BufWritePre *.py Black
augroup end
```

To run _Black_ on a key press (e.g. F9 below), add this:

```
nnoremap <F9> :Black<CR>
```

### With ALE

1. Install [`ale`](https://github.com/dense-analysis/ale)

1. Install `black`

1. Add this to your vimrc:

   ```vim
   let g:ale_fixers = {}
   let g:ale_fixers.python = ['black']
   ```

## Gedit

gedit is the default text editor of the GNOME, Unix like Operating Systems. Open gedit
as

```console
$ gedit <file_name>
```

1. `Go to edit > preferences > plugins`
1. Search for `external tools` and activate it.
1. In `Tools menu -> Manage external tools`
1. Add a new tool using `+` button.
1. Copy the below content to the code window.

```console
#!/bin/bash
Name=$GEDIT_CURRENT_DOCUMENT_NAME
black $Name
```

- Set a keyboard shortcut if you like, Ex. `ctrl-B`
- Save: `Nothing`
- Input: `Nothing`
- Output: `Display in bottom pane` if you like.
- Change the name of the tool if you like.

Use your keyboard shortcut or `Tools -> External Tools` to use your new tool. When you
close and reopen your File, _Black_ will be done with its job.

## Visual Studio Code

- Use the
  [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  ([instructions](https://code.visualstudio.com/docs/python/formatting)).

- Alternatively the pre-release
  [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter)
  extension can be used which runs a [Language Server Protocol](https://langserver.org/)
  server for Black. Formatting is much more responsive using this extension, **but the
  minimum supported version of Black is 22.3.0**.

## SublimeText

For SublimeText 3, use [sublack plugin](https://github.com/jgirardet/sublack). For
higher versions, it is recommended to use [LSP](#python-lsp-server) as documented below.

## Python LSP Server

If your editor supports the [Language Server Protocol](https://langserver.org/) (Atom,
Sublime Text, Visual Studio Code and many more), you can use the
[Python LSP Server](https://github.com/python-lsp/python-lsp-server) with the
[python-lsp-black](https://github.com/python-lsp/python-lsp-black) plugin.

## Atom/Nuclide

Use [python-black](https://atom.io/packages/python-black) or
[formatters-python](https://atom.io/packages/formatters-python).

## Gradle (the build tool)

Use the [Spotless](https://github.com/diffplug/spotless/tree/main/plugin-gradle) plugin.

## Kakoune

Add the following hook to your kakrc, then run _Black_ with `:format`.

```
hook global WinSetOption filetype=python %{
    set-option window formatcmd 'black -q  -'
}
```

## Thonny

Use [Thonny-black-formatter](https://pypi.org/project/thonny-black-formatter/).
````

## File: docs/integrations/github_actions.md
````markdown
# GitHub Actions integration

You can use _Black_ within a GitHub Actions workflow without setting your own Python
environment. Great for enforcing that your code matches the _Black_ code style.

## Compatibility

This action is known to support all GitHub-hosted runner OSes. In addition, only
published versions of _Black_ are supported (i.e. whatever is available on PyPI).

Finally, this action installs _Black_ with the `colorama` extra so the `--color` flag
should work fine.

## Usage

Create a file named `.github/workflows/black.yml` inside your repository with:

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: psf/black@stable
```

We recommend the use of the `@stable` tag, but per version tags also exist if you prefer
that. Note that the action's version you select is independent of the version of _Black_
the action will use.

The version of _Black_ the action will use can be configured via `version` or read from
the `pyproject.toml` file. `version` can be any
[valid version specifier](https://packaging.python.org/en/latest/glossary/#term-Version-Specifier)
or just the version number if you want an exact version. To read the version from the
`pyproject.toml` file instead, set `use_pyproject` to `true`. This will first look into
the `tool.black.required-version` field, then the `dependency-groups` table, then the
`project.dependencies` array and finally the `project.optional-dependencies` table. The
action defaults to the latest release available on PyPI. Only versions available from
PyPI are supported, so no commit SHAs or branch names.

If you want to include Jupyter Notebooks, _Black_ must be installed with the `jupyter`
extra. Installing the extra and including Jupyter Notebook files can be configured via
`jupyter` (default is `false`).

You can also configure the arguments passed to _Black_ via `options` (defaults to
`'--check --diff'`) and `src` (default is `'.'`). Please note that the
[`--check` flag](labels/exit-code) is required so that the workflow fails if _Black_
finds files that need to be formatted.

Here's an example configuration:

```yaml
- uses: psf/black@stable
  with:
    options: "--check --verbose"
    src: "./src"
    jupyter: true
    version: "21.5b1"
```

If you want to match versions covered by Black's
[stability policy](labels/stability-policy), you can use the compatible release operator
(`~=`):

```yaml
- uses: psf/black@stable
  with:
    options: "--check --verbose"
    src: "./src"
    version: "~= 22.0"
```

If you want to read the version from `pyproject.toml`, set `use_pyproject` to `true`.
Note that this requires Python >= 3.11, so using the setup-python action may be
required, for example:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.13"
- uses: psf/black@stable
  with:
    options: "--check --verbose"
    src: "./src"
    use_pyproject: true
```
````

## File: docs/integrations/index.md
````markdown
# Integrations

```{toctree}
---
hidden:
---

editors
github_actions
source_version_control
```

_Black_ can be integrated into many environments, providing a better and smoother
experience. Documentation for integrating _Black_ with a tool can be found for the
following areas:

- {doc}`Editor / IDE <./editors>`
- {doc}`GitHub Actions <./github_actions>`
- {doc}`Source version control <./source_version_control>`

Editors and tools not listed will require external contributions.

Patches welcome! ✨ 🍰 ✨

Any tool can pipe code through _Black_ using its stdio mode (just
[use `-` as the file name](https://www.tldp.org/LDP/abs/html/special-chars.html#DASHREF2)).
The formatted code will be returned on stdout (unless `--check` was passed). _Black_
will still emit messages on stderr but that shouldn't affect your use case.

This can be used for example with PyCharm's or IntelliJ's
[File Watchers](https://www.jetbrains.com/help/pycharm/file-watchers.html).
````

## File: docs/integrations/source_version_control.md
````markdown
# Version control integration

Use [pre-commit](https://pre-commit.com/). Once you
[have it installed](https://pre-commit.com/#install), add this to the
`.pre-commit-config.yaml` in your repository:

```yaml
repos:
  # Using this mirror lets us use mypyc-compiled black, which is about 2x faster
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.1.0
    hooks:
      - id: black
        # It is recommended to specify the latest version of Python
        # supported by your project here, or alternatively use
        # pre-commit's default_language_version, see
        # https://pre-commit.com/#top_level-default_language_version
        language_version: python3.11
```

Feel free to switch out the `rev` value to a different version of Black.

Note if you'd like to use a specific commit in `rev`, you'll need to swap the repo
specified from the mirror to https://github.com/psf/black. We discourage the use of
branches or other mutable refs since the hook [won't auto update as you may
expect][pre-commit-mutable-rev].

## Jupyter Notebooks

There is an alternate hook `black-jupyter` that expands the targets of `black` to
include Jupyter Notebooks. To use this hook, simply replace the hook's `id: black` with
`id: black-jupyter` in the `.pre-commit-config.yaml`:

```yaml
repos:
  # Using this mirror lets us use mypyc-compiled black, which is about 2x faster
  - repo: https://github.com/psf/black-pre-commit-mirror
    rev: 25.1.0
    hooks:
      - id: black-jupyter
        # It is recommended to specify the latest version of Python
        # supported by your project here, or alternatively use
        # pre-commit's default_language_version, see
        # https://pre-commit.com/#top_level-default_language_version
        language_version: python3.11
```

```{note}
The `black-jupyter` hook became available in version 21.8b0.
```

[pre-commit-mutable-rev]:
  https://pre-commit.com/#using-the-latest-version-for-a-repository
````

## File: docs/the_black_code_style/current_style.md
````markdown
# The _Black_ code style

## Code style

_Black_ aims for consistency, generality, readability and reducing git diffs. Similar
language constructs are formatted with similar rules. Style configuration options are
deliberately limited and rarely added. Previous formatting is taken into account as
little as possible, with rare exceptions like the magic trailing comma. The coding style
used by _Black_ can be viewed as a strict subset of PEP 8.

This document describes the current formatting style. If you're interested in trying out
where the style is heading, see [future style](./future_style.md) and try running
`black --preview`.

### How _Black_ wraps lines

_Black_ ignores previous formatting and applies uniform horizontal and vertical
whitespace to your code. The rules for horizontal whitespace can be summarized as: do
whatever makes `pycodestyle` happy.

As for vertical whitespace, _Black_ tries to render one full expression or simple
statement per line. If this fits the allotted line length, great.

```py3
# in:

j = [1,
     2,
     3
]

# out:

j = [1, 2, 3]
```

If not, _Black_ will look at the contents of the first outer matching brackets and put
that in a separate indented line.

```py3
# in:

ImportantClass.important_method(exc, limit, lookup_lines, capture_locals, extra_argument)

# out:

ImportantClass.important_method(
    exc, limit, lookup_lines, capture_locals, extra_argument
)
```

If that still doesn't fit the bill, it will decompose the internal expression further
using the same rule, indenting matching brackets every time. If the contents of the
matching brackets pair are comma-separated (like an argument list, or a dict literal,
and so on) then _Black_ will first try to keep them on the same line with the matching
brackets. If that doesn't work, it will put all of them in separate lines.

```py3
# in:

def very_important_function(template: str, *variables, file: os.PathLike, engine: str, header: bool = True, debug: bool = False):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, 'w') as f:
        ...

# out:

def very_important_function(
    template: str,
    *variables,
    file: os.PathLike,
    engine: str,
    header: bool = True,
    debug: bool = False,
):
    """Applies `variables` to the `template` and writes to `file`."""
    with open(file, "w") as f:
        ...
```

If a data structure literal (tuple, list, set, dict) or a line of "from" imports cannot
fit in the allotted length, it's always split into one element per line. This minimizes
diffs as well as enables readers of code to find which commit introduced a particular
entry. This also makes _Black_ compatible with
[isort](../guides/using_black_with_other_tools.md#isort) with the ready-made `black`
profile or manual configuration.

You might have noticed that closing brackets are always dedented and that a trailing
comma is always added. Such formatting produces smaller diffs; when you add or remove an
element, it's always just one line. Also, having the closing bracket dedented provides a
clear delimiter between two distinct sections of the code that otherwise share the same
indentation level (like the arguments list and the docstring in the example above).

(labels/why-no-backslashes)=

_Black_ prefers parentheses over backslashes, and will remove backslashes if found.

```py3
# in:

if some_short_rule1 \
  and some_short_rule2:
      ...

# out:

if some_short_rule1 and some_short_rule2:
  ...


# in:

if some_long_rule1 \
  and some_long_rule2:
    ...

# out:

if (
    some_long_rule1
    and some_long_rule2
):
    ...

```

Backslashes and multiline strings are one of the two places in the Python grammar that
break significant indentation. You never need backslashes, they are used to force the
grammar to accept breaks that would otherwise be parse errors. That makes them confusing
to look at and brittle to modify. This is why _Black_ always gets rid of them.

If you're reaching for backslashes, that's a clear signal that you can do better if you
slightly refactor your code. I hope some of the examples above show you that there are
many ways in which you can do it.

(labels/line-length)=

### Line length

You probably noticed the peculiar default line length. _Black_ defaults to 88 characters
per line, which happens to be 10% over 80. This number was found to produce
significantly shorter files than sticking with 80 (the most popular), or even 79 (used
by the standard library). In general,
[90-ish seems like the wise choice](https://youtu.be/wf-BqAjZb8M?t=260).

If you're paid by the lines of code you write, you can pass `--line-length` with a lower
number. _Black_ will try to respect that. However, sometimes it won't be able to without
breaking other rules. In those rare cases, auto-formatted code will exceed your allotted
limit.

You can also increase it, but remember that people with sight disabilities find it
harder to work with line lengths exceeding 100 characters. It also adversely affects
side-by-side diff review on typical screen resolutions. Long lines also make it harder
to present code neatly in documentation or talk slides.

#### Flake8 and other linters

See [Using _Black_ with other tools](../guides/using_black_with_other_tools.md) about
linter compatibility.

### Empty lines

_Black_ avoids spurious vertical whitespace. This is in the spirit of PEP 8 which says
that in-function vertical whitespace should only be used sparingly.

_Black_ will allow single empty lines inside functions, and single and double empty
lines on module level left by the original editors, except when they're within
parenthesized expressions. Since such expressions are always reformatted to fit minimal
space, this whitespace is lost.

```python
# in:

def function(
    some_argument: int,

    other_argument: int = 5,
) -> EmptyLineInParenWillBeDeleted:



    print("One empty line above me will be kept!")

def this_is_okay_too():
    print("No empty line here")
# out:

def function(
    some_argument: int,
    other_argument: int = 5,
) -> EmptyLineInParenWillBeDeleted:

    print("One empty line above me will be kept!")


def this_is_okay_too():
    print("No empty line here")
```

It will also insert proper spacing before and after function definitions. It's one line
before and after inner functions and two lines before and after module-level functions
and classes. _Black_ will not put empty lines between function/class definitions and
standalone comments that immediately precede the given function/class.

_Black_ will enforce single empty lines between a class-level docstring and the first
following field or method. This conforms to
[PEP 257](https://www.python.org/dev/peps/pep-0257/#multi-line-docstrings).

_Black_ won't insert empty lines after function docstrings unless that empty line is
required due to an inner function starting immediately after.

### Comments

_Black_ does not format comment contents, but it enforces two spaces between code and a
comment on the same line, and a space before the comment text begins. Some types of
comments that require specific spacing rules are respected: shebangs (`#! comment`), doc
comments (`#: comment`), section comments with long runs of hashes, and Spyder cells.
Non-breaking spaces after hashes are also preserved. Comments may sometimes be moved
because of formatting changes, which can break tools that assign special meaning to
them. See [AST before and after formatting](#ast-before-and-after-formatting) for more
discussion.

### Trailing commas

_Black_ will add trailing commas to expressions that are split by comma where each
element is on its own line. This includes function signatures.

One exception to adding trailing commas is function signatures containing `*`, `*args`,
or `**kwargs`. In this case a trailing comma is only safe to use on Python 3.6. _Black_
will detect if your file is already 3.6+ only and use trailing commas in this situation.
If you wonder how it knows, it looks for f-strings and existing use of trailing commas
in function signatures that have stars in them. In other words, if you'd like a trailing
comma in this situation and _Black_ didn't recognize it was safe to do so, put it there
manually and _Black_ will keep it.

A pre-existing trailing comma informs _Black_ to always explode contents of the current
bracket pair into one item per line. Read more about this in the
[Pragmatism](#pragmatism) section below.

(labels/strings)=

### Strings

_Black_ prefers double quotes (`"` and `"""`) over single quotes (`'` and `'''`). It
will replace the latter with the former as long as it does not result in more backslash
escapes than before.

_Black_ also standardizes string prefixes. Prefix characters are made lowercase with the
exception of [capital "R" prefixes](#rstrings-and-rstrings), unicode literal markers
(`u`) are removed because they are meaningless in Python 3, and in the case of multiple
characters "r" is put first as in spoken language: "raw f-string".

Another area where Python allows multiple ways to format a string is escape sequences.
For example, `"\uabcd"` and `"\uABCD"` evaluate to the same string. _Black_ normalizes
such escape sequences to lowercase, but uses uppercase for `\N` named character escapes,
such as `"\N{MEETEI MAYEK LETTER HUK}"`.

The main reason to standardize on a single form of quotes is aesthetics. Having one kind
of quotes everywhere reduces reader distraction. It will also enable a future version of
_Black_ to merge consecutive string literals that ended up on the same line (see
[#26](https://github.com/psf/black/issues/26) for details).

Why settle on double quotes? They anticipate apostrophes in English text. They match the
docstring standard described in
[PEP 257](https://www.python.org/dev/peps/pep-0257/#what-is-a-docstring). An empty
string in double quotes (`""`) is impossible to confuse with a one double-quote
regardless of fonts and syntax highlighting used. On top of this, double quotes for
strings are consistent with C which Python interacts a lot with.

On certain keyboard layouts like US English, typing single quotes is a bit easier than
double quotes. The latter requires use of the Shift key. My recommendation here is to
keep using whatever is faster to type and let _Black_ handle the transformation.

If you are adopting _Black_ in a large project with pre-existing string conventions
(like the popular
["single quotes for data, double quotes for human-readable strings"](https://stackoverflow.com/a/56190)),
you can pass `--skip-string-normalization` on the command line. This is meant as an
adoption helper, avoid using this for new projects.

_Black_ also processes docstrings. Firstly the indentation of docstrings is corrected
for both quotations and the text within, although relative indentation in the text is
preserved. Superfluous trailing whitespace on each line and unnecessary new lines at the
end of the docstring are removed. All leading tabs are converted to spaces, but tabs
inside text are preserved. Whitespace leading and trailing one-line docstrings is
removed.

### Numeric literals

_Black_ standardizes most numeric literals to use lowercase letters for the syntactic
parts and uppercase letters for the digits themselves: `0xAB` instead of `0XAB` and
`1e10` instead of `1E10`.

### Line breaks & binary operators

_Black_ will break a line before a binary operator when splitting a block of code over
multiple lines. This is so that _Black_ is compliant with the recent changes in the
[PEP 8](https://www.python.org/dev/peps/pep-0008/#should-a-line-break-before-or-after-a-binary-operator)
style guide, which emphasizes that this approach improves readability.

Almost all operators will be surrounded by single spaces, the only exceptions are unary
operators (`+`, `-`, and `~`), and power operators when both operands are simple. For
powers, an operand is considered simple if it's only a NAME, numeric CONSTANT, or
attribute access (chained attribute access is allowed), with or without a preceding
unary operator.

```python
# For example, these won't be surrounded by whitespace
a = x**y
b = config.base**5.2
c = config.base**runtime.config.exponent
d = 2**5
e = 2**~5

# ... but these will be surrounded by whitespace
f = 2 ** get_exponent()
g = get_x() ** get_y()
h = config['base'] ** 2
```

### Slices

PEP 8
[recommends](https://www.python.org/dev/peps/pep-0008/#whitespace-in-expressions-and-statements)
to treat `:` in slices as a binary operator with the lowest priority, and to leave an
equal amount of space on either side, except if a parameter is omitted (e.g.
`ham[1 + 1 :]`). It recommends no spaces around `:` operators for "simple expressions"
(`ham[lower:upper]`), and extra space for "complex expressions"
(`ham[lower : upper + offset]`). _Black_ treats anything more than variable names as
"complex" (`ham[lower : upper + 1]`). It also states that for extended slices, both `:`
operators have to have the same amount of spacing, except if a parameter is omitted
(`ham[1 + 1 ::]`). _Black_ enforces these rules consistently.

This behaviour may raise `E203 whitespace before ':'` warnings in style guide
enforcement tools like Flake8. Since `E203` is not PEP 8 compliant, you should tell
Flake8 to ignore these warnings.

### Parentheses

Some parentheses are optional in the Python grammar. Any expression can be wrapped in a
pair of parentheses to form an atom. There are a few interesting cases:

- `if (...):`
- `while (...):`
- `for (...) in (...):`
- `assert (...), (...)`
- `from X import (...)`
- assignments like:
  - `target = (...)`
  - `target: type = (...)`
  - `some, *un, packing = (...)`
  - `augmented += (...)`

In those cases, parentheses are removed when the entire statement fits in one line, or
if the inner expression doesn't have any delimiters to further split on. If there is
only a single delimiter and the expression starts or ends with a bracket, the
parentheses can also be successfully omitted since the existing bracket pair will
organize the expression neatly anyway. Otherwise, the parentheses are added.

Please note that _Black_ does not add or remove any additional nested parentheses that
you might want to have for clarity or further code organization. For example those
parentheses are not going to be removed:

```py3
return not (this or that)
decision = (maybe.this() and values > 0) or (maybe.that() and values < 0)
```

### Call chains

Some popular APIs, like ORMs, use call chaining. This API style is known as a
[fluent interface](https://en.wikipedia.org/wiki/Fluent_interface). _Black_ formats
those by treating dots that follow a call or an indexing operation like a very low
priority delimiter. It's easier to show the behavior than to explain it. Look at the
example:

```py3
def example(session):
    result = (
        session.query(models.Customer.id)
        .filter(
            models.Customer.account_id == account_id,
            models.Customer.email == email_address,
        )
        .order_by(models.Customer.id.asc())
        .all()
    )
```

### Typing stub files

PEP 484 describes the syntax for type hints in Python. One of the use cases for typing
is providing type annotations for modules which cannot contain them directly (they might
be written in C, or they might be third-party, or their implementation may be overly
dynamic, and so on).

To solve this,
[stub files with the `.pyi` file extension](https://www.python.org/dev/peps/pep-0484/#stub-files)
can be used to describe typing information for an external module. Those stub files omit
the implementation of classes and functions they describe, instead they only contain the
structure of the file (listing globals, functions, and classes with their members). The
recommended code style for those files is more terse than PEP 8:

- prefer `...` on the same line as the class/function signature;
- avoid vertical whitespace between consecutive module-level functions, names, or
  methods and fields within a single class;
- use a single blank line between top-level class definitions, or none if the classes
  are very small.

_Black_ enforces the above rules. There are additional guidelines for formatting `.pyi`
file that are not enforced yet but might be in a future version of the formatter:

- prefer `...` over `pass`;
- avoid using string literals in type annotations, stub files support forward references
  natively (like Python 3.7 code with `from __future__ import annotations`);
- use variable annotations instead of type comments, even for stubs that target older
  versions of Python.

### Line endings

_Black_ will normalize line endings (`\n` or `\r\n`) based on the first line ending of
the file.

### Form feed characters

_Black_ will retain form feed characters on otherwise empty lines at the module level.
Only one form feed is retained for a group of consecutive empty lines. Where there are
two empty lines in a row, the form feed is placed on the second line.

## Pragmatism

Early versions of _Black_ used to be absolutist in some respects. They took after its
initial author. This was fine at the time as it made the implementation simpler and
there were not many users anyway. Not many edge cases were reported. As a mature tool,
_Black_ does make some exceptions to rules it otherwise holds. This section documents
what those exceptions are and why this is the case.

(labels/magic-trailing-comma)=

### The magic trailing comma

_Black_ in general does not take existing formatting into account.

However, there are cases where you put a short collection or function call in your code
but you anticipate it will grow in the future.

For example:

```py3
TRANSLATIONS = {
    "en_us": "English (US)",
    "pl_pl": "polski",
}
```

Early versions of _Black_ used to ruthlessly collapse those into one line (it fits!).
Now, you can communicate that you don't want that by putting a trailing comma in the
collection yourself. When you do, _Black_ will know to always explode your collection
into one item per line.

How do you make it stop? Just delete that trailing comma and _Black_ will collapse your
collection into one line if it fits.

If you must, you can recover the behaviour of early versions of _Black_ with the option
`--skip-magic-trailing-comma` / `-C`.

### r"strings" and R"strings"

_Black_ normalizes string quotes as well as string prefixes, making them lowercase. One
exception to this rule is r-strings. It turns out that the very popular
[MagicPython](https://github.com/MagicStack/MagicPython/) syntax highlighter, used by
default by (among others) GitHub and Visual Studio Code, differentiates between
r-strings and R-strings. The former are syntax highlighted as regular expressions while
the latter are treated as true raw strings with no special semantics.

(labels/ast-changes)=

### AST before and after formatting

When run with `--safe` (the default), _Black_ checks that the code before and after is
semantically equivalent. This check is done by comparing the AST of the source with the
AST of the target. There are three limited cases in which the AST does differ:

1. _Black_ cleans up leading and trailing whitespace of docstrings, re-indenting them if
   needed. It's been one of the most popular user-reported features for the formatter to
   fix whitespace issues with docstrings. While the result is technically an AST
   difference, due to the various possibilities of forming docstrings, all real-world
   uses of docstrings that we're aware of sanitize indentation and leading/trailing
   whitespace anyway.

1. _Black_ manages optional parentheses for some statements. In the case of the `del`
   statement, presence of wrapping parentheses or lack of thereof changes the resulting
   AST but is semantically equivalent in the interpreter.

1. _Black_ might move comments around, which includes type comments. Those are part of
   the AST as of Python 3.8. While the tool implements a number of special cases for
   those comments, there is no guarantee they will remain where they were in the source.
   Note that this doesn't change runtime behavior of the source code.

To put things in perspective, the code equivalence check is a feature of _Black_ which
other formatters don't implement at all. It is of crucial importance to us to ensure
code behaves the way it did before it got reformatted. We treat this as a feature and
there are no plans to relax this in the future. The exceptions enumerated above stem
from either user feedback or implementation details of the tool. In each case we made
due diligence to ensure that the AST divergence is of no practical consequence.
````

## File: docs/the_black_code_style/future_style.md
````markdown
# The (future of the) Black code style

## Preview style

(labels/preview-style)=

Experimental, potentially disruptive style changes are gathered under the `--preview`
CLI flag. At the end of each year, these changes may be adopted into the default style,
as described in [The Black Code Style](index.md). Because the functionality is
experimental, feedback and issue reports are highly encouraged!

In the past, the preview style included some features with known bugs, so that we were
unable to move these features to the stable style. Therefore, such features are now
moved to the `--unstable` style. All features in the `--preview` style are expected to
make it to next year's stable style; features in the `--unstable` style will be
stabilized only if issues with them are fixed. If bugs are discovered in a `--preview`
feature, it is demoted to the `--unstable` style. To avoid thrash when a feature is
demoted from the `--preview` to the `--unstable` style, users can use the
`--enable-unstable-feature` flag to enable specific unstable features.

(labels/preview-features)=

Currently, the following features are included in the preview style:

- `always_one_newline_after_import`: Always force one blank line after import
  statements, except when the line after the import is a comment or an import statement
- `wrap_long_dict_values_in_parens`: Add parentheses around long values in dictionaries
  ([see below](labels/wrap-long-dict-values))
- `fix_fmt_skip_in_one_liners`: Fix `# fmt: skip` behaviour on one-liner declarations,
  such as `def foo(): return "mock"  # fmt: skip`, where previously the declaration
  would have been incorrectly collapsed.

(labels/unstable-features)=

The unstable style additionally includes the following features:

- `string_processing`: split long string literals and related changes
  ([see below](labels/string-processing))
- `multiline_string_handling`: more compact formatting of expressions involving
  multiline strings ([see below](labels/multiline-string-handling))
- `hug_parens_with_braces_and_square_brackets`: more compact formatting of nested
  brackets ([see below](labels/hug-parens))

(labels/wrap-long-dict-values)=

### Improved parentheses management in dicts

For dict literals with long values, they are now wrapped in parentheses. Unnecessary
parentheses are now removed. For example:

```python
my_dict = {
    "a key in my dict": a_very_long_variable
    * and_a_very_long_function_call()
    / 100000.0,
    "another key": (short_value),
}
```

will be changed to:

```python
my_dict = {
    "a key in my dict": (
        a_very_long_variable * and_a_very_long_function_call() / 100000.0
    ),
    "another key": short_value,
}
```

(labels/hug-parens)=

### Improved multiline dictionary and list indentation for sole function parameter

For better readability and less verticality, _Black_ now pairs parentheses ("(", ")")
with braces ("{", "}") and square brackets ("[", "]") on the same line. For example:

```python
foo(
    [
        1,
        2,
        3,
    ]
)

nested_array = [
    [
        1,
        2,
        3,
    ]
]
```

will be changed to:

```python
foo([
    1,
    2,
    3,
])

nested_array = [[
    1,
    2,
    3,
]]
```

This also applies to list and dictionary unpacking:

```python
foo(
    *[
        a_long_function_name(a_long_variable_name)
        for a_long_variable_name in some_generator
    ]
)
```

will become:

```python
foo(*[
    a_long_function_name(a_long_variable_name)
    for a_long_variable_name in some_generator
])
```

You can use a magic trailing comma to avoid this compacting behavior; by default,
_Black_ will not reformat the following code:

```python
foo(
    [
        1,
        2,
        3,
    ],
)
```

(labels/string-processing)=

### Improved string processing

_Black_ will split long string literals and merge short ones. Parentheses are used where
appropriate. When split, parts of f-strings that don't need formatting are converted to
plain strings. f-strings will not be merged if they contain internal quotes and it would
change their quotation mark style. User-made splits are respected when they do not
exceed the line length limit. Line continuation backslashes are converted into
parenthesized strings. Unnecessary parentheses are stripped. The stability and status of
this feature is tracked in [this issue](https://github.com/psf/black/issues/2188).

(labels/multiline-string-handling)=

### Improved multiline string handling

_Black_ is smarter when formatting multiline strings, especially in function arguments,
to avoid introducing extra line breaks. Previously, it would always consider multiline
strings as not fitting on a single line. With this new feature, _Black_ looks at the
context around the multiline string to decide if it should be inlined or split to a
separate line. For example, when a multiline string is passed to a function, _Black_
will only split the multiline string if a line is too long or if multiple arguments are
being passed.

For example, _Black_ will reformat

```python
textwrap.dedent(
    """\
    This is a
    multiline string
"""
)
```

to:

```python
textwrap.dedent("""\
    This is a
    multiline string
""")
```

And:

```python
MULTILINE = """
foobar
""".replace(
    "\n", ""
)
```

to:

```python
MULTILINE = """
foobar
""".replace("\n", "")
```

Implicit multiline strings are special, because they can have inline comments. Strings
without comments are merged, for example

```python
s = (
    "An "
    "implicit "
    "multiline "
    "string"
)
```

becomes

```python
s = "An implicit multiline string"
```

A comment on any line of the string (or between two string lines) will block the
merging, so

```python
s = (
    "An "  # Important comment concerning just this line
    "implicit "
    "multiline "
    "string"
)
```

and

```python
s = (
    "An "
    "implicit "
    # Comment in between
    "multiline "
    "string"
)
```

will not be merged. Having the comment after or before the string lines (but still
inside the parens) will merge the string. For example

```python
s = (  # Top comment
    "An "
    "implicit "
    "multiline "
    "string"
    # Bottom comment
)
```

becomes

```python
s = (  # Top comment
    "An implicit multiline string"
    # Bottom comment
)
```
````

## File: docs/the_black_code_style/index.md
````markdown
# The Black Code Style

```{toctree}
---
hidden:
---

Current style <current_style>
Future style <future_style>
```

_Black_ is a PEP 8 compliant opinionated formatter with its own style.

While keeping the style unchanged throughout releases has always been a goal, the
_Black_ code style isn't set in stone. It evolves to accommodate for new features in the
Python language and, occasionally, in response to user feedback. Large-scale style
preferences presented in {doc}`current_style` are very unlikely to change, but minor
style aspects and details might change according to the stability policy presented
below. Ongoing style considerations are tracked on GitHub with the
[style](https://github.com/psf/black/labels/T%3A%20style) issue label.

(labels/stability-policy)=

## Stability Policy

The following policy applies for the _Black_ code style, in non pre-release versions of
_Black_:

- If code has been formatted with _Black_, it will remain unchanged when formatted with
  the same options using any other release in the same calendar year.

  This means projects can safely use `black ~= 22.0` without worrying about formatting
  changes disrupting their project in 2022. We may still fix bugs where _Black_ crashes
  on some code, and make other improvements that do not affect formatting.

  In rare cases, we may make changes affecting code that has not been previously
  formatted with _Black_. For example, we have had bugs where we accidentally removed
  some comments. Such bugs can be fixed without breaking the stability policy.

- The first release in a new calendar year _may_ contain formatting changes, although
  these will be minimised as much as possible. This is to allow for improved formatting
  enabled by newer Python language syntax as well as due to improvements in the
  formatting logic.

- The `--preview` and `--unstable` flags are exempt from this policy. There are no
  guarantees around the stability of the output with these flags passed into _Black_.
  They are intended for allowing experimentation with proposed changes to the _Black_
  code style. The `--preview` style at the end of a year should closely match the stable
  style for the next year, but we may always make changes.

Documentation for both the current and future styles can be found:

- {doc}`current_style`
- {doc}`future_style`
````

## File: docs/usage_and_configuration/black_as_a_server.md
````markdown
# Black as a server (blackd)

`blackd` is a small HTTP server that exposes _Black_'s functionality over a simple
protocol. The main benefit of using it is to avoid the cost of starting up a new _Black_
process every time you want to blacken a file.

```{warning}
`blackd` should not be run as a publicly accessible server as there are no security
precautions in place to prevent abuse. **It is intended for local use only**.
```

## Usage

`blackd` is not packaged alongside _Black_ by default because it has additional
dependencies. You will need to execute `pip install 'black[d]'` to install it.

You can start the server on the default port, binding only to the local interface by
running `blackd`. You will see a single line mentioning the server's version, and the
host and port it's listening on. `blackd` will then print an access log similar to most
web servers on standard output, merged with any exception traces caused by invalid
formatting requests.

`blackd` provides even less options than _Black_. You can see them by running
`blackd --help`:

```{program-output} blackd --help

```

There is no official `blackd` client tool (yet!). You can test that blackd is working
using `curl`:

```sh
blackd --bind-port 9090 &  # or let blackd choose a port
curl -s -XPOST "localhost:9090" -d "print('valid')"
```

## Protocol

`blackd` only accepts `POST` requests at the `/` path. The body of the request should
contain the python source code to be formatted, encoded according to the `charset` field
in the `Content-Type` request header. If no `charset` is specified, `blackd` assumes
`UTF-8`.

There are a few HTTP headers that control how the source code is formatted. These
correspond to command line flags for _Black_. There is one exception to this:
`X-Protocol-Version` which if present, should have the value `1`, otherwise the request
is rejected with `HTTP 501` (Not Implemented).

The headers controlling how source code is formatted are:

- `X-Line-Length`: corresponds to the `--line-length` command line flag.
- `X-Skip-Source-First-Line`: corresponds to the `--skip-source-first-line` command line
  flag. If present and its value is not an empty string, the first line of the source
  code will be ignored.
- `X-Skip-String-Normalization`: corresponds to the `--skip-string-normalization`
  command line flag. If present and its value is not the empty string, no string
  normalization will be performed.
- `X-Skip-Magic-Trailing-Comma`: corresponds to the `--skip-magic-trailing-comma`
  command line flag. If present and its value is not an empty string, trailing commas
  will not be used as a reason to split lines.
- `X-Preview`: corresponds to the `--preview` command line flag. If present and its
  value is not an empty string, experimental and potentially disruptive style changes
  will be used.
- `X-Unstable`: corresponds to the `--unstable` command line flag. If present and its
  value is not an empty string, experimental style changes that are known to be buggy
  will be used.
- `X-Enable-Unstable-Feature`: corresponds to the `--enable-unstable-feature` flag. The
  contents of the flag must be a comma-separated list of unstable features to be
  enabled. Example: `X-Enable-Unstable-Feature: feature1, feature2`.
- `X-Fast-Or-Safe`: if set to `fast`, `blackd` will act as _Black_ does when passed the
  `--fast` command line flag.
- `X-Python-Variant`: if set to `pyi`, `blackd` will act as _Black_ does when passed the
  `--pyi` command line flag. Otherwise, its value must correspond to a Python version or
  a set of comma-separated Python versions, optionally prefixed with `py`. For example,
  to request code that is compatible with Python 3.5 and 3.6, set the header to
  `py3.5,py3.6`.
- `X-Diff`: corresponds to the `--diff` command line flag. If present, a diff of the
  formats will be output.

If any of these headers are set to invalid values, `blackd` returns a `HTTP 400` error
response, mentioning the name of the problematic header in the message body.

Apart from the above, `blackd` can produce the following response codes:

- `HTTP 204`: If the input is already well-formatted. The response body is empty.
- `HTTP 200`: If formatting was needed on the input. The response body contains the
  blackened Python code, and the `Content-Type` header is set accordingly.
- `HTTP 400`: If the input contains a syntax error. Details of the error are returned in
  the response body.
- `HTTP 500`: If there was any other kind of error while trying to format the input. The
  response body contains a textual representation of the error.

The response headers include a `X-Black-Version` header containing the version of
_Black_.
````

## File: docs/usage_and_configuration/black_docker_image.md
````markdown
# Black Docker image

Official _Black_ Docker images are available on
[Docker Hub](https://hub.docker.com/r/pyfound/black).

_Black_ images with the following tags are available:

- release numbers, e.g. `21.5b2`, `21.6b0`, `21.7b0` etc.\
  ℹ Recommended for users who want to use a particular version of _Black_.
- `latest_release` - tag created when a new version of _Black_ is released.\
  ℹ Recommended for users who want to use released versions of _Black_. It maps to
  [the latest release](https://github.com/psf/black/releases/latest) of _Black_.
- `latest_prerelease` - tag created when a new alpha (prerelease) version of _Black_ is
  released.\
  ℹ Recommended for users who want to preview or test alpha versions of _Black_. Note
  that the most recent release may be newer than any prerelease, because no prereleases
  are created before most releases.
- `latest` - tag used for the newest image of _Black_.\
  ℹ Recommended for users who always want to use the latest version of _Black_, even
  before it is released.

There is one more tag used for _Black_ Docker images - `latest_non_release`. It is
created for all unreleased
[commits on the `main` branch](https://github.com/psf/black/commits/main). This tag is
not meant to be used by external users.

From version 23.11.0 the Docker image installs a compiled black into the image.

## Usage

A permanent container doesn't have to be created to use _Black_ as a Docker image. It's
enough to run _Black_ commands for the chosen image denoted as `:tag`. In the below
examples, the `latest_release` tag is used. If `:tag` is omitted, the `latest` tag will
be used.

More about _Black_ usage can be found in
[Usage and Configuration: The basics](./the_basics.md).

### Check Black version

```console
$ docker run --rm pyfound/black:latest_release black --version
```

### Check code

```console
$ docker run --rm --volume $(pwd):/src --workdir /src pyfound/black:latest_release black --check .
```

_Remark_: besides [regular _Black_ exit codes](./the_basics.md) returned by `--check`
option, [Docker exit codes](https://docs.docker.com/engine/reference/run/#exit-status)
should also be considered.
````

## File: docs/usage_and_configuration/file_collection_and_discovery.md
````markdown
# File collection and discovery

You can directly pass _Black_ files, but you can also pass directories and _Black_ will
walk them, collecting files to format. It determines what files to format or skip
automatically using the inclusion and exclusion regexes and as well their modification
time.

## Ignoring unmodified files

_Black_ remembers files it has already formatted, unless the `--diff` flag is used or
code is passed via standard input. This information is stored per-user. The exact
location of the file depends on the _Black_ version and the system on which _Black_ is
run. The file is non-portable. The standard location on common operating systems is:

- Windows:
  `C:\\Users\<username>\AppData\Local\black\black\Cache\<version>\cache.<line-length>.<file-mode>.pickle`
- macOS:
  `/Users/<username>/Library/Caches/black/<version>/cache.<line-length>.<file-mode>.pickle`
- Linux:
  `/home/<username>/.cache/black/<version>/cache.<line-length>.<file-mode>.pickle`

`file-mode` is an int flag that determines whether the file was formatted as 3.6+ only,
as .pyi, and whether string normalization was omitted.

To override the location of these files on all systems, set the environment variable
`BLACK_CACHE_DIR` to the preferred location. Alternatively on macOS and Linux, set
`XDG_CACHE_HOME` to your preferred location. For example, if you want to put the cache
in the directory you're running _Black_ from, set `BLACK_CACHE_DIR=.cache/black`.
_Black_ will then write the above files to `.cache/black`. Note that `BLACK_CACHE_DIR`
will take precedence over `XDG_CACHE_HOME` if both are set.

## .gitignore

If `--exclude` is not set, _Black_ will automatically ignore files and directories in
`.gitignore` file(s), if present.

If you want _Black_ to continue using `.gitignore` while also configuring the exclusion
rules, please use `--extend-exclude`.
````

## File: docs/usage_and_configuration/index.md
````markdown
# Usage and Configuration

```{toctree}
---
hidden:
---

the_basics
file_collection_and_discovery
black_as_a_server
black_docker_image
```

Sometimes, running _Black_ with its defaults and passing filepaths to it just won't cut
it. Passing each file using paths will become burdensome, and maybe you would like
_Black_ to not touch your files and just output diffs. And yes, you _can_ tweak certain
parts of _Black_'s style, but please know that configurability in this area is
purposefully limited.

Using many of these more advanced features of _Black_ will require some configuration.
Configuration that will either live on the command line or in a TOML configuration file.

This section covers features of _Black_ and configuring _Black_ in detail:

- {doc}`The basics <./the_basics>`
- {doc}`File collection and discovery <file_collection_and_discovery>`
- {doc}`Black as a server (blackd) <./black_as_a_server>`
- {doc}`Black Docker image <./black_docker_image>`
````

## File: docs/usage_and_configuration/the_basics.md
````markdown
# The basics

Foundational knowledge on using and configuring Black.

_Black_ is a well-behaved Unix-style command-line tool:

- it does nothing if it finds no sources to format;
- it will read from standard input and write to standard output if `-` is used as the
  filename;
- it only outputs messages to users on standard error;
- exits with code 0 unless an internal error occurred or a CLI option prompted it.

## Usage

_Black_ will reformat entire files in place. To get started right away with sensible
defaults:

```sh
black {source_file_or_directory}
```

You can run _Black_ as a package if running it as a script doesn't work:

```sh
python -m black {source_file_or_directory}
```

### Ignoring sections

Black will not reformat lines that contain `# fmt: skip` or blocks that start with
`# fmt: off` and end with `# fmt: on`. `# fmt: skip` can be mixed with other
pragmas/comments either with multiple comments (e.g. `# fmt: skip # pylint # noqa`) or
as a semicolon separated list (e.g. `# fmt: skip; pylint; noqa`). `# fmt: on/off` must
be on the same level of indentation and in the same block, meaning no unindents beyond
the initial indentation level between them. Black also recognizes
[YAPF](https://github.com/google/yapf)'s block comments to the same effect, as a
courtesy for straddling code.

### Command line options

The CLI options of _Black_ can be displayed by running `black --help`. All options are
also covered in more detail below.

While _Black_ has quite a few knobs these days, it is still opinionated so style options
are deliberately limited and rarely added.

Note that all command-line options listed above can also be configured using a
`pyproject.toml` file (more on that below).

#### `-h`, `--help`

Show available command-line options and exit.

#### `-c`, `--code`

Format the code passed in as a string.

```console
$ black --code "print ( 'hello, world' )"
print("hello, world")
```

#### `-l`, `--line-length`

How many characters per line to allow. The default is 88.

See also [the style documentation](labels/line-length).

#### `-t`, `--target-version`

Python versions that should be supported by Black's output. You can run `black --help`
and look for the `--target-version` option to see the full list of supported versions.
You should include all versions that your code supports. If you support Python 3.11
through 3.13, you should write:

```console
$ black -t py311 -t py312 -t py313
```

In a [configuration file](#configuration-via-a-file), you can write:

```toml
target-version = ["py311", "py312", "py313"]
```

By default, Black will infer target versions from the project metadata in
`pyproject.toml`, specifically the `[project.requires-python]` field. If this does not
yield conclusive results, Black will use per-file auto-detection.

_Black_ uses this option to decide what grammar to use to parse your code. In addition,
it may use it to decide what style to use. For example, support for a trailing comma
after `*args` in a function call was added in Python 3.5, so _Black_ will add this comma
only if the target versions are all Python 3.5 or higher:

```console
$ black --line-length=10 --target-version=py35 -c 'f(a, *args)'
f(
    a,
    *args,
)
$ black --line-length=10 --target-version=py34 -c 'f(a, *args)'
f(
    a,
    *args
)
$ black --line-length=10 --target-version=py34 --target-version=py35 -c 'f(a, *args)'
f(
    a,
    *args
)
```

#### `--pyi`

Format all input files like typing stubs regardless of file extension. This is useful
when piping source on standard input.

#### `--ipynb`

Format all input files like Jupyter Notebooks regardless of file extension. This is
useful when piping source on standard input.

#### `--python-cell-magics`

When processing Jupyter Notebooks, add the given magic to the list of known python-
magics. Useful for formatting cells with custom python magics.

#### `-x, --skip-source-first-line`

Skip the first line of the source code.

#### `-S, --skip-string-normalization`

By default, _Black_ uses double quotes for all strings and normalizes string prefixes,
as described in [the style documentation](labels/strings). If this option is given,
strings are left unchanged instead.

#### `-C, --skip-magic-trailing-comma`

By default, _Black_ uses existing trailing commas as an indication that short lines
should be left separate, as described in
[the style documentation](labels/magic-trailing-comma). If this option is given, the
magic trailing comma is ignored.

#### `--preview`

Enable potentially disruptive style changes that we expect to add to Black's main
functionality in the next major release. Use this if you want a taste of what next
year's style will look like.

Read more about [our preview style](labels/preview-style).

There is no guarantee on the code style produced by this flag across releases.

#### `--unstable`

Enable all style changes in `--preview`, plus additional changes that we would like to
make eventually, but that have known issues that need to be fixed before they can move
back to the `--preview` style. Use this if you want to experiment with these changes and
help fix issues with them.

There is no guarantee on the code style produced by this flag across releases.

#### `--enable-unstable-feature`

Enable specific features from the `--unstable` style. See
[the preview style documentation](labels/unstable-features) for the list of supported
features. This flag can only be used when `--preview` is enabled. Users are encouraged
to use this flag if they use `--preview` style and a feature that affects their code is
moved from the `--preview` to the `--unstable` style, but they want to avoid the thrash
from undoing this change.

There are no guarantees on the behavior of these features, or even their existence,
across releases.

(labels/exit-code)=

#### `--check`

Don't write the files back, just return the status. _Black_ will exit with:

- code 0 if nothing would change;
- code 1 if some files would be reformatted; or
- code 123 if there was an internal error

If used in combination with `--quiet` then only the exit code will be returned, unless
there was an internal error.

```console
$ black test.py --check
All done! ✨ 🍰 ✨
1 file would be left unchanged.
$ echo $?
0

$ black test.py --check
would reformat test.py
Oh no! 💥 💔 💥
1 file would be reformatted.
$ echo $?
1

$ black test.py --check
error: cannot format test.py: INTERNAL ERROR: Black produced code that is not equivalent to the source.  Please report a bug on https://github.com/psf/black/issues.  This diff might be helpful: /tmp/blk_kjdr1oog.log
Oh no! 💥 💔 💥
1 file would fail to reformat.
$ echo $?
123
```

#### `--diff`

Don't write the files back, just output a diff to indicate what changes _Black_ would've
made. They are printed to stdout so capturing them is simple.

If you'd like colored diffs, you can enable them with `--color`.

```console
$ black test.py --diff
--- test.py     2021-03-08 22:23:40.848954+00:00
+++ test.py     2021-03-08 22:23:47.126319+00:00
@@ -1 +1 @@
-print ( 'hello, world' )
+print("hello, world")
would reformat test.py
All done! ✨ 🍰 ✨
1 file would be reformatted.
```

#### `--color` / `--no-color`

Show (or do not show) colored diff. Only applies when `--diff` is given.

#### `--line-ranges`

When specified, _Black_ will try its best to only format these lines.

This option can be specified multiple times, and a union of the lines will be formatted.
Each range must be specified as two integers connected by a `-`: `<START>-<END>`. The
`<START>` and `<END>` integer indices are 1-based and inclusive on both ends.

_Black_ may still format lines outside of the ranges for multi-line statements.
Formatting more than one file or any ipynb files with this option is not supported. This
option cannot be specified in the `pyproject.toml` config.

Example: `black --line-ranges=1-10 --line-ranges=21-30 test.py` will format lines from
`1` to `10` and `21` to `30`.

This option is mainly for editor integrations, such as "Format Selection".

```{note}
Due to [#4052](https://github.com/psf/black/issues/4052), `--line-ranges` might format
extra lines outside of the ranges when there are unformatted lines with the exact
formatted content next to the requested lines. It also disables _Black_'s formatting
stability check in `--safe` mode.
```

#### `--fast` / `--safe`

By default, _Black_ performs [an AST safety check](labels/ast-changes) after formatting
your code. The `--fast` flag turns off this check and the `--safe` flag explicitly
enables it.

#### `--required-version`

Require a specific version of _Black_ to be running. This is useful for ensuring that
all contributors to your project are using the same version, because different versions
of _Black_ may format code a little differently. This option can be set in a
configuration file for consistent results across environments.

```console
$ black --version
black, 25.1.0 (compiled: yes)
$ black --required-version 25.1.0 -c "format = 'this'"
format = "this"
$ black --required-version 31.5b2 -c "still = 'beta?!'"
Oh no! 💥 💔 💥 The required version does not match the running version!
```

You can also pass just the major version:

```console
$ black --required-version 22 -c "format = 'this'"
format = "this"
$ black --required-version 31 -c "still = 'beta?!'"
Oh no! 💥 💔 💥 The required version does not match the running version!
```

Because of our [stability policy](../the_black_code_style/index.md), this will guarantee
stable formatting, but still allow you to take advantage of improvements that do not
affect formatting.

#### `--exclude`

A regular expression that matches files and directories that should be excluded on
recursive searches. An empty value means no paths are excluded. Use forward slashes for
directories on all platforms (Windows, too). By default, Black also ignores all paths
listed in `.gitignore`. Changing this value will override all default exclusions.

Default Exclusions:
`['.direnv', '.eggs', '.git', '.hg', '.ipynb_checkpoints',  '.mypy_cache', '.nox', '.pytest_cache', '.ruff_cache', '.tox', '.svn', '.venv', '.vscode',  '__pypackages__', '_build', 'buck-out', 'build', 'dist', 'venv'] `

If the regular expression contains newlines, it is treated as a
[verbose regular expression](https://docs.python.org/3/library/re.html#re.VERBOSE). This
is typically useful when setting these options in a `pyproject.toml` configuration file;
see [Configuration format](#configuration-format) for more information.

#### `--extend-exclude`

Like `--exclude`, but adds additional files and directories on top of the default values
instead of overriding them.

#### `--force-exclude`

Like `--exclude`, but files and directories matching this regex will be excluded even
when they are passed explicitly as arguments. This is useful when invoking Black
programmatically on changed files, such as in a pre-commit hook or editor plugin.

#### `--stdin-filename`

The name of the file when passing it through stdin. Useful to make sure Black will
respect the `--force-exclude` option on some editors that rely on using stdin.

#### `--include`

A regular expression that matches files and directories that should be included on
recursive searches. An empty value means all files are included regardless of the name.
Use forward slashes for directories on all platforms (Windows, too). Overrides all
exclusions, including from `.gitignore` and command line options.

Default Inclusions: `['.pyi', '.ipynb']`

#### `-W`, `--workers`

When _Black_ formats multiple files, it may use a process pool to speed up formatting.
This option controls the number of parallel workers. This can also be specified via the
`BLACK_NUM_WORKERS` environment variable. Defaults to the number of CPUs in the system.

#### `-q`, `--quiet`

Stop emitting all non-critical output. Error messages will still be emitted (which can
silenced by `2>/dev/null`).

```console
$ black src/ -q
error: cannot format src/black_primer/cli.py: Cannot parse: 5:6: mport asyncio
```

#### `-v`, `--verbose`

Emit messages about files that were not changed or were ignored due to exclusion
patterns. If _Black_ is using a configuration file, a message detailing which one it is
using will be emitted.

```console
$ black src/ -v
Using configuration from /tmp/pyproject.toml.
src/blib2to3 ignored: matches the --extend-exclude regular expression
src/_black_version.py wasn't modified on disk since last run.
src/black/__main__.py wasn't modified on disk since last run.
error: cannot format src/black_primer/cli.py: Cannot parse: 5:6: mport asyncio
reformatted src/black_primer/lib.py
reformatted src/blackd/__init__.py
reformatted src/black/__init__.py
Oh no! 💥 💔 💥
3 files reformatted, 2 files left unchanged, 1 file failed to reformat
```

#### `--version`

You can check the version of _Black_ you have installed using the `--version` flag.

```console
$ black --version
black, 25.1.0
```

#### `--config`

Read configuration options from a configuration file. See
[below](#configuration-via-a-file) for more details on the configuration file.

### Environment variable options

_Black_ supports the following configuration via environment variables.

#### `BLACK_CACHE_DIR`

The directory where _Black_ should store its cache.

#### `BLACK_NUM_WORKERS`

The number of parallel workers _Black_ should use. The command line option `-W` /
`--workers` takes precedence over this environment variable.

### Code input alternatives

_Black_ supports formatting code via stdin, with the result being printed to stdout.
Just let _Black_ know with `-` as the path.

```console
$ echo "print ( 'hello, world' )" | black -
print("hello, world")
reformatted -
All done! ✨ 🍰 ✨
1 file reformatted.
```

**Tip:** if you need _Black_ to treat stdin input as a file passed directly via the CLI,
use `--stdin-filename`. Useful to make sure _Black_ will respect the `--force-exclude`
option on some editors that rely on using stdin.

You can also pass code as a string using the `--code` option.

### Writeback and reporting

By default _Black_ reformats the files given and/or found in place. Sometimes you need
_Black_ to just tell you what it _would_ do without actually rewriting the Python files.

There's two variations to this mode that are independently enabled by their respective
flags:

- `--check` (exit with code 1 if any file would be reformatted)
- `--diff` (print a diff instead of reformatting files)

Both variations can be enabled at once.

### Output verbosity

_Black_ in general tries to produce the right amount of output, balancing between
usefulness and conciseness. By default, _Black_ emits files modified and error messages,
plus a short summary.

```console
$ black src/
error: cannot format src/black_primer/cli.py: Cannot parse: 5:6: mport asyncio
reformatted src/black_primer/lib.py
reformatted src/blackd/__init__.py
reformatted src/black/__init__.py
Oh no! 💥 💔 💥
3 files reformatted, 2 files left unchanged, 1 file failed to reformat.
```

The `--quiet` and `--verbose` flags control output verbosity.

## Configuration via a file

_Black_ is able to read project-specific default values for its command line options
from a `pyproject.toml` file. This is especially useful for specifying custom
`--include` and `--exclude`/`--force-exclude`/`--extend-exclude` patterns for your
project.

**Pro-tip**: If you're asking yourself "Do I need to configure anything?" the answer is
"No". _Black_ is all about sensible defaults. Applying those defaults will have your
code in compliance with many other _Black_ formatted projects.

### What on Earth is a `pyproject.toml` file?

[PEP 518](https://www.python.org/dev/peps/pep-0518/) defines `pyproject.toml` as a
configuration file to store build system requirements for Python projects. With the help
of tools like [Poetry](https://python-poetry.org/),
[Flit](https://flit.readthedocs.io/en/latest/), or
[Hatch](https://hatch.pypa.io/latest/) it can fully replace the need for `setup.py` and
`setup.cfg` files.

### Where _Black_ looks for the file

By default _Black_ looks for `pyproject.toml` containing a `[tool.black]` section
starting from the common base directory of all files and directories passed on the
command line. If it's not there, it looks in parent directories. It stops looking when
it finds the file, or a `.git` directory, or a `.hg` directory, or the root of the file
system, whichever comes first.

If you're formatting standard input, _Black_ will look for configuration starting from
the current working directory.

You can use a "global" configuration, stored in a specific location in your home
directory. This will be used as a fallback configuration, that is, it will be used if
and only if _Black_ doesn't find any configuration as mentioned above. Depending on your
operating system, this configuration file should be stored as:

- Windows: `~\.black`
- Unix-like (Linux, MacOS, etc.): `$XDG_CONFIG_HOME/black` (`~/.config/black` if the
  `XDG_CONFIG_HOME` environment variable is not set)

Note that these are paths to the TOML file itself (meaning that they shouldn't be named
as `pyproject.toml`), not directories where you store the configuration (i.e.,
`black`/`.black` is the file to create and add your configuration options to, in the
`~/.config/` directory). Here, `~` refers to the path to your home directory. On
Windows, this will be something like `C:\\Users\UserName`.

You can also explicitly specify the path to a particular file that you want with
`--config`. In this situation _Black_ will not look for any other file.

If you're running with `--verbose`, you will see a message if a file was found and used.

Please note `blackd` will not use `pyproject.toml` configuration.

### Configuration format

As the file extension suggests, `pyproject.toml` is a
[TOML](https://github.com/toml-lang/toml) file. It contains separate sections for
different tools. _Black_ is using the `[tool.black]` section. The option keys are the
same as long names of options on the command line.

Note that you have to use single-quoted strings in TOML for regular expressions. It's
the equivalent of r-strings in Python. Multiline strings are treated as verbose regular
expressions by Black. Use `[ ]` to denote a significant space character.

<details>
<summary>Example <code>pyproject.toml</code></summary>

```toml
[tool.black]
line-length = 88
target-version = ['py37']
include = '\.pyi?$'
# 'extend-exclude' excludes files or directories in addition to the defaults
extend-exclude = '''
# A regex preceded with ^/ will apply only to files and directories
# in the root of the project.
(
  ^/foo.py    # exclude a file named foo.py in the root of the project
  | .*_pb2.py  # exclude autogenerated Protocol Buffer files anywhere in the project
)
'''
```

</details>

### Lookup hierarchy

Command-line options have defaults that you can see in `--help`. A `pyproject.toml` can
override those defaults. Finally, options provided by the user on the command line
override both.

_Black_ will only ever use one `pyproject.toml` file during an entire run. It doesn't
look for multiple files, and doesn't compose configuration from different levels of the
file hierarchy.

## Next steps

A good next step would be configuring auto-discovery so `black .` is all you need
instead of laborously listing every file or directory. You can get started by heading
over to [File collection and discovery](./file_collection_and_discovery.md).

Another good choice would be setting up an
[integration with your editor](../integrations/editors.md) of choice or with
[pre-commit for source version control](../integrations/source_version_control.md).
````

## File: docs/authors.md
````markdown
```{include} ../AUTHORS.md

```
````

## File: docs/change_log.md
````markdown
```{include} ../CHANGES.md

```
````

## File: docs/faq.md
````markdown
# Frequently Asked Questions

The most common questions and issues users face are aggregated to this FAQ.

```{contents}
:local:
:backlinks: none
:class: this-will-duplicate-information-and-it-is-still-useful-here
```

## Why spaces? I prefer tabs

PEP 8 recommends spaces over tabs, and they are used by most of the Python community.
_Black_ provides no options to configure the indentation style, and requests for such
options will not be considered.

However, we recognise that using tabs is an accessibility issue as well. While the
option will never be added to _Black_, visually impaired developers may find conversion
tools such as `expand/unexpand` (for Linux) useful when contributing to Python projects.
A workflow might consist of e.g. setting up appropriate pre-commit and post-merge git
hooks, and scripting `unexpand` to run after applying _Black_.

## Does Black have an API?

Not yet. _Black_ is fundamentally a command line tool. Many
[integrations](/integrations/index.md) are provided, but a Python interface is not one
of them. A simple API is being [planned](https://github.com/psf/black/issues/779)
though.

## Is Black safe to use?

Yes. _Black_ is strictly about formatting, nothing else. Black strives to ensure that
after formatting the AST is
[checked](the_black_code_style/current_style.md#ast-before-and-after-formatting) with
limited special cases where the code is allowed to differ. If issues are found, an error
is raised and the file is left untouched. Magical comments that influence linters and
other tools, such as `# noqa`, may be moved by _Black_. See below for more details.

## How stable is Black's style?

Stable. _Black_ aims to enforce one style and one style only, with some room for
pragmatism. See [The Black Code Style](the_black_code_style/index.md) for more details.

Starting in 2022, the formatting output is stable for the releases made in the same year
(other than unintentional bugs). At the beginning of every year, the first release will
make changes to the stable style. It is possible to opt in to the latest formatting
styles using the `--preview` flag.

## Why is my file not formatted?

Most likely because it is ignored in `.gitignore` or excluded with configuration. See
[file collection and discovery](usage_and_configuration/file_collection_and_discovery.md)
for details.

## Why is my Jupyter Notebook cell not formatted?

_Black_ is timid about formatting Jupyter Notebooks. Cells containing any of the
following will not be formatted:

- automagics (e.g. `pip install black`)
- non-Python cell magics (e.g. `%%writefile`). These can be added with the flag
  `--python-cell-magics`, e.g. `black --python-cell-magics writefile hello.ipynb`.
- multiline magics, e.g.:

  ```python
  %timeit f(1, \
          2, \
          3)
  ```

- code which `IPython`'s `TransformerManager` would transform magics into, e.g.:

  ```python
  get_ipython().system('ls')
  ```

- invalid syntax, as it can't be safely distinguished from automagics in the absence of
  a running `IPython` kernel.

## Why does Flake8 report warnings?

Some of Flake8's rules conflict with Black's style. We recommend disabling these rules.
See [Using _Black_ with other tools](labels/why-pycodestyle-warnings).

## Which Python versions does Black support?

_Black_ generally supports all Python versions supported by CPython (see
[the Python devguide](https://devguide.python.org/versions/) for current information).
We promise to support at least all Python versions that have not reached their end of
life. This is the case for both running _Black_ and formatting code.

Support for formatting Python 2 code was removed in version 22.0. While we've made no
plans to stop supporting older Python 3 minor versions immediately, their support might
also be removed some time in the future without a deprecation period.

`await`/`async` as soft keywords/indentifiers are no longer supported as of 25.2.0.

Runtime support for 3.6 was removed in version 22.10.0, for 3.7 in version 23.7.0, and
for 3.8 in version 24.10.0.

## Why does my linter or typechecker complain after I format my code?

Some linters and other tools use magical comments (e.g., `# noqa`, `# type: ignore`) to
influence their behavior. While Black does its best to recognize such comments and leave
them in the right place, this detection is not and cannot be perfect. Therefore, you'll
sometimes have to manually move these comments to the right place after you format your
codebase with _Black_.

## Can I run Black with PyPy?

Yes, there is support for PyPy 3.8 and higher.

## Why does Black not detect syntax errors in my code?

_Black_ is an autoformatter, not a Python linter or interpreter. Detecting all syntax
errors is not a goal. It can format all code accepted by CPython (if you find an example
where that doesn't hold, please report a bug!), but it may also format some code that
CPython doesn't accept.

(labels/mypyc-support)=

## What is `compiled: yes/no` all about in the version output?

While _Black_ is indeed a pure Python project, we use [mypyc] to compile _Black_ into a
C Python extension, usually doubling performance. These compiled wheels are available
for 64-bit versions of Windows, Linux (via the manylinux standard), and macOS across all
supported CPython versions.

Platforms including musl-based and/or ARM Linux distributions, and ARM Windows are
currently **not** supported. These platforms will fall back to the slower pure Python
wheel available on PyPI.

If you are experiencing exceptionally weird issues or even segfaults, you can try
passing `--no-binary black` to your pip install invocation. This flag excludes all
wheels (including the pure Python wheel), so this command will use the [sdist].

[mypyc]: https://mypyc.readthedocs.io/en/latest/
[sdist]:
  https://packaging.python.org/en/latest/glossary/#term-Source-Distribution-or-sdist

## Why are emoji not displaying correctly on Windows?

When using Windows, the emoji in _Black_'s output may not display correctly. This is not
fixable from _Black_'s end.

Instead, run your chosen command line/shell through [Windows Terminal], which will
properly handle rendering the emoji.

[Windows Terminal]: https://github.com/microsoft/terminal
````

## File: docs/getting_started.md
````markdown
# Getting Started

New to _Black_? Don't worry, you've found the perfect place to get started!

## Do you like the _Black_ code style?

Before using _Black_ on some of your code, it might be a good idea to first understand
how _Black_ will format your code. _Black_ isn't for everyone and you may find something
that is a dealbreaker for you personally, which is okay! The current _Black_ code style
[is described here](./the_black_code_style/current_style.md).

## Try it out online

Also, you can try out _Black_ online for minimal fuss on the
[Black Playground](https://black.vercel.app) generously created by José Padilla.

## Installation

_Black_ can be installed by running `pip install black`. It requires Python 3.9+ to run.
If you want to format Jupyter Notebooks, install with `pip install "black[jupyter]"`.

If you use pipx, you can install Black with `pipx install black`.

If you can't wait for the latest _hotness_ and want to install from GitHub, use:

`pip install git+https://github.com/psf/black`

## Basic usage

To get started right away with sensible defaults:

```sh
black {source_file_or_directory}...
```

You can run _Black_ as a package if running it as a script doesn't work:

```sh
python -m black {source_file_or_directory}...
```

## Next steps

Took a look at [the _Black_ code style](./the_black_code_style/current_style.md) and
tried out _Black_? Fantastic, you're ready for more. Why not explore some more on using
_Black_ by reading
[Usage and Configuration: The basics](./usage_and_configuration/the_basics.md).
Alternatively, you can check out the
[Introducing _Black_ to your project](./guides/introducing_black_to_your_project.md)
guide.
````

## File: docs/index.md
````markdown
<!--
black documentation master file, created by
sphinx-quickstart on Fri Mar 23 10:53:30 2018.
-->

# The uncompromising code formatter

> “Any color you like.”

By using _Black_, you agree to cede control over minutiae of hand-formatting. In return,
_Black_ gives you speed, determinism, and freedom from `pycodestyle` nagging about
formatting. You will save time and mental energy for more important matters.

_Black_ makes code review faster by producing the smallest diffs possible. Blackened
code looks the same regardless of the project you're reading. Formatting becomes
transparent after a while and you can focus on the content instead.

Try it out now using the [Black Playground](https://black.vercel.app).

```{admonition} Note - Black is now stable!
*Black* is [successfully used](https://github.com/psf/black#used-by) by
many projects, small and big. *Black* has a comprehensive test suite, with efficient
parallel tests, our own auto formatting and parallel Continuous Integration runner.
Now that we have become stable, you should not expect large changes to formatting in
the future. Stylistic changes will mostly be responses to bug reports and support for new Python
syntax.

Also, as a safety measure which slows down processing, *Black* will check that the
reformatted code still produces a valid AST that is effectively equivalent to the
original (see the
[Pragmatism](./the_black_code_style/current_style.md#pragmatism)
section for details). If you're feeling confident, use `--fast`.
```

```{note}
{doc}`Black is licensed under the MIT license <license>`.
```

## Testimonials

**Mike Bayer**, author of [SQLAlchemy](https://www.sqlalchemy.org/):

> _I can't think of any single tool in my entire programming career that has given me a
> bigger productivity increase by its introduction. I can now do refactorings in about
> 1% of the keystrokes that it would have taken me previously when we had no way for
> code to format itself._

**Dusty Phillips**,
[writer](https://smile.amazon.com/s/ref=nb_sb_noss?url=search-alias%3Daps&field-keywords=dusty+phillips):

> _Black is opinionated so you don't have to be._

**Hynek Schlawack**, creator of [attrs](https://www.attrs.org/), core developer of
Twisted and CPython:

> _An auto-formatter that doesn't suck is all I want for Xmas!_

**Carl Meyer**, [Django](https://www.djangoproject.com/) core developer:

> _At least the name is good._

**Kenneth Reitz**, creator of [requests](http://python-requests.org/) and
[pipenv](https://docs.pipenv.org/):

> _This vastly improves the formatting of our code. Thanks a ton!_

## Show your style

Use the badge in your project's README.md:

```md
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

Using the badge in README.rst:

```rst
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
```

Looks like this:

```{image} https://img.shields.io/badge/code%20style-black-000000.svg
:target: https://github.com/psf/black
```

## Contents

```{toctree}
---
maxdepth: 3
includehidden:
---

the_black_code_style/index
```

```{toctree}
---
maxdepth: 3
includehidden:
caption: User Guide
---

getting_started
usage_and_configuration/index
integrations/index
guides/index
faq
```

```{toctree}
---
maxdepth: 2
includehidden:
caption: Development
---

contributing/index
change_log
authors
```

```{toctree}
---
hidden:
caption: Project Links
---

GitHub <https://github.com/psf/black>
PyPI <https://pypi.org/project/black>
Chat <https://discord.gg/RtVdv86PrH>
```

# Indices and tables

- {ref}`genindex`
- {ref}`search`
````

## File: docs/license.md
````markdown
---
orphan: true
---

# License

```{include} ../LICENSE

```
````

## File: docs/requirements.txt
````
# Used by ReadTheDocs; pinned requirements for stability.

myst-parser==4.0.1
Sphinx==8.2.3
# Older versions break Sphinx even though they're declared to be supported.
docutils==0.21.2
sphinxcontrib-programoutput==0.18
sphinx_copybutton==0.5.2
furo==2025.7.19
````
