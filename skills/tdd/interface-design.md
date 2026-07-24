# Interface Design for Testability

Testability is one design signal, not the sole measure of good design. Make important dependencies and effects explicit at meaningful boundaries - without contorting the design just to make unit tests trivial.

## Explicit dependencies at boundaries

Accept the dependencies that cross a real boundary instead of constructing them inside:

```typescript
// Testable
function processOrder(order, paymentGateway) {}

// Hard to test
function processOrder(order) {
  const gateway = new StripeGateway();
}
```

But don't let dependency injection become the goal:

- Use explicit dependencies at meaningful boundaries, not everywhere.
- Don't thread every dependency through every function just to simplify unit tests.
- Don't expose private implementation structure through production interfaces.
- Don't add a DI framework unless the application already benefits from one.
- Don't replace cohesive object behavior with a bag of callbacks just because callbacks are easy to mock.
- Don't create an interface for a dependency that has one stable implementation unless the boundary or a real testing need justifies it.
- Prefer constructors, module composition, or boundary-level factories over threading dependencies through deep call chains.

**The "giant context object" anti-pattern.** A function with one parameter isn't automatically simple if that parameter is an enormous context object hiding twenty dependencies. The goal isn't fewer parameters; it's a small, meaningful, comprehensible interface.

## Separate decisions from effects - when it helps

Separate the decision from the effect when doing so makes important logic easier to understand and verify. Concentrate unavoidable effects behind explicit boundaries.

- Pure decision logic pays off for calculations, policies, validation, and state-transition decisions.
- Side effects are appropriate when they are the point of the operation: a payment command charges, a repository persists, a publisher publishes, a deployment command deploys.
- Don't wrap every simple mutation in pure-function-plus-executor ceremony.
- Make effects explicit, observable, idempotent where necessary, and concentrated at stable boundaries.
- Split the decision out to test it separately only when it's complex enough to justify the split.

```typescript
// Worth it when refund eligibility is genuinely complex:
const decision = decideRefund(order);
await refundExecutor.execute(decision);
```

Don't turn that into mandatory ceremony for every state change.

## Small surface area

A smaller, coherent interface usually needs less test setup - but only when the reduction reflects a genuine abstraction, not parameters swept into an options bag or a context object. Shrinking the parameter count is not the goal; a small, meaningful, comprehensible interface is. See [deep-modules.md](deep-modules.md).
