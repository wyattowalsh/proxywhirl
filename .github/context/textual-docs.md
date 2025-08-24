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
  api/
    app.md
    await_complete.md
    await_remove.md
    binding.md
    cache.md
    color.md
    command.md
    compose.md
    constants.md
    containers.md
    content.md
    coordinate.md
    dom_node.md
    errors.md
    events.md
    filter.md
    fuzzy_matcher.md
    geometry.md
    getters.md
    index.md
    layout.md
    lazy.md
    logger.md
    logging.md
    map_geometry.md
    markup.md
    message_pump.md
    message.md
    on.md
    pilot.md
    query.md
    reactive.md
    renderables.md
    screen.md
    scroll_view.md
    scrollbar.md
    signal.md
    strip.md
    style.md
    suggester.md
    system_commands_source.md
    timer.md
    types.md
    validation.md
    walk.md
    widget.md
    work.md
    worker_manager.md
    worker.md
  blog/
    posts/
      anatomy-of-a-textual-user-interface.md
      await-me-maybe.md
      be-the-keymaster.md
      better-sleep-on-windows.md
      create-task-psa.md
      creating-tasks-overhead.md
      darren-year-in-review.md
      future-of-textualize.md
      helo-world.md
      inline-mode.md
      looking-for-help.md
      on-dog-food-the-original-metaverse-and-not-being-bored.md
      placeholder-pr.md
      puppies-and-cake.md
      release0-11-0.md
      release0-12-0.md
      release0-14-0.md
      release0-15-0.md
      release0-16-0.md
      release0-17-0.md
      release0-18-0.md
      release0-23-0.md
      release0-24-0.md
      release0-27-0.md
      release0-29-0.md
      release0-30-0.md
      release0-38-0.md
      release0-4-0.md
      release0-6-0.md
      release0.37.0.md
      release1.0.0.md
      remote-memray.md
      responsive-app-background-task.md
      rich-inspect.md
      smooth-scrolling.md
      spinners-and-pbs-in-textual.md
      steal-this-code.md
      text-area-learnings.md
      textual-plotext.md
      textual-serve-files.md
      textual-web.md
      to-tui-or-not-to-tui.md
      toolong-retrospective.md
    index.md
  css_types/
    _template.md
    border.md
    color.md
    hatch.md
    horizontal.md
    index.md
    integer.md
    keyline.md
    name.md
    number.md
    overflow.md
    percentage.md
    position.md
    scalar.md
    text_align.md
    text_style.md
    vertical.md
  events/
    app_blur.md
    app_focus.md
    blur.md
    click.md
    descendant_blur.md
    descendant_focus.md
    enter.md
    focus.md
    hide.md
    index.md
    key.md
    leave.md
    load.md
    mount.md
    mouse_capture.md
    mouse_down.md
    mouse_move.md
    mouse_release.md
    mouse_scroll_down.md
    mouse_scroll_left.md
    mouse_scroll_right.md
    mouse_scroll_up.md
    mouse_up.md
    paste.md
    print.md
    resize.md
    screen_resume.md
    screen_suspend.md
    show.md
    unmount.md
  examples/
    styles/
      README.md
  guide/
    actions.md
    animation.md
    app.md
    command_palette.md
    content.md
    CSS.md
    design.md
    devtools.md
    events.md
    index.md
    input.md
    layout.md
    queries.md
    reactivity.md
    screens.md
    styles.md
    testing.md
    widgets.md
    workers.md
  how-to/
    center-things.md
    design-a-layout.md
    index.md
    package-with-hatch.md
    render-and-compose.md
    style-inline-apps.md
    work-with-containers.md
  reference/
    index.md
  snippets/
    border_sub_title_align_all_example.md
    border_title_color.md
    border_vs_outline_example.md
    see_also_border.md
    syntax_block_end.md
    syntax_block_start.md
  styles/
    grid/
      column_span.md
      grid_columns.md
      grid_gutter.md
      grid_rows.md
      grid_size.md
      index.md
      row_span.md
    links/
      index.md
      link_background_hover.md
      link_background.md
      link_color_hover.md
      link_color.md
      link_style_hover.md
      link_style.md
    scrollbar_colors/
      index.md
      scrollbar_background_active.md
      scrollbar_background_hover.md
      scrollbar_background.md
      scrollbar_color_active.md
      scrollbar_color_hover.md
      scrollbar_color.md
      scrollbar_corner_color.md
    _template.md
    align.md
    background_tint.md
    background.md
    border_subtitle_align.md
    border_subtitle_background.md
    border_subtitle_color.md
    border_subtitle_style.md
    border_title_align.md
    border_title_background.md
    border_title_color.md
    border_title_style.md
    border.md
    box_sizing.md
    color.md
    content_align.md
    display.md
    dock.md
    hatch.md
    height.md
    index.md
    keyline.md
    layer.md
    layers.md
    layout.md
    margin.md
    max_height.md
    max_width.md
    min_height.md
    min_width.md
    offset.md
    opacity.md
    outline.md
    overflow.md
    padding.md
    position.md
    scrollbar_gutter.md
    scrollbar_size.md
    text_align.md
    text_opacity.md
    text_overflow.md
    text_style.md
    text_wrap.md
    tint.md
    visibility.md
    width.md
  widgets/
    _template.md
    button.md
    checkbox.md
    collapsible.md
    content_switcher.md
    data_table.md
    digits.md
    directory_tree.md
    footer.md
    header.md
    index.md
    input.md
    label.md
    link.md
    list_item.md
    list_view.md
    loading_indicator.md
    log.md
    markdown_viewer.md
    markdown.md
    masked_input.md
    option_list.md
    placeholder.md
    pretty.md
    progress_bar.md
    radiobutton.md
    radioset.md
    rich_log.md
    rule.md
    select.md
    selection_list.md
    sparkline.md
    static.md
    switch.md
    tabbed_content.md
    tabs.md
    text_area.md
    toast.md
    tree.md
  FAQ.md
  getting_started.md
  help.md
  index.md
  roadmap.md
  robots.txt
  tutorial.md
  widget_gallery.md
```

# Files

## File: docs/api/app.md
````markdown
---
title: "textual.app"
---

::: textual.app
    options:
        filters:
          - "!^_"
          - "^__init__$"
````

## File: docs/api/await_complete.md
````markdown
---
title: "textual.await_complete"
---

This module contains the `AwaitComplete` class.
An `AwaitComplete` object is returned by methods that do work in the *background*.
You can await this object if you need to know when that work has completed.
Or you can ignore it, and Textual will automatically await the work before handling the next message.

!!! note

    You are unlikely to need to explicitly create these objects yourself.


::: textual.await_complete
````

## File: docs/api/await_remove.md
````markdown
---
title: "textual.await_remove"
---

This module contains the `AwaitRemove` class.
An `AwaitRemove` object is returned by [`Widget.remove()`][textual.widget.Widget.remove] and other methods which remove widgets.
You can await the return value if you need to know exactly when the widget(s) have been removed.
Or you can ignore it and Textual will wait for the widgets to be removed before handling the next message.

!!! note

    You are unlikely to need to explicitly create these objects yourself.


::: textual.await_remove
````

## File: docs/api/binding.md
````markdown
---
title: "textual.binding"
---

::: textual.binding
````

## File: docs/api/cache.md
````markdown
---
title: "textual.cache"
---

::: textual.cache
````

## File: docs/api/color.md
````markdown
---
title: "textual.color"
---

::: textual.color
````

## File: docs/api/command.md
````markdown
---
title: "textual.command"
---

::: textual.command
````

## File: docs/api/compose.md
````markdown
---
title: "textual.compose"
---

::: textual.compose.compose
````

## File: docs/api/constants.md
````markdown
---
title: "textual.constants"
---

::: textual.constants
````

## File: docs/api/containers.md
````markdown
---
title: "textual.containers"
---


::: textual.containers
````

## File: docs/api/content.md
````markdown
---
title: "textual.content"
---

::: textual.content
````

## File: docs/api/coordinate.md
````markdown
---
title: "textual.coordinate"
---


::: textual.coordinate
````

## File: docs/api/dom_node.md
````markdown
---
title: "textual.dom"
---

::: textual.dom
````

## File: docs/api/errors.md
````markdown
---
title: "textual.errors"
---

::: textual.errors
````

## File: docs/api/events.md
````markdown
---
title: "textual.events"
---


::: textual.events
````

## File: docs/api/filter.md
````markdown
---
title: "textual.filter"
---


::: textual.filter
````

## File: docs/api/fuzzy_matcher.md
````markdown
---
title: "textual.fuzzy"
---


::: textual.fuzzy
````

## File: docs/api/geometry.md
````markdown
---
title: "textual.geometry"
---


::: textual.geometry
````

## File: docs/api/getters.md
````markdown
---
title: "textual.getters"
---

::: textual.getters
````

## File: docs/api/index.md
````markdown
# API

This is a API-level reference to the Textual API. Click the links to your left (or in the :octicons-three-bars-16: menu) to open a reference for each module.

If you are new to Textual, you may want to read the [tutorial](./../tutorial.md) or [guide](../guide/index.md) first.
````

## File: docs/api/layout.md
````markdown
---
title: "textual.layout"
---


::: textual.layout
````

## File: docs/api/lazy.md
````markdown
---
title: "textual.lazy"
---


::: textual.lazy
````

## File: docs/api/logger.md
````markdown
---
title: "textual"
---


::: textual
````

## File: docs/api/logging.md
````markdown
---
title: "textual.logging"
---
::: textual.logging
````

## File: docs/api/map_geometry.md
````markdown
---
title: "textual.map_geometry"
---


A data structure returned by [screen.find_widget][textual.screen.Screen.find_widget].

::: textual.map_geometry
````

## File: docs/api/markup.md
````markdown
---
title: "textual.markup"
---

::: textual.markup
````

## File: docs/api/message_pump.md
````markdown
---
title: "textual.message_pump"
---

::: textual.message_pump
````

## File: docs/api/message.md
````markdown
---
title: "textual.message"
---

::: textual.message
````

## File: docs/api/on.md
````markdown
---
title: "textual.on"
---

# On

::: textual.on
````

## File: docs/api/pilot.md
````markdown
---
title: "textual.pilot"
---

::: textual.pilot
````

## File: docs/api/query.md
````markdown
---
title: "textual.css.query"
---

::: textual.css.query
````

## File: docs/api/reactive.md
````markdown
---
title: "textual.reactive"
---

::: textual.reactive
````

## File: docs/api/renderables.md
````markdown
---
title: "textual.renderables"
---

A collection of Rich renderables which may be returned from a widget's [`render()`][textual.widget.Widget.render] method.

::: textual.renderables.bar
::: textual.renderables.blank
::: textual.renderables.digits
::: textual.renderables.gradient
::: textual.renderables.sparkline
````

## File: docs/api/screen.md
````markdown
---
title: "textual.screen"
---


::: textual.screen
````

## File: docs/api/scroll_view.md
````markdown
---
title: "textual.scroll_view"
---


::: textual.scroll_view
````

## File: docs/api/scrollbar.md
````markdown
---
title: "textual.scrollbar"
---

::: textual.scrollbar
````

## File: docs/api/signal.md
````markdown
---
title: "textual.signal"
---

::: textual.signal
````

## File: docs/api/strip.md
````markdown
---
title: "textual.strip"
---


::: textual.strip
````

## File: docs/api/style.md
````markdown
---
title: "textual.style"
---

::: textual.style
````

## File: docs/api/suggester.md
````markdown
---
title: "textual.suggester"
---


::: textual.suggester
````

## File: docs/api/system_commands_source.md
````markdown
---
title: "textual.system_commands"
---



::: textual.system_commands
````

## File: docs/api/timer.md
````markdown
---
title: "textual.timer"
---

::: textual.timer
````

## File: docs/api/types.md
````markdown
---
title: "textual.types"
---


::: textual.types
````

## File: docs/api/validation.md
````markdown
---
title: "textual.validation"
---


::: textual.validation
````

## File: docs/api/walk.md
````markdown
---
title: "textual.walk"
---


::: textual.walk
````

## File: docs/api/widget.md
````markdown
---
title: "textual.widget"
---


::: textual.widget
    options:
        filters:
          - "!^_"
          - "^__init__$"
````

## File: docs/api/work.md
````markdown
---
title: "textual.work"
---


::: textual.work
````

## File: docs/api/worker_manager.md
````markdown
---
title: "textual.worker_manager"
---

::: textual.worker_manager
````

## File: docs/api/worker.md
````markdown
---
title: "textual.worker"
---

::: textual.worker
````

## File: docs/blog/posts/anatomy-of-a-textual-user-interface.md
````markdown
---
draft: false
date: 2024-09-15
categories:
  - DevLog
authors:
  - willmcgugan
---

# Anatomy of a Textual User Interface

!!! note "My bad 🤦"

    The date is wrong on this post&mdash;it was actually published on the 2nd of September 2024.
    I don't want to fix it, as that would break the URL.  

I recently wrote a [TUI](https://en.wikipedia.org/wiki/Text-based_user_interface) to chat to an AI agent in the terminal.
I'm not the first to do this (shout out to [Elia](https://github.com/darrenburns/elia) and [Paita](https://github.com/villekr/paita)), but I *may* be the first to have it reply as if it were the AI from the Aliens movies?

Here's a video of it in action:



<iframe width="100%" style="aspect-ratio:1512 / 982"  src="https://www.youtube.com/embed/hr5JvQS4d_w" title="Mother AI" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Now let's dissect the code like Bishop dissects a facehugger.

<!-- more -->

## All right, sweethearts, what are you waiting for? Breakfast in bed?

At the top of the file we have some boilerplate:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "llm",
#     "textual",
# ]
# ///
from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Header, Input, Footer, Markdown
from textual.containers import VerticalScroll
import llm

SYSTEM = """Formulate all responses as if you where the sentient AI named Mother from the Aliens movies."""
```

The text in the comment is a relatively new addition to the Python ecosystem.
It allows you to specify dependencies inline so that tools can setup an environment automatically.
The format of the comment was developed by [Ofek Lev](https://github.com/ofek) and first implemented in [Hatch](https://hatch.pypa.io/latest/blog/2024/05/02/hatch-v1100/#python-script-runner), and has since become a Python standard via [PEP 0723](https://peps.python.org/pep-0723/) (also authored by Ofek). 

!!! note

    PEP 0723 is also implemented in [uv](https://docs.astral.sh/uv/guides/scripts/#running-scripts).

I really like this addition to Python because it means I can now share a Python script without the recipient needing to manually setup a fresh environment and install dependencies.

After this comment we have a bunch of imports: [textual](https://github.com/textualize/textual) for the UI, and [llm](https://llm.datasette.io/en/stable/) to talk to ChatGPT (also supports other LLMs).

Finally, we define `SYSTEM`, which is the *system prompt* for the LLM.

## Look, those two specimens are worth millions to the bio-weapons division.

Next up we have the following:

```python

class Prompt(Markdown):
    pass


class Response(Markdown):
    BORDER_TITLE = "Mother"
```

These two classes define the widgets which will display text the user enters and the response from the LLM.
They both extend the builtin [Markdown](https://textual.textualize.io/widgets/markdown/) widget, since LLMs like to talk in that format.

## Well, somebody's gonna have to go out there. Take a portable terminal, go out there and patch in manually.

Following on from the widgets we have the following:

```python
class MotherApp(App):
    AUTO_FOCUS = "Input"

    CSS = """
    Prompt {
        background: $primary 10%;
        color: $text;
        margin: 1;        
        margin-right: 8;
        padding: 1 2 0 2;
    }

    Response {
        border: wide $success;
        background: $success 10%;   
        color: $text;             
        margin: 1;      
        margin-left: 8; 
        padding: 1 2 0 2;
    }
    """
```

This defines an app, which is the top-level object for any Textual app.

The `AUTO_FOCUS` string is a classvar which causes a particular widget to receive input focus when the app starts. In this case it is the `Input` widget, which we will define later.

The classvar is followed by a string containing CSS.
Technically, TCSS or *Textual Cascading Style Sheets*, a variant of CSS for terminal interfaces.

This isn't a tutorial, so I'm not going to go in to a details, but we're essentially setting properties on widgets which define how they look.
Here I styled the prompt and response widgets to have a different color, and tried to give the response a retro tech look with a green background and border.

We could express these styles in code.
Something like this:

```python
self.styles.color = "red"
self.styles.margin = 8
```

Which is fine, but CSS shines when the UI get's more complex.

## Look, man. I only need to know one thing: where they are.

After the app constants, we have a method called `compose`:

```python
    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="chat-view"):
            yield Response("INTERFACE 2037 READY FOR INQUIRY")
        yield Input(placeholder="How can I help you?")
        yield Footer()
```

This method adds the initial widgets to the UI. 

`Header` and `Footer` are builtin widgets.

Sandwiched between them is a `VerticalScroll` *container* widget, which automatically adds a scrollbar (if required). It is pre-populated with a single `Response` widget to show a welcome message (the `with` syntax places a widget within a parent widget). Below that is an `Input` widget where we can enter text for the LLM.

This is all we need to define the *layout* of the TUI.
In Textual the layout is defined with styles (in the same was as color and margin).
Virtually any layout is possible, and you never have to do any math to calculate sizes of widgets&mdash;it is all done declaratively.

We could add a little CSS to tweak the layout, but the defaults work well here.
The header and footer are *docked* to an appropriate edge.
The `VerticalScroll` widget is styled to consume any available space, leaving room for widgets with a defined height (like our `Input`).

If you resize the terminal it will keep those relative proportions.

## Look into my eye.

The next method is an *event handler*.


```python
    def on_mount(self) -> None:
        self.model = llm.get_model("gpt-4o")
```

This method is called when the app receives a Mount event, which is one of the first events sent and is typically used for any setup operations.

It gets a `Model` object got our LLM of choice, which we will use later.

Note that the [llm](https://llm.datasette.io/en/stable/) library supports a [large number of models](https://llm.datasette.io/en/stable/openai-models.html), so feel free to replace the string with the model of your choice.

## We're in the pipe, five by five.

The next method is also a message handler:

```python
    @on(Input.Submitted)
    async def on_input(self, event: Input.Submitted) -> None:
        chat_view = self.query_one("#chat-view")
        event.input.clear()
        await chat_view.mount(Prompt(event.value))
        await chat_view.mount(response := Response())
        response.anchor()
        self.send_prompt(event.value, response)
```

The decorator tells Textual to handle the `Input.Submitted` event, which is sent when the user hits return in the Input.

!!! info "More on event handlers"

    There are two ways to receive events in Textual: a naming convention or the decorator.
    They aren't on the base class because the app and widgets can receive arbitrary events.

When that happens, this method clears the input and adds the prompt text to the `VerticalScroll`.
It also adds a `Response` widget to contain the LLM's response, and *anchors* it.
Anchoring a widget will keep it at the bottom of a scrollable view, which is just what we need for a chat interface.

Finally in that method we call `send_prompt`.

## We're on an express elevator to hell, going down!

Here is `send_prompt`:

```python
    @work(thread=True)
    def send_prompt(self, prompt: str, response: Response) -> None:
        response_content = ""
        llm_response = self.model.prompt(prompt, system=SYSTEM)
        for chunk in llm_response:
            response_content += chunk
            self.call_from_thread(response.update, response_content)
```

You'll notice that it is decorated with `@work`, which turns this method in to a *worker*.
In this case, a *threaded* worker. Workers are a layer over async and threads, which takes some of the pain out of concurrency.

This worker is responsible for sending the prompt, and then reading the response piece-by-piece.
It calls the Markdown widget's `update` method which replaces its content with new Markdown code, to give that funky streaming text effect.


## Game over man, game over!

The last few lines creates an app instance and runs it:

```python
if __name__ == "__main__":
    app = MotherApp()
    app.run()
```

You may need to have your [API key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key) set in an environment variable.
Or if you prefer, you could set in the `on_mount` function with the following:

```python
self.model.key = "... key here ..."
```

## Not bad, for a human.

Here's the [code for the Mother AI](https://gist.github.com/willmcgugan/648a537c9d47dafa59cb8ece281d8c2c).

Run the following in your shell of choice to launch mother.py (assumes you have [uv](https://docs.astral.sh/uv/) installed):

```base
uv run mother.py
```

## You know, we manufacture those, by the way.

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) to discuss more 80s movies (or possibly TUIs).
````

## File: docs/blog/posts/await-me-maybe.md
````markdown
---
draft: false
date: 2023-03-15
categories:
  - DevLog
authors:
  - willmcgugan
---

# No-async async with Python

A (reasonable) criticism of async is that it tends to proliferate in your code. In order to `await` something, your functions must be `async` all the way up the call-stack. This tends to result in you making things `async` just to support that one call that needs it or, worse, adding `async` just-in-case. Given that going from `def` to `async def` is a breaking change there is a strong incentive to go straight there.

Before you know it, you have adopted a policy of "async all the things".

<!-- more -->

Textual is an async framework, but doesn't *require* the app developer to use the `async` and `await` keywords (but you can if you need to). This post is about how Textual accomplishes this async-agnosticism.

!!! info

    See this [example](https://textual.textualize.io/guide/widgets/#attributes-down) from the docs for an async-less Textual app.


## An apology

But first, an apology! In a previous post I said Textual "doesn't do any IO of its own". This is not accurate. Textual responds to keys and mouse events (**I**nput) and writes content to the terminal (**O**utput).

Although Textual clearly does do IO, it uses `asyncio` mainly for *concurrency*. It allows each widget to update its part of the screen independently from the rest of the app.

## Await me (maybe)

The first no-async async technique is the "Await me maybe" pattern, a term first coined by [Simon Willison](https://simonwillison.net/2020/Sep/2/await-me-maybe/). This is particularly applicable to callbacks (or in Textual terms, message handlers).

The `await_me_maybe` function below can run a callback that is either a plain old function *or* a coroutine (`async def`). It does this by awaiting the result of the callback if it is awaitable, or simply returning the result if it is not.


```python
import asyncio
import inspect


def plain_old_function():
    return "Plain old function"

async def async_function():
    return "Async function"


async def await_me_maybe(callback):
    result = callback()
    if inspect.isawaitable(result):
        return await result
    return result


async def run_framework():
    print(
        await await_me_maybe(plain_old_function)
    )
    print(
        await await_me_maybe(async_function)
    )


if __name__ == "__main__":
    asyncio.run(run_framework())
```

## Optionally awaitable

The "await me maybe" pattern is great when an async framework calls the app's code. The app developer can choose to write async code or not. Things get a little more complicated when the app wants to call the framework's API. If the API has *asynced all the things*, then it would force the app to do the same.

Textual's API consists of regular methods for the most part, but there are a few methods which are optionally awaitable. These are *not* coroutines (which must be awaited to do anything).

In practice, this means that those API calls initiate something which will complete a short time later. If you discard the return value then it won't prevent it from working. You only need to `await` if you want to know when it has finished.

The `mount` method is one such method. Calling it will add a widget to the screen:

```python
def on_key(self):
    # Add MyWidget to the screen
    self.mount(MyWidget("Hello, World!"))
```

In this example we don't care that the widget hasn't been mounted immediately, only that it will be soon.

!!! note

    Textual awaits the result of mount after the message handler, so even if you don't *explicitly* await it, it will have been completed by the time the next message handler runs.

We might care if we want to mount a widget then make some changes to it. By making the handler `async` and awaiting the result of mount, we can be sure that the widget has been initialized before we update it:

```python
async def on_key(self):
    # Add MyWidget to the screen
    await self.mount(MyWidget("Hello, World!"))
    # add a border
    self.query_one(MyWidget).styles.border = ("heavy", "red")
```

Incidentally, I found there were very few examples of writing awaitable objects in Python. So here is the code for `AwaitMount` which is returned by the `mount` method:

```python
class AwaitMount:
    """An awaitable returned by mount() and mount_all()."""

    def __init__(self, parent: Widget, widgets: Sequence[Widget]) -> None:
        self._parent = parent
        self._widgets = widgets

    async def __call__(self) -> None:
        """Allows awaiting via a call operation."""
        await self

    def __await__(self) -> Generator[None, None, None]:
        async def await_mount() -> None:
            if self._widgets:
                aws = [
                    create_task(widget._mounted_event.wait(), name="await mount")
                    for widget in self._widgets
                ]
                if aws:
                    await wait(aws)
                    self._parent.refresh(layout=True)

        return await_mount().__await__()
```

## Summing up

Textual did initially "async all the things", which you might see if you find some old Textual code. Now async is optional.

This is not because I dislike async. I'm a fan! But it does place a small burden on the developer (more to type and think about). With the current API you generally don't need to write coroutines, or remember to await things. But async is there if you need it.

We're finding that Textual is increasingly becoming a UI to things which are naturally concurrent, so async was a good move. Concurrency can be a tricky subject, so we're planning some API magic to take the pain out of running tasks, threads, and processes. Stay tuned!

Join us on our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to talk about these things with the Textualize developers.
````

## File: docs/blog/posts/be-the-keymaster.md
````markdown
---
draft: false
date: 2022-12-08
categories:
  - DevLog
authors:
  - davep
---

# Be the Keymaster!

## That didn't go to plan

So... yeah... the blog. When I wrote [my previous (and first)
post](https://textual.textualize.io/blog/2022/11/26/on-dog-food-the-original-metaverse-and-not-being-bored/)
I had wanted to try and do a post towards the end of each week, highlighting
what I'd done on the "dogfooding" front. Life kinda had other plans. Not in
a terrible way, but it turns out that getting both flu and Covid jabs (AKA
"jags" as they tend to say in my adopted home) on the same day doesn't
really agree with me too well.

I *have* been working, but there's been some odd moments in the past week
and a bit and, last week, once I got to the end, I was glad for it to end.
So no blog post happened.

Anyway...

<!-- more -->

## What have I been up to?

While mostly sat feeling sorry for myself on my sofa, I have been coding.
Rather than list all the different things here in detail, I'll quickly
mention them with links to where to find them and play with them if you
want:

### FivePyFive

While my Textual 5x5 puzzle is [one of the examples in the Textual
repo](https://github.com/Textualize/textual/tree/main/examples), I wanted to
make it more widely available so people can download it with `pip` or
[`pipx`](https://pypa.github.io/pipx/). See [over on
PyPi](https://pypi.org/project/fivepyfive/) and see if you can solve it. ;-)

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/Rf34Z5r7Q60"
        title="PISpy" frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

### textual-qrcode

I wanted to put together a very small example of how someone may put
together a third party widget library, and in doing so selected what I
thought was going to be a mostly-useless example: [a wrapper around a
text-based QR code generator
website](https://pypi.org/project/textual-qrcode/). Weirdly I've had a
couple of people express a need for QR codes in the terminal since
publishing that!

![A Textual QR Code](../images/2022-12-08-davep-devlog/textual-qrcode.png)

### PISpy

[PISpy](https://pypi.org/project/pispy-client/) is a very simple
terminal-based client for the [PyPi
API](https://warehouse.pypa.io/api-reference/). Mostly it provides a
hypertext interface to Python package details, letting you look up a package
and then follow its dependency links. It's *very* simple at the moment, but
I think more fun things can be done with this.

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/yMGD6bXqIEo"
        title="PISpy" frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

### OIDIA

I'm a big fan of the use of streak-tracking in one form or another.
Personally I use a [streak-tracking app](https://streaksapp.com/) for
keeping tabs of all sorts of good (and bad) habits, and as a heavy user of
all things Apple I make a lot of use of [the Fitness
rings](https://www.apple.com/uk/watch/close-your-rings/), etc. So I got to
thinking it might be fun to do a really simple, no shaming, no counting,
just recording, steak app for the Terminal.
[OIDIA](https://pypi.org/project/oidia/) is the result.

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/3Kz8eUzO9-8"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

As of the time of writing I only finished the first version of this
yesterday evening, so there are plenty of rough edges; but having got it to
a point where it performed the basic tasks I wanted from it, that seemed
like a good time to publish.

Expect to see this getting more updates and polish.

## Wait, what about this Keymaster thing?

Ahh, yes, about that... So one of the handy things I'm finding about Textual
is its [key binding
system](https://textual.textualize.io/guide/input/#bindings). The more
I build Textual apps, the more I appreciate the bindings, how they can be
associated with specific widgets, the use of actions (which can be used from
other places too), etc.

But... (there's always a "but" right -- I mean, there'd be no blog post to
be had here otherwise).

The terminal doesn't have access to all the key combinations you may want to
use, and also, because some keys can't necessarily be "typed", at least not
easily (think about it: there's no <kbd>F1</kbd> character, you have to type
`F1`), many keys and key combinations need to be bound with specific names.

So there's two problems here: how do I discover what keys even turn up in my
application, and when they do, what should I call them when I pass them to
[`Binding`](https://textual.textualize.io/api/binding/#textual.binding.Binding)?

That felt like a *"well Dave just build an app for it!"* problem. So I did:

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/-MV8LFfEOZo"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

If you're building apps with Textual and you want to discover what keys turn
up from your terminal and are available to your application, you can:

```sh
$ pipx install textual-keys
```

and then just run `textual-keys` and start mashing the keyboard to find out.

There's a good chance that this app, or at least a version of it, will make
it into Textual itself (very likely as one of the
[devtools](https://textual.textualize.io/guide/devtools/)). But for now it's
just an easy install away.

I think there's a call to be made here too: have you built anything to help
speed up how you work with Textual, or just make the development experience
"just so"? If so, do let us know, and come yell about it on the
[`#show-and-tell`
channel](https://discord.com/channels/1026214085173461072/1033752599112994867)
in [our Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/posts/better-sleep-on-windows.md
````markdown
---
draft: false
date: 2022-12-30
categories:
  - DevLog
authors:
  - willmcgugan
---
# A better asyncio sleep for Windows to fix animation

I spent some time optimizing Textual on Windows recently, and discovered something which may be of interest to anyone working with async code on that platform.

<!-- more -->

Animation, scrolling, and fading had always been unsatisfactory on Windows. Textual was usable, but the lag when scrolling made apps feel far less snappy that other platforms. On macOS and Linux, scrolling is fast enough that it feels close to a native app, not something running in a terminal. Yet the Windows experience never improved, even as Textual got faster with each release.

I had chalked this up to Windows Terminal being slow to render updates. After all, the classic Windows terminal was (and still is) glacially slow. Perhaps Microsoft just weren't focusing on performance.

In retrospect, that was highly improbable. Like all modern terminals, Windows Terminal uses the GPU to render updates. Even without focussing on performance, it should be fast.

I figured I'd give it one last attempt to speed up Textual on Windows. If I failed, Windows would forever be a third-class platform for Textual apps.

It turned out that it was nothing to do with performance, per se. The issue was with a single asyncio function: `asyncio.sleep`.

Textual has a `Timer` class which creates events at regular intervals. It powers the JS-like `set_interval` and `set_timer` functions. It is also used internally to do animation (such as smooth scrolling). This Timer class calls `asyncio.sleep` to wait the time between one event and the next.

On macOS and Linux, calling `asynco.sleep` is fairly accurate. If you call `sleep(3.14)`, it will return within 1% of 3.14 seconds. This is not the case for Windows, which for historical reasons uses a timer with a granularity of 15 milliseconds. The upshot is that sleep times will be rounded up to the nearest multiple of 15 milliseconds.

This limit appears to hold true for all async primitives on Windows. If you wait for something with a timeout, it will return on a multiple of 15 milliseconds. Fortunately there is work in the CPython pipeline to make this more accurate. Thanks to [Steve Dower](https://twitter.com/zooba) for pointing this out.

This lack of accuracy in the timer meant that timer events were created at a far slower rate than intended. Animation was slower because Textual was waiting too long between updates.

Once I had figured that out, I needed an alternative to `asyncio.sleep` for Textual's Timer class. And I found one. The following version of `sleep` is accurate to well within 1%:

```python
from time import sleep as time_sleep
from asyncio import get_running_loop

async def sleep(sleep_for: float) -> None:
    """An asyncio sleep.

    On Windows this achieves a better granularity than asyncio.sleep

    Args:
        sleep_for (float): Seconds to sleep for.
    """    
    await get_running_loop().run_in_executor(None, time_sleep, sleep_for)

```

That is a drop-in replacement for sleep on Windows. With it, Textual runs a *lot* smoother. Easily on par with macOS and Linux.

It's not quite perfect. There is a little *tearing* during full "screen" updates, but performance is decent all round. I suspect when [this bug]( https://bugs.python.org/issue37871) is fixed (big thanks to [Paul Moore](https://twitter.com/pf_moore) for looking in to that), and Microsoft implements [this protocol](https://gist.github.com/christianparpart/d8a62cc1ab659194337d73e399004036) then Textual on Windows will be A+.

This Windows improvement will be in v0.9.0 of [Textual](https://github.com/Textualize/textual), which will be released in a few days.
````

## File: docs/blog/posts/create-task-psa.md
````markdown
---
draft: false
date: 2023-02-11
categories:
  - DevLog
authors:
  - willmcgugan
---

# The Heisenbug lurking in your async code

I'm taking a brief break from blogging about [Textual](https://github.com/Textualize/textual) to bring you this brief PSA for Python developers who work with async code. I wanted to expand a little on this [tweet](https://twitter.com/willmcgugan/status/1624419352211603461).

<!-- more -->

If you have ever used `asyncio.create_task` you may have created a bug for yourself that is challenging (read *almost impossible*) to reproduce. If it occurs, your code will likely fail in unpredictable ways.

The root cause of this [Heisenbug](https://en.wikipedia.org/wiki/Heisenbug) is that if you don't hold a reference to the task object returned by `create_task` then the task may disappear without warning when Python runs garbage collection. In other words, the code in your task will stop running with no obvious indication why.

This behavior is [well documented](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task), as you can see from this excerpt (emphasis mine):

![create task](../images/async-create-task.jpeg)

But who reads all the docs? And who has perfect recall if they do? A search on GitHub indicates that there are a [lot of projects](https://github.com/search?q=%22asyncio.create_task%28%22&type=code) where this bug is waiting for just the right moment to ruin somebody's day.

I suspect the reason this mistake is so common is that tasks are a lot like threads (conceptually at least). With threads you can just launch them and forget. Unless you mark them as "daemon" threads they will exist for the lifetime of your app. Not so with Tasks.

The solution recommended in the docs is to keep a reference to the task for as long as you need it to live. On modern Python you could use [TaskGroups](https://docs.python.org/3/library/asyncio-task.html#task-groups) which will keep references to your tasks. As long as all the tasks you spin up are in TaskGroups, you should be fine.
````

## File: docs/blog/posts/creating-tasks-overhead.md
````markdown
---
draft: false
date: 2023-03-08
categories:
  - DevLog
authors:
  - willmcgugan
---

# Overhead of Python Asyncio tasks

Every widget in Textual, be it a button, tree view, or a text input, runs an [asyncio](https://docs.python.org/3/library/asyncio.html) task. There is even a task for [scrollbar corners](https://github.com/Textualize/textual/blob/e95a65fa56e5b19715180f9e17c7f6747ba15ec5/src/textual/scrollbar.py#L365) (the little space formed when horizontal and vertical scrollbars meet).

<!-- more -->

!!! info

    It may be IO that gives AsyncIO its name, but Textual doesn't do any IO of its own. Those tasks are used to power *message queues*, so that widgets (UI components) can do whatever they do at their own pace.

Its fair to say that Textual apps launch a lot of tasks. Which is why when I was trying to optimize startup (for apps with 1000s of widgets) I suspected it was task related.

I needed to know how much of an overhead it was to launch tasks. Tasks are lighter weight than threads, but how much lighter? The only way to know for certain was to profile.

The following code launches a load of *do nothing* tasks, then waits for them to shut down. This would give me an idea of how performant `create_task` is, and also a *baseline* for optimizations. I would know the absolute limit of any optimizations I make.

```python
from asyncio import create_task, wait, run
from time import process_time as time


async def time_tasks(count=100) -> float:
    """Time creating and destroying tasks."""

    async def nop_task() -> None:
        """Do nothing task."""
        pass

    start = time()
    tasks = [create_task(nop_task()) for _ in range(count)]
    await wait(tasks)
    elapsed = time() - start
    return elapsed


for count in range(100_000, 1000_000 + 1, 100_000):
    create_time = run(time_tasks(count))
    create_per_second = 1 / (create_time / count)
    print(f"{count:,} tasks \t {create_per_second:0,.0f} tasks per/s")
```

And here is the output:

```
100,000 tasks    280,003 tasks per/s
200,000 tasks    255,275 tasks per/s
300,000 tasks    248,713 tasks per/s
400,000 tasks    248,383 tasks per/s
500,000 tasks    241,624 tasks per/s
600,000 tasks    260,660 tasks per/s
700,000 tasks    244,510 tasks per/s
800,000 tasks    247,455 tasks per/s
900,000 tasks    242,744 tasks per/s
1,000,000 tasks          259,715 tasks per/s
```

!!! info

    Running on an M1 MacBook Pro.

This tells me I can create, run, and shutdown 260K tasks per second.

That's fast.

Clearly `create_task` is as close as you get to free in the Python world, and I would need to look elsewhere for optimizations. Turns out Textual spends far more time processing CSS rules than creating tasks (obvious in retrospect). I've noticed some big wins there, so the next version of Textual will be faster to start apps with a metric tonne of widgets.

But I still need to know what to do with those scrollbar corners. A task for two characters. I don't even...
````

## File: docs/blog/posts/darren-year-in-review.md
````markdown
---
draft: false
date: 2022-12-20
categories:
  - DevLog
authors:
  - darrenburns
---
# A year of building for the terminal

I joined Textualize back in January 2022, and since then have been hard at work with the team on both [Rich](https://github.com/Textualize/rich) and [Textual](https://github.com/Textualize/textual).
Over the course of the year, I’ve been able to work on a lot of really cool things.
In this post, I’ll review a subset of the more interesting and visual stuff I’ve built. If you’re into terminals and command line tooling, you’ll hopefully see at least one thing of interest!

<!-- more -->

## A file manager powered by Textual

I’ve been slowly developing a file manager as a “dogfooding” project for Textual. It takes inspiration from tools such as Ranger and Midnight Commander.

![Untitled](../images/darren-year-in-review/Untitled.png)

As of December 2022, it lets you browse your file system, filtering, multi-selection, creating and deleting files/directories, opening files in your `$EDITOR` and more.

I’m happy with how far this project has come — I think it’s a good example of the type of powerful application that can be built with Textual with relatively little code. I’ve been able to focus on *features*, instead of worrying about terminal emulator implementation details.

![filemanager-trimmed.gif](../images/darren-year-in-review/filemanager-trimmed.gif)

The project is available [on GitHub](https://github.com/darrenburns/kupo).

## Better diffs in the terminal

Diffs in the terminal are often difficult to read at a glance. I wanted to see how close I could get to achieving a diff display of a quality similar to that found in the GitHub UI.

To attempt this, I built a tool called [Dunk](https://github.com/darrenburns/dunk). It’s a command line program which you can pipe your `git diff` output into, and it’ll convert it into something which I find much more readable.

![Untitled](../images/darren-year-in-review/Untitled%201.png)

Although I’m not particularly proud of the code - there are a lot of “hacks” going on, but I’m proud of the result. If anything, it shows what can be achieved for tools like this.

For many diffs, the difference between running `git diff` and `git diff | dunk | less -R` is night and day.

![Untitled](../images/darren-year-in-review/Untitled%202.png)

It’d be interesting to revisit this at some point.
It has its issues, but I’d love to see how it can be used alongside Textual to build a terminal-based diff/merge tool. Perhaps it could be combined with…

## Code editor floating gutter

This is a common feature in text editors and IDEs: when you scroll to the right, you should still be able to see what line you’re on. Out of interest, I tried to recreate the effect in the terminal using Textual.

![floating-gutter.gif](../images/darren-year-in-review/floating-gutter.gif)

Textual CSS offers a `dock` property which allows you to attach a widget to an edge of its parent.
By creating a widget that contains a vertical list of numbers and setting the `dock` property to `left`, we can create a floating gutter effect.
Then, we just need to keep the `scroll_y` in sync between the gutter and the content to ensure the line numbers stay aligned.

## Dropdown autocompletion menu

While working on [Shira](https://github.com/darrenburns/shira) (a proof-of-concept, terminal-based Python object explorer), I wrote some autocompleting dropdown functionality.

![shira-demo.gif](../images/darren-year-in-review/shira-demo.gif)

Textual forgoes the z-index concept from browser CSS and instead uses a “named layer” system. Using the `layers` property you can defined an ordered list of named layers, and using the `layer` property, you can assign a descendant widget to one of those layers.

By creating a new layer above all others and assigning a widget to that layer, we can ensure that widget is painted above everything else.

In order to determine where to place the dropdown, we can track the current value in the dropdown by `watch`ing the reactive input “value” inside the Input widget. This method will be called every time the `value` of the Input changes, and we can use this hook to amend the position of our dropdown position to accommodate for the length of the input value.

![Untitled](../images/darren-year-in-review/Untitled%203.png)

I’ve now extracted this into a separate library called [textual-autocomplete](https://github.com/darrenburns/textual-autocomplete).

## Tabs with animated underline

The aim here was to create a tab widget with underlines that animates smoothly as another tab is selected.

<video style="position: relative; width: 100%;" controls autoplay loop><source src="../../../../images/darren-year-in-review/tabs-textual-video-demo.mp4" type="video/mp4"></video>

The difficulty with implementing something like this is that we don’t have pixel-perfect resolution when animating - a terminal window is just a big grid of fixed-width character cells.

![Untitled](../images/darren-year-in-review/Untitled%204.png){ align=right width=250 }
However, when animating things in a terminal, we can often achieve better granularity using Unicode related tricks. In this case, instead of shifting the bar along one whole cell, we adjust the endings of the bar to be a character which takes up half of a cell.

The exact characters that form the bar are "╺", "━" and "╸". When the bar sits perfectly within cell boundaries, every character is “━”. As it travels over a cell boundary, the left and right ends of the bar are updated to "╺" and "╸" respectively.

## Snapshot testing for terminal apps

One of the great features we added to Rich this year was the ability to export console contents to an SVG. This feature was later exposed to Textual, allowing users to capture screenshots of their running Textual apps.
Ultimately, I ended up creating a tool for snapshot testing in the Textual codebase.

Snapshot testing is used to ensure that Textual output doesn’t unexpectedly change. On disk, we store what we expect the output to look like. Then, when we run our unit tests, we get immediately alerted if the output has changed.

This essentially automates the process of manually spinning up several apps and inspecting them for unexpected visual changes. It’s great for catching subtle regressions!

In Textual, each CSS property has its own canonical example and an associated snapshot test.
If we accidentally break a property in a way that affects the visual output, the chances of it sneaking into a release are greatly reduced, because the corresponding snapshot test will fail.

As part of this work, I built a web interface for comparing snapshots with test output.
There’s even a little toggle which highlights the differences, since they’re sometimes rather subtle.

<video style="position: relative; width: 100%;" controls autoplay loop><source src="../../../../images/darren-year-in-review/Screen_Recording_2022-12-14_at_14.08.15.mov" type="video/mp4"></video>

Since the terminal output shown in the video above is just an SVG image, I was able to add the "Show difference" functionality
by overlaying the two images and applying a single CSS property: `mix-blend-mode: difference;`.

The snapshot testing functionality itself is implemented as a pytest plugin, and it builds on top of a snapshot testing framework called [syrupy](https://github.com/tophat/syrupy).

![Screenshot 2022-09-16 at 15.52.03.png](..%2Fimages%2Fdarren-year-in-review%2FScreenshot%202022-09-16%20at%2015.52.03.png)

It's quite likely that this will eventually be exposed to end-users of Textual.

## Demonstrating animation

I built an example app to demonstrate how to animate in Textual and the available easing functions.

<video style="position: relative; width: 100%;" controls loop><source src="../../../../images/darren-year-in-review/animation-easing-example.mov" type="video/mp4"></video>

The smoothness here is achieved using tricks similar to those used in the tabs I discussed earlier.
In fact, the bar that animates in the video above is the same Rich renderable that is used by Textual's scrollbars.

You can play with this app by running `textual easing`. Please use animation sparingly.

## Developer console

When developing terminal based applications, performing simple debugging using `print` can be difficult, since the terminal is in application mode.

A project I worked on earlier in the year to improve the situation was the Textual developer console, which you can launch with `textual console`.

<div>
<figure markdown>
    <img src="../../../../images/darren-year-in-review/devtools.png">
    <figcaption>On the right, <a href="https://twitter.com/davepdotorg">Dave's</a> 5x5 Textual app. On the left, the Textual console.</figcaption>
</figure>
</div>

Then, by running a Textual application with the `--dev` flag, all standard output will be redirected to it.
This means you can use the builtin `print` function and still immediately see the output.
Textual itself also writes information to this console, giving insight into the messages that are flowing through an application.

## Pixel art

Cells in the terminal are roughly two times taller than they are wide. This means, that two horizontally adjacent cells form an approximate square.

Using this fact, I wrote a simple library based on Rich and PIL which can convert an image file into terminal output.
You can find the library, `rich-pixels`, [on GitHub](https://github.com/darrenburns/rich-pixels).

It’s particularly good for displaying simple pixel art images. The SVG image below is also a good example of the SVG export functionality I touched on earlier.

<div>
--8<-- "docs/blog/images/darren-year-in-review/bulbasaur.svg"
</div>

Since the library generates an object which is renderable using Rich, these can easily be embedded inside Textual applications.

Here's an example of that in a scrapped "Pokédex" app I threw together:

<video style="position: relative; width: 100%;" controls autoplay loop><source src="../../../../images/darren-year-in-review/pokedex-terminal.mov" type="video/mp4"></video>

This is a rather naive approach to the problem... but I did it for fun!

Other methods for displaying images in the terminal include:

- A more advanced library like [chafa](https://github.com/hpjansson/chafa), which uses a range of Unicode characters to achieve a more accurate representation of the image.
- One of the available terminal image protocols, such as Sixel, Kitty’s Terminal Graphics Protocol, and iTerm Inline Images Protocol.

<hr>

That was a whirlwind tour of just some of the projects I tackled in 2022.
If you found it interesting, be sure to [follow me on Twitter](https://twitter.com/_darrenburns).
I don't post often, but when I do, it's usually about things similar to those I've discussed here.
````

## File: docs/blog/posts/future-of-textualize.md
````markdown
---
draft: false
date: 2025-05-07
title: "The future of Textualize"
categories:
  - News
authors:
  - willmcgugan
---

Textual has come a *long* way since I figured why not build an application framework on top of [Rich](https://github.com/Textualize/rich).

Both were initially hobby projects. I mean look how much fun I was having back then:

<!-- more -->

<blockquote class="twitter-tweet" data-media-max-width="560"><p lang="en" dir="ltr">Making good progress with Textual CSS. <br><br>Here&#39;s a &quot;basic&quot; app. The <a href="https://twitter.com/hashtag/Python?src=hash&amp;ref_src=twsrc%5Etfw">#Python</a> + CSS in the screenshots generates the layout in the terminal here.<br><br>Separating the layout and design from the runtime logic will make it easy to create gorgeous TUI apps. 🤩 <a href="https://t.co/Rxnwzs4pXd">pic.twitter.com/Rxnwzs4pXd</a></p>&mdash; Will McGugan (@willmcgugan) <a href="https://twitter.com/willmcgugan/status/1463977921891217411?ref_src=twsrc%5Etfw">November 25, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

Working on Textual has been a constant source of delight; figuring out how to make a terminal do things that it shouldn't really be able to do, and to a lesser extent a source of frustration when working around the baffling edge cases in emulators and the terminal protocol.

But work around it we did, and now Textual is an awesome piece of software that has spawned a community of developers building TUIs for [all kinds of things](https://github.com/textualize/transcendent-textual) (not to mention, [web apps](https://github.com/Textualize/textual-serve))!

Additionally, Textual has some of the [best docs](https://textual.textualize.io/guide/screens/) for any Open Source project. Shout out to [@squidfunk](https://x.com/squidfunk) and [@pawamoy](https://x.com/pawamoy) for the tech that makes these beautiful docs possible.

Ultimately though a business needs a product. Textual has always been a solution in search of a problem. And while there are plenty of problems to which Textual is a fantastic solution, we weren't able to find a shared problem or pain-point to build a viable business around. Which is why Textualize, the company, will be wrapping up in the next few weeks.

Textual will live on as an Open Source project. In the near term, nothing much will change. I will be maintaining Textual and Rich as I have always done. Software is never finished, but Textual is mature and battle-tested. I'm confident transitioning from a full-time funded project to a community project won't have a negative impact.

## Thanks!

I'd like to thank the awesome devs I worked with at Textualize, and the many developers that followed along, contributing and building apps. Wether you were an early adopter or you just discovered Textual, you made Textual what it is today.

## Get in touch

If you would like to talk Textual, feel free to find me on our [Discord server](https://github.com/textualize/textual/) or the socials.

I've also started a [blog](https://willmcgugan.github.io/) where I will write a little more on this from a more personal perspective.
````

## File: docs/blog/posts/helo-world.md
````markdown
---
draft: false 
date: 2022-11-06
categories:
  - News
authors:
  - willmcgugan
---

# New Blog

Welcome to the first post on the Textual blog.

<!-- more -->

I plan on using this as a place to make announcements regarding new releases of Textual, and any other relevant news.

The first piece of news is that we've reorganized this site a little. The Events, Styles, and Widgets references are now under "Reference", and what used to be under "Reference" is now "API" which contains API-level documentation. I hope that's a little clearer than it used to be!
````

## File: docs/blog/posts/inline-mode.md
````markdown
---
draft: false
date: 2024-04-20
categories:
  - DevLog
authors:
  - willmcgugan
---

# Behind the Curtain of Inline Terminal Applications

Textual recently added the ability to run *inline* terminal apps.
You can see this in action if you run the [calculator example](https://github.com/Textualize/textual/blob/main/examples/calculator.py):

![Inline Calculator](../images/calcinline.png)

The application appears directly under the prompt, rather than occupying the full height of the screen&mdash;which is more typical of TUI applications.
You can interact with this calculator using keys *or* the mouse.
When you press ++ctrl+q++ the calculator disappears and returns you to the prompt.

Here's another app that creates an inline code editor:

=== "Video"

    <div class="video-wrapper">
        <iframe width="852" height="525" src="https://www.youtube.com/embed/Dt70oSID1DY" title="Inline app" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>


=== "inline.py"
    ```python 
    from textual.app import App, ComposeResult
    from textual.widgets import TextArea


    class InlineApp(App):
        CSS = """
        TextArea {
            height: auto;
            max-height: 50vh;
        }
        """

        def compose(self) -> ComposeResult:
            yield TextArea(language="python")


    if __name__ == "__main__":
        InlineApp().run(inline=True)

    ```

This post will cover some of what goes on under the hood to make such inline apps work.

It's not going to go in to too much detail.
I'm assuming most readers will be more interested in a birds-eye view rather than all the gory details.

<!-- more -->

## Programming the terminal

Firstly, let's recap how you program the terminal.
Broadly speaking, the terminal is a device for displaying text.
You write (or print) text to the terminal which typically appears at the end of a continually growing text buffer.
In addition to text you can also send [escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code), which are short sequences of characters that instruct the terminal to do things such as change the text color, scroll, or other more exotic things.

We only need a few of these escape codes to implement inline apps.

!!! note

    I will gloss over the exact characters used for these escape codes.
    It's enough to know that they exist for now.
    If you implement any of this yourself, refer to the [wikipedia article](https://en.wikipedia.org/wiki/ANSI_escape_code). 

## Rendering frames

The first step is to display the app, which is simply text (possibly with escape sequences to change color and style).
The lines are terminated with a newline character (`"\n"`), *except* for the very last line (otherwise we get a blank line a the end which we don't need).
Rather than a final newline, we write an escape code that moves the *cursor* back to it's prior position.

The cursor is where text will be written.
It's the same cursor you see as you type.
Normally it will be at the end of the text in the terminal, but it can be moved around terminal with escape codes.
It can be made invisible (as in Textual apps), but the terminal will keep track of the cursor, even if it can not be seen.

Textual moves the cursor back to its original starting position so that subsequent frames will overwrite the previous frame.

Here's a diagram that shows how the cursor is positioned:

!!! note

    I've drawn the cursor in red, although it isn't typically visible.


<div class="excalidraw">
--8<-- "docs/blog/images/inline1.excalidraw.svg"
</div>


There is an additional consideration that comes in to play when the output has less lines than the previous frame.
If we were to write a shorter frame, it wouldn't fully overwrite the previous frame.
We would be left with a few lines of a previous frame that wouldn't update.

The solution to this problem is to write an escape code that clears lines from the cursor downwards before we write a smaller frame.
You can see this in action in the above video.
The inline app can grow or shrink in size, and still be anchored to the bottom of the terminal.

## Cursor input

The cursor tells the terminal where any text will be written by the app, but it also assumes this will be where the user enters text.
If you enter CJK (Chinese Japanese Korean) text in to the terminal, you will typically see a floating control that points where new text will be written.
If you are on a Mac, the emoji entry dialog (++ctrl+cmd+space++) will also point at the current cursor position. To make this work in a sane way, we need to move the terminal's cursor to where any new text will appear.

The following diagram shows the cursor moving to the point where new text is displayed.

<div class="excalidraw">
--8<-- "docs/blog/images/inline2.excalidraw.svg"
</div>

This only really impacts text entry (such as the [Input](https://textual.textualize.io/widget_gallery/#input) and [TextArea](https://textual.textualize.io/widget_gallery/#textarea) widgets).

## Mouse control

Inline apps in Textual support mouse input, which works the same as fullscreen apps.

To use the mouse in the terminal you send an escape code which tells the terminal to write encoded mouse coordinates to standard input.
The mouse coordinates can then be parsed in much the same was as reading keys.

In inline mode this works in a similar way, with an added complication that the mouse origin is at the top left of the terminal.
In other words if you move the mouse to the top left of the terminal you get coordinate (0, 0), but the app expects (0, 0) to be where it was displayed.

In order for the app to know where the mouse is relative to it's origin, we need to *ask* the terminal where the cursor is.
We do this with an escape code, which tells the terminal to write the current cursor coordinate to standard input.
We can then subtract that coordinate from the physical mouse coordinates, so we can send the app mouse events relative to its on-screen origin.


## tl;dr

[Escapes codes](https://en.wikipedia.org/wiki/ANSI_escape_code).

## Found this interesting?

If you are interested in Textual, join our [Discord server](https://discord.gg/Enf6Z3qhVr).

Or follow me for more terminal shenanigans.

- [@willmcgugan](https://twitter.com/willmcgugan)
- [mastodon.social/@willmcgugan](https://mastodon.social/@willmcgugan)
````

## File: docs/blog/posts/looking-for-help.md
````markdown
---
draft: false
date: 2023-01-09
categories:
  - DevLog
authors:
  - davep
---

# So you're looking for a wee bit of Textual help...

## Introduction

!!! quote

    Patience, Highlander. You have done well. But it'll take time. You are
    generations being born and dying. You are at one with all living things.
    Each man's thoughts and dreams are yours to know. You have power beyond
    imagination. Use it well, my friend. Don't lose your head.

    <cite>Juan Sánchez Villalobos Ramírez, Chief metallurgist to King Charles V of Spain</cite>

As of the time of writing, I'm a couple or so days off having been with
Textualize for 3 months. It's been fun, and educational, and every bit as
engaging as I'd hoped, and more. One thing I hadn't quite prepared for
though, but which I really love, is how so many other people are learning
Textual along with me.

<!-- more -->

Even in those three months the library has changed and expanded quite a lot,
and it continues to do so. Meanwhile, more people are turning up and using
the framework; you can see this online in social media, blogs and of course
[in the ever-growing list of projects on GitHub which depend on
Textual](https://github.com/Textualize/textual/network/dependents).

This inevitably means there's a lot of people getting to grips with a new
tool, and one that is still a bit of a moving target. This in turn means
lots of people are coming to us to get help.

As I've watched this happen I've noticed a few patterns emerging. Some of
these good or neutral, some... let's just say not really beneficial to those
seeking the help, or to those trying to provide the help. So I wanted to
write a little bit about the different ways you can get help with Textual
and your Textual-based projects, and to also try and encourage people to
take the most helpful and positive approach to getting that help.

Now, before I go on, I want to make something *very* clear: I'm writing this
as an individual. This is my own personal view, and my own advice from me to
anyone who wishes to take it. It's not Textual (the project) or Textualize
(the company) policy, rules or guidelines. This is just some ageing hacker's
take on how best to go about asking for help, informed by years of asking
for and also providing help in email, on Usenet, on forums, etc.

Or, put another way: if what you read in here seems sensible to you, I
figure we'll likely have already hit it off [over on
GitHub](https://github.com/Textualize/textual) or in [the Discord
server](https://discord.gg/Enf6Z3qhVr). ;-)

## Where to go for help

At this point this is almost a bit of an FAQ itself, so I thought I'd
address it here: where's the best place to ask for help about Textual, and
what's the difference between GitHub Issues, Discussions and our Discord
server?

I'd suggest thinking of them like this:

### Discord

You have a question, or need help with something, and perhaps you could do
with a reply as soon as possible. But, and this is the **really important
part**, it doesn't matter if you don't get a response. If you're in this
situation then the Discord server is possibly a good place to start. If
you're lucky someone will be hanging about who can help out.

I can't speak for anyone else, but keep this in mind: when I look in on
Discord I tend not to go scrolling back much to see if anything has been
missed. If something catches my eye, I'll try and reply, but if it
doesn't... well, it's mostly an instant chat thing so I don't dive too
deeply back in time.

!!! tip inline end "Going from Discord to a GitHub issue"

    As a slight aside here: sometimes people will pop up in Discord, ask a
    question about something that turns out looking like a bug, and that's
    the last we hear of it. Please, please, **please**, if this happens, the
    most helpful thing you can do is go raise an issue for us. It'll help us
    to keep track of problems, it'll help get your problem fixed, it'll mean
    everyone benefits.

My own advice would be to treat Discord as an ephemeral resource. It happens
in the moment but fades away pretty quickly. It's like knocking on a
friend's door to see if they're in. If they're not in, you might leave them
a note, which is sort of like going to...

### GitHub

On the other hand, if you have a question or need some help or something
where you want to stand a good chance of the Textual developers (amongst
others) seeing it and responding, I'd recommend that GitHub is the place to
go. Dropping something into the discussions there, or leaving an issue,
ensures it'll get seen. It won't get lost.

As for which you should use -- a discussion or an issue -- I'd suggest this:
if you need help with something, or you want to check your understanding of
something, or you just want to be sure something is a problem before taking
it further, a discussion might be the best thing. On the other hand, if
you've got a clear bug or feature request on your hands, an issue makes a
lot of sense.

Don't worry if you're not sure which camp your question or whatever falls
into though; go with what you think is right. There's no harm done either
way (I may move an issue to a discussion first before replying, if it's
really just a request for help -- but that's mostly so everyone can benefit
from finding it in the right place later on down the line).

## The dos and don'ts of getting help

Now on to the fun part. This is where I get a bit preachy. Ish. Kinda. A
little bit. Again, please remember, this isn't a set of rules, this isn't a
set of official guidelines, this is just a bunch of *"if you want my advice,
and I know you didn't ask but you've read this far so you actually sort of
did don't say I didn't warn you!"* waffle.

This isn't going to be an exhaustive collection, far from it. But I feel
these are some important highlights.

### Do...

When looking for help, in any of the locations mentioned above, I'd totally
encourage:

#### Be clear and detailed

Too much detail is almost always way better than not enough. *"My program
didn't run"*, often even with some of the code supplied, is so much harder
to help than *"I ran this code I'm posting here, and I expected this
particular outcome, and I expected it because I'd read this particular thing
in the docs and had comprehended it to mean this, but instead the outcome
was this exception here, and I'm a bit stuck -- can someone offer some
pointers?"*

The former approach means there often ends up having to be a back and forth
which can last a long time, and which can sometimes be frustrating for the
person asking. Manage frustration: be clear, tell us everything you can.

#### Say what resources you've used already

If you've read the potions of the documentation that relate to what you're
trying to do, it's going to be really helpful if you say so. If you don't,
it might be assumed you haven't and you may end up being pointed at them.

So, please, if you've checked the documentation, looked in the FAQ, done a
search of past issues or discussions or perhaps even done a search on the
Discord server... please say so.

#### Be polite

This one can go a long way when looking for help. Look, I get it,
programming is bloody frustrating at times. We've all rage-quit some code at
some point, I'm sure. It's likely going to be your moment of greatest
frustration when you go looking for help. But if you turn up looking for
help acting all grumpy and stuff it's not going to come over well. Folk are
less likely to be motivated to lend a hand to someone who seems rather
annoyed.

If you throw in a please and thank-you here and there that makes it all the
better.

#### Fully consider the replies

You could find yourself getting a reply that you're sure won't help at all.
That's fair. But be sure to fully consider it first. Perhaps you missed the
obvious along the way and this is 100% the course correction you'd
unknowingly come looking for in the first place. Sure, the person replying
might have totally misunderstood what was being asked, or might be giving a
wrong answer (it me! I've totally done that and will again!), but even then
a reply along the lines of *"I'm not sure that's what I'm looking for,
because..."* gets everyone to the solution faster than *"lol nah"*.

#### Entertain what might seem like odd questions

Aye, I get it, being asked questions when you're looking for an *answer* can
be a bit frustrating. But if you find yourself on the receiving end of a
small series of questions about your question, keep this in mind: Textual is
still rather new and still developing and it's possible that what you're
trying to do isn't the correct way to do that thing. To the person looking
to help you it may seem to them you have an [XY
problem](https://en.wikipedia.org/wiki/XY_problem).

Entertaining those questions might just get you to the real solution to your
problem.

#### Allow for language differences

You don't need me to tell you that a project such as Textual has a global
audience. With that rather obvious fact comes the other fact that we don't
all share the same first language. So, please, as much as possible, try and
allow for that. If someone is trying to help you out, and they make it clear
they're struggling to follow you, keep this in mind.

#### Acknowledge the answer

I suppose this is a variation on "be polite" (really, a thanks can go a long
way), but there's more to this than a friendly acknowledgement. If someone
has gone to the trouble of offering some help, it's helpful to everyone who
comes after you to acknowledge if it worked or not. That way a future
help-seeker will know if the answer they're reading stands a chance of being
the right one.

#### Accept that Textual is zero-point software (right now)

Of course the aim is to have every release of Textual be stable and useful,
but things will break. So, please, do keep in mind things like:

- Textual likely doesn't have your feature of choice just yet.
- We might accidentally break something (perhaps pinning Textual and testing
  each release is a good plan here?).
- We might deliberately break something because we've decided to take a
  particular feature or way of doing things in a better direction.

Of course it can be a bit frustrating a times, but overall the aim is to
have the best framework possible in the long run.

### Don't...

Okay, now for a bit of old-hacker finger-wagging. Here's a few things I'd
personally discourage:

#### Lack patience

Sure, it can be annoying. You're in your flow, you've got a neat idea for a
thing you want to build, you're stuck on one particular thing and you really
need help right now! Thing is, that's unlikely to happen. Badgering
individuals, or a whole resource, to reply right now, or complaining that
it's been `$TIME_PERIOD` since you asked and nobody has replied... that's
just going to make people less likely to reply.

#### Unnecessarily tag individuals

This one often goes hand in hand with the "lack patience" thing: Be it
asking on Discord, or in GitHub issues, discussions or even PRs,
unnecessarily tagging individuals is a bit rude. Speaking for myself and
only myself: I *love* helping folk with Textual. If I could help everyone
all the time the moment they have a problem, I would. But it doesn't work
like that. There's any number of reasons I might not be responding to a
particular request, including but not limited to (here I'm talking
personally because I don't want to speak for anyone else, but I'm sure I'm
not alone here):

- I have a job. Sure, my job is (in part) Textual, but there's more to it
  than that particular issue. I might be doing other stuff.
- I have my own projects to work on too. I like coding for fun as well (or
  writing preaching old dude blog posts like this I guess, but you get the
  idea).
- I actually have other interests outside of work hours so I might actually
  be out doing a 10k in the local glen, or battling headcrabs in VR, or
  something.
- Housework. :-/

You get the idea though. So while I'm off having a well-rounded life, it's
not good to get unnecessarily intrusive alerts to something that either a)
doesn't actually directly involve me or b) could wait.

#### Seek personal support

Again, I'm going to speak totally for myself here, but I also feel the
general case is polite for all: there's a lot of good support resources
available already; sending DMs on Discord or Twitter or in the Fediverse,
looking for direct personal support, isn't really the best way to get help.
Using the public/collective resources is absolutely the *best* way to get
that help. Why's it a bad idea to dive into DMs? Here's some reasons I think
it's not a good idea:

- It's a variation on "unnecessarily tagging individuals".
- You're short-changing yourself when it comes to getting help. If you ask
  somewhere more public you're asking a much bigger audience, who
  collectively have more time, more knowledge and more experience than a
  single individual.
- Following on from that, any answers can be (politely) fact-checked or
  enhanced by that audience, resulting in a better chance of getting the
  best help possible.
- The next seeker-of-help gets to miss out on your question and the answer.
  If asked and answered in public, it's a record that can help someone else
  in the future.

#### Doubt your ability or skill level

I suppose this should really be phrased as a do rather than a don't, as here
I want to encourage something positive. A few times I've helped people out
who have been very apologetic about their questions being "noob" questions,
or about how they're fairly new to Python, or programming in general.
Really, please, don't feel the need to apologise and don't be ashamed of
where you're at.

If you've asked something that's obviously answered in the documentation,
that's not a problem; you'll likely get pointed at the docs and it's what
happens next that's the key bit. If the attitude is *"oh, cool, that's
exactly what I needed to be reading, thanks!"* that's a really positive
thing. The only time it's a problem is when there's a real reluctance to use
the available resources. We've all seen that person somewhere at some point,
right? ;-)

Not knowing things [is totally cool](https://xkcd.com/1053/).

## Conclusion

So, that's my waffle over. As I said at the start: this is my own personal
thoughts on how to get help with Textual, both as someone whose job it is to
work on Textual and help people with Textual, and also as a FOSS advocate
and supporter who can normally be found helping Textual users when he's not
"on the clock" too.

What I've written here isn't exhaustive. Neither is it novel. Plenty has
been written on the general subject in the past, and I'm sure more will be
written on the subject in the future. I do, however, feel that these are the
most common things I notice. I'd say those dos and don'ts cover 90% of *"can
I get some help?"* interactions; perhaps closer to 99%.

Finally, and I think this is the most important thing to remember, the next
time you are battling some issue while working with Textual: [don't lose
your head](https://www.youtube.com/watch?v=KdYvKF9O7Y8)!
````

## File: docs/blog/posts/on-dog-food-the-original-metaverse-and-not-being-bored.md
````markdown
---
draft: false
date: 2022-11-26
categories:
  - DevLog
authors:
  - davep
---

# On dog food, the (original) Metaverse, and (not) being bored

## Introduction

!!! quote

    Cutler, armed with a schedule, was urging the team to "eat its own dog
    food". Part macho stunt and part common sense, the "dog food diet" was the
    cornerstone of Cutler’s philosophy.

    <cite>G. Pascal Zachary &mdash; Show-Stopper!</cite>

I can't remember exactly when it was -- it was likely late in 1994 or some
time in 1995 -- when I first came across the concept of, or rather the name
for the concept of, *"eating your own dog food"*. The idea and the name
played a huge part in the book [*Show-Stopper!* by G. Pascal
Zachary](https://www.gpascalzachary.com/showstopper__the_breakneck_race_to_create_windows_nt_and_the_next_generation_at_m_50101.htm).
The idea wasn't new to me of course; I'd been writing code for over a decade
by then and plenty of times I'd built things and then used those things to
do things, but it was fascinating to a mostly-self-taught 20-something me to
be reading this (excellent -- go read it if you care about the history of
your craft) book and to see the idea written down and named.

<!-- more -->

While [Textualize](https://www.textualize.io/) isn't (thankfully -- really,
I do recommend reading the book) anything like working on the team building
Windows NT, the idea of taking a little time out from working *on* Textual,
and instead work *with* Textual, makes a lot of sense. It's far too easy to
get focused on adding things and improving things and tweaking things while
losing sight of the fact that people will want to build **with** your
product.

So you can imagine how pleased I was when
[Will](https://mastodon.social/@willmcgugan) announced that he wanted [all
of us](https://www.textualize.io/about-us) to spend a couple or so weeks
building something with Textual. I had, of course, already written [one
small application with the
library](https://github.com/Textualize/textual/blob/main/examples/five_by_five.py),
and had plans for another (in part [it's how I ended up working
here](https://blog.davep.org/2022/10/05/on-to-something-new-redux.html)),
but I'd yet to really dive in and try and build something more involved.

Giving it some thought: I wasn't entirely sure what I wanted to build
though. I do want to use Textual to build a brand new terminal-based Norton
Guide reader ([not my first](https://github.com/davep/eg), not by [a long
way](https://github.com/davep/eg-OS2)) but I felt that was possibly a bit
too niche, and actually could take a bit too long anyway. Maybe not, it
remains to be seen.

Eventually I decided on this approach: try and do a quick prototype of some
daft idea each day or each couple of days, do that for a week or so, and
then finally try and settle down on something less trivial. This approach
should work well in that it'll help introduce me to more of Textual, help
try out a few different parts of the library, and also hopefully discover
some real pain-points with working with it and highlight a list of issues we
should address -- as seen from the perspective of a developer working with
the library.

So, here I am, at the end of week one. What I want to try and do is briefly
(yes yes, I know, this introduction is the antithesis of brief) talk about
what I built and perhaps try and highlight some lessons learnt, highlight
some patterns I think are useful, and generally do an end-of-week version of
a [TIL](https://simonwillison.net/2022/Nov/6/what-to-blog-about/). TWIL?

Yeah. I guess this is a TWIL.

## gridinfo

I started the week by digging out a quick hack I'd done a couple of weeks
earlier, with a view to cleaning it up. It started out as a fun attempt to
do something with [Rich Pixels](https://github.com/darrenburns/rich-pixels)
while also making a terminal-based take on
[`slstats.el`](https://github.com/davep/slstats.el). I'm actually pleased
with the result and how quickly it came together.

The point of the application itself is to show some general information
about the current state of the Second Life grid (hello to any fellow
residents of [the original
Metaverse](https://wiki.secondlife.com/wiki/History_of_Second_Life)!), and
to also provide a simple region lookup screen that, using Rich Pixels, will
display the object map (albeit in pretty low resolution -- but that's the
fun of this!).

So the opening screen looks like this:

![The initial screen of gridinfo, showing the main SL stats](../images/2022-11-26-davep-devlog/gridinfo-1.png)

and a lookup of a region looks like this:

![Looking up the details of the first even region](../images/2022-11-26-davep-devlog/gridinfo-2.png)

Here's a wee video of the whole thing in action:

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/dzpGgVPD2aM"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

### Worth a highlight

Here's a couple of things from the code that I think are worth a highlight,
as things to consider when building Textual apps:

#### Don't use the default screen

Use of the default `Screen` that's provided by the `App` is handy enough,
but I feel any non-trivial application should really put as much code as
possible in screens that relate to key "work". Here's the entirety of my
application code:

```python
class GridInfo( App[ None ] ):
    """TUI app for showing information about the Second Life grid."""

    CSS_PATH = "gridinfo.css"
    """The name of the CSS file for the app."""

    TITLE = "Grid Information"
    """str: The title of the application."""

    SCREENS = {
        "main": Main,
        "region": RegionInfo
    }
    """The collection of application screens."""

    def on_mount( self ) -> None:
        """Set up the application on startup."""
        self.push_screen( "main" )
```

You'll notice there's no work done in the app, other than to declare the
screens, and to set the `main` screen running when the app is mounted.

#### Don't work hard `on_mount`

My initial version of the application had it loading up the data from the
Second Life and GridSurvey APIs in `Main.on_mount`. This obviously wasn't a
great idea as it made the startup appear slow. That's when I realised just
how handy
[`call_after_refresh`](https://textual.textualize.io/api/message_pump/#textual.message_pump.MessagePump.call_after_refresh)
is. This meant I could show some placeholder information and then fire off
the requests (3 of them: one to get the main grid information, one to get
the grid concurrency data, and one to get the grid size data), keeping the
application looking active and updating the display when the replies came
in.

### Pain points

While building this app I think there was only really the one pain-point,
and I suspect it's mostly more on me than on Textual itself: getting a good
layout and playing whack-a-mole with CSS. I suspect this is going to be down
to getting more and more familiar with CSS and the terminal (which is
different from laying things out for the web), while also practising with
various layout schemes -- which is where the [revamped `Placeholder`
class](https://textual.textualize.io/blog/2022/11/22/what-i-learned-from-my-first-non-trivial-pr/#what-i-learned-from-my-first-non-trivial-pr)
is going to be really useful.

## unbored

The next application was initially going to be a very quick hack, but
actually turned into a less-trivial build than I'd initially envisaged; not
in a negative way though. The more I played with it the more I explored and
I feel that this ended up being my first really good exploration of some
useful (personal -- your kilometerage may vary) patterns and approaches when
working with Textual.

The application itself is a terminal client for [the
Bored-API](https://www.boredapi.com/). I had initially intended to roll my
own code for working with the API, but I noticed that [someone had done a
nice library for it](https://pypi.org/project/bored-api/) and it seemed
silly to not build on that. Not needing to faff with that, I could
concentrate on the application itself.

At first I was just going to let the user click away at a button that showed
a random activity, but this quickly morphed into a *"why don't I make this
into a sort of TODO list builder app, where you can add things to do when
you are bored, and delete things you don't care for or have done"* approach.

Here's a view of the main screen:

![The main Unbored screen](../images/2022-11-26-davep-devlog/unbored-1.png)

and here's a view of the filter pop-over:

![Setting filters for activities](../images/2022-11-26-davep-devlog/unbored-2.png)

### Worth a highlight

#### Don't put all your `BINDINGS` in one place

This came about from me overloading the use of the `escape` key. I wanted it
to work more or less like this:

- If you're inside an activity, move focus up to the activity type selection
  buttons.
- If the filter pop-over is visible, close that.
- Otherwise exit the application.

It was easy enough to do, and I had an action in the `Main` screen that
`escape` was bound to (again, in the `Main` screen) that did all this logic
with some `if`/`elif` work but it didn't feel elegant. Moreover, it meant
that the `Footer` always displayed the same description for the key.

That's when I realised that it made way more sense to have a `Binding` for
`escape` in every widget that was the actual context for escape's use. So I
went from one top-level binding to...

```python
...

class Activity( Widget ):
    """A widget that holds and displays a suggested activity."""

    BINDINGS = [
        ...
        Binding( "escape", "deselect", "Switch to Types" )
    ]

...

class Filters( Vertical ):
    """Filtering sidebar."""

    BINDINGS = [
        Binding( "escape", "close", "Close Filters" )
    ]

...

class Main( Screen ):
    """The main application screen."""

    BINDINGS = [
        Binding( "escape", "quit", "Close" )
    ]
    """The bindings for the main screen."""
```

This was so much cleaner **and** I got better `Footer` descriptions too. I'm
going to be leaning hard on this approach from now on.

#### Messages are awesome

Until I wrote this application I hadn't really had a need to define or use
my own `Message`s. During work on this I realised how handy they really are.
In the code I have an `Activity` widget which takes care of the job of
moving itself amongst its siblings if the user asks to move an activity up
or down. When this happens I also want the `Main` screen to save the
activities to the filesystem as things have changed.

Thing is: I don't want the screen to know what an `Activity` is capable of
and I don't want an `Activity` to know what the screen is capable of;
especially the latter as I really don't want a child of a screen to know
what the screen can do (in this case *"save stuff"*).

This is where messages come in. Using a message I could just set things up
so that the `Activity` could shout out **"HEY I JUST DID A THING THAT CHANGES
ME"** and not care who is listening and not care what they do with that
information.

So, thanks to this bit of code in my `Activity` widget...

```python
    class Moved( Message ):
        """A message to indicate that an activity has moved."""

    def action_move_up( self ) -> None:
        """Move this activity up one place in the list."""
        if self.parent is not None and not self.is_first:
            parent = cast( Widget, self.parent )
            parent.move_child(
                self, before=parent.children.index( self ) - 1
            )
            self.emit_no_wait( self.Moved( self ) )
            self.scroll_visible( top=True )
```

...the `Main` screen can do this:

```python
    def on_activity_moved( self, _: Activity.Moved ) -> None:
        """React to an activity being moved."""
        self.save_activity_list()
```

!!! warning

    The code above used `emit_no_wait`. Since this blog post was first
    published that method has been removed from Textual. You should use
    [`post_message_no_wait` or `post_message`](/guide/events/#sending-messages) instead now.

### Pain points

On top of the issues of getting to know terminal-based-CSS that I mentioned
earlier:

- Textual currently lacks any sort of selection list or radio-set widget.
  This meant that I couldn't quite do the activity type picking how I would
  have wanted. Of course I could have rolled my own widgets for this, but I
  think I'd sooner wait until such things [are in Textual
  itself](https://textual.textualize.io/roadmap/#widgets).
- Similar to that, I could have used some validating `Input` widgets. They
  too are on the roadmap but I managed to cobble together fairly good
  working versions for my purposes. In doing so though I did further
  highlight that the [reactive attribute
  facility](https://textual.textualize.io/tutorial/#reactive-attributes)
  needs a wee bit more attention as I ran into some
  ([already-known](https://github.com/Textualize/textual/issues/1216)) bugs.
  Thankfully in my case [it was a very easy
  workaround](https://github.com/davep/unbored/blob/d46f7959aeda0996f39d287388c6edd2077be935/unbored#L251-L255).
- Scrolling in general seems a wee bit off when it comes to widgets that are
  more than one line tall. While there's nothing really obvious I can point
  my finger at, I'm finding that scrolling containers sometimes get confused
  about what should be in view. This becomes very obvious when forcing
  things to scroll from code. I feel this deserves a dedicated test
  application to explore this more.

## Conclusion

The first week of *"dogfooding"* has been fun and I'm more convinced than
ever that it's an excellent exercise for Textualize to engage in. I didn't
quite manage my plan of *"one silly trivial prototype per day"*, which means
I've ended up with two (well technically one and a half I guess given that
`gridinfo` already existed as a prototype) applications rather than four.
I'm okay with that. I got a **lot** of utility out of this.

Now to look at the list of ideas I have going and think about what I'll kick
next week off with...
````

## File: docs/blog/posts/placeholder-pr.md
````markdown
---
draft: false
date: 2022-11-22
categories:
  - DevLog
authors:
  - rodrigo
---


# What I learned from my first non-trivial PR

<div>
--8<-- "docs/blog/images/placeholder-example.svg"
</div>

It's 8:59 am and, by my Portuguese standards, it is freezing cold outside: 5 or 6 degrees Celsius.
It is my second day at Textualize and I just got into the office.
I undress my many layers of clothing to protect me from the Scottish cold and I sit down in my improvised corner of the Textualize office.
As I sit down, I turn myself in my chair to face my boss and colleagues to ask “So, what should I do today?”.
I was not expecting Will's answer, but the challenge excited me:

<!-- more -->

 > “I thought I'll just throw you in the deep end and have you write some code.”

What happened next was that I spent two days [working on PR #1229](https://github.com/Textualize/textual/pull/1229) to add a new widget to the [Textual](https://github.com/Textualize/textual) code base.
At the time of writing, the pull request has not been merged yet.
Well, to be honest with you, it hasn't even been reviewed by anyone...
But that won't stop me from blogging about some of the things I learned while creating this PR.


## The placeholder widget

This PR adds a widget called `Placeholder` to Textual.
As per the documentation, this widget “is meant to have no complex functionality.
Use the placeholder widget when studying the layout of your app before having to develop your custom widgets.”

The point of the placeholder widget is that you can focus on building the layout of your app without having to have all of your (custom) widgets ready.
The placeholder widget also displays a couple of useful pieces of information to help you work out the layout of your app, namely the ID of the widget itself (or a custom label, if you provide one) and the width and height of the widget.

As an example of usage of the placeholder widget, you can refer to the screenshot at the top of this blog post, which I included below so you don't have to scroll up:

<div>
--8<-- "docs/blog/images/placeholder-example.svg"
</div>

The top left and top right widgets have custom labels.
Immediately under the top right placeholder, you can see some placeholders identified as `#p3`, `#p4`, and `#p5`.
Those are the IDs of the respective placeholders.
Then, rows 2 and 3 contain some placeholders that show their respective size and some placeholders that just contain some text.


## Bootstrapping the code for the widget

So, how does a code monkey start working on a non-trivial PR within 24 hours of joining a company?
The answer is simple: just copy and paste code!
But instead of copying and pasting from Stack Overflow, I decided to copy and paste from the internal code base.

My task was to create a new widget, so I thought it would be a good idea to take a look at the implementation of other Textual widgets.
For some reason I cannot seem to recall, I decided to take a look at the implementation of the button widget that you can find in [_button.py](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_button.py).
By looking at how the button widget is implemented, I could immediately learn a few useful things about what I needed to do and some other things about how Textual works.

For example, a widget can have a class attribute called `DEFAULT_CSS` that specifies the default CSS for that widget.
I learned this just from staring at the code for the button widget.

Studying the code base will also reveal the standards that are in place.
For example, I learned that for a widget with variants (like the button with its “success” and “error” variants), the widget gets a CSS class with the name of the variant prefixed by a dash.
You can learn this by looking at the method `Button.watch_variant`:

```py
class Button(Static, can_focus=True):
    # ...

    def watch_variant(self, old_variant: str, variant: str):
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")
```

In short, looking at code and files that are related to the things you need to do is a great way to get information about things you didn't even know you needed.


## Handling the placeholder variant

A button widget can have a different variant, which is mostly used by Textual to determine the CSS that should apply to the given button.
For the placeholder widget, we want the variant to determine what information the placeholder shows.
The [original GitHub issue](https://github.com/Textualize/textual/issues/1200) mentions 5 variants for the placeholder:

 - a variant that just shows a label or the placeholder ID;
 - a variant that shows the size and location of the placeholder;
 - a variant that shows the state of the placeholder (does it have focus? is the mouse over it?);
 - a variant that shows the CSS that is applied to the placeholder itself; and
 - a variant that shows some text inside the placeholder.

The variant can be assigned when the placeholder is first instantiated, for example, `Placeholder("css")` would create a placeholder that shows its own CSS.
However, we also want to have an `on_click` handler that cycles through all the possible variants.
I was getting ready to reinvent the wheel when I remembered that the standard module [`itertools`](https://docs.python.org/3/library/itertools) has a lovely tool that does exactly what I needed!
Thus, all I needed to do was create a new `cycle` through the variants each time a placeholder is created and then grab the next variant whenever the placeholder is clicked:

```py
class Placeholder(Static):
    def __init__(
        self,
        variant: PlaceholderVariant = "default",
        *,
        label: str | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        # ...

        self.variant = self.validate_variant(variant)
        # Set a cycle through the variants with the correct starting point.
        self._variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self._variants_cycle) != self.variant:
            pass

    def on_click(self) -> None:
        """Click handler to cycle through the placeholder variants."""
        self.cycle_variant()

    def cycle_variant(self) -> None:
        """Get the next variant in the cycle."""
        self.variant = next(self._variants_cycle)
```

I am just happy that I had the insight to add this little `while` loop when a placeholder is instantiated:

```py
from itertools import cycle
# ...
class Placeholder(Static):
    # ...
    def __init__(...):
        # ...
        self._variants_cycle = cycle(_VALID_PLACEHOLDER_VARIANTS_ORDERED)
        while next(self._variants_cycle) != self.variant:
            pass
```

Can you see what would be wrong if this loop wasn't there?


## Updating the render of the placeholder on variant change

If the variant of the placeholder is supposed to determine what information the placeholder shows, then that information must be updated every time the variant of the placeholder changes.
Thankfully, Textual has reactive attributes and watcher methods, so all I needed to do was...
Defer the problem to another method:

```py
class Placeholder(Static):
    # ...
    variant = reactive("default")
    # ...
    def watch_variant(
        self, old_variant: PlaceholderVariant, variant: PlaceholderVariant
    ) -> None:
        self.validate_variant(variant)
        self.remove_class(f"-{old_variant}")
        self.add_class(f"-{variant}")
        self.call_variant_update()  # <-- let this method do the heavy lifting!
```

Doing this properly required some thinking.
Not that the current proposed solution is the best possible, but I did think of worse alternatives while I was thinking how to tackle this.
I wasn't entirely sure how I would manage the variant-dependant rendering because I am not a fan of huge conditional statements that look like switch statements:

```py
if variant == "default":
    # render the default placeholder
elif variant == "size":
    # render the placeholder with its size
elif variant == "state":
    # render the state of the placeholder
elif variant == "css":
    # render the placeholder with its CSS rules
elif variant == "text":
    # render the placeholder with some text inside
```

However, I am a fan of using the built-in `getattr` and I thought of creating a rendering method for each different variant.
Then, all I needed to do was make sure the variant is part of the name of the method so that I can programmatically determine the name of the method that I need to call.
This means that the method `Placeholder.call_variant_update` is just this:

```py
class Placeholder(Static):
    # ...
    def call_variant_update(self) -> None:
        """Calls the appropriate method to update the render of the placeholder."""
        update_variant_method = getattr(self, f"_update_{self.variant}_variant")
        update_variant_method()
```

If `self.variant` is, say, `"size"`, then `update_variant_method` refers to `_update_size_variant`:

```py
class Placeholder(Static):
    # ...
    def _update_size_variant(self) -> None:
        """Update the placeholder with the size of the placeholder."""
        width, height = self.size
        self._placeholder_label.update(f"[b]{width} x {height}[/b]")
```

This variant `"size"` also interacts with resizing events, so we have to watch out for those:

```py
class Placeholder(Static):
    # ...
    def on_resize(self, event: events.Resize) -> None:
        """Update the placeholder "size" variant with the new placeholder size."""
        if self.variant == "size":
            self._update_size_variant()
```


## Deleting code is a (hurtful) blessing

To conclude this blog post, let me muse about the fact that the original issue mentioned five placeholder variants and that my PR only includes two and a half.

After careful consideration and after coming up with the `getattr` mechanism to update the display of the placeholder according to the active variant, I started showing the “final” product to Will and my other colleagues.
Eventually, we ended up getting rid of the variant for CSS and the variant that shows the placeholder state.
This means that I had to **delete part of my code** even before it saw the light of day.

On the one hand, deleting those chunks of code made me a bit sad.
After all, I had spent quite some time thinking about how to best implement that functionality!
But then, it was time to write documentation and tests, and I verified that the **best code** is the code that you don't even write!
The code you don't write is guaranteed to have zero bugs and it also does not need any documentation whatsoever!

So, it was a shame that some lines of code I poured my heart and keyboard into did not get merged into the Textual code base.
On the other hand, I am quite grateful that I won't have to fix the bugs that will certainly reveal themselves in a couple of weeks or months from now.
Heck, the code hasn't been merged yet and just by writing this blog post I noticed a couple of tweaks that were missing!
````

## File: docs/blog/posts/puppies-and-cake.md
````markdown
---
draft: false
date: 2023-07-29
categories:
  - DevLog
authors:
  - willmcgugan
title: "Pull Requests are cake or puppies"
---

# Pull Requests are cake or puppies

Broadly speaking, there are two types of contributions you can make to an Open Source project.

<!-- more -->

The first type is typically a bug fix, but could also be a documentation update, linting fix, or other change which doesn't impact core functionality.
Such a contribution is like *cake*.
It's a simple, delicious, gift to the project.

The second type of contribution often comes in the form of a new feature.
This contribution likely represents a greater investment of time and effort than a bug fix.
It is still a gift to the project, but this contribution is *not* cake.

A feature PR has far more in common with a puppy.
The maintainer(s) may really like the feature but hesitate to merge all the same.
They may even reject the contribution entirely.
This is because a feature PR requires an ongoing burden to maintain.
In the same way that a puppy needs food and walkies, a new feature will require updates and fixes long after the original contribution.
Even if it is an amazing feature, the maintainer may not want to commit to that ongoing work.

![Puppy cake](../images/puppy.jpg)

The chances of a feature being merged can depend on the maturity of the project.
At the beginning of a project, a maintainer may be delighted with a new feature contribution.
After all, having others join you to build something is the joy of Open Source.
And yet when a project gets more mature there may be a growing resistance to adding new features, and a greater risk that a feature PR is rejected or sits unappreciated in the PR queue.

So how should a contributor avoid this?
If there is any doubt, it's best to propose the feature to the maintainers before undertaking the work.
In all likelihood they will be happy for your contribution, just be prepared for them to say "thanks but no thanks".
Don't take it as a rejection of your gift: it's just that the maintainer can't commit to taking on a puppy.

There are other ways to contribute code to a project that don't require the code to be merged in to the core.
You could publish your change as a third party library.
Take it from me: maintainers love it when their project spawns an ecosystem.
You could also blog about how you solved your problem without an update to the core project.
Having a resource that can be googled for, or a maintainer can direct people to, can be a huge help.

What prompted me to think about this is that my two main projects, [Rich](https://github.com/Textualize/rich) and [Textual](https://github.com/Textualize/textual), are at quite different stages in their lifetime. Rich is relatively mature, and I'm unlikely to accept a puppy. If you can achieve what you need without adding to the core library, I am *probably* going to decline a new feature. Textual is younger and still accepting puppies &mdash; in addition to stick insects, gerbils, capybaras and giraffes.

!!! tip

    If you are maintainer, and you do have to close a feature PR, feel free to link to this post.

---

Join us on the [Discord Server](https://discord.gg/Enf6Z3qhVr) if you want to discuss puppies and other creatures.
````

## File: docs/blog/posts/release0-11-0.md
````markdown
---
draft: false
date: 2023-02-15
categories:
  - Release
title: "Textual 0.11.0 adds a beautiful Markdown widget"
authors:
  - willmcgugan
---

# Textual 0.11.0 adds a beautiful Markdown widget

We released Textual 0.10.0 25 days ago, which is a little longer than our usual release cycle. What have we been up to?

<!-- more -->

The headline feature of this release is the enhanced Markdown support. Here's a screenshot of an example:

<div>
--8<-- "docs/blog/images/markdown-viewer.svg"
</div>

!!! tip

    You can generate these SVG screenshots for your app with `textual run my_app.py --screenshot 5` which will export a screenshot after 5 seconds.

There are actually 2 new widgets: [Markdown](./../../widgets/markdown.md) for a simple Markdown document, and [MarkdownViewer](./../../widgets/markdown_viewer.md) which adds browser-like navigation and a table of contents.

Textual has had support for Markdown since day one by embedding a Rich [Markdown](https://rich.readthedocs.io/en/latest/markdown.html) object -- which still gives decent results! This new widget adds dynamic controls such as scrollable code fences and tables, in addition to working links.

In future releases we plan on adding more Markdown extensions, and the ability to easily embed custom widgets within the document. I'm sure there are plenty of interesting applications that could be powered by dynamically generated Markdown documents.

## DataTable improvements

There has been a lot of work on the [DataTable](../../widgets/data_table.md) API. We've added the ability to sort the data, which required that we introduce the concept of row and column keys. You can now reference rows / columns / cells by their coordinate or by row / column key.

Additionally there are new [update_cell][textual.widgets.DataTable.update_cell] and [update_cell_at][textual.widgets.DataTable.update_cell_at] methods to update cells after the data has been populated. Future releases will have more methods to manipulate table data, which will make it a very general purpose (and powerful) widget.

## Tree control

The [Tree](../../widgets/tree.md) widget has grown a few methods to programmatically expand, collapse and toggle tree nodes.

## Breaking changes

There are a few breaking changes in this release. These are mostly naming and import related, which should be easy to fix if you are affected. Here's a few notable examples:

- `Checkbox` has been renamed to `Switch`. This is because we plan to introduce complimentary `Checkbox` and `RadioButton` widgets in a future release, but we loved the look of *Switches* too much to drop them.
- We've dropped the `emit` and `emit_no_wait` methods. These methods posted message to the parent widget, but we found that made it problematic to subclass widgets. In almost all situations you want to replace these with `self.post_message` (or `self.post_message_no_wait`).

Be sure to check the [CHANGELOG](https://github.com/Textualize/textual/blob/main/CHANGELOG.md) for the full details on potential breaking changes.

## Join us!

We're having fun on our [Discord server](https://discord.gg/Enf6Z3qhVr). Join us there to talk to Textualize developers and share ideas.
````

## File: docs/blog/posts/release0-12-0.md
````markdown
---
draft: false
date: 2023-02-24
categories:
  - Release
title: "Textual 0.12.0 adds syntactical sugar and batch updates"
authors:
  - willmcgugan
---

# Textual 0.12.0 adds syntactical sugar and batch updates

It's been just 9 days since the previous release, but we have a few interesting enhancements to the Textual API to talk about.

<!-- more -->

## Better compose

We've added a little *syntactical sugar* to Textual's `compose` methods, which aids both
readability and *editability* (that might not be a word).

First, let's look at the old way of building compose methods. This snippet is taken from the `textual colors` command.


```python
for color_name in ColorSystem.COLOR_NAMES:

    items: list[Widget] = [ColorLabel(f'"{color_name}"')]
    for level in LEVELS:
        color = f"{color_name}-{level}" if level else color_name
        item = ColorItem(
            ColorBar(f"${color}", classes="text label"),
            ColorBar("$text-muted", classes="muted"),
            ColorBar("$text-disabled", classes="disabled"),
            classes=color,
        )
        items.append(item)

    yield ColorGroup(*items, id=f"group-{color_name}")
```

This code *composes* the following color swatches:

<div>
--8<-- "docs/blog/images/colors.svg"
</div>

!!! tip

    You can see this by running `textual colors` from the command line.


The old way was not all that bad, but it did make it hard to see the structure of your app at-a-glance, and editing compose methods always felt a little laborious.

Here's the new syntax, which uses context managers to add children to containers:

```python
for color_name in ColorSystem.COLOR_NAMES:
    with ColorGroup(id=f"group-{color_name}"):
        yield Label(f'"{color_name}"')
        for level in LEVELS:
            color = f"{color_name}-{level}" if level else color_name
            with ColorItem(classes=color):
                yield ColorBar(f"${color}", classes="text label")
                yield ColorBar("$text-muted", classes="muted")
                yield ColorBar("$text-disabled", classes="disabled")
```

The context manager approach generally results in fewer lines of code, and presents attributes on the same line as containers themselves. Additionally, adding widgets to a container can be as simple is indenting them.

You can still construct widgets and containers with positional arguments, but this new syntax is preferred. It's not documented yet, but you can start using it now. We will be updating our examples in the next few weeks.

## Batch updates

Textual is smart about performing updates to the screen. When you make a change that might *repaint* the screen, those changes don't happen immediately. Textual makes a note of them, and repaints the screen a short time later (around a 1/60th of a second). Multiple updates are combined so that Textual does less work overall, and there is none of the flicker you might get with multiple repaints.

Although this works very well, it is possible to introduce a little flicker if you make changes across multiple widgets. And especially if you add or remove many widgets at once. To combat this we have added a [batch_update][textual.app.App.batch_update] context manager which tells Textual to disable screen updates until the end of the with block.

The new [Markdown](./release0-11-0.md) widget uses this context manager when it updates its content. Here's the code:

```python
with self.app.batch_update():
    await self.query("MarkdownBlock").remove()
    await self.mount_all(output)
```

Without the batch update there are a few frames where the old markdown blocks are removed and the new blocks are added (which would be perceived as a brief flicker). With the update, the update appears instant.

## Disabled widgets

A few widgets (such as [Button](./../../widgets/button.md)) had a `disabled` attribute which would fade the widget a little and make it unselectable. We've extended this to all widgets. Although it is particularly applicable to input controls, anything may be disabled. Disabling a container makes its children disabled, so you could use this for disabling a form, for example.

!!! tip

    Disabled widgets may be styled with the `:disabled` CSS pseudo-selector.

## Preventing messages

Also in this release is another context manager, which will disable specified Message types. This doesn't come up as a requirement very often, but it can be very useful when it does. This one is documented, see [Preventing events](./../../guide/events.md#preventing-messages) for details.

## Full changelog

As always see the [release page](https://github.com/Textualize/textual/releases/tag/v0.12.0) for additional changes and bug fixes.

## Join us!

We're having fun on our [Discord server](https://discord.gg/Enf6Z3qhVr). Join us there to talk to Textualize developers and share ideas.
````

## File: docs/blog/posts/release0-14-0.md
````markdown
---
draft: false
date: 2023-03-09
categories:
  - Release
title: "Textual 0.14.0 shakes up posting messages"
authors:
  - willmcgugan
---

# Textual 0.14.0 shakes up posting messages

Textual version 0.14.0 has landed just a week after 0.13.0.

!!! note

    We like fast releases for Textual. Fast releases means quicker feedback, which means better code.

What's new?

<!-- more -->

We did a little shake-up of posting [messages](../../guide/events.md) which will simplify building widgets. But this does mean a few breaking changes.

There are two methods in Textual to post messages: `post_message` and `post_message_no_wait`. The former was asynchronous (you needed to `await` it), and the latter was a regular method call. These two methods have been replaced with a single `post_message` method.

To upgrade your project to Textual 0.14.0, you will need to do the following:

- Remove `await` keywords from any calls to `post_message`.
- Replace any calls to `post_message_no_wait` with `post_message`.


Additionally, we've simplified constructing messages classes. Previously all messages required a `sender` argument, which had to be manually set. This was a clear violation of our "no boilerplate" policy, and has been dropped. There is still a `sender` property on messages / events, but it is set automatically.

So prior to 0.14.0 you might have posted messages like the following:

```python
await self.post_message(self.Changed(self, item=self.item))
```

You can now replace it with this simpler function call:

```python
self.post_message(self.Change(item=self.item))
```

This also means that you will need to drop the sender from any custom messages you have created.

If this was code pre-0.14.0:

```python
class MyWidget(Widget):

    class Changed(Message):
        """My widget change event."""
        def __init__(self, sender:MessageTarget, item_index:int) -> None:
            self.item_index = item_index
            super().__init__(sender)

```

You would need to make the following change (dropping `sender`).

```python
class MyWidget(Widget):

    class Changed(Message):
        """My widget change event."""
        def __init__(self, item_index:int) -> None:
            self.item_index = item_index
            super().__init__()

```

If you have any problems upgrading, join our [Discord server](https://discord.gg/Enf6Z3qhVr), we would be happy to help.

See the [release notes](https://github.com/Textualize/textual/releases/tag/v0.14.0) for the full details on this update.
````

## File: docs/blog/posts/release0-15-0.md
````markdown
---
draft: false
date: 2023-03-13
categories:
  - Release
title: "Textual 0.15.0 adds a tabs widget"
authors:
  - willmcgugan
---

# Textual 0.15.0 adds a tabs widget

We've just pushed Textual 0.15.0, only 4 days after the previous version. That's a little faster than our typical release cadence of 1 to 2 weeks.

What's new in this release?

<!-- more -->

The highlight of this release is a new [Tabs](./widgets/../../../widgets/tabs.md) widget to display tabs which can be navigated much like tabs in a browser. Here's a screenshot:

<div>
--8<-- "docs/blog/images/tabs_widget.svg"
</div>

In a future release, this will be combined with the [ContentSwitcher](../../widgets/content_switcher.md) widget to create a traditional tabbed dialog. Although Tabs is still useful as a standalone widgets.

!!! tip

    I like to tweet progress with widgets on Twitter. See the [#textualtabs](https://twitter.com/search?q=%23textualtabs&src=typeahead_click) hashtag which documents progress on this widget.

Also in this release is a new [LoadingIndicator](./../../widgets/loading_indicator.md) widget to display a simple animation while waiting for data. Here's a screenshot:

<div>
--8<-- "docs/blog/images/loading_indicator.svg"
</div>

As always, see the [release notes](https://github.com/Textualize/textual/releases/tag/v0.15.0) for the full details on this update.

If you want to talk about these widgets, or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/posts/release0-16-0.md
````markdown
---
draft: false
date: 2023-03-22
categories:
  - Release
title: "Textual 0.16.0 adds TabbedContent and border titles"
authors:
  - willmcgugan
---

# Textual 0.16.0 adds TabbedContent and border titles

Textual 0.16.0 lands 9 days after the previous release. We have some new features to show you.

<!-- more -->

There are two highlights in this release. In no particular order, the first is [TabbedContent](../../widgets/tabbed_content.md) which uses a row of *tabs* to navigate content. You will have likely encountered this UI in the desktop and web. I think in Windows they are known as "Tabbed Dialogs".

This widget combines existing [Tabs](../../widgets/tabs.md) and [ContentSwitcher](../../api/content_switcher.md) widgets and adds an expressive interface for composing. Here's a trivial example to use content tabs to navigate a set of three markdown documents:

```python
def compose(self) -> ComposeResult:
    with TabbedContent("Leto", "Jessica", "Paul"):
        yield Markdown(LETO)
        yield Markdown(JESSICA)
        yield Markdown(PAUL)
```

Here's an example of the UI you can create with this widget (note the nesting)!

```{.textual path="docs/examples/widgets/tabbed_content.py" press="j"}
```


## Border titles

The second highlight is a frequently requested feature (FRF?). Widgets now have the two new string properties, `border_title` and `border_subtitle`, which will be displayed within the widget's border.

You can set the alignment of these titles via [`border-title-align`](../../styles/border_title_align.md) and [`border-subtitle-align`](../../styles/border_subtitle_align.md). Titles may contain [Console Markup](https://rich.readthedocs.io/en/latest/markup.html), so you can add additional color and style to the labels.

Here's an example of a widget with a title:

<div>
--8<-- "docs/blog/images/border-title.svg"
</div>

BTW the above is a command you can run to see the various border styles you can apply to widgets.

```
textual borders
```

## Container changes

!!! warning "Breaking change"

    If you have an app that uses any container classes, you should read this section.

We've made a change to containers in this release. Previously all containers had *auto* scrollbars, which means that any container would scroll if its children didn't fit. With nested layouts, it could be tricky to understand exactly which containers were scrolling. In 0.16.0 we split containers in to scrolling and non-scrolling versions. So `Horizontal` will now *not* scroll by default, but `HorizontalScroll` will have automatic scrollbars.


## What else?

As always, see the [release notes](https://github.com/Textualize/textual/releases/tag/v0.16.0) for the full details on this update.

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/posts/release0-17-0.md
````markdown
---
draft: false
date: 2023-03-29
categories:
  - Release
title: "Textual 0.17.0 adds translucent screens and Option List"
authors:
  - willmcgugan
---

# Textual 0.17.0 adds translucent screens and Option List

This is a surprisingly large release, given it has been just 7 days since the last version (and we were down a developer for most of that time).

What's new in this release?

<!-- more -->

There are two new notable features I want to cover. The first is a compositor effect.

## Translucent screens

Textual has a concept of "screens" which you can think of as independent UI modes, each with their own user interface and logic.
The App class keeps a stack of these screens so you can switch to a new screen and later return to the previous screen.

!!! tip inline end "Screens"

    See the [guide](../../guide/screens.md) to learn more about the screens API.

    <a href="/guide/screens">
    <div class="excalidraw">
    --8<-- "docs/images/screens/pop_screen.excalidraw.svg"
    </div>
    </a>

Screens can be used to build modal dialogs by *pushing* a screen with controls / buttons, and *popping* the screen when the user has finished with it.
The problem with this approach is that there was nothing to indicate to the user that the original screen was still there, and could be returned to.

In this release we have added alpha support to the Screen's background color which allows the screen underneath to show through, typically blended with a little color.
Applying this to a screen makes it clear than the user can return to the previous screen when they have finished interacting with the modal.

Here's how you can enable this effect with CSS:

```sass hl_lines="3"
DialogScreen {
    align: center middle;
    background: $primary 30%;
}
```

Setting the background to `$primary` will make the background blue (with the default theme).
The addition of `30%` sets the alpha so that it will be blended with the background.
Here's the kind of effect this creates:

<div>
--8<-- "docs/blog/images/transparent_background.svg"
</div>

There are 4 screens in the above screenshot, one for the base screen and one for each of the three dialogs.
Note how each screen modifies the color of the screen below, but leaves everything visible.

See the [docs on screen opacity](../../guide/screens.md#screen-opacity) if you want to add this to your apps.

## Option list

Textual has had a [ListView](../../widgets/list_view.md) widget for a while, which is an excellent way of navigating a list of items (actually other widgets). In this release we've added an [OptionList](../../widgets/option_list.md) which is similar in appearance, but uses the [line api](../../guide/widgets.md#line-api) under the hood. The Line API makes it more efficient when you approach thousands of items.

```{.textual path="docs/examples/widgets/option_list_strings.py"}
```

The Options List accepts [Rich](https://github.com/Textualize/rich/) *renderable*, which means that anything Rich can render may be displayed in a list. Here's an Option List of tables:

```{.textual path="docs/examples/widgets/option_list_tables.py" columns="100" lines="32"}
```

We plan to build on the `OptionList` widget to implement drop-downs, menus, check lists, etc.
But it is still very useful as it is, and you can add it to apps now.

## What else?

There are a number of fixes regarding refreshing in this release. If you had issues with parts of the screen not updating, the new version should resolve it.

There's also a new logging handler, and a "thick" border type.

See [release notes](https://github.com/Textualize/textual/releases/tag/v0.17.0) for the full details.


## Next week

Next week we plan to take a break from building Textual to *building apps* with Textual.
We do this now and again to give us an opportunity to step back and understand things from the perspective of a developer using Textual.
We will hopefully have something interesting to show from the exercise, and new Open Source apps to share.

## Join us

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/posts/release0-18-0.md
````markdown
---
draft: false
date: 2023-04-04
categories:
  - Release
title: "Textual 0.18.0 adds API for managing concurrent workers"
authors:
  - willmcgugan
---

# Textual 0.18.0 adds API for managing concurrent workers

Less than a week since the last release, and we have a new API to show you.

<!-- more -->

This release adds a new [Worker API](../../guide/workers.md) designed to manage concurrency, both asyncio tasks and threads.

An API to manage concurrency may seem like a strange addition to a library for building user interfaces, but on reflection it makes a lot of sense.
People are building Textual apps to interface with REST APIs, websockets, and processes; and they are running into predictable issues.
These aren't specifically Textual problems, but rather general problems related to async tasks and threads.
It's not enough for us to point users at the asyncio docs, we needed a better answer.

The new `run_worker` method provides an easy way of launching "Workers" (a wrapper over async tasks and threads) which also manages their lifetime.

One of the challenges I've found with tasks and threads is ensuring that they are shut down in an orderly manner. Interestingly enough, Textual already implemented an orderly shutdown procedure to close the tasks that power widgets: children are shut down before parents, all the way up to the App (the root node).
The new API piggybacks on to that existing mechanism to ensure that worker tasks are also shut down in the same order.

!!! tip

    You won't need to worry about this [gnarly issue](https://textual.textualize.io/blog/2023/02/11/the-heisenbug-lurking-in-your-async-code/) with the new Worker API.


I'm particularly pleased with the new `@work` decorator which can turn a coroutine OR a regular function into a Textual Worker object, by scheduling it as either an asyncio task or a thread.
I suspect this will solve 90% of the concurrency issues we see with Textual apps.

See the [Worker API](../../guide/workers.md) for the details.

## Join us

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/posts/release0-23-0.md
````markdown
---
draft: false
date: 2023-05-03
categories:
  - Release
title: "Textual 0.23.0 improves message handling"
authors:
  - willmcgugan
---

# Textual 0.23.0 improves message handling

It's been a busy couple of weeks at Textualize.
We've been building apps with [Textual](https://github.com/Textualize/textual), as part of our *dog-fooding* week.
The first app, [Frogmouth](https://github.com/Textualize/frogmouth), was released at the weekend and already has 1K GitHub stars!
Expect two more such apps this month.

<!-- more -->

<div>
--8<-- "docs/blog/images/frogmouth.svg"
</div>

!!! tip

    Join our [mailing list](http://eepurl.com/hL0BF1) if you would like to be the first to hear about our apps.

We haven't stopped developing Textual in that time.
Today we released version 0.23.0 which has a really interesting API update I'd like to introduce.

Textual *widgets* can send messages to each other.
To respond to those messages, you implement a message handler with a naming convention.
For instance, the [Button](/widget_gallery/#button) widget sends a `Pressed` event.
To handle that event, you implement a method called `on_button_pressed`.

Simple enough, but handler methods are called to handle pressed events from *all* Buttons.
To manage multiple buttons you typically had to write a large `if` statement to wire up each button to the code it should run.
It didn't take many Buttons before the handler became hard to follow.

## On decorator

Version 0.23.0 introduces the [`@on`](/guide/events/#on-decorator) decorator which allows you to dispatch events based on the widget that initiated them.

This is probably best explained in code.
The following two listings respond to buttons being pressed.
The first uses a single message handler, the second uses the decorator approach:

=== "on_decorator01.py"

    ```python title="on_decorator01.py"
    --8<-- "docs/examples/events/on_decorator01.py"
    ```

    1. The message handler is called when any button is pressed

=== "on_decorator02.py"

    ```python title="on_decorator02.py"
    --8<-- "docs/examples/events/on_decorator02.py"
    ```

    1. Matches the button with an id of "bell" (note the `#` to match the id)
    2. Matches the button with class names "toggle" *and* "dark"
    3. Matches the button with an id of "quit"

=== "Output"

    ```{.textual path="docs/examples/events/on_decorator01.py"}
    ```

The decorator dispatches events based on a CSS selector.
This means that you could have a handler per button, or a handler for buttons with a shared class, or parent.

We think this is a very flexible mechanism that will help keep code readable and maintainable.

## Why didn't we do this earlier?

It's a reasonable question to ask: why didn't we implement this in an earlier version?
We were certainly aware there was a deficiency in the API.

The truth is simply that we didn't have an elegant solution in mind until recently.
The `@on` decorator is, I believe, an elegant and powerful mechanism for dispatching handlers.
It might seem obvious in hindsight, but it took many iterations and brainstorming in the office to come up with it!


## Join us

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/posts/release0-24-0.md
````markdown
---
draft: false
date: 2023-05-08
categories:
  - Release
title: "Textual 0.24.0 adds a Select control"
authors:
  - willmcgugan
---

# Textual 0.24.0 adds a Select control

Coming just 5 days after the last release, we have version 0.24.0 which we are crowning the King of Textual releases.
At least until it is deposed by version 0.25.0.

<!-- more -->

The highlight of this release is the new [Select](/widget_gallery/#select) widget: a very familiar control from the web and desktop worlds.
Here's a screenshot and code:

=== "Output (expanded)"

    ```{.textual path="docs/examples/widgets/select_widget.py" press="tab,enter,down,down"}
    ```

=== "select_widget.py"

    ```python
    --8<-- "docs/examples/widgets/select_widget.py"
    ```

=== "select.css"

    ```sass
    --8<-- "docs/examples/widgets/select.css"
    ```

## New styles

This one required new functionality in Textual itself.
The "pull-down" overlay with options presented a difficulty with the previous API.
The overlay needed to appear over any content below it.
This is possible (using [layers](https://textual.textualize.io/styles/layers/)), but there was no simple way of positioning it directly under the parent widget.

We solved this with a new "overlay" concept, which can considered a special layer for user interactions like this Select, but also pop-up menus, tooltips, etc.
Widgets styled to use the overlay appear in their natural place in the "document", but on top of everything else.

A second problem we tackled was ensuring that an overlay widget was never clipped.
This was also solved with a new rule called "constrain".
Applying `constrain` to a widget will keep the widget within the bounds of the screen.
In the case of `Select`, if you expand the options while at the bottom of the screen, then the overlay will be moved up so that you can see all the options.

These new rules are currently undocumented as they are still subject to change, but you can see them in the [Select](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_select.py#L179) source if you are interested.

In a future release these will be finalized and you can confidently use them in your own projects.

## Fixes for the @on decorator

The new `@on` decorator is proving popular.
To recap, it is a more declarative and finely grained way of dispatching messages.
Here's a snippet from the [calculator](https://github.com/Textualize/textual/blob/main/examples/calculator.py) example which uses `@on`:

```python
    @on(Button.Pressed, "#plus,#minus,#divide,#multiply")
    def pressed_op(self, event: Button.Pressed) -> None:
        """Pressed one of the arithmetic operations."""
        self.right = Decimal(self.value or "0")
        self._do_math()
        assert event.button.id is not None
        self.operator = event.button.id
```

The decorator arranges for the method to be called when any of the four math operation buttons are pressed.

In 0.24.0 we've fixed some missing attributes which prevented the decorator from working with some messages.
We've also extended the decorator to use keywords arguments, so it will match attributes other than `control`.

## Other fixes

There is a surprising number of fixes in this release for just 5 days. See [CHANGELOG.md](https://github.com/Textualize/textual/blob/main/CHANGELOG.md) for details.


## Join us

If you want to talk about this update or anything else Textual related, join us on our [Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/posts/release0-27-0.md
````markdown
---
draft: false
date: 2023-06-01
categories:
  - Release
title: "Textual adds Sparklines, Selection list, Input validation, and tool tips"
authors:
  - willmcgugan
---

# Textual adds Sparklines, Selection list, Input validation, and tool tips

It's been 12 days since the last Textual release, which is longer than our usual release cycle of a week.

We've been a little distracted with our "dogfood" projects: [Frogmouth](https://github.com/Textualize/frogmouth) and [Trogon](https://github.com/Textualize/trogon). Both of which hit 1000 Github stars in 24 hours. We will be maintaining / updating those, but it is business as usual for this Textual release (and it's a big one). We have such sights to show you.

<!-- more -->

## Sparkline widget

A [Sparkline](../../widget_gallery.md#sparkline) is essentially a mini-plot. Just detailed enough to keep an eye on time-series data.

<div>
--8<-- "docs/blog/images/sparkline.svg"
</div>

Colors are configurable, and all it takes is a call to [`set_interval`](https://textual.textualize.io/api/message_pump/#textual.message_pump.MessagePump.set_interval) to make it animate.

## Selection list

Next up is the [SelectionList](../../widget_gallery.md#selectionlist) widget. Essentially a scrolling list of checkboxes. Lots of use cases for this one.

<div>
--8<-- "docs/blog/images/selection-list.svg"
</div>

## Tooltips

We've added [tooltips](../../guide/widgets.md#tooltips) to Textual widgets.

The API couldn't be simpler: simply assign a string to the `tooltip` property on any widget.
This string will be displayed after 300ms when you hover over the widget.


<div>
--8<-- "docs/blog/images/tooltips.svg"
</div>

As always, you can configure how the tooltips will be displayed with CSS.

## Input updates

We have some quality of life improvements for the [Input](../../widget_gallery.md#input) widget.

You can now use a simple declarative API to [validating input](/widgets/input/#validating-input).

<div>
--8<-- "docs/blog/images/validation.svg"
</div>

Also in this release is a suggestion API, which will *suggest* auto completions as you type.
Hit <kbd>right</kbd> to accept the suggestion.

Here's a screenshot:

<div>
--8<-- "docs/blog/images/suggest.svg"
</div>

You could use this API to offer suggestions from a fixed list, or even pull the data from a network request.

## Join us

Development on Textual is *fast*.
We're very responsive to issues and feature requests.

If you have any suggestions, jump on our [Discord server](https://discord.gg/Enf6Z3qhVr) and you may see your feature in the next release!
````

## File: docs/blog/posts/release0-29-0.md
````markdown
---
draft: false
date: 2023-07-03
categories:
  - Release
title: "Textual 0.29.0 refactors dev tools"
authors:
  - willmcgugan
---

# Textual 0.29.0 refactors dev tools

It's been a slow week or two at Textualize, with Textual devs taking well-earned annual leave, but we still managed to get a new version out.

<!-- more -->

Version 0.29.0 has shipped with a number of fixes (see the [release notes](https://github.com/Textualize/textual/releases/tag/v0.29.0) for details), but I'd like to use this post to explain a change we made to how Textual developer tools are distributed.

Previously if you installed `textual[dev]` you would get the Textual dev tools plus the library itself. If you were distributing Textual apps and didn't need the developer tools you could drop the `[dev]`.

We did this because the less dependencies a package has, the fewer installation issues you can expect to get in the future. And Textual is surprisingly lean if you only need to *run* apps, and not build them.

Alas, this wasn't quite as elegant solution as we hoped. The dependencies defined in extras wouldn't install commands, so `textual` was bundled with the core library. This meant that if you installed the Textual package *without* the `[dev]` you would still get the `textual` command on your path but it wouldn't run.

We solved this by creating two packages: `textual` contains the core library (with minimal dependencies) and `textual-dev` contains the developer tools. If you are building Textual apps, you should install both as follows:

```
pip install textual textual-dev
```

That's the only difference. If you run in to any issues feel free to ask on the [Discord server](https://discord.gg/Enf6Z3qhVr)!
````

## File: docs/blog/posts/release0-30-0.md
````markdown
---
draft: false
date: 2023-07-17
categories:
  - Release
title: "Textual 0.30.0 adds desktop-style notifications"
authors:
  - willmcgugan
---

# Textual 0.30.0 adds desktop-style notifications

We have a new release of Textual to talk about, but before that I'd like to cover a little Textual news.

<!-- more -->

By sheer coincidence we reached [20,000 stars on GitHub](https://github.com/Textualize/textual) today.
Now stars don't mean all that much (at least until we can spend them on coffee), but its nice to know that twenty thousand developers thought Textual was interesting enough to hit the ★ button.
Thank you!

In other news: we moved office.
We are now a stone's throw away from Edinburgh Castle.
The office is around three times as big as the old place, which means we have room for wide standup desks and dual monitors.
But more importantly we have room for new employees.
Don't send your CVs just yet, but we hope to grow the team before the end of the year.

Exciting times.

## New Release

And now, for the main feature.
Version 0.30 adds a new notification system.
Similar to desktop notifications, it displays a small window with a title and message (called a *toast*) for a pre-defined number of seconds.

Notifications are great for short timely messages to add supplementary information for the user.
Here it is in action:

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/HIHRefjfcVc"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

The API is super simple.
To display a notification, call `notify()` with a message and an optional title.

```python
def on_mount(self) -> None:
    self.notify("Hello, from Textual!", title="Welcome")
```

## Textualize Video Channel

In case you missed it; Textualize now has a [YouTube](https://www.youtube.com/channel/UCo4nHAZv_cIlAiCSP2IyiOA) channel.
Our very own [Rodrigo](https://twitter.com/mathsppblog) has recorded a video tutorial series on how to build Textual apps.
Check it out!

<div class="video-wrapper">
    <iframe
        width="560" height="315"
        src="https://www.youtube.com/embed/kpOBRI56GXM"
        title="YouTube video player"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
</div>

We will be adding more videos in the near future, covering anything from beginner to advanced topics.

Don't worry if you prefer reading to watching videos.
We will be adding plenty more content to the [Textual docs](https://textual.textualize.io/) in the near future.
Watch this space.

As always, if you want to discuss anything with the Textual developers, join us on the [Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/posts/release0-38-0.md
````markdown
---
draft: false
date: 2023-09-21
categories:
  - Release
title: "Textual 0.38.0 adds a syntax aware TextArea"
authors:
  - willmcgugan
---

# Textual 0.38.0 adds a syntax aware TextArea

This is the second big feature release this month after last week's [command palette](./release0.37.0.md).

<!-- more -->

The [TextArea](../../widgets/text_area.md) has finally landed.
I know a lot of folk have been waiting for this one.
Textual's TextArea is a fully-featured widget for editing code, with syntax highlighting and line numbers.
It is highly configurable, and looks great.

Darren Burns (the author of this widget) has penned a terrific write-up on the TextArea.
See [Things I learned while building Textual's TextArea](./text-area-learnings.md) for some of the challenges he faced.


## Scoped CSS

Another notable feature added in 0.38.0 is *scoped* CSS.
A common gotcha in building Textual widgets is that you could write CSS that impacted styles outside of that widget.

Consider the following widget:

```python
class MyWidget(Widget):
    DEFAULT_CSS = """
    MyWidget {
        height: auto;
        border: magenta;
    }
    Label {
        border: solid green;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("foo")
        yield Label("bar")
```

The author has intended to style the labels in that widget by adding a green border.
This does work for the widget in question, but (prior to 0.38.0) the `Label` rule would style *all* Labels (including any outside of the widget) &mdash; which was probably not intended.

With version 0.38.0, the CSS is scoped so that only the widget's labels will be styled.
This is almost always what you want, which is why it is enabled by default.
If you do want to style something outside of the widget you can set `SCOPED_CSS=False` (as a classvar).


## Light and Dark pseudo selectors

We've also made a slight quality of life improvement to the CSS, by adding `:light` and `:dark` pseudo selectors.
This allows you to change styles depending on whether the app is currently using a light or dark theme.

This was possible before, just a little verbose.
Here's how you would do it in 0.37.0:

```css
App.-dark-mode MyWidget Label {
    ...
}
```

In 0.38.0 it's a little more concise and readable:

```css
MyWidget:dark Label {
    ...
}
```

## Testing guide

Not strictly part of the release, but we've added a [guide on testing](/guide/testing) Textual apps.

As you may know, we are on a mission to make TUIs a serious proposition for critical apps, which makes testing essential.
We've extracted and documented our internal testing tools, including our snapshot tests pytest plugin [pytest-textual-snapshot](https://pypi.org/project/pytest-textual-snapshot/).

This gives devs powerful tools to ensure the quality of their apps.
Let us know your thoughts on that!

## Release notes

See the [release](https://github.com/Textualize/textual/releases/tag/v0.38.0) page for the full details on this release.


## What's next?

There's lots of features planned over the next few months.
One feature I am particularly excited by is a widget to generate plots by wrapping the awesome [Plotext](https://pypi.org/project/plotext/) library.
Check out some early work on this feature:

<div class="video-wrapper">
<iframe width="1163" height="1005" src="https://www.youtube.com/embed/A3uKzWErC8o" title="Preview of Textual Plot widget" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

## Join us

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to discuss Textual with the Textualize devs, or the community.
````

## File: docs/blog/posts/release0-4-0.md
````markdown
---
draft: false 
date: 2022-11-08
categories:
  - Release
authors:
  - willmcgugan
---

# Version 0.4.0

We've released version 0.4.0 of [Textual](https://pypi.org/search/?q=textual).

As this is the first post tagged with `release` let me first explain where the blog fits in with releases. We plan on doing a post for every note-worthy release. Which likely means all but the most trivial updates (typos just aren't that interesting). Blog posts will be supplementary to release notes which you will find on the [Textual repository](https://github.com/Textualize/textual).

Blog posts will give a little more background for the highlights in a release, and a rationale for changes and new additions. We embrace *building in public*, which means that we would like you to be as up-to-date with new developments as if you were sitting in our office. It's a small office, and you might not be a fan of the Scottish weather (it's [dreich](https://www.bbc.co.uk/news/uk-scotland-50476008)), but you can at least be here virtually.

<!-- more -->

Release 0.4.0 follows 0.3.0, released on October 31st. Here are the highlights of the update.

## Updated Mount Method

The [mount](/api/widget/#textual.widget.Widget.mount) method has seen some work. We've dropped the ability to assign an `id` via keyword attributes, which wasn't terribly useful. Now, an `id` must be assigned via the constructor. 

The mount method has also grown `before` and `after` parameters which tell Textual where to add a new Widget (the default was to add it to the end). Here are a few examples:

```python

# Mount at the start
self.mount(Button(id="Buy Coffee"), before=0)

# Mount after a selector
self.mount(Static("Password is incorrect"), after="Dialog Input.-error")

# Mount after a specific widget
tweet = self.query_one("Tweet")
self.mount(Static("Consider switching to Mastodon"), after=tweet)

```

Textual needs much of the same kind of operations as the [JS API](https://developer.mozilla.org/en-US/docs/Web/API/Node/appendChild) exposed by the browser. But we are determined to make this way more intuitive. The new mount method is a step towards that. 

## Faster Updates

Textual now writes to stdout in a thread. The upshot of this is that Textual can work on the next update before the terminal has displayed the previous frame.

This means smoother updates all round! You may notice this when scrolling and animating, but even if you don't, you will have more CPU cycles to play with in your Textual app.

<div class="excalidraw">
--8<-- "docs/blog/images/faster-updates.excalidraw.svg"
</div>


## Multiple CSS Paths

Up to version 0.3.0, Textual would only read a single CSS file set in the `CSS_PATH` class variable. You can now supply a list of paths if you have more than one CSS file.

This change was prompted by [tuilwindcss](https://github.com/koaning/tuilwindcss/) which brings a TailwindCSS like approach to building Textual Widgets. Also check out [calmcode.io](https://calmcode.io/) by the same author, which is an amazing resource.
````

## File: docs/blog/posts/release0-6-0.md
````markdown
---
draft: false
date: 2022-12-11
categories:
  - Release
title: "version-060"
authors:
  - willmcgugan
---

# Textual 0.6.0 adds a *tree*mendous new widget

A new release of Textual lands 3 weeks after the previous release -- and it's a big one.

<!-- more -->

!!! information

    If you're new here, [Textual](https://github.com/Textualize/textual) is TUI framework for Python.

## Tree Control

The headline feature of version 0.6.0 is a new tree control built from the ground-up. The previous Tree control suffered from an overly complex API and wasn't scalable (scrolling slowed down with 1000s of nodes).

This new version has a simpler API and is highly scalable (no slowdown with larger trees). There are also a number of visual enhancements in this version.

Here's a very simple example:

=== "Output"

    ```{.textual path="docs/examples/widgets/tree.py"}
    ```

=== "tree.py"

    ```python
    --8<-- "docs/examples/widgets/tree.py"
    ```

Here's the tree control being used to navigate some JSON ([json_tree.py](https://github.com/Textualize/textual/blob/main/examples/json_tree.py) in the examples directory).

<div class="video-wrapper">
<iframe width="auto"  src="https://www.youtube.com/embed/Fy9fPL37P6o" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

I'm biased of course, but I think this terminal based tree control is more usable (and even prettier) than just about anything I've seen on the web or desktop. So much of computing tends to organize itself in to a tree that I think this widget will find a lot of uses. 

The Tree control forms the foundation of the [DirectoryTree](../../widgets/directory_tree.md) widget, which has also been updated. Here it is used in the [code_browser.py](https://github.com/Textualize/textual/blob/main/examples/code_browser.py) example:

<div class="video-wrapper">
<iframe width="auto" src="https://www.youtube.com/embed/ZrYWyZXuYRY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

## List View

We have a new [ListView](../../widgets/list_view.md) control to navigate and select items in a list. Items can be widgets themselves, which makes this a great platform for building more sophisticated controls.

=== "Output"

    ```{.textual path="docs/examples/widgets/list_view.py"}
    ```

=== "list_view.py"

    ```python
    --8<-- "docs/examples/widgets/list_view.py"
    ```

=== "list_view.css"

    ```sass
    --8<-- "docs/examples/widgets/list_view.css"
    ```

## Placeholder

The [Placeholder](../../widgets/placeholder.md) widget was broken since the big CSS update. We've brought it back and given it a bit of a polish.

Use this widget in place of custom widgets you have yet to build when designing your UI. The colors are automatically cycled to differentiate one placeholder from the next. You can click a placeholder to cycle between its ID, size, and lorem ipsum text.

=== "Output"

    ```{.textual path="docs/examples/widgets/placeholder.py" columns="100" lines="45"}
    ```

=== "placeholder.py"

    ```python
    --8<-- "docs/examples/widgets/placeholder.py"
    ```

=== "placeholder.css"

    ```sass
    --8<-- "docs/examples/widgets/placeholder.css"
    ```


## Fixes

As always, there are a number of fixes in this release. Mostly related to layout. See [CHANGELOG.md](https://github.com/Textualize/textual/blob/main/CHANGELOG.md) for the details.

## What's next?

The next release will focus on *pain points* we discovered while in a dog-fooding phase (see the [DevLog](https://textual.textualize.io/blog/category/devlog/) for details on what Textual devs have been building).
````

## File: docs/blog/posts/release0.37.0.md
````markdown
---
draft: false
date: 2023-09-15
categories:
  - Release
title: "Textual 0.37.0 adds a command palette"
authors:
  - willmcgugan
---


# Textual 0.37.0 adds a command palette

Textual version 0.37.0 has landed!
The highlight of this release is the new command palette.

<!-- more -->

A command palette gives users quick access to features in your app.
If you hit ctrl+backslash in a Textual app, it will bring up the command palette where you can start typing commands.
The commands are matched with a *fuzzy* search, so you only need to type two or three characters to get to any command.

Here's a video of it in action:

<div class="video-wrapper">
<iframe width="1280" height="auto" src="https://www.youtube.com/embed/sOMIkjmM4MY" title="" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

Adding your own commands to the command palette is a piece of cake.
Here's the (command) Provider class used in the example above:

```python
class ColorCommands(Provider):
    """A command provider to select colors."""

    async def search(self, query: str) -> Hits:
        """Called for each key."""
        matcher = self.matcher(query)
        for color in COLOR_NAME_TO_RGB.keys():
            score = matcher.match(color)
            if score > 0:
                yield Hit(
                    score,
                    matcher.highlight(color),
                    partial(self.app.post_message, SwitchColor(color)),
                )
```

And here is how you add a provider to your app:

```python
class ColorApp(App):
    """Experiment with the command palette."""

    COMMANDS = App.COMMANDS | {ColorCommands}
```

We're excited about this feature because it is a step towards bringing a common user interface to Textual apps.

!!! quote

    It's a Textual app. I know this.

    &mdash; You, maybe.

The goal is to be able to build apps that may look quite different, but take no time to learn, because once you learn how to use one Textual app, you can use them all.

See the Guide for details on how to work with the [command palette](../../guide/command_palette.md).

## What else?

Also in 0.37.0 we have a new [Collapsible](/widget_gallery/#collapsible) widget, which is a great way of adding content while avoiding a cluttered screen.

And of course, bug fixes and other updates. See the [release](https://github.com/Textualize/textual/releases/tag/v0.37.0) page for the full details.

## What's next?

Coming very soon, is a new TextEditor widget.
This is a super powerful widget to enter arbitrary text, with beautiful syntax highlighting for a number of languages.
We're expecting that to land next week.
Watch this space, or join the [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to be the first to try it out.

## Join us

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to discuss Textual with the Textualize devs, or the community.
````

## File: docs/blog/posts/release1.0.0.md
````markdown
---
draft: false
date: 2024-12-12
categories:
  - Release
title: "Algorithms for high performance terminal apps"
authors:
  - willmcgugan
---


I've had the fortune of being able to work fulltime on a FOSS project for the last three plus years.


<div style="width:250px;float:right;margin:10px;max-width:50%;">
<a href="https://github.com/textualize/textual-demo">
--8<-- "docs/blog/images/textual-demo.svg"
</a>
</div>


Textual has been a constant source of programming challenges.
Often frustrating but never boring, the challenges arise because the terminal "specification" says nothing about how to build a modern User Interface.
The building blocks are there: after some effort you can move the cursor, write colored text, read keys and mouse movements, but that's about it.
Everything else we had to build from scratch. From the most basic [button](https://textual.textualize.io/widget_gallery/#button) to a syntax highlighted [TextArea](https://textual.textualize.io/widget_gallery/#textarea), and everything along the way.

I wanted to write-up some of the solutions we came up with, and the 1.0 milestone we just passed makes this a perfect time.

<!-- more -->

Run the demo with a single line (with [uv](https://docs.astral.sh/uv/) is installed):

```
uvx --python 3.12 textual-demo
```



## The Compositor

The first component of Textual I want to cover is the [compositor](https://github.com/Textualize/textual/blob/main/src/textual/_compositor.py).
The job of the compositor is to combine content from multiple sources into a single view.

We do this because the terminal itself has no notion of overlapping windows in the way a desktop does.

Here's a video I generated over a year ago, demonstrating the compositor:

<div class="video-wrapper">
<iframe width="100%" height="auto" src="https://www.youtube.com/embed/T8PZjUVVb50" title="" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

### The algorithm

You could be forgiven in thinking that the terminal is regular grid of characters and we can treat it like a 2D array.
If that were the case, we could use [painter's algorithm](https://en.wikipedia.org/wiki/Painter's_algorithm) to handle the overlapping widgets.
In other words, sort them back to front and render them as though they were bitmaps.

Unfortunately the terminal is *not* a true grid.
Some characters such as those in Asian languages and many emoji are double the width of latin alphabet characters &mdash; which complicates things (to put it mildly).

Textual's way of handling this is inherited from [Rich](https://github.com/Textualize/rich).
Anything you print in Rich, first generates a list of [Segments](https://github.com/Textualize/rich/blob/master/rich/segment.py) which consist of a string and associated style.
These Segments are converted into text with [ansi escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code) at the very end of the process.


The compositor takes lists of segments generated by widgets and further processes them, by dividing and combining, to produce the final output. 
In fact almost everything Textual does involves processing these segments in one way or another.

!!! tip "Switch the Primitive"
    
    If a problem is intractable, it can often be simplified by changing what you consider to be the atomic data and operations you are working with.
    I call this "switching the primitive".
    In Rich this was switching from thinking in characters to thinking in segments.

### Thinking in Segments 

In the following illustration we have an app with three widgets; the background "screen" (in blue) plus two floating widgets (in red and green).
There will be many more widgets in a typical app, but this is enough to show how it works.


<div class="excalidraw">
--8<-- "docs/blog/images/compositor/widgets.excalidraw.svg"
</div>

The lines are lists of Segments produced by the widget renderer.
The compositor will combine those lists in to a single list where nothing overlaps.

To illustrate how this process works, let's consider the highlighted line about a quarter of the way down.


### Compositing a line

Imagine you could view the terminal and widgets side on, so that you see a cross section of the terminal and the floating widgets.
It would appear something like the following:

<div class="excalidraw">
--8<-- "docs/blog/images/compositor/cuts0.excalidraw.svg"
</div>

We can't yet display the output as it would require writing each "layer" independently, potentially making the terminal flicker, and certainly writing more data than necessary.

We need a few more steps to combine these lines in to a single line.


### Step 1. Finding the cuts.

First thing the compositor does is to find every offset where a list of segments begins or ends.
We call these "cuts".

<div class="excalidraw">
--8<-- "docs/blog/images/compositor/cuts1.excalidraw.svg"
</div>

### Step 2. Applying the cuts.

The next step is to divide every list of segments at the cut offsets.
This will produce smaller lists of segments, which we refer to as *chops*.

<div class="excalidraw">
--8<-- "docs/blog/images/compositor/cuts2.excalidraw.svg"
</div>

After this step we have lists of chops where each chop is of the same size, and therefore nothing overlaps.
It's the non-overlapping property that makes the next step possible.

### Step 3. Discard chops.

Only the top-most chops will actually be visible to the viewer.
Anything not at the top will be occluded and can be thrown away.

<div class="excalidraw">
--8<-- "docs/blog/images/compositor/cuts3.excalidraw.svg"
</div>

### Step 4. Combine.

Now all that's left is to combine the top-most chops in to a single list of Segments.
It is this list of segments that becomes a line in the terminal.

<div class="excalidraw">
--8<-- "docs/blog/images/compositor/cuts4.excalidraw.svg"
</div>

As this is the final step in the process, these lines of segments will ultimately be converted to text plus escape sequences and written to the output.

### What I omitted

There is more going on than this explanation may suggest.
Widgets may contain other widgets which are clipped to their *parent's* boundaries, and widgets that contain other widgets may also scroll &mdash; the compositor must take all of this in to account.

!!! info "It's widgets all the way down"

    Not to mention there can be multiple "screens" of widgets stacked on top of each other, with a modal fade effect applied to lower screens. 

The compositor can also do partial updates.
In other words, if you click a button and it changes color, the compositor can update just the region occupied by the button.

The compositor does all of this fast enough to enable smooth scrolling, even with a metric tonne of widgets on screen.

## Spatial map

Textual apps typically contain many widgets of different sizes and at different locations within the terminal.
Not all of which widgets may be visible in the final view (if they are within a scrolling container).


!!! info "The smallest Widget"

    While it is possible to have a widget as small as a single character, I've never found a need for one.
    The closest we get in Textual is a [scrollbar corner](https://textual.textualize.io/api/scrollbar/#textual.scrollbar.ScrollBarCorner);
    a widget which exists to fill the space made when a vertical scrollbar and a horizontal scrollbar meet.
    It does nothing because it doesn't need to, but it is powered by an async task like all widgets and can receive input.
    I have often wondered if there could be something useful in there.
    A game perhaps?
    If you can think of a game that can be played in 2 characters &mdash; let me know!

The *spatial map*[^1] is a data structure used by the compositor to very quickly discard widgets that are not visible within a given region.
The algorithm it uses may be familiar if you have done any classic game-dev.


### The problem 

Consider the following arrangement of widgets:

<div class="excalidraw">
--8<-- "docs/blog/images/compositor/spatial-map.excalidraw.svg"
</div>

Here we have 8 widgets, where only 3 or 4 will be visible at any given time, depending on the position of the scrollbar.
We want to avoid doing work on widgets which will not be seen in the next frame.

A naive solution to this would be to check each widget's [Region][textual.geometry.Region] to see if it overlaps with the visible area.
This is a perfectly reasonable solution, but it won't scale well.
If we get in to the 1000s of widgets territory, it may become significant &mdash; and we may have to do this 30 times a second if we are scrolling.

### The Grid

The first step in the spatial map is to associate every widget with a tile in a regular grid[^2].

<div class="excalidraw">
--8<-- "docs/blog/images/compositor/spatial-map-grid.excalidraw.svg"
</div>

The size of the grid is fairly arbitrary, but it should be large enough to cover the viewable area with a relatively small number of grid tiles.
We use a grid size of 100 characters by 20 lines, which seems about right.

When the spatial map is first created it places each widget in one or more grid tiles.
At the end of that process we have a dict that maps every grid coordinate on to a list of widgets, which will look something like the following:

```python
{
    (0, 0): [widget1, widget2, widget3],
    (1, 0): [widget1, widget2, widget3],
    (0, 1): [widget4, widget5, widget6],
    (1, 1): [widget4, widget5, widget6],
    (0, 2): [widget7, widget8],
    (1, 2): [Widget7, widget8]
}
```

The up-front cost of [calculating](https://github.com/Textualize/textual/blob/main/src/textual/_spatial_map.py) this data is fairly low.
It is also very cacheable &mdash; we *do not* need to recalculate it when the user is just scrolling.

### Search the grid

The speedups from the spatial map come when we want to know which widgets are visible.
To do that, we first create a region that covers the area we want to consider &mdash; which may be the entire screen, or a smaller scrollable container.

In the following illustration we have scrolled the screen up[^3] a little so that Widget 3 is at the top of the screen:

<div class="excalidraw">
--8<-- "docs/blog/images/compositor/spatial-map-view1.excalidraw.svg"
</div>

We then determine which grid tiles overlap the viewable area.
In the above examples that would be the tiles with coordinates  `(0,0)`, `(1,0)`, `(0,1)`, and `(1,1)`.
Once we have that information, we can then then look up those coordinates in the spatial map data structure, which would retrieve 4 lists:

```python
[
  [widget1, widget2, widget3],
  [widget1, widget2, widget3],
  [widget4, widget5, widget6],
  [widget4, widget5, widget6],
]
```

Combining those together and de-duplicating we get:

```python
[widget1, widget2, widget3, widget4, widget5, widget6]
```

These widgets are either within the viewable area, or close by.
We can confidently conclude that the widgets *not* ion that list are hidden from view.
If we need to know precisely which widgets are visible we can check their regions individually.

The useful property of this algorithm is that as the number of widgets increases, the time it takes to figure out which are visible stays relatively constant. Scrolling a view of 8 widgets, takes much the same time as a view of 1000 widgets or more.

The code for our `SpatialMap` isn't part of the public API and therefore not in the docs, but if you are interested you can check it out here: [_spatial_map.py](https://github.com/Textualize/textual/blob/main/src/textual/_spatial_map.py).

## Wrapping up

If any of the code discussed here interests you, you have my blessing to [steal the code](./steal-this-code.md)!

As always, if you want to discuss this or Textual in general, we can be found on our [Discord server](https://discord.gg/Enf6Z3qhVr).



[^1]: A term I coined for the structure in Textual. There may be other unconnected things known as spatial maps.
[^2]: The [grid](https://www.youtube.com/watch?v=lILHEnz8fTk&ab_channel=DaftPunk-Topic).
[^3]: If you scroll the screen up, it moves *down* relative to the widgets.
````

## File: docs/blog/posts/remote-memray.md
````markdown
---
draft: false
date: 2024-02-20
categories:
  - DevLog
authors:
  - willmcgugan
---

# Remote memory profiling with Memray

[Memray](https://github.com/bloomberg/memray) is a memory profiler for Python, built by some very smart devs at Bloomberg.
It is a fantastic tool to identify memory leaks in your code or other libraries (down to the C level)!

They recently added a [Textual](https://github.com/textualize/textual/) interface which looks amazing, and lets you monitor your process right from the terminal:

![Memray](https://raw.githubusercontent.com/bloomberg/memray/main/docs/_static/images/live_animated.webp)

<!-- more -->

You would typically run this locally, or over a ssh session, but it is also possible to serve the interface over the web with the help of [textual-web](https://github.com/Textualize/textual-web).
I'm not sure if even the Memray devs themselves are aware of this, but here's how.

First install Textual web (ideally with pipx) alongside Memray:

```bash
pipx install textual-web
```

Now you can serve Memray with the following command (replace the text in quotes with your Memray options):

```bash
textual-web -r "memray run --live -m http.server"
```

This will return a URL you can use to access the Memray app from anywhere.
Here's a quick video of that in action:

<iframe style="aspect-ratio: 16 /10" width="100%" src="https://www.youtube.com/embed/7lpoUBdxzus" title="Serving Memray with Textual web" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Found this interesting?


Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you want to discuss this post with the Textual devs or community.
````

## File: docs/blog/posts/responsive-app-background-task.md
````markdown
---
draft: false
date: 2022-12-07
categories:
  - DevLog
authors:
  - rodrigo
---

# Letting your cook multitask while bringing water to a boil

Whenever you are cooking a time-consuming meal, you want to multitask as much as possible.
For example, you **do not** want to stand still while you wait for a pot of water to start boiling.
Similarly, you want your applications to remain responsive (i.e., you want the cook to “multitask”) while they do some time-consuming operations in the background (e.g., while the water heats up).

The animation below shows an example of an application that remains responsive (colours on the left still change on click) even while doing a bunch of time-consuming operations (shown on the right).

![](../images/2022-12-07-responsive-app-background-task/responsive-demo.gif)

In this blog post, I will teach you how to multitask like a good cook.

<!-- more -->


## Wasting time staring at pots

There is no point in me presenting a solution to a problem if you don't understand the problem I am trying to solve.
Suppose we have an application that needs to display a huge amount of data that needs to be read and parsed from a file.
The first time I had to do something like this, I ended up writing an application that “blocked”.
This means that _while_ the application was reading and parsing the data, nothing else worked.

To exemplify this type of scenario, I created a simple application that spends five seconds preparing some data.
After the data is ready, we display a `Label` on the right that says that the data has been loaded.
On the left, the app has a big rectangle (a custom widget called `ColourChanger`) that you can click and that changes background colours randomly.

When you start the application, you can click the rectangle on the left to change the background colour of the `ColourChanger`, as the animation below shows:

![](../images/2022-12-07-responsive-app-background-task/blocking01-colour-changer.gif)

However, as soon as you press `l` to trigger the data loading process, clicking the `ColourChanger` widget doesn't do anything.
The app doesn't respond because it is busy working on the data.
This is the code of the app so you can try it yourself:

```py hl_lines="11-13 21 35 36"
--8<-- "docs/blog/snippets/2022-12-07-responsive-app-background-task/blocking01.py"
```

1. The widget `ColourChanger` changes colours, randomly, when clicked.
2. We create a binding to the key `l` that runs an action that we know will take some time (for example, reading and parsing a huge file).
3. The method `action_load` is responsible for starting our time-consuming task and then reporting back.
4. To simplify things a bit, our “time-consuming task” is just standing still for 5 seconds.

I think it is easy to understand why the widget `ColourChanger` stops working when we hit the `time.sleep` call if we consider [the cooking analogy](https://mathspp.com/blog/til/cooking-with-asyncio) I have written about before in my blog.
In short, Python behaves like a lone cook in a kitchen:

 - the cook can be clever and multitask. For example, while water is heating up and being brought to a boil, the cook can go ahead and chop some vegetables.
 - however, there is _only one_ cook in the kitchen, so if the cook is chopping up vegetables, they can't be seasoning a salad.

Things like “chopping up vegetables” and “seasoning a salad” are _blocking_, i.e., they need the cook's time and attention.
In the app that I showed above, the call to `time.sleep` is blocking, so the cook can't go and do anything else until the time interval elapses.

## How can a cook multitask?

It makes a lot of sense to think that a cook would multitask in their kitchen, but Python isn't like a smart cook.
Python is like a very dumb cook who only ever does one thing at a time and waits until each thing is completely done before doing the next thing.
So, by default, Python would act like a cook who fills up a pan with water, starts heating the water, and then stands there staring at the water until it starts boiling instead of doing something else.
It is by using the module `asyncio` from the standard library that our cook learns to do other tasks while _awaiting_ the completion of the things they already started doing.

[Textual](https://github.com/textualize/textual) is an async framework, which means it knows how to interoperate with the module `asyncio` and this will be the solution to our problem.
By using `asyncio` with the tasks we want to run in the background, we will let the application remain responsive while we load and parse the data we need, or while we crunch the numbers we need to crunch, or while we connect to some slow API over the Internet, or whatever it is you want to do.

The module `asyncio` uses the keyword `async` to know which functions can be run asynchronously.
In other words, you use the keyword `async` to identify functions that contain tasks that would otherwise force the cook to waste time.
(Functions with the keyword `async` are called _coroutines_.)

The module `asyncio` also introduces a function `asyncio.create_task` that you can use to run coroutines concurrently.
So, if we create a coroutine that is in charge of doing the time-consuming operation and then run it with `asyncio.create_task`, we are well on our way to fix our issues.

However, the keyword `async` and `asyncio.create_task` alone aren't enough.
Consider this modification of the previous app, where the method `action_load` now uses `asyncio.create_task` to run a coroutine who does the sleeping:

```py hl_lines="36-37 39"
--8<-- "docs/blog/snippets/2022-12-07-responsive-app-background-task/blocking02.py"
```

1. The action method `action_load` now defers the heavy lifting to another method we created.
2. The time-consuming operation can be run concurrently with `asyncio.create_task` because it is a coroutine.
3. The method `_do_long_operation` has the keyword `async`, so it is a coroutine.

This modified app also works but it suffers from the same issue as the one before!
The keyword `async` tells Python that there will be things inside that function that can be _awaited_ by the cook.
That is, the function will do some time-consuming operation that doesn't require the cook's attention.
However, we need to tell Python which time-consuming operation doesn't require the cook's attention, i.e., which time-consuming operation can be _awaited_, with the keyword `await`.

Whenever we want to use the keyword `await`, we need to do it with objects that are compatible with it.
For many things, that means using specialised libraries:

 - instead of `time.sleep`, one can use `await asyncio.sleep`;
 - instead of the module `requests` to make Internet requests, use `aiohttp`; or
 - instead of using the built-in tools to read files, use `aiofiles`.

## Achieving good multitasking

To fix the last example application, all we need to do is replace the call to `time.sleep` with a call to `asyncio.sleep` and then use the keyword `await` to signal Python that we can be doing something else while we sleep.
The animation below shows that we can still change colours while the application is completing the time-consuming operation.

=== "Code"

    ```py hl_lines="40 41 42"
    --8<-- "docs/blog/snippets/2022-12-07-responsive-app-background-task/nonblocking01.py"
    ```

    1. We create a label that tells the user that we are starting our time-consuming operation.
    2. We `await` the time-consuming operation so that the application remains responsive.
    3. We create a label that tells the user that the time-consuming operation has been concluded.

=== "Animation"

    ![](../images/2022-12-07-responsive-app-background-task/non-blocking.gif)

Because our time-consuming operation runs concurrently, everything else in the application still works while we _await_ for the time-consuming operation to finish.
In particular, we can keep changing colours (like the animation above showed) but we can also keep activating the binding with the key `l` to start multiple instances of the same time-consuming operation!
The animation below shows just this:

![](../images/2022-12-07-responsive-app-background-task/responsive-demo.gif)

!!! warning

    The animation GIFs in this blog post show low-quality colours in an attempt to reduce the size of the media files you have to download to be able to read this blog post.
    If you run Textual locally you will see beautiful colours ✨
````

## File: docs/blog/posts/rich-inspect.md
````markdown
---
draft: false
date: 2023-07-27
categories:
  - DevLog
title: Using Rich Inspect to interrogate Python objects
authors:
  - willmcgugan
---

# Using Rich Inspect to interrogate Python objects

The [Rich](https://github.com/Textualize/rich) library has a few functions that are admittedly a little out of scope for a terminal color library. One such function is `inspect` which is so useful you may want to `pip install rich` just for this feature.

<!-- more -->

The easiest way to describe `inspect` is that it is Python's builtin `help()` but easier on the eye (and with a few more features).
If you invoke it with any object, `inspect` will display a nicely formatted report on that object &mdash; which makes it great for interrogating objects from the REPL. Here's an example:

```python
>>> from rich import inspect
>>> text_file = open("foo.txt", "w")
>>> inspect(text_file)
```

Here we're inspecting a file object, but it could be literally anything.
You will see the following output in the terminal:

<div>
--8<-- "docs/blog/images/inspect1.svg"
</div>

By default, `inspect` will generate a data-oriented summary with a text representation of the object and its data attributes.
You can also add `methods=True` to show all the methods in the public API.
Here's an example:

```python
>>> inspect(text_file, methods=True)
```

<div>
--8<-- "docs/blog/images/inspect2.svg"
</div>

The documentation is summarized by default to avoid generating verbose reports.
If you want to see the full unabbreviated help you can add `help=True`:

```python
>>> inspect(text_file, methods=True, help=True)
```

<div>
--8<-- "docs/blog/images/inspect3.svg"
</div>

There are a few more arguments to refine the level of detail you need (private methods, dunder attributes etc).
You can see the full range of options with this delightful little incantation:

```python
>>> inspect(inspect)
```

If you are interested in Rich or Textual, join our [Discord server](https://discord.gg/Enf6Z3qhVr)!


## Addendum

Here's how to have `inspect` always available without an explicit import:

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Put this in your pythonrc file: <a href="https://t.co/pXTi69ykZL">pic.twitter.com/pXTi69ykZL</a></p>&mdash; Tushar Sadhwani (@sadhlife) <a href="https://twitter.com/sadhlife/status/1684446413785280517?ref_src=twsrc%5Etfw">July 27, 2023</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
````

## File: docs/blog/posts/smooth-scrolling.md
````markdown
---
draft: false
date: 2025-02-16
categories:
  - DevLog
authors:
  - willmcgugan
---

# Smoother scrolling in the terminal &mdash; a feature decades in the making

The great philosopher F. Bueller once said “Life moves pretty fast. If you don't stop and look around once in a while, you could miss it.”

Beuller was *not* taking about terminals, which tend not to move very fast at all.
Until they do.
From time to time terminals acquire new abilities after a long plateau.
We are now seeing a kind of punctuated evolution in terminals which makes things possible that just weren't feasible a short time ago.

I want to talk about one such feature, which *I believe* has been decades[^1] in the making.
Take a look at the following screen recording (taken from a TUI running in the terminal):

![A TUI Scrollbar](../images/smooth-scroll/no-smooth-scroll.gif)

<!-- more -->

Note how the mouse pointer moves relatively smoothly, but the scrollbar jumps with a jerky motion.

This happens because the terminal reports the mouse coordinates in cells (a *cell* is the dimensions of a single latin-alphabet character). 
In other words, the app knows only which cell is under the pointer.
It isn't granular enough to know where the pointer is *within* a cell.

Until recently terminal apps couldn't do any better.
More granular mouse reporting is possible in the terminal; write the required escape sequence and mouse coordinates are reported in pixels rather than cells.

So why haven't TUIs been using this?

The problem is that pixel coordinates are pretty much useless in TUIs unless we have some way of translating between pixel and cell coordinates.
Without that, we can never know which cell the user clicked on.

It's a trivial calculation, but we are missing a vital piece of information; the size of the terminal window in pixels.
If we had that, we could divide the pixel dimensions by the cell dimensions to calculate the pixels per cell.
Divide pixel coordinates by *pixels per cell* and we have cell coordinates.

But the terminal reports its size in cells, and *not* pixels.
So we can't use granular mouse coordinates.

!!! question "What did people use pixel coordinate for?"

    This does make we wonder what pixel reporting was ever used for in terminals.
    Ping me on Discord if you know!


At least we couldn't until [this recent extension](https://gist.github.com/rockorager/e695fb2924d36b2bcf1fff4a3704bd83) which reports the size of the terminal in cell *and* pixel coordinates.
Once we have both the mouse coordinates in pixels and the dimensions of the terminal in pixels, we can implement much smoother scrolling.

Let's see how this looks.

On the left we have the default scrolling, on the right, Textual is using granular mouse coordinates.


| Default scrolling                                                | Smooth scrolling                                                                    |
| ---------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| ![A TUI Scrollbar](../images/smooth-scroll/no-smooth-scroll.gif) | ![A TUI Scrollbar with smooth scrolling](../images/smooth-scroll/smooth-scroll.gif) |

Notice how much smoother the motion of the table is, now that it tracks the mouse cursor more accurately.

If you have one of the terminals which support this feature[^2], and at least [Textual](https://github.com/textualize/textual/) 2.0.0 you will be able to see this in action.

I think Textual may be the first library to implement this.
Let me know, if you have encountered any non-Textual TUI app which implements this kind of smooth scrolling.

## Join us

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) to discuss anything terminal related with the Textualize devs, or the community!


[^1]: I'm not sure exactly when pixel mouse reporting was added to terminals. I'd be interested if anyone has a precised date.
[^2]: Kitty, Ghostty, and a few others.
````

## File: docs/blog/posts/spinners-and-pbs-in-textual.md
````markdown
---
draft: false
date: 2022-11-24
categories:
  - DevLog
authors:
  - rodrigo
---

# Spinners and progress bars in Textual

![](../images/spinners-and-pbs-in-textual/live-display.gif)

One of the things I love about mathematics is that you can solve a problem just by **guessing** the correct answer.
That is a perfectly valid strategy for solving a problem.
The only thing you need to do after guessing the answer is to prove that your guess is correct.

I used this strategy, to some success, to display spinners and indeterminate progress bars from [Rich](github.com/textualize/rich) in [Textual](https://github.com/textualize/textual).

<!-- more -->


## Display an indeterminate progress bar in Textual

I have been playing around with Textual and recently I decided I needed an indeterminate progress bar to show that some data was loading.
Textual is likely to [get progress bars in the future](https://github.com/Textualize/rich/issues/2665#issuecomment-1326229220), but I don't want to wait for the future!
I want my progress bars now!
Textual builds on top of Rich, so if [Rich has progress bars](https://rich.readthedocs.io/en/stable/progress.html), I reckoned I could use them in my Textual apps.


### Progress bars in Rich

Creating a progress bar in Rich is as easy as opening up the documentation for `Progress` and copying & pasting the code.


=== "Code"

    ```py
    import time
    from rich.progress import track

    for _ in track(range(20), description="Processing..."):
        time.sleep(0.5)  # Simulate work being done
    ```

=== "Output"

    ![](../images/spinners-and-pbs-in-textual/rich-progress-bar.gif)


The function `track` provides a very convenient interface for creating progress bars that keep track of a well-specified number of steps.
In the example above, we were keeping track of some task that was going to take 20 steps to complete.
(For example, if we had to process a list with 20 elements.)
However, I am looking for indeterminate progress bars.

Scrolling further down the documentation for `rich.progress` I found what I was looking for:

=== "Code"

    ```py hl_lines="5"
    import time
    from rich.progress import Progress

    with Progress() as progress:
        _ = progress.add_task("Loading...", total=None)  # (1)!
        while True:
            time.sleep(0.01)
    ```

    1. Setting `total=None` is what makes it an indeterminate progress bar.

=== "Output"

    ![](../images/spinners-and-pbs-in-textual/indeterminate-rich-progress-bar.gif)

So, putting an indeterminate progress bar on the screen is _easy_.
Now, I only needed to glue that together with the little I know about Textual to put an indeterminate progress bar in a Textual app.


### Guessing what is what and what goes where

What I want is to have an indeterminate progress bar inside my Textual app.
Something that looks like this:

![](../images/spinners-and-pbs-in-textual/bar-in-textual.gif)

The GIF above shows just the progress bar.
Obviously, the end goal is to have the progress bar be part of a Textual app that does something.

So, when I set out to do this, my first thought went to the stopwatch app in the [Textual tutorial](https://textual.textualize.io/tutorial) because it has a widget that updates automatically, the `TimeDisplay`.
Below you can find the essential part of the code for the `TimeDisplay` widget and a small animation of it updating when the stopwatch is started.


=== "`TimeDisplay` widget"

    ```py hl_lines="14 18 22"
    from time import monotonic

    from textual.reactive import reactive
    from textual.widgets import Static


    class TimeDisplay(Static):
        """A widget to display elapsed time."""

        start_time = reactive(monotonic)
        time = reactive(0.0)
        total = reactive(0.0)

        def on_mount(self) -> None:
            """Event handler called when widget is added to the app."""
            self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

        def update_time(self) -> None:
            """Method to update time to current."""
            self.time = self.total + (monotonic() - self.start_time)

        def watch_time(self, time: float) -> None:
            """Called when the time attribute changes."""
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")
    ```

=== "Output"

    ![](../images/spinners-and-pbs-in-textual/stopwatch-timedisplay.gif)


The reason the time display updates magically is due to the three methods that I highlighted in the code above:

 1. The method `on_mount` is called when the `TimeDisplay` widget is mounted on the app and, in it, we use the method `set_interval` to let Textual know that every `1 / 60` seconds we would like to call the method `update_time`. (In other words, we would like `update_time` to be called 60 times per second.)
 2. In turn, the method `update_time` (which is called _automatically_ a bunch of times per second) will update the reactive attribute `time`. _When_ this attribute update happens, the method `watch_time` kicks in.
 3. The method `watch_time` is a watcher method and gets called whenever the attribute `self.time` is assigned to.
 So, if the method `update_time` is called a bunch of times per second, the watcher method `watch_time` is also called a bunch of times per second. In it, we create a nice representation of the time that has elapsed and we use the method `update` to update the time that is being displayed.

I thought it would be reasonable if a similar mechanism needed to be in place for my progress bar, but then I realised that the progress bar seems to update itself...
Looking at the indeterminate progress bar example from before, the only thing going on was that we used `time.sleep` to stop our program for a bit.
We didn't do _anything_ to update the progress bar...
Look:

```py
with Progress() as progress:
    _ = progress.add_task("Loading...", total=None)  # (1)!
    while True:
        time.sleep(0.01)
```

After pondering about this for a bit, I realised I would not need a watcher method for anything.
The watcher method would only make sense if I needed to update an attribute related to some sort of artificial progress, but that clearly isn't needed to get the bar going...

At some point, I realised that the object `progress` is the object of interest.
At first, I thought `progress.add_task` would return the progress bar, but it actually returns the integer ID of the task added, so the object of interest is `progress`.
Because I am doing nothing to update the bar explicitly, the object `progress` must be updating itself.

The Textual documentation also says that we can [build widgets from Rich renderables](https://textual.textualize.io/guide/widgets/#rich-renderables), so I concluded that if `Progress` were a renderable, then I could inherit from `Static` and use the method `update` to update the widget with my instance of `Progress` directly.
I gave it a try and I put together this code:

```py hl_lines="10 11 15-17 20"
from rich.progress import Progress, BarColumn

from textual.app import App, ComposeResult
from textual.widgets import Static


class IndeterminateProgress(Static):
    def __init__(self):
        super().__init__("")
        self._bar = Progress(BarColumn())  # (1)!
        self._bar.add_task("", total=None)  # (2)!

    def on_mount(self) -> None:
        # When the widget is mounted start updating the display regularly.
        self.update_render = self.set_interval(
            1 / 60, self.update_progress_bar
        )  # (3)!

    def update_progress_bar(self) -> None:
        self.update(self._bar)  # (4)!


class MyApp(App):
    def compose(self) -> ComposeResult:
        yield IndeterminateProgress()


if __name__ == "__main__":
    app = MyApp()
    app.run()
```

 1. Create an instance of `Progress` that just cares about the bar itself (Rich progress bars can have a label, an indicator for the time left, etc).
 2. We add the indeterminate task with `total=None` for the indeterminate progress bar.
 3. When the widget is mounted on the app, we want to start calling `update_progress_bar` 60 times per second.
 4. To update the widget of the progress bar we just call the method `Static.update` with the `Progress` object because `self._bar` is a Rich renderable.

And lo and behold, it worked:

![](../images/spinners-and-pbs-in-textual/bar-in-textual.gif)


### Proving it works

I finished writing this piece of code and I was ecstatic because it was working!
After all, my Textual app starts and renders the progress bar.
And so, I shared this simple app with someone who wanted to do a similar thing, but I was left with a bad taste in my mouth because I couldn't really connect all the dots and explain exactly why it worked.

!!! warning "Plot twist"

    By the end of the blog post, I will be much closer to a full explanation!


## Display a Rich spinner in a Textual app

A day after creating my basic `IndeterminateProgress` widget, I found someone that was trying to display a Rich spinner in a Textual app.
Actually, it was someone that had [filed an issue against Rich](https://github.com/Textualize/rich/issues/2665).
They didn't ask “how can I display a Rich spinner in a Textual app?”, but they filed an alleged bug that crept up on them _when_ they tried displaying a spinner in a Textual app.

When reading the issue I realised that displaying a Rich spinner looked very similar to displaying a Rich progress bar, so I made a tiny change to my code and tried to run it:

=== "Code"

    ```py hl_lines="10"
    from rich.spinner import Spinner

    from textual.app import App, ComposeResult
    from textual.widgets import Static


    class SpinnerWidget(Static):
        def __init__(self):
            super().__init__("")
            self._spinner = Spinner("moon")  # (1)!

        def on_mount(self) -> None:
            self.update_render = self.set_interval(1 / 60, self.update_spinner)

        def update_spinner(self) -> None:
            self.update(self._spinner)


    class MyApp(App[None]):
        def compose(self) -> ComposeResult:
            yield SpinnerWidget()


    MyApp().run()
    ```

    1. Instead of creating an instance of `Progress`, we create an instance of `Spinner` and save it so we can call `self.update(self._spinner)` later on.

=== "Spinner running"

    ![](../images/spinners-and-pbs-in-textual/spinner.gif)


## Losing the battle against pausing the animations

After creating the progress bar and spinner widgets I thought of creating the little display that was shown at the beginning of the blog post:

![](../images/spinners-and-pbs-in-textual/live-display.gif)

When writing the code for this app, I realised both widgets had a lot of shared code and logic and I tried abstracting away their common functionality.
That led to the code shown below (more or less) where I implemented the updating functionality in `IntervalUpdater` and then let the `IndeterminateProgressBar` and `SpinnerWidget` instantiate the correct Rich renderable.

```py hl_lines="8-15 22 30"
from rich.progress import Progress, BarColumn
from rich.spinner import Spinner

from textual.app import RenderableType
from textual.widgets import Button, Static


class IntervalUpdater(Static):
    _renderable_object: RenderableType  # (1)!

    def update_rendering(self) -> None:  # (2)!
        self.update(self._renderable_object)

    def on_mount(self) -> None:  # (3)!
        self.interval_update = self.set_interval(1 / 60, self.update_rendering)


class IndeterminateProgressBar(IntervalUpdater):
    """Basic indeterminate progress bar widget based on rich.progress.Progress."""
    def __init__(self) -> None:
        super().__init__("")
        self._renderable_object = Progress(BarColumn())  # (4)!
        self._renderable_object.add_task("", total=None)


class SpinnerWidget(IntervalUpdater):
    """Basic spinner widget based on rich.spinner.Spinner."""
    def __init__(self, style: str) -> None:
        super().__init__("")
        self._renderable_object = Spinner(style)  # (5)!
```

 1. Instances of `IntervalUpdate` should set the attribute `_renderable_object` to the instance of the Rich renderable that we want to animate.
 2. The methods `update_rendering` and `on_mount` are exactly the same as what we had before, both in the progress bar widget and in the spinner widget.
 3. The methods `update_rendering` and `on_mount` are exactly the same as what we had before, both in the progress bar widget and in the spinner widget.
 4. For an indeterminate progress bar we set the attribute `_renderable_object` to an instance of `Progress`.
 5. For a spinner we set the attribute `_renderable_object` to an instance of `Spinner`.

But I wanted something more!
I wanted to make my app similar to the stopwatch app from the terminal and thus wanted to add a “Pause” and a “Resume” button.
These buttons should, respectively, stop the progress bar and the spinner animations and resume them.

Below you can see the code I wrote and a short animation of the app working.


=== "App code"

    ```py hl_lines="18-19 21-22 60-70 55-56"
    from rich.progress import Progress, BarColumn
    from rich.spinner import Spinner

    from textual.app import App, ComposeResult, RenderableType
    from textual.containers import Grid, Horizontal, Vertical
    from textual.widgets import Button, Static


    class IntervalUpdater(Static):
        _renderable_object: RenderableType

        def update_rendering(self) -> None:
            self.update(self._renderable_object)

        def on_mount(self) -> None:
            self.interval_update = self.set_interval(1 / 60, self.update_rendering)

        def pause(self) -> None:  # (1)!
            self.interval_update.pause()

        def resume(self) -> None:  # (2)!
            self.interval_update.resume()


    class IndeterminateProgressBar(IntervalUpdater):
        """Basic indeterminate progress bar widget based on rich.progress.Progress."""
        def __init__(self) -> None:
            super().__init__("")
            self._renderable_object = Progress(BarColumn())
            self._renderable_object.add_task("", total=None)


    class SpinnerWidget(IntervalUpdater):
        """Basic spinner widget based on rich.spinner.Spinner."""
        def __init__(self, style: str) -> None:
            super().__init__("")
            self._renderable_object = Spinner(style)


    class LiveDisplayApp(App[None]):
        """App showcasing some widgets that update regularly."""
        CSS_PATH = "myapp.css"

        def compose(self) -> ComposeResult:
            yield Vertical(
                    Grid(
                        SpinnerWidget("moon"),
                        IndeterminateProgressBar(),
                        SpinnerWidget("aesthetic"),
                        SpinnerWidget("bouncingBar"),
                        SpinnerWidget("earth"),
                        SpinnerWidget("dots8Bit"),
                    ),
                    Horizontal(
                        Button("Pause", id="pause"),  # (3)!
                        Button("Resume", id="resume", disabled=True),
                    ),
            )

        def on_button_pressed(self, event: Button.Pressed) -> None:  # (4)!
            pressed_id = event.button.id
            assert pressed_id is not None
            for widget in self.query(IntervalUpdater):
                getattr(widget, pressed_id)()  # (5)!

            for button in self.query(Button):  # (6)!
                if button.id == pressed_id:
                    button.disabled = True
                else:
                    button.disabled = False


    LiveDisplayApp().run()
    ```

    1. The method `pause` looks at the attribute `interval_update` (returned by the method `set_interval`) and tells it to stop calling the method `update_rendering` 60 times per second.
    2. The method `resume` looks at the attribute `interval_update` (returned by the method `set_interval`) and tells it to resume calling the method `update_rendering` 60 times per second.
    3. We set two distinct IDs for the two buttons so we can easily tell which button was pressed and _what_ the press of that button means.
    4. The event handler `on_button_pressed` will wait for button presses and will take care of pausing or resuming the animations.
    5. We look for all of the instances of `IntervalUpdater` in our app and use a little bit of introspection to call the correct method (`pause` or `resume`) in our widgets. Notice this was only possible because the buttons were assigned IDs that matched the names of the methods. (I love Python :snake:!)
    6. We go through our two buttons to disable the one that was just pressed and to enable the other one.

=== "CSS"

    ```sass
    Screen {
        align: center middle;
    }

    Horizontal {
        height: 1fr;
        align-horizontal: center;
    }

    Button {
        margin: 0 3 0 3;
    }

    Grid {
        height: 4fr;
        align: center middle;
        grid-size: 3 2;
        grid-columns: 8;
        grid-rows: 1;
        grid-gutter: 1;
        border: gray double;
    }

    IntervalUpdater {
        content-align: center middle;
    }
    ```

=== "Output"

    ![](../images/spinners-and-pbs-in-textual/pause-resume-appears-to-work.gif)


If you think this was a lot, take a couple of deep breaths before moving on.

The only issue with my app is that... it does not work!
If you press the button to pause the animations, it looks like the widgets are paused.
However, you can see that if I move my mouse over the paused widgets, they update:

![](../images/spinners-and-pbs-in-textual/fake-pause.gif)

Obviously, that caught me by surprise, in the sense that I expected it work.
On the other hand, this isn't surprising.
After all, I thought I had guessed how I could solve the problem of displaying these Rich renderables that update live and I thought I knew how to pause and resume their animations, but I hadn't convinced myself I knew exactly why it worked.

!!! warning

    This goes to show that sometimes it is not the best idea to commit code that you wrote and that works if you don't know _why_ it works.
    The code might _seem_ to work and yet have deficiencies that will hurt you further down the road.

As it turns out, the reason why pausing is not working is that I did not grok why the rendering worked in the first place...
So I had to go down that rabbit hole first.


## Understanding the Rich rendering magic

### How `Static.update` works

The most basic way of creating a Textual widget is to inherit from `Widget` and implement the method `render` that just returns the _thing_ that must be printed on the screen.
Then, the widget `Static` provides some functionality on top of that: the method `update`.

The method `Static.update(renderable)` is used to tell the widget in question that its method `render` (called when the widget needs to be drawn) should just return `renderable`.
So, if the implementation of the method `IntervalUpdater.update_rendering` (the method that gets called 60 times per second) is this:

```py
class IntervalUpdater(Static):
    # ...
    def update_rendering(self) -> None:
        self.update(self._renderable_object)
```

Then, we are essentially saying “hey, the thing in `self._renderable_object` is what must be returned whenever Textual asks you to render yourself.
So, this really proves that both `Progress` and `Spinner` from Rich are renderables.
But what is more, this shows that my implementation of `IntervalUpdater` can be simplified greatly!
In fact, we can boil it down to just this:

```py hl_lines="4-6 9"
class IntervalUpdater(Static):
    _renderable_object: RenderableType

    def __init__(self, renderable_object: RenderableType) -> None:  # (1)!
        super().__init__(renderable_object)  # (2)!

    def on_mount(self) -> None:
        self.interval_update = self.set_interval(1 / 60, self.refresh)  # (3)!
```

 1. To create an instance of `IntervalUpdater`, now we give it the Rich renderable that we want displayed.
If this Rich renderable is something that updates over time, then those changes will be reflected in the rendering.
 2. We initialise `Static` with the renderable object itself, instead of initialising with the empty string `""` and then updating repeatedly.
 3. We call `self.refresh` 60 times per second.
We don't need the auxiliary method `update_rendering` because this widget (an instance of `Static`) already knows what its renderable is.

Once you understand the code above you will realise that the previous implementation of `update_rendering` was actually doing superfluous work because the repeated calls to `self.update` always had the exact same object.
Again, we see strong evidence that the Rich progress bars and the spinners have the inherent ability to display a different representation of themselves as time goes by.

### How Rich spinners get updated

I kept seeing strong evidence that Rich spinners and Rich progress bars updated their own rendering but I still did not have actual proof.
So, I went digging around to see how `Spinner` was implemented and I found this code ([from the file `spinner.py`](https://github.com/Textualize/rich/blob/5f4e93efb159af99ed51f1fbfd8b793bb36448d9/rich/spinner.py) at the time of writing):

```py hl_lines="7 10 13-15"
class Spinner:
    # ...

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield self.render(console.get_time())  # (1)!

    # ...
    def render(self, time: float) -> "RenderableType":  # (2)!
        # ...

        frame_no = ((time - self.start_time) * self.speed) / (  # (3)!
            self.interval / 1000.0
        ) + self.frame_no_offset
        # ...

    # ...
```

 1. The Rich spinner implements the function `__rich_console__` that is supposed to return the result of rendering the spinner.
Instead, it defers its work to the method `render`...
However, to call the method `render`, we need to pass the argument `console.get_time()`, which the spinner uses to know in which state it is!
 2. The method `render` takes a `time` and returns a renderable!
 3. To determine the frame number (the current look of the spinner) we do some calculations with the “current time”, given by the parameter `time`, and the time when the spinner started!

The snippet of code shown above, from the implementation of `Spinner`, explains why moving the mouse over a spinner (or a progress bar) that supposedly was paused makes it move.
We no longer get repeated updates (60 times per second) because we told our app that we wanted to pause the result of `set_interval`, so we no longer get automatic updates.
However, moving the mouse over the spinners and the progress bar makes Textual want to re-render them and, when it does, it figures out that time was not frozen (obviously!) and so the spinners and the progress bar have a different frame to show.

To get a better feeling for this, do the following experiment:

 1. Run the command `textual console` in a terminal to open the Textual devtools console.
 2. Add a print statement like `print("Rendering from within spinner")` to the beginning of the method `Spinner.render` (from Rich).
 3. Add a print statement like `print("Rendering static")` to the beginning of the method `Static.render` (from Textual).
 4. Put a blank terminal and the devtools console side by side.
 5. Run the app: notice that you get a lot of both print statements.
 6. Hit the Pause button: the print statements stop.
 7. Move your mouse over a widget or two: you get a couple of print statements, one from the `Static.render` and another from the `Spinner.render`.

The result of steps 6 and 7 are shown below.
Notice that, in the beginning of the animation, the screen on the right shows some prints but is quiet because no more prints are coming in.
When the mouse enters the screen and starts going over widgets, the screen on the right gets new prints in pairs, first from `Static.render` (which Textual calls to render the widget) and then from `Spinner.render` because ultimately we need to know how the Spinner looks.

![](../images/spinners-and-pbs-in-textual/final-experiment.gif)

Now, at this point, I made another educated guess and deduced that progress bars work in the same way!
I still have to prove it, and I guess I will do so in another blog post, coming soon, where our spinner and progress bar widgets can be properly paused!

I will see you soon :wave:
````

## File: docs/blog/posts/steal-this-code.md
````markdown
---
draft: false
date: 2022-11-20
categories:
  - DevLog
authors:
  - willmcgugan
---

# Stealing Open Source code from Textual

I would like to talk about a serious issue in the Free and Open Source software world. Stealing code. You wouldn't steal a car would you?

<div class="video-wrapper">
<iframe width="auto" src="https://www.youtube.com/embed/HmZm8vNHBSU" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
</div>

But you *should* steal code from Open Source projects. Respect the license (you may need to give attribution) but stealing code is not like stealing a car. If I steal your car, I have deprived you of a car. If you steal my open source code, I haven't lost anything.

!!! warning

    I'm not advocating for *piracy*. Open source code gives you explicit permission to use it.


From my point of view, I feel like code has greater value when it has been copied / modified in another project.

There are a number of files and modules in [Textual](https://github.com/Textualize/textual) that could either be lifted as is, or wouldn't require much work to extract. I'd like to cover a few here. You might find them useful in your next project.

<!-- more -->

## Loop first / last

How often do you find yourself looping over an iterable and needing to know if an element is the first and/or last in the sequence? It's a simple thing, but I find myself needing this a *lot*, so I wrote some helpers in [_loop.py](https://github.com/Textualize/textual/blob/main/src/textual/_loop.py).

I'm sure there is an equivalent implementation on PyPI, but steal this if you need it.

Here's an example of use:

```python
for last, (y, line) in loop_last(enumerate(self.lines, self.region.y)):
    yield move_to(x, y)
    yield from line
    if not last:
        yield new_line
```

## LRU Cache

Python's [lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache) can be the one-liner that makes your code orders of magnitude faster. But it has a few gotchas.

The main issue is managing the lifetime of these caches. The decorator keeps a single global cache, which will keep a reference to every object in the function call. On an instance method that means you keep references to `self` for the lifetime of your app.

For a more flexibility you can use the [LRUCache](https://github.com/Textualize/textual/blob/main/src/textual/_cache.py) implementation from Textual. This uses essentially the same algorithm as the stdlib decorator, but it is implemented as a container.

Here's a quick example of its use. It works like a dictionary until you reach a maximum size. After that, new elements will kick out the element that was used least recently.

```python
>>> from textual._cache import LRUCache
>>> cache = LRUCache(maxsize=3)
>>> cache["foo"] = 1
>>> cache["bar"] = 2
>>> cache["baz"] = 3
>>> dict(cache)
{'foo': 1, 'bar': 2, 'baz': 3}
>>> cache["egg"] = 4
>>> dict(cache)
{'bar': 2, 'baz': 3, 'egg': 4}
```

In Textual, we use a [LRUCache](https://github.com/Textualize/textual/search?q=LRUCache) to store the results of rendering content to the terminal. For example, in a [datatable](https://twitter.com/search?q=%23textualdatatable&src=typed_query&f=live) it is too costly to render everything up front. So Textual renders only the lines that are currently visible on the "screen". The cache ensures that scrolling only needs to render the newly exposed lines, and lines that haven't been displayed in a while are discarded to save memory.


## Color

Textual has a [Color](https://github.com/Textualize/textual/blob/main/src/textual/color.py) class which could be extracted in to a module of its own.

The Color class can parse colors encoded in a variety of HTML and CSS formats. Color object support a variety of methods and operators you can use to manipulate colors, in a fairly natural way.

Here's some examples in the REPL.


```python
>>> from textual.color import Color
>>> color = Color.parse("lime")
>>> color
Color(0, 255, 0, a=1.0)
>>> color.darken(0.8)
Color(0, 45, 0, a=1.0)
>>> color + Color.parse("red").with_alpha(0.1)
Color(25, 229, 0, a=1.0)
>>> color = Color.parse("#12a30a")
>>> color
Color(18, 163, 10, a=1.0)
>>> color.css
'rgb(18,163,10)'
>>> color.hex
'#12A30A'
>>> color.monochrome
Color(121, 121, 121, a=1.0)
>>> color.monochrome.hex
'#797979'
>>> color.hsl
HSL(h=0.3246187363834423, s=0.8843930635838151, l=0.33921568627450976)
>>>
```

There are some very good color libraries in PyPI, which you should also consider using. But Textual's Color class is lean and performant, with no C dependencies.

## Geometry

This may be my favorite module in Textual: [geometry.py](https://github.com/Textualize/textual/blob/main/src/textual/geometry.py).

The geometry module contains a number of classes responsible for storing and manipulating 2D geometry. There is an `Offset` class which is a two dimensional point. A `Region` class which is a rectangular region defined by a coordinate and dimensions. There is a `Spacing` class which defines additional space around a region. And there is a `Size` class which defines the dimensions of an area by its width and height.

These objects are used by Textual's layout engine and compositor, which makes them the oldest and most thoroughly tested part of the project.

There's a lot going on in this module, but the docstrings are quite detailed and have unicode art like this to help explain things.

```
              cut_x ↓
          ┌────────┐ ┌───┐
          │        │ │   │
          │    0   │ │ 1 │
          │        │ │   │
  cut_y → └────────┘ └───┘
          ┌────────┐ ┌───┐
          │    2   │ │ 3 │
          └────────┘ └───┘
```

## You should steal our code

There is a lot going on in the [Textual Repository](https://github.com/Textualize/textual). Including a CSS parser, renderer, layout and compositing engine. All written in pure Python. Steal it with my blessing.
````

## File: docs/blog/posts/text-area-learnings.md
````markdown
---
draft: false
date: 2023-09-18
categories:
  - DevLog
authors:
  - darrenburns
title: "Things I learned while building Textual's TextArea"
---

# Things I learned building a text editor for the terminal

`TextArea` is the latest widget to be added to Textual's [growing collection](https://textual.textualize.io/widget_gallery/).
It provides a multi-line space to edit text, and features optional syntax highlighting for a selection of languages.

![text-area-welcome.gif](../images/text-area-learnings/text-area-welcome.gif)

Adding a `TextArea` to your Textual app is as simple as adding this to your `compose` method:

```python
yield TextArea()
```

Enabling syntax highlighting for a language is as simple as:

```python
yield TextArea(language="python")
```

Working on the `TextArea` widget for Textual taught me a lot about Python and my general
approach to software engineering. It gave me an appreciation for the subtle functionality behind
the editors we use on a daily basis — features we may not even notice, despite
some engineer spending hours perfecting it to provide a small boost to our development experience.

This post is a tour of some of these learnings.

<!-- more -->

## Vertical cursor movement is more than just `cursor_row++`

When you move the cursor vertically, you can't simply keep the same column index and clamp it within the line.
Editors should maintain the visual column offset where possible,
meaning they must account for double-width emoji (sigh 😔) and East-Asian characters.

![maintain_offset.gif](../images/text-area-learnings/maintain_offset.gif){ loading=lazy }

Notice that although the cursor is on column 11 while on line 1, it lands on column 6 when it
arrives at line 3.
This is because the 6th character of line 3 _visually_ aligns with the 11th character of line 1.


## Edits from other sources may move my cursor

There are two ways to interact with the `TextArea`:

1. You can type into it.
2. You can make API calls to edit the content in it.

In the example below, `Hello, world!\n` is repeatedly inserted at the start of the document via the
API.
Notice that this updates the location of my cursor, ensuring that I don't lose my place.

![text-area-api-insert.gif](../images/text-area-learnings/text-area-api-insert.gif){ loading=lazy }

This subtle feature should aid those implementing collaborative and multi-cursor editing.

This turned out to be one of the more complex features of the whole project, and went through several iterations before I was happy with the result.

Thankfully it resulted in some wonderful Tetris-esque whiteboards along the way!

<figure markdown>
  ![cursor_position_updating_via_api.png](../images/text-area-learnings/cursor_position_updating_via_api.png){ loading=lazy }
  <figcaption>A TetrisArea white-boarding session.</figcaption>
</figure>

Sometimes stepping away from the screen and scribbling on a whiteboard with your colleagues (thanks [Dave](https://fosstodon.org/@davep)!) is what's needed to finally crack a tough problem.

Many thanks to [David Brochart](https://mastodon.top/@davidbrochart) for sending me down this rabbit hole!

## Spending a few minutes running a profiler can be really beneficial

While building the `TextArea` widget I avoided heavy optimisation work that may have affected
readability or maintainability.

However, I did run a profiler in an attempt to detect flawed assumptions or mistakes which were
affecting the performance of my code.

I spent around 30 minutes profiling `TextArea`
using [pyinstrument](https://pyinstrument.readthedocs.io/en/latest/home.html), and the result was a
**~97%** reduction in the time taken to handle a key press.
What an amazing return on investment for such a minimal time commitment!


<figure markdown>
  ![text-area-pyinstrument.png](../images/text-area-learnings/text-area-pyinstrument.png){ loading=lazy }
  <figcaption>"pyinstrument -r html" produces this beautiful output.</figcaption>
</figure>

pyinstrument unveiled two issues that were massively impacting performance.

### 1. Reparsing highlighting queries on each key press

I was constructing a tree-sitter `Query` object on each key press, incorrectly assuming it was a
low-overhead call.
This query was completely static, so I moved it into the constructor ensuring the object was created
only once.
This reduced key processing time by around 94% - a substantial and very much noticeable improvement.

This seems obvious in hindsight, but the code in question was written earlier in the project and had
been relegated in my mind to "code that works correctly and will receive less attention from here on
out".
pyinstrument quickly brought this code back to my attention and highlighted it as a glaring
performance bug.

### 2. NamedTuples are slower than I expected

In Python, `NamedTuple`s are slow to create relative to `tuple`s, and this cost was adding up inside
an extremely hot loop which was instantiating a large number of them.
pyinstrument revealed that a large portion of the time during syntax highlighting was spent inside `NamedTuple.__new__`.

Here's a quick benchmark which constructs 10,000 `NamedTuple`s:

```toml
❯ hyperfine -w 2 'python sandbox/darren/make_namedtuples.py'
Benchmark 1: python sandbox/darren/make_namedtuples.py
  Time (mean ± σ):      15.9 ms ±   0.5 ms    [User: 12.8 ms, System: 2.5 ms]
  Range (min … max):    15.2 ms …  18.4 ms    165 runs
```

Here's the same benchmark using `tuple` instead:

```toml
❯ hyperfine -w 2 'python sandbox/darren/make_tuples.py'
Benchmark 1: python sandbox/darren/make_tuples.py
  Time (mean ± σ):       9.3 ms ±   0.5 ms    [User: 6.8 ms, System: 2.0 ms]
  Range (min … max):     8.7 ms …  12.3 ms    256 runs
```

Switching to `tuple` resulted in another noticeable increase in responsiveness.
Key-press handling time dropped by almost 50%!
Unfortunately, this change _does_ impact readability.
However, the scope in which these tuples were used was very small, and so I felt it was a worthy trade-off.


## Syntax highlighting is very different from what I expected

In order to support syntax highlighting, we make use of
the [tree-sitter](https://tree-sitter.github.io/tree-sitter/) library, which maintains a syntax tree
representing the structure of our document.

To perform highlighting, we follow these steps:

1. The user edits the document.
2. We inform tree-sitter of the location of this edit.
3. tree-sitter intelligently parses only the subset of the document impacted by the change, updating the tree.
4. We run a query against the tree to retrieve ranges of text we wish to highlight.
5. These ranges are mapped to styles (defined by the chosen "theme").
6. These styles to the appropriate text ranges when rendering the widget.

<figure markdown>
  ![text-area-theme-cycle.gif](../images/text-area-learnings/text-area-theme-cycle.gif){ loading=lazy }
  <figcaption>Cycling through a few of the builtin themes.</figcaption>
</figure>

Another benefit that I didn't consider before working on this project is that tree-sitter
parsers can also be used to highlight syntax errors in a document.
This can be useful in some situations - for example, highlighting mismatched HTML closing tags:

<figure markdown>
  ![text-area-syntax-error.gif](../images/text-area-learnings/text-area-syntax-error.gif){ loading=lazy }
  <figcaption>Highlighting mismatched closing HTML tags in red.</figcaption>
</figure>

Before building this widget, I was oblivious as to how we might approach syntax highlighting.
Without tree-sitter's incremental parsing approach, I'm not sure reasonable performance would have
been feasible.

## Edits are replacements

All single-cursor edits can be distilled into a single behaviour: `replace_range`.
This replaces a range of characters with some text.
We can use this one method to easily implement deletion, insertion, and replacement of text.

- Inserting text is replacing a zero-width range with the text to insert.
- Pressing backspace (delete left) is just replacing the character behind the cursor with an empty
  string.
- Selecting text and pressing delete is just replacing the selected text with an empty string.
- Selecting text and pasting is replacing the selected text with some other text.

This greatly simplified my initial approach, which involved unique implementations for inserting and
deleting.


## The line between "text area" and "VSCode in the terminal"

A project like this has no clear finish line.
There are always new features, optimisations, and refactors waiting to be made.

So where do we draw the line?

We want to provide a widget which can act as both a basic multiline text area that
anyone can drop into their app, yet powerful and extensible enough to act as the foundation
for a Textual-powered text editor.

Yet, the more features we add, the more opinionated the widget becomes, and the less that users
will feel like they can build it into their _own_ thing.
Finding the sweet spot between feature-rich and flexible is no easy task.

I don't think the answer is clear, and I don't believe it's possible to please everyone.

Regardless, I'm happy with where we've landed, and I'm really excited to see what people build using `TextArea` in the future!
````

## File: docs/blog/posts/textual-plotext.md
````markdown
---
draft: false
date: 2023-10-04
categories:
  - DevLog
title: "Announcing textual-plotext"
authors:
  - davep
---

# Announcing textual-plotext

It's no surprise that a common question on the [Textual Discord
server](https://discord.gg/Enf6Z3qhVr) is how to go about producing plots in
the terminal. A popular solution that has been suggested is
[Plotext](https://github.com/piccolomo/plotext). While Plotext doesn't
directly support Textual, it is [easy to use with
Rich](https://github.com/piccolomo/plotext/blob/master/readme/environments.md#rich)
and, because of this, we wanted to make it just as easy to use in your
Textual applications.

<!-- more -->

With this in mind we've created
[`textual-plotext`](https://github.com/Textualize/textual-plotext): a library
that provides a widget for using Plotext plots in your app. In doing this
we've tried our best to make it as similar as possible to using Plotext in a
conventional Python script.

Take this code from the [Plotext README](https://github.com/piccolomo/plotext#readme):

```python
import plotext as plt
y = plt.sin() # sinusoidal test signal
plt.scatter(y)
plt.title("Scatter Plot") # to apply a title
plt.show() # to finally plot
```

The Textual equivalent of this (including everything needed to make this a
fully-working Textual application) is:

```python
from textual.app import App, ComposeResult

from textual_plotext import PlotextPlot

class ScatterApp(App[None]):

    def compose(self) -> ComposeResult:
        yield PlotextPlot()

    def on_mount(self) -> None:
        plt = self.query_one(PlotextPlot).plt
        y = plt.sin() # sinusoidal test signal
        plt.scatter(y)
        plt.title("Scatter Plot") # to apply a title

if __name__ == "__main__":
    ScatterApp().run()
```

When run the result will look like this:

![Scatter plot in a Textual application](/blog/images/textual-plotext/scatter.png)

Aside from a couple of the more far-out plot types[^1] you should find that
everything you can do with Plotext in a conventional script can also be done
in a Textual application.

Here's a small selection of screenshots from a demo built into the library,
each of the plots taken from the Plotext README:

![Sample from the library demo application](/blog/images/textual-plotext/demo1.png)

![Sample from the library demo application](/blog/images/textual-plotext/demo2.png)

![Sample from the library demo application](/blog/images/textual-plotext/demo3.png)

![Sample from the library demo application](/blog/images/textual-plotext/demo4.png)

A key design goal of this widget is that you can develop your plots so that
the resulting code looks very similar to that in the Plotext documentation.
The core difference is that, where you'd normally import the `plotext`
module `as plt` and then call functions via `plt`, you instead use the `plt`
property made available by the widget.

You don't even need to call the `build` or `show` functions as
`textual-plotext` takes care of this for you. You can see this in action in
the scatter code shown earlier.

Of course, moving any existing plotting code into your Textual app means you
will need to think about how you get the data and when and where you build
your plot. This might be where the [Textual worker
API](https://textual.textualize.io/guide/workers/) becomes useful.

We've included a longer-form example application that shows off the glorious
Scottish weather we enjoy here at Textual Towers, with [an application that
uses workers to pull down weather data from a year ago and plot
it](https://github.com/Textualize/textual-plotext/blob/main/examples/textual_towers_weather.py).

![The Textual Towers weather history app](/blog/images/textual-plotext/weather.png)

If you are an existing Plotext user who wants to turn your plots into full
terminal applications, we think this will be very familiar and accessible.
If you're a Textual user who wants to add plots to your application, we
think Plotext is a great library for this.

If you have any questions about this, or anything else to do with Textual,
feel free to come and join us on our [Discord
server](https://discord.gg/Enf6Z3qhVr) or in our [GitHub
discussions](https://github.com/Textualize/textual/discussions).

[^1]: Right now there's no [animated
    gif](https://github.com/piccolomo/plotext/blob/master/readme/image.md#gif-plot)
    or
    [video](https://github.com/piccolomo/plotext/blob/master/readme/video.md)
    support.
````

## File: docs/blog/posts/textual-serve-files.md
````markdown
---
draft: false 
date: 2024-09-08
categories:
  - DevLog
authors:
  - darrenburns
title: "Towards Textual Web Applications"
---

In this post we'll look at some new functionality available in Textual apps accessed via a browser and how it helps provide a more equal experience across platforms.

<!-- more -->

## What is `textual-serve`?

[`textual-serve`](https://github.com/Textualize/textual-serve) is an open source project which allows you to serve and access your Textual app via a browser. The Textual app runs on a machine/server under your control, and communicates with the browser via a protocol which runs over websocket. End-users interacting with the app via their browser do not have access to the machine the application is running on via their browser, only the running Textual app.

For example, you could install [`harlequin`](https://github.com/tconbeer/harlequin) (a terminal-based SQL IDE)  on a machine on your network, run it using `textual-serve`, and then share the URL with others. Anyone with the URL would then be able to use `harlequin` to query databases accessible from that server. Or, you could deploy [`posting`](https://github.com/darrenburns/posting) (a terminal-based API client) on a server, and provide your colleagues with the URL, allowing them to quickly send HTTP requests *from that server*, right from within their browser.

<figure markdown>
![posting running in a browser](../images/textual-serve-files/posting-textual-serve.png)
  <figcaption>Accessing an instance of Posting via a web browser.</figcaption>
</figure>

## Providing an equal experience

While you're interacting with the Textual app using your web browser, it's not *running* in your browser. It's running on the machine you've installed it on, similar to typical server driven web app. This creates some interesting challenges for us if we want to provide an equal experience across browser and terminal.

A Textual app running in the browser is inherently more accessible to non-technical users, and we don't want to limit access to important functionality for those users. We also don't want Textual app developers to have to repeatedly check "is the the end-user using a browser or a terminal?".

To solve this, we've created APIs which allow developers to add web links to their apps and deliver files to end-users in a platform agnostic way. The goal of these APIs is to allow developers to write applications knowing that they'll provide a sensible user experience in both terminals and web browsers without any extra effort.

## Opening web links

The ability to click on and open links is a pretty fundamental expectation when interacting with an app running in your browser.

Python offers a [`webbrowser`](https://docs.python.org/3/library/webbrowser.html) module which allows you to open a URL in a web browser. When a Textual app is running in a terminal, a simple call to this module does exactly what we'd expect.

If the app is being used via a browser however, the `webbrowser` module would attempt to open the browser on the machine the app is being served from. This is clearly not very useful to the end-user!

To solve this, we've added a new method to Textual: [`App.open_url`](https://textual.textualize.io/api/app/#textual.app.App.open_url). When running in the terminal, this will use `webbrowser` to open the URL as you would expect. 

When the Textual app is being served and used via the browser however, the running app will inform `textual-serve`, which will in turn tell the browser via websocket that the end-user is requesting to open a link, which will then be opened in their browser - just like a normal web link.

The developer doesn't need to think about *where* their application might be running. By using `open_url`, Textual will ensure that end-users get the experience they expect.

## Saving files to disk

When running a Textual app in the terminal, getting a file into the hands of the end user is relatively simple - you could just write it to disk and notify them of the location, or perhaps open their `$EDITOR` with the content loaded into it. Given they're using a terminal, we can also make an assumption that the end-user is at least some technical knowledge.

Run that same app in the browser however, and we have a problem. If you simply write the file to disk, the end-user would need to be able to access the machine the app is running on and navigate the file system in order to retrieve it. This may not be possible: they may not be permitted to access the machine, or they simply may not know how!

The new [`App.deliver_text`][textual.app.App.deliver_text] and [`App.deliver_binary`][textual.app.App.deliver_binary] methods are designed to let developers get files into the hands of end users, regardless of whether the app is being accessed via the browser or a terminal.

When accessing a Textual app using a terminal, these methods will write a file to disk, and notify the `App` when the write is complete.

In the browser, however, a download will be initiated and the file will be streamed via an ephemeral (one-time) download URL from the server that the Textual app is running on to the end-user's browser. If the app developer wishes, they can specify a custom file name, MIME type, and even whether the browser should attempt to open the file in a new tab or be downloaded.

## How it works

Input in Textual apps is handled, at the lowest level, by "driver" classes. We have different drivers for Linux and Windows, and also one for handling apps being served via web. 

When running in a terminal, the Windows/Linux drivers will read `stdin`, and parse incoming ANSI escape sequences sent by the terminal emulator as a result of mouse movement or keyboard interaction. The driver translates these escape sequences into Textual "Events", which are sent on to your application's message queue for asynchronous handling.

For apps being served over the web, things are again a bit more complex. Interaction between the application and the end-user happens inside the browser - with a terminal rendered using [`xterm.js`](https://xtermjs.org/) - the same front-end terminal engine used in VS Code. `xterm.js` fills the roll of a terminal emulator here, translating user interactions into ANSI escape codes on `stdin`.

These escape codes are sent through websocket to `textual-serve` and then piped to the `stdin` stream of the Textual app which is running as a subprocess. Inside the Textual app, these can be processed and converted into events as normal by Textual's web driver.

A Textual app also writes to the `stdout` stream, which is then read by your emulator and translated into visual output. When running on the web, this stdout is also sent over websocket to the end-user's browser, and `xterm.js` takes care of rendering.

Although most of the data flowing back and forth from browser to Textual app is going to be ANSI escape sequences, we can in reality send anything we wish.

To support file delivery we updated our protocol to allow applications to signal that a file is "ready" for delivery when one of the new "deliver file" APIs is called. An ephemeral, single-use, download link is then generated and sent to the browser via websocket. The front-end of `textual-serve` opens this URL and the file is streamed to the browser.

This streaming process involves continuous delivery of encoded chunks of the file (using a variation of [Bencode](https://en.wikipedia.org/wiki/Bencode) - the encoding used by [BitTorrent](https://en.wikipedia.org/wiki/BitTorrent)) from the Textual app process to `textual-serve`, and then through to the end-user via the download URL.

![textual-serve-overview](../images/textual-serve-files/textual-serve-overview.png)

## The result

These new APIs close an important feature gap and give developers the option to build apps that can accessed via terminals or browsers without worrying that those on the web might miss out on important functionality!

## Found this interesting?

Join our [Discord server](https://discord.gg/Enf6Z3qhVr) to chat to myself and other Textual developers.
````

## File: docs/blog/posts/textual-web.md
````markdown
---
draft: false
date: 2023-09-06
categories:
  - News
title: "What is Textual Web?"
authors:
  - willmcgugan
---

# What is Textual Web?

If you know us, you will know that we are the team behind [Rich](https://github.com/Textualize/rich) and [Textual](https://github.com/Textualize/textual) &mdash; two popular Python libraries that work magic in the terminal.

!!! note

    Not to mention [Rich-CLI](https://github.com/Textualize/rich-cli), [Trogon](https://github.com/Textualize/trogon), and [Frogmouth](https://github.com/Textualize/frogmouth)

Today we are adding one project more to that lineup: [textual-web](https://github.com/Textualize/textual-web).


<!-- more -->

Textual Web takes a Textual-powered TUI and turns it in to a web application.
Here's a video of that in action:

<div class="video-wrapper">
<iframe width="auto" src="https://www.youtube.com/embed/A8k8TD7_wg0" title="Textual Web in action" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

With the `textual-web` command you can publish any Textual app on the web, making it available to anyone you send the URL to.
This works without creating a socket server on your machine, so you won't have to configure firewalls and ports to share your applications.

We're excited about the possibilities here.
Textual web apps are fast to spin up and tear down, and they can run just about anywhere that has an outgoing internet connection.
They can be built by a single developer without any experience with a traditional web stack.
All you need is proficiency in Python and a little time to read our [lovely docs](https://textual.textualize.io/).

Future releases will expose more of the Web platform APIs to Textual apps, such as notifications and file system access.
We plan to do this in a way that allows the same (Python) code to drive those features.
For instance, a Textual app might save a file to disk in a terminal, but offer to download it in the browser.

Also in the pipeline is [PWA](https://en.wikipedia.org/wiki/Progressive_web_app) support, so you can build terminal apps, web apps, and desktop apps with a single codebase.

Textual Web is currently in a public beta. Join our [Discord server](https://discord.gg/Enf6Z3qhVr) if you would like to help us test, or if you have any questions.
````

## File: docs/blog/posts/to-tui-or-not-to-tui.md
````markdown
---
draft: false
date: 2023-06-06
categories:
  - DevLog
title: "To TUI or not to TUI"
authors:
  - willmcgugan
---

# To TUI or not to TUI

Tech moves pretty fast.
If you don’t stop and look around once in a while, you could miss it.
And yet some technology feels like it has been around forever.

Terminals are one of those forever-technologies.

<!-- more -->

My interest is in Text User Interfaces:  interactive apps that run within a terminal.
I spend lot of time thinking about where TUIs might fit within the tech ecosystem, and how much more they could be doing for developers.
Hardly surprising, since that is what we do at [Textualize](https://textual.textualize.io/).

Recently I had the opportunity to test how new TUI projects would be received.
You can consider these to be "testing the water", and hopefully representative of TUI apps in general.

## The projects

In April we took a break from building [Textual](https://github.com/Textualize/textual), to building apps *with* Textual.
We had three ideas to work on, and three devs to do the work.
One idea we parked for later.
The other two were so promising we devoted more time to them.
Both projects took around three developer-weeks to build, which also included work on Textual itself and standard duties for responding to issues / community requests.
We released them in May.

The first project was [Frogmouth](https://github.com/Textualize/frogmouth), a Markdown browser.
I think this TUI does better than the equivalent web experience in many ways.
The only notable missing feature is images, and that will happen before too long.

Here's a screenshot:

<div>
--8<-- "docs/blog/images/frogmouth.svg"
</div>


!!! info

    Quick aside about these "screenshots", because its a common ask.
    They aren't true screenshots, but rather SVGs exported by Textual.

We posted Frogmouth on Hacker News and Reddit on a Sunday morning (US time).
A day later, it had 1,000 stars and lots of positive feedback.

The second project was [Trogon](https://github.com/Textualize/trogon), a library this time.
Trogon automatically creates a TUI for command line apps.
Same deal: we released it on a Sunday morning, and it reached 1K stars even quicker than Frogmouth.

<div>
--8<-- "docs/blog/images/trogon.svg"
</div>

Both of these projects are very young, but off to a great start.
I'm looking forward to seeing how far we can taken them.

![Star history for Trogon and Frogmouth](../images/star-history-trogon-frogmouth.png)

## Wrapping up

With previous generations of software, TUIs have required a high degree of motivation to build.
That has changed with the work that we (and others) have been doing.
A TUI can be a powerful and maintainable piece of software which works as a standalone project, or as a value-add to an existing project.

As a forever-technology, a TUI is a safe bet.

## Discord

Want to discuss this post with myself or other Textualize devs?
Join our [Discord server](https://discord.gg/Enf6Z3qhVr)...
````

## File: docs/blog/posts/toolong-retrospective.md
````markdown
---
draft: false
date: 2024-02-11
categories:
  - DevLog
authors:
  - willmcgugan
---

# File magic with the Python standard library

I recently published [Toolong](https://github.com/textualize/toolong), an app for viewing log files.
There were some interesting technical challenges in building Toolong that I'd like to cover in this post.

<!-- more -->

!!! note "Python is awesome"

    This isn't specifically [Textual](https://github.com/textualize/textual/) related. These techniques could be employed in any Python project.

These techniques aren't difficult, and shouldn't be beyond anyone with an intermediate understanding of Python.
They are the kind of "if you know it you know it" knowledge that you may not need often, but can make a massive difference when you do!

## Opening large files

If you were to open a very large text file (multiple gigabyte in size) in an editor, you will almost certainly find that it takes a while. You may also find that it doesn't load at all because you don't have enough memory, or it disables features like syntax highlighting.

This is because most app will do something analogous to this:

```python
with open("access.log", "rb") as log_file:
    log_data = log_file.read()
```

All the data is read in to memory, where it can be easily processed.
This is fine for most files of a reasonable size, but when you get in to the gigabyte territory the read and any additional processing will start to use a significant amount of time and memory.

Yet Toolong can open a file of *any* size in a second or so, with syntax highlighting.
It can do this because it doesn't need to read the entire log file in to memory.
Toolong opens a file and reads only the portion of it required to display whatever is on screen at that moment.
When you scroll around the log file, Toolong reads the data off disk as required -- fast enough that you may never even notice it.

### Scanning lines

There is an additional bit of work that Toolong has to do up front in order to show the file.
If you open a large file you may see a progress bar and a message about "scanning".

Toolong needs to know where every line starts and ends in a log file, so it can display a scrollbar bar and allow the user to navigate lines in the file.
In other words it needs to know the offset of every new line (`\n`) character within the file.

This isn't a hard problem in itself.
You might have imagined a loop that reads a chunk at a time and searches for new lines characters.
And that would likely have worked just fine, but there is a bit of magic in the Python standard library that can speed that up.

The [mmap](https://docs.python.org/3/library/mmap.html) module is a real gem for this kind of thing.
A *memory mapped file* is an OS-level construct that *appears* to load a file instantaneously.
In Python you get an object which behaves like a `bytearray`, but loads data from disk when it is accessed.
The beauty of this module is that you can work with files in much the same way as if you had read the entire file in to memory, while leaving the actual reading of the file to the OS.

Here's the method that Toolong uses to scan for line breaks.
Forgive the micro-optimizations, I was going for raw execution speed here.

```python
    def scan_line_breaks(
        self, batch_time: float = 0.25
    ) -> Iterable[tuple[int, list[int]]]:
        """Scan the file for line breaks.

        Args:
            batch_time: Time to group the batches.

        Returns:
            An iterable of tuples, containing the scan position and a list of offsets of new lines.
        """
        fileno = self.fileno
        size = self.size
        if not size:
            return
        log_mmap = mmap.mmap(fileno, size, prot=mmap.PROT_READ)
        rfind = log_mmap.rfind
        position = size
        batch: list[int] = []
        append = batch.append
        get_length = batch.__len__
        monotonic = time.monotonic
        break_time = monotonic()

        while (position := rfind(b"\n", 0, position)) != -1:
            append(position)
            if get_length() % 1000 == 0 and monotonic() - break_time > batch_time:
                break_time = monotonic()
                yield (position, batch)
                batch = []
                append = batch.append
        yield (0, batch)
        log_mmap.close()
```

This code runs in a thread (actually a [worker](https://textual.textualize.io/guide/workers/)), and will generate line breaks in batches. Without batching, it risks slowing down the UI with millions of rapid events.

It's fast because most of the work is done in `rfind`, which runs at C speed, while the OS reads from the disk.

## Watching a file for changes

Toolong can tail files in realtime.
When something appends to the file, it will be read and displayed virtually instantly.
How is this done?

You can easily *poll* a file for changes, by periodically querying the size or timestamp of a file until it changes.
The downside of this is that you don't get notified immediately if a file changes between polls.
You could poll at a very fast rate, but if you were to do that you would end up burning a lot of CPU for no good reason.

There is a very good solution for this in the standard library.
The [selectors](https://docs.python.org/3/library/selectors.html) module is typically used for working with sockets (network data), but can also work with files (at least on macOS and Linux).

!!! info "Software developers are an unimaginative bunch when it comes to naming things"

    Not to be confused with CSS [selectors](https://textual.textualize.io/guide/CSS/#selectors)!    

The selectors module can tell you precisely when a file can be read.
It can do this very efficiently, because it relies on the OS to tell us when a file can be read, and doesn't need to poll.

You register a file with a `Selector` object, then call `select()` which returns as soon as there is new data available for reading.

See [watcher.py](https://github.com/Textualize/toolong/blob/main/src/toolong/watcher.py) in Toolong, which runs a thread to monitors files for changes with a selector.

!!! warning "Addendum"

    So it turns out that watching regular files for changes with selectors only works with `KqueueSelector` which is the default on macOS.
    Disappointingly, the Python docs aren't clear on this.
    Toolong will use a polling approach where this selector is unavailable.

## Textual learnings

This project was a chance for me to "dogfood" Textual.
Other Textual devs have build some cool projects ([Trogon](https://github.com/Textualize/trogon) and [Frogmouth](https://github.com/Textualize/frogmouth)), but before Toolong I had only ever written example apps for docs.

I paid particular attention to Textual error messages when working on Toolong, and improved many of them in Textual.
Much of what I improved were general programming errors, and not Textual errors per se.
For instance, if you forget to call `super()` on a widget constructor, Textual used to give a fairly cryptic error.
It's a fairly common gotcha, even for experience devs, but now Textual will detect that and tell you how to fix it.

There's a lot of other improvements which I thought about when working on this app.
Mostly quality of life features that will make implementing some features more intuitive.
Keep an eye out for those in the next few weeks.

## Found this interesting?

If you would like to talk about this post or anything Textual related, join us on the [Discord server](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/blog/index.md
````markdown
# Textual Blog
````

## File: docs/css_types/_template.md
````markdown
<!-- Template file for a Textual CSS type reference page. -->

# &lt;type-name&gt;

<!-- Short description of the type. -->

## Syntax


<!--
For a simple type like <integer>:

Describe the type in a short paragraph with an absolute link to the type page.
E.g., “The [`<my-type>`](/css_types/my_type) type is such and such with sprinkles on top.”
-->

<!--
For a type with many different values like <color>:

Introduce the type with a link to [`<my-type>`](/css_types/my_type).
Then, a bullet list with the variants accepted:

 - you can create this type with X Y Z;
 - you can also do A B C; and
 - also use D E F.
-->

<!--
For a type that accepts specific options like <border>:

Add a sentence and a table. Consider ordering values in alphabetical order if there is no other obvious ordering. See below:

The [`<my-type>`](/css_types/my_type) type can take any of the following values:

| Value         | Description                                   |
|---------------|-----------------------------------------------|
| `abc`         | Describe here.                                |
| `other val`   | Describe this one also.                       |
| `value three` | Please use full stops.                        |
| `zyx`         | Describe the value without assuming any rule. |
-->


## Examples

### CSS

<!--
Include a good variety of examples.
If the type has many different syntaxes, cover all of them.
Add comments when needed/if helpful.
-->

```css
.some-class {
    rule: type-value-1;
    rule: type-value-2;
    rule: type-value-3;
}
```

### Python

<!-- Same examples as above. -->

```py
widget.styles.rule = type_value_1
widget.styles.rule = type_value_2
widget.styles.rule = type_value_3
```
````

## File: docs/css_types/border.md
````markdown
# &lt;border&gt;

The `<border>` CSS type represents a border style.

## Syntax

The [`<border>`](./border.md) type can take any of the following values:

| Border type | Description                                              |
|-------------|----------------------------------------------------------|
| `ascii`     | A border with plus, hyphen, and vertical bar characters. |
| `blank`     | A blank border (reserves space for a border).            |
| `dashed`    | Dashed line border.                                      |
| `double`    | Double lined border.                                     |
| `heavy`     | Heavy border.                                            |
| `hidden`    | Alias for "none".                                        |
| `hkey`      | Horizontal key-line border.                              |
| `inner`     | Thick solid border.                                      |
| `none`      | Disabled border.                                         |
| `outer`     | Solid border with additional space around content.       |
| `panel`     | Solid border with thick top.                             |
| `round`     | Rounded corners.                                         |
| `solid`     | Solid border.                                            |
| `tall`      | Solid border with additional space top and bottom.       |
| `thick`     | Border style that is consistently thick across edges.    |
| `vkey`      | Vertical key-line border.                                |
| `wide`      | Solid border with additional space left and right.       |

## Border command

The `textual` CLI has a subcommand which will let you explore the various border types interactively, when applied to the CSS rule [`border`](../styles/border.md):

```
textual borders
```

## Examples

### CSS

```css
#container {
    border: heavy red;
}

#heading {
    border-bottom: solid blue;
}
```

### Python

```py
widget.styles.border = ("heavy", "red")
widget.styles.border_bottom = ("solid", "blue")
```
````

## File: docs/css_types/color.md
````markdown
# &lt;color&gt;

The `<color>` CSS type represents a color.

!!! warning

    Not to be confused with the [`color`](../styles/color.md) CSS rule to set text color.

## Syntax

A [`<color>`](./color.md) should be in one of the formats explained in this section.
A bullet point summary of the formats available follows:

 - a recognised [named color](#named-colors) (e.g., `red`);
 - a 3 or 6 hexadecimal digit number representing the [RGB values](#hex-rgb-value) of the color (e.g., `#F35573`);
 - a 4 or 8 hexadecimal digit number representing the [RGBA values](#hex-rgba-value) of the color (e.g., `#F35573A0`);
 - a color description in the RGB system, [with](#rgba-description) or [without](#rgb-description) opacity (e.g., `rgb(23, 78, 200)`);
 - a color description in the HSL system, [with](#hsla-description) or [without](#hsl-description) opacity (e.g., `hsl(290, 70%, 80%)`);

[Textual's default themes](../guide/design.md) also provide many CSS variables with colors that can be used out of the box.

### Named colors

A named color is a [`<name>`](./name.md) that Textual recognises.
Below, you can find a (collapsed) list of all of the named colors that Textual recognises, along with their hexadecimal values, their RGB values, and a visual sample.

<details>
<summary>All named colors available.</summary>

```{.rich columns="80" title="colors"}
from textual._color_constants import COLOR_NAME_TO_RGB
from textual.color import Color
from rich.table import Table
from rich.text import Text
table = Table("Name", "hex", "RGB", "Color", expand=True, highlight=True)

for name, triplet in sorted(COLOR_NAME_TO_RGB.items()):
    if len(triplet) != 3:
        continue
    color = Color(*triplet)
    r, g, b = triplet
    table.add_row(
        f'"{name}"',
        Text(f"{color.hex}", "bold green"),
        f"rgb({r}, {g}, {b})",
        Text("                    ", style=f"on rgb({r},{g},{b})")
    )
output = table
```

</details>

### Hex RGB value

The hexadecimal RGB format starts with an octothorpe `#` and is then followed by 3 or 6 hexadecimal digits: `0123456789ABCDEF`.
Casing is ignored.

 - If 6 digits are used, the format is `#RRGGBB`:
   - `RR` represents the red channel;
   - `GG` represents the green channel; and
   - `BB` represents the blue channel.
 - If 3 digits are used, the format is `#RGB`.

In a 3 digit color, each channel is represented by a single digit which is duplicated when converting to the 6 digit format.
For example, the color `#A2F` is the same as `#AA22FF`.

### Hex RGBA value

This is the same as the [hex RGB value](#hex-rgb-value), but with an extra channel for the alpha component (that sets opacity).

 - If 8 digits are used, the format is `#RRGGBBAA`, equivalent to the format `#RRGGBB` with two extra digits for opacity.
 - If 4 digits are used, the format is `#RGBA`, equivalent to the format `#RGB` with an extra digit for opacity.

### `rgb` description

The `rgb` format description is a functional description of a color in the RGB color space.
This description follows the format `rgb(red, green, blue)`, where `red`, `green`, and `blue` are decimal integers between 0 and 255.
They represent the value of the channel with the same name.

For example, `rgb(0, 255, 32)` is equivalent to `#00FF20`.

### `rgba` description

The `rgba` format description is the same as the `rgb` with an extra parameter for opacity, which should be a value between `0` and `1`.

For example, `rgba(0, 255, 32, 0.5)` is the color `rgb(0, 255, 32)` with 50% opacity.

### `hsl` description

The `hsl` format description is a functional description of a color in the HSL color space.
This description follows the format `hsl(hue, saturation, lightness)`, where

 - `hue` is a float between 0 and 360;
 - `saturation` is a percentage between `0%` and `100%`; and
 - `lightness` is a percentage between `0%` and `100%`.

For example, the color `#00FF20` would be represented as `hsl(128, 100%, 50%)` in the HSL color space.

### `hsla` description

The `hsla` format description is the same as the `hsl` with an extra parameter for opacity, which should be a value between `0` and `1`.

For example, `hsla(128, 100%, 50%, 0.5)` is the color `hsl(128, 100%, 50%)` with 50% opacity.

## Examples

### CSS

```css
Header {
    background: red;           /* Color name */
}

.accent {
    color: $accent;            /* Textual variable */
}

#footer {
    tint: hsl(300, 20%, 70%);  /* HSL description */
}
```

### Python

In Python, rules that expect a `<color>` can also accept an instance of the type [`Color`][textual.color.Color].

```py
# Mimicking the CSS syntax
widget.styles.background = "red"           # Color name
widget.styles.color = "$accent"            # Textual variable
widget.styles.tint = "hsl(300, 20%, 70%)"  # HSL description

from textual.color import Color
# Using a Color object directly...
color = Color(16, 200, 45)
# ... which can also parse the CSS syntax
color = Color.parse("#A8F")
```
````

## File: docs/css_types/hatch.md
````markdown
# &lt;hatch&gt;

The `<hatch>` CSS type represents a character used in the [hatch](../styles/hatch.md) rule.

## Syntax

| Value        | Description                    |
| ------------ | ------------------------------ |
| `cross`      | A diagonal crossed line.       |
| `horizontal` | A horizontal line.             |
| `left`       | A left leaning diagonal line.  |
| `right`      | A right leaning diagonal line. |
| `vertical`   | A vertical line.               |


## Examples

### CSS


```css
.some-class {
    hatch: cross green;
}
```

### Python

```py
widget.styles.hatch = ("cross", "red")
```
````

## File: docs/css_types/horizontal.md
````markdown
# &lt;horizontal&gt;

The `<horizontal>` CSS type represents a position along the horizontal axis.

## Syntax

The [`<horizontal>`](./horizontal.md) type can take any of the following values:

| Value            | Description                                  |
| ---------------- | -------------------------------------------- |
| `center`         | Aligns in the center of the horizontal axis. |
| `left` (default) | Aligns on the left of the horizontal axis.   |
| `right`          | Aligns on the right of the horizontal axis.  |

## Examples

### CSS

```css
.container {
    align-horizontal: right;
}
```

### Python

```py
widget.styles.align_horizontal = "right"
```
````

## File: docs/css_types/index.md
````markdown
# CSS Types

CSS types define the values that Textual CSS styles accept.

CSS types will be linked from within the [styles reference](../styles/index.md) in the "Formal Syntax" section of each style.
The CSS types will be denoted by a keyword enclosed by angle brackets `<` and `>`.

For example, the style [`align-horizontal`](../styles/align.md) references the CSS type [`<horizontal>`](./horizontal.md):

--8<-- "docs/snippets/syntax_block_start.md"
align-horizontal: <a href="./horizontal/">&lt;horizontal&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"
````

## File: docs/css_types/integer.md
````markdown
# &lt;integer&gt;

The `<integer>` CSS type represents an integer number.

## Syntax

An [`<integer>`](./integer.md) is any valid integer number like `-10` or `42`.

!!! note

    Some CSS rules may expect an `<integer>` within certain bounds. If that is the case, it will be noted in that rule.

## Examples

### CSS

```css
.classname {
    offset: 10 -20
}
```

### Python

In Python, a rule that expects a CSS type `<integer>` will expect a value of the type `int`:

```py
widget.styles.offset = (10, -20)
```
````

## File: docs/css_types/keyline.md
````markdown
# &lt;keyline&gt;

The `<keyline>` CSS type represents a line style used in the [keyline](../styles/keyline.md) rule.


## Syntax

| Value    | Description                |
| -------- | -------------------------- |
| `none`   | No line (disable keyline). |
| `thin`   | A thin line.               |
| `heavy`  | A heavy (thicker) line.    |
| `double` | A double line.             |

## Examples

### CSS

```css
Vertical {
    keyline: thin green;
}
```

### Python

```py
# A tuple of <keyline> and color
widget.styles.keyline = ("thin", "green")
```
````

## File: docs/css_types/name.md
````markdown
# &lt;name&gt;

The `<name>` type represents a sequence of characters that identifies something.

## Syntax

A [`<name>`](./name.md) is any non-empty sequence of characters:

 - starting with a letter `a-z`, `A-Z`, or underscore `_`; and
 - followed by zero or more letters `a-zA-Z`, digits `0-9`, underscores `_`, and hiphens `-`.

## Examples

### CSS

```css
Screen {
    layers: onlyLetters Letters-and-hiphens _lead-under letters-1-digit;
}
```

### Python

```py
widget.styles.layers = "onlyLetters Letters-and-hiphens _lead-under letters-1-digit"
```
````

## File: docs/css_types/number.md
````markdown
# &lt;number&gt;

The `<number>` CSS type represents a real number, which can be an integer or a number with a decimal part (akin to a `float` in Python).

## Syntax

A [`<number>`](./number.md) is an [`<integer>`](./integer.md), optionally followed by the decimal point `.` and a decimal part composed of one or more digits.

## Examples

### CSS

```css
Grid {
    grid-size: 3 6  /* Integers are numbers */
}

.translucid {
    opacity: 0.5    /* Numbers can have a decimal part */
}
```

### Python

In Python, a rule that expects a CSS type `<number>` will accept an `int` or a `float`:

```py
widget.styles.grid_size = (3, 6)  # Integers are numbers
widget.styles.opacity = 0.5       # Numbers can have a decimal part
```
````

## File: docs/css_types/overflow.md
````markdown
# &lt;overflow&gt;

The `<overflow>` CSS type represents overflow modes.

## Syntax

The [`<overflow>`](./overflow.md) type can take any of the following values:

| Value    | Description                            |
|----------|----------------------------------------|
| `auto`   | Determine overflow mode automatically. |
| `hidden` | Don't overflow.                        |
| `scroll` | Allow overflowing.                     |

## Examples

### CSS

```css
#container {
    overflow-y: hidden;  /* Don't overflow */
}
```

### Python

```py
widget.styles.overflow_y = "hidden"  # Don't overflow
```
````

## File: docs/css_types/percentage.md
````markdown
# &lt;percentage&gt;

The `<percentage>` CSS type represents a percentage value.
It is often used to represent values that are relative to the parent's values.

!!! warning

    Not to be confused with the [`<scalar>`](./scalar.md) type.

## Syntax

A [`<percentage>`](./percentage.md) is a [`<number>`](./number.md) followed by the percent sign `%` (without spaces).
Some rules may clamp the values between `0%` and `100%`.

## Examples

### CSS

```css
#footer {
    /* Integer followed by % */
    color: red 70%;

    /* The number can be negative/decimal, although that may not make sense */
    offset: -30% 12.5%;
}
```

### Python

```py
# Integer followed by %
widget.styles.color = "red 70%"

# The number can be negative/decimal, although that may not make sense
widget.styles.offset = ("-30%", "12.5%")
```
````

## File: docs/css_types/position.md
````markdown
# &lt;position&gt;

The `<position>` CSS type defines how the the `offset` rule is applied..


## Syntax

A [`<position>`](./position.md) may be any of the following values:

| Value      | Alignment type                                               |
| ---------- | ------------------------------------------------------------ |
| `relative` | Offset is applied to widgets default position.               |
| `absolute` | Offset is applied to the origin (top left) of its container. |

## Examples

### CSS

```css
Label {
    position: absolute;
    offset: 10 5;
}
```

### Python

```py
widget.styles.position = "absolute"
widget.styles.offset = (10, 5)
```
````

## File: docs/css_types/scalar.md
````markdown
# &lt;scalar&gt;

The `<scalar>` CSS type represents a length.
It can be a [`<number>`](./number.md) and a unit, or the special value `auto`.
It is used to represent lengths, for example in the [`width`](../styles/width.md) and [`height`](../styles/height.md) rules.

!!! warning

    Not to be confused with the [`<number>`](./number.md) or [`<percentage>`](./percentage.md) types.

## Syntax

A [`<scalar>`](./scalar.md) can be any of the following:

 - a fixed number of cells (e.g., `10`);
 - a fractional proportion relative to the sizes of the other widgets (e.g., `1fr`);
 - a percentage relative to the container widget (e.g., `50%`);
 - a percentage relative to the container width/height (e.g., `25w`/`75h`);
 - a percentage relative to the viewport width/height (e.g., `25vw`/`75vh`); or
 - the special value `auto` to compute the optimal size to fit without scrolling.

A complete reference table and detailed explanations follow.
You can [skip to the examples](#examples).

| Unit symbol | Unit            | Example | Description                                                 |
|-------------|-----------------|---------|-------------------------------------------------------------|
| `""`        | Cell            | `10`    | Number of cells (rows or columns).                          |
| `"fr"`      | Fraction        | `1fr`   | Specifies the proportion of space the widget should occupy. |
| `"%"`       | Percent         | `75%`   | Length relative to the container widget.                    |
| `"w"`       | Width           | `25w`   | Percentage relative to the width of the container widget.   |
| `"h"`       | Height          | `75h`   | Percentage relative to the height of the container widget.  |
| `"vw"`      | Viewport width  | `25vw`  | Percentage relative to the viewport width.                  |
| `"vh"`      | Viewport height | `75vh`  | Percentage relative to the viewport height.                 |
| -           | Auto            | `auto`  | Tries to compute the optimal size to fit without scrolling. |

### Cell

The number of cells is the only unit for a scalar that is _absolute_.
This can be an integer or a float but floats are truncated to integers.

If used to specify a horizontal length, it corresponds to the number of columns.
For example, in `width: 15`, this sets the width of a widget to be equal to 15 cells, which translates to 15 columns.

If used to specify a vertical length, it corresponds to the number of lines.
For example, in `height: 10`, this sets the height of a widget to be equal to 10 cells, which translates to 10 lines.

### Fraction

The unit fraction is used to represent proportional sizes.

For example, if two widgets are side by side and one has `width: 1fr` and the other has `width: 3fr`, the second one will be three times as wide as the first one.

### Percent

The percent unit matches a [`<percentage>`](./percentage.md) and is used to specify a total length relative to the space made available by the container widget.

If used to specify a horizontal length, it will be relative to the width of the container.
For example, `width: 50%` sets the width of a widget to 50% of the width of its container.

If used to specify a vertical length, it will be relative to the height of the container.
For example, `height: 50%` sets the height of a widget to 50% of the height of its container.

### Width

The width unit is similar to the percent unit, except it sets the percentage to be relative to the width of the container.

For example, `width: 25w` sets the width of a widget to 25% of the width of its container and `height: 25w` sets the height of a widget to 25% of the width of its container.
So, if the container has a width of 100 cells, the width and the height of the child widget will be of 25 cells.

### Height

The height unit is similar to the percent unit, except it sets the percentage to be relative to the height of the container.

For example, `height: 75h` sets the height of a widget to 75% of the height of its container and `width: 75h` sets the width of a widget to 75% of the height of its container.
So, if the container has a height of 100 cells, the width and the height of the child widget will be of 75 cells.

### Viewport width

This is the same as the [width unit](#width), except that it is relative to the width of the viewport instead of the width of the immediate container.
The width of the viewport is the width of the terminal minus the widths of widgets that are docked left or right.

For example, `width: 25vw` will try to set the width of a widget to be 25% of the viewport width, regardless of the widths of its containers.

### Viewport height

This is the same as the [height unit](#height), except that it is relative to the height of the viewport instead of the height of the immediate container.
The height of the viewport is the height of the terminal minus the heights of widgets that are docked top or bottom.

For example, `height: 75vh` will try to set the height of a widget to be 75% of the viewport height, regardless of the height of its containers.

### Auto

This special value will try to calculate the optimal size to fit the contents of the widget without scrolling.

For example, if its container is big enough, a label with `width: auto` will be just as wide as its text.

## Examples

### CSS

```css
Horizontal {
    width: 60;     /* 60 cells */
    height: 1fr;   /* proportional size of 1 */
}
```

### Python

```py
widget.styles.width = 16       # Cell unit can be specified with an int/float
widget.styles.height = "1fr"   # proportional size of 1
```
````

## File: docs/css_types/text_align.md
````markdown
# &lt;text-align&gt;

The `<text-align>` CSS type represents alignments that can be applied to text.

!!! warning

    Not to be confused with the [`text-align`](../styles/text_align.md) CSS rule that sets the alignment of text in a widget.

## Syntax

A [`<text-align>`](./text_align.md) can be any of the following values:

| Value     | Alignment type                       |
|-----------|--------------------------------------|
| `center`  | Center alignment.                    |
| `end`     | Alias for `right`.                   |
| `justify` | Text is justified inside the widget. |
| `left`    | Left alignment.                      |
| `right`   | Right alignment.                     |
| `start`   | Alias for `left`.                    |

!!! tip

    The meanings of `start` and `end` will likely change when RTL languages become supported by Textual.

## Examples

### CSS

```css
Label {
    text-align: justify;
}
```

### Python

```py
widget.styles.text_align = "justify"
```
````

## File: docs/css_types/text_style.md
````markdown
# &lt;text-style&gt;

The `<text-style>` CSS type represents styles that can be applied to text.

!!! warning

    Not to be confused with the [`text-style`](../styles/text_style.md) CSS rule that sets the style of text in a widget.

## Syntax

A [`<text-style>`](./text_style.md) can be the value `none` for plain text with no styling,
or any _space-separated_ combination of the following values:

| Value       | Description                                                     |
|-------------|-----------------------------------------------------------------|
| `bold`      | **Bold text.**                                                  |
| `italic`    | _Italic text._                                                  |
| `reverse`   | Reverse video text (foreground and background colors reversed). |
| `strike`    | <s>Strikethrough text.</s>                                      |
| `underline` | <u>Underline text.</u>                                          |

## Examples

### CSS

```css
#label1 {
    /* You can specify any value by itself. */
    rule: strike;
}

#label2 {
    /* You can also combine multiple values. */
    rule: strike bold italic reverse;
}
```

### Python

```py
# You can specify any value by itself
widget.styles.text_style = "strike"

# You can also combine multiple values
widget.styles.text_style = "strike bold italic reverse
```
````

## File: docs/css_types/vertical.md
````markdown
# &lt;vertical&gt;

The `<vertical>` CSS type represents a position along the vertical axis.

## Syntax

The [`<vertical>`](./vertical.md) type can take any of the following values:

| Value           | Description                                |
| --------------- | ------------------------------------------ |
| `bottom`        | Aligns at the bottom of the vertical axis. |
| `middle`        | Aligns in the middle of the vertical axis. |
| `top` (default) | Aligns at the top of the vertical axis.    |

## Examples

### CSS

```css
.container {
    align-vertical: top;
}
```

### Python

```py
widget.styles.align_vertical = "top"
```
````

## File: docs/events/app_blur.md
````markdown
---
title: AppBlur
---

::: textual.events.AppBlur
    options:
      heading_level: 1

## See also

- [AppFocus](app_focus.md)
````

## File: docs/events/app_focus.md
````markdown
---
title: AppFocus
---

::: textual.events.AppFocus
    options:
      heading_level: 1

## See also

- [AppBlur](app_blur.md)
````

## File: docs/events/blur.md
````markdown
::: textual.events.Blur
    options:
      heading_level: 1

## See also

- [DescendantBlur](descendant_blur.md)
- [DescendantFocus](descendant_focus.md)
- [Focus](focus.md)
````

## File: docs/events/click.md
````markdown
::: textual.events.Click
    options:
      heading_level: 1

## Double & triple clicks

The `chain` attribute on the `Click` event can be used to determine the number of clicks that occurred in quick succession.
A value of `1` indicates a single click, `2` indicates a double click, and so on.

By default, clicks must occur within 500ms of each other for them to be considered a chain.
You can change this value by setting the `CLICK_CHAIN_TIME_THRESHOLD` class variable on your `App` subclass.

See [MouseEvent][textual.events.MouseEvent] for the list of properties and methods on the parent class.

## See also

- [Enter](enter.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/descendant_blur.md
````markdown
---
title: DescendantBlur
---

::: textual.events.DescendantBlur
    options:
      heading_level: 1

## See also

- [AppBlur](app_blur.md)
- [AppFocus](app_focus.md)
- [Blur](blur.md)
- [DescendantFocus](descendant_focus.md)
- [Focus](focus.md)
````

## File: docs/events/descendant_focus.md
````markdown
---
title: DescendantFocus
---

::: textual.events.DescendantFocus
    options:
      heading_level: 1

## See also

- [AppBlur](app_blur.md)
- [AppFocus](app_focus.md)
- [Blur](blur.md)
- [DescendantBlur](descendant_blur.md)
- [Focus](focus.md)
````

## File: docs/events/enter.md
````markdown
::: textual.events.Enter
    options:
      heading_level: 1

## See also

- [Click](click.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/focus.md
````markdown
::: textual.events.Focus
    options:
      heading_level: 1

## See also

- [AppBlur](app_blur.md)
- [AppFocus](app_focus.md)
- [Blur](blur.md)
- [DescendantBlur](descendant_blur.md)
- [DescendantFocus](descendant_focus.md)
````

## File: docs/events/hide.md
````markdown
::: textual.events.Hide
    options:
      heading_level: 1
````

## File: docs/events/index.md
````markdown
# Events

A reference to Textual [events](../guide/events.md).

See the links to the left of the page, or click :octicons-three-bars-16: (top left).
````

## File: docs/events/key.md
````markdown
::: textual.events.Key
    options:
      heading_level: 1
````

## File: docs/events/leave.md
````markdown
::: textual.events.Leave
    options:
      heading_level: 1

## See also

- [Click](click.md)
- [Enter](enter.md)
- [MouseDown](mouse_down.md)
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/load.md
````markdown
::: textual.events.Load
    options:
      heading_level: 1

## See also

- [Mount](mount.md)
````

## File: docs/events/mount.md
````markdown
::: textual.events.Mount
    options:
      heading_level: 1

## See also

- [Load](load.md)
- [Unmount](unmount.md)
````

## File: docs/events/mouse_capture.md
````markdown
---
title: MouseCapture
---

::: textual.events.MouseCapture
    options:
      heading_level: 1

## See also

- [capture_mouse][textual.widget.Widget.capture_mouse]
- [release_mouse][textual.widget.Widget.release_mouse]
- [MouseRelease](mouse_release.md)
````

## File: docs/events/mouse_down.md
````markdown
---
title: MouseDown
---

::: textual.events.MouseDown
    options:
      heading_level: 1

See [MouseEvent][textual.events.MouseEvent] for the full list of properties and methods.

## See also

- [Click](click.md)
- [Enter](enter.md)
- [Leave](leave.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/mouse_move.md
````markdown
---
title: MouseMove
---

::: textual.events.MouseMove
    options:
      heading_level: 1

See [MouseEvent][textual.events.MouseEvent] for the full list of properties and methods.

## See also

- [Click](click.md)
- [Enter](enter.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/mouse_release.md
````markdown
---
title: MouseRelease
---

::: textual.events.MouseRelease
    options:
      heading_level: 1

## See also

- [capture_mouse][textual.widget.Widget.capture_mouse]
- [release_mouse][textual.widget.Widget.release_mouse]
- [MouseCapture](mouse_capture.md)
````

## File: docs/events/mouse_scroll_down.md
````markdown
---
title: MouseScrollDown
---

::: textual.events.MouseScrollDown
    options:
      heading_level: 1

See [MouseEvent][textual.events.MouseEvent] for the full list of properties and methods.

## See also

- [Click](click.md)
- [Enter](enter.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseMove](mouse_move.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/mouse_scroll_left.md
````markdown
---
title: MouseScrollLeft
---

::: textual.events.MouseScrollLeft
    options:
      heading_level: 1

See [MouseEvent][textual.events.MouseEvent] for the full list of properties and methods.

## See also

- [Click](click.md)
- [Enter](enter.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/mouse_scroll_right.md
````markdown
---
title: MouseScrollRight
---

::: textual.events.MouseScrollRight
    options:
      heading_level: 1

See [MouseEvent][textual.events.MouseEvent] for the full list of properties and methods.

## See also

- [Click](click.md)
- [Enter](enter.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollUp](mouse_scroll_up.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/mouse_scroll_up.md
````markdown
---
title: MouseScrollUp
---

::: textual.events.MouseScrollUp
    options:
      heading_level: 1

See [MouseEvent][textual.events.MouseEvent] for the full list of properties and methods.

## See also

- [Click](click.md)
- [Enter](enter.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseUp](mouse_up.md)
````

## File: docs/events/mouse_up.md
````markdown
---
title: MouseUp
---

::: textual.events.MouseUp
    options:
      heading_level: 1

See [MouseEvent][textual.events.MouseEvent] for the full list of properties and methods.

## See also

- [Click](click.md)
- [Enter](enter.md)
- [Leave](leave.md)
- [MouseDown](mouse_down.md)
- [MouseEvent][textual.events.MouseEvent]
- [MouseMove](mouse_move.md)
- [MouseScrollDown](mouse_scroll_down.md)
- [MouseScrollLeft](mouse_scroll_left.md)
- [MouseScrollRight](mouse_scroll_right.md)
- [MouseScrollUp](mouse_scroll_up.md)
````

## File: docs/events/paste.md
````markdown
::: textual.events.Paste
    options:
      heading_level: 1
````

## File: docs/events/print.md
````markdown
::: textual.events.Print
    options:
      heading_level: 1
````

## File: docs/events/resize.md
````markdown
::: textual.events.Resize
    options:
      heading_level: 1
````

## File: docs/events/screen_resume.md
````markdown
---
title: ScreenResume
---

::: textual.events.ScreenResume
    options:
      heading_level: 1

## See also

- [ScreenSuspend](screen_suspend.md)
````

## File: docs/events/screen_suspend.md
````markdown
---
title: ScreenSuspend
---

::: textual.events.ScreenSuspend
    options:
      heading_level: 1

## See also

- [ScreenResume](screen_resume.md)
````

## File: docs/events/show.md
````markdown
::: textual.events.Show
    options:
      heading_level: 1
````

## File: docs/events/unmount.md
````markdown
::: textual.events.Unmount
    options:
      heading_level: 1

## See also

- [Mount](mount.md)
````

## File: docs/examples/styles/README.md
````markdown
These are the examples from the documentation, used to generate screenshots.

You can run them with the textual CLI.

For example:

```
textual run text_style.py
```
````

## File: docs/guide/actions.md
````markdown
# Actions

Actions are allow-listed functions with a string syntax you can embed in links and bind to keys. In this chapter we will discuss how to create actions and how to run them.

## Action methods

Action methods are methods on your app or widgets prefixed with `action_`. Aside from the prefix these are regular methods which you could call directly if you wished.

!!! information

    Action methods may be coroutines (defined with the `async` keyword).

Let's write an app with a simple action method.

```python title="actions01.py" hl_lines="6-7 11"
--8<-- "docs/examples/guide/actions/actions01.py"
```

The `action_set_background` method is an action method which sets the background of the screen. The key handler above will call this action method if you press the ++r++ key.

Although it is possible (and occasionally useful) to call action methods in this way, they are intended to be parsed from an _action string_. For instance, the string `"set_background('red')"` is an action string which would call `self.action_set_background('red')`.

The following example replaces the immediate call with a call to [run_action()][textual.widgets.Widget.run_action] which parses an action string and dispatches it to the appropriate method.

```python title="actions02.py" hl_lines="9-11"
--8<-- "docs/examples/guide/actions/actions02.py"
```

Note that the `run_action()` method is a coroutine so `on_key` needs to be prefixed with the `async` keyword.

You will not typically need this in a real app as Textual will run actions in links or key bindings. Before we discuss these, let's have a closer look at the syntax for action strings.

## Syntax

Action strings have a simple syntax, which for the most part replicates Python's function call syntax.

!!! important

    As much as they *look* like Python code, Textual does **not** call Python's `eval` function to compile action strings.

Action strings have the following format:

- The name of an action on its own will call the action method with no parameters. For example, an action string of `"bell"` will call `action_bell()`.
- Action strings may be followed by parenthesis containing Python objects. For example, the action string `set_background("red")` will call `action_set_background("red")`.
- Action strings may be prefixed with a _namespace_ ([see below](#namespaces)) and a dot.

<div class="excalidraw">
--8<-- "docs/images/actions/format.excalidraw.svg"
</div>

### Parameters

If the action string contains parameters, these must be valid Python literals, which means you can include numbers, strings, dicts, lists, etc., but you can't include variables or references to any other Python symbols.

Consequently `"set_background('blue')"` is a valid action string, but `"set_background(new_color)"` is not &mdash; because `new_color` is a variable and not a literal.

## Links

Actions may be embedded in [markup](./content.md#actions) with the `@click` tag.

The following example mounts simple static text with embedded action links:

=== "actions03.py"

    ```python title="actions03.py" hl_lines="4-9 13-14"
    --8<-- "docs/examples/guide/actions/actions03.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/actions/actions03.py"}
    ```

When you click any of the links, Textual runs the `"set_background"` action to change the background to the given color.

## Bindings

Textual will run actions bound to keys. The following example adds key [bindings](./input.md#bindings) for the ++r++, ++g++, and ++b++ keys which call the `"set_background"` action.

=== "actions04.py"

    ```python title="actions04.py" hl_lines="13-17"
    --8<-- "docs/examples/guide/actions/actions04.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/actions/actions04.py" press="g"}
    ```

If you run this example, you can change the background by pressing keys in addition to clicking links.

See the previous section on [input](./input.md#bindings) for more information on bindings.

## Namespaces

Textual will look for action methods in the class where they are defined (App, Screen, or Widget). If we were to create a [custom widget](./widgets.md#custom-widgets) it can have its own set of actions.

The following example defines a custom widget with its own `set_background` action.

=== "actions05.py"

    ```python title="actions05.py" hl_lines="13-14"
    --8<-- "docs/examples/guide/actions/actions05.py"
    ```

=== "actions05.tcss"

    ```css title="actions05.tcss"
    --8<-- "docs/examples/guide/actions/actions05.tcss"
    ```

There are two instances of the custom widget mounted. If you click the links in either of them it will change the background for that widget only. The ++r++, ++g++, and ++b++ key bindings are set on the App so will set the background for the screen.

You can optionally prefix an action with a _namespace_, which tells Textual to run actions for a different object.

Textual supports the following action namespaces:

- `app` invokes actions on the App.
- `screen` invokes actions on the screen.
- `focused` invokes actions on the currently focused widget (if there is one).

In the previous example if you wanted a link to set the background on the app rather than the widget, we could set a link to `app.set_background('red')`.


## Dynamic actions

!!! tip "Added in version 0.61.0"

There may be situations where an action is temporarily unavailable due to some internal state within your app.
For instance, consider an app with a fixed number of pages and actions to go to the next and previous page.
It doesn't make sense to go to the previous page if we are on the first, or the next page when we are on the last page.

We could easily add this logic to the action methods, but the [footer][textual.widgets.Footer] would still display the keys even if they would have no effect.
The user may wonder why the app is showing keys that don't appear to work.

We can solve this issue by implementing the [`check_action`][textual.dom.DOMNode.check_action] on our app, screen, or widget.
This method is called with the name of the action and any parameters, prior to running actions or refreshing the footer.
It should return one of the following values:

- `True` to show the key and run the action as normal.
- `False` to hide the key and prevent the action running.
- `None` to disable the key (show dimmed), and prevent the action running.

Let's write an app to put this into practice:

=== "actions06.py"

    ```python title="actions06.py" hl_lines="27 32 35-43"
    --8<-- "docs/examples/guide/actions/actions06.py"
    ```

    1. Prompts the footer to refresh, if bindings change.
    2. Prompts the footer to refresh, if bindings change.
    3. Guards the actions from running and also what keys are displayed in the footer.

=== "actions06.tcss"

    ```css title="actions06.tcss"
    --8<-- "docs/examples/guide/actions/actions06.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/actions/actions06.py"}
    ```

This app has key bindings for ++n++ and ++p++ to navigate the pages.
Notice how the keys are hidden from the footer when they would have no effect.

The actions above call [`refresh_bindings`][textual.dom.DOMNode.refresh_bindings] to prompt Textual to refresh the footer.
An alternative to doing this manually is to set `bindings=True` on a [reactive](./reactivity.md), which will refresh the bindings if the reactive changes.

Let's make this change.
We will also demonstrate what the footer will show if we return `None` from `check_action` (rather than `False`):


=== "actions07.py"

    ```python title="actions06.py" hl_lines="17 36 38"
    --8<-- "docs/examples/guide/actions/actions07.py"
    ```

    1. The `bindings=True` causes the footer to refresh when `page_no` changes.
    2. Returning `None` disables the key in the footer rather than hides it
    3. Returning `None` disables the key in the footer rather than hides it.

=== "actions06.tcss"

    ```css title="actions06.tcss"
    --8<-- "docs/examples/guide/actions/actions06.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/actions/actions07.py"}
    ```

Note how the logic is the same but we don't need to explicitly call [`refresh_bindings`][textual.dom.DOMNode.refresh_bindings].
The change to `check_action` also causes the disabled footer keys to be grayed out, indicating they are temporarily unavailable.


## Builtin actions

Textual supports the following builtin actions which are defined on the app.

- [action_add_class][textual.app.App.action_add_class]
- [action_back][textual.app.App.action_back]
- [action_bell][textual.app.App.action_bell]
- [action_focus_next][textual.app.App.action_focus_next]
- [action_focus_previous][textual.app.App.action_focus_previous]
- [action_focus][textual.app.App.action_focus]
- [action_pop_screen][textual.app.App.action_pop_screen]
- [action_push_screen][textual.app.App.action_push_screen]
- [action_quit][textual.app.App.action_quit]
- [action_remove_class][textual.app.App.action_remove_class]
- [action_screenshot][textual.app.App.action_screenshot]
- [action_simulate_key][textual.app.App.action_simulate_key]
- [action_suspend_process][textual.app.App.action_suspend_process]
- [action_switch_screen][textual.app.App.action_switch_screen]
- [action_toggle_class][textual.app.App.action_toggle_class]
- [action_toggle_dark][textual.app.App.action_toggle_dark]
````

## File: docs/guide/animation.md
````markdown
# Animation

This chapter discusses how to use Textual's animation system to create visual effects such as movement, blending, and fading.


## Animating styles

Textual's animator can change an attribute from one value to another in fixed increments over a period of time. You can apply animations to [styles](styles.md) such as `offset` to move widgets around the screen, and `opacity` to create fading effects.

Apps and widgets both have an [animate][textual.app.App.animate] method which will animate properties on those objects. Additionally, `styles` objects have an identical `animate` method which will animate styles.

Let's look at an example of how we can animate the opacity of a widget to make it fade out.
The following example app contains a single `Static` widget which is immediately animated to an opacity of `0.0` (making it invisible) over a duration of two seconds.

```python hl_lines="14"
--8<-- "docs/examples/guide/animator/animation01.py"
```

The animator updates the value of the `opacity` attribute on the `styles` object in small increments over two seconds. Here's how the widget will change as time progresses:

=== "After 0s"

    ```{.textual path="docs/examples/guide/animator/animation01_static.py"}
    ```

=== "After 1s"

    ```{.textual path="docs/examples/guide/animator/animation01_static.py" press="1"}
    ```

=== "After 1.5s"

    ```{.textual path="docs/examples/guide/animator/animation01_static.py" press="2"}
    ```

=== "After 2s"

    ```{.textual path="docs/examples/guide/animator/animation01_static.py" press="3"}
    ```

## Duration and Speed

When requesting an animation you can specify a *duration* or *speed*.
The duration is how long the animation should take in seconds. The speed is how many units a value should change in one second.
For instance, if you animate a value at 0 to 10 with a speed of 2, it will complete in 5 seconds.

## Easing functions

The easing function determines the journey a value takes on its way to the target value.
It could move at a constant pace, or it might start off slow then accelerate towards its final value.
Textual supports a number of [easing functions](https://easings.net/).

<div class="excalidraw">
--8<-- "docs/images/animation/animation.excalidraw.svg"
</div>


Run the following from the command prompt to preview them.

```bash
textual easing
```

You can specify which easing method to use via the `easing` parameter on the `animate` method. The default easing method is `"in_out_cubic"` which accelerates and then decelerates to produce a pleasing organic motion.

!!! note

    The `textual easing` preview requires the `textual-dev` package to be installed (using `pip install textual-dev`).


## Completion callbacks

You can pass a callable to the animator via the `on_complete` parameter. Textual will run the callable when the animation has completed.

## Delaying animations

You can delay the start of an animation with the `delay` parameter of the `animate` method.
This parameter accepts a `float` value representing the number of seconds to delay the animation by.
For example, `self.box.styles.animate("opacity", value=0.0, duration=2.0, delay=5.0)` delays the start of the animation by five seconds,
meaning the animation will start after 5 seconds and complete 2 seconds after that.
````

## File: docs/guide/app.md
````markdown
# App Basics

In this chapter we will cover how to use Textual's App class to create an application. Just enough to get you up to speed. We will go into more detail in the following chapters.

## The App class

The first step in building a Textual app is to import the [App][textual.app.App] class and create a subclass. Let's look at the simplest app class:

```python
--8<-- "docs/examples/app/simple01.py"
```


### The run method

To run an app we create an instance and call [run()][textual.app.App.run].

```python hl_lines="8-10" title="simple02.py"
--8<-- "docs/examples/app/simple02.py"
```

Apps don't get much simpler than this&mdash;don't expect it to do much.

!!! tip

    The `__name__ == "__main__":` condition is true only if you run the file with `python` command. This allows us to import `app` without running the app immediately. It also allows the [devtools run](devtools.md#run) command to run the app in development mode. See the [Python docs](https://docs.python.org/3/library/__main__.html#idiomatic-usage) for more information.

If we run this app with `python simple02.py` you will see a blank terminal, something like the following:

```{.textual path="docs/examples/app/simple02.py"}
```

When you call [App.run()][textual.app.App.run] Textual puts the terminal into a special state called *application mode*. When in application mode the terminal will no longer echo what you type. Textual will take over responding to user input (keyboard and mouse) and will update the visible portion of the terminal (i.e. the *screen*).

If you hit ++ctrl+q++ Textual will exit application mode and return you to the command prompt. Any content you had in the terminal prior to application mode will be restored.


#### Run inline

!!! tip "Added in version 0.55.0"

You can also run apps in _inline_ mode, which will cause the app to appear beneath the prompt (and won't go into application mode).
Inline apps are useful for tools that integrate closely with the typical workflow of a terminal.

To run an app in inline mode set the `inline` parameter to `True` when you call [App.run()][textual.app.App.run]. See [Style Inline Apps](../how-to/style-inline-apps.md) for how to apply additional styles to inline apps.

!!! note

    Inline mode is not currently supported on Windows.


#### ANSI colors

!!! tip "Added in version 0.80.0"

Terminals support 16 theme-able *ANSI* colors, which you can personalize from your terminal settings.
By default, Textual will replace these colors with its own color choices (see the [FAQ for details](../FAQ.md#why-doesnt-textual-support-ansi-themes)).

You can disable this behavior by setting `ansi_color=True` in the [App constructor][textual.app.App].

We recommend the default behavior for full-screen apps, but you may want to preserve ANSI colors in [inline](#run-inline) apps.

## Events

Textual has an [event system](./events.md) you can use to respond to key presses, mouse actions, and internal state changes. Event handlers are methods prefixed with `on_` followed by the name of the event.

One such event is the *mount* event which is sent to an application after it enters application mode. You can respond to this event by defining a method called `on_mount`.

Another such event is the *key* event which is sent when the user presses a key. The following example contains handlers for both those events:

```python title="event01.py"
--8<-- "docs/examples/app/event01.py"
```

The `on_mount` handler sets the `self.screen.styles.background` attribute to `"darkblue"` which (as you can probably guess) turns the background blue. Since the mount event is sent immediately after entering application mode, you will see a blue screen when you run this code.

```{.textual path="docs/examples/app/event01.py" hl_lines="23-25"}
```

When you press a key, the key event handler (`on_key`) which will receive a [Key][textual.events.Key] instance.
If you don't require the event in your handler, you can omit it.

Events may contain additional information which you can inspect in the handler.
In the case of the [Key][textual.events.Key] event, there is a `key` attribute which is the name of the key that was pressed.
The `on_key` method above uses this attribute to change the background color if any of the keys from ++0++ to ++9++ are pressed.

### Async events

Textual is powered by Python's [asyncio](https://docs.python.org/3/library/asyncio.html) framework which uses the `async` and `await` keywords.

Textual knows to *await* your event handlers if they are coroutines (i.e. prefixed with the `async` keyword). Regular functions are generally fine unless you plan on integrating other async libraries (such as [httpx](https://www.python-httpx.org/) for reading data from the internet).

!!! tip

    For a friendly introduction to async programming in Python, see FastAPI's [concurrent burgers](https://fastapi.tiangolo.com/async/) article.


## Widgets

Widgets are self-contained components responsible for generating the output for a portion of the screen. Widgets respond to events in much the same way as the App. Most apps that do anything interesting will contain at least one (and probably many) widgets which together form a User Interface.

Widgets can be as simple as a piece of text, a button, or a fully-fledged component like a text editor or file browser (which may contain widgets of their own).

### Composing

To add widgets to your app implement a [`compose()`][textual.app.App.compose] method which should return an iterable of `Widget` instances. A list would work, but it is convenient to yield widgets, making the method a *generator*.

The following example imports a builtin `Welcome` widget and yields it from `App.compose()`.

```python title="widgets01.py"
--8<-- "docs/examples/app/widgets01.py"
```

When you run this code, Textual will *mount* the `Welcome` widget which contains Markdown content and a button:

```{.textual path="docs/examples/app/widgets01.py"}
```

Notice the `on_button_pressed` method which handles the [Button.Pressed][textual.widgets.Button] event sent by a button contained in the `Welcome` widget. The handler calls [App.exit()][textual.app.App.exit] to exit the app.

### Mounting

While composing is the preferred way of adding widgets when your app starts it is sometimes necessary to add new widget(s) in response to events. You can do this by calling [mount()][textual.widget.Widget.mount] which will add a new widget to the UI.

Here's an app which adds a welcome widget in response to any key press:

```python title="widgets02.py"
--8<-- "docs/examples/app/widgets02.py"
```

When you first run this you will get a blank screen. Press any key to add the welcome widget. You can even press a key multiple times to add several widgets.

```{.textual path="docs/examples/app/widgets02.py" press="a,a,a,down,down,down,down,down,down"}
```

#### Awaiting mount

When you mount a widget, Textual will mount everything the widget *composes*.
Textual guarantees that the mounting will be complete by the *next* message handler, but not immediately after the call to `mount()`.
This may be a problem if you want to make any changes to the widget in the same message handler.

Let's first illustrate the problem with an example.
The following code will mount the Welcome widget in response to a key press.
It will also attempt to modify the Button in the Welcome widget by changing its label from "OK" to "YES!".

```python hl_lines="2 8"
from textual.app import App
from textual.widgets import Button, Welcome


class WelcomeApp(App):
    def on_key(self) -> None:
        self.mount(Welcome())
        self.query_one(Button).label = "YES!" # (1)!


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
```

1. See [queries](./queries.md) for more information on the `query_one` method.

If you run this example, you will find that Textual raises a [NoMatches][textual.css.query.NoMatches] exception when you press a key.
This is because the mount process has not yet completed when we attempt to change the button.

To solve this we can optionally await the result of `mount()`, which requires we make the function `async`.
This guarantees that by the following line, the Button has been mounted, and we can change its label.


```python hl_lines="6 7"
from textual.app import App
from textual.widgets import Button, Welcome


class WelcomeApp(App):
    async def on_key(self) -> None:
        await self.mount(Welcome())
        self.query_one(Button).label = "YES!"


if __name__ == "__main__":
    app = WelcomeApp()
    app.run()
```

Here's the output. Note the changed button text:

```{.textual path="docs/examples/app/widgets04.py" press=["a"]}
```

## Exiting

An app will run until you call [App.exit()][textual.app.App.exit] which will exit application mode and the [run][textual.app.App.run] method will return. If this is the last line in your code you will return to the command prompt.

The exit method will also accept an optional positional value to be returned by `run()`. The following example uses this to return the `id` (identifier) of a clicked button.

```python title="question01.py"
--8<-- "docs/examples/app/question01.py"
```

Running this app will give you the following:

```{.textual path="docs/examples/app/question01.py"}
```

Clicking either of those buttons will exit the app, and the `run()` method will return either `"yes"` or `"no"` depending on button clicked.

### Return type

You may have noticed that we subclassed `App[str]` rather than the usual `App`.

```python title="question01.py" hl_lines="5"
--8<-- "docs/examples/app/question01.py"
```

The addition of `[str]` tells mypy that `run()` is expected to return a string. It may also return `None` if [App.exit()][textual.app.App.exit] is called without a return value, so the return type of `run` will be `str | None`. Replace the `str` in `[str]` with the type of the value you intend to call the exit method with.

!!! note "Typing in Textual"

    Type annotations are entirely optional (but recommended) with Textual.

### Return code

When you exit a Textual app with [`App.exit()`][textual.app.App.exit], you can optionally specify a *return code* with the `return_code` parameter.


!!! info "What are return codes?"

    Returns codes are a standard feature provided by your operating system.
    When any application exits it can return an integer to indicate if it was successful or not.
    A return code of `0` indicates success, any other value indicates that an error occurred.
    The exact meaning of a non-zero return code is application-dependant.

When a Textual app exits normally, the return code will be `0`. If there is an unhandled exception, Textual will set a return code of `1`.
You may want to set a different value for the return code if there is error condition that you want to differentiate from an unhandled exception.

Here's an example of setting a return code for an error condition:

```python
if critical_error:
    self.exit(return_code=4, message="Critical error occurred")
```

The app's return code can be queried with `app.return_code`, which will be `None` if it hasn't been set, or an integer.

Textual won't explicitly exit the process.
To exit the app with a return code, you should call `sys.exit`.
Here's how you might do that:

```python
if __name__ == "__main__"
    app = MyApp()
    app.run()
    import sys
    sys.exit(app.return_code or 0)
```

## Suspending

A Textual app may be suspended so you can leave application mode for a period of time.
This is often used to temporarily replace your app with another terminal application.

You could use this to allow the user to edit content with their preferred text editor, for example.

!!! info

    App suspension is unavailable with [textual-web](https://github.com/Textualize/textual-web).

### Suspend context manager

You can use the [App.suspend](/api/app/#textual.app.App.suspend) context manager to suspend your app.
The following Textual app will launch [vim](https://www.vim.org/) (a text editor) when the user clicks a button:

=== "suspend.py"

    ```python hl_lines="15-16"
    --8<-- "docs/examples/app/suspend.py"
    ```

    1. All code in the body of the `with` statement will be run while the app is suspended.

=== "Output"

    ```{.textual path="docs/examples/app/suspend.py"}
    ```

### Suspending from foreground

On Unix and Unix-like systems (GNU/Linux, macOS, etc) Textual has support for the user pressing a key combination to suspend the application as the foreground process.
Ordinarily this key combination is <kbd>Ctrl</kbd>+<kbd>Z</kbd>;
in a Textual application this is disabled by default, but an action is provided ([`action_suspend_process`](/api/app/#textual.app.App.action_suspend_process)) that you can bind in the usual way.
For example:

=== "suspend_process.py"

    ```python hl_lines="8"
    --8<-- "docs/examples/app/suspend_process.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/app/suspend_process.py"}
    ```

!!! note

    If `suspend_process` is called on Windows, or when your application is being hosted under Textual Web, the call will be ignored.

## CSS

Textual apps can reference [CSS](CSS.md) files which define how your app and widgets will look, while keeping your project free of messy display related code.

!!! info

    Textual apps typically use the extension `.tcss` for external CSS files to differentiate them from browser (`.css`) files.

The chapter on [Textual CSS](CSS.md) describes how to use CSS in detail. For now let's look at how your app references external CSS files.

The following example enables loading of CSS by adding a `CSS_PATH` class variable:

```python title="question02.py" hl_lines="6 9"
--8<-- "docs/examples/app/question02.py"
```

!!! note

    We also added an `id` to the `Label`, because we want to style it in the CSS.

If the path is relative (as it is above) then it is taken as relative to where the app is defined. Hence this example references `"question01.tcss"` in the same directory as the Python code. Here is that CSS file:

```css title="question02.tcss"
--8<-- "docs/examples/app/question02.tcss"
```

When `"question02.py"` runs it will load `"question02.tcss"` and update the app and widgets accordingly. Even though the code is almost identical to the previous sample, the app now looks quite different:

```{.textual path="docs/examples/app/question02.py"}
```


### Classvar CSS

While external CSS files are recommended for most applications, and enable some cool features like *live editing*, you can also specify the CSS directly within the Python code.

To do this set a `CSS` class variable on the app to a string containing your CSS.

Here's the question app with classvar CSS:

```python title="question03.py" hl_lines="6-24"
--8<-- "docs/examples/app/question03.py"
```


## Title and subtitle

Textual apps have a `title` attribute which is typically the name of your application, and an optional `sub_title` attribute which adds additional context (such as the file your are working on).
By default, `title` will be set to the name of your App class, and `sub_title` is empty.
You can change these defaults by defining `TITLE` and `SUB_TITLE` class variables. Here's an example of that:

```py title="question_title01.py" hl_lines="7-8 11"
--8<-- "docs/examples/app/question_title01.py"
```

Note that the title and subtitle are displayed by the builtin [Header](./../widgets/header.md) widget at the top of the screen:

```{.textual path="docs/examples/app/question_title01.py"}
```

You can also set the title attributes dynamically within a method of your app. The following example sets the title and subtitle in response to a key press:

```py title="question_title02.py" hl_lines="20-22"
--8<-- "docs/examples/app/question_title02.py"
```

If you run this app and press the ++t++ key, you should see the header update accordingly:

```{.textual path="docs/examples/app/question_title02.py" press="t"}
```

!!! info

    Note that there is no need to explicitly refresh the screen when setting the title attributes. This is an example of [reactivity](./reactivity.md), which we will cover later in the guide.

## What's next

In the following chapter we will learn more about how to apply styles to your widgets and app.
````

## File: docs/guide/command_palette.md
````markdown
# Command Palette

Textual apps have a built-in *command palette*, which gives users a quick way to access certain functionality within your app.

In this chapter we will explain what a command palette is, how to use it, and how you can add your own commands.

## Launching the command palette

Press ++ctrl+p++ to invoke the command palette screen, which contains of a single input widget.
Textual will suggest commands as you type in that input.
Press ++up++ or ++down++ to select a command from the list, and ++enter++ to invoke it.

Commands are looked up via a *fuzzy* search, which means Textual will show commands that match the keys you type in the same order, but not necessarily at the start of the command.
For instance the "Change theme" command will be shown if you type "ch" (for **ch**ange), but you could also type "th" (to match **t**heme).
This scheme allows the user to quickly get to a particular command with fewer key-presses.


=== "Command Palette"

    ```{.textual path="docs/examples/guide/command_palette/command01.py" press="ctrl+p"}
    ```

=== "Command Palette after 't'"

    ```{.textual path="docs/examples/guide/command_palette/command01.py" press="ctrl+p,t"}
    ```

=== "Command Palette after 'td'"

    ```{.textual path="docs/examples/guide/command_palette/command01.py" press="ctrl+p,t,d"}
    ```

## System commands

Textual apps have a number of *system* commands enabled by default.
These are declared in the [`App.get_system_commands`][textual.app.App.get_system_commands] method.
You can implement this method in your App class to add more commands.

To declare a command, define a `get_system_commands` method on your App.
Textual will call this method with the screen that was active when the user summoned the command palette. 

You can add a command by yielding a [`SystemCommand`][textual.app.SystemCommand] object which contains `title` and `help` text to be shown in the command palette, and `callback` which is a callable to run when the user selects the command.
Additionally, there is a `discover` boolean which when `True` (the default) shows the command even if the search import is empty. When set to `False`, the command will show only when there is input.

Here's how we would add a command to ring the terminal bell (a super useful piece of functionality):

=== "command01.py"

    ```python title="command01.py" hl_lines="18-24 29"
    --8<-- "docs/examples/guide/command_palette/command01.py"
    ```

    1. Adds the default commands from the base class.
    2. Adds a new command.

=== "Output"

    ```{.textual path="docs/examples/guide/command_palette/command01.py" press="ctrl+p"}
    ```

This is a straightforward way of adding commands to your app.
For more advanced integrations you can implement your own *command providers*.


## Command providers

To add your own command(s) to the command palette, define a [`command.Provider`][textual.command.Provider] class then add it to the [`COMMANDS`][textual.app.App.COMMANDS] class var on your `App` class.

Let's look at a simple example which adds the ability to open Python files via the command palette.

The following example will display a blank screen initially, but if you bring up the command palette and start typing the name of a Python file, it will show the command to open it.

!!! tip

    If you are running that example from the repository, you may want to add some additional Python files to see how the examples works with multiple files.


  ```python title="command02.py" hl_lines="12-40 46"
  --8<-- "docs/examples/guide/command_palette/command02.py"
  ```

  1. This method is called when the command palette is first opened.
  2. Called on each key-press.
  3. Get a [Matcher][textual.fuzzy.Matcher] instance to compare against hits.
  4. Use the matcher to get a score.
  5. Highlights matching letters in the search.
  6. Adds our custom command provider and the default command provider.

There are four methods you can override in a command provider: [`startup`][textual.command.Provider.startup], [`search`][textual.command.Provider.search], [`discover`][textual.command.Provider.discover] and [`shutdown`][textual.command.Provider.shutdown].
All of these methods should be coroutines (`async def`). Only `search` is required, the other methods are optional.
Let's explore those methods in detail.

### startup method

The [`startup`][textual.command.Provider.startup] method is called when the command palette is opened.
You can use this method as way of performing work that needs to be done prior to searching.
In the example, we use this method to get the Python (.py) files in the current working directory.

### search method

The [`search`][textual.command.Provider.search] method is responsible for finding results (or *hits*) that match the user's input.
This method should *yield* [`Hit`][textual.command.Hit] objects for any command that matches the `query` argument.

Exactly how the matching is implemented is up to the author of the command provider, but we recommend using the builtin fuzzy matcher object, which you can get by calling [`matcher`][textual.command.Provider.matcher].
This object has a [`match()`][textual.fuzzy.Matcher.match] method which compares the user's search term against the potential command and returns a *score*.
A score of zero means *no hit*, and you can discard the potential command.
A score of above zero indicates the confidence in the result, where 1 is an exact match, and anything lower indicates a less confident match.

The [`Hit`][textual.command.Hit] contains information about the score (used in ordering) and how the hit should be displayed, and an optional help string.
It also contains a callback, which will be run if the user selects that command.

In the example above, the callback is a lambda which calls the `open_file` method in the example app.

!!! note

    Unlike most other places in Textual, errors in command provider will not *exit* the app.
    This is a deliberate design decision taken to prevent a single broken `Provider` class from making the command palette unusable.
    Errors in command providers will be logged to the [console](./devtools.md).

### discover method

The [`discover`][textual.command.Provider.discover] method is responsible for providing results (or *discovery hits*) that should be shown to the user when the command palette input is empty;
this is to aid in command discoverability.

!!! note

    Because `discover` hits are shown the moment the command palette is opened, these should ideally be quick to generate;
    commands that might take time to generate are best left for `search` -- use `discover` to help the user easily find the most important commands.

`discover` is similar to `search` but with these differences:

- `discover` accepts no parameters (instead of the search value)
- `discover` yields instances of [`DiscoveryHit`][textual.command.DiscoveryHit] (instead of instances of [`Hit`][textual.command.Hit])

Instances of [`DiscoveryHit`][textual.command.DiscoveryHit] contain information about how the hit should be displayed, an optional help string, and a callback which will be run if the user selects that command.

### shutdown method

The [`shutdown`][textual.command.Provider.shutdown] method is called when the command palette is closed.
You can use this as a hook to gracefully close any objects you created in [`startup`][textual.command.Provider.startup].

## Screen commands

You can also associate commands with a screen by adding a `COMMANDS` class var to your Screen class.

Commands defined on a screen are only considered when that screen is active.
You can use this to implement commands that are specific to a particular screen, that wouldn't be applicable everywhere in the app.

## Disabling the command palette

The command palette is enabled by default.
If you would prefer not to have the command palette, you can set `ENABLE_COMMAND_PALETTE = False` on your app class.

Here's an app class with no command palette:

```python
class NoPaletteApp(App):
    ENABLE_COMMAND_PALETTE = False
```

## Changing command palette key

You can change the key that opens the command palette by setting the class variable `COMMAND_PALETTE_BINDING` on your app.

Prior to version 0.77.0, Textual used the binding `ctrl+backslash` to launch the command palette.
Here's how you would restore the older key binding:

```python
class NewPaletteBindingApp(App):
    COMMAND_PALETTE_BINDING = "ctrl+backslash"
```
````

## File: docs/guide/content.md
````markdown
# Content

The *content* of widget (displayed within the widget's borders) is typically specified in a call to [`Static.update`][textual.widgets.Static.update] or returned from [`render()`][textual.widget.Widget.render] in the case of [custom widgets](./widgets.md#custom-widgets).

There are a few ways for you to specify this content.

- Text &mdash; a string containing [markup](#markup).
- [Content](#content-class) objects &mdash; for more advanced control over output.
- Rich renderables &mdash; any object that may be printed with [Rich](https://rich.readthedocs.io/en/latest/).

In this chapter, we will cover all these methods. 

## Markup

When building a custom widget you can embed color and style information in the string returned from the Widget's [`render()`][textual.widget.Widget.render] method.
Markup is specified as a string which contains 
Text enclosed in square brackets (`[]`) won't appear in the output, but will modify the style of the text that follows.
This is known as *content markup*.

Before we explore content markup in detail, let's first demonstrate some of what it can do.
In the following example, we have two widgets.
The top has content markup enabled, while the bottom widget has content markup *disabled*.

Notice how the markup *tags* change the style in the first widget, but are left unaltered in the second:


=== "Output"

    ```{.textual path="docs/examples/guide/content/content01.py"}
    ```

=== "content01.py"

    ```python 
    --8<-- "docs/examples/guide/content/content01.py"
    ```
    
    1. With `markup=False`, tags have no effect and left in the output.


### Playground

Textual comes with a markup playground where you can enter content markup and see the result's live.
To launch the playground, run the following command:

```
python -m textual.markup
```

You can experiment with markup by entering it in to the textarea at the top of the terminal, and seeing the results in the lower pane:

```{.textual path="docs/examples/guide/content/playground.py", type="[i]Hello!"] lines=16}
```

You might find it helpful to try out some of the examples from this guide in the playground.

!!! note "What are Variables?"

    You may have noticed the "Variables" tab. This allows you to experiment with [variable substitution](#markup-variables).

### Tags

There are two types of tag: an *opening* tag which starts a style change, and a *closing* tag which ends a style change.
An opening tag looks like this:

```
[bold]
```


The second type of tag, known as a *closing* tag, is almost identical, but starts with a forward slash inside the first square bracket.
A closing tag looks like this:

```
[/bold]
```

A closing tag marks the end of a style from the corresponding opening tag.

By wrapping text in an opening and closing tag, we can apply the style to just the characters we want.
For example, the following makes just the first word in "Hello, World!" bold:

```
[bold]Hello[/bold], World!
```

Note how the tags change the style but are removed from the output:

```{.textual path="docs/examples/guide/content/playground.py", type="[bold]Hello[/bold], World!" lines=16}
```

You can use any number of tags. 
If tags overlap their styles are combined.
For instance, the following combines the bold and italic styles:

```
[bold]Bold [italic]Bold and italic[/italic][/bold]
```

Here's the output:

```{.textual path="docs/examples/guide/content/playground.py", type="[bold]Bold [italic]Bold and italic[/italic][/bold]" lines=16}
```

#### Auto-closing tags

A closing tag without any style information (i.e. `[/]`) is an *auto-closing* tag.
Auto-closing tags will close the last opened tag.

The following uses an auto-closing tag to end the bold style:

```
[bold]Hello[/], World!
```

This is equivalent to the following (but saves typing a few characters):

```
[bold]Hello[/bold], World!
```

Auto-closing tags are recommended when it is clear which tag they are intended to close. 

### Styles

Tags may contain any number of the following values:

| Style       | Abbreviation | Description                                                                                                                                               |
| ----------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `bold`      | `b`          | **Bold text**                                                                                                                                             |
| `dim`       | `d`          | <span style="opacity: 0.6;">Dim text </span> (slightly transparent)                                                                                       |
| `italic`    | `i`          | *Italic text*                                                                                                                                             |
| `underline` | `u`          | <u>Underlined text</u>                                                                                                                                    |
| `strike`    | `s`          | <strike>Strikethrough text<strile>                                                                                                                        |
| `reverse`   | `r`          | <span style="background: var(--md-primary-bg-color); color: var(--md-primary-fg-color);">Reversed colors text</span> (background swapped with foreground) |

These styles can be abbreviate to save typing.
For example `[bold]` and `[b]` are equivalent.

Styles can also be combined within the same tag, so `[bold italic]` produces text that is both bold *and* italic.

#### Inverting styles

You can invert a style by preceding it with the word `not`. 
This is useful if you have text with a given style, but you temporarily want to disable it.

For instance, the following starts with `[bold]`, which would normally make the rest of the text bold.
However, the `[not bold]` tag disables bold until the corresponding `[/not bold]` tag:

```
[bold]This is bold [not bold]This is not bold[/not bold] This is bold.
```

Here's what this markup will produce:

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="[bold]This is bold [not bold]This is not bold[/not bold] This is bold."]}
```

### Colors

Colors may specified in the same way as a CSS [&lt;color&gt;](/css_types/color).
Here are a few examples:

```
[#ff0000]HTML hex style[/]
[rgba(0,255,0)]HTML RGB style[/]

```

You can also any of the [named colors](/css_types/color).

```
[chartreuse]This is a green color[/]
[sienna]This is a kind of yellow-brown.[/]
```

Colors may also include an *alpha* component, which makes the color fade in to the background.
For instance, if we specify the color with `rgba(...)`, then we can add an alpha component between 0 and 1.
An alpha of 0 is fully transparent (and therefore invisible). An alpha of 1 is fully opaque, and equivalent to a color without an alpha component.
A value between 0 and 1 results in a faded color.

In the following example we have an alpha of 0.5, which will produce a color half way between the background and solid green:

```
[rgba(0, 255, 0, 0.5)]Faded green (and probably hard to read)[/]
```

Here's the output:

```{.textual path="docs/examples/guide/content/playground.py", type="[rgba(0, 255, 0, 0.5)]Faded green (and probably hard to read)[/]" lines=16}
```

!!! warning

    Be careful when using colors with an alpha component. Text that is blended too much with the background may become hard to read.


#### Auto colors

You can also specify a color as "auto", which is a special value that tells Textual to pick either white or black text -- whichever has the best contrast.

For example, the following will produce either white or black text (I haven't checked) on a sienna background:

```
[auto on sienna]This should be fairly readable.
```


#### Opacity

While you can set the opacity in the color itself by adding an alpha component to the color, you can also modify the alpha of the previous color with a percentage.

For example, the addition of `50%` will result in a color half way between the background and "red":

```
[red 50%]This is in faded red[/]
```


#### Background colors

Background colors may be specified by preceding a color with the world `on`.
Here's an example:

```
[on #ff0000]Background is bright red.
```

Background colors may also have an alpha component (either in the color itself or with a percentage).
This will result in a color that is blended with the widget's parent (or Screen).

Here's an example that tints the background with 20% red:

```
[on #ff0000 20%]The background has a red tint.[/]
```

Here's the output:

```{.textual path="docs/examples/guide/content/playground.py" lines=15 type="[on #ff0000 20%]The background has a red tint.[/]"]}
```


### CSS variables

You can also use CSS variables in markup, such as those specified in the [design](./design.md#base-colors) guide.

To use any of the theme colors, simple use the name of the color including the `$` at the first position.
For example, this will display text in the *accent* color:

```
[$accent]Accent color[/]
```

You may also use a color variable in the background position.
The following displays text in the 'warning' style on a muted 'warning' background for emphasis:

```
[$warning on $warning-muted]This is a warning![/]
```

Here's the result of that markup:

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="[$warning on $warning-muted]This is a warning![/]"]}
```

### Links

Styles may contain links which will create clickable links that launch your web browser, if supported by your terminal.

To create a link add `link=` followed by your link in quotes (single or double).
For instance, the following create a clickable link:

```
[link="https://www.willmcgugan.com"]Visit my blog![/link]
```

This will produce the following output:
<code><pre><a href="https://www.willmcgugan.com">Visit my blog!</a></pre></code>

### Actions

In addition to links, you can also markup content that runs [actions](./actions.md) when clicked.
To do this create a style that starts with `@click=` and is followed by the action you wish to run.

For instance, the following will highlight the word "bell", which plays the terminal bell sound when click:

```
Play the [@click=app.bell]bell[/]
```

Here's what it looks like:

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="Play the [@click=app.bell]bell[/]"]}
```

We've used an [auto-closing](#auto-closing-tags) to close the click action here. 
If you do need to close the tag explicitly, you can omit the action:

```
Play the [@click=app.bell]bell[/@click=]
```

Actions may be combined with other styles, so you could set the style of the clickable link:

```
Play the [on $success 30% @click=app.bell]bell[/]
```

Here's what that looks like:

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="Play the [on $success 30% @click=app.bell]bell[/]"]}
```

### Escaping

If you precede an open bracket with a backslash (`\`), then Textual will not consider it to be a tag and the square bracket will be displayed without modification. 

For example, the backslash in the following content prevents the following text from becoming bold, and the text `[bold]` will be in the output.

```{.textual path="docs/examples/guide/content/playground.py" lines=16 type="\[bold]This is not bold"]}
```

!!! tip "Escaping markup"

    You can also use the [escape][textual.markup.escape] function to escape tags

Some methods, such as [`notify()`][textual.widget.Widget.notify], have a `markup` switch that you can use to disable markup.
You may want to use this if you want to output a Python repr strings, so that Textual doesn't interpret a list as a tag.

Here's an example:

```python
# debug code: what is my_list at this point?
self.notify(repr(my_list), markup=False)
```

## Content class

Under the hood, Textual will convert markup into a [Content][textual.content.Content] instance.
You can also return a Content object directly from `render()`.
This can give you more flexibility beyond the markup.

To clarify, here's a render method that returns a string with markup:

```python
class WelcomeWidget(Widget):
    def render(self) -> RenderResult:
        return "[b]Hello, World![/b]"
```

This is roughly the equivalent to the following code:

```python
class WelcomeWidget(Widget):
    def render(self) -> RenderResult:
        return Content.from_markup("[b]Hello, World![/b]")
```

### Constructing content

The [Content][textual.content.Content] class accepts a default string in it's constructor.

Here's an example:

```python
Content("hello, World!")
```

Note that if you construct Content in this way, it *won't* process markup (any square brackets will be displayed literally).

If you want markup, you can create a `Content` with the [Content.from_markup][textual.content.Content.from_markup] alternative constructor:

```python
Content.from_markup("hello, [bold]World[/bold]!")
```

### Styling content

You can add styles to content with the [stylize][textual.content.Content.stylize] or [stylize_before][textual.content.Content.stylize] methods.

For instance, in the following code we create content with the text "Hello, World!" and style "World" to be bold:

```python
content = Content("Hello, World!")
content = content.stylize(7, 12, "bold")
```

Note that `Content` is *immutable* and methods will return new instances rather than updating the current instance.


### Markup variables

You may be tempted to combine markup with Python's f-strings (or other string template system).
Something along these lines:

```python
class WelcomeWidget(Widget):
    def render(self) -> RenderResult:
        name = "Will"
        return f"Hello [bold]{name}[/bold]!"
```

While this is straightforward and intuitive, it can potentially break in subtle ways.
If the 'name' variable contains square brackets, these may be interpreted as markup.
For instance if the user entered their name at some point as "[magenta italic]Will" then your app will display those styles where you didn't intend them to be.

We can avoid this problem by relying on the [Content.from_markup][textual.content.Content.from_markup] method to insert the variables for us.
If you supply variables as keyword arguments, these will be substituted in the markup using the same syntax as [string.Template](https://docs.python.org/3/library/string.html#template-strings).
Any square brackets in the variables will be present in the output, but won't change the styles.

Here's how we can fix the previous example:

```python
return Content.from_markup("hello [bold]$name[/bold]!", name=name)
```

You can experiment with this feature by entering a dictionary of variables in the variables text-area.

Here's what that looks like:

```{.textual path="docs/examples/guide/content/playground.py" lines=20 columns=110 type='hello [bold]$name[/bold]!\t{"name": "[magenta italic]Will"}\t']}
```

## Rich renderables

Textual supports Rich *renderables*, which means you can display any object that works with Rich, such as Rich's [Text](https://rich.readthedocs.io/en/latest/text.html) object.

The Content class is preferred for simple text, as it supports more of Textual's features.
But you can display any of the objects in the [Rich library](https://github.com/Textualize/rich) (or ecosystem) within a widget.

Here's an example which displays its own code using Rich's [Syntax](https://rich.readthedocs.io/en/latest/syntax.html) object.

=== "Output"

    ```{.textual path="docs/examples/guide/content/renderables.py"}
    ```

=== "renderables.py"

    ```python 
    --8<-- "docs/examples/guide/content/renderables.py"
    ```
````

## File: docs/guide/CSS.md
````markdown
# Textual CSS

Textual uses CSS to apply style to widgets. If you have any exposure to web development you will have encountered CSS, but don't worry if you haven't: this chapter will get you up to speed.

!!! tip "VSCode User?"

    The official [Textual CSS](https://marketplace.visualstudio.com/items?itemName=Textualize.textual-syntax-highlighter) extension adds syntax highlighting for both external files and inline CSS.

## Stylesheets

CSS stands for _Cascading Stylesheet_. A stylesheet is a list of styles and rules about how those styles should be applied to a web page. In the case of Textual, the stylesheet applies [styles](./styles.md) to widgets, but otherwise it is the same idea.

Let's look at some Textual CSS.

```css
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

This is an example of a CSS _rule set_. There may be many such sections in any given CSS file.

Let's break this CSS code down a bit.

```css hl_lines="1"
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

The first line is a _selector_ which tells Textual which widget(s) to modify. In the above example, the styles will be applied to a widget defined by the Python class `Header`.

```css hl_lines="2 3 4 5 6"
Header {
  dock: top;
  height: 3;
  content-align: center middle;
  background: blue;
  color: white;
}
```

The lines inside the curly braces contains CSS _rules_, which consist of a rule name and rule value separated by a colon and ending in a semicolon. Such rules are typically written one per line, but you could add additional rules as long as they are separated by semicolons.

The first rule in the above example reads `"dock: top;"`. The rule name is `dock` which tells Textual to place the widget on an edge of the screen. The text after the colon is `top` which tells Textual to dock to the _top_ of the screen. Other valid values for `dock` are "right", "bottom", or "left"; but "top" is most appropriate for a header.


## The DOM

The DOM, or _Document Object Model_, is a term borrowed from the web world. Textual doesn't use documents but the term has stuck. In Textual CSS, the DOM is an arrangement of widgets you can visualize as a tree-like structure.

Some widgets contain other widgets: for instance, a list control widget will likely also have item widgets, or a dialog widget may contain button widgets. These _child_ widgets form the branches of the tree.

Let's look at a trivial Textual app.

=== "dom1.py"

    ```python
    --8<-- "docs/examples/guide/dom1.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/dom1.py"}
    ```

This example creates an instance of `ExampleApp`, which will implicitly create a `Screen` object. In DOM terms, the `Screen` is a _child_ of `ExampleApp`.

With the above example, the DOM will look like the following:

<div class="excalidraw">
--8<-- "docs/images/dom1.excalidraw.svg"
</div>

This doesn't look much like a tree yet. Let's add a header and a footer to this application, which will create more _branches_ of the tree:

=== "dom2.py"

    ```python hl_lines="7 8"
    --8<-- "docs/examples/guide/dom2.py"
    ```


=== "Output"

    ```{.textual path="docs/examples/guide/dom2.py"}
    ```

With a header and a footer widget the DOM looks like this:

<div class="excalidraw">
--8<-- "docs/images/dom2.excalidraw.svg"
</div>

!!! note "What we didn't show"

    We've simplified the above example somewhat. Both the Header and Footer widgets contain children of their own. When building an app with pre-built widgets you rarely need to know how they are constructed unless you plan on changing the styles of individual components.

Both Header and Footer are children of the Screen object.

To further explore the DOM, we're going to build a simple dialog with a question and two buttons. To do this we're going to import and use a few more builtin widgets:

- [`textual.containers.Container`][textual.containers.Container] For our top-level dialog.
- [`textual.containers.Horizontal`][textual.containers.Horizontal] To arrange widgets left to right.
- [`textual.widgets.Static`][textual.widgets.Static] For simple content.
- [`textual.widgets.Button`][textual.widgets.Button] For a clickable button.


```python hl_lines="12 13 14 15 16 17 18 19 20" title="dom3.py"
--8<-- "docs/examples/guide/dom3.py"
```

We've added a Container to our DOM which (as the name suggests) contains other widgets. The container has a number of other widgets passed as positional arguments which will be added as the children of the container. Not all widgets accept child widgets in this way. A Button widget doesn't require any children, for example.

Here's the DOM created by the above code:

<div class="excalidraw">
--8<-- "docs/images/dom3.excalidraw.svg"
</div>

Here's the output from this example:

```{.textual path="docs/examples/guide/dom3.py"}

```

You may recognize some elements in the above screenshot, but it doesn't quite look like a dialog. This is because we haven't added a stylesheet.

## CSS files

To add a stylesheet set the `CSS_PATH` classvar to a relative path:


!!! note "What are TCSS files?"

    Textual CSS files are typically given the extension `.tcss` to differentiate them from browser CSS (`.css`).


```python hl_lines="9" title="dom4.py"
--8<-- "docs/examples/guide/dom4.py"
```

You may have noticed that some constructors have additional keyword arguments: `id` and `classes`.
These are used by the CSS to identify parts of the DOM. We will cover these in the next section.

Here's the CSS file we are applying:

```css title="dom4.tcss"
--8<-- "docs/examples/guide/dom4.tcss"
```

The CSS contains a number of rule sets with a selector and a list of rules. You can also add comments with text between `/*` and `*/` which will be ignored by Textual. Add comments to leave yourself reminders or to temporarily disable selectors.

With the CSS in place, the output looks very different:

```{.textual path="docs/examples/guide/dom4.py"}

```

### Using multiple CSS files

You can also set the `CSS_PATH` class variable to a list of paths. Textual will combine the rules from all of the supplied paths.

### Why CSS?

It is reasonable to ask why use CSS at all? Python is a powerful and expressive language. Wouldn't it be easier to set styles in your `.py` files?

A major advantage of CSS is that it separates how your app _looks_ from how it _works_. Setting styles in Python can generate a lot of spaghetti code which can make it hard to see the important logic in your application.

A second advantage of CSS is that you can customize builtin and third-party widgets just as easily as you can your own app or widgets.

Finally, Textual CSS allows you to _live edit_ the styles in your app. If you run your application with the following command, any changes you make to the CSS file will be instantly updated in the terminal:

```bash
textual run my_app.py --dev
```

Being able to iterate on the design without restarting the application makes it easier and faster to design beautiful interfaces.

## Selectors

A selector is the text which precedes the curly braces in a set of rules. It tells Textual which widgets it should apply the rules to.

Selectors can target a kind of widget or a very specific widget. For instance, you could have a selector that modifies all buttons, or you could target an individual button used in one dialog. This gives you a lot of flexibility in customizing your user interface.

Let's look at the selectors supported by Textual CSS.

### Type selector

The _type_ selector matches the name of the (Python) class.
Consider the following widget class:

```python
from textual.widgets import Static

class Alert(Static):
    pass
```

Alert widgets may be styled with the following CSS (to give them a red border):

```css
Alert {
  border: solid red;
}
```

The type selector will also match a widget's base classes.
Consequently, a `Static` selector will also style the button because the `Alert` (Python) class extends `Static`.

```css
Static {
  background: blue;
  border: round green;
}
```

!!! note "This is different to browser CSS"

    The fact that the type selector matches base classes is a departure from browser CSS which doesn't have the same concept.

You may have noticed that the `border` rule exists in both `Static` and `Alert`.
When this happens, Textual will use the most recently defined sub-class.
So `Alert` wins over `Static`, and `Static` wins over `Widget` (the base class of all widgets).
Hence if both rules were in a stylesheet, `Alert` widgets would have a "solid red" border and not a "round green" border.

### ID selector

Every Widget can have a single `id` attribute, which is set via the constructor. The ID should be unique to its container.

Here's an example of a widget with an ID:

```python
yield Button(id="next")
```

You can match an ID with a selector starting with a hash (`#`). Here is how you might draw a red outline around the above button:

```css
#next {
  outline: red;
}
```

A Widget's `id` attribute can not be changed after the Widget has been constructed.

### Class-name selector

Every widget can have a number of class names applied. The term "class" here is borrowed from web CSS, and has a different meaning to a Python class. You can think of a CSS class as a tag of sorts. Widgets with the same tag will share styles.

CSS classes are set via the widget's `classes` parameter in the constructor. Here's an example:

```python
yield Button(classes="success")
```

This button will have a single class called `"success"` which we could target via CSS to make the button a particular color.

You may also set multiple classes separated by spaces. For instance, here is a button with both an `error` class and a `disabled` class:

```python
yield Button(classes="error disabled")
```

To match a Widget with a given class in CSS you can precede the class name with a dot (`.`). Here's a rule with a class selector to match the `"success"` class name:

```css
.success {
  background: green;
  color: white;
}
```

!!! note

    You can apply a class name to any widget, which means that widgets of different types could share classes.

Class name selectors may be _chained_ together by appending another full stop and class name. The selector will match a widget that has _all_ of the class names set. For instance, the following sets a red background on widgets that have both `error` _and_ `disabled` class names.

```css
.error.disabled {
  background: darkred;
}
```

Unlike the `id` attribute, a widget's classes can be changed after the widget was created. Adding and removing CSS classes is the recommended way of changing the display while your app is running. There are a few methods you can use to manage CSS classes.

- [add_class()][textual.dom.DOMNode.add_class] Adds one or more classes to a widget.
- [remove_class()][textual.dom.DOMNode.remove_class] Removes class name(s) from a widget.
- [toggle_class()][textual.dom.DOMNode.toggle_class] Removes a class name if it is present, or adds the name if it's not already present.
- [has_class()][textual.dom.DOMNode.has_class] Checks if one or more classes are set on a widget.
- [set_class()][textual.css.query.DOMQuery.set_class] Sets or removes a class dependant on a boolean.
- [classes][textual.dom.DOMNode.classes] Is a frozen set of the class(es) set on a widget.


### Universal selector

The _universal_ selector is denoted by an asterisk and will match _all_ widgets.

For example, the following will draw a red outline around all widgets:

```css
* {
  outline: solid red;
}
```

While it is rare to need to style all widgets, you can combine the universal selector with a parent, to select all children of that parent.

For instance, here's how we would make all children of a `VerticalScroll` have a red background:

```css
VerticalScroll * {
  background: red;
}
```

See [Combinators](#combinators) for more details on combining selectors like this.

### Pseudo classes

Pseudo classes can be used to match widgets in a particular state. Pseudo classes are set automatically by Textual. For instance, you might want a button to have a green background when the mouse cursor moves over it. We can do this with the `:hover` pseudo selector.

```css
Button:hover {
  background: green;
}
```

The `background: green` is only applied to the Button underneath the mouse cursor. When you move the cursor away from the button it will return to its previous background color.

Here are some other pseudo classes:

- `:blur` Matches widgets which *do not* have input focus.
- `:dark` Matches widgets in dark themes (where `App.theme.dark == True`).
- `:disabled` Matches widgets which are in a disabled state.
- `:empty` Matches widgets which have no displayed children.
- `:enabled` Matches widgets which are in an enabled state.
- `:even` Matches a widget at an evenly numbered position within its siblings.
- `:first-child` Matches a widget that is the first amongst its siblings.
- `:first-of-type` Matches a widget that is the first of its type amongst its siblings.
- `:focus-within` Matches widgets with a focused child widget.
- `:focus` Matches widgets which have input focus.
- `:inline` Matches widgets when the app is running in inline mode.
- `:last-child` Matches a widget that is the last amongst its siblings.
- `:last-of-type` Matches a widget that is the last of its type amongst its siblings.
- `:light` Matches widgets in light themes (where `App.theme.dark == False`).
- `:odd` Matches a widget at an oddly numbered position within its siblings.

## Combinators

More sophisticated selectors can be created by combining simple selectors. The logic used to combine selectors is know as a _combinator_.

### Descendant combinator

If you separate two selectors with a space it will match widgets with the second selector that have an ancestor that matches the first selector.

Here's a section of DOM to illustrate this combinator:

<div class="excalidraw">
--8<-- "docs/images/descendant_combinator.excalidraw.svg"
</div>

Let's say we want to make the text of the buttons in the dialog bold, but we _don't_ want to change the Button in the sidebar. We can do this with the following rule:

```css hl_lines="1"
#dialog Button {
  text-style: bold;
}
```

The `#dialog Button` selector matches all buttons that are below the widget with an ID of "dialog". No other buttons will be matched.

As with all selectors, you can combine as many as you wish. The following will match a `Button` that is under a `Horizontal` widget _and_ under a widget with an id of `"dialog"`:

```css
#dialog Horizontal Button {
  text-style: bold;
}
```

### Child combinator

The child combinator is similar to the descendant combinator but will only match an immediate child. To create a child combinator, separate two selectors with a greater than symbol (`>`). Any whitespace around the `>` will be ignored.

Let's use this to match the Button in the sidebar given the following DOM:

<div class="excalidraw">
--8<-- "docs/images/child_combinator.excalidraw.svg"
</div>

We can use the following CSS to style all buttons which have a parent with an ID of `sidebar`:

```css
#sidebar > Button {
  text-style: underline;
}
```

## Specificity

It is possible that several selectors match a given widget. If the same style is applied by more than one selector then Textual needs a way to decide which rule _wins_. It does this by following these rules:

- The selector with the most IDs wins. For instance `#next` beats `.button` and `#dialog #next` beats `#next`. If the selectors have the same number of IDs then move to the next rule.

- The selector with the most class names wins. For instance `.button.success` beats `.success`. For the purposes of specificity, pseudo classes are treated the same as regular class names, so `.button:hover` counts as _2_ class names. If the selectors have the same number of class names then move to the next rule.

- The selector with the most types wins. For instance `Container Button` beats `Button`.

### Important rules

The specificity rules are usually enough to fix any conflicts in your stylesheets. There is one last way of resolving conflicting selectors which applies to individual rules. If you add the text `!important` to the end of a rule then it will "win" regardless of the specificity.

!!! warning "If everything is Important, nothing is Important"

    Use `!important` sparingly (if at all) as it can make it difficult to modify your CSS in the future.

Here's an example that makes buttons blue when hovered over with the mouse, regardless of any other selectors that match Buttons:

```css hl_lines="2"
Button:hover {
  background: blue !important;
}
```

## CSS Variables

You can define variables to reduce repetition and encourage consistency in your CSS.
Variables in Textual CSS are prefixed with `$`.
Here's an example of how you might define a variable called `$border`:

```css
$border: wide green;
```

With our variable assigned, we can write `$border` and it will be substituted with `wide green`.
Consider the following snippet:

```css
#foo {
  border: $border;
}
```

This will be translated into:

```css
#foo {
  border: wide green;
}
```

Variables allow us to define reusable styling in a single place.
If we decide we want to change some aspect of our design in the future, we only have to update a single variable.

!!! note "Where can variables be used?"

    Variables can only be used in the _values_ of a CSS declaration. You cannot, for example, refer to a variable inside a selector.

Variables can refer to other variables.
Let's say we define a variable `$success: lime;`.
Our `$border` variable could then be updated to `$border: wide $success;`, which will
be translated to `$border: wide lime;`.

## Initial value

All CSS rules support a special value called `initial`, which will reset a value back to its default.

Let's look at an example.
The following will set the background of a button to green:

```css
Button {
  background: green;
}
```

If we want a specific button (or buttons) to use the default color, we can set the value to `initial`.
For instance, if we have a widget with a (CSS) class called `dialog`, we could reset the background color of all buttons inside the dialog with the following CSS:

```css
.dialog Button {
  background: initial;
}
```

Note that `initial` will set the value back to the value defined in any [default css](./widgets.md#default-css).
If you use `initial` within default css, it will treat the rule as completely unstyled.


## Nesting CSS

!!! tip "Added in version 0.47.0"

CSS rule sets may be *nested*, i.e. they can contain other rule sets.
When a rule set occurs within an existing rule set, it inherits the selector from the enclosing rule set.

Let's put this into practical terms.
The following example will display two boxes containing the text "Yes" and "No" respectively.
These could eventually form the basis for buttons, but for this demonstration we are only interested in the CSS.

=== "nesting01.tcss (no nesting)"

    ```css
    --8<-- "docs/examples/guide/css/nesting01.tcss"
    ```

=== "nesting01.py"

    ```python
    --8<-- "docs/examples/guide/css/nesting01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/css/nesting01.py"}
    ```

The CSS is quite straightforward; there is one rule for the container, one for all buttons, and one rule for each of the buttons.
However it is easy to imagine this stylesheet growing more rules as we add features.

Nesting allows us to group rule sets which have common selectors.
In the example above, the rules all start with `#questions`.
When we see a common prefix on the selectors, this is a good indication that we can use nesting.

The following produces identical results to the previous example, but adds nesting of the rules.

=== "nesting02.tcss (with nesting)"

    ```css
    --8<-- "docs/examples/guide/css/nesting02.tcss"
    ```

=== "nesting02.py"

    ```python
    --8<-- "docs/examples/guide/css/nesting02.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/css/nesting02.py"}
    ```

!!! tip

    Indenting the rule sets is not strictly required, but it does make it easier to understand how the rule sets are related to each other.

In the first example we had a rule set that began with the selector `#questions .button`, which would match any widget with a class called "button" that is inside a container with id `questions`.

In the second example, the button rule selector is simply `.button`, but it is *within* the rule set with selector `#questions`.
The nesting means that the button rule set will inherit the selector from the outer rule set, so it is equivalent to `#questions .button`.

### Nesting selector

The two remaining rules are nested within the button rule, which means they will inherit their selectors from the button rule set *and* the outer `#questions` rule set.

You may have noticed that the rules for the button styles contain a syntax we haven't seen before.
The rule for the Yes button is `&.affirmative`.
The ampersand (`&`) is known as the *nesting selector* and it tells Textual that the selector should be combined with the selector from the outer rule set.

So `&.affirmative` in the example above, produces the equivalent of `#questions .button.affirmative` which selects a widget with both the `button` and `affirmative` classes.
Without `&` it would be equivalent to `#questions .button .affirmative` (note the additional space) which would only match a widget with class `affirmative` inside a container with class `button`.


For reference, lets see those two CSS files side-by-side:

=== "nesting01.tcss"

    ```css
    --8<-- "docs/examples/guide/css/nesting01.tcss"
    ```

=== "nesting02.tcss"

    ```sass
    --8<-- "docs/examples/guide/css/nesting02.tcss"
    ```


Note how nesting bundles related rules together.
If we were to add other selectors for additional screens or widgets, it would be easier to find the rules which will be applied.

### Why use nesting?

There is no requirement to use nested CSS, but grouping related rules together avoids repetition (in the nested CSS we only need to type `#questions` once, rather than four times in the non-nested CSS).

Nesting CSS will also make rules that are *more* specific.
This is useful if you find your rules are applying to widgets that you didn't intend.
````

## File: docs/guide/design.md
````markdown
# Themes

Textual comes with several built-in *themes*, and it's easy to create your own.
A theme provides variables which can be used in the CSS of your app.
Click on the tabs below to see how themes can change the appearance of an app.

=== "nord"

    ```{.textual path="docs/examples/themes/todo_app.py"}
    ```

=== "gruvbox"

    ```{.textual path="docs/examples/themes/todo_app.py" press="ctrl+t"}
    ```

=== "tokyo-night"

    ```{.textual path="docs/examples/themes/todo_app.py" press="ctrl+t,ctrl+t"}
    ```

=== "textual-dark"

    ```{.textual path="docs/examples/themes/todo_app.py" press="ctrl+t,ctrl+t,ctrl+t"}
    ```

=== "solarized-light"

    ```{.textual path="docs/examples/themes/todo_app.py" press="ctrl+t,ctrl+t,ctrl+t,ctrl+t"}
    ```

## Changing the theme

The theme can be changed at runtime via the [Command Palette](./command_palette.md) (++ctrl+p++).

You can also programmatically change the theme by setting the value of `App.theme` to the name of a theme:

```python
class MyApp(App):
    def on_mount(self) -> None:
        self.theme = "nord"
```

A theme must be *registered* before it can be used.
Textual comes with a selection of built-in themes which are registered by default.

## Registering a theme

A theme is a simple Python object which maps variable names to colors.
Here's an example:

```python
from textual.theme import Theme

arctic_theme = Theme(
    name="arctic",
    primary="#88C0D0",
    secondary="#81A1C1",
    accent="#B48EAD",
    foreground="#D8DEE9",
    background="#2E3440",
    success="#A3BE8C",
    warning="#EBCB8B",
    error="#BF616A",
    surface="#3B4252",
    panel="#434C5E",
    dark=True,
    variables={
        "block-cursor-text-style": "none",
        "footer-key-foreground": "#88C0D0",
        "input-selection-background": "#81a1c1 35%",
    },
)
```

You can register this theme by calling `App.register_theme` in the `on_mount` method of your `App`.

```python
from textual.app import App

class MyApp(App):
    def on_mount(self) -> None:
        # Register the theme
        self.register_theme(arctic_theme)  # (1)!

        # Set the app's theme
        self.theme = "arctic"  # (2)!
```

1. Register the theme, making it available to the app (and command palette)
2. Set the app's theme. When this line runs, the app immediately refreshes to use the new theme.

## Theme variables

Themes consist of up to 11 *base colors*, (`primary`, `secondary`, `accent`, etc.), which Textual uses to generate a broad range of CSS variables.
For example, the `textual-dark` theme defines the *primary* base color as `#004578`.

Here's an example of CSS which uses these variables:

```css
MyWidget {
    background: $primary;
    color: $foreground;
}
```

On changing the theme, the values stored in these variables are updated to match the new theme, and the colors of `MyWidget` are updated accordingly.

## Base colors

When defining a theme, only the `primary` color is required.
Textual will attempt to generate the other base colors if they're not supplied.

The following table lists each of 11 base colors (as used in CSS) and a description of where they are used by default.

| Color                   | Description                                                                                                                                         |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$primary`              | The primary color, can be considered the *branding* color. Typically used for titles, and backgrounds for strong emphasis.                          |
| `$secondary`            | An alternative branding color, used for similar purposes as `$primary`, where an app needs to differentiate something from the primary color.       |
| `$foreground`           | The default text color, which should be legible on `$background`, `$surface`, and `$panel`.                                                         |
| `$background`           | A color used for the background, where there is no content. Used as the default background color for screens.                                       |
| `$surface`              | The default background color of widgets, typically sitting on top of `$background`.                                                                 |
| `$panel`                | A color used to differentiate a part of the UI form the main content. Used sparingly in Textual itself.                                             |
| `$boost`                | A color with alpha that can be used to create *layers* on a background.                                                                             |
| `$warning`              | Indicates a warning. Typically used as a background color. `$text-warning` can be used for foreground.                                                                                                            |
| `$error`                | Indicates an error. Typically used as a background color. `$text-error` can be used for foreground.                                                                                                             |
| `$success`              | Used to indicate success. Typically used as a background color. `$text-success` can be used for foreground.                                                                                                      |
| `$accent`               | Used sparingly to draw attention. Typically contrasts with `$primary` and `$secondary`.                                                                 |

## Shades

For every color, Textual generates 3 dark shades and 3 light shades.

- Add `-lighten-1`, `-lighten-2`, or `-lighten-3` to the color's variable name to get lighter shades (3 is the lightest).
- Add `-darken-1`, `-darken-2`, and `-darken-3` to a color to get the darker shades (3 is the darkest).

For example, `$secondary-darken-1` is a slightly darkened `$secondary`, and `$error-lighten-3` is a very light version of the `$error` color.

## Light and dark themes

Themes can be either *light* or *dark*.
This setting is specified in the `Theme` constructor via the `dark` argument, and influences how Textual
generates variables.
Built-in widgets may also use the value of `dark` to influence their appearance.

## Text color

The default color of text in a theme is `$foreground`.
This color should be legible on `$background`, `$surface`, and `$panel` backgrounds.

There is also `$foreground-muted` for text which has lower importance.
`$foreground-disabled` can be used for text which is disabled, for example a menu item which can't be selected.

You can set the text color via the [color](../styles/color.md) CSS property.

The available text colors are:

- `$text-primary`
- `$text-secondary`
- `$text-accent`
- `$text-warning`
- `$text-error`
- `$text-success`

### Ensuring text legibility

In some cases, the background color of a widget is unpredictable, so we cannot be certain our text will be readable against it.

The theme system defines three CSS variables which you can use to ensure that text is legible on any background.

- `$text` is set to a slightly transparent black or white, depending on which has better contrast against the background the text is on.
- `$text-muted` sets a slightly faded text color. Use this for text which has lower importance. For instance a sub-title or supplementary information.
- `$text-disabled` sets faded out text which indicates it has been disabled. For instance, menu items which are not applicable and can't be clicked.

### Colored text

Colored text is also generated from the base colors, which is guaranteed to be legible against a background of `$background`, `$surface`, and `$panel`.
For example, `$text-primary` is a version of the `$primary` color tinted to ensure legibility.

=== "Output (Theme: textual-dark)"

    ```{.textual path="docs/examples/themes/colored_text.py" lines="9" columns="30"}
    ```

=== "colored_text.py"

    ```python title="colored_text.py"
    --8<-- "docs/examples/themes/colored_text.py"
    ```

These colors are also be guaranteed to be legible when used as the foreground color of a widget with a *muted color* background.

## Muted colors

Muted colors are generated from the base colors by blending them with `$background` at 70% opacity.
For example, `$primary-muted` is a muted version of the `$primary` color.

Textual aims to ensure that the colored text it generates is legible against the corresponding muted color.
In other words, `$text-primary` text should be legible against a background of `$primary-muted`:

=== "Output (Theme: textual-dark)"

    ```{.textual path="docs/examples/themes/muted_backgrounds.py" lines="9" columns="40"}
    ```

=== "muted_backgrounds.py"

    ```python title="muted_backgrounds.py"
    --8<-- "docs/examples/themes/muted_backgrounds.py"
    ```

The available muted colors are:

- `$primary-muted`
- `$secondary-muted`
- `$accent-muted`
- `$warning-muted`
- `$error-muted`
- `$success-muted`

## Additional variables

Textual uses the base colors as default values for additional variables used throughout the framework.
These variables can be overridden by passing a `variables` argument to the `Theme` constructor.
This also allows you to override variables such as `$primary-muted`, described above.

In the Gruvbox theme, for example, we override the foreground color of the block cursor (the cursor used in widgets like `OptionList`) to be `$foreground`.

```python hl_lines="14-17"
Theme(
    name="gruvbox",
    primary="#85A598",
    secondary="#A89A85",
    warning="#fabd2f",
    error="#fb4934",
    success="#b8bb26",
    accent="#fabd2f",
    foreground="#fbf1c7",
    background="#282828",
    surface="#3c3836",
    panel="#504945",
    dark=True,
    variables={
        "block-cursor-foreground": "#fbf1c7",
        "input-selection-background": "#689d6a40",
    },
)
```

Here's a comprehensive list of these variables, their purposes, and default values:

### Border

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$border` | The border color for focused widgets with a border | `$primary` |
| `$border-blurred` | The border color for unfocused widgets | Slightly darkened `$surface` |

### Cursor

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$block-cursor-foreground` | Text color for block cursor (e.g., in OptionList) | `$text` |
| `$block-cursor-background` | Background color for block cursor | `$primary` |
| `$block-cursor-text-style` | Text style for block cursor | `"bold"` |
| `$block-cursor-blurred-foreground` | Text color for unfocused block cursor | `$text` |
| `$block-cursor-blurred-background` | Background color for unfocused block cursor | `$primary` with 30% opacity |
| `$block-cursor-blurred-text-style` | Text style for unfocused block cursor | `"none"` |
| `$block-hover-background` | Background color when hovering over a block | `$boost` with 5% opacity |

### Input

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$input-cursor-background` | Background color of the input cursor | `$foreground` |
| `$input-cursor-foreground` | Text color of the input cursor | `$background` |
| `$input-cursor-text-style` | Text style of the input cursor | `"none"` |
| `$input-selection-background` | Background color of selected text | `$primary-lighten-1` with 40% opacity |

### Scrollbar

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$scrollbar` | Color of the scrollbar | `$panel` |
| `$scrollbar-hover` | Color of the scrollbar when hovered | `$panel-lighten-1` |
| `$scrollbar-active` | Color of the scrollbar when active (being dragged) | `$panel-lighten-2` |
| `$scrollbar-background` | Color of the scrollbar track | `$background-darken-1` |
| `$scrollbar-corner-color` | Color of the scrollbar corner | Same as `$scrollbar-background` |
| `$scrollbar-background-hover` | Color of the scrollbar track when hovering over the scrollbar area | Same as `$scrollbar-background` |
| `$scrollbar-background-active` | Color of the scrollbar track when the scrollbar is active | Same as `$scrollbar-background` |

### Links

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$link-background` | Background color of links | `"initial"` |
| `$link-background-hover` | Background color of links when hovered | `$primary` |
| `$link-color` | Text color of links | `$text` |
| `$link-style` | Text style of links | `"underline"` |
| `$link-color-hover` | Text color of links when hovered | `$text` |
| `$link-style-hover` | Text style of links when hovered | `"bold not underline"` |

### Footer

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$footer-foreground` | Text color in the footer | `$foreground` |
| `$footer-background` | Background color of the footer | `$panel` |
| `$footer-key-foreground` | Text color for key bindings in the footer | `$accent` |
| `$footer-key-background` | Background color for key bindings in the footer | `"transparent"` |
| `$footer-description-foreground` | Text color for descriptions in the footer | `$foreground` |
| `$footer-description-background` | Background color for descriptions in the footer | `"transparent"` |
| `$footer-item-background` | Background color for items in the footer | `"transparent"` |

### Button

| Variable | Purpose | Default Value |
|----------|---------|---------------|
| `$button-foreground` | Foreground color for standard buttons | `$foreground` |
| `$button-color-foreground` | Foreground color for colored buttons | `$text` |
| `$button-focus-text-style` | Text style for focused buttons | `"bold reverse"` |

## App-specific variables

The variables above are defined and used by Textual itself.
However, you may also wish to expose other variables which are specific to your application.

You can do this by overriding `App.get_theme_variable_defaults` in your `App` subclass.

This method should return a dictionary of variable names and their default values.
If a variable defined in this dictionary is also defined in a theme's `variables` dictionary, the theme's value will be used.

## Previewing colors

Run the following from the command line to preview the colors defined in the color system:

```bash
textual colors
```

Inside the preview you can change the theme via the Command Palette (++ctrl+p++), and view the base variables and shades generated from the theme.
````

## File: docs/guide/devtools.md
````markdown
# Devtools

!!! note inline end

    If you don't have the `textual` command on your path, you may have forgotten to install the `textual-dev` package.

    See [getting started](../getting_started.md#installation) for details.

Textual comes with a command line application of the same name. The `textual` command is a super useful tool that will help you to build apps.

Take a moment to look through the available subcommands. There will be even more helpful tools here in the future.

```bash
textual --help
```


## Run

The `run` sub-command runs Textual apps. If you supply a path to a Python file it will load and run the app.

```bash
textual run my_app.py
```

This is equivalent to running `python my_app.py` from the command prompt, but will allow you to set various switches which can help you debug, such as `--dev` which enable the [Console](#console).

See the `run` subcommand's help for details:

```bash
textual run --help
```

You can also run Textual apps from a python import.
The following command would import `music.play` and run a Textual app in that module:

```bash
textual run music.play
```

This assumes you have a Textual app instance called `app` in `music.play`.
If your app has a different name, you can append it after a colon:

```bash
textual run music.play:MusicPlayerApp
```

!!! note

    This works for both Textual app *instances* and *classes*.


### Running from commands

If your app is installed as a command line script, you can use the `-c` switch to run it.
For instance, the following will run the `textual colors` command:

```bash
textual run -c textual colors
```

## Serve

The devtools can also serve your application in a browser.
Effectively turning your terminal app into a web application!

The `serve` sub-command is similar to `run`. Here's how you can serve an app launched from a Python file:

```
textual serve my_app.py
```

You can also serve a Textual app launched via a command. Here's an example:

```
textual serve "textual keys"
```

The syntax for launching an app in a module is slightly different from `run`.
You need to specify the full command, including `python`.
Here's how you would run the Textual demo:

```
textual serve "python -m textual"
```

Textual's builtin web-server is quite powerful.
You can serve multiple instances of your application at once!

!!! tip

    Textual serve is also useful when developing your app.
    If you make changes to your code, simply refresh the browser to update.

There are some additional switches for serving Textual apps. Run the following for a list:

```
textual serve --help
```

## Live editing

If you combine the `run` command with the `--dev` switch your app will run in *development mode*.

```bash
textual run --dev my_app.py
```

One of the features of *dev* mode is live editing of CSS files: any changes to your CSS will be reflected in the terminal a few milliseconds later.

This is a great feature for iterating on your app's look and feel. Open the CSS in your editor and have your app running in a terminal. Edits to your CSS will appear almost immediately after you save.

## Console

When building a typical terminal application you are generally unable to use `print` when debugging (or log to the console). This is because anything you write to standard output will overwrite application content. Textual has a solution to this in the form of a debug console which restores `print` and adds a few additional features to help you debug.

To use the console, open up **two** terminal emulators. Run the following in one of the terminals:

```bash
textual console
```

You should see the Textual devtools welcome message:

```{.textual title="textual console" path="docs/examples/getting_started/console.py"}
```

In the other console, run your application with `textual run` and the `--dev` switch:

```bash
textual run --dev my_app.py
```

Anything you `print` from your application will be displayed in the console window. Textual will also write log messages to this window which may be helpful when debugging your application.


### Increasing verbosity

Textual writes log messages to inform you about certain events, such as when the user presses a key or clicks on the terminal. To avoid swamping you with too much information, some events are marked as "verbose" and will be excluded from the logs. If you want to see these log messages, you can add the `-v` switch.

```bash
textual console -v
```

### Decreasing verbosity

Log messages are classififed into groups, and the `-x` flag can be used to **exclude** all message from a group. The groups are: `EVENT`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `PRINT`, `SYSTEM`, `LOGGING` and `WORKER`. The group a message belongs to is printed after its timestamp.

Multiple groups may be excluded, for example to exclude everything except warning, errors, and `print` statements:

```bash
textual console -x SYSTEM -x EVENT -x DEBUG -x INFO
```

### Custom port

You can use the option `--port` to specify a custom port to run the console on, which comes in handy if you have other software running on the port that Textual uses by default:

```bash
textual console --port 7342
```

Then, use the command `run` with the same `--port` option:

```bash
textual run --dev --port 7342 my_app.py
```


## Textual log

Use the `log` function to pretty-print data structures and anything that [Rich](https://rich.readthedocs.io/en/latest/) can display.

You can import the log function as follows:

```python
from textual import log
```

Here's a few examples of writing to the console, with `log`:



```python
def on_mount(self) -> None:
    log("Hello, World")  # simple string
    log(locals())  # Log local variables
    log(children=self.children, pi=3.141592)  # key/values
    log(self.tree)  # Rich renderables
```

### Log method

There's a convenient shortcut to `log` on the `App` and `Widget` objects. This is useful in event handlers. Here's an example:

```python
from textual.app import App

class LogApp(App):

    def on_load(self):
        self.log("In the log handler!", pi=3.141529)

    def on_mount(self):
        self.log(self.tree)

if __name__ == "__main__":
    LogApp().run()
```

## Logging handler

Textual has a [logging handler][textual.logging.TextualHandler] which will write anything logged via the builtin logging library to the devtools.
This may be useful if you have a third-party library that uses the logging module, and you want to see those logs with Textual logs.

!!! note

    The logging library works with strings only, so you won't be able to log Rich renderables such as `self.tree` with the logging handler.

Here's an example of configuring logging to use the `TextualHandler`.

```python
import logging
from textual.app import App
from textual.logging import TextualHandler

logging.basicConfig(
    level="NOTSET",
    handlers=[TextualHandler()],
)


class LogApp(App):
    """Using logging with Textual."""

    def on_mount(self) -> None:
        logging.debug("Logged via TextualHandler")


if __name__ == "__main__":
    LogApp().run()
```
````

## File: docs/guide/events.md
````markdown
# Events and Messages

We've used event handler methods in many of the examples in this guide. This chapter explores [events](../events/index.md) and messages (see below) in more detail.

## Messages

Events are a particular kind of *message* sent by Textual in response to input and other state changes. Events are reserved for use by Textual, but you can also create custom messages for the purpose of coordinating between widgets in your app.

More on that later, but for now keep in mind that events are also messages, and anything that is true of messages is true of events.

## Message Queue

Every [App][textual.app.App] and [Widget][textual.widget.Widget] object contains a *message queue*. You can think of a message queue as orders at a restaurant. The chef takes an order and makes the dish. Orders that arrive while the chef is cooking are placed in a line. When the chef has finished a dish they pick up the next order in the line.

Textual processes messages in the same way. Messages are picked off a queue and processed (cooked) by a handler method. This guarantees messages and events are processed even if your code can not handle them right away.

This processing of messages is done within an asyncio Task which is started when you mount the widget. The task monitors a queue for new messages and dispatches them to the appropriate handler when they arrive.

!!! tip

    The FastAPI docs have an [excellent introduction](https://fastapi.tiangolo.com/async/) to Python async programming.

By way of an example, let's consider what happens if you were to type "Text" into a `Input` widget. When you hit the ++t++ key, Textual creates a [key][textual.events.Key] event and sends it to the widget's message queue. Ditto for ++e++, ++x++, and ++t++.

The widget's task will pick the first message from the queue (a key event for the ++t++ key) and call the `on_key` method with the event as the first argument. In other words it will call `Input.on_key(event)`, which updates the display to show the new letter.

<div class="excalidraw">
--8<-- "docs/images/events/queue.excalidraw.svg"
</div>

When the `on_key` method returns, Textual will get the next event from the queue and repeat the process for the remaining keys. At some point the queue will be empty and the widget is said to be in an *idle* state.

!!! note

    This example illustrates a point, but a typical app will be fast enough to have processed a key before the next event arrives. So it is unlikely you will have so many key events in the message queue.

<div class="excalidraw">
--8<-- "docs/images/events/queue2.excalidraw.svg"
</div>


## Default behaviors

You may be familiar with Python's [super](https://docs.python.org/3/library/functions.html#super) function to call a function defined in a base class. You will not have to use this in event handlers as Textual will automatically call handler methods defined in a widget's base class(es).

For instance, let's say we are building the classic game of Pong and we have written a `Paddle` widget which extends [Static][textual.widgets.Static]. When a [Key][textual.events.Key] event arrives, Textual calls `Paddle.on_key` (to respond to ++up++ and ++down++ keys), then `Static.on_key`, and finally `Widget.on_key`.

### Preventing default behaviors

If you don't want this behavior you can call [prevent_default()][textual.message.Message.prevent_default] on the event object. This tells Textual not to call any more handlers on base classes.

!!! warning

    You won't need `prevent_default` very often. Be sure to know what your base classes do before calling it, or you risk disabling some core features builtin to Textual.

## Bubbling

Messages have a `bubble` attribute. If this is set to `True` then events will be sent to a widget's parent after processing. Input events typically bubble so that a widget will have the opportunity to respond to input events if they aren't handled by their children.

The following diagram shows an (abbreviated) DOM for a UI with a container and two buttons. With the "No" button [focused](#), it will receive the key event first.

<div class="excalidraw">
--8<-- "docs/images/events/bubble1.excalidraw.svg"
</div>

After Textual calls `Button.on_key` the event _bubbles_ to the button's parent and will call `Container.on_key` (if it exists).

<div class="excalidraw">
--8<-- "docs/images/events/bubble2.excalidraw.svg"
</div>

As before, the event bubbles to its parent (the App class).

<div class="excalidraw">
--8<-- "docs/images/events/bubble3.excalidraw.svg"
</div>

The App class is always the root of the DOM, so there is nowhere for the event to bubble to.

### Stopping bubbling

Event handlers may stop this bubble behavior by calling the [stop()][textual.message.Message.stop] method on the event or message. You might want to do this if a widget has responded to the event in an authoritative way. For instance when a text input widget responds to a key event it stops the bubbling so that the key doesn't also invoke a key binding.

## Custom messages

You can create custom messages for your application that may be used in the same way as events (recall that events are simply messages reserved for use by Textual).

The most common reason to do this is if you are building a custom widget and you need to inform a parent widget about a state change.

Let's look at an example which defines a custom message. The following example creates color buttons which&mdash;when clicked&mdash;send a custom message.

=== "custom01.py"

    ```python title="custom01.py" hl_lines="10-15 27-29 42-43"
    --8<-- "docs/examples/events/custom01.py"
    ```
=== "Output"

    ```{.textual path="docs/examples/events/custom01.py"}
    ```


Note the custom message class which extends [Message][textual.message.Message]. The constructor stores a [color][textual.color.Color] object which handler methods will be able to inspect.

The message class is defined within the widget class itself. This is not strictly required but recommended, for these reasons:

- It reduces the amount of imports. If you import `ColorButton`, you have access to the message class via `ColorButton.Selected`.
- It creates a namespace for the handler. So rather than `on_selected`, the handler name becomes `on_color_button_selected`. This makes it less likely that your chosen name will clash with another message.

### Sending messages

To send a message call the [post_message()][textual.message_pump.MessagePump.post_message] method. This will place a message on the widget's message queue and run any message handlers.

It is common for widgets to send messages to themselves, and allow them to bubble. This is so a base class has an opportunity to handle the message. We do this in the example above, which means a subclass could add a `on_color_button_selected` if it wanted to handle the message itself.

## Preventing messages

You can *temporarily* disable posting of messages of a particular type by calling [prevent][textual.message_pump.MessagePump.prevent], which returns a context manager (used with Python's `with` keyword). This is typically used when updating data in a child widget and you don't want to receive notifications that something has changed.

The following example will play the terminal bell as you type. It does this by handling [Input.Changed][textual.widgets.Input.Changed] and calling [bell()][textual.app.App.bell]. There is a Clear button which sets the input's value to an empty string. This would normally also result in a `Input.Changed` event being sent (and the bell playing). Since we don't want the button to make a sound, the assignment to `value` is wrapped within a [prevent][textual.message_pump.MessagePump.prevent] context manager.

!!! tip

    In reality, playing the terminal bell as you type would be very irritating -- we don't recommend it!

=== "prevent.py"

    ```python title="prevent.py"
    --8<-- "docs/examples/events/prevent.py"
    ```

    1. Clear the input without sending an Input.Changed event.
    2. Plays the terminal sound when typing.

=== "Output"

    ```{.textual path="docs/examples/events/prevent.py"}
    ```



## Message handlers

Most of the logic in a Textual app will be written in message handlers. Let's explore handlers in more detail.

### Handler naming

Textual uses the following scheme to map messages classes on to a Python method.

- Start with `"on_"`.
- Add the message's namespace (if any) converted from CamelCase to snake_case plus an underscore `"_"`.
- Add the name of the class converted from CamelCase to snake_case.

<div class="excalidraw">
--8<-- "docs/images/events/naming.excalidraw.svg"
</div>

Messages have a namespace if they are defined as a child class of a Widget.
The namespace is the name of the parent class.
For instance, the builtin `Input` class defines its `Changed` message as follows:

```python
class Input(Widget):
    ...
    class Changed(Message):
        """Posted when the value changes."""
        ...
```

Because `Changed` is a *child* class of `Input`, its namespace will be "input" (and the handler name will be `on_input_changed`).
This allows you to have similarly named events, without clashing event handler names.

!!! tip

    If you are ever in doubt about what the handler name should be for a given event, print the `handler_name` class variable for your event class.

    Here's how you would check the handler name for the `Input.Changed` event:

    ```py
    >>> from textual.widgets import Input
    >>> Input.Changed.handler_name
    'on_input_changed'
    ```

### On decorator

In addition to the naming convention, message handlers may be created with the [`on`][textual.on] decorator, which turns a method into a handler for the given message or event.

For instance, the two methods declared below are equivalent:

```python
@on(Button.Pressed)
def handle_button_pressed(self):
    ...

def on_button_pressed(self):
    ...
```

While this allows you to name your method handlers anything you want, the main advantage of the decorator approach over the naming convention is that you can specify *which* widget(s) you want to handle messages for.

Let's first explore where this can be useful.
In the following example we have three buttons, each of which does something different; one plays the bell, one toggles dark mode, and the other quits the app.

=== "on_decorator01.py"

    ```python title="on_decorator01.py"
    --8<-- "docs/examples/events/on_decorator01.py"
    ```

    1. The message handler is called when any button is pressed

=== "on_decorator.tcss"

    ```css title="on_decorator.tcss"
    --8<-- "docs/examples/events/on_decorator.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/events/on_decorator01.py"}
    ```

Note how the message handler has a chained `if` statement to match the action to the button.
While this works just fine, it can be a little hard to follow when the number of buttons grows.

The `on` decorator takes a [CSS selector](./CSS.md#selectors) in addition to the event type which will be used to select which controls the handler should work with.
We can use this to write a handler per control rather than manage them all in a single handler.

The following example uses the decorator approach to write individual message handlers for each of the three buttons:

=== "on_decorator02.py"

    ```python title="on_decorator02.py"
    --8<-- "docs/examples/events/on_decorator02.py"
    ```

    1. Matches the button with an id of "bell" (note the `#` to match the id)
    2. Matches the button with class names "toggle" *and* "dark"
    3. Matches the button with an id of "quit"

=== "on_decorator.tcss"

    ```css title="on_decorator.tcss"
    --8<-- "docs/examples/events/on_decorator.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/events/on_decorator02.py"}
    ```

While there are a few more lines of code, it is clearer what will happen when you click any given button.

Note that the decorator requires that the message class has a `control` property which should return the widget associated with the message.
Messages from builtin controls will have this attribute, but you may need to add a `control` property to any [custom messages](#custom-messages) you write.

!!! note

    If multiple decorated handlers match the message, then they will *all* be called in the order they are defined.

    The naming convention handler will be called *after* any decorated handlers.

#### Applying CSS selectors to arbitrary attributes

The `on` decorator also accepts selectors as keyword arguments that may be used to match other attributes in a Message, provided those attributes are in [`Message.ALLOW_SELECTOR_MATCH`][textual.message.Message.ALLOW_SELECTOR_MATCH].

The snippet below shows how to match the message [`TabbedContent.TabActivated`][textual.widgets.TabbedContent.TabActivated] only when the tab with id `home` was activated:

```py
@on(TabbedContent.TabActivated, pane="#home")
def home_tab(self) -> None:
    self.log("Switched back to home tab.")
    ...
```

### Handler arguments

Message handler methods can be written with or without a positional argument. If you add a positional argument, Textual will call the handler with the event object. The following handler (taken from `custom01.py` above) contains a `message` parameter. The body of the code makes use of the message to set a preset color.

```python
    def on_color_button_selected(self, message: ColorButton.Selected) -> None:
        self.screen.styles.animate("background", message.color, duration=0.5)
```

A similar handler can be written using the decorator `on`:

```python
    @on(ColorButton.Selected)
    def animate_background_color(self, message: ColorButton.Selected) -> None:
        self.screen.styles.animate("background", message.color, duration=0.5)
```

If the body of your handler doesn't require any information in the message you can omit it from the method signature. If we just want to play a bell noise when the button is clicked, we could write our handler like this:

```python
    def on_color_button_selected(self) -> None:
        self.app.bell()
```

This pattern is a convenience that saves writing out a parameter that may not be used.

### Async handlers

Message handlers may be coroutines. If you prefix your handlers with the `async` keyword, Textual will `await` them. This lets your handler use the `await` keyword for asynchronous APIs.

If your event handlers are coroutines it will allow multiple events to be processed concurrently, but bear in mind an individual widget (or app) will not be able to pick up a new message from its message queue until the handler has returned. This is rarely a problem in practice; as long as handlers return within a few milliseconds the UI will remain responsive. But slow handlers might make your app hard to use.

!!! info

    To re-use the chef analogy, if an order comes in for beef wellington (which takes a while to cook), orders may start to pile up and customers may have to wait for their meal. The solution would be to have another chef work on the wellington while the first chef picks up new orders.

Network access is a common cause of slow handlers. If you try to retrieve a file from the internet, the message handler may take anything up to a few seconds to return, which would prevent the widget or app from updating during that time. The solution is to launch a new asyncio task to do the network task in the background.

Let's look at an example which looks up word definitions from an [api](https://dictionaryapi.dev/) as you type.

!!! note

    You will need to install [httpx](https://www.python-httpx.org/) with `pip install httpx` to run this example.

=== "dictionary.py"

    ```python title="dictionary.py" hl_lines="28"
    --8<-- "docs/examples/events/dictionary.py"
    ```
=== "dictionary.tcss"

    ```css title="dictionary.tcss"
    --8<-- "docs/examples/events/dictionary.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/events/dictionary.py"}
    ```

Note the highlighted line in the above code which calls `asyncio.create_task` to run a coroutine in the background. Without this you would find typing into the text box to be unresponsive.
````

## File: docs/guide/index.md
````markdown
# Guide

Welcome to the Textual Guide! An in-depth reference on how to build apps with Textual.

## Example code

Most of the code in this guide is fully working&mdash;you could cut and paste it if you wanted to.

Although it is probably easier to check out the [Textual repository](https://github.com/Textualize/textual) and navigate to the `docs/examples/guide` directory and run the examples from there.
````

## File: docs/guide/input.md
````markdown
# Input

This chapter will discuss how to make your app respond to input in the form of key presses and mouse actions.

!!! quote

    More Input!

    &mdash; Johnny Five

## Keyboard input

The most fundamental way to receive input is via [Key][textual.events.Key] events which are sent to your app when the user presses a key. Let's write an app to show key events as you type.

=== "key01.py"

    ```python title="key01.py" hl_lines="12-13"
    --8<-- "docs/examples/guide/input/key01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/input/key01.py", press="T,e,x,t,u,a,l,!"}
    ```

When you press a key, the app will receive the event and write it to a [RichLog](../widgets/rich_log.md) widget. Try pressing a few keys to see what happens.

!!! tip

    For a more feature rich version of this example, run `textual keys` from the command line.

### Key Event

The key event contains the following attributes which your app can use to know how to respond.

#### key

The `key` attribute is a string which identifies the key that was pressed. The value of `key` will be a single character for letters and numbers, or a longer identifier for other keys.

Some keys may be combined with the ++shift++ key. In the case of letters, this will result in a capital letter as you might expect. For non-printable keys, the `key` attribute will be prefixed with `shift+`. For example, ++shift+home++ will produce an event with `key="shift+home"`.

Many keys can also be combined with ++ctrl++ which will prefix the key with `ctrl+`. For instance, ++ctrl+p++ will produce an event with `key="ctrl+p"`.

!!! warning

    Not all keys combinations are supported in terminals and some keys may be intercepted by your OS. If in doubt, run `textual keys` from the command line.

#### character

If the key has an associated printable character, then `character` will contain a string with a single Unicode character. If there is no printable character for the key (such as for function keys) then `character` will be `None`.

For example the ++p++ key will produce `character="p"` but ++f2++ will produce `character=None`.

#### name

The `name` attribute is similar to `key` but, unlike `key`, is guaranteed to be valid within a Python function name. Textual derives `name` from the `key` attribute by lower casing it and replacing `+` with `_`. Upper case letters are prefixed with `upper_` to distinguish them from lower case names.

For example, ++ctrl+p++ produces `name="ctrl_p"` and ++shift+p++ produces `name="upper_p"`.

#### is_printable

The `is_printable` attribute is a boolean which indicates if the key would typically result in something that could be used in an input widget. If `is_printable` is `False` then the key is a control code or function key that you wouldn't expect to produce anything in an input.

#### aliases

Some keys or combinations of keys can produce the same event. For instance, the ++tab++ key is indistinguishable from ++ctrl+i++ in the terminal. For such keys, Textual events will contain a list of the possible keys that may have produced this event. In the case of ++tab++, the `aliases` attribute will contain `["tab", "ctrl+i"]`


### Key methods

Textual offers a convenient way of handling specific keys. If you create a method beginning with `key_` followed by the key name (the event's `name` attribute), then that method will be called in response to the key press.

Let's add a key method to the example code.

```python title="key02.py" hl_lines="15-16"
--8<-- "docs/examples/guide/input/key02.py"
```

Note the addition of a `key_space` method which is called in response to the space key, and plays the terminal bell noise.

!!! note

    Consider key methods to be a convenience for experimenting with Textual features. In nearly all cases, key [bindings](#bindings) and [actions](../guide/actions.md) are preferable.

## Input focus

Only a single widget may receive key events at a time. The widget which is actively receiving key events is said to have input _focus_.

The following example shows how focus works in practice.

=== "key03.py"

    ```python title="key03.py" hl_lines="16-20"
    --8<-- "docs/examples/guide/input/key03.py"
    ```

=== "key03.tcss"

    ```css title="key03.tcss" hl_lines="15-17"
    --8<-- "docs/examples/guide/input/key03.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/input/key03.py", press="H,e,l,l,o,tab,W,o,r,l,d,!"}
    ```

The app splits the screen into quarters, with a `RichLog` widget in each quarter. If you click any of the text logs, you should see that it is highlighted to show that the widget has focus. Key events will be sent to the focused widget only.

!!! tip

    the `:focus` CSS pseudo-selector can be used to apply a style to the focused widget.

You can move focus by pressing the ++tab++ key to focus the next widget. Pressing ++shift+tab++ moves the focus in the opposite direction.

### Focusable widgets

Each widget has a boolean `can_focus` attribute which determines if it is capable of receiving focus.
Note that `can_focus=True` does not mean the widget will _always_ be focusable.
For example, a disabled widget cannot receive focus even if `can_focus` is `True`.

### Controlling focus

Textual will handle keyboard focus automatically, but you can tell Textual to focus a widget by calling the widget's [focus()][textual.widget.Widget.focus] method.
By default, Textual will focus the first focusable widget when the app starts.

### Focus events

When a widget receives focus, it is sent a [Focus](../events/focus.md) event. When a widget loses focus it is sent a [Blur](../events/blur.md) event.

## Bindings

Keys may be associated with [actions](../guide/actions.md) for a given widget. This association is known as a key _binding_.

To create bindings, add a `BINDINGS` class variable to your app or widget. This should be a list of tuples of three strings.
The first value is the key, the second is the action, the third value is a short human readable description.

The following example binds the keys ++r++, ++g++, and ++b++ to an action which adds a bar widget to the screen.

=== "binding01.py"

    ```python title="binding01.py" hl_lines="12-16"
    --8<-- "docs/examples/guide/input/binding01.py"
    ```

=== "binding01.tcss"

    ```css title="binding01.tcss"
    --8<-- "docs/examples/guide/input/binding01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/input/binding01.py", press="r,g,b,b"}
    ```

Note how the footer displays bindings and makes them clickable.

!!! tip

    Multiple keys can be bound to a single action by comma-separating them.
    For example, `("r,t", "add_bar('red')", "Add Red")` means both ++r++ and ++t++ are bound to `add_bar('red')`.

When you press a key, Textual will first check for a matching binding in the `BINDINGS` list of the currently focused widget.
If no match is found, it will search upwards through the DOM all the way up to the `App` looking for a match.

### Binding class

The tuple of three strings may be enough for simple bindings, but you can also replace the tuple with a [Binding][textual.binding.Binding] instance which exposes a few more options.

### Priority bindings

Individual bindings may be marked as a *priority*, which means they will be checked prior to the bindings of the focused widget. This feature is often used to create hot-keys on the app or screen. Such bindings can not be disabled by binding the same key on a widget.

You can create priority key bindings by setting `priority=True` on the Binding object. Textual uses this feature to add a default binding for ++ctrl+q++ so there is always a way to exit the app. Here's the `BINDINGS` from the App base class. Note the quit binding is set as a priority:

```python
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=False, priority=True)
    ]
```

### Show bindings

The [footer](../widgets/footer.md) widget can inspect bindings to display available keys. If you don't want a binding to display in the footer you can set `show=False`. The default bindings on App do this so that the standard ++ctrl+c++, ++tab++ and ++shift+tab++ bindings don't typically appear in the footer.


### Dynamic bindings?

You may find you have bindings which are not always applicable given the current state of your app.
For instance a "Save file" binding when there are no changes to save.
It wouldn't be a good user experience if the save key did nothing, or raised an error.

Textual doesn't support modifying the bindings at runtime, but you can accomplish this with [dynamic actions](./actions.md#dynamic-actions) which offers greater flexibility.


## Mouse Input

Textual will send events in response to mouse movement and mouse clicks. These events contain the coordinates of the mouse cursor relative to the terminal or widget.

!!! information

    The trackpad (and possibly other pointer devices) are treated the same as the mouse in terminals.

Terminal coordinates are given by a pair values named `x` and `y`. The X coordinate is an offset in characters, extending from the left to the right of the screen. The Y coordinate is an offset in _lines_, extending from the top of the screen to the bottom.

Coordinates may be relative to the screen, so `(0, 0)` would be the top left of the screen. Coordinates may also be relative to a widget, where `(0, 0)` would be the top left of the widget itself.


<div class="excalidraw">
--8<-- "docs/images/input/coords.excalidraw.svg"
</div>

### Mouse movements

When you move the mouse cursor over a widget it will receive [MouseMove](../events/mouse_move.md) events which contain the coordinate of the mouse and information about what modifier keys (++ctrl++, ++shift++ etc) are held down.

The following example shows mouse movements being used to _attach_ a widget to the mouse cursor.

=== "mouse01.py"

    ```python title="mouse01.py" hl_lines="17-19"
    --8<-- "docs/examples/guide/input/mouse01.py"
    ```

=== "mouse01.tcss"

    ```css title="mouse01.tcss"
    --8<-- "docs/examples/guide/input/mouse01.tcss"
    ```

If you run `mouse01.py` you should find that it logs the mouse move event, and keeps a widget pinned directly under the cursor.

The `on_mouse_move` handler sets the [offset](../styles/offset.md) style of the ball (a rectangular one) to match the mouse coordinates.

### Mouse capture

In the `mouse01.py` example there was a call to `capture_mouse()` in the mount handler. Textual will send mouse move events to the widget directly under the cursor. You can tell Textual to send all mouse events to a widget regardless of the position of the mouse cursor by calling [capture_mouse][textual.widget.Widget.capture_mouse].

Call [release_mouse][textual.widget.Widget.release_mouse] to restore the default behavior.

!!! warning

    If you capture the mouse, be aware you might get negative mouse coordinates if the cursor is to the left of the widget.

Textual will send a [MouseCapture](../events/mouse_capture.md) event when the mouse is captured, and a [MouseRelease](../events/mouse_release.md) event when it is released.

### Enter and Leave events

Textual will send a [Enter](../events/enter.md) event to a widget when the mouse cursor first moves over it, and a [Leave](../events/leave.md) event when the cursor moves off a widget.

Both `Enter` and `Leave` _bubble_, so a widget may receive these events from a child widget.
You can check the initial widget these events were sent to by comparing the `node` attribute against `self` in the message handler.

### Click events

There are three events associated with clicking a button on your mouse. When the button is initially pressed, Textual sends a [MouseDown](../events/mouse_down.md) event, followed by [MouseUp](../events/mouse_up.md) when the button is released. Textual then sends a final [Click](../events/click.md) event.

If you want your app to respond to a mouse click you should prefer the Click event (and not MouseDown or MouseUp). This is because a future version of Textual may support other pointing devices which don't have up and down states.

### Scroll events

Most mice have a scroll wheel which you can use to scroll the window underneath the cursor. Scrollable containers in Textual will handle these automatically, but you can handle [MouseScrollDown](../events/mouse_scroll_down.md) and [MouseScrollUp](../events/mouse_scroll_up.md) if you want build your own scrolling functionality.

For terminals that support horizontal mouse wheel, Textual sends [MouseScrollLeft](../events/mouse_scroll_left.md) and [MouseScrollRight](../events/mouse_scroll_right.md), and scrollable containers handle them automatically.

!!! information

    Terminal emulators will typically convert trackpad gestures into scroll events.
````

## File: docs/guide/layout.md
````markdown
# Layout

In Textual, the *layout* defines how widgets will be arranged (or *laid out*) inside a container.
Textual supports a number of layouts which can be set either via a widget's `styles` object or via CSS.
Layouts can be used for both high-level positioning of widgets on screen, and for positioning of nested widgets.

## Vertical

The `vertical` layout arranges child widgets vertically, from top to bottom.

<div class="excalidraw">
--8<-- "docs/images/layout/vertical.excalidraw.svg"
</div>

The example below demonstrates how children are arranged inside a container with the `vertical` layout.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/vertical_layout.py"}
    ```

=== "vertical_layout.py"

    ```python
    --8<-- "docs/examples/guide/layout/vertical_layout.py"
    ```

=== "vertical_layout.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/guide/layout/vertical_layout.tcss"
    ```

Notice that the first widget yielded from the `compose` method appears at the top of the display,
the second widget appears below it, and so on.
Inside `vertical_layout.tcss`, we've assigned `layout: vertical` to `Screen`.
`Screen` is the parent container of the widgets yielded from the `App.compose` method, and can be thought of as the terminal window itself.

!!! note

    The `layout: vertical` CSS isn't *strictly* necessary in this case, since Screens use a `vertical` layout by default.

We've assigned each child `.box` a height of `1fr`, which ensures they're each allocated an equal portion of the available height.

You might also have noticed that the child widgets are the same width as the screen, despite nothing in our CSS file suggesting this.
This is because widgets expand to the width of their parent container (in this case, the `Screen`).

Just like other styles, `layout` can be adjusted at runtime by modifying the `styles` of a `Widget` instance:

```python
widget.styles.layout = "vertical"
```

Using `fr` units guarantees that the children fill the available height of the parent.
However, if the total height of the children exceeds the available space, then Textual will automatically add
a scrollbar to the parent `Screen`.

!!! note

    A scrollbar is added automatically because `Screen` contains the declaration `overflow-y: auto;`.

For example, if we swap out `height: 1fr;` for `height: 10;` in the example above, the child widgets become a fixed height of 10, and a scrollbar appears (assuming our terminal window is sufficiently small):

```{.textual path="docs/examples/guide/layout/vertical_layout_scrolled.py"}
```

[//]: # (TODO: Add link to "focus" docs in paragraph below.)

With the parent container in focus, we can use our mouse wheel, trackpad, or keyboard to scroll it.

## Horizontal

The `horizontal` layout arranges child widgets horizontally, from left to right.

<div class="excalidraw">
--8<-- "docs/images/layout/horizontal.excalidraw.svg"
</div>

The example below shows how we can arrange widgets horizontally, with minimal changes to the vertical layout example above.


=== "Output"

    ```{.textual path="docs/examples/guide/layout/horizontal_layout.py"}
    ```

=== "horizontal_layout.py"

    ```python
    --8<-- "docs/examples/guide/layout/horizontal_layout.py"
    ```

=== "horizontal_layout.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/guide/layout/horizontal_layout.tcss"
    ```


We've changed the `layout` to `horizontal` inside our CSS file.
As a result, the widgets are now arranged from left to right instead of top to bottom.

We also adjusted the height of the child `.box` widgets to `100%`.
As mentioned earlier, widgets expand to fill the _width_ of their parent container.
They do not, however, expand to fill the container's height.
Thus, we need explicitly assign `height: 100%` to achieve this.

A consequence of this "horizontal growth" behavior is that if we remove the width restriction from the above example (by deleting `width: 1fr;`), each child widget will grow to fit the width of the screen,
and only the first widget will be visible.
The other two widgets in our layout are offscreen, to the right-hand side of the screen.
In the case of `horizontal` layout, Textual will _not_ automatically add a scrollbar.

To enable horizontal scrolling, we can use the `overflow-x: auto;` declaration:

=== "Output"

    ```{.textual path="docs/examples/guide/layout/horizontal_layout_overflow.py"}
    ```

=== "horizontal_layout_overflow.py"

    ```python
    --8<-- "docs/examples/guide/layout/horizontal_layout_overflow.py"
    ```

=== "horizontal_layout_overflow.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/guide/layout/horizontal_layout_overflow.tcss"
    ```

With `overflow-x: auto;`, Textual automatically adds a horizontal scrollbar since the width of the children
exceeds the available horizontal space in the parent container.

## Utility containers

Textual comes with [several "container" widgets][textual.containers].
Among them, we have [Vertical][textual.containers.Vertical], [Horizontal][textual.containers.Horizontal], and [Grid][textual.containers.Grid] which have the corresponding layout.

The example below shows how we can combine these containers to create a simple 2x2 grid.
Inside a single `Horizontal` container, we place two `Vertical` containers.
In other words, we have a single row containing two columns.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/utility_containers.py"}
    ```

=== "utility_containers.py"

    ```python
    --8<-- "docs/examples/guide/layout/utility_containers.py"
    ```

=== "utility_containers.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/guide/layout/utility_containers.tcss"
    ```

You may be tempted to use many levels of nested utility containers in order to build advanced, grid-like layouts.
However, Textual comes with a more powerful mechanism for achieving this known as _grid layout_, which we'll discuss below.

## Composing with context managers

In the previous section, we've shown how you add children to a container (such as `Horizontal` and `Vertical`) using positional arguments.
It's fine to do it this way, but Textual offers a simplified syntax using [context managers](https://docs.python.org/3/reference/datamodel.html#context-managers), which is generally easier to write and edit.

When composing a widget, you can introduce a container using Python's `with` statement.
Any widgets yielded within that block are added as a child of the container.

Let's update the [utility containers](#utility-containers) example to use the context manager approach.

=== "utility_containers_using_with.py"

    !!! note

        This code uses context managers to compose widgets.

    ```python hl_lines="10-16"
    --8<-- "docs/examples/guide/layout/utility_containers_using_with.py"
    ```

=== "utility_containers.py"

    !!! note

        This is the original code using positional arguments.

    ```python hl_lines="10-21"
    --8<-- "docs/examples/guide/layout/utility_containers.py"
    ```

=== "utility_containers.tcss"

    ```css
    --8<-- "docs/examples/guide/layout/utility_containers.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/layout/utility_containers_using_with.py"}
    ```

Note how the end result is the same, but the code with context managers is a little easier to read. It is up to you which method you want to use, and you can mix context managers with positional arguments if you like!

## Grid

The `grid` layout arranges widgets within a grid.
Widgets can span multiple rows and columns to create complex layouts.
The diagram below hints at what can be achieved using `layout: grid`.

<div class="excalidraw">
--8<-- "docs/images/layout/grid.excalidraw.svg"
</div>

!!! note

    Grid layouts in Textual have little in common with browser-based CSS Grid.

To get started with grid layout, define the number of columns and rows in your grid with the `grid-size` CSS property and set `layout: grid`. Widgets are inserted into the "cells" of the grid from left-to-right and top-to-bottom order.

The following example creates a 3 x 2 grid and adds six widgets to it

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout1.py"}
    ```

=== "grid_layout1.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout1.py"
    ```

=== "grid_layout1.tcss"

    ```css hl_lines="2 3"
    --8<-- "docs/examples/guide/layout/grid_layout1.tcss"
    ```


If we were to yield a seventh widget from our `compose` method, it would not be visible as the grid does not contain enough cells to accommodate it. We can tell Textual to add new rows on demand to fit the number of widgets, by omitting the number of rows from `grid-size`. The following example creates a grid with three columns, with rows created on demand:


=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout2.py"}
    ```

=== "grid_layout2.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout2.py"
    ```

=== "grid_layout2.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/guide/layout/grid_layout2.tcss"
    ```

Since we specified that our grid has three columns (`grid-size: 3`), and we've yielded seven widgets in total,
a third row has been created to accommodate the seventh widget.

Now that we know how to define a simple uniform grid, let's look at how we can
customize it to create more complex layouts.

### Row and column sizes

You can adjust the width of columns and the height of rows in your grid using the `grid-columns` and `grid-rows` properties.
These properties can take multiple values, letting you specify dimensions on a column-by-column or row-by-row basis.

Continuing on from our earlier 3x2 example grid, let's adjust the width of the columns using `grid-columns`.
We'll make the first column take up half of the screen width, with the other two columns sharing the remaining space equally.


=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout3_row_col_adjust.py"}
    ```

=== "grid_layout3_row_col_adjust.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout3_row_col_adjust.py"
    ```

=== "grid_layout3_row_col_adjust.tcss"

    ```css hl_lines="4"
    --8<-- "docs/examples/guide/layout/grid_layout3_row_col_adjust.tcss"
    ```


Since our `grid-size` is 3 (meaning it has three columns), our `grid-columns` declaration has three space-separated values.
Each of these values sets the width of a column.
The first value refers to the left-most column, the second value refers to the next column, and so on.
In the example above, we've given the left-most column a width of `2fr` and the other columns widths of `1fr`.
As a result, the first column is allocated twice the width of the other columns.

Similarly, we can adjust the height of a row using `grid-rows`.
In the following example, we use `%` units to adjust the first row of our grid to `25%` height,
and the second row to `75%` height (while retaining the `grid-columns` change from above).


=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout4_row_col_adjust.py"}
    ```

=== "grid_layout4_row_col_adjust.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout4_row_col_adjust.py"
    ```

=== "grid_layout4_row_col_adjust.tcss"

    ```css hl_lines="5"
    --8<-- "docs/examples/guide/layout/grid_layout4_row_col_adjust.tcss"
    ```


If you don't specify enough values in a `grid-columns` or `grid-rows` declaration, the values you _have_ provided will be "repeated".
For example, if your grid has four columns (i.e. `grid-size: 4;`), then `grid-columns: 2 4;` is equivalent to `grid-columns: 2 4 2 4;`.
If it instead had three columns, then `grid-columns: 2 4;` would be equivalent to `grid-columns: 2 4 2;`.

#### Auto rows / columns

The `grid-columns` and `grid-rows` rules can both accept a value of "auto" in place of any of the dimensions, which tells Textual to calculate an optimal size based on the content.

Let's modify the previous example to make the first column an `auto` column.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout_auto.py"}
    ```

=== "grid_layout_auto.py"

    ```python hl_lines="6 9"
    --8<-- "docs/examples/guide/layout/grid_layout_auto.py"
    ```

=== "grid_layout_auto.tcss"

    ```css hl_lines="4"
    --8<-- "docs/examples/guide/layout/grid_layout_auto.tcss"
    ```

Notice how the first column is just wide enough to fit the content of each cell.
The layout will adjust accordingly if you update the content for any widget in that column.


### Cell spans

Cells may _span_ multiple rows or columns, to create more interesting grid arrangements.

To make a single cell span multiple rows or columns in the grid, we need to be able to select it using CSS.
To do this, we'll add an ID to the widget inside our `compose` method so we can set the `row-span` and `column-span` properties using CSS.

Let's add an ID of `#two` to the second widget yielded from `compose`, and give it a `column-span` of 2 to make that widget span two columns.
We'll also add a slight tint using `tint: magenta 40%;` to draw attention to it.


=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout5_col_span.py"}
    ```

=== "grid_layout5_col_span.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout5_col_span.py"
    ```

=== "grid_layout5_col_span.tcss"

    ```css hl_lines="6-9"
    --8<-- "docs/examples/guide/layout/grid_layout5_col_span.tcss"
    ```



Notice that the widget expands to fill columns to the _right_ of its original position.
Since `#two` now spans two cells instead of one, all widgets that follow it are shifted along one cell in the grid to accommodate.
As a result, the final widget wraps on to a new row at the bottom of the grid.

!!! note

    In the example above, setting the `column-span` of `#two` to be 3 (instead of 2) would have the same effect, since there are only 2 columns available (including `#two`'s original column).

We can similarly adjust the `row-span` of a cell to have it span multiple rows.
This can be used in conjunction with `column-span`, meaning one cell may span multiple rows and columns.
The example below shows `row-span` in action.
We again target widget `#two` in our CSS, and add a `row-span: 2;` declaration to it.


=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout6_row_span.py"}
    ```

=== "grid_layout6_row_span.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout6_row_span.py"
    ```

=== "grid_layout6_row_span.tcss"

    ```css hl_lines="8"
    --8<-- "docs/examples/guide/layout/grid_layout6_row_span.tcss"
    ```



Widget `#two` now spans two columns and two rows, covering a total of four cells.
Notice how the other cells are moved to accommodate this change.
The widget that previously occupied a single cell now occupies four cells, thus displacing three cells to a new row.

### Gutter

The spacing between cells in the grid can be adjusted using the `grid-gutter` CSS property.
By default, cells have no gutter, meaning their edges touch each other.
Gutter is applied across every cell in the grid, so `grid-gutter` must be used on a widget with `layout: grid` (_not_ on a child/cell widget).

To illustrate gutter let's set our `Screen` background color to `lightgreen`, and the background color of the widgets we yield to `darkmagenta`.
Now if we add `grid-gutter: 1;` to our grid, one cell of spacing appears between the cells and reveals the light green background of the `Screen`.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/grid_layout7_gutter.py"}
    ```

=== "grid_layout7_gutter.py"

    ```python
    --8<-- "docs/examples/guide/layout/grid_layout7_gutter.py"
    ```

=== "grid_layout7_gutter.tcss"

    ```css hl_lines="4"
    --8<-- "docs/examples/guide/layout/grid_layout7_gutter.tcss"
    ```

Notice that gutter only applies _between_ the cells in a grid, pushing them away from each other.
It doesn't add any spacing between cells and the edges of the parent container.

!!! tip

    You can also supply two values to the `grid-gutter` property to set vertical and horizontal gutters respectively.
    Since terminal cells are typically two times taller than they are wide,
    it's common to set the horizontal gutter equal to double the vertical gutter (e.g. `grid-gutter: 1 2;`) in order to achieve visually consistent spacing around grid cells.

## Docking

Widgets may be *docked*.
Docking a widget removes it from the layout and fixes its position, aligned to either the top, right, bottom, or left edges of a container.
Docked widgets will not scroll out of view, making them ideal for sticky headers, footers, and sidebars.

<div class="excalidraw">
--8<-- "docs/images/layout/dock.excalidraw.svg"
</div>

To dock a widget to an edge, add a `dock: <EDGE>;` declaration to it, where `<EDGE>` is one of `top`, `right`, `bottom`, or `left`.
For example, a sidebar similar to that shown in the diagram above can be achieved using `dock: left;`.
The code below shows a simple sidebar implementation.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout1_sidebar.py" press="pagedown,down,down"}
    ```

=== "dock_layout1_sidebar.py"

    ```python
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.py"
    ```

=== "dock_layout1_sidebar.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.tcss"
    ```

If we run the app above and scroll down, the body text will scroll but the sidebar does not (note the position of the scrollbar in the output shown above).

Docking multiple widgets to the same edge will result in overlap.
The first widget yielded from `compose` will appear below widgets yielded after it.
Let's dock a second sidebar, `#another-sidebar`, to the left of the screen.
This new sidebar is double the width of the one previous one, and has a `deeppink` background.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout2_sidebar.py" press="pagedown,down,down"}
    ```

=== "dock_layout2_sidebar.py"

    ```python hl_lines="16"
    --8<-- "docs/examples/guide/layout/dock_layout2_sidebar.py"
    ```

=== "dock_layout2_sidebar.tcss"

    ```css hl_lines="1-6"
    --8<-- "docs/examples/guide/layout/dock_layout2_sidebar.tcss"
    ```

Notice that the original sidebar (`#sidebar`) appears on top of the newly docked widget.
This is because `#sidebar` was yielded _after_ `#another-sidebar` inside the `compose` method.

Of course, we can also dock widgets to multiple edges within the same container.
The built-in `Header` widget contains some internal CSS which docks it to the top.
We can yield it inside `compose`, and without any additional CSS, we get a header fixed to the top of the screen.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout3_sidebar_header.py"}
    ```

=== "dock_layout3_sidebar_header.py"

    ```python hl_lines="14"
    --8<-- "docs/examples/guide/layout/dock_layout3_sidebar_header.py"
    ```

=== "dock_layout3_sidebar_header.tcss"

    ```css
    --8<-- "docs/examples/guide/layout/dock_layout3_sidebar_header.tcss"
    ```

If we wished for the sidebar to appear below the header, it'd simply be a case of yielding the sidebar before we yield the header.

## Layers

Textual has a concept of _layers_ which gives you finely grained control over the order widgets are placed.

When drawing widgets, Textual will first draw on _lower_ layers, working its way up to higher layers.
As such, widgets on higher layers will be drawn on top of those on lower layers.

Layer names are defined with a `layers` style on a container (parent) widget.
Descendants of this widget can then be assigned to one of these layers using a `layer` style.

The `layers` style takes a space-separated list of layer names.
The leftmost name is the lowest layer, and the rightmost is the highest layer.
Therefore, if you assign a descendant to the rightmost layer name, it'll be drawn on the top layer and will be visible above all other descendants.

An example `layers` declaration looks like: `layers: one two three;`.
To add a widget to the topmost layer in this case, you'd add a declaration of `layer: three;` to it.

In the example below, `#box1` is yielded before `#box2`.
Given our earlier discussion on yield order, you'd expect `#box2` to appear on top.
However, in this case, both `#box1` and `#box2` are assigned to layers which define the reverse order, so `#box1` is on top of `#box2`


[//]: # (NOTE: the example below also appears in the layers and layer style reference)

=== "Output"

    ```{.textual path="docs/examples/guide/layout/layers.py"}
    ```

=== "layers.py"

    ```python
    --8<-- "docs/examples/guide/layout/layers.py"
    ```

=== "layers.tcss"

    ```css hl_lines="3 14 19"
    --8<-- "docs/examples/guide/layout/layers.tcss"
    ```

## Offsets

Widgets have a relative offset which is added to the widget's location, _after_ its location has been determined via its parent's layout.
This means that if a widget hasn't had its offset modified using CSS or Python code, it will have an offset of `(0, 0)`.

<div class="excalidraw">
--8<-- "docs/images/layout/offset.excalidraw.svg"
</div>

The offset of a widget can be set using the `offset` CSS property.
`offset` takes two values.

* The first value defines the `x` (horizontal) offset. Positive values will shift the widget to the right. Negative values will shift the widget to the left.
* The second value defines the `y` (vertical) offset. Positive values will shift the widget down. Negative values will shift the widget up.

[//]: # (TODO Link the word animation below to animation docs)

## Putting it all together

The sections above show how the various layouts in Textual can be used to position widgets on screen.
In a real application, you'll make use of several layouts.

The example below shows how an advanced layout can be built by combining the various techniques described on this page.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/combining_layouts.py"}
    ```

=== "combining_layouts.py"

    ```python
    --8<-- "docs/examples/guide/layout/combining_layouts.py"
    ```

=== "combining_layouts.tcss"

    ```css
    --8<-- "docs/examples/guide/layout/combining_layouts.tcss"
    ```

Textual layouts make it easy to design and build real-life applications with relatively little code.
````

## File: docs/guide/queries.md
````markdown
# DOM Queries

In the [CSS chapter](./CSS.md) we introduced the [DOM](../guide/CSS.md#the-dom) which is how Textual apps keep track of widgets. We saw how you can apply styles to the DOM with CSS [selectors](./CSS.md#selectors).

Selectors are a very useful idea and can do more than apply styles. We can also find widgets in Python code with selectors, and make updates to widgets in a simple expressive way. Let's look at how!

!!! tip

    See the [Textual Query Sandbox](https://github.com/davep/textual-query-sandbox/) project for an interactive way of experimenting with DOM queries.

## Query one

The [query_one][textual.dom.DOMNode.query_one] method is used to retrieve a single widget that matches a selector or a type.

Let's say we have a widget with an ID of `send` and we want to get a reference to it in our app.
We could do this with the following line of code:

```python
send_button = self.query_one("#send")
```

This will retrieve the first widget discovered with an ID of `send`.
If there are no matching widgets, Textual will raise a [NoMatches][textual.css.query.NoMatches] exception.

You can also add a second parameter for the expected type, which will ensure that you get the type you are expecting.

```python
send_button = self.query_one("#send", Button)
```

If the matched widget is *not* a button (i.e. if `isinstance(widget, Button)` equals `False`), Textual will raise a [WrongType][textual.css.query.WrongType] exception.

!!! tip

    The second parameter allows type-checkers like MyPy to know the exact return type. Without it, MyPy would only know the result of `query_one` is a Widget (the base class).

You can also specify a widget type in place of a selector, which will return a widget of that type.
For instance, the following would return a `Button` instance (assuming there is a single Button).

```python
my_button = self.query_one(Button)
```

`query_one` searches the DOM *below* the widget it is called on, so if you call `query_one` on a widget, it will only find widgets that are descendants of that widget.

If you wish to search the entire DOM, you should call `query_one` on the `App` or `Screen` instance.

```python
# Search the entire Screen for a widget with an ID of "send-email"
self.screen.query_one("#send-email")
```

## Making queries

Apps and widgets also have a [query][textual.dom.DOMNode.query] method which finds (or queries) widgets. This method returns a [DOMQuery][textual.css.query.DOMQuery] object which is a list-like container of widgets.

If you call `query` with no arguments, you will get back a `DOMQuery` containing all widgets. This method is *recursive*, meaning it will also return child widgets (as many levels as required).

Here's how you might iterate over all the widgets in your app:

```python
for widget in self.query():
    print(widget)
```

Called on the `app`, this will retrieve all widgets in the app. If you call the same method on a widget, it will return the children of that widget.

!!! note

    All the query and related methods work on both App and Widget sub-classes.

### Query selectors

You can call `query` with a CSS selector. Let's look a few examples:

If we want to find all the button widgets, we could do something like the following:

```python
for button in self.query("Button"):
    print(button)
```

Any selector that works in CSS will work with the `query` method. For instance, if we want to find all the disabled buttons in a Dialog widget, we could do this:

```python
for button in self.query("Dialog Button.disabled"):
    print(button)
```

!!! info

    The selector `Dialog Button.disabled` says find all the `Button` with a CSS class of `disabled` that are a child of a `Dialog` widget.

### Results

Query objects have a [results][textual.css.query.DOMQuery.results] method which is an alternative way of iterating over widgets. If you supply a type (i.e. a Widget class) then this method will generate only objects of that type.

The following example queries for widgets with the `disabled` CSS class and iterates over just the Button objects.

```python
for button in self.query(".disabled").results(Button):
    print(button)
```

!!! tip

    This method allows type-checkers like MyPy to know the exact type of the object in the loop. Without it, MyPy would only know that `button` is a `Widget` (the base class).

## Query objects

We've seen that the [query][textual.dom.DOMNode.query] method returns a [DOMQuery][textual.css.query.DOMQuery] object you can iterate over in a for loop. Query objects behave like Python lists and support all of the same operations (such as `query[0]`, `len(query)` ,`reverse(query)` etc). They also have a number of other methods to simplify retrieving and modifying widgets.

## First and last

The [first][textual.css.query.DOMQuery.first] and [last][textual.css.query.DOMQuery.last] methods return the first or last matching widget from the selector, respectively.

Here's how we might find the _last_ button in an app:

```python
last_button = self.query("Button").last()
```

If there are no buttons, Textual will raise a [NoMatches][textual.css.query.NoMatches] exception. Otherwise it will return a button widget.

Both `first()` and `last()` accept an `expect_type` argument that should be the class of the widget you are expecting. Let's say we want to get the last widget with class `.disabled`, and we want to check it really is a button. We could do this:

```python
disabled_button = self.query(".disabled").last(Button)
```

The query selects all widgets with a `disabled` CSS class. The `last` method gets the last disabled widget and checks it is a `Button` and not any other kind of widget.

If the last widget is *not* a button, Textual will raise a [WrongType][textual.css.query.WrongType] exception.

!!! tip

    Specifying the expected type allows type-checkers like MyPy to know the exact return type.

## Filter

Query objects have a [filter][textual.css.query.DOMQuery.filter] method which further refines a query. This method will return a new query object with widgets that match both the original query _and_ the new selector.

Let's say we have a query which gets all the buttons in an app, and we want a new query object with just the disabled buttons. We could write something like this:

```python
# Get all the Buttons
buttons_query = self.query("Button")
# Buttons with 'disabled' CSS class
disabled_buttons = buttons_query.filter(".disabled")
```

Iterating over `disabled_buttons` will give us all the disabled buttons.

## Exclude

Query objects have an [exclude][textual.css.query.DOMQuery.exclude] method which is the logical opposite of [filter][textual.css.query.DOMQuery.filter]. The `exclude` method removes any widgets from the query object which match a selector.

Here's how we could get all the buttons which *don't* have the `disabled` class set.

```python
# Get all the Buttons
buttons_query = self.query("Button")
# Remove all the Buttons with the 'disabled' CSS class
enabled_buttons = buttons_query.exclude(".disabled")
```

## Loop-free operations

Once you have a query object, you can loop over it to call methods on the matched widgets. Query objects also support a number of methods which make an update to every matched widget without an explicit loop.

For instance, let's say we want to disable all buttons in an app. We could do this by calling [add_class()][textual.css.query.DOMQuery.add_class] on a query object.

```python
self.query("Button").add_class("disabled")
```

This single line is equivalent to the following:

```python
for widget in self.query("Button"):
    widget.add_class("disabled")
```

Here are the other loop-free methods on query objects:

- [add_class][textual.css.query.DOMQuery.add_class] Adds a CSS class (or classes) to matched widgets.
- [blur][textual.css.query.DOMQuery.focus] Blurs (removes focus) from matching widgets.
- [focus][textual.css.query.DOMQuery.focus] Focuses the first matching widgets.
- [refresh][textual.css.query.DOMQuery.refresh] Refreshes matched widgets.
- [remove_class][textual.css.query.DOMQuery.remove_class] Removes a CSS class (or classes) from matched widgets.
- [remove][textual.css.query.DOMQuery.remove] Removes matched widgets from the DOM.
- [set_class][textual.css.query.DOMQuery.set_class] Sets a CSS class (or classes) on matched widgets.
- [set][textual.css.query.DOMQuery.set] Sets common attributes on a widget.
- [toggle_class][textual.css.query.DOMQuery.toggle_class] Sets a CSS class (or classes) if it is not set, or removes the class (or classes) if they are set on the matched widgets.
````

## File: docs/guide/reactivity.md
````markdown
# Reactivity

Textual's reactive attributes are attributes _with superpowers_. In this chapter we will look at how reactive attributes can simplify your apps.

!!! quote

    With great power comes great responsibility.

    &mdash; Uncle Ben

## Reactive attributes

Textual provides an alternative way of adding attributes to your widget or App, which doesn't require adding them to your class constructor (`__init__`). To create these attributes import [reactive][textual.reactive.reactive] from `textual.reactive`, and assign them in the class scope.

The following code illustrates how to create reactive attributes:

```python
from textual.reactive import reactive
from textual.widget import Widget

class Reactive(Widget):

    name = reactive("Paul")  # (1)!
    count = reactive(0) # (2)!
    is_cool = reactive(True)  # (3)!
```

1. Create a string attribute with a default of `"Paul"`
2. Creates an integer attribute with a default of `0`.
3. Creates a boolean attribute with a default of `True`.

The `reactive` constructor accepts a default value as the first positional argument.

!!! information

    Textual uses Python's _descriptor protocol_ to create reactive attributes, which is the same protocol used by the builtin `property` decorator.

You can get and set these attributes in the same way as if you had assigned them in an `__init__` method. For instance `self.name = "Jessica"`, `self.count += 1`, or `print(self.is_cool)`.

### Dynamic defaults

You can also set the default to a function (or other callable). Textual will call this function to get the default value. The following code illustrates a reactive value which will be automatically assigned the current time when the widget is created:

```python
from time import time
from textual.reactive import reactive
from textual.widget import Widget

class Timer(Widget):

    start_time = reactive(time)  # (1)!
```

1. The `time` function returns the current time in seconds.

### Typing reactive attributes

There is no need to specify a type hint if a reactive attribute has a default value, as type checkers will assume the attribute is the same type as the default.

You may want to add explicit type hints if the attribute type is a superset of the default type. For instance if you want to make an attribute optional. Here's how you would create a reactive string attribute which may be `None`:

```python
    name: reactive[str | None] = reactive("Paul")
```

## Smart refresh

The first superpower we will look at is "smart refresh". When you modify a reactive attribute, Textual will make note of the fact that it has changed and refresh automatically by calling the widget's [`render()`][textual.widget.Widget.render] method to get updated content.

!!! information

    If you modify multiple reactive attributes, Textual will only do a single refresh to minimize updates.

Let's look at an example which illustrates this. In the following app, the value of an input is used to update a "Hello, World!" type greeting.

=== "refresh01.py"

    ```python hl_lines="7-13 24"
    --8<-- "docs/examples/guide/reactivity/refresh01.py"
    ```

=== "refresh01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/refresh01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/refresh01.py" press="T,e,x,t,u,a,l"}
    ```

The `Name` widget has a reactive `who` attribute. When the app modifies that attribute, a refresh happens automatically.

!!! information

    Textual will check if a value has really changed, so assigning the same value wont prompt an unnecessary refresh.

### Disabling refresh

If you *don't* want an attribute to prompt a refresh or layout but you still want other reactive superpowers, you can use [var][textual.reactive.var] to create an attribute. You can import `var` from `textual.reactive`.

The following code illustrates how you create non-refreshing reactive attributes.

```python
class MyWidget(Widget):
    count = var(0)  # (1)!
```

1. Changing `self.count` wont cause a refresh or layout.

### Layout

The smart refresh feature will update the content area of a widget, but will not change its size. If modifying an attribute should change the size of the widget, you can set `layout=True` on the reactive attribute. This ensures that your CSS layout will update accordingly.

The following example modifies "refresh01.py" so that the greeting has an automatic width.

=== "refresh02.py"

    ```python hl_lines="10"
    --8<-- "docs/examples/guide/reactivity/refresh02.py"
    ```

    1. This attribute will update the layout when changed.

=== "refresh02.tcss"

    ```css hl_lines="7-9"
    --8<-- "docs/examples/guide/reactivity/refresh02.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/refresh02.py" press="n,a,m,e"}
    ```

If you type into the input now, the greeting will expand to fit the content. If you were to set `layout=False` on the reactive attribute, you should see that the box remains the same size when you type.

## Validation

The next superpower we will look at is _validation_, which can check and potentially modify a value you assign to a reactive attribute.

If you add a method that begins with `validate_` followed by the name of your attribute, it will be called when you assign a value to that attribute. This method should accept the incoming value as a positional argument, and return the value to set (which may be the same or a different value).

A common use for this is to restrict numbers to a given range. The following example keeps a count. There is a button to increase the count, and a button to decrease it. The validation ensures that the count will never go above 10 or below zero.

=== "validate01.py"

    ```python hl_lines="12-18 30 32"
    --8<-- "docs/examples/guide/reactivity/validate01.py"
    ```

=== "validate01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/validate01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/validate01.py"}
    ```

If you click the buttons in the above example it will show the current count. When `self.count` is modified in the button handler, Textual runs `validate_count` which performs the validation to limit the value of count.

## Watch methods

Watch methods are another superpower.
Textual will call watch methods when reactive attributes are modified.
Watch method names begin with `watch_` followed by the name of the attribute, and should accept one or two arguments.
If the method accepts a single argument, it will be called with the new assigned value.
If the method accepts *two* positional arguments, it will be called with both the *old* value and the *new* value.

The following app will display any color you type into the input. Try it with a valid color in Textual CSS. For example `"darkorchid"` or `"#52de44"`.

=== "watch01.py"

    ```python hl_lines="17-19 28"
    --8<-- "docs/examples/guide/reactivity/watch01.py"
    ```

    1. Creates a reactive [color][textual.color.Color] attribute.
    2. Called when `self.color` is changed.
    3. New color is assigned here.

=== "watch01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/watch01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/watch01.py" press="d,a,r,k,o,r,c,h,i,d"}
    ```

The color is parsed in `on_input_submitted` and assigned to `self.color`. Because `color` is reactive, Textual also calls `watch_color` with the old and new values.

### When are watch methods called?

Textual only calls watch methods if the value of a reactive attribute _changes_.
If the newly assigned value is the same as the previous value, the watch method is not called.
You can override this behavior by passing `always_update=True` to `reactive`.


### Dynamically watching reactive attributes

You can programmatically add watchers to reactive attributes with the method [`watch`][textual.dom.DOMNode.watch].
This is useful when you want to react to changes to reactive attributes for which you can't edit the watch methods.

The example below shows a widget `Counter` that defines a reactive attribute `counter`.
The app that uses `Counter` uses the method `watch` to keep its progress bar synced with the reactive attribute:

=== "dynamic_watch.py"

    ```python hl_lines="9 28-29 31"
    --8<-- "docs/examples/guide/reactivity/dynamic_watch.py"
    ```

    1. `counter` is a reactive attribute defined inside `Counter`.
    2. `update_progress` is a custom callback that will update the progress bar when `counter` changes.
    3. We use the method `watch` to set `update_progress` as an additional watcher for the reactive attribute `counter`.

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/dynamic_watch.py" press="enter,enter,enter"}
    ```

## Recompose

An alternative to a refresh is *recompose*.
If you set `recompose=True` on a reactive, then Textual will remove all the child widgets and call [`compose()`][textual.widget.Widget.compose] again, when the reactive attribute changes.
The process of removing and mounting new widgets occurs in a single update, so it will appear as though the content has simply updated.

The following example uses recompose:

=== "refresh03.py"

    ```python hl_lines="10 12-13"
    --8<-- "docs/examples/guide/reactivity/refresh03.py"
    ```

    1. Setting `recompose=True` will cause all child widgets to be removed and `compose` called again to add new widgets.
    2. This `compose()` method will be called when `who` is changed.

=== "refresh03.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/refresh03.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/refresh03.py" press="P,a,u,l"}
    ```

While the end-result is identical to `refresh02.py`, this code works quite differently.
The main difference is that recomposing creates an entirely new set of child widgets rather than updating existing widgets.
So when the `who` attribute changes, the `Name` widget will replace its `Label` with a new instance (containing updated content).

!!! warning 

    You should avoid storing a reference to child widgets when using recompose.
    Better to [query](../guide/queries.md) for a child widget when you need them.

It is important to note that any child widgets will have their state reset after a recompose.
For simple content, that doesn't matter much.
But widgets with an internal state (such as [`DataTable`](../widgets/data_table.md), [`Input`](../widgets/input.md), or [`TextArea`](../widgets/text_area.md)) would not be particularly useful if recomposed.

Recomposing is slightly less efficient than a simple refresh, and best avoided if you need to update rapidly or you have many child widgets.
That said, it can often simplify your code.
Let's look at a practical example.
First a version *without* recompose:

=== "recompose01.py"

    ```python hl_lines="20 26-27"
    --8<-- "docs/examples/guide/reactivity/recompose01.py"
    ```

    1. Called when the `time` attribute changes.
    2. Update the time once a second.

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/recompose01.py" }
    ```

This displays a clock which updates once a second.
The code is straightforward, but note how we format the time in two places: `compose()` *and* `watch_time()`.
We can simplify this by recomposing rather than refreshing:

=== "recompose02.py"

    ```python hl_lines="15"
    --8<-- "docs/examples/guide/reactivity/recompose02.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/recompose02.py" }
    ```

In this version, the app is recomposed when the `time` attribute changes, which replaces the `Digits` widget with a new instance and updated time.
There's no need for the `watch_time` method, because the new `Digits` instance will already show the current time.


## Compute methods

Compute methods are the final superpower offered by the `reactive` descriptor. Textual runs compute methods to calculate the value of a reactive attribute. Compute methods begin with `compute_` followed by the name of the reactive value.

You could be forgiven in thinking this sounds a lot like Python's property decorator. The difference is that Textual will cache the value of compute methods, and update them when any other reactive attribute changes.

The following example uses a computed attribute. It displays three inputs for each color component (red, green, and blue). If you enter numbers into these inputs, the background color of another widget changes.

=== "computed01.py"

    ```python hl_lines="25-26 28-29"
    --8<-- "docs/examples/guide/reactivity/computed01.py"
    ```

    1. Combines color components into a Color object.
    2. The watch method is called when the _result_ of `compute_color` changes.

=== "computed01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/computed01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/computed01.py"}
    ```

Note the `compute_color` method which combines the color components into a [Color][textual.color.Color] object. It will be recalculated when any of the `red` , `green`, or `blue` attributes are modified.

When the result of `compute_color` changes, Textual will also call `watch_color` since `color` still has the [watch method](#watch-methods) superpower.

!!! note

    Textual will first attempt to call the compute method for a reactive attribute, followed by the validate method, and finally the watch method.

!!! note

    It is best to avoid doing anything slow or CPU-intensive in a compute method. Textual calls compute methods on an object when _any_ reactive attribute changes.

## Setting reactives without superpowers 

You may find yourself in a situation where you want to set a reactive value, but you *don't* want to invoke watchers or the other super powers.
This is fairly common in constructors which run prior to mounting; any watcher which queries the DOM may break if the widget has not yet been mounted.

To work around this issue, you can call [set_reactive][textual.dom.DOMNode.set_reactive] as an alternative to setting the attribute.
The `set_reactive` method accepts the reactive attribute (as a class variable) and the new value.

Let's look at an example.
The following app is intended to cycle through various greeting when you press ++space++, however it contains a bug.

```python title="set_reactive01.py"
--8<-- "docs/examples/guide/reactivity/set_reactive01.py"
```

1. Setting this reactive attribute invokes a watcher.
2. The watcher attempts to update a label before it is mounted.

If you run this app, you will find Textual raises a `NoMatches` error in `watch_greeting`. 
This is because the constructor has assigned the reactive before the widget has fully mounted.

The following app contains a fix for this issue:

=== "set_reactive02.py"

    ```python hl_lines="33 34"
    --8<-- "docs/examples/guide/reactivity/set_reactive02.py"
    ```

    1. The attribute is set via `set_reactive`, which avoids calling the watcher.

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/set_reactive02.py"}
    ```

The line `self.set_reactive(Greeter.greeting, greeting)` sets the `greeting` attribute but doesn't immediately invoke the watcher.

## Mutable reactives

Textual can detect when you set a reactive to a new value, but it can't detect when you _mutate_ a value.
In practice, this means that Textual can detect changes to basic types (int, float, str, etc.), but not if you update a collection, such as a list or dict. 

You can still use collections and other mutable objects in reactives, but you will need to call [`mutate_reactive`][textual.dom.DOMNode.mutate_reactive] after making changes for the reactive superpowers to work.

Here's an example, that uses a reactive list:

=== "set_reactive03.py"

    ```python hl_lines="16"
    --8<-- "docs/examples/guide/reactivity/set_reactive03.py"
    ```

    1. Creates a reactive list of strings.
    2. Explicitly mutate the reactive list.

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/set_reactive03.py" press="W,i,l,l,enter"}
    ```

Note the call to `mutate_reactive`. Without it, the display would not update when a new name is appended to the list.

## Data binding

Reactive attributes may be *bound* (connected) to attributes on child widgets, so that changes to the parent are automatically reflected in the children.
This can simplify working with compound widgets where the value of an attribute might be used in multiple places.

To bind reactive attributes, call [data_bind][textual.dom.DOMNode.data_bind] on a widget.
This method accepts reactives (as class attributes) in positional arguments or keyword arguments.

Let's look at an app that could benefit from data binding.
In the following code we have a `WorldClock` widget which displays the time in any given timezone.


!!! note

    This example uses the [pytz](https://pypi.org/project/pytz/) library for working with timezones.
    You can install pytz with `pip install pytz`.


=== "world_clock01.py"

    ```python
    --8<-- "docs/examples/guide/reactivity/world_clock01.py"
    ```

    1. Update the `time` reactive attribute of every `WorldClock`.

=== "world_clock01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/world_clock01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/world_clock01.py"}
    ```

We've added three world clocks for London, Paris, and Tokyo.
The clocks are kept up-to-date by watching the app's `time` reactive, and updating the clocks in a loop.

While this approach works fine, it does require we take care to update every `WorldClock` we mount.
Let's see how data binding can simplify this.

The following app calls `data_bind` on the world clock widgets to connect the app's `time` with the widget's `time` attribute:

=== "world_clock02.py"

    ```python hl_lines="34-36"
    --8<-- "docs/examples/guide/reactivity/world_clock02.py"
    ```

    1. Bind the `time` attribute, so that changes to `time` will also change the `time` attribute on the `WorldClock` widgets. The `data_bind` method also returns the widget, so we can yield its return value.

=== "world_clock01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/world_clock01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/world_clock02.py"}
    ```

Note how the addition of the `data_bind` methods negates the need for the watcher in `world_clock01.py`.


!!! note

    Data binding works in a single direction.
    Setting `time` on the app updates the clocks.
    But setting `time` on the clocks will *not* update `time` on the app.


In the previous example app, the call to `data_bind(WorldClockApp.time)` worked because both reactive attributes were named `time`.
If you want to bind a reactive attribute which has a different name, you can use keyword arguments.

In the following app we have changed the attribute name on `WorldClock` from `time` to `clock_time`.
We can make the app continue to work by changing the `data_bind` call to `data_bind(clock_time=WorldClockApp.time)`:


=== "world_clock03.py"

    ```python hl_lines="34-38"
    --8<-- "docs/examples/guide/reactivity/world_clock03.py"
    ```

    1. Uses keyword arguments to bind the `time` attribute of `WorldClockApp` to `clock_time` on `WorldClock`.

=== "world_clock01.tcss"

    ```css
    --8<-- "docs/examples/guide/reactivity/world_clock01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/reactivity/world_clock02.py"}
    ```
````

## File: docs/guide/screens.md
````markdown
# Screens

This chapter covers Textual's screen API. We will discuss how to create screens and switch between them.

## What is a screen?

Screens are containers for widgets that occupy the dimensions of your terminal. There can be many screens in a given app, but only one screen is active at a time.

Textual requires that there be at least one screen object and will create one implicitly in the App class. If you don't change the screen, any widgets you [mount][textual.widget.Widget.mount] or [compose][textual.widget.Widget.compose] will be added to this default screen.

<div class="excalidraw">
--8<-- "docs/images/dom1.excalidraw.svg"
</div>

## Creating a screen

You can create a screen by extending the [Screen][textual.screen.Screen] class which you can import from `textual.screen`. The screen may be styled in the same way as other widgets, with the exception that you can't modify the screen's dimensions (as these will always be the size of your terminal).

Let's look at a simple example of writing a screen class to simulate Window's [blue screen of death](https://en.wikipedia.org/wiki/Blue_screen_of_death).

=== "screen01.py"

    ```python title="screen01.py" hl_lines="17-23 29"
    --8<-- "docs/examples/guide/screens/screen01.py"
    ```

=== "screen01.tcss"

    ```css title="screen01.tcss"
    --8<-- "docs/examples/guide/screens/screen01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/screens/screen01.py" press="b"}
    ```

If you run this you will see an empty screen. Hit the ++b++ key to show a blue screen of death. Hit ++escape++ to return to the default screen.

The `BSOD` class above defines a screen with a key binding and compose method. These should be familiar as they work in the same way as apps.

The app class has a new `SCREENS` class variable. Textual uses this class variable to associate a name with screen object (the name is used to reference screens in the screen API). Also in the app is a key binding associated with the action `"push_screen('bsod')"`. The screen class has a similar action `"pop_screen"` bound to the ++escape++ key. We will cover these actions below.

## Named screens

You can associate a screen with a name by defining a `SCREENS` class variable in your app, which should be a `dict` that maps names on to `Screen` objects. The name of the screen may be used interchangeably with screen objects in much of the screen API.

You can also _install_ new named screens dynamically with the [install_screen][textual.app.App.install_screen] method. The following example installs the `BSOD` screen in a mount handler rather than from the `SCREENS` variable.

=== "screen02.py"

    ```python title="screen02.py" hl_lines="31"
    --8<-- "docs/examples/guide/screens/screen02.py"
    ```

=== "screen02.tcss"

    ```css title="screen02.tcss"
    --8<-- "docs/examples/guide/screens/screen02.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/screens/screen02.py" press="b"}
    ```

Although both do the same thing, we recommend `SCREENS` for screens that exist for the lifetime of your app.

### Uninstalling screens

Screens defined in `SCREENS` or added with [install_screen][textual.app.App.install_screen] are _installed_ screens. Textual will keep these screens in memory for the lifetime of your app.

If you have installed a screen, but you later want it to be removed and cleaned up, you can call [uninstall_screen][textual.app.App.uninstall_screen].

## Screen stack

Textual apps keep a _stack_ of screens. You can think of this screen stack as a stack of paper, where only the very top sheet is visible. If you remove the top sheet, the paper underneath becomes visible. Screens work in a similar way.

!!! note

    You can also make parts of the top screen translucent, so that deeper screens show through. See [Screen opacity](#screen-opacity).

The active screen (top of the stack) will render the screen and receive input events. The following API methods on the App class can manipulate this stack, and let you decide which screen the user can interact with.

### Push screen

The [push_screen][textual.app.App.push_screen] method puts a screen on top of the stack and makes that screen active. You can call this method with the name of an installed screen, or a screen object.

<div class="excalidraw">
--8<-- "docs/images/screens/push_screen.excalidraw.svg"
</div>

#### Action

You can also push screens with the `"app.push_screen"` action, which requires the name of an installed screen.

### Pop screen

The [pop_screen][textual.app.App.pop_screen] method removes the top-most screen from the stack, and makes the new top screen active.

!!! note

    The screen stack must always have at least one screen. If you attempt to remove the last screen, Textual will raise a [ScreenStackError][textual.app.ScreenStackError] exception.

<div class="excalidraw">
--8<-- "docs/images/screens/pop_screen.excalidraw.svg"
</div>


When you pop a screen it will be removed and deleted unless it has been installed or there is another copy of the screen on the stack.

#### Action

You can also pop screens with the `"app.pop_screen"` action.

### Switch screen

The [switch_screen][textual.app.App.switch_screen] method replaces the top of the stack with a new screen.

<div class="excalidraw">
--8<-- "docs/images/screens/switch_screen.excalidraw.svg"
</div>

Like [pop_screen](#pop-screen), if the screen being replaced is not installed it will be removed and deleted.

#### Action

You can also switch screens with the `"app.switch_screen"` action which accepts the name of the screen to switch to.



## Screen opacity

If a screen has a background color with an *alpha* component, then the background color will be blended with the screen beneath it.
For example, if the top-most screen has a background set to `rgba(0,0,255,0.5)` then anywhere in the screen not occupied with a widget will display the *second* screen from the top, tinted with 50% blue.


<div class="excalidraw">
--8<-- "docs/images/screens/screen_alpha.excalidraw.svg"
</div>


!!! note

    Although parts of other screens may be made visible with background alpha, only the top-most is *active* (can respond to mouse and keyboard).

One use of background alpha is to style *modal dialogs* (see below).


## Modal screens

Screens may be used to create modal dialogs, where the main interface is temporarily disabled (but still visible) while the user is entering information.

The following example pushes a screen when you hit the ++q++ key to ask you if you really want to quit.
From the quit screen you can click either Quit to exit the app immediately, or Cancel to dismiss the screen and return to the main screen.

=== "Output"

    ```{.textual path="docs/examples/guide/screens/modal01.py"}
    ```

=== "Output (after pressing ++q++)"

    ```{.textual path="docs/examples/guide/screens/modal01.py" press="q"}
    ```

=== "modal01.py"

    ```python title="modal01.py"
    --8<-- "docs/examples/guide/screens/modal01.py"
    ```

=== "modal01.tcss"

    ```css title="modal01.tcss"
    --8<-- "docs/examples/guide/screens/modal01.tcss"
    ```


Note the `request_quit` action in the app which pushes a new instance of `QuitScreen`.
This makes the quit screen active. If you click Cancel, the quit screen calls [pop_screen][textual.app.App.pop_screen] to return the default screen. This also removes and deletes the `QuitScreen` object.

There are two flaws with this modal screen, which we can fix in the same way.

The first flaw is that the app adds a new quit screen every time you press ++q++, even when the quit screen is still visible.
Consequently if you press ++q++ three times, you will have to click Cancel three times to get back to the main screen.
This is because bindings defined on App are always checked, and we call `push_screen` for every press of ++q++.

The second flaw is that the modal dialog doesn't *look* modal.
There is no indication that the main interface is still there, waiting to become active again.

We can solve both those issues by replacing our use of [Screen][textual.screen.Screen] with [ModalScreen][textual.screen.ModalScreen].
This screen sub-class will prevent key bindings on the app from being processed.
It also sets a background with a little alpha to allow the previous screen to show through.

Let's see what happens when we use `ModalScreen`.


=== "Output"

    ```{.textual path="docs/examples/guide/screens/modal02.py"}
    ```

=== "Output (after pressing ++q++)"

    ```{.textual path="docs/examples/guide/screens/modal02.py" press="q"}
    ```

=== "modal02.py"

    ```python title="modal02.py" hl_lines="3 15"
    --8<-- "docs/examples/guide/screens/modal02.py"
    ```

=== "modal01.tcss"

    ```css title="modal01.tcss"
    --8<-- "docs/examples/guide/screens/modal01.tcss"
    ```

Now when we press ++q++, the dialog is displayed over the main screen.
The main screen is darkened to indicate to the user that it is not active, and only the dialog will respond to input.

## Returning data from screens

It is a common requirement for screens to be able to return data.
For instance, you may want a screen to show a dialog and have the result of that dialog processed *after* the screen has been popped.

To return data from a screen, call [`dismiss()`][textual.screen.Screen.dismiss] on the screen with the data you wish to return.
This will pop the screen and invoke a callback set when the screen was pushed (with [`push_screen`][textual.app.App.push_screen]).

Let's modify the previous example to use `dismiss` rather than an explicit `pop_screen`.

=== "modal03.py"

    ```python title="modal03.py" hl_lines="15 27-30 47-50 52"
    --8<-- "docs/examples/guide/screens/modal03.py"
    ```

    1. See below for an explanation of the `[bool]`

=== "modal01.tcss"

    ```css title="modal01.tcss"
    --8<-- "docs/examples/guide/screens/modal01.tcss"
    ```

In the `on_button_pressed` message handler we call `dismiss` with a boolean that indicates if the user has chosen to quit the app.
This boolean is passed to the `check_quit` function we provided when `QuitScreen` was pushed.

Although this example behaves the same as the previous code, it is more flexible because it has removed responsibility for exiting from the modal screen to the caller.
This makes it easier for the app to perform any cleanup actions prior to exiting, for example.

Returning data in this way can help keep your code manageable by making it easy to re-use your `Screen` classes in other contexts.

### Typing screen results

You may have noticed in the previous example that we changed the base class to `ModalScreen[bool]`.
The addition of `[bool]` adds typing information that tells the type checker to expect a boolean in the call to `dismiss`, and that any callback set in `push_screen` should also expect the same type. As always, typing is optional in Textual, but this may help you catch bugs.


### Waiting for screens

It is also possible to wait on a screen to be dismissed, which can feel like a more natural way of expressing logic than a callback.
The [`push_screen_wait()`][textual.app.App.push_screen_wait] method will push a screen and wait for its result (the value from [`Screen.dismiss()`][textual.screen.Screen.dismiss]).

This can only be done from a [worker](./workers.md), so that waiting for the screen doesn't prevent your app from updating.

Let's look at an example that uses `push_screen_wait` to ask a question and waits for the user to reply by clicking a button.


=== "questions01.py"

    ```python title="questions01.py" hl_lines="35-37"
    --8<-- "docs/examples/guide/screens/questions01.py"
    ```

    1. Dismiss with `True` when pressing the Yes button.
    2. Dismiss with `False` when pressing the No button.
    3. The `work` decorator will make this method run in a worker (background task).
    4. Will return a result when the user clicks one of the buttons.


=== "questions01.tcss"

    ```css title="questions01.tcss"
    --8<-- "docs/examples/guide/screens/questions01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/screens/questions01.py"}
    ```

The mount handler on the app is decorated with `@work`, which makes the code run in a worker (background task).
In the mount handler we push the screen with the `push_screen_wait`.
When the user presses one of the buttons, the screen calls [`dismiss()`][textual.screen.Screen.dismiss] with either `True` or `False`.
This value is then returned from the `push_screen_wait` method in the mount handler.


## Modes

Some apps may benefit from having multiple screen stacks, rather than just one.
Consider an app with a dashboard screen, a settings screen, and a help screen.
These are independent in the sense that we don't want to prevent the user from switching between them, even if there are one or more modal screens on the screen stack.
But we may still want each individual screen to have a navigation stack where we can push and pop screens.

In Textual we can manage this with *modes*.
A mode is simply a named screen stack, which we can switch between as required.
When we switch modes, the topmost screen in the new mode becomes the active visible screen.

The following diagram illustrates such an app with modes.
On startup the app switches to the "dashboard" mode which makes the top of the stack visible.

<div class="excalidraw">
--8<-- "docs/images/screens/modes1.excalidraw.svg"
</div>

If we later change the mode to "settings", the top of that mode's screen stack becomes visible.

<div class="excalidraw">
--8<-- "docs/images/screens/modes2.excalidraw.svg"
</div>

To add modes to your app, define a [`MODES`][textual.app.App.MODES] class variable in your App class which should be a `dict` that maps the name of the mode on to either a screen object, a callable that returns a screen, or the name of an installed screen.
However you specify it, the values in `MODES` set the base screen for each mode's screen stack.

You can switch between these screens at any time by calling [`App.switch_mode`][textual.app.App.switch_mode].
When you switch to a new mode, the topmost screen in the new stack becomes visible.
Any calls to [`App.push_screen`][textual.app.App.push_screen] or [`App.pop_screen`][textual.app.App.pop_screen] will affect only the active mode.

You can set which mode will be active when the app starts by setting the [`DEFAULT_MODE`][textual.app.App.DEFAULT_MODE] class variable.

Let's look at an example with modes:

=== "modes01.py"

    ```python hl_lines="25-29 30-34 37"
    --8<-- "docs/examples/guide/screens/modes01.py"
    ```

    1. `switch_mode` is a builtin action to switch modes.
    2. Associates `DashboardScreen` with the name "dashboard".
    3. Switches to the dashboard mode.

=== "Output"

    ```{.textual path="docs/examples/guide/screens/modes01.py"}
    ```

=== "Output (after pressing S)"

    ```{.textual path="docs/examples/guide/screens/modes01.py", press="s"}
    ```

Here we have defined three screens.
One for a dashboard, one for settings, and one for help.
We've bound keys to each of these screens, so the user can switch between the screens.

Pressing ++d++, ++s++, or ++h++ switches between these modes.


## Screen events

Textual will send a [ScreenSuspend](../events/screen_suspend.md) event to screens that have become inactive due to another screen being pushed, or switching via a mode.

When a screen becomes active, Textual will send a [ScreenResume](../events/screen_resume.md) event to the newly active screen.

These events can be useful if you want to disable processing for a screen that is no longer visible, for example.
````

## File: docs/guide/styles.md
````markdown
# Styles

In this chapter we will explore how you can apply styles to your application to create beautiful user interfaces.

## Styles object

Every Textual widget class provides a `styles` object which contains a number of attributes. These attributes tell Textual how the widget should be displayed. Setting any of these attributes will update the screen accordingly.

!!! note

    These docs use the term *screen* to describe the contents of the terminal, which will typically be a window on your desktop.

Let's look at a simple example which sets styles on `screen` (a special widget that represents the screen).

```python title="screen.py" hl_lines="6-7"
--8<-- "docs/examples/guide/styles/screen.py"
```

The first line sets the [background](../styles/background.md) style to `"darkblue"` which will change the background color to dark blue. There are a few other ways of setting color which we will explore later.

The second line sets [border](../styles/border.md) to a tuple of `("heavy", "white")` which tells Textual to draw a white border with a style of `"heavy"`. Running this code will show the following:

```{.textual path="docs/examples/guide/styles/screen.py"}
```

## Styling widgets

Setting styles on screen is useful, but to create most user interfaces we will also need to apply styles to other widgets.

The following example adds a static widget which we will apply some styles to:

```python title="widget.py" hl_lines="7 11-12"
--8<-- "docs/examples/guide/styles/widget.py"
```

The compose method stores a reference to the widget before yielding it. In the mount handler we use that reference to set the same styles on the widget as we did for the screen example. Here is the result:

```{.textual path="docs/examples/guide/styles/widget.py"}
```

Widgets will occupy the full width of their container and as many lines as required to fit in the vertical direction.

Note how the combined height of the widget is three rows in the terminal. This is because a border adds two rows (and two columns). If you were to remove the line that sets the border style, the widget would occupy a single row.

!!! information

    Widgets will wrap text by default. If you were to replace `"Textual"` with a long paragraph of text, the widget will expand downwards to fit.

## Colors

There are a number of style attributes which accept colors. The most commonly used are [color](../styles/color.md) which sets the default color of text on a widget, and [background](../styles/background.md) which sets the background color (beneath the text).

You can set a color value to one of a number of pre-defined color constants, such as `"crimson"`, `"lime"`, and `"palegreen"`. You can find a full list in the [Color API](../api/color.md#textual.color--named-colors).

Here's how you would set the screen background to lime:

```python
self.screen.styles.background = "lime"
```

In addition to color names, you can also use any of the following ways of expressing a color:

- RGB hex colors starts with a `#` followed by three pairs of one or two hex digits; one for the red, green, and blue color components. For example, `#f00` is an intense red color, and `#9932CC` is *dark orchid*.
- RGB decimal color start with `rgb` followed by a tuple of three numbers in the range 0 to 255. For example `rgb(255,0,0)` is intense red, and `rgb(153,50,204)` is *dark orchid*.
- HSL colors start with `hsl` followed by a angle between 0 and 360 and two percentage values, representing Hue, Saturation and Lightness. For example `hsl(0,100%,50%)` is intense red and `hsl(280,60%,49%)` is *dark orchid*.


The background and color styles also accept a [Color][textual.color.Color] object which can be used to create colors dynamically.

The following example adds three widgets and sets their color styles.

```python title="colors01.py" hl_lines="16-19"
--8<-- "docs/examples/guide/styles/colors01.py"
```

Here is the output:

```{.textual path="docs/examples/guide/styles/colors01.py"}
```

### Alpha

Textual represents color internally as a tuple of three values for the red, green, and blue components.

Textual supports a common fourth value called *alpha* which can make a color translucent. If you set alpha on a background color, Textual will blend the background with the color beneath it. If you set alpha on the text color, then Textual will blend the text with the background color.

There are a few ways you can set alpha on a color in Textual.

- You can set the alpha value of a color by adding a fourth digit or pair of digits to a hex color. The extra digits form an alpha component which ranges from 0 for completely transparent to 255 (completely opaque). Any value between 0 and 255 will be translucent. For example `"#9932CC7f"` is a dark orchid which is roughly 50% translucent.
- You can also set alpha with the `rgba` format, which is identical to `rgb` with the additional of a fourth value that should be between 0 and 1, where 0 is invisible and 1 is opaque. For example `"rgba(192,78,96,0.5)"`.
- You can add the `a` parameter on a [Color][textual.color.Color] object. For example `Color(192, 78, 96, a=0.5)` creates a translucent dark orchid.

The following example shows what happens when you set alpha on background colors:

```python title="colors01.py" hl_lines="12-15"
--8<-- "docs/examples/guide/styles/colors02.py"
```

Notice that at an alpha of 0.1 the background almost matches the screen, but at 1.0 it is a solid color.

```{.textual path="docs/examples/guide/styles/colors02.py"}
```

## Dimensions

Widgets occupy a rectangular region of the screen, which may be as small as a single character or as large as the screen (potentially *larger* if [scrolling](../styles/overflow.md) is enabled).

### Box Model

The following styles influence the dimensions of a widget.

- [width](../styles/width.md) and [height](../styles/height.md) define the size of the widget.
- [padding](../styles/padding.md) adds optional space around the content area.
- [border](../styles/border.md) draws an optional rectangular border around the padding and the content area.

Additionally, the [margin](../styles/margin.md) style adds space around a widget's border, which isn't technically part of the widget, but provides visual separation between widgets.

Together these styles compose the widget's *box model*. The following diagram shows how these settings are combined:

<div class="excalidraw">
--8<-- "docs/images/styles/box.excalidraw.svg"
</div>

### Width and height

Setting the width restricts the number of columns used by a widget, and setting the height restricts the number of rows. Let's look at an example which sets both dimensions.

```python title="dimensions01.py" hl_lines="21-22"
--8<-- "docs/examples/guide/styles/dimensions01.py"
```

This code produces the following result.

```{.textual path="docs/examples/guide/styles/dimensions01.py"}
```

Note how the text wraps, but doesn't fit in the 10 lines provided, resulting in the last line being omitted entirely.

#### Auto dimensions

In practice, we generally want the size of a widget to adapt to its content, which we can do by setting a dimension to `"auto"`.

Let's set the height to auto and see what happens.

```python title="dimensions02.py" hl_lines="22"
--8<-- "docs/examples/guide/styles/dimensions02.py"
```

If you run this you will see the height of the widget now grows to accommodate the full text:

```{.textual path="docs/examples/guide/styles/dimensions02.py"}
```

### Units

Textual offers a few different *units* which allow you to specify dimensions relative to the screen or container. Relative units can better make use of available space if the user resizes the terminal.

- Percentage units are given as a number followed by a percent (`%`) symbol and will set a dimension to a proportion of the widget's *parent* size. For instance, setting width to `"50%"` will cause a widget to be half the width of its parent.
- View units are similar to percentage units, but explicitly reference a dimension. The `vw` unit sets a dimension to a percentage of the terminal *width*, and `vh` sets a dimension to a percentage of the terminal *height*.
- The `w` unit sets a dimension to a percentage of the available width (which may be smaller than the terminal size if the widget is within another widget).
- The `h` unit sets a dimension to a percentage of the available height.


The following example demonstrates applying percentage units:

```python title="dimensions03.py" hl_lines="21-22"
--8<-- "docs/examples/guide/styles/dimensions03.py"
```

With the width set to `"50%"` and the height set to `"80%"`, the widget will keep those relative dimensions when resizing the terminal window:


=== "60 x 20"

    ```{.textual path="docs/examples/guide/styles/dimensions03.py" columns="60" lines="20"}
    ```

=== "80 x 30"

    ```{.textual path="docs/examples/guide/styles/dimensions03.py" columns="80" lines="30"}
    ```

=== "120 x 40"

    ```{.textual path="docs/examples/guide/styles/dimensions03.py" columns="120" lines="40"}
    ```

#### FR units

Percentage units can be problematic for some relative values. For instance, if we want to divide the screen into thirds, we would have to set a dimension to `33.3333333333%` which is awkward. Textual supports `fr` units which are often better than percentage-based units for these situations.

When specifying `fr` units for a given dimension, Textual will divide the available space by the sum of the `fr` units for that dimension. That space is then assigned according to each widget's `fr` values.

Let's look at an example. We will create two widgets, one with a height of `"2fr"` and one with a height of `"1fr"`.

```python title="dimensions04.py" hl_lines="24-25"
--8<-- "docs/examples/guide/styles/dimensions04.py"
```

The total `fr` units for height is 3.
The first widget has a height ot `2fr`, which results in the height being two thirds of the total height.
The second widget has a height of `1fr` which makes it take up the remaining third of the height.
Here's what that looks like.

```{.textual path="docs/examples/guide/styles/dimensions04.py"}
```

### Maximum and minimums

The same units may also be used to set limits on a dimension.
The following styles set minimum and maximum sizes and can accept any of the values used in width and height.

- [min-width](../styles/min_width.md) sets a minimum width.
- [max-width](../styles/max_width.md) sets a maximum width.
- [min-height](../styles/min_height.md) sets a minimum height.
- [max-height](../styles/max_height.md) sets a maximum height.

### Padding

Padding adds space around your content which can aid readability. Setting [padding](../styles/padding.md) to an integer will add that number additional rows and columns around the content area. The following example sets padding to 2:

```python title="padding01.py" hl_lines="22"
--8<-- "docs/examples/guide/styles/padding01.py"
```

Notice the additional space around the text:

```{.textual path="docs/examples/guide/styles/padding01.py"}
```

You can also set padding to a tuple of *two* integers which will apply padding to the top/bottom and left/right edges. The following example sets padding to `(2, 4)` which adds two rows to the top and bottom of the widget, and 4 columns to the left and right of the widget.

```python title="padding02.py" hl_lines="22"
--8<-- "docs/examples/guide/styles/padding02.py"
```

Compare the output of this example to the previous example:

```{.textual path="docs/examples/guide/styles/padding02.py"}
```

You can also set padding to a tuple of *four* values which applies padding to each edge individually. The first value is the padding for the top of the widget, followed by the right of the widget, then bottom, then left.

### Border

The [border](../styles/border.md) style draws a border around a widget. To add a border set `styles.border` to a tuple of two values. The first value is the border type, which should be a string. The second value is the border color which will accept any value that works with  [color](../styles/color.md) and [background](../styles/background.md).

The following example adds a border around a widget:

```python title="border01.py" hl_lines="21"
--8<-- "docs/examples/guide/styles/border01.py"
```

Here is the result:

```{.textual path="docs/examples/guide/styles/border01.py"}
```

There are many other border types. Run the following from the command prompt to preview them.


```bash
textual borders
```


#### Title alignment

Widgets have two attributes, `border_title` and `border_subtitle` which (if set) will be displayed within the border.
The `border_title` attribute is displayed in the top border, and `border_subtitle` is displayed in the bottom border.

There are two styles to set the alignment of these border labels, which may be set to "left", "right", or "center".

 - [`border-title-align`](../styles/border_title_align.md) sets the alignment of the title, which defaults to "left".
 - [`border-subtitle-align`](../styles/border_subtitle_align.md) sets the alignment of the subtitle, which defaults to "right".

The following example sets both titles and changes the alignment of the title (top) to "center".

```py hl_lines="22-24"
--8<-- "docs/examples/guide/styles/border_title.py"
```

Note the addition of the titles and their alignments:

```{.textual path="docs/examples/guide/styles/border_title.py"}
```

### Outline

[Outline](../styles/outline.md) is similar to border and is set in the same way. The difference is that outline will not change the size of the widget, and may overlap the content area. The following example sets an outline on a widget:

```python title="outline01.py" hl_lines="22"
--8<-- "docs/examples/guide/styles/outline01.py"
```

Notice how the outline overlaps the text in the widget.

```{.textual path="docs/examples/guide/styles/outline01.py"}
```

Outline can be useful to emphasize a widget, but be mindful that it may obscure your content.

### Box sizing

When you set padding or border it reduces the size of the widget's content area. In other words, setting padding or border won't change the width or height of the widget.

This is generally desirable when you arrange things on screen as you can add border or padding without breaking your layout. Occasionally though you may want to keep the size of the content area constant and grow the size of the widget to fit padding and border. The [box-sizing](../styles/box_sizing.md) style allows you to switch between these two modes.

If you set `box_sizing` to `"content-box"` then the space required for padding and border will be added to the widget dimensions. The default value of `box_sizing` is `"border-box"`. Compare the box model diagram for `content-box` to the box model for `border-box`.

=== "content-box"

    <div class="excalidraw">
    --8<-- "docs/images/styles/content_box.excalidraw.svg"
    </div>

=== "border-box"

    <div class="excalidraw">
    --8<-- "docs/images/styles/border_box.excalidraw.svg"
    </div>


The following example creates two widgets with a width of 30, a height of 6, and a border and padding of 1.
The first widget has the default `box_sizing` (`"border-box"`).
The second widget sets `box_sizing` to `"content-box"`.

```python title="box_sizing01.py" hl_lines="32"
--8<-- "docs/examples/guide/styles/box_sizing01.py"
```

The padding and border of the first widget is subtracted from the height leaving only 2 lines in the content area. The second widget also has a height of 6, but the padding and border adds additional height so that the content area remains 6 lines.

```{.textual path="docs/examples/guide/styles/box_sizing01.py"}
```

### Margin

Margin is similar to padding in that it adds space, but unlike padding, [margin](../styles/margin.md) is outside of the widget's border. It is used to add space between widgets.

The following example creates two widgets, each with a margin of 2.

```python title="margin01.py" hl_lines="26-27"
--8<-- "docs/examples/guide/styles/margin01.py"
```

Notice how each widget has an additional two rows and columns around the border.

```{.textual path="docs/examples/guide/styles/margin01.py"}
```

!!! note "Margins overlap"

    In the above example both widgets have a margin of 2, but there are only 2 lines of space between the widgets. This is because margins of consecutive widgets *overlap*. In other words when there are two widgets next to each other Textual picks the greater of the two margins.

## More styles

We've covered some fundamental styles used by Textual apps, but there are many more which you can use to customize all aspects of how your app looks. See the [Styles reference](../styles/index.md) for a comprehensive list.

In the next chapter we will discuss Textual CSS which is a powerful way of applying styles to widgets that keeps your code free of style attributes.
````

## File: docs/guide/testing.md
````markdown
# Testing

Code testing is an important part of software development.
This chapter will cover how to write tests for your Textual apps.

## What is testing?

It is common to write tests alongside your app.
A *test* is simply a function that confirms your app is working correctly.

!!! tip "Learn more about testing"

    We recommend [Python Testing with pytest](https://pythontest.com/pytest-book/) for a comprehensive guide to writing tests.

## Do you need to write tests?

The short answer is "no", you don't *need* to write tests.

In practice however, it is almost always a good idea to write tests.
Writing code that is completely bug free is virtually impossible, even for experienced developers.
If you want to have confidence that your application will run as you intended it to, then you should write tests.
Your test code will help you find bugs early, and alert you if you accidentally break something in the future.

## Testing frameworks for Textual

Textual is an async framework powered by Python's [asyncio](https://docs.python.org/3/library/asyncio.html) library.
While Textual doesn't require a particular test framework, it must provide support for asyncio testing.

You can use any test framework you are familiar with, but we will be using [pytest](https://docs.pytest.org/)
along with the [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) plugin in this chapter.

By default, the `pytest-asyncio` plugin requires each async test to be decorated with `@pytest.mark.asyncio`.
You can avoid having to add this marker to every async test
by setting `asyncio_mode = auto` in your pytest configuration
or by running pytest with the `--asyncio-mode=auto` option.

## Testing apps

You can often test Textual code in the same way as any other app, and use similar techniques.
But when testing user interface interactions, you may need to use Textual's dedicated test features.

Let's write a simple Textual app so we can demonstrate how to test it.
The following app shows three buttons labelled "red", "green", and "blue".
Clicking one of those buttons or pressing a corresponding ++r++, ++g++, and ++b++ key will change the background color.

=== "rgb.py"

    ```python
    --8<-- "docs/examples/guide/testing/rgb.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/testing/rgb.py"}
    ```

Although it is straightforward to test an app like this manually, it is not practical to click every button and hit every key in your app after changing a single line of code.
Tests allow us to automate such testing so we can quickly simulate user interactions and check the result.

To test our simple app we will use the [`run_test()`][textual.app.App.run_test] method on the `App` class.
This replaces the usual call to [`run()`][textual.app.App.run] and will run the app in *headless* mode, which prevents Textual from updating the terminal but otherwise behaves as normal.

The `run_test()` method is an *async context manager* which returns a [`Pilot`][textual.pilot.Pilot] object.
You can use this object to interact with the app as if you were operating it with a keyboard and mouse.

Let's look at the tests for the example above:

```python title="test_rgb.py"
--8<-- "docs/examples/guide/testing/test_rgb.py"
```

1. The `run_test()` method requires that it run in a coroutine, so tests must use the `async` keyword.
2. This runs the app and returns a Pilot instance we can use to interact with it.
3. Simulates pressing the ++r++ key.
4. This checks that pressing the ++r++ key has resulted in the background color changing.
5. Simulates clicking on the widget with an `id` of `red` (the button labelled "Red").

There are two tests defined in `test_rgb.py`.
The first to test keys and the second to test button clicks.
Both tests first construct an instance of the app and then call `run_test()` to get a Pilot object.
The `test_keys` function simulates key presses with [`Pilot.press`][textual.pilot.Pilot.press], and `test_buttons` simulates button clicks with [`Pilot.click`][textual.pilot.Pilot.click].

After simulating a user interaction, Textual tests will typically check the state has been updated with an `assert` statement.
The `pytest` module will record any failures of these assert statements as a test fail.

If you run the tests with `pytest test_rgb.py` you should get 2 passes, which will confirm that the user will be able to click buttons or press the keys to change the background color.

If you later update this app, and accidentally break this functionality, one or more of your tests will fail.
Knowing which test has failed will help you quickly track down where your code was broken.

## Simulating key presses

We've seen how the [`press`][textual.pilot.Pilot] method simulates keys.
You can also supply multiple keys to simulate the user typing into the app.
Here's an example of simulating the user typing the word "hello".

```python
await pilot.press("h", "e", "l", "l", "o")
```

Each string creates a single keypress.
You can also use the name for non-printable keys (such as "enter") and the "ctrl+" modifier.
These are the same identifiers as used for key events, which you can experiment with by running `textual keys`.

## Simulating clicks

You can simulate mouse clicks in a similar way with [`Pilot.click`][textual.pilot.Pilot.click].
If you supply a CSS selector Textual will simulate clicking on the matching widget.

!!! note

    If there is another widget in front of the widget you want to click, you may end up clicking the topmost widget rather than the widget indicated in the selector.
    This is generally what you want, because a real user would experience the same thing.

### Clicking the screen

If you don't supply a CSS selector, then the click will be relative to the screen.
For example, the following simulates a click at (0, 0):

```python
await pilot.click()
```

### Click offsets

If you supply an `offset` value, it will be added to the coordinates of the simulated click.
For example the following line would simulate a click at the coordinates (10, 5).


```python
await pilot.click(offset=(10, 5))
```

If you combine this with a selector, then the offset will be relative to the widget.
Here's how you would click the line *above* a button.

```python
await pilot.click(Button, offset=(0, -1))
```

### Double & triple clicks

You can simulate double and triple clicks by setting the `times` parameter.

```python
await pilot.click(Button, times=2)  # Double click
await pilot.click(Button, times=3)  # Triple click
```

### Modifier keys

You can simulate clicks in combination with modifier keys, by setting the `shift`, `meta`, or `control` parameters.
Here's how you could simulate ctrl-clicking a widget with an ID of "slider":

```python
await pilot.click("#slider", control=True)
```

## Changing the screen size

The default size of a simulated app is (80, 24).
You may want to test what happens when the app has a different size.
To do this, set the `size` parameter of [`run_test`][textual.app.App.run_test] to a different size.
For example, here is how you would simulate a terminal resized to 100 columns and 50 lines:

```python
async with app.run_test(size=(100, 50)) as pilot:
    ...
```

## Pausing the pilot

Some actions in a Textual app won't change the state immediately.
For instance, messages may take a moment to bubble from the widget that sent them.
If you were to post a message and immediately `assert` you may find that it fails because the message hasn't yet been processed.

You can generally solve this by calling [`pause()`][textual.pilot.Pilot.pause] which will wait for all pending messages to be processed.
You can also supply a `delay` parameter, which will insert a delay prior to waiting for pending messages.


## Textual's tests

Textual itself has a large battery of tests.
If you are interested in how we write tests, see the [tests/](https://github.com/Textualize/textual/tree/main/tests) directory in the Textual repository.

## Snapshot testing

Snapshot testing is the process of recording the output of a test, and comparing it against the output from previous runs.

Textual uses snapshot testing internally to ensure that the builtin widgets look and function correctly in every release.
We've made the pytest plugin we built available for public use.

The [official Textual pytest plugin](https://github.com/Textualize/pytest-textual-snapshot) can help you catch otherwise difficult to detect visual changes in your app.

It works by generating an SVG _screenshot_ (such as the images in these docs) from your app.
If the screenshot changes in any test run, you will have the opportunity to visually compare the new output against previous runs.


### Installing the plugin

You can install `pytest-textual-snapshot` using your favorite package manager (`pip`, `poetry`, etc.).

```
pip install pytest-textual-snapshot
```

### Creating a snapshot test

With the package installed, you now have access to the `snap_compare` pytest fixture.

Let's look at an example of how we'd create a snapshot test for the [calculator app](https://github.com/Textualize/textual/blob/main/examples/calculator.py) below.

```{.textual path="examples/calculator.py" columns=100 lines=41 press="3,.,1,4,5,9,2,wait:400"}
```

First, we need to create a new test and specify the path to the Python file containing the app.
This path should be relative to the location of the test.

```python
def test_calculator(snap_compare):
    assert snap_compare("path/to/calculator.py")
```

Let's run the test as normal using `pytest`.

```
pytest
```

When this test runs for the first time, an SVG screenshot of the calculator app is generated, and the test will fail.
Snapshot tests always fail on the first run, since there's no previous version to compare the snapshot to.

![snapshot_report_console_output.png](../images/testing/snapshot_report_console_output.png)

If you open the snapshot report in your browser, you'll see something like this:

![snapshot_report_example.png](../images/testing/snapshot_report_example.png)

!!! tip

    You can usually open the link directly from the terminal, but some terminal emulators may
    require you to hold ++ctrl++ or ++command++ while clicking for links to work.

The report explains that there's "No history for this test".
It's our job to validate that the initial snapshot looks correct before proceeding.
Our calculator is rendering as we expect, so we'll save this snapshot:

```
pytest --snapshot-update
```

!!! warning

    Only ever run pytest with `--snapshot-update` if you're happy with how the output looks
    on the left hand side of the snapshot report. When using `--snapshot-update`, you're saying "I'm happy with all of the
    screenshots in the snapshot test report, and they will now represent the ground truth which all future runs will be compared
    against". As such, you should only run `pytest --snapshot-update` _after_ running `pytest` and confirming the output looks good.

Now that our snapshot is saved, if we run `pytest` (with no arguments) again, the test will pass.
This is because the screenshot taken during this test run matches the one we saved earlier.

### Catching a bug

The real power of snapshot testing comes from its ability to catch visual regressions which could otherwise easily be missed.

Imagine a new developer joins your team, and tries to make a few changes to the calculator.
While making this change they accidentally break some styling which removes the orange coloring from the buttons on the right of the app.
When they run `pytest`, they're presented with a report which reveals the damage:

![snapshot_report_diff_before.png](../images/testing/snapshot_report_diff_before.png)

On the right, we can see our "historical" snapshot - this is the one we saved earlier.
On the left is how our app is currently rendering - clearly not how we intended!

We can click the "Show difference" toggle at the top right of the diff to overlay the two versions:

![snapshot_report_diff_after.png](../images/testing/snapshot_report_diff_after.png)

This reveals another problem, which could easily be missed in a quick visual inspection -
our new developer has also deleted the number 4!

!!! tip

    Snapshot tests work well in CI on all supported operating systems, and the snapshot
    report is just an HTML file which can be exported as a build artifact.


### Pressing keys

You can simulate pressing keys before the snapshot is captured using the `press` parameter.

```python
def test_calculator_pressing_numbers(snap_compare):
    assert snap_compare("path/to/calculator.py", press=["1", "2", "3"])
```

### Changing the terminal size

To capture the snapshot with a different terminal size, pass a tuple `(width, height)` as the `terminal_size` parameter.

```python
def test_calculator(snap_compare):
    assert snap_compare("path/to/calculator.py", terminal_size=(50, 100))
```

### Running setup code

You can also run arbitrary code before the snapshot is captured using the `run_before` parameter.

In this example, we use `run_before` to hover the mouse cursor over the widget with ID `number-5`
before taking the snapshot.

```python
def test_calculator_hover_number(snap_compare):
    async def run_before(pilot) -> None:
        await pilot.hover("#number-5")

    assert snap_compare("path/to/calculator.py", run_before=run_before)
```

For more information, visit the [`pytest-textual-snapshot` repo on GitHub](https://github.com/Textualize/pytest-textual-snapshot).
````

## File: docs/guide/widgets.md
````markdown
# Widgets

In this chapter we will explore widgets in more detail, and how you can create custom widgets of your own.


## What is a widget?

A widget is a component of your UI responsible for managing a rectangular region of the screen. Widgets may respond to [events](./events.md) in much the same way as an app. In many respects, widgets are like mini-apps.

!!! information

    Every widget runs in its own asyncio task.

## Custom widgets

There is a growing collection of [builtin widgets](../widgets/index.md) in Textual, but you can build entirely custom widgets that work in the same way.

The first step in building a widget is to import and extend a widget class. This can either be [Widget][textual.widget.Widget] which is the base class of all widgets, or one of its subclasses.

Let's create a simple custom widget to display a greeting.


```python title="hello01.py" hl_lines="5-9"
--8<-- "docs/examples/guide/widgets/hello01.py"
```

The highlighted lines define a custom widget class with just a [render()][textual.widget.Widget.render] method.
Textual will display whatever is returned from render in the [content](./content.md) area of your widget.

Note that the text contains tags in square brackets, i.e. `[b]`.
This is [content markup](./content.md#markup) which allows you to embed various styles within your content.
If you run this you will find that `World` is in bold.

```{.textual path="docs/examples/guide/widgets/hello01.py"}
```

This (very simple) custom widget may be [styled](./styles.md) in the same way as builtin widgets, and targeted with CSS. Let's add some CSS to this app.


=== "hello02.py"

    ```python title="hello02.py" hl_lines="13"
    --8<-- "docs/examples/guide/widgets/hello02.py"
    ```

=== "hello02.tcss"

    ```css title="hello02.tcss"
    --8<-- "docs/examples/guide/widgets/hello02.tcss"
    ```

The addition of the CSS has completely transformed our custom widget.

```{.textual path="docs/examples/guide/widgets/hello02.py"}
```

## Static widget

While you can extend the Widget class, a subclass will typically be a better starting point. The [Static][textual.widgets.Static] class is a widget subclass which caches the result of render, and provides an [update()][textual.widgets.Static.update] method to update the content area.

Let's use Static to create a widget which cycles through "hello" in various languages.

=== "hello03.py"

    ```python title="hello03.py" hl_lines="23-35"
    --8<-- "docs/examples/guide/widgets/hello03.py"
    ```

=== "hello03.tcss"

    ```css title="hello03.tcss"
    --8<-- "docs/examples/guide/widgets/hello03.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello03.py"}
    ```

Note that there is no `render()` method on this widget. The Static class is handling the render for us. Instead we call `update()` when we want to update the content within the widget.

The `next_word` method updates the greeting. We call this method from the mount handler to get the first word, and from a click handler to cycle through the greetings when we click the widget.

### Default CSS

When building an app it is best to keep your CSS in an external file. This allows you to see all your CSS in one place, and to enable live editing. However if you intend to distribute a widget (via PyPI for instance) it can be convenient to bundle the code and CSS together. You can do this by adding a `DEFAULT_CSS` class variable inside your widget class.

Textual's builtin widgets bundle CSS in this way, which is why you can see nicely styled widgets without having to copy any CSS code.

Here's the Hello example again, this time the widget has embedded default CSS:

=== "hello04.py"

    ```python title="hello04.py" hl_lines="26-35"
    --8<-- "docs/examples/guide/widgets/hello04.py"
    ```

=== "hello04.tcss"

    ```css title="hello04.tcss"
    --8<-- "docs/examples/guide/widgets/hello04.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello04.py"}
    ```

#### Scoped CSS

Default CSS is *scoped* by default.
All this means is that CSS defined in `DEFAULT_CSS` will affect the widget and potentially its children only.
This is to prevent you from inadvertently breaking an unrelated widget.

You can disable scoped CSS by setting the class var `SCOPED_CSS` to `False`.

#### Default specificity

CSS defined within `DEFAULT_CSS` has an automatically lower [specificity](./CSS.md#specificity) than CSS read from either the App's `CSS` class variable or an external stylesheet. In practice this means that your app's CSS will take precedence over any CSS bundled with widgets.


## Text links

Text in a widget may be marked up with links which perform an action when clicked.
Links in markup use the following format:

```
"Click [@click=app.bell]Me[/]"
```

The `@click` tag introduces a click handler, which runs the `app.bell` action.

Let's use links in the hello example so that the greeting becomes a link which updates the widget.


=== "hello05.py"

    ```python title="hello05.py"  hl_lines="23-32"
    --8<-- "docs/examples/guide/widgets/hello05.py"
    ```

=== "hello05.tcss"

    ```css title="hello05.tcss"
    --8<-- "docs/examples/guide/widgets/hello05.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello05.py"}
    ```

If you run this example you will see that the greeting has been underlined, which indicates it is clickable. If you click on the greeting it will run the `next_word` action which updates the next word.


## Border titles

Every widget has a [`border_title`][textual.widgets.Widget.border_title] and [`border_subtitle`][textual.widgets.Widget.border_subtitle] attribute.
Setting `border_title` will display text within the top border, and setting `border_subtitle` will display text within the bottom border.

!!! note

    Border titles will only display if the widget has a [border](../styles/border.md) enabled.

The default value for these attributes is empty string, which disables the title.
You can change the default value for the title attributes with the [`BORDER_TITLE`][textual.widget.Widget.BORDER_TITLE] and [`BORDER_SUBTITLE`][textual.widget.Widget.BORDER_SUBTITLE] class variables.

Let's demonstrate setting a title, both as a class variable and a instance variable:


=== "hello06.py"

    ```python title="hello06.py"  hl_lines="26 30"
    --8<-- "docs/examples/guide/widgets/hello06.py"
    ```

    1. Setting the default for the `title` attribute via class variable.
    2. Setting `subtitle` via an instance attribute.

=== "hello06.tcss"

    ```css title="hello06.tcss"
    --8<-- "docs/examples/guide/widgets/hello06.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/hello06.py"}
    ```

Note that titles are limited to a single line of text.
If the supplied text is too long to fit within the widget, it will be cropped (and an ellipsis added).

There are a number of styles that influence how titles are displayed (color and alignment).
See the [style reference](../styles/index.md) for details.

## Focus & keybindings

Widgets can have a list of associated key [bindings](../guide/input.md#bindings),
which let them call [actions](../guide/actions.md) in response to key presses.

A widget is able to handle key presses if it or one of its descendants has [focus](../guide/input.md#input-focus).

Widgets aren't focusable by default.
To allow a widget to be focused, we need to set `can_focus=True` when defining a widget subclass.
Here's an example of a simple focusable widget:

=== "counter01.py"

    ```python title="counter01.py" hl_lines="6"
    --8<-- "docs/examples/guide/widgets/counter01.py"
    ```

    1. Allow the widget to receive input focus.

=== "counter.tcss"

    ```css title="counter.tcss" hl_lines="6-11"
    --8<-- "docs/examples/guide/widgets/counter.tcss"
    ```

    1. These styles are applied only when the widget has focus.

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/counter01.py"}
    ```


The app above contains three `Counter` widgets, which we can focus by clicking or using ++tab++ and ++shift+tab++.

Now that our counter is focusable, let's add some keybindings to it to allow us to change the count using the keyboard.
To do this, we add a `BINDINGS` class variable to `Counter`, with bindings for ++up++ and ++down++.
These new bindings are linked to the `change_count` action, which updates the `count` reactive attribute.

With our bindings in place, we can now change the count of the _currently focused_ counter using ++up++ and ++down++.

=== "counter02.py"

    ```python title="counter02.py" hl_lines="9-12 19-20"
    --8<-- "docs/examples/guide/widgets/counter02.py"
    ```

    1. Associates presses of ++up++ or ++k++ with the `change_count` action, passing `1` as the argument to increment the count. The final argument ("Increment") is a user-facing label displayed in the footer when this binding is active.
    2. Called when the binding is triggered. Take care to add the `action_` prefix to the method name.

=== "counter.tcss"

    ```css title="counter.tcss"
    --8<-- "docs/examples/guide/widgets/counter.tcss"
    ```

    1. These styles are applied only when the widget has focus.

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/counter02.py" press="up,tab,down,down"}
    ```

## Rich renderables

In previous examples we've set strings as content for Widgets. You can also use special objects called [renderables](https://rich.readthedocs.io/en/latest/protocol.html) for advanced visuals. You can use any renderable defined in [Rich](https://github.com/Textualize/rich) or third party libraries.

Lets make a widget that uses a Rich table for its content. The following app is a solution to the classic [fizzbuzz](https://en.wikipedia.org/wiki/Fizz_buzz) problem often used to screen software engineers in job interviews. The problem is this: Count up from 1 to 100, when the number is divisible by 3, output "fizz"; when the number is divisible by 5, output "buzz"; and when the number is divisible by both 3 and 5 output "fizzbuzz".

This app will "play" fizz buzz by displaying a table of the first 15 numbers and columns for fizz and buzz.

=== "fizzbuzz01.py"

    ```python title="fizzbuzz01.py" hl_lines="18"
    --8<-- "docs/examples/guide/widgets/fizzbuzz01.py"
    ```

=== "fizzbuzz01.tcss"

    ```css title="fizzbuzz01.tcss" hl_lines="32-35"
    --8<-- "docs/examples/guide/widgets/fizzbuzz01.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/fizzbuzz01.py"}
    ```

## Content size

Textual will auto-detect the dimensions of the content area from rich renderables if width or height is set to `auto`. You can override auto dimensions by implementing [get_content_width()][textual.widget.Widget.get_content_width] or [get_content_height()][textual.widget.Widget.get_content_height].

Let's modify the default width for the fizzbuzz example. By default, the table will be just wide enough to fix the columns. Let's force it to be 50 characters wide.


=== "fizzbuzz02.py"

    ```python title="fizzbuzz02.py" hl_lines="10 21-23"
    --8<-- "docs/examples/guide/widgets/fizzbuzz02.py"
    ```

=== "fizzbuzz02.tcss"

    ```css title="fizzbuzz02.tcss"
    --8<-- "docs/examples/guide/widgets/fizzbuzz02.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/fizzbuzz02.py"}
    ```

Note that we've added `expand=True` to tell the `Table` to expand beyond the optimal width, so that it fills the 50 characters returned by `get_content_width`.

## Tooltips

Widgets can have *tooltips* which is content displayed when the user hovers the mouse over the widget.
You can use tooltips to add supplementary information or help messages.

!!! tip

    It is best not to rely on tooltips for essential information.
    Some users prefer to use the keyboard exclusively and may never see tooltips.


To add a tooltip, assign to the widget's [`tooltip`][textual.widgets.Widget.tooltip] property.
You can set text or any other [Rich](https://github.com/Textualize/rich) renderable.

The following example adds a tooltip to a button:

=== "tooltip01.py"

    ```python title="tooltip01.py"
    --8<-- "docs/examples/guide/widgets/tooltip01.py"
    ```

=== "Output (before hover)"

    ```{.textual path="docs/examples/guide/widgets/tooltip01.py"}
    ```

=== "Output (after hover)"

    ```{.textual path="docs/examples/guide/widgets/tooltip01.py" hover="Button"}
    ```

### Customizing the tooltip

If you don't like the default look of the tooltips, you can customize them to your liking with CSS.
Add a rule to your CSS that targets `Tooltip`. Here's an example:

=== "tooltip02.py"

    ```python title="tooltip02.py" hl_lines="15-19"
    --8<-- "docs/examples/guide/widgets/tooltip02.py"
    ```

=== "Output (before hover)"

    ```{.textual path="docs/examples/guide/widgets/tooltip02.py"}
    ```

=== "Output (after hover)"

    ```{.textual path="docs/examples/guide/widgets/tooltip02.py" hover="Button"}
    ```

## Loading indicator

Widgets have a [`loading`][textual.widget.Widget.loading] reactive which when set to `True` will temporarily replace your widget with a [`LoadingIndicator`](../widgets/loading_indicator.md).

You can use this to indicate to the user that the app is currently working on getting data, and there will be content when that data is available.
Let's look at an example of this.

=== "loading01.py"

    ```python title="loading01.py"
    --8<-- "docs/examples/guide/widgets/loading01.py"
    ```

    1. Shows the loading indicator in place of the data table.
    2. Insert a random sleep to simulate a network request.
    3. Show the new data.

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/loading01.py"}
    ```


In this example we have four [DataTable](../widgets/data_table.md) widgets, which we put into a loading state by setting the widget's `loading` property to `True`.
This will temporarily replace the widget with a loading indicator animation.
When the (simulated) data has been retrieved, we reset the `loading` property to show the new data.

!!! tip

    See the guide on [Workers](./workers.md) if you want to know more about the `@work` decorator.

## Line API

A downside of widgets that return Rich renderables is that Textual will redraw the entire widget when its state is updated or it changes size.
If a widget is large enough to require scrolling, or updates frequently, then this redrawing can make your app feel less responsive.
Textual offers an alternative API which reduces the amount of work required to refresh a widget, and makes it possible to update portions of a widget (as small as a single character) without a full redraw. This is known as the *line API*.

!!! note

    The Line API requires a little more work that typical Rich renderables, but can produce powerful widgets such as the builtin [DataTable](./../widgets/data_table.md) which can handle thousands or even millions of rows.

### Render Line method

To build a widget with the line API, implement a `render_line` method rather than a `render` method. The `render_line` method takes a single integer argument `y` which is an offset from the top of the widget, and should return a [Strip][textual.strip.Strip] object containing that line's content.
Textual will call this method as required to get content for every row of characters in the widget.

<div class="excalidraw">
--8<-- "docs/images/render_line.excalidraw.svg"
</div>

Let's look at an example before we go into the details. The following Textual app implements a widget with the line API that renders a checkerboard pattern. This might form the basis of a chess / checkers game. Here's the code:

=== "checker01.py"

    ```python title="checker01.py" hl_lines="12-31"
    --8<-- "docs/examples/guide/widgets/checker01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker01.py"}
    ```


The `render_line` method above calculates a `Strip` for every row of characters in the widget. Each strip contains alternating black and white space characters which form the squares in the checkerboard.

You may have noticed that the checkerboard widget makes use of some objects we haven't covered before. Let's explore those.

#### Segment and Style

A [Segment](https://rich.readthedocs.io/en/latest/protocol.html#low-level-render) is a class borrowed from the [Rich](https://github.com/Textualize/rich) project. It is small object (actually a named tuple) which bundles a string to be displayed and a [Style](https://rich.readthedocs.io/en/latest/style.html) which tells Textual how the text should look (color, bold, italic etc).

Let's look at a simple segment which would produce the text "Hello, World!" in bold.

```python
greeting = Segment("Hello, World!", Style(bold=True))
```

This would create the following object:

<div class="excalidraw">
--8<-- "docs/images/segment.excalidraw.svg"
</div>

Both Rich and Textual work with segments to generate content. A Textual app is the result of combining hundreds, or perhaps thousands, of segments,

#### Strips

A [Strip][textual.strip.Strip] is a container for a number of segments covering a single *line* (or row) in the Widget. A Strip will contain at least one segment, but often many more.

A `Strip` is constructed from a list of `Segment` objects. Here's now you might construct a strip that displays the text "Hello, World!", but with the second word in bold:

```python
segments = [
    Segment("Hello, "),
    Segment("World", Style(bold=True)),
    Segment("!")
]
strip = Strip(segments)
```

The first and third `Segment` omit a style, which results in the widget's default style being used. The second segment has a style object which applies bold to the text "World". If this were part of a widget it would produce the text: <code>Hello, **World**!</code>

The `Strip` constructor has an optional second parameter, which should be the *cell length* of the strip. The strip above has a length of 13, so we could have constructed it like this:

```python
strip = Strip(segments, 13)
```

Note that the cell length parameter is _not_ the total number of characters in the string. It is the number of terminal "cells". Some characters (such as Asian language characters and certain emoji) take up the space of two Western alphabet characters. If you don't know in advance the number of cells your segments will occupy, it is best to omit the length parameter so that Textual calculates it automatically.

### Component classes

When applying styles to widgets we can use CSS to select the child widgets. Widgets rendered with the line API don't have children per-se, but we can still use CSS to apply styles to parts of our widget by defining *component classes*. Component classes are associated with a widget by defining a `COMPONENT_CLASSES` class variable which should be a `set` of strings containing CSS class names.

In the checkerboard example above we hard-coded the color of the squares to "white" and "black". But what if we want to create a checkerboard with different colors? We can do this by defining two component classes, one for the "white" squares and one for the "dark" squares. This will allow us to change the colors with CSS.

The following example replaces our hard-coded colors with component classes.

=== "checker02.py"

    ```python title="checker02.py" hl_lines="11-13 16-23 35-36"
    --8<-- "docs/examples/guide/widgets/checker02.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker02.py"}
    ```

The `COMPONENT_CLASSES` class variable above adds two class names: `checkerboard--white-square` and `checkerboard--black-square`. These are set in the `DEFAULT_CSS` but can modified in the app's `CSS` class variable or external CSS.

!!! tip

    Component classes typically begin with the name of the widget followed by *two* hyphens. This is a convention to avoid potential name clashes.

The `render_line` method calls [get_component_rich_style][textual.widget.Widget.get_component_rich_style] to get `Style` objects from the CSS, which we apply to the segments to create a more colorful looking checkerboard.

### Scrolling

A Line API widget can be made to scroll by extending the [ScrollView][textual.scroll_view.ScrollView] class (rather than `Widget`).
The `ScrollView` class will do most of the work, but we will need to manage the following details:

1. The `ScrollView` class requires a *virtual size*, which is the size of the scrollable content and should be set via the `virtual_size` property. If this is larger than the widget then Textual will add scrollbars.
2. We need to update the `render_line` method to generate strips for the visible area of the widget, taking into account the current position of the scrollbars.

Let's add scrolling to our checkerboard example. A standard 8 x 8 board isn't sufficient to demonstrate scrolling so we will make the size of the board configurable and set it to 100 x 100, for a total of 10,000 squares.

=== "checker03.py"

    ```python title="checker03.py" hl_lines="4 26-30 35-36 52-53"
    --8<-- "docs/examples/guide/widgets/checker03.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker03.py"}
    ```

The virtual size is set in the constructor to match the total size of the board, which will enable scrollbars (unless you have your terminal zoomed out very far). You can update the `virtual_size` attribute dynamically as required, but our checkerboard isn't going to change size so we only need to set it once.

The `render_line` method gets the *scroll offset* which is an [Offset][textual.geometry.Offset] containing the current position of the scrollbars. We add `scroll_offset.y` to the `y` argument because `y` is relative to the top of the widget, and we need a Y coordinate relative to the scrollable content.

We also need to compensate for the position of the horizontal scrollbar. This is done in the call to `strip.crop` which *crops* the strip to the visible area between `scroll_x` and `scroll_x + self.size.width`.

!!! tip

    [Strip][textual.strip.Strip] objects are immutable, so methods will return a new Strip rather than modifying the original.

<div class="excalidraw">
--8<-- "docs/images/scroll_view.excalidraw.svg"
</div>

### Region updates

The Line API makes it possible to refresh parts of a widget, as small as a single character.
Refreshing smaller regions makes updates more efficient, and keeps your widget feeling responsive.

To demonstrate this we will update the checkerboard to highlight the square under the mouse pointer.
Here's the code:

=== "checker04.py"

    ```python title="checker04.py" hl_lines="18 28-30 33 41-44 46-63 74 81-92"
    --8<-- "docs/examples/guide/widgets/checker04.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/widgets/checker04.py"}
    ```

We've added a style to the checkerboard which is the color of the highlighted square, with a default of "darkred".
We will need this when we come to render the highlighted square.

We've also added a [reactive variable](./reactivity.md) called `cursor_square` which will hold the coordinate of the square underneath the mouse. Note that we have used [var][textual.reactive.var] which gives us reactive superpowers but won't automatically refresh the whole widget, because we want to update only the squares under the cursor.

The `on_mouse_move` handler takes the mouse coordinates from the [MouseMove][textual.events.MouseMove] object and calculates the coordinate of the square underneath the mouse. There's a little math here, so let's break it down.

- The event contains the coordinates of the mouse relative to the top left of the widget, but we need the coordinate relative to the top left of board which depends on the position of the scrollbars.
We can perform this conversion by adding `self.scroll_offset` to `event.offset`.
- Once we have the board coordinate underneath the mouse we divide the x coordinate by 8 and divide the y coordinate by 4 to give us the coordinate of a square.

If the cursor square coordinate calculated in `on_mouse_move` changes, Textual will call `watch_cursor_square` with the previous coordinate and new coordinate of the square. This method works out the regions of the widget to update and essentially does the reverse of the steps we took to go from mouse coordinates to square coordinates.
The `get_square_region` function calculates a [Region][textual.geometry.Region] object for each square and uses them as a positional argument in a call to [refresh][textual.widget.Widget.refresh]. Passing Region objects to `refresh` tells Textual to update only the cells underneath those regions, and not the entire widget.

!!! note

    Textual is smart about performing updates. If you refresh multiple regions, Textual will combine them into as few non-overlapping regions as possible.

The final step is to update the `render_line` method to use the cursor style when rendering the square underneath the mouse.

You should find that if you move the mouse over the widget now, it will highlight the square underneath the mouse pointer in red.

### Line API examples

The following builtin widgets use the Line API. If you are building advanced widgets, it may be worth looking through the code for inspiration!

- [DataTable](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_data_table.py)
- [RichLog](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_rich_log.py)
- [Tree](https://github.com/Textualize/textual/blob/main/src/textual/widgets/_tree.py)

## Compound widgets

Widgets may be combined to create new widgets with additional features.
Such widgets are known as *compound widgets*.
The stopwatch in the [tutorial](./../tutorial.md) is an example of a compound widget.

A compound widget can be used like any other widget.
The only thing that differs is that when you build a compound widget, you write a `compose()` method which yields *child* widgets, rather than implement a `render` or `render_line` method.

The following is an example of a compound widget.

=== "compound01.py"

    ```python title="compound01.py" hl_lines="28-30 44-47"
    --8<-- "docs/examples/guide/compound/compound01.py"
    ```

    1. The `compose` method makes this widget a *compound* widget.

=== "Output"

    ```{.textual path="docs/examples/guide/compound/compound01.py"}
    ```

The `InputWithLabel` class bundles an [Input](../widgets/input.md) with a [Label](../widgets/label.md) to create a new widget that displays a right-aligned label next to an input control. You can re-use this `InputWithLabel` class anywhere in a Textual app, including in other widgets.

## Coordinating widgets

Widgets rarely exist in isolation, and often need to communicate or exchange data with other parts of your app.
This is not difficult to do, but there is a risk that widgets can become dependant on each other, making it impossible to reuse a widget without copying a lot of dependant code.

In this section we will show how to design and build a fully-working app, while keeping widgets reusable.

### Designing the app

We are going to build a *byte editor* which allows you to enter a number in both decimal and binary. You could use this as a teaching aid for binary numbers.

Here's a sketch of what the app should ultimately look like:

!!! tip

    There are plenty of resources on the web, such as this [excellent video from Khan Academy](https://www.khanacademy.org/math/algebra-home/alg-intro-to-algebra/algebra-alternate-number-bases/v/number-systems-introduction) if you want to brush up on binary numbers.


<div class="excalidraw">
--8<-- "docs/images/byte01.excalidraw.svg"
</div>

There are three types of built-in widget in the sketch, namely ([Input](../widgets/input.md), [Label](../widgets/label.md), and [Switch](../widgets/switch.md)). Rather than manage these as a single collection of widgets, we can arrange them into logical groups with compound widgets. This will make our app easier to work with.

###  Identifying components

We will divide this UI into three compound widgets:

1. `BitSwitch` for a switch with a numeric label.
2. `ByteInput` which contains 8 `BitSwitch` widgets.
3. `ByteEditor` which contains a `ByteInput` and an [Input](../widgets/input.md) to show the decimal value.

This is not the only way we could implement our design with compound widgets.
So why these three widgets?
As a rule of thumb, a widget should handle one piece of data, which is why we have an independent widget for a bit, a byte, and the decimal value.

<div class="excalidraw">
--8<-- "docs/images/byte02.excalidraw.svg"
</div>

In the following code we will implement the three widgets. There will be no functionality yet, but it should look like our design.

=== "byte01.py"

    ```python title="byte01.py" hl_lines="28-30 48-50 67-71"
    --8<-- "docs/examples/guide/compound/byte01.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/compound/byte01.py" columns="90" line="30"}
    ```

Note the `compose()` methods of each of the widgets.

- The `BitSwitch` yields a [Label](../widgets/label.md) which displays the bit number, and a [Switch](../widgets/switch.md) control for that bit. The default CSS for `BitSwitch` aligns its children vertically, and sets the label's [text-align](../styles/text_align.md) to center.

- The `ByteInput` yields 8 `BitSwitch` widgets and arranges them horizontally. It also adds a `focus-within` style in its CSS to draw an accent border when any of the switches are focused.

- The `ByteEditor` yields a `ByteInput` and an `Input` control. The default CSS stacks the two controls on top of each other to divide the screen into two parts.

With these three widgets, the [DOM](CSS.md#the-dom) for our app will look like this:

<div class="excalidraw">
--8<-- "docs/images/byte_input_dom.excalidraw.svg"
</div>

Now that we have the design in place, we can implement the behavior.


### Data flow

We want to ensure that our widgets are re-usable, which we can do by following the guideline of "attributes down, messages up". This means that a widget can update a child by setting its attributes or calling its methods, but widgets should only ever send [messages](./events.md) to their *parent* (or other ancestors).

!!! info

    This pattern of only setting attributes in one direction and using messages for the opposite direction is known as *uni-directional data flow*.

In practice, this means that to update a child widget you get a reference to it and use it like any other Python object. Here's an example of an [action](actions.md) that updates a child widget:

```python
def action_set_true(self):
    self.query_one(Switch).value = 1
```

If a child needs to update a parent, it should send a message with [post_message][textual.message_pump.MessagePump.post_message].

Here's an example of posting message:

```python
def on_click(self):
    self.post_message(MyWidget.Change(active=True))
```

Note that *attributes down and messages up* means that you can't modify widgets on the same level directly. If you want to modify a *sibling*, you will need to send a message to the parent, and the parent would make the changes.

The following diagram illustrates this concept:


<div class="excalidraw">
--8<-- "docs/images/attributes_messages.excalidraw.svg"
</div>

### Messages up

Let's extend the `ByteEditor` so that clicking any of the 8 `BitSwitch` widgets updates the decimal value. To do this we will add a custom message to `BitSwitch` that we catch in the `ByteEditor`.

=== "byte02.py"

    ```python title="byte02.py" hl_lines="5-6 26-32 34 44-48 91-96"
    --8<-- "docs/examples/guide/compound/byte02.py"
    ```

    1. This will store the value of the "bit".
    2. This is sent by the builtin `Switch` widgets, when it changes state.
    3. Stop the event, because we don't want it to go to the parent.
    4. Store the new value of the "bit".

=== "Output"

    ```{.textual path="docs/examples/guide/compound/byte02.py" columns="90" line="30", press="tab,tab,tab,enter"}
    ```

- The `BitSwitch` widget now has an `on_switch_changed` method which will handle a [`Switch.Changed`][textual.widgets.Switch.Changed] message, sent when the user clicks a switch. We use this to store the new value of the bit, and sent a new custom message, `BitSwitch.BitChanged`.
- The `ByteEditor` widget handles the `BitSwitch.Changed` message by calculating the decimal value and setting it on the input.

The following is a (simplified) DOM diagram to show how the new message is processed:

<div class="excalidraw">
--8<-- "docs/images/bit_switch_message.excalidraw.svg"
</div>


### Attributes down

We also want the switches to update if the user edits the decimal value.

Since the switches are children of `ByteEditor` we can update them by setting their attributes directly.
This is an example of "attributes down".

=== "byte03.py"

    ```python title="byte03.py" hl_lines="5 45-47 90 92-94 109-114 116-120"
    --8<-- "docs/examples/guide/compound/byte03.py"
    ```

    1. When the `BitSwitch`'s value changed, we want to update the builtin `Switch` to match.
    2. Ensure the value is in a the range of a byte.
    3. Handle the `Input.Changed` event when the user modified the value in the input.
    4. When the `ByteEditor` value changes, update all the switches to match.
    5. Prevent the `BitChanged` message from being sent.
    6. Because `switch` is a child, we can set its attributes directly.


=== "Output"

    ```{.textual path="docs/examples/guide/compound/byte03.py" columns="90" line="30", press="1,0,0"}
    ```

- When the user edits the input, the [Input](../widgets/input.md) widget sends a `Changed` event, which we handle with `on_input_changed` by setting `self.value`, which is a reactive value we added to `ByteEditor`.
- If the value has changed, Textual will call `watch_value` which sets the value of each of the eight switches. Because we are working with children of the `ByteEditor`, we can set attributes directly without going via a message.
````

## File: docs/guide/workers.md
````markdown
# Workers

In this chapter we will explore the topic of *concurrency* and how to use Textual's Worker API to make it easier.

!!! tip "The Worker API was added in version 0.18.0"

## Concurrency

There are many interesting uses for Textual which require reading data from an internet service.
When an app requests data from the network it is important that it doesn't prevent the user interface from updating.
In other words, the requests should be concurrent (happen at the same time) as the UI updates.

This is also true for anything that could take a significant time (more than a few milliseconds) to complete.
For instance, reading from a [subprocess](https://docs.python.org/3/library/asyncio-subprocess.html#asyncio-subprocess) or doing compute heavy work.

Managing this concurrency is a tricky topic, in any language or framework.
Even for experienced developers, there are gotchas which could make your app lock up or behave oddly.
Textual's Worker API makes concurrency far less error prone and easier to reason about.

## Workers

Before we go into detail, let's see an example that demonstrates a common pitfall for apps that make network requests.

The following app uses [httpx](https://www.python-httpx.org/) to get the current weather for any given city, by making a request to [wttr.in](https://wttr.in/).

=== "weather01.py"

    ```python title="weather01.py"
    --8<-- "docs/examples/guide/workers/weather01.py"
    ```

=== "weather.tcss"

    ```css title="weather.tcss"
    --8<-- "docs/examples/guide/workers/weather.tcss"
    ```

=== "Output"

    ```{.textual path="docs/examples/guide/workers/weather01.py"}
    ```

If you were to run this app, you should see weather information update as you type.
But you may find that the input is not as responsive as usual, with a noticeable delay between pressing a key and seeing it echoed in screen.
This is because we are making a request to the weather API within a message handler, and the app will not be able to process other messages until the request has completed (which may be anything from a few hundred milliseconds to several seconds later).

To resolve this we can use the [run_worker][textual.dom.DOMNode.run_worker] method which runs the `update_weather` coroutine (`async def` function) in the background. Here's the code:

```python title="weather02.py" hl_lines="21"
--8<-- "docs/examples/guide/workers/weather02.py"
```

This one line change will make typing as responsive as you would expect from any app.

The `run_worker` method schedules a new *worker* to run `update_weather`, and returns a [Worker][textual.worker.Worker] object. This happens almost immediately, so it won't prevent other messages from being processed. The `update_weather` function is now running concurrently, and will finish a second or two later.

!!! tip

    The [Worker][textual.worker.Worker] object has a few useful methods on it, but you can often ignore it as we did in `weather02.py`.

The call to `run_worker` also sets `exclusive=True` which solves an additional problem with concurrent network requests: when pulling data from the network, there is no guarantee that you will receive the responses in the same order as the requests.
For instance, if you start typing "Paris", you may get the response for "Pari" *after* the response for "Paris", which could show the wrong weather information.
The `exclusive` flag tells Textual to cancel all previous workers before starting the new one.

### Work decorator

An alternative to calling `run_worker` manually is the [work][textual.work] decorator, which automatically generates a worker from the decorated method.

Let's use this decorator in our weather app:

```python title="weather03.py" hl_lines="4 22 24"
--8<-- "docs/examples/guide/workers/weather03.py"
```

The addition of `@work(exclusive=True)` converts the `update_weather` coroutine into a regular function which when called will create and start a worker.
Note that even though `update_weather` is an `async def` function, the decorator means that we don't need to use the `await` keyword when calling it.

!!! tip

    The decorator takes the same arguments as `run_worker`.

### Worker return values

When you run a worker, the return value of the function won't be available until the work has completed.
You can check the return value of a worker with the `worker.result` attribute which will initially be `None`, but will be replaced with the return value of the function when it completes.

If you need the return value you can call [worker.wait][textual.worker.Worker.wait] which is a coroutine that will wait for the work to complete.
But note that if you do this in a message handler it will also prevent the widget from updating until the worker returns.
Often a better approach is to handle [worker events](#worker-events) which will notify your app when a worker completes, and the return value is available without waiting.

### Cancelling workers

You can cancel a worker at any time before it is finished by calling [Worker.cancel][textual.worker.Worker.cancel].
This will raise a [CancelledError][asyncio.CancelledError] within the coroutine, and should cause it to exit prematurely.

### Worker errors

The default behavior when a worker encounters an exception is to exit the app and display the traceback in the terminal.
You can also create workers which will *not* immediately exit on exception, by setting `exit_on_error=False` on the call to `run_worker` or the `@work` decorator.

### Worker lifetime

Workers are managed by a single [WorkerManager][textual.worker_manager.WorkerManager] instance, which you can access via `app.workers`.
This is a container-like object which you iterate over to see your active workers.

Workers are tied to the DOM node (widget, screen, or app) where they are created.
This means that if you remove the widget or pop the screen where they are created, then the tasks will be cleaned up automatically.
Similarly if you exit the app, any running tasks will be cancelled.

Worker objects have a `state` attribute which will contain a [WorkerState][textual.worker.WorkerState] enumeration that indicates what the worker is doing at any given time.
The `state` attribute will contain one of the following values:


| Value     | Description                                                                         |
| --------- | ----------------------------------------------------------------------------------- |
| PENDING   | The worker was created, but not yet started.                                        |
| RUNNING   | The worker is currently running.                                                    |
| CANCELLED | The worker was cancelled and is no longer running.                                  |
| ERROR     | The worker raised an exception, and `worker.error` will contain the exception.      |
| SUCCESS   | The worker completed successful, and `worker.result` will contain the return value. |

Workers start with a `PENDING` state, then go to `RUNNING`. From there, they will go to `CANCELLED`, `ERROR` or `SUCCESS`.

<div class="excalidraw">
--8<-- "docs/images/workers/lifetime.excalidraw.svg"
</div>

### Worker events

When a worker changes state, it sends a [Worker.StateChanged][textual.worker.Worker.StateChanged] event to the widget where the worker was created.
You can handle this message by defining an `on_worker_state_changed` event handler.
For instance, here is how we might log the state of the worker that updates the weather:

```python title="weather04.py" hl_lines="4 40-42"
--8<-- "docs/examples/guide/workers/weather04.py"
```

If you run the above code with `textual` you should see the worker lifetime events logged in the Textual [console](./devtools.md#console).

```
textual run weather04.py --dev
```

### Thread workers

In previous examples we used `run_worker` or the `work` decorator in conjunction with coroutines.
This works well if you are using an async API like `httpx`, but if your API doesn't support async you may need to use *threads*.

!!! info "What are threads?"

    Threads are a form of concurrency supplied by your Operating System. Threads allow your code to run more than a single function simultaneously.

You can create threads by setting `thread=True` on the `run_worker` method or the `work` decorator.
The API for thread workers is identical to async workers, but there are a few differences you need to be aware of when writing code for thread workers.

The first difference is that you should avoid calling methods on your UI directly, or setting reactive variables.
You can work around this with the [App.call_from_thread][textual.app.App.call_from_thread] method which schedules a call in the main thread.

The second difference is that you can't cancel threads in the same way as coroutines, but you *can* manually check if the worker was cancelled.

Let's demonstrate thread workers by replacing `httpx` with `urllib.request` (in the standard library).
The `urllib` module is not async aware, so we will need to use threads:

```python title="weather05.py" hl_lines="1-2 27-44"
--8<-- "docs/examples/guide/workers/weather05.py"
```

In this example, the `update_weather` is not asynchronous (i.e. a regular function).
The `@work` decorator has `thread=True` which makes it a thread worker.
Note the use of [get_current_worker][textual.worker.get_current_worker] which the function uses to check if it has been cancelled or not.

!!! important

    Textual will raise an exception if you add the `work` decorator to a regular function without `thread=True`.


#### Posting messages

Most Textual functions are not thread-safe which means you will need to use [call_from_thread][textual.app.App.call_from_thread] to run them from a thread worker.
An exception would be [post_message][textual.widget.Widget.post_message] which *is* thread-safe.
If your worker needs to make multiple updates to the UI, it is a good idea to send [custom messages](./events.md) and let the message handler update the state of the UI.
````

## File: docs/how-to/center-things.md
````markdown
# Center things

If you have ever needed to center something in a web page, you will be glad to know it is **much** easier in Textual.

This article discusses a few different ways in which things can be centered, and the differences between them.

## Aligning widgets

The [align](../styles/align.md) rule will center a widget relative to one or both edges.
This rule is applied to a *container*, and will impact how the container's children are arranged.
Let's see this in practice with a trivial app containing a [Static](../widgets/static.md) widget:

```python
--8<-- "docs/examples/how-to/center01.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/center01.py"}
```

The container of the widget is the screen, which has the `align: center middle;` rule applied. The
`center` part tells Textual to align in the horizontal direction, and `middle` tells Textual to align in the vertical direction.

The output *may* surprise you.
The text appears to be aligned in the middle (i.e. vertical edge), but *left* aligned on the horizontal.
This isn't a bug &mdash; I promise.
Let's make a small change to reveal what is happening here.
In the next example, we will add a background and a border to our text:

!!! tip

    Adding a border is a very good way of visualizing layout issues, if something isn't behaving as you would expect.

```python hl_lines="13-16 20"
--8<-- "docs/examples/how-to/center02.py"
```

The static widget will now have a blue background and white border:

```{.textual path="docs/examples/how-to/center02.py"}
```

Note the static widget is as wide as the screen.
Since the widget is as wide as its container, there is no room for it to move in the horizontal direction.

!!! info

    The `align` rule applies to *widgets*, not the text.

In order to see the `center` alignment, we will have to make the widget smaller than the width of the screen.
Let's set the width of the Static widget to `auto`, which will make the widget just wide enough to fit the content:

```python hl_lines="16"
--8<-- "docs/examples/how-to/center03.py"
```

If you run this now, you should see the widget is aligned on both axis:

```{.textual path="docs/examples/how-to/center03.py"}
```

## Aligning text

In addition to aligning widgets, you may also want to align *text*.
In order to demonstrate the difference, lets update the example with some longer text.
We will also set the width of the widget to something smaller, to force the text to wrap.

```python hl_lines="4 18 23"
--8<-- "docs/examples/how-to/center04.py"
```

Here's what it looks like with longer text:

```{.textual path="docs/examples/how-to/center04.py"}
```

Note how the widget is centered, but the text within it is flushed to the left edge.
Left aligned text is the default, but you can also center the text with the [text-align](../styles/text_align.md) rule.
Let's center align the longer text by setting this rule:

```python hl_lines="19"
--8<-- "docs/examples/how-to/center05.py"
```

If you run this, you will see that each line of text is individually centered:

```{.textual path="docs/examples/how-to/center05.py"}
```

You can also use `text-align` to right align text or justify the text (align to both edges).

## Aligning content

There is one last rule that can help us center things.
The [content-align](../styles/content_align.md) rule aligns content *within* a widget.
It treats the text as a rectangular region and positions it relative to the space inside a widget's border.

In order to see why we might need this rule, we need to make the Static widget larger than required to fit the text.
Let's set the height of the Static widget to 9 to give the content room to move:

```python hl_lines="19"
--8<-- "docs/examples/how-to/center06.py"
```

Here's what it looks like with the larger widget:

```{.textual path="docs/examples/how-to/center06.py"}
```

Textual aligns a widget's content to the top border by default, which is why the space is below the text.
We can tell Textual to align the content to the center by setting `content-align: center middle`;

!!! note

    Strictly speaking, we only need to align the content vertically here (there is no room to move the content left or right)
    So we could have done `content-align-vertical: middle;`

```python hl_lines="21"
--8<-- "docs/examples/how-to/center07.py"
```

If you run this now, the content will be centered within the widget:

```{.textual path="docs/examples/how-to/center07.py"}
```

## Aligning multiple widgets

It's just as easy to align multiple widgets as it is a single widget.
Applying `align: center middle;` to the parent widget (screen or other container) will align all its children.

Let's create an example with two widgets.
The following code adds two widgets with auto dimensions:

```python
--8<-- "docs/examples/how-to/center08.py"
```

This produces the following output:

```{.textual path="docs/examples/how-to/center08.py"}
```

We can center both those widgets by applying the `align` rule as before:

```python hl_lines="9-11"
--8<-- "docs/examples/how-to/center09.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/center09.py"}
```

Note how the widgets are aligned as if they are a single group.
In other words, their position relative to each other didn't change, just their position relative to the screen.

If you do want to center each widget independently, you can place each widget inside its own container, and set `align` for those containers.
Textual has a builtin [`Center`][textual.containers.Center] container for just this purpose.

Let's wrap our two widgets in a `Center` container:

```python hl_lines="2 22 24"
--8<-- "docs/examples/how-to/center10.py"
```

If you run this, you will see that the widgets are centered relative to each other, not just the screen:

```{.textual path="docs/examples/how-to/center10.py"}
```

## Summary

Keep the following in mind when you want to center content in Textual:

- In order to center a widget, it needs to be smaller than its container.
- The `align` rule is applied to the *parent* of the widget you want to center (i.e. the widget's container).
- The `text-align` rule aligns text on a line by line basis.
- The `content-align` rule aligns content *within* a widget.
- Use the [`Center`][textual.containers.Center] container if you want to align multiple widgets relative to each other.
- Add a border if the alignment isn't working as you would expect.

---

If you need further help, we are here to [help](../help.md).
````

## File: docs/how-to/design-a-layout.md
````markdown
# Design a Layout

This article discusses an approach you can take when designing the layout for your applications.

Textual's layout system is flexible enough to accommodate just about any application design you could conceive of, but it may be hard to know where to start. We will go through a few tips which will help you get over the initial hurdle of designing an application layout.


## Tip 1. Make a sketch

The initial design of your application is best done with a sketch.
You could use a drawing package such as [Excalidraw](https://excalidraw.com/) for your sketch, but pen and paper is equally as good.

Start by drawing a rectangle to represent a blank terminal, then draw a rectangle for each element in your application. Annotate each of the rectangles with the content they will contain, and note wether they will scroll (and in what direction).

For the purposes of this article we are going to design a layout for a Twitter or Mastodon client, which will have a header / footer and a number of columns.

!!! note

    The approach we are discussing here is applicable even if the app you want to build looks nothing like our sketch!

Here's our sketch:

<div class="excalidraw">
--8<-- "docs/images/how-to/layout.excalidraw.svg"
</div>

It's rough, but it's all we need.

## Tip 2. Work outside in

Like a sculpture with a block of marble, it is best to work from the outside towards the center.
If your design has fixed elements (like a header, footer, or sidebar), start with those first.

In our sketch we have a header and footer.
Since these are the outermost widgets, we will begin by adding them.

!!! tip

    Textual has builtin [Header](../widgets/header.md) and [Footer](../widgets/footer.md) widgets which you could use in a real application.

The following example defines an [app](../guide/app.md), a [screen](../guide/screens.md), and our header and footer widgets.
Since we're starting from scratch and don't have any functionality for our widgets, we are going to use the [Placeholder][textual.widgets.Placeholder] widget to help us visualize our design.

In a real app, we would replace these placeholders with more useful content.

=== "layout01.py"

    ```python
    --8<-- "docs/examples/how-to/layout01.py"
    ```

    1. The Header widget extends Placeholder.
    2. The footer widget extends Placeholder.
    3. Creates the header widget (the id will be displayed within the placeholder widget).
    4. Creates the footer widget.

=== "Output"

    ```{.textual path="docs/examples/how-to/layout01.py"}
    ```

## Tip 3. Apply docks

This app works, but the header and footer don't behave as expected.
We want both of these widgets to be fixed to an edge of the screen and limited in height.
In Textual this is known as *docking* which you can apply with the [dock](../styles/dock.md) rule.

We will dock the header and footer to the top and bottom edges of the screen respectively, by adding a little [CSS](../guide/CSS.md) to the widget classes:

=== "layout02.py"

    ```python hl_lines="7-12 16-21"
    --8<-- "docs/examples/how-to/layout02.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/how-to/layout02.py"}
    ```

The `DEFAULT_CSS` class variable is used to set CSS directly in Python code.
We could define these in an external CSS file, but writing the CSS inline like this can be convenient if it isn't too complex.

When you dock a widget, it reduces the available area for other widgets.
This means that Textual will automatically compensate for the 6 additional lines reserved for the header and footer.

## Tip 4. Use FR Units for flexible things

After we've added the header and footer, we want the remaining space to be used for the main interface, which will contain the columns in the sketch.
This area is flexible (will change according to the size of the terminal), so how do we ensure that it takes up precisely the space needed?

The simplest way is to use [fr](../css_types/scalar.md#fraction) units.
By setting both the width and height to `1fr`, we are telling Textual to divide the space equally amongst the remaining widgets.
There is only a single widget, so that widget will fill all of the remaining space.

Let's make that change.

=== "layout03.py"

    ```python hl_lines="24-31 38"
    --8<-- "docs/examples/how-to/layout03.py"
    ```

    1. Here's where we set the width and height to `1fr`. We also add a border just to illustrate the dimensions better.

=== "Output"

    ```{.textual path="docs/examples/how-to/layout03.py"}
    ```

As you can see, the central Columns area will resize with the terminal window.

## Tip 5. Use containers

Before we add content to the Columns area, we have an opportunity to simplify.
Rather than extend `Placeholder` for our `ColumnsContainer` widget, we can use one of the builtin *containers*.
A container is simply a widget designed to *contain* other widgets.
Containers are styled with `fr` units to fill the remaining space so we won't need to add any more CSS.

Let's replace the `ColumnsContainer` class in the previous example with a `HorizontalScroll` container, which also adds an automatic horizontal scrollbar.

=== "layout04.py"

    ```python hl_lines="2 29"
    --8<-- "docs/examples/how-to/layout04.py"
    ```

    1. The builtin container widget.


=== "Output"

    ```{.textual path="docs/examples/how-to/layout04.py"}
    ```

The container will appear as blank space until we add some widgets to it.

Let's add the columns to the `HorizontalScroll`.
A column is itself a container which will have a vertical scrollbar, so we will define our `Column` by subclassing `VerticalScroll`.
In a real app, these columns will likely be added dynamically from some kind of configuration, but let's add 4 to visualize the layout.

We will also define a `Tweet` placeholder and add a few to each column.

=== "layout05.py"

    ```python hl_lines="2 25-26 29-32 39-43"
    --8<-- "docs/examples/how-to/layout05.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/how-to/layout05.py"}
    ```

Note from the output that each `Column` takes a quarter of the screen width.
This happens because `Column` extends a container which has a width of `1fr`.

It makes more sense for a column in a Twitter / Mastodon client to use a fixed width.
Let's set the width of the columns to 32.

We also want to reduce the height of each "tweet".
In the real app, you might set the height to "auto" so it fits the content, but lets set it to 5 lines for now.

Here's the final example and a reminder of the sketch.

=== "layout06.py"

    ```python hl_lines="25-32 36-46"
    --8<-- "docs/examples/how-to/layout06.py"
    ```

=== "Output"

    ```{.textual path="docs/examples/how-to/layout06.py" columns="100" lines="32"}
    ```

=== "Sketch"

    <div class="excalidraw">
    --8<-- "docs/images/how-to/layout.excalidraw.svg"
    </div>


A layout like this is a great starting point.
In a real app, you would start replacing each of the placeholders with [builtin](../widget_gallery.md) or [custom](../guide/widgets.md) widgets.


## Summary

Layout is the first thing you will tackle when building a Textual app.
The following tips will help you get started.

1. Make a sketch (pen and paper is fine).
2. Work outside in. Start with the entire space of the terminal, add the outermost content first.
3. Dock fixed widgets. If the content doesn't move or scroll, you probably want to *dock* it.
4. Make use of `fr` for flexible space within layouts.
5. Use containers to contain other widgets, particularly if they scroll!

---

If you need further help, we are here to [help](../help.md).
````

## File: docs/how-to/index.md
````markdown
# How To

Welcome to the How To section.

Here you will find How To articles which cover various topics at a higher level than the Guide or Reference.
We will be adding more articles in the future.
If there is anything you would like to see covered, [open an issue](https://github.com/Textualize/textual/issues) in the Textual repository!
````

## File: docs/how-to/package-with-hatch.md
````markdown
# Package a Textual app with Hatch

Python apps may be distributed via [PyPI](https://pypi.org/) so they can be installed via `pip`.
This is known as *packaging*.
The packaging process for Textual apps is much the same as any Python library, with the additional requirement that we can launch our app from the command line.

!!! tip

    An alternative to packaging your app is to turn it into a web application with [textual-serve](https://github.com/Textualize/textual-serve).

In this How To we will cover how to use [Hatch](https://github.com/pypa/hatch) to package an example application.

Hatch is a *build tool* (a command line app to assist with packaging).
You could use any build tool to package a Textual app (such as [Poetry](https://python-poetry.org/) for example), but Hatch is a good choice given its large feature set and ease of use.


!!! info inline end "Calculator example"

    ```{.textual path="examples/calculator.py" columns=100 lines=41 press="3,.,1,4,5,9,2,wait:400"}
    ```

    This example is [`calculator.py`](https://github.com/Textualize/textual/blob/main/examples/calculator.py) taken from the examples directory in the Textual repository.


## Foreword

Packaging with Python can be a little intimidating if you haven't tackled it before.
But it's not all that complicated. 
When you have been through it once or twice, you should find it fairly straightforward.

## Example repository

See the [textual-calculator-hatch](https://github.com/Textualize/textual-calculator-hatch) repository for the project created in this How To.

## The example app

To demonstrate packaging we are going to take the calculator example from the examples directory, and publish it to PyPI.
The end goal is to allow a user to install it with pip:


```bash
pip install textual-calculator
```

Then launch the app from the command line:

```bash
calculator
```

## Installing Hatch

There are a few ways to install Hatch.
See the [official docs on installation](https://hatch.pypa.io/latest/install/) for the best method for your operating system.

Once installed, you should have the `hatch` command available on the command line.
Run the following to check Hatch was installed correctly:

```bash
hatch
```

## Hatch new

Hatch can create an initial directory structure and files with the `new` *subcommand*.
Enter `hatch new` followed by the name of your project.
For the calculator example, the name will be "textual calculator":

```batch
hatch new "textual calculator"
```

This will create the following directory structure:

```
textual-calculator
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   └── textual_calculator
│       ├── __about__.py
│       └── __init__.py
└── tests
    └── __init__.py
```

This follows a well established convention when packaging Python code, and will create the following files:

- `LICENSE.txt` contains the license you want to distribute your code under.
- `README.md` is a markdown file containing information about your project, which will be displayed in PyPI and Github (if you use it). You can edit this with information about your app and how to use it.
- `pyproject.toml` is a [TOML](https://en.wikipedia.org/wiki/TOML) file which contains *metadata* (additional information) about your project and how to package it. This is a Python standard. This file may be edited manually or by a build tool (such as Hatch).
- `src/textual_calculator/__about__.py` contains the version number of your app. You should update this when you release new versions.
- `src/textual_calculator/__init__.py`  and `tests/__init__py` indicate the directory they are within contains Python code (these files are often empty).
 
In the top level is a directory called `src`.
This should contain a directory named after your project, and will be the name your code can be imported from.
In our example, this directory is `textual_calculator` so we can do `import textual_calculator` in Python code.

Additionally, there is a `tests` directory where you can add any [test](../guide/testing.md) code.

### More on naming

Note how Hatch replaced the space in the project name with a hyphen (i.e. `textual-calculator`), but the directory in `src` with an underscore (i.e. `textual_calculator`). This is because the directory in `src` contains the Python module, and a hyphen is not legal in a Python import. The top-level directory doesn't have this restriction and uses a hyphen, which is more typical for a directory name.

Bear this in mind if your project name contains spaces.


### Got existing code?

The `hatch new` command assumes you are starting from scratch.
If you have existing code you would like to package, navigate to your directory and run the following command (replace `<YOUR ROJECT NAME>` with the name of your project):

```
hatch new --init <YOUR PROJECT NAME>
```

This will generate a `pyproject.toml` in the current directory.

!!! note
    
    It will simplify things if your code follows the directory structure convention above. This may require that you move your files -- you only need to do this once!

## Adding code

Your code should reside inside `src/<PROJECT NAME>`.
For the calculator example we will copy `calculator.py` and `calculator.tcss` into the `src/textual_calculator` directory, so our directory will look like the following:

```
textual-calculator
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   └── textual_calculator
│       ├── __about__.py
│       ├── __init__.py
│       ├── calculator.py
│       └── calculator.tcss
└── tests
    └── __init__.py
```

## Adding dependencies

Your Textual app will likely depend on other Python libraries (at the very least Textual itself).
We need to list these in `pyproject.toml` to ensure that these *dependencies* are installed alongside your app.

In `pyproject.toml` there should be a section beginning with `[project]`, which will look something like the following:

```toml
[project]
name = "textual-calculator"
dynamic = ["version"]
description = 'A example app'
readme = "README.md"
requires-python = ">=3.8"
license = "MIT"
keywords = []
authors = [
  { name = "Will McGugan", email = "redacted@textualize.io" },
]
classifiers = [
  "Development Status :: 4 - Beta",
  "Programming Language :: Python",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: Implementation :: CPython",
  "Programming Language :: Python :: Implementation :: PyPy",
]
dependencies = []
```

We are interested in the `dependencies` value, which should list the app's dependencies.
If you want a particular version of a project you can add `==` followed by the version.

For the calculator, the only dependency is Textual.
We can add Textual by modifying the following line:

```toml
dependencies = ["textual==0.47.1"]
```

At the time of writing, the latest Textual is `0.47.1`.
The entry in `dependencies` will ensure we get that particular version, even when newer versions are released.

See the Hatch docs for more information on specifying [dependencies](https://hatch.pypa.io/latest/config/dependency/).

## Environments

A common problem when working with Python code is managing multiple projects with different dependencies.
For instance, if we had another app that used version `0.40.0` of Textual, it *may* break if we installed version `0.47.1`.

The standard way of solving this is with *virtual environments* (or *venvs*), which allow each project to have its own set of dependencies.
Hatch can create virtual environments for us, and makes working with them very easy.

To create a new virtual environment, navigate to the directory with the `pyproject.toml` file and run the following command (this is only require once, as the virtual environment will persist):

```bash
hatch env create
```

Then run the following command to activate the virtual environment:

```bash
hatch shell
```

If you run `python` now, it will have our app and its dependencies available for import:

```
$ python
Python 3.11.1 (main, Jan  1 2023, 10:28:48) [Clang 14.0.0 (clang-1400.0.29.202)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from textual_calculator import calculator
```

### Running the app

You can launch the calculator from the command line with the following command:

```bash
python -m textual_calculator.calculator
```

The `-m` switch tells Python to import the module and run it.

Although you can run your app this way (and it is fine for development), it's not ideal for sharing.
It would be preferable to have a dedicated command to launch the app, so the user can easily run it from the command line.
To do that, we will need to add an *entry point* to pyproject.toml

## Entry points

An entry point is a function in your project that can be run from the command line.
For our calculator example, we first need to create a function that will run the app.
Add the following file to the `src/textual_calculator` folder, and name it `entry_points.py`:

```python
from textual_calculator.calculator import CalculatorApp


def calculator():
    app = CalculatorApp()
    app.run()
```

!!! tip

    If you already have a function that runs your app, you may not need an `entry_points.py` file.

Then edit `pyproject.toml` to add the following section:

```toml
[project.scripts]
calculator = "textual_calculator.entry_points:calculator"
```

Each entry in the `[project.scripts]` section (there can be more than one) maps a command on to an import and function name.
In the second line above, before the `=` character, `calculator` is the name of the command.
The string after the `=` character contains the name of the import (`textual_calculator.entry_points`), followed by a colon (`:`), and then the name of the function (also called `calculator`).

Specifying an entry point like this is equivalent to doing the following from the Python REPL:

```
>>> import textual_calculator.entry_points
>>> textual_calculator.entry_points.calculator()
```

To add the `calculator` command once you have edited `pyproject.toml`, run the following from the command line:

```bash
pip install -e .
```

!!! info

    You will have no doubt used `pip` before, but perhaps not with `-e .`.
    The addition of `-e` installs the project in *editable* mode which means pip won't copy the `.py` files code anywhere, the dot (`.`) indicates were installing the project in the current directory. 

Now you can launch the calculator from the command line as follows:

```bash
calculator
```

## Building 

Building produces archive files that contain your code.
When you install a package via pip or other tool, it will download one of these archives.

To build your project with Hatch, change to the directory containing your `pyproject.toml` and run the `hatch build` subcommand:

```
cd textual-calculator
hatch build
```

After a moment, you should find that Hatch has created a `dist` (distribution) folder, which contains the project archive files.
You don't typically need to use these files directly, but feel free to have a look at the directory contents.

!!! note "Packaging TCSS and other files"

    Hatch will typically include all the files needed by your project, i.e. the `.py` files.
    It will also include any Textual CSS (`.tcss`) files in the project directory.
    Not all build tools will include files other than `.py`; if you are using another build tool, you may have to consult the documentation for how to add the Textual CSS files.


## Publishing

After your project has been successfully built you are ready to publish it to PyPI.

If you don't have a PyPI account, you can [create one now](https://pypi.org/account/register/).
Be sure to follow the instructions to validate your email and set up 2FA (Two Factor Authentication).

Once you have an account, login to PyPI and go to the Account Settings tab.
Scroll down and click the "Add API token" button.
In the "Create API Token" form, create a token with name "Uploads" and select the "Entire project" scope, then click the "Create token" button.

Copy this API token (long string of random looking characters) somewhere safe.
This API token is how PyPI authenticates uploads are for your account, so you should never share your API token or upload it to the internet.

Run the following command (replacing `<YOUR API TOKEN>` with the text generated in the previous step):

```bash
hatch publish -u __token__ -a <YOUR API TOKEN>
```

Hatch will upload the distribution files, and you should see a PyPI URL in the terminal.

### Managing API Tokens

Creating an API token with the "all projects" permission is required for the first upload.
You may want to generate a new API token with permissions to upload a single project when you upload a new version of your app (and delete the old one).
This way if your token is leaked, it will only impact the one project.

### Publishing new versions

If you have made changes to your app, and you want to publish the updates, you will need to update the `version` value in the `__about__.py` file, then repeat the build and publish steps.

!!! tip "Managing version numbers"

    See [Semver](https://semver.org/) for a popular versioning system (used by Textual itself).

## Installing the calculator

From the user's point of view, they only need run the following command to install the calculator:

```bash
pip install textual_calculator
```

They will then be able to launch the calculator with the following command:

```bash
calculator
```

### Pipx

A downside of installing apps this way is that unless the user has created a [virtual environment](https://docs.python.org/3/library/venv.html), they may find it breaks other packages with conflicting dependencies.

A good solution to this issue is [pipx](https://github.com/pypa/pipx) which automatically creates virtual environments that won't conflict with any other Python commands.
Once PipX is installed, you can advise users to install your app with the following command:

```bash
pipx install textual_calculator
```

This will install the calculator and the `textual` dependency as before, but without the potential of dependency conflicts.

## Summary

1. Use a build system, such as [Hatch](https://hatch.pypa.io/latest/).
2. Initialize your project with `hatch new` (or equivalent).
3. Write a function to run your app, if there isn't one already.
4. Add your dependencies and entry points to `pyproject.toml`.
5. Build your app with `hatch build`.
6. Publish your app with `hatch publish`.

---

If you have any problems packaging Textual apps, we are here to [help](../help.md)!
````

## File: docs/how-to/render-and-compose.md
````markdown
# Render and compose

A common question that comes up on the [Textual Discord server](https://discord.gg/Enf6Z3qhVr) is what is the difference between [`render`][textual.widget.Widget.render] and [`compose`][textual.widget.Widget.compose] methods on a widget?
In this article we will clarify the differences, and use both these methods to build something fun.

<div class="video-wrapper">
<iframe width="1280" height="922" src="https://www.youtube.com/embed/dYU7jHyabX8" title="" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
</div>

## Which method to use?

Render and compose are easy to confuse because they both ultimately define what a widget will look like, but they have quite different uses. 

The `render` method on a widget returns a [Rich](https://rich.readthedocs.io/en/latest/) renderable, which is anything you could print with Rich.
The simplest renderable is just text; so `render()` methods often return a string, but could equally return a [`Text`](https://rich.readthedocs.io/en/latest/text.html) instance, a [`Table`](https://rich.readthedocs.io/en/latest/tables.html), or anything else from Rich (or third party library).
Whatever is returned from `render()` will be combined with any styles from CSS and displayed within the widget's borders.

The `compose` method is used to build [*compound* widgets](../guide/widgets.md#compound-widgets) (widgets composed of other widgets).

A general rule of thumb, is that if you implement a `compose` method, there is no need for a `render` method because it is the widgets yielded from `compose` which define how the custom widget will look.
However, you *can* mix these two methods.
If you implement both, the `render` method will set the custom widget's *background* and `compose` will add widgets on top of that background.

## Combining render and compose

Let's look at an example that combines both these methods.
We will create a custom widget with a [linear gradient][textual.renderables.gradient.LinearGradient] as a background.
The background will be animated (I did promise *fun*)!

=== "render_compose.py"

    ```python
    --8<-- "docs/examples/how-to/render_compose.py"
    ```

    1. Refresh the widget 30 times a second.
    2. Compose our compound widget, which contains a single Static.
    3. Render a linear gradient in the background.

=== "Output"

    ```{.textual path="docs/examples/how-to/render_compose.py" columns="100" lines="40"}
    ```

The `Splash` custom widget has a `compose` method which adds a simple `Static` widget to display a message.
Additionally there is a `render` method which returns a renderable to fill the background with a gradient.

!!! tip

    As fun as this is, spinning animated gradients may be too distracting for most apps!

## Summary

Keep the following in mind when building [custom widgets](../guide/widgets.md).

1. Use `render` to return simple text, or a Rich renderable.
2. Use `compose` to create a widget out of other widgets.
3. If you define both, then `render` will be used as a *background*.


---

We are here to [help](../help.md)!
````

## File: docs/how-to/style-inline-apps.md
````markdown
# Style Inline Apps

Version 0.55.0 of Textual added support for running apps *inline* (below the prompt).
Running an inline app is as simple as adding `inline=True` to [`run()`][textual.app.App.run].

<iframe width="100%" style="aspect-ratio:757/804;" src="https://www.youtube.com/embed/dxAf3vDr4aQ" title="Textual Inline mode" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Your apps will typically run inline without modification, but you may want to make some tweaks for inline mode, which you can do with a little CSS.
This How-To will explain how.

Let's look at an inline app.
The following app displays the the current time (and keeps it up to date).

```python hl_lines="31"
--8<-- "docs/examples/how-to/inline01.py"
```

1. The `inline=True` runs the app inline.

With Textual's default settings, this clock will be displayed in 5 lines; 3 for the digits and 2 for a top and bottom border.

You can change the height or the border with CSS and the `:inline` pseudo-selector, which only matches rules in inline mode.
Let's update this app to remove the default border, and increase the height:

```python hl_lines="11-17"
--8<-- "docs/examples/how-to/inline02.py"
```

The highlighted CSS targets online inline mode.
By setting the `height` rule on Screen we can define how many lines the app should consume when it runs.
Setting `border: none` removes the default border when running in inline mode.

We've also added a rule to change the color of the clock when running inline.

## Summary

Most apps will not require modification to run inline, but if you want to tweak the height and border you can write CSS that targets inline mode with the `:inline` pseudo-selector.
````

## File: docs/how-to/work-with-containers.md
````markdown
# Save time with Textual containers

Textual's [containers][textual.containers] provide a convenient way of arranging your widgets. Let's look at them in a little detail.

!!! info "Are you in the right place?"

    We are talking about Textual container widgets here. Not to be confused with [containerization](https://en.wikipedia.org/wiki/Containerization_(computing))&mdash;which is something else entirely!


## What are containers?

Containers are reusable [compound widgets](../guide/widgets.md#compound-widgets) with preset styles to arrange their children.
For instance, there is a [Horizontal][textual.containers.Horizontal] container which arranges all of its children in a horizontal row.
Let's look at a quick example of that:

```python hl_lines="2 21"
--8<-- "docs/examples/how-to/containers01.py"
```

1. Use the with statement to add the Horizontal container.
2. Any widgets yielded within the Horizontal block will be arranged in a horizontal row.

Here's the output:

```{.textual path="docs/examples/how-to/containers01.py"}
```

Note that inside the `Horizontal` block new widgets will be placed to the right of previous widgets, forming a row.
This will still be the case if you later add or remove widgets.
Without the container, the widgets would be stacked vertically.

### How are containers implemented?

Before I describe some of the other containers, I would like to show how containers are implemented.
The following is the actual source of the `Horizontal` widget:

```python
class Horizontal(Widget):
    """An expanding container with horizontal layout and no scrollbars."""

    DEFAULT_CSS = """
    Horizontal {
        width: 1fr;
        height: 1fr;
        layout: horizontal;
        overflow: hidden hidden;
    }
    """
```

That's it!
A simple widget with a few preset styles.
The other containers are just as simple.

## Horizontal and Vertical

We've seen the `Horizontal` container in action.
The [Vertical][textual.containers.Vertical] container, as you may have guessed, work the same but arranges its children vertically, i.e. from top to bottom.

You can probably imagine what this looks like, but for sake of completeness, here is an example with a Vertical container:

```python hl_lines="2 21"
--8<-- "docs/examples/how-to/containers02.py"
```

1. Stack the widgets vertically.

And here's the output:

```{.textual path="docs/examples/how-to/containers02.py"}
```

Three boxes, vertically stacked.

!!! tip "Styling layout"

    You can set the layout of a compound widget with the [layout](../styles/layout.md) rule.

### Size behavior

Something to keep in mind when using `Horizontal` or `Vertical` is that they will consume the remaining space in the screen. Let's look at an example to illustrate that.

The following code adds a `with-border` style which draws a green border around the container.
This will help us visualize the dimensions of the container.

```python
--8<-- "docs/examples/how-to/containers03.py"
```

1. Add the `with-border` class to draw a border around the container.

Here's the output:

```{.textual path="docs/examples/how-to/containers03.py"}
```

Notice how the container is as large as the screen.
Let's look at what happens if we add another container:

```python hl_lines="31-34"
--8<-- "docs/examples/how-to/containers04.py"
```

And here's the result:

```{.textual path="docs/examples/how-to/containers04.py"}
```

Two horizontal containers divide the remaining screen space in two.
If you were to add another horizontal it would divide the screen space in to thirds&mdash;and so on.

This makes `Horizontal` and `Vertical` excellent for designing the macro layout of your app's interface, but not for making tightly packed rows or columns. For that you need the *group* containers which I'll cover next.

!!! tip "FR Units"

    You can implement this behavior of dividing the screen in your own widgets with [FR units](../guide/styles.md#fr-units)


## Group containers

The [HorizontalGroup][textual.containers.HorizontalGroup] and [VerticalGroup][textual.containers.VerticalGroup] containers are very similar to their non-group counterparts, but don't expand to fill the screen space.

Let's look at an example.
In the following code, we have two HorizontalGroups with a border so we can visualize their size.

```python hl_lines="2 27 31"
--8<-- "docs/examples/how-to/containers05.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/containers05.py"}
```

We can see that the widgets are arranged horizontally as before, but they only use as much vertical space as required to fit.

## Scrolling containers

Something to watch out for regarding the previous containers we have discussed, is that they don't scroll by default.
Let's see what happens if we add more boxes than could fit on the screen.

In the following example, we will add 10 boxes:

```python hl_lines="28 29"
--8<-- "docs/examples/how-to/containers06.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/containers06.py"}
```

We have add 10 `Box` widgets, but there is not enough room for them to fit.
The remaining boxes are off-screen and can't be viewed unless the user resizes their screen.

If we expect more content that fits, we can replacing the containers with [HorizontalScroll][textual.containers.HorizontalScroll] or [VerticalScroll][textual.containers.VerticalScroll], which will automatically add scrollbars if required.

Let's make that change:

```python hl_lines="2 27"
--8<-- "docs/examples/how-to/containers07.py"
```

Here's the output:

```{.textual path="docs/examples/how-to/containers07.py"}
```

We now have a scrollbar we can click and drag to see all the boxes.

!!! tip "Automatic scrollbars"  

    You can also implement automatic scrollbars with the [overflow](../styles/overflow.md) style.


## Center, Right, and Middle

The [Center][textual.containers.Center], [Right][textual.containers.Right], and [Middle][textual.containers.Middle] containers are handy for setting the alignment of select widgets.

First lets look at `Center` and `Right` which align their children on the horizontal axis (there is no `Left` container, as this is the default).

Here's an example:

```python hl_lines="2 28 30"
--8<-- "docs/examples/how-to/containers08.py"
```

1. The default is to align widgets to the left.
2. Align the child to the center.
3. Align the child to the right edge.

Here's the output:

```{.textual path="docs/examples/how-to/containers08.py"}
```

Note how `Center` and `Right` expand to fill the horizontal dimension, but are only as tall as they need to be.

!!! tip "Alignment in TCSS"

    You can set alignment in TCSS with the [align](../styles/align.md) rule.

The [Middle][textual.containers.Middle] container aligns its children to the center of the *vertical* axis.
Let's look at an example.
The following code aligns three boxes on the vertical axis:

```python hl_lines="2 27"
--8<-- "docs/examples/how-to/containers09.py"
```

1. Align children to the center of the vertical axis.

Here's the output:

```{.textual path="docs/examples/how-to/containers09.py"}
```

Note how the container expands on the vertical axis, but fits on the horizontal axis.

## Other containers

This how-to covers the most common widgets, but isn't exhausted.
Be sure to visit the [container reference][textual.containers] for the full list.
There may be new containers added in future versions of Textual.

## Custom containers

The builtin [containers][textual.containers] cover a number of common layout patterns, but are unlikely to cover every possible requirement.
Fortunately, creating your own is easy.
Just like the builtin containers, you can create a container by extending Widget and adding little TCSS.

Here's a template for a custom container:

```python
class MyContainer(Widget):
    """My custom container."""    
    DEFAULT_CSS = """
    MyContainer {
        # Your rules here
    }
    """    
```

## Summary

- Containers are compound widgets with preset styles for arranging their children.
- [`Horizontal`][textual.containers.Horizontal] and [`Vertical`][textual.containers.Vertical] containers stretch to fill available space.
- [`HorizontalGroup`][textual.containers.HorizontalGroup] and [`VerticalGroup`][textual.containers.VerticalGroup] fit to the height of their contents.
- [`HorizontalScroll`][textual.containers.HorizontalScroll] and [`VerticalScroll`][textual.containers.VerticalScroll] add automatic scrollbars.
- [`Center`][textual.containers.Center], [`Right`][textual.containers.Right], and [`Middle`][textual.containers.Middle] set alignment.
- Custom containers are trivial to create.
````

## File: docs/reference/index.md
````markdown
# Reference

Welcome to the Textual Reference.

<div class="grid cards" markdown>

-   :octicons-book-16:{ .lg .middle } __CSS Types__

    ---

    CSS Types are the data types that CSS [styles](../styles/index.md) accept in their rules.

    :octicons-arrow-right-24: [CSS Types Reference](../css_types/index.md)


-   :octicons-book-16:{ .lg .middle } __Events__

    ---

    Events are how Textual communicates with your application.

    :octicons-arrow-right-24: [Events Reference](../events/index.md)


-   :octicons-book-16:{ .lg .middle } __Styles__

    ---

    All the styles you can use to take your Textual app to the next level.

    [:octicons-arrow-right-24: Styles Reference](../styles/index.md)


-   :octicons-book-16:{ .lg .middle } __Widgets__

    ---

    How to use the many widgets builtin to Textual.

    :octicons-arrow-right-24: [Widgets Reference](../widgets/index.md)

  

</div>
````

## File: docs/snippets/border_sub_title_align_all_example.md
````markdown
This example shows all border title and subtitle alignments, together with some examples of how (sub)titles can have custom markup.
Open the code tabs to see the details of the code examples.

=== "Output"

    ```{.textual path="docs/examples/styles/border_sub_title_align_all.py"}
    ```

=== "border_sub_title_align_all.py"

    ```py hl_lines="6 20 26 32 41 42 44 47 53 59 65"
    --8<-- "docs/examples/styles/border_sub_title_align_all.py"
    ```

    1. Border (sub)titles can contain nested markup.
    2. Long (sub)titles get truncated and occupy as much space as possible.
    3. (Sub)titles can be stylised with Rich markup.
    4. An empty (sub)title isn't displayed.
    5. The markup can even contain Rich links.
    6. If the widget does not have a border, the title and subtitle are not shown.
    7. When the side borders are not set, the (sub)title will align with the edge of the widget.
    8. The title and subtitle are aligned on the left and very long, so they get truncated and we can still see the rightmost character of the border edge.
    9. The title and subtitle are centered and very long, so they get truncated and are centered with one character of padding on each side.
    10. The title and subtitle are aligned on the right and very long, so they get truncated and we can still see the leftmost character of the border edge.
    11. An auxiliary function to create labels with border title and subtitle.

=== "border_sub_title_align_all.tcss"

    ```css hl_lines="12 16 30 34 41 46"
    --8<-- "docs/examples/styles/border_sub_title_align_all.tcss"
    ```

    1. The default alignment for the title is `left` and the default alignment for the subtitle is `right`.
    2. Specifying an alignment when the (sub)title is too long has no effect. (Although, it will have an effect if the (sub)title is shortened or if the widget is widened.)
    3. Setting the alignment does not affect empty (sub)titles.
    4. If the border is not set, or set to `none`/`hidden`, the (sub)title is not shown.
    5. If the (sub)title alignment is on a side which does not have a border edge, the (sub)title will be flush to that side.
    6. Naturally, (sub)title positioning is affected by padding.
````

## File: docs/snippets/border_title_color.md
````markdown
The following examples demonstrates customization of the border color and text style rules.

=== "Output"

    ```{.textual path="docs/examples/styles/border_title_colors.py"}
    ```

=== "border_title_colors.py"

    ```python
    --8<-- "docs/examples/styles/border_title_colors.py"
    ```

=== "border_title_colors.tcss"

    ```css
    --8<-- "docs/examples/styles/border_title_colors.tcss"
    ```
````

## File: docs/snippets/border_vs_outline_example.md
````markdown
The next example makes the difference between [`border`](../styles/border.md) and [`outline`](../styles/outline.md) clearer by having three labels side-by-side.
They contain the same text, have the same width and height, and are styled exactly the same up to their [`border`](../styles/border.md) and [`outline`](../styles/outline.md) styles.

This example also shows that a widget cannot contain both a `border` and an `outline`:

=== "Output"

    ```{.textual path="docs/examples/styles/outline_vs_border.py"}
    ```

=== "outline_vs_border.py"

    ```python
    --8<-- "docs/examples/styles/outline_vs_border.py"
    ```

=== "outline_vs_border.tcss"

    ```css hl_lines="5-7 9-11"
    --8<-- "docs/examples/styles/outline_vs_border.tcss"
    ```
````

## File: docs/snippets/see_also_border.md
````markdown
- [`border-title-align`](./border_title_align.md) to set the title's alignment.
- [`border-title-color`](./border_subtitle_color.md) to set the title's color.
- [`border-title-background`](./border_subtitle_background.md) to set the title's background color.
- [`border-title-style`](./border_subtitle_style.md) to set the title's text style.

- [`border-subtitle-align`](./border_subtitle_align.md) to set the sub-title's alignment.
- [`border-subtitle-color`](./border_subtitle_color.md) to set the sub-title's color.
- [`border-subtitle-background`](./border_subtitle_background.md) to set the sub-title's background color.
- [`border-subtitle-style`](./border_subtitle_style.md) to set the sub-title's text style.
````

## File: docs/snippets/syntax_block_end.md
````markdown
</div>
<!-- Include this snippet when ending a code block that shows the syntax of a CSS rule. -->
````

## File: docs/snippets/syntax_block_start.md
````markdown
<!-- Include this snippet when starting a code block that shows the syntax of a CSS rule. -->
<div class="highlight" style="padding: 0.5em 1em; background: var(--md-code-bg-color);font-family: 'Roboto Mono',monospace;">
````

## File: docs/styles/grid/column_span.md
````markdown
# Column-span

The `column-span` style specifies how many columns a widget will span in a grid layout.

!!! note

    This style only affects widgets that are direct children of a widget with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
column-span: <a href="../../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `column-span` style accepts a single non-negative [`<integer>`](../../css_types/integer.md) that quantifies how many columns the given widget spans.

## Example

The example below shows a 4 by 4 grid where many placeholders span over several columns.

=== "Output"

    ```{.textual path="docs/examples/styles/column_span.py"}
    ```

=== "column_span.py"

    ```py
    --8<-- "docs/examples/styles/column_span.py"
    ```

=== "column_span.tcss"

    ```css hl_lines="2 5 8 11 14 20"
    --8<-- "docs/examples/styles/column_span.tcss"
    ```

## CSS

```css
column-span: 3;
```

## Python

```py
widget.styles.column_span = 3
```

## See also

 - [`row-span`](./row_span.md) to specify how many rows a widget spans.
````

## File: docs/styles/grid/grid_columns.md
````markdown
# Grid-columns

The `grid-columns` style allows to define the width of the columns of the grid.

!!! note

    This style only affects widgets with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
grid-columns: <a href="../../../css_types/scalar">&lt;scalar&gt;</a>+;
--8<-- "docs/snippets/syntax_block_end.md"

The `grid-columns` style takes one or more [`<scalar>`](../../css_types/scalar.md) that specify the length of the columns of the grid.

If there are more columns in the grid than scalars specified in `grid-columns`, they are reused cyclically.
If the number of [`<scalar>`](../../css_types/scalar.md) is in excess, the excess is ignored.

## Example

The example below shows a grid with 10 labels laid out in a grid with 2 rows and 5 columns.

We set `grid-columns: 1fr 16 2fr`.
Because there are more rows than scalars in the style definition, the scalars will be reused:

 - columns 1 and 4 have width `1fr`;
 - columns 2 and 5 have width `16`; and
 - column 3 has width `2fr`.


=== "Output"

    ```{.textual path="docs/examples/styles/grid_columns.py"}
    ```

=== "grid_columns.py"

    ```py
    --8<-- "docs/examples/styles/grid_columns.py"
    ```

=== "grid_columns.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/grid_columns.tcss"
    ```

## CSS

```css
/* Set all columns to have 50% width */
grid-columns: 50%;

/* Every other column is twice as wide as the first one */
grid-columns: 1fr 2fr;
```

## Python

```py
grid.styles.grid_columns = "50%"
grid.styles.grid_columns = "1fr 2fr"
```

## See also

 - [`grid-rows`](./grid_rows.md) to specify the height of the grid rows.
````

## File: docs/styles/grid/grid_gutter.md
````markdown
# Grid-gutter

The `grid-gutter` style sets the size of the gutter in the grid layout.
That is, it sets the space between adjacent cells in the grid.

Gutter is only applied _between_ the edges of cells.
No spacing is added between the edges of the cells and the edges of the container.

!!! note

    This style only affects widgets with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
grid-gutter: <a href="../../../css_types/integer">&lt;integer&gt;</a> [<a href="../../../css_types/integer">&lt;integer&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `grid-gutter` style takes one or two [`<integer>`](../../css_types/integer.md) that set the length of the gutter along the vertical and horizontal axes.
If only one [`<integer>`](../../css_types/integer.md) is supplied, it sets the vertical and horizontal gutters.
If two are supplied, they set the vertical and horizontal gutters, respectively.

## Example

The example below employs a common trick to apply visually consistent spacing around all grid cells.

=== "Output"

    ```{.textual path="docs/examples/styles/grid_gutter.py"}
    ```

=== "grid_gutter.py"

    ```py
    --8<-- "docs/examples/styles/grid_gutter.py"
    ```

=== "grid_gutter.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/grid_gutter.tcss"
    ```

    1. We set the horizontal gutter to be double the vertical gutter because terminal cells are typically two times taller than they are wide. Thus, the result shows visually consistent spacing around grid cells.

## CSS

```css
/* Set vertical and horizontal gutters to be the same */
grid-gutter: 5;

/* Set vertical and horizontal gutters separately */
grid-gutter: 1 2;
```

## Python

Vertical and horizontal gutters correspond to different Python properties, so they must be set separately:

```py
widget.styles.grid_gutter_vertical = "1"
widget.styles.grid_gutter_horizontal = "2"
```
````

## File: docs/styles/grid/grid_rows.md
````markdown
# Grid-rows

The `grid-rows` style allows to define the height of the rows of the grid.

!!! note

    This style only affects widgets with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
grid-rows: <a href="../../../css_types/scalar">&lt;scalar&gt;</a>+;
--8<-- "docs/snippets/syntax_block_end.md"

The `grid-rows` style takes one or more [`<scalar>`](../../css_types/scalar.md) that specify the length of the rows of the grid.

If there are more rows in the grid than scalars specified in `grid-rows`, they are reused cyclically.
If the number of [`<scalar>`](../../css_types/scalar.md) is in excess, the excess is ignored.

## Example

The example below shows a grid with 10 labels laid out in a grid with 5 rows and 2 columns.

We set `grid-rows: 1fr 6 25%`.
Because there are more rows than scalars in the style definition, the scalars will be reused:

 - rows 1 and 4 have height `1fr`;
 - rows 2 and 5 have height `6`; and
 - row 3 has height `25%`.


=== "Output"

    ```{.textual path="docs/examples/styles/grid_rows.py"}
    ```

=== "grid_rows.py"

    ```py
    --8<-- "docs/examples/styles/grid_rows.py"
    ```

=== "grid_rows.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/grid_rows.tcss"
    ```

## CSS

```css
/* Set all rows to have 50% height */
grid-rows: 50%;

/* Every other row is twice as tall as the first one */
grid-rows: 1fr 2fr;
```

## Python

```py
grid.styles.grid_rows = "50%"
grid.styles.grid_rows = "1fr 2fr"
```

## See also

 - [`grid-columns`](./grid_columns.md) to specify the width of the grid columns.
````

## File: docs/styles/grid/grid_size.md
````markdown
# Grid-size

The `grid-size` style sets the number of columns and rows in a grid layout.

The number of rows can be left unspecified and it will be computed automatically.

!!! note

    This style only affects widgets with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
grid-size: <a href="../../../css_types/integer">&lt;integer&gt;</a> [<a href="../../../css_types/integer">&lt;integer&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `grid-size` style takes one or two non-negative [`<integer>`](../../css_types/integer.md).
The first defines how many columns there are in the grid.
If present, the second one sets the number of rows – regardless of the number of children of the grid –, otherwise the number of rows is computed automatically.

## Examples

### Columns and rows

In the first example, we create a grid with 2 columns and 5 rows, although we do not have enough labels to fill in the whole grid:

=== "Output"

    ```{.textual path="docs/examples/styles/grid_size_both.py"}
    ```

=== "grid_size_both.py"

    ```py
    --8<-- "docs/examples/styles/grid_size_both.py"
    ```

=== "grid_size_both.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/grid_size_both.tcss"
    ```

    1. Create a grid with 2 columns and 4 rows.

### Columns only

In the second example, we create a grid with 2 columns and however many rows are needed to display all of the grid children:

=== "Output"

    ```{.textual path="docs/examples/styles/grid_size_columns.py"}
    ```

=== "grid_size_columns.py"

    ```py
    --8<-- "docs/examples/styles/grid_size_columns.py"
    ```

=== "grid_size_columns.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/grid_size_columns.tcss"
    ```

    1. Create a grid with 2 columns and however many rows.

## CSS

```css
/* Grid with 3 columns and 5 rows */
grid-size: 3 5;

/* Grid with 4 columns and as many rows as needed */
grid-size: 4;
```

## Python

To programmatically change the grid size, the number of rows and columns must be specified separately:

```py
widget.styles.grid_size_rows = 3
widget.styles.grid_size_columns = 6
```
````

## File: docs/styles/grid/index.md
````markdown
# Grid

There are a number of styles relating to the Textual `grid` layout.

For an in-depth look at the grid layout, visit the grid [guide](../../guide/layout.md#grid).

| Property       | Description                                    |
|----------------|------------------------------------------------|
| [`column-span`](./column_span.md)  | Number of columns a cell spans.                |
| [`grid-columns`](./grid_columns.md) | Width of grid columns.                         |
| [`grid-gutter`](./grid_gutter.md)  | Spacing between grid cells.                    |
| [`grid-rows`](./grid_rows.md)    | Height of grid rows.                           |
| [`grid-size`](./grid_size.md)    | Number of columns and rows in the grid layout. |
| [`row-span`](./row_span.md)     | Number of rows a cell spans.                   |

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./column_span/">column-span</a>: <a href="../../../css_types/integer">&lt;integer&gt;</a>;

<a href="./grid_columns/">grid-columns</a>: <a href="../../../css_types/scalar">&lt;scalar&gt;</a>+;

<a href="./grid_gutter/">grid-gutter</a>: <a href="../../../css_types/scalar">&lt;scalar&gt;</a> [<a href="../../../css_types/scalar">&lt;scalar&gt;</a>];

<a href="./grid_rows/">grid-rows</a>: <a href="../../../css_types/scalar">&lt;scalar&gt;</a>+;

<a href="./grid_size/">grid-size</a>: <a href="../../../css_types/integer">&lt;integer&gt;</a> [<a href="../../../css_types/integer">&lt;integer&gt;</a>];

<a href="./row_span/">row-span</a>: <a href="../../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

Visit each style's reference page to learn more about how the values are used.

## Example

The example below shows all the styles above in action.
The `grid-size: 3 4;` declaration sets the grid to 3 columns and 4 rows.
The first cell of the grid, tinted magenta, shows a cell spanning multiple rows and columns.
The spacing between grid cells is defined by the `grid-gutter` style.

=== "Output"

    ```{.textual path="docs/examples/styles/grid.py"}
    ```

=== "grid.py"

    ```python
    --8<-- "docs/examples/styles/grid.py"
    ```

=== "grid.tcss"

    ```css
    --8<-- "docs/examples/styles/grid.tcss"
    ```

!!! warning

    The styles listed on this page will only work when the layout is `grid`.

## See also

 - The [grid layout](../../guide/layout.md#grid) guide.
````

## File: docs/styles/grid/row_span.md
````markdown
# Row-span

The `row-span` style specifies how many rows a widget will span in a grid layout.

!!! note

    This style only affects widgets that are direct children of a widget with `layout: grid`.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
row-span: <a href="../../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `row-span` style accepts a single non-negative [`<integer>`](../../css_types/integer.md) that quantifies how many rows the given widget spans.

## Example

The example below shows a 4 by 4 grid where many placeholders span over several rows.

Notice that grid cells are filled from left to right, top to bottom.
After placing the placeholders `#p1`, `#p2`, `#p3`, and `#p4`, the next available cell is in the second row, fourth column, which is where the top of `#p5` is.

=== "Output"

    ```{.textual path="docs/examples/styles/row_span.py"}
    ```

=== "row_span.py"

    ```py
    --8<-- "docs/examples/styles/row_span.py"
    ```

=== "row_span.tcss"

    ```css hl_lines="2 5 8 11 14 17 20"
    --8<-- "docs/examples/styles/row_span.tcss"
    ```

## CSS

```css
row-span: 3
```

## Python

```py
widget.styles.row_span = 3
```

## See also

 - [`column-span`](./column_span.md) to specify how many columns a widget spans.
````

## File: docs/styles/links/index.md
````markdown
# Links

Textual supports the concept of inline "links" embedded in text which trigger an action when pressed.
There are a number of styles which influence the appearance of these links within a widget.

!!! note

    These CSS rules only target Textual action links. Internet hyperlinks are not affected by these styles.

| Property                                              | Description                                                       |
|-------------------------------------------------------|-------------------------------------------------------------------|
| [`link-background`](./link_background.md)             | The background color of the link text.                            |
| [`link-background-hover`](./link_background_hover.md) | The background color of the link text when the cursor is over it. |
| [`link-color`](./link_color.md)                       | The color of the link text.                                       |
| [`link-color-hover`](./link_color_hover.md)           | The color of the link text when the cursor is over it.            |
| [`link-style`](./link_style.md)                       | The style of the link text (e.g. underline).                      |
| [`link-style-hover`](./link_style_hover.md)           | The style of the link text when the cursor is over it.            |

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./link_background">link-background</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./link_color">link-color</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./link_style">link-style</a>: <a href="../../../css_types/text_style">&lt;text-style&gt;</a>;

<a href="./link_background_hover">link-background-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./link_color_hover">link-color-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./link_style_hover">link-style-hover</a>: <a href="../../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

Visit each style's reference page to learn more about how the values are used.

## Example

In the example below, the first label illustrates default link styling.
The second label uses CSS to customize the link color, background, and style.

=== "Output"

    ```{.textual path="docs/examples/styles/links.py"}
    ```

=== "links.py"

    ```python
    --8<-- "docs/examples/styles/links.py"
    ```

=== "links.tcss"

    ```css
    --8<-- "docs/examples/styles/links.tcss"
    ```

## Additional Notes

* Inline links are not widgets, and thus cannot be focused.

## See Also

* An [introduction to links](../../guide/actions.md#links) in the Actions guide.

[//]: # (TODO: Links are documented twice in the guide, and one will likely be removed. Check the link above still works after that.)
````

## File: docs/styles/links/link_background_hover.md
````markdown
# Link-background-hover

The `link-background-hover` style sets the background color of the link when the mouse cursor is over the link.

!!! note

    `link-background-hover` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-background-hover: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-background-hover` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the background color of text enclosed in Textual action links when the mouse pointer is over it.

### Defaults

If not provided, a Textual action link will have `link-background-hover` set to `$accent`.

## Example

The example below shows some links that have their background color changed when the mouse moves over it and it shows that there is a default color for `link-background-hover`.

It also shows that `link-background-hover` does not affect hyperlinks.

=== "Output"

    ![](./demos/link_background_hover_demo.gif)

    !!! note

        The GIF has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/link_background_hover.py`.

=== "link_background_hover.py"

    ```py hl_lines="10-11 14-15 18-19 22-23"
    --8<-- "docs/examples/styles/link_background_hover.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-background-hover` rule.
    2. This label has an "action link" that can be styled with `link-background-hover`.
    3. This label has an "action link" that can be styled with `link-background-hover`.
    4. This label has an "action link" that can be styled with `link-background-hover`.

=== "link_background_hover.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_background_hover.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.
    2. The default behavior for links on hover is to change to a different background color, so we don't need to change anything if all we want is to add emphasis to the link under the mouse.

## CSS

```css
link-background-hover: red 70%;
link-background-hover: $accent;
```

## Python

```py
widget.styles.link_background_hover = "red 70%"
widget.styles.link_background_hover = "$accent"

# You can also use a `Color` object directly:
widget.styles.link_background_hover = Color(100, 30, 173)
```

## See also

 - [`link-background`](./link_background.md) to set the background color of link text.
 - [`link-color-hover`](./link_color_hover.md) to set the color of link text when the mouse pointer is over it.
 - [`link-style-hover`](./link_style_hover.md) to set the style of link text when the mouse pointer is over it.
````

## File: docs/styles/links/link_background.md
````markdown
# Link-background

The `link-background` style sets the background color of the link.

!!! note

    `link-background` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-background: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-background` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the background color of text enclosed in Textual action links.

## Example

The example below shows some links with their background color changed.
It also shows that `link-background` does not affect hyperlinks.

=== "Output"

    ```{.textual path="docs/examples/styles/link_background.py" lines=6}
    ```

=== "link_background.py"

    ```py hl_lines="10-11 14-15 18-20 22-23"
    --8<-- "docs/examples/styles/link_background.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-background` rule.
    2. This label has an "action link" that can be styled with `link-background`.
    3. This label has an "action link" that can be styled with `link-background`.
    4. This label has an "action link" that can be styled with `link-background`.

=== "link_background.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_background.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```css
link-background: red 70%;
link-background: $accent;
```

## Python

```py
widget.styles.link_background = "red 70%"
widget.styles.link_background = "$accent"

# You can also use a `Color` object directly:
widget.styles.link_background = Color(100, 30, 173)
```

## See also

 - [`link-color`](./link_color.md) to set the color of link text.
 - [`link-background-hover`](./link_background_hover.md) to set the background color of link text when the mouse pointer is over it.
````

## File: docs/styles/links/link_color_hover.md
````markdown
# Link-color-hover

The `link-color-hover` style sets the color of the link text when the mouse cursor is over the link.

!!! note

    `link-color-hover` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-color-hover: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-color-hover` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the color of text enclosed in Textual action links when the mouse pointer is over it.

### Defaults

If not provided, a Textual action link will have `link-color-hover` set to `white`.

## Example

The example below shows some links that have their color changed when the mouse moves over it.
It also shows that `link-color-hover` does not affect hyperlinks.

=== "Output"

    ![](./demos/link_color_hover_demo.gif)

    !!! note

        The background color also changes when the mouse moves over the links because that is the default behavior.
        That can be customised by setting [`link-background-hover`](./link_background_hover.md) but we haven't done so in this example.

    !!! note

        The GIF has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/link_color_hover.py`.

=== "link_color_hover.py"

    ```py hl_lines="10-11 14-15 18-19 22-23"
    --8<-- "docs/examples/styles/link_color_hover.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-color-hover` rule.
    2. This label has an "action link" that can be styled with `link-color-hover`.
    3. This label has an "action link" that can be styled with `link-color-hover`.
    4. This label has an "action link" that can be styled with `link-color-hover`.

=== "link_color_hover.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_color_hover.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```css
link-color-hover: red 70%;
link-color-hover: black;
```

## Python

```py
widget.styles.link_color_hover = "red 70%"
widget.styles.link_color_hover = "black"

# You can also use a `Color` object directly:
widget.styles.link_color_hover = Color(100, 30, 173)
```

## See also

 - [`link-color`](./link_color.md) to set the color of link text.
 - [`link-background-hover`](./link_background_hover.md) to set the background color of link text when the mouse pointer is over it.
 - [`link-style-hover`](./link_style_hover.md) to set the style of link text when the mouse pointer is over it.
````

## File: docs/styles/links/link_color.md
````markdown
# Link-color

The `link-color` style sets the color of the link text.

!!! note

    `link-color` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-color: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`link-color` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the color of text enclosed in Textual action links.

## Example

The example below shows some links with their color changed.
It also shows that `link-color` does not affect hyperlinks.

=== "Output"

    ```{.textual path="docs/examples/styles/link_color.py" lines=6}
    ```

=== "link_color.py"

    ```py hl_lines="10-11 14-15 18-19 22-23"
    --8<-- "docs/examples/styles/link_color.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-color` rule.
    2. This label has an "action link" that can be styled with `link-color`.
    3. This label has an "action link" that can be styled with `link-color`.
    4. This label has an "action link" that can be styled with `link-color`.

=== "link_color.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_color.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```css
link-color: red 70%;
link-color: $accent;
```

## Python

```py
widget.styles.link_color = "red 70%"
widget.styles.link_color = "$accent"

# You can also use a `Color` object directly:
widget.styles.link_color = Color(100, 30, 173)
```

## See also

 - [`link-background`](./link_background.md) to set the background color of link text.
 - [`link-color-hover`](./link_color_hover.md) to set the color of link text when the mouse pointer is over it.
````

## File: docs/styles/links/link_style_hover.md
````markdown
# Link-style-hover

The `link-style-hover` style sets the text style for the link text when the mouse cursor is over the link.

!!! note

    `link-style-hover` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-style-hover: <a href="../../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

`link-style-hover` applies its [`<text-style>`](../../css_types/text_style.md) to the text of Textual action links when the mouse pointer is over them.

### Defaults

If not provided, a Textual action link will have `link-style-hover` set to `bold`.

## Example

The example below shows some links that have their color changed when the mouse moves over it.
It also shows that `link-style-hover` does not affect hyperlinks.

=== "Output"

    ![](./demos/link_style_hover_demo.gif)

    !!! note

        The background color also changes when the mouse moves over the links because that is the default behavior.
        That can be customised by setting [`link-background-hover`](./link_background_hover.md) but we haven't done so in this example.

    !!! note

        The GIF has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/link_style_hover.py`.

=== "link_style_hover.py"

    ```py hl_lines="10-11 14-15 18-19 22-23"
    --8<-- "docs/examples/styles/link_style_hover.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-style-hover` rule.
    2. This label has an "action link" that can be styled with `link-style-hover`.
    3. This label has an "action link" that can be styled with `link-style-hover`.
    4. This label has an "action link" that can be styled with `link-style-hover`.

=== "link_style_hover.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_style_hover.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.
    2. The default behavior for links on hover is to change to a different text style, so we don't need to change anything if all we want is to add emphasis to the link under the mouse.

## CSS

```css
link-style-hover: bold;
link-style-hover: bold italic reverse;
```

## Python

```py
widget.styles.link_style_hover = "bold"
widget.styles.link_style_hover = "bold italic reverse"
```

## See also

 - [`link-background-hover`](./link_background_hover.md) to set the background color of link text when the mouse pointer is over it.
 - [`link-color-hover`](./link_color_hover.md) to set the color of link text when the mouse pointer is over it.
 - [`link-style`](./link_style.md) to set the style of link text.
 - [`text-style`](../text_style.md) to set the style of text in a widget.
````

## File: docs/styles/links/link_style.md
````markdown
# Link-style

The `link-style` style sets the text style for the link text.

!!! note

    `link-style` only applies to Textual action links as described in the [actions guide](../../guide/actions.md#links) and not to regular hyperlinks.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
link-style: <a href="../../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

`link-style` will take all the values specified and will apply that styling to text that is enclosed by a Textual action link.

### Defaults

If not provided, a Textual action link will have `link-style` set to `underline`.

## Example

The example below shows some links with different styles applied to their text.
It also shows that `link-style` does not affect hyperlinks.

=== "Output"

    ```{.textual path="docs/examples/styles/link_style.py" lines=6}
    ```

=== "link_style.py"

    ```py hl_lines="10-11 14-15 18-19 22-23"
    --8<-- "docs/examples/styles/link_style.py"
    ```

    1. This label has a hyperlink so it won't be affected by the `link-style` rule.
    2. This label has an "action link" that can be styled with `link-style`.
    3. This label has an "action link" that can be styled with `link-style`.
    4. This label has an "action link" that can be styled with `link-style`.

=== "link_style.tcss"

    ```css hl_lines="2 6 10"
    --8<-- "docs/examples/styles/link_style.tcss"
    ```

    1. This will only affect one of the labels because action links are the only links that this rule affects.

## CSS

```css
link-style: bold;
link-style: bold italic reverse;
```

## Python

```py
widget.styles.link_style = "bold"
widget.styles.link_style = "bold italic reverse"
```

## See also

 - [`link-style-hover`](./link_style_hover.md) to set the style of link text when the mouse pointer is over it.
 - [`text-style`](../text_style.md) to set the style of text in a widget.
````

## File: docs/styles/scrollbar_colors/index.md
````markdown
# Scrollbar colors

There are a number of styles to set the colors used in Textual scrollbars.
You won't typically need to do this, as the default themes have carefully chosen colors, but you can if you want to.

| Style                                                             | Applies to                                               |
|-------------------------------------------------------------------|----------------------------------------------------------|
| [`scrollbar-background`](./scrollbar_background.md)               | Scrollbar background.                                    |
| [`scrollbar-background-active`](./scrollbar_background_active.md) | Scrollbar background when the thumb is being dragged.    |
| [`scrollbar-background-hover`](./scrollbar_background_hover.md)   | Scrollbar background when the mouse is hovering over it. |
| [`scrollbar-color`](./scrollbar_color.md)                         | Scrollbar "thumb" (movable part).                        |
| [`scrollbar-color-active`](./scrollbar_color_active.md)           | Scrollbar thumb when it is active (being dragged).       |
| [`scrollbar-color-hover`](./scrollbar_color_hover.md)             | Scrollbar thumb when the mouse is hovering over it.      |
| [`scrollbar-corner-color`](./scrollbar_corner_color.md)           | The gap between the horizontal and vertical scrollbars.  |

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_background">scrollbar-background</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_background_active">scrollbar-background-active</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_background_hover">scrollbar-background-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_color">scrollbar-color</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_color_active">scrollbar-color-active</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_color_hover">scrollbar-color-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];

<a href="./scrollbar_corner_color">scrollbar-corner-color</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

Visit each style's reference page to learn more about how the values are used.

## Example

This example shows two panels that contain oversized text.
The right panel sets `scrollbar-background`, `scrollbar-color`, and `scrollbar-corner-color`, and the left panel shows the default colors for comparison.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbars.py"}
    ```

=== "scrollbars.py"

    ```python
    --8<-- "docs/examples/styles/scrollbars.py"
    ```

=== "scrollbars.tcss"

    ```css
    --8<-- "docs/examples/styles/scrollbars.tcss"
    ```
````

## File: docs/styles/scrollbar_colors/scrollbar_background_active.md
````markdown
# Scrollbar-background-active

The `scrollbar-background-active` style sets the background color of the scrollbar when the thumb is being dragged.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_background_active">scrollbar-background-active</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-background-active` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the background color of a scrollbar when its thumb is being dragged.

## Example

=== "Output"

    ![](scrollbar_colors_demo.gif)

    !!! note

        The GIF above has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/scrollbars2.py`.

=== "scrollbars2.py"

    ```py
    --8<-- "docs/examples/styles/scrollbars2.py"
    ```

=== "scrollbars2.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/scrollbars2.tcss"
    ```

## CSS

```css
scrollbar-background-active: red;
```

## Python

```py
widget.styles.scrollbar_background_active = "red"
```

## See also

 - [`scrollbar-background`](./scrollbar_background.md) to set the background color of scrollbars.
 - [`scrollbar-background-hover`](./scrollbar_color_hover.md) to set the scrollbar background color when the mouse pointer is over it.
 - [`scrollbar-color-active`](./scrollbar_color_active.md) to set the scrollbar color when the scrollbar is being dragged.
````

## File: docs/styles/scrollbar_colors/scrollbar_background_hover.md
````markdown
# Scrollbar-background-hover

The `scrollbar-background-hover` style sets the background color of the scrollbar when the cursor is over it.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_background_hover">scrollbar-background-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-background-hover` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the background color of a scrollbar when the cursor is over it.

## Example

=== "Output"

    ![](scrollbar_colors_demo.gif)

    !!! note

        The GIF above has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/scrollbars2.py`.

=== "scrollbars2.py"

    ```py
    --8<-- "docs/examples/styles/scrollbars2.py"
    ```

=== "scrollbars2.tcss"

    ```css hl_lines="4"
    --8<-- "docs/examples/styles/scrollbars2.tcss"
    ```

## CSS

```css
scrollbar-background-hover: purple;
```

## Python

```py
widget.styles.scrollbar_background_hover = "purple"
```

## See also

## See also

 - [`scrollbar-background`](./scrollbar_background.md) to set the background color of scrollbars.
 - [`scrollbar-background-active`](./scrollbar_color_active.md) to set the scrollbar background color when the scrollbar is being dragged.
 - [`scrollbar-color-hover`](./scrollbar_color_hover.md) to set the scrollbar color when the mouse pointer is over it.
````

## File: docs/styles/scrollbar_colors/scrollbar_background.md
````markdown
# Scrollbar-background

The `scrollbar-background` style sets the background color of the scrollbar.
## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_background">scrollbar-background</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-background` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the background color of a scrollbar.

## Example

=== "Output"

    ![](scrollbar_colors_demo.gif)

    !!! note

        The GIF above has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/scrollbars2.py`.

=== "scrollbars2.py"

    ```py
    --8<-- "docs/examples/styles/scrollbars2.py"
    ```

=== "scrollbars2.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/scrollbars2.tcss"
    ```

## CSS

```css
scrollbar-background: blue;
```

## Python

```py
widget.styles.scrollbar_background = "blue"
```

## See also

 - [`scrollbar-background-active`](./scrollbar_color_active.md) to set the scrollbar background color when the scrollbar is being dragged.
 - [`scrollbar-background-hover`](./scrollbar_color_hover.md) to set the scrollbar background color when the mouse pointer is over it.
 - [`scrollbar-color`](./scrollbar_color.md) to set the color of scrollbars.
 - [`scrollbar-corner-color`](./scrollbar_corner_color.md) to set the color of the corner where horizontal and vertical scrollbars meet.
````

## File: docs/styles/scrollbar_colors/scrollbar_color_active.md
````markdown
# Scrollbar-color-active

The `scrollbar-color-active` style sets the color of the scrollbar when the thumb is being dragged.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_color_active">scrollbar-color-active</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-color-active` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the color of a scrollbar when its thumb is being dragged.

## Example

=== "Output"

    ![](scrollbar_colors_demo.gif)

    !!! note

        The GIF above has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/scrollbars2.py`.

=== "scrollbars2.py"

    ```py
    --8<-- "docs/examples/styles/scrollbars2.py"
    ```

=== "scrollbars2.tcss"

    ```css hl_lines="6"
    --8<-- "docs/examples/styles/scrollbars2.tcss"
    ```

## CSS

```css
scrollbar-color-active: yellow;
```

## Python

```py
widget.styles.scrollbar_color_active = "yellow"
```

## See also

 - [`scrollbar-background-active`](./scrollbar_color_active.md) to set the scrollbar background color when the scrollbar is being dragged.
 - [`scrollbar-color`](./scrollbar_color.md) to set the color of scrollbars.
 - [`scrollbar-color-hover`](./scrollbar_color_hover.md) to set the scrollbar color when the mouse pointer is over it.
````

## File: docs/styles/scrollbar_colors/scrollbar_color_hover.md
````markdown
# Scrollbar-color-hover

The `scrollbar-color-hover` style sets the color of the scrollbar when the cursor is over it.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_color_hover">scrollbar-color-hover</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-color-hover` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the color of a scrollbar when the cursor is over it.

## Example

=== "Output"

    ![](scrollbar_colors_demo.gif)

    !!! note

        The GIF above has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/scrollbars2.py`.

=== "scrollbars2.py"

    ```py
    --8<-- "docs/examples/styles/scrollbars2.py"
    ```

=== "scrollbars2.tcss"

    ```css hl_lines="7"
    --8<-- "docs/examples/styles/scrollbars2.tcss"
    ```

## CSS

```css
scrollbar-color-hover: pink;
```

## Python

```py
widget.styles.scrollbar_color_hover = "pink"
```

## See also

 - [`scrollbar-background-hover`](./scrollbar_color_hover.md) to set the scrollbar background color when the mouse pointer is over it.
 - [`scrollbar-color`](./scrollbar_color.md) to set the color of scrollbars.
 - [`scrollbar-color-active`](./scrollbar_color_active.md) to set the scrollbar color when the scrollbar is being dragged.
````

## File: docs/styles/scrollbar_colors/scrollbar_color.md
````markdown
# Scrollbar-color

The `scrollbar-color` style sets the color of the scrollbar.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_color">scrollbar-color</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-color` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the color of a scrollbar.

## Example

=== "Output"

    ![](scrollbar_colors_demo.gif)

    !!! note

        The GIF above has reduced quality to make it easier to load in the documentation.
        Try running the example yourself with `textual run docs/examples/styles/scrollbars2.py`.

=== "scrollbars2.py"

    ```py
    --8<-- "docs/examples/styles/scrollbars2.py"
    ```

=== "scrollbars2.tcss"

    ```css hl_lines="5"
    --8<-- "docs/examples/styles/scrollbars2.tcss"
    ```

## CSS

```css
scrollbar-color: cyan;
```

## Python

```py
widget.styles.scrollbar_color = "cyan"
```

## See also

 - [`scrollbar-background`](./scrollbar_background.md) to set the background color of scrollbars.
 - [`scrollbar-color-active`](./scrollbar_color_active.md) to set the scrollbar color when the scrollbar is being dragged.
 - [`scrollbar-color-hover`](./scrollbar_color_hover.md) to set the scrollbar color when the mouse pointer is over it.
 - [`scrollbar-corner-color`](./scrollbar_corner_color.md) to set the color of the corner where horizontal and vertical scrollbars meet.
````

## File: docs/styles/scrollbar_colors/scrollbar_corner_color.md
````markdown
# Scrollbar-corner-color

The `scrollbar-corner-color` style sets the color of the gap between the horizontal and vertical scrollbars.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<a href="./scrollbar_corner_color">scrollbar-corner-color</a>: <a href="../../../css_types/color">&lt;color&gt;</a> [<a href="../../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

`scrollbar-corner-color` accepts a [`<color>`](../../css_types/color.md) (with an optional opacity level defined by a [`<percentage>`](../../css_types/percentage.md)) that is used to define the color of the gap between the horizontal and vertical scrollbars of a widget.

## Example

The example below sets the scrollbar corner (bottom-right corner of the screen) to white.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_corner_color.py" lines=5}
    ```

=== "scrollbar_corner_color.py"

    ```py
    --8<-- "docs/examples/styles/scrollbar_corner_color.py"
    ```

=== "scrollbar_corner_color.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/scrollbar_corner_color.tcss"
    ```

## CSS

```css
scrollbar-corner-color: white;
```

## Python

```py
widget.styles.scrollbar_corner_color = "white"
```

## See also

 - [`scrollbar-background`](./scrollbar_background.md) to set the background color of scrollbars.
 - [`scrollbar-color`](./scrollbar_color.md) to set the color of scrollbars.
````

## File: docs/styles/_template.md
````markdown
<!-- This is the template file for a CSS style reference page. -->

# Style-name

<!-- Short description of what the style does, without syntax details or anything.
One or two sentences is typically enough. -->

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
<!--
Formal syntax description of the style
style-name: <a href="../../css_types/type_one">&lt;type-one&gt;</a>;
-->
--8<-- "docs/snippets/syntax_block_end.md"

<!-- Description of what the style uses the types/values for. -->

### Values

<!--
For enum-like styles that don't warrant a dedicated type.
-->

### Defaults

<!-- If necessary, make note of the default values here.
Otherwise, delete this section.
E.g., `border` contains this section. -->

## Examples

<!--
Short description of the first example.

=== "Output"

    ```{.textual path="docs/examples/styles/style.py"}
    ```

=== "style.py"

    ```py
    --8<-- "docs/examples/styles/style.py"
    ```

=== "style.tcss"

    ```css
    --8<-- "docs/examples/styles/style.tcss"
    ```
-->

<!--
Short description of the second example.
(If only one example is given, make sure the section is called "Example" and not "Examples".)

=== "Output"

    ```{.textual path="docs/examples/styles/style.py"}
    ```

=== "style.py"

    ```py
    --8<-- "docs/examples/styles/style.py"
    ```

=== "style.tcss"

    ```css
    --8<-- "docs/examples/styles/style.tcss"
    ```

-->

<!-- ... -->

## CSS

<!--
The CSS syntax for the rule definitions.
Include comments when relevant.
Include all variations.
List all values, if possible and sensible.

```css
rule-name: value1
rule-name: value2
rule-name: different-syntax-value shown-here

rule-name-variant: value3
rule-name-variant: value4
```

-->

## Python

<!--
The Python syntax for the style definitions.
Copy the same examples as the ones shown in the CSS above.

If the programmatic way of setting the property differs significantly from the CSS way, make note of that here.

```py
widget.styles.property_name = value1
widget.styles.property_name = value2
widget.styles.property_name = (different_syntax_value, shown_here)

widget.styles.property_name_variant = value3
widget.styles.property_name_variant = value4
```

-->
````

## File: docs/styles/align.md
````markdown
# Align

The `align` style aligns children within a container.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a> <a href="../../css_types/vertical">&lt;vertical&gt;</a>;

align-horizontal: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
align-vertical: <a href="../../css_types/vertical">&lt;vertical&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `align` style takes a [`<horizontal>`](../css_types/horizontal.md) followed by a [`<vertical>`](../css_types/vertical.md).

You can also set the alignment for each axis individually with `align-horizontal` and `align-vertical`.

## Examples

### Basic usage

This example contains a simple app with two labels centered on the screen with `align: center middle;`:

=== "Output"

    ```{.textual path="docs/examples/styles/align.py"}
    ```

=== "align.py"

    ```python
    --8<-- "docs/examples/styles/align.py"
    ```

=== "align.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/align.tcss"
    ```

### All alignments

The next example shows a 3 by 3 grid of containers with text labels.
Each label has been aligned differently inside its container, and its text shows its `align: ...` value.

=== "Output"

    ```{.textual path="docs/examples/styles/align_all.py"}
    ```

=== "align_all.py"

    ```python
    --8<-- "docs/examples/styles/align_all.py"
    ```

=== "align_all.tcss"

    ```css hl_lines="2 6 10 14 18 22 26 30 34"
    --8<-- "docs/examples/styles/align_all.tcss"
    ```

## CSS

```css
/* Align child widgets to the center. */
align: center middle;
/* Align child widget to the top right */
align: right top;

/* Change the horizontal alignment of the children of a widget */
align-horizontal: right;
/* Change the vertical alignment of the children of a widget */
align-vertical: middle;
```

## Python
```python
# Align child widgets to the center
widget.styles.align = ("center", "middle")
# Align child widgets to the top right
widget.styles.align = ("right", "top")

# Change the horizontal alignment of the children of a widget
widget.styles.align_horizontal = "right"
# Change the vertical alignment of the children of a widget
widget.styles.align_vertical = "middle"
```

## See also

 - [`content-align`](./content_align.md) to set the alignment of content inside a widget.
 - [`text-align`](./text_align.md) to set the alignment of text in a widget.
````

## File: docs/styles/background_tint.md
````markdown
# Background-tint

The `background-tint` style modifies the background color by tinting (blending) it with a new color.

This style is typically used to subtly change the background of a widget for emphasis.
For instance the following would make a focused widget have a slightly lighter background.

```css
MyWidget:focus {
    background-tint: white 10%
}
```

The background tint color should typically have less than 100% alpha, in order to modify the background color.
If the alpha component is 100% then the tint color will replace the background color entirely.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
background-tint: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `background-tint` style requires a [`<color>`](../css_types/color.md) optionally followed by [`<percentage>`](../css_types/percentage.md) to specify the color's opacity (clamped between `0%` and `100%`).

## Examples

### Basic usage

This example shows background tint applied with alpha from 0 to 100%.

=== "Output"

    ```{.textual path="docs/examples/styles/background_tint.py"}
    ```

=== "background_tint.py"

    ```python
    --8<-- "docs/examples/styles/background_tint.py"
    ```

=== "background.tcss"

    ```css hl_lines="5-9"
    --8<-- "docs/examples/styles/background_tint.tcss"
    ```


## CSS

```css
/* 10% backgrouhnd tint */
background-tint: blue 10%;


/* 20% RGB color */
background-tint: rgb(100, 120, 200, 0.2);

```

## Python

You can use the same syntax as CSS, or explicitly set a `Color` object for finer-grained control.

```python
# Set 20% blue background tint
widget.styles.background_tint = "blue 20%"

from textual.color import Color
# Set with a color object
widget.styles.background_tint = Color(120, 60, 100, 0.5)
```

## See also

 - [`background`](./background.md) to set the background color of a widget.
 - [`color`](./color.md) to set the color of text in a widget.
````

## File: docs/styles/background.md
````markdown
# Background

The `background` style sets the background color of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
background: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `background` style requires a [`<color>`](../css_types/color.md) optionally followed by [`<percentage>`](../css_types/percentage.md) to specify the color's opacity (clamped between `0%` and `100%`).

## Examples

### Basic usage

This example creates three widgets and applies a different background to each.

=== "Output"

    ```{.textual path="docs/examples/styles/background.py"}
    ```

=== "background.py"

    ```python
    --8<-- "docs/examples/styles/background.py"
    ```

=== "background.tcss"

    ```css hl_lines="9 13 17"
    --8<-- "docs/examples/styles/background.tcss"
    ```

### Different opacity settings

The next example creates ten widgets laid out side by side to show the effect of setting different percentages for the background color's opacity.

=== "Output"

    ```{.textual path="docs/examples/styles/background_transparency.py"}
    ```

=== "background_transparency.py"

    ```python
    --8<-- "docs/examples/styles/background_transparency.py"
    ```

=== "background_transparency.tcss"

    ```css hl_lines="2 6 10 14 18 22 26 30 34 38"
    --8<-- "docs/examples/styles/background_transparency.tcss"
    ```

## CSS

```css
/* Blue background */
background: blue;

/* 20% red background */
background: red 20%;

/* RGB color */
background: rgb(100, 120, 200);

/* HSL color */
background: hsl(290, 70%, 80%);
```

## Python

You can use the same syntax as CSS, or explicitly set a `Color` object for finer-grained control.

```python
# Set blue background
widget.styles.background = "blue"
# Set through HSL model
widget.styles.background = "hsl(351,32%,89%)"

from textual.color import Color
# Set with a color object by parsing a string
widget.styles.background = Color.parse("pink")
widget.styles.background = Color.parse("#FF00FF")
# Set with a color object instantiated directly
widget.styles.background = Color(120, 60, 100)
```

## See also

 - [`background-tint`](./background_tint.md) to blend a color with the background.
 - [`color`](./color.md) to set the color of text in a widget.
````

## File: docs/styles/border_subtitle_align.md
````markdown
# Border-subtitle-align

The `border-subtitle-align` style sets the horizontal alignment for the border subtitle.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-subtitle-align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `border-subtitle-align` style takes a [`<horizontal>`](../css_types/horizontal.md) that determines where the border subtitle is aligned along the top edge of the border.
This means that the border corners are always visible.

### Default

The default alignment is `right`.


## Examples

### Basic usage

This example shows three labels, each with a different border subtitle alignment:

=== "Output"

    ```{.textual path="docs/examples/styles/border_subtitle_align.py"}
    ```

=== "border_subtitle_align.py"

    ```py
    --8<-- "docs/examples/styles/border_subtitle_align.py"
    ```

=== "border_subtitle_align.tcss"

    ```css
    --8<-- "docs/examples/styles/border_subtitle_align.tcss"
    ```


### Complete usage reference

--8<-- "docs/snippets/border_sub_title_align_all_example.md"


## CSS

```css
border-subtitle-align: left;
border-subtitle-align: center;
border-subtitle-align: right;
```

## Python

```py
widget.styles.border_subtitle_align = "left"
widget.styles.border_subtitle_align = "center"
widget.styles.border_subtitle_align = "right"
```

## See also

--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/border_subtitle_background.md
````markdown
# Border-subtitle-background

The `border-subtitle-background` style sets the *background* color of the [border_subtitle][textual.widget.Widget.border_subtitle].

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-subtitle-background: (<a href="../../css_types/color">&lt;color&gt;</a> | auto) [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"



## Example

--8<-- "docs/snippets/border_title_color.md"



## CSS

```css
border-subtitle-background: blue;
```

## Python

```python
widget.styles.border_subtitle_background = "blue"
```


## See also

--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/border_subtitle_color.md
````markdown
# Border-subtitle-color

The `border-subtitle-color` style sets the color of the [border_subtitle][textual.widget.Widget.border_subtitle].

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-subtitle-color: (<a href="../../css_types/color">&lt;color&gt;</a> | auto) [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"


## Example

--8<-- "docs/snippets/border_title_color.md"



## CSS

```css
border-subtitle-color: red;
```

## Python

```python
widget.styles.border_subtitle_color = "red"
```


## See also

--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/border_subtitle_style.md
````markdown
# Border-subtitle-style

The `border-subtitle-style` style sets the text style of the [border_subtitle][textual.widget.Widget.border_subtitle].


## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-subtitle-style: <a href="../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"


## Example

--8<-- "docs/snippets/border_title_color.md"


## CSS

```css
border-subtitle-style: bold underline;
```

## Python

```python
widget.styles.border_subtitle_style = "bold underline"
```




## See also

--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/border_title_align.md
````markdown
# Border-title-align

The `border-title-align` style sets the horizontal alignment for the border title.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-title-align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `border-title-align` style takes a [`<horizontal>`](../css_types/horizontal.md) that determines where the border title is aligned along the top edge of the border.
This means that the border corners are always visible.

### Default

The default alignment is `left`.


## Examples

### Basic usage

This example shows three labels, each with a different border title alignment:

=== "Output"

    ```{.textual path="docs/examples/styles/border_title_align.py"}
    ```

=== "border_title_align.py"

    ```py
    --8<-- "docs/examples/styles/border_title_align.py"
    ```

=== "border_title_align.tcss"

    ```css
    --8<-- "docs/examples/styles/border_title_align.tcss"
    ```


### Complete usage reference

--8<-- "docs/snippets/border_sub_title_align_all_example.md"


## CSS

```css
border-title-align: left;
border-title-align: center;
border-title-align: right;
```

## Python

```py
widget.styles.border_title_align = "left"
widget.styles.border_title_align = "center"
widget.styles.border_title_align = "right"
```

## See also

--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/border_title_background.md
````markdown
# Border-title-background

The `border-title-background` style sets the *background* color of the [border_title][textual.widget.Widget.border_title].

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-title-background: (<a href="../../css_types/color">&lt;color&gt;</a> | auto) [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"



## Example

--8<-- "docs/snippets/border_title_color.md"


## CSS

```css
border-title-background: blue;
```

## Python

```python
widget.styles.border_title_background = "blue"
```


## See also

--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/border_title_color.md
````markdown
# Border-title-color

The `border-title-color` style sets the color of the [border_title][textual.widget.Widget.border_title].

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-title-color: (<a href="../../css_types/color">&lt;color&gt;</a> | auto) [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

## Example

--8<-- "docs/snippets/border_title_color.md"


## CSS

```css
border-title-color: red;
```

## Python

```python
widget.styles.border_title_color = "red"
```


## See also

--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/border_title_style.md
````markdown
# Border-title-style

The `border-title-style` style sets the text style of the [border_title][textual.widget.Widget.border_title].


## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border-title-style: <a href="../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"



## Example

--8<-- "docs/snippets/border_title_color.md"


## CSS

```css
border-title-style: bold underline;
```

## Python

```python
widget.styles.border_title_style = "bold underline"
```



## See also

--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/border.md
````markdown
# Border

The `border` style enables the drawing of a box around a widget.

A border style may also be applied to individual edges with `border-top`, `border-right`, `border-bottom`, and `border-left`.

!!! note

    [`border`](./border.md) and [`outline`](./outline.md) cannot coexist in the same edge of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
border: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>] [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];

border-top: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>] [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
border-right: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>]];
border-bottom: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>]];
border-left: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>]];
--8<-- "docs/snippets/syntax_block_end.md"

In CSS, the border is set with a [border style](./border.md) and a color. Both are optional. An optional percentage may be added to blend the border with the background color.

In Python, the border is set with a tuple of [border style](./border.md) and a color.


## Border command

The `textual` CLI has a subcommand which will let you explore the various border types interactively:

```
textual borders
```

Alternatively, you can see the examples below.

## Examples

### Basic usage

This examples shows three widgets with different border styles.

=== "Output"

    ```{.textual path="docs/examples/styles/border.py"}
    ```

=== "border.py"

    ```python
    --8<-- "docs/examples/styles/border.py"
    ```

=== "border.tcss"

    ```css hl_lines="4 10 16"
    --8<-- "docs/examples/styles/border.tcss"
    ```

### All border types

The next example shows a grid with all the available border types.

=== "Output"

    ```{.textual path="docs/examples/styles/border_all.py"}
    ```

=== "border_all.py"

    ```py
    --8<-- "docs/examples/styles/border_all.py"
    ```

=== "border_all.tcss"

    ```css
    --8<-- "docs/examples/styles/border_all.tcss"
    ```

### Borders and outlines

--8<-- "docs/snippets/border_vs_outline_example.md"

## CSS

```css
/* Set a heavy white border */
border: heavy white;

/* Set a red border on the left */
border-left: outer red;

/* Set a rounded orange border, 50% opacity. */
border: round orange 50%;
```

## Python

```python
# Set a heavy white border
widget.styles.border = ("heavy", "white")

# Set a red border on the left
widget.styles.border_left = ("outer", "red")
```

## See also

 - [`box-sizing`](./box_sizing.md) to specify how to account for the border in a widget's dimensions.
 - [`outline`](./outline.md) to add an outline around the content of a widget.
--8<-- "docs/snippets/see_also_border.md"
````

## File: docs/styles/box_sizing.md
````markdown
# Box-sizing

The `box-sizing` style determines how the width and height of a widget are calculated.

## Syntax

```
box-sizing: border-box | content-box;
```

### Values

| Value                  | Description                                                                                                                                                             |
|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `border-box` (default) | Padding and border are included in the width and height. If you add padding and/or border the widget will not change in size, but you will have less space for content. |
| `content-box`          | Padding and border will increase the size of the widget, leaving the content area unaffected.                                                                           |

## Example

Both widgets in this example have the same height (5).
The top widget has `box-sizing: border-box` which means that padding and border reduce the space for content.
The bottom widget has `box-sizing: content-box` which increases the size of the widget to compensate for padding and border.

=== "Output"

    ```{.textual path="docs/examples/styles/box_sizing.py"}
    ```

=== "box_sizing.py"

    ```python
    --8<-- "docs/examples/styles/box_sizing.py"
    ```

=== "box_sizing.tcss"

    ```css hl_lines="2 6"
    --8<-- "docs/examples/styles/box_sizing.tcss"
    ```

## CSS

```css
/* Set box sizing to border-box (default) */
box-sizing: border-box;

/* Set box sizing to content-box */
box-sizing: content-box;
```

## Python

```python
# Set box sizing to border-box (default)
widget.box_sizing = "border-box"

# Set box sizing to content-box
widget.box_sizing = "content-box"
```

## See also

 - [`border`](./border.md) to add a border around a widget.
 - [`padding`](./padding.md) to add spacing around the content of a widget.
````

## File: docs/styles/color.md
````markdown
# Color

The `color` style sets the text color of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
color: (<a href="../../css_types/color">&lt;color&gt;</a> | auto) [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The `color` style requires a [`<color>`](../css_types/color.md) followed by an optional [`<percentage>`](../css_types/percentage.md) to specify the color's opacity.

You can also use the special value of `"auto"` in place of a color. This tells Textual to automatically select either white or black text for best contrast against the background.

## Examples

### Basic usage

This example sets a different text color for each of three different widgets.

=== "Output"

    ```{.textual path="docs/examples/styles/color.py"}
    ```

=== "color.py"

    ```python
    --8<-- "docs/examples/styles/color.py"
    ```

=== "color.tcss"

    ```css hl_lines="8 12 16"
    --8<-- "docs/examples/styles/color.tcss"
    ```

### Auto

The next example shows how `auto` chooses between a lighter or a darker text color to increase the contrast and improve readability.

=== "Output"

    ```{.textual path="docs/examples/styles/color_auto.py"}
    ```

=== "color_auto.py"

    ```py
    --8<-- "docs/examples/styles/color_auto.py"
    ```

=== "color_auto.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/color_auto.tcss"
    ```

## CSS

```css
/* Blue text */
color: blue;

/* 20% red text */
color: red 20%;

/* RGB color */
color: rgb(100, 120, 200);

/* Automatically choose color with suitable contrast for readability */
color: auto;
```

## Python

You can use the same syntax as CSS, or explicitly set a `Color` object.

```python
# Set blue text
widget.styles.color = "blue"

from textual.color import Color
# Set with a color object
widget.styles.color = Color.parse("pink")
```

## See also

 - [`background`](./background.md) to set the background color in a widget.
````

## File: docs/styles/content_align.md
````markdown
# Content-align

The `content-align` style aligns content _inside_ a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
content-align: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a> <a href="../../css_types/vertical">&lt;vertical&gt;</a>;

content-align-horizontal: <a href="../../css_types/horizontal">&lt;horizontal&gt;</a>;
content-align-vertical: <a href="../../css_types/vertical">&lt;vertical&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `content-align` style takes a [`<horizontal>`](../css_types/horizontal.md) followed by a [`<vertical>`](../css_types/vertical.md).

You can specify the alignment of content on both the horizontal and vertical axes at the same time,
or on each of the axis separately.
To specify content alignment on a single axis, use the respective style and type:

 - `content-align-horizontal` takes a [`<horizontal>`](../css_types/horizontal.md) and does alignment along the horizontal axis; and
 - `content-align-vertical` takes a [`<vertical>`](../css_types/vertical.md) and does alignment along the vertical axis.

## Examples

### Basic usage

This first example shows three labels stacked vertically, each with different content alignments.

=== "Output"

    ```{.textual path="docs/examples/styles/content_align.py"}
    ```

=== "content_align.py"

    ```python
    --8<-- "docs/examples/styles/content_align.py"
    ```

=== "content_align.tcss"

    ```css hl_lines="2 7-8 13"
    --8<-- "docs/examples/styles/content_align.tcss"
    ```

### All content alignments

The next example shows a 3 by 3 grid of labels.
Each label has its text aligned differently.

=== "Output"

    ```{.textual path="docs/examples/styles/content_align_all.py"}
    ```

=== "content_align_all.py"

    ```py
    --8<-- "docs/examples/styles/content_align_all.py"
    ```

=== "content_align_all.tcss"

    ```css hl_lines="2 5 8 11 14 17 20 23 26"
    --8<-- "docs/examples/styles/content_align_all.tcss"
    ```

## CSS

```css
/* Align content in the very center of a widget */
content-align: center middle;
/* Align content at the top right of a widget */
content-align: right top;

/* Change the horizontal alignment of the content of a widget */
content-align-horizontal: right;
/* Change the vertical alignment of the content of a widget */
content-align-vertical: middle;
```

## Python
```python
# Align content in the very center of a widget
widget.styles.content_align = ("center", "middle")
# Align content at the top right of a widget
widget.styles.content_align = ("right", "top")

# Change the horizontal alignment of the content of a widget
widget.styles.content_align_horizontal = "right"
# Change the vertical alignment of the content of a widget
widget.styles.content_align_vertical = "middle"
```

## See also

 - [`align`](./align.md) to set the alignment of children widgets inside a container.
 - [`text-align`](./text_align.md) to set the alignment of text in a widget.
````

## File: docs/styles/display.md
````markdown
# Display

The `display` style defines whether a widget is displayed or not.

## Syntax

```
display: block | none;
```

### Values

| Value             | Description                                                              |
|-------------------|--------------------------------------------------------------------------|
| `block` (default) | Display the widget as normal.                                            |
| `none`            | The widget is not displayed and space will no longer be reserved for it. |

## Example

Note that the second widget is hidden by adding the `"remove"` class which sets the display style to `none`.

=== "Output"

    ```{.textual path="docs/examples/styles/display.py"}
    ```

=== "display.py"

    ```python
    --8<-- "docs/examples/styles/display.py"
    ```

=== "display.tcss"

    ```css hl_lines="13"
    --8<-- "docs/examples/styles/display.tcss"
    ```

## CSS

```css
/* Widget is shown */
display: block;

/* Widget is not shown */
display: none;
```

## Python

```python
# Hide the widget
self.styles.display = "none"

# Show the widget again
self.styles.display = "block"
```

There is also a shortcut to show / hide a widget. The `display` property on `Widget` may be set to `True` or `False` to show or hide the widget.

```python
# Hide the widget
widget.display = False

# Show the widget
widget.display = True
```

## See also

 - [`visibility`](./visibility.md) to specify whether a widget is visible or not.
````

## File: docs/styles/dock.md
````markdown
# Dock

The `dock` style is used to fix a widget to the edge of a container (which may be the entire terminal window).

## Syntax

```
dock: bottom | left | right | top;
```

The option chosen determines the edge to which the widget is docked.

## Examples

### Basic usage

The example below shows a `left` docked sidebar.
Notice that even though the content is scrolled, the sidebar remains fixed.

=== "Output"

    ```{.textual path="docs/examples/guide/layout/dock_layout1_sidebar.py" press="pagedown,down,down"}
    ```

=== "dock_layout1_sidebar.py"

    ```python
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.py"
    ```

=== "dock_layout1_sidebar.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/guide/layout/dock_layout1_sidebar.tcss"
    ```

### Advanced usage

The second example shows how one can use full-width or full-height containers to dock labels to the edges of a larger container.
The labels will remain in that position (docked) even if the container they are in scrolls horizontally and/or vertically.

=== "Output"

    ```{.textual path="docs/examples/styles/dock_all.py"}
    ```

=== "dock_all.py"

    ```py
    --8<-- "docs/examples/styles/dock_all.py"
    ```

=== "dock_all.tcss"

    ```css hl_lines="2-5 8-11 14-17 20-23"
    --8<-- "docs/examples/styles/dock_all.tcss"
    ```

## CSS

```css
dock: bottom;  /* Docks on the bottom edge of the parent container. */
dock: left;    /* Docks on the   left edge of the parent container. */
dock: right;   /* Docks on the  right edge of the parent container. */
dock: top;     /* Docks on the    top edge of the parent container. */
```

## Python

```python
widget.styles.dock = "bottom"  # Dock bottom.
widget.styles.dock = "left"    # Dock   left.
widget.styles.dock = "right"   # Dock  right.
widget.styles.dock = "top"     # Dock    top.
```

## See also

 - The [layout guide](../guide/layout.md#docking) section on docking.
````

## File: docs/styles/hatch.md
````markdown
# Hatch

The `hatch` style fills a widget's background with a repeating character for a pleasing textured effect.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
hatch: (<a href="../../css_types/hatch">&lt;hatch&gt;</a> | CHARACTER) <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>]
--8<-- "docs/snippets/syntax_block_end.md"

The hatch type can be specified with a constant, or a string. For example, `cross` for cross hatch, or `"T"` for a custom character.

The color can be any Textual color value.

An optional percentage can be used to set the opacity.

## Examples


An app to show a few hatch effects.

=== "Output"

    ```{.textual path="docs/examples/styles/hatch.py"}
    ```

=== "hatch.py"

    ```py
    --8<-- "docs/examples/styles/hatch.py"
    ```

=== "hatch.tcss"

    ```css
    --8<-- "docs/examples/styles/hatch.tcss"
    ```


## CSS

```css
/* Red cross hatch */
hatch: cross red;
/* Right diagonals, 50% transparent green. */
hatch: right green 50%;
/* T custom character in 80% blue. **/
hatch: "T" blue 80%;
```


## Python

```py
widget.styles.hatch = ("cross", "red")
widget.styles.hatch = ("right", "rgba(0,255,0,128)")
widget.styles.hatch = ("T", "blue")
```
````

## File: docs/styles/height.md
````markdown
# Height

The `height` style sets a widget's height.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
height: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `height` style needs a [`<scalar>`](../css_types/scalar.md) to determine the vertical length of the widget.
By default, it sets the height of the content area, but if [`box-sizing`](./box_sizing.md) is set to `border-box` it sets the height of the border area.

## Examples

### Basic usage

This examples creates a widget with a height of 50% of the screen.

=== "Output"

    ```{.textual path="docs/examples/styles/height.py"}
    ```

=== "height.py"

    ```python
    --8<-- "docs/examples/styles/height.py"
    ```

=== "height.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/height.tcss"
    ```

### All height formats

The next example creates a series of wide widgets with heights set with different units.
Open the CSS file tab to see the comments that explain how each height is computed.
(The output includes a vertical ruler on the right to make it easier to check the height of each widget.)

=== "Output"

    ```{.textual path="docs/examples/styles/height_comparison.py" lines=24 columns=80}
    ```

=== "height_comparison.py"

    ```py hl_lines="17-25"
    --8<-- "docs/examples/styles/height_comparison.py"
    ```

    1. The id of the placeholder identifies which unit will be used to set the height of the widget.

=== "height_comparison.tcss"

    ```css hl_lines="2 5 8 11 14 17 20 23 26"
    --8<-- "docs/examples/styles/height_comparison.tcss"
    ```

    1. This sets the height to 2 lines.
    2. This sets the height to 12.5% of the space made available by the container. The container is 24 lines tall, so 12.5% of 24 is 3.
    3. This sets the height to 5% of the width of the direct container, which is the `VerticalScroll` container. Because it expands to fit all of the terminal, the width of the `VerticalScroll` is 80 and 5% of 80 is 4.
    4. This sets the height to 12.5% of the height of the direct container, which is the `VerticalScroll` container. Because it expands to fit all of the terminal, the height of the `VerticalScroll` is 24 and 12.5% of 24 is 3.
    5. This sets the height to 6.25% of the viewport width, which is 80. 6.25% of 80 is 5.
    6. This sets the height to 12.5% of the viewport height, which is 24. 12.5% of 24 is 3.
    7. This sets the height of the placeholder to be the optimal size that fits the content without scrolling.
    Because the content only spans one line, the placeholder has its height set to 1.
    8. This sets the height to `1fr`, which means this placeholder will have half the height of a placeholder with `2fr`.
    9. This sets the height to `2fr`, which means this placeholder will have twice the height of a placeholder with `1fr`.


## CSS

```css
/* Explicit cell height */
height: 10;

/* Percentage height */
height: 50%;

/* Automatic height */
height: auto
```

## Python

```python
self.styles.height = 10  # Explicit cell height can be an int
self.styles.height = "50%"
self.styles.height = "auto"
```

## See also

 - [`max-height`](./max_height.md) and [`min-height`](./min_height.md) to limit the height of a widget.
 - [`width`](./width.md) to set the width of a widget.
````

## File: docs/styles/index.md
````markdown
# Styles

A reference to Widget [styles](../guide/styles.md).

See the links to the left of the page, or in the hamburger menu (three horizontal bars, top left).
````

## File: docs/styles/keyline.md
````markdown
# Keyline

The `keyline` style is applied to a container and will draw lines around child widgets.

A keyline is superficially like the [border](./border.md) rule, but rather than draw inside the widget, a keyline is drawn outside of the widget's border. Additionally, unlike `border`, keylines can overlap and cross to create dividing lines between widgets.

Because keylines are drawn in the widget's margin, you will need to apply the [margin](./margin.md) or [grid-gutter](./grid/grid_gutter.md) rule to see the effect.


## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
keyline: [<a href="../../css_types/keyline">&lt;keyline&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"


## Examples

### Horizontal Keyline

The following examples shows a simple horizontal layout with a thin keyline.

=== "Output"

    ```{.textual path="docs/examples/styles/keyline_horizontal.py"}
    ```

=== "keyline.py"

    ```python
    --8<-- "docs/examples/styles/keyline_horizontal.py"
    ```

=== "keyline.tcss"

    ```css
    --8<-- "docs/examples/styles/keyline_horizontal.tcss"
    ```



### Grid keyline

The following examples shows a grid layout with a *heavy* keyline.

=== "Output"

    ```{.textual path="docs/examples/styles/keyline.py"}
    ```

=== "keyline.py"

    ```python
    --8<-- "docs/examples/styles/keyline.py"
    ```

=== "keyline.tcss"

    ```css 
    --8<-- "docs/examples/styles/keyline.tcss"
    ```


## CSS

```css
/* Set a thin green keyline */
/* Note: Must be set on a container or a widget with a layout. */
keyline: thin green;
```

## Python

You can set a keyline in Python with a tuple of type and color:

```python
widget.styles.keyline = ("thin", "green")
```


## See also

 - [`border`](./border.md) to add a border around a widget.
````

## File: docs/styles/layer.md
````markdown
# Layer

The `layer` style defines the layer a widget belongs to.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
layer: <a href="../../css_types/name">&lt;name&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `layer` style accepts a [`<name>`](../css_types/name.md) that defines the layer this widget belongs to.
This [`<name>`](../css_types/name.md) must correspond to a [`<name>`](../css_types/name.md) that has been defined in a [`layers`](./layers.md) style by an ancestor of this widget.

More information on layers can be found in the [guide](../guide/layout.md#layers).

!!! warning

    Using a `<name>` that hasn't been defined in a [`layers`](./layers.md) declaration of an ancestor of this widget has no effect.

## Example

In the example below, `#box1` is yielded before `#box2`.
However, since `#box1` is on the higher layer, it is drawn on top of `#box2`.

[//]: # (NOTE: the example below also appears in the guide and 'layers.md'.)

=== "Output"

    ```{.textual path="docs/examples/guide/layout/layers.py"}
    ```

=== "layers.py"

    ```python
    --8<-- "docs/examples/guide/layout/layers.py"
    ```

=== "layers.tcss"

    ```css hl_lines="3 14 19"
    --8<-- "docs/examples/guide/layout/layers.tcss"
    ```

## CSS

```css
/* Draw the widget on the layer called 'below' */
layer: below;
```

## Python

```python
# Draw the widget on the layer called 'below'
widget.styles.layer = "below"
```

## See also

 - The [layout guide](../guide/layout.md#layers) section on layers.
 - [`layers`](./layers.md) to define an ordered set of layers.
````

## File: docs/styles/layers.md
````markdown
# Layers

The `layers` style allows you to define an ordered set of layers.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
layers: <a href="../../css_types/name">&lt;name&gt;</a>+;
--8<-- "docs/snippets/syntax_block_end.md"

The `layers` style accepts one or more [`<name>`](../css_types/name.md) that define the layers that the widget is aware of, and the order in which they will be painted on the screen.

The values used here can later be referenced using the [`layer`](./layer.md) property.
The layers defined first in the list are drawn under the layers that are defined later in the list.

More information on layers can be found in the [guide](../guide/layout.md#layers).

## Example

In the example below, `#box1` is yielded before `#box2`.
However, since `#box1` is on the higher layer, it is drawn on top of `#box2`.

[//]: # (NOTE: the example below also appears in the guide and 'layer.md'.)

=== "Output"

    ```{.textual path="docs/examples/guide/layout/layers.py"}
    ```

=== "layers.py"

    ```python
    --8<-- "docs/examples/guide/layout/layers.py"
    ```

=== "layers.tcss"

    ```css hl_lines="3 14 19"
    --8<-- "docs/examples/guide/layout/layers.tcss"
    ```

## CSS

```css
/* Bottom layer is called 'below', layer above it is called 'above' */
layers: below above;
```

## Python

```python
# Bottom layer is called 'below', layer above it is called 'above'
widget.style.layers = ("below", "above")
```

## See also

 - The [layout guide](../guide/layout.md#layers) section on layers.
 - [`layer`](./layer.md) to set the layer a widget belongs to.
````

## File: docs/styles/layout.md
````markdown
# Layout

The `layout` style defines how a widget arranges its children.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
layout: grid | horizontal | vertical;
--8<-- "docs/snippets/syntax_block_end.md"

The `layout` style takes an option that defines how child widgets will be arranged, as per the table shown below.

### Values

| Value                | Description                                                                   |
| -------------------- | ----------------------------------------------------------------------------- |
| `grid`               | Child widgets will be arranged in a grid.                                     |
| `horizontal`         | Child widgets will be arranged along the horizontal axis, from left to right. |
| `vertical` (default) | Child widgets will be arranged along the vertical axis, from top to bottom.   |

See the [layout](../guide/layout.md) guide for more information.

## Example

Note how the `layout` style affects the arrangement of widgets in the example below.
To learn more about the grid layout, you can see the [layout guide](../guide/layout.md) or the [grid reference](./grid/index.md).

=== "Output"

    ```{.textual path="docs/examples/styles/layout.py"}
    ```

=== "layout.py"

    ```python
    --8<-- "docs/examples/styles/layout.py"
    ```

=== "layout.tcss"

    ```css hl_lines="2 8"
    --8<-- "docs/examples/styles/layout.tcss"
    ```

## CSS

```css
layout: horizontal;
```

## Python

```python
widget.styles.layout = "horizontal"
```

## See also

 - [Layout guide](../guide/layout.md).
 - [Grid reference](./grid/index.md).
````

## File: docs/styles/margin.md
````markdown
# Margin

The `margin` style specifies spacing around a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
margin: <a href="../../css_types/integer">&lt;integer&gt;</a>
      # one value for all edges
      | <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>
      # top/bot   left/right
      | <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>;
      # top       right     bot       left

margin-top: <a href="../../css_types/integer">&lt;integer&gt;</a>;
margin-right: <a href="../../css_types/integer">&lt;integer&gt;</a>;
margin-bottom: <a href="../../css_types/integer">&lt;integer&gt;</a>;
margin-left: <a href="../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `margin` specifies spacing around the four edges of the widget equal to the [`<integer>`](../css_types/integer.md) specified.
The number of values given defines what edges get what margin:

 - 1 [`<integer>`](../css_types/integer.md) sets the same margin for the four edges of the widget;
 - 2 [`<integer>`](../css_types/integer.md) set margin for top/bottom and left/right edges, respectively.
 - 4 [`<integer>`](../css_types/integer.md) set margin for the top, right, bottom, and left edges, respectively.

!!! tip

    To remember the order of the edges affected by the rule `margin` when it has 4 values, think of a clock.
    Its hand starts at the top and the goes clockwise: top, right, bottom, left.

Alternatively, margin can be set for each edge individually through the styles `margin-top`, `margin-right`, `margin-bottom`, and `margin-left`, respectively.

## Examples

### Basic usage

In the example below we add a large margin to a label, which makes it move away from the top-left corner of the screen.

=== "Output"

    ```{.textual path="docs/examples/styles/margin.py"}
    ```

=== "margin.py"

    ```python
    --8<-- "docs/examples/styles/margin.py"
    ```

=== "margin.tcss"

    ```css hl_lines="7"
    --8<-- "docs/examples/styles/margin.tcss"
    ```

### All margin settings

The next example shows a grid.
In each cell, we have a placeholder that has its margins set in different ways.

=== "Output"

    ```{.textual path="docs/examples/styles/margin_all.py"}
    ```

=== "margin_all.py"

    ```py
    --8<-- "docs/examples/styles/margin_all.py"
    ```

=== "margin_all.tcss"

    ```css hl_lines="25 29 33 37 41 45 49 53"
    --8<-- "docs/examples/styles/margin_all.tcss"
    ```

## CSS

```css
/* Set margin of 1 around all edges */
margin: 1;
/* Set margin of 2 on the top and bottom edges, and 4 on the left and right */
margin: 2 4;
/* Set margin of 1 on the top, 2 on the right,
                 3 on the bottom, and 4 on the left */
margin: 1 2 3 4;

margin-top: 1;
margin-right: 2;
margin-bottom: 3;
margin-left: 4;
```

## Python

Python does not provide the properties `margin-top`, `margin-right`, `margin-bottom`, and `margin-left`.
However, you _can_ set the margin to a single integer, a tuple of 2 integers, or a tuple of 4 integers:

```python
# Set margin of 1 around all edges
widget.styles.margin = 1
# Set margin of 2 on the top and bottom edges, and 4 on the left and right
widget.styles.margin = (2, 4)
# Set margin of 1 on top, 2 on the right, 3 on the bottom, and 4 on the left
widget.styles.margin = (1, 2, 3, 4)
```

## See also

 - [`padding`](./padding.md) to add spacing around the content of a widget.
````

## File: docs/styles/max_height.md
````markdown
# Max-height

The `max-height` style sets a maximum height for a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
max-height: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `max-height` style accepts a [`<scalar>`](../css_types/scalar.md) that defines an upper bound for the [`height`](./height.md) of a widget.
That is, the height of a widget is never allowed to exceed `max-height`.

## Example

The example below shows some placeholders that were defined to span vertically from the top edge of the terminal to the bottom edge.
Then, we set `max-height` individually on each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/max_height.py"}
    ```

=== "max_height.py"

    ```py
    --8<-- "docs/examples/styles/max_height.py"
    ```

=== "max_height.tcss"

    ```css hl_lines="12 16 20 24"
    --8<-- "docs/examples/styles/max_height.tcss"
    ```

    1. This won't affect the placeholder because its height is less than the maximum height.

## CSS

```css
/* Set the maximum height to 10 rows */
max-height: 10;

/* Set the maximum height to 25% of the viewport height */
max-height: 25vh;
```

## Python

```python
# Set the maximum height to 10 rows
widget.styles.max_height = 10

# Set the maximum height to 25% of the viewport height
widget.styles.max_height = "25vh"
```

## See also

 - [`min-height`](./min_height.md) to set a lower bound on the height of a widget.
 - [`height`](./height.md) to set the height of a widget.
````

## File: docs/styles/max_width.md
````markdown
# Max-width

The `max-width` style sets a maximum width for a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
max-width: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `max-width` style accepts a [`<scalar>`](../css_types/scalar.md) that defines an upper bound for the [`width`](./width.md) of a widget.
That is, the width of a widget is never allowed to exceed `max-width`.

## Example

The example below shows some placeholders that were defined to span horizontally from the left edge of the terminal to the right edge.
Then, we set `max-width` individually on each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/max_width.py"}
    ```

=== "max_width.py"

    ```py
    --8<-- "docs/examples/styles/max_width.py"
    ```

=== "max_width.tcss"

    ```css hl_lines="12 16 20 24"
    --8<-- "docs/examples/styles/max_width.tcss"
    ```

    1. This won't affect the placeholder because its width is less than the maximum width.

## CSS

```css
/* Set the maximum width to 10 rows */
max-width: 10;

/* Set the maximum width to 25% of the viewport width */
max-width: 25vw;
```

## Python

```python
# Set the maximum width to 10 rows
widget.styles.max_width = 10

# Set the maximum width to 25% of the viewport width
widget.styles.max_width = "25vw"
```

## See also

 - [`min-width`](./min_width.md) to set a lower bound on the width of a widget.
 - [`width`](./width.md) to set the width of a widget.
````

## File: docs/styles/min_height.md
````markdown
# Min-height

The `min-height` style sets a minimum height for a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
min-height: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `min-height` style accepts a [`<scalar>`](../css_types/scalar.md) that defines a lower bound for the [`height`](./height.md) of a widget.
That is, the height of a widget is never allowed to be under `min-height`.

## Example

The example below shows some placeholders with their height set to `50%`.
Then, we set `min-height` individually on each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/min_height.py"}
    ```

=== "min_height.py"

    ```py
    --8<-- "docs/examples/styles/min_height.py"
    ```

=== "min_height.tcss"

    ```css hl_lines="13 17 21 25"
    --8<-- "docs/examples/styles/min_height.tcss"
    ```

    1. This won't affect the placeholder because its height is larger than the minimum height.

## CSS

```css
/* Set the minimum height to 10 rows */
min-height: 10;

/* Set the minimum height to 25% of the viewport height */
min-height: 25vh;
```

## Python

```python
# Set the minimum height to 10 rows
widget.styles.min_height = 10

# Set the minimum height to 25% of the viewport height
widget.styles.min_height = "25vh"
```

## See also

 - [`max-height`](./max_height.md) to set an upper bound on the height of a widget.
 - [`height`](./height.md) to set the height of a widget.
````

## File: docs/styles/min_width.md
````markdown
# Min-width

The `min-width` style sets a minimum width for a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
min-width: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `min-width` style accepts a [`<scalar>`](../css_types/scalar.md) that defines a lower bound for the [`width`](./width.md) of a widget.
That is, the width of a widget is never allowed to be under `min-width`.

## Example

The example below shows some placeholders with their width set to `50%`.
Then, we set `min-width` individually on each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/min_width.py"}
    ```

=== "min_width.py"

    ```py
    --8<-- "docs/examples/styles/min_width.py"
    ```

=== "min_width.tcss"

    ```css hl_lines="13 17 21 25"
    --8<-- "docs/examples/styles/min_width.tcss"
    ```

    1. This won't affect the placeholder because its width is larger than the minimum width.

## CSS

```css
/* Set the minimum width to 10 rows */
min-width: 10;

/* Set the minimum width to 25% of the viewport width */
min-width: 25vw;
```

## Python

```python
# Set the minimum width to 10 rows
widget.styles.min_width = 10

# Set the minimum width to 25% of the viewport width
widget.styles.min_width = "25vw"
```

## See also

 - [`max-width`](./max_width.md) to set an upper bound on the width of a widget.
 - [`width`](./width.md) to set the width of a widget.
````

## File: docs/styles/offset.md
````markdown
# Offset

The `offset` style defines an offset for the position of the widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
offset: <a href="../../css_types/scalar">&lt;scalar&gt;</a> <a href="../../css_types/scalar">&lt;scalar&gt;</a>;

offset-x: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
offset-y: <a href="../../css_types/scalar">&lt;scalar&gt;</a>
--8<-- "docs/snippets/syntax_block_end.md"

The two [`<scalar>`](../css_types/scalar.md) in the `offset` define, respectively, the offsets in the horizontal and vertical axes for the widget.

To specify an offset along a single axis, you can use `offset-x` and `offset-y`.

## Example

In this example, we have 3 widgets with differing offsets.

=== "Output"

    ```{.textual path="docs/examples/styles/offset.py"}
    ```

=== "offset.py"

    ```python
    --8<-- "docs/examples/styles/offset.py"
    ```

=== "offset.tcss"

    ```css hl_lines="13 20 27"
    --8<-- "docs/examples/styles/offset.tcss"
    ```

## CSS

```css
/* Move the widget 8 cells in the x direction and 2 in the y direction */
offset: 8 2;

/* Move the widget 4 cells in the x direction
offset-x: 4;
/* Move the widget -3 cells in the y direction
offset-y: -3;
```

## Python

You cannot change programmatically the offset for a single axis.
You have to set the two axes at the same time.

```python
# Move the widget 2 cells in the x direction, and 4 in the y direction.
widget.styles.offset = (2, 4)
```

## See also

 - The [layout guide](../guide/layout.md#offsets) section on offsets.
````

## File: docs/styles/opacity.md
````markdown
# Opacity

The `opacity` style sets the opacity of a widget.

While terminals are not capable of true opacity, Textual can create an approximation by blending widgets with their background color.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
opacity: <a href="../../css_types/number">&lt;number&gt;</a> | <a href="../../css_types/percentage">&lt;percentage&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The opacity of a widget can be set as a [`<number>`](../css_types/number.md) or a [`<percentage>`](../css_types/percentage.md).
If given as a number, then `opacity` should be a value between 0 and 1, where 0 is the background color and 1 is fully opaque.
If given as a percentage, 0% is the background color and 100% is fully opaque.

Typically, if you set this value it would be somewhere between the two extremes.
For instance, setting the opacity of a widget to `70%` will make it appear dimmer than surrounding widgets, which could be used to display a *disabled* state.


## Example

This example shows, from top to bottom, increasing opacity values for a label with a border and some text.
When the opacity is zero, all we see is the (black) background.

=== "Output"

    ```{.textual path="docs/examples/styles/opacity.py"}
    ```

=== "opacity.py"

    ```python
    --8<-- "docs/examples/styles/opacity.py"
    ```

=== "opacity.tcss"

    ```css hl_lines="2 6 10 14 18"
    --8<-- "docs/examples/styles/opacity.tcss"
    ```

## CSS

```css
/* Fade the widget to 50% against its parent's background */
opacity: 50%;
```

## Python

```python
# Fade the widget to 50% against its parent's background
widget.styles.opacity = "50%"
```

## See also

 - [`text-opacity`](./text_opacity.md) to blend the color of a widget's content with its background color.
````

## File: docs/styles/outline.md
````markdown
# Outline

The `outline` style enables the drawing of a box around the content of a widget, which means the outline is drawn _over_ the content area.

!!! note

    [`border`](./border.md) and [`outline`](./outline.md) cannot coexist in the same edge of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
outline: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];

outline-top: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
outline-right: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
outline-bottom: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
outline-left: [<a href="../../css_types/border">&lt;border&gt;</a>] [<a href="../../css_types/color">&lt;color&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The style `outline` accepts an optional [`<border>`](../css_types/border.md) that sets the visual style of the widget outline and an optional [`<color>`](../css_types/color.md) to set the color of the outline.

Unlike the style [`border`](./border.md), the frame of the outline is drawn over the content area of the widget.
This rule can be useful to add temporary emphasis on the content of a widget, if you want to draw the user's attention to it.

## Border command

The `textual` CLI has a subcommand which will let you explore the various border types interactively, when applied to the CSS rule [`border`](../styles/border.md):

```
textual borders
```

## Examples

### Basic usage

This example shows a widget with an outline.
Note how the outline occludes the text area.

=== "Output"

    ```{.textual path="docs/examples/styles/outline.py"}
    ```

=== "outline.py"

    ```python
    --8<-- "docs/examples/styles/outline.py"
    ```

=== "outline.tcss"

    ```css hl_lines="8"
    --8<-- "docs/examples/styles/outline.tcss"
    ```

### All outline types

The next example shows a grid with all the available outline types.

=== "Output"

    ```{.textual path="docs/examples/styles/outline_all.py"}
    ```

=== "outline_all.py"

    ```py
    --8<-- "docs/examples/styles/outline_all.py"
    ```

=== "outline_all.tcss"

    ```css hl_lines="2 6 10 14 18 22 26 30 34 38 42 46 50 54 58"
    --8<-- "docs/examples/styles/outline_all.tcss"
    ```

### Borders and outlines

--8<-- "docs/snippets/border_vs_outline_example.md"

## CSS

```css
/* Set a heavy white outline */
outline:heavy white;

/* set a red outline on the left */
outline-left:outer red;
```

## Python

```python
# Set a heavy white outline
widget.outline = ("heavy", "white")

# Set a red outline on the left
widget.outline_left = ("outer", "red")
```

## See also

 - [`border`](./border.md) to add a border around a widget.
````

## File: docs/styles/overflow.md
````markdown
# Overflow

The `overflow` style specifies if and when scrollbars should be displayed.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
overflow: <a href="../../css_types/overflow">&lt;overflow&gt;</a> <a href="../../css_types/overflow">&lt;overflow&gt;</a>;

overflow-x: <a href="../../css_types/overflow">&lt;overflow&gt;</a>;
overflow-y: <a href="../../css_types/overflow">&lt;overflow&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The style `overflow` accepts two values that determine when to display scrollbars in a container widget.
The two values set the overflow for the horizontal and vertical axes, respectively.

Overflow may also be set individually for each axis:

 - `overflow-x` sets the overflow for the horizontal axis; and
 - `overflow-y` sets the overflow for the vertical axis.

### Defaults

The default setting for containers is `overflow: auto auto`.

!!! warning

    Some built-in containers like `Horizontal` and `VerticalScroll` override these defaults.

## Example

Here we split the screen into left and right sections, each with three vertically scrolling widgets that do not fit into the height of the terminal.

The left side has `overflow-y: auto` (the default) and will automatically show a scrollbar.
The right side has `overflow-y: hidden` which will prevent a scrollbar from being shown.

=== "Output"

    ```{.textual path="docs/examples/styles/overflow.py"}
    ```

=== "overflow.py"

    ```python
    --8<-- "docs/examples/styles/overflow.py"
    ```

=== "overflow.tcss"

    ```css hl_lines="19"
    --8<-- "docs/examples/styles/overflow.tcss"
    ```

## CSS

```css
/* Automatic scrollbars on both axes (the default) */
overflow: auto auto;

/* Hide the vertical scrollbar */
overflow-y: hidden;

/* Always show the horizontal scrollbar */
overflow-x: scroll;
```

## Python

Overflow cannot be programmatically set for both axes at the same time.

```python
# Hide the vertical scrollbar
widget.styles.overflow_y = "hidden"

# Always show the horizontal scrollbar
widget.styles.overflow_x = "scroll"
```
````

## File: docs/styles/padding.md
````markdown
# Padding

The `padding` style specifies spacing around the content of a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
padding: <a href="../../css_types/integer">&lt;integer&gt;</a> # one value for all edges
       | <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>
       # top/bot   left/right
       | <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>;
       # top       right     bot       left

padding-top: <a href="../../css_types/integer">&lt;integer&gt;</a>;
padding-right: <a href="../../css_types/integer">&lt;integer&gt;</a>;
padding-bottom: <a href="../../css_types/integer">&lt;integer&gt;</a>;
padding-left: <a href="../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `padding` specifies spacing around the _content_ of a widget, thus this spacing is added _inside_ the widget.
The values of the [`<integer>`](../css_types/integer.md) determine how much spacing is added and the number of values define what edges get what padding:

 - 1 [`<integer>`](../css_types/integer.md) sets the same padding for the four edges of the widget;
 - 2 [`<integer>`](../css_types/integer.md) set padding for top/bottom and left/right edges, respectively.
 - 4 [`<integer>`](../css_types/integer.md) set padding for the top, right, bottom, and left edges, respectively.

!!! tip

    To remember the order of the edges affected by the rule `padding` when it has 4 values, think of a clock.
    Its hand starts at the top and then goes clockwise: top, right, bottom, left.

Alternatively, padding can be set for each edge individually through the rules `padding-top`, `padding-right`, `padding-bottom`, and `padding-left`, respectively.

## Example

### Basic usage

This example adds padding around some text.

=== "Output"

    ```{.textual path="docs/examples/styles/padding.py"}
    ```

=== "padding.py"

    ```python
    --8<-- "docs/examples/styles/padding.py"
    ```

=== "padding.tcss"

    ```css hl_lines="7"
    --8<-- "docs/examples/styles/padding.tcss"
    ```

### All padding settings

The next example shows a grid.
In each cell, we have a placeholder that has its padding set in different ways.
The effect of each padding setting is noticeable in the colored background around the text of each placeholder.

=== "Output"

    ```{.textual path="docs/examples/styles/padding_all.py"}
    ```

=== "padding_all.py"

    ```py
    --8<-- "docs/examples/styles/padding_all.py"
    ```

=== "padding_all.tcss"

    ```css hl_lines="16 20 24 28 32 36 40 44"
    --8<-- "docs/examples/styles/padding_all.tcss"
    ```

## CSS

```css
/* Set padding of 1 around all edges */
padding: 1;
/* Set padding of 2 on the top and bottom edges, and 4 on the left and right */
padding: 2 4;
/* Set padding of 1 on the top, 2 on the right,
                 3 on the bottom, and 4 on the left */
padding: 1 2 3 4;

padding-top: 1;
padding-right: 2;
padding-bottom: 3;
padding-left: 4;
```

## Python

In Python, you cannot set any of the individual `padding` styles `padding-top`, `padding-right`, `padding-bottom`, and `padding-left`.

However, you _can_ set padding to a single integer, a tuple of 2 integers, or a tuple of 4 integers:

```python
# Set padding of 1 around all edges
widget.styles.padding = 1
# Set padding of 2 on the top and bottom edges, and 4 on the left and right
widget.styles.padding = (2, 4)
# Set padding of 1 on top, 2 on the right, 3 on the bottom, and 4 on the left
widget.styles.padding = (1, 2, 3, 4)
```

## See also

 - [`box-sizing`](./box_sizing.md) to specify how to account for padding in a widget's dimensions.
 - [`margin`](./margin.md) to add spacing around a widget.
````

## File: docs/styles/position.md
````markdown
# Position

The `position` style modifies what [`offset`](./offset.md) is applied to.
The default for `position` is `"relative"`, which means the offset is applied to the normal position of the widget.
In other words, if `offset` is (1, 1), then the widget will be moved 1 cell and 1 line down from its usual position.

The alternative value of `position` is `"absolute"`.
With absolute positioning, the offset is relative to the origin (i.e. the top left of the container).
So a widget with offset (1, 1) and absolute positioning will be 1 cell and 1 line down from the top left corner.

!!! note

    Absolute positioning takes precedence over the parent's alignment rule.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
position: <a href="../../css_types/position">&lt;position&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"


## Examples


Two labels, the first is absolute positioned and is displayed relative to the top left of the screen.
The second label is relative and is displayed offset from the center.

=== "Output"

    ```{.textual path="docs/examples/styles/position.py"}
    ```

=== "position.py"

    ```py
    --8<-- "docs/examples/styles/position.py"
    ```

=== "position.tcss"

    ```css
    --8<-- "docs/examples/styles/position.tcss"
    ```




## CSS

```css
position: relative;
position: absolute;
```

## Python

```py
widget.styles.position = "relative"
widget.styles.position = "absolute"
```
````

## File: docs/styles/scrollbar_gutter.md
````markdown
# Scrollbar-gutter

The `scrollbar-gutter` style allows reserving space for a vertical scrollbar.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
scrollbar-gutter: auto | stable;
--8<-- "docs/snippets/syntax_block_end.md"

### Values

| Value            | Description                                    |
|------------------|------------------------------------------------|
| `auto` (default) | No space is reserved for a vertical scrollbar. |
| `stable`         | Space is reserved for a vertical scrollbar.    |

Setting the value to `stable` prevents unwanted layout changes when the scrollbar becomes visible, whereas the default value of `auto` means that the layout of your application is recomputed when a vertical scrollbar becomes needed.

## Example

In the example below, notice the gap reserved for the scrollbar on the right side of the
terminal window.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_gutter.py"}
    ```

=== "scrollbar_gutter.py"

    ```python
    --8<-- "docs/examples/styles/scrollbar_gutter.py"
    ```

=== "scrollbar_gutter.tcss"

    ```css hl_lines="2"
    --8<-- "docs/examples/styles/scrollbar_gutter.tcss"
    ```

## CSS

```css
scrollbar-gutter: auto;    /* Don't reserve space for a vertical scrollbar. */
scrollbar-gutter: stable;  /* Reserve space for a vertical scrollbar. */
```

## Python

```python
self.styles.scrollbar_gutter = "auto"    # Don't reserve space for a vertical scrollbar.
self.styles.scrollbar_gutter = "stable"  # Reserve space for a vertical scrollbar.
```
````

## File: docs/styles/scrollbar_size.md
````markdown
# Scrollbar-size

The `scrollbar-size` style defines the width of the scrollbars.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
scrollbar-size: <a href="../../css_types/integer">&lt;integer&gt;</a> <a href="../../css_types/integer">&lt;integer&gt;</a>;
              # horizontal vertical

scrollbar-size-horizontal: <a href="../../css_types/integer">&lt;integer&gt;</a>;
scrollbar-size-vertical: <a href="../../css_types/integer">&lt;integer&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `scrollbar-size` style takes two [`<integer>`](../css_types/integer.md) to set the horizontal and vertical scrollbar sizes, respectively.
This customisable size is the width of the scrollbar, given that its length will always be 100% of the container.

The scrollbar widths may also be set individually with `scrollbar-size-horizontal` and `scrollbar-size-vertical`.

## Examples

### Basic usage

In this example we modify the size of the widget's scrollbar to be _much_ larger than usual.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_size.py"}
    ```

=== "scrollbar_size.py"

    ```python
    --8<-- "docs/examples/styles/scrollbar_size.py"
    ```

=== "scrollbar_size.tcss"

    ```css hl_lines="13"
    --8<-- "docs/examples/styles/scrollbar_size.tcss"
    ```

### Scrollbar sizes comparison

In the next example we show three containers with differently sized scrollbars.

!!! tip

    If you want to hide the scrollbar but still allow the container to scroll
    using the mousewheel or keyboard, you can set the scrollbar size to `0`.

=== "Output"

    ```{.textual path="docs/examples/styles/scrollbar_size2.py"}
    ```

=== "scrollbar_size2.py"

    ```python
    --8<-- "docs/examples/styles/scrollbar_size2.py"
    ```

=== "scrollbar_size2.tcss"

    ```css hl_lines="6 11 16"
    --8<-- "docs/examples/styles/scrollbar_size2.tcss"
    ```

## CSS

```css
/* Set horizontal scrollbar to 10, and vertical scrollbar to 4 */
scrollbar-size: 10 4;

/* Set horizontal scrollbar to 10 */
scrollbar-size-horizontal: 10;

/* Set vertical scrollbar to 4 */
scrollbar-size-vertical: 4;
```

## Python

The style `scrollbar-size` has no Python equivalent.
The scrollbar sizes must be set independently:

```py
# Set horizontal scrollbar to 10:
widget.styles.scrollbar_size_horizontal = 10
# Set vertical scrollbar to 4:
widget.styles.scrollbar_size_vertical = 4
```
````

## File: docs/styles/text_align.md
````markdown
# Text-align

The `text-align` style sets the text alignment in a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-align: <a href="../../css_types/text_align">&lt;text-align&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The `text-align` style accepts a value of the type [`<text-align>`](../css_types/text_align.md) that defines how text is aligned inside the widget.

### Defaults

The default value is `start`.

## Example

This example shows, from top to bottom: `left`, `center`, `right`, and `justify` text alignments.

=== "Output"

    ```{.textual path="docs/examples/styles/text_align.py"}
    ```

=== "text_align.py"

    ```python
    --8<-- "docs/examples/styles/text_align.py"
    ```

=== "text_align.tcss"

    ```css hl_lines="2 7 12 17"
    --8<-- "docs/examples/styles/text_align.tcss"
    ```

[//]: # (TODO: Add an example that shows how `start` and `end` change when RTL support is added.)

## CSS

```css
/* Set text in the widget to be right aligned */
text-align: right;
```

## Python

```python
# Set text in the widget to be right aligned
widget.styles.text_align = "right"
```

## See also

 - [`align`](./align.md) to set the alignment of children widgets inside a container.
 - [`content-align`](./content_align.md) to set the alignment of content inside a widget.
````

## File: docs/styles/text_opacity.md
````markdown
# Text-opacity

The `text-opacity` style blends the foreground color (i.e. text) with the background color.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-opacity: <a href="../../css_types/number">&lt;number&gt;</a> | <a href="../../css_types/percentage">&lt;percentage&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"


The text opacity of a widget can be set as a [`<number>`](../css_types/number.md) or a [`<percentage>`](../css_types/percentage.md).
If given as a number, then `text-opacity` should be a value between 0 and 1, where 0 makes the foreground color match the background (effectively making text invisible) and 1 will display text as normal.
If given as a percentage, 0% will result in invisible text, and 100% will display fully opaque text.

Typically, if you set this value it would be somewhere between the two extremes.
For instance, setting `text-opacity` to `70%` would result in slightly faded text. Setting it to `0.3` would result in very dim text.

!!! warning

    Be careful not to set text opacity so low as to make it hard to read.


## Example

This example shows, from top to bottom, increasing `text-opacity` values.

=== "Output"

    ```{.textual path="docs/examples/styles/text_opacity.py"}
    ```

=== "text_opacity.py"

    ```python
    --8<-- "docs/examples/styles/text_opacity.py"
    ```

=== "text_opacity.tcss"

    ```css hl_lines="2 6 10 14 18"
    --8<-- "docs/examples/styles/text_opacity.tcss"
    ```

## CSS

```css
/* Set the text to be "half-faded" against the background of the widget */
text-opacity: 50%;
```

## Python

```python
# Set the text to be "half-faded" against the background of the widget
widget.styles.text_opacity = "50%"
```

## See also

 - [`opacity`](./opacity.md) to specify the opacity of a whole widget.
````

## File: docs/styles/text_overflow.md
````markdown
# Text-overflow

The `text-overflow` style defines what happens when text *overflows*.

Text overflow occurs when there is not enough space to fit the text on a line.
This may happen if wrapping is disabled (via [text-wrap](./text_wrap.md)) or if a single word is too large to fit within the width of its container.

## Syntax 

--8<-- "docs/snippets/syntax_block_start.md"
text-overflow: clip | fold | ellipsis;
--8<-- "docs/snippets/syntax_block_end.md"

### Values

| Value      | Description                                                                                          |
| ---------- | ---------------------------------------------------------------------------------------------------- |
| `clip`     | Overflowing text will be clipped (the overflow portion is removed from the output).                  |
| `fold`     | Overflowing text will fold on to the next line(s).                                                   |
| `ellipsis` | Overflowing text will be truncated and the last visible character will be replaced with an ellipsis. |


## Example

In the following example we show the output of each of the values of `text_overflow`.

The widgets all have [text wrapping](./text_wrap.md) disabled, which will cause the
example string to overflow as it is longer than the available width.

In the first (top) widget, `text-overflow` is set to "clip" which clips any text that is overflowing, resulting in a single line.

In the second widget, `text-overflow` is set to "fold", which causes the overflowing text to *fold* on to the next line.
When text folds like this, it won't respect word boundaries--so you may get words broken across lines.

In the third widget, `text-overflow` is set to "ellipsis", which is similar to "clip", but with the last character set to an ellipsis.
This option is useful to indicate to the user that there may be more text.

=== "Output"

    ```{.textual path="docs/examples/styles/text_overflow.py"}
    ```

=== "text_overflow.py"

    ```py
    --8<-- "docs/examples/styles/text_overflow.py"
    ```

=== "text_overflow.tcss"

    ```css
    --8<-- "docs/examples/styles/text_overflow.tcss"
    ```


### CSS

```css
#widget {
    text-overflow: ellipsis; 
}
```

### Python

```py
widget.styles.text_overflow = "ellipsis" 
```


## See also

 - [`text-wrap`](./text_wrap.md) which is used to enable or disable wrapping.
````

## File: docs/styles/text_style.md
````markdown
# Text-style

The `text-style` style sets the style for the text in a widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-style: <a href="../../css_types/text_style">&lt;text-style&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

`text-style` will take all the values specified and will apply that styling combination to the text in the widget.

## Examples

### Basic usage

Each of the three text panels has a different text style, respectively `bold`, `italic`, and `reverse`, from left to right.

=== "Output"

    ```{.textual path="docs/examples/styles/text_style.py" lines=14}
    ```

=== "text_style.py"

    ```python
    --8<-- "docs/examples/styles/text_style.py"
    ```

=== "text_style.tcss"

    ```css hl_lines="9 13 17"
    --8<-- "docs/examples/styles/text_style.tcss"
    ```

### All text styles

The next example shows all different text styles on their own, as well as some combinations of styles in a single widget.

=== "Output"

    ```{.textual path="docs/examples/styles/text_style_all.py"}
    ```

=== "text_style_all.py"

    ```python
    --8<-- "docs/examples/styles/text_style_all.py"
    ```

=== "text_style_all.tcss"

    ```css hl_lines="2 6 10 14 18 22 26 30"
    --8<-- "docs/examples/styles/text_style_all.tcss"
    ```

## CSS

```css
text-style: italic;
```

## Python

```python
widget.styles.text_style = "italic"
```
````

## File: docs/styles/text_wrap.md
````markdown
# Text-wrap

The `text-wrap` style set how Textual should wrap text.
The default value is "wrap" which will word-wrap text.
You can also set this style to "nowrap" which will disable wrapping entirely.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
text-wrap: wrap | nowrap;
--8<-- "docs/snippets/syntax_block_end.md"


## Example

In the following example we have two pieces of text.

The first (top) text has the default value for `text-wrap` ("wrap") which will cause text to be word wrapped as normal.
The second has `text-wrap` set to "nowrap" which disables text wrapping and results in a single line.

=== "Output"

    ```{.textual path="docs/examples/styles/text_wrap.py"}
    ```

=== "text_wrap.py"

    ```py
    --8<-- "docs/examples/styles/text_wrap.py"
    ```

=== "text_wrap.tcss"

    ```css
    --8<-- "docs/examples/styles/text_wrap.tcss"
    ```


## CSS


```css
text-wrap: wrap;
text-wrap: nowrap;
```


## Python


```py
widget.styles.text_wrap = "wrap"
widget.styles.text_wrap = "nowrap"
```



## See also

 - [`text-overflow`](./text_overflow.md) to set what happens to text that overflows the available width.
````

## File: docs/styles/tint.md
````markdown
# Tint

The `tint` style blends a color with the whole widget.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
tint: <a href="../../css_types/color">&lt;color&gt;</a> [<a href="../../css_types/percentage">&lt;percentage&gt;</a>];
--8<-- "docs/snippets/syntax_block_end.md"

The tint style blends a [`<color>`](../css_types/color.md) with the widget. The color should likely have an _alpha_ component (specified directly in the color used or by the optional [`<percentage>`](../css_types/percentage.md)), otherwise the end result will obscure the widget content.

## Example

This examples shows a green tint with gradually increasing alpha.

=== "Output"

    ```{.textual path="docs/examples/styles/tint.py"}
    ```

=== "tint.py"

    ```python hl_lines="13"
    --8<-- "docs/examples/styles/tint.py"
    ```

    1. We set the tint to a `Color` instance with varying levels of opacity, set through the method [with_alpha][textual.color.Color.with_alpha].

=== "tint.tcss"

    ```css
    --8<-- "docs/examples/styles/tint.tcss"
    ```

## CSS

```css
/* A red tint (could indicate an error) */
tint: red 20%;

/* A green tint */
tint: rgba(0, 200, 0, 0.3);
```

## Python

```python
# A red tint
from textual.color import Color
widget.styles.tint = Color.parse("red").with_alpha(0.2);

# A green tint
widget.styles.tint = "rgba(0, 200, 0, 0.3)"
```
````

## File: docs/styles/visibility.md
````markdown
# Visibility

The `visibility` style determines whether a widget is visible or not.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
visibility: hidden | visible;
--8<-- "docs/snippets/syntax_block_end.md"

`visibility` takes one of two values to set the visibility of a widget.

### Values

| Value               | Description                             |
|---------------------|-----------------------------------------|
| `hidden`            | The widget will be invisible.           |
| `visible` (default) | The widget will be displayed as normal. |

### Visibility inheritance

!!! note

    Children of an invisible container _can_ be visible.

By default, children inherit the visibility of their parents.
So, if a container is set to be invisible, its children widgets will also be invisible by default.
However, those widgets can be made visible if their visibility is explicitly set to `visibility: visible`.
This is shown in the second example below.

## Examples

### Basic usage

Note that the second widget is hidden while leaving a space where it would have been rendered.

=== "Output"

    ```{.textual path="docs/examples/styles/visibility.py"}
    ```

=== "visibility.py"

    ```python
    --8<-- "docs/examples/styles/visibility.py"
    ```

=== "visibility.tcss"

    ```css hl_lines="14"
    --8<-- "docs/examples/styles/visibility.tcss"
    ```

### Overriding container visibility

The next example shows the interaction of the `visibility` style with invisible containers that have visible children.
The app below has three rows with a `Horizontal` container per row and three placeholders per row.
The containers all have a white background, and then:

 - the top container is visible by default (we can see the white background around the placeholders);
 - the middle container is invisible and the children placeholders inherited that setting;
 - the bottom container is invisible _but_ the children placeholders are visible because they were set to be visible.

=== "Output"

    ```{.textual path="docs/examples/styles/visibility_containers.py"}
    ```

=== "visibility_containers.py"

    ```python
    --8<-- "docs/examples/styles/visibility_containers.py"
    ```

=== "visibility_containers.tcss"

    ```css hl_lines="2-3 7 9-11 13-15 17-19"
    --8<-- "docs/examples/styles/visibility_containers.tcss"
    ```

    1. The padding and the white background let us know when the `Horizontal` is visible.
    2. The top `Horizontal` is visible by default, and so are its children.
    3. The middle `Horizontal` is made invisible and its children will inherit that setting.
    4. The bottom `Horizontal` is made invisible...
    5. ... but its children override that setting and become visible.

## CSS

```css
/* Widget is invisible */
visibility: hidden;

/* Widget is visible */
visibility: visible;
```

## Python

```python
# Widget is invisible
self.styles.visibility = "hidden"

# Widget is visible
self.styles.visibility = "visible"
```

There is also a shortcut to set a Widget's visibility. The `visible` property on `Widget` may be set to `True` or `False`.

```python
# Make a widget invisible
widget.visible = False

# Make the widget visible again
widget.visible = True
```

## See also

 - [`display`](./display.md) to specify whether a widget is displayed or not.
````

## File: docs/styles/width.md
````markdown
# Width

The `width` style sets a widget's width.

## Syntax

--8<-- "docs/snippets/syntax_block_start.md"
width: <a href="../../css_types/scalar">&lt;scalar&gt;</a>;
--8<-- "docs/snippets/syntax_block_end.md"

The style `width` needs a [`<scalar>`](../css_types/scalar.md) to determine the horizontal length of the width.
By default, it sets the width of the content area, but if [`box-sizing`](./box_sizing.md) is set to `border-box` it sets the width of the border area.

## Examples

### Basic usage

This example adds a widget with 50% width of the screen.

=== "Output"

    ```{.textual path="docs/examples/styles/width.py"}
    ```

=== "width.py"

    ```python
    --8<-- "docs/examples/styles/width.py"
    ```

=== "width.tcss"

    ```css hl_lines="3"
    --8<-- "docs/examples/styles/width.tcss"
    ```

### All width formats

=== "Output"

    ```{.textual path="docs/examples/styles/width_comparison.py" lines=24 columns=80}
    ```

=== "width_comparison.py"

    ```py hl_lines="15-23"
    --8<-- "docs/examples/styles/width_comparison.py"
    ```

    1. The id of the placeholder identifies which unit will be used to set the width of the widget.

=== "width_comparison.tcss"

    ```css hl_lines="2 5 8 11 14 17 20 23 26"
    --8<-- "docs/examples/styles/width_comparison.tcss"
    ```

    1. This sets the width to 9 columns.
    2. This sets the width to 12.5% of the space made available by the container.
    The container is 80 columns wide, so 12.5% of 80 is 10.
    3. This sets the width to 10% of the width of the direct container, which is the `Horizontal` container.
    Because it expands to fit all of the terminal, the width of the `Horizontal` is 80 and 10% of 80 is 8.
    4. This sets the width to 25% of the height of the direct container, which is the `Horizontal` container.
    Because it expands to fit all of the terminal, the height of the `Horizontal` is 24 and 25% of 24 is 6.
    5. This sets the width to 15% of the viewport width, which is 80.
    15% of 80 is 12.
    6. This sets the width to 25% of the viewport height, which is 24.
    25% of 24 is 6.
    7. This sets the width of the placeholder to be the optimal size that fits the content without scrolling.
    Because the content is the string `"#auto"`, the placeholder has its width set to 5.
    8. This sets the width to `1fr`, which means this placeholder will have a third of the width of a placeholder with `3fr`.
    9. This sets the width to `3fr`, which means this placeholder will have triple the width of a placeholder with `1fr`.


## CSS

```css
/* Explicit cell width */
width: 10;

/* Percentage width */
width: 50%;

/* Automatic width */
width: auto;
```

## Python

```python
widget.styles.width = 10
widget.styles.width = "50%
widget.styles.width = "auto"
```

## See also

 - [`max-width`](./max_width.md) and [`min-width`](./min_width.md) to limit the width of a widget.
 - [`height`](./height.md) to set the height of a widget.
````

## File: docs/widgets/_template.md
````markdown
# Widget

!!! tip "Added in version x.y.z"

Widget description.

- [ ] Focusable
- [ ] Container


## Example

Example app showing the widget:

=== "Output"

    ```{.textual path="docs/examples/widgets/checkbox.py"}
    ```

=== "checkbox.py"

    ```python
    --8<-- "docs/examples/widgets/checkbox.py"
    ```

=== "checkbox.tcss"

    ```css
    --8<-- "docs/examples/widgets/checkbox.tcss"
    ```


## Reactive Attributes

## Messages

## Bindings

The WIDGET widget defines the following bindings:

::: textual.widgets.WIDGET.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false


## Component classes

The WIDGET widget provides the following component classes:

::: textual.widget.WIDGET.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false


## Additional notes

- Did you know this?
- Another pro tip.


## See also

- Another related API.
- Something else useful.


---


::: textual.widgets.WIDGET
    options:
      heading_level: 2
````

## File: docs/widgets/button.md
````markdown
# Button


A simple button widget which can be pressed using a mouse click or by pressing ++return++
when it has focus.

- [x] Focusable
- [ ] Container

## Example

The example below shows each button variant, and its disabled equivalent.
Clicking any of the non-disabled buttons in the example app below will result in the app exiting and the details of the selected button being printed to the console.

=== "Output"

    ```{.textual path="docs/examples/widgets/button.py"}
    ```

=== "button.py"

    ```python
    --8<-- "docs/examples/widgets/button.py"
    ```

=== "button.tcss"

    ```css
    --8<-- "docs/examples/widgets/button.tcss"
    ```

## Reactive Attributes

| Name       | Type            | Default     | Description                                                                                                                       |
|------------|-----------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------|
| `label`    | `str`           | `""`        | The text that appears inside the button.                                                                                          |
| `variant`  | `ButtonVariant` | `"default"` | Semantic styling variant. One of `default`, `primary`, `success`, `warning`, `error`.                                             |
| `disabled` | `bool`          | `False`     | Whether the button is disabled or not. Disabled buttons cannot be focused or clicked, and are styled in a way that suggests this. |

## Messages

- [Button.Pressed][textual.widgets.Button.Pressed]

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

## Additional Notes

- The spacing between the text and the edges of a button are _not_ due to padding. The default styling for a `Button` includes borders and a `min-width` of 16 columns. To remove the spacing, set `border: none;` in your CSS and adjust the minimum width as needed.

---


::: textual.widgets.Button
    options:
      heading_level: 2

::: textual.widgets.button
    options:
      show_root_heading: true
      show_root_toc_entry: true
````

## File: docs/widgets/checkbox.md
````markdown
# Checkbox

!!! tip "Added in version 0.13.0"

A simple checkbox widget which stores a boolean value.

- [x] Focusable
- [ ] Container

## Example

The example below shows check boxes in various states.

=== "Output"

    ```{.textual path="docs/examples/widgets/checkbox.py"}
    ```

=== "checkbox.py"

    ```python
    --8<-- "docs/examples/widgets/checkbox.py"
    ```

=== "checkbox.tcss"

    ```css
    --8<-- "docs/examples/widgets/checkbox.tcss"
    ```

## Reactive Attributes

| Name    | Type   | Default | Description                |
| ------- | ------ | ------- | -------------------------- |
| `value` | `bool` | `False` | The value of the checkbox. |

## Messages

- [Checkbox.Changed][textual.widgets.Checkbox.Changed]

## Bindings

The checkbox widget defines the following bindings:

::: textual.widgets._toggle_button.ToggleButton.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The checkbox widget inherits the following component classes:

::: textual.widgets._toggle_button.ToggleButton.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false


---


::: textual.widgets.Checkbox
    options:
      heading_level: 2
````

## File: docs/widgets/collapsible.md
````markdown
# Collapsible

!!! tip "Added in version 0.37"

A container with a title that can be used to show (expand) or hide (collapse) content, either by clicking or focusing and pressing ++enter++.

- [x] Focusable
- [x] Container


## Composing

You can add content to a Collapsible widget either by passing in children to the constructor, or with a context manager (`with` statement).

Here is an example of using the constructor to add content:

```python
def compose(self) -> ComposeResult:
    yield Collapsible(Label("Hello, world."))
```

Here's how the to use it with the context manager:

```python
def compose(self) -> ComposeResult:
    with Collapsible():
        yield Label("Hello, world.")
```

The second form is generally preferred, but the end result is the same.

## Title

The default title "Toggle" can be customized by setting the `title` parameter of the constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="An interesting story."):
        yield Label("Interesting but verbose story.")
```

## Initial State

The initial state of the `Collapsible` widget can be customized via the `collapsed` parameter of the constructor:

```python
def compose(self) -> ComposeResult:
    with Collapsible(title="Contents 1", collapsed=False):
        yield Label("Hello, world.")

    with Collapsible(title="Contents 2", collapsed=True):  # Default.
        yield Label("Hello, world.")
```

## Collapse/Expand Symbols

The symbols used to show the collapsed / expanded state can be customized by setting the parameters `collapsed_symbol` and `expanded_symbol`:

```python
def compose(self) -> ComposeResult:
    with Collapsible(collapsed_symbol=">>>", expanded_symbol="v"):
        yield Label("Hello, world.")
```

## Examples


The following example contains three `Collapsible`s in different states.

=== "All expanded"

    ```{.textual path="docs/examples/widgets/collapsible.py" press="e"}
    ```

=== "All collapsed"

    ```{.textual path="docs/examples/widgets/collapsible.py" press="c"}
    ```

=== "Mixed"

    ```{.textual path="docs/examples/widgets/collapsible.py"}
    ```

=== "collapsible.py"

    ```python
    --8<-- "docs/examples/widgets/collapsible.py"
    ```

### Setting Initial State

The example below shows nested `Collapsible` widgets and how to set their initial state.


=== "Output"

    ```{.textual path="docs/examples/widgets/collapsible_nested.py"}
    ```

=== "collapsible_nested.py"

    ```python hl_lines="7"
    --8<-- "docs/examples/widgets/collapsible_nested.py"
    ```

### Custom Symbols

The following example shows `Collapsible` widgets with custom expand/collapse symbols.


=== "Output"

    ```{.textual path="docs/examples/widgets/collapsible_custom_symbol.py"}
    ```

=== "collapsible_custom_symbol.py"

    ```python
    --8<-- "docs/examples/widgets/collapsible_custom_symbol.py"
    ```

## Reactive Attributes

| Name        | Type   | Default     | Description                                          |
| ----------- | ------ | ------------| ---------------------------------------------------- |
| `collapsed` | `bool` | `True`      | Controls the collapsed/expanded state of the widget. |
| `title`     | `str`  | `"Toggle"`  | Title of the collapsed/expanded contents.            |

## Messages

- [Collapsible.Toggled][textual.widgets.Collapsible.Toggled]

## Bindings

The collapsible widget defines the following binding on its title:

::: textual.widgets._collapsible.CollapsibleTitle.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

This widget has no component classes.


::: textual.widgets.Collapsible
    options:
      heading_level: 2
````

## File: docs/widgets/content_switcher.md
````markdown
# ContentSwitcher

!!! tip "Added in version 0.14.0"

A widget for containing and switching display between multiple child
widgets.

- [ ] Focusable
- [X] Container

## Example

The example below uses a `ContentSwitcher` in combination with two `Button`s
to create a simple tabbed view. Note how each `Button` has an ID set, and
how each child of the `ContentSwitcher` has a corresponding ID; then a
`Button.Clicked` handler is used to set `ContentSwitcher.current` to switch
between the different views.

=== "Output"

    ```{.textual path="docs/examples/widgets/content_switcher.py"}
    ```

=== "content_switcher.py"

    ~~~python
    --8<-- "docs/examples/widgets/content_switcher.py"
    ~~~

    1. A `Horizontal` to hold the buttons, each with a unique ID.
    2. This button will select the `DataTable` in the `ContentSwitcher`.
    3. This button will select the `Markdown` in the `ContentSwitcher`.
    4. Note that the initial visible content is set by its ID, see below.
    5. When a button is pressed, its ID is used to switch to a different widget in the `ContentSwitcher`. Remember that IDs are unique within parent, so the buttons and the widgets in the `ContentSwitcher` can share IDs.

=== "content_switcher.tcss"

    ~~~sass
    --8<-- "docs/examples/widgets/content_switcher.tcss"
    ~~~

When the user presses the "Markdown" button the view is switched:

```{.textual path="docs/examples/widgets/content_switcher.py" lines="40" press="tab,enter"}
```

## Reactive Attributes

| Name      | Type            | Default | Description                                                             |
| --------- | --------------- | ------- | ----------------------------------------------------------------------- |
| `current` | `str` \| `None` | `None`  | The ID of the currently-visible child. `None` means nothing is visible. |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.


---


::: textual.widgets.ContentSwitcher
    options:
      heading_level: 2
````

## File: docs/widgets/data_table.md
````markdown
# DataTable

A widget to display text in a table.  This includes the ability to update data, use a cursor to navigate data, respond to mouse clicks, delete rows or columns, and individually render each cell as a Rich Text renderable.  DataTable provides an efficiently displayed and updated table capable for most applications.

Applications may have custom rules for formatting, numbers, repopulating tables after searching or filtering, and responding to selections.  The widget emits events to interface with custom logic.

- [x] Focusable
- [ ] Container

## Guide

### Adding data

The following example shows how to fill a table with data.
First, we use [add_columns][textual.widgets.DataTable.add_columns] to include the `lane`, `swimmer`, `country`, and `time` columns in the table.
After that, we use the [add_rows][textual.widgets.DataTable.add_rows] method to insert the rows into the table.

=== "Output"

    ```{.textual path="docs/examples/widgets/data_table.py"}
    ```

=== "data_table.py"

    ```python
    --8<-- "docs/examples/widgets/data_table.py"
    ```

To add a single row or column use [add_row][textual.widgets.DataTable.add_row] and [add_column][textual.widgets.DataTable.add_column], respectively.

#### Styling and justifying cells

Cells can contain more than just plain strings - [Rich](https://rich.readthedocs.io/en/stable/introduction.html) renderables such as [`Text`](https://rich.readthedocs.io/en/stable/text.html?highlight=Text#rich-text) are also supported.
`Text` objects provide an easy way to style and justify cell content:

=== "Output"

    ```{.textual path="docs/examples/widgets/data_table_renderables.py"}
    ```

=== "data_table_renderables.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_renderables.py"
    ```

### Keys

When adding a row to the table, you can supply a _key_ to [add_row][textual.widgets.DataTable.add_row].
A key is a unique identifier for that row.
If you don't supply a key, Textual will generate one for you and return it from `add_row`.
This key can later be used to reference the row, regardless of its current position in the table.

When working with data from a database, for example, you may wish to set the row `key` to the primary key of the data to ensure uniqueness.
The method [add_column][textual.widgets.DataTable.add_column] also accepts a `key` argument and works similarly.

Keys are important because cells in a data table can change location due to factors like row deletion and sorting.
Thus, using keys instead of coordinates allows us to refer to data without worrying about its current location in the table.

If you want to change the table based solely on coordinates, you may need to convert that coordinate to a cell key first using the [coordinate_to_cell_key][textual.widgets.DataTable.coordinate_to_cell_key] method.

### Cursors

A cursor allows navigating within a table with the keyboard or mouse. There are four cursor types: `"cell"` (the default), `"row"`, `"column"`, and `"none"`.

 Change the cursor type by assigning to 
the [`cursor_type`][textual.widgets.DataTable.cursor_type] reactive attribute.  
The coordinate of the cursor is exposed via the [`cursor_coordinate`][textual.widgets.DataTable.cursor_coordinate] reactive attribute.

Using the keyboard, arrow keys,  ++page-up++, ++page-down++, ++home++ and ++end++ move the cursor highlight, emitting a [`CellHighlighted`][textual.widgets.DataTable.CellHighlighted] 
message, then enter selects the cell, emitting a [`CellSelected`][textual.widgets.DataTable.CellSelected] message.  If the 
`cursor_type` is row, then [`RowHighlighted`][textual.widgets.DataTable.RowHighlighted] and [`RowSelected`][textual.widgets.DataTable.RowSelected]
are emitted, similarly for  [`ColumnHighlighted`][textual.widgets.DataTable.ColumnHighlighted] and [`ColumnSelected`][textual.widgets.DataTable.ColumnSelected].

When moving the mouse over the table, a [`MouseMove`][textual.events.MouseMove] event is emitted, the cell hovered over is styled,
and the [`hover_coordinate`][textual.widgets.DataTable.hover_coordinate] reactive attribute is updated.  Clicking the mouse
then emits the [`CellHighlighted`][textual.widgets.DataTable.CellHighlighted] and  [`CellSelected`][textual.widgets.DataTable.CellSelected]
events. 

=== "Column Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py"}
    ```

=== "Row Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py" press="c"}
    ```

=== "Cell Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py" press="c,c"}
    ```

=== "No Cursor"

    ```{.textual path="docs/examples/widgets/data_table_cursors.py" press="c,c,c"}
    ```

=== "data_table_cursors.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_cursors.py"
    ```


### Updating data

Cells can be updated using the [update_cell][textual.widgets.DataTable.update_cell] and [update_cell_at][textual.widgets.DataTable.update_cell_at] methods.

### Removing data

To remove all data in the table, use the [clear][textual.widgets.DataTable.clear] method.
To remove individual rows, use [remove_row][textual.widgets.DataTable.remove_row].
The `remove_row` method accepts a `key` argument, which identifies the row to be removed.

If you wish to remove the row below the cursor in the `DataTable`, use `coordinate_to_cell_key` to get the row key of
the row under the current `cursor_coordinate`, then supply this key to `remove_row`:

```python
# Get the keys for the row and column under the cursor.
row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
# Supply the row key to `remove_row` to delete the row.
table.remove_row(row_key)
```

### Removing columns

To remove individual columns, use [remove_column][textual.widgets.DataTable.remove_column].
The `remove_column` method accepts a `key` argument, which identifies the column to be removed.

You can remove the column below the cursor using the same `coordinate_to_cell_key` method described above:

```python
# Get the keys for the row and column under the cursor.
_, column_key = table.coordinate_to_cell_key(table.cursor_coordinate)
# Supply the column key to `column_row` to delete the column.
table.remove_column(column_key)
```

### Fixed data

You can fix a number of rows and columns in place, keeping them pinned to the top and left of the table respectively.
To do this, assign an integer to the `fixed_rows` or `fixed_columns` reactive attributes of the `DataTable`.

=== "Fixed data"

    ```{.textual path="docs/examples/widgets/data_table_fixed.py" press="end"}
    ```

=== "data_table_fixed.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_fixed.py"
    ```

In the example above, we set `fixed_rows` to `2`, and `fixed_columns` to `1`,
meaning the first two rows and the leftmost column do not scroll - they always remain
visible as you scroll through the data table.

### Sorting

The DataTable rows can be sorted using the  [`sort`][textual.widgets.DataTable.sort]  method.

There are three methods of using [`sort`][textual.widgets.DataTable.sort]:

* By Column.  Pass columns in as parameters to sort by the natural order of one or more columns.  Specify a column using either a [`ColumnKey`][textual.widgets.data_table.ColumnKey] instance or the `key` you supplied to [`add_column`][textual.widgets.DataTable.add_column].  For example, `sort("country", "region")` would sort by country, and, when the country values are equal, by region.
* By Key function.  Pass a function as the `key` parameter to sort, similar to the [key function parameter](https://docs.python.org/3/howto/sorting.html#key-functions)  of Python's [`sorted`](https://docs.python.org/3/library/functions.html#sorted) built-in.   The function will be called once per row with a tuple of all row values.
* By both Column and Key function.   You can specify which columns to include as parameters to your key function.  For example, `sort("hours", "rate", key=lambda h, r: h*r)` passes two values to the key function for each row.

The `reverse` argument reverses the order of your sort.  Note that correct sorting may require your key function to undo your formatting.
 
=== "Output"

    ```{.textual path="docs/examples/widgets/data_table_sort.py"}
    ```

=== "data_table_sort.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_sort.py"
    ```

### Labeled rows

A "label" can be attached to a row using the [add_row][textual.widgets.DataTable.add_row] method.
This will add an extra column to the left of the table which the cursor cannot interact with.
This column is similar to the leftmost column in a spreadsheet containing the row numbers.
The example below shows how to attach simple numbered labels to rows.

=== "Labeled rows"

    ```{.textual path="docs/examples/widgets/data_table_labels.py"}
    ```

=== "data_table_labels.py"

    ```python
    --8<-- "docs/examples/widgets/data_table_labels.py"
    ```

## Reactive Attributes

| Name                | Type                                        | Default            | Description                                           |
|---------------------|---------------------------------------------|--------------------|-------------------------------------------------------|
| `show_header`       | `bool`                                      | `True`             | Show the table header                                 |
| `show_row_labels`   | `bool`                                      | `True`             | Show the row labels (if applicable)                   |
| `fixed_rows`        | `int`                                       | `0`                | Number of fixed rows (rows which do not scroll)       |
| `fixed_columns`     | `int`                                       | `0`                | Number of fixed columns (columns which do not scroll) |
| `zebra_stripes`     | `bool`                                      | `False`            | Style with alternating colors on rows                 |
| `header_height`     | `int`                                       | `1`                | Height of header row                                  |
| `show_cursor`       | `bool`                                      | `True`             | Show the cursor                                       |
| `cursor_type`       | `str`                                       | `"cell"`           | One of `"cell"`, `"row"`, `"column"`, or `"none"`     |
| `cursor_coordinate` | [Coordinate][textual.coordinate.Coordinate] | `Coordinate(0, 0)` | The current coordinate of the cursor                  |
| `hover_coordinate`  | [Coordinate][textual.coordinate.Coordinate] | `Coordinate(0, 0)` | The coordinate the _mouse_ cursor is above            |

## Messages

- [DataTable.CellHighlighted][textual.widgets.DataTable.CellHighlighted]
- [DataTable.CellSelected][textual.widgets.DataTable.CellSelected]
- [DataTable.RowHighlighted][textual.widgets.DataTable.RowHighlighted]
- [DataTable.RowSelected][textual.widgets.DataTable.RowSelected]
- [DataTable.ColumnHighlighted][textual.widgets.DataTable.ColumnHighlighted]
- [DataTable.ColumnSelected][textual.widgets.DataTable.ColumnSelected]
- [DataTable.HeaderSelected][textual.widgets.DataTable.HeaderSelected]
- [DataTable.RowLabelSelected][textual.widgets.DataTable.RowLabelSelected]

## Bindings

The data table widget defines the following bindings:

::: textual.widgets.DataTable.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The data table widget provides the following component classes:

::: textual.widgets.DataTable.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

---


::: textual.widgets.DataTable
    options:
      heading_level: 2

::: textual.widgets.data_table
    options:
      show_root_heading: true
      show_root_toc_entry: true
````

## File: docs/widgets/digits.md
````markdown
# Digits

!!! tip "Added in version 0.33.0"

A widget to display numerical values in tall multi-line characters.

The digits 0-9 and characters A-F are supported, in addition to `+`, `-`, `^`, `:`, and `×`.
Other characters will be displayed in a regular size font.

You can set the text to be displayed in the constructor, or call [`update()`][textual.widgets.Digits.update] to change the text after the widget has been mounted.

!!! note "This widget will respect the [text-align](../styles/text_align.md) rule."

- [ ] Focusable
- [ ] Container


## Example

The following example displays a few digits of Pi:

=== "Output"

    ```{.textual path="docs/examples/widgets/digits.py"}
    ```

=== "digits.py"

    ```python
    --8<-- "docs/examples/widgets/digits.py"
    ```

Here's another example which uses `Digits` to display the current time:


=== "Output"

    ```{.textual path="docs/examples/widgets/clock.py"}
    ```

=== "clock.py"

    ```python
    --8<-- "docs/examples/widgets/clock.py"
    ```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.



---


::: textual.widgets.Digits
    options:
      heading_level: 2
````

## File: docs/widgets/directory_tree.md
````markdown
# DirectoryTree

A tree control to navigate the contents of your filesystem.

- [x] Focusable
- [ ] Container


## Example

The example below creates a simple tree to navigate the current working directory.

```python
--8<-- "docs/examples/widgets/directory_tree.py"
```

## Filtering

There may be times where you want to filter what appears in the
`DirectoryTree`. To do this inherit from `DirectoryTree` and implement your
own version of the `filter_paths` method. It should take an iterable of
Python `Path` objects, and return those that pass the filter. For example,
if you wanted to take the above code an filter out all of the "hidden" files
and directories:

=== "Output"

    ```{.textual path="docs/examples/widgets/directory_tree_filtered.py"}
    ```

=== "directory_tree_filtered.py"

    ~~~python
    --8<-- "docs/examples/widgets/directory_tree_filtered.py"
    ~~~

## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |

## Messages

- [DirectoryTree.FileSelected][textual.widgets.DirectoryTree.FileSelected]

## Bindings

The directory tree widget inherits [the bindings from the tree widget][textual.widgets.Tree.BINDINGS].

## Component Classes

The directory tree widget provides the following component classes:

::: textual.widgets.DirectoryTree.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## See Also

* [Tree][textual.widgets.Tree] code reference



---


::: textual.widgets.DirectoryTree
    options:
      heading_level: 2
````

## File: docs/widgets/footer.md
````markdown
# Footer

!!! tip "Added in version 0.63.0"

A simple footer widget which is docked to the bottom of its parent container. Displays
available keybindings for the currently focused widget.

- [ ] Focusable
- [ ] Container


## Example

The example below shows an app with a single keybinding that contains only a `Footer`
widget. Notice how the `Footer` automatically displays the keybinding.

=== "Output"

    ```{.textual path="docs/examples/widgets/footer.py"}
    ```

=== "footer.py"

    ```python
    --8<-- "docs/examples/widgets/footer.py"
    ```

## Reactive Attributes

| Name                   | Type   | Default | Description                                                                                |
| ---------------------- | ------ | ------- | ------------------------------------------------------------------------------------------ |
| `compact`              | `bool` | `False` | Display a more compact footer.                                                             |
| `show_command_palette` | `bool` | `True`  | Display the key to invoke the command palette (show on the right hand side of the footer). |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.


## Additional Notes

* You can prevent keybindings from appearing in the footer by setting the `show` argument of the `Binding` to `False`.
* You can customize the text that appears for the key itself in the footer using the `key_display` argument of `Binding`.


---


::: textual.widgets.Footer
    options:
      heading_level: 2
````

## File: docs/widgets/header.md
````markdown
# Header

A simple header widget which docks itself to the top of the parent container.

!!! note

    The application title which is shown in the header is taken from the [`title`][textual.app.App.title] and [`sub_title`][textual.app.App.sub_title] of the application.

- [ ] Focusable
- [ ] Container

## Example

The example below shows an app with a `Header`.

=== "Output"

    ```{.textual path="docs/examples/widgets/header.py"}
    ```

=== "header.py"

    ```python
    --8<-- "docs/examples/widgets/header.py"
    ```

This example shows how to set the text in the `Header` using `App.title` and `App.sub_title`:

=== "Output"

    ```{.textual path="docs/examples/widgets/header_app_title.py"}
    ```

=== "header_app_title.py"

    ```python
    --8<-- "docs/examples/widgets/header_app_title.py"
    ```

## Reactive Attributes

| Name   | Type   | Default | Description                                                                                                                                                                                      |
| ------ | ------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `tall` | `bool` | `True`  | Whether the `Header` widget is displayed as tall or not. The tall variant is 3 cells tall by default. The non-tall variant is a single cell tall. This can be toggled by clicking on the header. |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.Header
    options:
      heading_level: 2
````

## File: docs/widgets/index.md
````markdown
# Widgets

A reference to the builtin [widgets](../guide/widgets.md).

See the links to the left of the page, or in the hamburger menu (three horizontal bars, top left).
````

## File: docs/widgets/input.md
````markdown
# Input

A single-line text input widget.

- [x] Focusable
- [ ] Container

## Examples

### A Simple Example

The example below shows how you might create a simple form using two `Input` widgets.

=== "Output"

    ```{.textual path="docs/examples/widgets/input.py" press="D,a,r,r,e,n"}
    ```

=== "input.py"

    ```python
    --8<-- "docs/examples/widgets/input.py"
    ```


### Input Types

The `Input` widget supports a `type` parameter which will prevent the user from typing invalid characters.
You can set `type` to any of the following values:


| input.type  | Description                                 |
| ----------- | ------------------------------------------- |
| `"integer"` | Restricts input to integers.                |
| `"number"`  | Restricts input to a floating point number. |
| `"text"`    | Allow all text (no restrictions).           |

=== "Output"

    ```{.textual path="docs/examples/widgets/input_types.py" press="1234"}
    ```

=== "input_types.py"

    ```python
    --8<-- "docs/examples/widgets/input_types.py"
    ```

If you set `type` to something other than `"text"`, then the `Input` will apply the appropriate [validator](#validating-input).

### Restricting Input

You can limit input to particular characters by supplying the `restrict` parameter, which should be a regular expression.
The `Input` widget will prevent the addition of any characters that would cause the regex to no longer match.
For instance, if you wanted to limit characters to binary you could set `restrict=r"[01]*"`.

!!! note

    The `restrict` regular expression is applied to the full value and not just to the new character.

### Maximum Length

You can limit the length of the input by setting `max_length` to a value greater than zero.
This will prevent the user from typing any more characters when the maximum has been reached.

### Validating Input

You can supply one or more *[validators][textual.validation.Validator]* to the `Input` widget to validate the value.

All the supplied validators will run when the value changes, the `Input` is submitted, or focus moves _out_ of the `Input`.
The values `"changed"`, `"submitted"`, and `"blur"`, can be passed as an iterable to the `Input` parameter `validate_on` to request that validation occur only on the respective mesages.
(See [`InputValidationOn`][textual.widgets._input.InputValidationOn] and [`Input.validate_on`][textual.widgets.Input.validate_on].)
For example, the code below creates an `Input` widget that only gets validated when the value is submitted explicitly:

```python
input = Input(validate_on=["submitted"])
```

Validation is considered to have failed if *any* of the validators fail.

You can check whether the validation succeeded or failed inside an [Input.Changed][textual.widgets.Input.Changed], [Input.Submitted][textual.widgets.Input.Submitted], or [Input.Blurred][textual.widgets.Input.Blurred] handler by looking at the `validation_result` attribute on these events.

In the example below, we show how to combine multiple validators and update the UI to tell the user
why validation failed.
Click the tabs to see the output for validation failures and successes.

=== "input_validation.py"

    ```python hl_lines="8-15 31-35 42-45 56-62"
    --8<-- "docs/examples/widgets/input_validation.py"
    ```

    1. `Number` is a built-in `Validator`. It checks that the value in the `Input` is a valid number, and optionally can check that it falls within a range.
    2. `Function` lets you quickly define custom validation constraints. In this case, we check the value in the `Input` is even.
    3. `Palindrome` is a custom `Validator` defined below.
    4. The `Input.Changed` event has a `validation_result` attribute which contains information about the validation that occurred when the value changed.
    5. Here's how we can implement a custom validator which checks if a string is a palindrome. Note how the description passed into `self.failure` corresponds to the message seen on UI.
    6. Textual offers default styling for the `-invalid` CSS class (a red border), which is automatically applied to `Input` when validation fails. We can also provide custom styling for the `-valid` class, as seen here. In this case, we add a green border around the `Input` to indicate successful validation.

=== "Validation Failure"

    ```{.textual path="docs/examples/widgets/input_validation.py" press="-,2,3"}
    ```

=== "Validation Success"

    ```{.textual path="docs/examples/widgets/input_validation.py" press="4,4"}
    ```

Textual offers several [built-in validators][textual.validation] for common requirements,
but you can easily roll your own by extending [Validator][textual.validation.Validator],
as seen for `Palindrome` in the example above.

#### Validate Empty

If you set `valid_empty=True` then empty values will bypass any validators, and empty values will be considered valid.

## Reactive Attributes

| Name              | Type   | Default  | Description                                                     |
| ----------------- | ------ | -------- | --------------------------------------------------------------- |
| `cursor_blink`    | `bool` | `True`   | True if cursor blinking is enabled.                             |
| `value`           | `str`  | `""`     | The value currently in the text input.                          |
| `cursor_position` | `int`  | `0`      | The index of the cursor in the value string.                    |
| `placeholder`     | `str`  | `""`     | The dimmed placeholder text to display when the input is empty. |
| `password`        | `bool` | `False`  | True if the input should be masked.                             |
| `restrict`        | `str`  | `None`   | Optional regular expression to restrict input.                  |
| `type`            | `str`  | `"text"` | The type of the input.                                          |
| `max_length`      | `int`  | `None`   | Maximum length of the input value.                              |
| `valid_empty`     | `bool` | `False`  | Allow empty values to bypass validation.                        |

## Messages

- [Input.Blurred][textual.widgets.Input.Blurred]
- [Input.Changed][textual.widgets.Input.Changed]
- [Input.Submitted][textual.widgets.Input.Submitted]

## Bindings

The input widget defines the following bindings:

::: textual.widgets.Input.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The input widget provides the following component classes:

::: textual.widgets.Input.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Additional Notes

* The spacing around the text content is due to border. To remove it, set `border: none;` in your CSS.

---


::: textual.widgets.Input
    options:
      heading_level: 2
````

## File: docs/widgets/label.md
````markdown
# Label

!!! tip "Added in version 0.5.0"

A widget which displays static text, but which can also contain more complex Rich renderables.

- [ ] Focusable
- [ ] Container

## Example

The example below shows how you can use a `Label` widget to display some text.

=== "Output"

    ```{.textual path="docs/examples/widgets/label.py"}
    ```

=== "label.py"

    ```python
    --8<-- "docs/examples/widgets/label.py"
    ```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.Label
    options:
      heading_level: 2
````

## File: docs/widgets/link.md
````markdown
# Link

!!! tip "Added in version 0.84.0"

A widget to display a piece of text that opens a URL when clicked, like a web browser link.

- [x] Focusable
- [ ] Container


## Example

A trivial app with a link.
Clicking the link open's a web-browser&mdash;as you might expect!

=== "Output"

    ```{.textual path="docs/examples/widgets/link.py"}
    ```

=== "link.py"

    ```python
    --8<-- "docs/examples/widgets/link.py"
    ```


## Reactive Attributes

| Name   | Type  | Default | Description                               |
| ------ | ----- | ------- | ----------------------------------------- |
| `text` | `str` | `""`    | The text of the link.                     |
| `url`  | `str` | `""`    | The URL to open when the link is clicked. |


## Messages

This widget sends no messages.

## Bindings

The Link widget defines the following bindings:

::: textual.widgets.Link.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false


## Component classes

This widget contains no component classes.



---


::: textual.widgets.Link
    options:
      heading_level: 2
````

## File: docs/widgets/list_item.md
````markdown
# ListItem

!!! tip "Added in version 0.6.0"

`ListItem` is the type of the elements in a `ListView`.

- [ ] Focusable
- [ ] Container

## Example

The example below shows an app with a simple `ListView`, consisting
of multiple `ListItem`s. The arrow keys can be used to navigate the list.

=== "Output"

    ```{.textual path="docs/examples/widgets/list_view.py"}
    ```

=== "list_view.py"

    ```python
    --8<-- "docs/examples/widgets/list_view.py"
    ```

## Reactive Attributes

| Name          | Type   | Default | Description                          |
| ------------- | ------ | ------- | ------------------------------------ |
| `highlighted` | `bool` | `False` | True if this ListItem is highlighted |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.ListItem
    options:
      heading_level: 2
````

## File: docs/widgets/list_view.md
````markdown
# ListView

!!! tip "Added in version 0.6.0"

Displays a vertical list of `ListItem`s which can be highlighted and selected.
Supports keyboard navigation.

- [x] Focusable
- [x] Container

## Example

The example below shows an app with a simple `ListView`.

=== "Output"

    ```{.textual path="docs/examples/widgets/list_view.py"}
    ```

=== "list_view.py"

    ```python
    --8<-- "docs/examples/widgets/list_view.py"
    ```

=== "list_view.tcss"

    ```css
    --8<-- "docs/examples/widgets/list_view.tcss"
    ```

## Reactive Attributes

| Name    | Type  | Default | Description                      |
| ------- | ----- | ------- | -------------------------------- |
| `index` | `int` | `0`     | The currently highlighted index. |

## Messages

- [ListView.Highlighted][textual.widgets.ListView.Highlighted]
- [ListView.Selected][textual.widgets.ListView.Selected]

## Bindings

The list view widget defines the following bindings:

::: textual.widgets.ListView.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

This widget has no component classes.

---


::: textual.widgets.ListView
    options:
      heading_level: 2
````

## File: docs/widgets/loading_indicator.md
````markdown
# LoadingIndicator

!!! tip "Added in version 0.15.0"

Displays pulsating dots to indicate when data is being loaded.

- [ ] Focusable
- [ ] Container


!!! tip

    Widgets have a [`loading`][textual.widget.Widget.loading] reactive which
    you can use to temporarily replace your widget with a `LoadingIndicator`.
    See the [Loading Indicator](../guide/widgets.md#loading-indicator) section
    in the Widgets guide for details.


## Example

Simple usage example:

=== "Output"

    ```{.textual path="docs/examples/widgets/loading_indicator.py"}
    ```

=== "loading_indicator.py"

    ```python
    --8<-- "docs/examples/widgets/loading_indicator.py"
    ```

## Changing Indicator Color

You can set the color of the loading indicator by setting its `color` style.

Here's how you would do that with CSS:

```css
LoadingIndicator {
    color: red;
}
```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.LoadingIndicator
    options:
      heading_level: 2
````

## File: docs/widgets/log.md
````markdown
# Log

!!! tip "Added in version 0.32.0"

A Log widget displays lines of text which may be appended to in realtime.

Call [Log.write_line][textual.widgets.Log.write_line] to write a line at a time, or [Log.write_lines][textual.widgets.Log.write_lines] to write multiple lines at once. Call [Log.clear][textual.widgets.Log.clear] to clear the Log widget.

!!! tip

    See also [RichLog](../widgets/rich_log.md) which can write more than just text, and supports a number of advanced features.

- [X] Focusable
- [ ] Container

## Example

The example below shows how to write text to a `Log` widget:

=== "Output"

    ```{.textual path="docs/examples/widgets/log.py"}
    ```

=== "log.py"

    ```python
    --8<-- "docs/examples/widgets/log.py"
    ```



## Reactive Attributes

| Name          | Type   | Default | Description                                                  |
| ------------- | ------ | ------- | ------------------------------------------------------------ |
| `max_lines`   | `int`  | `None`  | Maximum number of lines in the log or `None` for no maximum. |
| `auto_scroll` | `bool` | `False` | Scroll to end of log when new lines are added.               |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.


---


::: textual.widgets.Log
    options:
      heading_level: 2
````

## File: docs/widgets/markdown_viewer.md
````markdown
# MarkdownViewer

!!! tip "Added in version 0.11.0"

A Widget to display Markdown content with an optional Table of Contents.

- [x] Focusable
- [ ] Container

!!! note

    This Widget adds browser-like functionality on top of the [Markdown](./markdown.md) widget.


## Example

The following example displays Markdown from a string and a Table of Contents.

=== "Output"

    ```{.textual path="docs/examples/widgets/markdown_viewer.py" columns="100" lines="42"}
    ```

=== "markdown.py"

    ~~~python
    --8<-- "docs/examples/widgets/markdown_viewer.py"
    ~~~

## Reactive Attributes

| Name                     | Type | Default | Description                                                        |
| ------------------------ | ---- | ------- | ------------------------------------------------------------------ |
| `show_table_of_contents` | bool | True    | Whether a Table of Contents should be displayed with the Markdown. |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

## See Also

* [Markdown][textual.widgets.Markdown] code reference



---


::: textual.widgets.MarkdownViewer
    options:
      heading_level: 2


::: textual.widgets.markdown
    options:
      show_root_heading: true
      show_root_toc_entry: true
````

## File: docs/widgets/markdown.md
````markdown
# Markdown

!!! tip "Added in version 0.11.0"

A widget to display a Markdown document.

- [ ] Focusable
- [ ] Container


!!! tip

    See [MarkdownViewer](./markdown_viewer.md) for a widget that adds additional features such as a Table of Contents.

## Example

The following example displays Markdown from a string.

=== "Output"

    ```{.textual path="docs/examples/widgets/markdown.py"}
    ```

=== "markdown.py"

    ~~~python
    --8<-- "docs/examples/widgets/markdown.py"
    ~~~

## Reactive Attributes

This widget has no reactive attributes.

## Messages

- [Markdown.TableOfContentsUpdated][textual.widgets.Markdown.TableOfContentsUpdated]
- [Markdown.TableOfContentsSelected][textual.widgets.Markdown.TableOfContentsSelected]
- [Markdown.LinkClicked][textual.widgets.Markdown.LinkClicked]

## Bindings

This widget has no bindings.

## Component Classes

The markdown widget provides the following component classes:

::: textual.widgets.Markdown.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false


## See Also


* [MarkdownViewer][textual.widgets.MarkdownViewer] code reference


---


::: textual.widgets.Markdown
    options:
      heading_level: 2
````

## File: docs/widgets/masked_input.md
````markdown
# MaskedInput

!!! tip "Added in version 0.80.0"

A masked input derived from `Input`, allowing to restrict user input and give visual aid via a simple template mask, which also acts as an implicit *[validator][textual.validation.Validator]*.

- [x] Focusable
- [ ] Container

## Example

The example below shows a masked input to ease entering a credit card number.

=== "Output"

    ```{.textual path="docs/examples/widgets/masked_input.py"}
    ```

=== "masked_input.py"

    ```python hl_lines="6-13 25"
    --8<-- "docs/examples/widgets/masked_input.py"
    ```

    1. Textual offers default styling for the `-invalid` CSS class (a red border), which is automatically applied to the `MaskedInput` when validation fails. We can also provide custom styling for the `-valid` class, as seen here. In this case, we add a green border around the `MaskedInput` to indicate successful validation.
    2. This example shows how to define a template mask for a credit card number, which requires 16 digits in groups of 4.

## Reactive Attributes

| Name       | Type  | Default | Description               |
| ---------- | ----- | ------- | ------------------------- |
| `template` | `str` | `""`    | The template mask string. |

### The template string format

A `MaskedInput` template length defines the maximum length of the input value. Each character of the mask defines a regular expression used to restrict what the user can insert in the corresponding position, and whether the presence of the character in the user input is required for the `MaskedInput` value to be considered valid, according to the following table:

| Mask character | Regular expression | Required? |
| -------------- | ------------------ | --------- |
| `A`            | `[A-Za-z]`         | Yes       |
| `a`            | `[A-Za-z]`         | No        |
| `N`            | `[A-Za-z0-9]`      | Yes       |
| `n`            | `[A-Za-z0-9]`      | No        |
| `X`            | `[^ ]`             | Yes       |
| `x`            | `[^ ]`             | No        |
| `9`            | `[0-9]`            | Yes       |
| `0`            | `[0-9]`            | No        |
| `D`            | `[1-9]`            | Yes       |
| `d`            | `[1-9]`            | No        |
| `#`            | `[0-9+\-]`         | No        |
| `H`            | `[A-Fa-f0-9]`      | Yes       |
| `h`            | `[A-Fa-f0-9]`      | No        |
| `B`            | `[0-1]`            | Yes       |
| `b`            | `[0-1]`            | No        |

There are some special characters that can be used to control automatic case conversion during user input: `>` converts all subsequent user input to uppercase; `<` to lowercase; `!` disables automatic case conversion. Any other character that appears in the template mask is assumed to be a separator, which is a character that is automatically inserted when user reaches its position. All mask characters can be escaped by placing `\` in front of them, allowing any character to be used as separator.
The mask can be terminated by `;c`, where `c` is any character you want to be used as placeholder character. The `placeholder` parameter inherited by `Input` can be used to override this allowing finer grain tuning of the placeholder string.

## Messages

- [MaskedInput.Changed][textual.widgets.MaskedInput.Changed]
- [MaskedInput.Submitted][textual.widgets.MaskedInput.Submitted]

## Bindings

The masked input widget defines the following bindings:

::: textual.widgets.MaskedInput.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The masked input widget provides the following component classes:

::: textual.widgets.MaskedInput.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

---


::: textual.widgets.MaskedInput
    options:
      heading_level: 2
````

## File: docs/widgets/option_list.md
````markdown
# OptionList

!!! tip "Added in version 0.17.0"

A widget for showing a vertical list of Rich renderable options.

- [x] Focusable
- [ ] Container

## Examples

### Options as simple strings

An `OptionList` can be constructed with a simple collection of string
options:

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_strings.py"}
    ```

=== "option_list_strings.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_strings.py"
    ~~~

=== "option_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/option_list.tcss"
    ~~~

### Options as `Option` instances

For finer control over the options, the `Option` class can be used; this
allows for setting IDs, setting initial disabled state, etc. The `Separator`
class can be used to add separator lines between options.

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_options.py"}
    ```

=== "option_list_options.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_options.py"
    ~~~

=== "option_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/option_list.tcss"
    ~~~

### Options as Rich renderables

Because the prompts for the options can be [Rich
renderables](https://rich.readthedocs.io/en/latest/protocol.html), this
means they can be any height you wish. As an example, here is an option list
comprised of [Rich
tables](https://rich.readthedocs.io/en/latest/tables.html):

=== "Output"

    ```{.textual path="docs/examples/widgets/option_list_tables.py"}
    ```

=== "option_list_tables.py"

    ~~~python
    --8<-- "docs/examples/widgets/option_list_tables.py"
    ~~~

=== "option_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/option_list.tcss"
    ~~~

## Reactive Attributes

| Name          | Type            | Default | Description                                                               |
| ------------- | --------------- | ------- | ------------------------------------------------------------------------- |
| `highlighted` | `int` \| `None` | `None`  | The index of the highlighted option. `None` means nothing is highlighted. |

## Messages

- [OptionList.OptionHighlighted][textual.widgets.OptionList.OptionHighlighted]
- [OptionList.OptionSelected][textual.widgets.OptionList.OptionSelected]

Both of the messages above inherit from the common base [`OptionList.OptionMessage`][textual.widgets.OptionList.OptionMessage], so refer to its documentation to see what attributes are available.

## Bindings

The option list widget defines the following bindings:

::: textual.widgets.OptionList.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The option list provides the following component classes:

::: textual.widgets.OptionList.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false



::: textual.widgets.OptionList
    options:
      heading_level: 2


::: textual.widgets.option_list
    options:
      heading_level: 2
````

## File: docs/widgets/placeholder.md
````markdown
# Placeholder

!!! tip "Added in version 0.6.0"

A widget that is meant to have no complex functionality.
Use the placeholder widget when studying the layout of your app before having to develop your custom widgets.

The placeholder widget has variants that display different bits of useful information.
Clicking a placeholder will cycle through its variants.

- [ ] Focusable
- [ ] Container

## Example

The example below shows each placeholder variant.

=== "Output"

    ```{.textual path="docs/examples/widgets/placeholder.py"}
    ```

=== "placeholder.py"

    ```python
    --8<-- "docs/examples/widgets/placeholder.py"
    ```

=== "placeholder.tcss"

    ```css
    --8<-- "docs/examples/widgets/placeholder.tcss"
    ```

## Reactive Attributes

| Name      | Type  | Default     | Description                                        |
| --------- | ----- | ----------- | -------------------------------------------------- |
| `variant` | `str` | `"default"` | Styling variant. One of `default`, `size`, `text`. |


## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.Placeholder
    options:
      heading_level: 2
````

## File: docs/widgets/pretty.md
````markdown
# Pretty

Display a pretty-formatted object.

- [ ] Focusable
- [ ] Container

## Example

The example below shows a pretty-formatted `dict`, but `Pretty` can display any Python object.

=== "Output"

    ```{.textual path="docs/examples/widgets/pretty.py"}
    ```

=== "pretty.py"

    ```python
    --8<-- "docs/examples/widgets/pretty.py"
    ```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.Pretty
    options:
        heading_level: 2
````

## File: docs/widgets/progress_bar.md
````markdown
# ProgressBar


A widget that displays progress on a time-consuming task.

- [ ] Focusable
- [ ] Container

## Examples

### Progress Bar in Isolation

The example below shows a progress bar in isolation.
It shows the progress bar in:

 - its indeterminate state, when the `total` progress hasn't been set yet;
 - the middle of the progress; and
 - the completed state.

=== "Indeterminate state"

    ```{.textual path="docs/examples/widgets/progress_bar_isolated_.py" press="f"}
    ```

=== "39% done"

    ```{.textual path="docs/examples/widgets/progress_bar_isolated_.py" press="t"}
    ```

=== "Completed"

    ```{.textual path="docs/examples/widgets/progress_bar_isolated_.py" press="u"}
    ```

=== "progress_bar_isolated.py"

    ```python
    --8<-- "docs/examples/widgets/progress_bar_isolated.py"
    ```

### Complete App Example

The example below shows a simple app with a progress bar that is keeping track of a fictitious funding level for an organisation.

=== "Output"

    ```{.textual path="docs/examples/widgets/progress_bar.py"}
    ```

=== "Output (partial funding)"

    ```{.textual path="docs/examples/widgets/progress_bar.py" press="1,5,enter,2,0,enter"}
    ```

=== "Output (full funding)"

    ```{.textual path="docs/examples/widgets/progress_bar.py" press="1,5,enter,2,0,enter,6,5,enter"}
    ```

=== "progress_bar.py"

    ```python hl_lines="15"
    --8<-- "docs/examples/widgets/progress_bar.py"
    ```

    1. We create a progress bar with a total of `100` steps and we hide the ETA countdown because we are not keeping track of a continuous, uninterrupted task.

=== "progress_bar.tcss"

    ```css
    --8<-- "docs/examples/widgets/progress_bar.tcss"
    ```

### Gradient Bars

Progress bars support an optional `gradient` parameter, which renders a smooth gradient rather than a solid bar.
To use a gradient, create and set a [Gradient][textual.color.Gradient] object on the ProgressBar widget.

!!! note

    Setting a gradient will override styles set in CSS.

Here's an example:

=== "Output"

    ```{.textual path="docs/examples/widgets/progress_bar_gradient.py"}
    ```

=== "progress_bar_gradient.py"

    ```python hl_lines="11-23 27"
    --8<-- "docs/examples/widgets/progress_bar_gradient.py"
    ```

### Custom Styling

This shows a progress bar with custom styling.
Refer to the [section below](#styling-the-progress-bar) for more information.

=== "Indeterminate state"

    ```{.textual path="docs/examples/widgets/progress_bar_styled_.py" press="f"}
    ```

=== "39% done"

    ```{.textual path="docs/examples/widgets/progress_bar_styled_.py" press="t"}
    ```

=== "Completed"

    ```{.textual path="docs/examples/widgets/progress_bar_styled_.py" press="u"}
    ```

=== "progress_bar_styled.py"

    ```python
    --8<-- "docs/examples/widgets/progress_bar_styled.py"
    ```

=== "progress_bar_styled.tcss"

    ```css
    --8<-- "docs/examples/widgets/progress_bar_styled.tcss"
    ```

## Styling the Progress Bar

The progress bar is composed of three sub-widgets that can be styled independently:

| Widget name        | ID            | Description                                                      |
| ------------------ | ------------- | ---------------------------------------------------------------- |
| `Bar`              | `#bar`        | The bar that visually represents the progress made.              |
| `PercentageStatus` | `#percentage` | [Label](./label.md) that shows the percentage of completion.     |
| `ETAStatus`        | `#eta`        | [Label](./label.md) that shows the estimated time to completion. |

### Bar Component Classes

::: textual.widgets._progress_bar.Bar.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Reactive Attributes

| Name         | Type    | Default | Description                                                                                             |
| ------------ | ------- | ------- | ------------------------------------------------------------------------------------------------------- |
| `percentage` | `float  | None`   | The read-only percentage of progress that has been made. This is `None` if the `total` hasn't been set. |
| `progress`   | `float` | `0`     | The number of steps of progress already made.                                                           |
| `total`      | `float  | None`   | The total number of steps that we are keeping track of.                                                 |

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---

::: textual.widgets.ProgressBar
    options:
      heading_level: 2
````

## File: docs/widgets/radiobutton.md
````markdown
# RadioButton

!!! tip "Added in version 0.13.0"

A simple radio button which stores a boolean value.

- [x] Focusable
- [ ] Container

A radio button is best used with others inside a [`RadioSet`](./radioset.md).

## Example

The example below shows radio buttons, used within a [`RadioSet`](./radioset.md).

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_button.py"}
    ```

=== "radio_button.py"

    ```python
    --8<-- "docs/examples/widgets/radio_button.py"
    ```

=== "radio_button.tcss"

    ```css
    --8<-- "docs/examples/widgets/radio_button.tcss"
    ```

## Reactive Attributes

| Name    | Type   | Default | Description                    |
| ------- | ------ | ------- | ------------------------------ |
| `value` | `bool` | `False` | The value of the radio button. |

## Messages

- [RadioButton.Changed][textual.widgets.RadioButton.Changed]

## Bindings

The radio button widget defines the following bindings:

::: textual.widgets._toggle_button.ToggleButton.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The checkbox widget inherits the following component classes:

::: textual.widgets._toggle_button.ToggleButton.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## See Also

- [RadioSet](./radioset.md)

---


::: textual.widgets.RadioButton
    options:
      heading_level: 2
````

## File: docs/widgets/radioset.md
````markdown
# RadioSet

!!! tip "Added in version 0.13.0"

A container widget that groups [`RadioButton`](./radiobutton.md)s together.

- [ ] Focusable
- [x] Container

## Example

### Simple example

The example below shows two radio sets, one built using a collection of
[radio buttons](./radiobutton.md), the other a collection of simple strings.

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_set.py"}
    ```

=== "radio_set.py"

    ```python
    --8<-- "docs/examples/widgets/radio_set.py"
    ```

=== "radio_set.tcss"

    ```css
    --8<-- "docs/examples/widgets/radio_set.tcss"
    ```

### Reacting to Changes in a Radio Set

Here is an example of using the message to react to changes in a `RadioSet`:

=== "Output"

    ```{.textual path="docs/examples/widgets/radio_set_changed.py" press="enter"}
    ```

=== "radio_set_changed.py"

    ```python
    --8<-- "docs/examples/widgets/radio_set_changed.py"
    ```

=== "radio_set_changed.tcss"

    ```css
    --8<-- "docs/examples/widgets/radio_set_changed.tcss"
    ```

## Messages

-  [RadioSet.Changed][textual.widgets.RadioSet.Changed]

## Bindings

The `RadioSet` widget defines the following bindings:

::: textual.widgets.RadioSet.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

This widget has no component classes.

## See Also


- [RadioButton](./radiobutton.md)

---


::: textual.widgets.RadioSet
    options:
      heading_level: 2
````

## File: docs/widgets/rich_log.md
````markdown
# RichLog

A RichLog is a widget which displays scrollable content that may be appended to in realtime.

Call [RichLog.write][textual.widgets.RichLog.write] with a string or [Rich Renderable](https://rich.readthedocs.io/en/latest/protocol.html) to write content to the end of the RichLog. Call [RichLog.clear][textual.widgets.RichLog.clear] to clear the content.

!!! tip

    See also [Log](../widgets/log.md) which is an alternative to `RichLog` but specialized for simple text.

- [X] Focusable
- [ ] Container

## Example

The example below shows an application showing a `RichLog` with different kinds of data logged.

=== "Output"

    ```{.textual path="docs/examples/widgets/rich_log.py" press="H,i"}
    ```

=== "rich_log.py"

    ```python
    --8<-- "docs/examples/widgets/rich_log.py"
    ```



## Reactive Attributes

| Name        | Type   | Default | Description                                                  |
| ----------- | ------ | ------- | ------------------------------------------------------------ |
| `highlight` | `bool` | `False` | Automatically highlight content.                             |
| `markup`    | `bool` | `False` | Apply markup.                                                |
| `max_lines` | `int`  | `None`  | Maximum number of lines in the log or `None` for no maximum. |
| `min_width` | `int`  | 78      | Minimum width of renderables.                                |
| `wrap`      | `bool` | `False` | Enable word wrapping.                                        |

## Messages

This widget sends no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.


---


::: textual.widgets.RichLog
    options:
      heading_level: 2
````

## File: docs/widgets/rule.md
````markdown
# Rule

A rule widget to separate content, similar to a `<hr>` HTML tag.

- [ ] Focusable
- [ ] Container

## Examples

### Horizontal Rule

The default orientation of a rule is horizontal.

The example below shows horizontal rules with all the available line styles.

=== "Output"

    ```{.textual path="docs/examples/widgets/horizontal_rules.py"}
    ```

=== "horizontal_rules.py"

    ```python
    --8<-- "docs/examples/widgets/horizontal_rules.py"
    ```

=== "horizontal_rules.tcss"

    ```css
    --8<-- "docs/examples/widgets/horizontal_rules.tcss"
    ```

### Vertical Rule

The example below shows vertical rules with all the available line styles.

=== "Output"

    ```{.textual path="docs/examples/widgets/vertical_rules.py"}
    ```

=== "vertical_rules.py"

    ```python
    --8<-- "docs/examples/widgets/vertical_rules.py"
    ```

=== "vertical_rules.tcss"

    ```css
    --8<-- "docs/examples/widgets/vertical_rules.tcss"
    ```

## Reactive Attributes

| Name          | Type              | Default        | Description                  |
| ------------- | ----------------- | -------------- | ---------------------------- |
| `orientation` | `RuleOrientation` | `"horizontal"` | The orientation of the rule. |
| `line_style`  | `LineStyle`       | `"solid"`      | The line style of the rule.  |

## Messages

This widget sends no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

---


::: textual.widgets.Rule
    options:
      heading_level: 2

::: textual.widgets.rule
    options:
      show_root_heading: true
      show_root_toc_entry: true
````

## File: docs/widgets/select.md
````markdown
# Select

!!! tip "Added in version 0.24.0"

A Select widget is a compact control to allow the user to select between a number of possible options.


- [X] Focusable
- [ ] Container


The options in a select control may be passed into the constructor or set later with [set_options][textual.widgets.Select.set_options].
Options should be given as a sequence of tuples consisting of two values: the first is the string (or [Rich Renderable](https://rich.readthedocs.io/en/latest/protocol.html)) to display in the control and list of options, the second is the value of option.

The value of the currently selected option is stored in the `value` attribute of the widget, and the `value` attribute of the [Changed][textual.widgets.Select.Changed] message.


## Typing

The `Select` control is a typing Generic which allows you to set the type of the option values.
For instance, if the data type for your values is an integer, you would type the widget as follows:

```python
options = [("First", 1), ("Second", 2)]
my_select: Select[int] =  Select(options)
```

!!! note

    Typing is entirely optional.

    If you aren't familiar with typing or don't want to worry about it right now, feel free to ignore it.

## Examples

### Basic Example

The following example presents a `Select` with a number of options.

=== "Output"

    ```{.textual path="docs/examples/widgets/select_widget.py"}
    ```

=== "Output (expanded)"

    ```{.textual path="docs/examples/widgets/select_widget.py" press="tab,enter,down,down"}
    ```

=== "select_widget.py"

    ```python
    --8<-- "docs/examples/widgets/select_widget.py"
    ```

=== "select.tcss"

    ```css
    --8<-- "docs/examples/widgets/select.tcss"
    ```

### Example using Class Method

The following example presents a `Select` created using the `from_values` class method.

=== "Output"

    ```{.textual path="docs/examples/widgets/select_from_values_widget.py"}
    ```

=== "Output (expanded)"

    ```{.textual path="docs/examples/widgets/select_from_values_widget.py" press="tab,enter,down,down"}
    ```


=== "select_from_values_widget.py"

    ```python
    --8<-- "docs/examples/widgets/select_from_values_widget.py"
    ```

=== "select.tcss"

    ```css
    --8<-- "docs/examples/widgets/select.tcss"
    ```

## Blank state

The `Select` widget has an option `allow_blank` for its constructor.
If set to `True`, the widget may be in a state where there is no selection, in which case its value will be the special constant [`Select.BLANK`][textual.widgets.Select.BLANK].
The auxiliary methods [`Select.is_blank`][textual.widgets.Select.is_blank] and [`Select.clear`][textual.widgets.Select.clear] provide a convenient way to check if the widget is in this state and to set this state, respectively.

## Type to search

The `Select` widget has a `type_to_search` attribute which allows you to type to move the cursor to a matching option when the widget is expanded. To disable this behavior, set the attribute to `False`.

## Reactive Attributes

| Name       | Type                           | Default                                        | Description                         |
|------------|--------------------------------|------------------------------------------------|-------------------------------------|
| `expanded` | `bool`                         | `False`                                        | True to expand the options overlay. |
| `value`    | `SelectType` \| `_NoSelection` | [`Select.BLANK`][textual.widgets.Select.BLANK] | Current value of the Select.        |

## Messages

-  [Select.Changed][textual.widgets.Select.Changed]

## Bindings

The Select widget defines the following bindings:

::: textual.widgets.Select.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

This widget has no component classes.

---


::: textual.widgets.Select
    options:
      heading_level: 2

::: textual.widgets.select
    options:
      heading_level: 2
````

## File: docs/widgets/selection_list.md
````markdown
# SelectionList

!!! tip "Added in version 0.27.0"

A widget for showing a vertical list of selectable options.

- [x] Focusable
- [ ] Container

## Typing

The `SelectionList` control is a
[`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic),
which allows you to set the type of the
[selection values][textual.widgets.selection_list.Selection.value]. For instance, if
the data type for your values is an integer, you would type the widget as
follows:

```python
selections = [("First", 1), ("Second", 2)]
my_selection_list: SelectionList[int] =  SelectionList(*selections)
```

!!! note

    Typing is entirely optional.

    If you aren't familiar with typing or don't want to worry about it right now, feel free to ignore it.

## Examples

A selection list is designed to be built up of single-line prompts (which
can be [Rich `Text`](https://rich.readthedocs.io/en/stable/text.html)) and
an associated unique value.

### Selections as tuples

A selection list can be built with tuples, either of two or three values in
length. Each tuple must contain a prompt and a value, and it can also
optionally contain a flag for the initial selected state of the option.

=== "Output"

    ```{.textual path="docs/examples/widgets/selection_list_tuples.py"}
    ```

=== "selection_list_tuples.py"

    ~~~python
    --8<-- "docs/examples/widgets/selection_list_tuples.py"
    ~~~

    1. Note that the `SelectionList` is typed as `int`, for the type of the values.

=== "selection_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/selection_list.tcss"
    ~~~

### Selections as Selection objects

Alternatively, selections can be passed in as
[`Selection`][textual.widgets.selection_list.Selection]s:

=== "Output"

    ```{.textual path="docs/examples/widgets/selection_list_selections.py"}
    ```

=== "selection_list_selections.py"

    ~~~python
    --8<-- "docs/examples/widgets/selection_list_selections.py"
    ~~~

    1. Note that the `SelectionList` is typed as `int`, for the type of the values.

=== "selection_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/selection_list.tcss"
    ~~~

### Handling changes to the selections

Most of the time, when using the `SelectionList`, you will want to know when
the collection of selected items has changed; this is ideally done using the
[`SelectedChanged`][textual.widgets.SelectionList.SelectedChanged] message.
Here is an example of using that message to update a `Pretty` with the
collection of selected values:

=== "Output"

    ```{.textual path="docs/examples/widgets/selection_list_selected.py"}
    ```

=== "selection_list_selections.py"

    ~~~python
    --8<-- "docs/examples/widgets/selection_list_selected.py"
    ~~~

    1. Note that the `SelectionList` is typed as `str`, for the type of the values.

=== "selection_list.tcss"

    ~~~css
    --8<-- "docs/examples/widgets/selection_list_selected.tcss"
    ~~~

## Reactive Attributes

| Name          | Type            | Default | Description                                                                  |
|---------------|-----------------|---------|------------------------------------------------------------------------------|
| `highlighted` | `int` \| `None` | `None`  | The index of the highlighted selection. `None` means nothing is highlighted. |

## Messages

- [SelectionList.SelectionHighlighted][textual.widgets.SelectionList.SelectionHighlighted]
- [SelectionList.SelectionToggled][textual.widgets.SelectionList.SelectionToggled]
- [SelectionList.SelectedChanged][textual.widgets.SelectionList.SelectedChanged]

## Bindings

The selection list widget defines the following bindings:

::: textual.widgets.SelectionList.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

It inherits from [`OptionList`][textual.widgets.OptionList]
and so also inherits the following bindings:

::: textual.widgets.OptionList.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The selection list provides the following component classes:

::: textual.widgets.SelectionList.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

It inherits from [`OptionList`][textual.widgets.OptionList] and so also
makes use of the following component classes:

::: textual.widgets.OptionList.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

::: textual.widgets.SelectionList
    options:
      heading_level: 2

::: textual.widgets.selection_list
    options:
      heading_level: 2
````

## File: docs/widgets/sparkline.md
````markdown
# Sparkline

!!! tip "Added in version 0.27.0"

A widget that is used to visually represent numerical data.

- [ ] Focusable
- [ ] Container

## Examples

### Basic example

The example below illustrates the relationship between the data, its length, the width of the sparkline, and the number of bars displayed.

!!! tip

    The sparkline data is split into equally-sized chunks.
    Each chunk is represented by a bar and the width of the sparkline dictates how many bars there are.

=== "Output"

    ```{.textual path="docs/examples/widgets/sparkline_basic.py" lines="5" columns="30"}
    ```

=== "sparkline_basic.py"

    ```python hl_lines="4 11 12 13"
    --8<-- "docs/examples/widgets/sparkline_basic.py"
    ```

    1. We have 12 data points.
    2. This sparkline will have its width set to 3 via CSS.
    3. The data (12 numbers) will be split across 3 bars, so 4 data points are associated with each bar.
    4. Each bar will represent its largest value.
    The largest value of each chunk is 2, 4, and 8, respectively.
    That explains why the first bar is half the height of the second and the second bar is half the height of the third.

=== "sparkline_basic.tcss"

    ```css
    --8<-- "docs/examples/widgets/sparkline_basic.tcss"
    ```

    1. By setting the width to 3 we get three buckets.

### Different summary functions

The example below shows a sparkline widget with different summary functions.
The summary function is what determines the height of each bar.

=== "Output"

    ```{.textual path="docs/examples/widgets/sparkline.py" lines="11"}
    ```

=== "sparkline.py"

    ```python hl_lines="15-17"
    --8<-- "docs/examples/widgets/sparkline.py"
    ```

    1. Each bar will show the largest value of that bucket.
    2. Each bar will show the mean value of that bucket.
    3. Each bar will show the smaller value of that bucket.

=== "sparkline.tcss"

    ```css
    --8<-- "docs/examples/widgets/sparkline.tcss"
    ```

### Changing the colors

The example below shows how to use component classes to change the colors of the sparkline.

=== "Output"

    ```{.textual path="docs/examples/widgets/sparkline_colors.py" lines=22}
    ```

=== "sparkline_colors.py"

    ```python
    --8<-- "docs/examples/widgets/sparkline_colors.py"
    ```

=== "sparkline_colors.tcss"

    ```css
    --8<-- "docs/examples/widgets/sparkline_colors.tcss"
    ```


## Reactive Attributes

| Name      | Type  | Default     | Description                                        |
| --------- | ----- | ----------- | -------------------------------------------------- |
| `data` | `Sequence[float] | None` | `None` | The data represented by the sparkline. |
| `summary_function` | `Callable[[Sequence[float]], float]` | `max` | The function that computes the height of each bar. |


## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

The sparkline widget provides the following component classes:

::: textual.widgets.Sparkline.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

---


::: textual.widgets.Sparkline
    options:
      heading_level: 2
````

## File: docs/widgets/static.md
````markdown
# Static

A widget which displays static content.
Can be used for Rich renderables and can also be the base for other types of widgets.

- [ ] Focusable
- [ ] Container

## Example

The example below shows how you can use a `Static` widget as a simple text label (but see [Label](./label.md) as a way of displaying text).

=== "Output"

    ```{.textual path="docs/examples/widgets/static.py"}
    ```

=== "static.py"

    ```python
    --8<-- "docs/examples/widgets/static.py"
    ```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

## See Also

* [Label](./label.md)
* [Pretty](./pretty.md)


---


::: textual.widgets.Static
    options:
      heading_level: 2
````

## File: docs/widgets/switch.md
````markdown
# Switch

A simple switch widget which stores a boolean value.

- [x] Focusable
- [ ] Container

## Example

The example below shows switches in various states.

=== "Output"

    ```{.textual path="docs/examples/widgets/switch.py"}
    ```

=== "switch.py"

    ```python
    --8<-- "docs/examples/widgets/switch.py"
    ```

=== "switch.tcss"

    ```css
    --8<-- "docs/examples/widgets/switch.tcss"
    ```

## Reactive Attributes

| Name    | Type   | Default | Description              |
| ------- | ------ | ------- | ------------------------ |
| `value` | `bool` | `False` | The value of the switch. |

## Messages

- [Switch.Changed][textual.widgets.Switch.Changed]

## Bindings

The switch widget defines the following bindings:

::: textual.widgets.Switch.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The switch widget provides the following component classes:

::: textual.widgets.Switch.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Additional Notes

- To remove the spacing around a `Switch`, set `border: none;` and `padding: 0;`.

---


::: textual.widgets.Switch
    options:
      heading_level: 2
````

## File: docs/widgets/tabbed_content.md
````markdown
# TabbedContent

!!! tip "Added in version 0.16.0"

Switch between mutually exclusive content panes via a row of tabs.

- [x] Focusable
- [x] Container

This widget combines the [Tabs](../widgets/tabs.md) and [ContentSwitcher](../widgets/content_switcher.md) widgets to create a convenient way of navigating content.

Only a single child of TabbedContent is visible at once.
Each child has an associated tab which will make it visible and hide the others.

## Composing

There are two ways to provide the titles for the tab.
You can pass them as positional arguments to the [TabbedContent][textual.widgets.TabbedContent] constructor:

```python
def compose(self) -> ComposeResult:
    with TabbedContent("Leto", "Jessica", "Paul"):
        yield Markdown(LETO)
        yield Markdown(JESSICA)
        yield Markdown(PAUL)
```

Alternatively you can wrap the content in a [TabPane][textual.widgets.TabPane] widget, which takes the tab title as the first parameter:

```python
def compose(self) -> ComposeResult:
    with TabbedContent():
        with TabPane("Leto"):
            yield Markdown(LETO)
        with TabPane("Jessica"):
            yield Markdown(JESSICA)
        with TabPane("Paul"):
            yield Markdown(PAUL)
```

## Switching tabs

If you need to programmatically switch tabs, you should provide an `id` attribute to the `TabPane`s.

```python
def compose(self) -> ComposeResult:
    with TabbedContent():
        with TabPane("Leto", id="leto"):
            yield Markdown(LETO)
        with TabPane("Jessica", id="jessica"):
            yield Markdown(JESSICA)
        with TabPane("Paul", id="paul"):
            yield Markdown(PAUL)
```

You can then switch tabs by setting the `active` reactive attribute:

```python
# Switch to Jessica tab
self.query_one(TabbedContent).active = "jessica"
```

!!! note

    If you don't provide `id` attributes to the tab panes, they will be assigned sequentially starting at `tab-1` (then `tab-2` etc).

## Initial tab

The first child of `TabbedContent` will be the initial active tab by default. You can pick a different initial tab by setting the `initial` argument to the `id` of the tab:

```python
def compose(self) -> ComposeResult:
    with TabbedContent(initial="jessica"):
        with TabPane("Leto", id="leto"):
            yield Markdown(LETO)
        with TabPane("Jessica", id="jessica"):
            yield Markdown(JESSICA)
        with TabPane("Paul", id="paul"):
            yield Markdown(PAUL)
```

## Example

The following example contains a `TabbedContent` with three tabs.

=== "Output"

    ```{.textual path="docs/examples/widgets/tabbed_content.py"}
    ```

=== "tabbed_content.py"

    ```python
    --8<-- "docs/examples/widgets/tabbed_content.py"
    ```

## Styling

The `TabbedContent` widget is composed of two main sub-widgets: a
[`Tabs`](tabs.md) and a [`ContentSwitcher`](content_switcher.md); you can
style them accordingly.

The tabs within the `Tabs` widget will have prefixed IDs; each ID being the
ID of the `TabPane` the `Tab` is for, prefixed with `--content-tab-`. If you
wish to style individual tabs within the `TabbedContent` widget you will
need to use that prefix for the `Tab` IDs.

For example, to create a `TabbedContent` that has red and green labels:

=== "Output"

    ```{.textual path="docs/examples/widgets/tabbed_content_label_color.py"}
    ```

=== "tabbed_content.py"

    ```python
    --8<-- "docs/examples/widgets/tabbed_content_label_color.py"
    ```

## Reactive Attributes

| Name     | Type  | Default | Description                                                    |
| -------- | ----- | ------- | -------------------------------------------------------------- |
| `active` | `str` | `""`    | The `id` attribute of the active tab. Set this to switch tabs. |


## Messages

- [TabbedContent.Cleared][textual.widgets.TabbedContent.Cleared]
- [TabbedContent.TabActivated][textual.widgets.TabbedContent.TabActivated]

## Bindings

This widget has no bindings.

## Component Classes

This widget has no component classes.

## See also


- [Tabs](tabs.md)
- [ContentSwitcher](content_switcher.md)


---


::: textual.widgets.TabbedContent
    options:
      heading_level: 2


---


::: textual.widgets.TabPane
    options:
      heading_level: 2
````

## File: docs/widgets/tabs.md
````markdown
# Tabs

!!! tip "Added in version 0.15.0"

Displays a number of tab headers which may be activated with a click or navigated with cursor keys.

- [x] Focusable
- [ ] Container

Construct a `Tabs` widget with strings or [Text][rich.text.Text] objects as positional arguments, which will set the labels in the tabs. Here's an example with three tabs:

```python
def compose(self) -> ComposeResult:
    yield Tabs("First tab", "Second tab", Text.from_markup("[u]Third[/u] tab"))
```

This will create [Tab][textual.widgets.Tab] widgets internally, with auto-incrementing `id` attributes (`"tab-1"`, `"tab-2"` etc).
You can also supply `Tab` objects directly in the constructor, which will allow you to explicitly set an `id`. Here's an example:

```python
def compose(self) -> ComposeResult:
    yield Tabs(
        Tab("First tab", id="one"),
        Tab("Second tab", id="two"),
    )
```

When the user switches to a tab by clicking or pressing keys, then `Tabs` will send a [Tabs.TabActivated][textual.widgets.Tabs.TabActivated] message which contains the `tab` that was activated.
You can then use `event.tab.id` attribute to perform any related actions.

## Clearing tabs

Clear tabs by calling the [clear][textual.widgets.Tabs.clear] method. Clearing the tabs will send a [Tabs.TabActivated][textual.widgets.Tabs.TabActivated] message with the `tab` attribute set to `None`.

## Adding tabs

Tabs may be added dynamically with the [add_tab][textual.widgets.Tabs.add_tab] method, which accepts strings, [Text][rich.text.Text], or [Tab][textual.widgets.Tab] objects.

## Example

The following example adds a `Tabs` widget above a text label. Press ++a++ to add a tab, ++c++ to clear the tabs.

=== "Output"

    ```{.textual path="docs/examples/widgets/tabs.py" press="a,a,a,a,right,right"}
    ```

=== "tabs.py"

    ```python
    --8<-- "docs/examples/widgets/tabs.py"
    ```


## Reactive Attributes

| Name     | Type  | Default | Description                                                                        |
| -------- | ----- | ------- | ---------------------------------------------------------------------------------- |
| `active` | `str` | `""`    | The ID of the active tab. Set this attribute to a tab ID to change the active tab. |


## Messages

- [Tabs.TabActivated][textual.widgets.Tabs.TabActivated]
- [Tabs.Cleared][textual.widgets.Tabs.Cleared]

## Bindings

The Tabs widget defines the following bindings:

::: textual.widgets.Tabs.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

This widget has no component classes.

---


::: textual.widgets.Tabs
    options:
      heading_level: 2


---

::: textual.widgets.Tab
    options:
      heading_level: 2
````

## File: docs/widgets/text_area.md
````markdown
# TextArea

!!! tip

    Added in version 0.38.0. Soft wrapping added in version 0.48.0.

A widget for editing text which may span multiple lines.
Supports text selection, soft wrapping, optional syntax highlighting with tree-sitter
and a variety of keybindings.

- [x] Focusable
- [ ] Container

## Guide

### Code editing vs plain text editing

By default, the `TextArea` widget is a standard multi-line input box with soft-wrapping enabled.

If you're interested in editing code, you may wish to use the [`TextArea.code_editor`][textual.widgets._text_area.TextArea.code_editor] convenience constructor.
This is a method which, by default, returns a new `TextArea` with soft-wrapping disabled, line numbers enabled, and the tab key behavior configured to insert `\t`.

### Syntax highlighting dependencies

To enable syntax highlighting, you'll need to install the `syntax` extra dependencies:

=== "pip"

    ```
    pip install "textual[syntax]"
    ```

=== "poetry"

    ```
    poetry add "textual[syntax]"
    ```

This will install `tree-sitter` and `tree-sitter-languages`.
These packages are distributed as binary wheels, so it may limit your applications ability to run in environments where these wheels are not available.
After installing, you can set the [`language`][textual.widgets._text_area.TextArea.language] reactive attribute on the `TextArea` to enable highlighting.

### Loading text

In this example we load some initial text into the `TextArea`, and set the language to `"python"` to enable syntax highlighting.

=== "Output"

    ```{.textual path="docs/examples/widgets/text_area_example.py" columns="42" lines="8"}
    ```

=== "text_area_example.py"

    ```python
    --8<-- "docs/examples/widgets/text_area_example.py"
    ```

To update the content programmatically, set the [`text`][textual.widgets._text_area.TextArea.text] property to a string value.

To update the parser used for syntax highlighting, set the [`language`][textual.widgets._text_area.TextArea.language] reactive attribute:

```python
# Set the language to Markdown
text_area.language = "markdown"
```

!!! note
    More built-in languages will be added in the future. For now, you can [add your own](#adding-support-for-custom-languages).

### Reading content from `TextArea`

There are a number of ways to retrieve content from the `TextArea`:

- The [`TextArea.text`][textual.widgets._text_area.TextArea.text] property returns all content in the text area as a string.
- The [`TextArea.selected_text`][textual.widgets._text_area.TextArea.selected_text] property returns the text corresponding to the current selection.
- The [`TextArea.get_text_range`][textual.widgets._text_area.TextArea.get_text_range] method returns the text between two locations.

In all cases, when multiple lines of text are retrieved, the [document line separator](#line-separators) will be used.

### Editing content inside `TextArea`

The content of the `TextArea` can be updated using the [`replace`][textual.widgets._text_area.TextArea.replace] method.
This method is the programmatic equivalent of selecting some text and then pasting.

Some other convenient methods are available, such as [`insert`][textual.widgets._text_area.TextArea.insert], [`delete`][textual.widgets._text_area.TextArea.delete], and [`clear`][textual.widgets._text_area.TextArea.clear].

!!! tip
    The `TextArea.document.end` property returns the location at the end of the
    document, which might be convenient when editing programmatically.

### Working with the cursor

#### Moving the cursor

The cursor location is available via the [`cursor_location`][textual.widgets._text_area.TextArea.cursor_location] property, which represents
the location of the cursor as a tuple `(row_index, column_index)`. These indices are zero-based and represent the position of the cursor in the content.
Writing a new value to `cursor_location` will immediately update the location of the cursor.

```python
>>> text_area = TextArea()
>>> text_area.cursor_location
(0, 0)
>>> text_area.cursor_location = (0, 4)
>>> text_area.cursor_location
(0, 4)
```

`cursor_location` is a simple way to move the cursor programmatically, but it doesn't let us select text.

#### Selecting text

To select text, we can use the `selection` reactive attribute.
Let's select the first two lines of text in a document by adding `text_area.selection = Selection(start=(0, 0), end=(2, 0))` to our code:

=== "Output"

    ```{.textual path="docs/examples/widgets/text_area_selection.py" columns="42" lines="8"}
    ```

=== "text_area_selection.py"

    ```python hl_lines="17"
    --8<-- "docs/examples/widgets/text_area_selection.py"
    ```

    1. Selects the first two lines of text.

Note that selections can happen in both directions, so `Selection((2, 0), (0, 0))` is also valid.

!!! tip

    The `end` attribute of the `selection` is always equal to `TextArea.cursor_location`. In other words,
    the `cursor_location` attribute is simply a convenience for accessing `text_area.selection.end`.

#### More cursor utilities

There are a number of additional utility methods available for interacting with the cursor.

##### Location information

Many properties exist on `TextArea` which give information about the current cursor location.
These properties begin with `cursor_at_`, and return booleans.
For example, [`cursor_at_start_of_line`][textual.widgets._text_area.TextArea.cursor_at_start_of_line] tells us if the cursor is at a start of line.

We can also check the location the cursor _would_ arrive at if we were to move it.
For example, [`get_cursor_right_location`][textual.widgets._text_area.TextArea.get_cursor_right_location] returns the location
the cursor would move to if it were to move right.
A number of similar methods exist, with names like `get_cursor_*_location`.

##### Cursor movement methods

The [`move_cursor`][textual.widgets._text_area.TextArea.move_cursor] method allows you to move the cursor to a new location while selecting
text, or move the cursor and scroll to keep it centered.

```python
# Move the cursor from its current location to row index 4,
# column index 8, while selecting all the text between.
text_area.move_cursor((4, 8), select=True)
```

The [`move_cursor_relative`][textual.widgets._text_area.TextArea.move_cursor_relative] method offers a very similar interface, but moves the cursor relative
to its current location.

##### Common selections

There are some methods available which make common selections easier:

- [`select_line`][textual.widgets._text_area.TextArea.select_line] selects a line by index. Bound to ++f6++ by default.
- [`select_all`][textual.widgets._text_area.TextArea.select_all] selects all text. Bound to ++f7++ by default.

### Themes

`TextArea` ships with some builtin themes, and you can easily add your own.

Themes give you control over the look and feel, including syntax highlighting,
the cursor, selection, gutter, and more.

#### Default theme

The default `TextArea` theme is called `css`, which takes its values entirely from CSS.
This means that the default appearance of the widget fits nicely into a standard Textual application,
and looks right on both dark and light mode.

When using the `css` theme, you can make use of [component classes][textual.widgets.TextArea.COMPONENT_CLASSES] to style elements of the `TextArea`.
For example, the CSS code `TextArea .text-area--cursor { background: green; }` will make the cursor `green`.

More complex applications such as code editors may want to use pre-defined themes such as `monokai`.
This involves using a `TextAreaTheme` object, which we cover in detail below.
This allows full customization of the `TextArea`, including syntax highlighting, at the code level.

#### Using builtin themes

The initial theme of the `TextArea` is determined by the `theme` parameter.

```python
# Create a TextArea with the 'dracula' theme.
yield TextArea.code_editor("print(123)", language="python", theme="dracula")
```

You can check which themes are available using the [`available_themes`][textual.widgets._text_area.TextArea.available_themes] property.

```python
>>> text_area = TextArea()
>>> print(text_area.available_themes)
{'css', 'dracula', 'github_light', 'monokai', 'vscode_dark'}
```

After creating a `TextArea`, you can change the theme by setting the [`theme`][textual.widgets._text_area.TextArea.theme]
attribute to one of the available themes.

```python
text_area.theme = "vscode_dark"
```

On setting this attribute the `TextArea` will immediately refresh to display the updated theme.

#### Custom themes

!!! note

    Custom themes are only relevant for people who are looking to customize syntax highlighting.
    If you're only editing plain text, and wish to recolor aspects of the `TextArea`, you should use the [provided component classes][textual.widgets.TextArea.COMPONENT_CLASSES].

Using custom (non-builtin) themes is a two-step process:

1. Create an instance of [`TextAreaTheme`][textual.widgets.text_area.TextAreaTheme].
2. Register it using [`TextArea.register_theme`][textual.widgets._text_area.TextArea.register_theme].

##### 1. Creating a theme

Let's create a simple theme, `"my_cool_theme"`, which colors the cursor <span style="background-color: dodgerblue; color: white; padding: 0 2px;">blue</span>, and the cursor line <span style="background-color: yellow; color: black; padding: 0 2px;">yellow</span>.
Our theme will also syntax highlight strings as <span style="background-color: red; color: white; padding: 0 2px;">red</span>, and comments as <span style="background-color: magenta; color: black; padding: 0 2px;">magenta</span>.

```python
from rich.style import Style
from textual.widgets.text_area import TextAreaTheme
# ...
my_theme = TextAreaTheme(
    # This name will be used to refer to the theme...
    name="my_cool_theme",
    # Basic styles such as background, cursor, selection, gutter, etc...
    cursor_style=Style(color="white", bgcolor="blue"),
    cursor_line_style=Style(bgcolor="yellow"),
    # `syntax_styles` is for syntax highlighting.
    # It maps tokens parsed from the document to Rich styles.
    syntax_styles={
        "string": Style(color="red"),
        "comment": Style(color="magenta"),
    }
)
```

Attributes like `cursor_style` and `cursor_line_style` apply general language-agnostic
styling to the widget.
If you choose not to supply a value for one of these attributes, it will be taken from the CSS component styles.

The `syntax_styles` attribute of `TextAreaTheme` is used for syntax highlighting and
depends on the `language` currently in use.
For more details, see [syntax highlighting](#syntax-highlighting).

If you wish to build on an existing theme, you can obtain a reference to it using the [`TextAreaTheme.get_builtin_theme`][textual.widgets.text_area.TextAreaTheme.get_builtin_theme] classmethod:

```python
from textual.widgets.text_area import TextAreaTheme

monokai = TextAreaTheme.get_builtin_theme("monokai")
```

##### 2. Registering a theme

Our theme can now be registered with the `TextArea` instance.

```python
text_area.register_theme(my_theme)
```

After registering a theme, it'll appear in the `available_themes`:

```python
>>> print(text_area.available_themes)
{'dracula', 'github_light', 'monokai', 'vscode_dark', 'my_cool_theme'}
```

We can now switch to it:

```python
text_area.theme = "my_cool_theme"
```

This immediately updates the appearance of the `TextArea`:

```{.textual path="docs/examples/widgets/text_area_custom_theme.py" columns="42" lines="8"}
```

### Tab and Escape behavior

Pressing the ++tab++ key will shift focus to the next widget in your application by default.
This matches how other widgets work in Textual.

To have ++tab++ insert a `\t` character, set the `tab_behavior` attribute to the string value `"indent"`.
While in this mode, you can shift focus by pressing the ++escape++ key.

### Indentation

The character(s) inserted when you press tab is controlled by setting the `indent_type` attribute to either `tabs` or `spaces`.

If `indent_type == "spaces"`, pressing ++tab++ will insert up to `indent_width` spaces in order to align with the next tab stop.

### Undo and redo

`TextArea` offers `undo` and `redo` methods.
By default, `undo` is bound to <kbd>Ctrl</kbd>+<kbd>Z</kbd> and `redo` to <kbd>Ctrl</kbd>+<kbd>Y</kbd>.

The `TextArea` uses a heuristic to place _checkpoints_ after certain types of edit.
When you call `undo`, all of the edits between now and the most recent checkpoint are reverted.
You can manually add a checkpoint by calling the [`TextArea.history.checkpoint()`][textual.widgets.text_area.EditHistory.checkpoint] instance method.

The undo and redo history uses a stack-based system, where a single item on the stack represents a single checkpoint.
In memory-constrained environments, you may wish to reduce the maximum number of checkpoints that can exist.
You can do this by passing the `max_checkpoints` argument to the `TextArea` constructor.

### Read-only mode

`TextArea.read_only` is a boolean reactive attribute which, if `True`, will prevent users from modifying content in the `TextArea`.

While `read_only=True`, you can still modify the content programmatically.

While this mode is active, the `TextArea` receives the `-read-only` CSS class, which you can use to supply custom styles for read-only mode.

### Line separators

When content is loaded into `TextArea`, the content is scanned from beginning to end
and the first occurrence of a line separator is recorded.

This separator will then be used when content is later read from the `TextArea` via
the `text` property. The `TextArea` widget does not support exporting text which
contains mixed line endings.

Similarly, newline characters pasted into the `TextArea` will be converted.

You can check the line separator of the current document by inspecting `TextArea.document.newline`:

```python
>>> text_area = TextArea()
>>> text_area.document.newline
'\n'
```

### Line numbers

The gutter (column on the left containing line numbers) can be toggled by setting
the `show_line_numbers` attribute to `True` or `False`.

Setting this attribute will immediately repaint the `TextArea` to reflect the new value.

You can also change the start line number (the topmost line number in the gutter) by setting the `line_number_start` reactive attribute.

### Extending `TextArea`

Sometimes, you may wish to subclass `TextArea` to add some extra functionality.
In this section, we'll briefly explore how we can extend the widget to achieve common goals.

#### Hooking into key presses

You may wish to hook into certain key presses to inject some functionality.
This can be done by over-riding `_on_key` and adding the required functionality.

##### Example - closing parentheses automatically

Let's extend `TextArea` to add a feature which automatically closes parentheses and moves the cursor to a sensible location.

```python
--8<-- "docs/examples/widgets/text_area_extended.py"
```

This intercepts the key handler when `"("` is pressed, and inserts `"()"` instead.
It then moves the cursor so that it lands between the open and closing parentheses.

Typing "`def hello(`" into the `TextArea` now results in the bracket automatically being closed:

```{.textual path="docs/examples/widgets/text_area_extended.py" columns="36" lines="4" press="d,e,f,space,h,e,l,l,o,left_parenthesis"}
```

### Advanced concepts

#### Syntax highlighting

Syntax highlighting inside the `TextArea` is powered by a library called [`tree-sitter`](https://tree-sitter.github.io/tree-sitter/).

Each time you update the document in a `TextArea`, an internal syntax tree is updated.
This tree is frequently _queried_ to find location ranges relevant to syntax highlighting.
We give these ranges _names_, and ultimately map them to Rich styles inside `TextAreaTheme.syntax_styles`.

To illustrate how this works, lets look at how the "Monokai" `TextAreaTheme` highlights Markdown files.

When the `language` attribute is set to `"markdown"`, a highlight query similar to the one below is used (trimmed for brevity).

```scheme
(heading_content) @heading
(link) @link
```

This highlight query maps `heading_content` nodes returned by the Markdown parser to the name `@heading`,
and `link` nodes to the name `@link`.

Inside our `TextAreaTheme.syntax_styles` dict, we can map the name `@heading` to a Rich style.
Here's a snippet from the "Monokai" theme which does just that:

```python
TextAreaTheme(
    name="monokai",
    base_style=Style(color="#f8f8f2", bgcolor="#272822"),
    gutter_style=Style(color="#90908a", bgcolor="#272822"),
    # ...
    syntax_styles={
        # Colorise @heading and make them bold
        "heading": Style(color="#F92672", bold=True),
        # Colorise and underline @link
        "link": Style(color="#66D9EF", underline=True),
        # ...
    },
)
```

To understand which names can be mapped inside `syntax_styles`, we recommend looking at the existing
themes and highlighting queries (`.scm` files) in the Textual repository.

!!! tip

    You may also wish to take a look at the contents of `TextArea._highlights` on an
    active `TextArea` instance to see which highlights have been generated for the
    open document.

#### Adding support for custom languages

To add support for a language to a `TextArea`, use the [`register_language`][textual.widgets._text_area.TextArea.register_language] method.

To register a language, we require two things:

1. A tree-sitter `Language` object which contains the grammar for the language.
2. A highlight query which is used for [syntax highlighting](#syntax-highlighting).

##### Example - adding Java support

The easiest way to obtain a `Language` object is using the [`py-tree-sitter-languages`](https://github.com/grantjenks/py-tree-sitter-languages) package. Here's how we can use this package to obtain a reference to a `Language` object representing Java:

```python
from tree_sitter_languages import get_language
java_language = get_language("java")
```

The exact version of the parser used when you call `get_language` can be checked via
the [`repos.txt` file](https://github.com/grantjenks/py-tree-sitter-languages/blob/a6d4f7c903bf647be1bdcfa504df967d13e40427/repos.txt) in
the version of `py-tree-sitter-languages` you're using. This file contains links to the GitHub
repos and commit hashes of the tree-sitter parsers. In these repos you can often find pre-made highlight queries at `queries/highlights.scm`,
and a file showing all the available node types which can be used in highlight queries at `src/node-types.json`.

Since we're adding support for Java, lets grab the Java highlight query from the repo by following these steps:

1. Open [`repos.txt` file](https://github.com/grantjenks/py-tree-sitter-languages/blob/a6d4f7c903bf647be1bdcfa504df967d13e40427/repos.txt) from the `py-tree-sitter-languages` repo.
2. Find the link corresponding to `tree-sitter-java` and go to the repo on GitHub (you may also need to go to the specific commit referenced in `repos.txt`).
3. Go to [`queries/highlights.scm`](https://github.com/tree-sitter/tree-sitter-java/blob/ac14b4b1884102839455d32543ab6d53ae089ab7/queries/highlights.scm) to see the example highlight query for Java.

Be sure to check the license in the repo to ensure it can be freely copied.

!!! warning

    It's important to use a highlight query which is compatible with the parser in use, so
    pay attention to the commit hash when visiting the repo via `repos.txt`.

We now have our `Language` and our highlight query, so we can register Java as a language.

```python
--8<-- "docs/examples/widgets/text_area_custom_language.py"
```

Running our app, we can see that the Java code is highlighted.
We can freely edit the text, and the syntax highlighting will update immediately.

```{.textual path="docs/examples/widgets/text_area_custom_language.py" columns="52" lines="8"}
```

Recall that we map names (like `@heading`) from the tree-sitter highlight query to Rich style objects inside the `TextAreaTheme.syntax_styles` dictionary.
If you notice some highlights are missing after registering a language, the issue may be:

1. The current `TextAreaTheme` doesn't contain a mapping for the name in the highlight query. Adding a new key-value pair to `syntax_styles` should resolve the issue.
2. The highlight query doesn't assign a name to the pattern you expect to be highlighted. In this case you'll need to update the highlight query to assign to the name.

!!! tip

    The names assigned in tree-sitter highlight queries are often reused across multiple languages.
    For example, `@string` is used in many languages to highlight strings.

#### Navigation and wrapping information

If you're building functionality on top of `TextArea`, it may be useful to inspect the `navigator` and `wrapped_document` attributes.

- `navigator` is a [`DocumentNavigator`][textual.widgets.text_area.DocumentNavigator] instance which can give us general information about the cursor's location within a document, as well as where the cursor will move to when certain actions are performed.
- `wrapped_document` is a [`WrappedDocument`][textual.widgets.text_area.WrappedDocument] instance which can be used to convert document locations to visual locations, taking wrapping into account. It also offers a variety of other convenience methods and properties.

A detailed view of these classes is out of scope, but do note that a lot of the functionality of `TextArea` exists within them, so inspecting them could be worthwhile.

## Reactive attributes

| Name                   | Type                     | Default       | Description                                                      |
|------------------------|--------------------------|---------------|------------------------------------------------------------------|
| `language`             | `str | None`             | `None`        | The language to use for syntax highlighting.                     |
| `theme`                | `str`                    | `"css"`       | The theme to use.                                                |
| `selection`            | `Selection`              | `Selection()` | The current selection.                                           |
| `show_line_numbers`    | `bool`                   | `False`       | Show or hide line numbers.                                       |
| `line_number_start`    | `int`                    | `1`           | The start line number in the gutter.                            |
| `indent_width`         | `int`                    | `4`           | The number of spaces to indent and width of tabs.                |
| `match_cursor_bracket` | `bool`                   | `True`        | Enable/disable highlighting matching brackets under cursor.      |
| `cursor_blink`         | `bool`                   | `True`        | Enable/disable blinking of the cursor when the widget has focus. |
| `soft_wrap`            | `bool`                   | `True`        | Enable/disable soft wrapping.                                    |
| `read_only`            | `bool`                   | `False`       | Enable/disable read-only mode.                                   |

## Messages

- [TextArea.Changed][textual.widgets._text_area.TextArea.Changed]
- [TextArea.SelectionChanged][textual.widgets._text_area.TextArea.SelectionChanged]

## Bindings

The `TextArea` widget defines the following bindings:

::: textual.widgets._text_area.TextArea.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component classes

The `TextArea` defines component classes that can style various aspects of the widget.
Styles from the `theme` attribute take priority.

::: textual.widgets.TextArea.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

## See also

- [`Input`][textual.widgets.Input] - single-line text input widget
- [`TextAreaTheme`][textual.widgets.text_area.TextAreaTheme] - theming the `TextArea`
- [`DocumentNavigator`][textual.widgets.text_area.DocumentNavigator] - guides cursor movement 
- [`WrappedDocument`][textual.widgets.text_area.WrappedDocument] - manages wrapping the document 
- [`EditHistory`][textual.widgets.text_area.EditHistory] - manages the undo stack
- The tree-sitter documentation [website](https://tree-sitter.github.io/tree-sitter/).
- The tree-sitter Python bindings [repository](https://github.com/tree-sitter/py-tree-sitter).
- `py-tree-sitter-languages` [repository](https://github.com/grantjenks/py-tree-sitter-languages) (provides binary wheels for a large variety of tree-sitter languages).

## Additional notes

- To remove the outline effect when the `TextArea` is focused, you can set `border: none; padding: 0;` in your CSS.

---

::: textual.widgets._text_area.TextArea
    options:
      heading_level: 2

---

::: textual.widgets.text_area
    options:
      heading_level: 2
````

## File: docs/widgets/toast.md
````markdown
# Toast

!!! tip "Added in version 0.30.0"

A widget which displays a notification message.

- [ ] Focusable
- [ ] Container

!!! warning "Note that `Toast` isn't designed to be used directly in your applications, but it is instead used by [`notify`][textual.app.App.notify] to display a message when using Textual's built-in notification system."

## Styling

You can customize the style of Toasts by targeting the `Toast` [CSS type](../guide/CSS.md#type-selector).
For example:

```scss
Toast {
    padding: 3;
}
```

If you wish to change the location of Toasts, it is possible by targeting the `ToastRack` CSS type.
For example:

```scss
ToastRack {
        align: right top;
}
```

The three severity levels also have corresponding
[classes](../guide/CSS.md#class-name-selector), allowing you to target the
different styles of notification. They are:

- `-information`
- `-warning`
- `-error`

If you wish to tailor the notifications for your application you can add
rules to your CSS like this:

```scss
Toast.-information {
    /* Styling here. */
}

Toast.-warning {
    /* Styling here. */
}

Toast.-error {
    /* Styling here. */
}
```

You can customize just the title wih the `toast--title` class.
The following would make the title italic for an information toast:

```scss
Toast.-information .toast--title {
    text-style: italic;
}

```

## Example

=== "Output"

    ```{.textual path="docs/examples/widgets/toast.py"}
    ```

=== "toast.py"

    ```python
    --8<-- "docs/examples/widgets/toast.py"
    ```

## Reactive Attributes

This widget has no reactive attributes.

## Messages

This widget posts no messages.

## Bindings

This widget has no bindings.

## Component Classes

The toast widget provides the following component classes:

::: textual.widgets._toast.Toast.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false

---

::: textual.widgets._toast.Toast
    options:
      show_root_heading: true
      show_root_toc_entry: true
````

## File: docs/widgets/tree.md
````markdown
# Tree

!!! tip "Added in version 0.6.0"

A tree control widget.

- [x] Focusable
- [ ] Container


## Example

The example below creates a simple tree.

=== "Output"

    ```{.textual path="docs/examples/widgets/tree.py"}
    ```

=== "tree.py"

    ```python
    --8<-- "docs/examples/widgets/tree.py"
    ```

Tree widgets have a "root" attribute which is an instance of a [TreeNode][textual.widgets.tree.TreeNode]. Call [add()][textual.widgets.tree.TreeNode.add] or [add_leaf()][textual.widgets.tree.TreeNode.add_leaf] to add new nodes underneath the root. Both these methods return a TreeNode for the child which you can use to add additional levels.


## Reactive Attributes

| Name          | Type   | Default | Description                                     |
| ------------- | ------ | ------- | ----------------------------------------------- |
| `show_root`   | `bool` | `True`  | Show the root node.                             |
| `show_guides` | `bool` | `True`  | Show guide lines between levels.                |
| `guide_depth` | `int`  | `4`     | Amount of indentation between parent and child. |

## Messages

- [Tree.NodeCollapsed][textual.widgets.Tree.NodeCollapsed]
- [Tree.NodeExpanded][textual.widgets.Tree.NodeExpanded]
- [Tree.NodeHighlighted][textual.widgets.Tree.NodeHighlighted]
- [Tree.NodeSelected][textual.widgets.Tree.NodeSelected]

## Bindings

The tree widget defines the following bindings:

::: textual.widgets.Tree.BINDINGS
    options:
      show_root_heading: false
      show_root_toc_entry: false

## Component Classes

The tree widget provides the following component classes:

::: textual.widgets.Tree.COMPONENT_CLASSES
    options:
      show_root_heading: false
      show_root_toc_entry: false


---


::: textual.widgets.Tree
    options:
      heading_level: 2

---

::: textual.widgets.tree
    options:
      heading_level: 2
````

## File: docs/FAQ.md
````markdown
---
hide:
  - navigation
---

<!-- Auto-generated by FAQtory -->
<!-- Do not edit by hand! -->

# Frequently Asked Questions


Welcome to the Textual FAQ.
Here we try and answer any question that comes up frequently.
If you can't find what you are looking for here, see our other [help](./help.md) channels.

<a name="does-textual-support-images"></a>
## Does Textual support images?

Textual doesn't have built-in support for images yet, but it is on the [Roadmap](https://textual.textualize.io/roadmap/).

See also the [rich-pixels](https://github.com/darrenburns/rich-pixels) project for a Rich renderable for images that works with Textual.

---

<a name="how-can-i-fix-importerror-cannot-import-name-composeresult-from-textualapp-"></a>
## How can I fix ImportError cannot import name ComposeResult from textual.app ?

You likely have an older version of Textual. You can install the latest version by adding the `-U` switch which will force pip to upgrade.

The following should do it:

```
pip install textual-dev -U
```

---

<a name="how-can-i-select-and-copy-text-in-a-textual-app"></a>
## How can I select and copy text in a Textual app?

Textual supports text selection for most widgets, via click and drag. Press ctrl+c to copy.

For widgets that don't yet support text selection, you can try and use your terminal's builtin support.
Most terminal emulators offer a modifier key which you can hold while you click and drag to restore the behavior you
may expect from the command line. The exact modifier key depends on the terminal and platform you are running on.

- **iTerm** Hold the OPTION key.
- **Gnome Terminal** Hold the SHIFT key.
- **Windows Terminal** Hold the SHIFT key.

Refer to the documentation for your terminal emulator, if it is not listed above.

---

<a name="how-can-i-set-a-translucent-app-background"></a>
## How can I set a translucent app background?

Some terminal emulators have a translucent background feature which allows the desktop underneath to be partially visible.

This feature is unlikely to work with Textual, as the translucency effect requires the use of ANSI background colors, which Textual doesn't use.
Textual uses 16.7 million colors where available which enables consistent colors across all platforms and additional effects which aren't possible with ANSI colors.

For more information on ANSI colors in Textual, see [Why no ANSI Themes?](#why-doesnt-textual-support-ansi-themes).

---

<a name="how-do-i-center-a-widget-in-a-screen"></a>
## How do I center a widget in a screen?

!!! tip

    See [*How To Center Things*](https://textual.textualize.io/how-to/center-things/) in the
    Textual documentation for a more comprehensive answer to this question.

To center a widget within a container use
[`align`](https://textual.textualize.io/styles/align/). But remember that
`align` works on the *children* of a container, it isn't something you use
on the child you want centered.

For example, here's an app that shows a `Button` in the middle of a
`Screen`:

```python
from textual.app import App, ComposeResult
from textual.widgets import Button

class ButtonApp(App):

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("PUSH ME!")

if __name__ == "__main__":
    ButtonApp().run()
```

If you use the above on multiple widgets, you'll find they appear to
"left-align" in the center of the screen, like this:

```
+-----+
|     |
+-----+

+---------+
|         |
+---------+

+---------------+
|               |
+---------------+
```

If you want them more like this:

```
     +-----+
     |     |
     +-----+

   +---------+
   |         |
   +---------+

+---------------+
|               |
+---------------+
```

The best approach is to wrap each widget in a [`Center`
container](https://textual.textualize.io/api/containers/#textual.containers.Center)
that individually centers it. For example:

```python
from textual.app import App, ComposeResult
from textual.containers import Center
from textual.widgets import Button

class ButtonApp(App):

    CSS = """
    Screen {
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Center(Button("PUSH ME!"))
        yield Center(Button("AND ME!"))
        yield Center(Button("ALSO PLEASE PUSH ME!"))
        yield Center(Button("HEY ME ALSO!!"))

if __name__ == "__main__":
    ButtonApp().run()
```

---

<a name="how-do-i-fix-workerdeclarationerror"></a>
## How do I fix WorkerDeclarationError?

Textual version 0.31.0 requires that you set `thread=True` on the `@work` decorator if you want to run a threaded worker.

If you want a threaded worker, you would declare it in the following way:

```python
@work(thread=True)
def run_in_background():
    ...
```

If you *don't* want a threaded worker, you should make your work function `async`:

```python
@work()
async def run_in_background():
    ...
```

This change was made because it was too easy to accidentally create a threaded worker, which may produce unexpected results.

---

<a name="how-do-i-pass-arguments-to-an-app"></a>
## How do I pass arguments to an app?

When creating your `App` class, override `__init__` as you would when
inheriting normally. For example:

```python
from textual.app import App, ComposeResult
from textual.widgets import Static

class Greetings(App[None]):

    def __init__(self, greeting: str="Hello", to_greet: str="World") -> None:
        self.greeting = greeting
        self.to_greet = to_greet
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(f"{self.greeting}, {self.to_greet}")
```

Then the app can be run, passing in various arguments; for example:

```python
# Running with default arguments.
Greetings().run()

# Running with a keyword argument.
Greetings(to_greet="davep").run()

# Running with both positional arguments.
Greetings("Well hello", "there").run()
```

---

<a name="why-do-some-key-combinations-never-make-it-to-my-app"></a>
## Why do some key combinations never make it to my app?

Textual can only ever support key combinations that are passed on by your
terminal application. Which keys get passed on can differ from terminal to
terminal, and from operating system to operating system.

Because of this it's best to stick to key combinations that are known to be
universally-supported; these include the likes of:

- Letters
- Numbers
- Numbered function keys (especially F1 through F10)
- Space
- Return
- Arrow, home, end and page keys
- Control
- Shift

When [creating bindings for your
application](https://textual.textualize.io/guide/input/#bindings) we
recommend picking keys and key combinations from the above.

Keys that aren't normally passed through by terminals include Cmd and Option
on macOS, and the Windows key on Windows.

If you need to test what [key
combinations](https://textual.textualize.io/guide/input/#keyboard-input)
work in different environments you can try them out with `textual keys`.

---

<a name="why-doesnt-textual-look-good-on-macos"></a>
## Why doesn't Textual look good on macOS?

You may find that the default macOS Terminal.app doesn't render Textual apps (and likely other TUIs) very well, particularly when it comes to box characters.
For instance, you may find it displays misaligned blocks and lines like this:

<img width="1042" alt="Screenshot 2023-06-19 at 10 43 02" src="https://github.com/Textualize/textual/assets/554369/e61f3876-3dd1-4ac8-b380-22922c89c7d6">

You can (mostly) fix this by opening settings -> profiles > Text tab, and changing the font settings.
We have found that Menlo Regular font, with a character spacing of 1 and line spacing of 0.805 produces reasonable results.
If you want to use another font, you may have to tweak the line spacing until you get good results.

<img width="737" alt="Screenshot 2023-06-19 at 10 44 00" src="https://github.com/Textualize/textual/assets/554369/0a052a93-b1fd-4327-9d33-d954b51a9ad2">

With these changes, Textual apps render more as intended:

<img width="1042" alt="Screenshot 2023-06-19 at 10 43 23" src="https://github.com/Textualize/textual/assets/554369/a0c4aa05-c509-4ac1-b0b8-e68ce4433f70">

Even with this *fix*, Terminal.app has a few limitations.
It is limited to 256 colors, and can be a little slow compared to more modern alternatives.
Fortunately there are a number of free terminal emulators for macOS which produces high quality results.

We recommend any of the following terminals:

- [iTerm2](https://iterm2.com/)
- [Kitty](https://sw.kovidgoyal.net/kitty/)
- [WezTerm](https://wezfurlong.org/wezterm/)

### Terminal.app colors

<img width="762" alt="Screenshot 2023-06-19 at 11 00 12" src="https://github.com/Textualize/textual/assets/554369/e0555d23-e141-4069-b318-f3965c880208">

### iTerm2 colors

<img width="1002" alt="Screenshot 2023-06-19 at 11 00 25" src="https://github.com/Textualize/textual/assets/554369/9a8cde57-5121-49a7-a2e0-5f6fc871b7a6">

---

<a name="why-doesnt-textual-support-ansi-themes"></a>
## Why doesn't Textual support ANSI themes?

Textual will not generate escape sequences for the 16 themeable *ANSI* colors.

This is an intentional design decision we took for for the following reasons:

- Not everyone has a carefully chosen ANSI color theme. Color combinations which may look fine on your system, may be unreadable on another machine. There is very little an app author or Textual can do to resolve this. Asking users to simply pick a better theme is not a good solution, since not all users will know how.
- ANSI colors can't be manipulated in the way Textual can do with other colors. Textual can blend colors and produce light and dark shades from an original color, which is used to create more readable text and user interfaces. Color blending will also be used to power future accessibility features.

Textual has a design system which guarantees apps will be readable on all platforms and terminals, and produces better results than ANSI colors.

There is currently a light and dark version of the design system, but more are planned. It will also be possible for users to customize the source colors on a per-app or per-system basis. This means that in the future you will be able to modify the core colors to blend in with your chosen terminal theme.

!!! tip "Changed in version 0.80.0"

    Textual added an `ansi_color` boolean to App. If you set this to `True`, then Textual will not attempt to convert ANSI colors. Note that you will lose transparency effects if you enable this setting.

---

Generated by [FAQtory](https://github.com/willmcgugan/faqtory)
````

## File: docs/getting_started.md
````markdown
All you need to get started building Textual apps.

## Requirements

Textual requires Python 3.8 or later (if you have a choice, pick the most recent Python). Textual runs on Linux, macOS, Windows and probably any OS where Python also runs.

!!! info "Your platform"

    ### :fontawesome-brands-linux: Linux (all distros)

    All Linux distros come with a terminal emulator that can run Textual apps.

    ### :material-apple: macOS

    The default terminal app is limited to 256 colors. We recommend installing a newer terminal such as [iterm2](https://iterm2.com/), [Ghostty](https://ghostty.org/), [Kitty](https://sw.kovidgoyal.net/kitty/), or [WezTerm](https://wezfurlong.org/wezterm/).

    ### :material-microsoft-windows: Windows

    The new [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701?hl=en-gb&gl=GB) runs Textual apps beautifully.


## Installation

Here's how to install Textual.

### From PyPI

You can install Textual via PyPI, with the following command:

```
pip install textual
```

If you plan on developing Textual apps, you should also install textual developer tools:

```
pip install textual-dev
```

If you would like to enable syntax highlighting in the [TextArea](./widgets/text_area.md) widget, you should specify the "syntax" extras when you install Textual:

```
pip install "textual[syntax]"
```

### From conda-forge

Textual is also available on [conda-forge](https://conda-forge.org/). The preferred package manager for conda-forge is currently [micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html):

```
micromamba install -c conda-forge textual
```

And for the textual developer tools:

```
micromamba install -c conda-forge textual-dev
```

### Textual CLI

If you installed the developer tools you should have access to the `textual` command. There are a number of sub-commands available which will aid you in building Textual apps. Run the following for a list of the available commands:

```bash
textual --help
```

See [devtools](guide/devtools.md) for more about the `textual` command.

## Demo

Once you have Textual installed, run the following to get an impression of what it can do:

```bash
python -m textual
```

## Examples


The Textual repository comes with a number of example apps. To try out the examples, first clone the Textual repository:

=== "HTTPS"

    ```bash
    git clone https://github.com/Textualize/textual.git
    ```

=== "SSH"

    ```bash
    git clone git@github.com:Textualize/textual.git
    ```

=== "GitHub CLI"

    ```bash
    gh repo clone Textualize/textual
    ```


With the repository cloned, navigate to the `/examples/` directory where you will find a number of Python files you can run from the command line:

```bash
cd textual/examples/
python code_browser.py ../
```

### Widget examples

In addition to the example apps, you can also find the code listings used to generate the screenshots in these docs in the `docs/examples` directory.

## Need help?

See the [help](./help.md) page for how to get help with Textual, or to report bugs.
````

## File: docs/help.md
````markdown
# Help

If you need help with any aspect of Textual, let us know! We would be happy to hear from you.

## Bugs and feature requests

Report bugs via GitHub on the Textual [issues](https://github.com/Textualize/textual/issues) page. You can also post feature requests via GitHub issues, but see the [Roadmap](./roadmap.md) first.

## Help with using Textual

You can seek help with using Textual [in the discussion area on GitHub](https://github.com/Textualize/textual/discussions).

## Discord Server

For more realtime feedback or chat, join our Discord server to connect with the [Textual community](https://discord.gg/Enf6Z3qhVr).
````

## File: docs/index.md
````markdown
---
hide:
  - toc
  - navigation
---

!!! tip inline end

    See the navigation links in the header or side-bar.

    Click :octicons-three-bars-16: (top left) on mobile.


# Welcome

Welcome to the [Textual](https://github.com/Textualize/textual) framework documentation.

[Get started](./getting_started.md){ .md-button .md-button--primary } or go straight to the [Tutorial](./tutorial.md)



## What is Textual?

Textual is a *Rapid Application Development* framework for Python, built by [Textualize.io](https://www.textualize.io).


Build sophisticated user interfaces with a simple Python API. Run your apps in the terminal *or* a [web browser](https://github.com/Textualize/textual-serve)!



<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } :material-language-python:{. lg .middle } __Rapid development__

    ---

    Uses your existing Python skills to build beautiful user interfaces.


-   :material-raspberry-pi:{ .lg .middle } __Low requirements__

    ---

    Run Textual on a single board computer if you want to.



-   :material-microsoft-windows:{ .lg .middle } :material-apple:{ .lg .middle } :fontawesome-brands-linux:{ .lg .middle } __Cross platform__

    ---

    Textual runs just about everywhere.



-   :material-network:{ .lg .middle } __Remote__

    ---

    Textual apps can run over SSH.


-   :fontawesome-solid-terminal:{ .lg .middle } __CLI Integration__

    ---

    Textual apps can be launched and run from the command prompt.



-   :material-scale-balance:{ .lg .middle } __Open Source__

    ---

    Textual is licensed under MIT.


</div>



---

# Built with Textual

Textual has enabled an ecosystem of applications and tools for developers and non-developers alike.

Here are a few examples.


## Posting

The API client that lives in your terminal.
Posting is a beautiful open-source terminal app for developing and testing APIs.

[Posting Website](https://posting.sh/)

[Posting Github Repository](https://github.com/darrenburns/posting)

<div>
<a href="https://posting.sh">
--8<-- "docs/images/screenshots/posting.svg"
</a>
</div>

---

## Toolong

A terminal application to view, tail, merge, and search log files (plus JSONL).

[Toolong Github Repository](https://github.com/textualize/toolong)

<div>
<a href="https://github.com/Textualize/toolong">
--8<-- "docs/images/screenshots/toolong.svg"
</a>
</div>

---


## Memray

Memray is a memory profiler for Python, built by Bloomberg.

[Memray Github Repository](https://github.com/bloomberg/memray)

<div>
<a href="https://github.com/bloomberg/memray">
--8<-- "docs/images/screenshots/memray.svg"
</a>
</div>

---

## Dolphie

Your single pane of glass for real-time analytics into MySQL/MariaDB & ProxySQL

[Dolphie Github Repository](https://github.com/charles-001/dolphie)


<div>
<a href="https://github.com/charles-001/dolphie">
--8<-- "docs/images/screenshots/dolphie.svg"
</a>
</div>


---

## Harlequin

An easy, fast, and beautiful database client for the terminal.

[Harlequin website](https://harlequin.sh/)

<div>
<a href="https://harlequin.sh">
--8<-- "docs/images/screenshots/harlequin.svg"
</a>
</div>



---

# Examples

The following examples are taken from the [examples directory](https://github.com/Textualize/textual/tree/main/examples).

Click the tabs to see the code behind the example. 

=== "Pride example"

    ```{.textual path="examples/pride.py"}
    ```

=== "pride.py"

    ```py
    --8<-- "examples/pride.py"
    ```


---

=== "Calculator example"

    ```{.textual path="examples/calculator.py" columns=100 lines=41 press="6,.,2,8,3,1,8,5,3,0,7,1,wait:400"}
    ```

=== "calculator.py"

    ```python
    --8<-- "examples/calculator.py"
    ```

=== "calculator.tcss"

    ```css
    --8<-- "examples/calculator.tcss"
    ```
````

## File: docs/roadmap.md
````markdown
---
hide:
  - navigation
---


# Roadmap

We ([textualize.io](https://www.textualize.io/)) are actively building and maintaining Textual.

We have many new features in the pipeline. This page will keep track of that work.

## Features

High-level features we plan on implementing.

- [ ] Accessibility
    * [ ] Integration with screen readers
    * [x] Monochrome mode
    * [ ] High contrast theme
    * [ ] Color-blind themes
- [X] Command palette
    * [X] Fuzzy search
- [ ] Configuration (.toml based extensible configuration format)
- [x] Console
- [ ] Devtools
    * [ ] Integrated log
    * [ ] DOM tree view
    * [ ] REPL
- [ ] Reactive state abstraction
- [x] Themes
    * [ ] Customize via config
    * [ ] Builtin theme editor

## Widgets

Widgets are key to making user-friendly interfaces. The builtin widgets should cover many common (and some uncommon) use-cases. The following is a list of the widgets we have built or are planning to build.

- [x] Buttons
    * [x] Error / warning variants
- [ ] Color picker
- [X] Checkbox
- [X] Content switcher
- [x] DataTable
    * [x] Cell select
    * [x] Row / Column select
    * [x] API to update cells / rows
    * [ ] Lazy loading API
- [ ] Date picker
- [ ] Drop-down menus
- [ ] Form Widget
    * [ ] Serialization / Deserialization
    * [ ] Export to `attrs` objects
    * [ ] Export to `PyDantic` objects
- [ ] Image support
    * [ ] Half block
    * [ ] Braille
    * [ ] Sixels, and other image extensions
- [x] Input
    * [x] Validation
    * [ ] Error / warning states
    * [ ] Template types: IP address, physical units (weight, volume), currency, credit card etc
- [X] Select control (pull-down)
- [X] Markdown viewer
    * [ ] Collapsible sections
    * [ ] Custom widgets
- [ ] Plots
    * [ ] bar chart
    * [ ] line chart
    * [ ] Candlestick chars
- [X] Progress bars
    * [ ] Style variants (solid, thin etc)
- [X] Radio boxes
- [X] Spark-lines
- [X] Switch
- [X] Tabs
- [X] TextArea (multi-line input)
    * [X] Basic controls
    * [ ] Indentation guides
    * [ ] Smart features for various languages
    * [X] Syntax highlighting
````

## File: docs/robots.txt
````
Sitemap: https://textual.textualize.io/sitemap.xml
````

## File: docs/tutorial.md
````markdown
---
hide:
  - navigation
---

# Tutorial

Welcome to the Textual Tutorial!

By the end of this page you should have a solid understanding of app development with Textual.

!!! quote

    If you want people to build things, make it fun.

    &mdash; **Will McGugan** (creator of Rich and Textual)

## Video series

This tutorial has an accompanying [video series](https://www.youtube.com/playlist?list=PLHhDR_Q5Me1MxO4LmfzMNNQyKfwa275Qe) which covers the same content.

## Stopwatch Application

We're going to build a stopwatch application. This application should show a list of stopwatches with buttons to start, stop, and reset the stopwatches. We also want the user to be able to add and remove stopwatches as required.

This will be a simple yet **fully featured** app &mdash; you could distribute this app if you wanted to!

Here's what the finished app will look like:


```{.textual path="docs/examples/tutorial/stopwatch.py" title="stopwatch.py" press="tab,enter,tab,enter,tab,enter,tab,enter"}
```

!!! info

    Did you notice the `^p palette` at the bottom right hand corner?
    This is the [Command Palette](./guide/command_palette.md).
    You can think of it as a dedicated command prompt for your app.

### Get the code

If you want to try the finished Stopwatch app and follow along with the code, first make sure you have [Textual installed](getting_started.md) then check out the [Textual](https://github.com/Textualize/textual) repository:

=== "HTTPS"

    ```bash
    git clone https://github.com/Textualize/textual.git
    ```

=== "SSH"

    ```bash
    git clone git@github.com:Textualize/textual.git
    ```

=== "GitHub CLI"

    ```bash
    gh repo clone Textualize/textual
    ```


With the repository cloned, navigate to `docs/examples/tutorial` and run `stopwatch.py`.

```bash
cd textual/docs/examples/tutorial
python stopwatch.py
```

## Type hints (in brief)

!!! tip inline end

    Type hints are entirely optional in Textual. We've included them in the example code but it's up to you whether you add them to your own projects.

We're a big fan of Python type hints at Textualize. If you haven't encountered type hinting, it's a way to express the types of your data, parameters, and return values. Type hinting allows tools like [mypy](https://mypy.readthedocs.io/en/stable/) to catch bugs before your code runs.

The following function contains type hints:

```python
def repeat(text: str, count: int) -> str:
    """Repeat a string a given number of times."""
    return text * count
```

Parameter types follow a colon. So `text: str` indicates that `text` requires a string and `count: int` means that `count` requires an integer.

Return types follow `->`. So `-> str:` indicates this method returns a string.


## The App class

The first step in building a Textual app is to import and extend the `App` class. Here's a basic app class we will use as a starting point for the stopwatch app.

```python title="stopwatch01.py"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

If you run this code, you should see something like the following:


```{.textual path="docs/examples/tutorial/stopwatch01.py" title="stopwatch01.py"}
```

Hit the ++d++ key to toggle between light and dark themes.

```{.textual path="docs/examples/tutorial/stopwatch01.py" press="d" title="stopwatch01.py"}
```

Hit ++ctrl+q++ to exit the app and return to the command prompt.

### A closer look at the App class

Let's examine `stopwatch01.py` in more detail.

```python title="stopwatch01.py" hl_lines="1 2"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The first line imports `App` class, which is the base class for all Textual apps.
The second line imports two builtin widgets: [`Footer`](widgets/footer.md) which shows a bar at the bottom of the screen with bound keys, and [`Header`](widgets/header.md) which shows a title at the top of the screen.
Widgets are re-usable components responsible for managing a part of the screen.
We will cover how to build widgets in this tutorial.

The following lines define the app itself:

```python title="stopwatch01.py" hl_lines="5-19"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The App class is where most of the logic of Textual apps is written. It is responsible for loading configuration, setting up widgets, handling keys, and more.

Here's what the above app defines:

- `BINDINGS` is a list of tuples that maps (or *binds*) keys to actions in your app. The first value in the tuple is the key; the second value is the name of the action; the final value is a short description. We have a single binding which maps the ++d++ key on to the "toggle_dark" action. See [key bindings](./guide/input.md#bindings) in the guide for details.

-  `compose()` is where we construct a user interface with widgets. The `compose()` method may return a list of widgets, but it is generally easier to _yield_ them (making this method a generator). In the example code we yield an instance of each of the widget classes we imported, i.e. `Header()` and `Footer()`.

- `action_toggle_dark()` defines an _action_ method. Actions are methods beginning with `action_` followed by the name of the action. The `BINDINGS` list above tells Textual to run this action when the user hits the ++d++ key. See [actions](./guide/actions.md) in the guide for details.

```python title="stopwatch01.py" hl_lines="22-24"
--8<-- "docs/examples/tutorial/stopwatch01.py"
```

The final three lines create an instance of the app and calls the [run()][textual.app.App.run] method which puts your terminal into *application mode* and runs the app until you exit with ++ctrl+q++. This happens within a `__name__ == "__main__"` block so we could run the app with `python stopwatch01.py` or import it as part of a larger project.

## Designing a UI with widgets

Textual has a large number of [builtin widgets](./widget_gallery.md).
For our app we will need new widgets, which we can create by extending and combining the builtin widgets.

Before we dive into building widgets, let's first sketch a design for the app &mdash; so we know what we're aiming for.


<div class="excalidraw">
--8<-- "docs/images/stopwatch.excalidraw.svg"
</div>

### Custom widgets

We need a `Stopwatch` widget composed of the following _child_ widgets:

- A "Start" button
- A "Stop" button
- A "Reset" button
- A time display

Let's add those to the app.
Just a skeleton for now, we will add the rest of the features as we go.

```python title="stopwatch02.py" hl_lines="2-3 6-7 10-18 30"
--8<-- "docs/examples/tutorial/stopwatch02.py"
```

We've imported two new widgets in this code: [`Button`](widgets/button.md) for the buttons and [`Digits`](widgets/digits.md) for the time display.
Additionally, we've imported [`HorizontalGroup`][textual.containers.HorizontalGroup] and [`VerticalScroll`][textual.containers.VerticalScroll] from `textual.containers` (as the name of the module suggests, *containers* are widgets which contain other widgets).
We will use these container widgets to define the general layout of our interface.

The `TimeDisplay` is currently very simple, all it does is extend `Digits` without adding any new features. We will flesh this out later.

The `Stopwatch` widget class extends the `HorizontalGroup` container class, which will arrange its children into a horizontal row. The Stopwatch's `compose()` adds those children, which correspond to the components from the sketch above.

!!! tip "Coordinating widgets"

    If you are building custom widgets of your own, be sure to see guide on [coordinating widgets](./guide/widgets.md#coordinating-widgets).

#### The buttons

The Button constructor takes a label to be displayed in the button (`"Start"`, `"Stop"`, or `"Reset"`). Additionally, some of the buttons set the following parameters:

- `id` is an identifier we can use to tell the buttons apart in code and apply styles. More on that later.
- `variant` is a string which selects a default style. The "success" variant makes the button green, and the "error" variant makes it red.

### Composing the widgets

The new line in `StopwatchApp.compose()` yields a single `VerticalScroll` which will scroll if the contents don't quite fit. This widget also takes care of key bindings required for scrolling, like ++up++, ++down++, ++page-down++, ++page-up++, ++home++, ++end++, etc.

When widgets contain other widgets (like `VerticalScroll`) they will typically accept their child widgets as positional arguments.
So the line `yield VerticalScroll(Stopwatch(), Stopwatch(), Stopwatch())` creates a `VerticalScroll` containing three `Stopwatch` widgets.


### The unstyled app

Let's see what happens when we run `stopwatch02.py`.

```{.textual path="docs/examples/tutorial/stopwatch02.py" title="stopwatch02.py"}
```

The elements of the stopwatch application are there, but it doesn't look much like the sketch. This is because we have yet to apply any _styles_ to our new widgets.

## Writing Textual CSS

Every widget has a `styles` object with a number of attributes that impact how the widget will appear. Here's how you might set white text and a blue background for a widget:

```python
self.styles.background = "blue"
self.styles.color = "white"
```

While it's possible to set all styles for an app this way, it is rarely necessary. Textual has support for CSS (Cascading Style Sheets), a technology used by web browsers. CSS files are data files loaded by your app which contain information about styles to apply to your widgets.

!!! info

    The dialect of CSS used in Textual is greatly simplified over web based CSS and easier to learn.


CSS makes it easy to iterate on the design of your app and enables [live-editing](./guide/devtools.md#live-editing) &mdash; you can edit CSS and see the changes without restarting the app!


Let's add a CSS file to our application.

```python title="stopwatch03.py" hl_lines="24"
--8<-- "docs/examples/tutorial/stopwatch03.py"
```

Adding the `CSS_PATH` class variable tells Textual to load the following file when the app starts:

```css title="stopwatch03.tcss"
--8<-- "docs/examples/tutorial/stopwatch03.tcss"
```

If we run the app now, it will look *very* different.

```{.textual path="docs/examples/tutorial/stopwatch03.py" title="stopwatch03.py"}
```

This app looks much more like our sketch. Let's look at how Textual uses `stopwatch03.tcss` to apply styles.

### CSS basics

CSS files contain a number of _declaration blocks_. Here's the first such block from `stopwatch03.tcss` again:

```css
Stopwatch {
    background: $boost;
    height: 5;
    margin: 1;
    min-width: 50;
    padding: 1;
}
```

The first line tells Textual that the styles should apply to the `Stopwatch` widget. The lines between the curly brackets contain the styles themselves.

Here's how this CSS code changes how the `Stopwatch` widget is displayed.

<div class="excalidraw">
--8<-- "docs/images/stopwatch_widgets.excalidraw.svg"
</div>

- `background: $boost` sets the background color to `$boost`. The `$` prefix picks a pre-defined color from the builtin theme. There are other ways to specify colors such as `"blue"` or `rgb(20,46,210)`.
- `height: 5` sets the height of our widget to 5 lines of text.
- `margin: 1` sets a margin of 1 cell around the `Stopwatch` widget to create a little space between widgets in the list.
- `min-width: 50` sets the minimum width of our widget to 50 cells.
- `padding: 1` sets a padding of 1 cell around the child widgets.


Here's the rest of `stopwatch03.tcss` which contains further declaration blocks:

```css
TimeDisplay {   
    text-align: center;
    color: $foreground-muted;
    height: 3;
}

Button {
    width: 16;
}

#start {
    dock: left;
}

#stop {
    dock: left;
    display: none;
}

#reset {
    dock: right;
}
```

The `TimeDisplay` block aligns text to the center (`text-align:`), sets its color (`color:`), and sets its height (`height:`) to 3 lines.

The `Button` block sets the width (`width:`) of buttons to 16 cells (character widths).

The last 3 blocks have a slightly different format. When the declaration begins with a `#` then the styles will be applied to widgets with a matching "id" attribute. We've set an ID on the `Button` widgets we yielded in `compose`. For instance the first button has `id="start"` which matches `#start` in the CSS.

The buttons have a `dock` style which aligns the widget to a given edge.
The start and stop buttons are docked to the left edge, while the reset button is docked to the right edge.

You may have noticed that the stop button (`#stop` in the CSS) has `display: none;`. This tells Textual to not show the button. We do this because we don't want to display the stop button when the timer is *not* running. Similarly, we don't want to show the start button when the timer is running. We will cover how to manage such dynamic user interfaces in the next section.

### Dynamic CSS

We want our `Stopwatch` widget to have two states: a default state with a Start and Reset button; and a _started_ state with a Stop button. When a stopwatch is started it should also have a green background to indicate it is currently active.

<div class="excalidraw">
--8<-- "docs/images/css_stopwatch.excalidraw.svg"
</div>


We can accomplish this with a CSS _class_. Not to be confused with a Python class, a CSS class is like a tag you can add to a widget to modify its styles. A widget may have any number of CSS classes, which may be added and removed to change its appearance.

Here's the new CSS:

```css title="stopwatch04.tcss" hl_lines="32-52"
--8<-- "docs/examples/tutorial/stopwatch04.tcss"
```

These new rules are prefixed with `.started`. The `.` indicates that `.started` refers to a CSS class called "started". The new styles will be applied only to widgets that have this CSS class.

Some of the new styles have more than one selector separated by a space. The space indicates that the rule should match the second selector if it is a child of the first. Let's look at one of these styles:

```css
.started #start {
    display: none
}
```

The `.started` selector matches any widget with a `"started"` CSS class.
While `#start` matches a widget with an ID of `"start"`.
Combining the two selectors with a space (`.started #start`) creates a new selector that will match the start button *only* if it is also inside a container with a CSS class of "started".

As before, the `display: none` rule will cause any matching widgets to be hidden from view. 

If we were to write this in English, it would be something like: "Hide the start button if the widget is already started".

### Manipulating classes

Modifying a widget's CSS classes is a convenient way to update visuals without introducing a lot of messy display related code.

You can add and remove CSS classes with the [add_class()][textual.dom.DOMNode.add_class] and [remove_class()][textual.dom.DOMNode.remove_class] methods.
We will use these methods to connect the started state to the Start / Stop buttons.

The following code will start or stop the stopwatches in response to clicking a button:

```python title="stopwatch04.py" hl_lines="13-18"
--8<-- "docs/examples/tutorial/stopwatch04.py"
```

The `on_button_pressed` method is an *event handler*. Event handlers are methods called by Textual in response to an *event* such as a key press, mouse click, etc.
Event handlers begin with `on_` followed by the name of the event they will handle.
Hence `on_button_pressed` will handle the button pressed event.

See the guide on [message handlers](./guide/events.md#message-handlers) for the details on how to write event handlers.

If you run `stopwatch04.py` now you will be able to toggle between the two states by clicking the first button:

```{.textual path="docs/examples/tutorial/stopwatch04.py" title="stopwatch04.py" press="tab,tab,tab,enter"}
```

When the button event handler adds or removes the `"started"` CSS class, Textual re-applies the CSS and updates the visuals.


## Reactive attributes

A recurring theme in Textual is that you rarely need to explicitly update a widget's visuals.
It is possible: you can call [refresh()][textual.widget.Widget.refresh] to display new data.
However, Textual prefers to do this automatically via _reactive_ attributes.

Reactive attributes work like any other attribute, such as those you might set in an `__init__` method, but allow Textual to detect when you assign to them, in addition to some other [*superpowers*](./guide/reactivity.md).

To add a reactive attribute, import [reactive][textual.reactive.reactive] and create an instance in your class scope.

Let's add reactives to our stopwatch to calculate and display the elapsed time.

```python title="stopwatch05.py" hl_lines="1 5 12-27 45"
--8<-- "docs/examples/tutorial/stopwatch05.py"
```

We have added two reactive attributes to the `TimeDisplay` widget: `start_time` will contain the time the stopwatch was started (in seconds), and `time` will contain the time to be displayed in the `Stopwatch` widget.

Both attributes will be available on `self` as if you had assigned them in `__init__`.
If you write to either of these attributes the widget will update automatically.

!!! info

    The `monotonic` function in this example is imported from the standard library `time` module.
    It is similar to `time.time` but won't go backwards if the system clock is changed.

The first argument to `reactive` may be a default value for the attribute or a callable that returns a default value.
We set the default for `start_time` to the `monotonic` function which will be called to initialize the attribute with the current time when the `TimeDisplay` is added to the app.
The `time` attribute has a simple float as the default, so `self.time` will be initialized to `0`.


The `on_mount` method is an event handler called when the widget is first added to the application (or _mounted_ in Textual terminology). In this method we call [set_interval()][textual.message_pump.MessagePump.set_interval] to create a timer which calls `self.update_time` sixty times a second. This `update_time` method calculates the time elapsed since the widget started and assigns it to `self.time` &mdash; which brings us to one of Reactive's super-powers.

If you implement a method that begins with `watch_` followed by the name of a reactive attribute, then the method will be called when the attribute is modified.
Such methods are known as *watch methods*.

Because `watch_time` watches the `time` attribute, when we update `self.time` 60 times a second we also implicitly call `watch_time` which converts the elapsed time to a string and updates the widget with a call to `self.update`.
Because this happens automatically, we don't need to pass in an initial argument to `TimeDisplay`.

The end result is that the `Stopwatch` widgets show the time elapsed since the widget was created:

```{.textual path="docs/examples/tutorial/stopwatch05.py" title="stopwatch05.py"}
```

We've seen how we can update widgets with a timer, but we still need to wire up the buttons so we can operate stopwatches independently.

### Wiring buttons

We need to be able to start, stop, and reset each stopwatch independently. We can do this by adding a few more methods to the `TimeDisplay` class.


```python title="stopwatch06.py" hl_lines="14 18 22 30-44 50-61"
--8<-- "docs/examples/tutorial/stopwatch06.py"
```

Here's a summary of the changes made to `TimeDisplay`.

- We've added a `total` reactive attribute to store the total time elapsed between clicking the start and stop buttons.
- The call to `set_interval` has grown a `pause=True` argument which starts the timer in pause mode (when a timer is paused it won't run until [resume()][textual.timer.Timer.resume] is called). This is because we don't want the time to update until the user hits the start button.
- The `update_time` method now adds `total` to the current time to account for the time between any previous clicks of the start and stop buttons.
- We've stored the result of `set_interval` which returns a [Timer](textual.timer.Timer) object. We will use this to _resume_ the timer when we start the Stopwatch.
- We've added `start()`, `stop()`, and `reset()` methods.

In addition, the `on_button_pressed` method on `Stopwatch` has grown some code to manage the time display when the user clicks a button. Let's look at that in detail:

```python
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "reset":
            time_display.reset()
```

This code supplies missing features and makes our app useful. We've made the following changes.

- The first line retrieves `id` attribute of the button that was pressed. We can use this to decide what to do in response.
- The second line calls [`query_one`][textual.dom.DOMNode.query_one] to get a reference to the `TimeDisplay` widget.
- We call the method on `TimeDisplay` that matches the pressed button.
- We add the `"started"` class when the Stopwatch is started (`self.add_class("started")`), and remove it (`self.remove_class("started")`) when it is stopped. This will update the Stopwatch visuals via CSS.

If you run `stopwatch06.py` you will be able to use the stopwatches independently.

```{.textual path="docs/examples/tutorial/stopwatch06.py" title="stopwatch06.py" press="tab,enter,tab,enter,tab"}
```

The only remaining feature of the Stopwatch app left to implement is the ability to add and remove stopwatches.

## Dynamic widgets

The Stopwatch app creates widgets when it starts via the `compose` method. We will also need to create new widgets while the app is running, and remove widgets we no longer need. We can do this by calling [mount()][textual.widget.Widget.mount] to add a widget, and [remove()][textual.widget.Widget.remove] to remove a widget.

Let's use these methods to implement adding and removing stopwatches to our app.

```python title="stopwatch.py" hl_lines="78-79 86 88-92 94-98"
--8<-- "docs/examples/tutorial/stopwatch.py"
```

Here's a summary of the changes:

- The `VerticalScroll` object in `StopWatchApp` grew a `"timers"` ID.
- Added `action_add_stopwatch` to add a new stopwatch.
- Added `action_remove_stopwatch` to remove a stopwatch.
- Added keybindings for the actions.

The `action_add_stopwatch` method creates and mounts a new stopwatch. Note the call to [query_one()][textual.dom.DOMNode.query_one] with a CSS selector of `"#timers"` which gets the timer's container via its ID.
Once mounted, the new Stopwatch will appear in the terminal. That last line in `action_add_stopwatch` calls [scroll_visible()][textual.widget.Widget.scroll_visible] which will scroll the container to make the new `Stopwatch` visible (if required).

The `action_remove_stopwatch` function calls [query()][textual.dom.DOMNode.query] with a CSS selector of `"Stopwatch"` which gets all the `Stopwatch` widgets.
If there are stopwatches then the action calls [last()][textual.css.query.DOMQuery.last] to get the last stopwatch, and [remove()][textual.css.query.DOMQuery.remove] to remove it.

If you run `stopwatch.py` now you can add a new stopwatch with the ++a++ key and remove a stopwatch with ++r++.

```{.textual path="docs/examples/tutorial/stopwatch.py" title="stopwatch.py" press="d,a,a,a,a,a,a,a,tab,enter,tab"}
```

## What next?

Congratulations on building your first Textual application! This tutorial has covered a lot of ground. If you are the type that prefers to learn a framework by coding, feel free. You could tweak `stopwatch.py` or look through the examples.

Read the guide for the full details on how to build sophisticated TUI applications with Textual.
````

## File: docs/widget_gallery.md
````markdown
---
hide:
  - navigation
---

# Widgets

Welcome to the Textual widget gallery.

We have many more widgets planned, or you can [build your own](./guide/widgets.md).


!!! info

    Textual is a **TUI** framework. Everything below runs in the *terminal*.


## Button

A simple button with a variety of semantic styles.

[Button reference](./widgets/button.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/button.py"}
```


## Checkbox

A classic checkbox control.

[Checkbox reference](./widgets/checkbox.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/checkbox.py"}
```


## Collapsible

Content that may be toggled on and off by clicking a title.

[Collapsible reference](./widgets/collapsible.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/collapsible.py"}
```


## ContentSwitcher

A widget for containing and switching display between multiple child
widgets.

[ContentSwitcher reference](./widgets/content_switcher.md){ .md-button .md-button--primary }


## DataTable

A powerful data table, with configurable cursors.

[DataTable reference](./widgets/data_table.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/data_table.py"}
```

## Digits

Display numbers in tall characters.

[Digits reference](./widgets/digits.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/digits.py"}
```

## DirectoryTree

A tree view of files and folders.

[DirectoryTree reference](./widgets/directory_tree.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/directory_tree.py"}
```

## Footer

A footer to display and interact with key bindings.

[Footer reference](./widgets/footer.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/footer.py" columns="70" lines="12"}
```



## Header

A header to display the app's title and subtitle.


[Header reference](./widgets/header.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/header.py" columns="70" lines="12"}
```


## Input

A control to enter text.

[Input reference](./widgets/input.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/input.py" press="D,a,r,r,e,n"}
```


## Label

A simple text label.

[Label reference](./widgets/label.md){ .md-button .md-button--primary }


## Link

A clickable link that opens a URL.

[Link reference](./widgets/link.md){ .md-button .md-button--primary }


## ListView

Display a list of items (items may be other widgets).

[ListView reference](./widgets/list_view.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/list_view.py"}
```

## LoadingIndicator

Display an animation while data is loading.

[LoadingIndicator reference](./widgets/loading_indicator.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/loading_indicator.py"}
```

## Log

Display and update lines of text (such as from a file).

[Log reference](./widgets/log.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/log.py"}
```

## MarkdownViewer

Display and interact with a Markdown document (adds a table of contents and browser-like navigation to Markdown).

[MarkdownViewer reference](./widgets/markdown_viewer.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/markdown_viewer.py" columns="120" lines="50" press="tab,down"}
```

## Markdown

Display a markdown document.

[Markdown reference](./widgets/markdown.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/markdown.py" columns="120" lines="53"}
```

## MaskedInput

A control to enter input according to a template mask.

[MaskedInput reference](./widgets/masked_input.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/masked_input.py"}
```

## OptionList

Display a vertical list of options (options may be Rich renderables).

[OptionList reference](./widgets/option_list.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/option_list_options.py"}
```

## Placeholder

Display placeholder content while you are designing a UI.

[Placeholder reference](./widgets/placeholder.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/placeholder.py"}
```

## Pretty

Display a pretty-formatted Rich renderable.

[Pretty reference](./widgets/pretty.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/pretty.py"}
```

## ProgressBar

A configurable progress bar with ETA and percentage complete.

[ProgressBar reference](./widgets/progress_bar.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/progress_bar.py" press="5,0,tab,enter"}
```


## RadioButton

A simple radio button.

[RadioButton reference](./widgets/radiobutton.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/radio_button.py"}
```

## RadioSet

A collection of radio buttons, that enforces uniqueness.

[RadioSet reference](./widgets/radioset.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/radio_set.py"}
```

## RichLog

Display and update text in a scrolling panel.

[RichLog reference](./widgets/rich_log.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/rich_log.py" press="H,i"}
```

## Rule

A rule widget to separate content, similar to a `<hr>` HTML tag.

[Rule reference](./widgets/rule.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/horizontal_rules.py"}
```

## Select

Select from a number of possible options.

[Select reference](./widgets/select.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/select_widget.py" press="tab,enter,down,down"}
```

## SelectionList

Select multiple values from a list of options.

[SelectionList reference](./widgets/selection_list.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/selection_list_selections.py" press="down,down,down"}
```

## Sparkline

Display numerical data.

[Sparkline reference](./widgets/sparkline.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/sparkline.py" lines="11"}
```

## Static

Displays simple static content. Typically used as a base class.

[Static reference](./widgets/static.md){ .md-button .md-button--primary }


## Switch

An on / off control, inspired by toggle buttons.

[Switch reference](./widgets/switch.md){ .md-button .md-button--primary }


```{.textual path="docs/examples/widgets/switch.py"}
```

## Tabs

A row of tabs you can select with the mouse or navigate with keys.

[Tabs reference](./widgets/tabs.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/tabs.py" press="a,a,a,a,right,right"}
```

## TabbedContent

A Combination of Tabs and ContentSwitcher to navigate static content.

[TabbedContent reference](./widgets/tabbed_content.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/tabbed_content.py" press="j"}
```

## TextArea

A multi-line text area which supports syntax highlighting various languages.

[TextArea reference](./widgets/text_area.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/text_area_example.py" columns="42" lines="8"}
```

## Tree

A tree control with expandable nodes.

[Tree reference](./widgets/tree.md){ .md-button .md-button--primary }

```{.textual path="docs/examples/widgets/tree.py"}
```
````
