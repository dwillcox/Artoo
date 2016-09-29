# SELinux Sandbox Home Directory

This directory serves as the home directory for programs Artoo runs
using the SELinux sandbox.

`python` will need to load libraries at runtime from the python distribution, so for Anaconda installed in, e.g. `$(HOME)/anaconda`, you need to *copy* (NOT LINK) as follows:

```
$ cp -r $(HOME)/anaconda .
```

Linking instead of copying will allow a sandboxed program to modify python libraries which run Artoo.