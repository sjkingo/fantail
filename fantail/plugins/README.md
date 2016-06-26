# fantail plugins

fantail is extensible through the addition of plugins: modules that add
functionality. Each module in this directory that is named with the `plugin_`
prefix will be automatically loaded by fantail at startup. Any functions inside
these modules that are prefixed with `register_` will be registered.

Currently there is only one type of plugin: `filter`.

## Filters

Filters take an input argument `content`, which is the content part of a post,
and must return a string containing the transformed content. An example is below:

```
def register_uppercase_filter(content):
    return content.upper()
register_uppercase_filter.plugin_type = 'filter'
```

If no transformation is to be performed, the filter **must** return the content
string unchanged, not `None` - a warning will be logged if the function
does not return a string and the output will be discarded.
