
## What is DesignKit?

DesignKit is a modern Python architecture toolkit that draws inspiration from the 23 Gang of Four design patterns with original architectural abstractions, expressive APIs, and efficient utilities to build cleaner, more maintainable software.

Every API is carefully designed with developer experience in mind, featuring first-class support for async/await, metaprogramming, extensibility hooks, multiple programming paradigms, operator overloading where appropriate, and other modern Python capabilities.

> [!IMPORTANT]
> DesignKit does **not** aim to provide literal implementations of the Gang of Four patterns. Instead, it offers expressive APIs inspired by those ideas, redesigned to solve real-world Python architecture problems while embracing modern language features.

***Write software that's easier to understand, extend, and maintain!***

## What DesignKit Is Not?

DesignKit is **not**:

- an application framework.
- an inversion-of-control container.
- an ORM.
- a web framework.
- a dependency injection framework.
- a replacement for your existing architecture.

Basically, there is no such thing as a design pattern for creating a payment agent.
**Instead**, it is a toolkit of architectural APIs that you can adopt independently, wherever they make sense.

## How to Use DesignKit?

To start using DesignKit, you first need to install it.

```bash
# via pip
pip install designkit

# via uv
uv install designkit

# via poetry
poetry add designkit
```

So, you can import the DesignKit library in your Python code with the following statement:

```python
from designkit.<section>.<pattern> import <utilities>, <exceptions>, <abstractions>

# Example:
from designkit.behavioral.state import (
    StateMachine, # implementation
    Reactive, # utility
    GuardRejectedError, InvalidTransitionError # exceptions
)
```

Where `<section>` is the section of the design pattern (e.g., `behavioral`, `creational`, `structural`), `<pattern>` is the name of the design pattern (e.g., `matcher`, `factory`, `adapter`), and `<utilities>`, `<exceptions>`, and `<abstractions>` are the specific utilities, exceptions, and abstractions you want to use from that pattern.

> [!IMPORTANT]
> To see most examples of usage, you can check [`samples/`](samples/) directory on [GitHub][platform-github] with at least one example for each design pattern.

## Features
DesignKit features all **23** Gang of Four ([GoF][authors-gof]) design patterns, plus **6** original design patterns.

#### Design Patterns

- Behavioral
    1. `Chain of Responsibility`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Passes a request along a chain of handlers. Upon receiving a request, each handler decides either to process the request or to pass it to the next handler in the chain.
        - **Example:** ...
    2. `Command`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Encapsulates a request as an object, thereby allowing for parameterization of clients with queues, requests, and operations.
        - **Example:** ...
    3. `Interpreter`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Given a language, defines a representation for its grammar along with an interpreter that uses the representation to interpret sentences in the language.
        - **Example:** ...
    4. `Iterator`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Provides a way to access the elements of an aggregate object sequentially without exposing its underlying representation.
        - **Example:** ...
    5. `Mediator`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Defines an object that encapsulates how a set of objects interact. Mediator promotes loose coupling by keeping objects from referring to each other explicitly, and it lets you vary their interaction independently.
        - **Example:** ...
    6. `Memento`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Without violating encapsulation, captures and externalizes an object's internal state so that the object can be restored to this state later.
        - **Example:** ...
    7. `Observer`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.
        - **Example:** ...
    8. `State`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Allows an object to alter its behavior when its internal state changes. The object will appear to change its class.
        - **Example:** ...
    9. `Strategy`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Defines a family of algorithms, encapsulates each one, and makes them interchangeable. Strategy lets the algorithm vary independently from clients that use it.
        - **Example:** ...
    10. `Policy`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Defines a family of algorithms, encapsulates each one, and makes them interchangeable. Policy lets the algorithm vary independently from clients that use it.
        - **Example:** ...
    11. `Template Method`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Defines the skeleton of an algorithm in a method, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure.
        - **Example:** ...
    12. `Visitor`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Represents an operation to be performed on the elements of an object structure. Visitor lets you define a new operation without changing the classes of the elements on which it operates.
        - **Example:** ...

- Creational
    1. `Abstract Factory`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Provides an interface for creating families of related or dependent objects without specifying their concrete classes.
        - **Example:** ...
    2. `Builder`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Separates the construction of a complex object from its representation, allowing the same construction process to create different representations.
        - **Example:** ...
    3. `Factory Method`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Defines an interface for creating an object, but lets subclasses alter the type of objects that will be created.
        - **Example:** ...
    4. `Prototype`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Specifies the kinds of objects to create using a prototypical instance, and create new objects by copying this prototype.
        - **Example:** ...
    5. `Singleton` -- Only one instance.
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Ensures a class has only one instance and provides a global point of access to it.
        - **Example:** ...
- Structural
    1. `Adapter`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Converts the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.
        - **Example:** ...
    2. `Bridge`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Decouples an abstraction from its implementation so that the two can vary independently.
        - **Example:** ...
    3. `Composite`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Composes objects into tree structures to represent part-whole hierarchies. Composite lets clients treat individual objects and compositions of objects uniformly.
        - **Example:** ...
    4. `Decorator`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Attaches additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.
        - **Example:** ...
    5. `Facade`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Provides a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use.
        - **Example:** ...
    6. `Flyweight`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Uses sharing to support large numbers of fine-grained objects efficiently.
        - **Example:** ...
    7. `Proxy`
        - **Author:** [GoF][authors-gof], [Sheñey][authors-sheniey]
        - **Description:** Provides a surrogate or placeholder for another object to control access to it.
        - **Example:** ...

## Tech Stack

| | Technology | Purpose |
|---|---|---|
| 🎨 | [Rich][tech-rich] | Rich text and beautiful formatting in the terminal |
| 🔤 | [DesignKit Utils][tech-designkit-utils] | Utility functions and helpers for DesignKit |

## Getting Started

```bash
# clone the repository
git clone https://github.com/Sheniey/designkit.git
cd designkit

# install dependencies
pip install -r requirements.txt # via pip
uv install -r requirements.txt  # via uv
```

## Commands

| Command | Action |
|---|---|
| `maturin develop` | Start development build of Crates |
| `maturin build` | Build production release of Crates to `./target/` |
| `maturin publish` | Publish entire project to PyPI -- future deprecation |
| `pytest` | Run all tests in the project -- requires `pytest` to be installed |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

Licensed under the [MIT License](LICENSE) &copy; 2026 [Sheñey][platform-sheniey-portfolio].


<!-- Platform Links -->
[platform-pypi]: https://pypi.org/project/designkit/
[platform-uv]: https://uv.run/pypi/designkit
[platform-poetry]: https://python-poetry.org/docs/cli/#add
[platform-github]: https://github.com/Sheniey/designkit
[platform-sheniey-portfolio]: https://sheney.dev

<!-- Author Links -->
[authors-gof]: https://en.wikipedia.org/wiki/Design_Patterns
[authors-sheniey]: https://github.com/Sheniey

<!-- Sample Links -->
[samples-chain-of-responsibility]: samples/behavioral/chain_of_responsibility/test.py
[samples-command]: samples/behavioral/command/test.py

<!-- Tech Links -->
[tech-rich]: https://rich.readthedocs.io/
[tech-designkit-utils]: https://pypi.org/project/designkit-utils/
