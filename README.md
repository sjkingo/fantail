# fantail

[![Build Status](https://travis-ci.org/sjkingo/fantail.svg?branch=master)](https://travis-ci.org/sjkingo/fantail)
[![Coverage Status](https://coveralls.io/repos/github/sjkingo/fantail/badge.svg?branch=master)](https://coveralls.io/github/sjkingo/fantail?branch=master)

fantail is (yet another) static site generator written in pure-Python.

It is fast, extensible and requires zero configuration to use.

## Why?

There are many different static site generators available to use. Not all of
them do a particularly good job, or contain features that detract from the
simple goal of generating a static website.

fantail aims to change that by providing a simple, minimal site generator
in pure-Python. It requires no configuration or complex setup: simply point
it at a directory (the "site" source), add some content and 3 commands will
have a static site generated ready to upload to your favourite hosting site.

It is extensible through the use of plugins that can be used to extend the
default functionality:

* a [Markdown filter][https://github.com/sjkingo/fantail/blob/master/fantail/plugins/plugin_markdown.py]

## Features

* Fast, efficient generation of static pages
* No database required
* Minimal dependencies
* Full test suite
* Extensible through plugins
* Markdown support (optional)

## Requirements

* Python 3.4 or 3.5
* `jinja2`
* Optional: `mistune` if you want to enable [Markdown][markdown-syntax] support

[markdown-syntax]: https://daringfireball.net/projects/markdown/syntax

## Installation

Installation is as simple as installing with `pip`:

```
$ pip install -e git+https://github.com/sjkingo/fantail.git
```

It is recommended (but not required) you install the `mistune` library to
provide Markdown support:

```
$ pip install mistune
```

A full test suite is provided with 100% coverage:

```
$ pip install tox
$ tox
```

This script will attempt to install the test requirements if needed.


## Usage

1. `$ fantail init` - this will create a new site directory called `fantail-site`
   in the current directory and populate it with some folders and files.

2. Add some pages to the `fantail-site/pages` directory. For more information
   on how to format these pages, see the **Page design** section, below.

3. (Optionally) edit the templates in `fantail-site/templates`. A minimal
   HTML5 template is provided to get you started, and will be used by default
   if you do not specify a per-page template.

4. Run `$ fantail build` and your pages will be parsed and a static site will
   be generated.

You may run `fantail build` each time you modify a page or template and it will
re-generate the site. If an error occurs during generation, a message will
be printed and any existing output (from a previous run) will not be lost -
only once the site is successfully generated is it copied over to the `output`
directory.

See [this gist][example] for an example session.

[example]: https://gist.github.com/sjkingo/d83a24184794db303d1e70998d7bd232

## Page design

A fantail site is made up of *input pages* that reside in the site's `pages`
directory. Each page represents a single page on the site and must end with
the `.txt` extension to be recognised.

Each file is split into two sections: the headers, and the content. Similar
to an RFC2822-formatted email message, there is one header per line, separated
by a colon, like so:

```
title: This is the title of this page
```

There must not be a blank line between headers, as a blank line signifies the
end of the headers and the beginning of the content, like so:

```
title: Happy Days
template: blog.html

This is the page's content that will be rendered.
```

All headers will be added to the template context when generating, so you may
add as many different headers as you would like. See the **Templating** section
for more information.

### Required headers

The only header required for successful parsing of a page is `title`: this is
used as the `<title>` of the resulting page. It is also used in the RSS/Atom
generation.

### Optional headers

`template`

The `template` header may be used to control which template file is used to
render the current page. By default if this header is missing, the `base.html`
template is used. An error is raised if the specified template cannot be found.

More information on the templates is available in the **Templating** section.

## Templating

fantail uses `jinja2` to generate its output and makes full use of its template
system. Templates live in the `templates` directory inside a site, and the
template loader will look inside here when running.

All features of `jinja2`'s templating language can be used. For more information
see the excellent [templating documentation](http://jinja.pocoo.org/docs/dev/templates/).

## Plugins

See the [plugins documentation][plugins-doc] for more information.

[plugins-doc]: https://github.com/sjkingo/fantail/blob/master/fantail/plugins/README.md
