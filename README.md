Parsely API python
==================

This repo is a simple python binding for the Parsely API.
API docs, on which this binding is based, can be found at
http://parsely.com/api/api\_ref.html

To use these bindings:

    ipython
    >>> import parsely
    >>> p = parsely.Parsely("arstechnica.com", secret="asf98gf7aw98ev7nwe98vfayewfa9hew8f7ha")
    >>> p.shares()
    ...
    >>> p.analytics()
    ...
    # et cetera

To point the binding at the hackathon API, you can initialize the `Parsely`
object with

    >>> p = parsely.Parsely("arstechnica.com", root="http://hack.parsely.com/hackapi")

**DISCLAIMER**: This binding is almost completely untested and feedback, error
reports, or github issues are appreciated!
