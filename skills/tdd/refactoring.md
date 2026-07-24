# Refactor Candidates

After returning to GREEN, refactor on evidence, not by reflex. Don't apply named code-smell transformations automatically - each has a real cost.

## Duplication

- Tolerate small local duplication when the copies may evolve differently.
- Extract when the repeated code is the same _stable_ concept and changing it in one place but not the other would be a bug.
- A weak or premature abstraction costs more than duplicated code. Prefer duplication over the wrong abstraction.

## Long methods

- Split when the extracted pieces represent meaningful concepts or independent responsibilities.
- Don't create private helpers solely to reduce line count - a linear method is often easier to follow than logic fragmented across many tiny helpers.
- Extract when naming a concept improves comprehension, reuse, testing, or isolation of change.

## Private helpers

Keep tests on public behavior regardless of how the internals are split. Don't extract private methods just to make code look modular.

## Feature envy

"Move logic to where the data lives" is a heuristic, not a law. Before moving, ask:

- Is this logic really that object's responsibility?
- Would moving it bloat the entity?
- Would a domain service, policy object, or use-case module be more coherent?
- Would the object need unrelated dependencies after the move?

## Primitive obsession

Don't introduce a value object merely because a primitive appears more than once. Introduce one when it earns its keep - enforcing validation, preserving units, preventing invalid states, encoding domain operations, making incompatible values unmixable, or centralizing parsing/normalization. Avoid wrapper types that add ceremony without semantics.

## Shallow modules

Combine or deepen them. See [deep-modules.md](deep-modules.md).

## Existing code the new work reveals as problematic

When new work exposes a broader problem, record it separately - unless fixing it is necessary for correctness, materially reduces the current implementation's risk, or is small enough to address without obscuring the active change. Don't automatically expand scope.
