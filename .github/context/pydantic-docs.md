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
    aliases.md
    annotated_handlers.md
    base_model.md
    config.md
    dataclasses.md
    errors.md
    experimental.md
    fields.md
    functional_serializers.md
    functional_validators.md
    json_schema.md
    networks.md
    pydantic_core_schema.md
    pydantic_core.md
    pydantic_extra_types_color.md
    pydantic_extra_types_coordinate.md
    pydantic_extra_types_country.md
    pydantic_extra_types_currency_code.md
    pydantic_extra_types_isbn.md
    pydantic_extra_types_language_code.md
    pydantic_extra_types_mac_address.md
    pydantic_extra_types_payment.md
    pydantic_extra_types_pendulum_dt.md
    pydantic_extra_types_phone_numbers.md
    pydantic_extra_types_routing_numbers.md
    pydantic_extra_types_script_code.md
    pydantic_extra_types_semantic_version.md
    pydantic_extra_types_timezone_name.md
    pydantic_extra_types_ulid.md
    pydantic_settings.md
    root_model.md
    standard_library_types.md
    type_adapter.md
    types.md
    validate_call.md
    version.md
  concepts/
    alias.md
    config.md
    conversion_table.md
    dataclasses.md
    experimental.md
    fields.md
    forward_annotations.md
    json_schema.md
    json.md
    models.md
    performance.md
    pydantic_settings.md
    serialization.md
    strict_mode.md
    type_adapter.md
    types.md
    unions.md
    validation_decorator.md
    validators.md
  errors/
    errors.md
    usage_errors.md
    validation_errors.md
  examples/
    custom_validators.md
    files.md
    orms.md
    queues.md
    requests.md
  integrations/
    aws_lambda.md
    datamodel_code_generator.md
    devtools.md
    documentation.md
    hypothesis.md
    linting.md
    llms.md
    logfire.md
    mypy.md
    pycharm.md
    rich.md
    visual_studio_code.md
  internals/
    architecture.md
    resolving_annotations.md
  contributing.md
  help_with_pydantic.md
  index.md
  install.md
  migration.md
  pydantic_people.md
  version-policy.md
  why.md
```

# Files

## File: docs/api/aliases.md
````markdown
::: pydantic.aliases
````

## File: docs/api/annotated_handlers.md
````markdown
::: pydantic.annotated_handlers
````

## File: docs/api/base_model.md
````markdown
Pydantic models are simply classes which inherit from `BaseModel` and define fields as annotated attributes.

::: pydantic.BaseModel
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - model_config
          - model_fields
          - model_computed_fields
          - __pydantic_core_schema__
          - model_extra
          - model_fields_set
          - model_construct
          - model_copy
          - model_dump
          - model_dump_json
          - model_json_schema
          - model_parametrized_name
          - model_post_init
          - model_rebuild
          - model_validate
          - model_validate_json
          - model_validate_strings

::: pydantic.create_model
    options:
        show_root_heading: true
````

## File: docs/api/config.md
````markdown
::: pydantic.config
    options:
      group_by_category: false
      members:
        - ConfigDict
        - with_config
        - ExtraValues
        - BaseConfig

::: pydantic.alias_generators
    options:
      show_root_heading: true
````

## File: docs/api/dataclasses.md
````markdown
::: pydantic.dataclasses
````

## File: docs/api/errors.md
````markdown
::: pydantic.errors
````

## File: docs/api/experimental.md
````markdown
# Experimental API

## Pipeline API

::: pydantic.experimental.pipeline
    options:
        members:
            - _Pipeline

## Arguments schema API

::: pydantic.experimental.arguments_schema
    options:
        members:
            - generate_arguments_schema
````

## File: docs/api/fields.md
````markdown
::: pydantic.fields
    options:
      group_by_category: false
      members:
        - Field
        - FieldInfo
        - PrivateAttr
        - ModelPrivateAttr
        - computed_field
        - ComputedFieldInfo
````

## File: docs/api/functional_serializers.md
````markdown
::: pydantic.functional_serializers
````

## File: docs/api/functional_validators.md
````markdown
::: pydantic.functional_validators
````

## File: docs/api/json_schema.md
````markdown
::: pydantic.json_schema
````

## File: docs/api/networks.md
````markdown
::: pydantic.networks
````

## File: docs/api/pydantic_core_schema.md
````markdown
::: pydantic_core.core_schema
````

## File: docs/api/pydantic_core.md
````markdown
::: pydantic_core
    options:
        allow_inspection: false
        show_source: false
        members:
        - SchemaValidator
        - SchemaSerializer
        - ValidationError
        - ErrorDetails
        - InitErrorDetails
        - SchemaError
        - PydanticCustomError
        - PydanticKnownError
        - PydanticOmit
        - PydanticUseDefault
        - PydanticSerializationError
        - PydanticSerializationUnexpectedValue
        - Url
        - MultiHostUrl
        - MultiHostHost
        - ArgsKwargs
        - Some
        - TzInfo
        - to_json
        - from_json
        - to_jsonable_python
        - list_all_errors
        - ErrorTypeInfo
        - __version__
````

## File: docs/api/pydantic_extra_types_color.md
````markdown
::: pydantic_extra_types.color
````

## File: docs/api/pydantic_extra_types_coordinate.md
````markdown
::: pydantic_extra_types.coordinate
````

## File: docs/api/pydantic_extra_types_country.md
````markdown
::: pydantic_extra_types.country
````

## File: docs/api/pydantic_extra_types_currency_code.md
````markdown
::: pydantic_extra_types.currency_code
````

## File: docs/api/pydantic_extra_types_isbn.md
````markdown
::: pydantic_extra_types.isbn
````

## File: docs/api/pydantic_extra_types_language_code.md
````markdown
::: pydantic_extra_types.language_code
````

## File: docs/api/pydantic_extra_types_mac_address.md
````markdown
::: pydantic_extra_types.mac_address
````

## File: docs/api/pydantic_extra_types_payment.md
````markdown
::: pydantic_extra_types.payment
````

## File: docs/api/pydantic_extra_types_pendulum_dt.md
````markdown
::: pydantic_extra_types.pendulum_dt
````

## File: docs/api/pydantic_extra_types_phone_numbers.md
````markdown
::: pydantic_extra_types.phone_numbers
````

## File: docs/api/pydantic_extra_types_routing_numbers.md
````markdown
::: pydantic_extra_types.routing_number
````

## File: docs/api/pydantic_extra_types_script_code.md
````markdown
::: pydantic_extra_types.script_code
````

## File: docs/api/pydantic_extra_types_semantic_version.md
````markdown
::: pydantic_extra_types.semantic_version
````

## File: docs/api/pydantic_extra_types_timezone_name.md
````markdown
::: pydantic_extra_types.timezone_name
````

## File: docs/api/pydantic_extra_types_ulid.md
````markdown
::: pydantic_extra_types.ulid
````

## File: docs/api/pydantic_settings.md
````markdown
::: pydantic_settings
````

## File: docs/api/root_model.md
````markdown
::: pydantic.root_model
````

## File: docs/api/standard_library_types.md
````markdown
---
description: Support for common types from the Python standard library.
---

Pydantic supports many common types from the Python standard library. If you need stricter processing see
[Strict Types](../concepts/types.md#strict-types), including if you need to constrain the values allowed (e.g. to require a positive `int`).

!!! note
    Pydantic still supports older (3.8-) typing constructs like `typing.List` and `typing.Dict`, but
    it's best practice to use the newer types like `list` and `dict`.

## Booleans

A standard `bool` field will raise a `ValidationError` if the value is not one of the following:

* A valid boolean (i.e. `True` or `False`),
* The integers `0` or `1`,
* a `str` which when converted to lower case is one of
  `'0', 'off', 'f', 'false', 'n', 'no', '1', 'on', 't', 'true', 'y', 'yes'`
* a `bytes` which is valid per the previous rule when decoded to `str`

!!! note
    If you want stricter boolean logic (e.g. a field which only permits `True` and `False`) you can
    use [`StrictBool`](../api/types.md#pydantic.types.StrictBool).

Here is a script demonstrating some of these behaviors:

```python
from pydantic import BaseModel, ValidationError


class BooleanModel(BaseModel):
    bool_value: bool


print(BooleanModel(bool_value=False))
#> bool_value=False
print(BooleanModel(bool_value='False'))
#> bool_value=False
print(BooleanModel(bool_value=1))
#> bool_value=True
try:
    BooleanModel(bool_value=[])
except ValidationError as e:
    print(str(e))
    """
    1 validation error for BooleanModel
    bool_value
      Input should be a valid boolean [type=bool_type, input_value=[], input_type=list]
    """
```

## Datetime Types

Pydantic supports the following [datetime](https://docs.python.org/library/datetime.html#available-types)
types:

### [`datetime.datetime`][]

* `datetime` fields will accept values of type:
    * `datetime`; an existing `datetime` object
    * `int` or `float`; assumed as Unix time, i.e. seconds (if >= `-2e10` and <= `2e10`) or milliseconds
      (if < `-2e10`or > `2e10`) since 1 January 1970
    * `str`; the following formats are accepted:
        * `YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]`
        * `YYYY-MM-DD` is accepted in lax mode, but not in strict mode
        * `int` or `float` as a string (assumed as Unix time)
    * [`datetime.date`][] instances are accepted in lax mode, but not in strict mode

```python
from datetime import datetime

from pydantic import BaseModel


class Event(BaseModel):
    dt: datetime = None


event = Event(dt='2032-04-23T10:20:30.400+02:30')

print(event.model_dump())
"""
{'dt': datetime.datetime(2032, 4, 23, 10, 20, 30, 400000, tzinfo=TzInfo(9000))}
"""
```

### [`datetime.date`][]

* `date` fields will accept values of type:
    * `date`; an existing `date` object
    * `int` or `float`; handled the same as described for `datetime` above
    * `str`; the following formats are accepted:
        * `YYYY-MM-DD`
        * `int` or `float` as a string (assumed as Unix time)

```python
from datetime import date

from pydantic import BaseModel


class Birthday(BaseModel):
    d: date = None


my_birthday = Birthday(d=1679616000.0)

print(my_birthday.model_dump())
#> {'d': datetime.date(2023, 3, 24)}
```

### [`datetime.time`][]

* `time` fields will accept values of type:

    * `time`; an existing `time` object
    * `str`; the following formats are accepted:
        * `HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]`

```python
from datetime import time

from pydantic import BaseModel


class Meeting(BaseModel):
    t: time = None


m = Meeting(t=time(4, 8, 16))

print(m.model_dump())
#> {'t': datetime.time(4, 8, 16)}
```

### [`datetime.timedelta`][]

* `timedelta` fields will accept values of type:

    * `timedelta`; an existing `timedelta` object
    * `int` or `float`; assumed to be seconds
    * `str`; the following formats are accepted:
        * `[-][[DD]D,]HH:MM:SS[.ffffff]`
            * Ex: `'1d,01:02:03.000004'` or `'1D01:02:03.000004'` or `'01:02:03'`
        * `[±]P[DD]DT[HH]H[MM]M[SS]S` ([ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) format for timedelta)

```python
from datetime import timedelta

from pydantic import BaseModel


class Model(BaseModel):
    td: timedelta = None


m = Model(td='P3DT12H30M5S')

print(m.model_dump())
#> {'td': datetime.timedelta(days=3, seconds=45005)}
```

## Number Types

Pydantic supports the following numeric types from the Python standard library:

### [`int`][]

* Pydantic uses `int(v)` to coerce types to an `int`;
  see [Data conversion](../concepts/models.md#data-conversion) for details on loss of information during data conversion.

### [`float`][]

* Pydantic uses `float(v)` to coerce values to floats.

### [`enum.IntEnum`][]

* Validation: Pydantic checks that the value is a valid `IntEnum` instance.
* Validation for subclass of `enum.IntEnum`: checks that the value is a valid member of the integer enum;
  see [Enums and Choices](#enum) for more details.

### [`decimal.Decimal`][]

* Validation: Pydantic attempts to convert the value to a string, then passes the string to `Decimal(v)`.
* Serialization: Pydantic serializes [`Decimal`][decimal.Decimal] types as strings.
You can use a custom serializer to override this behavior if desired. For example:

```python
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, PlainSerializer


class Model(BaseModel):
    x: Decimal
    y: Annotated[
        Decimal,
        PlainSerializer(
            lambda x: float(x), return_type=float, when_used='json'
        ),
    ]


my_model = Model(x=Decimal('1.1'), y=Decimal('2.1'))

print(my_model.model_dump())  # (1)!
#> {'x': Decimal('1.1'), 'y': Decimal('2.1')}
print(my_model.model_dump(mode='json'))  # (2)!
#> {'x': '1.1', 'y': 2.1}
print(my_model.model_dump_json())  # (3)!
#> {"x":"1.1","y":2.1}
```

1. Using [`model_dump`][pydantic.main.BaseModel.model_dump], both `x` and `y` remain instances of the `Decimal` type
2. Using [`model_dump`][pydantic.main.BaseModel.model_dump] with `mode='json'`, `x` is serialized as a `string`, and `y` is serialized as a `float` because of the custom serializer applied.
3. Using [`model_dump_json`][pydantic.main.BaseModel.model_dump_json], `x` is serialized as a `string`, and `y` is serialized as a `float` because of the custom serializer applied.

### [`complex`][]

* Validation: Pydantic supports `complex` types or `str` values that can be converted to a `complex` type.
* Serialization: Pydantic serializes [`complex`][] types as strings.

### [`fractions.Fraction`][fractions.Fraction]

* Validation: Pydantic attempts to convert the value to a `Fraction` using `Fraction(v)`.
* Serialization: Pydantic serializes [`Fraction`][fractions.Fraction] types as strings.

## [`Enum`][enum.Enum]

Pydantic uses Python's standard [`enum`][] classes to define choices.

`enum.Enum` checks that the value is a valid `Enum` instance.
Subclass of `enum.Enum` checks that the value is a valid member of the enum.

```python
from enum import Enum, IntEnum

from pydantic import BaseModel, ValidationError


class FruitEnum(str, Enum):
    pear = 'pear'
    banana = 'banana'


class ToolEnum(IntEnum):
    spanner = 1
    wrench = 2


class CookingModel(BaseModel):
    fruit: FruitEnum = FruitEnum.pear
    tool: ToolEnum = ToolEnum.spanner


print(CookingModel())
#> fruit=<FruitEnum.pear: 'pear'> tool=<ToolEnum.spanner: 1>
print(CookingModel(tool=2, fruit='banana'))
#> fruit=<FruitEnum.banana: 'banana'> tool=<ToolEnum.wrench: 2>
try:
    CookingModel(fruit='other')
except ValidationError as e:
    print(e)
    """
    1 validation error for CookingModel
    fruit
      Input should be 'pear' or 'banana' [type=enum, input_value='other', input_type=str]
    """
```

## Lists and Tuples

### [`list`][]

Allows [`list`][], [`tuple`][], [`set`][], [`frozenset`][], [`deque`][collections.deque], or generators and casts to a [`list`][].
When a generic parameter is provided, the appropriate validation is applied to all items of the list.

```python
from typing import Optional

from pydantic import BaseModel


class Model(BaseModel):
    simple_list: Optional[list] = None
    list_of_ints: Optional[list[int]] = None


print(Model(simple_list=['1', '2', '3']).simple_list)
#> ['1', '2', '3']
print(Model(list_of_ints=['1', '2', '3']).list_of_ints)
#> [1, 2, 3]
```

### [`tuple`][]

Allows [`list`][], [`tuple`][], [`set`][], [`frozenset`][], [`deque`][collections.deque], or generators and casts to a [`tuple`][].
When generic parameters are provided, the appropriate validation is applied to the respective items of the tuple

### [`typing.Tuple`][]

Handled the same as `tuple` above.

```python
from typing import Optional

from pydantic import BaseModel


class Model(BaseModel):
    simple_tuple: Optional[tuple] = None
    tuple_of_different_types: Optional[tuple[int, float, bool]] = None


print(Model(simple_tuple=[1, 2, 3, 4]).simple_tuple)
#> (1, 2, 3, 4)
print(Model(tuple_of_different_types=[3, 2, 1]).tuple_of_different_types)
#> (3, 2.0, True)
```

### [`typing.NamedTuple`][]

Subclasses of [`typing.NamedTuple`][] are similar to `tuple`, but create instances of the given `namedtuple` class.

Subclasses of [`collections.namedtuple`][] are similar to subclass of [`typing.NamedTuple`][], but since field types are not specified,
all fields are treated as having type [`Any`][typing.Any].

```python
from typing import NamedTuple

from pydantic import BaseModel, ValidationError


class Point(NamedTuple):
    x: int
    y: int


class Model(BaseModel):
    p: Point


try:
    Model(p=('1.3', '2'))
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    p.0
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='1.3', input_type=str]
    """
```

## Deque

### [`deque`][collections.deque]

Allows [`list`][], [`tuple`][], [`set`][], [`frozenset`][], [`deque`][collections.deque], or generators and casts to a [`deque`][collections.deque].
When generic parameters are provided, the appropriate validation is applied to the respective items of the `deque`.

### [`typing.Deque`][]

Handled the same as `deque` above.

```python
from typing import Deque, Optional

from pydantic import BaseModel


class Model(BaseModel):
    deque: Optional[Deque[int]] = None


print(Model(deque=[1, 2, 3]).deque)
#> deque([1, 2, 3])
```

## Sets

### [`set`][]

Allows [`list`][], [`tuple`][], [`set`][], [`frozenset`][], [`deque`][collections.deque], or generators and casts to a [`set`][].
When a generic parameter is provided, the appropriate validation is applied to all items of the set.

### [`typing.Set`][]

Handled the same as `set` above.

```python
from typing import Optional, Set

from pydantic import BaseModel


class Model(BaseModel):
    simple_set: Optional[set] = None
    set_of_ints: Optional[Set[int]] = None


print(Model(simple_set={'1', '2', '3'}).simple_set)
#> {'1', '2', '3'}
print(Model(simple_set=['1', '2', '3']).simple_set)
#> {'1', '2', '3'}
print(Model(set_of_ints=['1', '2', '3']).set_of_ints)
#> {1, 2, 3}
```

### [`frozenset`][]

Allows [`list`][], [`tuple`][], [`set`][], [`frozenset`][], [`deque`][collections.deque], or generators and casts to a [`frozenset`][].
When a generic parameter is provided, the appropriate validation is applied to all items of the frozen set.

### [`typing.FrozenSet`][]

Handled the same as `frozenset` above.

```python
from typing import FrozenSet, Optional

from pydantic import BaseModel


class Model(BaseModel):
    simple_frozenset: Optional[frozenset] = None
    frozenset_of_ints: Optional[FrozenSet[int]] = None


m1 = Model(simple_frozenset=['1', '2', '3'])
print(type(m1.simple_frozenset))
#> <class 'frozenset'>
print(sorted(m1.simple_frozenset))
#> ['1', '2', '3']

m2 = Model(frozenset_of_ints=['1', '2', '3'])
print(type(m2.frozenset_of_ints))
#> <class 'frozenset'>
print(sorted(m2.frozenset_of_ints))
#> [1, 2, 3]
```

## Other Iterables

### [`typing.Sequence`][]

This is intended for use when the provided value should meet the requirements of the `Sequence` ABC, and it is
desirable to do eager validation of the values in the container. Note that when validation must be performed on the
values of the container, the type of the container may not be preserved since validation may end up replacing values.
We guarantee that the validated value will be a valid [`typing.Sequence`][], but it may have a different type than was
provided (generally, it will become a `list`).

### [`typing.Iterable`][]

This is intended for use when the provided value may be an iterable that shouldn't be consumed.
See [Infinite Generators](#infinite-generators) below for more detail on parsing and validation.
Similar to [`typing.Sequence`][], we guarantee that the validated result will be a valid [`typing.Iterable`][],
but it may have a different type than was provided. In particular, even if a non-generator type such as a `list`
is provided, the post-validation value of a field of type [`typing.Iterable`][] will be a generator.

Here is a simple example using [`typing.Sequence`][]:

```python
from typing import Sequence

from pydantic import BaseModel


class Model(BaseModel):
    sequence_of_ints: Sequence[int] = None


print(Model(sequence_of_ints=[1, 2, 3, 4]).sequence_of_ints)
#> [1, 2, 3, 4]
print(Model(sequence_of_ints=(1, 2, 3, 4)).sequence_of_ints)
#> (1, 2, 3, 4)
```

### Infinite Generators

If you have a generator you want to validate, you can still use `Sequence` as described above.
In that case, the generator will be consumed and stored on the model as a list and its values will be
validated against the type parameter of the `Sequence` (e.g. `int` in `Sequence[int]`).

However, if you have a generator that you *don't* want to be eagerly consumed (e.g. an infinite
generator or a remote data loader), you can use a field of type [`Iterable`][typing.Iterable]:

```python
from typing import Iterable

from pydantic import BaseModel


class Model(BaseModel):
    infinite: Iterable[int]


def infinite_ints():
    i = 0
    while True:
        yield i
        i += 1


m = Model(infinite=infinite_ints())
print(m)
"""
infinite=ValidatorIterator(index=0, schema=Some(Int(IntValidator { strict: false })))
"""

for i in m.infinite:
    print(i)
    #> 0
    #> 1
    #> 2
    #> 3
    #> 4
    #> 5
    #> 6
    #> 7
    #> 8
    #> 9
    #> 10
    if i == 10:
        break
```

!!! warning
    During initial validation, `Iterable` fields only perform a simple check that the provided argument is iterable.
    To prevent it from being consumed, no validation of the yielded values is performed eagerly.

Though the yielded values are not validated eagerly, they are still validated when yielded, and will raise a
`ValidationError` at yield time when appropriate:

```python
from typing import Iterable

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    int_iterator: Iterable[int]


def my_iterator():
    yield 13
    yield '27'
    yield 'a'


m = Model(int_iterator=my_iterator())
print(next(m.int_iterator))
#> 13
print(next(m.int_iterator))
#> 27
try:
    next(m.int_iterator)
except ValidationError as e:
    print(e)
    """
    1 validation error for ValidatorIterator
    2
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """
```

## Mapping Types

### [`dict`][]

`dict(v)` is used to attempt to convert a dictionary.

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: dict[str, int]


m = Model(x={'foo': 1})
print(m.model_dump())
#> {'x': {'foo': 1}}

try:
    Model(x={'foo': '1'})
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    x
      Input should be a valid dictionary [type=dict_type, input_value='test', input_type=str]
    """
```

### TypedDict

!!! note
    This is a new feature of the Python standard library as of Python 3.8.
    Because of limitations in [typing.TypedDict][] before 3.12, the [typing-extensions](https://pypi.org/project/typing-extensions/)
    package is required for Python <3.12. You'll need to import `TypedDict` from `typing_extensions` instead of `typing` and will
    get a build time error if you don't.

[`TypedDict`][typing.TypedDict] declares a dictionary type that expects all of
its instances to have a certain set of keys, where each key is associated with a value of a consistent type.

It is same as [`dict`][] but Pydantic will validate the dictionary since keys are annotated.

```python
from typing_extensions import TypedDict

from pydantic import TypeAdapter, ValidationError


class User(TypedDict):
    name: str
    id: int


ta = TypeAdapter(User)

print(ta.validate_python({'name': 'foo', 'id': 1}))
#> {'name': 'foo', 'id': 1}

try:
    ta.validate_python({'name': 'foo'})
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    id
      Field required [type=missing, input_value={'name': 'foo'}, input_type=dict]
    """
```

You can define `__pydantic_config__` to change the model inherited from [`TypedDict`][typing.TypedDict].
See the [`ConfigDict` API reference][pydantic.config.ConfigDict] for more details.

```python
from typing import Optional

from typing_extensions import TypedDict

from pydantic import ConfigDict, TypeAdapter, ValidationError


# `total=False` means keys are non-required
class UserIdentity(TypedDict, total=False):
    name: Optional[str]
    surname: str


class User(TypedDict):
    __pydantic_config__ = ConfigDict(extra='forbid')

    identity: UserIdentity
    age: int


ta = TypeAdapter(User)

print(
    ta.validate_python(
        {'identity': {'name': 'Smith', 'surname': 'John'}, 'age': 37}
    )
)
#> {'identity': {'name': 'Smith', 'surname': 'John'}, 'age': 37}

print(
    ta.validate_python(
        {'identity': {'name': None, 'surname': 'John'}, 'age': 37}
    )
)
#> {'identity': {'name': None, 'surname': 'John'}, 'age': 37}

print(ta.validate_python({'identity': {}, 'age': 37}))
#> {'identity': {}, 'age': 37}


try:
    ta.validate_python(
        {'identity': {'name': ['Smith'], 'surname': 'John'}, 'age': 24}
    )
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    identity.name
      Input should be a valid string [type=string_type, input_value=['Smith'], input_type=list]
    """

try:
    ta.validate_python(
        {
            'identity': {'name': 'Smith', 'surname': 'John'},
            'age': '37',
            'email': 'john.smith@me.com',
        }
    )
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    email
      Extra inputs are not permitted [type=extra_forbidden, input_value='john.smith@me.com', input_type=str]
    """
```

## Callable

See below for more detail on parsing and validation

Fields can also be of type [`Callable`][typing.Callable]:

```python
from typing import Callable

from pydantic import BaseModel


class Foo(BaseModel):
    callback: Callable[[int], int]


m = Foo(callback=lambda x: x)
print(m)
#> callback=<function <lambda> at 0x0123456789ab>
```

!!! warning
    Callable fields only perform a simple check that the argument is
    callable; no validation of arguments, their types, or the return
    type is performed.

## IP Address Types

* [`ipaddress.IPv4Address`][]: Uses the type itself for validation by passing the value to `IPv4Address(v)`.
* [`ipaddress.IPv4Interface`][]: Uses the type itself for validation by passing the value to `IPv4Address(v)`.
* [`ipaddress.IPv4Network`][]: Uses the type itself for validation by passing the value to `IPv4Network(v)`.
* [`ipaddress.IPv6Address`][]: Uses the type itself for validation by passing the value to `IPv6Address(v)`.
* [`ipaddress.IPv6Interface`][]: Uses the type itself for validation by passing the value to `IPv6Interface(v)`.
* [`ipaddress.IPv6Network`][]: Uses the type itself for validation by passing the value to `IPv6Network(v)`.

See [Network Types](../api/networks.md) for other custom IP address types.

## UUID

For UUID, Pydantic tries to use the type itself for validation by passing the value to `UUID(v)`.
There's a fallback to `UUID(bytes=v)` for `bytes` and `bytearray`.

In case you want to constrain the UUID version, you can check the following types:

* [`UUID1`][pydantic.types.UUID1]: requires UUID version 1.
* [`UUID3`][pydantic.types.UUID3]: requires UUID version 3.
* [`UUID4`][pydantic.types.UUID4]: requires UUID version 4.
* [`UUID5`][pydantic.types.UUID5]: requires UUID version 5.

## Union

Pydantic has extensive support for union validation, both [`typing.Union`][] and Python 3.10's pipe syntax (`A | B`) are supported.
Read more in the [`Unions`](../concepts/unions.md) section of the concepts docs.

## [`type`][]

Pydantic supports the use of `type[T]` to specify that a field may only accept classes (not instances)
that are subclasses of `T`.

```python
from pydantic import BaseModel, ValidationError


class Foo:
    pass


class Bar(Foo):
    pass


class Other:
    pass


class SimpleModel(BaseModel):
    just_subclasses: type[Foo]


SimpleModel(just_subclasses=Foo)
SimpleModel(just_subclasses=Bar)
try:
    SimpleModel(just_subclasses=Other)
except ValidationError as e:
    print(e)
    """
    1 validation error for SimpleModel
    just_subclasses
      Input should be a subclass of Foo [type=is_subclass_of, input_value=<class '__main__.Other'>, input_type=type]
    """
```

You may also use `type` to specify that any class is allowed.

```python {upgrade="skip"}
from pydantic import BaseModel, ValidationError


class Foo:
    pass


class LenientSimpleModel(BaseModel):
    any_class_goes: type


LenientSimpleModel(any_class_goes=int)
LenientSimpleModel(any_class_goes=Foo)
try:
    LenientSimpleModel(any_class_goes=Foo())
except ValidationError as e:
    print(e)
    """
    1 validation error for LenientSimpleModel
    any_class_goes
      Input should be a type [type=is_type, input_value=<__main__.Foo object at 0x0123456789ab>, input_type=Foo]
    """
```

## [`typing.TypeVar`][]

[`TypeVar`][typing.TypeVar] is supported either unconstrained, constrained or with a bound.

```python
from typing import TypeVar

from pydantic import BaseModel

Foobar = TypeVar('Foobar')
BoundFloat = TypeVar('BoundFloat', bound=float)
IntStr = TypeVar('IntStr', int, str)


class Model(BaseModel):
    a: Foobar  # equivalent of ": Any"
    b: BoundFloat  # equivalent of ": float"
    c: IntStr  # equivalent of ": Union[int, str]"


print(Model(a=[1], b=4.2, c='x'))
#> a=[1] b=4.2 c='x'

# a may be None
print(Model(a=None, b=1, c=1))
#> a=None b=1.0 c=1
```

## None Types

[`None`][], `type(None)`, or `Literal[None]` are all equivalent according to [the typing specification](https://typing.readthedocs.io/en/latest/spec/special-types.html#none).
Allows only `None` value.

## Strings

* [`str`][]: Strings are accepted as-is.
* [`bytes`][] and [`bytearray`][] are converted using the [`decode()`][bytes.decode] method.
* Enums inheriting from [`str`][] are converted using the [`value`][enum.Enum.value] attribute.

All other types cause an error.
<!-- * TODO: add note about optional number to string conversion from lig's PR -->

!!! warning "Strings aren't Sequences"

    While instances of `str` are technically valid instances of the `Sequence[str]` protocol from a type-checker's point of
    view, this is frequently not intended as is a common source of bugs.

    As a result, Pydantic raises a `ValidationError` if you attempt to pass a `str` or `bytes` instance into a field of type
    `Sequence[str]` or `Sequence[bytes]`:

```python
from typing import Optional, Sequence

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    sequence_of_strs: Optional[Sequence[str]] = None
    sequence_of_bytes: Optional[Sequence[bytes]] = None


print(Model(sequence_of_strs=['a', 'bc']).sequence_of_strs)
#> ['a', 'bc']
print(Model(sequence_of_strs=('a', 'bc')).sequence_of_strs)
#> ('a', 'bc')
print(Model(sequence_of_bytes=[b'a', b'bc']).sequence_of_bytes)
#> [b'a', b'bc']
print(Model(sequence_of_bytes=(b'a', b'bc')).sequence_of_bytes)
#> (b'a', b'bc')


try:
    Model(sequence_of_strs='abc')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    sequence_of_strs
      'str' instances are not allowed as a Sequence value [type=sequence_str, input_value='abc', input_type=str]
    """
try:
    Model(sequence_of_bytes=b'abc')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    sequence_of_bytes
      'bytes' instances are not allowed as a Sequence value [type=sequence_str, input_value=b'abc', input_type=bytes]
    """
```

## Bytes

[`bytes`][] are accepted as-is. [`bytearray`][] is converted using `bytes(v)`. `str` are converted using `v.encode()`. `int`, `float`, and `Decimal` are coerced using `str(v).encode()`. See [ByteSize](types.md#pydantic.types.ByteSize) for more details.

## [`typing.Literal`][]

Pydantic supports the use of [`typing.Literal`][] as a lightweight way to specify that a field may accept only specific literal values:

```python
from typing import Literal

from pydantic import BaseModel, ValidationError


class Pie(BaseModel):
    flavor: Literal['apple', 'pumpkin']


Pie(flavor='apple')
Pie(flavor='pumpkin')
try:
    Pie(flavor='cherry')
except ValidationError as e:
    print(str(e))
    """
    1 validation error for Pie
    flavor
      Input should be 'apple' or 'pumpkin' [type=literal_error, input_value='cherry', input_type=str]
    """
```

One benefit of this field type is that it can be used to check for equality with one or more specific values
without needing to declare custom validators:

```python
from typing import ClassVar, Literal, Union

from pydantic import BaseModel, ValidationError


class Cake(BaseModel):
    kind: Literal['cake']
    required_utensils: ClassVar[list[str]] = ['fork', 'knife']


class IceCream(BaseModel):
    kind: Literal['icecream']
    required_utensils: ClassVar[list[str]] = ['spoon']


class Meal(BaseModel):
    dessert: Union[Cake, IceCream]


print(type(Meal(dessert={'kind': 'cake'}).dessert).__name__)
#> Cake
print(type(Meal(dessert={'kind': 'icecream'}).dessert).__name__)
#> IceCream
try:
    Meal(dessert={'kind': 'pie'})
except ValidationError as e:
    print(str(e))
    """
    2 validation errors for Meal
    dessert.Cake.kind
      Input should be 'cake' [type=literal_error, input_value='pie', input_type=str]
    dessert.IceCream.kind
      Input should be 'icecream' [type=literal_error, input_value='pie', input_type=str]
    """
```

With proper ordering in an annotated `Union`, you can use this to parse types of decreasing specificity:

```python
from typing import Literal, Optional, Union

from pydantic import BaseModel


class Dessert(BaseModel):
    kind: str


class Pie(Dessert):
    kind: Literal['pie']
    flavor: Optional[str]


class ApplePie(Pie):
    flavor: Literal['apple']


class PumpkinPie(Pie):
    flavor: Literal['pumpkin']


class Meal(BaseModel):
    dessert: Union[ApplePie, PumpkinPie, Pie, Dessert]


print(type(Meal(dessert={'kind': 'pie', 'flavor': 'apple'}).dessert).__name__)
#> ApplePie
print(type(Meal(dessert={'kind': 'pie', 'flavor': 'pumpkin'}).dessert).__name__)
#> PumpkinPie
print(type(Meal(dessert={'kind': 'pie'}).dessert).__name__)
#> Dessert
print(type(Meal(dessert={'kind': 'cake'}).dessert).__name__)
#> Dessert
```

## [`typing.Any`][]

Allows any value, including `None`.

## [`typing.Hashable`][]

* From Python, supports any data that passes an `isinstance(v, Hashable)` check.
* From JSON, first loads the data via an `Any` validator, then checks if the data is hashable with `isinstance(v, Hashable)`.

## [`typing.Annotated`][]

Allows wrapping another type with arbitrary metadata, as per [PEP-593](https://www.python.org/dev/peps/pep-0593/). The `Annotated` hint may contain a single call to the [`Field` function](../concepts/types.md#using-the-annotated-pattern), but otherwise the additional metadata is ignored and the root type is used.

## [`typing.Pattern`][]

Will cause the input value to be passed to `re.compile(v)` to create a regular expression pattern.

## [`pathlib.Path`][]

Simply uses the type itself for validation by passing the value to `Path(v)`.
````

## File: docs/api/type_adapter.md
````markdown
::: pydantic.type_adapter.TypeAdapter
````

## File: docs/api/types.md
````markdown
::: pydantic.types
    options:
        show_root_heading: true
        merge_init_into_class: false
````

## File: docs/api/validate_call.md
````markdown
::: pydantic.validate_call_decorator
````

## File: docs/api/version.md
````markdown
::: pydantic.__version__
    options:
        show_root_heading: true

::: pydantic.version.version_info
    options:
        show_root_heading: true
````

## File: docs/concepts/alias.md
````markdown
An alias is an alternative name for a field, used when serializing and deserializing data.

You can specify an alias in the following ways:

* `alias` on the [`Field`][pydantic.fields.Field]
    * must be a `str`
* `validation_alias` on the [`Field`][pydantic.fields.Field]
    * can be an instance of `str`, [`AliasPath`][pydantic.aliases.AliasPath], or [`AliasChoices`][pydantic.aliases.AliasChoices]
* `serialization_alias` on the [`Field`][pydantic.fields.Field]
    * must be a `str`
* `alias_generator` on the [`Config`][pydantic.config.ConfigDict.alias_generator]
    * can be a callable or an instance of [`AliasGenerator`][pydantic.aliases.AliasGenerator]

For examples of how to use `alias`, `validation_alias`, and `serialization_alias`, see [Field aliases](../concepts/fields.md#field-aliases).

## `AliasPath` and `AliasChoices`

??? api "API Documentation"

    [`pydantic.aliases.AliasPath`][pydantic.aliases.AliasPath]<br>
    [`pydantic.aliases.AliasChoices`][pydantic.aliases.AliasChoices]<br>

Pydantic provides two special types for convenience when using `validation_alias`: `AliasPath` and `AliasChoices`.

The `AliasPath` is used to specify a path to a field using aliases. For example:

```python {lint="skip"}
from pydantic import BaseModel, Field, AliasPath


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasPath('names', 0))
    last_name: str = Field(validation_alias=AliasPath('names', 1))

user = User.model_validate({'names': ['John', 'Doe']})  # (1)!
print(user)
#> first_name='John' last_name='Doe'
```

1. We are using `model_validate` to validate a dictionary using the field aliases.

    You can see more details about [`model_validate`][pydantic.main.BaseModel.model_validate] in the API reference.

In the `'first_name'` field, we are using the alias `'names'` and the index `0` to specify the path to the first name.
In the `'last_name'` field, we are using the alias `'names'` and the index `1` to specify the path to the last name.

`AliasChoices` is used to specify a choice of aliases. For example:

```python {lint="skip"}
from pydantic import BaseModel, Field, AliasChoices


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', 'fname'))
    last_name: str = Field(validation_alias=AliasChoices('last_name', 'lname'))

user = User.model_validate({'fname': 'John', 'lname': 'Doe'})  # (1)!
print(user)
#> first_name='John' last_name='Doe'
user = User.model_validate({'first_name': 'John', 'lname': 'Doe'})  # (2)!
print(user)
#> first_name='John' last_name='Doe'
```

1. We are using the second alias choice for both fields.
2. We are using the first alias choice for the field `'first_name'` and the second alias choice
   for the field `'last_name'`.

You can also use `AliasChoices` with `AliasPath`:

```python {lint="skip"}
from pydantic import BaseModel, Field, AliasPath, AliasChoices


class User(BaseModel):
    first_name: str = Field(validation_alias=AliasChoices('first_name', AliasPath('names', 0)))
    last_name: str = Field(validation_alias=AliasChoices('last_name', AliasPath('names', 1)))


user = User.model_validate({'first_name': 'John', 'last_name': 'Doe'})
print(user)
#> first_name='John' last_name='Doe'
user = User.model_validate({'names': ['John', 'Doe']})
print(user)
#> first_name='John' last_name='Doe'
user = User.model_validate({'names': ['John'], 'last_name': 'Doe'})
print(user)
#> first_name='John' last_name='Doe'
```

## Using alias generators

You can use the `alias_generator` parameter of [`Config`][pydantic.config.ConfigDict.alias_generator] to specify
a callable (or group of callables, via `AliasGenerator`) that will generate aliases for all fields in a model.
This is useful if you want to use a consistent naming convention for all fields in a model, but do not
want to specify the alias for each field individually.

!!! note
    Pydantic offers three built-in alias generators that you can use out of the box:

    [`to_pascal`][pydantic.alias_generators.to_pascal]<br>
    [`to_camel`][pydantic.alias_generators.to_camel]<br>
    [`to_snake`][pydantic.alias_generators.to_snake]<br>

### Using a callable

Here's a basic example using a callable:

```python
from pydantic import BaseModel, ConfigDict


class Tree(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda field_name: field_name.upper()
    )

    age: int
    height: float
    kind: str


t = Tree.model_validate({'AGE': 12, 'HEIGHT': 1.2, 'KIND': 'oak'})
print(t.model_dump(by_alias=True))
#> {'AGE': 12, 'HEIGHT': 1.2, 'KIND': 'oak'}
```

### Using an `AliasGenerator`

??? api "API Documentation"

    [`pydantic.aliases.AliasGenerator`][pydantic.aliases.AliasGenerator]<br>

`AliasGenerator` is a class that allows you to specify multiple alias generators for a model.
You can use an `AliasGenerator` to specify different alias generators for validation and serialization.

This is particularly useful if you need to use different naming conventions for loading and saving data,
but you don't want to specify the validation and serialization aliases for each field individually.

For example:

```python
from pydantic import AliasGenerator, BaseModel, ConfigDict


class Tree(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=lambda field_name: field_name.upper(),
            serialization_alias=lambda field_name: field_name.title(),
        )
    )

    age: int
    height: float
    kind: str


t = Tree.model_validate({'AGE': 12, 'HEIGHT': 1.2, 'KIND': 'oak'})
print(t.model_dump(by_alias=True))
#> {'Age': 12, 'Height': 1.2, 'Kind': 'oak'}
```

## Alias Precedence

If you specify an `alias` on the [`Field`][pydantic.fields.Field], it will take precedence over the generated alias by default:

```python
from pydantic import BaseModel, ConfigDict, Field


def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


class Voice(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    name: str
    language_code: str = Field(alias='lang')


voice = Voice(Name='Filiz', lang='tr-TR')
print(voice.language_code)
#> tr-TR
print(voice.model_dump(by_alias=True))
#> {'Name': 'Filiz', 'lang': 'tr-TR'}
```

### Alias Priority

You may set `alias_priority` on a field to change this behavior:

* `alias_priority=2` the alias will *not* be overridden by the alias generator.
* `alias_priority=1` the alias *will* be overridden by the alias generator.
* `alias_priority` not set:
    * alias is set: the alias will *not* be overridden by the alias generator.
    * alias is not set: the alias *will* be overridden by the alias generator.

The same precedence applies to `validation_alias` and `serialization_alias`.
See more about the different field aliases under [field aliases](../concepts/fields.md#field-aliases).

## Alias Configuration

You can use [`ConfigDict`](./config.md) settings or runtime validation/serialization
settings to control whether or not aliases are used.

### `ConfigDict` Settings

You can use [configuration settings](./config.md) to control, at the model level,
whether or not aliases are used for validation and serialization. If you would like to control
this behavior for nested models/surpassing the config-model boundary, use [runtime settings](#runtime-settings).

#### Validation

When validating data, you can enable population of attributes by attribute name, alias, or both.
**By default**, Pydantic uses aliases for validation. Further configuration is available via:

* [`ConfigDict.validate_by_alias`][pydantic.config.ConfigDict.validate_by_alias]: `True` by default
* [`ConfigDict.validate_by_name`][pydantic.config.ConfigDict.validate_by_name]: `False` by default

=== "`validate_by_alias`"

    ```python
    from pydantic import BaseModel, ConfigDict, Field


    class Model(BaseModel):
        my_field: str = Field(validation_alias='my_alias')

        model_config = ConfigDict(validate_by_alias=True, validate_by_name=False)


    print(repr(Model(my_alias='foo')))  # (1)!
    #> Model(my_field='foo')
    ```

    1. The alias `my_alias` is used for validation.

=== "`validate_by_name`"

    ```python
    from pydantic import BaseModel, ConfigDict, Field


    class Model(BaseModel):
        my_field: str = Field(validation_alias='my_alias')

        model_config = ConfigDict(validate_by_alias=False, validate_by_name=True)


    print(repr(Model(my_field='foo')))  # (1)!
    #> Model(my_field='foo')
    ```

    1. the attribute identifier `my_field` is used for validation.

=== "`validate_by_alias` and `validate_by_name`"

    ```python
    from pydantic import BaseModel, ConfigDict, Field


    class Model(BaseModel):
        my_field: str = Field(validation_alias='my_alias')

        model_config = ConfigDict(validate_by_alias=True, validate_by_name=True)


    print(repr(Model(my_alias='foo')))  # (1)!
    #> Model(my_field='foo')

    print(repr(Model(my_field='foo')))  # (2)!
    #> Model(my_field='foo')
    ```

    1. The alias `my_alias` is used for validation.
    2. the attribute identifier `my_field` is used for validation.

!!! warning
    You cannot set both `validate_by_alias` and `validate_by_name` to `False`.
    A [user error](../errors/usage_errors.md#validate-by-alias-and-name-false) is raised in this case.

#### Serialization

When serializing data, you can enable serialization by alias, which is disabled by default.
See the [`ConfigDict.serialize_by_alias`][pydantic.config.ConfigDict.serialize_by_alias] API documentation
for more details.

```python
from pydantic import BaseModel, ConfigDict, Field


class Model(BaseModel):
    my_field: str = Field(serialization_alias='my_alias')

    model_config = ConfigDict(serialize_by_alias=True)


m = Model(my_field='foo')
print(m.model_dump())  # (1)!
#> {'my_alias': 'foo'}
```

1. The alias `my_alias` is used for serialization.

!!! note
    The fact that serialization by alias is disabled by default is notably inconsistent with the default for
    validation (where aliases are used by default). We anticipate changing this default in V3.

### Runtime Settings

You can use runtime alias flags to control alias use for validation and serialization
on a per-call basis. If you would like to control this behavior on a model level, use
[`ConfigDict` settings](#configdict-settings).

#### Validation

When validating data, you can enable population of attributes by attribute name, alias, or both.

The `by_alias` and `by_name` flags are available on the [`model_validate()`][pydantic.main.BaseModel.model_validate],
[`model_validate_json()`][pydantic.main.BaseModel.model_validate_json], and [`model_validate_strings()`][pydantic.main.BaseModel.model_validate_strings] methods, as well as the [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] validation methods.

By default:

* `by_alias` is `True`
* `by_name` is `False`

=== "`by_alias`"

    ```python
    from pydantic import BaseModel, Field


    class Model(BaseModel):
        my_field: str = Field(validation_alias='my_alias')


    m = Model.model_validate(
        {'my_alias': 'foo'},  # (1)!
        by_alias=True,
        by_name=False,
    )
    print(repr(m))
    #> Model(my_field='foo')
    ```

    1. The alias `my_alias` is used for validation.

=== "`by_name`"

    ```python
    from pydantic import BaseModel, Field


    class Model(BaseModel):
        my_field: str = Field(validation_alias='my_alias')


    m = Model.model_validate(
        {'my_field': 'foo'}, by_alias=False, by_name=True  # (1)!
    )
    print(repr(m))
    #> Model(my_field='foo')
    ```

    1. The attribute name `my_field` is used for validation.

=== "`validate_by_alias` and `validate_by_name`"

    ```python
    from pydantic import BaseModel, Field


    class Model(BaseModel):
        my_field: str = Field(validation_alias='my_alias')


    m = Model.model_validate(
        {'my_alias': 'foo'}, by_alias=True, by_name=True  # (1)!
    )
    print(repr(m))
    #> Model(my_field='foo')

    m = Model.model_validate(
        {'my_field': 'foo'}, by_alias=True, by_name=True  # (2)!
    )
    print(repr(m))
    #> Model(my_field='foo')
    ```

    1. The alias `my_alias` is used for validation.
    2. The attribute name `my_field` is used for validation.

!!! warning
    You cannot set both `by_alias` and `by_name` to `False`.
    A [user error](../errors/usage_errors.md#validate-by-alias-and-name-false) is raised in this case.

#### Serialization

When serializing data, you can enable serialization by alias via the `by_alias` flag
which is available on the [`model_dump()`][pydantic.main.BaseModel.model_dump] and
[`model_dump_json()`][pydantic.main.BaseModel.model_dump_json] methods, as well as
the [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] ones.

By default, `by_alias` is `False`.

```py
from pydantic import BaseModel, Field


class Model(BaseModel):
    my_field: str = Field(serialization_alias='my_alias')


m = Model(my_field='foo')
print(m.model_dump(by_alias=True))  # (1)!
#> {'my_alias': 'foo'}
```

1. The alias `my_alias` is used for serialization.

!!! note
    The fact that serialization by alias is disabled by default is notably inconsistent with the default for
    validation (where aliases are used by default). We anticipate changing this default in V3.
````

## File: docs/concepts/config.md
````markdown
The behaviour of Pydantic can be controlled via a variety of configuration values, documented
on the [`ConfigDict`][pydantic.ConfigDict] class. This page describes how configuration can be
specified for Pydantic's supported types.

## Configuration on Pydantic models

On Pydantic models, configuration can be specified in two ways:

* Using the [`model_config`][pydantic.BaseModel.model_config] class attribute:

    ```python
    from pydantic import BaseModel, ConfigDict, ValidationError


    class Model(BaseModel):
        model_config = ConfigDict(str_max_length=5)  # (1)!

        v: str


    try:
        m = Model(v='abcdef')
    except ValidationError as e:
        print(e)
        """
        1 validation error for Model
        v
          String should have at most 5 characters [type=string_too_long, input_value='abcdef', input_type=str]
        """
    ```

    1. A plain dictionary (i.e. `{'str_max_length': 5}`) can also be used.

    !!! note
        In Pydantic V1, the `Config` class was used. This is still supported, but **deprecated**.

* Using class arguments:

    ```python
    from pydantic import BaseModel


    class Model(BaseModel, frozen=True):
        a: str  # (1)!
    ```

    1. Unlike the [`model_config`][pydantic.BaseModel.model_config] class attribute,
       static type checkers will recognize the `frozen` argument, and so any instance
       mutation will be flagged as an type checking error.

## Configuration on Pydantic dataclasses

[Pydantic dataclasses](./dataclasses.md) also support configuration (read more in the
[dedicated section](./dataclasses.md#dataclass-config)).

```python
from pydantic import ConfigDict, ValidationError
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(str_max_length=10, validate_assignment=True))
class User:
    name: str


user = User(name='John Doe')
try:
    user.name = 'x' * 20
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    name
      String should have at most 10 characters [type=string_too_long, input_value='xxxxxxxxxxxxxxxxxxxx', input_type=str]
    """
```

## Configuration on `TypeAdapter`

[Type adapters](./type_adapter.md) (using the [`TypeAdapter`][pydantic.TypeAdapter] class) support configuration,
by providing a `config` argument.

```python
from pydantic import ConfigDict, TypeAdapter

ta = TypeAdapter(list[str], config=ConfigDict(coerce_numbers_to_str=True))

print(ta.validate_python([1, 2]))
#> ['1', '2']
```

## Configuration on other supported types

If you are using [standard library dataclasses][dataclasses] or [`TypedDict`][typing.TypedDict] classes,
the configuration can be set in two ways:

* Using the `__pydantic_config__` class attribute:

    ```python
    from dataclasses import dataclass

    from pydantic import ConfigDict


    @dataclass
    class User:
        __pydantic_config__ = ConfigDict(strict=True)

        id: int
        name: str = 'John Doe'
    ```

* Using the [`with_config`][pydantic.config.with_config] decorator (this avoids static type checking errors with
  [`TypedDict`][typing.TypedDict]):

    ```python
    from typing_extensions import TypedDict

    from pydantic import ConfigDict, with_config


    @with_config(ConfigDict(str_to_lower=True))
    class Model(TypedDict):
        x: str
    ```

## Change behaviour globally

If you wish to change the behaviour of Pydantic globally, you can create your own custom parent class
with a custom configuration, as the configuration is inherited:

```python
from pydantic import BaseModel, ConfigDict


class Parent(BaseModel):
    model_config = ConfigDict(extra='allow')


class Model(Parent):
    x: str


m = Model(x='foo', y='bar')
print(m.model_dump())
#> {'x': 'foo', 'y': 'bar'}
```

If you provide configuration to the subclasses, it will be *merged* with the parent configuration:

```python
from pydantic import BaseModel, ConfigDict


class Parent(BaseModel):
    model_config = ConfigDict(extra='allow', str_to_lower=False)


class Model(Parent):
    model_config = ConfigDict(str_to_lower=True)

    x: str


m = Model(x='FOO', y='bar')
print(m.model_dump())
#> {'x': 'foo', 'y': 'bar'}
print(Model.model_config)
#> {'extra': 'allow', 'str_to_lower': True}
```

!!! warning
    If your model inherits from multiple bases, Pydantic currently *doesn't* follow the
    [MRO]. For more details, see [this issue](https://github.com/pydantic/pydantic/issues/9992).

    [MRO]: https://docs.python.org/3/glossary.html#term-method-resolution-order

## Configuration propagation

When using types that support configuration as field annotations, configuration may not be propagated:

* For Pydantic models and dataclasses, configuration will *not* be propagated, each model has its own
  "configuration boundary":

    ```python
    from pydantic import BaseModel, ConfigDict


    class User(BaseModel):
        name: str


    class Parent(BaseModel):
        user: User

        model_config = ConfigDict(str_to_lower=True)


    print(Parent(user={'name': 'JOHN'}))
    #> user=User(name='JOHN')
    ```

* For stdlib types (dataclasses and typed dictionaries), configuration will be propagated, unless
  the type has its own configuration set:

    ```python
    from dataclasses import dataclass

    from pydantic import BaseModel, ConfigDict, with_config


    @dataclass
    class UserWithoutConfig:
        name: str


    @dataclass
    @with_config(str_to_lower=False)
    class UserWithConfig:
        name: str


    class Parent(BaseModel):
        user_1: UserWithoutConfig
        user_2: UserWithConfig

        model_config = ConfigDict(str_to_lower=True)


    print(Parent(user_1={'name': 'JOHN'}, user_2={'name': 'JOHN'}))
    #> user_1=UserWithoutConfig(name='john') user_2=UserWithConfig(name='JOHN')
    ```
````

## File: docs/concepts/conversion_table.md
````markdown
The following table provides details on how Pydantic converts data during validation in both strict and lax modes.

The "Strict" column contains checkmarks for type conversions that are allowed when validating in
[Strict Mode](strict_mode.md).

=== "All"
{{ conversion_table_all }}

=== "JSON"
{{ conversion_table_json }}

=== "JSON - Strict"
{{ conversion_table_json_strict }}

=== "Python"
{{ conversion_table_python }}

=== "Python - Strict"
{{ conversion_table_python_strict }}
````

## File: docs/concepts/dataclasses.md
````markdown
??? api "API Documentation"
    [`@pydantic.dataclasses.dataclass`][pydantic.dataclasses.dataclass]<br>

If you don't want to use Pydantic's [`BaseModel`][pydantic.BaseModel] you can instead get the same data validation
on standard [dataclasses][dataclasses].

```python
from datetime import datetime
from typing import Optional

from pydantic.dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str = 'John Doe'
    signup_ts: Optional[datetime] = None


user = User(id='42', signup_ts='2032-06-21T12:00')
print(user)
"""
User(id=42, name='John Doe', signup_ts=datetime.datetime(2032, 6, 21, 12, 0))
"""
```

!!! note
    Keep in mind that Pydantic dataclasses are **not** a replacement for [Pydantic models](../concepts/models.md).
    They provide a similar functionality to stdlib dataclasses with the addition of Pydantic validation.

    There are cases where subclassing using Pydantic models is the better choice.

    For more information and discussion see
    [pydantic/pydantic#710](https://github.com/pydantic/pydantic/issues/710).

Similarities between Pydantic dataclasses and models include support for:

* [Configuration](#dataclass-config) support
* [Nested](./models.md#nested-models) classes
* [Generics](./models.md#generic-models)

Some differences between Pydantic dataclasses and models include:

* [validators](#validators-and-initialization-hooks)
* The behavior with the [`extra`][pydantic.ConfigDict.extra] configuration value

Similarly to Pydantic models, arguments used to instantiate the dataclass are [copied](./models.md#attribute-copies).

To make use of the [various methods](./models.md#model-methods-and-properties) to validate, dump and generate a JSON Schema,
you can wrap the dataclass with a [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] and make use of its methods.

You can use both the Pydantic's [`Field()`][pydantic.Field] and the stdlib's [`field()`][dataclasses.field] functions:

```python
import dataclasses
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class User:
    id: int
    name: str = 'John Doe'
    friends: list[int] = dataclasses.field(default_factory=lambda: [0])
    age: Optional[int] = dataclasses.field(
        default=None,
        metadata={'title': 'The age of the user', 'description': 'do not lie!'},
    )
    height: Optional[int] = Field(
        default=None, title='The height in cm', ge=50, le=300
    )


user = User(id='42', height='250')
print(user)
#> User(id=42, name='John Doe', friends=[0], age=None, height=250)
```

The Pydantic [`@dataclass`][pydantic.dataclasses.dataclass] decorator accepts the same arguments as the standard decorator,
with the addition of a `config` parameter.

## Dataclass config

If you want to modify the configuration like you would with a [`BaseModel`][pydantic.BaseModel], you have two options:

* Use the `config` argument of the decorator.
* Define the configuration with the `__pydantic_config__` attribute.

```python
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


# Option 1 -- using the decorator argument:
@dataclass(config=ConfigDict(validate_assignment=True))  # (1)!
class MyDataclass1:
    a: int


# Option 2 -- using an attribute:
@dataclass
class MyDataclass2:
    a: int

    __pydantic_config__ = ConfigDict(validate_assignment=True)
```

1. You can read more about `validate_assignment` in the [API reference][pydantic.config.ConfigDict.validate_assignment].

!!! note
    While Pydantic dataclasses support the [`extra`][pydantic.config.ConfigDict.extra] configuration value, some default
    behavior of stdlib dataclasses may prevail. For example, any extra fields present on a Pydantic dataclass with
    [`extra`][pydantic.config.ConfigDict.extra] set to `'allow'` are omitted in the dataclass' string representation.
    There is also no way to provide validation [using the `__pydantic_extra__` attribute](./models.md#extra-data).

## Rebuilding dataclass schema

The [`rebuild_dataclass()`][pydantic.dataclasses.rebuild_dataclass] function can be used to rebuild the core schema of the dataclass.
See the [rebuilding model schema](./models.md#rebuilding-model-schema) section for more details.

## Stdlib dataclasses and Pydantic dataclasses

### Inherit from stdlib dataclasses

Stdlib dataclasses (nested or not) can also be inherited and Pydantic will automatically validate
all the inherited fields.

```python
import dataclasses

import pydantic


@dataclasses.dataclass
class Z:
    z: int


@dataclasses.dataclass
class Y(Z):
    y: int = 0


@pydantic.dataclasses.dataclass
class X(Y):
    x: int = 0


foo = X(x=b'1', y='2', z='3')
print(foo)
#> X(z=3, y=2, x=1)

try:
    X(z='pika')
except pydantic.ValidationError as e:
    print(e)
    """
    1 validation error for X
    z
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='pika', input_type=str]
    """
```

The decorator can also be applied directly on a stdlib dataclass, in which case a new subclass will be created:

```python
import dataclasses

import pydantic


@dataclasses.dataclass
class A:
    a: int


PydanticA = pydantic.dataclasses.dataclass(A)
print(PydanticA(a='1'))
#> A(a=1)
```

### Usage of stdlib dataclasses with `BaseModel`

When a standard library dataclass is used within a Pydantic model, a Pydantic dataclass or a [`TypeAdapter`][pydantic.TypeAdapter],
validation will be applied (and the [configuration](#dataclass-config) stays the same). This means that using a stdlib or a Pydantic
dataclass as a field annotation is functionally equivalent.

```python
import dataclasses
from typing import Optional

from pydantic import BaseModel, ConfigDict, ValidationError


@dataclasses.dataclass(frozen=True)
class User:
    name: str


class Foo(BaseModel):
    # Required so that pydantic revalidates the model attributes:
    model_config = ConfigDict(revalidate_instances='always')

    user: Optional[User] = None


# nothing is validated as expected:
user = User(name=['not', 'a', 'string'])
print(user)
#> User(name=['not', 'a', 'string'])


try:
    Foo(user=user)
except ValidationError as e:
    print(e)
    """
    1 validation error for Foo
    user.name
      Input should be a valid string [type=string_type, input_value=['not', 'a', 'string'], input_type=list]
    """

foo = Foo(user=User(name='pika'))
try:
    foo.user.name = 'bulbi'
except dataclasses.FrozenInstanceError as e:
    print(e)
    #> cannot assign to field 'name'
```

### Using custom types

As said above, validation is applied on standard library dataclasses. If you make use
of custom types, you will get an error when trying to refer to the dataclass. To circumvent
the issue, you can set the [`arbitrary_types_allowed`][pydantic.ConfigDict.arbitrary_types_allowed]
configuration value on the dataclass:

```python
import dataclasses

from pydantic import BaseModel, ConfigDict
from pydantic.errors import PydanticSchemaGenerationError


class ArbitraryType:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'ArbitraryType(value={self.value!r})'


@dataclasses.dataclass
class DC:
    a: ArbitraryType
    b: str


# valid as it is a stdlib dataclass without validation:
my_dc = DC(a=ArbitraryType(value=3), b='qwe')

try:

    class Model(BaseModel):
        dc: DC
        other: str

    # invalid as dc is now validated with pydantic, and ArbitraryType is not a known type
    Model(dc=my_dc, other='other')

except PydanticSchemaGenerationError as e:
    print(e.message)
    """
    Unable to generate pydantic-core schema for <class '__main__.ArbitraryType'>. Set `arbitrary_types_allowed=True` in the model_config to ignore this error or implement `__get_pydantic_core_schema__` on your type to fully support it.

    If you got this error by calling handler(<some type>) within `__get_pydantic_core_schema__` then you likely need to call `handler.generate_schema(<some type>)` since we do not call `__get_pydantic_core_schema__` on `<some type>` otherwise to avoid infinite recursion.
    """


# valid as we set arbitrary_types_allowed=True, and that config pushes down to the nested vanilla dataclass
class Model(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dc: DC
    other: str


m = Model(dc=my_dc, other='other')
print(repr(m))
#> Model(dc=DC(a=ArbitraryType(value=3), b='qwe'), other='other')
```

### Checking if a dataclass is a Pydantic dataclass

Pydantic dataclasses are still considered dataclasses, so using [`dataclasses.is_dataclass()`][dataclasses.is_dataclass]
will return `True`. To check if a type is specifically a Pydantic dataclass you can use the
[`is_pydantic_dataclass()`][pydantic.dataclasses.is_pydantic_dataclass] function.

```python
import dataclasses

import pydantic


@dataclasses.dataclass
class StdLibDataclass:
    id: int


PydanticDataclass = pydantic.dataclasses.dataclass(StdLibDataclass)

print(dataclasses.is_dataclass(StdLibDataclass))
#> True
print(pydantic.dataclasses.is_pydantic_dataclass(StdLibDataclass))
#> False

print(dataclasses.is_dataclass(PydanticDataclass))
#> True
print(pydantic.dataclasses.is_pydantic_dataclass(PydanticDataclass))
#> True
```

## Validators and initialization hooks

Validators also work with Pydantic dataclasses:

```python
from pydantic import field_validator
from pydantic.dataclasses import dataclass


@dataclass
class DemoDataclass:
    product_id: str  # should be a five-digit string, may have leading zeros

    @field_validator('product_id', mode='before')
    @classmethod
    def convert_int_serial(cls, v):
        if isinstance(v, int):
            v = str(v).zfill(5)
        return v


print(DemoDataclass(product_id='01234'))
#> DemoDataclass(product_id='01234')
print(DemoDataclass(product_id=2468))
#> DemoDataclass(product_id='02468')
```

<!-- markdownlint-disable-next-line strong-style -->
The dataclass [`__post_init__()`][dataclasses.__post_init__] method is also supported, and will
be called between the calls to *before* and *after* model validators.

??? example

    ```python
    from pydantic_core import ArgsKwargs
    from typing_extensions import Self

    from pydantic import model_validator
    from pydantic.dataclasses import dataclass


    @dataclass
    class Birth:
        year: int
        month: int
        day: int


    @dataclass
    class User:
        birth: Birth

        @model_validator(mode='before')
        @classmethod
        def before(cls, values: ArgsKwargs) -> ArgsKwargs:
            print(f'First: {values}')  # (1)!
            """
            First: ArgsKwargs((), {'birth': {'year': 1995, 'month': 3, 'day': 2}})
            """
            return values

        @model_validator(mode='after')
        def after(self) -> Self:
            print(f'Third: {self}')
            #> Third: User(birth=Birth(year=1995, month=3, day=2))
            return self

        def __post_init__(self):
            print(f'Second: {self.birth}')
            #> Second: Birth(year=1995, month=3, day=2)


    user = User(**{'birth': {'year': 1995, 'month': 3, 'day': 2}})
    ```

    1. Unlike Pydantic models, the `values` parameter is of type [`ArgsKwargs`][pydantic_core.ArgsKwargs]
````

## File: docs/concepts/experimental.md
````markdown
# Experimental Features

In this section you will find documentation for new, experimental features in Pydantic. These features are subject to change or removal, and we are looking for feedback and suggestions before making them a permanent part of Pydantic.

See our [Version Policy](../version-policy.md#experimental-features) for more information on experimental features.

## Feedback

We welcome feedback on experimental features! Please open an issue on the [Pydantic GitHub repository](https://github.com/pydantic/pydantic/issues/new/choose) to share your thoughts, requests, or suggestions.

We also encourage you to read through existing feedback and add your thoughts to existing issues.

## Warnings on Import

When you import an experimental feature from the `experimental` module, you'll see a warning message that the feature is experimental. You can disable this warning with the following:

```python
import warnings

from pydantic import PydanticExperimentalWarning

warnings.filterwarnings('ignore', category=PydanticExperimentalWarning)
```

## Pipeline API

Pydantic v2.8.0 introduced an experimental "pipeline" API that allows composing of parsing (validation), constraints and transformations in a more type-safe manner than existing APIs. This API is subject to change or removal, we are looking for feedback and suggestions before making it a permanent part of Pydantic.

??? api "API Documentation"
    [`pydantic.experimental.pipeline`][pydantic.experimental.pipeline]<br>

Generally, the pipeline API is used to define a sequence of steps to apply to incoming data during validation. The pipeline API is designed to be more type-safe and composable than the existing Pydantic API.

Each step in the pipeline can be:

* A validation step that runs pydantic validation on the provided type
* A transformation step that modifies the data
* A constraint step that checks the data against a condition
* A predicate step that checks the data against a condition and raises an error if it returns `False`

<!-- TODO: add more documentation once we solidify the API during the experimental phase -->

Note that the following example attempts to be exhaustive at the cost of complexity: if you find yourself writing this many transformations in type annotations you may want to consider having a `UserIn` and `UserOut` model (example below) or similar where you make the transformations via idiomatic plain Python code.
These APIs are meant for situations where the code savings are significant and the added complexity is relatively small.

```python
from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from pydantic.experimental.pipeline import validate_as


class User(BaseModel):
    name: Annotated[str, validate_as(str).str_lower()]  # (1)!
    age: Annotated[int, validate_as(int).gt(0)]  # (2)!
    username: Annotated[str, validate_as(str).str_pattern(r'[a-z]+')]  # (3)!
    password: Annotated[
        str,
        validate_as(str)
        .transform(str.lower)
        .predicate(lambda x: x != 'password'),  # (4)!
    ]
    favorite_number: Annotated[  # (5)!
        int,
        (validate_as(int) | validate_as(str).str_strip().validate_as(int)).gt(
            0
        ),
    ]
    friends: Annotated[list[User], validate_as(...).len(0, 100)]  # (6)!
    bio: Annotated[
        datetime,
        validate_as(int)
        .transform(lambda x: x / 1_000_000)
        .validate_as(...),  # (8)!
    ]
```

1. Lowercase a string.
2. Constrain an integer to be greater than zero.
3. Constrain a string to match a regex pattern.
4. You can also use the lower level transform, constrain and predicate methods.
5. Use the `|` or `&` operators to combine steps (like a logical OR or AND).
6. Calling `validate_as(...)` with `Ellipsis`, `...` as the first positional argument implies `validate_as(<field type>)`. Use `validate_as(Any)` to accept any type.
7. You can call `validate_as()` before or after other steps to do pre or post processing.

### Mapping from `BeforeValidator`, `AfterValidator` and `WrapValidator`

The `validate_as` method is a more type-safe way to define `BeforeValidator`, `AfterValidator` and `WrapValidator`:

```python
from typing import Annotated

from pydantic.experimental.pipeline import transform, validate_as

# BeforeValidator
Annotated[int, validate_as(str).str_strip().validate_as(...)]  # (1)!
# AfterValidator
Annotated[int, transform(lambda x: x * 2)]  # (2)!
# WrapValidator
Annotated[
    int,
    validate_as(str)
    .str_strip()
    .validate_as(...)
    .transform(lambda x: x * 2),  # (3)!
]
```

1. Strip whitespace from a string before parsing it as an integer.
2. Multiply an integer by 2 after parsing it.
3. Strip whitespace from a string, validate it as an integer, then multiply it by 2.

### Alternative patterns

There are many alternative patterns to use depending on the scenario.
Just as an example, consider the `UserIn` and `UserOut` pattern mentioned above:

```python
from __future__ import annotations

from pydantic import BaseModel


class UserIn(BaseModel):
    favorite_number: int | str


class UserOut(BaseModel):
    favorite_number: int


def my_api(user: UserIn) -> UserOut:
    favorite_number = user.favorite_number
    if isinstance(favorite_number, str):
        favorite_number = int(user.favorite_number.strip())

    return UserOut(favorite_number=favorite_number)


assert my_api(UserIn(favorite_number=' 1 ')).favorite_number == 1
```

This example uses plain idiomatic Python code that may be easier to understand, type-check, etc. than the examples above.
The approach you choose should really depend on your use case.
You will have to compare verbosity, performance, ease of returning meaningful errors to your users, etc. to choose the right pattern.
Just be mindful of abusing advanced patterns like the pipeline API just because you can.

## Partial Validation

Pydantic v2.10.0 introduces experimental support for "partial validation".

This allows you to validate an incomplete JSON string, or a Python object representing incomplete input data.

Partial validation is particularly helpful when processing the output of an LLM, where the model streams structured responses, and you may wish to begin validating the stream while you're still receiving data (e.g. to show partial data to users).

!!! warning
    Partial validation is an experimental feature and may change in future versions of Pydantic. The current implementation should be considered a proof of concept at this time and has a number of [limitations](#limitations-of-partial-validation).

Partial validation can be enabled when using the three validation methods on `TypeAdapter`: [`TypeAdapter.validate_json()`][pydantic.TypeAdapter.validate_json], [`TypeAdapter.validate_python()`][pydantic.TypeAdapter.validate_python], and [`TypeAdapter.validate_strings()`][pydantic.TypeAdapter.validate_strings]. This allows you to parse and validation incomplete JSON, but also to validate Python objects created by parsing incomplete data of any format.

The `experimental_allow_partial` flag can be passed to these methods to enable partial validation.
It can take the following values (and is `False`, by default):

* `False` or `'off'` - disable partial validation
* `True` or `'on'` - enable partial validation, but don't support trailing strings
* `'trailing-strings'` - enable partial validation and support trailing strings

!!! info "`'trailing-strings'` mode"
    `'trailing-strings'` mode allows for trailing incomplete strings at the end of partial JSON to be included in the output.
    For example, if you're validating against the following model:

    ```python
    from typing import TypedDict


    class Model(TypedDict):
        a: str
        b: str
    ```

    Then the following JSON input would be considered valid, despite the incomplete string at the end:

    ```json
    '{"a": "hello", "b": "wor'
    ```

    And would be validated as:

    ```python {test="skip" lint="skip"}
    {'a': 'hello', 'b': 'wor'}
    ```

`experiment_allow_partial` in action:

```python
from typing import Annotated

from annotated_types import MinLen
from typing_extensions import NotRequired, TypedDict

from pydantic import TypeAdapter


class Foobar(TypedDict):  # (1)!
    a: int
    b: NotRequired[float]
    c: NotRequired[Annotated[str, MinLen(5)]]


ta = TypeAdapter(list[Foobar])

v = ta.validate_json('[{"a": 1, "b"', experimental_allow_partial=True)  # (2)!
print(v)
#> [{'a': 1}]

v = ta.validate_json(
    '[{"a": 1, "b": 1.0, "c": "abcd', experimental_allow_partial=True  # (3)!
)
print(v)
#> [{'a': 1, 'b': 1.0}]

v = ta.validate_json(
    '[{"b": 1.0, "c": "abcde"', experimental_allow_partial=True  # (4)!
)
print(v)
#> []

v = ta.validate_json(
    '[{"a": 1, "b": 1.0, "c": "abcde"},{"a": ', experimental_allow_partial=True
)
print(v)
#> [{'a': 1, 'b': 1.0, 'c': 'abcde'}]

v = ta.validate_python([{'a': 1}], experimental_allow_partial=True)  # (5)!
print(v)
#> [{'a': 1}]

v = ta.validate_python(
    [{'a': 1, 'b': 1.0, 'c': 'abcd'}], experimental_allow_partial=True  # (6)!
)
print(v)
#> [{'a': 1, 'b': 1.0}]

v = ta.validate_json(
    '[{"a": 1, "b": 1.0, "c": "abcdefg',
    experimental_allow_partial='trailing-strings',  # (7)!
)
print(v)
#> [{'a': 1, 'b': 1.0, 'c': 'abcdefg'}]
```

1. The TypedDict `Foobar` has three field, but only `a` is required, that means that a valid instance of `Foobar` can be created even if the `b` and `c` fields are missing.
2. Parsing JSON, the input is valid JSON up to the point where the string is truncated.
3. In this case truncation of the input means the value of `c` (`abcd`) is invalid as input to `c` field, hence it's omitted.
4. The `a` field is required, so validation on the only item in the list fails and is dropped.
5. Partial validation also works with Python objects, it should have the same semantics as with JSON except of course you can't have a genuinely "incomplete" Python object.
6. The same as above but with a Python object, `c` is dropped as it's not required and failed validation.
7. The `trailing-strings` mode allows for incomplete strings at the end of partial JSON to be included in the output, in this case the input is valid JSON up to the point where the string is truncated, so the last string is included.

### How Partial Validation Works

Partial validation follows the zen of Pydantic — it makes no guarantees about what the input data might have been, but it does guarantee to return a valid instance of the type you required, or raise a validation error.

To do this, the `experimental_allow_partial` flag enables two pieces of behavior:

#### 1. Partial JSON parsing

The [jiter](https://github.com/pydantic/jiter) JSON parser used by Pydantic already supports parsing partial JSON,
`experimental_allow_partial` is simply passed to jiter via the `allow_partial` argument.

!!! note
    If you just want pure JSON parsing with support for partial JSON, you can use the [`jiter`](https://pypi.org/project/jiter/) Python library directly, or pass the `allow_partial` argument when calling [`pydantic_core.from_json`][pydantic_core.from_json].

#### 2. Ignore errors in the last element of the input {#2-ignore-errors-in-last}

Only having access to part of the input data means errors can commonly occur in the last element of the input data.

For example:

* if a string has a constraint `MinLen(5)`, when you only see part of the input, validation might fail because part of the string is missing (e.g. `{"name": "Sam` instead of `{"name": "Samuel"}`)
* if an `int` field has a constraint `Ge(10)`, when you only see part of the input, validation might fail because the number is too small (e.g. `1` instead of `10`)
* if a `TypedDict` field has 3 required fields, but the partial input only has two of the fields, validation would fail because some field are missing
* etc. etc. — there are lost more cases like this

The point is that if you only see part of some valid input data, validation errors can often occur in the last element of a sequence or last value of mapping.

To avoid these errors breaking partial validation, Pydantic will ignore ALL errors in the last element of the input data.

```python {title="Errors in last element ignored"}
from typing import Annotated

from annotated_types import MinLen

from pydantic import BaseModel, TypeAdapter


class MyModel(BaseModel):
    a: int
    b: Annotated[str, MinLen(5)]


ta = TypeAdapter(list[MyModel])
v = ta.validate_json(
    '[{"a": 1, "b": "12345"}, {"a": 1,',
    experimental_allow_partial=True,
)
print(v)
#> [MyModel(a=1, b='12345')]
```

### Limitations of Partial Validation

#### TypeAdapter only

You can only pass `experiment_allow_partial` to [`TypeAdapter`][pydantic.TypeAdapter] methods, it's not yet supported via other Pydantic entry points like [`BaseModel`][pydantic.BaseModel].

#### Types supported

Right now only a subset of collection validators know how to handle partial validation:

* `list`
* `set`
* `frozenset`
* `dict` (as in `dict[X, Y]`)
* `TypedDict` — only non-required fields may be missing, e.g. via [`NotRequired`][typing.NotRequired] or [`total=False`][typing.TypedDict.__total__])

While you can use `experimental_allow_partial` while validating against types that include other collection validators, those types will be validated "all or nothing", and partial validation will not work on more nested types.

E.g. in the [above](#2-ignore-errors-in-last) example partial validation works although the second item in the list is dropped completely since `BaseModel` doesn't (yet) support partial validation.

But partial validation won't work at all in the follow example because `BaseModel` doesn't support partial validation so it doesn't forward the `allow_partial` instruction down to the list validator in `b`:

```python
from typing import Annotated

from annotated_types import MinLen

from pydantic import BaseModel, TypeAdapter, ValidationError


class MyModel(BaseModel):
    a: int = 1
    b: list[Annotated[str, MinLen(5)]] = []  # (1)!


ta = TypeAdapter(MyModel)
try:
    v = ta.validate_json(
        '{"a": 1, "b": ["12345", "12', experimental_allow_partial=True
    )
except ValidationError as e:
    print(e)
    """
    1 validation error for MyModel
    b.1
      String should have at least 5 characters [type=string_too_short, input_value='12', input_type=str]
    """
```

1. The list validator for `b` doesn't get the `allow_partial` instruction passed down to it by the model validator so it doesn't know to ignore errors in the last element of the input.

#### Some invalid but complete JSON will be accepted

The way [jiter](https://github.com/pydantic/jiter) (the JSON parser used by Pydantic) works means it's currently not possible to differentiate between complete JSON like `{"a": 1, "b": "12"}` and incomplete JSON like `{"a": 1, "b": "12`.

This means that some invalid JSON will be accepted by Pydantic when using `experimental_allow_partial`, e.g.:

```python
from typing import Annotated

from annotated_types import MinLen
from typing_extensions import TypedDict

from pydantic import TypeAdapter


class Foobar(TypedDict, total=False):
    a: int
    b: Annotated[str, MinLen(5)]


ta = TypeAdapter(Foobar)

v = ta.validate_json(
    '{"a": 1, "b": "12', experimental_allow_partial=True  # (1)!
)
print(v)
#> {'a': 1}

v = ta.validate_json(
    '{"a": 1, "b": "12"}', experimental_allow_partial=True  # (2)!
)
print(v)
#> {'a': 1}
```

1. This will pass validation as expected although the last field will be omitted as it failed validation.
2. This will also pass validation since the binary representation of the JSON data passed to pydantic-core is indistinguishable from the previous case.

#### Any error in the last field of the input will be ignored

As described [above](#2-ignore-errors-in-last), many errors can result from truncating the input. Rather than trying to specifically ignore errors that could result from truncation, Pydantic ignores all errors in the last element of the input in partial validation mode.

This means clearly invalid data will pass validation if the error is in the last field of the input:

```python
from typing import Annotated

from annotated_types import Ge

from pydantic import TypeAdapter

ta = TypeAdapter(list[Annotated[int, Ge(10)]])
v = ta.validate_python([20, 30, 4], experimental_allow_partial=True)  # (1)!
print(v)
#> [20, 30]

ta = TypeAdapter(list[int])

v = ta.validate_python([1, 2, 'wrong'], experimental_allow_partial=True)  # (2)!
print(v)
#> [1, 2]
```

1. As you would expect, this will pass validation since Pydantic correctly ignores the error in the (truncated) last item.
2. This will also pass validation since the error in the last item is ignored.

## Validation of a callable's arguments

Pydantic provides the [`@validate_call`][pydantic.validate_call] decorator to perform validation on the provided
arguments (and additionally return type) of a callable. However, it only allows arguments to be provided
by actually calling the decorated callable. In some situations, you may want to just *validate* the arguments,
such as when loading from other data sources such as JSON data.

For this reason, the experimental [`generate_arguments_schema()`][pydantic.experimental.arguments_schema.generate_arguments_schema]
function can be used to construct a core schema, which can later be used with a [`SchemaValidator`][pydantic_core.SchemaValidator].

```python
from pydantic_core import SchemaValidator

from pydantic.experimental.arguments_schema import generate_arguments_schema


def func(p: bool, *args: str, **kwargs: int) -> None: ...


arguments_schema = generate_arguments_schema(func=func)

val = SchemaValidator(arguments_schema, config={'coerce_numbers_to_str': True})

args, kwargs = val.validate_json(
    '{"p": true, "args": ["arg1", 1], "kwargs": {"extra": 1}}'
)
print(args, kwargs)  # (1)!
#> (True, 'arg1', '1') {'extra': 1}
```

1. If you want the validated arguments as a dictionary, you can use the [`Signature.bind()`][inspect.Signature.bind]
   method:

     ```python {test="skip" lint="skip"}
     from inspect import signature

     signature(func).bind(*args, **kwargs).arguments
     #> {'p': True, 'args': ('arg1', '1'), 'kwargs': {'extra': 1}}
     ```

!!! note
    Unlike [`@validate_call`][pydantic.validate_call], this core schema will only validate the provided arguments;
    the underlying callable will *not* be called.

Additionally, you can ignore specific parameters by providing a callback, which is called for every parameter:

```python
from typing import Any

from pydantic_core import SchemaValidator

from pydantic.experimental.arguments_schema import generate_arguments_schema


def func(p: bool, *args: str, **kwargs: int) -> None: ...


def skip_first_parameter(index: int, name: str, annotation: Any) -> Any:
    if index == 0:
        return 'skip'


arguments_schema = generate_arguments_schema(
    func=func,
    parameters_callback=skip_first_parameter,
)

val = SchemaValidator(arguments_schema)

args, kwargs = val.validate_json('{"args": ["arg1"], "kwargs": {"extra": 1}}')
print(args, kwargs)
#> ('arg1',) {'extra': 1}
```

## `MISSING` sentinel

The `MISSING` sentinel is a singleton indicating a field value was not provided during validation.

This singleton can be used as a default value, as an alternative to `None` when it has an explicit
meaning. During serialization, any field with `MISSING` as a value is excluded from the output.

```python
from typing import Union

from pydantic import BaseModel
from pydantic.experimental.missing_sentinel import MISSING


class Configuration(BaseModel):
    timeout: Union[int, None, MISSING] = MISSING


# configuration defaults, stored somewhere else:
defaults = {'timeout': 200}

conf = Configuration()

# `timeout` is excluded from the serialization output:
conf.model_dump()
# {}

# The `MISSING` value doesn't appear in the JSON Schema:
Configuration.model_json_schema()['properties']['timeout']
#> {'anyOf': [{'type': 'integer'}, {'type': 'null'}], 'title': 'Timeout'}}


# `is` can be used to discrimate between the sentinel and other values:
timeout = conf.timeout if conf.timeout is not MISSING else defaults['timeout']
```

This feature is marked as experimental because it relies on the draft [PEP 661](https://peps.python.org/pep-0661/), introducing sentinels in the standard library.

As such, the following limitations currently apply:

* Static type checking of sentinels is only supported with Pyright
  [1.1.402](https://github.com/microsoft/pyright/releases/tag/1.1.402)
  or greater, and the `enableExperimentalFeatures` type evaluation setting
  should be enabled.
* Pickling of models containing `MISSING` as a value is not supported.
````

## File: docs/concepts/fields.md
````markdown
??? api "API Documentation"
    [`pydantic.fields.Field`][pydantic.fields.Field]<br>

In this section, we will go through the available mechanisms to customize Pydantic model fields:
default values, JSON Schema metadata, constraints, etc.

To do so, the [`Field()`][pydantic.fields.Field] function is used a lot, and behaves the same way as
the standard library [`field()`][dataclasses.field] function for dataclasses:

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    name: str = Field(frozen=True)
```

!!! note
    Even though `name` is assigned a value, it is still required and has no default value. If you want
    to emphasize on the fact that a value must be provided, you can use the [ellipsis][Ellipsis]:

    ```python {lint="skip" test="skip"}
    class Model(BaseModel):
        name: str = Field(..., frozen=True)
    ```

    However, its usage is discouraged as it doesn't play well with static type checkers.

## The annotated pattern

To apply constraints or attach [`Field()`][pydantic.fields.Field] functions to a model field, Pydantic
supports the [`Annotated`][typing.Annotated] typing construct to attach metadata to an annotation:

```python
from typing import Annotated

from pydantic import BaseModel, Field, WithJsonSchema


class Model(BaseModel):
    name: Annotated[str, Field(strict=True), WithJsonSchema({'extra': 'data'})]
```

As far as static type checkers are concerned, `name` is still typed as `str`, but Pydantic leverages
the available metadata to add validation logic, type constraints, etc.

Using this pattern has some advantages:

* Using the `f: <type> = Field(...)` form can be confusing and might trick users into thinking `f`
  has a default value, while in reality it is still required.
* You can provide an arbitrary amount of metadata elements for a field. As shown in the example above,
  the [`Field()`][pydantic.fields.Field] function only supports a limited set of constraints/metadata,
  and you may have to use different Pydantic utilities such as [`WithJsonSchema`][pydantic.WithJsonSchema]
  in some cases.
* Types can be made reusable (see the documentation on [custom types](./types.md#using-the-annotated-pattern)
  using this pattern).

However, note that certain arguments to the [`Field()`][pydantic.fields.Field] function (namely, `default`,
`default_factory`, and `alias`) are taken into account by static type checkers to synthesize a correct
`__init__` method. The annotated pattern is *not* understood by them, so you should use the normal
assignment form instead.

!!! tip
    The annotated pattern can also be used to add metadata to specific parts of the type. For instance,
    [validation constraints](#field-constraints) can be added this way:

    ```python
    from typing import Annotated

    from pydantic import BaseModel, Field


    class Model(BaseModel):
        int_list: list[Annotated[int, Field(gt=0)]]
        # Valid: [1, 3]
        # Invalid: [-1, 2]
    ```

    Be careful not mixing *field* and *type* metadata:

    ```python {test="skip" lint="skip"}
    class Model(BaseModel):
        field_bad: Annotated[int, Field(deprecated=True)] | None = None  # (1)!
        field_ok: Annotated[int | None, Field(deprecated=True)] = None  # (2)!
    ```

      1. The [`Field()`][pydantic.fields.Field] function is applied to `int` type, hence the
         `deprecated` flag won't have any effect. While this may be confusing given that the name of
         the [`Field()`][pydantic.fields.Field] function would imply it should apply to the field,
         the API was designed when this function was the only way to provide metadata. You can
         alternatively make use of the [`annotated_types`](https://github.com/annotated-types/annotated-types)
         library which is now supported by Pydantic.

      2. The [`Field()`][pydantic.fields.Field] function is applied to the "top-level" union type,
         hence the `deprecated` flag will be applied to the field.

## Default values

Default values for fields can be provided using the normal assignment syntax or by providing a value
to the `default` argument:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    # Both fields aren't required:
    name: str = 'John Doe'
    age: int = Field(default=20)
```

!!! warning
    [In Pydantic V1](../migration.md#required-optional-and-nullable-fields), a type annotated as [`Any`][typing.Any]
    or wrapped by [`Optional`][typing.Optional] would be given an implicit default of `None` even if no
    default was explicitly specified. This is no longer the case in Pydantic V2.

You can also pass a callable to the `default_factory` argument that will be called to generate a default value:

```python
from uuid import uuid4

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
```

The default factory can also take a single required argument, in which case the already validated data will be passed as a dictionary.

```python
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    email: EmailStr
    username: str = Field(default_factory=lambda data: data['email'])


user = User(email='user@example.com')
print(user.username)
#> user@example.com
```

The `data` argument will *only* contain the already validated data, based on the [order of model fields](./models.md#field-ordering)
(the above example would fail if `username` were to be defined before `email`).

## Validate default values

By default, Pydantic will *not* validate default values. The `validate_default` field parameter
(or the [`validate_default`][pydantic.ConfigDict.validate_default] configuration value) can be used
to enable this behavior:

```python
from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    age: int = Field(default='twelve', validate_default=True)


try:
    user = User()
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    age
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='twelve', input_type=str]
    """
```

### Mutable default values

A common source of bugs in Python is to use a mutable object as a default value for a function or method argument,
as the same instance ends up being reused in each call.

The [`dataclasses`][dataclasses] module actually raises an error in this case, indicating that you should use
a [default factory](https://docs.python.org/3/library/dataclasses.html#default-factory-functions) instead.

While the same thing can be done in Pydantic, it is not required. In the event that the default value is not hashable,
Pydantic will create a deep copy of the default value when creating each instance of the model:

```python
from pydantic import BaseModel


class Model(BaseModel):
    item_counts: list[dict[str, int]] = [{}]


m1 = Model()
m1.item_counts[0]['a'] = 1
print(m1.item_counts)
#> [{'a': 1}]

m2 = Model()
print(m2.item_counts)
#> [{}]
```

## Field aliases

!!! tip
    Read more about aliases in the [dedicated section](./alias.md).

For validation and serialization, you can define an alias for a field.

There are three ways to define an alias:

* `Field(alias='foo')`
* `Field(validation_alias='foo')`
* `Field(serialization_alias='foo')`

The `alias` parameter is used for both validation *and* serialization. If you want to use
*different* aliases for validation and serialization respectively, you can use the `validation_alias`
and `serialization_alias` parameters, which will apply only in their respective use cases.

Here is an example of using the `alias` parameter:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(alias='username')


user = User(username='johndoe')  # (1)!
print(user)
#> name='johndoe'
print(user.model_dump(by_alias=True))  # (2)!
#> {'username': 'johndoe'}
```

1. The alias `'username'` is used for instance creation and validation.
2. We are using [`model_dump()`][pydantic.main.BaseModel.model_dump] to convert the model into a serializable format.

    Note that the `by_alias` keyword argument defaults to `False`, and must be specified explicitly to dump
    models using the field (serialization) aliases.

    You can also use [`ConfigDict.serialize_by_alias`][pydantic.config.ConfigDict.serialize_by_alias] to
    configure this behavior at the model level.

    When `by_alias=True`, the alias `'username'` used during serialization.

If you want to use an alias *only* for validation, you can use the `validation_alias` parameter:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(validation_alias='username')


user = User(username='johndoe')  # (1)!
print(user)
#> name='johndoe'
print(user.model_dump(by_alias=True))  # (2)!
#> {'name': 'johndoe'}
```

1. The validation alias `'username'` is used during validation.
2. The field name `'name'` is used during serialization.

If you only want to define an alias for *serialization*, you can use the `serialization_alias` parameter:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(serialization_alias='username')


user = User(name='johndoe')  # (1)!
print(user)
#> name='johndoe'
print(user.model_dump(by_alias=True))  # (2)!
#> {'username': 'johndoe'}
```

1. The field name `'name'` is used for validation.
2. The serialization alias `'username'` is used for serialization.

!!! note "Alias precedence and priority"
    In case you use `alias` together with `validation_alias` or `serialization_alias` at the same time,
    the `validation_alias` will have priority over `alias` for validation, and `serialization_alias` will have priority
    over `alias` for serialization.

    If you provide a value for the [`alias_generator`][pydantic.config.ConfigDict.alias_generator] model setting, you can control the order of precedence for field alias and generated aliases via the `alias_priority` field parameter. You can read more about alias precedence [here](../concepts/alias.md#alias-precedence).

??? tip "Static type checking/IDE support"
    If you provide a value for the `alias` field parameter, static type checkers will use this alias instead
    of the actual field name to synthesize the `__init__` method:

    ```python
    from pydantic import BaseModel, Field


    class User(BaseModel):
        name: str = Field(alias='username')


    user = User(username='johndoe')  # (1)!
    ```

    1. Accepted by type checkers.

    This means that when using the [`validate_by_name`][pydantic.config.ConfigDict.validate_by_name] model setting (which allows both the field name and alias to be used during model validation), type checkers will error when the actual field name is used:

    ```python
    from pydantic import BaseModel, ConfigDict, Field


    class User(BaseModel):
        model_config = ConfigDict(validate_by_name=True)

        name: str = Field(alias='username')


    user = User(name='johndoe')  # (1)!
    ```

    1. *Not* accepted by type checkers.

    If you still want type checkers to use the field name and not the alias, the [annotated pattern](#the-annotated-pattern)
    can be used (which is only understood by Pydantic):

    ```python
    from typing import Annotated

    from pydantic import BaseModel, ConfigDict, Field


    class User(BaseModel):
        model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

        name: Annotated[str, Field(alias='username')]


    user = User(name='johndoe')  # (1)!
    user = User(username='johndoe')  # (2)!
    ```

    1. Accepted by type checkers.
    2. *Not* accepted by type checkers.

    <h3>Validation Alias</h3>

    Even though Pydantic treats `alias` and `validation_alias` the same when creating model instances, type checkers
    only understand the `alias` field parameter. As a workaround, you can instead specify both an `alias` and
    `serialization_alias` (identical to the field name), as the `serialization_alias` will override the `alias` during
    serialization:

    ```python
    from pydantic import BaseModel, Field


    class MyModel(BaseModel):
        my_field: int = Field(validation_alias='myValidationAlias')
    ```

    with:

    ```python
    from pydantic import BaseModel, Field


    class MyModel(BaseModel):
        my_field: int = Field(
            alias='myValidationAlias',
            serialization_alias='my_field',
        )


    m = MyModel(myValidationAlias=1)
    print(m.model_dump(by_alias=True))
    #> {'my_field': 1}
    ```

<!-- markdownlint-disable-next-line no-empty-links -->
[](){#field-constraints}

## Numeric Constraints

There are some keyword arguments that can be used to constrain numeric values:

* `gt` - greater than
* `lt` - less than
* `ge` - greater than or equal to
* `le` - less than or equal to
* `multiple_of` - a multiple of the given number
* `allow_inf_nan` - allow `'inf'`, `'-inf'`, `'nan'` values

Here's an example:

```python
from pydantic import BaseModel, Field


class Foo(BaseModel):
    positive: int = Field(gt=0)
    non_negative: int = Field(ge=0)
    negative: int = Field(lt=0)
    non_positive: int = Field(le=0)
    even: int = Field(multiple_of=2)
    love_for_pydantic: float = Field(allow_inf_nan=True)


foo = Foo(
    positive=1,
    non_negative=0,
    negative=-1,
    non_positive=0,
    even=2,
    love_for_pydantic=float('inf'),
)
print(foo)
"""
positive=1 non_negative=0 negative=-1 non_positive=0 even=2 love_for_pydantic=inf
"""
```

??? info "JSON Schema"
    In the generated JSON schema:

    * `gt` and `lt` constraints will be translated to `exclusiveMinimum` and `exclusiveMaximum`.
    * `ge` and `le` constraints will be translated to `minimum` and `maximum`.
    * `multiple_of` constraint will be translated to `multipleOf`.

    The above snippet will generate the following JSON Schema:

    ```json
    {
      "title": "Foo",
      "type": "object",
      "properties": {
        "positive": {
          "title": "Positive",
          "type": "integer",
          "exclusiveMinimum": 0
        },
        "non_negative": {
          "title": "Non Negative",
          "type": "integer",
          "minimum": 0
        },
        "negative": {
          "title": "Negative",
          "type": "integer",
          "exclusiveMaximum": 0
        },
        "non_positive": {
          "title": "Non Positive",
          "type": "integer",
          "maximum": 0
        },
        "even": {
          "title": "Even",
          "type": "integer",
          "multipleOf": 2
        },
        "love_for_pydantic": {
          "title": "Love For Pydantic",
          "type": "number"
        }
      },
      "required": [
        "positive",
        "non_negative",
        "negative",
        "non_positive",
        "even",
        "love_for_pydantic"
      ]
    }
    ```

    See the [JSON Schema Draft 2020-12] for more details.

!!! warning "Constraints on compound types"
    In case you use field constraints with compound types, an error can happen in some cases. To avoid potential issues,
    you can use `Annotated`:

    ```python
    from typing import Annotated, Optional

    from pydantic import BaseModel, Field


    class Foo(BaseModel):
        positive: Optional[Annotated[int, Field(gt=0)]]
        # Can error in some cases, not recommended:
        non_negative: Optional[int] = Field(ge=0)
    ```

## String Constraints

??? api "API Documentation"
    [`pydantic.types.StringConstraints`][pydantic.types.StringConstraints]<br>

There are fields that can be used to constrain strings:

* `min_length`: Minimum length of the string.
* `max_length`: Maximum length of the string.
* `pattern`: A regular expression that the string must match.

Here's an example:

```python
from pydantic import BaseModel, Field


class Foo(BaseModel):
    short: str = Field(min_length=3)
    long: str = Field(max_length=10)
    regex: str = Field(pattern=r'^\d*$')  # (1)!


foo = Foo(short='foo', long='foobarbaz', regex='123')
print(foo)
#> short='foo' long='foobarbaz' regex='123'
```

1. Only digits are allowed.

??? info "JSON Schema"
    In the generated JSON schema:

    * `min_length` constraint will be translated to `minLength`.
    * `max_length` constraint will be translated to `maxLength`.
    * `pattern` constraint will be translated to `pattern`.

    The above snippet will generate the following JSON Schema:

    ```json
    {
      "title": "Foo",
      "type": "object",
      "properties": {
        "short": {
          "title": "Short",
          "type": "string",
          "minLength": 3
        },
        "long": {
          "title": "Long",
          "type": "string",
          "maxLength": 10
        },
        "regex": {
          "title": "Regex",
          "type": "string",
          "pattern": "^\\d*$"
        }
      },
      "required": [
        "short",
        "long",
        "regex"
      ]
    }
    ```

## Decimal Constraints

There are fields that can be used to constrain decimals:

* `max_digits`: Maximum number of digits within the `Decimal`. It does not include a zero before the decimal point or
  trailing decimal zeroes.
* `decimal_places`: Maximum number of decimal places allowed. It does not include trailing decimal zeroes.

Here's an example:

```python
from decimal import Decimal

from pydantic import BaseModel, Field


class Foo(BaseModel):
    precise: Decimal = Field(max_digits=5, decimal_places=2)


foo = Foo(precise=Decimal('123.45'))
print(foo)
#> precise=Decimal('123.45')
```

## Dataclass Constraints

There are fields that can be used to constrain dataclasses:

* `init`: Whether the field should be included in the `__init__` of the dataclass.
* `init_var`: Whether the field should be seen as an [init-only field] in the dataclass.
* `kw_only`: Whether the field should be a keyword-only argument in the constructor of the dataclass.

Here's an example:

```python
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass


@dataclass
class Foo:
    bar: str
    baz: str = Field(init_var=True)
    qux: str = Field(kw_only=True)


class Model(BaseModel):
    foo: Foo


model = Model(foo=Foo('bar', baz='baz', qux='qux'))
print(model.model_dump())  # (1)!
#> {'foo': {'bar': 'bar', 'qux': 'qux'}}
```

1. The `baz` field is not included in the `model_dump()` output, since it is an init-only field.

## Field Representation

The parameter `repr` can be used to control whether the field should be included in the string
representation of the model.

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(repr=True)  # (1)!
    age: int = Field(repr=False)


user = User(name='John', age=42)
print(user)
#> name='John'
```

1. This is the default value.

## Discriminator

The parameter `discriminator` can be used to control the field that will be used to discriminate between different
models in a union. It takes either the name of a field or a `Discriminator` instance. The `Discriminator`
approach can be useful when the discriminator fields aren't the same for all the models in the `Union`.

The following example shows how to use `discriminator` with a field name:

```python
from typing import Literal, Union

from pydantic import BaseModel, Field


class Cat(BaseModel):
    pet_type: Literal['cat']
    age: int


class Dog(BaseModel):
    pet_type: Literal['dog']
    age: int


class Model(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator='pet_type')


print(Model.model_validate({'pet': {'pet_type': 'cat', 'age': 12}}))  # (1)!
#> pet=Cat(pet_type='cat', age=12)
```

1. See more about [Validating data] in the [Models] page.

The following example shows how to use the `discriminator` keyword argument with a `Discriminator` instance:

```python
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Discriminator, Field, Tag


class Cat(BaseModel):
    pet_type: Literal['cat']
    age: int


class Dog(BaseModel):
    pet_kind: Literal['dog']
    age: int


def pet_discriminator(v):
    if isinstance(v, dict):
        return v.get('pet_type', v.get('pet_kind'))
    return getattr(v, 'pet_type', getattr(v, 'pet_kind', None))


class Model(BaseModel):
    pet: Union[Annotated[Cat, Tag('cat')], Annotated[Dog, Tag('dog')]] = Field(
        discriminator=Discriminator(pet_discriminator)
    )


print(repr(Model.model_validate({'pet': {'pet_type': 'cat', 'age': 12}})))
#> Model(pet=Cat(pet_type='cat', age=12))

print(repr(Model.model_validate({'pet': {'pet_kind': 'dog', 'age': 12}})))
#> Model(pet=Dog(pet_kind='dog', age=12))
```

You can also take advantage of `Annotated` to define your discriminated unions.
See the [Discriminated Unions] docs for more details.

## Strict Mode

The `strict` parameter on a [`Field`][pydantic.fields.Field] specifies whether the field should be validated in "strict mode".
In strict mode, Pydantic throws an error during validation instead of coercing data on the field where `strict=True`.

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str = Field(strict=True)
    age: int = Field(strict=False)  # (1)!


user = User(name='John', age='42')  # (2)!
print(user)
#> name='John' age=42
```

1. This is the default value.
2. The `age` field is not validated in the strict mode. Therefore, it can be assigned a string.

See [Strict Mode](strict_mode.md) for more details.

See [Conversion Table](conversion_table.md) for more details on how Pydantic converts data in both strict and lax modes.

## Immutability

The parameter `frozen` is used to emulate the frozen dataclass behaviour. It is used to prevent the field from being
assigned a new value after the model is created (immutability).

See the [frozen dataclass documentation] for more details.

```python
from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    name: str = Field(frozen=True)
    age: int


user = User(name='John', age=42)

try:
    user.name = 'Jane'  # (1)!
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    name
      Field is frozen [type=frozen_field, input_value='Jane', input_type=str]
    """
```

1. Since `name` field is frozen, the assignment is not allowed.

## Exclude

The `exclude` parameter can be used to control which fields should be excluded from the
model when exporting the model.

See the following example:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    name: str
    age: int = Field(exclude=True)


user = User(name='John', age=42)
print(user.model_dump())  # (1)!
#> {'name': 'John'}
```

1. The `age` field is not included in the `model_dump()` output, since it is excluded.

See the [Serialization] section for more details.

## Deprecated fields

The `deprecated` parameter can be used to mark a field as being deprecated. Doing so will result in:

* a runtime deprecation warning emitted when accessing the field.
* The [deprecated](https://json-schema.org/draft/2020-12/json-schema-validation#section-9.3) keyword
  being set in the generated JSON schema.

This parameter accepts different types, described below.

### `deprecated` as a string

The value will be used as the deprecation message.

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Model(BaseModel):
    deprecated_field: Annotated[int, Field(deprecated='This is deprecated')]


print(Model.model_json_schema()['properties']['deprecated_field'])
#> {'deprecated': True, 'title': 'Deprecated Field', 'type': 'integer'}
```

### `deprecated` via the `@warnings.deprecated` decorator

The [`@warnings.deprecated`][warnings.deprecated] decorator (or the
[`typing_extensions` backport][typing_extensions.deprecated] on Python
3.12 and lower) can be used as an instance.

<!-- TODO: tabs should be auto-generated if using Ruff (https://github.com/pydantic/pydantic/issues/10083) -->

=== "Python 3.9 and above"

    ```python
    from typing import Annotated

    from typing_extensions import deprecated

    from pydantic import BaseModel, Field


    class Model(BaseModel):
        deprecated_field: Annotated[int, deprecated('This is deprecated')]

        # Or explicitly using `Field`:
        alt_form: Annotated[int, Field(deprecated=deprecated('This is deprecated'))]
    ```

=== "Python 3.13 and above"

    ```python {requires="3.13"}
    from typing import Annotated
    from warnings import deprecated

    from pydantic import BaseModel, Field


    class Model(BaseModel):
        deprecated_field: Annotated[int, deprecated('This is deprecated')]

        # Or explicitly using `Field`:
        alt_form: Annotated[int, Field(deprecated=deprecated('This is deprecated'))]
    ```

!!! note "Support for `category` and `stacklevel`"
    The current implementation of this feature does not take into account the `category` and `stacklevel`
    arguments to the `deprecated` decorator. This might land in a future version of Pydantic.

### `deprecated` as a boolean

```python
from typing import Annotated

from pydantic import BaseModel, Field


class Model(BaseModel):
    deprecated_field: Annotated[int, Field(deprecated=True)]


print(Model.model_json_schema()['properties']['deprecated_field'])
#> {'deprecated': True, 'title': 'Deprecated Field', 'type': 'integer'}
```

!!! warning "Accessing a deprecated field in validators"
    When accessing a deprecated field inside a validator, the deprecation warning will be emitted. You can use
    [`catch_warnings`][warnings.catch_warnings] to explicitly ignore it:

    ```python
    import warnings

    from typing_extensions import Self

    from pydantic import BaseModel, Field, model_validator


    class Model(BaseModel):
        deprecated_field: int = Field(deprecated='This is deprecated')

        @model_validator(mode='after')
        def validate_model(self) -> Self:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', DeprecationWarning)
                self.deprecated_field = self.deprecated_field * 2
    ```

## Customizing JSON Schema

Some field parameters are used exclusively to customize the generated JSON schema. The parameters in question are:

* `title`
* `description`
* `examples`
* `json_schema_extra`

Read more about JSON schema customization / modification with fields in the [Customizing JSON Schema] section of the JSON schema docs.

## The `computed_field` decorator

??? api "API Documentation"
    [`computed_field`][pydantic.fields.computed_field]<br>

The [`computed_field`][pydantic.fields.computed_field] decorator can be used to include [`property`][] or
[`cached_property`][functools.cached_property] attributes when serializing a model or dataclass.
The property will also be taken into account in the JSON Schema (in serialization mode).

!!! note
    Properties can be useful for fields that are computed from other fields, or for fields that
    are expensive to be computed (and thus, are cached if using [`cached_property`][functools.cached_property]).

    However, note that Pydantic will *not* perform any additional logic on the wrapped property
    (validation, cache invalidation, etc.).

Here's an example of the JSON schema (in serialization mode) generated for a model with a computed field:

```python
from pydantic import BaseModel, computed_field


class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property  # (1)!
    def volume(self) -> float:
        return self.width * self.height * self.depth


print(Box.model_json_schema(mode='serialization'))
"""
{
    'properties': {
        'width': {'title': 'Width', 'type': 'number'},
        'height': {'title': 'Height', 'type': 'number'},
        'depth': {'title': 'Depth', 'type': 'number'},
        'volume': {'readOnly': True, 'title': 'Volume', 'type': 'number'},
    },
    'required': ['width', 'height', 'depth', 'volume'],
    'title': 'Box',
    'type': 'object',
}
"""
```

1. If not specified, [`computed_field`][pydantic.fields.computed_field] will implicitly convert the method
   to a [`property`][]. However, it is preferable to explicitly use the [`@property`][property] decorator
   for type checking purposes.

Here's an example using the `model_dump` method with a computed field:

```python
from pydantic import BaseModel, computed_field


class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property
    def volume(self) -> float:
        return self.width * self.height * self.depth


b = Box(width=1, height=2, depth=3)
print(b.model_dump())
#> {'width': 1.0, 'height': 2.0, 'depth': 3.0, 'volume': 6.0}
```

As with regular fields, computed fields can be marked as being deprecated:

```python
from typing_extensions import deprecated

from pydantic import BaseModel, computed_field


class Box(BaseModel):
    width: float
    height: float
    depth: float

    @computed_field
    @property
    @deprecated("'volume' is deprecated")
    def volume(self) -> float:
        return self.width * self.height * self.depth
```

[Discriminated Unions]: ../concepts/unions.md#discriminated-unions
[Validating data]: models.md#validating-data
[Models]: models.md
[init-only field]: https://docs.python.org/3/library/dataclasses.html#init-only-variables
[frozen dataclass documentation]: https://docs.python.org/3/library/dataclasses.html#frozen-instances
[Customizing JSON Schema]: json_schema.md#field-level-customization
````

## File: docs/concepts/forward_annotations.md
````markdown
Forward annotations (wrapped in quotes) or using the `from __future__ import annotations` [future statement]
(as introduced in [PEP563](https://www.python.org/dev/peps/pep-0563/)) are supported:

```python
from __future__ import annotations

from pydantic import BaseModel

MyInt = int


class Model(BaseModel):
    a: MyInt
    # Without the future import, equivalent to:
    # a: 'MyInt'


print(Model(a='1'))
#> a=1
```

As shown in the following sections, forward annotations are useful when you want to reference
a type that is not yet defined in your code.

The internal logic to resolve forward annotations is described in detail in [this section](../internals/resolving_annotations.md).

## Self-referencing (or "Recursive") Models

Models with self-referencing fields are also supported. These annotations will be resolved during model creation.

Within the model, you can either add the `from __future__ import annotations` import or wrap the annotation
in a string:

```python
from typing import Optional

from pydantic import BaseModel


class Foo(BaseModel):
    a: int = 123
    sibling: 'Optional[Foo]' = None


print(Foo())
#> a=123 sibling=None
print(Foo(sibling={'a': '321'}))
#> a=123 sibling=Foo(a=321, sibling=None)
```

### Cyclic references

When working with self-referencing recursive models, it is possible that you might encounter cyclic references
in validation inputs. For example, this can happen when validating ORM instances with back-references from
attributes.

Rather than raising a [`RecursionError`][] while attempting to validate data with cyclic references, Pydantic is able
to detect the cyclic reference and raise an appropriate [`ValidationError`][pydantic_core.ValidationError]:

```python
from typing import Optional

from pydantic import BaseModel, ValidationError


class ModelA(BaseModel):
    b: 'Optional[ModelB]' = None


class ModelB(BaseModel):
    a: Optional[ModelA] = None


cyclic_data = {}
cyclic_data['a'] = {'b': cyclic_data}
print(cyclic_data)
#> {'a': {'b': {...}}}

try:
    ModelB.model_validate(cyclic_data)
except ValidationError as exc:
    print(exc)
    """
    1 validation error for ModelB
    a.b
      Recursion error - cyclic reference detected [type=recursion_loop, input_value={'a': {'b': {...}}}, input_type=dict]
    """
```

Because this error is raised without actually exceeding the maximum recursion depth, you can catch and
handle the raised [`ValidationError`][pydantic_core.ValidationError] without needing to worry about the limited
remaining recursion depth:

```python
from contextlib import contextmanager
from dataclasses import field
from typing import Iterator

from pydantic import BaseModel, ValidationError, field_validator


def is_recursion_validation_error(exc: ValidationError) -> bool:
    errors = exc.errors()
    return len(errors) == 1 and errors[0]['type'] == 'recursion_loop'


@contextmanager
def suppress_recursion_validation_error() -> Iterator[None]:
    try:
        yield
    except ValidationError as exc:
        if not is_recursion_validation_error(exc):
            raise exc


class Node(BaseModel):
    id: int
    children: list['Node'] = field(default_factory=list)

    @field_validator('children', mode='wrap')
    @classmethod
    def drop_cyclic_references(cls, children, h):
        try:
            return h(children)
        except ValidationError as exc:
            if not (
                is_recursion_validation_error(exc)
                and isinstance(children, list)
            ):
                raise exc

            value_without_cyclic_refs = []
            for child in children:
                with suppress_recursion_validation_error():
                    value_without_cyclic_refs.extend(h([child]))
            return h(value_without_cyclic_refs)


# Create data with cyclic references representing the graph 1 -> 2 -> 3 -> 1
node_data = {'id': 1, 'children': [{'id': 2, 'children': [{'id': 3}]}]}
node_data['children'][0]['children'][0]['children'] = [node_data]

print(Node.model_validate(node_data))
#> id=1 children=[Node(id=2, children=[Node(id=3, children=[])])]
```

Similarly, if Pydantic encounters a recursive reference during *serialization*, rather than waiting
for the maximum recursion depth to be exceeded, a [`ValueError`][] is raised immediately:

```python
from pydantic import TypeAdapter

# Create data with cyclic references representing the graph 1 -> 2 -> 3 -> 1
node_data = {'id': 1, 'children': [{'id': 2, 'children': [{'id': 3}]}]}
node_data['children'][0]['children'][0]['children'] = [node_data]

try:
    # Try serializing the circular reference as JSON
    TypeAdapter(dict).dump_json(node_data)
except ValueError as exc:
    print(exc)
    """
    Error serializing to JSON: ValueError: Circular reference detected (id repeated)
    """
```

This can also be handled if desired:

```python
from dataclasses import field
from typing import Any

from pydantic import (
    SerializerFunctionWrapHandler,
    TypeAdapter,
    field_serializer,
)
from pydantic.dataclasses import dataclass


@dataclass
class NodeReference:
    id: int


@dataclass
class Node(NodeReference):
    children: list['Node'] = field(default_factory=list)

    @field_serializer('children', mode='wrap')
    def serialize(
        self, children: list['Node'], handler: SerializerFunctionWrapHandler
    ) -> Any:
        """
        Serialize a list of nodes, handling circular references by excluding the children.
        """
        try:
            return handler(children)
        except ValueError as exc:
            if not str(exc).startswith('Circular reference'):
                raise exc

            result = []
            for node in children:
                try:
                    serialized = handler([node])
                except ValueError as exc:
                    if not str(exc).startswith('Circular reference'):
                        raise exc
                    result.append({'id': node.id})
                else:
                    result.append(serialized)
            return result


# Create a cyclic graph:
nodes = [Node(id=1), Node(id=2), Node(id=3)]
nodes[0].children.append(nodes[1])
nodes[1].children.append(nodes[2])
nodes[2].children.append(nodes[0])

print(nodes[0])
#> Node(id=1, children=[Node(id=2, children=[Node(id=3, children=[...])])])

# Serialize the cyclic graph:
print(TypeAdapter(Node).dump_python(nodes[0]))
"""
{
    'id': 1,
    'children': [{'id': 2, 'children': [{'id': 3, 'children': [{'id': 1}]}]}],
}
"""
```

[future statement]: https://docs.python.org/3/reference/simple_stmts.html#future
````

## File: docs/concepts/json_schema.md
````markdown
??? api "API Documentation"
    [`pydantic.json_schema`][pydantic.json_schema]<br>

Pydantic allows automatic creation and customization of JSON schemas from models.
The generated JSON schemas are compliant with the following specifications:

* [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/release-notes.html)
* [OpenAPI Specification v3.1.0](https://github.com/OAI/OpenAPI-Specification).

## Generating JSON Schema

Use the following functions to generate JSON schema:

* [`BaseModel.model_json_schema`][pydantic.main.BaseModel.model_json_schema] returns a jsonable dict of a model's schema.
* [`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] returns a jsonable dict of an adapted type's schema.

!!! note
    These methods are not to be confused with [`BaseModel.model_dump_json`][pydantic.main.BaseModel.model_dump_json]
    and [`TypeAdapter.dump_json`][pydantic.type_adapter.TypeAdapter.dump_json], which serialize instances of the
    model or adapted type, respectively. These methods return JSON strings. In comparison,
    [`BaseModel.model_json_schema`][pydantic.main.BaseModel.model_json_schema] and
    [`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] return a jsonable dict
    representing the JSON schema of the model or adapted type, respectively.

!!! note "on the "jsonable" nature of JSON schema"
    Regarding the "jsonable" nature of the [`model_json_schema`][pydantic.main.BaseModel.model_json_schema] results,
    calling `json.dumps(m.model_json_schema())`on some `BaseModel` `m` returns a valid JSON string. Similarly, for
    [`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema], calling
    `json.dumps(TypeAdapter(<some_type>).json_schema())` returns a valid JSON string.

!!! tip
    Pydantic offers support for both of:

    1. [Customizing JSON Schema](#customizing-json-schema)
    2. [Customizing the JSON Schema Generation Process](#customizing-the-json-schema-generation-process)

    The first approach generally has a more narrow scope, allowing for customization of the JSON schema for
    more specific cases and types. The second approach generally has a more broad scope, allowing for customization
    of the JSON schema generation process overall. The same effects can be achieved with either approach, but
    depending on your use case, one approach might offer a more simple solution than the other.

Here's an example of generating JSON schema from a `BaseModel`:

```python {output="json"}
import json
from enum import Enum
from typing import Annotated, Union

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class FooBar(BaseModel):
    count: int
    size: Union[float, None] = None


class Gender(str, Enum):
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'


class MainModel(BaseModel):
    """
    This is the description of the main model
    """

    model_config = ConfigDict(title='Main')

    foo_bar: FooBar
    gender: Annotated[Union[Gender, None], Field(alias='Gender')] = None
    snap: int = Field(
        default=42,
        title='The Snap',
        description='this is the value of snap',
        gt=30,
        lt=50,
    )


main_model_schema = MainModel.model_json_schema()  # (1)!
print(json.dumps(main_model_schema, indent=2))  # (2)!
"""
{
  "$defs": {
    "FooBar": {
      "properties": {
        "count": {
          "title": "Count",
          "type": "integer"
        },
        "size": {
          "anyOf": [
            {
              "type": "number"
            },
            {
              "type": "null"
            }
          ],
          "default": null,
          "title": "Size"
        }
      },
      "required": [
        "count"
      ],
      "title": "FooBar",
      "type": "object"
    },
    "Gender": {
      "enum": [
        "male",
        "female",
        "other",
        "not_given"
      ],
      "title": "Gender",
      "type": "string"
    }
  },
  "description": "This is the description of the main model",
  "properties": {
    "foo_bar": {
      "$ref": "#/$defs/FooBar"
    },
    "Gender": {
      "anyOf": [
        {
          "$ref": "#/$defs/Gender"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "snap": {
      "default": 42,
      "description": "this is the value of snap",
      "exclusiveMaximum": 50,
      "exclusiveMinimum": 30,
      "title": "The Snap",
      "type": "integer"
    }
  },
  "required": [
    "foo_bar"
  ],
  "title": "Main",
  "type": "object"
}
"""
```

1. This produces a "jsonable" dict of `MainModel`'s schema.
2. Calling `json.dumps` on the schema dict produces a JSON string.

The [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] class lets you create an object with methods for validating, serializing,
and producing JSON schemas for arbitrary types. This serves as a complete replacement for `schema_of` in
Pydantic V1 (which is now deprecated).

Here's an example of generating JSON schema from a [`TypeAdapter`][pydantic.type_adapter.TypeAdapter]:

```python
from pydantic import TypeAdapter

adapter = TypeAdapter(list[int])
print(adapter.json_schema())
#> {'items': {'type': 'integer'}, 'type': 'array'}
```

You can also generate JSON schemas for combinations of [`BaseModel`s][pydantic.main.BaseModel]
and [`TypeAdapter`s][pydantic.type_adapter.TypeAdapter], as shown in this example:

```python {output="json"}
import json
from typing import Union

from pydantic import BaseModel, TypeAdapter


class Cat(BaseModel):
    name: str
    color: str


class Dog(BaseModel):
    name: str
    breed: str


ta = TypeAdapter(Union[Cat, Dog])
ta_schema = ta.json_schema()
print(json.dumps(ta_schema, indent=2))
"""
{
  "$defs": {
    "Cat": {
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "color": {
          "title": "Color",
          "type": "string"
        }
      },
      "required": [
        "name",
        "color"
      ],
      "title": "Cat",
      "type": "object"
    },
    "Dog": {
      "properties": {
        "name": {
          "title": "Name",
          "type": "string"
        },
        "breed": {
          "title": "Breed",
          "type": "string"
        }
      },
      "required": [
        "name",
        "breed"
      ],
      "title": "Dog",
      "type": "object"
    }
  },
  "anyOf": [
    {
      "$ref": "#/$defs/Cat"
    },
    {
      "$ref": "#/$defs/Dog"
    }
  ]
}
"""
```

### Configuring the `JsonSchemaMode`

Specify the mode of JSON schema generation via the `mode` parameter in the
[`model_json_schema`][pydantic.main.BaseModel.model_json_schema] and
[`TypeAdapter.json_schema`][pydantic.type_adapter.TypeAdapter.json_schema] methods. By default, the mode is set to
`'validation'`, which produces a JSON schema corresponding to the model's validation schema.

The [`JsonSchemaMode`][pydantic.json_schema.JsonSchemaMode] is a type alias that represents the available options for the `mode` parameter:

* `'validation'`
* `'serialization'`

Here's an example of how to specify the `mode` parameter, and how it affects the generated JSON schema:

```python
from decimal import Decimal

from pydantic import BaseModel


class Model(BaseModel):
    a: Decimal = Decimal('12.34')


print(Model.model_json_schema(mode='validation'))
"""
{
    'properties': {
        'a': {
            'anyOf': [
                {'type': 'number'},
                {
                    'pattern': '^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d*$',
                    'type': 'string',
                },
            ],
            'default': '12.34',
            'title': 'A',
        }
    },
    'title': 'Model',
    'type': 'object',
}
"""

print(Model.model_json_schema(mode='serialization'))
"""
{
    'properties': {
        'a': {
            'default': '12.34',
            'pattern': '^(?!^[-+.]*$)[+-]?0*\\d*\\.?\\d*$',
            'title': 'A',
            'type': 'string',
        }
    },
    'title': 'Model',
    'type': 'object',
}
"""
```

## Customizing JSON Schema

The generated JSON schema can be customized at both the field level and model level via:

1. [Field-level customization](#field-level-customization) with the [`Field`][pydantic.fields.Field] constructor
2. [Model-level customization](#model-level-customization) with [`model_config`][pydantic.config.ConfigDict]

At both the field and model levels, you can use the `json_schema_extra` option to add extra information to the JSON schema.
The [Using `json_schema_extra`](#using-json_schema_extra) section below provides more details on this option.

For custom types, Pydantic offers other tools for customizing JSON schema generation:

1. [`WithJsonSchema` annotation](#withjsonschema-annotation)
2. [`SkipJsonSchema` annotation](#skipjsonschema-annotation)
3. [Implementing `__get_pydantic_core_schema__`](#implementing_get_pydantic_core_schema)
4. [Implementing `__get_pydantic_json_schema__`](#implementing_get_pydantic_json_schema)

### Field-Level Customization

Optionally, the [`Field`][pydantic.fields.Field] function can be used to provide extra information about the field
and validations.

Some field parameters are used exclusively to customize the generated JSON Schema:

* `title`: The title of the field.
* `description`: The description of the field.
* `examples`: The examples of the field.
* `json_schema_extra`: Extra JSON Schema properties to be added to the field.
* `field_title_generator`: A function that programmatically sets the field's title, based on its name and info.

Here's an example:

```python {output="json"}
import json

from pydantic import BaseModel, EmailStr, Field, SecretStr


class User(BaseModel):
    age: int = Field(description='Age of the user')
    email: EmailStr = Field(examples=['marcelo@mail.com'])
    name: str = Field(title='Username')
    password: SecretStr = Field(
        json_schema_extra={
            'title': 'Password',
            'description': 'Password of the user',
            'examples': ['123456'],
        }
    )


print(json.dumps(User.model_json_schema(), indent=2))
"""
{
  "properties": {
    "age": {
      "description": "Age of the user",
      "title": "Age",
      "type": "integer"
    },
    "email": {
      "examples": [
        "marcelo@mail.com"
      ],
      "format": "email",
      "title": "Email",
      "type": "string"
    },
    "name": {
      "title": "Username",
      "type": "string"
    },
    "password": {
      "description": "Password of the user",
      "examples": [
        "123456"
      ],
      "format": "password",
      "title": "Password",
      "type": "string",
      "writeOnly": true
    }
  },
  "required": [
    "age",
    "email",
    "name",
    "password"
  ],
  "title": "User",
  "type": "object"
}
"""
```

#### Unenforced `Field` constraints

If Pydantic finds constraints which are not being enforced, an error will be raised. If you want to force the
constraint to appear in the schema, even though it's not being checked upon parsing, you can use variadic arguments
to [`Field`][pydantic.fields.Field] with the raw schema attribute name:

```python
from pydantic import BaseModel, Field, PositiveInt

try:
    # this won't work since `PositiveInt` takes precedence over the
    # constraints defined in `Field`, meaning they're ignored
    class Model(BaseModel):
        foo: PositiveInt = Field(lt=10)

except ValueError as e:
    print(e)


# if you find yourself needing this, an alternative is to declare
# the constraints in `Field` (or you could use `conint()`)
# here both constraints will be enforced:
class ModelB(BaseModel):
    # Here both constraints will be applied and the schema
    # will be generated correctly
    foo: int = Field(gt=0, lt=10)


print(ModelB.model_json_schema())
"""
{
    'properties': {
        'foo': {
            'exclusiveMaximum': 10,
            'exclusiveMinimum': 0,
            'title': 'Foo',
            'type': 'integer',
        }
    },
    'required': ['foo'],
    'title': 'ModelB',
    'type': 'object',
}
"""
```

You can specify JSON schema modifications via the [`Field`][pydantic.fields.Field] constructor via [`typing.Annotated`][] as well:

```python {output="json"}
import json
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field


class Foo(BaseModel):
    id: Annotated[str, Field(default_factory=lambda: uuid4().hex)]
    name: Annotated[str, Field(max_length=256)] = Field(
        'Bar', title='CustomName'
    )


print(json.dumps(Foo.model_json_schema(), indent=2))
"""
{
  "properties": {
    "id": {
      "title": "Id",
      "type": "string"
    },
    "name": {
      "default": "Bar",
      "maxLength": 256,
      "title": "CustomName",
      "type": "string"
    }
  },
  "title": "Foo",
  "type": "object"
}
"""
```

### Programmatic field title generation

The `field_title_generator` parameter can be used to programmatically generate the title for a field based on its name and info.

See the following example:

```python
import json

from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo


def make_title(field_name: str, field_info: FieldInfo) -> str:
    return field_name.upper()


class Person(BaseModel):
    name: str = Field(field_title_generator=make_title)
    age: int = Field(field_title_generator=make_title)


print(json.dumps(Person.model_json_schema(), indent=2))
"""
{
  "properties": {
    "name": {
      "title": "NAME",
      "type": "string"
    },
    "age": {
      "title": "AGE",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "Person",
  "type": "object"
}
"""
```

### Model-Level Customization

You can also use [model config][pydantic.config.ConfigDict] to customize JSON schema generation on a model.
Specifically, the following config options are relevant:

* [`title`][pydantic.config.ConfigDict.title]
* [`json_schema_extra`][pydantic.config.ConfigDict.json_schema_extra]
* [`json_schema_mode_override`][pydantic.config.ConfigDict.json_schema_mode_override]
* [`field_title_generator`][pydantic.config.ConfigDict.field_title_generator]
* [`model_title_generator`][pydantic.config.ConfigDict.model_title_generator]

### Using `json_schema_extra`

The `json_schema_extra` option can be used to add extra information to the JSON schema, either at the
[Field level](#field-level-customization) or at the [Model level](#model-level-customization).
You can pass a `dict` or a `Callable` to `json_schema_extra`.

#### Using `json_schema_extra` with a `dict`

You can pass a `dict` to `json_schema_extra` to add extra information to the JSON schema:

```python {output="json"}
import json

from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    a: str

    model_config = ConfigDict(json_schema_extra={'examples': [{'a': 'Foo'}]})


print(json.dumps(Model.model_json_schema(), indent=2))
"""
{
  "examples": [
    {
      "a": "Foo"
    }
  ],
  "properties": {
    "a": {
      "title": "A",
      "type": "string"
    }
  },
  "required": [
    "a"
  ],
  "title": "Model",
  "type": "object"
}
"""
```

#### Using `json_schema_extra` with a `Callable`

You can pass a `Callable` to `json_schema_extra` to modify the JSON schema with a function:

```python {output="json"}
import json

from pydantic import BaseModel, Field


def pop_default(s):
    s.pop('default')


class Model(BaseModel):
    a: int = Field(default=1, json_schema_extra=pop_default)


print(json.dumps(Model.model_json_schema(), indent=2))
"""
{
  "properties": {
    "a": {
      "title": "A",
      "type": "integer"
    }
  },
  "title": "Model",
  "type": "object"
}
"""
```

#### Merging `json_schema_extra`

Starting in v2.9, Pydantic merges `json_schema_extra` dictionaries from annotated types.
This pattern offers a more additive approach to merging rather than the previous override behavior.
This can be quite helpful for cases of reusing json schema extra information across multiple types.

We viewed this change largely as a bug fix, as it resolves unintentional differences in the `json_schema_extra` merging behavior
between `BaseModel` and `TypeAdapter` instances - see [this issue](https://github.com/pydantic/pydantic/issues/9210)
for more details.

```python
import json
from typing import Annotated

from typing_extensions import TypeAlias

from pydantic import Field, TypeAdapter

ExternalType: TypeAlias = Annotated[
    int, Field(json_schema_extra={'key1': 'value1'})
]

ta = TypeAdapter(
    Annotated[ExternalType, Field(json_schema_extra={'key2': 'value2'})]
)
print(json.dumps(ta.json_schema(), indent=2))
"""
{
  "key1": "value1",
  "key2": "value2",
  "type": "integer"
}
"""
```

!!! note
    We no longer (and never fully did) support composing a mix of `dict` and `callable` type `json_schema_extra` specifications.
    If this is a requirement for your use case, please [open a pydantic issue](https://github.com/pydantic/pydantic/issues/new/choose) and explain your situation - we'd be happy to reconsider this decision when presented with a compelling case.

### `WithJsonSchema` annotation

??? api "API Documentation"
    [`pydantic.json_schema.WithJsonSchema`][pydantic.json_schema.WithJsonSchema]<br>

!!! tip
    Using [`WithJsonSchema`][pydantic.json_schema.WithJsonSchema] is preferred over
    [implementing `__get_pydantic_json_schema__`](#implementing_get_pydantic_json_schema) for custom types,
    as it's more simple and less error-prone.

The [`WithJsonSchema`][pydantic.json_schema.WithJsonSchema] annotation can be used to override the generated (base)
JSON schema for a given type without the need to implement `__get_pydantic_core_schema__`
or `__get_pydantic_json_schema__` on the type itself. Note that this overrides the whole JSON Schema generation process
for the field (in the following example, the `'type'` also needs to be provided).

```python {output="json"}
import json
from typing import Annotated

from pydantic import BaseModel, WithJsonSchema

MyInt = Annotated[
    int,
    WithJsonSchema({'type': 'integer', 'examples': [1, 0, -1]}),
]


class Model(BaseModel):
    a: MyInt


print(json.dumps(Model.model_json_schema(), indent=2))
"""
{
  "properties": {
    "a": {
      "examples": [
        1,
        0,
        -1
      ],
      "title": "A",
      "type": "integer"
    }
  },
  "required": [
    "a"
  ],
  "title": "Model",
  "type": "object"
}
"""
```

!!! note
    You might be tempted to use the [`WithJsonSchema`][pydantic.json_schema.WithJsonSchema] annotation
    to fine-tune the JSON Schema of fields having [validators](./validators.md) attached. Instead, it
    is recommended to use [the `json_schema_input_type` argument](./validators.md#json-schema-and-field-validators).

### `SkipJsonSchema` annotation

??? api "API Documentation"
    [`pydantic.json_schema.SkipJsonSchema`][pydantic.json_schema.SkipJsonSchema]<br>

The [`SkipJsonSchema`][pydantic.json_schema.SkipJsonSchema] annotation can be used to skip an included field (or part of a field's specifications)
from the generated JSON schema. See the API docs for more details.

### Implementing `__get_pydantic_core_schema__` <a name="implementing_get_pydantic_core_schema"></a>

Custom types (used as `field_name: TheType` or `field_name: Annotated[TheType, ...]`) as well as `Annotated` metadata
(used as `field_name: Annotated[int, SomeMetadata]`)
can modify or override the generated schema by implementing `__get_pydantic_core_schema__`.
This method receives two positional arguments:

1. The type annotation that corresponds to this type (so in the case of `TheType[T][int]` it would be `TheType[int]`).
2. A handler/callback to call the next implementer of `__get_pydantic_core_schema__`.

The handler system works just like [*wrap* field validators](validators.md#field-wrap-validator).
In this case the input is the type and the output is a `core_schema`.

Here is an example of a custom type that *overrides* the generated `core_schema`:

```python
from dataclasses import dataclass
from typing import Any

from pydantic_core import core_schema

from pydantic import BaseModel, GetCoreSchemaHandler


@dataclass
class CompressedString:
    dictionary: dict[int, str]
    text: list[int]

    def build(self) -> str:
        return ' '.join([self.dictionary[key] for key in self.text])

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        assert source is CompressedString
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )

    @staticmethod
    def _validate(value: str) -> 'CompressedString':
        inverse_dictionary: dict[str, int] = {}
        text: list[int] = []
        for word in value.split(' '):
            if word not in inverse_dictionary:
                inverse_dictionary[word] = len(inverse_dictionary)
            text.append(inverse_dictionary[word])
        return CompressedString(
            {v: k for k, v in inverse_dictionary.items()}, text
        )

    @staticmethod
    def _serialize(value: 'CompressedString') -> str:
        return value.build()


class MyModel(BaseModel):
    value: CompressedString


print(MyModel.model_json_schema())
"""
{
    'properties': {'value': {'title': 'Value', 'type': 'string'}},
    'required': ['value'],
    'title': 'MyModel',
    'type': 'object',
}
"""
print(MyModel(value='fox fox fox dog fox'))
"""
value = CompressedString(dictionary={0: 'fox', 1: 'dog'}, text=[0, 0, 0, 1, 0])
"""

print(MyModel(value='fox fox fox dog fox').model_dump(mode='json'))
#> {'value': 'fox fox fox dog fox'}
```

Since Pydantic would not know how to generate a schema for `CompressedString`, if you call `handler(source)` in its
`__get_pydantic_core_schema__` method you would get a `pydantic.errors.PydanticSchemaGenerationError` error.
This will be the case for most custom types, so you almost never want to call into `handler` for custom types.

The process for `Annotated` metadata is much the same except that you can generally call into `handler` to have
Pydantic handle generating the schema.

```python
from dataclasses import dataclass
from typing import Annotated, Any, Sequence

from pydantic_core import core_schema

from pydantic import BaseModel, GetCoreSchemaHandler, ValidationError


@dataclass
class RestrictCharacters:
    alphabet: Sequence[str]

    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        if not self.alphabet:
            raise ValueError('Alphabet may not be empty')
        schema = handler(
            source
        )  # get the CoreSchema from the type / inner constraints
        if schema['type'] != 'str':
            raise TypeError('RestrictCharacters can only be applied to strings')
        return core_schema.no_info_after_validator_function(
            self.validate,
            schema,
        )

    def validate(self, value: str) -> str:
        if any(c not in self.alphabet for c in value):
            raise ValueError(
                f'{value!r} is not restricted to {self.alphabet!r}'
            )
        return value


class MyModel(BaseModel):
    value: Annotated[str, RestrictCharacters('ABC')]


print(MyModel.model_json_schema())
"""
{
    'properties': {'value': {'title': 'Value', 'type': 'string'}},
    'required': ['value'],
    'title': 'MyModel',
    'type': 'object',
}
"""
print(MyModel(value='CBA'))
#> value='CBA'

try:
    MyModel(value='XYZ')
except ValidationError as e:
    print(e)
    """
    1 validation error for MyModel
    value
      Value error, 'XYZ' is not restricted to 'ABC' [type=value_error, input_value='XYZ', input_type=str]
    """
```

So far we have been wrapping the schema, but if you just want to *modify* it or *ignore* it you can as well.

To modify the schema, first call the handler, then mutate the result:

```python
from typing import Annotated, Any

from pydantic_core import ValidationError, core_schema

from pydantic import BaseModel, GetCoreSchemaHandler


class SmallString:
    def __get_pydantic_core_schema__(
        self,
        source: type[Any],
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        schema = handler(source)
        assert schema['type'] == 'str'
        schema['max_length'] = 10  # modify in place
        return schema


class MyModel(BaseModel):
    value: Annotated[str, SmallString()]


try:
    MyModel(value='too long!!!!!')
except ValidationError as e:
    print(e)
    """
    1 validation error for MyModel
    value
      String should have at most 10 characters [type=string_too_long, input_value='too long!!!!!', input_type=str]
    """
```

!!! tip
    Note that you *must* return a schema, even if you are just mutating it in place.

To override the schema completely, do not call the handler and return your own
`CoreSchema`:

```python
from typing import Annotated, Any

from pydantic_core import ValidationError, core_schema

from pydantic import BaseModel, GetCoreSchemaHandler


class AllowAnySubclass:
    def __get_pydantic_core_schema__(
        self, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        # we can't call handler since it will fail for arbitrary types
        def validate(value: Any) -> Any:
            if not isinstance(value, source):
                raise ValueError(
                    f'Expected an instance of {source}, got an instance of {type(value)}'
                )

        return core_schema.no_info_plain_validator_function(validate)


class Foo:
    pass


class Model(BaseModel):
    f: Annotated[Foo, AllowAnySubclass()]


print(Model(f=Foo()))
#> f=None


class NotFoo:
    pass


try:
    Model(f=NotFoo())
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    f
      Value error, Expected an instance of <class '__main__.Foo'>, got an instance of <class '__main__.NotFoo'> [type=value_error, input_value=<__main__.NotFoo object at 0x0123456789ab>, input_type=NotFoo]
    """
```

### Implementing `__get_pydantic_json_schema__` <a name="implementing_get_pydantic_json_schema"></a>

You can also implement `__get_pydantic_json_schema__` to modify or override the generated json schema.
Modifying this method only affects the JSON schema - it doesn't affect the core schema, which is used for validation and serialization.

Here's an example of modifying the generated JSON schema:

```python {output="json"}
import json
from typing import Any

from pydantic_core import core_schema as cs

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
from pydantic.json_schema import JsonSchemaValue


class Person:
    name: str
    age: int

    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> cs.CoreSchema:
        return cs.typed_dict_schema(
            {
                'name': cs.typed_dict_field(cs.str_schema()),
                'age': cs.typed_dict_field(cs.int_schema()),
            },
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: cs.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema['examples'] = [
            {
                'name': 'John Doe',
                'age': 25,
            }
        ]
        json_schema['title'] = 'Person'
        return json_schema


print(json.dumps(TypeAdapter(Person).json_schema(), indent=2))
"""
{
  "examples": [
    {
      "age": 25,
      "name": "John Doe"
    }
  ],
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "age": {
      "title": "Age",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "Person",
  "type": "object"
}
"""
```

### Using `field_title_generator`

The `field_title_generator` parameter can be used to programmatically generate the title for a field based on its name and info.
This is similar to the field level `field_title_generator`, but the `ConfigDict` option will be applied to all fields of the class.

See the following example:

```python
import json

from pydantic import BaseModel, ConfigDict


class Person(BaseModel):
    model_config = ConfigDict(
        field_title_generator=lambda field_name, field_info: field_name.upper()
    )
    name: str
    age: int


print(json.dumps(Person.model_json_schema(), indent=2))
"""
{
  "properties": {
    "name": {
      "title": "NAME",
      "type": "string"
    },
    "age": {
      "title": "AGE",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "Person",
  "type": "object"
}
"""
```

### Using `model_title_generator`

The `model_title_generator` config option is similar to the `field_title_generator` option, but it applies to the title of the model itself,
and accepts the model class as input.

See the following example:

```python
import json

from pydantic import BaseModel, ConfigDict


def make_title(model: type) -> str:
    return f'Title-{model.__name__}'


class Person(BaseModel):
    model_config = ConfigDict(model_title_generator=make_title)
    name: str
    age: int


print(json.dumps(Person.model_json_schema(), indent=2))
"""
{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "age": {
      "title": "Age",
      "type": "integer"
    }
  },
  "required": [
    "name",
    "age"
  ],
  "title": "Title-Person",
  "type": "object"
}
"""
```

## JSON schema types

Types, custom field types, and constraints (like `max_length`) are mapped to the corresponding spec formats in the
following priority order (when there is an equivalent available):

1. [JSON Schema Core](https://json-schema.org/draft/2020-12/json-schema-core)
2. [JSON Schema Validation](https://json-schema.org/draft/2020-12/json-schema-validation)
3. [OpenAPI Data Types](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#data-types)
4. The standard `format` JSON field is used to define Pydantic extensions for more complex `string` sub-types.

The field schema mapping from Python or Pydantic to JSON schema is done as follows:

{{ schema_mappings_table }}

## Top-level schema generation

You can also generate a top-level JSON schema that only includes a list of models and related
sub-models in its `$defs`:

```python {output="json"}
import json

from pydantic import BaseModel
from pydantic.json_schema import models_json_schema


class Foo(BaseModel):
    a: str = None


class Model(BaseModel):
    b: Foo


class Bar(BaseModel):
    c: int


_, top_level_schema = models_json_schema(
    [(Model, 'validation'), (Bar, 'validation')], title='My Schema'
)
print(json.dumps(top_level_schema, indent=2))
"""
{
  "$defs": {
    "Bar": {
      "properties": {
        "c": {
          "title": "C",
          "type": "integer"
        }
      },
      "required": [
        "c"
      ],
      "title": "Bar",
      "type": "object"
    },
    "Foo": {
      "properties": {
        "a": {
          "default": null,
          "title": "A",
          "type": "string"
        }
      },
      "title": "Foo",
      "type": "object"
    },
    "Model": {
      "properties": {
        "b": {
          "$ref": "#/$defs/Foo"
        }
      },
      "required": [
        "b"
      ],
      "title": "Model",
      "type": "object"
    }
  },
  "title": "My Schema"
}
"""
```

## Customizing the JSON Schema Generation Process

??? api "API Documentation"
    [`pydantic.json_schema`][pydantic.json_schema.GenerateJsonSchema]<br>

If you need custom schema generation, you can use a `schema_generator`, modifying the
[`GenerateJsonSchema`][pydantic.json_schema.GenerateJsonSchema] class as necessary for your application.

The various methods that can be used to produce JSON schema accept a keyword argument `schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema`, and you can pass your custom subclass to these methods in order to use your own approach to generating JSON schema.

`GenerateJsonSchema` implements the translation of a type's `pydantic-core` schema into a JSON schema.
By design, this class breaks the JSON schema generation process into smaller methods that can be easily overridden in
subclasses to modify the "global" approach to generating JSON schema.

```python
from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema


class MyGenerateJsonSchema(GenerateJsonSchema):
    def generate(self, schema, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        json_schema['title'] = 'Customize title'
        json_schema['$schema'] = self.schema_dialect
        return json_schema


class MyModel(BaseModel):
    x: int


print(MyModel.model_json_schema(schema_generator=MyGenerateJsonSchema))
"""
{
    'properties': {'x': {'title': 'X', 'type': 'integer'}},
    'required': ['x'],
    'title': 'Customize title',
    'type': 'object',
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
}
"""
```

Below is an approach you can use to exclude any fields from the schema that don't have valid json schemas:

```python
from typing import Callable

from pydantic_core import PydanticOmit, core_schema

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue


class MyGenerateJsonSchema(GenerateJsonSchema):
    def handle_invalid_for_json_schema(
        self, schema: core_schema.CoreSchema, error_info: str
    ) -> JsonSchemaValue:
        raise PydanticOmit


def example_callable():
    return 1


class Example(BaseModel):
    name: str = 'example'
    function: Callable = example_callable


instance_example = Example()

validation_schema = instance_example.model_json_schema(
    schema_generator=MyGenerateJsonSchema, mode='validation'
)
print(validation_schema)
"""
{
    'properties': {
        'name': {'default': 'example', 'title': 'Name', 'type': 'string'}
    },
    'title': 'Example',
    'type': 'object',
}
"""
```

### JSON schema sorting

By default, Pydantic recursively sorts JSON schemas by alphabetically sorting keys. Notably, Pydantic skips sorting the values of the `properties` key,
to preserve the order of the fields as they were defined in the model.

If you would like to customize this behavior, you can override the `sort` method in your custom `GenerateJsonSchema` subclass. The below example
uses a no-op `sort` method to disable sorting entirely, which is reflected in the preserved order of the model fields and `json_schema_extra` keys:

```python
import json
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue


class MyGenerateJsonSchema(GenerateJsonSchema):
    def sort(
        self, value: JsonSchemaValue, parent_key: Optional[str] = None
    ) -> JsonSchemaValue:
        """No-op, we don't want to sort schema values at all."""
        return value


class Bar(BaseModel):
    c: str
    b: str
    a: str = Field(json_schema_extra={'c': 'hi', 'b': 'hello', 'a': 'world'})


json_schema = Bar.model_json_schema(schema_generator=MyGenerateJsonSchema)
print(json.dumps(json_schema, indent=2))
"""
{
  "type": "object",
  "properties": {
    "c": {
      "type": "string",
      "title": "C"
    },
    "b": {
      "type": "string",
      "title": "B"
    },
    "a": {
      "type": "string",
      "c": "hi",
      "b": "hello",
      "a": "world",
      "title": "A"
    }
  },
  "required": [
    "c",
    "b",
    "a"
  ],
  "title": "Bar"
}
"""
```

## Customizing the `$ref`s in JSON Schema

The format of `$ref`s can be altered by calling [`model_json_schema()`][pydantic.main.BaseModel.model_json_schema]
or [`model_dump_json()`][pydantic.main.BaseModel.model_dump_json] with the `ref_template` keyword argument.
The definitions are always stored under the key `$defs`, but a specified prefix can be used for the references.

This is useful if you need to extend or modify the JSON schema default definitions location. For example, with OpenAPI:

```python {output="json"}
import json

from pydantic import BaseModel
from pydantic.type_adapter import TypeAdapter


class Foo(BaseModel):
    a: int


class Model(BaseModel):
    a: Foo


adapter = TypeAdapter(Model)

print(
    json.dumps(
        adapter.json_schema(ref_template='#/components/schemas/{model}'),
        indent=2,
    )
)
"""
{
  "$defs": {
    "Foo": {
      "properties": {
        "a": {
          "title": "A",
          "type": "integer"
        }
      },
      "required": [
        "a"
      ],
      "title": "Foo",
      "type": "object"
    }
  },
  "properties": {
    "a": {
      "$ref": "#/components/schemas/Foo"
    }
  },
  "required": [
    "a"
  ],
  "title": "Model",
  "type": "object"
}
"""
```

## Miscellaneous Notes on JSON Schema Generation

* The JSON schema for `Optional` fields indicates that the value `null` is allowed.
* The `Decimal` type is exposed in JSON schema (and serialized) as a string.
* Since the `namedtuple` type doesn't exist in JSON, a model's JSON schema does not preserve `namedtuple`s as `namedtuple`s.
* Sub-models used are added to the `$defs` JSON attribute and referenced, as per the spec.
* Sub-models with modifications (via the `Field` class) like a custom title, description, or default value,
    are recursively included instead of referenced.
* The `description` for models is taken from either the docstring of the class or the argument `description` to
    the `Field` class.
* The schema is generated by default using aliases as keys, but it can be generated using model
    property names instead by calling [`model_json_schema()`][pydantic.main.BaseModel.model_json_schema] or
    [`model_dump_json()`][pydantic.main.BaseModel.model_dump_json] with the `by_alias=False` keyword argument.
````

## File: docs/concepts/json.md
````markdown
# JSON

## Json Parsing

??? api "API Documentation"
    [`pydantic.main.BaseModel.model_validate_json`][pydantic.main.BaseModel.model_validate_json]
    [`pydantic.type_adapter.TypeAdapter.validate_json`][pydantic.type_adapter.TypeAdapter.validate_json]
    [`pydantic_core.from_json`][pydantic_core.from_json]

Pydantic provides builtin JSON parsing, which helps achieve:

* Significant performance improvements without the cost of using a 3rd party library
* Support for custom errors
* Support for `strict` specifications

Here's an example of Pydantic's builtin JSON parsing via the [`model_validate_json`][pydantic.main.BaseModel.model_validate_json] method, showcasing the support for `strict` specifications while parsing JSON data that doesn't match the model's type annotations:

```python
from datetime import date

from pydantic import BaseModel, ConfigDict, ValidationError


class Event(BaseModel):
    model_config = ConfigDict(strict=True)

    when: date
    where: tuple[int, int]


json_data = '{"when": "1987-01-28", "where": [51, -1]}'
print(Event.model_validate_json(json_data))  # (1)!
#> when=datetime.date(1987, 1, 28) where=(51, -1)

try:
    Event.model_validate({'when': '1987-01-28', 'where': [51, -1]})  # (2)!
except ValidationError as e:
    print(e)
    """
    2 validation errors for Event
    when
      Input should be a valid date [type=date_type, input_value='1987-01-28', input_type=str]
    where
      Input should be a valid tuple [type=tuple_type, input_value=[51, -1], input_type=list]
    """
```

1. JSON has no `date` or tuple types, but Pydantic knows that so allows strings and arrays as inputs respectively when parsing JSON directly.
2. If you pass the same values to the [`model_validate`][pydantic.main.BaseModel.model_validate] method, Pydantic will raise a validation error because the `strict` configuration is enabled.

In v2.5.0 and above, Pydantic uses [`jiter`](https://docs.rs/jiter/latest/jiter/), a fast and iterable JSON parser, to parse JSON data.
Using `jiter` compared to `serde` results in modest performance improvements that will get even better in the future.

The `jiter` JSON parser is almost entirely compatible with the `serde` JSON parser,
with one noticeable enhancement being that `jiter` supports deserialization of `inf` and `NaN` values.
In the future, `jiter` is intended to enable support validation errors to include the location
in the original JSON input which contained the invalid value.

### Partial JSON Parsing

**Starting in v2.7.0**, Pydantic's [JSON parser](https://docs.rs/jiter/latest/jiter/) offers support for partial JSON parsing, which is exposed via [`pydantic_core.from_json`][pydantic_core.from_json]. Here's an example of this feature in action:

```python
from pydantic_core import from_json

partial_json_data = '["aa", "bb", "c'  # (1)!

try:
    result = from_json(partial_json_data, allow_partial=False)
except ValueError as e:
    print(e)  # (2)!
    #> EOF while parsing a string at line 1 column 15

result = from_json(partial_json_data, allow_partial=True)
print(result)  # (3)!
#> ['aa', 'bb']
```

1. The JSON list is incomplete - it's missing a closing `"]`
2. When `allow_partial` is set to `False` (the default), a parsing error occurs.
3. When `allow_partial` is set to `True`, part of the input is deserialized successfully.

This also works for deserializing partial dictionaries. For example:

```python
from pydantic_core import from_json

partial_dog_json = '{"breed": "lab", "name": "fluffy", "friends": ["buddy", "spot", "rufus"], "age'
dog_dict = from_json(partial_dog_json, allow_partial=True)
print(dog_dict)
#> {'breed': 'lab', 'name': 'fluffy', 'friends': ['buddy', 'spot', 'rufus']}
```

!!! tip "Validating LLM Output"
    This feature is particularly beneficial for validating LLM outputs.
    We've written some blog posts about this topic, which you can find [here](https://pydantic.dev/articles).

In future versions of Pydantic, we expect to expand support for this feature through either Pydantic's other JSON validation functions
([`pydantic.main.BaseModel.model_validate_json`][pydantic.main.BaseModel.model_validate_json] and
[`pydantic.type_adapter.TypeAdapter.validate_json`][pydantic.type_adapter.TypeAdapter.validate_json]) or model configuration. Stay tuned 🚀!

For now, you can use [`pydantic_core.from_json`][pydantic_core.from_json] in combination with [`pydantic.main.BaseModel.model_validate`][pydantic.main.BaseModel.model_validate] to achieve the same result. Here's an example:

```python
from pydantic_core import from_json

from pydantic import BaseModel


class Dog(BaseModel):
    breed: str
    name: str
    friends: list


partial_dog_json = '{"breed": "lab", "name": "fluffy", "friends": ["buddy", "spot", "rufus"], "age'
dog = Dog.model_validate(from_json(partial_dog_json, allow_partial=True))
print(repr(dog))
#> Dog(breed='lab', name='fluffy', friends=['buddy', 'spot', 'rufus'])
```

!!! tip
    For partial JSON parsing to work reliably, all fields on the model should have default values.

Check out the following example for a more in-depth look at how to use default values with partial JSON parsing:

!!! example "Using default values with partial JSON parsing"

    ```python
    from typing import Annotated, Any, Optional

    import pydantic_core

    from pydantic import BaseModel, ValidationError, WrapValidator


    def default_on_error(v, handler) -> Any:
        """
        Raise a PydanticUseDefault exception if the value is missing.

        This is useful for avoiding errors from partial
        JSON preventing successful validation.
        """
        try:
            return handler(v)
        except ValidationError as exc:
            # there might be other types of errors resulting from partial JSON parsing
            # that you allow here, feel free to customize as needed
            if all(e['type'] == 'missing' for e in exc.errors()):
                raise pydantic_core.PydanticUseDefault()
            else:
                raise


    class NestedModel(BaseModel):
        x: int
        y: str


    class MyModel(BaseModel):
        foo: Optional[str] = None
        bar: Annotated[
            Optional[tuple[str, int]], WrapValidator(default_on_error)
        ] = None
        nested: Annotated[
            Optional[NestedModel], WrapValidator(default_on_error)
        ] = None


    m = MyModel.model_validate(
        pydantic_core.from_json('{"foo": "x", "bar": ["world",', allow_partial=True)
    )
    print(repr(m))
    #> MyModel(foo='x', bar=None, nested=None)


    m = MyModel.model_validate(
        pydantic_core.from_json(
            '{"foo": "x", "bar": ["world", 1], "nested": {"x":', allow_partial=True
        )
    )
    print(repr(m))
    #> MyModel(foo='x', bar=('world', 1), nested=None)
    ```

### Caching Strings

**Starting in v2.7.0**, Pydantic's [JSON parser](https://docs.rs/jiter/latest/jiter/) offers support for configuring how Python strings are cached during JSON parsing and validation (when Python strings are constructed from Rust strings during Python validation, e.g. after `strip_whitespace=True`).
The `cache_strings` setting is exposed via both [model config][pydantic.config.ConfigDict] and [`pydantic_core.from_json`][pydantic_core.from_json].

The `cache_strings` setting can take any of the following values:

* `True` or `'all'` (the default): cache all strings
* `'keys'`: cache only dictionary keys, this **only** applies when used with [`pydantic_core.from_json`][pydantic_core.from_json] or when parsing JSON using [`Json`][pydantic.types.Json]
* `False` or `'none'`: no caching

Using the string caching feature results in performance improvements, but increases memory usage slightly.

!!! note "String Caching Details"

    1. Strings are cached using a fully associative cache with a size of
    [16,384](https://github.com/pydantic/jiter/blob/5bbdcfd22882b7b286416b22f74abd549c7b2fd7/src/py_string_cache.rs#L113).
    2. Only strings where `len(string) < 64` are cached.
    3. There is some overhead to looking up the cache, which is normally worth it to avoid constructing strings.
    However, if you know there will be very few repeated strings in your data, you might get a performance boost by disabling this setting with `cache_strings=False`.

## JSON Serialization

??? api "API Documentation"
    [`pydantic.main.BaseModel.model_dump_json`][pydantic.main.BaseModel.model_dump_json]<br>
    [`pydantic.type_adapter.TypeAdapter.dump_json`][pydantic.type_adapter.TypeAdapter.dump_json]<br>
    [`pydantic_core.to_json`][pydantic_core.to_json]<br>

For more information on JSON serialization, see the [serialization concepts](./serialization.md) page.
````

## File: docs/concepts/models.md
````markdown
??? api "API Documentation"
    [`pydantic.main.BaseModel`][pydantic.main.BaseModel]<br>

One of the primary ways of defining schema in Pydantic is via models. Models are simply classes which inherit from
[`BaseModel`][pydantic.main.BaseModel] and define fields as annotated attributes.

You can think of models as similar to structs in languages like C, or as the requirements of a single endpoint
in an API.

Models share many similarities with Python's [dataclasses][dataclasses], but have been designed with some subtle-yet-important
differences that streamline certain workflows related to validation, serialization, and JSON schema generation.
You can find more discussion of this in the [Dataclasses](dataclasses.md) section of the docs.

Untrusted data can be passed to a model and, after parsing and validation, Pydantic guarantees that the fields
of the resultant model instance will conform to the field types defined on the model.

!!! note "Validation — a *deliberate* misnomer"
    <h3>TL;DR</h3>

    We use the term "validation" to refer to the process of instantiating a model (or other type) that adheres to specified types and
    constraints. This task, which Pydantic is well known for, is most widely recognized as "validation" in colloquial terms,
    even though in other contexts the term "validation" may be more restrictive.

    ---

    <h3>The long version</h3>

    The potential confusion around the term "validation" arises from the fact that, strictly speaking, Pydantic's
    primary focus doesn't align precisely with the dictionary definition of "validation":

    > <h3>validation</h3>
    > _noun_
    > the action of checking or proving the validity or accuracy of something.

    In Pydantic, the term "validation" refers to the process of instantiating a model (or other type) that adheres to specified
    types and constraints. Pydantic guarantees the types and constraints of the output, not the input data.
    This distinction becomes apparent when considering that Pydantic's `ValidationError` is raised
    when data cannot be successfully parsed into a model instance.

    While this distinction may initially seem subtle, it holds practical significance.
    In some cases, "validation" goes beyond just model creation, and can include the copying and coercion of data.
    This can involve copying arguments passed to the constructor in order to perform coercion to a new type
    without mutating the original input data. For a more in-depth understanding of the implications for your usage,
    refer to the [Data Conversion](#data-conversion) and [Attribute Copies](#attribute-copies) sections below.

    In essence, Pydantic's primary goal is to assure that the resulting structure post-processing (termed "validation")
    precisely conforms to the applied type hints. Given the widespread adoption of "validation" as the colloquial term
    for this process, we will consistently use it in our documentation.

    While the terms "parse" and "validation" were previously used interchangeably, moving forward, we aim to exclusively employ "validate",
    with "parse" reserved specifically for discussions related to [JSON parsing](../concepts/json.md).

## Basic model usage

!!! note

    Pydantic relies heavily on the existing Python typing constructs to define models. If you are not familiar with those, the following resources
    can be useful:

    * The [Type System Guides](https://typing.readthedocs.io/en/latest/guides/index.html)
    * The [mypy documentation](https://mypy.readthedocs.io/en/latest/)

```python {group="basic-model"}
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    name: str = 'Jane Doe'

    model_config = ConfigDict(str_max_length=10)  # (1)!
```

1. Pydantic models support a variety of [configuration values](./config.md)
   (see [here][pydantic.ConfigDict] for the available configuration values).

In this example, `User` is a model with two fields:

* `id`, which is an integer and is required
* `name`, which is a string and is not required (it has a default value).

Fields can be customized in a number of ways using the [`Field()`][pydantic.Field] function.
See the [documentation on fields](./fields.md) for more information.

The model can then be instantiated:

```python {group="basic-model"}
user = User(id='123')
```

`user` is an instance of `User`. Initialization of the object will perform all parsing and validation.
If no [`ValidationError`][pydantic_core.ValidationError] exception is raised,
you know the resulting model instance is valid.

Fields of a model can be accessed as normal attributes of the `user` object:

```python {group="basic-model"}
assert user.name == 'Jane Doe'  # (1)!
assert user.id == 123  # (2)!
assert isinstance(user.id, int)
```

1. `name` wasn't set when `user` was initialized, so the default value was used.
   The [`model_fields_set`][pydantic.BaseModel.model_fields_set] attribute can be
   inspected to check the field names explicitly set during instantiation.
2. Note that the string `'123'` was coerced to an integer and its value is `123`.
   More details on Pydantic's coercion logic can be found in the [data conversion](#data-conversion) section.

The model instance can be serialized using the [`model_dump()`][pydantic.BaseModel.model_dump] method:

```python {group="basic-model"}
assert user.model_dump() == {'id': 123, 'name': 'Jane Doe'}
```

Calling [dict][] on the instance will also provide a dictionary, but nested fields will not be
recursively converted into dictionaries. [`model_dump()`][pydantic.BaseModel.model_dump] also
provides numerous arguments to customize the serialization result.

By default, models are mutable and field values can be changed through attribute assignment:

```python {group="basic-model"}
user.id = 321
assert user.id == 321
```

!!! warning
    When defining your models, watch out for naming collisions between your field name and its type annotation.

    For example, the following will not behave as expected and would yield a validation error:

    ```python {test="skip"}
    from typing import Optional

    from pydantic import BaseModel


    class Boo(BaseModel):
        int: Optional[int] = None


    m = Boo(int=123)  # Will fail to validate.
    ```

    Because of how Python evaluates [annotated assignment statements][annassign], the statement is equivalent to `int: None = None`, thus
    leading to a validation error.

### Model methods and properties

The example above only shows the tip of the iceberg of what models can do.
Models possess the following methods and attributes:

* [`model_validate()`][pydantic.main.BaseModel.model_validate]: Validates the given object against the Pydantic model. See [Validating data](#validating-data).
* [`model_validate_json()`][pydantic.main.BaseModel.model_validate_json]: Validates the given JSON data against the Pydantic model. See
    [Validating data](#validating-data).
* [`model_construct()`][pydantic.main.BaseModel.model_construct]: Creates models without running validation. See
    [Creating models without validation](#creating-models-without-validation).
* [`model_dump()`][pydantic.main.BaseModel.model_dump]: Returns a dictionary of the model's fields and values. See
    [Serialization](serialization.md#python-mode).
* [`model_dump_json()`][pydantic.main.BaseModel.model_dump_json]: Returns a JSON string representation of [`model_dump()`][pydantic.main.BaseModel.model_dump]. See [Serialization](serialization.md#json-mode).
* [`model_copy()`][pydantic.main.BaseModel.model_copy]: Returns a copy (by default, shallow copy) of the model. See
    [Model copy](#model-copy).
* [`model_json_schema()`][pydantic.main.BaseModel.model_json_schema]: Returns a jsonable dictionary representing the model's JSON Schema. See [JSON Schema](json_schema.md).
* [`model_fields`][pydantic.main.BaseModel.model_fields]: A mapping between field names and their definitions ([`FieldInfo`][pydantic.fields.FieldInfo] instances).
* [`model_computed_fields`][pydantic.main.BaseModel.model_computed_fields]: A mapping between computed field names and their definitions ([`ComputedFieldInfo`][pydantic.fields.ComputedFieldInfo] instances).
* [`model_extra`][pydantic.main.BaseModel.model_extra]: The extra fields set during validation.
* [`model_fields_set`][pydantic.main.BaseModel.model_fields_set]: The set of fields which were explicitly provided when the model was initialized.
* [`model_parametrized_name()`][pydantic.main.BaseModel.model_parametrized_name]: Computes the class name for parametrizations of generic classes.
* [`model_post_init()`][pydantic.main.BaseModel.model_post_init]: Performs additional actions after the model is instantiated and all field validators are applied.
* [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild]: Rebuilds the model schema, which also supports building recursive generic models.
    See [Rebuilding model schema](#rebuilding-model-schema).

!!! note
    See the API documentation of [`BaseModel`][pydantic.main.BaseModel] for the class definition including a full list of methods and attributes.

!!! tip
    See [Changes to `pydantic.BaseModel`](../migration.md#changes-to-pydanticbasemodel) in the
    [Migration Guide](../migration.md) for details on changes from Pydantic V1.

## Data conversion

Pydantic may cast input data to force it to conform to model field types,
and in some cases this may result in a loss of information.
For example:

```python
from pydantic import BaseModel


class Model(BaseModel):
    a: int
    b: float
    c: str


print(Model(a=3.000, b='2.72', c=b'binary data').model_dump())
#> {'a': 3, 'b': 2.72, 'c': 'binary data'}
```

This is a deliberate decision of Pydantic, and is frequently the most useful approach. See
[here](https://github.com/pydantic/pydantic/issues/578) for a longer discussion on the subject.

Nevertheless, Pydantic provides a [strict mode](strict_mode.md), where no data conversion is performed.
Values must be of the same type than the declared field type.

This is also the case for collections. In most cases, you shouldn't make use of abstract container classes
and just use a concrete type, such as [`list`][]:

```python
from pydantic import BaseModel


class Model(BaseModel):
    items: list[int]  # (1)!


print(Model(items=(1, 2, 3)))
#> items=[1, 2, 3]
```

1. In this case, you might be tempted to use the abstract [`Sequence`][collections.abc.Sequence] type
   to allow both lists and tuples. But Pydantic takes care of converting the tuple input to a list, so
   in most cases this isn't necessary.

Besides, using these abstract types can also lead to [poor validation performance](./performance.md#sequence-vs-list-or-tuple-with-mapping-vs-dict), and in general using concrete container types
will avoid unnecessary checks.

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#extra-fields}

## Extra data

By default, Pydantic models **won't error when you provide extra data**, and these values will simply be ignored:

```python
from pydantic import BaseModel


class Model(BaseModel):
    x: int


m = Model(x=1, y='a')
assert m.model_dump() == {'x': 1}
```

The [`extra`][pydantic.ConfigDict.extra] configuration value can be used to control this behavior:

```python
from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    x: int

    model_config = ConfigDict(extra='allow')


m = Model(x=1, y='a')  # (1)!
assert m.model_dump() == {'x': 1, 'y': 'a'}
assert m.__pydantic_extra__ == {'y': 'a'}
```

1. If [`extra`][pydantic.ConfigDict.extra] was set to `'forbid'`, this would fail.

The configuration can take three values:

* `'ignore'`: Providing extra data is ignored (the default).
* `'forbid'`: Providing extra data is not permitted.
* `'allow'`: Providing extra data is allowed and stored in the `__pydantic_extra__` dictionary attribute.
  The `__pydantic_extra__` can explicitly be annotated to provide validation for extra fields.

For more details, refer to the [`extra`][pydantic.ConfigDict.extra] API documentation.

Pydantic dataclasses also support extra data (see the [dataclass configuration](./dataclasses.md#dataclass-config) section).

## Nested models

More complex hierarchical data structures can be defined using models themselves as types in annotations.

```python
from typing import Optional

from pydantic import BaseModel


class Foo(BaseModel):
    count: int
    size: Optional[float] = None


class Bar(BaseModel):
    apple: str = 'x'
    banana: str = 'y'


class Spam(BaseModel):
    foo: Foo
    bars: list[Bar]


m = Spam(foo={'count': 4}, bars=[{'apple': 'x1'}, {'apple': 'x2'}])
print(m)
"""
foo=Foo(count=4, size=None) bars=[Bar(apple='x1', banana='y'), Bar(apple='x2', banana='y')]
"""
print(m.model_dump())
"""
{
    'foo': {'count': 4, 'size': None},
    'bars': [{'apple': 'x1', 'banana': 'y'}, {'apple': 'x2', 'banana': 'y'}],
}
"""
```

Self-referencing models are supported. For more details, see  the documentation related to
[forward annotations](forward_annotations.md#self-referencing-or-recursive-models).

## Rebuilding model schema

When you define a model class in your code, Pydantic will analyze the body of the class to collect a variety of information
required to perform validation and serialization, gathered in a core schema. Notably, the model's type annotations are evaluated to
understand the valid types for each field (more information can be found in the [Architecture](../internals/architecture.md) documentation).
However, it might be the case that annotations refer to symbols not defined when the model class is being created.
To circumvent this issue, the [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] method can be used:

```python
from pydantic import BaseModel, PydanticUserError


class Foo(BaseModel):
    x: 'Bar'  # (1)!


try:
    Foo.model_json_schema()
except PydanticUserError as e:
    print(e)
    """
    `Foo` is not fully defined; you should define `Bar`, then call `Foo.model_rebuild()`.

    For further information visit https://errors.pydantic.dev/2/u/class-not-fully-defined
    """


class Bar(BaseModel):
    pass


Foo.model_rebuild()
print(Foo.model_json_schema())
"""
{
    '$defs': {'Bar': {'properties': {}, 'title': 'Bar', 'type': 'object'}},
    'properties': {'x': {'$ref': '#/$defs/Bar'}},
    'required': ['x'],
    'title': 'Foo',
    'type': 'object',
}
"""
```

1. `Bar` is not yet defined when the `Foo` class is being created. For this reason,
    a [forward annotation](forward_annotations.md) is being used.

Pydantic tries to determine when this is necessary automatically and error if it wasn't done, but you may want to
call [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] proactively when dealing with recursive models or generics.

In V2, [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] replaced `update_forward_refs()` from V1. There are some slight differences with the new behavior.
The biggest change is that when calling [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] on the outermost model, it builds a core schema used for validation of the
whole model (nested models and all), so all types at all levels need to be ready before [`model_rebuild()`][pydantic.main.BaseModel.model_rebuild] is called.

## Arbitrary class instances

(Formerly known as "ORM Mode"/`from_orm`).

Pydantic models can also be created from arbitrary class instances by reading the instance attributes corresponding
to the model field names. One common application of this functionality is integration with object-relational mappings
(ORMs).

To do this, set the [`from_attributes`][pydantic.config.ConfigDict.from_attributes] config value to `True`
(see the documentation on [Configuration](./config.md) for more details).

The example here uses [SQLAlchemy](https://www.sqlalchemy.org/), but the same approach should work for any ORM.

```python
from typing import Annotated

from sqlalchemy import ARRAY, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pydantic import BaseModel, ConfigDict, StringConstraints


class Base(DeclarativeBase):
    pass


class CompanyOrm(Base):
    __tablename__ = 'companies'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    public_key: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False, unique=True
    )
    domains: Mapped[list[str]] = mapped_column(ARRAY(String(255)))


class CompanyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    public_key: Annotated[str, StringConstraints(max_length=20)]
    domains: list[Annotated[str, StringConstraints(max_length=255)]]


co_orm = CompanyOrm(
    id=123,
    public_key='foobar',
    domains=['example.com', 'foobar.com'],
)
print(co_orm)
#> <__main__.CompanyOrm object at 0x0123456789ab>
co_model = CompanyModel.model_validate(co_orm)
print(co_model)
#> id=123 public_key='foobar' domains=['example.com', 'foobar.com']
```

### Nested attributes

When using attributes to parse models, model instances will be created from both top-level attributes and
deeper-nested attributes as appropriate.

Here is an example demonstrating the principle:

```python
from pydantic import BaseModel, ConfigDict


class PetCls:
    def __init__(self, *, name: str, species: str):
        self.name = name
        self.species = species


class PersonCls:
    def __init__(self, *, name: str, age: float = None, pets: list[PetCls]):
        self.name = name
        self.age = age
        self.pets = pets


class Pet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    species: str


class Person(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    age: float = None
    pets: list[Pet]


bones = PetCls(name='Bones', species='dog')
orion = PetCls(name='Orion', species='cat')
anna = PersonCls(name='Anna', age=20, pets=[bones, orion])
anna_model = Person.model_validate(anna)
print(anna_model)
"""
name='Anna' age=20.0 pets=[Pet(name='Bones', species='dog'), Pet(name='Orion', species='cat')]
"""
```

## Error handling

Pydantic will raise a [`ValidationError`][pydantic_core.ValidationError] exception whenever it finds an error in the data it's validating.

A single exception will be raised regardless of the number of errors found, and that validation error
will contain information about all of the errors and how they happened.

See [Error Handling](../errors/errors.md) for details on standard and custom errors.

As a demonstration:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    list_of_ints: list[int]
    a_float: float


data = dict(
    list_of_ints=['1', 2, 'bad'],
    a_float='not a float',
)

try:
    Model(**data)
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    list_of_ints.2
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='bad', input_type=str]
    a_float
      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='not a float', input_type=str]
    """
```

## Validating data

Pydantic provides three methods on models classes for parsing data:

* [`model_validate()`][pydantic.main.BaseModel.model_validate]: this is very similar to the `__init__` method of the model,
  except it takes a dictionary or an object rather than keyword arguments. If the object passed cannot be validated,
  or if it's not a dictionary or instance of the model in question, a [`ValidationError`][pydantic_core.ValidationError] will be raised.
* [`model_validate_json()`][pydantic.main.BaseModel.model_validate_json]: this validates the provided data as a JSON string or `bytes` object.
  If your incoming data is a JSON payload, this is generally considered faster (instead of manually parsing the data as a dictionary).
  Learn more about JSON parsing in the [JSON](../concepts/json.md) section of the docs.
* [`model_validate_strings()`][pydantic.main.BaseModel.model_validate_strings]: this takes a dictionary (can be nested) with string keys and values and validates the data in JSON mode so that said strings can be coerced into the correct types.

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ValidationError


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: Optional[datetime] = None


m = User.model_validate({'id': 123, 'name': 'James'})
print(m)
#> id=123 name='James' signup_ts=None

try:
    User.model_validate(['not', 'a', 'dict'])
except ValidationError as e:
    print(e)
    """
    1 validation error for User
      Input should be a valid dictionary or instance of User [type=model_type, input_value=['not', 'a', 'dict'], input_type=list]
    """

m = User.model_validate_json('{"id": 123, "name": "James"}')
print(m)
#> id=123 name='James' signup_ts=None

try:
    m = User.model_validate_json('{"id": 123, "name": 123}')
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    name
      Input should be a valid string [type=string_type, input_value=123, input_type=int]
    """

try:
    m = User.model_validate_json('invalid JSON')
except ValidationError as e:
    print(e)
    """
    1 validation error for User
      Invalid JSON: expected value at line 1 column 1 [type=json_invalid, input_value='invalid JSON', input_type=str]
    """

m = User.model_validate_strings({'id': '123', 'name': 'James'})
print(m)
#> id=123 name='James' signup_ts=None

m = User.model_validate_strings(
    {'id': '123', 'name': 'James', 'signup_ts': '2024-04-01T12:00:00'}
)
print(m)
#> id=123 name='James' signup_ts=datetime.datetime(2024, 4, 1, 12, 0)

try:
    m = User.model_validate_strings(
        {'id': '123', 'name': 'James', 'signup_ts': '2024-04-01'}, strict=True
    )
except ValidationError as e:
    print(e)
    """
    1 validation error for User
    signup_ts
      Input should be a valid datetime, invalid datetime separator, expected `T`, `t`, `_` or space [type=datetime_parsing, input_value='2024-04-01', input_type=str]
    """
```

If you want to validate serialized data in a format other than JSON, you should load the data into a dictionary yourself and
then pass it to [`model_validate`][pydantic.main.BaseModel.model_validate].

!!! note
    Depending on the types and model configs involved, [`model_validate`][pydantic.main.BaseModel.model_validate]
    and [`model_validate_json`][pydantic.main.BaseModel.model_validate_json] may have different validation behavior.
    If you have data coming from a non-JSON source, but want the same validation
    behavior and errors you'd get from [`model_validate_json`][pydantic.main.BaseModel.model_validate_json],
    our recommendation for now is to use either use `model_validate_json(json.dumps(data))`, or use [`model_validate_strings`][pydantic.main.BaseModel.model_validate_strings] if the data takes the form of a (potentially nested) dictionary with string keys and values.

!!! note
    If you're passing in an instance of a model to [`model_validate`][pydantic.main.BaseModel.model_validate], you will want to consider setting
    [`revalidate_instances`][pydantic.ConfigDict.revalidate_instances] in the model's config.
    If you don't set this value, then validation will be skipped on model instances. See the below example:

    === ":x: `revalidate_instances='never'`"
        ```python
        from pydantic import BaseModel


        class Model(BaseModel):
            a: int


        m = Model(a=0)
        # note: setting `validate_assignment` to `True` in the config can prevent this kind of misbehavior.
        m.a = 'not an int'

        # doesn't raise a validation error even though m is invalid
        m2 = Model.model_validate(m)
        ```

    === ":white_check_mark: `revalidate_instances='always'`"
        ```python
        from pydantic import BaseModel, ConfigDict, ValidationError


        class Model(BaseModel):
            a: int

            model_config = ConfigDict(revalidate_instances='always')


        m = Model(a=0)
        # note: setting `validate_assignment` to `True` in the config can prevent this kind of misbehavior.
        m.a = 'not an int'

        try:
            m2 = Model.model_validate(m)
        except ValidationError as e:
            print(e)
            """
            1 validation error for Model
            a
              Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='not an int', input_type=str]
            """
        ```

### Creating models without validation

Pydantic also provides the [`model_construct()`][pydantic.main.BaseModel.model_construct] method, which allows models to be created **without validation**.
This can be useful in at least a few cases:

* when working with complex data that is already known to be valid (for performance reasons)
* when one or more of the validator functions are non-idempotent
* when one or more of the validator functions have side effects that you don't want to be triggered.

!!! warning
    [`model_construct()`][pydantic.main.BaseModel.model_construct] does not do any validation, meaning it can create
    models which are invalid. **You should only ever use the [`model_construct()`][pydantic.main.BaseModel.model_construct]
    method with data which has already been validated, or that you definitely trust.**

!!! note
    In Pydantic V2, the performance gap between validation (either with direct instantiation or the `model_validate*` methods)
    and [`model_construct()`][pydantic.main.BaseModel.model_construct] has been narrowed
    considerably. For simple models, going with validation may even be faster. If you are using [`model_construct()`][pydantic.main.BaseModel.model_construct]
    for performance reasons, you may want to profile your use case before assuming it is actually faster.

Note that for [root models](#rootmodel-and-custom-root-types), the root value can be passed to
[`model_construct()`][pydantic.main.BaseModel.model_construct] positionally, instead of using a keyword argument.

Here are some additional notes on the behavior of [`model_construct()`][pydantic.main.BaseModel.model_construct]:

* When we say "no validation is performed" — this includes converting dictionaries to model instances. So if you have a field
  referring to a model type, you will need to convert the inner dictionary to a model yourself.
* If you do not pass keyword arguments for fields with defaults, the default values will still be used.
* For models with private attributes, the `__pydantic_private__` dictionary will be populated the same as it would be when
  creating the model with validation.
* No `__init__` method from the model or any of its parent classes will be called, even when a custom `__init__` method is defined.

!!! note "On [extra data](#extra-data) behavior with [`model_construct()`][pydantic.main.BaseModel.model_construct]"

    * For models with [`extra`][pydantic.ConfigDict.extra] set to `'allow'`, data not corresponding to fields will be correctly stored in
    the `__pydantic_extra__` dictionary and saved to the model's `__dict__` attribute.
    * For models with [`extra`][pydantic.ConfigDict.extra] set to `'ignore'`, data not corresponding to fields will be ignored — that is,
    not stored in `__pydantic_extra__` or `__dict__` on the instance.
    * Unlike when instantiating the model with validation, a call to [`model_construct()`][pydantic.main.BaseModel.model_construct] with [`extra`][pydantic.ConfigDict.extra] set to `'forbid'` doesn't raise an error in the presence of data not corresponding to fields. Rather, said input data is simply ignored.

## Model copy

??? api "API Documentation"
    [`pydantic.main.BaseModel.model_copy`][pydantic.main.BaseModel.model_copy]<br>

The [`model_copy()`][pydantic.BaseModel.model_copy] method allows models to be duplicated (with optional updates),
which is particularly useful when working with frozen models.

```python
from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    banana: float
    foo: str
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})

print(m.model_copy(update={'banana': 0}))
#> banana=0 foo='hello' bar=BarModel(whatever=123)

# normal copy gives the same object reference for bar:
print(id(m.bar) == id(m.model_copy().bar))
#> True
# deep copy gives a new object reference for `bar`:
print(id(m.bar) == id(m.model_copy(deep=True).bar))
#> False
```

## Generic models

Pydantic supports the creation of generic models to make it easier to reuse a common model structure. Both the new
[type parameter syntax][type-params] (introduced by [PEP 695](https://peps.python.org/pep-0695/) in Python 3.12)
and the old syntax are supported (refer to
[the Python documentation](https://docs.python.org/3/library/typing.html#building-generic-types-and-type-aliases)
for more details).

Here is an example using a generic Pydantic model to create an easily-reused HTTP response payload wrapper:

<!-- TODO: tabs should be auto-generated if using Ruff (https://github.com/pydantic/pydantic/issues/10083) -->

=== "Python 3.9 and above"

    ```python {upgrade="skip"}
    from typing import Generic, TypeVar

    from pydantic import BaseModel, ValidationError

    DataT = TypeVar('DataT')  # (1)!


    class DataModel(BaseModel):
        number: int


    class Response(BaseModel, Generic[DataT]):  # (2)!
        data: DataT  # (3)!


    print(Response[int](data=1))
    #> data=1
    print(Response[str](data='value'))
    #> data='value'
    print(Response[str](data='value').model_dump())
    #> {'data': 'value'}

    data = DataModel(number=1)
    print(Response[DataModel](data=data).model_dump())
    #> {'data': {'number': 1}}
    try:
        Response[int](data='value')
    except ValidationError as e:
        print(e)
        """
        1 validation error for Response[int]
        data
          Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='value', input_type=str]
        """
    ```

    1. Declare one or more [type variables][typing.TypeVar] to use to parameterize your model.
    2. Declare a Pydantic model that inherits from [`BaseModel`][pydantic.BaseModel] and [`typing.Generic`][]
       (in this specific order), and add the list of type variables you declared previously as parameters to the
       [`Generic`][typing.Generic] parent.
    3. Use the type variables as annotations where you will want to replace them with other types.

=== "Python 3.12 and above (new syntax)"

    ```python {requires="3.12" upgrade="skip"}
    from pydantic import BaseModel, ValidationError


    class DataModel(BaseModel):
        number: int


    class Response[DataT](BaseModel):  # (1)!
        data: DataT  # (2)!


    print(Response[int](data=1))
    #> data=1
    print(Response[str](data='value'))
    #> data='value'
    print(Response[str](data='value').model_dump())
    #> {'data': 'value'}

    data = DataModel(number=1)
    print(Response[DataModel](data=data).model_dump())
    #> {'data': {'number': 1}}
    try:
        Response[int](data='value')
    except ValidationError as e:
        print(e)
        """
        1 validation error for Response[int]
        data
          Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='value', input_type=str]
        """
    ```

    1. Declare a Pydantic model and add the list of type variables as type parameters.
    2. Use the type variables as annotations where you will want to replace them with other types.

!!! warning
    When parametrizing a model with a concrete type, Pydantic **does not** validate that the provided type
    is [assignable to the type variable][spec-typevars-bound] if it has an upper bound.

    [spec-typevars-bound]: https://typing.readthedocs.io/en/latest/spec/generics.html#type-variables-with-an-upper-bound

Any [configuration](./config.md), [validation](./validators.md) or [serialization](./serialization.md) logic
set on the generic model will also be applied to the parametrized classes, in the same way as when inheriting from
a model class. Any custom methods or attributes will also be inherited.

Generic models also integrate properly with type checkers, so you get all the type checking
you would expect if you were to declare a distinct type for each parametrization.

!!! note
    Internally, Pydantic creates subclasses of the generic model at runtime when the generic model class is parametrized.
    These classes are cached, so there should be minimal overhead introduced by the use of generics models.

To inherit from a generic model and preserve the fact that it is generic, the subclass must also inherit from
[`Generic`][typing.Generic]:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

TypeX = TypeVar('TypeX')


class BaseClass(BaseModel, Generic[TypeX]):
    X: TypeX


class ChildClass(BaseClass[TypeX], Generic[TypeX]):
    pass


# Parametrize `TypeX` with `int`:
print(ChildClass[int](X=1))
#> X=1
```

You can also create a generic subclass of a model that partially or fully replaces the type variables in the
superclass:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

TypeX = TypeVar('TypeX')
TypeY = TypeVar('TypeY')
TypeZ = TypeVar('TypeZ')


class BaseClass(BaseModel, Generic[TypeX, TypeY]):
    x: TypeX
    y: TypeY


class ChildClass(BaseClass[int, TypeY], Generic[TypeY, TypeZ]):
    z: TypeZ


# Parametrize `TypeY` with `str`:
print(ChildClass[str, int](x='1', y='y', z='3'))
#> x=1 y='y' z=3
```

If the name of the concrete subclasses is important, you can also override the default name generation
by overriding the [`model_parametrized_name()`][pydantic.main.BaseModel.model_parametrized_name] method:

```python
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar('DataT')


class Response(BaseModel, Generic[DataT]):
    data: DataT

    @classmethod
    def model_parametrized_name(cls, params: tuple[type[Any], ...]) -> str:
        return f'{params[0].__name__.title()}Response'


print(repr(Response[int](data=1)))
#> IntResponse(data=1)
print(repr(Response[str](data='a')))
#> StrResponse(data='a')
```

You can use parametrized generic models as types in other models:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    content: T


class Product(BaseModel):
    name: str
    price: float


class Order(BaseModel):
    id: int
    product: ResponseModel[Product]


product = Product(name='Apple', price=0.5)
response = ResponseModel[Product](content=product)
order = Order(id=1, product=response)
print(repr(order))
"""
Order(id=1, product=ResponseModel[Product](content=Product(name='Apple', price=0.5)))
"""
```

Using the same type variable in nested models allows you to enforce typing relationships at different points in your model:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar('T')


class InnerT(BaseModel, Generic[T]):
    inner: T


class OuterT(BaseModel, Generic[T]):
    outer: T
    nested: InnerT[T]


nested = InnerT[int](inner=1)
print(OuterT[int](outer=1, nested=nested))
#> outer=1 nested=InnerT[int](inner=1)
try:
    print(OuterT[int](outer='a', nested=InnerT(inner='a')))  # (1)!
except ValidationError as e:
    print(e)
    """
    2 validation errors for OuterT[int]
    outer
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    nested.inner
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """
```

1. The `OuterT` model is parametrized with `int`, but the data associated with the the `T` annotations during validation is of type `str`, leading to validation errors.

!!! warning
    While it may not raise an error, we strongly advise against using parametrized generics in [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) checks.

    For example, you should not do `isinstance(my_model, MyGenericModel[int])`. However, it is fine to do `isinstance(my_model, MyGenericModel)` (note that, for standard generics, it would raise an error to do a subclass check with a parameterized generic class).

    If you need to perform [`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) checks against parametrized generics, you can do this by subclassing the parametrized generic class:

    ```python {test="skip" lint="skip"}
    class MyIntModel(MyGenericModel[int]): ...

    isinstance(my_model, MyIntModel)
    ```

??? note "Implementation Details"
    When using nested generic models, Pydantic sometimes performs revalidation in an attempt to produce the most intuitive validation result.
    Specifically, if you have a field of type `GenericModel[SomeType]` and you validate data like `GenericModel[SomeCompatibleType]` against this field,
    we will inspect the data, recognize that the input data is sort of a "loose" subclass of `GenericModel`, and revalidate the contained `SomeCompatibleType` data.

    This adds some validation overhead, but makes things more intuitive for cases like that shown below.

    ```python
    from typing import Any, Generic, TypeVar

    from pydantic import BaseModel

    T = TypeVar('T')


    class GenericModel(BaseModel, Generic[T]):
        a: T


    class Model(BaseModel):
        inner: GenericModel[Any]


    print(repr(Model.model_validate(Model(inner=GenericModel[int](a=1)))))
    #> Model(inner=GenericModel[Any](a=1))
    ```

    Note, validation will still fail if you, for example are validating against `GenericModel[int]` and pass in an instance `GenericModel[str](a='not an int')`.

    It's also worth noting that this pattern will re-trigger any custom validation as well, like additional model validators and the like.
    Validators will be called once on the first pass, validating directly against `GenericModel[Any]`. That validation fails, as `GenericModel[int]` is not a subclass of `GenericModel[Any]`. This relates to the warning above about the complications of using parametrized generics in `isinstance()` and `issubclass()` checks.
    Then, the validators will be called again on the second pass, during more lax force-revalidation phase, which succeeds.
    To better understand this consequence, see below:

    ```python {test="skip"}
    from typing import Any, Generic, Self, TypeVar

    from pydantic import BaseModel, model_validator

    T = TypeVar('T')


    class GenericModel(BaseModel, Generic[T]):
        a: T

        @model_validator(mode='after')
        def validate_after(self: Self) -> Self:
            print('after validator running custom validation...')
            return self


    class Model(BaseModel):
        inner: GenericModel[Any]


    m = Model.model_validate(Model(inner=GenericModel[int](a=1)))
    #> after validator running custom validation...
    #> after validator running custom validation...
    print(repr(m))
    #> Model(inner=GenericModel[Any](a=1))
    ```

### Validation of unparametrized type variables

When leaving type variables unparametrized, Pydantic treats generic models similarly to how it treats built-in generic
types like [`list`][] and [`dict`][]:

* If the type variable is [bound](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-upper-bounds)
  or [constrained](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints) to a specific type,
  it will be used.
* If the type variable has a default type (as specified by [PEP 696](https://peps.python.org/pep-0696/)), it will be used.
* For unbound or unconstrained type variables, Pydantic will fallback to [`Any`][typing.Any].

```python
from typing import Generic

from typing_extensions import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar('T')
U = TypeVar('U', bound=int)
V = TypeVar('V', default=str)


class Model(BaseModel, Generic[T, U, V]):
    t: T
    u: U
    v: V


print(Model(t='t', u=1, v='v'))
#> t='t' u=1 v='v'

try:
    Model(t='t', u='u', v=1)
except ValidationError as exc:
    print(exc)
    """
    2 validation errors for Model
    u
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='u', input_type=str]
    v
      Input should be a valid string [type=string_type, input_value=1, input_type=int]
    """
```

!!! warning

    In some cases, validation against an unparametrized generic model can lead to data loss. Specifically, if a subtype of the type variable upper bound, constraints, or default is being used and the model isn't explicitly parametrized, the resulting type **will not be** the one being provided:

    ```python
    from typing import Generic, TypeVar

    from pydantic import BaseModel

    ItemT = TypeVar('ItemT', bound='ItemBase')


    class ItemBase(BaseModel): ...


    class IntItem(ItemBase):
        value: int


    class ItemHolder(BaseModel, Generic[ItemT]):
        item: ItemT


    loaded_data = {'item': {'value': 1}}


    print(ItemHolder(**loaded_data))  # (1)!
    #> item=ItemBase()

    print(ItemHolder[IntItem](**loaded_data))  # (2)!
    #> item=IntItem(value=1)
    ```

    1. When the generic isn't parametrized, the input data is validated against the `ItemT` upper bound.
       Given that `ItemBase` has no fields, the `item` field information is lost.
    2. In this case, the type variable is explicitly parametrized, so the input data is validated against the `IntItem` class.

### Serialization of unparametrized type variables

The behavior of serialization differs when using type variables with [upper bounds](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-upper-bounds), [constraints](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints), or a default value:

If a Pydantic model is used in a type variable upper bound and the type variable is never parametrized, then Pydantic will use the upper bound for validation but treat the value as [`Any`][typing.Any] in terms of serialization:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel


class ErrorDetails(BaseModel):
    foo: str


ErrorDataT = TypeVar('ErrorDataT', bound=ErrorDetails)


class Error(BaseModel, Generic[ErrorDataT]):
    message: str
    details: ErrorDataT


class MyErrorDetails(ErrorDetails):
    bar: str


# serialized as Any
error = Error(
    message='We just had an error',
    details=MyErrorDetails(foo='var', bar='var2'),
)
assert error.model_dump() == {
    'message': 'We just had an error',
    'details': {
        'foo': 'var',
        'bar': 'var2',
    },
}

# serialized using the concrete parametrization
# note that `'bar': 'var2'` is missing
error = Error[ErrorDetails](
    message='We just had an error',
    details=ErrorDetails(foo='var'),
)
assert error.model_dump() == {
    'message': 'We just had an error',
    'details': {
        'foo': 'var',
    },
}
```

Here's another example of the above behavior, enumerating all permutations regarding bound specification and generic type parametrization:

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

TBound = TypeVar('TBound', bound=BaseModel)
TNoBound = TypeVar('TNoBound')


class IntValue(BaseModel):
    value: int


class ItemBound(BaseModel, Generic[TBound]):
    item: TBound


class ItemNoBound(BaseModel, Generic[TNoBound]):
    item: TNoBound


item_bound_inferred = ItemBound(item=IntValue(value=3))
item_bound_explicit = ItemBound[IntValue](item=IntValue(value=3))
item_no_bound_inferred = ItemNoBound(item=IntValue(value=3))
item_no_bound_explicit = ItemNoBound[IntValue](item=IntValue(value=3))

# calling `print(x.model_dump())` on any of the above instances results in the following:
#> {'item': {'value': 3}}
```

However, if [constraints](https://typing.readthedocs.io/en/latest/reference/generics.html#type-variables-with-constraints)
or a default value (as per [PEP 696](https://peps.python.org/pep-0696/)) is being used, then the default type or constraints
will be used for both validation and serialization if the type variable is not parametrized. You can override this behavior
using [`SerializeAsAny`](./serialization.md#serializeasany-annotation):

```python
from typing import Generic

from typing_extensions import TypeVar

from pydantic import BaseModel, SerializeAsAny


class ErrorDetails(BaseModel):
    foo: str


ErrorDataT = TypeVar('ErrorDataT', default=ErrorDetails)


class Error(BaseModel, Generic[ErrorDataT]):
    message: str
    details: ErrorDataT


class MyErrorDetails(ErrorDetails):
    bar: str


# serialized using the default's serializer
error = Error(
    message='We just had an error',
    details=MyErrorDetails(foo='var', bar='var2'),
)
assert error.model_dump() == {
    'message': 'We just had an error',
    'details': {
        'foo': 'var',
    },
}
# If `ErrorDataT` was using an upper bound, `bar` would be present in `details`.


class SerializeAsAnyError(BaseModel, Generic[ErrorDataT]):
    message: str
    details: SerializeAsAny[ErrorDataT]


# serialized as Any
error = SerializeAsAnyError(
    message='We just had an error',
    details=MyErrorDetails(foo='var', bar='baz'),
)
assert error.model_dump() == {
    'message': 'We just had an error',
    'details': {
        'foo': 'var',
        'bar': 'baz',
    },
}
```

## Dynamic model creation

??? api "API Documentation"
    [`pydantic.main.create_model`][pydantic.main.create_model]<br>

There are some occasions where it is desirable to create a model using runtime information to specify the fields.
Pydantic provides the [`create_model()`][pydantic.create_model] function to allow models to be created dynamically:

```python
from pydantic import BaseModel, create_model

DynamicFoobarModel = create_model('DynamicFoobarModel', foo=str, bar=(int, 123))

# Equivalent to:


class StaticFoobarModel(BaseModel):
    foo: str
    bar: int = 123
```

Field definitions are specified as keyword arguments, and should either be:

* A single element, representing the type annotation of the field.
* A two-tuple, the first element being the type and the second element the assigned value
  (either a default or the [`Field()`][pydantic.Field] function).

Here is a more advanced example:

```python
from typing import Annotated

from pydantic import BaseModel, Field, PrivateAttr, create_model

DynamicModel = create_model(
    'DynamicModel',
    foo=(str, Field(alias='FOO')),
    bar=Annotated[str, Field(description='Bar field')],
    _private=(int, PrivateAttr(default=1)),
)


class StaticModel(BaseModel):
    foo: str = Field(alias='FOO')
    bar: Annotated[str, Field(description='Bar field')]
    _private: int = PrivateAttr(default=1)
```

The special keyword arguments `__config__` and `__base__` can be used to customize the new model.
This includes extending a base model with extra fields.

```python
from pydantic import BaseModel, create_model


class FooModel(BaseModel):
    foo: str
    bar: int = 123


BarModel = create_model(
    'BarModel',
    apple=(str, 'russet'),
    banana=(str, 'yellow'),
    __base__=FooModel,
)
print(BarModel)
#> <class '__main__.BarModel'>
print(BarModel.model_fields.keys())
#> dict_keys(['foo', 'bar', 'apple', 'banana'])
```

You can also add validators by passing a dictionary to the `__validators__` argument.

```python {rewrite_assert="false"}
from pydantic import ValidationError, create_model, field_validator


def alphanum(cls, v):
    assert v.isalnum(), 'must be alphanumeric'
    return v


validators = {
    'username_validator': field_validator('username')(alphanum)  # (1)!
}

UserModel = create_model(
    'UserModel', username=(str, ...), __validators__=validators
)

user = UserModel(username='scolvin')
print(user)
#> username='scolvin'

try:
    UserModel(username='scolvi%n')
except ValidationError as e:
    print(e)
    """
    1 validation error for UserModel
    username
      Assertion failed, must be alphanumeric [type=assertion_error, input_value='scolvi%n', input_type=str]
    """
```

1. Make sure that the validators names do not clash with any of the field names as
   internally, Pydantic gathers all members into a namespace and mimics the normal
   creation of a class using the [`types` module utilities](https://docs.python.org/3/library/types.html#dynamic-type-creation).

!!! note
    To pickle a dynamically created model:

    * the model must be defined globally
    * the `__module__` argument must be provided

## `RootModel` and custom root types

??? api "API Documentation"
    [`pydantic.root_model.RootModel`][pydantic.root_model.RootModel]<br>

Pydantic models can be defined with a "custom root type" by subclassing [`pydantic.RootModel`][pydantic.RootModel].

The root type can be any type supported by Pydantic, and is specified by the generic parameter to `RootModel`.
The root value can be passed to the model `__init__` or [`model_validate`][pydantic.main.BaseModel.model_validate]
via the first and only argument.

Here's an example of how this works:

```python
from pydantic import RootModel

Pets = RootModel[list[str]]
PetsByName = RootModel[dict[str, str]]


print(Pets(['dog', 'cat']))
#> root=['dog', 'cat']
print(Pets(['dog', 'cat']).model_dump_json())
#> ["dog","cat"]
print(Pets.model_validate(['dog', 'cat']))
#> root=['dog', 'cat']
print(Pets.model_json_schema())
"""
{'items': {'type': 'string'}, 'title': 'RootModel[list[str]]', 'type': 'array'}
"""

print(PetsByName({'Otis': 'dog', 'Milo': 'cat'}))
#> root={'Otis': 'dog', 'Milo': 'cat'}
print(PetsByName({'Otis': 'dog', 'Milo': 'cat'}).model_dump_json())
#> {"Otis":"dog","Milo":"cat"}
print(PetsByName.model_validate({'Otis': 'dog', 'Milo': 'cat'}))
#> root={'Otis': 'dog', 'Milo': 'cat'}
```

If you want to access items in the `root` field directly or to iterate over the items, you can implement
custom `__iter__` and `__getitem__` functions, as shown in the following example.

```python
from pydantic import RootModel


class Pets(RootModel):
    root: list[str]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


pets = Pets.model_validate(['dog', 'cat'])
print(pets[0])
#> dog
print([pet for pet in pets])
#> ['dog', 'cat']
```

You can also create subclasses of the parametrized root model directly:

```python
from pydantic import RootModel


class Pets(RootModel[list[str]]):
    def describe(self) -> str:
        return f'Pets: {", ".join(self.root)}'


my_pets = Pets.model_validate(['dog', 'cat'])

print(my_pets.describe())
#> Pets: dog, cat
```

## Faux immutability

Models can be configured to be immutable via `model_config['frozen'] = True`. When this is set, attempting to change the
values of instance attributes will raise errors. See the [API reference][pydantic.config.ConfigDict.frozen] for more details.

!!! note
    This behavior was achieved in Pydantic V1 via the config setting `allow_mutation = False`.
    This config flag is deprecated in Pydantic V2, and has been replaced with `frozen`.

!!! warning
    In Python, immutability is not enforced. Developers have the ability to modify objects
    that are conventionally considered "immutable" if they choose to do so.

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class FooBarModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    a: str
    b: dict


foobar = FooBarModel(a='hello', b={'apple': 'pear'})

try:
    foobar.a = 'different'
except ValidationError as e:
    print(e)
    """
    1 validation error for FooBarModel
    a
      Instance is frozen [type=frozen_instance, input_value='different', input_type=str]
    """

print(foobar.a)
#> hello
print(foobar.b)
#> {'apple': 'pear'}
foobar.b['apple'] = 'grape'
print(foobar.b)
#> {'apple': 'grape'}
```

Trying to change `a` caused an error, and `a` remains unchanged. However, the dict `b` is mutable, and the
immutability of `foobar` doesn't stop `b` from being changed.

## Abstract base classes

Pydantic models can be used alongside Python's
[Abstract Base Classes](https://docs.python.org/3/library/abc.html) (ABCs).

```python
import abc

from pydantic import BaseModel


class FooBarModel(BaseModel, abc.ABC):
    a: str
    b: int

    @abc.abstractmethod
    def my_abstract_method(self):
        pass
```

## Field ordering

Field order affects models in the following ways:

* field order is preserved in the model [JSON Schema](json_schema.md)
* field order is preserved in [validation errors](#error-handling)
* field order is preserved when [serializing data](serialization.md#serializing-data)

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    a: int
    b: int = 2
    c: int = 1
    d: int = 0
    e: float


print(Model.model_fields.keys())
#> dict_keys(['a', 'b', 'c', 'd', 'e'])
m = Model(e=2, a=1)
print(m.model_dump())
#> {'a': 1, 'b': 2, 'c': 1, 'd': 0, 'e': 2.0}
try:
    Model(a='x', b='x', c='x', d='x', e='x')
except ValidationError as err:
    error_locations = [e['loc'] for e in err.errors()]

print(error_locations)
#> [('a',), ('b',), ('c',), ('d',), ('e',)]
```

## Automatically excluded attributes

### Class variables

Attributes annotated with [`ClassVar`][typing.ClassVar] are properly treated by Pydantic as class variables, and will not
become fields on model instances:

```python
from typing import ClassVar

from pydantic import BaseModel


class Model(BaseModel):
    x: ClassVar[int] = 1

    y: int = 2


m = Model()
print(m)
#> y=2
print(Model.x)
#> 1
```

### Private model attributes

??? api "API Documentation"
    [`pydantic.fields.PrivateAttr`][pydantic.fields.PrivateAttr]<br>

Attributes whose name has a leading underscore are not treated as fields by Pydantic, and are not included in the
model schema. Instead, these are converted into a "private attribute" which is not validated or even set during
calls to `__init__`, `model_validate`, etc.

Here is an example of usage:

```python
from datetime import datetime
from random import randint
from typing import Any

from pydantic import BaseModel, PrivateAttr


class TimeAwareModel(BaseModel):
    _processed_at: datetime = PrivateAttr(default_factory=datetime.now)
    _secret_value: str

    def model_post_init(self, context: Any) -> None:
        # this could also be done with `default_factory`:
        self._secret_value = randint(1, 5)


m = TimeAwareModel()
print(m._processed_at)
#> 2032-01-02 03:04:05.000006
print(m._secret_value)
#> 3
```

Private attribute names must start with underscore to prevent conflicts with model fields. However, dunder names
(such as `__attr__`) are not supported, and will be completely ignored from the model definition.

## Model signature

All Pydantic models will have their signature generated based on their fields:

```python
import inspect

from pydantic import BaseModel, Field


class FooModel(BaseModel):
    id: int
    name: str = None
    description: str = 'Foo'
    apple: int = Field(alias='pear')


print(inspect.signature(FooModel))
#> (*, id: int, name: str = None, description: str = 'Foo', pear: int) -> None
```

An accurate signature is useful for introspection purposes and libraries like `FastAPI` or `hypothesis`.

The generated signature will also respect custom `__init__` functions:

```python
import inspect

from pydantic import BaseModel


class MyModel(BaseModel):
    id: int
    info: str = 'Foo'

    def __init__(self, id: int = 1, *, bar: str, **data) -> None:
        """My custom init!"""
        super().__init__(id=id, bar=bar, **data)


print(inspect.signature(MyModel))
#> (id: int = 1, *, bar: str, info: str = 'Foo') -> None
```

To be included in the signature, a field's alias or name must be a valid Python identifier.
Pydantic will prioritize a field's alias over its name when generating the signature, but may use the field name if the
alias is not a valid Python identifier.

If a field's alias and name are *both* not valid identifiers (which may be possible through exotic use of `create_model`),
a `**data` argument will be added. In addition, the `**data` argument will always be present in the signature if
`model_config['extra'] == 'allow'`.

## Structural pattern matching

Pydantic supports structural pattern matching for models, as introduced by [PEP 636](https://peps.python.org/pep-0636/) in Python 3.10.

```python {requires="3.10" lint="skip"}
from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    species: str


a = Pet(name='Bones', species='dog')

match a:
    # match `species` to 'dog', declare and initialize `dog_name`
    case Pet(species='dog', name=dog_name):
        print(f'{dog_name} is a dog')
#> Bones is a dog
    # default case
    case _:
        print('No dog matched')
```

!!! note
    A match-case statement may seem as if it creates a new model, but don't be fooled;
    it is just syntactic sugar for getting an attribute and either comparing it or declaring and initializing it.

## Attribute copies

In many cases, arguments passed to the constructor will be copied in order to perform validation and, where necessary,
coercion.

In this example, note that the ID of the list changes after the class is constructed because it has been
copied during validation:

```python
from pydantic import BaseModel


class C1:
    arr = []

    def __init__(self, in_arr):
        self.arr = in_arr


class C2(BaseModel):
    arr: list[int]


arr_orig = [1, 9, 10, 3]


c1 = C1(arr_orig)
c2 = C2(arr=arr_orig)
print(f'{id(c1.arr) == id(c2.arr)=}')
#> id(c1.arr) == id(c2.arr)=False
```

!!! note
    There are some situations where Pydantic does not copy attributes, such as when passing models &mdash; we use the
    model as is. You can override this behaviour by setting
    [`model_config['revalidate_instances'] = 'always'`](../api/config.md#pydantic.config.ConfigDict).
````

## File: docs/concepts/performance.md
````markdown
# Performance tips

In most cases Pydantic won't be your bottle neck, only follow this if you're sure it's necessary.

## In general, use `model_validate_json()` not `model_validate(json.loads(...))`

On `model_validate(json.loads(...))`, the JSON is parsed in Python, then converted to a dict, then it's validated internally.
On the other hand, `model_validate_json()` already performs the validation internally.

There are a few cases where `model_validate(json.loads(...))` may be faster. Specifically, when using a `'before'` or `'wrap'` validator
on a model, validation may be faster with the two step method. You can read more about these special cases in
[this discussion](https://github.com/pydantic/pydantic/discussions/6388#discussioncomment-8193105).

Many performance improvements are currently in the works for `pydantic-core`, as discussed
[here](https://github.com/pydantic/pydantic/discussions/6388#discussioncomment-8194048). Once these changes are merged, we should be at
the point where `model_validate_json()` is always faster than `model_validate(json.loads(...))`.

## `TypeAdapter` instantiated once

The idea here is to avoid constructing validators and serializers more than necessary. Each time a `TypeAdapter` is instantiated,
it will construct a new validator and serializer. If you're using a `TypeAdapter` in a function, it will be instantiated each time
the function is called. Instead, instantiate it once, and reuse it.

=== ":x: Bad"

    ```python {lint="skip"}
    from pydantic import TypeAdapter


    def my_func():
        adapter = TypeAdapter(list[int])
        # do something with adapter
    ```

=== ":white_check_mark: Good"

    ```python {lint="skip"}
    from pydantic import TypeAdapter

    adapter = TypeAdapter(list[int])

    def my_func():
        ...
        # do something with adapter
    ```

## `Sequence` vs `list` or `tuple` with `Mapping` vs `dict`

When using `Sequence`, Pydantic calls `isinstance(value, Sequence)` to check if the value is a sequence.
Also, Pydantic will try to validate against different types of sequences, like `list` and `tuple`.
If you know the value is a `list` or `tuple`, use `list` or `tuple` instead of `Sequence`.

The same applies to `Mapping` and `dict`.
If you know the value is a `dict`, use `dict` instead of `Mapping`.

## Don't do validation when you don't have to, use `Any` to keep the value unchanged

If you don't need to validate a value, use `Any` to keep the value unchanged.

```python
from typing import Any

from pydantic import BaseModel


class Model(BaseModel):
    a: Any


model = Model(a=1)
```

## Avoid extra information via subclasses of primitives

=== "Don't do this"

    ```python
    class CompletedStr(str):
        def __init__(self, s: str):
            self.s = s
            self.done = False
    ```

=== "Do this"

    ```python
    from pydantic import BaseModel


    class CompletedModel(BaseModel):
        s: str
        done: bool = False
    ```

## Use tagged union, not union

Tagged union (or discriminated union) is a union with a field that indicates which type it is.

```python {test="skip"}
from typing import Any, Literal

from pydantic import BaseModel, Field


class DivModel(BaseModel):
    el_type: Literal['div'] = 'div'
    class_name: str | None = None
    children: list[Any] | None = None


class SpanModel(BaseModel):
    el_type: Literal['span'] = 'span'
    class_name: str | None = None
    contents: str | None = None


class ButtonModel(BaseModel):
    el_type: Literal['button'] = 'button'
    class_name: str | None = None
    contents: str | None = None


class InputModel(BaseModel):
    el_type: Literal['input'] = 'input'
    class_name: str | None = None
    value: str | None = None


class Html(BaseModel):
    contents: DivModel | SpanModel | ButtonModel | InputModel = Field(
        discriminator='el_type'
    )
```

See [Discriminated Unions] for more details.

## Use `TypedDict` over nested models

Instead of using nested models, use `TypedDict` to define the structure of the data.

??? info "Performance comparison"
    With a simple benchmark, `TypedDict` is about ~2.5x faster than nested models:

    ```python {test="skip"}
    from timeit import timeit

    from typing_extensions import TypedDict

    from pydantic import BaseModel, TypeAdapter


    class A(TypedDict):
        a: str
        b: int


    class TypedModel(TypedDict):
        a: A


    class B(BaseModel):
        a: str
        b: int


    class Model(BaseModel):
        b: B


    ta = TypeAdapter(TypedModel)
    result1 = timeit(
        lambda: ta.validate_python({'a': {'a': 'a', 'b': 2}}), number=10000
    )
    result2 = timeit(
        lambda: Model.model_validate({'b': {'a': 'a', 'b': 2}}), number=10000
    )
    print(result2 / result1)
    ```

## Avoid wrap validators if you really care about performance

Wrap validators are generally slower than other validators. This is because they require
that data is materialized in Python during validation. Wrap validators can be incredibly useful
for complex validation logic, but if you're looking for the best performance, you should avoid them.

## Failing early with `FailFast`

Starting in v2.8+, you can apply the `FailFast` annotation to sequence types to fail early if any item in the sequence fails validation.
If you use this annotation, you won't get validation errors for the rest of the items in the sequence if one fails, so you're effectively
trading off visibility for performance.

```python
from typing import Annotated

from pydantic import FailFast, TypeAdapter, ValidationError

ta = TypeAdapter(Annotated[list[bool], FailFast()])
try:
    ta.validate_python([True, 'invalid', False, 'also invalid'])
except ValidationError as exc:
    print(exc)
    """
    1 validation error for list[bool]
    1
      Input should be a valid boolean, unable to interpret input [type=bool_parsing, input_value='invalid', input_type=str]
    """
```

Read more about `FailFast` [here][pydantic.types.FailFast].

[Discriminated Unions]: ../concepts/unions.md#discriminated-unions
````

## File: docs/concepts/pydantic_settings.md
````markdown
---
description: Support for loading a settings or config class from environment variables or secrets files.
---

# Settings Management

[Pydantic Settings](https://github.com/pydantic/pydantic-settings) provides optional Pydantic features for loading a settings or config class from environment variables or secrets files.

{{ pydantic_settings }}
````

## File: docs/concepts/serialization.md
````markdown
Beyond accessing model attributes directly via their field names (e.g. `model.foobar`), models can be converted, dumped,
serialized, and exported in a number of ways. Serialization can be customized for the whole model, or on a per-field
or per-type basis.

??? abstract "Serialize versus dump"
    Pydantic uses the terms "serialize" and "dump" interchangeably. Both refer to the process of converting a model to a
    dictionary or JSON-encoded string.

    Outside of Pydantic, the word "serialize" usually refers to converting in-memory data into a string or bytes.
    However, in the context of Pydantic, there is a very close relationship between converting an object from a more
    structured form &mdash; such as a Pydantic model, a dataclass, etc. &mdash; into a less structured form comprised of
    Python built-ins such as dict.

    While we could (and on occasion, do) distinguish between these scenarios by using the word "dump" when converting to
    primitives and "serialize" when converting to string, for practical purposes, we frequently use the word "serialize"
    to refer to both of these situations, even though it does not always imply conversion to a string or bytes.

!!! tip
    Want to quickly jump to the relevant serializer section?

    <div class="grid cards" markdown>

    *   Field serializer

        ---

        * [field *plain* serializer](#field-plain-serializer)
        * [field *wrap* serializer](#field-wrap-serializer)

    *   Model serializer

        ---

        * [model *plain* serializer](#model-plain-serializer)
        * [model *wrap* serializer](#model-wrap-serializer)

    </div>

## Serializing data

Pydantic allows models (and any other type using [type adapters](./type_adapter.md)) to be serialized in *two* modes:
[Python](#python-mode) and [JSON](#json-mode). The Python output may contain non-JSON serializable data (although this
can be emulated).

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#modelmodel_dump}

### Python mode

When using the Python mode, Pydantic models (and model-like types such as [dataclasses][]) (1) will be (recursively) converted to dictionaries. This is achievable by using the [`model_dump()`][pydantic.BaseModel.model_dump] method:
{ .annotate }

1. With the exception of [root models](./models.md#rootmodel-and-custom-root-types), where the root value is dumped directly.

```python {group="python-dump"}
from typing import Optional

from pydantic import BaseModel, Field


class BarModel(BaseModel):
    whatever: tuple[int, ...]


class FooBarModel(BaseModel):
    banana: Optional[float] = 1.1
    foo: str = Field(serialization_alias='foo_alias')
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': (1, 2)})

# returns a dictionary:
print(m.model_dump())
#> {'banana': 3.14, 'foo': 'hello', 'bar': {'whatever': (1, 2)}}

print(m.model_dump(by_alias=True))
#> {'banana': 3.14, 'foo_alias': 'hello', 'bar': {'whatever': (1, 2)}}
```

Notice that the value of `whatever` was dumped as tuple, which isn't a known JSON type. The `mode` argument can be set to `'json'`
to ensure JSON-compatible types are used:

```python {group="python-dump"}
print(m.model_dump(mode='json'))
#> {'banana': 3.14, 'foo': 'hello', 'bar': {'whatever': [1, 2]}}
```

!!! info "See also"
    The [`TypeAdapter.dump_python()`][pydantic.TypeAdapter.dump_python] method, useful when *not* dealing with Pydantic models.

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#modelmodel_dump_json}

### JSON mode

Pydantic allows data to be serialized directly to a JSON-encoded string, by trying its best to convert Python values to valid
JSON data. This is achievable by using the [`model_dump_json()`][pydantic.BaseModel.model_dump_json] method:

```python
from datetime import datetime

from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: tuple[int, ...]


class FooBarModel(BaseModel):
    foo: datetime
    bar: BarModel


m = FooBarModel(foo=datetime(2032, 6, 1, 12, 13, 14), bar={'whatever': (1, 2)})

print(m.model_dump_json(indent=2))
"""
{
  "foo": "2032-06-01T12:13:14",
  "bar": {
    "whatever": [
      1,
      2
    ]
  }
}
"""
```

In addition to the [supported types][json.JSONEncoder] by the standard library [`json`][] module, Pydantic supports a wide
variety of types ([date and time types][datetime], [`UUID`][uuid.UUID] objects, [sets][set], etc). If an unsupported type
is used and can't be serialized to JSON, a [`PydanticSerializationError`][pydantic_core.PydanticSerializationError] exception
is raised.

!!! info "See also"
    The [`TypeAdapter.dump_json()`][pydantic.TypeAdapter.dump_json] method, useful when *not* dealing with Pydantic models.

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#dictmodel-and-iteration}

## Iterating over models

Pydantic models can also be iterated over, yielding `(field_name, field_value)` pairs. Note that field values
are left as is, so sub-models will *not* be converted to dictionaries:

```python {group="iterating-model"}
from pydantic import BaseModel


class BarModel(BaseModel):
    whatever: int


class FooBarModel(BaseModel):
    banana: float
    foo: str
    bar: BarModel


m = FooBarModel(banana=3.14, foo='hello', bar={'whatever': 123})

for name, value in m:
    print(f'{name}: {value}')
    #> banana: 3.14
    #> foo: hello
    #> bar: whatever=123
```

This means that calling [`dict()`][dict] on a model can be used to construct a dictionary of the model:

```python {group="iterating-model"}
print(dict(m))
#> {'banana': 3.14, 'foo': 'hello', 'bar': BarModel(whatever=123)}
```

!!! note
    [Root models](models.md#rootmodel-and-custom-root-types) *does* get converted to a dictionary with the key `'root'`.

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#pickledumpsmodel}

## Pickling support

Pydantic models support efficient pickling and unpickling.

<!-- TODO need to get pickling doctest to work -->
```python {test="skip"}
import pickle

from pydantic import BaseModel


class FooBarModel(BaseModel):
    a: str
    b: int


m = FooBarModel(a='hello', b=123)
print(m)
#> a='hello' b=123
data = pickle.dumps(m)
print(data[:20])
#> b'\x80\x04\x95\x95\x00\x00\x00\x00\x00\x00\x00\x8c\x08__main_'
m2 = pickle.loads(data)
print(m2)
#> a='hello' b=123
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#custom-serializers}

## Serializers

Similar to [custom validators](./validators.md), you can leverage custom serializers at the field and model levels to further
control the serialization behavior.

!!! warning
    Only *one* serializer can be defined per field/model. It is not possible to combine multiple serializers together
    (including *plain* and *wrap* serializers).

### Field serializers

??? api "API Documentation"
    [`pydantic.functional_serializers.PlainSerializer`][pydantic.functional_serializers.PlainSerializer]<br>
    [`pydantic.functional_serializers.WrapSerializer`][pydantic.functional_serializers.WrapSerializer]<br>
    [`pydantic.functional_serializers.field_serializer`][pydantic.functional_serializers.field_serializer]<br>

In its simplest form, a field serializer is a callable taking the value to be serialized as an argument and
**returning the serialized value**.

If the `return_type` argument is provided to the serializer (or if a return type annotation is available on the serializer function),
it will be used to build an extra serializer, to ensure that the serialized field value complies with this return type.

**Two** different types of serializers can be used. They can all be defined using the
[annotated pattern](./fields.md#the-annotated-pattern) or using the
[`@field_serializer`][pydantic.field_serializer] decorator, applied on instance or [static methods][staticmethod].

* ***Plain* serializers**: are called unconditionally to serialize a field. The serialization logic for types supported
  by Pydantic will *not* be called. Using such serializers is also useful to specify the logic for arbitrary types.
  {#field-plain-serializer}

    === "Annotated pattern"

        ```python
        from typing import Annotated, Any

        from pydantic import BaseModel, PlainSerializer


        def ser_number(value: Any) -> Any:
            if isinstance(value, int):
                return value * 2
            else:
                return value


        class Model(BaseModel):
            number: Annotated[int, PlainSerializer(ser_number)]


        print(Model(number=4).model_dump())
        #> {'number': 8}
        m = Model(number=1)
        m.number = 'invalid'
        print(m.model_dump())  # (1)!
        #> {'number': 'invalid'}
        ```

        1. Pydantic will *not* validate that the serialized value complies with the `int` type.

    === "Decorator"

        ```python
        from typing import Any

        from pydantic import BaseModel, field_serializer


        class Model(BaseModel):
            number: int

            @field_serializer('number', mode='plain')  # (1)!
            def ser_number(self, value: Any) -> Any:
                if isinstance(value, int):
                    return value * 2
                else:
                    return value


        print(Model(number=4).model_dump())
        #> {'number': 8}
        m = Model(number=1)
        m.number = 'invalid'
        print(m.model_dump())  # (2)!
        #> {'number': 'invalid'}
        ```

        1. `'plain'` is the default mode for the decorator, and can be omitted.
        2. Pydantic will *not* validate that the serialized value complies with the `int` type.

* ***Wrap* serializers**: give more flexibility to customize the serialization behavior. You can run code before or after
  the Pydantic serialization logic.
  {#field-wrap-serializer}

    Such serializers must be defined with a **mandatory** extra *handler* parameter: a callable taking the value to be serialized
    as an argument. Internally, this handler will delegate serialization of the value to Pydantic. You are free to *not* call the
    handler at all.

    === "Annotated pattern"

        ```python
        from typing import Annotated, Any

        from pydantic import BaseModel, SerializerFunctionWrapHandler, WrapSerializer


        def ser_number(value: Any, handler: SerializerFunctionWrapHandler) -> int:
            return handler(value) + 1


        class Model(BaseModel):
            number: Annotated[int, WrapSerializer(ser_number)]


        print(Model(number=4).model_dump())
        #> {'number': 5}
        ```

    === "Decorator"

        ```python
        from typing import Any

        from pydantic import BaseModel, SerializerFunctionWrapHandler, field_serializer


        class Model(BaseModel):
            number: int

            @field_serializer('number', mode='wrap')
            def ser_number(
                self, value: Any, handler: SerializerFunctionWrapHandler
            ) -> int:
                return handler(value) + 1


        print(Model(number=4).model_dump())
        #> {'number': 5}
        ```

<!-- Note: keep this section updated with [the validator one](./validators.md#which-validator-pattern-to-use) -->

#### Which serializer pattern to use

While both approaches can achieve the same thing, each pattern provides different benefits.

##### Using the annotated pattern

One of the key benefits of using the [annotated pattern](./fields.md#the-annotated-pattern) is to make
serializers reusable:

```python
from typing import Annotated

from pydantic import BaseModel, Field, PlainSerializer

DoubleNumber = Annotated[int, PlainSerializer(lambda v: v * 2)]


class Model1(BaseModel):
    my_number: DoubleNumber


class Model2(BaseModel):
    other_number: Annotated[DoubleNumber, Field(description='My other number')]


class Model3(BaseModel):
    list_of_even_numbers: list[DoubleNumber]  # (1)!
```

1. As mentioned in the [annotated pattern](./fields.md#the-annotated-pattern) documentation,
   we can also make use of serializers for specific parts of the annotation (in this case,
   serialization is applied for list items, but not the whole list).

It is also easier to understand which serializers are applied to a type, by just looking at the field annotation.

##### Using the decorator pattern

One of the key benefits of using the [`@field_serializer`][pydantic.field_serializer] decorator is to apply
the function to multiple fields:

```python
from pydantic import BaseModel, field_serializer


class Model(BaseModel):
    f1: str
    f2: str

    @field_serializer('f1', 'f2', mode='plain')
    def capitalize(self, value: str) -> str:
        return value.capitalize()
```

Here are a couple additional notes about the decorator usage:

* If you want the serializer to apply to all fields (including the ones defined in subclasses), you can pass
  `'*'` as the field name argument.
* By default, the decorator will ensure the provided field name(s) are defined on the model. If you want to
  disable this check during class creation, you can do so by passing `False` to the `check_fields` argument.
  This is useful when the field serializer is defined on a base class, and the field is expected to exist on
  subclasses.

### Model serializers

??? api "API Documentation"
    [`pydantic.functional_serializers.model_serializer`][pydantic.functional_serializers.model_serializer]<br>

Serialization can also be customized on the entire model using the [`@model_serializer`][pydantic.model_serializer]
decorator.

If the `return_type` argument is provided to the [`@model_serializer`][pydantic.model_serializer] decorator
(or if a return type annotation is available on the serializer function), it will be used to build an extra serializer,
to ensure that the serialized model value complies with this return type.

As with [field serializers](#field-serializers), **two** different types of model serializers can be used:

* ***Plain* serializers**: are called unconditionally to serialize the model.
  {#model-plain-serializer}

    ```python
    from pydantic import BaseModel, model_serializer


    class UserModel(BaseModel):
        username: str
        password: str

        @model_serializer(mode='plain')  # (1)!
        def serialize_model(self) -> str:  # (2)!
            return f'{self.username} - {self.password}'


    print(UserModel(username='foo', password='bar').model_dump())
    #> foo - bar
    ```

      1. `'plain'` is the default mode for the decorator, and can be omitted.
      2. You are free to return a value that *isn't* a dictionary.

* ***Wrap* serializers**: give more flexibility to customize the serialization behavior. You can run code before or after
  the Pydantic serialization logic.
  {#model-wrap-serializer}

    Such serializers must be defined with a **mandatory** extra *handler* parameter: a callable taking the instance of the model
    as an argument. Internally, this handler will delegate serialization of the model to Pydantic. You are free to *not* call the
    handler at all.

      ```python
      from pydantic import BaseModel, SerializerFunctionWrapHandler, model_serializer


      class UserModel(BaseModel):
          username: str
          password: str

          @model_serializer(mode='wrap')
          def serialize_model(
              self, handler: SerializerFunctionWrapHandler
          ) -> dict[str, object]:
              serialized = handler(self)
              serialized['fields'] = list(serialized)
              return serialized


      print(UserModel(username='foo', password='bar').model_dump())
      #> {'username': 'foo', 'password': 'bar', 'fields': ['username', 'password']}
      ```

## Serialization info

Both the field and model serializers callables (in all modes) can optionally take an extra `info` argument,
providing useful extra information, such as:

* [user defined context](#serialization-context)
* the current serialization mode: either `'python'` or `'json'` (see the [`mode`][pydantic.SerializationInfo.mode] property)
* the various parameters set during serialization using the [serialization methods](#serializing-data)
  (e.g. [`exclude_unset`][pydantic.SerializationInfo.exclude_unset], [`serialize_as_any`][pydantic.SerializationInfo.serialize_as_any])
* the current field name, if using a [field serializer](#field-serializers) (see the
  [`field_name`][pydantic.FieldSerializationInfo.field_name] property).

### Serialization context

You can pass a context object to the [serialization methods](#serializing-data), which can be accessed
inside the serializer functions using the [`context`][pydantic.SerializationInfo.context] property:

```python
from pydantic import BaseModel, FieldSerializationInfo, field_serializer


class Model(BaseModel):
    text: str

    @field_serializer('text', mode='plain')
    @classmethod
    def remove_stopwords(cls, v: str, info: FieldSerializationInfo) -> str:
        if isinstance(info.context, dict):
            stopwords = info.context.get('stopwords', set())
            v = ' '.join(w for w in v.split() if w.lower() not in stopwords)
        return v


model = Model(text='This is an example document')
print(model.model_dump())  # no context
#> {'text': 'This is an example document'}
print(model.model_dump(context={'stopwords': ['this', 'is', 'an']}))
#> {'text': 'example document'}
```

Similarly, you can [use a context for validation](../concepts/validators.md#validation-context).

## Serializing subclasses

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#subclasses-of-standard-types}

### Subclasses of supported types

Subclasses of supported types are serialized according to their super class:

```python
from datetime import date

from pydantic import BaseModel


class MyDate(date):
    @property
    def my_date_format(self) -> str:
        return self.strftime('%d/%m/%Y')


class FooModel(BaseModel):
    date: date


m = FooModel(date=MyDate(2023, 1, 1))
print(m.model_dump_json())
#> {"date":"2023-01-01"}
```

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#subclass-instances-for-fields-of-basemodel-dataclasses-typeddict}

### Subclasses of model-like types

When using model-like classes (Pydantic models, dataclasses, etc.) as field annotations, the default behavior is to
serializer the field value as though it was an instance of the class, even if it is a subclass. More specifically,
only the fields declared on the type annotation will be included in the serialization result:

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str


class UserLogin(User):
    password: str


class OuterModel(BaseModel):
    user: User


user = UserLogin(name='pydantic', password='hunter2')

m = OuterModel(user=user)
print(m)
#> user=UserLogin(name='pydantic', password='hunter2')
print(m.model_dump())  # (1)!
#> {'user': {'name': 'pydantic'}}
```

1. Note: the password field is not included

!!! warning "Migration Warning"
    This behavior is different from how things worked in Pydantic V1, where we would always include
    all (subclass) fields when recursively serializing models to dictionaries. The motivation behind this change
    in behavior is that it helps ensure that you know precisely which fields could be included when serializing,
    even if subclasses get passed when instantiating the object. In particular, this can help prevent surprises
    when adding sensitive information like secrets as fields of subclasses. To enable the old V1 behavior, refer
    to the next section.

### Serializing with duck typing 🦆

Duck typing serialization is the behavior of serializing a model instance based on the actual field values, rather
than the field definitions. This means that for a field annotated with a model-like class, all the fields present
in subclasses of such class will be included in the serialized output.

This behavior can be configured at the field level and at runtime, for a specific serialization call:

* Field level: use the [`SerializeAsAny`][pydantic.functional_serializers.SerializeAsAny] annotation.
* Runtime level: use the `serialize_as_any` argument when calling the [serialization methods](#serializing-data).

We discuss these options below in more detail:

#### `SerializeAsAny` annotation

If you want duck typing serialization behavior, this can be done using the
[`SerializeAsAny`][pydantic.functional_serializers.SerializeAsAny] annotation
on a type:

```python
from pydantic import BaseModel, SerializeAsAny


class User(BaseModel):
    name: str


class UserLogin(User):
    password: str


class OuterModel(BaseModel):
    as_any: SerializeAsAny[User]
    as_user: User


user = UserLogin(name='pydantic', password='password')

print(OuterModel(as_any=user, as_user=user).model_dump())
"""
{
    'as_any': {'name': 'pydantic', 'password': 'password'},
    'as_user': {'name': 'pydantic'},
}
"""
```

When a type is annotated as `SerializeAsAny[<type>]`, the validation behavior will be the same as if it was
annotated as `<type>`, and static type checkers will treat the annotation as if it was simply `<type>`.
When serializing, the field will be serialized as though the type hint for the field was [`Any`][typing.Any],
which is where the name comes from.

#### `serialize_as_any` runtime setting

The `serialize_as_any` runtime setting can be used to serialize model data with or without duck typed serialization behavior.
`serialize_as_any` can be passed as a keyword argument to the various [serialization methods](#serializing-data) (such as
[`model_dump()`][pydantic.BaseModel.model_dump] and [`model_dump_json()`][pydantic.BaseModel.model_dump_json] on Pydantic models).

```python
from pydantic import BaseModel


class User(BaseModel):
    name: str


class UserLogin(User):
    password: str


class OuterModel(BaseModel):
    user1: User
    user2: User


user = UserLogin(name='pydantic', password='password')

outer_model = OuterModel(user1=user, user2=user)
print(outer_model.model_dump(serialize_as_any=True))  # (1)!
"""
{
    'user1': {'name': 'pydantic', 'password': 'password'},
    'user2': {'name': 'pydantic', 'password': 'password'},
}
"""

print(outer_model.model_dump(serialize_as_any=False))  # (2)!
#> {'user1': {'name': 'pydantic'}, 'user2': {'name': 'pydantic'}}
```

1. With `serialize_as_any` set to `True`, the result matches that of V1.
2. With `serialize_as_any` set to `False` (the V2 default), fields present on the subclass,
   but not the base class, are not included in serialization.

<!-- old anchor added for backwards compatibility -->
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#advanced-include-and-exclude}
<!-- markdownlint-disable-next-line no-empty-links -->
[](){#model-and-field-level-include-and-exclude}

## Field inclusion and exclusion

For serialization, field inclusion and exclusion can be configured in two ways:

* at the field level, using the `exclude` and `exclude_if` parameters on [the `Field()` function](fields.md).
* using the various serialization parameters on the [serialization methods](#serializing-data).

### At the field level

At the field level, the `exclude` and `exclude_if` parameters can be used:

```python
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    id: int
    private_id: int = Field(exclude=True)
    value: int = Field(ge=0, exclude_if=lambda v: v == 0)


print(Transaction(id=1, private_id=2, value=0).model_dump())
#> {'id': 1}
```

Exclusion at the field level takes priority over the `include` serialization parameter described below.

### As parameters to the serialization methods

When using the [serialization methods](#serializing-data) (such as [`model_dump()`][pydantic.BaseModel.model_dump]),
several parameters can be used to exclude or include fields.

#### Excluding and including specific fields

Consider the following models:

```python {group="simple-exclude-include"}
from pydantic import BaseModel, Field, SecretStr


class User(BaseModel):
    id: int
    username: str
    password: SecretStr


class Transaction(BaseModel):
    id: str
    private_id: str = Field(exclude=True)
    user: User
    value: int


t = Transaction(
    id='1234567890',
    private_id='123',
    user=User(id=42, username='JohnDoe', password='hashedpassword'),
    value=9876543210,
)
```

The `exclude` parameter can be used to specify which fields should be excluded (including the others), and vice-versa
using the `include` parameter.

```python {group="simple-exclude-include"}
# using a set:
print(t.model_dump(exclude={'user', 'value'}))
#> {'id': '1234567890'}

# using a dictionary:
print(t.model_dump(exclude={'user': {'username', 'password'}, 'value': True}))
#> {'id': '1234567890', 'user': {'id': 42}}

# same configuration using `include`:
print(t.model_dump(include={'id': True, 'user': {'id'}}))
#> {'id': '1234567890', 'user': {'id': 42}}
```

Note that using `False` to *include* a field in `exclude` (or to *exclude* a field in `include`) is not supported.

It is also possible to exclude or include specific items from sequence and dictionaries:

```python {group="advanced-include-exclude"}
from pydantic import BaseModel


class Hobby(BaseModel):
    name: str
    info: str


class User(BaseModel):
    hobbies: list[Hobby]


user = User(
    hobbies=[
        Hobby(name='Programming', info='Writing code and stuff'),
        Hobby(name='Gaming', info='Hell Yeah!!!'),
    ],
)

print(user.model_dump(exclude={'hobbies': {-1: {'info'}}}))  # (1)!
"""
{
    'hobbies': [
        {'name': 'Programming', 'info': 'Writing code and stuff'},
        {'name': 'Gaming'},
    ]
}
"""
```

1. The equivalent call with `include` would be:

     ```python {lint="skip" group="advanced-include-exclude"}
     user.model_dump(
        include={'hobbies': {0: True, -1: {'name'}}}
     )
     ```

The special key `'__all__'` can be used to apply an exclusion/inclusion pattern to all members:

```python {group="advanced-include-exclude"}
print(user.model_dump(exclude={'hobbies': {'__all__': {'info'}}}))
#> {'hobbies': [{'name': 'Programming'}, {'name': 'Gaming'}]}
```

#### Excluding and including fields based on their value

When using the [serialization methods](#serializing-data), it is possible to exclude fields based on their value,
using the following parameters:

* `exclude_defaults`: Exclude all fields whose value compares equal to the default value
  (using the equality (`==`) comparison operator).
* `exclude_none`: Exclude all fields whose value is `None`.
* `exclude_unset`: Pydantic keeps track of fields that were *explicitly* set during instantiation (using the
  [`model_fields_set`][pydantic.BaseModel.model_fields_set] property). Using `exclude_unset`, any field that
  was not explicitly provided will be excluded:

    ```python {group="exclude-unset"}
    from pydantic import BaseModel


    class UserModel(BaseModel):
        name: str
        age: int = 18


    user = UserModel(name='John')
    print(user.model_fields_set)
    #> {'name'}

    print(user.model_dump(exclude_unset=True))
    #> {'name': 'John'}
    ```

    Note that altering a field *after* the instance has been created will remove it from the unset fields:

    ```python {group="exclude-unset"}
    user.age = 21

    print(user.model_dump(exclude_unset=True))
    #> {'name': 'John', 'age': 21}
    ```

    !!! tip
        The experimental [`MISSING` sentinel](./experimental.md#missing-sentinel) can be used as an alternative to `exclude_unset`.
        Any field with `MISSING` as a value is automatically excluded from the serialization output.
````

## File: docs/concepts/strict_mode.md
````markdown
??? api "API Documentation"
    [`pydantic.types.Strict`][pydantic.types.Strict]<br>

By default, Pydantic will attempt to coerce values to the desired type when possible.
For example, you can pass the string `"123"` as the input to an `int` field, and it will be converted to `123`.
This coercion behavior is useful in many scenarios — think: UUIDs, URL parameters, HTTP headers, environment variables,
user input, etc.

However, there are also situations where this is not desirable, and you want Pydantic to error instead of coercing data.

To better support this use case, Pydantic provides a "strict mode" that can be enabled on a per-model, per-field, or
even per-validation-call basis. When strict mode is enabled, Pydantic will be much less lenient when coercing data,
and will instead error if the data is not of the correct type.

Here is a brief example showing the difference between validation behavior in strict and the default/"lax" mode:

```python
from pydantic import BaseModel, ValidationError


class MyModel(BaseModel):
    x: int


print(MyModel.model_validate({'x': '123'}))  # lax mode
#> x=123

try:
    MyModel.model_validate({'x': '123'}, strict=True)  # strict mode
except ValidationError as exc:
    print(exc)
    """
    1 validation error for MyModel
    x
      Input should be a valid integer [type=int_type, input_value='123', input_type=str]
    """
```

There are various ways to get strict-mode validation while using Pydantic, which will be discussed in more detail below:

* [Passing `strict=True` to the validation methods](#strict-mode-in-method-calls), such as `BaseModel.model_validate`,
  `TypeAdapter.validate_python`, and similar for JSON
* [Using `Field(strict=True)`](#strict-mode-with-field) with fields of a `BaseModel`, `dataclass`, or `TypedDict`
* [Using `pydantic.types.Strict` as a type annotation](#strict-mode-with-annotated-strict) on a field
    * Pydantic provides some type aliases that are already annotated with `Strict`, such as `pydantic.types.StrictInt`
* [Using `ConfigDict(strict=True)`](#strict-mode-with-configdict)

## Type coercions in strict mode

For most types, when validating data from python in strict mode, only the instances of the exact types are accepted.
For example, when validating an `int` field, only instances of `int` are accepted; passing instances of `float` or `str`
will result in raising a `ValidationError`.

Note that we are looser when validating data from JSON in strict mode. For example, when validating a `UUID` field,
instances of `str` will be accepted when validating from JSON, but not from python:

```python
import json
from uuid import UUID

from pydantic import BaseModel, ValidationError


class MyModel(BaseModel):
    guid: UUID


data = {'guid': '12345678-1234-1234-1234-123456789012'}

print(MyModel.model_validate(data))  # OK: lax
#> guid=UUID('12345678-1234-1234-1234-123456789012')

print(
    MyModel.model_validate_json(json.dumps(data), strict=True)
)  # OK: strict, but from json
#> guid=UUID('12345678-1234-1234-1234-123456789012')

try:
    MyModel.model_validate(data, strict=True)  # Not OK: strict, from python
except ValidationError as exc:
    print(exc.errors(include_url=False))
    """
    [
        {
            'type': 'is_instance_of',
            'loc': ('guid',),
            'msg': 'Input should be an instance of UUID',
            'input': '12345678-1234-1234-1234-123456789012',
            'ctx': {'class': 'UUID'},
        }
    ]
    """
```

For more details about what types are allowed as inputs in strict mode, you can review the
[Conversion Table](conversion_table.md).

## Strict mode in method calls

All the examples included so far get strict-mode validation through the use of `strict=True` as a keyword argument to
the validation methods. While we have shown this for `BaseModel.model_validate`, this also works with arbitrary types
through the use of `TypeAdapter`:

```python
from pydantic import TypeAdapter, ValidationError

print(TypeAdapter(bool).validate_python('yes'))  # OK: lax
#> True

try:
    TypeAdapter(bool).validate_python('yes', strict=True)  # Not OK: strict
except ValidationError as exc:
    print(exc)
    """
    1 validation error for bool
      Input should be a valid boolean [type=bool_type, input_value='yes', input_type=str]
    """
```

Note this also works even when using more "complex" types in `TypeAdapter`:

```python
from dataclasses import dataclass

from pydantic import TypeAdapter, ValidationError


@dataclass
class MyDataclass:
    x: int


try:
    TypeAdapter(MyDataclass).validate_python({'x': '123'}, strict=True)
except ValidationError as exc:
    print(exc)
    """
    1 validation error for MyDataclass
      Input should be an instance of MyDataclass [type=dataclass_exact_type, input_value={'x': '123'}, input_type=dict]
    """
```

This also works with the `TypeAdapter.validate_json` and `BaseModel.model_validate_json` methods:

```python
import json
from uuid import UUID

from pydantic import BaseModel, TypeAdapter, ValidationError

try:
    TypeAdapter(list[int]).validate_json('["1", 2, "3"]', strict=True)
except ValidationError as exc:
    print(exc)
    """
    2 validation errors for list[int]
    0
      Input should be a valid integer [type=int_type, input_value='1', input_type=str]
    2
      Input should be a valid integer [type=int_type, input_value='3', input_type=str]
    """


class Model(BaseModel):
    x: int
    y: UUID


data = {'x': '1', 'y': '12345678-1234-1234-1234-123456789012'}
try:
    Model.model_validate(data, strict=True)
except ValidationError as exc:
    # Neither x nor y are valid in strict mode from python:
    print(exc)
    """
    2 validation errors for Model
    x
      Input should be a valid integer [type=int_type, input_value='1', input_type=str]
    y
      Input should be an instance of UUID [type=is_instance_of, input_value='12345678-1234-1234-1234-123456789012', input_type=str]
    """

json_data = json.dumps(data)
try:
    Model.model_validate_json(json_data, strict=True)
except ValidationError as exc:
    # From JSON, x is still not valid in strict mode, but y is:
    print(exc)
    """
    1 validation error for Model
    x
      Input should be a valid integer [type=int_type, input_value='1', input_type=str]
    """
```

## Strict mode with `Field`

For individual fields on a model, you can [set `strict=True` on the field](../api/fields.md#pydantic.fields.Field).
This will cause strict-mode validation to be used for that field, even when the validation methods are called without
`strict=True`.

Only the fields for which `strict=True` is set will be affected:

```python
from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    name: str
    age: int
    n_pets: int


user = User(name='John', age='42', n_pets='1')
print(user)
#> name='John' age=42 n_pets=1


class AnotherUser(BaseModel):
    name: str
    age: int = Field(strict=True)
    n_pets: int


try:
    anotheruser = AnotherUser(name='John', age='42', n_pets='1')
except ValidationError as e:
    print(e)
    """
    1 validation error for AnotherUser
    age
      Input should be a valid integer [type=int_type, input_value='42', input_type=str]
    """
```

Note that making fields strict will also affect the validation performed when instantiating the model class:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(strict=True)
    y: int = Field(strict=False)


try:
    Model(x='1', y='2')
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Model
    x
      Input should be a valid integer [type=int_type, input_value='1', input_type=str]
    """
```

### Using `Field` as an annotation

Note that `Field(strict=True)` (or with any other keyword arguments) can be used as an annotation if necessary, e.g.,
when working with `TypedDict`:

```python
from typing import Annotated

from typing_extensions import TypedDict

from pydantic import Field, TypeAdapter, ValidationError


class MyDict(TypedDict):
    x: Annotated[int, Field(strict=True)]


try:
    TypeAdapter(MyDict).validate_python({'x': '1'})
except ValidationError as exc:
    print(exc)
    """
    1 validation error for MyDict
    x
      Input should be a valid integer [type=int_type, input_value='1', input_type=str]
    """
```

## Strict mode with `Annotated[..., Strict()]`

??? api "API Documentation"
    [`pydantic.types.Strict`][pydantic.types.Strict]<br>

Pydantic also provides the [`Strict`](../api/types.md#pydantic.types.Strict) class, which is intended for use as
metadata with [`typing.Annotated`][] class; this annotation indicates that the annotated field should be validated in
strict mode:

```python
from typing import Annotated

from pydantic import BaseModel, Strict, ValidationError


class User(BaseModel):
    name: str
    age: int
    is_active: Annotated[bool, Strict()]


User(name='David', age=33, is_active=True)
try:
    User(name='David', age=33, is_active='True')
except ValidationError as exc:
    print(exc)
    """
    1 validation error for User
    is_active
      Input should be a valid boolean [type=bool_type, input_value='True', input_type=str]
    """
```

This is, in fact, the method used to implement some of the strict-out-of-the-box types provided by Pydantic,
such as [`StrictInt`](../api/types.md#pydantic.types.StrictInt).

## Strict mode with `ConfigDict`

### `BaseModel`

If you want to enable strict mode for all fields on a complex input type, you can use
[`ConfigDict(strict=True)`](../api/config.md#pydantic.config.ConfigDict) in the `model_config`:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class User(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    age: int
    is_active: bool


try:
    User(name='David', age='33', is_active='yes')
except ValidationError as exc:
    print(exc)
    """
    2 validation errors for User
    age
      Input should be a valid integer [type=int_type, input_value='33', input_type=str]
    is_active
      Input should be a valid boolean [type=bool_type, input_value='yes', input_type=str]
    """
```

!!! note
    When using `strict=True` through a model's `model_config`, you can still override the strictness
    of individual fields by setting `strict=False` on individual fields:

    ```python
    from pydantic import BaseModel, ConfigDict, Field


    class User(BaseModel):
        model_config = ConfigDict(strict=True)

        name: str
        age: int = Field(strict=False)
    ```

Note that strict mode is not recursively applied to nested model fields:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Inner(BaseModel):
    y: int


class Outer(BaseModel):
    model_config = ConfigDict(strict=True)

    x: int
    inner: Inner


print(Outer(x=1, inner=Inner(y='2')))
#> x=1 inner=Inner(y=2)

try:
    Outer(x='1', inner=Inner(y='2'))
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Outer
    x
      Input should be a valid integer [type=int_type, input_value='1', input_type=str]
    """
```

(This is also the case for dataclasses and `TypedDict`.)

If this is undesirable, you should make sure that strict mode is enabled for all the types involved.
For example, this can be done for model classes by using a shared base class with
`model_config = ConfigDict(strict=True)`:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class MyBaseModel(BaseModel):
    model_config = ConfigDict(strict=True)


class Inner(MyBaseModel):
    y: int


class Outer(MyBaseModel):
    x: int
    inner: Inner


try:
    Outer.model_validate({'x': 1, 'inner': {'y': '2'}})
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Outer
    inner.y
      Input should be a valid integer [type=int_type, input_value='2', input_type=str]
    """
```

### Dataclasses and `TypedDict`

Pydantic dataclasses behave similarly to the examples shown above with `BaseModel`, just that instead of `model_config`
you should use the `config` keyword argument to the `@pydantic.dataclasses.dataclass` decorator.

When possible, you can achieve nested strict mode for vanilla dataclasses or `TypedDict` subclasses by annotating fields
with the [`pydantic.types.Strict` annotation](#strict-mode-with-annotated-strict).

However, if this is *not* possible (e.g., when working with third-party types), you can set the config that Pydantic
should use for the type by setting the `__pydantic_config__` attribute on the type:

```python
from typing_extensions import TypedDict

from pydantic import ConfigDict, TypeAdapter, ValidationError


class Inner(TypedDict):
    y: int


Inner.__pydantic_config__ = ConfigDict(strict=True)


class Outer(TypedDict):
    x: int
    inner: Inner


adapter = TypeAdapter(Outer)
print(adapter.validate_python({'x': '1', 'inner': {'y': 2}}))
#> {'x': 1, 'inner': {'y': 2}}


try:
    adapter.validate_python({'x': '1', 'inner': {'y': '2'}})
except ValidationError as exc:
    print(exc)
    """
    1 validation error for Outer
    inner.y
      Input should be a valid integer [type=int_type, input_value='2', input_type=str]
    """
```

### `TypeAdapter`

You can also get strict mode through the use of the config keyword argument to the
[`TypeAdapter`](../api/type_adapter.md) class:

```python
from pydantic import ConfigDict, TypeAdapter, ValidationError

adapter = TypeAdapter(bool, config=ConfigDict(strict=True))

try:
    adapter.validate_python('yes')
except ValidationError as exc:
    print(exc)
    """
    1 validation error for bool
      Input should be a valid boolean [type=bool_type, input_value='yes', input_type=str]
    """
```

### `@validate_call`

Strict mode is also usable with the [`@validate_call`](../api/validate_call.md#pydantic.validate_call_decorator.validate_call)
decorator by passing the `config` keyword argument:

```python
from pydantic import ConfigDict, ValidationError, validate_call


@validate_call(config=ConfigDict(strict=True))
def foo(x: int) -> int:
    return x


try:
    foo('1')
except ValidationError as exc:
    print(exc)
    """
    1 validation error for foo
    0
      Input should be a valid integer [type=int_type, input_value='1', input_type=str]
    """
```
````

## File: docs/concepts/type_adapter.md
````markdown
You may have types that are not `BaseModel`s that you want to validate data against.
Or you may want to validate a `list[SomeModel]`, or dump it to JSON.

??? api "API Documentation"
    [`pydantic.type_adapter.TypeAdapter`][pydantic.type_adapter.TypeAdapter]<br>

For use cases like this, Pydantic provides [`TypeAdapter`][pydantic.type_adapter.TypeAdapter],
which can be used for type validation, serialization, and JSON schema generation without needing to create a
[`BaseModel`][pydantic.main.BaseModel].

A [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] instance exposes some of the functionality from
[`BaseModel`][pydantic.main.BaseModel] instance methods for types that do not have such methods
(such as dataclasses, primitive types, and more):

```python
from typing_extensions import TypedDict

from pydantic import TypeAdapter, ValidationError


class User(TypedDict):
    name: str
    id: int


user_list_adapter = TypeAdapter(list[User])
user_list = user_list_adapter.validate_python([{'name': 'Fred', 'id': '3'}])
print(repr(user_list))
#> [{'name': 'Fred', 'id': 3}]

try:
    user_list_adapter.validate_python(
        [{'name': 'Fred', 'id': 'wrong', 'other': 'no'}]
    )
except ValidationError as e:
    print(e)
    """
    1 validation error for list[User]
    0.id
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='wrong', input_type=str]
    """

print(repr(user_list_adapter.dump_json(user_list)))
#> b'[{"name":"Fred","id":3}]'
```

!!! info "`dump_json` returns `bytes`"
    `TypeAdapter`'s `dump_json` methods returns a `bytes` object, unlike the corresponding method for `BaseModel`, `model_dump_json`, which returns a `str`.
    The reason for this discrepancy is that in V1, model dumping returned a str type, so this behavior is retained in V2 for backwards compatibility.
    For the `BaseModel` case, `bytes` are coerced to `str` types, but `bytes` are often the desired end type.
    Hence, for the new `TypeAdapter` class in V2, the return type is simply `bytes`, which can easily be coerced to a `str` type if desired.

!!! note
    Despite some overlap in use cases with [`RootModel`][pydantic.root_model.RootModel],
    [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] should not be used as a type annotation for
    specifying fields of a `BaseModel`, etc.

## Parsing data into a specified type

[`TypeAdapter`][pydantic.type_adapter.TypeAdapter] can be used to apply the parsing logic to populate Pydantic models
in a more ad-hoc way. This function behaves similarly to
[`BaseModel.model_validate`][pydantic.main.BaseModel.model_validate],
but works with arbitrary Pydantic-compatible types.

This is especially useful when you want to parse results into a type that is not a direct subclass of
[`BaseModel`][pydantic.main.BaseModel]. For example:

```python
from pydantic import BaseModel, TypeAdapter


class Item(BaseModel):
    id: int
    name: str


# `item_data` could come from an API call, eg., via something like:
# item_data = requests.get('https://my-api.com/items').json()
item_data = [{'id': 1, 'name': 'My Item'}]

items = TypeAdapter(list[Item]).validate_python(item_data)
print(items)
#> [Item(id=1, name='My Item')]
```

[`TypeAdapter`][pydantic.type_adapter.TypeAdapter] is capable of parsing data into any of the types Pydantic can
handle as fields of a [`BaseModel`][pydantic.main.BaseModel].

!!! info "Performance considerations"
    When creating an instance of [`TypeAdapter`][pydantic.type_adapter.TypeAdapter], the provided type must be analyzed and converted into a pydantic-core
    schema. This comes with some non-trivial overhead, so it is recommended to create a `TypeAdapter` for a given type
    just once and reuse it in loops or other performance-critical code.

## Rebuilding a `TypeAdapter`'s schema

In v2.10+, [`TypeAdapter`][pydantic.type_adapter.TypeAdapter]'s support deferred schema building and manual rebuilds. This is helpful for the case of:

* Types with forward references
* Types for which core schema builds are expensive

When you initialize a [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] with a type, Pydantic analyzes the type and creates a core schema for it.
This core schema contains the information needed to validate and serialize data for that type.
See the [architecture documentation](../internals/architecture.md) for more information on core schemas.

If you set [`defer_build`][pydantic.config.ConfigDict.defer_build] to `True` when initializing a `TypeAdapter`,
Pydantic will defer building the core schema until the first time it is needed (for validation or serialization).

In order to manually trigger the building of the core schema, you can call the
[`rebuild`][pydantic.type_adapter.TypeAdapter.rebuild] method on the [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] instance:

```python
from pydantic import ConfigDict, TypeAdapter

ta = TypeAdapter('MyInt', config=ConfigDict(defer_build=True))

# some time later, the forward reference is defined
MyInt = int

ta.rebuild()
assert ta.validate_python(1) == 1
```
````

## File: docs/concepts/types.md
````markdown
Where possible Pydantic uses [standard library types](../api/standard_library_types.md) to define fields, thus smoothing
the learning curve. For many useful applications, however, no standard library type exists,
so Pydantic implements many commonly used types.

There are also more complex types that can be found in the
[Pydantic Extra Types](https://github.com/pydantic/pydantic-extra-types) package.

If no existing type suits your purpose you can also implement your [own Pydantic-compatible types](#custom-types) with custom properties and validation.

The following sections describe the types supported by Pydantic.

* [Standard Library Types](../api/standard_library_types.md) &mdash; types from the Python standard library.
* [Strict Types](#strict-types) &mdash; types that enable you to prevent coercion from compatible types.
* [Custom Data Types](#custom-types) &mdash; create your own custom data types.
* [Field Type Conversions](../concepts/conversion_table.md) &mdash; strict and lax conversion between different field types.

## Type conversion

During validation, Pydantic can coerce data into expected types.

There are two modes of coercion: strict and lax. See [Conversion Table](../concepts/conversion_table.md) for more details on how Pydantic converts data in both strict and lax modes.

See [Strict mode](../concepts/strict_mode.md) and [Strict Types](#strict-types) for details on enabling strict coercion.

## Strict Types

Pydantic provides the following strict types:

* [`StrictBool`][pydantic.types.StrictBool]
* [`StrictBytes`][pydantic.types.StrictBytes]
* [`StrictFloat`][pydantic.types.StrictFloat]
* [`StrictInt`][pydantic.types.StrictInt]
* [`StrictStr`][pydantic.types.StrictStr]

These types will only pass validation when the validated value is of the respective type or is a subtype of that type.

### Constrained types

This behavior is also exposed via the `strict` field of the constrained types and can be combined with a multitude of complex validation rules. See the individual type signatures for supported arguments.

* [`conbytes()`][pydantic.types.conbytes]
* [`condate()`][pydantic.types.condate]
* [`condecimal()`][pydantic.types.condecimal]
* [`confloat()`][pydantic.types.confloat]
* [`confrozenset()`][pydantic.types.confrozenset]
* [`conint()`][pydantic.types.conint]
* [`conlist()`][pydantic.types.conlist]
* [`conset()`][pydantic.types.conset]
* [`constr()`][pydantic.types.constr]

The following caveats apply:

* `StrictBytes` (and the `strict` option of `conbytes()`) will accept both `bytes`,
   and `bytearray` types.
* `StrictInt` (and the `strict` option of `conint()`) will not accept `bool` types,
    even though `bool` is a subclass of `int` in Python. Other subclasses will work.
* `StrictFloat` (and the `strict` option of `confloat()`) will not accept `int`.

Besides the above, you can also have a [`FiniteFloat`][pydantic.types.FiniteFloat] type that will only accept finite values (i.e. not `inf`, `-inf` or `nan`).

## Custom Types

You can also define your own custom data types. There are several ways to achieve it.

### Using the annotated pattern

The [annotated pattern](./fields.md#the-annotated-pattern) can be used to make types reusable across your code base.
For example, to create a type representing a positive integer:

```python
from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError

PositiveInt = Annotated[int, Field(gt=0)]  # (1)!

ta = TypeAdapter(PositiveInt)

print(ta.validate_python(1))
#> 1

try:
    ta.validate_python(-1)
except ValidationError as exc:
    print(exc)
    """
    1 validation error for constrained-int
      Input should be greater than 0 [type=greater_than, input_value=-1, input_type=int]
    """
```

1. Note that you can also use constraints from the [annotated-types](https://github.com/annotated-types/annotated-types)
  library to make this Pydantic-agnostic:

    ```python {test="skip" lint="skip"}
    from annotated_types import Gt

    PositiveInt = Annotated[int, Gt(0)]
    ```

#### Adding validation and serialization

You can add or override validation, serialization, and JSON schemas to an arbitrary type using the markers that
Pydantic exports:

```python
from typing import Annotated

from pydantic import (
    AfterValidator,
    PlainSerializer,
    TypeAdapter,
    WithJsonSchema,
)

TruncatedFloat = Annotated[
    float,
    AfterValidator(lambda x: round(x, 1)),
    PlainSerializer(lambda x: f'{x:.1e}', return_type=str),
    WithJsonSchema({'type': 'string'}, mode='serialization'),
]


ta = TypeAdapter(TruncatedFloat)

input = 1.02345
assert input != 1.0

assert ta.validate_python(input) == 1.0

assert ta.dump_json(input) == b'"1.0e+00"'

assert ta.json_schema(mode='validation') == {'type': 'number'}
assert ta.json_schema(mode='serialization') == {'type': 'string'}
```

#### Generics

[Type variables][typing.TypeVar] can be used within the [`Annotated`][typing.Annotated] type:

```python
from typing import Annotated, TypeVar

from annotated_types import Gt, Len

from pydantic import TypeAdapter, ValidationError

T = TypeVar('T')


ShortList = Annotated[list[T], Len(max_length=4)]


ta = TypeAdapter(ShortList[int])

v = ta.validate_python([1, 2, 3, 4])
assert v == [1, 2, 3, 4]

try:
    ta.validate_python([1, 2, 3, 4, 5])
except ValidationError as exc:
    print(exc)
    """
    1 validation error for list[int]
      List should have at most 4 items after validation, not 5 [type=too_long, input_value=[1, 2, 3, 4, 5], input_type=list]
    """


PositiveList = list[Annotated[T, Gt(0)]]

ta = TypeAdapter(PositiveList[float])

v = ta.validate_python([1.0])
assert type(v[0]) is float


try:
    ta.validate_python([-1.0])
except ValidationError as exc:
    print(exc)
    """
    1 validation error for list[constrained-float]
    0
      Input should be greater than 0 [type=greater_than, input_value=-1.0, input_type=float]
    """
```

### Named type aliases

The above examples make use of *implicit* type aliases, assigned to a variable. At runtime, Pydantic
has no way of knowing the name of the variable it was assigned to, and this can be problematic for
two reasons:

* The [JSON Schema](./json_schema.md) of the alias won't be converted into a
  [definition](https://json-schema.org/understanding-json-schema/structuring#defs).
  This is mostly useful when you are using the alias more than once in a model definition.
* In most cases, [recursive type aliases](#named-recursive-types) won't work.

By leveraging the new [`type` statement](https://typing.readthedocs.io/en/latest/spec/aliases.html#type-statement)
(introduced in [PEP 695](https://peps.python.org/pep-0695/)), you can define aliases as follows:

=== "Python 3.9 and above"

    ```python
    from typing import Annotated

    from annotated_types import Gt
    from typing_extensions import TypeAliasType

    from pydantic import BaseModel

    PositiveIntList = TypeAliasType('PositiveIntList', list[Annotated[int, Gt(0)]])


    class Model(BaseModel):
        x: PositiveIntList
        y: PositiveIntList


    print(Model.model_json_schema())  # (1)!
    """
    {
        '$defs': {
            'PositiveIntList': {
                'items': {'exclusiveMinimum': 0, 'type': 'integer'},
                'type': 'array',
            }
        },
        'properties': {
            'x': {'$ref': '#/$defs/PositiveIntList'},
            'y': {'$ref': '#/$defs/PositiveIntList'},
        },
        'required': ['x', 'y'],
        'title': 'Model',
        'type': 'object',
    }
    """
    ```

    1. If `PositiveIntList` were to be defined as an implicit type alias, its definition
       would have been duplicated in both `'x'` and `'y'`.

=== "Python 3.12 and above (new syntax)"

    ```python {requires="3.12" upgrade="skip" lint="skip"}
    from typing import Annotated

    from annotated_types import Gt

    from pydantic import BaseModel

    type PositiveIntList = list[Annotated[int, Gt(0)]]


    class Model(BaseModel):
        x: PositiveIntList
        y: PositiveIntList


    print(Model.model_json_schema())  # (1)!
    """
    {
        '$defs': {
            'PositiveIntList': {
                'items': {'exclusiveMinimum': 0, 'type': 'integer'},
                'type': 'array',
            }
        },
        'properties': {
            'x': {'$ref': '#/$defs/PositiveIntList'},
            'y': {'$ref': '#/$defs/PositiveIntList'},
        },
        'required': ['x', 'y'],
        'title': 'Model',
        'type': 'object',
    }
    """
    ```

    1. If `PositiveIntList` were to be defined as an implicit type alias, its definition
       would have been duplicated in both `'x'` and `'y'`.

!!! warning "When to use named type aliases"

    While (named) PEP 695 and implicit type aliases are meant to be equivalent for static type checkers,
    Pydantic will *not* understand field-specific metadata inside named aliases. That is, metadata such as
    `alias`, `default`, `deprecated`, *cannot* be used:

    === "Python 3.9 and above"

        ```python {test="skip"}
        from typing import Annotated

        from typing_extensions import TypeAliasType

        from pydantic import BaseModel, Field

        MyAlias = TypeAliasType('MyAlias', Annotated[int, Field(default=1)])


        class Model(BaseModel):
            x: MyAlias  # This is not allowed
        ```

    === "Python 3.12 and above (new syntax)"

        ```python {requires="3.12" upgrade="skip" lint="skip" test="skip"}
        from typing import Annotated

        from pydantic import BaseModel, Field

        type MyAlias = Annotated[int, Field(default=1)]


        class Model(BaseModel):
            x: MyAlias  # This is not allowed
        ```

    Only metadata that can be applied to the annotated type itself is allowed
    (e.g. [validation constraints](./fields.md#field-constraints) and JSON metadata).
    Trying to support field-specific metadata would require eagerly inspecting the
    type alias's [`__value__`][typing.TypeAliasType.__value__], and as such Pydantic
    wouldn't be able to have the alias stored as a JSON Schema definition.

!!! note
    As with implicit type aliases, [type variables][typing.TypeVar] can also be used inside the generic alias:

    === "Python 3.9 and above"

        ```python
        from typing import Annotated, TypeVar

        from annotated_types import Len
        from typing_extensions import TypeAliasType

        T = TypeVar('T')

        ShortList = TypeAliasType(
            'ShortList', Annotated[list[T], Len(max_length=4)], type_params=(T,)
        )
        ```

    === "Python 3.12 and above (new syntax)"

        ```python {requires="3.12" upgrade="skip" lint="skip"}
        from typing import Annotated, TypeVar

        from annotated_types import Len

        type ShortList[T] = Annotated[list[T], Len(max_length=4)]
        ```

#### Named recursive types

Named type aliases should be used whenever you need to define recursive type aliases (1).
{ .annotate }

1. For several reasons, Pydantic isn't able to support implicit recursive aliases. For
   instance, it won't be able to resolve [forward annotations](./forward_annotations.md)
   across modules.

For instance, here is an example definition of a JSON type:

=== "Python 3.9 and above"

    ```python
    from typing import Union

    from typing_extensions import TypeAliasType

    from pydantic import TypeAdapter

    Json = TypeAliasType(
        'Json',
        'Union[dict[str, Json], list[Json], str, int, float, bool, None]',  # (1)!
    )

    ta = TypeAdapter(Json)
    print(ta.json_schema())
    """
    {
        '$defs': {
            'Json': {
                'anyOf': [
                    {
                        'additionalProperties': {'$ref': '#/$defs/Json'},
                        'type': 'object',
                    },
                    {'items': {'$ref': '#/$defs/Json'}, 'type': 'array'},
                    {'type': 'string'},
                    {'type': 'integer'},
                    {'type': 'number'},
                    {'type': 'boolean'},
                    {'type': 'null'},
                ]
            }
        },
        '$ref': '#/$defs/Json',
    }
    """
    ```

    1. Wrapping the annotation in quotes is necessary as it is eagerly evaluated
       (and `Json` has yet to be defined).

=== "Python 3.12 and above (new syntax)"

    ```python {requires="3.12" upgrade="skip" lint="skip"}
    from pydantic import TypeAdapter

    type Json = dict[str, Json] | list[Json] | str | int | float | bool | None  # (1)!

    ta = TypeAdapter(Json)
    print(ta.json_schema())
    """
    {
        '$defs': {
            'Json': {
                'anyOf': [
                    {
                        'additionalProperties': {'$ref': '#/$defs/Json'},
                        'type': 'object',
                    },
                    {'items': {'$ref': '#/$defs/Json'}, 'type': 'array'},
                    {'type': 'string'},
                    {'type': 'integer'},
                    {'type': 'number'},
                    {'type': 'boolean'},
                    {'type': 'null'},
                ]
            }
        },
        '$ref': '#/$defs/Json',
    }
    """
    ```

    1. The value of a named type alias is lazily evaluated, so there's no need to use forward annotations.

!!! tip
    Pydantic defines a [`JsonValue`][pydantic.types.JsonValue] type as a convenience.

### Customizing validation with `__get_pydantic_core_schema__` <a name="customizing_validation_with_get_pydantic_core_schema"></a>

To do more extensive customization of how Pydantic handles custom classes, and in particular when you have access to the
class or can subclass it, you can implement a special `__get_pydantic_core_schema__` to tell Pydantic how to generate the
`pydantic-core` schema.

While `pydantic` uses `pydantic-core` internally to handle validation and serialization, it is a new API for Pydantic V2,
thus it is one of the areas most likely to be tweaked in the future and you should try to stick to the built-in
constructs like those provided by `annotated-types`, `pydantic.Field`, or `BeforeValidator` and so on.

You can implement `__get_pydantic_core_schema__` both on a custom type and on metadata intended to be put in `Annotated`.
In both cases the API is middleware-like and similar to that of "wrap" validators: you get a `source_type` (which isn't
necessarily the same as the class, in particular for generics) and a `handler` that you can call with a type to either
call the next metadata in `Annotated` or call into Pydantic's internal schema generation.

The simplest no-op implementation calls the handler with the type you are given, then returns that as the result. You can
also choose to modify the type before calling the handler, modify the core schema returned by the handler, or not call the
handler at all.

#### As a method on a custom type

The following is an example of a type that uses `__get_pydantic_core_schema__` to customize how it gets validated.
This is equivalent to implementing `__get_validators__` in Pydantic V1.

```python
from typing import Any

from pydantic_core import CoreSchema, core_schema

from pydantic import GetCoreSchemaHandler, TypeAdapter


class Username(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))


ta = TypeAdapter(Username)
res = ta.validate_python('abc')
assert isinstance(res, Username)
assert res == 'abc'
```

See [JSON Schema](../concepts/json_schema.md) for more details on how to customize JSON schemas for custom types.

#### As an annotation

Often you'll want to parametrize your custom type by more than just generic type parameters (which you can do via the type system and will be discussed later). Or you may not actually care (or want to) make an instance of your subclass; you actually want the original type, just with some extra validation done.

For example, if you were to implement `pydantic.AfterValidator` (see [Adding validation and serialization](#adding-validation-and-serialization)) yourself, you'd do something similar to the following:

```python
from dataclasses import dataclass
from typing import Annotated, Any, Callable

from pydantic_core import CoreSchema, core_schema

from pydantic import BaseModel, GetCoreSchemaHandler


@dataclass(frozen=True)  # (1)!
class MyAfterValidator:
    func: Callable[[Any], Any]

    def __get_pydantic_core_schema__(
        self, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            self.func, handler(source_type)
        )


Username = Annotated[str, MyAfterValidator(str.lower)]


class Model(BaseModel):
    name: Username


assert Model(name='ABC').name == 'abc'  # (2)!
```

1. The `frozen=True` specification makes `MyAfterValidator` hashable. Without this, a union such as `Username | None` will raise an error.
2. Notice that type checkers will not complain about assigning `'ABC'` to `Username` like they did in the previous example because they do not consider `Username` to be a distinct type from `str`.

#### Handling third-party types

Another use case for the pattern in the previous section is to handle third party types.

```python
from typing import Annotated, Any

from pydantic_core import core_schema

from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
    ValidationError,
)
from pydantic.json_schema import JsonSchemaValue


class ThirdPartyType:
    """
    This is meant to represent a type from a third-party library that wasn't designed with Pydantic
    integration in mind, and so doesn't have a `pydantic_core.CoreSchema` or anything.
    """

    x: int

    def __init__(self):
        self.x = 0


class _ThirdPartyTypePydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        We return a pydantic_core.CoreSchema that behaves in the following ways:

        * ints will be parsed as `ThirdPartyType` instances with the int as the x attribute
        * `ThirdPartyType` instances will be parsed as `ThirdPartyType` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just an int
        """

        def validate_from_int(value: int) -> ThirdPartyType:
            result = ThirdPartyType()
            result.x = value
            return result

        from_int_schema = core_schema.chain_schema(
            [
                core_schema.int_schema(),
                core_schema.no_info_plain_validator_function(validate_from_int),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_int_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(ThirdPartyType),
                    from_int_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.x
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `int`
        return handler(core_schema.int_schema())


# We now create an `Annotated` wrapper that we'll use as the annotation for fields on `BaseModel`s, etc.
PydanticThirdPartyType = Annotated[
    ThirdPartyType, _ThirdPartyTypePydanticAnnotation
]


# Create a model class that uses this annotation as a field
class Model(BaseModel):
    third_party_type: PydanticThirdPartyType


# Demonstrate that this field is handled correctly, that ints are parsed into `ThirdPartyType`, and that
# these instances are also "dumped" directly into ints as expected.
m_int = Model(third_party_type=1)
assert isinstance(m_int.third_party_type, ThirdPartyType)
assert m_int.third_party_type.x == 1
assert m_int.model_dump() == {'third_party_type': 1}

# Do the same thing where an instance of ThirdPartyType is passed in
instance = ThirdPartyType()
assert instance.x == 0
instance.x = 10

m_instance = Model(third_party_type=instance)
assert isinstance(m_instance.third_party_type, ThirdPartyType)
assert m_instance.third_party_type.x == 10
assert m_instance.model_dump() == {'third_party_type': 10}

# Demonstrate that validation errors are raised as expected for invalid inputs
try:
    Model(third_party_type='a')
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    third_party_type.is-instance[ThirdPartyType]
      Input should be an instance of ThirdPartyType [type=is_instance_of, input_value='a', input_type=str]
    third_party_type.chain[int,function-plain[validate_from_int()]]
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """


assert Model.model_json_schema() == {
    'properties': {
        'third_party_type': {'title': 'Third Party Type', 'type': 'integer'}
    },
    'required': ['third_party_type'],
    'title': 'Model',
    'type': 'object',
}
```

You can use this approach to e.g. define behavior for Pandas or Numpy types.

#### Using `GetPydanticSchema` to reduce boilerplate

??? api "API Documentation"
    [`pydantic.types.GetPydanticSchema`][pydantic.types.GetPydanticSchema]<br>

You may notice that the above examples where we create a marker class require a good amount of boilerplate.
For many simple cases you can greatly minimize this by using `pydantic.GetPydanticSchema`:

```python
from typing import Annotated

from pydantic_core import core_schema

from pydantic import BaseModel, GetPydanticSchema


class Model(BaseModel):
    y: Annotated[
        str,
        GetPydanticSchema(
            lambda tp, handler: core_schema.no_info_after_validator_function(
                lambda x: x * 2, handler(tp)
            )
        ),
    ]


assert Model(y='ab').y == 'abab'
```

#### Summary

Let's recap:

1. Pydantic provides high level hooks to customize types via `Annotated` like `AfterValidator` and `Field`. Use these when possible.
2. Under the hood these use `pydantic-core` to customize validation, and you can hook into that directly using `GetPydanticSchema` or a marker class with `__get_pydantic_core_schema__`.
3. If you really want a custom type you can implement `__get_pydantic_core_schema__` on the type itself.

### Handling custom generic classes

!!! warning
    This is an advanced technique that you might not need in the beginning. In most of
    the cases you will probably be fine with standard Pydantic models.

You can use
[Generic Classes](https://docs.python.org/3/library/typing.html#typing.Generic) as
field types and perform custom validation based on the "type parameters" (or sub-types)
with `__get_pydantic_core_schema__`.

If the Generic class that you are using as a sub-type has a classmethod
`__get_pydantic_core_schema__`, you don't need to use
[`arbitrary_types_allowed`][pydantic.config.ConfigDict.arbitrary_types_allowed] for it to work.

Because the `source_type` parameter is not the same as the `cls` parameter, you can use `typing.get_args` (or `typing_extensions.get_args`) to extract the generic parameters.
Then you can use the `handler` to generate a schema for them by calling `handler.generate_schema`.
Note that we do not do something like `handler(get_args(source_type)[0])` because we want to generate an unrelated
schema for that generic parameter, not one that is influenced by the current context of `Annotated` metadata and such.
This is less important for custom types, but crucial for annotated metadata that modifies schema building.

```python
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from pydantic_core import CoreSchema, core_schema
from typing_extensions import get_args, get_origin

from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    ValidationError,
    ValidatorFunctionWrapHandler,
)

ItemType = TypeVar('ItemType')


# This is not a pydantic model, it's an arbitrary generic class
@dataclass
class Owner(Generic[ItemType]):
    name: str
    item: ItemType

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        origin = get_origin(source_type)
        if origin is None:  # used as `x: Owner` without params
            origin = source_type
            item_tp = Any
        else:
            item_tp = get_args(source_type)[0]
        # both calling handler(...) and handler.generate_schema(...)
        # would work, but prefer the latter for conceptual and consistency reasons
        item_schema = handler.generate_schema(item_tp)

        def val_item(
            v: Owner[Any], handler: ValidatorFunctionWrapHandler
        ) -> Owner[Any]:
            v.item = handler(v.item)
            return v

        python_schema = core_schema.chain_schema(
            # `chain_schema` means do the following steps in order:
            [
                # Ensure the value is an instance of Owner
                core_schema.is_instance_schema(cls),
                # Use the item_schema to validate `items`
                core_schema.no_info_wrap_validator_function(
                    val_item, item_schema
                ),
            ]
        )

        return core_schema.json_or_python_schema(
            # for JSON accept an object with name and item keys
            json_schema=core_schema.chain_schema(
                [
                    core_schema.typed_dict_schema(
                        {
                            'name': core_schema.typed_dict_field(
                                core_schema.str_schema()
                            ),
                            'item': core_schema.typed_dict_field(item_schema),
                        }
                    ),
                    # after validating the json data convert it to python
                    core_schema.no_info_before_validator_function(
                        lambda data: Owner(
                            name=data['name'], item=data['item']
                        ),
                        # note that we reuse the same schema here as below
                        python_schema,
                    ),
                ]
            ),
            python_schema=python_schema,
        )


class Car(BaseModel):
    color: str


class House(BaseModel):
    rooms: int


class Model(BaseModel):
    car_owner: Owner[Car]
    home_owner: Owner[House]


model = Model(
    car_owner=Owner(name='John', item=Car(color='black')),
    home_owner=Owner(name='James', item=House(rooms=3)),
)
print(model)
"""
car_owner=Owner(name='John', item=Car(color='black')) home_owner=Owner(name='James', item=House(rooms=3))
"""

try:
    # If the values of the sub-types are invalid, we get an error
    Model(
        car_owner=Owner(name='John', item=House(rooms=3)),
        home_owner=Owner(name='James', item=Car(color='black')),
    )
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    wine
      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='Kinda good', input_type=str]
    cheese
      Input should be a valid boolean, unable to interpret input [type=bool_parsing, input_value='yeah', input_type=str]
    """

# Similarly with JSON
model = Model.model_validate_json(
    '{"car_owner":{"name":"John","item":{"color":"black"}},"home_owner":{"name":"James","item":{"rooms":3}}}'
)
print(model)
"""
car_owner=Owner(name='John', item=Car(color='black')) home_owner=Owner(name='James', item=House(rooms=3))
"""

try:
    Model.model_validate_json(
        '{"car_owner":{"name":"John","item":{"rooms":3}},"home_owner":{"name":"James","item":{"color":"black"}}}'
    )
except ValidationError as e:
    print(e)
    """
    2 validation errors for Model
    car_owner.item.color
      Field required [type=missing, input_value={'rooms': 3}, input_type=dict]
    home_owner.item.rooms
      Field required [type=missing, input_value={'color': 'black'}, input_type=dict]
    """
```

#### Generic containers

The same idea can be applied to create generic container types, like a custom `Sequence` type:

```python
from typing import Any, Sequence, TypeVar

from pydantic_core import ValidationError, core_schema
from typing_extensions import get_args

from pydantic import BaseModel, GetCoreSchemaHandler

T = TypeVar('T')


class MySequence(Sequence[T]):
    def __init__(self, v: Sequence[T]):
        self.v = v

    def __getitem__(self, i):
        return self.v[i]

    def __len__(self):
        return len(self.v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        instance_schema = core_schema.is_instance_schema(cls)

        args = get_args(source)
        if args:
            # replace the type and rely on Pydantic to generate the right schema
            # for `Sequence`
            sequence_t_schema = handler.generate_schema(Sequence[args[0]])
        else:
            sequence_t_schema = handler.generate_schema(Sequence)

        non_instance_schema = core_schema.no_info_after_validator_function(
            MySequence, sequence_t_schema
        )
        return core_schema.union_schema([instance_schema, non_instance_schema])


class M(BaseModel):
    model_config = dict(validate_default=True)

    s1: MySequence = [3]


m = M()
print(m)
#> s1=<__main__.MySequence object at 0x0123456789ab>
print(m.s1.v)
#> [3]


class M(BaseModel):
    s1: MySequence[int]


M(s1=[1])
try:
    M(s1=['a'])
except ValidationError as exc:
    print(exc)
    """
    2 validation errors for M
    s1.is-instance[MySequence]
      Input should be an instance of MySequence [type=is_instance_of, input_value=['a'], input_type=list]
    s1.function-after[MySequence(), json-or-python[json=list[int],python=chain[is-instance[Sequence],function-wrap[sequence_validator()]]]].0
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    """
```

### Access to field name

!!!note
    This was not possible with Pydantic V2 to V2.3, it was [re-added](https://github.com/pydantic/pydantic/pull/7542) in Pydantic V2.4.

As of Pydantic V2.4, you can access the field name via the `handler.field_name` within `__get_pydantic_core_schema__`
and thereby set the field name which will be available from `info.field_name`.

```python
from typing import Any

from pydantic_core import core_schema

from pydantic import BaseModel, GetCoreSchemaHandler, ValidationInfo


class CustomType:
    """Custom type that stores the field it was used in."""

    def __init__(self, value: int, field_name: str):
        self.value = value
        self.field_name = field_name

    def __repr__(self):
        return f'CustomType<{self.value} {self.field_name!r}>'

    @classmethod
    def validate(cls, value: int, info: ValidationInfo):
        return cls(value, info.field_name)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.with_info_after_validator_function(
            cls.validate, handler(int)
        )


class MyModel(BaseModel):
    my_field: CustomType


m = MyModel(my_field=1)
print(m.my_field)
#> CustomType<1 'my_field'>
```

You can also access `field_name` from the markers used with `Annotated`, like [`AfterValidator`][pydantic.functional_validators.AfterValidator].

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ValidationInfo


def my_validators(value: int, info: ValidationInfo):
    return f'<{value} {info.field_name!r}>'


class MyModel(BaseModel):
    my_field: Annotated[int, AfterValidator(my_validators)]


m = MyModel(my_field=1)
print(m.my_field)
#> <1 'my_field'>
```
````

## File: docs/concepts/unions.md
````markdown
Unions are fundamentally different to all other types Pydantic validates - instead of requiring all fields/items/values to be valid, unions require only one member to be valid.

This leads to some nuance around how to validate unions:

* which member(s) of the union should you validate data against, and in which order?
* which errors to raise when validation fails?

Validating unions feels like adding another orthogonal dimension to the validation process.

To solve these problems, Pydantic supports three fundamental approaches to validating unions:

1. [left to right mode](#left-to-right-mode) - the simplest approach, each member of the union is tried in order and the first match is returned
2. [smart mode](#smart-mode) - similar to "left to right mode" members are tried in order; however, validation will proceed past the first match to attempt to find a better match, this is the default mode for most union validation
3. [discriminated unions](#discriminated-unions) - only one member of the union is tried, based on a discriminator

!!! tip

    In general, we recommend using [discriminated unions](#discriminated-unions). They are both more performant and more predictable than untagged unions, as they allow you to control which member of the union to validate against.

    For complex cases, if you're using untagged unions, it's recommended to use `union_mode='left_to_right'` if you need guarantees about the order of validation attempts against the union members.

    If you're looking for incredibly specialized behavior, you can use a [custom validator](../concepts/validators.md#field-validators).

## Union Modes

### Left to Right Mode

!!! note
    Because this mode often leads to unexpected validation results, it is not the default in Pydantic >=2, instead `union_mode='smart'` is the default.

With this approach, validation is attempted against each member of the union in their order they're defined, and the first successful validation is accepted as input.

If validation fails on all members, the validation error includes the errors from all members of the union.

`union_mode='left_to_right'` must be set as a [`Field`](../concepts/fields.md) parameter on union fields where you want to use it.

```python {title="Union with left to right mode"}
from typing import Union

from pydantic import BaseModel, Field, ValidationError


class User(BaseModel):
    id: Union[str, int] = Field(union_mode='left_to_right')


print(User(id=123))
#> id=123
print(User(id='hello'))
#> id='hello'

try:
    User(id=[])
except ValidationError as e:
    print(e)
    """
    2 validation errors for User
    id.str
      Input should be a valid string [type=string_type, input_value=[], input_type=list]
    id.int
      Input should be a valid integer [type=int_type, input_value=[], input_type=list]
    """
```

The order of members is very important in this case, as demonstrated by tweak the above example:

```python {title="Union with left to right - unexpected results"}
from typing import Union

from pydantic import BaseModel, Field


class User(BaseModel):
    id: Union[int, str] = Field(union_mode='left_to_right')


print(User(id=123))  # (1)
#> id=123
print(User(id='456'))  # (2)
#> id=456
```

1. As expected the input is validated against the `int` member and the result is as expected.
2. We're in lax mode and the numeric string `'123'` is valid as input to the first member of the union, `int`.
   Since that is tried first, we get the surprising result of `id` being an `int` instead of a `str`.

### Smart Mode

Because of the potentially surprising results of `union_mode='left_to_right'`, in Pydantic >=2 the default mode for `Union` validation is `union_mode='smart'`.

In this mode, pydantic attempts to select the best match for the input from the union members. The exact algorithm may change between Pydantic minor releases to allow for improvements in both performance and accuracy.

!!! note

    We reserve the right to tweak the internal `smart` matching algorithm in future versions of Pydantic. If you rely on very specific
    matching behavior, it's recommended to use `union_mode='left_to_right'` or [discriminated unions](#discriminated-unions).

??? info "Smart Mode Algorithm"

    The smart mode algorithm uses two metrics to determine the best match for the input:

    1. The number of valid fields set (relevant for models, dataclasses, and typed dicts)
    2. The exactness of the match (relevant for all types)

    #### Number of valid fields set

    !!! note
        This metric was introduced in Pydantic v2.8.0. Prior to this version, only exactness was used to determine the best match.

    This metric is currently only relevant for models, dataclasses, and typed dicts.

    The greater the number of valid fields set, the better the match. The number of fields set on nested models is also taken into account.
    These counts bubble up to the top-level union, where the union member with the highest count is considered the best match.

    For data types where this metric is relevant, we prioritize this count over exactness. For all other types, we use solely exactness.

    #### Exactness

    For `exactness`, Pydantic scores a match of a union member into one of the following three groups (from highest score to lowest score):

    * An exact type match, for example an `int` input to a `float | int` union validation is an exact type match for the `int` member
    * Validation would have succeeded in [`strict` mode](../concepts/strict_mode.md)
    * Validation would have succeeded in lax mode

    The union match which produced the highest exactness score will be considered the best match.

    In smart mode, the following steps are taken to try to select the best match for the input:

    === "`BaseModel`, `dataclass`, and `TypedDict`"

        1. Union members are attempted left to right, with any successful matches scored into one of the three exactness categories described above,
        with the valid fields set count also tallied.
        2. After all members have been evaluated, the member with the highest "valid fields set" count is returned.
        3. If there's a tie for the highest "valid fields set" count, the exactness score is used as a tiebreaker, and the member with the highest exactness score is returned.
        4. If validation failed on all the members, return all the errors.

    === "All other data types"

        1. Union members are attempted left to right, with any successful matches scored into one of the three exactness categories described above.
            * If validation succeeds with an exact type match, that member is returned immediately and following members will not be attempted.
        2. If validation succeeded on at least one member as a "strict" match, the leftmost of those "strict" matches is returned.
        3. If validation succeeded on at least one member in "lax" mode, the leftmost match is returned.
        4. Validation failed on all the members, return all the errors.

```python
from typing import Union
from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: Union[int, str, UUID]
    name: str


user_01 = User(id=123, name='John Doe')
print(user_01)
#> id=123 name='John Doe'
print(user_01.id)
#> 123
user_02 = User(id='1234', name='John Doe')
print(user_02)
#> id='1234' name='John Doe'
print(user_02.id)
#> 1234
user_03_uuid = UUID('cf57432e-809e-4353-adbd-9d5c0d733868')
user_03 = User(id=user_03_uuid, name='John Doe')
print(user_03)
#> id=UUID('cf57432e-809e-4353-adbd-9d5c0d733868') name='John Doe'
print(user_03.id)
#> cf57432e-809e-4353-adbd-9d5c0d733868
print(user_03_uuid.int)
#> 275603287559914445491632874575877060712
```

## Discriminated Unions

**Discriminated unions are sometimes referred to as "Tagged Unions".**

We can use discriminated unions to more efficiently validate `Union` types, by choosing which member of the union to validate against.

This makes validation more efficient and also avoids a proliferation of errors when validation fails.

Adding discriminator to unions also means the generated JSON schema implements the [associated OpenAPI specification](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#discriminator-object).

### Discriminated Unions with `str` discriminators

Frequently, in the case of a `Union` with multiple models,
there is a common field to all members of the union that can be used to distinguish
which union case the data should be validated against; this is referred to as the "discriminator" in
[OpenAPI](https://swagger.io/docs/specification/data-models/inheritance-and-polymorphism/).

To validate models based on that information you can set the same field - let's call it `my_discriminator` -
in each of the models with a discriminated value, which is one (or many) `Literal` value(s).
For your `Union`, you can set the discriminator in its value: `Field(discriminator='my_discriminator')`.

```python
from typing import Literal, Union

from pydantic import BaseModel, Field, ValidationError


class Cat(BaseModel):
    pet_type: Literal['cat']
    meows: int


class Dog(BaseModel):
    pet_type: Literal['dog']
    barks: float


class Lizard(BaseModel):
    pet_type: Literal['reptile', 'lizard']
    scales: bool


class Model(BaseModel):
    pet: Union[Cat, Dog, Lizard] = Field(discriminator='pet_type')
    n: int


print(Model(pet={'pet_type': 'dog', 'barks': 3.14}, n=1))
#> pet=Dog(pet_type='dog', barks=3.14) n=1
try:
    Model(pet={'pet_type': 'dog'}, n=1)
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    pet.dog.barks
      Field required [type=missing, input_value={'pet_type': 'dog'}, input_type=dict]
    """
```

### Discriminated Unions with callable `Discriminator`

??? api "API Documentation"
    [`pydantic.types.Discriminator`][pydantic.types.Discriminator]<br>

In the case of a `Union` with multiple models, sometimes there isn't a single uniform field
across all models that you can use as a discriminator.
This is the perfect use case for a callable `Discriminator`.

!!! tip
    When you're designing callable discriminators, remember that you might have to account
    for both `dict` and model type inputs. This pattern is similar to that of `mode='before'` validators,
    where you have to anticipate various forms of input.

    But wait! You ask, I only anticipate passing in `dict` types, why do I need to account for models?
    Pydantic uses callable discriminators for serialization as well, at which point the input to your callable is
    very likely to be a model instance.

    In the following examples, you'll see that the callable discriminators are designed to handle both `dict` and model inputs.
    If you don't follow this practice, it's likely that you'll, in the best case, get warnings during serialization,
    and in the worst case, get runtime errors during validation.

```python
from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Discriminator, Tag


class Pie(BaseModel):
    time_to_cook: int
    num_ingredients: int


class ApplePie(Pie):
    fruit: Literal['apple'] = 'apple'


class PumpkinPie(Pie):
    filling: Literal['pumpkin'] = 'pumpkin'


def get_discriminator_value(v: Any) -> str:
    if isinstance(v, dict):
        return v.get('fruit', v.get('filling'))
    return getattr(v, 'fruit', getattr(v, 'filling', None))


class ThanksgivingDinner(BaseModel):
    dessert: Annotated[
        Union[
            Annotated[ApplePie, Tag('apple')],
            Annotated[PumpkinPie, Tag('pumpkin')],
        ],
        Discriminator(get_discriminator_value),
    ]


apple_variation = ThanksgivingDinner.model_validate(
    {'dessert': {'fruit': 'apple', 'time_to_cook': 60, 'num_ingredients': 8}}
)
print(repr(apple_variation))
"""
ThanksgivingDinner(dessert=ApplePie(time_to_cook=60, num_ingredients=8, fruit='apple'))
"""

pumpkin_variation = ThanksgivingDinner.model_validate(
    {
        'dessert': {
            'filling': 'pumpkin',
            'time_to_cook': 40,
            'num_ingredients': 6,
        }
    }
)
print(repr(pumpkin_variation))
"""
ThanksgivingDinner(dessert=PumpkinPie(time_to_cook=40, num_ingredients=6, filling='pumpkin'))
"""
```

`Discriminator`s can also be used to validate `Union` types with combinations of models and primitive types.

For example:

```python
from typing import Annotated, Any, Union

from pydantic import BaseModel, Discriminator, Tag, ValidationError


def model_x_discriminator(v: Any) -> str:
    if isinstance(v, int):
        return 'int'
    if isinstance(v, (dict, BaseModel)):
        return 'model'
    else:
        # return None if the discriminator value isn't found
        return None


class SpecialValue(BaseModel):
    value: int


class DiscriminatedModel(BaseModel):
    value: Annotated[
        Union[
            Annotated[int, Tag('int')],
            Annotated['SpecialValue', Tag('model')],
        ],
        Discriminator(model_x_discriminator),
    ]


model_data = {'value': {'value': 1}}
m = DiscriminatedModel.model_validate(model_data)
print(m)
#> value=SpecialValue(value=1)

int_data = {'value': 123}
m = DiscriminatedModel.model_validate(int_data)
print(m)
#> value=123

try:
    DiscriminatedModel.model_validate({'value': 'not an int or a model'})
except ValidationError as e:
    print(e)  # (1)!
    """
    1 validation error for DiscriminatedModel
    value
      Unable to extract tag using discriminator model_x_discriminator() [type=union_tag_not_found, input_value='not an int or a model', input_type=str]
    """
```

1. Notice the callable discriminator function returns `None` if a discriminator value is not found.
   When `None` is returned, this `union_tag_not_found` error is raised.

!!! note
    Using the [annotated pattern](./fields.md#the-annotated-pattern) can be handy to regroup
    the `Union` and `discriminator` information. See the next example for more details.

    There are a few ways to set a discriminator for a field, all varying slightly in syntax.

    For `str` discriminators:

    ```python {lint="skip" test="skip"}
    some_field: Union[...] = Field(discriminator='my_discriminator')
    some_field: Annotated[Union[...], Field(discriminator='my_discriminator')]
    ```

    For callable `Discriminator`s:

    ```python {lint="skip" test="skip"}
    some_field: Union[...] = Field(discriminator=Discriminator(...))
    some_field: Annotated[Union[...], Discriminator(...)]
    some_field: Annotated[Union[...], Field(discriminator=Discriminator(...))]
    ```

!!! warning
    Discriminated unions cannot be used with only a single variant, such as `Union[Cat]`.

    Python changes `Union[T]` into `T` at interpretation time, so it is not possible for `pydantic` to
    distinguish fields of `Union[T]` from `T`.

### Nested Discriminated Unions

Only one discriminator can be set for a field but sometimes you want to combine multiple discriminators.
You can do it by creating nested `Annotated` types, e.g.:

```python
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, ValidationError


class BlackCat(BaseModel):
    pet_type: Literal['cat']
    color: Literal['black']
    black_name: str


class WhiteCat(BaseModel):
    pet_type: Literal['cat']
    color: Literal['white']
    white_name: str


Cat = Annotated[Union[BlackCat, WhiteCat], Field(discriminator='color')]


class Dog(BaseModel):
    pet_type: Literal['dog']
    name: str


Pet = Annotated[Union[Cat, Dog], Field(discriminator='pet_type')]


class Model(BaseModel):
    pet: Pet
    n: int


m = Model(pet={'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'}, n=1)
print(m)
#> pet=BlackCat(pet_type='cat', color='black', black_name='felix') n=1
try:
    Model(pet={'pet_type': 'cat', 'color': 'red'}, n='1')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    pet.cat
      Input tag 'red' found using 'color' does not match any of the expected tags: 'black', 'white' [type=union_tag_invalid, input_value={'pet_type': 'cat', 'color': 'red'}, input_type=dict]
    """
try:
    Model(pet={'pet_type': 'cat', 'color': 'black'}, n='1')
except ValidationError as e:
    print(e)
    """
    1 validation error for Model
    pet.cat.black.black_name
      Field required [type=missing, input_value={'pet_type': 'cat', 'color': 'black'}, input_type=dict]
    """
```

!!! tip
    If you want to validate data against a union, and solely a union, you can use pydantic's [`TypeAdapter`](../concepts/type_adapter.md) construct instead of inheriting from the standard `BaseModel`.

    In the context of the previous example, we have the following:

    ```python {lint="skip" test="skip"}
    type_adapter = TypeAdapter(Pet)

    pet = type_adapter.validate_python(
        {'pet_type': 'cat', 'color': 'black', 'black_name': 'felix'}
    )
    print(repr(pet))
    #> BlackCat(pet_type='cat', color='black', black_name='felix')
    ```

## Union Validation Errors

When `Union` validation fails, error messages can be quite verbose, as they will produce validation errors for
each case in the union.
This is especially noticeable when dealing with recursive models, where reasons may be generated at each level of
recursion.
Discriminated unions help to simplify error messages in this case, as validation errors are only produced for
the case with a matching discriminator value.

You can also customize the error type, message, and context for a `Discriminator` by passing
these specifications as parameters to the `Discriminator` constructor, as seen in the example below.

```python
from typing import Annotated, Union

from pydantic import BaseModel, Discriminator, Tag, ValidationError


# Errors are quite verbose with a normal Union:
class Model(BaseModel):
    x: Union[str, 'Model']


try:
    Model.model_validate({'x': {'x': {'x': 1}}})
except ValidationError as e:
    print(e)
    """
    4 validation errors for Model
    x.str
      Input should be a valid string [type=string_type, input_value={'x': {'x': 1}}, input_type=dict]
    x.Model.x.str
      Input should be a valid string [type=string_type, input_value={'x': 1}, input_type=dict]
    x.Model.x.Model.x.str
      Input should be a valid string [type=string_type, input_value=1, input_type=int]
    x.Model.x.Model.x.Model
      Input should be a valid dictionary or instance of Model [type=model_type, input_value=1, input_type=int]
    """

try:
    Model.model_validate({'x': {'x': {'x': {}}}})
except ValidationError as e:
    print(e)
    """
    4 validation errors for Model
    x.str
      Input should be a valid string [type=string_type, input_value={'x': {'x': {}}}, input_type=dict]
    x.Model.x.str
      Input should be a valid string [type=string_type, input_value={'x': {}}, input_type=dict]
    x.Model.x.Model.x.str
      Input should be a valid string [type=string_type, input_value={}, input_type=dict]
    x.Model.x.Model.x.Model.x
      Field required [type=missing, input_value={}, input_type=dict]
    """


# Errors are much simpler with a discriminated union:
def model_x_discriminator(v):
    if isinstance(v, str):
        return 'str'
    if isinstance(v, (dict, BaseModel)):
        return 'model'


class DiscriminatedModel(BaseModel):
    x: Annotated[
        Union[
            Annotated[str, Tag('str')],
            Annotated['DiscriminatedModel', Tag('model')],
        ],
        Discriminator(
            model_x_discriminator,
            custom_error_type='invalid_union_member',  # (1)!
            custom_error_message='Invalid union member',  # (2)!
            custom_error_context={'discriminator': 'str_or_model'},  # (3)!
        ),
    ]


try:
    DiscriminatedModel.model_validate({'x': {'x': {'x': 1}}})
except ValidationError as e:
    print(e)
    """
    1 validation error for DiscriminatedModel
    x.model.x.model.x
      Invalid union member [type=invalid_union_member, input_value=1, input_type=int]
    """

try:
    DiscriminatedModel.model_validate({'x': {'x': {'x': {}}}})
except ValidationError as e:
    print(e)
    """
    1 validation error for DiscriminatedModel
    x.model.x.model.x.model.x
      Field required [type=missing, input_value={}, input_type=dict]
    """

# The data is still handled properly when valid:
data = {'x': {'x': {'x': 'a'}}}
m = DiscriminatedModel.model_validate(data)
print(m.model_dump())
#> {'x': {'x': {'x': 'a'}}}
```

1. `custom_error_type` is the `type` attribute of the `ValidationError` raised when validation fails.
2. `custom_error_message` is the `msg` attribute of the `ValidationError` raised when validation fails.
3. `custom_error_context` is the `ctx` attribute of the `ValidationError` raised when validation fails.

You can also simplify error messages by labeling each case with a [`Tag`][pydantic.types.Tag].
This is especially useful when you have complex types like those in this example:

```python
from typing import Annotated, Union

from pydantic import AfterValidator, Tag, TypeAdapter, ValidationError

DoubledList = Annotated[list[int], AfterValidator(lambda x: x * 2)]
StringsMap = dict[str, str]


# Not using any `Tag`s for each union case, the errors are not so nice to look at
adapter = TypeAdapter(Union[DoubledList, StringsMap])

try:
    adapter.validate_python(['a'])
except ValidationError as exc_info:
    print(exc_info)
    """
    2 validation errors for union[function-after[<lambda>(), list[int]],dict[str,str]]
    function-after[<lambda>(), list[int]].0
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    dict[str,str]
      Input should be a valid dictionary [type=dict_type, input_value=['a'], input_type=list]
    """

tag_adapter = TypeAdapter(
    Union[
        Annotated[DoubledList, Tag('DoubledList')],
        Annotated[StringsMap, Tag('StringsMap')],
    ]
)

try:
    tag_adapter.validate_python(['a'])
except ValidationError as exc_info:
    print(exc_info)
    """
    2 validation errors for union[DoubledList,StringsMap]
    DoubledList.0
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='a', input_type=str]
    StringsMap
      Input should be a valid dictionary [type=dict_type, input_value=['a'], input_type=list]
    """
```
````

## File: docs/concepts/validation_decorator.md
````markdown
??? api "API Documentation"
    [`pydantic.validate_call_decorator.validate_call`][pydantic.validate_call_decorator.validate_call]<br>

The [`validate_call()`][pydantic.validate_call] decorator allows the arguments passed to a function to be parsed
and validated using the function's annotations before the function is called.

While under the hood this uses the same approach of model creation and initialisation
(see [Validators](validators.md) for more details), it provides an extremely easy way to apply validation
to your code with minimal boilerplate.

Example of usage:

```python
from pydantic import ValidationError, validate_call


@validate_call
def repeat(s: str, count: int, *, separator: bytes = b'') -> bytes:
    b = s.encode()
    return separator.join(b for _ in range(count))


a = repeat('hello', 3)
print(a)
#> b'hellohellohello'

b = repeat('x', '4', separator=b' ')
print(b)
#> b'x x x x'

try:
    c = repeat('hello', 'wrong')
except ValidationError as exc:
    print(exc)
    """
    1 validation error for repeat
    1
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='wrong', input_type=str]
    """
```

## Parameter types

Parameter types are inferred from type annotations on the function, or as [`Any`][typing.Any] if not annotated. All types listed in [types](types.md) can be validated, including Pydantic models and [custom types](types.md#custom-types).
As with the rest of Pydantic, types are by default coerced by the decorator before they're passed to the actual function:

```python
from datetime import date

from pydantic import validate_call


@validate_call
def greater_than(d1: date, d2: date, *, include_equal=False) -> date:  # (1)!
    if include_equal:
        return d1 >= d2
    else:
        return d1 > d2


d1 = '2000-01-01'  # (2)!
d2 = date(2001, 1, 1)
greater_than(d1, d2, include_equal=True)
```

1. Because `include_equal` has no type annotation, it will be inferred as [`Any`][typing.Any].
2. Although `d1` is a string, it will be converted to a [`date`][datetime.date] object.

Type coercion like this can be extremely helpful, but also confusing or not desired (see [model data conversion](models.md#data-conversion)). [Strict mode](strict_mode.md)
can be enabled by using a [custom configuration](#custom-configuration).

!!! note "Validating the return value"
    By default, the return value of the function is **not** validated. To do so, the `validate_return` argument
    of the decorator can be set to `True`.

## Function signatures

The [`validate_call()`][pydantic.validate_call] decorator is designed to work with functions
using all possible [parameter configurations][parameter] and all possible combinations of these:

* Positional or keyword parameters with or without defaults.
* Keyword-only parameters: parameters after `*,`.
* Positional-only parameters: parameters before `, /`.
* Variable positional parameters defined via `*` (often `*args`).
* Variable keyword parameters defined via `**` (often `**kwargs`).

??? example

    ```python
    from pydantic import validate_call


    @validate_call
    def pos_or_kw(a: int, b: int = 2) -> str:
        return f'a={a} b={b}'


    print(pos_or_kw(1, b=3))
    #> a=1 b=3


    @validate_call
    def kw_only(*, a: int, b: int = 2) -> str:
        return f'a={a} b={b}'


    print(kw_only(a=1))
    #> a=1 b=2
    print(kw_only(a=1, b=3))
    #> a=1 b=3


    @validate_call
    def pos_only(a: int, b: int = 2, /) -> str:
        return f'a={a} b={b}'


    print(pos_only(1))
    #> a=1 b=2


    @validate_call
    def var_args(*args: int) -> str:
        return str(args)


    print(var_args(1))
    #> (1,)
    print(var_args(1, 2, 3))
    #> (1, 2, 3)


    @validate_call
    def var_kwargs(**kwargs: int) -> str:
        return str(kwargs)


    print(var_kwargs(a=1))
    #> {'a': 1}
    print(var_kwargs(a=1, b=2))
    #> {'a': 1, 'b': 2}


    @validate_call
    def armageddon(
        a: int,
        /,
        b: int,
        *c: int,
        d: int,
        e: int = None,
        **f: int,
    ) -> str:
        return f'a={a} b={b} c={c} d={d} e={e} f={f}'


    print(armageddon(1, 2, d=3))
    #> a=1 b=2 c=() d=3 e=None f={}
    print(armageddon(1, 2, 3, 4, 5, 6, d=8, e=9, f=10, spam=11))
    #> a=1 b=2 c=(3, 4, 5, 6) d=8 e=9 f={'f': 10, 'spam': 11}
    ```

!!! note "[`Unpack`][typing.Unpack] for keyword parameters"
    [`Unpack`][typing.Unpack] and typed dictionaries can be used to annotate the variable
    keyword parameters of a function:

    ```python
    from typing_extensions import TypedDict, Unpack

    from pydantic import validate_call


    class Point(TypedDict):
        x: int
        y: int


    @validate_call
    def add_coords(**kwargs: Unpack[Point]) -> int:
        return kwargs['x'] + kwargs['y']


    add_coords(x=1, y=2)
    ```

    For reference, see the [related specification section] and [PEP 692].

    [related specification section]: https://typing.readthedocs.io/en/latest/spec/callables.html#unpack-for-keyword-arguments
    [PEP 692]: https://peps.python.org/pep-0692/

## Using the [`Field()`][pydantic.Field] function to describe function parameters

The [`Field()` function](fields.md) can also be used with the decorator to provide extra information about
the field and validations. If you don't make use of the `default` or `default_factory` parameter, it is
recommended to use the [annotated pattern](./fields.md#the-annotated-pattern) (so that type checkers
infer the parameter as being required). Otherwise, the [`Field()`][pydantic.Field] function can be used
as a default value (again, to trick type checkers into thinking a default value is provided for the parameter).

```python
from typing import Annotated

from pydantic import Field, ValidationError, validate_call


@validate_call
def how_many(num: Annotated[int, Field(gt=10)]):
    return num


try:
    how_many(1)
except ValidationError as e:
    print(e)
    """
    1 validation error for how_many
    0
      Input should be greater than 10 [type=greater_than, input_value=1, input_type=int]
    """


@validate_call
def return_value(value: str = Field(default='default value')):
    return value


print(return_value())
#> default value
```

[Aliases](fields.md#field-aliases) can be used with the decorator as normal:

```python
from typing import Annotated

from pydantic import Field, validate_call


@validate_call
def how_many(num: Annotated[int, Field(gt=10, alias='number')]):
    return num


how_many(number=42)
```

## Accessing the original function

The original function which was decorated can still be accessed by using the `raw_function` attribute.
This is useful if in some scenarios you trust your input arguments and want to call the function in the most efficient way (see [notes on performance](#performance) below):

```python
from pydantic import validate_call


@validate_call
def repeat(s: str, count: int, *, separator: bytes = b'') -> bytes:
    b = s.encode()
    return separator.join(b for _ in range(count))


a = repeat('hello', 3)
print(a)
#> b'hellohellohello'

b = repeat.raw_function('good bye', 2, separator=b', ')
print(b)
#> b'good bye, good bye'
```

## Async functions

[`validate_call()`][pydantic.validate_call] can also be used on async functions:

```python
class Connection:
    async def execute(self, sql, *args):
        return 'testing@example.com'


conn = Connection()
# ignore-above
import asyncio

from pydantic import PositiveInt, ValidationError, validate_call


@validate_call
async def get_user_email(user_id: PositiveInt):
    # `conn` is some fictional connection to a database
    email = await conn.execute('select email from users where id=$1', user_id)
    if email is None:
        raise RuntimeError('user not found')
    else:
        return email


async def main():
    email = await get_user_email(123)
    print(email)
    #> testing@example.com
    try:
        await get_user_email(-4)
    except ValidationError as exc:
        print(exc.errors())
        """
        [
            {
                'type': 'greater_than',
                'loc': (0,),
                'msg': 'Input should be greater than 0',
                'input': -4,
                'ctx': {'gt': 0},
                'url': 'https://errors.pydantic.dev/2/v/greater_than',
            }
        ]
        """


asyncio.run(main())
# requires: `conn.execute()` that will return `'testing@example.com'`
```

## Compatibility with type checkers

As the [`validate_call()`][pydantic.validate_call] decorator preserves the decorated function's signature,
it should be compatible with type checkers (such as mypy and pyright). However, due to current limitations in the Python type system,
the [`raw_function`](#accessing-the-original-function) or other attributes won't be recognized and you will
need to suppress the error using (usually with a `# type: ignore` comment).

## Custom configuration

Similarly to Pydantic models, the `config` parameter of the decorator can be used to specify a custom configuration:

```python
from pydantic import ConfigDict, ValidationError, validate_call


class Foobar:
    def __init__(self, v: str):
        self.v = v

    def __add__(self, other: 'Foobar') -> str:
        return f'{self} + {other}'

    def __str__(self) -> str:
        return f'Foobar({self.v})'


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def add_foobars(a: Foobar, b: Foobar):
    return a + b


c = add_foobars(Foobar('a'), Foobar('b'))
print(c)
#> Foobar(a) + Foobar(b)

try:
    add_foobars(1, 2)
except ValidationError as e:
    print(e)
    """
    2 validation errors for add_foobars
    0
      Input should be an instance of Foobar [type=is_instance_of, input_value=1, input_type=int]
    1
      Input should be an instance of Foobar [type=is_instance_of, input_value=2, input_type=int]
    """
```

## Extension — validating arguments before calling a function

In some cases, it may be helpful to separate validation of a function's arguments from the function call itself.
This might be useful when a particular function is costly/time consuming.

Here's an example of a workaround you can use for that pattern:

```python
from pydantic import validate_call


@validate_call
def validate_foo(a: int, b: int):
    def foo():
        return a + b

    return foo


foo = validate_foo(a=1, b=2)
print(foo())
#> 3
```

## Limitations

### Validation exception

Currently upon validation failure, a standard Pydantic [`ValidationError`][pydantic_core.ValidationError] is raised
(see [model error handling](models.md#error-handling) for details). This is also true for missing required arguments,
where Python normally raises a [`TypeError`][].

### Performance

We've made a big effort to make Pydantic as performant as possible. While the inspection of the decorated
function is only performed once, there will still be a performance impact when making calls to the function
compared to using the original function.

In many situations, this will have little or no noticeable effect. However, be aware that
[`validate_call()`][pydantic.validate_call] is not an equivalent or alternative to function
definitions in strongly typed languages, and it never will be.
````

## File: docs/concepts/validators.md
````markdown
In addition to Pydantic's [built-in validation capabilities](./fields.md#field-constraints),
you can leverage custom validators at the field and model levels to enforce more complex constraints
and ensure the integrity of your data.

!!! tip
    Want to quickly jump to the relevant validator section?

    <div class="grid cards" markdown>

    *   Field validators

        ---

        * [field *after* validators](#field-after-validator)
        * [field *before* validators](#field-before-validator)
        * [field *plain* validators](#field-plain-validator)
        * [field *wrap* validators](#field-wrap-validator)

    *   Model validators

        ---

        * [model *before* validators](#model-before-validator)
        * [model *after* validators](#model-after-validator)
        * [model *wrap* validators](#model-wrap-validator)

    </div>

## Field validators

??? api "API Documentation"
    [`pydantic.functional_validators.WrapValidator`][pydantic.functional_validators.WrapValidator]<br>
    [`pydantic.functional_validators.PlainValidator`][pydantic.functional_validators.PlainValidator]<br>
    [`pydantic.functional_validators.BeforeValidator`][pydantic.functional_validators.BeforeValidator]<br>
    [`pydantic.functional_validators.AfterValidator`][pydantic.functional_validators.AfterValidator]<br>
    [`pydantic.functional_validators.field_validator`][pydantic.functional_validators.field_validator]<br>

In its simplest form, a field validator is a callable taking the value to be validated as an argument and
**returning the validated value**. The callable can perform checks for specific conditions (see
[raising validation errors](#raising-validation-errors)) and make changes to the validated value (coercion or mutation).

**Four** different types of validators can be used. They can all be defined using the
[annotated pattern](./fields.md#the-annotated-pattern) or using the
[`field_validator()`][pydantic.field_validator] decorator, applied on a [class method][classmethod]:

* ***After* validators**: run after Pydantic's internal validation. They are generally more type safe and thus easier to implement.
{#field-after-validator}

    === "Annotated pattern"

        Here is an example of a validator performing a validation check, and returning the value unchanged.

        ```python
        from typing import Annotated

        from pydantic import AfterValidator, BaseModel, ValidationError


        def is_even(value: int) -> int:
            if value % 2 == 1:
                raise ValueError(f'{value} is not an even number')
            return value  # (1)!


        class Model(BaseModel):
            number: Annotated[int, AfterValidator(is_even)]


        try:
            Model(number=1)
        except ValidationError as err:
            print(err)
            """
            1 validation error for Model
            number
              Value error, 1 is not an even number [type=value_error, input_value=1, input_type=int]
            """
        ```

        1. Note that it is important to return the validated value.

    === "Decorator"

        Here is an example of a validator performing a validation check, and returning the value unchanged,
        this time using the [`field_validator()`][pydantic.field_validator] decorator.

        ```python
        from pydantic import BaseModel, ValidationError, field_validator


        class Model(BaseModel):
            number: int

            @field_validator('number', mode='after')  # (1)!
            @classmethod
            def is_even(cls, value: int) -> int:
                if value % 2 == 1:
                    raise ValueError(f'{value} is not an even number')
                return value  # (2)!


        try:
            Model(number=1)
        except ValidationError as err:
            print(err)
            """
            1 validation error for Model
            number
              Value error, 1 is not an even number [type=value_error, input_value=1, input_type=int]
            """
        ```

        1. `'after'` is the default mode for the decorator, and can be omitted.
        2. Note that it is important to return the validated value.

    ??? example "Example mutating the value"
        Here is an example of a validator making changes to the validated value (no exception is raised).

        === "Annotated pattern"

            ```python
            from typing import Annotated

            from pydantic import AfterValidator, BaseModel


            def double_number(value: int) -> int:
                return value * 2


            class Model(BaseModel):
                number: Annotated[int, AfterValidator(double_number)]


            print(Model(number=2))
            #> number=4
            ```

        === "Decorator"

            ```python
            from pydantic import BaseModel, field_validator


            class Model(BaseModel):
                number: int

                @field_validator('number', mode='after')  # (1)!
                @classmethod
                def double_number(cls, value: int) -> int:
                    return value * 2


            print(Model(number=2))
            #> number=4
            ```

            1. `'after'` is the default mode for the decorator, and can be omitted.

* ***Before* validators**: run before Pydantic's internal parsing and validation (e.g. coercion of a `str` to an `int`).
  These are more flexible than [*after* validators](#field-after-validator), but they also have to deal with the raw input, which
  in theory could be any arbitrary object. You should also avoid mutating the value directly if you are raising a
  [validation error](#raising-validation-errors) later in your validator function, as the mutated value may be passed to other
  validators if using [unions](./unions.md).
  {#field-before-validator}

    The value returned from this callable is then validated against the provided type annotation by Pydantic.

    === "Annotated pattern"

        ```python
        from typing import Annotated, Any

        from pydantic import BaseModel, BeforeValidator, ValidationError


        def ensure_list(value: Any) -> Any:  # (1)!
            if not isinstance(value, list):  # (2)!
                return [value]
            else:
                return value


        class Model(BaseModel):
            numbers: Annotated[list[int], BeforeValidator(ensure_list)]


        print(Model(numbers=2))
        #> numbers=[2]
        try:
            Model(numbers='str')
        except ValidationError as err:
            print(err)  # (3)!
            """
            1 validation error for Model
            numbers.0
              Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='str', input_type=str]
            """
        ```

        1. Notice the use of [`Any`][typing.Any] as a type hint for `value`. *Before* validators take the raw input, which
           can be anything.

        2. Note that you might want to check for other sequence types (such as tuples) that would normally successfully
           validate against the `list` type. *Before* validators give you more flexibility, but you have to account for
           every possible case.

        3. Pydantic still performs validation against the `int` type, no matter if our `ensure_list` validator
           did operations on the original input type.

    === "Decorator"

        ```python
        from typing import Any

        from pydantic import BaseModel, ValidationError, field_validator


        class Model(BaseModel):
            numbers: list[int]

            @field_validator('numbers', mode='before')
            @classmethod
            def ensure_list(cls, value: Any) -> Any:  # (1)!
                if not isinstance(value, list):  # (2)!
                    return [value]
                else:
                    return value


        print(Model(numbers=2))
        #> numbers=[2]
        try:
            Model(numbers='str')
        except ValidationError as err:
            print(err)  # (3)!
            """
            1 validation error for Model
            numbers.0
              Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='str', input_type=str]
            """
        ```

        1. Notice the use of [`Any`][typing.Any] as a type hint for `value`. *Before* validators take the raw input, which
           can be anything.

        2. Note that you might want to check for other sequence types (such as tuples) that would normally successfully
           validate against the `list` type. *Before* validators give you more flexibility, but you have to account for
           every possible case.

        3. Pydantic still performs validation against the `int` type, no matter if our `ensure_list` validator
           did operations on the original input type.

* ***Plain* validators**: act similarly to *before* validators but they **terminate validation immediately** after returning,
  so no further validators are called and Pydantic does not do any of its internal validation against the field type.
  {#field-plain-validator}

    === "Annotated pattern"

        ```python
        from typing import Annotated, Any

        from pydantic import BaseModel, PlainValidator


        def val_number(value: Any) -> Any:
            if isinstance(value, int):
                return value * 2
            else:
                return value


        class Model(BaseModel):
            number: Annotated[int, PlainValidator(val_number)]


        print(Model(number=4))
        #> number=8
        print(Model(number='invalid'))  # (1)!
        #> number='invalid'
        ```

        1. Although `'invalid'` shouldn't validate against the `int` type, Pydantic accepts the input.

    === "Decorator"

        ```python
        from typing import Any

        from pydantic import BaseModel, field_validator


        class Model(BaseModel):
            number: int

            @field_validator('number', mode='plain')
            @classmethod
            def val_number(cls, value: Any) -> Any:
                if isinstance(value, int):
                    return value * 2
                else:
                    return value


        print(Model(number=4))
        #> number=8
        print(Model(number='invalid'))  # (1)!
        #> number='invalid'
        ```

        1. Although `'invalid'` shouldn't validate against the `int` type, Pydantic accepts the input.

* ***Wrap* validators**: are the most flexible of all. You can run code before or after Pydantic and other validators
  process the input, or you can terminate validation immediately, either by returning the value early or by raising an
  error.
  {#field-wrap-validator}

    Such validators must be defined with a **mandatory** extra *handler* parameter: a callable taking the value to be validated
    as an argument. Internally, this handler will delegate validation of the value to Pydantic. You are free to wrap the call
    to the handler in a [`try..except`][handling exceptions] block, or not call it at all.

    [handling exceptions]: https://docs.python.org/3/tutorial/errors.html#handling-exceptions

    === "Annotated pattern"

        ```python {lint="skip"}
        from typing import Any

        from typing import Annotated

        from pydantic import BaseModel, Field, ValidationError, ValidatorFunctionWrapHandler, WrapValidator


        def truncate(value: Any, handler: ValidatorFunctionWrapHandler) -> str:
            try:
                return handler(value)
            except ValidationError as err:
                if err.errors()[0]['type'] == 'string_too_long':
                    return handler(value[:5])
                else:
                    raise


        class Model(BaseModel):
            my_string: Annotated[str, Field(max_length=5), WrapValidator(truncate)]


        print(Model(my_string='abcde'))
        #> my_string='abcde'
        print(Model(my_string='abcdef'))
        #> my_string='abcde'
        ```

    === "Decorator"

        ```python {lint="skip"}
        from typing import Any

        from typing import Annotated

        from pydantic import BaseModel, Field, ValidationError, ValidatorFunctionWrapHandler, field_validator


        class Model(BaseModel):
            my_string: Annotated[str, Field(max_length=5)]

            @field_validator('my_string', mode='wrap')
            @classmethod
            def truncate(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> str:
                try:
                    return handler(value)
                except ValidationError as err:
                    if err.errors()[0]['type'] == 'string_too_long':
                        return handler(value[:5])
                    else:
                        raise


        print(Model(my_string='abcde'))
        #> my_string='abcde'
        print(Model(my_string='abcdef'))
        #> my_string='abcde'
        ```

!!! note "Validation of default values"
    As mentioned in the [fields documentation](./fields.md#validate-default-values), default values of fields
    are *not* validated unless configured to do so, and thus custom validators will not be applied as well.

### Which validator pattern to use

While both approaches can achieve the same thing, each pattern provides different benefits.

#### Using the annotated pattern

One of the key benefits of using the [annotated pattern](./fields.md#the-annotated-pattern) is to make
validators reusable:

```python
from typing import Annotated

from pydantic import AfterValidator, BaseModel


def is_even(value: int) -> int:
    if value % 2 == 1:
        raise ValueError(f'{value} is not an even number')
    return value


EvenNumber = Annotated[int, AfterValidator(is_even)]


class Model1(BaseModel):
    my_number: EvenNumber


class Model2(BaseModel):
    other_number: Annotated[EvenNumber, AfterValidator(lambda v: v + 2)]


class Model3(BaseModel):
    list_of_even_numbers: list[EvenNumber]  # (1)!
```

1. As mentioned in the [annotated pattern](./fields.md#the-annotated-pattern) documentation,
   we can also make use of validators for specific parts of the annotation (in this case,
   validation is applied for list items, but not the whole list).

It is also easier to understand which validators are applied to a type, by just looking at the field annotation.

#### Using the decorator pattern

One of the key benefits of using the [`field_validator()`][pydantic.field_validator] decorator is to apply
the function to multiple fields:

```python
from pydantic import BaseModel, field_validator


class Model(BaseModel):
    f1: str
    f2: str

    @field_validator('f1', 'f2', mode='before')
    @classmethod
    def capitalize(cls, value: str) -> str:
        return value.capitalize()
```

Here are a couple additional notes about the decorator usage:

* If you want the validator to apply to all fields (including the ones defined in subclasses), you can pass
  `'*'` as the field name argument.
* By default, the decorator will ensure the provided field name(s) are defined on the model. If you want to
  disable this check during class creation, you can do so by passing `False` to the `check_fields` argument.
  This is useful when the field validator is defined on a base class, and the field is expected to exist on
  subclasses.

## Model validators

??? api "API Documentation"
    [`pydantic.functional_validators.model_validator`][pydantic.functional_validators.model_validator]<br>

Validation can also be performed on the entire model's data using the [`model_validator()`][pydantic.model_validator]
decorator.

**Three** different types of model validators can be used:

* ***After* validators**: run after the whole model has been validated. As such, they are defined as
  *instance* methods and can be seen as post-initialization hooks. Important note: the validated instance
  should be returned.
  {#model-after-validator}

    ```python
    from typing_extensions import Self

    from pydantic import BaseModel, model_validator


    class UserModel(BaseModel):
        username: str
        password: str
        password_repeat: str

        @model_validator(mode='after')
        def check_passwords_match(self) -> Self:
            if self.password != self.password_repeat:
                raise ValueError('Passwords do not match')
            return self
    ```

* ***Before* validators**: are run before the model is instantiated. These are more flexible than *after* validators,
  but they also have to deal with the raw input, which in theory could be any arbitrary object. You should also avoid
  mutating the value directly if you are raising a [validation error](#raising-validation-errors) later in your validator
  function, as the mutated value may be passed to other validators if using [unions](./unions.md).
  {#model-before-validator}

    ```python
    from typing import Any

    from pydantic import BaseModel, model_validator


    class UserModel(BaseModel):
        username: str

        @model_validator(mode='before')
        @classmethod
        def check_card_number_not_present(cls, data: Any) -> Any:  # (1)!
            if isinstance(data, dict):  # (2)!
                if 'card_number' in data:
                    raise ValueError("'card_number' should not be included")
            return data
    ```

    1. Notice the use of [`Any`][typing.Any] as a type hint for `data`. *Before* validators take the raw input, which
       can be anything.
    2. Most of the time, the input data will be a dictionary (e.g. when calling `UserModel(username='...')`). However,
       this is not always the case. For instance, if the [`from_attributes`][pydantic.ConfigDict.from_attributes]
       configuration value is set, you might receive an arbitrary class instance for the `data` argument.

* ***Wrap* validators**: are the most flexible of all. You can run code before or after Pydantic and
  other validators process the input data, or you can terminate validation immediately, either by returning
  the data early or by raising an error.
  {#model-wrap-validator}

    ```python {lint="skip"}
    import logging
    from typing import Any

    from typing_extensions import Self

    from pydantic import BaseModel, ModelWrapValidatorHandler, ValidationError, model_validator


    class UserModel(BaseModel):
        username: str

        @model_validator(mode='wrap')
        @classmethod
        def log_failed_validation(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
            try:
                return handler(data)
            except ValidationError:
                logging.error('Model %s failed to validate with data %s', cls, data)
                raise
    ```

!!! note "On inheritance"
    A model validator defined in a base class will be called during the validation of a subclass instance.

    Overriding a model validator in a subclass will override the base class' validator, and thus only the subclass' version of said validator will be called.

## Raising validation errors

To raise a validation error, three types of exceptions can be used:

* [`ValueError`][]: this is the most common exception raised inside validators.
* [`AssertionError`][]: using the [assert][] statement also works, but be aware that these statements
  are skipped when Python is run with the [-O][] optimization flag.
* [`PydanticCustomError`][pydantic_core.PydanticCustomError]: a bit more verbose, but provides extra flexibility:

    ```python
    from pydantic_core import PydanticCustomError

    from pydantic import BaseModel, ValidationError, field_validator


    class Model(BaseModel):
        x: int

        @field_validator('x', mode='after')
        @classmethod
        def validate_x(cls, v: int) -> int:
            if v % 42 == 0:
                raise PydanticCustomError(
                    'the_answer_error',
                    '{number} is the answer!',
                    {'number': v},
                )
            return v


    try:
        Model(x=42 * 2)
    except ValidationError as e:
        print(e)
        """
        1 validation error for Model
        x
          84 is the answer! [type=the_answer_error, input_value=84, input_type=int]
        """
    ```

## Validation info

Both the field and model validators callables (in all modes) can optionally take an extra
[`ValidationInfo`][pydantic.ValidationInfo] argument, providing useful extra information, such as:

* [already validated data](#validation-data)
* [user defined context](#validation-context)
* the current validation mode: either `'python'` or `'json'` (see the [`mode`][pydantic.ValidationInfo.mode] property)
* the current field name, if using a [field validator](#field-validators) (see the [`field_name`][pydantic.ValidationInfo.field_name] property).

### Validation data

For field validators, the already validated data can be accessed using the [`data`][pydantic.ValidationInfo.data]
property. Here is an example than can be used as an alternative to the [*after* model validator](#model-after-validator)
example:

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class UserModel(BaseModel):
    password: str
    password_repeat: str
    username: str

    @field_validator('password_repeat', mode='after')
    @classmethod
    def check_passwords_match(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data['password']:
            raise ValueError('Passwords do not match')
        return value
```

!!! warning
    As validation is performed in the [order fields are defined](./models.md#field-ordering), you have to
    make sure you are not accessing a field that hasn't been validated yet. In the code above, for example,
    the `username` validated value is not available yet, as it is defined *after* `password_repeat`.

The [`data`][pydantic.ValidationInfo.data] property is `None` for [model validators](#model-validators).

### Validation context

You can pass a context object to the [validation methods](./models.md#validating-data), which can be accessed
inside the validator functions using the [`context`][pydantic.ValidationInfo.context] property:

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class Model(BaseModel):
    text: str

    @field_validator('text', mode='after')
    @classmethod
    def remove_stopwords(cls, v: str, info: ValidationInfo) -> str:
        if isinstance(info.context, dict):
            stopwords = info.context.get('stopwords', set())
            v = ' '.join(w for w in v.split() if w.lower() not in stopwords)
        return v


data = {'text': 'This is an example document'}
print(Model.model_validate(data))  # no context
#> text='This is an example document'
print(Model.model_validate(data, context={'stopwords': ['this', 'is', 'an']}))
#> text='example document'
```

Similarly, you can [use a context for serialization](../concepts/serialization.md#serialization-context).

??? note "Providing context when directly instantiating a model"
    It is currently not possible to provide a context when directly instantiating a model
    (i.e. when calling `Model(...)`). You can work around this through the use of a
    [`ContextVar`][contextvars.ContextVar] and a custom `__init__` method:

    ```python
    from __future__ import annotations

    from contextlib import contextmanager
    from contextvars import ContextVar
    from typing import Any, Generator

    from pydantic import BaseModel, ValidationInfo, field_validator

    _init_context_var = ContextVar('_init_context_var', default=None)


    @contextmanager
    def init_context(value: dict[str, Any]) -> Generator[None]:
        token = _init_context_var.set(value)
        try:
            yield
        finally:
            _init_context_var.reset(token)


    class Model(BaseModel):
        my_number: int

        def __init__(self, /, **data: Any) -> None:
            self.__pydantic_validator__.validate_python(
                data,
                self_instance=self,
                context=_init_context_var.get(),
            )

        @field_validator('my_number')
        @classmethod
        def multiply_with_context(cls, value: int, info: ValidationInfo) -> int:
            if isinstance(info.context, dict):
                multiplier = info.context.get('multiplier', 1)
                value = value * multiplier
            return value


    print(Model(my_number=2))
    #> my_number=2

    with init_context({'multiplier': 3}):
        print(Model(my_number=2))
        #> my_number=6

    print(Model(my_number=2))
    #> my_number=2
    ```

## Ordering of validators

When using the [annotated pattern](#using-the-annotated-pattern), the order in which validators are applied
is defined as follows: [*before*](#field-before-validator) and [*wrap*](#field-wrap-validator) validators
are run from right to left, and [*after*](#field-after-validator) validators are then run from left to right:

```python {lint="skip" test="skip"}
from pydantic import AfterValidator, BaseModel, BeforeValidator, WrapValidator


class Model(BaseModel):
    name: Annotated[
        str,
        AfterValidator(runs_3rd),
        AfterValidator(runs_4th),
        BeforeValidator(runs_2nd),
        WrapValidator(runs_1st),
    ]
```

Internally, validators defined using [the decorator](#using-the-decorator-pattern) are converted to their annotated
form counterpart and added last after the existing metadata for the field. This means that the same ordering
logic applies.

## Special types

Pydantic provides a few special utilities that can be used to customize validation.

* [`InstanceOf`][pydantic.functional_validators.InstanceOf] can be used to validate that a value is an instance of a given class.

    ```python
    from pydantic import BaseModel, InstanceOf, ValidationError


    class Fruit:
        def __repr__(self):
            return self.__class__.__name__


    class Banana(Fruit): ...


    class Apple(Fruit): ...


    class Basket(BaseModel):
        fruits: list[InstanceOf[Fruit]]


    print(Basket(fruits=[Banana(), Apple()]))
    #> fruits=[Banana, Apple]
    try:
        Basket(fruits=[Banana(), 'Apple'])
    except ValidationError as e:
        print(e)
        """
        1 validation error for Basket
        fruits.1
          Input should be an instance of Fruit [type=is_instance_of, input_value='Apple', input_type=str]
        """
    ```

* [`SkipValidation`][pydantic.functional_validators.SkipValidation] can be used to skip validation on a field.

    ```python
    from pydantic import BaseModel, SkipValidation


    class Model(BaseModel):
        names: list[SkipValidation[str]]


    m = Model(names=['foo', 'bar'])
    print(m)
    #> names=['foo', 'bar']

    m = Model(names=['foo', 123])  # (1)!
    print(m)
    #> names=['foo', 123]
    ```

    1. Note that the validation of the second item is skipped. If it has the wrong type it will emit a
       warning during serialization.

* [`PydanticUseDefault`][pydantic_core.PydanticUseDefault] can be used to notify Pydantic that the default value
  should be used.

    ```python
    from typing import Annotated, Any

    from pydantic_core import PydanticUseDefault

    from pydantic import BaseModel, BeforeValidator


    def default_if_none(value: Any) -> Any:
        if value is None:
            raise PydanticUseDefault()
        return value


    class Model(BaseModel):
        name: Annotated[str, BeforeValidator(default_if_none)] = 'default_name'


    print(Model(name=None))
    #> name='default_name'
    ```

## JSON Schema and field validators

When using [*before*](#field-before-validator), [*plain*](#field-plain-validator) or [*wrap*](#field-wrap-validator)
field validators, the accepted input type may be different from the field annotation.

Consider the following example:

```python
from typing import Any

from pydantic import BaseModel, field_validator


class Model(BaseModel):
    value: str

    @field_validator('value', mode='before')
    @classmethod
    def cast_ints(cls, value: Any) -> Any:
        if isinstance(value, int):
            return str(value)
        else:
            return value


print(Model(value='a'))
#> value='a'
print(Model(value=1))
#> value='1'
```

While the type hint for `value` is `str`, the `cast_ints` validator also allows integers. To specify the correct
input type, the `json_schema_input_type` argument can be provided:

```python
from typing import Any, Union

from pydantic import BaseModel, field_validator


class Model(BaseModel):
    value: str

    @field_validator(
        'value', mode='before', json_schema_input_type=Union[int, str]
    )
    @classmethod
    def cast_ints(cls, value: Any) -> Any:
        if isinstance(value, int):
            return str(value)
        else:
            return value


print(Model.model_json_schema()['properties']['value'])
#> {'anyOf': [{'type': 'integer'}, {'type': 'string'}], 'title': 'Value'}
```

As a convenience, Pydantic will use the field type if the argument is not provided (unless you are using
a [*plain*](#field-plain-validator) validator, in which case `json_schema_input_type` defaults to
[`Any`][typing.Any] as the field type is completely discarded).
````

## File: docs/errors/errors.md
````markdown
Pydantic will raise a [`ValidationError`][pydantic_core.ValidationError] whenever it finds an error in the data it's validating.

!!! note
    Validation code should not raise the [`ValidationError`][pydantic_core.ValidationError] itself,
    but rather raise a [`ValueError`][] or a [`AssertionError`][] (or subclass thereof) which will
    be caught and used to populate the final [`ValidationError`][pydantic_core.ValidationError].

    For more details, refer to the [dedicated section](../concepts/validators.md#raising-validation-errors)
    of the validators documentation.

That [`ValidationError`][pydantic_core.ValidationError] will contain information about all the errors and how they happened.

You can access these errors in several ways:

| Method                                                       | Description                                                                                    |
|--------------------------------------------------------------|------------------------------------------------------------------------------------------------|
| [`errors()`][pydantic_core.ValidationError.errors]           | Returns a list of [`ErrorDetails`][pydantic_core.ErrorDetails] errors found in the input data. |
| [`error_count()`][pydantic_core.ValidationError.error_count] | Returns the number of errors.                                                                  |
| [`json()`][pydantic_core.ValidationError.json]               | Returns a JSON representation of the list errors.                                              |
| `str(e)`                                                     | Returns a human-readable representation of the errors.                                         |

The [`ErrorDetails`][pydantic_core.ErrorDetails] object is a dictionary. It contains the following:

| Property                                    | Description                                                                    |
|---------------------------------------------|--------------------------------------------------------------------------------|
| [`ctx`][pydantic_core.ErrorDetails.ctx]     | An optional object which contains values required to render the error message. |
| [`input`][pydantic_core.ErrorDetails.input] | The input provided for validation.                                             |
| [`loc`][pydantic_core.ErrorDetails.loc]     | The error's location as a list.                                                |
| [`msg`][pydantic_core.ErrorDetails.msg]     | A human-readable explanation of the error.                                     |
| [`type`][pydantic_core.ErrorDetails.type]   | A computer-readable identifier of the error type.                              |
| [`url`][pydantic_core.ErrorDetails.url]     | The documentation URL giving information about the error.                      |

The first item in the [`loc`][pydantic_core.ErrorDetails.loc] list will be the field where the error occurred, and if the field is a
[sub-model](../concepts/models.md#nested-models), subsequent items will be present to indicate the nested location of the error.

As a demonstration:

```python
from pydantic import BaseModel, Field, ValidationError, field_validator


class Location(BaseModel):
    lat: float = 0.1
    lng: float = 10.1


class Model(BaseModel):
    is_required: float
    gt_int: int = Field(gt=42)
    list_of_ints: list[int]
    a_float: float
    recursive_model: Location

    @field_validator('a_float', mode='after')
    @classmethod
    def validate_float(cls, value: float) -> float:
        if value > 2.0:
            raise ValueError('Invalid float value')
        return value


data = {
    'list_of_ints': ['1', 2, 'bad'],
    'a_float': 3.0,
    'recursive_model': {'lat': 4.2, 'lng': 'New York'},
    'gt_int': 21,
}

try:
    Model(**data)
except ValidationError as e:
    print(e)
    """
    5 validation errors for Model
    is_required
      Field required [type=missing, input_value={'list_of_ints': ['1', 2,...ew York'}, 'gt_int': 21}, input_type=dict]
    gt_int
      Input should be greater than 42 [type=greater_than, input_value=21, input_type=int]
    list_of_ints.2
      Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='bad', input_type=str]
    a_float
      Value error, Invalid float value [type=value_error, input_value=3.0, input_type=float]
    recursive_model.lng
      Input should be a valid number, unable to parse string as a number [type=float_parsing, input_value='New York', input_type=str]
    """

try:
    Model(**data)
except ValidationError as e:
    print(e.errors())
    """
    [
        {
            'type': 'missing',
            'loc': ('is_required',),
            'msg': 'Field required',
            'input': {
                'list_of_ints': ['1', 2, 'bad'],
                'a_float': 3.0,
                'recursive_model': {'lat': 4.2, 'lng': 'New York'},
                'gt_int': 21,
            },
            'url': 'https://errors.pydantic.dev/2/v/missing',
        },
        {
            'type': 'greater_than',
            'loc': ('gt_int',),
            'msg': 'Input should be greater than 42',
            'input': 21,
            'ctx': {'gt': 42},
            'url': 'https://errors.pydantic.dev/2/v/greater_than',
        },
        {
            'type': 'int_parsing',
            'loc': ('list_of_ints', 2),
            'msg': 'Input should be a valid integer, unable to parse string as an integer',
            'input': 'bad',
            'url': 'https://errors.pydantic.dev/2/v/int_parsing',
        },
        {
            'type': 'value_error',
            'loc': ('a_float',),
            'msg': 'Value error, Invalid float value',
            'input': 3.0,
            'ctx': {'error': ValueError('Invalid float value')},
            'url': 'https://errors.pydantic.dev/2/v/value_error',
        },
        {
            'type': 'float_parsing',
            'loc': ('recursive_model', 'lng'),
            'msg': 'Input should be a valid number, unable to parse string as a number',
            'input': 'New York',
            'url': 'https://errors.pydantic.dev/2/v/float_parsing',
        },
    ]
    """
```

## Error messages

Pydantic attempts to provide useful default error messages for validation and usage errors, which can be found here:

* [Validation Errors](validation_errors.md): Errors that happen during data validation.
* [Usage Errors](usage_errors.md): Errors that happen when using Pydantic.

### Customize error messages

You can customize error messages by creating a custom error handler.

```python
from pydantic_core import ErrorDetails

from pydantic import BaseModel, HttpUrl, ValidationError

CUSTOM_MESSAGES = {
    'int_parsing': 'This is not an integer! 🤦',
    'url_scheme': 'Hey, use the right URL scheme! I wanted {expected_schemes}.',
}


def convert_errors(
    e: ValidationError, custom_messages: dict[str, str]
) -> list[ErrorDetails]:
    new_errors: list[ErrorDetails] = []
    for error in e.errors():
        custom_message = custom_messages.get(error['type'])
        if custom_message:
            ctx = error.get('ctx')
            error['msg'] = (
                custom_message.format(**ctx) if ctx else custom_message
            )
        new_errors.append(error)
    return new_errors


class Model(BaseModel):
    a: int
    b: HttpUrl


try:
    Model(a='wrong', b='ftp://example.com')
except ValidationError as e:
    errors = convert_errors(e, CUSTOM_MESSAGES)
    print(errors)
    """
    [
        {
            'type': 'int_parsing',
            'loc': ('a',),
            'msg': 'This is not an integer! 🤦',
            'input': 'wrong',
            'url': 'https://errors.pydantic.dev/2/v/int_parsing',
        },
        {
            'type': 'url_scheme',
            'loc': ('b',),
            'msg': "Hey, use the right URL scheme! I wanted 'http' or 'https'.",
            'input': 'ftp://example.com',
            'ctx': {'expected_schemes': "'http' or 'https'"},
            'url': 'https://errors.pydantic.dev/2/v/url_scheme',
        },
    ]
    """
```

A common use case would be to translate error messages. For example, in the above example,
we could translate the error messages replacing the `CUSTOM_MESSAGES` dictionary with a
dictionary of translations.

Another example is customizing the way that the `'loc'` value of an error is represented.

```python
from typing import Any, Union

from pydantic import BaseModel, ValidationError


def loc_to_dot_sep(loc: tuple[Union[str, int], ...]) -> str:
    path = ''
    for i, x in enumerate(loc):
        if isinstance(x, str):
            if i > 0:
                path += '.'
            path += x
        elif isinstance(x, int):
            path += f'[{x}]'
        else:
            raise TypeError('Unexpected type')
    return path


def convert_errors(e: ValidationError) -> list[dict[str, Any]]:
    new_errors: list[dict[str, Any]] = e.errors()
    for error in new_errors:
        error['loc'] = loc_to_dot_sep(error['loc'])
    return new_errors


class TestNestedModel(BaseModel):
    key: str
    value: str


class TestModel(BaseModel):
    items: list[TestNestedModel]


data = {'items': [{'key': 'foo', 'value': 'bar'}, {'key': 'baz'}]}

try:
    TestModel.model_validate(data)
except ValidationError as e:
    print(e.errors())  # (1)!
    """
    [
        {
            'type': 'missing',
            'loc': ('items', 1, 'value'),
            'msg': 'Field required',
            'input': {'key': 'baz'},
            'url': 'https://errors.pydantic.dev/2/v/missing',
        }
    ]
    """
    pretty_errors = convert_errors(e)
    print(pretty_errors)  # (2)!
    """
    [
        {
            'type': 'missing',
            'loc': 'items[1].value',
            'msg': 'Field required',
            'input': {'key': 'baz'},
            'url': 'https://errors.pydantic.dev/2/v/missing',
        }
    ]
    """
```

1. By default, `e.errors()` produces a list of errors with `loc` values that take the form of tuples.
2. With our custom `loc_to_dot_sep` function, we've modified the form of the `loc` representation.
````

## File: docs/errors/usage_errors.md
````markdown
Pydantic attempts to provide useful errors. The following sections provide details on common errors developers may
encounter when working with Pydantic, along with suggestions for addressing the error condition.

## Class not fully defined {#class-not-fully-defined}

This error is raised when a type referenced in an annotation of a pydantic-validated type
(such as a subclass of `BaseModel`, or a pydantic `dataclass`) is not defined:

```python
from typing import ForwardRef

from pydantic import BaseModel, PydanticUserError

UndefinedType = ForwardRef('UndefinedType')


class Foobar(BaseModel):
    a: UndefinedType


try:
    Foobar(a=1)
except PydanticUserError as exc_info:
    assert exc_info.code == 'class-not-fully-defined'
```

Or when the type has been defined after usage:

```python
from typing import Optional

from pydantic import BaseModel, PydanticUserError


class Foo(BaseModel):
    a: Optional['Bar'] = None


try:
    # this doesn't work, see raised error
    foo = Foo(a={'b': {'a': None}})
except PydanticUserError as exc_info:
    assert exc_info.code == 'class-not-fully-defined'


class Bar(BaseModel):
    b: 'Foo'


# this works, though
foo = Foo(a={'b': {'a': None}})
```

For BaseModel subclasses, it can be fixed by defining the type and then calling `.model_rebuild()`:

```python
from typing import Optional

from pydantic import BaseModel


class Foo(BaseModel):
    a: Optional['Bar'] = None


class Bar(BaseModel):
    b: 'Foo'


Foo.model_rebuild()

foo = Foo(a={'b': {'a': None}})
```

In other cases, the error message should indicate how to rebuild the class with the appropriate type defined.

## Custom JSON Schema {#custom-json-schema}

The `__modify_schema__` method is no longer supported in V2. You should use the `__get_pydantic_json_schema__` method instead.

The `__modify_schema__` used to receive a single argument representing the JSON schema. See the example below:

```python {title="Old way"}
from pydantic import BaseModel, PydanticUserError

try:

    class Model(BaseModel):
        @classmethod
        def __modify_schema__(cls, field_schema):
            field_schema.update(examples=['example'])

except PydanticUserError as exc_info:
    assert exc_info.code == 'custom-json-schema'
```

The new method `__get_pydantic_json_schema__` receives two arguments: the first is a dictionary denoted as `CoreSchema`,
and the second a callable `handler` that receives a `CoreSchema` as parameter, and returns a JSON schema. See the example
below:

```python {title="New way"}
from typing import Any

from pydantic_core import CoreSchema

from pydantic import BaseModel, GetJsonSchemaHandler


class Model(BaseModel):
    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> dict[str, Any]:
        json_schema = super().__get_pydantic_json_schema__(core_schema, handler)
        json_schema = handler.resolve_ref_schema(json_schema)
        json_schema.update(examples=['example'])
        return json_schema


print(Model.model_json_schema())
"""
{'examples': ['example'], 'properties': {}, 'title': 'Model', 'type': 'object'}
"""
```

## Decorator on missing field {#decorator-missing-field}

This error is raised when you define a decorator with a field that is not valid.

```python
from typing import Any

from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: str

        @field_validator('b')
        def check_b(cls, v: Any):
            return v

except PydanticUserError as exc_info:
    assert exc_info.code == 'decorator-missing-field'
```

You can use `check_fields=False` if you're inheriting from the model and intended this.

```python
from typing import Any

from pydantic import BaseModel, create_model, field_validator


class Model(BaseModel):
    @field_validator('a', check_fields=False)
    def check_a(cls, v: Any):
        return v


model = create_model('FooModel', a=(str, 'cake'), __base__=Model)
```

## Discriminator no field {#discriminator-no-field}

This error is raised when a model in discriminated unions doesn't define a discriminator field.

```python
from typing import Literal, Union

from pydantic import BaseModel, Field, PydanticUserError


class Cat(BaseModel):
    c: str


class Dog(BaseModel):
    pet_type: Literal['dog']
    d: str


try:

    class Model(BaseModel):
        pet: Union[Cat, Dog] = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-no-field'
```

## Discriminator alias type {#discriminator-alias-type}

This error is raised when you define a non-string alias on a discriminator field.

```python
from typing import Literal, Union

from pydantic import AliasChoices, BaseModel, Field, PydanticUserError


class Cat(BaseModel):
    pet_type: Literal['cat'] = Field(
        validation_alias=AliasChoices('Pet', 'PET')
    )
    c: str


class Dog(BaseModel):
    pet_type: Literal['dog']
    d: str


try:

    class Model(BaseModel):
        pet: Union[Cat, Dog] = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-alias-type'
```

## Discriminator needs literal {#discriminator-needs-literal}

This error is raised when you define a non-`Literal` type on a discriminator field.

```python
from typing import Literal, Union

from pydantic import BaseModel, Field, PydanticUserError


class Cat(BaseModel):
    pet_type: int
    c: str


class Dog(BaseModel):
    pet_type: Literal['dog']
    d: str


try:

    class Model(BaseModel):
        pet: Union[Cat, Dog] = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-needs-literal'
```

## Discriminator alias {#discriminator-alias}

This error is raised when you define different aliases on discriminator fields.

```python
from typing import Literal, Union

from pydantic import BaseModel, Field, PydanticUserError


class Cat(BaseModel):
    pet_type: Literal['cat'] = Field(validation_alias='PET')
    c: str


class Dog(BaseModel):
    pet_type: Literal['dog'] = Field(validation_alias='Pet')
    d: str


try:

    class Model(BaseModel):
        pet: Union[Cat, Dog] = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-alias'
```

## Invalid discriminator validator {#discriminator-validator}

This error is raised when you use a before, wrap, or plain validator on a discriminator field.

This is disallowed because the discriminator field is used to determine the type of the model to use for validation,
so you can't use a validator that might change its value.

```python
from typing import Literal, Union

from pydantic import BaseModel, Field, PydanticUserError, field_validator


class Cat(BaseModel):
    pet_type: Literal['cat']

    @field_validator('pet_type', mode='before')
    @classmethod
    def validate_pet_type(cls, v):
        if v == 'kitten':
            return 'cat'
        return v


class Dog(BaseModel):
    pet_type: Literal['dog']


try:

    class Model(BaseModel):
        pet: Union[Cat, Dog] = Field(discriminator='pet_type')
        number: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'discriminator-validator'
```

This can be worked around by using a standard `Union`, dropping the discriminator:

```python
from typing import Literal, Union

from pydantic import BaseModel, field_validator


class Cat(BaseModel):
    pet_type: Literal['cat']

    @field_validator('pet_type', mode='before')
    @classmethod
    def validate_pet_type(cls, v):
        if v == 'kitten':
            return 'cat'
        return v


class Dog(BaseModel):
    pet_type: Literal['dog']


class Model(BaseModel):
    pet: Union[Cat, Dog]


assert Model(pet={'pet_type': 'kitten'}).pet.pet_type == 'cat'
```

## Callable discriminator case with no tag {#callable-discriminator-no-tag}

This error is raised when a `Union` that uses a callable `Discriminator` doesn't have `Tag` annotations for all cases.

```python
from typing import Annotated, Union

from pydantic import BaseModel, Discriminator, PydanticUserError, Tag


def model_x_discriminator(v):
    if isinstance(v, str):
        return 'str'
    if isinstance(v, (dict, BaseModel)):
        return 'model'


# tag missing for both union choices
try:

    class DiscriminatedModel(BaseModel):
        x: Annotated[
            Union[str, 'DiscriminatedModel'],
            Discriminator(model_x_discriminator),
        ]

except PydanticUserError as exc_info:
    assert exc_info.code == 'callable-discriminator-no-tag'

# tag missing for `'DiscriminatedModel'` union choice
try:

    class DiscriminatedModel(BaseModel):
        x: Annotated[
            Union[Annotated[str, Tag('str')], 'DiscriminatedModel'],
            Discriminator(model_x_discriminator),
        ]

except PydanticUserError as exc_info:
    assert exc_info.code == 'callable-discriminator-no-tag'

# tag missing for `str` union choice
try:

    class DiscriminatedModel(BaseModel):
        x: Annotated[
            Union[str, Annotated['DiscriminatedModel', Tag('model')]],
            Discriminator(model_x_discriminator),
        ]

except PydanticUserError as exc_info:
    assert exc_info.code == 'callable-discriminator-no-tag'
```

## `TypedDict` version {#typed-dict-version}

This error is raised when you use [typing.TypedDict][]
instead of `typing_extensions.TypedDict` on Python < 3.12.

## Model parent field overridden {#model-field-overridden}

This error is raised when a field defined on a base class was overridden by a non-annotated attribute.

```python
from pydantic import BaseModel, PydanticUserError


class Foo(BaseModel):
    a: float


try:

    class Bar(Foo):
        x: float = 12.3
        a = 123.0

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-field-overridden'
```

## Model field missing annotation {#model-field-missing-annotation}

This error is raised when a field doesn't have an annotation.

```python
from pydantic import BaseModel, Field, PydanticUserError

try:

    class Model(BaseModel):
        a = Field('foobar')
        b = None

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-field-missing-annotation'
```

If the field is not meant to be a field, you may be able to resolve the error
by annotating it as a `ClassVar`:

```python
from typing import ClassVar

from pydantic import BaseModel


class Model(BaseModel):
    a: ClassVar[str]
```

Or updating `model_config['ignored_types']`:

```python
from pydantic import BaseModel, ConfigDict


class IgnoredType:
    pass


class MyModel(BaseModel):
    model_config = ConfigDict(ignored_types=(IgnoredType,))

    _a = IgnoredType()
    _b: int = IgnoredType()
    _c: IgnoredType
    _d: IgnoredType = IgnoredType()
```

## `Config` and `model_config` both defined {#config-both}

This error is raised when `class Config` and `model_config` are used together.

```python
from pydantic import BaseModel, ConfigDict, PydanticUserError

try:

    class Model(BaseModel):
        model_config = ConfigDict(from_attributes=True)

        a: str

        class Config:
            from_attributes = True

except PydanticUserError as exc_info:
    assert exc_info.code == 'config-both'
```

## Keyword arguments removed {#removed-kwargs}

This error is raised when the keyword arguments are not available in Pydantic V2.

For example, `regex` is removed from Pydantic V2:

```python
from pydantic import BaseModel, Field, PydanticUserError

try:

    class Model(BaseModel):
        x: str = Field(regex='test')

except PydanticUserError as exc_info:
    assert exc_info.code == 'removed-kwargs'
```

## Circular reference schema {#circular-reference-schema}

This error is raised when a circular reference is found that would otherwise result in an infinite recursion.

For example, this is a valid type alias:

```python {test="skip" lint="skip" upgrade="skip"}
type A = list[A] | None
```

while these are not:

```python {test="skip" lint="skip" upgrade="skip"}
type A = A

type B = C
type C = B
```

## JSON schema invalid type {#invalid-for-json-schema}

This error is raised when Pydantic fails to generate a JSON schema for some `CoreSchema`.

```python
from pydantic import BaseModel, ImportString, PydanticUserError


class Model(BaseModel):
    a: ImportString


try:
    Model.model_json_schema()
except PydanticUserError as exc_info:
    assert exc_info.code == 'invalid-for-json-schema'
```

## JSON schema already used {#json-schema-already-used}

This error is raised when the JSON schema generator has already been used to generate a JSON schema.
You must create a new instance to generate a new JSON schema.

## BaseModel instantiated {#base-model-instantiated}

This error is raised when you instantiate `BaseModel` directly. Pydantic models should inherit from `BaseModel`.

```python
from pydantic import BaseModel, PydanticUserError

try:
    BaseModel()
except PydanticUserError as exc_info:
    assert exc_info.code == 'base-model-instantiated'
```

## Undefined annotation {#undefined-annotation}

This error is raised when handling undefined annotations during `CoreSchema` generation.

```python
from pydantic import BaseModel, PydanticUndefinedAnnotation


class Model(BaseModel):
    a: 'B'  # noqa F821


try:
    Model.model_rebuild()
except PydanticUndefinedAnnotation as exc_info:
    assert exc_info.code == 'undefined-annotation'
```

## Schema for unknown type {#schema-for-unknown-type}

This error is raised when Pydantic fails to generate a `CoreSchema` for some type.

```python
from pydantic import BaseModel, PydanticUserError

try:

    class Model(BaseModel):
        x: 43 = 123

except PydanticUserError as exc_info:
    assert exc_info.code == 'schema-for-unknown-type'
```

## Import error {#import-error}

This error is raised when you try to import an object that was available in Pydantic V1, but has been removed in
Pydantic V2.

See the [Migration Guide](../migration.md) for more information.

## `create_model` field definitions {#create-model-field-definitions}

This error is raised when you provide invalid field definitions in [`create_model()`][pydantic.create_model].

```python
from pydantic import PydanticUserError, create_model

try:
    create_model('FooModel', foo=(str, 'default value', 'more'))
except PydanticUserError as exc_info:
    assert exc_info.code == 'create-model-field-definitions'
```

The fields definition syntax can be found in the [dynamic model creation](../concepts/models.md#dynamic-model-creation) documentation.

## Validator with no fields {#validator-no-fields}

This error is raised when you use validator bare (with no fields).

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: str

        @field_validator
        def checker(cls, v):
            return v

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-no-fields'
```

Validators should be used with fields and keyword arguments.

```python
from pydantic import BaseModel, field_validator


class Model(BaseModel):
    a: str

    @field_validator('a')
    def checker(cls, v):
        return v
```

## Invalid validator fields {#validator-invalid-fields}

This error is raised when you use a validator with non-string fields.

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: str
        b: str

        @field_validator(['a', 'b'])
        def check_fields(cls, v):
            return v

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-invalid-fields'
```

Fields should be passed as separate string arguments:

```python
from pydantic import BaseModel, field_validator


class Model(BaseModel):
    a: str
    b: str

    @field_validator('a', 'b')
    def check_fields(cls, v):
        return v
```

## Validator on instance method {#validator-instance-method}

This error is raised when you apply a validator on an instance method.

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: int = 1

        @field_validator('a')
        def check_a(self, value):
            return value

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-instance-method'
```

## `json_schema_input_type` used with the wrong mode {#validator-input-type}

This error is raised when you explicitly specify a value for the `json_schema_input_type`
argument and `mode` isn't set to either `'before'`, `'plain'` or `'wrap'`.

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: int = 1

        @field_validator('a', mode='after', json_schema_input_type=int)
        @classmethod
        def check_a(self, value):
            return value

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-input-type'
```

Documenting the JSON Schema input type is only possible for validators where the given
value can be anything. That is why it isn't available for `after` validators, where
the value is first validated against the type annotation.

## Root validator, `pre`, `skip_on_failure` {#root-validator-pre-skip}

If you use `@root_validator` with `pre=False` (the default) you MUST specify `skip_on_failure=True`.
The `skip_on_failure=False` option is no longer available.

If you were not trying to set `skip_on_failure=False`, you can safely set `skip_on_failure=True`.
If you do, this root validator will no longer be called if validation fails for any of the fields.

Please see the [Migration Guide](../migration.md) for more details.

## `model_serializer` instance methods {#model-serializer-instance-method}

`@model_serializer` must be applied to instance methods.

This error is raised when you apply `model_serializer` on an instance method without `self`:

```python
from pydantic import BaseModel, PydanticUserError, model_serializer

try:

    class MyModel(BaseModel):
        a: int

        @model_serializer
        def _serialize(slf, x, y, z):
            return slf

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-serializer-instance-method'
```

Or on a class method:

```python
from pydantic import BaseModel, PydanticUserError, model_serializer

try:

    class MyModel(BaseModel):
        a: int

        @model_serializer
        @classmethod
        def _serialize(self, x, y, z):
            return self

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-serializer-instance-method'
```

## `validator`, `field`, `config`, and `info` {#validator-field-config-info}

The `field` and `config` parameters are not available in Pydantic V2.
Please use the `info` parameter instead.

You can access the configuration via `info.config`,
but it is a dictionary instead of an object like it was in Pydantic V1.

The `field` argument is no longer available.

## Pydantic V1 validator signature {#validator-v1-signature}

This error is raised when you use an unsupported signature for Pydantic V1-style validator.

```python
import warnings

from pydantic import BaseModel, PydanticUserError, validator

warnings.filterwarnings('ignore', category=DeprecationWarning)

try:

    class Model(BaseModel):
        a: int

        @validator('a')
        def check_a(cls, value, foo):
            return value

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-v1-signature'
```

## Unrecognized `field_validator` signature {#validator-signature}

This error is raised when a `field_validator` or `model_validator` function has the wrong signature.

```python
from pydantic import BaseModel, PydanticUserError, field_validator

try:

    class Model(BaseModel):
        a: str

        @field_validator('a')
        @classmethod
        def check_a(cls):
            return 'a'

except PydanticUserError as exc_info:
    assert exc_info.code == 'validator-signature'
```

## Unrecognized `field_serializer` signature {#field-serializer-signature}

This error is raised when the `field_serializer` function has the wrong signature.

```python
from pydantic import BaseModel, PydanticUserError, field_serializer

try:

    class Model(BaseModel):
        x: int

        @field_serializer('x')
        def no_args():
            return 'x'

except PydanticUserError as exc_info:
    assert exc_info.code == 'field-serializer-signature'
```

Valid field serializer signatures are:

```python {test="skip" lint="skip" upgrade="skip"}
from pydantic import FieldSerializationInfo, SerializerFunctionWrapHandler, field_serializer

# an instance method with the default mode or `mode='plain'`
@field_serializer('x')  # or @field_serializer('x', mode='plain')
def ser_x(self, value: Any, info: FieldSerializationInfo): ...

# a static method or function with the default mode or `mode='plain'`
@field_serializer('x')  # or @field_serializer('x', mode='plain')
@staticmethod
def ser_x(value: Any, info: FieldSerializationInfo): ...

# equivalent to
def ser_x(value: Any, info: FieldSerializationInfo): ...
serializer('x')(ser_x)

# an instance method with `mode='wrap'`
@field_serializer('x', mode='wrap')
def ser_x(self, value: Any, nxt: SerializerFunctionWrapHandler, info: FieldSerializationInfo): ...

# a static method or function with `mode='wrap'`
@field_serializer('x', mode='wrap')
@staticmethod
def ser_x(value: Any, nxt: SerializerFunctionWrapHandler, info: FieldSerializationInfo): ...

# equivalent to
def ser_x(value: Any, nxt: SerializerFunctionWrapHandler, info: FieldSerializationInfo): ...
serializer('x')(ser_x)

# For all of these, you can also choose to omit the `info` argument, for example:
@field_serializer('x')
def ser_x(self, value: Any): ...

@field_serializer('x', mode='wrap')
def ser_x(self, value: Any, handler: SerializerFunctionWrapHandler): ...
```

## Unrecognized `model_serializer` signature {#model-serializer-signature}

This error is raised when the `model_serializer` function has the wrong signature.

```python
from pydantic import BaseModel, PydanticUserError, model_serializer

try:

    class MyModel(BaseModel):
        a: int

        @model_serializer
        def _serialize(self, x, y, z):
            return self

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-serializer-signature'
```

Valid model serializer signatures are:

```python {test="skip" lint="skip" upgrade="skip"}
from pydantic import SerializerFunctionWrapHandler, SerializationInfo, model_serializer

# an instance method with the default mode or `mode='plain'`
@model_serializer  # or model_serializer(mode='plain')
def mod_ser(self, info: SerializationInfo): ...

# an instance method with `mode='wrap'`
@model_serializer(mode='wrap')
def mod_ser(self, handler: SerializerFunctionWrapHandler, info: SerializationInfo):

# For all of these, you can also choose to omit the `info` argument, for example:
@model_serializer(mode='plain')
def mod_ser(self): ...

@model_serializer(mode='wrap')
def mod_ser(self, handler: SerializerFunctionWrapHandler): ...
```

## Multiple field serializers {#multiple-field-serializers}

This error is raised when multiple `model_serializer` functions are defined for a field.

```python
from pydantic import BaseModel, PydanticUserError, field_serializer

try:

    class MyModel(BaseModel):
        x: int
        y: int

        @field_serializer('x', 'y')
        def serializer1(v):
            return f'{v:,}'

        @field_serializer('x')
        def serializer2(v):
            return v

except PydanticUserError as exc_info:
    assert exc_info.code == 'multiple-field-serializers'
```

## Invalid annotated type {#invalid-annotated-type}

This error is raised when an annotation cannot annotate a type.

```python
from typing import Annotated

from pydantic import BaseModel, FutureDate, PydanticUserError

try:

    class Model(BaseModel):
        foo: Annotated[str, FutureDate()]

except PydanticUserError as exc_info:
    assert exc_info.code == 'invalid-annotated-type'
```

## `config` is unused with `TypeAdapter` {#type-adapter-config-unused}

You will get this error if you try to pass `config` to `TypeAdapter` when the type is a type that
has its own config that cannot be overridden (currently this is only `BaseModel`, `TypedDict` and `dataclass`):

```python
from typing_extensions import TypedDict

from pydantic import ConfigDict, PydanticUserError, TypeAdapter


class MyTypedDict(TypedDict):
    x: int


try:
    TypeAdapter(MyTypedDict, config=ConfigDict(strict=True))
except PydanticUserError as exc_info:
    assert exc_info.code == 'type-adapter-config-unused'
```

Instead you'll need to subclass the type and override or set the config on it:

```python
from typing_extensions import TypedDict

from pydantic import ConfigDict, TypeAdapter


class MyTypedDict(TypedDict):
    x: int

    # or `model_config = ...` for BaseModel
    __pydantic_config__ = ConfigDict(strict=True)


TypeAdapter(MyTypedDict)  # ok
```

## Cannot specify `model_config['extra']` with `RootModel` {#root-model-extra}

Because `RootModel` is not capable of storing or even accepting extra fields during initialization, we raise an error
if you try to specify a value for the config setting `'extra'` when creating a subclass of `RootModel`:

```python
from pydantic import PydanticUserError, RootModel

try:

    class MyRootModel(RootModel):
        model_config = {'extra': 'allow'}
        root: int

except PydanticUserError as exc_info:
    assert exc_info.code == 'root-model-extra'
```

## Cannot evaluate type annotation {#unevaluable-type-annotation}

Because type annotations are evaluated *after* assignments, you might get unexpected results when using a type annotation name
that clashes with one of your fields. We raise an error in the following case:

```python {test="skip"}
from datetime import date

from pydantic import BaseModel, Field


class Model(BaseModel):
    date: date = Field(description='A date')
```

As a workaround, you can either use an alias or change your import:

```python {lint="skip"}
import datetime
# Or `from datetime import date as _date`

from pydantic import BaseModel, Field


class Model(BaseModel):
    date: datetime.date = Field(description='A date')
```

## Incompatible `dataclass` `init` and `extra` settings {#dataclass-init-false-extra-allow}

Pydantic does not allow the specification of the `extra='allow'` setting on a dataclass
while any of the fields have `init=False` set.

Thus, you may not do something like the following:

```python {test="skip"}
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(extra='allow'))
class A:
    a: int = Field(init=False, default=1)
```

The above snippet results in the following error during schema building for the `A` dataclass:

```output
pydantic.errors.PydanticUserError: Field a has `init=False` and dataclass has config setting `extra="allow"`.
This combination is not allowed.
```

## Incompatible `init` and `init_var` settings on `dataclass` field {#clashing-init-and-init-var}

The `init=False` and `init_var=True` settings are mutually exclusive. Doing so results in the `PydanticUserError` shown in the example below.

```python {test="skip"}
from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass
class Foo:
    bar: str = Field(init=False, init_var=True)


"""
pydantic.errors.PydanticUserError: Dataclass field bar has init=False and init_var=True, but these are mutually exclusive.
"""
```

## `model_config` is used as a model field {#model-config-invalid-field-name}

This error is raised when `model_config` is used as the name of a field.

```python
from pydantic import BaseModel, PydanticUserError

try:

    class Model(BaseModel):
        model_config: str

except PydanticUserError as exc_info:
    assert exc_info.code == 'model-config-invalid-field-name'
```

## [`with_config`][pydantic.config.with_config] is used on a `BaseModel` subclass {#with-config-on-model}

This error is raised when the [`with_config`][pydantic.config.with_config] decorator is used on a class which is already a Pydantic model (use the `model_config` attribute instead).

```python
from pydantic import BaseModel, PydanticUserError, with_config

try:

    @with_config({'allow_inf_nan': True})
    class Model(BaseModel):
        bar: str

except PydanticUserError as exc_info:
    assert exc_info.code == 'with-config-on-model'
```

## `dataclass` is used on a `BaseModel` subclass {#dataclass-on-model}

This error is raised when the Pydantic `dataclass` decorator is used on a class which is already
a Pydantic model.

```python
from pydantic import BaseModel, PydanticUserError
from pydantic.dataclasses import dataclass

try:

    @dataclass
    class Model(BaseModel):
        bar: str

except PydanticUserError as exc_info:
    assert exc_info.code == 'dataclass-on-model'
```

## Unsupported type for `validate_call` {#validate-call-type}

`validate_call` has some limitations on the callables it can validate. This error is raised when you try to use it with an unsupported callable.
Currently the supported callables are functions (including lambdas, but not built-ins) and methods and instances of [`partial`][functools.partial].
In the case of [`partial`][functools.partial], the function being partially applied must be one of the supported callables.

### `@classmethod`, `@staticmethod`, and `@property`

These decorators must be put before `validate_call`.

```python
from pydantic import PydanticUserError, validate_call

# error
try:

    class A:
        @validate_call
        @classmethod
        def f1(cls): ...

except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-call-type'


# correct
@classmethod
@validate_call
def f2(cls): ...
```

### Classes

While classes are callables themselves, `validate_call` can't be applied on them, as it needs to know about which method to use (`__init__` or `__new__`) to fetch type annotations. If you want to validate the constructor of a class, you should put `validate_call` on top of the appropriate method instead.

```python
from pydantic import PydanticUserError, validate_call

# error
try:

    @validate_call
    class A1: ...

except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-call-type'


# correct
class A2:
    @validate_call
    def __init__(self): ...

    @validate_call
    def __new__(cls): ...
```

### Callable instances

Although instances can be callable by implementing a `__call__` method, currently the instances of these types cannot be validated with `validate_call`.
This may change in the future, but for now, you should use `validate_call` explicitly on `__call__` instead.

```python
from pydantic import PydanticUserError, validate_call

# error
try:

    class A1:
        def __call__(self): ...

    validate_call(A1())

except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-call-type'


# correct
class A2:
    @validate_call
    def __call__(self): ...
```

### Invalid signature

This is generally less common, but a possible reason is that you are trying to validate a method that doesn't have at least one argument (usually `self`).

```python
from pydantic import PydanticUserError, validate_call

try:

    class A:
        def f(): ...

    validate_call(A().f)
except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-call-type'
```

## [`Unpack`][typing.Unpack] used without a [`TypedDict`][typing.TypedDict] {#unpack-typed-dict}

This error is raised when [`Unpack`][typing.Unpack] is used with something other than
a [`TypedDict`][typing.TypedDict] class object to type hint variadic keyword parameters.

For reference, see the [related specification section] and [PEP 692].

```python
from typing_extensions import Unpack

from pydantic import PydanticUserError, validate_call

try:

    @validate_call
    def func(**kwargs: Unpack[int]):
        pass

except PydanticUserError as exc_info:
    assert exc_info.code == 'unpack-typed-dict'
```

## Overlapping unpacked [`TypedDict`][typing.TypedDict] fields and arguments {#overlapping-unpack-typed-dict}

This error is raised when the typed dictionary used to type hint variadic keywords parameters has field names
overlapping with other parameters (unless [positional only][positional-only_parameter]).

For reference, see the [related specification section] and [PEP 692].

```python
from typing_extensions import TypedDict, Unpack

from pydantic import PydanticUserError, validate_call


class TD(TypedDict):
    a: int


try:

    @validate_call
    def func(a: int, **kwargs: Unpack[TD]):
        pass

except PydanticUserError as exc_info:
    assert exc_info.code == 'overlapping-unpack-typed-dict'
```

[related specification section]: https://typing.readthedocs.io/en/latest/spec/callables.html#unpack-for-keyword-arguments
[PEP 692]: https://peps.python.org/pep-0692/

## Invalid `Self` type {#invalid-self-type}

Currently, [`Self`][typing.Self] can only be used to annotate a field of a class (specifically, subclasses of [`BaseModel`][pydantic.BaseModel], [`NamedTuple`][typing.NamedTuple], [`TypedDict`][typing.TypedDict], or dataclasses). Attempting to use [`Self`][typing.Self] in any other ways will raise this error.

```python
from typing_extensions import Self

from pydantic import PydanticUserError, validate_call

try:

    @validate_call
    def func(self: Self):
        pass

except PydanticUserError as exc_info:
    assert exc_info.code == 'invalid-self-type'
```

The following example of [`validate_call()`][pydantic.validate_call] will also raise this error, even though it is correct from a type-checking perspective. This may be supported in the future.

```python
from typing_extensions import Self

from pydantic import BaseModel, PydanticUserError, validate_call

try:

    class A(BaseModel):
        @validate_call
        def func(self, arg: Self):
            pass

except PydanticUserError as exc_info:
    assert exc_info.code == 'invalid-self-type'
```

## `validate_by_alias` and `validate_by_name` both set to `False` {#validate-by-alias-and-name-false}

This error is raised when you set `validate_by_alias` and `validate_by_name` to `False` in the configuration.

This is not allowed because it would make it impossible to populate attributes.

```python
from pydantic import BaseModel, ConfigDict, Field, PydanticUserError

try:

    class Model(BaseModel):
        a: int = Field(alias='A')

        model_config = ConfigDict(
            validate_by_alias=False, validate_by_name=False
        )

except PydanticUserError as exc_info:
    assert exc_info.code == 'validate-by-alias-and-name-false'
```
````

## File: docs/errors/validation_errors.md
````markdown
Pydantic attempts to provide useful validation errors. Below are details on common validation errors users
may encounter when working with pydantic, together with some suggestions on how to fix them.

## `arguments_type`

This error is raised when an object that would be passed as arguments to a function during validation is not
a `tuple`, `list`, or `dict`. Because `NamedTuple` uses function calls in its implementation, that is one way to
produce this error:

```python
from typing import NamedTuple

from pydantic import BaseModel, ValidationError


class MyNamedTuple(NamedTuple):
    x: int


class MyModel(BaseModel):
    field: MyNamedTuple


try:
    MyModel.model_validate({'field': 'invalid'})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'arguments_type'
```

## `assertion_error`

This error is raised when a failing `assert` statement is encountered during validation:

```python
from pydantic import BaseModel, ValidationError, field_validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    @classmethod
    def force_x_positive(cls, v):
        assert v > 0
        return v


try:
    Model(x=-1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'assertion_error'
```

## `bool_parsing`

This error is raised when the input value is a string that is not valid for coercion to a boolean:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: bool


Model(x='true')  # OK

try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bool_parsing'
```

## `bool_type`

This error is raised when the input value's type is not valid for a `bool` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: bool


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bool_type'
```

This error is also raised for strict fields when the input value is not an instance of `bool`.

## `bytes_invalid_encoding`

This error is raised when a `bytes` value is invalid under the configured encoding.
In the following example, `b'a'` is invalid hex (odd number of digits).

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: bytes
    model_config = {'val_json_bytes': 'hex'}


try:
    Model(x=b'a')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bytes_invalid_encoding'
```

## `bytes_too_long`

This error is raised when the length of a `bytes` value is greater than the field's `max_length` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: bytes = Field(max_length=3)


try:
    Model(x=b'test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bytes_too_long'
```

## `bytes_too_short`

This error is raised when the length of a `bytes` value is less than the field's `min_length` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: bytes = Field(min_length=3)


try:
    Model(x=b't')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bytes_too_short'
```

## `bytes_type`

This error is raised when the input value's type is not valid for a `bytes` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: bytes


try:
    Model(x=123)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'bytes_type'
```

This error is also raised for strict fields when the input value is not an instance of `bytes`.

## `callable_type`

This error is raised when the input value is not valid as a `Callable`:

```python
from typing import Any, Callable

from pydantic import BaseModel, ImportString, ValidationError


class Model(BaseModel):
    x: ImportString[Callable[[Any], Any]]


Model(x='math:cos')  # OK

try:
    Model(x='os.path')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'callable_type'
```

## `complex_str_parsing`

This error is raised when the input value is a string but cannot be parsed as a complex number because
it does not follow the [rule](https://docs.python.org/3/library/functions.html#complex) in Python:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    num: complex


try:
    # Complex numbers in json are expected to be valid complex strings.
    # This value `abc` is not a valid complex string.
    Model.model_validate_json('{"num": "abc"}')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'complex_str_parsing'
```

## `complex_type`

This error is raised when the input value cannot be interpreted as a complex number:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    num: complex


try:
    Model(num=False)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'complex_type'
```

## `dataclass_exact_type`

This error is raised when validating a dataclass with `strict=True` and the input is not an instance of the dataclass:

```python
import pydantic.dataclasses
from pydantic import TypeAdapter, ValidationError


@pydantic.dataclasses.dataclass
class MyDataclass:
    x: str


adapter = TypeAdapter(MyDataclass)

print(adapter.validate_python(MyDataclass(x='test'), strict=True))
#> MyDataclass(x='test')
print(adapter.validate_python({'x': 'test'}))
#> MyDataclass(x='test')

try:
    adapter.validate_python({'x': 'test'}, strict=True)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'dataclass_exact_type'
```

## `dataclass_type`

This error is raised when the input value is not valid for a `dataclass` field:

```python
from pydantic import ValidationError, dataclasses


@dataclasses.dataclass
class Inner:
    x: int


@dataclasses.dataclass
class Outer:
    y: Inner


Outer(y=Inner(x=1))  # OK

try:
    Outer(y=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'dataclass_type'
```

## `date_from_datetime_inexact`

This error is raised when the input `datetime` value provided for a `date` field has a nonzero time component.
For a timestamp to parse into a field of type `date`, the time components must all be zero:

```python
from datetime import date, datetime

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: date


Model(x='2023-01-01')  # OK
Model(x=datetime(2023, 1, 1))  # OK

try:
    Model(x=datetime(2023, 1, 1, 12))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_from_datetime_inexact'
```

## `date_from_datetime_parsing`

This error is raised when the input value is a string that cannot be parsed for a `date` field:

```python
from datetime import date

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: date


try:
    Model(x='XX1494012000')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_from_datetime_parsing'
```

## `date_future`

This error is raised when the input value provided for a `FutureDate` field is not in the future:

```python
from datetime import date

from pydantic import BaseModel, FutureDate, ValidationError


class Model(BaseModel):
    x: FutureDate


try:
    Model(x=date(2000, 1, 1))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_future'
```

## `date_parsing`

This error is raised when validating JSON where the input value is string that cannot be parsed for a `date` field:

```python
import json
from datetime import date

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: date = Field(strict=True)


try:
    Model.model_validate_json(json.dumps({'x': '1'}))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_parsing'
```

## `date_past`

This error is raised when the value provided for a `PastDate` field is not in the past:

```python
from datetime import date, timedelta

from pydantic import BaseModel, PastDate, ValidationError


class Model(BaseModel):
    x: PastDate


try:
    Model(x=date.today() + timedelta(1))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_past'
```

## `date_type`

This error is raised when the input value's type is not valid for a `date` field:

```python
from datetime import date

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: date


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'date_type'
```

This error is also raised for strict fields when the input value is not an instance of `date`.

## `datetime_from_date_parsing`

This error is raised when the input value is a string that cannot be parsed for a `datetime` field:

```python
from datetime import datetime

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: datetime


try:
    # there is no 13th month
    Model(x='2023-13-01')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_from_date_parsing'
```

## `datetime_future`

This error is raised when the value provided for a `FutureDatetime` field is not in the future:

```python
from datetime import datetime

from pydantic import BaseModel, FutureDatetime, ValidationError


class Model(BaseModel):
    x: FutureDatetime


try:
    Model(x=datetime(2000, 1, 1))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_future'
```

## `datetime_object_invalid`

This error is raised when something about the `datetime` object is not valid:

```python
from datetime import datetime, tzinfo

from pydantic import AwareDatetime, BaseModel, ValidationError


class CustomTz(tzinfo):
    # utcoffset is not implemented!

    def tzname(self, _dt):
        return 'CustomTZ'


class Model(BaseModel):
    x: AwareDatetime


try:
    Model(x=datetime(2023, 1, 1, tzinfo=CustomTz()))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_object_invalid'
```

## `datetime_parsing`

This error is raised when the value is a string that cannot be parsed for a `datetime` field:

```python
import json
from datetime import datetime

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: datetime = Field(strict=True)


try:
    Model.model_validate_json(json.dumps({'x': 'not a datetime'}))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_parsing'
```

## `datetime_past`

This error is raised when the value provided for a `PastDatetime` field is not in the past:

```python
from datetime import datetime, timedelta

from pydantic import BaseModel, PastDatetime, ValidationError


class Model(BaseModel):
    x: PastDatetime


try:
    Model(x=datetime.now() + timedelta(100))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_past'
```

## `datetime_type`

This error is raised when the input value's type is not valid for a `datetime` field:

```python
from datetime import datetime

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: datetime


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'datetime_type'
```

This error is also raised for strict fields when the input value is not an instance of `datetime`.

## `decimal_max_digits`

This error is raised when the value provided for a `Decimal` has too many digits:

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(max_digits=3)


try:
    Model(x='42.1234')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_max_digits'
```

## `decimal_max_places`

This error is raised when the value provided for a `Decimal` has too many digits after the decimal point:

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(decimal_places=3)


try:
    Model(x='42.1234')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_max_places'
```

## `decimal_parsing`

This error is raised when the value provided for a `Decimal` could not be parsed as a decimal number:

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(decimal_places=3)


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_parsing'
```

## `decimal_type`

This error is raised when the value provided for a `Decimal` is of the wrong type:

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(decimal_places=3)


try:
    Model(x=[1, 2, 3])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_type'
```

This error is also raised for strict fields when the input value is not an instance of `Decimal`.

## `decimal_whole_digits`

This error is raised when the value provided for a `Decimal` has more digits before the decimal point than `max_digits` - `decimal_places` (as long as both are specified):

```python
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: Decimal = Field(max_digits=6, decimal_places=3)


try:
    Model(x='12345.6')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'decimal_whole_digits'
```

## `dict_type`

This error is raised when the input value's type is not `dict` for a `dict` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: dict


try:
    Model(x=['1', '2'])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'dict_type'
```

## `enum`

This error is raised when the input value does not exist in an `enum` field members:

```python
from enum import Enum

from pydantic import BaseModel, ValidationError


class MyEnum(str, Enum):
    option = 'option'


class Model(BaseModel):
    x: MyEnum


try:
    Model(x='other_option')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'enum'
```

## `extra_forbidden`

This error is raised when the input value contains extra fields, but `model_config['extra'] == 'forbid'`:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    x: str

    model_config = ConfigDict(extra='forbid')


try:
    Model(x='test', y='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'extra_forbidden'
```

You can read more about the `extra` configuration in the [Extra Attributes][pydantic.config.ConfigDict.extra] section.

## `finite_number`

This error is raised when the value is infinite, or too large to be represented as a 64-bit floating point number
during validation:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


try:
    Model(x=2.2250738585072011e308)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'finite_number'
```

## `float_parsing`

This error is raised when the value is a string that can't be parsed as a `float`:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: float


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'float_parsing'
```

## `float_type`

This error is raised when the input value's type is not valid for a `float` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: float


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'float_type'
```

## `frozen_field`

This error is raised when you attempt to assign a value to a field with `frozen=True`, or to delete such a field:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: str = Field('test', frozen=True)


model = Model()

try:
    model.x = 'test1'
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_field'

try:
    del model.x
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_field'
```

## `frozen_instance`

This error is raised when `model_config['frozen] == True` and you attempt to delete or assign a new value to
any of the fields:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    x: int

    model_config = ConfigDict(frozen=True)


m = Model(x=1)

try:
    m.x = 2
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_instance'

try:
    del m.x
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_instance'
```

## `frozen_set_type`

This error is raised when the input value's type is not valid for a `frozenset` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: frozenset


try:
    model = Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'frozen_set_type'
```

## `get_attribute_error`

This error is raised when `model_config['from_attributes'] == True` and an error is raised while reading the attributes:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Foobar:
    def __init__(self):
        self.x = 1

    @property
    def y(self):
        raise RuntimeError('intentional error')


class Model(BaseModel):
    x: int
    y: str

    model_config = ConfigDict(from_attributes=True)


try:
    Model.model_validate(Foobar())
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'get_attribute_error'
```

## `greater_than`

This error is raised when the value is not greater than the field's `gt` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(gt=10)


try:
    Model(x=10)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'greater_than'
```

## `greater_than_equal`

This error is raised when the value is not greater than or equal to the field's `ge` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(ge=10)


try:
    Model(x=9)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'greater_than_equal'
```

## `int_from_float`

This error is raised when you provide a `float` value for an `int` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


try:
    Model(x=0.5)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_from_float'
```

## `int_parsing`

This error is raised when the value can't be parsed as `int`:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_parsing'
```

## `int_parsing_size`

This error is raised when attempting to parse a python or JSON value from a string outside the maximum range that Python
`str` to `int` parsing permits:

```python
import json

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


# from Python
assert Model(x='1' * 4_300).x == int('1' * 4_300)  # OK

too_long = '1' * 4_301
try:
    Model(x=too_long)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_parsing_size'

# from JSON
try:
    Model.model_validate_json(json.dumps({'x': too_long}))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_parsing_size'
```

## `int_type`

This error is raised when the input value's type is not valid for an `int` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'int_type'
```

## `invalid_key`

This error is raised when attempting to validate a `dict` that has a key that is not an instance of `str`:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Model(BaseModel):
    x: int

    model_config = ConfigDict(extra='allow')


try:
    Model.model_validate({'x': 1, b'y': 2})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'invalid_key'
```

## `is_instance_of`

This error is raised when the input value is not an instance of the expected type:

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Nested:
    x: str


class Model(BaseModel):
    y: Nested

    model_config = ConfigDict(arbitrary_types_allowed=True)


try:
    Model(y='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'is_instance_of'
```

## `is_subclass_of`

This error is raised when the input value is not a subclass of the expected type:

```python
from pydantic import BaseModel, ValidationError


class Nested:
    x: str


class Model(BaseModel):
    y: type[Nested]


try:
    Model(y='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'is_subclass_of'
```

## `iterable_type`

This error is raised when the input value is not valid as an `Iterable`:

```python
from typing import Iterable

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    y: Iterable


try:
    Model(y=123)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'iterable_type'
```

## `iteration_error`

This error is raised when an error occurs during iteration:

```python
from pydantic import BaseModel, ValidationError


def gen():
    yield 1
    raise RuntimeError('error')


class Model(BaseModel):
    x: list[int]


try:
    Model(x=gen())
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'iteration_error'
```

## `json_invalid`

This error is raised when the input value is not a valid JSON string:

```python
from pydantic import BaseModel, Json, ValidationError


class Model(BaseModel):
    x: Json


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'json_invalid'
```

## `json_type`

This error is raised when the input value is of a type that cannot be parsed as JSON:

```python
from pydantic import BaseModel, Json, ValidationError


class Model(BaseModel):
    x: Json


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'json_type'
```

## `less_than`

This error is raised when the input value is not less than the field's `lt` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(lt=10)


try:
    Model(x=10)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'less_than'
```

## `less_than_equal`

This error is raised when the input value is not less than or equal to the field's `le` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(le=10)


try:
    Model(x=11)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'less_than_equal'
```

## `list_type`

This error is raised when the input value's type is not valid for a `list` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: list[int]


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'list_type'
```

## `literal_error`

This error is raised when the input value is not one of the expected literal values:

```python
from typing import Literal

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: Literal['a', 'b']


Model(x='a')  # OK

try:
    Model(x='c')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'literal_error'
```

## `mapping_type`

This error is raised when a problem occurs during validation due to a failure in a call to the methods from the
`Mapping` protocol, such as `.items()`:

```python
from collections.abc import Mapping

from pydantic import BaseModel, ValidationError


class BadMapping(Mapping):
    def items(self):
        raise ValueError()

    def __iter__(self):
        raise ValueError()

    def __getitem__(self, key):
        raise ValueError()

    def __len__(self):
        return 1


class Model(BaseModel):
    x: dict[str, str]


try:
    Model(x=BadMapping())
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'mapping_type'
```

## `missing`

This error is raised when there are required fields missing from the input value:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: str


try:
    Model()
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing'
```

## `missing_argument`

This error is raised when a required positional-or-keyword argument is not passed to a function decorated with
`validate_call`:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(a: int):
    return a


try:
    foo()
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing_argument'
```

## `missing_keyword_only_argument`

This error is raised when a required keyword-only argument is not passed to a function decorated with `validate_call`:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(*, a: int):
    return a


try:
    foo()
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing_keyword_only_argument'
```

## `missing_positional_only_argument`

This error is raised when a required positional-only argument is not passed to a function decorated with
`validate_call`:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(a: int, /):
    return a


try:
    foo()
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing_positional_only_argument'
```

## `missing_sentinel_error`

This error is raised when the experimental `MISSING` sentinel is the only value allowed, and wasn't
provided during validation:

```python
from pydantic import BaseModel, ValidationError
from pydantic.experimental.missing_sentinel import MISSING


class Model(BaseModel):
    f: MISSING


try:
    Model(f=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'missing_sentinel_error'
```

## `model_attributes_type`

This error is raised when the input value is not a valid dictionary, model instance, or instance that fields can be extracted from:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    a: int
    b: int


# simply validating a dict
print(Model.model_validate({'a': 1, 'b': 2}))
#> a=1 b=2


class CustomObj:
    def __init__(self, a, b):
        self.a = a
        self.b = b


# using from attributes to extract fields from an objects
print(Model.model_validate(CustomObj(3, 4), from_attributes=True))
#> a=3 b=4

try:
    Model.model_validate('not an object', from_attributes=True)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'model_attributes_type'
```

## `model_type`

This error is raised when the input to a model is not an instance of the model or dict:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    a: int
    b: int


# simply validating a dict
m = Model.model_validate({'a': 1, 'b': 2})
print(m)
#> a=1 b=2

# validating an existing model instance
print(Model.model_validate(m))
#> a=1 b=2

try:
    Model.model_validate('not an object')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'model_type'
```

## `multiple_argument_values`

This error is raised when you provide multiple values for a single argument while calling a function decorated with
`validate_call`:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(a: int):
    return a


try:
    foo(1, a=2)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'multiple_argument_values'
```

## `multiple_of`

This error is raised when the input is not a multiple of a field's `multiple_of` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: int = Field(multiple_of=5)


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'multiple_of'
```

## `needs_python_object`

This type of error is raised when validation is attempted from a format that cannot be converted to a Python object.
For example, we cannot check `isinstance` or `issubclass` from JSON:

```python
import json

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    bm: type[BaseModel]


try:
    Model.model_validate_json(json.dumps({'bm': 'not a basemodel class'}))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'needs_python_object'
```

## `no_such_attribute`

This error is raised when `validate_assignment=True` in the config, and you attempt to assign a value to an attribute
that is not an existing field:

```python
from pydantic import ConfigDict, ValidationError, dataclasses


@dataclasses.dataclass(config=ConfigDict(validate_assignment=True))
class MyDataclass:
    x: int


m = MyDataclass(x=1)
try:
    m.y = 10
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'no_such_attribute'
```

## `none_required`

This error is raised when the input value is not `None` for a field that requires `None`:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: None


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'none_required'
```

!!! note
    You may encounter this error when there is a naming collision in your model between a field name and its type. More specifically, this error is likely to be thrown when the default value of that field is `None`.

    For example, the following would yield the `none_required` validation error since the field `int` is set to a default value of `None` and has the exact same name as its type, which causes problems with validation.

    ```python {test="skip"}
    from typing import Optional

    from pydantic import BaseModel


    class M1(BaseModel):
        int: Optional[int] = None


    m = M1(int=123)  # errors
    ```

## `recursion_loop`

This error is raised when a cyclic reference is detected:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: list['Model']


d = {'x': []}
d['x'].append(d)
try:
    Model(**d)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'recursion_loop'
```

## `set_item_not_hashable`

This error is raised when an unhashable value is validated against a [`set`][] or a [`frozenset`][]:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: set[object]


class Unhashable:
    __hash__ = None


try:
    Model(x=[{'a': 'b'}, Unhashable()])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'set_item_not_hashable'
    print(repr(exc.errors()[1]['type']))
    #> 'set_item_not_hashable'
```

## `set_type`

This error is raised when the value type is not valid for a `set` field:

```python
from typing import Set

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: Set[int]


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'set_type'
```

## `string_pattern_mismatch`

This error is raised when the input value doesn't match the field's `pattern` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: str = Field(pattern='test')


try:
    Model(x='1')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_pattern_mismatch'
```

## `string_sub_type`

This error is raised when the value is an instance of a strict subtype of `str` when the field is strict:

```python
from enum import Enum

from pydantic import BaseModel, Field, ValidationError


class MyEnum(str, Enum):
    foo = 'foo'


class Model(BaseModel):
    x: str = Field(strict=True)


try:
    Model(x=MyEnum.foo)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_sub_type'
```

## `string_too_long`

This error is raised when the input value is a string whose length is greater than the field's `max_length` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: str = Field(max_length=3)


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_too_long'
```

## `string_too_short`

This error is raised when the input value is a string whose length is less than the field's `min_length` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: str = Field(min_length=3)


try:
    Model(x='t')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_too_short'
```

## `string_type`

This error is raised when the input value's type is not valid for a `str` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: str


try:
    Model(x=1)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_type'
```

This error is also raised for strict fields when the input value is not an instance of `str`.

## `string_unicode`

This error is raised when the value cannot be parsed as a Unicode string:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: str


try:
    Model(x=b'\x81')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'string_unicode'
```

## `time_delta_parsing`

This error is raised when the input value is a string that cannot be parsed for a `timedelta` field:

```python
from datetime import timedelta

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: timedelta


try:
    Model(x='t')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'time_delta_parsing'
```

## `time_delta_type`

This error is raised when the input value's type is not valid for a `timedelta` field:

```python
from datetime import timedelta

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: timedelta


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'time_delta_type'
```

This error is also raised for strict fields when the input value is not an instance of `timedelta`.

## `time_parsing`

This error is raised when the input value is a string that cannot be parsed for a `time` field:

```python
from datetime import time

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: time


try:
    Model(x='25:20:30.400')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'time_parsing'
```

## `time_type`

This error is raised when the value type is not valid for a `time` field:

```python
from datetime import time

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: time


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'time_type'
```

This error is also raised for strict fields when the input value is not an instance of `time`.

## `timezone_aware`

This error is raised when the `datetime` value provided for a timezone-aware `datetime` field
doesn't have timezone information:

```python
from datetime import datetime

from pydantic import AwareDatetime, BaseModel, ValidationError


class Model(BaseModel):
    x: AwareDatetime


try:
    Model(x=datetime.now())
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'timezone_aware'
```

## `timezone_naive`

This error is raised when the `datetime` value provided for a timezone-naive `datetime` field
has timezone info:

```python
from datetime import datetime, timezone

from pydantic import BaseModel, NaiveDatetime, ValidationError


class Model(BaseModel):
    x: NaiveDatetime


try:
    Model(x=datetime.now(tz=timezone.utc))
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'timezone_naive'
```

## `too_long`

This error is raised when the input value's length is greater than the field's `max_length` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: list[int] = Field(max_length=3)


try:
    Model(x=[1, 2, 3, 4])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'too_long'
```

## `too_short`

This error is raised when the value length is less than the field's `min_length` constraint:

```python
from pydantic import BaseModel, Field, ValidationError


class Model(BaseModel):
    x: list[int] = Field(min_length=3)


try:
    Model(x=[1, 2])
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'too_short'
```

## `tuple_type`

This error is raised when the input value's type is not valid for a `tuple` field:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: tuple[int]


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'tuple_type'
```

This error is also raised for strict fields when the input value is not an instance of `tuple`.

## `unexpected_keyword_argument`

This error is raised when you provide a value by keyword for a positional-only
argument while calling a function decorated with `validate_call`:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(a: int, /):
    return a


try:
    foo(a=2)
except ValidationError as exc:
    print(repr(exc.errors()[1]['type']))
    #> 'unexpected_keyword_argument'
```

It is also raised when using pydantic.dataclasses and `extra=forbid`:

```python
from pydantic import TypeAdapter, ValidationError
from pydantic.dataclasses import dataclass


@dataclass(config={'extra': 'forbid'})
class Foo:
    bar: int


try:
    TypeAdapter(Foo).validate_python({'bar': 1, 'foobar': 2})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'unexpected_keyword_argument'
```

## `unexpected_positional_argument`

This error is raised when you provide a positional value for a keyword-only
argument while calling a function decorated with `validate_call`:

```python
from pydantic import ValidationError, validate_call


@validate_call
def foo(*, a: int):
    return a


try:
    foo(2)
except ValidationError as exc:
    print(repr(exc.errors()[1]['type']))
    #> 'unexpected_positional_argument'
```

## `union_tag_invalid`

This error is raised when the input's discriminator is not one of the expected values:

```python
from typing import Literal, Union

from pydantic import BaseModel, Field, ValidationError


class BlackCat(BaseModel):
    pet_type: Literal['blackcat']


class WhiteCat(BaseModel):
    pet_type: Literal['whitecat']


class Model(BaseModel):
    cat: Union[BlackCat, WhiteCat] = Field(discriminator='pet_type')


try:
    Model(cat={'pet_type': 'dog'})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'union_tag_invalid'
```

## `union_tag_not_found`

This error is raised when it is not possible to extract a discriminator value from the input:

```python
from typing import Literal, Union

from pydantic import BaseModel, Field, ValidationError


class BlackCat(BaseModel):
    pet_type: Literal['blackcat']


class WhiteCat(BaseModel):
    pet_type: Literal['whitecat']


class Model(BaseModel):
    cat: Union[BlackCat, WhiteCat] = Field(discriminator='pet_type')


try:
    Model(cat={'name': 'blackcat'})
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'union_tag_not_found'
```

## `url_parsing`

This error is raised when the input value cannot be parsed as a URL:

```python
from pydantic import AnyUrl, BaseModel, ValidationError


class Model(BaseModel):
    x: AnyUrl


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_parsing'
```

## `url_scheme`

This error is raised when the URL scheme is not valid for the URL type of the field:

```python
from pydantic import BaseModel, HttpUrl, ValidationError


class Model(BaseModel):
    x: HttpUrl


try:
    Model(x='ftp://example.com')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_scheme'
```

## `url_syntax_violation`

This error is raised when the URL syntax is not valid:

```python
from pydantic import BaseModel, Field, HttpUrl, ValidationError


class Model(BaseModel):
    x: HttpUrl = Field(strict=True)


try:
    Model(x='http:////example.com')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_syntax_violation'
```

## `url_too_long`

This error is raised when the URL length is greater than 2083:

```python
from pydantic import BaseModel, HttpUrl, ValidationError


class Model(BaseModel):
    x: HttpUrl


try:
    Model(x='x' * 2084)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_too_long'
```

## `url_type`

This error is raised when the input value's type is not valid for a URL field:

```python
from pydantic import BaseModel, HttpUrl, ValidationError


class Model(BaseModel):
    x: HttpUrl


try:
    Model(x=None)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'url_type'
```

## `uuid_parsing`

This error is raised when the input value's type is not valid for a UUID field:

```python
from uuid import UUID

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    u: UUID


try:
    Model(u='12345678-124-1234-1234-567812345678')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'uuid_parsing'
```

## `uuid_type`

This error is raised when the input value's type is not valid instance for a UUID field (str, bytes or UUID):

```python
from uuid import UUID

from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    u: UUID


try:
    Model(u=1234567812412341234567812345678)
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'uuid_type'
```

## `uuid_version`

This error is raised when the input value's type is not match UUID version:

```python
from pydantic import UUID5, BaseModel, ValidationError


class Model(BaseModel):
    u: UUID5


try:
    Model(u='a6cc5730-2261-11ee-9c43-2eb5a363657c')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'uuid_version'
```

## `value_error`

This error is raised when a `ValueError` is raised during validation:

```python
from pydantic import BaseModel, ValidationError, field_validator


class Model(BaseModel):
    x: str

    @field_validator('x')
    @classmethod
    def repeat_b(cls, v):
        raise ValueError()


try:
    Model(x='test')
except ValidationError as exc:
    print(repr(exc.errors()[0]['type']))
    #> 'value_error'
```
````

## File: docs/examples/custom_validators.md
````markdown
This page provides example snippets for creating more complex, custom validators in Pydantic.
Many of these examples are adapted from Pydantic issues and discussions, and are intended to showcase
the flexibility and power of Pydantic's validation system.

## Custom `datetime` Validator via [`Annotated`][typing.Annotated] Metadata

In this example, we'll construct a custom validator, attached to an [`Annotated`][typing.Annotated] type,
that ensures a [`datetime`][datetime.datetime] object adheres to a given timezone constraint.

The custom validator supports string specification of the timezone, and will raise an error if the [`datetime`][datetime.datetime] object does not have the correct timezone.

We use `__get_pydantic_core_schema__` in the validator to customize the schema of the annotated type (in this case, [`datetime`][datetime.datetime]), which allows us to add custom validation logic. Notably, we use a `wrap` validator function so that we can perform operations both before and after the default `pydantic` validation of a [`datetime`][datetime.datetime].

```python
import datetime as dt
from dataclasses import dataclass
from pprint import pprint
from typing import Annotated, Any, Callable, Optional

import pytz
from pydantic_core import CoreSchema, core_schema

from pydantic import (
    GetCoreSchemaHandler,
    PydanticUserError,
    TypeAdapter,
    ValidationError,
)


@dataclass(frozen=True)
class MyDatetimeValidator:
    tz_constraint: Optional[str] = None

    def tz_constraint_validator(
        self,
        value: dt.datetime,
        handler: Callable,  # (1)!
    ):
        """Validate tz_constraint and tz_info."""
        # handle naive datetimes
        if self.tz_constraint is None:
            assert (
                value.tzinfo is None
            ), 'tz_constraint is None, but provided value is tz-aware.'
            return handler(value)

        # validate tz_constraint and tz-aware tzinfo
        if self.tz_constraint not in pytz.all_timezones:
            raise PydanticUserError(
                f'Invalid tz_constraint: {self.tz_constraint}',
                code='unevaluable-type-annotation',
            )
        result = handler(value)  # (2)!
        assert self.tz_constraint == str(
            result.tzinfo
        ), f'Invalid tzinfo: {str(result.tzinfo)}, expected: {self.tz_constraint}'

        return result

    def __get_pydantic_core_schema__(
        self,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            self.tz_constraint_validator,
            handler(source_type),
        )


LA = 'America/Los_Angeles'
ta = TypeAdapter(Annotated[dt.datetime, MyDatetimeValidator(LA)])
print(
    ta.validate_python(dt.datetime(2023, 1, 1, 0, 0, tzinfo=pytz.timezone(LA)))
)
#> 2023-01-01 00:00:00-07:53

LONDON = 'Europe/London'
try:
    ta.validate_python(
        dt.datetime(2023, 1, 1, 0, 0, tzinfo=pytz.timezone(LONDON))
    )
except ValidationError as ve:
    pprint(ve.errors(), width=100)
    """
    [{'ctx': {'error': AssertionError('Invalid tzinfo: Europe/London, expected: America/Los_Angeles')},
    'input': datetime.datetime(2023, 1, 1, 0, 0, tzinfo=<DstTzInfo 'Europe/London' LMT-1 day, 23:59:00 STD>),
    'loc': (),
    'msg': 'Assertion failed, Invalid tzinfo: Europe/London, expected: America/Los_Angeles',
    'type': 'assertion_error',
    'url': 'https://errors.pydantic.dev/2.8/v/assertion_error'}]
    """
```

1. The `handler` function is what we call to validate the input with standard `pydantic` validation
2. We call the `handler` function to validate the input with standard `pydantic` validation in this wrap validator

We can also enforce UTC offset constraints in a similar way.  Assuming we have a `lower_bound` and an `upper_bound`, we can create a custom validator to ensure our `datetime` has a UTC offset that is inclusive within the boundary we define:

```python
import datetime as dt
from dataclasses import dataclass
from pprint import pprint
from typing import Annotated, Any, Callable

import pytz
from pydantic_core import CoreSchema, core_schema

from pydantic import GetCoreSchemaHandler, TypeAdapter, ValidationError


@dataclass(frozen=True)
class MyDatetimeValidator:
    lower_bound: int
    upper_bound: int

    def validate_tz_bounds(self, value: dt.datetime, handler: Callable):
        """Validate and test bounds"""
        assert value.utcoffset() is not None, 'UTC offset must exist'
        assert self.lower_bound <= self.upper_bound, 'Invalid bounds'

        result = handler(value)

        hours_offset = value.utcoffset().total_seconds() / 3600
        assert (
            self.lower_bound <= hours_offset <= self.upper_bound
        ), 'Value out of bounds'

        return result

    def __get_pydantic_core_schema__(
        self,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            self.validate_tz_bounds,
            handler(source_type),
        )


LA = 'America/Los_Angeles'  # UTC-7 or UTC-8
ta = TypeAdapter(Annotated[dt.datetime, MyDatetimeValidator(-10, -5)])
print(
    ta.validate_python(dt.datetime(2023, 1, 1, 0, 0, tzinfo=pytz.timezone(LA)))
)
#> 2023-01-01 00:00:00-07:53

LONDON = 'Europe/London'
try:
    print(
        ta.validate_python(
            dt.datetime(2023, 1, 1, 0, 0, tzinfo=pytz.timezone(LONDON))
        )
    )
except ValidationError as e:
    pprint(e.errors(), width=100)
    """
    [{'ctx': {'error': AssertionError('Value out of bounds')},
    'input': datetime.datetime(2023, 1, 1, 0, 0, tzinfo=<DstTzInfo 'Europe/London' LMT-1 day, 23:59:00 STD>),
    'loc': (),
    'msg': 'Assertion failed, Value out of bounds',
    'type': 'assertion_error',
    'url': 'https://errors.pydantic.dev/2.8/v/assertion_error'}]
    """
```

## Validating Nested Model Fields

Here, we demonstrate two ways to validate a field of a nested model, where the validator utilizes data from the parent model.

In this example, we construct a validator that checks that each user's password is not in a list of forbidden passwords specified by the parent model.

One way to do this is to place a custom validator on the outer model:

```python
from typing_extensions import Self

from pydantic import BaseModel, ValidationError, model_validator


class User(BaseModel):
    username: str
    password: str


class Organization(BaseModel):
    forbidden_passwords: list[str]
    users: list[User]

    @model_validator(mode='after')
    def validate_user_passwords(self) -> Self:
        """Check that user password is not in forbidden list. Raise a validation error if a forbidden password is encountered."""
        for user in self.users:
            current_pw = user.password
            if current_pw in self.forbidden_passwords:
                raise ValueError(
                    f'Password {current_pw} is forbidden. Please choose another password for user {user.username}.'
                )
        return self


data = {
    'forbidden_passwords': ['123'],
    'users': [
        {'username': 'Spartacat', 'password': '123'},
        {'username': 'Iceburgh', 'password': '87'},
    ],
}
try:
    org = Organization(**data)
except ValidationError as e:
    print(e)
    """
    1 validation error for Organization
      Value error, Password 123 is forbidden. Please choose another password for user Spartacat. [type=value_error, input_value={'forbidden_passwords': [...gh', 'password': '87'}]}, input_type=dict]
    """
```

Alternatively, a custom validator can be used in the nested model class (`User`), with the forbidden passwords data from the parent model being passed in via validation context.

!!! warning
    The ability to mutate the context within a validator adds a lot of power to nested validation, but can also lead to confusing or hard-to-debug code. Use this approach at your own risk!

```python
from pydantic import BaseModel, ValidationError, ValidationInfo, field_validator


class User(BaseModel):
    username: str
    password: str

    @field_validator('password', mode='after')
    @classmethod
    def validate_user_passwords(
        cls, password: str, info: ValidationInfo
    ) -> str:
        """Check that user password is not in forbidden list."""
        forbidden_passwords = (
            info.context.get('forbidden_passwords', []) if info.context else []
        )
        if password in forbidden_passwords:
            raise ValueError(f'Password {password} is forbidden.')
        return password


class Organization(BaseModel):
    forbidden_passwords: list[str]
    users: list[User]

    @field_validator('forbidden_passwords', mode='after')
    @classmethod
    def add_context(cls, v: list[str], info: ValidationInfo) -> list[str]:
        if info.context is not None:
            info.context.update({'forbidden_passwords': v})
        return v


data = {
    'forbidden_passwords': ['123'],
    'users': [
        {'username': 'Spartacat', 'password': '123'},
        {'username': 'Iceburgh', 'password': '87'},
    ],
}

try:
    org = Organization.model_validate(data, context={})
except ValidationError as e:
    print(e)
    """
    1 validation error for Organization
    users.0.password
      Value error, Password 123 is forbidden. [type=value_error, input_value='123', input_type=str]
    """
```

Note that if the context property is not included in `model_validate`, then `info.context` will be `None` and the forbidden passwords list will not get added to the context in the above implementation. As such, `validate_user_passwords` would not carry out the desired password validation.

More details about validation context can be found [here](../concepts/validators.md#validation-context).
````

## File: docs/examples/files.md
````markdown
`pydantic` is a great tool for validating data coming from various sources.
In this section, we will look at how to validate data from different types of files.

!!! note
    If you're using any of the below file formats to parse configuration / settings, you might want to
    consider using the [`pydantic-settings`][pydantic_settings] library, which offers builtin
    support for parsing this type of data.

## JSON data

`.json` files are a common way to store key / value data in a human-readable format.
Here is an example of a `.json` file:

```json
{
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com"
}
```

To validate this data, we can use a `pydantic` model:

```python {test="skip"}
import pathlib

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


json_string = pathlib.Path('person.json').read_text()
person = Person.model_validate_json(json_string)
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

If the data in the file is not valid, `pydantic` will raise a [`ValidationError`][pydantic_core.ValidationError].
Let's say we have the following `.json` file:

```json
{
    "age": -30,
    "email": "not-an-email-address"
}
```

This data is flawed for three reasons:

1. It's missing the `name` field.
2. The `age` field is negative.
3. The `email` field is not a valid email address.

When we try to validate this data, `pydantic` raises a [`ValidationError`][pydantic_core.ValidationError] with all of the
above issues:

```python {test="skip"}
import pathlib

from pydantic import BaseModel, EmailStr, PositiveInt, ValidationError


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


json_string = pathlib.Path('person.json').read_text()
try:
    person = Person.model_validate_json(json_string)
except ValidationError as err:
    print(err)
    """
    3 validation errors for Person
    name
    Field required [type=missing, input_value={'age': -30, 'email': 'not-an-email-address'}, input_type=dict]
        For further information visit https://errors.pydantic.dev/2.10/v/missing
    age
    Input should be greater than 0 [type=greater_than, input_value=-30, input_type=int]
        For further information visit https://errors.pydantic.dev/2.10/v/greater_than
    email
    value is not a valid email address: An email address must have an @-sign. [type=value_error, input_value='not-an-email-address', input_type=str]
    """
```

Often, it's the case that you have an abundance of a certain type of data within a `.json` file.
For example, you might have a list of people:

```json
[
    {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    },
    {
        "name": "Jane Doe",
        "age": 25,
        "email": "jane@example.com"
    }
]
```

In this case, you can validate the data against a `list[Person]` model:

```python {test="skip"}
import pathlib

from pydantic import BaseModel, EmailStr, PositiveInt, TypeAdapter


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


person_list_adapter = TypeAdapter(list[Person])  # (1)!

json_string = pathlib.Path('people.json').read_text()
people = person_list_adapter.validate_json(json_string)
print(people)
#> [Person(name='John Doe', age=30, email='john@example.com'), Person(name='Jane Doe', age=25, email='jane@example.com')]
```

1. We use [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] to validate a list of `Person` objects.
[`TypeAdapter`][pydantic.type_adapter.TypeAdapter] is a Pydantic construct used to validate data against a single type.

## JSON lines files

Similar to validating a list of objects from a `.json` file, you can validate a list of objects from a `.jsonl` file.
`.jsonl` files are a sequence of JSON objects separated by newlines.

Consider the following `.jsonl` file:

```json
{"name": "John Doe", "age": 30, "email": "john@example.com"}
{"name": "Jane Doe", "age": 25, "email": "jane@example.com"}
```

We can validate this data with a similar approach to the one we used for `.json` files:

```python {test="skip"}
import pathlib

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


json_lines = pathlib.Path('people.jsonl').read_text().splitlines()
people = [Person.model_validate_json(line) for line in json_lines]
print(people)
#> [Person(name='John Doe', age=30, email='john@example.com'), Person(name='Jane Doe', age=25, email='jane@example.com')]
```

## CSV files

CSV is one of the most common file formats for storing tabular data.
To validate data from a CSV file, you can use the `csv` module from the Python standard library to load
the data and validate it against a Pydantic model.

Consider the following CSV file:

```csv
name,age,email
John Doe,30,john@example.com
Jane Doe,25,jane@example.com
```

Here's how we validate that data:

```python {test="skip"}
import csv

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


with open('people.csv') as f:
    reader = csv.DictReader(f)
    people = [Person.model_validate(row) for row in reader]

print(people)
#> [Person(name='John Doe', age=30, email='john@example.com'), Person(name='Jane Doe', age=25, email='jane@example.com')]
```

## TOML files

TOML files are often used for configuration due to their simplicity and readability.

Consider the following TOML file:

```toml
name = "John Doe"
age = 30
email = "john@example.com"
```

Here's how we validate that data:

```python {test="skip"}
import tomllib

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


with open('person.toml', 'rb') as f:
    data = tomllib.load(f)

person = Person.model_validate(data)
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

## YAML files

YAML (YAML Ain't Markup Language) is a human-readable data serialization format that is often used for configuration files.

Consider the following YAML file:

```yaml
name: John Doe
age: 30
email: john@example.com
```

Here's how we validate that data:

```python {test="skip"}
import yaml

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


with open('person.yaml') as f:
    data = yaml.safe_load(f)

person = Person.model_validate(data)
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

## XML files

XML (eXtensible Markup Language) is a markup language that defines a set of rules for encoding documents in a format that is both human-readable and machine-readable.

Consider the following XML file:

```xml
<?xml version="1.0"?>
<person>
    <name>John Doe</name>
    <age>30</age>
    <email>john@example.com</email>
</person>
```

Here's how we validate that data:

```python {test="skip"}
import xml.etree.ElementTree as ET

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


tree = ET.parse('person.xml').getroot()
data = {child.tag: child.text for child in tree}
person = Person.model_validate(data)
print(person)
#> name='John Doe' age=30 email='john@example.com'
```

## INI files

INI files are a simple configuration file format that uses sections and key-value pairs. They are commonly used in Windows applications and older software.

Consider the following INI file:

```ini
[PERSON]
name = John Doe
age = 30
email = john@example.com
```

Here's how we validate that data:

```python {test="skip"}
import configparser

from pydantic import BaseModel, EmailStr, PositiveInt


class Person(BaseModel):
    name: str
    age: PositiveInt
    email: EmailStr


config = configparser.ConfigParser()
config.read('person.ini')
person = Person.model_validate(config['PERSON'])
print(person)
#> name='John Doe' age=30 email='john@example.com'
```
````

## File: docs/examples/orms.md
````markdown
Pydantic serves as a great tool for defining models for ORM (object relational mapping) libraries.
ORMs are used to map objects to database tables, and vice versa.

## SQLAlchemy

Pydantic can pair with SQLAlchemy, as it can be used to define the schema of the database models.

!!! warning "Code Duplication"
    If you use Pydantic with SQLAlchemy, you might experience some frustration with code duplication.
    If you find yourself experiencing this difficulty, you might also consider [`SQLModel`](https://sqlmodel.tiangolo.com/) which integrates Pydantic with SQLAlchemy such that much of the code duplication is eliminated.

If you'd prefer to use pure Pydantic with SQLAlchemy, we recommend using Pydantic models alongside of SQLAlchemy models
as shown in the example below. In this case, we take advantage of Pydantic's aliases feature to name a `Column` after a reserved SQLAlchemy field, thus avoiding conflicts.

```python
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

from pydantic import BaseModel, ConfigDict, Field


class MyModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metadata: dict[str, str] = Field(alias='metadata_')


Base = declarative_base()


class MyTableModel(Base):
    __tablename__ = 'my_table'
    id = sa.Column('id', sa.Integer, primary_key=True)
    # 'metadata' is reserved by SQLAlchemy, hence the '_'
    metadata_ = sa.Column('metadata', sa.JSON)


sql_model = MyTableModel(metadata_={'key': 'val'}, id=1)
pydantic_model = MyModel.model_validate(sql_model)

print(pydantic_model.model_dump())
#> {'metadata': {'key': 'val'}}
print(pydantic_model.model_dump(by_alias=True))
#> {'metadata_': {'key': 'val'}}
```

!!! note
    The example above works because aliases have priority over field names for
    field population. Accessing `SQLModel`'s `metadata` attribute would lead to a `ValidationError`.

<!-- TODO: add examples for Django with Pydantic models -->
````

## File: docs/examples/queues.md
````markdown
Pydantic is quite helpful for validating data that goes into and comes out of queues. Below,
we'll explore how to validate / serialize data with various queue systems.

## Redis queue

Redis is a popular in-memory data structure store.

In order to run this example locally, you'll first need to [install Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
and start your server up locally.

Here's a simple example of how you can use Pydantic to:

1. Serialize data to push to the queue
2. Deserialize and validate data when it's popped from the queue

```python {test="skip"}
import redis

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


r = redis.Redis(host='localhost', port=6379, db=0)
QUEUE_NAME = 'user_queue'


def push_to_queue(user_data: User) -> None:
    serialized_data = user_data.model_dump_json()
    r.rpush(QUEUE_NAME, serialized_data)
    print(f'Added to queue: {serialized_data}')


user1 = User(id=1, name='John Doe', email='john@example.com')
user2 = User(id=2, name='Jane Doe', email='jane@example.com')

push_to_queue(user1)
#> Added to queue: {"id":1,"name":"John Doe","email":"john@example.com"}

push_to_queue(user2)
#> Added to queue: {"id":2,"name":"Jane Doe","email":"jane@example.com"}


def pop_from_queue() -> None:
    data = r.lpop(QUEUE_NAME)

    if data:
        user = User.model_validate_json(data)
        print(f'Validated user: {repr(user)}')
    else:
        print('Queue is empty')


pop_from_queue()
#> Validated user: User(id=1, name='John Doe', email='john@example.com')

pop_from_queue()
#> Validated user: User(id=2, name='Jane Doe', email='jane@example.com')

pop_from_queue()
#> Queue is empty
```

## RabbitMQ

RabbitMQ is a popular message broker that implements the AMQP protocol.

In order to run this example locally, you'll first need to [install RabbitMQ](https://www.rabbitmq.com/download.html) and start your server.

Here's a simple example of how you can use Pydantic to:

1. Serialize data to push to the queue
2. Deserialize and validate data when it's popped from the queue

First, let's create a sender script.

```python {test="skip"}
import pika

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
QUEUE_NAME = 'user_queue'
channel.queue_declare(queue=QUEUE_NAME)


def push_to_queue(user_data: User) -> None:
    serialized_data = user_data.model_dump_json()
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=serialized_data,
    )
    print(f'Added to queue: {serialized_data}')


user1 = User(id=1, name='John Doe', email='john@example.com')
user2 = User(id=2, name='Jane Doe', email='jane@example.com')

push_to_queue(user1)
#> Added to queue: {"id":1,"name":"John Doe","email":"john@example.com"}

push_to_queue(user2)
#> Added to queue: {"id":2,"name":"Jane Doe","email":"jane@example.com"}

connection.close()
```

And here's the receiver script.

```python {test="skip"}
import pika

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    QUEUE_NAME = 'user_queue'
    channel.queue_declare(queue=QUEUE_NAME)

    def process_message(
        ch: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ):
        user = User.model_validate_json(body)
        print(f'Validated user: {repr(user)}')
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
```

To test this example:

1. Run the receiver script in one terminal to start the consumer.
2. Run the sender script in another terminal to send messages.

## ARQ

ARQ is a fast Redis-based job queue for Python.
It's built on top of Redis and provides a simple way to handle background tasks.

In order to run this example locally, you’ll need to [Install Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/) and start your server.

Here's a simple example of how you can use Pydantic with ARQ to:

1. Define a model for your job data
2. Serialize data when enqueueing jobs
3. Validate and deserialize data when processing jobs

```python {test="skip"}
import asyncio
from typing import Any

from arq import create_pool
from arq.connections import RedisSettings

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


REDIS_SETTINGS = RedisSettings()


async def process_user(ctx: dict[str, Any], user_data: dict[str, Any]) -> None:
    user = User.model_validate(user_data)
    print(f'Processing user: {repr(user)}')


async def enqueue_jobs(redis):
    user1 = User(id=1, name='John Doe', email='john@example.com')
    user2 = User(id=2, name='Jane Doe', email='jane@example.com')

    await redis.enqueue_job('process_user', user1.model_dump())
    print(f'Enqueued user: {repr(user1)}')

    await redis.enqueue_job('process_user', user2.model_dump())
    print(f'Enqueued user: {repr(user2)}')


class WorkerSettings:
    functions = [process_user]
    redis_settings = REDIS_SETTINGS


async def main():
    redis = await create_pool(REDIS_SETTINGS)
    await enqueue_jobs(redis)


if __name__ == '__main__':
    asyncio.run(main())
```

This script is complete.
It should run "as is" both to enqueue jobs and to process them.
<!-- TODO: kafka, celery, etc - better for SEO, great for new contributors! -->
````

## File: docs/examples/requests.md
````markdown
Pydantic models are a great way to validating and serializing data for requests and responses.
Pydantic is instrumental in many web frameworks and libraries, such as FastAPI, Django, Flask, and HTTPX.

## `httpx` requests

[`httpx`](https://www.python-httpx.org/) is a HTTP client for Python 3 with synchronous and asynchronous APIs.
In the below example, we query the [JSONPlaceholder API](https://jsonplaceholder.typicode.com/) to get a user's data and validate it with a Pydantic model.

```python {test="skip"}
import httpx

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


url = 'https://jsonplaceholder.typicode.com/users/1'

response = httpx.get(url)
response.raise_for_status()

user = User.model_validate(response.json())
print(repr(user))
#> User(id=1, name='Leanne Graham', email='Sincere@april.biz')
```

The [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] tool from Pydantic often comes in quite
handy when working with HTTP requests. Consider a similar example where we are validating a list of users:

```python {test="skip"}
from pprint import pprint

import httpx

from pydantic import BaseModel, EmailStr, TypeAdapter


class User(BaseModel):
    id: int
    name: str
    email: EmailStr


url = 'https://jsonplaceholder.typicode.com/users/'  # (1)!

response = httpx.get(url)
response.raise_for_status()

users_list_adapter = TypeAdapter(list[User])

users = users_list_adapter.validate_python(response.json())
pprint([u.name for u in users])
"""
['Leanne Graham',
 'Ervin Howell',
 'Clementine Bauch',
 'Patricia Lebsack',
 'Chelsey Dietrich',
 'Mrs. Dennis Schulist',
 'Kurtis Weissnat',
 'Nicholas Runolfsdottir V',
 'Glenna Reichert',
 'Clementina DuBuque']
"""
```

1. Note, we're querying the `/users/` endpoint here to get a list of users.

<!-- TODO: httpx, flask, Django rest framework, FastAPI -->
````

## File: docs/integrations/aws_lambda.md
````markdown
`pydantic` integrates well with AWS Lambda functions. In this guide, we'll discuss how to setup `pydantic` for an AWS Lambda function.

## Installing Python libraries for AWS Lambda functions

There are many ways to utilize Python libraries in AWS Lambda functions. As outlined in the [AWS Lambda documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html), the most common approaches include:

* Using a [`.zip` file archive](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html) to package your code and dependencies
* Using [AWS Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/python-layers.html) to share libraries across multiple functions
* Using a [container image](https://docs.aws.amazon.com/lambda/latest/dg/python-image.html) to package your code and dependencies

All of these approaches can be used with `pydantic`. The best approach for you will depend on your specific requirements and constraints. We'll cover the first two cases more in-depth here, as dependency management with
a container image is more straightforward. If you're using a container image, you might find [this comment](https://github.com/pydantic/pydantic/issues/6557#issuecomment-1699456562) helpful for installing `pydantic`.

!!! tip
    If you use `pydantic` across multiple functions, you may want to consider AWS Lambda Layers, which support seamless sharing of libraries across multiple functions.

Regardless of the dependencies management approach you choose, it's beneficial to adhere to these guidelines to ensure a smooth
dependency management process.

## Installing `pydantic` for AWS Lambda functions

When you're building your `.zip` file archive with your code and dependencies or organizing your `.zip` file for a Lambda Layer, you'll likely use a local virtual environment to install and manage your dependencies. This can be a bit tricky if you're using `pip` because `pip` installs wheels compiled for your local platform, which may not be compatible with the Lambda environment.

Thus, we suggest you use a command similar to the following:

```bash
pip install \
    --platform manylinux2014_x86_64 \  # (1)!
    --target=<your_package_dir> \  # (2)!
    --implementation cp \  # (3)!
    --python-version 3.10 \  # (4)!
    --only-binary=:all: \  # (5)!
    --upgrade pydantic  # (6)!
```

1. Use the platform corresponding to your Lambda runtime.
2. Specify the directory where you want to install the package (often `python` for Lambda Layers).
3. Use the CPython implementation.
4. The Python version must be compatible with the Lambda runtime.
5. This flag ensures that the package is installed pre-built binary wheels.
6. The latest version of `pydantic` will be installed.

## Troubleshooting

### Missing `pydantic_core` module

The

```output
no module named `pydantic_core._pydantic_core`
```

error is a common issue that indicates you have installed `pydantic` incorrectly. To debug this issue, you can try the following steps (before the failing import):

1. Check the contents of the installed `pydantic-core` package. Are the compiled library and its type stubs both present?

    ```python {test="skip" lint="skip"}
    from importlib.metadata import files
    print([file for file in files('pydantic-core') if file.name.startswith('_pydantic_core')])
    """
    [PackagePath('pydantic_core/_pydantic_core.pyi'), PackagePath('pydantic_core/_pydantic_core.cpython-312-x86_64-linux-gnu.so')]
    """
    ```

    You should expect to see two files like those printed above. The compiled library file should have the `.so` or `.pyd` extension with a name that varies according to the OS and Python version.

2. Check that your lambda's Python version is compatible with the compiled library version found above.

    ```python {test="skip" lint="skip"}
    import sysconfig
    print(sysconfig.get_config_var("EXT_SUFFIX"))
    #> '.cpython-312-x86_64-linux-gnu.so'
    ```

You should expect to see the same suffix here as the compiled library, for example here we see this suffix `.cpython-312-x86_64-linux-gnu.so` indeed matches `_pydantic_core.cpython-312-x86_64-linux-gnu.so`.

If these two checks do not match, your build steps have not installed the correct native code for your lambda's target platform. You should adjust your build steps to change the version of the installed library which gets installed.

Most likely errors:

* Your OS or CPU architecture is mismatched (e.g. darwin vs x86_64-linux-gnu). Try passing correct `--platform` argument to `pip install` when installing your lambda dependencies, or build inside a linux docker container for the correct platform. Possible platforms at the moment include `--platform manylinux2014_x86_64` or `--platform manylinux2014_aarch64`, but these may change with a future Pydantic major release.

* Your Python version is mismatched (e.g. `cpython-310` vs `cpython-312`). Try passing correct `--python-version` argument to `pip install`, or otherwise change the Python version used on your build.

### No package metadata was found for `email-validator`

Pydantic uses `version` from `importlib.metadata` to [check what version](https://github.com/pydantic/pydantic/pull/6033) of `email-validator` is installed.
This package versioning mechanism is somewhat incompatible with AWS Lambda, even though it's the industry standard for versioning packages in Python. There
are a few ways to fix this issue:

If you're deploying your lambda with the serverless framework, it's likely that the appropriate metadata for the `email-validator` package is not being included in your deployment package. Tools like [`serverless-python-requirements`](https://github.com/serverless/serverless-python-requirements/tree/master)
remove metadata to reduce package size. You can fix this issue by setting the `slim` setting to false in your `serverless.yml` file:

```yaml
pythonRequirements:
    dockerizePip: non-linux
    slim: false
    fileName: requirements.txt
```

You can read more about this fix, and other `slim` settings that might be relevant [here](https://biercoff.com/how-to-fix-package-not-found-error-importlib-metadata/).

If you're using a `.zip` archive for your code and/or dependencies, make sure that your package contains the required version metadata. To do this, make sure you include the `dist-info` directory in your `.zip` archive for the `email-validator` package.

This issue has been reported for other popular python libraries like [`jsonschema`](https://github.com/python-jsonschema/jsonschema/issues/584), so you can
read more about the issue and potential fixes there as well.

## Extra Resources

### More Debugging Tips

If you're still struggling with installing `pydantic` for your AWS Lambda, you might consult with [this issue](https://github.com/pydantic/pydantic/issues/6557), which covers a variety of problems and solutions encountered by other developers.

### Validating `event` and `context` data

Check out our [blog post](https://pydantic.dev/articles/lambda-intro) to learn more about how to use `pydantic` to validate `event` and `context` data in AWS Lambda functions.
````

## File: docs/integrations/datamodel_code_generator.md
````markdown
# Code Generation with datamodel-code-generator

The [datamodel-code-generator](https://github.com/koxudaxi/datamodel-code-generator/) project is a library and command-line utility to generate pydantic models from just about any data source, including:

* OpenAPI 3 (YAML/JSON)
* JSON Schema
* JSON/YAML/CSV Data (which will be converted to JSON Schema)
* Python dictionary (which will be converted to JSON Schema)
* GraphQL schema

Whenever you find yourself with any data convertible JSON but without pydantic models, this tool will allow you to generate type-safe model hierarchies on demand.

## Installation

```bash
pip install datamodel-code-generator
```

## Example

In this case, datamodel-code-generator creates pydantic models from a JSON Schema file.

```bash
datamodel-codegen  --input person.json --input-file-type jsonschema --output model.py
```

person.json:

```json
{
  "$id": "person.json",
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Person",
  "type": "object",
  "properties": {
    "first_name": {
      "type": "string",
      "description": "The person's first name."
    },
    "last_name": {
      "type": "string",
      "description": "The person's last name."
    },
    "age": {
      "description": "Age in years.",
      "type": "integer",
      "minimum": 0
    },
    "pets": {
      "type": "array",
      "items": [
        {
          "$ref": "#/definitions/Pet"
        }
      ]
    },
    "comment": {
      "type": "null"
    }
  },
  "required": [
      "first_name",
      "last_name"
  ],
  "definitions": {
    "Pet": {
      "properties": {
        "name": {
          "type": "string"
        },
        "age": {
          "type": "integer"
        }
      }
    }
  }
}
```

model.py:

```python {upgrade="skip" requires="3.10"}
# generated by datamodel-codegen:
#   filename:  person.json
#   timestamp: 2020-05-19T15:07:31+00:00
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, conint


class Pet(BaseModel):
    name: str | None = None
    age: int | None = None


class Person(BaseModel):
    first_name: str = Field(description="The person's first name.")
    last_name: str = Field(description="The person's last name.")
    age: conint(ge=0) | None = Field(None, description='Age in years.')
    pets: list[Pet] | None = None
    comment: Any | None = None
```

More information can be found on the
[official documentation](https://koxudaxi.github.io/datamodel-code-generator/)
````

## File: docs/integrations/devtools.md
````markdown
!!! note
    **Admission:** I (the primary developer of Pydantic) also develop python-devtools.

[python-devtools](https://python-devtools.helpmanual.io/) (`pip install devtools`) provides a number of tools which
are useful during Python development, including `debug()` an alternative to `print()` which formats output in a way
which should be easier to read than `print` as well as giving information about which file/line the print statement
is on and what value was printed.

Pydantic integrates with *devtools* by implementing the `__pretty__` method on most public classes.

In particular `debug()` is useful when inspecting models:

```python {test="no-print-intercept"}
from datetime import datetime

from devtools import debug

from pydantic import BaseModel


class Address(BaseModel):
    street: str
    country: str
    lat: float
    lng: float


class User(BaseModel):
    id: int
    name: str
    signup_ts: datetime
    friends: list[int]
    address: Address


user = User(
    id='123',
    name='John Doe',
    signup_ts='2019-06-01 12:22',
    friends=[1234, 4567, 7890],
    address=dict(street='Testing', country='uk', lat=51.5, lng=0),
)
debug(user)
print('\nshould be much easier read than:\n')
print('user:', user)
```

Will output in your terminal:

{{ devtools_example }}

!!! note
    `python-devtools` doesn't yet support Python 3.13.
````

## File: docs/integrations/documentation.md
````markdown
Pydantic uses [MkDocs](https://www.mkdocs.org/) for documentation, together with
[mkdocstrings](https://mkdocstrings.github.io/). As such, you can make use of Pydantic's
Sphinx object inventory to cross-reference the Pydantic API documentation.

=== "Sphinx"

    In your [Sphinx configuration](https://www.sphinx-doc.org/en/master/usage/configuration.html),
    add the following to the [`intersphinx` extension configuration](https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration):

    ```python {test="skip"}
    intersphinx_mapping = {
        'pydantic': ('https://docs.pydantic.dev/latest', None),  # (1)!
    }
    ```

    1. You can also use `dev` instead of `latest` to target the latest documentation build, up to date
       with the [`main`](https://github.com/pydantic/pydantic/tree/main) branch.

=== "mkdocstrings"

    In your [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/), add the following
    import to your [mkdocstrings plugin configuration](https://mkdocstrings.github.io/usage/#cross-references-to-other-projects-inventories):

    ```yaml
    plugins:
    - mkdocstrings:
        handlers:
          python:
            import:
            - https://docs.pydantic.dev/latest/objects.inv  # (1)!
    ```

    1. You can also use `dev` instead of `latest` to target the latest documentation build, up to date
       with the [`main`](https://github.com/pydantic/pydantic/tree/main) branch.
````

## File: docs/integrations/hypothesis.md
````markdown
[Hypothesis](https://hypothesis.readthedocs.io/) is the Python library for
[property-based testing](https://increment.com/testing/in-praise-of-property-based-testing/).
Hypothesis can infer how to construct type-annotated classes, and supports builtin types,
many standard library types, and generic types from the
[`typing`](https://docs.python.org/3/library/typing.html) and
[`typing_extensions`](https://pypi.org/project/typing-extensions/) modules by default.

Pydantic v2.0 drops built-in support for Hypothesis and no more ships with the integrated Hypothesis plugin.

!!! warning
    We are temporarily removing the Hypothesis plugin in favor of studying a different mechanism. For more information, see the issue [annotated-types/annotated-types#37](https://github.com/annotated-types/annotated-types/issues/37).

    The Hypothesis plugin may be back in a future release. Subscribe to [pydantic/pydantic#4682](https://github.com/pydantic/pydantic/issues/4682) for updates.
````

## File: docs/integrations/linting.md
````markdown
## Flake8 plugin

If using Flake8 in your project, a [plugin](https://pypi.org/project/flake8-pydantic/) is available
and can be installed using the following:

```bash
pip install flake8-pydantic
```

The lint errors provided by this plugin are namespaced under the `PYDXXX` code. To ignore some unwanted
rules, the Flake8 configuration can be adapted:

```ini
[flake8]
extend-ignore = PYD001,PYD002
```
````

## File: docs/integrations/llms.md
````markdown
The Pydantic documentation is available in the [llms.txt](https://llmstxt.org/) format.
This format is defined in Markdown and suited for large language models.

Two formats are available:

* [llms.txt](https://docs.pydantic.dev/latest/llms.txt): a file containing a brief description
  of the project, along with links to the different sections of the documentation. The structure
  of this file is described in details [here](https://llmstxt.org/#format).
* [llms-full.txt](https://docs.pydantic.dev/latest/llms-full.txt): Similar to the `llms.txt` file,
  but every link content is included. Note that this file may be too large for some LLMs.

As of today, these files *cannot* be natively leveraged by LLM frameworks or IDEs. Alternatively,
a [MCP server](https://modelcontextprotocol.io/) can be implemented to properly parse the `llms.txt`
file.
````

## File: docs/integrations/logfire.md
````markdown
Pydantic integrates seamlessly with **Pydantic Logfire**, an observability platform built by us on the same belief as our open source library — that the most powerful tools can be easy to use.

## Getting Started

Logfire has an out-of-the-box Pydantic integration that lets you understand the data passing through your Pydantic models and get analytics on validations. For existing Pydantic users, it delivers unparalleled insights into your usage of Pydantic models.

[Getting started](https://logfire.pydantic.dev/docs/) with Logfire can be done in three simple steps:

1. Set up your Logfire account.
2. Install the Logfire SDK.
3. Instrument your project.

### Basic Usage

Once you've got Logfire set up, you can start using it to monitor your Pydantic models and get insights into your data validation:

```python {test="skip"}
from datetime import date

import logfire

from pydantic import BaseModel

logfire.configure()  # (1)!


class User(BaseModel):
    name: str
    country_code: str
    dob: date


user = User(name='Anne', country_code='USA', dob='2000-01-01')
logfire.info('user processed: {user!r}', user=user)  # (2)!
```

1. The `logfire.configure()` call is all you need to instrument your project with Logfire.
2. The `logfire.info()` call logs the `user` object to Logfire, with builtin support for Pydantic models.

![basic pydantic logfire usage](../img/basic_logfire.png)

### Pydantic Instrumentation

You can even record information about the validation process automatically by
using the builtin [Pydantic integration](https://logfire.pydantic.dev/docs/why-logfire/pydantic/):

```python {test="skip"}
from datetime import date

import logfire

from pydantic import BaseModel

logfire.configure()
logfire.instrument_pydantic()  # (1)!


class User(BaseModel):
    name: str
    country_code: str
    dob: date


User(name='Anne', country_code='USA', dob='2000-01-01')
User(name='David', country_code='GBR', dob='invalid-dob')
```

1. The `logfire.instrument_pydantic()` call automatically logs validation information for all Pydantic models in your project.

You'll see each successful and failed validation logged in Logfire:

![logfire instrumentation](../img/logfire_instrument.png)

And you can investigate each of the corresponding spans to get validation details:

![logfire span details](../img/logfire_span.png)

<!-- TODO: add examples re tracing performance issues - what kind of example do we want to use? -->
````

## File: docs/integrations/mypy.md
````markdown
Pydantic works well with [mypy](http://mypy-lang.org) right out of the box.

However, Pydantic also ships with a mypy plugin that adds a number of important Pydantic-specific
features that improve its ability to type-check your code.

For example, consider the following script:

```python {test="skip" linenums="1"}
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Model(BaseModel):
    age: int
    first_name = 'John'
    last_name: Optional[str] = None
    signup_ts: Optional[datetime] = None
    list_of_ints: list[int]


m = Model(age=42, list_of_ints=[1, '2', b'3'])
print(m.middle_name)  # not a model field!
Model()  # will raise a validation error for age and list_of_ints
```

Without any special configuration, mypy does not catch the [missing model field annotation](../errors/usage_errors.md#model-field-missing-annotation)
and errors about the `list_of_ints` argument which Pydantic parses correctly:

```output
15: error: List item 1 has incompatible type "str"; expected "int"  [list-item]
15: error: List item 2 has incompatible type "bytes"; expected "int"  [list-item]
16: error: "Model" has no attribute "middle_name"  [attr-defined]
17: error: Missing named argument "age" for "Model"  [call-arg]
17: error: Missing named argument "list_of_ints" for "Model"  [call-arg]
```

But [with the plugin enabled](#enabling-the-plugin), it gives the correct errors:

```output
9: error: Untyped fields disallowed  [pydantic-field]
16: error: "Model" has no attribute "middle_name"  [attr-defined]
17: error: Missing named argument "age" for "Model"  [call-arg]
17: error: Missing named argument "list_of_ints" for "Model"  [call-arg]
```

With the pydantic mypy plugin, you can fearlessly refactor your models knowing mypy will catch any mistakes
if your field names or types change.

Note that mypy already supports some features without using the Pydantic plugin, such as synthesizing a `__init__`
method for Pydantic models and dataclasses. See the [mypy plugin capabilities](#mypy-plugin-capabilities) for a list
of additional features.

The Pydantic mypy plugin is tested against the latest mypy version. Older versions might work but won't be tested.

## Enabling the Plugin

To enable the plugin, just add `pydantic.mypy` to the list of plugins in your
[mypy config file](https://mypy.readthedocs.io/en/latest/config_file.html):

=== "`mypy.ini`"

    ```ini
    [mypy]
    plugins = pydantic.mypy
    ```

=== "`pyproject.toml`"

    ```toml
    [tool.mypy]
    plugins = ['pydantic.mypy']
    ```

!!! note

    If you're using `pydantic.v1` models, you'll need to add `pydantic.v1.mypy` to your list of plugins.

See the [plugin configuration](#configuring-the-plugin) for more details.

## Mypy plugin capabilities

### Generate a `__init__` signature for Pydantic models

* Any required fields that don't have dynamically-determined aliases will be included as required
  keyword arguments.
* If the [`validate_by_name`][pydantic.ConfigDict.validate_by_name] model configuration value is set to
  `True`, the generated signature will use the field names rather than aliases.
* The [`init_forbid_extra`](#init_forbid_extra) and [`init_typed`](#init_typed) plugin configuration
  values can further fine-tune the synthesized `__init__` method.

### Generate a typed signature for `model_construct`

* The [`model_construct`][pydantic.BaseModel.model_construct] method is an alternative to model validation when input data is
  known to be valid and should not be parsed (see the [documentation](../concepts/models.md#creating-models-without-validation)).
  Because this method performs no runtime validation, static checking is important to detect errors.

### Support for frozen models

* If the [`frozen`][pydantic.ConfigDict.frozen] configuration is set to `True`, you will get
  an error if you try mutating a model field (see [faux immutability](../concepts/models.md#faux-immutability))

### Respect the type of the `Field`'s `default` and `default_factory`

* Field with both a `default` and a `default_factory` will result in an error during static checking.
* The type of the `default` and `default_factory` value must be compatible with the one of the field.

### Warn about the use of untyped fields

* While defining a field without an annotation will result in a [runtime error](../errors/usage_errors.md#model-field-missing-annotation),
  the plugin will also emit a type checking error.

### Prevent the use of required dynamic aliases

See the documentation of the [`warn_required_dynamic_aliases`](#warn_required_dynamic_aliases) plugin configuration value.

## Configuring the Plugin

To change the values of the plugin settings, create a section in your mypy config file called `[pydantic-mypy]`,
and add any key-value pairs for settings you want to override.

A configuration file with all plugin strictness flags enabled (and some other mypy strictness flags, too) might look like:

=== "`mypy.ini`"

    ```ini
    [mypy]
    plugins = pydantic.mypy

    follow_imports = silent
    warn_redundant_casts = True
    warn_unused_ignores = True
    disallow_any_generics = True
    no_implicit_reexport = True
    disallow_untyped_defs = True

    [pydantic-mypy]
    init_forbid_extra = True
    init_typed = True
    warn_required_dynamic_aliases = True
    ```

=== "`pyproject.toml`"

    ```toml
    [tool.mypy]
    plugins = ["pydantic.mypy"]

    follow_imports = "silent"
    warn_redundant_casts = true
    warn_unused_ignores = true
    disallow_any_generics = true
    no_implicit_reexport = true
    disallow_untyped_defs = true

    [tool.pydantic-mypy]
    init_forbid_extra = true
    init_typed = true
    warn_required_dynamic_aliases = true
    ```

### `init_typed`

Because Pydantic performs [data conversion](../concepts/models.md#data-conversion) by default, the following is still valid at runtime:

```python {test="skip" lint="skip"}
class Model(BaseModel):
    a: int


Model(a='1')
```

For this reason, the plugin will use [`Any`][typing.Any] for field annotations when synthesizing the `__init__` method,
unless `init_typed` is set or [strict mode](../concepts/strict_mode.md) is enabled on the model.

### `init_forbid_extra`

By default, Pydantic allows (and ignores) any extra provided argument:

```python {test="skip" lint="skip"}
class Model(BaseModel):
    a: int = 1


Model(unrelated=2)
```

For this reason, the plugin will add an extra `**kwargs: Any` parameter when synthesizing the `__init__` method, unless
`init_forbid_extra` is set or the [`extra`][pydantic.ConfigDict.extra] is set to `'forbid'`.

### `warn_required_dynamic_aliases`

Whether to error when using a dynamically-determined alias or alias generator on a model with
[`validate_by_name`][pydantic.ConfigDict.validate_by_name] set to `False`. If such aliases are
present, mypy cannot properly type check calls to `__init__`. In this case, it will default to
treating all arguments as not required.

!!! note "Compatibility with `Any` being disallowed"
    Some mypy configuration options (such as [`disallow_any_explicit`](https://mypy.readthedocs.io/en/stable/config_file.html#confval-disallow_any_explicit))
    will error because the synthesized `__init__` method contains [`Any`][typing.Any] annotations. To circumvent the issue, you will have
    to enable both `init_forbid_extra` and `init_typed`.
````

## File: docs/integrations/pycharm.md
````markdown
While pydantic will work well with any IDE out of the box, a
[PyCharm plugin](https://plugins.jetbrains.com/plugin/12861-pydantic)
offering improved pydantic integration is available on the JetBrains Plugins Repository for PyCharm.
You can install the plugin for free from the plugin marketplace
(PyCharm's Preferences -> Plugin -> Marketplace -> search "pydantic").

The plugin currently supports the following features:

* For `pydantic.BaseModel.__init__`:
    * Inspection
    * Autocompletion
    * Type-checking

* For fields of `pydantic.BaseModel`:
    * Refactor-renaming fields updates `__init__` calls, and affects sub- and super-classes
    * Refactor-renaming `__init__` keyword arguments updates field names, and affects sub- and super-classes

More information can be found on the
[official plugin page](https://plugins.jetbrains.com/plugin/12861-pydantic)
and [Github repository](https://github.com/koxudaxi/pydantic-pycharm-plugin).
````

## File: docs/integrations/rich.md
````markdown
Pydantic models may be printed with the [Rich](https://github.com/willmcgugan/rich) library which will add additional formatting and color to the output. Here's an example:

![Printing Pydantic models with Rich](../img/rich_pydantic.png)

See the Rich documentation on [pretty printing](https://rich.readthedocs.io/en/latest/pretty.html) for more information.
````

## File: docs/integrations/visual_studio_code.md
````markdown
Pydantic works well with any editor or IDE out of the box because it's made on top of standard Python type annotations.

When using [Visual Studio Code (VS Code)](https://code.visualstudio.com/), there are some **additional editor features** supported, comparable to the ones provided by the [PyCharm plugin](../integrations/pycharm.md).

This means that you will have **autocompletion** (or "IntelliSense") and **error checks** for types and required arguments even while creating new Pydantic model instances.

![pydantic autocompletion in VS Code](../img/vs_code_01.png)

## Configure VS Code

To take advantage of these features, you need to make sure you configure VS Code correctly, using the recommended settings.

In case you have a different configuration, here's a short overview of the steps.

### Install Pylance

You should use the [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension for VS Code. It is the recommended, next-generation, official VS Code plug-in for Python.

Pylance is installed as part of the [Python Extension for VS Code](https://marketplace.visualstudio.com/items?itemName=ms-python.python) by default, so it should probably just work. Otherwise, you can double check it's installed and enabled in your editor.

### Configure your environment

Then you need to make sure your editor knows the [Python environment](https://code.visualstudio.com/docs/python/python-tutorial#_install-and-use-packages) (probably a virtual environment) for your Python project.

This would be the environment in where you installed Pydantic.

### Configure Pylance

With the default configurations, you will get support for autocompletion, but Pylance might not check for type errors.

You can enable type error checks from Pylance with these steps:

* Open the "User Settings"
* Search for `Type Checking Mode`
* You will find an option under `Python › Analysis: Type Checking Mode`
* Set it to `basic` or `strict` (by default it's `off`)

![Type Checking Mode set to strict in VS Code](../img/vs_code_02.png)

Now you will not only get autocompletion when creating new Pydantic model instances but also error checks for **required arguments**.

![Required arguments error checks in VS Code](../img/vs_code_03.png)

And you will also get error checks for **invalid data types**.

![Invalid data types error checks in VS Code](../img/vs_code_04.png)

!!! note "Technical Details"
    Pylance is the VS Code extension, it's closed source, but free to use. Underneath, Pylance uses an open source tool (also from Microsoft) called [Pyright](https://github.com/microsoft/pyright) that does all the heavy lifting.

    You can read more about it in the [Pylance Frequently Asked Questions](https://github.com/microsoft/pylance-release/blob/main/FAQ.md#what-is-the-relationship-between-pylance-pyright-and-the-python-extension).

### Configure mypy

You might also want to configure mypy in VS Code to get mypy error checks inline in your editor (alternatively/additionally to Pylance).

This would include the errors detected by the [Pydantic mypy plugin](../integrations/mypy.md), if you configured it.

To enable mypy in VS Code, do the following:

* Open the "User Settings"
* Search for `Mypy Enabled`
* You will find an option under `Python › Linting: Mypy Enabled`
* Check the box (by default it's unchecked)

![mypy enabled in VS Code](../img/vs_code_05.png)

## Tips and tricks

Here are some additional tips and tricks to improve your developer experience when using VS Code with Pydantic.

### Strict errors

The way this additional editor support works is that Pylance will treat your Pydantic models as if they were Python's pure `dataclasses`.

And it will show **strict type error checks** about the data types passed in arguments when creating a new Pydantic model instance.

In this example you can see that it shows that a `str` of `'23'` is not a valid `int` for the argument `age`.

![VS Code strict type errors](../img/vs_code_06.png)

It would expect `age=23` instead of `age='23'`.

Nevertheless, the design, and one of the main features of Pydantic, is that it is very **lenient with data types**.

It will actually accept the `str` with value `'23'` and will convert it to an `int` with value `23`.

These strict error checks are **very useful** most of the time and can help you **detect many bugs early**. But there are cases, like with `age='23'`, where they could be inconvenient by reporting a "false positive" error.

---

This example above with `age='23'` is intentionally simple, to show the error and the differences in types.

But more common cases where these strict errors would be inconvenient would be when using more sophisticated data types, like `int` values for `datetime` fields, or `dict` values for Pydantic sub-models.

For example, this is valid for Pydantic:

```python {hl_lines="12 17"}
from pydantic import BaseModel


class Knight(BaseModel):
    title: str
    age: int
    color: str = 'blue'


class Quest(BaseModel):
    title: str
    knight: Knight


quest = Quest(
    title='To seek the Holy Grail', knight={'title': 'Sir Lancelot', 'age': 23}
)
```

The type of the field `knight` is declared with the class `Knight` (a Pydantic model) and the code is passing a literal `dict` instead. This is still valid for Pydantic, and the `dict` would be automatically converted to a `Knight` instance.

Nevertheless, it would be detected as a type error:

![VS Code strict type errors with model](../img/vs_code_07.png)

In those cases, there are several ways to disable or ignore strict errors in very specific places, while still preserving them in the rest of the code.

Below are several techniques to achieve it.

#### Disable type checks in a line

You can disable the errors for a specific line using a comment of:

```python
# type: ignore
```

or (to be specific to pylance/pyright):

```python
# pyright: ignore
```

([pyright](https://github.com/microsoft/pyright) is the language server used by Pylance.).

coming back to the example with `age='23'`, it would be:

```python {hl_lines="10"}
from pydantic import BaseModel


class Knight(BaseModel):
    title: str
    age: int
    color: str = 'blue'


lancelot = Knight(title='Sir Lancelot', age='23')  # pyright: ignore
```

that way Pylance and mypy will ignore errors in that line.

**Pros**: it's a simple change in that line to remove errors there.

**Cons**: any other error in that line will also be omitted, including type checks, misspelled arguments, required arguments not provided, etc.

#### Override the type of a variable

You can also create a variable with the value you want to use and declare its type explicitly with `Any`.

```python {hl_lines="1 11-12"}
from typing import Any

from pydantic import BaseModel


class Knight(BaseModel):
    title: str
    age: int
    color: str = 'blue'


age_str: Any = '23'
lancelot = Knight(title='Sir Lancelot', age=age_str)
```

that way Pylance and mypy will interpret the variable `age_str` as if they didn't know its type, instead of knowing it has a type of `str` when an `int` was expected (and then showing the corresponding error).

**Pros**: errors will be ignored only for a specific value, and you will still see any additional errors for the other arguments.

**Cons**: it requires importing `Any` and a new variable in a new line for each argument that needs ignoring errors.

#### Override the type of a value with `cast`

The same idea from the previous example can be put on the same line with the help of `cast()`.

This way, the type declaration of the value is overridden inline, without requiring another variable.

```python {hl_lines="1 11"}
from typing import Any, cast

from pydantic import BaseModel


class Knight(BaseModel):
    title: str
    age: int
    color: str = 'blue'


lancelot = Knight(title='Sir Lancelot', age=cast(Any, '23'))
```

`cast(Any, '23')` doesn't affect the value, it's still just `'23'`, but now Pylance and mypy will assume it is of type `Any`, which means, they will act as if they didn't know the type of the value.

So, this is the equivalent of the previous example, without the additional variable.

**Pros**: errors will be ignored only for a specific value, and you will still see any additional errors for the other arguments. There's no need for additional variables.

**Cons**: it requires importing `Any` and `cast`, and if you are not used to using `cast()`, it could seem strange at first.

### Config in class arguments

Pydantic has a rich set of [Model Configurations][pydantic.config.ConfigDict] available.

These configurations can be set in an internal `class Config` on each model:

```python {hl_lines="9-10"}
from pydantic import BaseModel


class Knight(BaseModel):
    model_config = dict(frozen=True)
    title: str
    age: int
    color: str = 'blue'
```

or passed as keyword arguments when defining the model class:

```python {hl_lines="4"}
from pydantic import BaseModel


class Knight(BaseModel, frozen=True):
    title: str
    age: int
    color: str = 'blue'
```

The specific configuration **`frozen`** (in beta) has a special meaning.

It prevents other code from changing a model instance once it's created, keeping it **"frozen"**.

When using the second version to declare `frozen=True` (with **keyword arguments** in the class definition),
Pylance can use it to help you check in your code and **detect errors** when something is trying to set values
in a model that is "frozen".

![VS Code strict type errors with model](../img/vs_code_08.png)

## Adding a default with `Field`

Pylance/pyright requires `default` to be a keyword argument to `Field` in order to infer that the field is optional.

```python
from pydantic import BaseModel, Field


class Knight(BaseModel):
    title: str = Field(default='Sir Lancelot')  # this is okay
    age: int = Field(
        23
    )  # this works fine at runtime but will case an error for pyright


lance = Knight()  # error: Argument missing for parameter "age"
```

This is a limitation of dataclass transforms and cannot be fixed in pydantic.

## Technical Details

!!! warning
    As a Pydantic user, you don't need the details below. Feel free to skip the rest of this section.

    These details are only useful for other library authors, etc.

This additional editor support works by making use of the [`@dataclass_transform` decorator](https://typing.python.org/en/latest/spec/dataclasses.html#the-dataclass-transform-decorator)
(introduced by [PEP 681](https://peps.python.org/pep-0681/)).

The standard provides a way for libraries like Pydantic and others to tell editors and tools that they (the editors) should treat these libraries (e.g. Pydantic) as if they were [dataclasses][dataclasses], providing autocompletion, type checks, etc.
````

## File: docs/internals/architecture.md
````markdown
!!! note
    This section is part of the *internals* documentation, and is partly targeted to contributors.

Starting with Pydantic V2, part of the codebase is written in Rust in a separate package called `pydantic-core`.
This was done partly in order to improve validation and serialization performance (with the cost of limited
customization and extendibility of the internal logic).

This architecture documentation will first cover how the two `pydantic` and `pydantic-core` packages interact
together, then will go through the architecture specifics for various patterns (model definition, validation,
serialization, JSON Schema).

Usage of the Pydantic library can be divided into two parts:

* Model definition, done in the `pydantic` package.
* Model validation and serialization, done in the `pydantic-core` package.

## Model definition

Whenever a Pydantic [`BaseModel`][pydantic.main.BaseModel] is defined, the metaclass
will analyze the body of the model to collect a number of elements:

* Defined annotations to build model fields (collected in the [`model_fields`][pydantic.main.BaseModel.model_fields] attribute).
* Model configuration, set with [`model_config`][pydantic.main.BaseModel.model_config].
* Additional validators/serializers.
* Private attributes, class variables, identification of generic parametrization, etc.

### Communicating between `pydantic` and `pydantic-core`: the core schema

We then need a way to communicate the collected information from the model definition to `pydantic-core`,
so that validation and serialization is performed accordingly. To do so, Pydantic uses the concept
of a core schema: a structured (and serializable) Python dictionary (represented using
[`TypedDict`][typing.TypedDict] definitions) describing a specific validation and serialization
logic. It is the core data structure used to communicate between the `pydantic` and `pydantic-core`
packages. Every core schema has a required `type` key, and extra properties depending on this `type`.

The generation of a core schema is handled in a single place, by the `GenerateSchema` class
(no matter if it is for a Pydantic model or anything else).

!!! note
    It is not possible to define a custom core schema. A core schema needs to be understood by the
    `pydantic-core` package, and as such we only support a fixed number of core schema types.
    This is also part of the reason why the `GenerateSchema` isn't truly exposed and properly
    documented.

    The core schema definitions can be found in the [`pydantic_core.core_schema`][] module.

In the case of a Pydantic model, a core schema will be constructed and set as the
[`__pydantic_core_schema__`][pydantic.main.BaseModel.__pydantic_core_schema__] attribute.

To illustrate what a core schema looks like, we will take the example of the
[`bool`][pydantic_core.core_schema.bool_schema] core schema:

```python {lint="skip" test="skip"}
class BoolSchema(TypedDict, total=False):
    type: Required[Literal['bool']]
    strict: bool
    ref: str
    metadata: Any
    serialization: SerSchema
```

When defining a Pydantic model with a boolean field:

```python
from pydantic import BaseModel, Field


class Model(BaseModel):
    foo: bool = Field(strict=True)
```

The core schema for the `foo` field will look like:

```python
{
    'type': 'bool',
    'strict': True,
}
```

As seen in the [`BoolSchema`][pydantic_core.core_schema.bool_schema] definition,
the serialization logic is also defined in the core schema.
If we were to define a custom serialization function for `foo` (1), the `serialization` key would look like:
{ .annotate }

1. For example using the [`field_serializer`][pydantic.functional_serializers.field_serializer] decorator:

    ```python {test="skip" lint="skip"}
    class Model(BaseModel):
        foo: bool = Field(strict=True)

        @field_serializer('foo', mode='plain')
        def serialize_foo(self, value: bool) -> Any:
            ...
    ```

```python {lint="skip" test="skip"}
{
    'type': 'function-plain',
    'function': <function Model.serialize_foo at 0x111>,
    'is_field_serializer': True,
    'info_arg': False,
    'return_schema': {'type': 'int'},
}
```

Note that this is also a core schema definition, just that it is only relevant for `pydantic-core` during serialization.

Core schemas cover a broad scope, and are used whenever we want to communicate between the Python and Rust side.
While the previous examples were related to validation and serialization, it could in theory be used for anything:
error management, extra metadata, etc.

### JSON Schema generation

You may have noticed that the previous serialization core schema has a `return_schema` key.
This is because the core schema is also used to generate the corresponding JSON Schema.

Similar to how the core schema is generated, the JSON Schema generation is handled by the
[`GenerateJsonSchema`][pydantic.json_schema.GenerateJsonSchema] class.
The [`generate`][pydantic.json_schema.GenerateJsonSchema.generate] method
is the main entry point and is given the core schema of that model.

Coming back to our `bool` field example, the [`bool_schema`][pydantic.json_schema.GenerateJsonSchema.bool_schema]
method will be given the previously generated [boolean core schema][pydantic_core.core_schema.bool_schema]
and will return the following JSON Schema:

```json
{
    {"type": "boolean"}
}
```

### Customizing the core schema and JSON schema

!!! abstract "Usage Documentation"
    [Custom types](../concepts/types.md#custom-types)

    [Implementing `__get_pydantic_core_schema__`](../concepts/json_schema.md#implementing-__get_pydantic_core_schema__)

    [Implementing `__get_pydantic_json_schema__`](../concepts/json_schema.md#implementing-__get_pydantic_json_schema__)

While the `GenerateSchema` and [`GenerateJsonSchema`][pydantic.json_schema.GenerateJsonSchema] classes handle
the creation of the corresponding schemas, Pydantic offers a way to customize them in some cases, following a wrapper pattern.
This customization is done through the `__get_pydantic_core_schema__` and `__get_pydantic_json_schema__` methods.

To understand this wrapper pattern, we will take the example of metadata classes used with [`Annotated`][typing.Annotated],
where the `__get_pydantic_core_schema__` method can be used:

```python
from typing import Annotated, Any

from pydantic_core import CoreSchema

from pydantic import GetCoreSchemaHandler, TypeAdapter


class MyStrict:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        schema = handler(source)  # (1)!
        schema['strict'] = True
        return schema


class MyGt:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        schema = handler(source)  # (2)!
        schema['gt'] = 1
        return schema


ta = TypeAdapter(Annotated[int, MyStrict(), MyGt()])
```

1. `MyStrict` is the first annotation to be applied. At this point, `schema = {'type': 'int'}`.
2. `MyGt` is the last annotation to be applied. At this point, `schema = {'type': 'int', 'strict': True}`.

When the `GenerateSchema` class builds the core schema for `Annotated[int, MyStrict(), MyGt()]`, it will
create an instance of a `GetCoreSchemaHandler` to be passed to the `MyGt.__get_pydantic_core_schema__` method. (1)
{ .annotate }

1. In the case of our [`Annotated`][typing.Annotated] pattern, the `GetCoreSchemaHandler` is defined in a nested way.
    Calling it will recursively call the other `__get_pydantic_core_schema__` methods until it reaches the `int` annotation,
    where a simple `{'type': 'int'}` schema is returned.

The `source` argument depends on the core schema generation pattern. In the case of [`Annotated`][typing.Annotated],
the `source` will be the type being annotated. When [defining a custom type](../concepts/types.md#as-a-method-on-a-custom-type),
the `source` will be the actual class where `__get_pydantic_core_schema__` is defined.

## Model validation and serialization

While model definition was scoped to the *class* level (i.e. when defining your model), model validation
and serialization happens at the *instance* level. Both these concepts are handled in `pydantic-core`
(providing a 5 to 20 performance increase compared to Pydantic V1), by using the previously built core schema.

`pydantic-core` exposes a [`SchemaValidator`][pydantic_core.SchemaValidator] and
[`SchemaSerializer`][pydantic_core.SchemaSerializer] class to perform these tasks:

```python
from pydantic import BaseModel


class Model(BaseModel):
    foo: int


model = Model.model_validate({'foo': 1})  # (1)!
dumped = model.model_dump()  # (2)!
```

1. The provided data is sent to `pydantic-core` by using the
   [`SchemaValidator.validate_python`][pydantic_core.SchemaValidator.validate_python] method.
   `pydantic-core` will validate (following the core schema of the model) the data and populate
   the model's `__dict__` attribute.
2. The `model` instance is sent to `pydantic-core` by using the
   [`SchemaSerializer.to_python`][pydantic_core.SchemaSerializer.to_python] method.
   `pydantic-core` will read the instance's `__dict__` attribute and built the appropriate result
   (again, following the core schema of the model).
````

## File: docs/internals/resolving_annotations.md
````markdown
!!! note
    This section is part of the *internals* documentation, and is partly targeted to contributors.

Pydantic heavily relies on [type hints][type hint] at runtime to build schemas for validation, serialization, etc.

While type hints were primarily introduced for static type checkers (such as [Mypy] or [Pyright]), they are
accessible (and sometimes evaluated) at runtime. This means that the following would fail at runtime,
because `Node` has yet to be defined in the current module:

```python {test="skip" lint="skip"}
class Node:
    """Binary tree node."""

    # NameError: name 'Node' is not defined:
    def __init__(self, l: Node, r: Node) -> None:
        self.left = l
        self.right = r
```

To circumvent this issue, forward references can be used (by wrapping the annotation in quotes).

In Python 3.7, [PEP 563] introduced the concept of *postponed evaluation of annotations*, meaning
with the `from __future__ import annotations` [future statement], type hints are stringified by default:

```python {requires="3.12" lint="skip"}
from __future__ import annotations

from pydantic import BaseModel


class Foo(BaseModel):
    f: MyType
    # Given the future import above, this is equivalent to:
    # f: 'MyType'


type MyType = int

print(Foo.__annotations__)
#> {'f': 'MyType'}
```

## The challenges of runtime evaluation

Static type checkers make use of the <abbr title="Abstract Syntax Tree">AST</abbr> to analyze the defined annotations.
Regarding the previous example, this has the benefit of being able to understand what `MyType` refers to when analyzing
the class definition of `Foo`, even if `MyType` isn't yet defined at runtime.

However, for runtime tools such as Pydantic, it is more challenging to correctly resolve these forward annotations.
The Python standard library provides some tools to do so ([`typing.get_type_hints()`][typing.get_type_hints],
[`inspect.get_annotations()`][inspect.get_annotations]), but they come with some limitations. Thus, they are
being re-implemented in Pydantic with improved support for edge cases.

As Pydantic as grown, it's adapted to support many edge cases requiring irregular patterns for annotation evaluation.
Some of these use cases aren't necessarily sound from a static type checking perspective. In v2.10, the internal
logic was refactored in an attempt to simplify and standardize annotation evaluation. Admittedly, backwards compatibility
posed some challenges, and there is still some noticeable scar tissue in the codebase because of this.There's a hope that
[PEP 649] (introduced in Python 3.14) will greatly simplify the process, especially when it comes to dealing with locals
of a function.

To evaluate forward references, Pydantic roughly follows the same logic as described in the documentation of the
[`typing.get_type_hints()`][typing.get_type_hints] function. That is, the built-in [`eval()`][eval] function is used
by passing the forward reference, a global, and a local namespace. The namespace fetching logic is defined in the
sections below.

## Resolving annotations at class definition

The following example will be used as a reference throughout this section:

```python {test="skip" lint="skip"}
# module1.py:
type MyType = int

class Base:
    f1: 'MyType'

# module2.py:
from pydantic import BaseModel

from module1 import Base

type MyType = str


def inner() -> None:
    type InnerType = bool

    class Model(BaseModel, Base):
        type LocalType = bytes

        f2: 'MyType'
        f3: 'InnerType'
        f4: 'LocalType'
        f5: 'UnknownType'

    type InnerType2 = complex
```

When the `Model` class is being built, different [namespaces][namespace] are at play. For each base class
of the `Model`'s [MRO][method resolution order] (in reverse order — that is, starting with `Base`), the
following logic is applied:

1. Fetch the `__annotations__` key from the current base class' `__dict__`, if present. For `Base`, this will be
   `{'f1': 'MyType'}`.
2. Iterate over the `__annotations__` items and try to evaluate the annotation [^1] using a custom wrapper around
   the built-in [`eval()`][eval] function. This function takes two `globals` and `locals` arguments:
     * The current module's `__dict__` is naturally used as `globals`. For `Base`, this will be
       `sys.modules['module1'].__dict__`.
     * For the `locals` argument, Pydantic will try to resolve symbols in the following namespaces, sorted by highest priority:
         * A namespace created on the fly, containing the current class name (`{cls.__name__: cls}`). This is done
           in order to support recursive references.
         * The locals of the current class (i.e. `cls.__dict__`). For `Model`, this will include `LocalType`.
         * The parent namespace of the class, if different from the globals described above. This is the
           [locals][frame.f_locals] of the frame where the class is being defined. For `Base`, because the class is being
           defined in the module directly, this namespace won't be used as it will result in the globals being used again.
           For `Model`, the parent namespace is the locals of the frame of `inner()`.
3. If the annotation failed to evaluate, it is kept as is, so that the model can be rebuilt at a later stage. This will
   be the case for `f5`.

The following table lists the resolved type annotations for every field, once the `Model` class has been created:

| Field name | Resolved annotation |
|------------|---------------------|
| `f1`       | [`int`][]           |
| `f2`       | [`str`][]           |
| `f3`       | [`bool`][]          |
| `f4`       | [`bytes`][]         |
| `f5`       | `'UnknownType'`     |

### Limitations and backwards compatibility concerns

While the namespace fetching logic is trying to be as accurate as possible, we still face some limitations:

<div class="annotate" markdown>

* The locals of the current class (`cls.__dict__`) may include irrelevant entries, most of them being dunder attributes.
  This means that the following annotation: `f: '__doc__'` will successfully (and unexpectedly) be resolved.
* When the `Model` class is being created inside a function, we keep a copy of the [locals][frame.f_locals] of the frame.
  This copy only includes the symbols defined in the locals when `Model` is being defined, meaning `InnerType2` won't be included
  (and will **not be** if doing a model rebuild at a later point!).
    * To avoid memory leaks, we use [weak references][weakref] to the locals of the function, meaning some forward references might
    not resolve outside the function (1).
    * Locals of the function are only taken into account for Pydantic models, but this pattern does not apply to dataclasses, typed
    dictionaries or named tuples.

</div>

1. Here is an example:

    ```python {test="skip" lint="skip"}
    def func():
        A = int

        class Model(BaseModel):
            f: 'A | Forward'

        return Model


    Model = func()

    Model.model_rebuild(_types_namespace={'Forward': str})
    # pydantic.errors.PydanticUndefinedAnnotation: name 'A' is not defined
    ```

For backwards compatibility reasons, and to be able to support valid use cases without having to rebuild models,
the namespace logic described above is a bit different when it comes to core schema generation.
Taking the following example:
{#backwards-compatibility-logic}

```python
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class Foo:
    a: 'Bar | None' = None


class Bar(BaseModel):
    b: Foo
```

Once the fields for `Bar` have been collected (meaning annotations resolved), the `GenerateSchema` class converts
every field into a core schema. When it encounters another class-like field type (such as a dataclass), it will
try to evaluate annotations, following roughly the same logic as [described above](#resolving-annotations-at-class-definition).
However, to evaluate the `'Bar | None'` annotation, `Bar` needs to be present in the globals or locals, which is normally
*not* the case: `Bar` is being created, so it is not "assigned" to the current module's `__dict__` at that point.

To avoid having to call [`model_rebuild()`][pydantic.BaseModel.model_rebuild] on `Bar`, both the parent namespace
(if `Bar` was to be defined inside a function, and [the namespace provided during a model rebuild](#model-rebuild-semantics))
and the `{Bar.__name__: Bar}` namespace are included in the locals during annotations evaluation of `Foo`
(with the lowest priority) (1).
{ .annotate }

1. This backwards compatibility logic can introduce some inconsistencies, such as the following:

    ```python {lint="skip"}
    from dataclasses import dataclass

    from pydantic import BaseModel


    @dataclass
    class Foo:
        # `a` and `b` shouldn't resolve:
        a: 'Model'
        b: 'Inner'


    def func():
        Inner = int

        class Model(BaseModel):
            foo: Foo

        Model.__pydantic_complete__
        #> True, should be False.
    ```

## Resolving annotations when rebuilding a model

When a forward reference fails to evaluate, Pydantic will silently fail and stop the core schema
generation process. This can be seen by inspecting the `__pydantic_core_schema__` of a model class:

```python {lint="skip"}
from pydantic import BaseModel


class Foo(BaseModel):
    f: 'MyType'


Foo.__pydantic_core_schema__
#> <pydantic._internal._mock_val_ser.MockCoreSchema object at 0x73cd0d9e6d00>
```

If you then properly define `MyType`, you can rebuild the model:

```python {test="skip" lint="skip"}
type MyType = int

Foo.model_rebuild()
Foo.__pydantic_core_schema__
#> {'type': 'model', 'schema': {...}, ...}
```

The [`model_rebuild()`][pydantic.BaseModel.model_rebuild] method uses a *rebuild namespace*, with the following semantics:
{#model-rebuild-semantics}

* If an explicit `_types_namespace` argument is provided, it is used as the rebuild namespace.
* If no namespace is provided, the namespace where the method is called will be used as the rebuild namespace.

This *rebuild namespace* will be merged with the model's parent namespace (if it was defined in a function) and used as is
(see the [backwards compatibility logic](#backwards-compatibility-logic) described above).

[Mypy]: https://www.mypy-lang.org/
[Pyright]: https://github.com/microsoft/pyright/
[PEP 563]: https://peps.python.org/pep-0563/
[PEP 649]: https://peps.python.org/pep-0649/
[future statement]: https://docs.python.org/3/reference/simple_stmts.html#future

[^1]: This is done unconditionally, as forward annotations can be only present *as part* of a type hint (e.g. `Optional['int']`), as dictated by
      the [typing specification](https://typing.readthedocs.io/en/latest/spec/annotations.html#string-annotations).
````

## File: docs/contributing.md
````markdown
We'd love you to contribute to Pydantic!

## Issues

Questions, feature requests and bug reports are all welcome as [discussions or issues](https://github.com/pydantic/pydantic/issues/new/choose).
**However, to report a security vulnerability, please see our [security policy](https://github.com/pydantic/pydantic/security/policy).**

To make it as simple as possible for us to help you, please include the output of the following call in your issue:

```bash
python -c "import pydantic.version; print(pydantic.version.version_info())"
```

If you're using Pydantic prior to **v2.0** please use:

```bash
python -c "import pydantic.utils; print(pydantic.utils.version_info())"
```

Please try to always include the above unless you're unable to install Pydantic or **know** it's not relevant
to your question or feature request.

## Pull Requests

It should be extremely simple to get started and create a Pull Request.
Pydantic is released regularly so you should see your improvements release in a matter of days or weeks 🚀.

Unless your change is trivial (typo, docs tweak etc.), please create an issue to discuss the change before
creating a pull request.

!!! note "Pydantic V1 is in maintenance mode"
    Pydantic v1 is in maintenance mode, meaning that only bug fixes and security fixes will be accepted.
    New features should be targeted at Pydantic v2.

    To submit a fix to Pydantic v1, use the `1.10.X-fixes` as a target branch.

If you're looking for something to get your teeth into, check out the
["help wanted"](https://github.com/pydantic/pydantic/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22)
label on github.

To make contributing as easy and fast as possible, you'll want to run tests and linting locally. Luckily,
Pydantic has few dependencies, doesn't require compiling and tests don't need access to databases, etc.
Because of this, setting up and running the tests should be very simple.

!!! tip
    **tl;dr**: use `make format` to fix formatting, `make` to run tests and linting and `make docs`
    to build the docs.

### Prerequisites

You'll need the following prerequisites:

* Any Python version between **Python 3.9 and 3.12**
* [**uv**](https://docs.astral.sh/uv/getting-started/installation/) or other virtual environment tool
* **git**
* **make**

### Installation and setup

Fork the repository on GitHub and clone your fork locally.

```bash
# Clone your fork and cd into the repo directory
git clone git@github.com:<your username>/pydantic.git
cd pydantic

# Install UV and pre-commit
# We use pipx here, for other options see:
# https://docs.astral.sh/uv/getting-started/installation/
# https://pre-commit.com/#install
# To get pipx itself:
# https://pypa.github.io/pipx/
pipx install uv
pipx install pre-commit

# Install pydantic, dependencies, test dependencies and doc dependencies
make install
```

### Check out a new branch and make your changes

Create a new branch for your changes.

```bash
# Checkout a new branch and make your changes
git checkout -b my-new-feature-branch
# Make your changes...
```

### Run tests and linting

Run tests and linting locally to make sure everything is working as expected.

```bash
# Run automated code formatting and linting
make format
# Pydantic uses ruff, an awesome Python linter written in rust
# https://github.com/astral-sh/ruff

# Run tests and linting
make
# There are a few sub-commands in Makefile like `test`, `testcov` and `lint`
# which you might want to use, but generally just `make` should be all you need.
# You can run `make help` to see more options.
```

### Build documentation

If you've made any changes to the documentation (including changes to function signatures, class definitions, or docstrings that will appear in the API documentation), make sure it builds successfully.

We use `mkdocs-material[imaging]` to support social previews.
You can find directions on how to install the required dependencies [here](https://squidfunk.github.io/mkdocs-material/plugins/requirements/image-processing/).

```bash
# Build documentation
make docs
# If you have changed the documentation, make sure it builds successfully.
# You can also use `uv run mkdocs serve` to serve the documentation at localhost:8000
```

If this isn't working due to issues with the imaging plugin, try commenting out the `social` plugin line in `mkdocs.yml` and running `make docs` again.

#### Updating the documentation

We push a new version of the documentation with each minor release, and we push to a `dev` path with each commit to `main`.

If you're updating the documentation out of cycle with a minor release and want your changes to be reflected on `latest`,
do the following:

1. Open a PR against `main` with your docs changes
2. Once the PR is merged, checkout the `docs-update` branch. This branch should be up to date with the latest patch release.
For example, if the latest release is `v2.9.2`, you should make sure `docs-update` is up to date with the `v2.9.2` tag.
3. Checkout a new branch from `docs-update` and cherry-pick your changes onto this branch.
4. Push your changes and open a PR against `docs-update`.
5. Once the PR is merged, the new docs will be built and deployed.

!!! note
    Maintainer shortcut - as a maintainer, you can skip the second PR and just cherry pick directly onto the `docs-update` branch.

### Commit and push your changes

Commit your changes, push your branch to GitHub, and create a pull request.

Please follow the pull request template and fill in as much information as possible. Link to any relevant issues and include a description of your changes.

When your pull request is ready for review, add a comment with the message "please review" and we'll take a look as soon as we can.

## Documentation style

Documentation is written in Markdown and built using [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/). API documentation is build from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

### Code documentation

When contributing to Pydantic, please make sure that all code is well documented. The following should be documented using properly formatted docstrings:

* Modules
* Class definitions
* Function definitions
* Module-level variables

Pydantic uses [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) formatted according to [PEP 257](https://www.python.org/dev/peps/pep-0257/) guidelines. (See [Example Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for further examples.)

[pydocstyle](https://www.pydocstyle.org/en/stable/index.html) is used for linting docstrings. You can run `make format` to check your docstrings.

Where this is a conflict between Google-style docstrings and pydocstyle linting, follow the pydocstyle linting hints.

Class attributes and function arguments should be documented in the format "name: description." When applicable, a return type should be documented with just a description. Types are inferred from the signature.

```python
class Foo:
    """A class docstring.

    Attributes:
        bar: A description of bar. Defaults to "bar".
    """

    bar: str = 'bar'
```

```python
def bar(self, baz: int) -> str:
    """A function docstring.

    Args:
        baz: A description of `baz`.

    Returns:
        A description of the return value.
    """

    return 'bar'
```

You may include example code in docstrings. This code should be complete, self-contained, and runnable. Docstring examples are tested, so make sure they are correct and complete. See [`FieldInfo.from_annotated_attribute`][pydantic.fields.FieldInfo.from_annotated_attribute] for an example.

!!! note "Class and instance attributes"
    Class attributes should be documented in the class docstring.

    Instance attributes should be documented as "Args" in the `__init__` docstring.

### Documentation Style

In general, documentation should be written in a friendly, approachable style. It should be easy to read and understand, and should be as concise as possible while still being complete.

Code examples are encouraged, but should be kept short and simple. However, every code example should be complete, self-contained, and runnable. (If you're not sure how to do this, ask for help!) We prefer print output to naked asserts, but if you're testing something that doesn't have a useful print output, asserts are fine.

Pydantic's unit test will test all code examples in the documentation, so it's important that they are correct and complete. When adding a new code example, use the following to test examples and update their formatting and output:

```bash
# Run tests and update code examples
pytest tests/test_docs.py --update-examples
```

## Debugging Python and Rust

If you're working with `pydantic` and `pydantic-core`, you might find it helpful to debug Python and Rust code together.
Here's a quick guide on how to do that. This tutorial is done in VSCode, but you can use similar steps in other IDEs.

<div style="position: relative; padding-bottom: 56.4035546262415%; height: 0;">
    <iframe src="https://www.loom.com/embed/71019f8b92b04839ae233eb70c23c5b5?sid=1ea39ca9-d0cc-494b-8214-159f7cc26190" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    </iframe>
</div>

## Badges

[![Pydantic v1](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v1.json)](https://pydantic.dev)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)

Pydantic has a badge that you can use to show that your project uses Pydantic. You can use this badge in your `README.md`:

### With Markdown

```md
[![Pydantic v1](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v1.json)](https://pydantic.dev)

[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
```

### With reStructuredText

```rst
.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v1.json
    :target: https://pydantic.dev
    :alt: Pydantic

.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json
    :target: https://pydantic.dev
    :alt: Pydantic
```

### With HTML

```html
<a href="https://pydantic.dev"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v1.json" alt="Pydantic Version 1" style="max-width:100%;"></a>

<a href="https://pydantic.dev"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json" alt="Pydantic Version 2" style="max-width:100%;"></a>
```

## Adding your library as part of Pydantic's third party test suite

To be able to identify regressions early during development, Pydantic runs tests on various third-party projects
using Pydantic. We consider adding support for testing new open source projects (that rely heavily on Pydantic) if your said project matches some of the following criteria:

* The project is actively maintained.
* The project makes use of Pydantic internals (e.g. relying on the [`BaseModel`][pydantic.BaseModel] metaclass, typing utilities).
* The project is popular enough (although small projects can still be included depending on how Pydantic is being used).
* The project CI is simple enough to be ported into Pydantic's testing workflow.

If your project meets some of these criteria, you can [open feature request][open feature request]
to discuss the inclusion of your project.

[open feature request]: https://github.com/pydantic/pydantic/issues/new?assignees=&labels=feature+request&projects=&template=feature_request.yml
````

## File: docs/help_with_pydantic.md
````markdown
# Getting help with Pydantic

If you need help getting started with Pydantic or with advanced usage, the following sources may be useful.

## :material-help: Usage Documentation

The [usage documentation](concepts/models.md) is the most complete guide on how to use Pydantic.

## :material-api: API Documentation

The [API documentation](api/base_model.md) gives reference docs for all public Pydantic APIs.

## :simple-github: GitHub Discussions

[GitHub discussions](https://github.com/pydantic/pydantic/discussions) are useful for asking questions, your question and the answer will help everyone.

## :simple-stackoverflow: Stack Overflow

Use the [`pydantic`](https://stackoverflow.com/questions/tagged/pydantic) tag on Stack Overflow to ask questions, note this is not always monitored by the core Pydantic team.

## :simple-youtube: YouTube

Youtube has lots of useful [videos on Pydantic](https://www.youtube.com/results?search_query=pydantic).

In particular Marcelo Trylesinski's video ["Pydantic V1 to V2 - The Migration"](https://youtu.be/sD_xpYl4fPU) has helped people a lot when migrating from Pydantic V1 to V2.
````

## File: docs/index.md
````markdown
# Pydantic Validation

[![CI](https://img.shields.io/github/actions/workflow/status/pydantic/pydantic/ci.yml?branch=main&logo=github&label=CI)](https://github.com/pydantic/pydantic/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)
[![Coverage](https://coverage-badge.samuelcolvin.workers.dev/pydantic/pydantic.svg)](https://github.com/pydantic/pydantic/actions?query=event%3Apush+branch%3Amain+workflow%3ACI)<br>
[![pypi](https://img.shields.io/pypi/v/pydantic.svg)](https://pypi.python.org/pypi/pydantic)
[![CondaForge](https://img.shields.io/conda/v/conda-forge/pydantic.svg)](https://anaconda.org/conda-forge/pydantic)
[![downloads](https://static.pepy.tech/badge/pydantic/month)](https://pepy.tech/project/pydantic)<br>
[![license](https://img.shields.io/github/license/pydantic/pydantic.svg)](https://github.com/pydantic/pydantic/blob/main/LICENSE)
[![llms.txt](https://img.shields.io/badge/llms.txt-green)](https://docs.pydantic.dev/latest/llms.txt)

{{ version }}.

Pydantic is the most widely used data validation library for Python.

Fast and extensible, Pydantic plays nicely with your linters/IDE/brain. Define how data should be in pure, canonical Python 3.9+; validate it with Pydantic.

!!! logfire "Monitor Pydantic with Pydantic Logfire :fire:"
    **[Pydantic Logfire](https://pydantic.dev/logfire)** is an application monitoring tool that is as simple to use and powerful as Pydantic itself.

    Logfire integrates with many popular Python libraries including FastAPI, OpenAI and Pydantic itself, so you can use Logfire to monitor Pydantic validations and understand why some inputs fail validation:

    ```python {title="Monitoring Pydantic with Logfire" test="skip"}
    from datetime import datetime

    import logfire

    from pydantic import BaseModel

    logfire.configure()
    logfire.instrument_pydantic()  # (1)!


    class Delivery(BaseModel):
        timestamp: datetime
        dimensions: tuple[int, int]


    # this will record details of a successful validation to logfire
    m = Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10', '20'])
    print(repr(m.timestamp))
    #> datetime.datetime(2020, 1, 2, 3, 4, 5, tzinfo=TzInfo(UTC))
    print(m.dimensions)
    #> (10, 20)

    Delivery(timestamp='2020-01-02T03:04:05Z', dimensions=['10'])  # (2)!
    ```

    1. Set logfire record all both successful and failed validations, use `record='failure'` to only record failed validations, [learn more](https://logfire.pydantic.dev/docs/integrations/pydantic/).
    2. This will raise a `ValidationError` since there are too few `dimensions`, details of the input data and validation errors will be recorded in Logfire.

    Would give you a view like this in the Logfire platform:

    [![Logfire Pydantic Integration](img/logfire-pydantic-integration.png)](https://logfire.pydantic.dev/docs/guides/web-ui/live/)

    This is just a toy example, but hopefully makes clear the potential value of instrumenting a more complex application.

    **[Learn more about Pydantic Logfire](https://logfire.pydantic.dev/docs/)**

    **Sign up to *The Pydantic Stack* newsletter, with updates & tutorials on Logfire, Pydantic AI and Pydantic:**

      <form method="POST" action="https://eu.customerioforms.com/forms/submit_action?site_id=53d2086c3c4214eaecaa&form_id=14b22611745b458&success_url=https://docs.pydantic.dev/" style="display: flex; align-items: center; gap: 10px; max-width: 85%;">
          <input
          type="email"
          id="email_input"
          name="email"
          class="md-input"
          style="border-bottom: none; flex: 1;"
          required
          placeholder="Email"
          data-1p-ignore
          data-lpignore="true"
          data-protonpass-ignore="true"
          data-bwignore="true"
          />
          <input type="hidden" id="source_input" name="source" value="pydantic" />
          <button type="submit" class="md-button" style="width: fit-content;">Subscribe</button>
      </form>

## Why use Pydantic?

* **Powered by type hints** &mdash; with Pydantic, schema validation and serialization are controlled by type annotations; less to learn, less code to write, and integration with your IDE and static analysis tools. [Learn more…](why.md#type-hints)
* **Speed** &mdash; Pydantic's core validation logic is written in Rust. As a result, Pydantic is among the fastest data validation libraries for Python. [Learn more…](why.md#performance)
* **JSON Schema** &mdash; Pydantic models can emit JSON Schema, allowing for easy integration with other tools. [Learn more…](why.md#json-schema)
* **Strict** and **Lax** mode &mdash; Pydantic can run in either strict mode (where data is not converted) or lax mode where Pydantic tries to coerce data to the correct type where appropriate. [Learn more…](why.md#strict-lax)
* **Dataclasses**, **TypedDicts** and more &mdash; Pydantic supports validation of many standard library types including `dataclass` and `TypedDict`. [Learn more…](why.md#dataclasses-typeddict-more)
* **Customisation** &mdash; Pydantic allows custom validators and serializers to alter how data is processed in many powerful ways. [Learn more…](why.md#customisation)
* **Ecosystem** &mdash; around 8,000 packages on PyPI use Pydantic, including massively popular libraries like
  *FastAPI*, *huggingface*, *Django Ninja*, *SQLModel*, & *LangChain*. [Learn more…](why.md#ecosystem)
* **Battle tested** &mdash; Pydantic is downloaded over 360M times/month and is used by all FAANG companies and 20 of the 25 largest companies on NASDAQ. If you're trying to do something with Pydantic, someone else has probably already done it. [Learn more…](why.md#using-pydantic)

[Installing Pydantic](install.md) is as simple as: `pip install pydantic`

## Pydantic examples

To see Pydantic at work, let's start with a simple example, creating a custom class that inherits from `BaseModel`:

```python {upgrade="skip" title="Validation Successful" requires="3.10"}
from datetime import datetime

from pydantic import BaseModel, PositiveInt


class User(BaseModel):
    id: int  # (1)!
    name: str = 'John Doe'  # (2)!
    signup_ts: datetime | None  # (3)!
    tastes: dict[str, PositiveInt]  # (4)!


external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',  # (5)!
    'tastes': {
        'wine': 9,
        b'cheese': 7,  # (6)!
        'cabbage': '1',  # (7)!
    },
}

user = User(**external_data)  # (8)!

print(user.id)  # (9)!
#> 123
print(user.model_dump())  # (10)!
"""
{
    'id': 123,
    'name': 'John Doe',
    'signup_ts': datetime.datetime(2019, 6, 1, 12, 22),
    'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},
}
"""
```

1. `id` is of type `int`; the annotation-only declaration tells Pydantic that this field is required. Strings,
   bytes, or floats will be coerced to integers if possible; otherwise an exception will be raised.
2. `name` is a string; because it has a default, it is not required.
3. `signup_ts` is a [`datetime`][datetime.datetime] field that is required, but the value `None` may be provided;
   Pydantic will process either a [Unix timestamp](https://en.wikipedia.org/wiki/Unix_time) integer (e.g. `1496498400`)
   or a string representing the date and time.
4. `tastes` is a dictionary with string keys and positive integer values. The `PositiveInt` type is
   shorthand for `Annotated[int, annotated_types.Gt(0)]`.
5. The input here is an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) formatted datetime, but Pydantic will
   convert it to a [`datetime`][datetime.datetime] object.
6. The key here is `bytes`, but Pydantic will take care of coercing it to a string.
7. Similarly, Pydantic will coerce the string `'1'` to the integer `1`.
8. We create instance of `User` by passing our external data to `User` as keyword arguments.
9. We can access fields as attributes of the model.
10. We can convert the model to a dictionary with [`model_dump()`][pydantic.BaseModel.model_dump].

If validation fails, Pydantic will raise an error with a breakdown of what was wrong:

```python {upgrade="skip" title="Validation Error" test="skip" lint="skip"}
# continuing the above example...

from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError


class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]


external_data = {'id': 'not an int', 'tastes': {}}  # (1)!

try:
    User(**external_data)  # (2)!
except ValidationError as e:
    print(e.errors())
    """
    [
        {
            'type': 'int_parsing',
            'loc': ('id',),
            'msg': 'Input should be a valid integer, unable to parse string as an integer',
            'input': 'not an int',
            'url': 'https://errors.pydantic.dev/2/v/int_parsing',
        },
        {
            'type': 'missing',
            'loc': ('signup_ts',),
            'msg': 'Field required',
            'input': {'id': 'not an int', 'tastes': {}},
            'url': 'https://errors.pydantic.dev/2/v/missing',
        },
    ]
    """
```

1. The input data is wrong here &mdash; `id` is not a valid integer, and `signup_ts` is missing.
2. Trying to instantiate `User` will raise a [`ValidationError`][pydantic_core.ValidationError] with a list of errors.

## Who is using Pydantic?

Hundreds of organisations and packages are using Pydantic. Some of the prominent companies and organizations around the world who are using Pydantic include:

{{ organisations }}

For a more comprehensive list of open-source projects using Pydantic see the
[list of dependents on github](https://github.com/pydantic/pydantic/network/dependents), or you can find some awesome projects using Pydantic in [awesome-pydantic](https://github.com/Kludex/awesome-pydantic).
````

## File: docs/install.md
````markdown
Installation is as simple as:

=== "pip"

    ```bash
    pip install pydantic
    ```

=== "uv"

    ```bash
    uv add pydantic
    ```

Pydantic has a few dependencies:

* [`pydantic-core`](https://pypi.org/project/pydantic-core/): Core validation logic for Pydantic written in Rust.
* [`typing-extensions`](https://pypi.org/project/typing-extensions/): Backport of the standard library [typing][] module.
* [`annotated-types`](https://pypi.org/project/annotated-types/): Reusable constraint types to use with [`typing.Annotated`][].

If you've got Python 3.9+ and `pip` installed, you're good to go.

Pydantic is also available on [conda](https://www.anaconda.com) under the [conda-forge](https://conda-forge.org)
channel:

```bash
conda install pydantic -c conda-forge
```

## Optional dependencies

Pydantic has the following optional dependencies:

* `email`: Email validation provided by the [email-validator](https://pypi.org/project/email-validator/) package.
* `timezone`: Fallback IANA time zone database provided by the [tzdata](https://pypi.org/project/tzdata/) package.

To install optional dependencies along with Pydantic:

=== "pip"

    ```bash
    # with the `email` extra:
    pip install 'pydantic[email]'
    # or with `email` and `timezone` extras:
    pip install 'pydantic[email,timezone]'
    ```

=== "uv"

    ```bash
    # with the `email` extra:
    uv add 'pydantic[email]'
    # or with `email` and `timezone` extras:
    uv add 'pydantic[email,timezone]'
    ```

Of course, you can also install requirements manually with `pip install email-validator tzdata`.

## Install from repository

And if you prefer to install Pydantic directly from the repository:

=== "pip"

    ```bash
    pip install 'git+https://github.com/pydantic/pydantic@main'
    # or with `email` and `timezone` extras:
    pip install 'git+https://github.com/pydantic/pydantic@main#egg=pydantic[email,timezone]'
    ```

=== "uv"

    ```bash
    uv add 'git+https://github.com/pydantic/pydantic@main'
    # or with `email` and `timezone` extras:
    uv add 'git+https://github.com/pydantic/pydantic@main#egg=pydantic[email,timezone]'
    ```
````

## File: docs/migration.md
````markdown
---
description: Migrating from Pydantic V1.
---

Pydantic V2 introduces a number of changes to the API, including some breaking changes.

This page provides a guide highlighting the most
important changes to help you migrate your code from Pydantic V1 to Pydantic V2.

## Install Pydantic V2

Pydantic V2 is now the current production release of Pydantic.
You can install Pydantic V2 from PyPI:

```bash
pip install -U pydantic
```

If you encounter any issues, please [create an issue in GitHub](https://github.com/pydantic/pydantic/issues) using
the `bug V2` label. This will help us to actively monitor and track errors, and to continue to improve the library's
performance.

If you need to use latest Pydantic V1 for any reason, see the [Continue using Pydantic V1 features](#continue-using-pydantic-v1-features) section below for details on installation and imports from `pydantic.v1`.

## Code transformation tool

We have created a tool to help you migrate your code. This tool is still in beta, but we hope it will help you to
migrate your code more quickly.

You can install the tool from PyPI:

```bash
pip install bump-pydantic
```

The usage is simple. If your project structure is:

    * repo_folder
        * my_package
            * <python source files> ...

Then you'll want to do:

    cd /path/to/repo_folder
    bump-pydantic my_package

See more about it on the [Bump Pydantic](https://github.com/pydantic/bump-pydantic) repository.

## Continue using Pydantic V1 features

Pydantic V1 is still available when you need it, though we recommend migrating to
Pydantic V2 for its improvements and new features.

If you need to use latest Pydantic V1, you can install it with:

```bash
pip install "pydantic==1.*"
```

The Pydantic V2 package also continues to provide access to the Pydantic V1 API
by importing through `pydantic.v1`.

For example, you can use the `BaseModel` class from Pydantic V1 instead of the
Pydantic V2 `pydantic.BaseModel` class:

```python {test="skip" lint="skip" upgrade="skip"}
from pydantic.v1 import BaseModel
```

You can also import functions that have been removed from Pydantic V2, such as `lenient_isinstance`:

```python {test="skip" lint="skip" upgrade="skip"}
from pydantic.v1.utils import lenient_isinstance
```

Pydantic V1 documentation is available at [https://docs.pydantic.dev/1.10/](https://docs.pydantic.dev/1.10/).

### Using Pydantic v1 features in a v1/v2 environment

As of `pydantic>=1.10.17`, the `pydantic.v1` namespace can be used within V1.
This makes it easier to migrate to V2, which also supports the `pydantic.v1`
namespace. In order to unpin a `pydantic<2` dependency and continue using V1
features, take the following steps:

1. Replace `pydantic<2` with `pydantic>=1.10.17`
2. Find and replace all occurrences of:

```python {test="skip" lint="skip" upgrade="skip"}
from pydantic.<module> import <object>
```

with:

```python {test="skip" lint="skip" upgrade="skip"}
from pydantic.v1.<module> import <object>
```

Here's how you can import `pydantic`'s v1 features based on your version of `pydantic`:

=== "`pydantic>=1.10.17,<3`"
    As of `v1.10.17` the `.v1` namespace is available in V1, allowing imports as below:

    ```python {test="skip" lint="skip" upgrade="skip"}
    from pydantic.v1.fields import ModelField
    ```

=== "`pydantic<3`"
    All versions of Pydantic V1 and V2 support the following import pattern, in case you don't
    know which version of Pydantic you are using:

    ```python {test="skip" lint="skip" upgrade="skip"}
    try:
        from pydantic.v1.fields import ModelField
    except ImportError:
        from pydantic.fields import ModelField
    ```

!!! note
    When importing modules using `pydantic>=1.10.17,<2` with the `.v1` namespace
    these modules will *not* be the **same** module as the same import without the `.v1`
    namespace, but the symbols imported *will* be. For example `pydantic.v1.fields is not pydantic.fields`
    but `pydantic.v1.fields.ModelField is pydantic.fields.ModelField`. Luckily, this is not likely to be relevant
    in the vast majority of cases. It's just an unfortunate consequence of providing a smoother migration experience.

## Migration guide

The following sections provide details on the most important changes in Pydantic V2.

### Changes to `pydantic.BaseModel`

Various method names have been changed; all non-deprecated `BaseModel` methods now have names matching either the
format `model_.*` or `__.*pydantic.*__`. Where possible, we have retained the deprecated methods with their old names
to help ease migration, but calling them will emit `DeprecationWarning`s.

| Pydantic V1 | Pydantic V2  |
| ----------- | ------------ |
| `__fields__` | `model_fields` |
| `__private_attributes__` | `__pydantic_private__` |
| `__validators__` | `__pydantic_validator__` |
| `construct()` | `model_construct()` |
| `copy()` | `model_copy()` |
| `dict()` | `model_dump()` |
| `json_schema()` | `model_json_schema()` |
| `json()` | `model_dump_json()` |
| `parse_obj()` | `model_validate()` |
| `update_forward_refs()` | `model_rebuild()` |

* Some of the built-in data-loading functionality has been slated for removal. In particular,
    `parse_raw` and `parse_file` are now deprecated. In Pydantic V2, `model_validate_json` works like `parse_raw`. Otherwise, you should load the data and then pass it to `model_validate`.
* The `from_orm` method has been deprecated; you can now just use `model_validate` (equivalent to `parse_obj` from
  Pydantic V1) to achieve something similar, as long as you've set `from_attributes=True` in the model config.
* The `__eq__` method has changed for models.
    * Models can only be equal to other `BaseModel` instances.
    * For two model instances to be equal, they must have the same:
        * Type (or, in the case of generic models, non-parametrized generic origin type)
        * Field values
        * Extra values (only relevant when `model_config['extra'] == 'allow'`)
        * Private attribute values; models with different values of private attributes are no longer equal.
        * Models are no longer equal to the dicts containing their data.
        * Non-generic models of different types are never equal.
        * Generic models with different origin types are never equal. We don't require *exact* type equality so that,
            for example, instances of `MyGenericModel[Any]` could be equal to instances of `MyGenericModel[int]`.
* We have replaced the use of the `__root__` field to specify a "custom root model" with a new type called
    [`RootModel`](concepts/models.md#rootmodel-and-custom-root-types) which is intended to replace the functionality of
    using a field called `__root__` in Pydantic V1. Note, `RootModel` types no longer support the `arbitrary_types_allowed`
    config setting. See [this issue comment](https://github.com/pydantic/pydantic/issues/6710#issuecomment-1700948167) for an explanation.
* We have significantly expanded Pydantic's capabilities related to customizing serialization. In particular, we have
    added the [`@field_serializer`](api/functional_serializers.md#pydantic.functional_serializers.field_serializer),
    [`@model_serializer`](api/functional_serializers.md#pydantic.functional_serializers.model_serializer), and
    [`@computed_field`](api/fields.md#pydantic.fields.computed_field) decorators, which each address various
    shortcomings from Pydantic V1.
    * See [Custom serializers](concepts/serialization.md#serializers) for the usage docs of these new decorators.
    * Due to performance overhead and implementation complexity, we have now deprecated support for specifying
        `json_encoders` in the model config. This functionality was originally added for the purpose of achieving custom
        serialization logic, and we think the new serialization decorators are a better choice in most common scenarios.
* We have changed the behavior related to serializing subclasses of models when they occur as nested fields in a parent
  model. In V1, we would always include all fields from the subclass instance. In V2, when we dump a model, we only
  include the fields that are defined on the annotated type of the field. This helps prevent some accidental security
  bugs. You can read more about this (including how to opt out of this behavior) in the
  [relevant section](concepts/serialization.md#subclasses-of-model-like-types) of the model exporting docs.
* `GetterDict` has been removed as it was just an implementation detail of `orm_mode`, which has been removed.
* In many cases, arguments passed to the constructor will be **copied** in order to perform validation and, where necessary, coercion.
  This is notable in the case of passing mutable objects as arguments to a constructor.
  You can see an example + more detail [here](https://docs.pydantic.dev/latest/concepts/models/#attribute-copies).
* The `.json()` method is deprecated, and attempting to use this deprecated method with arguments such as
`indent` or `ensure_ascii` may lead to confusing errors. For best results, switch to V2's equivalent, `model_dump_json()`.
If you'd still like to use said arguments, you can use [this workaround](https://github.com/pydantic/pydantic/issues/8825#issuecomment-1946206415).
* JSON serialization of non-string key values is generally done with `str(key)`, leading to some changes in behavior such as the following:

```python {test="skip"}
from typing import Optional

from pydantic import BaseModel as V2BaseModel
from pydantic.v1 import BaseModel as V1BaseModel


class V1Model(V1BaseModel):
    a: dict[Optional[str], int]


class V2Model(V2BaseModel):
    a: dict[Optional[str], int]


v1_model = V1Model(a={None: 123})
v2_model = V2Model(a={None: 123})

# V1
print(v1_model.json())
#> {"a": {"null": 123}}

# V2
print(v2_model.model_dump_json())
#> {"a":{"None":123}}
```

* `model_dump_json()` results are compacted in order to save space, and don't always exactly match that of `json.dumps()` output.
That being said, you can easily modify the separators used in `json.dumps()` results in order to align the two outputs:

```python {test="skip"}
import json

from pydantic import BaseModel as V2BaseModel
from pydantic.v1 import BaseModel as V1BaseModel


class V1Model(V1BaseModel):
    a: list[str]


class V2Model(V2BaseModel):
    a: list[str]


v1_model = V1Model(a=['fancy', 'sushi'])
v2_model = V2Model(a=['fancy', 'sushi'])

# V1
print(v1_model.json())
#> {"a": ["fancy", "sushi"]}

# V2
print(v2_model.model_dump_json())
#> {"a":["fancy","sushi"]}

# Plain json.dumps
print(json.dumps(v2_model.model_dump()))
#> {"a": ["fancy", "sushi"]}

# Modified json.dumps
print(json.dumps(v2_model.model_dump(), separators=(',', ':')))
#> {"a":["fancy","sushi"]}
```

### Changes to `pydantic.generics.GenericModel`

The `pydantic.generics.GenericModel` class is no longer necessary, and has been removed. Instead, you can now
create generic `BaseModel` subclasses by just adding `Generic` as a parent class on a `BaseModel` subclass directly.
This looks like `class MyGenericModel(BaseModel, Generic[T]): ...`.

Mixing of V1 and V2 models is not supported which means that type parameters of such generic `BaseModel` (V2)
cannot be V1 models.

While it may not raise an error, we strongly advise against using *parametrized* generics in `isinstance` checks.

* For example, you should not do `isinstance(my_model, MyGenericModel[int])`.
    However, it is fine to do `isinstance(my_model, MyGenericModel)`. (Note that for standard generics, it would raise
    an error to do a subclass check with a parameterized generic.)
* If you need to perform `isinstance` checks against parametrized generics, you can do this by subclassing the
    parametrized generic class. This looks like `class MyIntModel(MyGenericModel[int]): ...` and
    `isinstance(my_model, MyIntModel)`.

Find more information in the [Generic models](concepts/models.md#generic-models) documentation.

### Changes to `pydantic.Field`

`Field` no longer supports arbitrary keyword arguments to be added to the JSON schema. Instead, any extra
data you want to add to the JSON schema should be passed as a dictionary to the `json_schema_extra` keyword argument.

In Pydantic V1, the `alias` property returns the field's name when no alias is set.
In Pydantic V2, this behavior has changed to return `None` when no alias is set.

The following properties have been removed from or changed in `Field`:

* `const`
* `min_items` (use `min_length` instead)
* `max_items` (use `max_length` instead)
* `unique_items`
* `allow_mutation` (use `frozen` instead)
* `regex` (use `pattern` instead)
* `final` (use the [typing.Final][] type hint instead)

Field constraints are no longer automatically pushed down to the parameters of generics.  For example, you can no longer validate every element of a list matches a regex by providing `my_list: list[str] = Field(pattern=".*")`.  Instead, use [`typing.Annotated`][] to provide an annotation on the `str` itself: `my_list: list[Annotated[str, Field(pattern=".*")]]`

### Changes to dataclasses

Pydantic [dataclasses](concepts/dataclasses.md) continue to be useful for enabling the data validation on standard
dataclasses without having to subclass `BaseModel`. Pydantic V2 introduces the following changes to this dataclass behavior:

* When used as fields, dataclasses (Pydantic or vanilla) no longer accept tuples as validation inputs; dicts should be
  used instead.
* The `__post_init__` in Pydantic dataclasses will now be called *after* validation, rather than before.
    * As a result, the `__post_init_post_parse__` method would have become redundant, so has been removed.
* Pydantic no longer supports `extra='allow'` for Pydantic dataclasses, where extra fields passed to the initializer would be
    stored as extra attributes on the dataclass. `extra='ignore'` is still supported for the purpose of ignoring
    unexpected fields while parsing data, they just won't be stored on the instance.
* Pydantic dataclasses no longer have an attribute `__pydantic_model__`, and no longer use an underlying `BaseModel`
    to perform validation or provide other functionality.
    * To perform validation, generate a JSON schema, or make use of
        any other functionality that may have required `__pydantic_model__` in V1, you should now wrap the dataclass
        with a [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] ([discussed more below](#introduction-of-typeadapter)) and
        make use of its methods.
* In Pydantic V1, if you used a vanilla (i.e., non-Pydantic) dataclass as a field, the config of the parent type would
    be used as though it was the config for the dataclass itself as well. In Pydantic V2, this is no longer the case.
    * In Pydantic V2, to override the config (like you would with `model_config` on a `BaseModel`),
        you can use the `config` parameter on the `@dataclass` decorator.
        See [Dataclass Config](concepts/dataclasses.md#dataclass-config) for examples.

### Changes to config

* In Pydantic V2, to specify config on a model, you should set a class attribute called `model_config` to be a dict
  with the key/value pairs you want to be used as the config. The Pydantic V1 behavior to create a class called `Config`
  in the namespace of the parent `BaseModel` subclass is now deprecated.

* When subclassing a model, the `model_config` attribute is inherited. This is helpful in the case where you'd like to use
a base class with a given configuration for many models. Note, if you inherit from multiple `BaseModel` subclasses,
like `class MyModel(Model1, Model2)`, the non-default settings in the `model_config` attribute from the two models
will be merged, and for any settings defined in both, those from `Model2` will override those from `Model1`.

* The following config settings have been removed:
    * `allow_mutation` — this has been removed. You should be able to use [frozen](api/config.md#pydantic.config.ConfigDict) equivalently (inverse of current use).
    * `error_msg_templates`
    * `fields` — this was the source of various bugs, so has been removed.
      You should be able to use `Annotated` on fields to modify them as desired.
    * `getter_dict` — `orm_mode` has been removed, and this implementation detail is no longer necessary.
    * `smart_union` - the default `union_mode` in Pydantic V2 is `'smart'`.
    * `underscore_attrs_are_private` — the Pydantic V2 behavior is now the same as if this was always set
      to `True` in Pydantic V1.
    * `json_loads`
    * `json_dumps`
    * `copy_on_model_validation`
    * `post_init_call`

* The following config settings have been renamed:
    * `allow_population_by_field_name` → `populate_by_name` (or `validate_by_name` starting in v2.11)
    * `anystr_lower` → `str_to_lower`
    * `anystr_strip_whitespace` → `str_strip_whitespace`
    * `anystr_upper` → `str_to_upper`
    * `keep_untouched` → `ignored_types`
    * `max_anystr_length` → `str_max_length`
    * `min_anystr_length` → `str_min_length`
    * `orm_mode` → `from_attributes`
    * `schema_extra` → `json_schema_extra`
    * `validate_all` → `validate_default`

See the [`ConfigDict` API reference][pydantic.config.ConfigDict] for more details.

### Changes to validators

#### `@validator` and `@root_validator` are deprecated

* `@validator` has been deprecated, and should be replaced with [`@field_validator`](concepts/validators.md), which provides various new features
    and improvements.
    * The new `@field_validator` decorator does not have the `each_item` keyword argument; validators you want to
        apply to items within a generic container should be added by annotating the type argument. See
        [validators in Annotated metadata](concepts/types.md#using-the-annotated-pattern) for details.
        This looks like `list[Annotated[int, Field(ge=0)]]`
    * Even if you keep using the deprecated `@validator` decorator, you can no longer add the `field` or
        `config` arguments to the signature of validator functions. If you need access to these, you'll need
        to migrate to `@field_validator` — see the [next section](#changes-to-validators-allowed-signatures)
        for more details.
    * If you use the `always=True` keyword argument to a validator function, note that standard validators
        for the annotated type will *also* be applied even to defaults, not just the custom validators. For
        example, despite the fact that the validator below will never error, the following code raises a `ValidationError`:

!!! note
    To avoid this, you can use the `validate_default` argument in the `Field` function. When set to `True`, it mimics the behavior of `always=True` in Pydantic v1. However, the new way of using `validate_default` is encouraged as it provides more flexibility and control.

```python {test="skip"}
from pydantic import BaseModel, validator


class Model(BaseModel):
    x: str = 1

    @validator('x', always=True)
    @classmethod
    def validate_x(cls, v):
        return v


Model()
```

* `@root_validator` has been deprecated, and should be replaced with
    [`@model_validator`](api/functional_validators.md#pydantic.functional_validators.model_validator), which also provides new features and improvements.
    * Under some circumstances (such as assignment when `model_config['validate_assignment'] is True`),
        the `@model_validator` decorator will receive an instance of the model, not a dict of values. You may
        need to be careful to handle this case.
    * Even if you keep using the deprecated `@root_validator` decorator, due to refactors in validation logic,
        you can no longer run with `skip_on_failure=False` (which is the default value of this keyword argument,
        so must be set explicitly to `True`).

#### Changes to `@validator`'s allowed signatures

In Pydantic V1, functions wrapped by `@validator` could receive keyword arguments with metadata about what was
being validated. Some of these arguments have been removed from `@field_validator` in Pydantic V2:

* `config`: Pydantic V2's config is now a dictionary instead of a class, which means this argument is no longer
    backwards compatible. If you need to access the configuration you should migrate to `@field_validator` and use
    `info.config`.
* `field`: this argument used to be a `ModelField` object, which was a quasi-internal class that no longer exists
    in Pydantic V2. Most of this information can still be accessed by using the field name from `info.field_name`
    to index into `cls.model_fields`

```python
from pydantic import BaseModel, ValidationInfo, field_validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    def val_x(cls, v: int, info: ValidationInfo) -> int:
        assert info.config is not None
        print(info.config.get('title'))
        #> Model
        print(cls.model_fields[info.field_name].is_required())
        #> True
        return v


Model(x=1)
```

#### `TypeError` is no longer converted to `ValidationError` in validators

Previously, when raising a `TypeError` within a validator function, that error would be wrapped into a `ValidationError`
and, in some cases (such as with FastAPI), these errors might be displayed to end users. This led to a variety of
undesirable behavior &mdash; for example, calling a function with the wrong signature might produce a user-facing
`ValidationError`.

However, in Pydantic V2, when a `TypeError` is raised in a validator, it is no longer converted into a
`ValidationError`:

```python
import pytest

from pydantic import BaseModel, field_validator


class Model(BaseModel):
    x: int

    @field_validator('x')
    def val_x(cls, v: int) -> int:
        return str.lower(v)  # raises a TypeError


with pytest.raises(TypeError):
    Model(x=1)
```

This applies to all validation decorators.

#### Validator behavior changes

Pydantic V2 includes some changes to type coercion. For example:

* coercing `int`, `float`, and `Decimal` values to strings is now optional and disabled by default, see
  [Coerce Numbers to Strings][pydantic.config.ConfigDict.coerce_numbers_to_str].
* iterable of pairs is no longer coerced to a dict.

See the [Conversion table](concepts/conversion_table.md) for details on Pydantic V2 type coercion defaults.

#### The `allow_reuse` keyword argument is no longer necessary

Previously, Pydantic tracked "reused" functions in decorators as this was a common source of mistakes.
We did this by comparing the function's fully qualified name (module name + function name), which could result in false
positives. The `allow_reuse` keyword argument could be used to disable this when it was intentional.

Our approach to detecting repeatedly defined functions has been overhauled to only error for redefinition within a
single class, reducing false positives and bringing the behavior more in line with the errors that type checkers
and linters would give for defining a method with the same name multiple times in a single class definition.

In nearly all cases, if you were using `allow_reuse=True`, you should be able to simply delete that keyword argument and
have things keep working as expected.

#### `@validate_arguments` has been renamed to `@validate_call`

In Pydantic V2, the `@validate_arguments` decorator has been renamed to `@validate_call`.

In Pydantic V1, the decorated function had various attributes added, such as `raw_function`, and `validate`
(which could be used to validate arguments without actually calling the decorated function). Due to limited use of
these attributes, and performance-oriented changes in implementation, we have not preserved this functionality in
`@validate_call`.

### Input types are not preserved

In Pydantic V1 we made great efforts to preserve the types of all field inputs for generic collections when they were
proper subtypes of the field annotations. For example, given the annotation `Mapping[str, int]` if you passed in a
`collection.Counter()` you'd get a `collection.Counter()` as the value.

Supporting this behavior in V2 would have negative performance implications for the general case
(we'd have to check types every time) and would add a lot of complexity to validation. Further, even in V1 this behavior
was inconsistent and partially broken: it did not work for many types (`str`, `UUID`, etc.), and for generic
collections it's impossible to re-build the original input correctly without a lot of special casing
(consider `ChainMap`; rebuilding the input is necessary because we need to replace values after validation, e.g.
if coercing strings to ints).

In Pydantic V2 we no longer attempt to preserve the input type in all cases; instead, we only promise that the output
type will match the type annotations.

Going back to the `Mapping` example, we promise the output will be a valid `Mapping`, and in practice it will be a
plain `dict`:

```python
from typing import Mapping

from pydantic import TypeAdapter


class MyDict(dict):
    pass


ta = TypeAdapter(Mapping[str, int])
v = ta.validate_python(MyDict())
print(type(v))
#> <class 'dict'>
```

If you want the output type to be a specific type, consider annotating it as such or implementing a custom validator:

```python
from typing import Annotated, Any, Mapping, TypeVar

from pydantic import (
    TypeAdapter,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    WrapValidator,
)


def restore_input_type(
    value: Any, handler: ValidatorFunctionWrapHandler, _info: ValidationInfo
) -> Any:
    return type(value)(handler(value))


T = TypeVar('T')
PreserveType = Annotated[T, WrapValidator(restore_input_type)]


ta = TypeAdapter(PreserveType[Mapping[str, int]])


class MyDict(dict):
    pass


v = ta.validate_python(MyDict())
assert type(v) is MyDict
```

While we don't promise to preserve input types everywhere, we *do* preserve them for subclasses of `BaseModel`,
and for dataclasses:

```python
import pydantic.dataclasses
from pydantic import BaseModel


class InnerModel(BaseModel):
    x: int


class OuterModel(BaseModel):
    inner: InnerModel


class SubInnerModel(InnerModel):
    y: int


m = OuterModel(inner=SubInnerModel(x=1, y=2))
print(m)
#> inner=SubInnerModel(x=1, y=2)


@pydantic.dataclasses.dataclass
class InnerDataclass:
    x: int


@pydantic.dataclasses.dataclass
class SubInnerDataclass(InnerDataclass):
    y: int


@pydantic.dataclasses.dataclass
class OuterDataclass:
    inner: InnerDataclass


d = OuterDataclass(inner=SubInnerDataclass(x=1, y=2))
print(d)
#> OuterDataclass(inner=SubInnerDataclass(x=1, y=2))
```

### Changes to Handling of Standard Types

#### Dicts

Iterables of pairs (which include empty iterables) no longer pass validation for fields of type `dict`.

#### Unions

While union types will still attempt validation of each choice from left to right, they now preserve the type of the
input whenever possible, even if the correct type is not the first choice for which the input would pass validation.
As a demonstration, consider the following example:

```python
from typing import Union

from pydantic import BaseModel


class Model(BaseModel):
    x: Union[int, str]


print(Model(x='1'))
#> x='1'
```

In Pydantic V1, the printed result would have been `x=1`, since the value would pass validation as an `int`.
In Pydantic V2, we recognize that the value is an instance of one of the cases and short-circuit the standard union validation.

To revert to the non-short-circuiting left-to-right behavior of V1, annotate the union with `Field(union_mode='left_to_right')`.
See [Union Mode](./concepts/unions.md#union-modes) for more details.

#### Required, optional, and nullable fields

Pydantic V2 changes some of the logic for specifying whether a field annotated as `Optional` is required
(i.e., has no default value) or not (i.e., has a default value of `None` or any other value of the corresponding type), and now more closely matches the
behavior of `dataclasses`. Similarly, fields annotated as `Any` no longer have a default value of `None`.

The following table describes the behavior of field annotations in V2:

| State                                                 | Field Definition            |
|-------------------------------------------------------|-----------------------------|
| Required, cannot be `None`                            | `f1: str`                   |
| Not required, cannot be `None`, is `'abc'` by default | `f2: str = 'abc'`           |
| Required, can be `None`                               | `f3: Optional[str]`         |
| Not required, can be `None`, is `None` by default     | `f4: Optional[str] = None`  |
| Not required, can be `None`, is `'abc'` by default    | `f5: Optional[str] = 'abc'` |
| Required, can be any type (including `None`)          | `f6: Any`                   |
| Not required, can be any type (including `None`)      | `f7: Any = None`            |

!!! note
    A field annotated as `typing.Optional[T]` will be required, and will allow for a value of `None`.
    It does not mean that the field has a default value of `None`. *(This is a breaking change from V1.)*

!!! note
    Any default value if provided makes a field not required.

Here is a code example demonstrating the above:

```python
from typing import Optional

from pydantic import BaseModel, ValidationError


class Foo(BaseModel):
    f1: str  # required, cannot be None
    f2: Optional[str]  # required, can be None - same as str | None
    f3: Optional[str] = None  # not required, can be None
    f4: str = 'Foobar'  # not required, but cannot be None


try:
    Foo(f1=None, f2=None, f4='b')
except ValidationError as e:
    print(e)
    """
    1 validation error for Foo
    f1
      Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    """
```

#### Patterns / regex on strings

Pydantic V1 used Python's regex library. Pydantic V2 uses the Rust [regex crate].
This crate is not just a "Rust version of regular expressions", it's a completely different approach to regular expressions.
In particular, it promises linear time searching of strings in exchange for dropping a couple of features (namely look arounds and backreferences).
We believe this is a tradeoff worth making, in particular because Pydantic is used to validate untrusted input where ensuring things don't accidentally run in exponential time depending on the untrusted input is important.
On the flipside, for anyone not using these features complex regex validation should be orders of magnitude faster because it's done in Rust and in linear time.

If you still want to use Python's regex library, you can use the [`regex_engine`](./api/config.md#pydantic.config.ConfigDict.regex_engine) config setting.

[regex crate]: https://github.com/rust-lang/regex

### Type conversion from floats to integers

In V1, whenever a field was annotated as `int`, any float value would be accepted, which could lead to a potential data
loss if the float value contains a non-zero decimal part. In V2, type conversion from floats to integers is only allowed
if the decimal part is zero:

```python
from pydantic import BaseModel, ValidationError


class Model(BaseModel):
    x: int


print(Model(x=10.0))
#> x=10
try:
    Model(x=10.2)
except ValidationError as err:
    print(err)
    """
    1 validation error for Model
    x
      Input should be a valid integer, got a number with a fractional part [type=int_from_float, input_value=10.2, input_type=float]
    """
```

### Introduction of `TypeAdapter`

Pydantic V1 had weak support for validating or serializing non-`BaseModel` types.

To work with them, you had to either create a "root" model or use the utility functions in `pydantic.tools`
(namely, `parse_obj_as` and `schema_of`).

In Pydantic V2 this is *a lot* easier: the [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] class lets you create an object
with methods for validating, serializing, and producing JSON schemas for arbitrary types.
This serves as a complete replacement for `parse_obj_as` and `schema_of` (which are now deprecated),
and also covers some of the use cases of "root" models. ([`RootModel`](concepts/models.md#rootmodel-and-custom-root-types),
[discussed above](#changes-to-pydanticbasemodel), covers the others.)

```python
from pydantic import TypeAdapter

adapter = TypeAdapter(list[int])
assert adapter.validate_python(['1', '2', '3']) == [1, 2, 3]
print(adapter.json_schema())
#> {'items': {'type': 'integer'}, 'type': 'array'}
```

Due to limitations of inferring generic types with common type checkers, to get proper typing in some scenarios, you
may need to explicitly specify the generic parameter:

```python {test="skip"}
from pydantic import TypeAdapter

adapter = TypeAdapter[str | int](str | int)
...
```

See [Type Adapter](concepts/type_adapter.md) for more information.

### Defining custom types

We have completely overhauled the way custom types are defined in pydantic.

We have exposed hooks for generating both `pydantic-core` and JSON schemas, allowing you to get all the performance
benefits of Pydantic V2 even when using your own custom types.

We have also introduced ways to use [`typing.Annotated`][] to add custom validation to your own types.

The main changes are:

* `__get_validators__` should be replaced with `__get_pydantic_core_schema__`.
  See [Custom Data Types](concepts/types.md#customizing_validation_with_get_pydantic_core_schema) for more information.
* `__modify_schema__` becomes `__get_pydantic_json_schema__`.
  See [JSON Schema Customization](concepts/json_schema.md#customizing-json-schema) for more information.

Additionally, you can use [`typing.Annotated`][] to modify or provide the `__get_pydantic_core_schema__` and
`__get_pydantic_json_schema__` functions of a type by annotating it, rather than modifying the type itself.
This provides a powerful and flexible mechanism for integrating third-party types with Pydantic, and in some cases
may help you remove hacks from Pydantic V1 introduced to work around the limitations for custom types.

See [Custom Data Types](concepts/types.md#custom-types) for more information.

### Changes to JSON schema generation

We received many requests over the years to make changes to the JSON schemas that pydantic generates.

In Pydantic V2, we have tried to address many of the common requests:

* The JSON schema for `Optional` fields now indicates that the value `null` is allowed.
* The `Decimal` type is now exposed in JSON schema (and serialized) as a string.
* The JSON schema no longer preserves namedtuples as namedtuples.
* The JSON schema we generate by default now targets draft 2020-12 (with some OpenAPI extensions).
* When they differ, you can now specify if you want the JSON schema representing the inputs to validation,
    or the outputs from serialization.

However, there have been many reasonable requests over the years for changes which we have not chosen to implement.

In Pydantic V1, even if you were willing to implement changes yourself, it was very difficult because the JSON schema
generation process involved various recursive function calls; to override one, you'd have to copy and modify the whole
implementation.

In Pydantic V2, one of our design goals was to make it easier to customize JSON schema generation. To this end, we have
introduced the class [`GenerateJsonSchema`](api/json_schema.md#pydantic.json_schema.GenerateJsonSchema),
which implements the translation of a type's pydantic-core schema into
a JSON schema. By design, this class breaks the JSON schema generation process into smaller methods that can be
easily overridden in subclasses to modify the "global" approach to generating JSON schema.

The various methods that can be used to produce JSON schema (such as `BaseModel.model_json_schema` or
`TypeAdapter.json_schema`) accept a keyword argument `schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema`,
and you can pass your custom subclass to these methods in order to use your own approach to generating JSON schema.

Hopefully this means that if you disagree with any of the choices we've made, or if you are reliant on behaviors in
Pydantic V1 that have changed in Pydantic V2, you can use a custom `schema_generator`, modifying the
`GenerateJsonSchema` class as necessary for your application.

### `BaseSettings` has moved to `pydantic-settings`

[`BaseSettings`](api/pydantic_settings.md#pydantic_settings.BaseSettings), the base object for Pydantic
[settings management](concepts/pydantic_settings.md), has been moved to a separate package,
[`pydantic-settings`](https://github.com/pydantic/pydantic-settings).

Also, the `parse_env_var` classmethod has been removed. So, you need to
[customise settings sources](concepts/pydantic_settings.md#customise-settings-sources)
to have your own parsing function.

### Color and Payment Card Numbers moved to `pydantic-extra-types`

The following special-use types have been moved to the
[Pydantic Extra Types](https://github.com/pydantic/pydantic-extra-types) package,
which may be installed separately if needed.

* [Color Types](api/pydantic_extra_types_color.md)
* [Payment Card Numbers](api/pydantic_extra_types_payment.md)

### Url and Dsn types in `pydantic.networks` no longer inherit from `str`

In Pydantic V1 the [`AnyUrl`][pydantic.networks.AnyUrl] type inherited from `str`, and all the other
`Url` and `Dsn` types inherited from these. In Pydantic V2 these types are built on two new `Url` and `MultiHostUrl`
classes using `Annotated`.

Inheriting from `str` had upsides and downsides, and for V2 we decided it would be better to remove this. To use these
types in APIs which expect `str` you'll now need to convert them (with `str(url)`).

Pydantic V2 uses Rust's [Url](https://crates.io/crates/url) crate for URL validation.
Some of the URL validation differs slightly from the previous behavior in V1.
One notable difference is that the new `Url` types append slashes to the validated version if no path is included,
even if a slash is not specified in the argument to a `Url` type constructor. See the example below for this behavior:

```python
from pydantic import AnyUrl

assert str(AnyUrl(url='https://google.com')) == 'https://google.com/'
assert str(AnyUrl(url='https://google.com/')) == 'https://google.com/'
assert str(AnyUrl(url='https://google.com/api')) == 'https://google.com/api'
assert str(AnyUrl(url='https://google.com/api/')) == 'https://google.com/api/'
```

If you still want to use the old behavior without the appended slash, take a look at this [solution](https://github.com/pydantic/pydantic/issues/7186#issuecomment-1690235887).

### Constrained types

The `Constrained*` classes were *removed*, and you should replace them by `Annotated[<type>, Field(...)]`, for example:

```python {test="skip"}
from pydantic import BaseModel, ConstrainedInt


class MyInt(ConstrainedInt):
    ge = 0


class Model(BaseModel):
    x: MyInt
```

...becomes:

```python
from typing import Annotated

from pydantic import BaseModel, Field

MyInt = Annotated[int, Field(ge=0)]


class Model(BaseModel):
    x: MyInt
```

Read more about it in the [Composing types via `Annotated`](concepts/types.md#using-the-annotated-pattern)
docs.

For `ConstrainedStr` you can use [`StringConstraints`][pydantic.types.StringConstraints] instead.

### Mypy plugins

Pydantic V2 contains a [mypy](https://mypy.readthedocs.io/en/stable/extending_mypy.html#configuring-mypy-to-use-plugins) plugin in
`pydantic.mypy`.

When using [V1 features](migration.md#continue-using-pydantic-v1-features) the
`pydantic.v1.mypy` plugin might need to also be enabled.

To configure the mypy plugins:

=== "`mypy.ini`"

    ```ini
    [mypy]
    plugins = pydantic.mypy, pydantic.v1.mypy  # include `.v1.mypy` if required.
    ```

=== "`pyproject.toml`"

    ```toml
    [tool.mypy]
    plugins = [
        "pydantic.mypy",
        "pydantic.v1.mypy",  # include `.v1.mypy` if required.
    ]
    ```

## Other changes

* Dropped support for [`email-validator<2.0.0`](https://github.com/JoshData/python-email-validator). Make sure to update
  using `pip install -U email-validator`.

## Moved in Pydantic V2

| Pydantic V1 | Pydantic V2 |
| --- | --- |
| `pydantic.BaseSettings` | [`pydantic_settings.BaseSettings`](#basesettings-has-moved-to-pydantic-settings) |
| `pydantic.color` | [`pydantic_extra_types.color`][pydantic_extra_types.color] |
| `pydantic.types.PaymentCardBrand` | [`pydantic_extra_types.PaymentCardBrand`](#color-and-payment-card-numbers-moved-to-pydantic-extra-types) |
| `pydantic.types.PaymentCardNumber` | [`pydantic_extra_types.PaymentCardNumber`](#color-and-payment-card-numbers-moved-to-pydantic-extra-types) |
| `pydantic.utils.version_info` | [`pydantic.version.version_info`][pydantic.version.version_info] |
| `pydantic.error_wrappers.ValidationError` | [`pydantic.ValidationError`][pydantic_core.ValidationError] |
| `pydantic.utils.to_camel` | [`pydantic.alias_generators.to_pascal`][pydantic.alias_generators.to_pascal] |
| `pydantic.utils.to_lower_camel` | [`pydantic.alias_generators.to_camel`][pydantic.alias_generators.to_camel] |
| `pydantic.PyObject` | [`pydantic.ImportString`][pydantic.types.ImportString] |

## Deprecated and moved in Pydantic V2

| Pydantic V1 | Pydantic V2 |
| --- | --- |
| `pydantic.tools.schema_of` | `pydantic.deprecated.tools.schema_of` |
| `pydantic.tools.parse_obj_as` | `pydantic.deprecated.tools.parse_obj_as` |
| `pydantic.tools.schema_json_of` | `pydantic.deprecated.tools.schema_json_of` |
| `pydantic.json.pydantic_encoder` | `pydantic.deprecated.json.pydantic_encoder` |
| `pydantic.validate_arguments` | `pydantic.deprecated.decorator.validate_arguments` |
| `pydantic.json.custom_pydantic_encoder` | `pydantic.deprecated.json.custom_pydantic_encoder` |
| `pydantic.json.ENCODERS_BY_TYPE` | `pydantic.deprecated.json.ENCODERS_BY_TYPE` |
| `pydantic.json.timedelta_isoformat` | `pydantic.deprecated.json.timedelta_isoformat` |
| `pydantic.decorator.validate_arguments` | `pydantic.deprecated.decorator.validate_arguments` |
| `pydantic.class_validators.validator` | `pydantic.deprecated.class_validators.validator` |
| `pydantic.class_validators.root_validator` | `pydantic.deprecated.class_validators.root_validator` |
| `pydantic.utils.deep_update` | `pydantic.v1.utils.deep_update` |
| `pydantic.utils.GetterDict` | `pydantic.v1.utils.GetterDict` |
| `pydantic.utils.lenient_issubclass` | `pydantic.v1.utils.lenient_issubclass` |
| `pydantic.utils.lenient_isinstance` | `pydantic.v1.utils.lenient_isinstance` |
| `pydantic.utils.is_valid_field` | `pydantic.v1.utils.is_valid_field` |
| `pydantic.utils.update_not_none` | `pydantic.v1.utils.update_not_none` |
| `pydantic.utils.import_string` | `pydantic.v1.utils.import_string` |
| `pydantic.utils.Representation` | `pydantic.v1.utils.Representation` |
| `pydantic.utils.ROOT_KEY` | `pydantic.v1.utils.ROOT_KEY` |
| `pydantic.utils.smart_deepcopy` | `pydantic.v1.utils.smart_deepcopy` |
| `pydantic.utils.sequence_like` | `pydantic.v1.utils.sequence_like` |

## Removed in Pydantic V2

* `pydantic.ConstrainedBytes`
* `pydantic.ConstrainedDate`
* `pydantic.ConstrainedDecimal`
* `pydantic.ConstrainedFloat`
* `pydantic.ConstrainedFrozenSet`
* `pydantic.ConstrainedInt`
* `pydantic.ConstrainedList`
* `pydantic.ConstrainedSet`
* `pydantic.ConstrainedStr`
* `pydantic.JsonWrapper`
* `pydantic.NoneBytes`
    * This was an alias to `None | bytes`.
* `pydantic.NoneStr`
    * This was an alias to `None | str`.
* `pydantic.NoneStrBytes`
    * This was an alias to `None | str | bytes`.
* `pydantic.Protocol`
* `pydantic.Required`
* `pydantic.StrBytes`
    * This was an alias to `str | bytes`.
* `pydantic.compiled`
* `pydantic.config.get_config`
* `pydantic.config.inherit_config`
* `pydantic.config.prepare_config`
* `pydantic.create_model_from_namedtuple`
* `pydantic.create_model_from_typeddict`
* `pydantic.dataclasses.create_pydantic_model_from_dataclass`
* `pydantic.dataclasses.make_dataclass_validator`
* `pydantic.dataclasses.set_validation`
* `pydantic.datetime_parse.parse_date`
* `pydantic.datetime_parse.parse_time`
* `pydantic.datetime_parse.parse_datetime`
* `pydantic.datetime_parse.parse_duration`
* `pydantic.error_wrappers.ErrorWrapper`
* `pydantic.errors.AnyStrMaxLengthError`
* `pydantic.errors.AnyStrMinLengthError`
* `pydantic.errors.ArbitraryTypeError`
* `pydantic.errors.BoolError`
* `pydantic.errors.BytesError`
* `pydantic.errors.CallableError`
* `pydantic.errors.ClassError`
* `pydantic.errors.ColorError`
* `pydantic.errors.ConfigError`
* `pydantic.errors.DataclassTypeError`
* `pydantic.errors.DateError`
* `pydantic.errors.DateNotInTheFutureError`
* `pydantic.errors.DateNotInThePastError`
* `pydantic.errors.DateTimeError`
* `pydantic.errors.DecimalError`
* `pydantic.errors.DecimalIsNotFiniteError`
* `pydantic.errors.DecimalMaxDigitsError`
* `pydantic.errors.DecimalMaxPlacesError`
* `pydantic.errors.DecimalWholeDigitsError`
* `pydantic.errors.DictError`
* `pydantic.errors.DurationError`
* `pydantic.errors.EmailError`
* `pydantic.errors.EnumError`
* `pydantic.errors.EnumMemberError`
* `pydantic.errors.ExtraError`
* `pydantic.errors.FloatError`
* `pydantic.errors.FrozenSetError`
* `pydantic.errors.FrozenSetMaxLengthError`
* `pydantic.errors.FrozenSetMinLengthError`
* `pydantic.errors.HashableError`
* `pydantic.errors.IPv4AddressError`
* `pydantic.errors.IPv4InterfaceError`
* `pydantic.errors.IPv4NetworkError`
* `pydantic.errors.IPv6AddressError`
* `pydantic.errors.IPv6InterfaceError`
* `pydantic.errors.IPv6NetworkError`
* `pydantic.errors.IPvAnyAddressError`
* `pydantic.errors.IPvAnyInterfaceError`
* `pydantic.errors.IPvAnyNetworkError`
* `pydantic.errors.IntEnumError`
* `pydantic.errors.IntegerError`
* `pydantic.errors.InvalidByteSize`
* `pydantic.errors.InvalidByteSizeUnit`
* `pydantic.errors.InvalidDiscriminator`
* `pydantic.errors.InvalidLengthForBrand`
* `pydantic.errors.JsonError`
* `pydantic.errors.JsonTypeError`
* `pydantic.errors.ListError`
* `pydantic.errors.ListMaxLengthError`
* `pydantic.errors.ListMinLengthError`
* `pydantic.errors.ListUniqueItemsError`
* `pydantic.errors.LuhnValidationError`
* `pydantic.errors.MissingDiscriminator`
* `pydantic.errors.MissingError`
* `pydantic.errors.NoneIsAllowedError`
* `pydantic.errors.NoneIsNotAllowedError`
* `pydantic.errors.NotDigitError`
* `pydantic.errors.NotNoneError`
* `pydantic.errors.NumberNotGeError`
* `pydantic.errors.NumberNotGtError`
* `pydantic.errors.NumberNotLeError`
* `pydantic.errors.NumberNotLtError`
* `pydantic.errors.NumberNotMultipleError`
* `pydantic.errors.PathError`
* `pydantic.errors.PathNotADirectoryError`
* `pydantic.errors.PathNotAFileError`
* `pydantic.errors.PathNotExistsError`
* `pydantic.errors.PatternError`
* `pydantic.errors.PyObjectError`
* `pydantic.errors.PydanticTypeError`
* `pydantic.errors.PydanticValueError`
* `pydantic.errors.SequenceError`
* `pydantic.errors.SetError`
* `pydantic.errors.SetMaxLengthError`
* `pydantic.errors.SetMinLengthError`
* `pydantic.errors.StrError`
* `pydantic.errors.StrRegexError`
* `pydantic.errors.StrictBoolError`
* `pydantic.errors.SubclassError`
* `pydantic.errors.TimeError`
* `pydantic.errors.TupleError`
* `pydantic.errors.TupleLengthError`
* `pydantic.errors.UUIDError`
* `pydantic.errors.UUIDVersionError`
* `pydantic.errors.UrlError`
* `pydantic.errors.UrlExtraError`
* `pydantic.errors.UrlHostError`
* `pydantic.errors.UrlHostTldError`
* `pydantic.errors.UrlPortError`
* `pydantic.errors.UrlSchemeError`
* `pydantic.errors.UrlSchemePermittedError`
* `pydantic.errors.UrlUserInfoError`
* `pydantic.errors.WrongConstantError`
* `pydantic.main.validate_model`
* `pydantic.networks.stricturl`
* `pydantic.parse_file_as`
* `pydantic.parse_raw_as`
* `pydantic.stricturl`
* `pydantic.tools.parse_file_as`
* `pydantic.tools.parse_raw_as`
* `pydantic.types.JsonWrapper`
* `pydantic.types.NoneBytes`
* `pydantic.types.NoneStr`
* `pydantic.types.NoneStrBytes`
* `pydantic.types.PyObject`
* `pydantic.types.StrBytes`
* `pydantic.typing.evaluate_forwardref`
* `pydantic.typing.AbstractSetIntStr`
* `pydantic.typing.AnyCallable`
* `pydantic.typing.AnyClassMethod`
* `pydantic.typing.CallableGenerator`
* `pydantic.typing.DictAny`
* `pydantic.typing.DictIntStrAny`
* `pydantic.typing.DictStrAny`
* `pydantic.typing.IntStr`
* `pydantic.typing.ListStr`
* `pydantic.typing.MappingIntStrAny`
* `pydantic.typing.NoArgAnyCallable`
* `pydantic.typing.NoneType`
* `pydantic.typing.ReprArgs`
* `pydantic.typing.SetStr`
* `pydantic.typing.StrPath`
* `pydantic.typing.TupleGenerator`
* `pydantic.typing.WithArgsTypes`
* `pydantic.typing.all_literal_values`
* `pydantic.typing.display_as_type`
* `pydantic.typing.get_all_type_hints`
* `pydantic.typing.get_args`
* `pydantic.typing.get_origin`
* `pydantic.typing.get_sub_types`
* `pydantic.typing.is_callable_type`
* `pydantic.typing.is_classvar`
* `pydantic.typing.is_finalvar`
* `pydantic.typing.is_literal_type`
* `pydantic.typing.is_namedtuple`
* `pydantic.typing.is_new_type`
* `pydantic.typing.is_none_type`
* `pydantic.typing.is_typeddict`
* `pydantic.typing.is_typeddict_special`
* `pydantic.typing.is_union`
* `pydantic.typing.new_type_supertype`
* `pydantic.typing.resolve_annotations`
* `pydantic.typing.typing_base`
* `pydantic.typing.update_field_forward_refs`
* `pydantic.typing.update_model_forward_refs`
* `pydantic.utils.ClassAttribute`
* `pydantic.utils.DUNDER_ATTRIBUTES`
* `pydantic.utils.PyObjectStr`
* `pydantic.utils.ValueItems`
* `pydantic.utils.almost_equal_floats`
* `pydantic.utils.get_discriminator_alias_and_values`
* `pydantic.utils.get_model`
* `pydantic.utils.get_unique_discriminator_alias`
* `pydantic.utils.in_ipython`
* `pydantic.utils.is_valid_identifier`
* `pydantic.utils.path_type`
* `pydantic.utils.validate_field_name`
* `pydantic.validate_model`
````

## File: docs/pydantic_people.md
````markdown
# Pydantic People

Pydantic has an amazing community of contributors, reviewers, and experts that help propel the project forward.
Here, we celebrate those people and their contributions.

## Maintainers

These are the current maintainers of the Pydantic repository. Feel free to tag us if you have questions, review requests, or feature requests for which you'd like feedback!

{{ maintainers }}

## Experts

These are the users that have helped others the most with questions in GitHub through *all time*.

{{ experts }}

### Most active users last month

These are the users that have helped others the most with questions in GitHub during the last month.

{{ most_active_users }}

## Top contributors

These are the users that have created the most pull requests that have been *merged*.

{{ top_contributors }}

## Top Reviewers

These are the users that have reviewed the most Pull Requests from others, assisting with code quality, documentation, bug fixes, feature requests, etc.

{{ top_reviewers }}

## About the data

The data displayed above is calculated monthly via the Github GraphQL API.

The source code for this script is located [here](https://github.com/pydantic/pydantic/tree/main/.github/actions/people/people.py).
Many thanks to [Sebastián Ramírez](https://github.com/tiangolo) for the script from which we based this logic.

Depending on changing conditions, the thresholds for the different categories of contributors may change in the future.
````

## File: docs/version-policy.md
````markdown
First of all, we recognize that the transitions from Pydantic V1 to V2 has been and will be painful for some users.
We're sorry about this pain :pray:, it was an unfortunate but necessary step to correct design mistakes of V1.

**There will not be another breaking change of this magnitude!**

## Pydantic V1

Active development of V1 has already stopped, however critical bug fixes and security vulnerabilities will be fixed in V1 until
the release of Pydantic V3.

## Pydantic V2

We will not intentionally make breaking changes in minor releases of V2.

Functionality marked as deprecated will not be removed until the next major V3 release.

Of course, some apparently safe changes and bug fixes will inevitably break some users' code &mdash; obligatory link to [xkcd](https://xkcd.com/1172/).

The following changes will **NOT** be considered breaking changes, and may occur in minor releases:

* Bug fixes that may result in existing code breaking, provided that such code was relying on undocumented features/constructs.
* Changing the format of JSON Schema [references](https://json-schema.org/understanding-json-schema/structuring#dollarref).
* Changing the `msg`, `ctx`, and `loc` fields of [`ValidationError`][pydantic_core.ValidationError] exceptions. `type` will not change &mdash; if you're programmatically parsing error messages, you should use `type`.
* Adding new keys to [`ValidationError`][pydantic_core.ValidationError] exceptions &mdash; e.g. we intend to add `line_number` and `column_number` to errors when validating JSON once we migrate to a new JSON parser.
* Adding new [`ValidationError`][pydantic_core.ValidationError] errors.
* Changing how `__repr__` behaves, even of public classes.

In all cases we will aim to minimize churn and do so only when justified by the increase of quality of Pydantic for users.

## Pydantic V3 and beyond

We expect to make new major releases roughly once a year going forward, although as mentioned above, any associated breaking changes should be trivial to fix compared to the V1-to-V2 transition.

## Experimental Features

At Pydantic, we like to move quickly and innovate! To that end, we may introduce experimental features in minor releases.

!!! abstract "Usage Documentation"
    To learn more about our current experimental features, see the [experimental features documentation](./concepts/experimental.md).

Please keep in mind, experimental features are active works in progress. If these features are successful, they'll eventually become part of Pydantic. If unsuccessful, said features will be removed with little notice. While in its experimental phase, a feature's API and behaviors may not be stable, and it's very possible that changes made to the feature will not be backward-compatible.

### Naming Conventions

We use one of the following naming conventions to indicate that a feature is experimental:

1. The feature is located in the [`experimental`](api/experimental.md) module. In this case, you can access the feature like this:

    ```python {test="skip" lint="skip"}
    from pydantic.experimental import feature_name
    ```

2. The feature is located in the main module, but prefixed with `experimental_`. This case occurs when we add a new field, argument, or method to an existing data structure already within the main `pydantic` module.

New features with these naming conventions are subject to change or removal, and we are looking for feedback and suggestions before making them a permanent part of Pydantic. See the [feedback section](./concepts/experimental.md#feedback) for more information.

### Importing Experimental Features

When you import an experimental feature from the [`experimental`](api/experimental.md) module, you'll see a warning message that the feature is experimental. You can disable this warning with the following:

```python
import warnings

from pydantic import PydanticExperimentalWarning

warnings.filterwarnings('ignore', category=PydanticExperimentalWarning)
```

### Lifecycle of Experimental Features

1. A new feature is added, either in the [`experimental`](api/experimental.md) module or with the `experimental_` prefix.
2. The behavior is often modified during patch/minor releases, with potential API/behavior changes.
3. If the feature is successful, we promote it to Pydantic with the following steps:

    a. If it was in the [`experimental`](api/experimental.md) module, the feature is cloned to Pydantic's main module. The original experimental feature still remains in the [`experimental`](api/experimental.md) module, but it will show a warning when used. If the feature was already in the main Pydantic module, we create a copy of the feature without the `experimental_` prefix, so the feature exists with both the official and experimental names. A deprecation warning is attached to the experimental version.

    b. At some point, the code of the experimental feature is removed, but there will still be a stub of the feature that provides an error message with appropriate instructions.

    c. As a last step, the experimental version of the feature is entirely removed from the codebase.

If the feature is unsuccessful or unpopular, it's removed with little notice. A stub will remain in the location of the deprecated feature with an error message.

Thanks to [streamlit](https://docs.streamlit.io/develop/quick-reference/prerelease) for the inspiration for the lifecycle and naming conventions of our new experimental feature patterns.

## Support for Python versions

Pydantic will drop support for a Python version when the following conditions are met:

* The Python version has reached its [expected end of life](https://devguide.python.org/versions/).
* less than 5% of downloads of the most recent minor release are using that version.
````

## File: docs/why.md
````markdown
# Why use Pydantic Validation?

Today, Pydantic is downloaded <span id="download-count">many</span> times a month and used by some of the largest and most recognisable organisations in the world.

It's hard to know why so many people have adopted Pydantic since its inception six years ago, but here are a few guesses.

## Type hints powering schema validation {#type-hints}

The schema that Pydantic validates against is generally defined by Python [type hints](https://docs.python.org/3/glossary.html#term-type-hint).

Type hints are great for this since, if you're writing modern Python, you already know how to use them.
Using type hints also means that Pydantic integrates well with static typing tools
(like [mypy](https://www.mypy-lang.org/) and [Pyright](https://github.com/microsoft/pyright/))
and IDEs (like [PyCharm](https://www.jetbrains.com/pycharm/) and [VSCode](https://code.visualstudio.com/)).

???+ example "Example - just type hints"
    ```python
    from typing import Annotated, Literal

    from annotated_types import Gt

    from pydantic import BaseModel


    class Fruit(BaseModel):
        name: str  # (1)!
        color: Literal['red', 'green']  # (2)!
        weight: Annotated[float, Gt(0)]  # (3)!
        bazam: dict[str, list[tuple[int, bool, float]]]  # (4)!


    print(
        Fruit(
            name='Apple',
            color='red',
            weight=4.2,
            bazam={'foobar': [(1, True, 0.1)]},
        )
    )
    #> name='Apple' color='red' weight=4.2 bazam={'foobar': [(1, True, 0.1)]}
    ```

    1. The `name` field is simply annotated with `str` &mdash; any string is allowed.
    2. The [`Literal`][typing.Literal] type is used to enforce that `color` is either `'red'` or `'green'`.
    3. Even when we want to apply constraints not encapsulated in Python types, we can use [`Annotated`][typing.Annotated]
       and [`annotated-types`](https://github.com/annotated-types/annotated-types) to enforce constraints while still keeping typing support.
    4. I'm not claiming "bazam" is really an attribute of fruit, but rather to show that arbitrarily complex types can easily be validated.

!!! tip "Learn more"
    See the [documentation on supported types](concepts/types.md).

## Performance

Pydantic's core validation logic is implemented in a separate package ([`pydantic-core`](https://github.com/pydantic/pydantic-core)),
where validation for most types is implemented in Rust.

As a result, Pydantic is among the fastest data validation libraries for Python.

??? example "Performance Example - Pydantic vs. dedicated code"
    In general, dedicated code should be much faster than a general-purpose validator, but in this example
    Pydantic is >300% faster than dedicated code when parsing JSON and validating URLs.

    ```python {title="Performance Example" test="skip"}
    import json
    import timeit
    from urllib.parse import urlparse

    import requests

    from pydantic import HttpUrl, TypeAdapter

    reps = 7
    number = 100
    r = requests.get('https://api.github.com/emojis')
    r.raise_for_status()
    emojis_json = r.content


    def emojis_pure_python(raw_data):
        data = json.loads(raw_data)
        output = {}
        for key, value in data.items():
            assert isinstance(key, str)
            url = urlparse(value)
            assert url.scheme in ('https', 'http')
            output[key] = url


    emojis_pure_python_times = timeit.repeat(
        'emojis_pure_python(emojis_json)',
        globals={
            'emojis_pure_python': emojis_pure_python,
            'emojis_json': emojis_json,
        },
        repeat=reps,
        number=number,
    )
    print(f'pure python: {min(emojis_pure_python_times) / number * 1000:0.2f}ms')
    #> pure python: 5.32ms

    type_adapter = TypeAdapter(dict[str, HttpUrl])
    emojis_pydantic_times = timeit.repeat(
        'type_adapter.validate_json(emojis_json)',
        globals={
            'type_adapter': type_adapter,
            'HttpUrl': HttpUrl,
            'emojis_json': emojis_json,
        },
        repeat=reps,
        number=number,
    )
    print(f'pydantic: {min(emojis_pydantic_times) / number * 1000:0.2f}ms')
    #> pydantic: 1.54ms

    print(
        f'Pydantic {min(emojis_pure_python_times) / min(emojis_pydantic_times):0.2f}x faster'
    )
    #> Pydantic 3.45x faster
    ```

Unlike other performance-centric libraries written in compiled languages, Pydantic also has excellent support for customizing validation via [functional validators](#customisation).

!!! tip "Learn more"
    Samuel Colvin's [talk at PyCon 2023](https://youtu.be/pWZw7hYoRVU) explains how [`pydantic-core`](https://github.com/pydantic/pydantic-core)
    works and how it integrates with Pydantic.

## Serialization

Pydantic provides functionality to serialize model in three ways:

1. To a Python `dict` made up of the associated Python objects.
2. To a Python `dict` made up only of "jsonable" types.
3. To a JSON string.

In all three modes, the output can be customized by excluding specific fields, excluding unset fields, excluding default values, and excluding `None` values.

??? example "Example - Serialization 3 ways"

    ```python
    from datetime import datetime

    from pydantic import BaseModel


    class Meeting(BaseModel):
        when: datetime
        where: bytes
        why: str = 'No idea'


    m = Meeting(when='2020-01-01T12:00', where='home')
    print(m.model_dump(exclude_unset=True))
    #> {'when': datetime.datetime(2020, 1, 1, 12, 0), 'where': b'home'}
    print(m.model_dump(exclude={'where'}, mode='json'))
    #> {'when': '2020-01-01T12:00:00', 'why': 'No idea'}
    print(m.model_dump_json(exclude_defaults=True))
    #> {"when":"2020-01-01T12:00:00","where":"home"}
    ```

!!! tip "Learn more"
    See the [documentation on serialization](concepts/serialization.md).

## JSON Schema

A [JSON Schema](https://json-schema.org/) can be generated for any Pydantic schema &mdash; allowing self-documenting APIs and integration with a wide variety of tools which support the JSON Schema format.

??? example "Example - JSON Schema"

    ```python
    from datetime import datetime

    from pydantic import BaseModel


    class Address(BaseModel):
        street: str
        city: str
        zipcode: str


    class Meeting(BaseModel):
        when: datetime
        where: Address
        why: str = 'No idea'


    print(Meeting.model_json_schema())
    """
    {
        '$defs': {
            'Address': {
                'properties': {
                    'street': {'title': 'Street', 'type': 'string'},
                    'city': {'title': 'City', 'type': 'string'},
                    'zipcode': {'title': 'Zipcode', 'type': 'string'},
                },
                'required': ['street', 'city', 'zipcode'],
                'title': 'Address',
                'type': 'object',
            }
        },
        'properties': {
            'when': {'format': 'date-time', 'title': 'When', 'type': 'string'},
            'where': {'$ref': '#/$defs/Address'},
            'why': {'default': 'No idea', 'title': 'Why', 'type': 'string'},
        },
        'required': ['when', 'where'],
        'title': 'Meeting',
        'type': 'object',
    }
    """
    ```

Pydantic is compliant with the latest version of JSON Schema specification
([2020-12](https://json-schema.org/draft/2020-12/release-notes.html)), which
is compatible with [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0.html).

!!! tip "Learn more"
    See the [documentation on JSON Schema](concepts/json_schema.md).

## Strict mode and data coercion {#strict-lax}

By default, Pydantic is tolerant to common incorrect types and coerces data to the right type &mdash;
e.g. a numeric string passed to an `int` field will be parsed as an `int`.

Pydantic also has as [strict mode](concepts/strict_mode.md), where types are not coerced and a
validation error is raised unless the input data exactly matches the expected schema.

But strict mode would be pretty useless when validating JSON data since JSON doesn't have types matching
many common Python types like [`datetime`][datetime.datetime], [`UUID`][uuid.UUID] or [`bytes`][].

To solve this, Pydantic can parse and validate JSON in one step. This allows sensible data conversion
(e.g. when parsing strings into [`datetime`][datetime.datetime] objects). Since the JSON parsing is
implemented in Rust, it's also very performant.

??? example "Example - Strict mode that's actually useful"

    ```python
    from datetime import datetime

    from pydantic import BaseModel, ValidationError


    class Meeting(BaseModel):
        when: datetime
        where: bytes


    m = Meeting.model_validate({'when': '2020-01-01T12:00', 'where': 'home'})
    print(m)
    #> when=datetime.datetime(2020, 1, 1, 12, 0) where=b'home'
    try:
        m = Meeting.model_validate(
            {'when': '2020-01-01T12:00', 'where': 'home'}, strict=True
        )
    except ValidationError as e:
        print(e)
        """
        2 validation errors for Meeting
        when
          Input should be a valid datetime [type=datetime_type, input_value='2020-01-01T12:00', input_type=str]
        where
          Input should be a valid bytes [type=bytes_type, input_value='home', input_type=str]
        """

    m_json = Meeting.model_validate_json(
        '{"when": "2020-01-01T12:00", "where": "home"}'
    )
    print(m_json)
    #> when=datetime.datetime(2020, 1, 1, 12, 0) where=b'home'
    ```

!!! tip "Learn more"
    See the [documentation on strict mode](concepts/strict_mode.md).

## Dataclasses, TypedDicts, and more {#dataclasses-typeddict-more}

Pydantic provides four ways to create schemas and perform validation and serialization:

1. [`BaseModel`](concepts/models.md) &mdash; Pydantic's own super class with many common utilities available via instance methods.
2. [Pydantic dataclasses](concepts/dataclasses.md) &mdash; a wrapper around standard dataclasses with additional validation performed.
3. [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] &mdash; a general way to adapt any type for validation and serialization.
   This allows types like [`TypedDict`](api/standard_library_types.md#typeddict) and [`NamedTuple`](api/standard_library_types.md#typingnamedtuple)
   to be validated as well as simple types (like [`int`][] or [`timedelta`][datetime.timedelta]) &mdash; [all types](concepts/types.md) supported
   can be used with [`TypeAdapter`][pydantic.type_adapter.TypeAdapter].
4. [`validate_call`](concepts/validation_decorator.md) &mdash; a decorator to perform validation when calling a function.

??? example "Example - schema based on a [`TypedDict`][typing.TypedDict]"

    ```python
    from datetime import datetime

    from typing_extensions import NotRequired, TypedDict

    from pydantic import TypeAdapter


    class Meeting(TypedDict):
        when: datetime
        where: bytes
        why: NotRequired[str]


    meeting_adapter = TypeAdapter(Meeting)
    m = meeting_adapter.validate_python(  # (1)!
        {'when': '2020-01-01T12:00', 'where': 'home'}
    )
    print(m)
    #> {'when': datetime.datetime(2020, 1, 1, 12, 0), 'where': b'home'}
    meeting_adapter.dump_python(m, exclude={'where'})  # (2)!

    print(meeting_adapter.json_schema())  # (3)!
    """
    {
        'properties': {
            'when': {'format': 'date-time', 'title': 'When', 'type': 'string'},
            'where': {'format': 'binary', 'title': 'Where', 'type': 'string'},
            'why': {'title': 'Why', 'type': 'string'},
        },
        'required': ['when', 'where'],
        'title': 'Meeting',
        'type': 'object',
    }
    """
    ```

    1. [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] for a [`TypedDict`][typing.TypedDict] performing validation,
       it can also validate JSON data directly with [`validate_json`][pydantic.type_adapter.TypeAdapter.validate_json].
    2. [`dump_python`][pydantic.type_adapter.TypeAdapter.dump_python] to serialise a [`TypedDict`][typing.TypedDict]
       to a python object, it can also serialise to JSON with [`dump_json`][pydantic.type_adapter.TypeAdapter.dump_json].
    3. [`TypeAdapter`][pydantic.type_adapter.TypeAdapter] can also generate a JSON Schema.

## Customisation

Functional validators and serializers, as well as a powerful protocol for custom types, means the way Pydantic operates can be customized on a per-field or per-type basis.

??? example "Customisation Example - wrap validators"
    "wrap validators" are new in Pydantic V2 and are one of the most powerful ways to customize validation.

    ```python
    from datetime import datetime, timezone
    from typing import Any

    from pydantic_core.core_schema import ValidatorFunctionWrapHandler

    from pydantic import BaseModel, field_validator


    class Meeting(BaseModel):
        when: datetime

        @field_validator('when', mode='wrap')
        def when_now(
            cls, input_value: Any, handler: ValidatorFunctionWrapHandler
        ) -> datetime:
            if input_value == 'now':
                return datetime.now()
            when = handler(input_value)
            # in this specific application we know tz naive datetimes are in UTC
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return when


    print(Meeting(when='2020-01-01T12:00+01:00'))
    #> when=datetime.datetime(2020, 1, 1, 12, 0, tzinfo=TzInfo(3600))
    print(Meeting(when='now'))
    #> when=datetime.datetime(2032, 1, 2, 3, 4, 5, 6)
    print(Meeting(when='2020-01-01T12:00'))
    #> when=datetime.datetime(2020, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
    ```

!!! tip "Learn more"
    See the documentation on [validators](concepts/validators.md), [custom serializers](concepts/serialization.md#serializers),
    and [custom types](concepts/types.md#custom-types).

## Ecosystem

At the time of writing there are 466,400 repositories on GitHub and 8,119 packages on PyPI that depend on Pydantic.

Some notable libraries that depend on Pydantic:

{{ libraries }}

More libraries using Pydantic can be found at [`Kludex/awesome-pydantic`](https://github.com/Kludex/awesome-pydantic).

## Organisations using Pydantic {#using-pydantic}

Some notable companies and organisations using Pydantic together with comments on why/how we know they're using Pydantic.

The organisations below are included because they match one or more of the following criteria:

* Using Pydantic as a dependency in a public repository.
* Referring traffic to the Pydantic documentation site from an organization-internal domain &mdash; specific referrers are not included since they're generally not in the public domain.
* Direct communication between the Pydantic team and engineers employed by the organization about usage of Pydantic within the organization.

We've included some extra detail where appropriate and already in the public domain.

{{ organisations }}
````
