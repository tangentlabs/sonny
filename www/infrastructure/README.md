Guide to importing framework
====

The point of this framework is to make allow to alter and monitor the behaviour
of importers uniformly, and transparently to the importers. It's usefulness
lies in the interfaces it provides for developers who want to write an Importer
to use various facilities, like logging or settings, and developers who want
to write a Facility.

You can find a copy-pastable [quick start guide], to get you started quickly.
An [annotated guide] with more commentary is available, to get a better
understanding of the conventions, by example.


Philosophy behind the choices:
====

## Automatic reuse of functionality and workflow

As a lot of functionality is **universal to all importing jobs** (eg profiling,
notifying), and we want to have the ability to **add such functionality,
without changing the importers** (eg log the first 5 lines of data, alert if
data doesn't "look like" historic records), we use **dependency injection and
inversion of control**.

## Transparency between layers of importing

The importer doesn't need to know about such a functionality, but can use it if
necessary (eg logging, config), even define importer-specifc overrides for it.

## Separation of concerns

We use a different piece of code for each type of fucntionality or operation,
in order to make it more testable and re-usable. To do this, we define very few
points of interfacing and conventions.

Layers structure
====

There are 4 layers of functionality:

1. Context: the mediator between Operations/Importers and Facilities -
   everything shoud pass through it
2. Facilities: Importer-generic functionality, that operates on `Job` and
   `Step` signals
3. Operations: Bundled up pieces of importing (eg FTP fetching, CSV loading)
4. Importers: Steps of Operations to perform a specific (or generic) import


API
====

All of these layers should communicate through the following interfaces:

## An importer

1. Should be a subclass of [Importer]
2. Should implement `do_run` with a `@helpers.step` decorator
3. Every step that is distinct and a part of the data flow should be decorated
   or inside a `with` statement of `step`
4. Can provide overrides for specific facilities via `JobSettings`
5. Can access any facility by `self.job.<facility>`
6. Should pass around generators for data, not huge lists/tuples

## An operation

1. Should encapsulate a single atomic operation
2. Should use `step` decorators/with statements for logging/profiling substeps
3. Should subclass 'OperationSettings' to allow importers to override per-run
   settings
3. Can access facilities via `helpers.get_current_job().<facility>`
4. Should provide an interface which implements, allowing specialisations
5. Should provide a no-op mock, if it makes sense for local testing

## A facility

1. Should be a subclass of [Facility]
2. Should subclass `FacilitySettings` to allow importers to override per-run
   settings
2. Should initialise in `enter_job`, and clean up in `exit_job`
3. Can use `enter_step` and `exit_step` to track steps
4. Can use `wrap_step` to manipulate the inputs and outputs of the step


[quick start guide]: https://github.com/tangentlabs/tangent-importer/blob/develop/docs/quick-start-guide.md
[annotated guide]: https://github.com/tangentlabs/tangent-importer/blob/develop/docs/annotated-guide.md

[Importer]: https://github.com/tangentlabs/tangent-importer/blob/develop/import_jobs/base.py
[Facility]: https://github.com/tangentlabs/tangent-importer/blob/develop/infrastructure/facilities/base.py
