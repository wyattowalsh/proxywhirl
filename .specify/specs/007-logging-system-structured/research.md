# Research: Structured Logging with Loguru

**Feature**: 007-logging-system-structured
**Date**: 2025-11-01

## Question

For implementing structured JSON logging with Loguru, should we use an external library like `python-json-logger` or implement the formatting manually using Loguru's built-in features?

## Findings

Based on a review of Loguru's documentation and best practices, Loguru provides robust native support for structured JSON logging.

1.  **Built-in Serialization**: Loguru's `add()` sink function has a `serialize=True` parameter that automatically converts log records into a comprehensive JSON format. This is the simplest method and provides a rich default set of fields (`time`, `level`, `message`, `record`, `extra`, etc.).

2.  **Custom Serialization**: For more fine-grained control over the JSON schema, Loguru allows providing a custom serialization function. This function receives the log record and can return a dictionary with a specific structure, which Loguru then serializes to JSON. This is ideal for standardizing log formats and integrating with specific log aggregation platforms.

3.  **Contextual Data**: Loguru's `bind()` method allows attaching arbitrary contextual data to log records, which is automatically included in the `extra` field of the serialized JSON. This is a powerful feature for adding request IDs, user IDs, and other metadata.

4.  **No Direct Comparison Found**: The research did not yield a direct comparison showing a significant advantage of using `python-json-logger` *with* Loguru. Loguru's native capabilities appear to cover the primary use cases for structured logging.

## Decision

**Decision**: We will **not** add `python-json-logger` as a dependency. We will implement structured JSON formatting using Loguru's built-in `serialize=True` feature, in combination with a custom serialization function to define a standardized JSON schema.

**Rationale**:

*   **Avoids a New Dependency**: This approach avoids adding an unnecessary dependency to the project, keeping the dependency footprint smaller.
*   **Leverages Existing Library**: It makes full use of the features already provided by `loguru`, which is an existing dependency.
*   **Sufficiently Powerful**: Loguru's native serialization is flexible enough to meet all the feature requirements, including custom schemas and contextual metadata.
*   **Simplicity**: Using the built-in features is more straightforward than integrating and managing another library.

## Alternatives Considered

*   **Using `python-json-logger`**: This would have involved creating a custom Loguru handler that uses `python-json-logger` for formatting. This was deemed an unnecessary layer of complexity.
*   **Manual JSON Formatting in `format`**: Manually constructing a JSON string in the `format` parameter of the sink is error-prone and less flexible than using the `serialize` feature.