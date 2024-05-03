# Django Hashids Field is now retired

I have decided to retire this module. This means:

- I do not recommend using this module.
- I will *not* be adding any more functionality.
- I will *not* be addressing any bugs, especially problems interoperating with other modules.
- I *will* fix any security critical bugs.

## What does this mean for me?

If django-hashids-field works for you in your project, then you don't need to make any changes. I will keep this
repository and pypi package around indefinitely.

If you are creating a new project, I suggest looking at other solutions, such as django-hashids, django-sqids,
UUIDs, NanoIDs, or something else.

## Migrating to django-hashids or django-squids

You are free to either remove this module or migrate your project to another library, such as django-hashids or
django-sqids. Since this library merely "masks" the underlying integer IDs and does not modify the data, then there is
no process required to migrate data.

The main problem you'll face is that any published links with IDs in them, which is the main reason for a library such
as this, will no longer work. In those cases you may need to add some code to handle legacy links. If you used prefixes
then you will probably have to handle them yourself, since django-hashids and django-squids do not support prefixes.
This means stripping the prefix off of the string, then making the lookup with just the hashids part of the string.
Conversely, anywhere you generate a link and want a prefixed ID, then you'll need to stick it on manually.

Migrating to django-sqids would be a completely breaking change, since sqids are not compatible with hashids at all. So
their generated strings would not match.

## Reasoning 

There are many reasons which I feel a duty to explain.

### Hashids itself is retired

A big reason is that the Hashids libraries have been retired, and replaced with Sqids. You can read more on the 
[squids site](https://sqids.org/faq#why-hashids) about why this was done.

A new library called [django-sqids](https://pypi.org/project/django-sqids/) is available on PyPi. I have not used it
myself and so can not vouch for it. It's forked from the existing django-hashids library.

### The descriptor causes issues with other libraries

When I first wrote this library, for a project I was working on, it suited my uses perfectly. Still does. However, at
that time I didn't realize that it was considered bad practice in the Django world to use a descriptor that returns
an instance of an object, and does fancy stuff when you assign new values. It worked perfectly for me, made some
debugging and testing more straightforward, and didn't cause me any issues. However, it causes havoc with other
libraries that are written with the assumption that values of a Model object are basic types, like strings or ints.
The Hashid object and/or descriptor can be disabled to increase compatibility, but they are enabled by default.

### Replacing the id field causes issues

I designed this library to allow drop-in replacement so there is little or no changes necessary to get the benefit.
However, this again can cause major issues with other libraries that don't know what to do with a Hashid*Field. I
provided extra help for Django Rest Framework, for example, but as time has gone on, there have been other libraries
that are also confused. And since they can't just ignore the primary key field, there can sometimes be no way to get
them to work with this library.

### I am no longer a primary Django dev

I have moved away from Python and Django for my projects and career. I personally do not like the direction
that Python and Django are moving in. I think single-threaded async/await patterns are fragile, complicated, and I do
not like working with them. Also architecting more interactive features using websockets and advanced front-ends are
more complicated than they need to be. Before I get flamed to death, yes they are possible. I just don't like the
available solutions.

I found Elixir (the language) and Phoenix (the framework) many years ago, and started playing around and using it for
all of my personal projects. Even though it is missing some things (though not many) that the Python and Django world
have, it makes a lot of the hard things trivially easy. It vertically scales with much less friction than the
equivalent WSGI/ASGI application server, requiring no tuning of processes or threads. It supports websockets easily and
goes even farther with the magic that is Live View. It also has true preemptive concurrency and parallelism that isn't
built on fragile callbacks. It's much easier to reason about how things are processed and you never have an issue with
a function, async or not, stalling or crashing the system. It was built for high available, fault tolerance, and
both vertical and horizontal scaling in mind.

As a side note, in a recent project I duplicated all the parts of this library I cared about, based on NanoIDs,
including prefixes, in a custom Ecto.Field that is about 10 lines of code.

## Thank you

I'm sad to see this library retire, but I think it's time. It's been my most successful repo on github, and I thank
everyone for their support in the form of Issues and PRs. If you have any questions feel free to create a new Issue,
I will still be monitoring them.
