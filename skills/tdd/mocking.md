# When to Mock

Default: test against the real implementation. Mock or fake a boundary when the real thing would make a focused test slow, nondeterministic, destructive, costly, unsafe, rate-limited, or operationally impractical.

**Keep these defaults** - they keep tests behavior-oriented and refactor-proof:

- Don't mock private methods.
- Don't mock internal call chains just to verify orchestration.
- Don't assert internal call counts or order unless the ordering is itself part of a public contract.
- Prefer tests that survive refactoring.

## Boundaries worth mocking or faking

- Payment providers
- Email or SMS delivery
- Cloud APIs and external identity providers
- Time and randomness
- Destructive filesystem operations
- Slow queues
- Expensive model APIs
- Hardware and third-party services
- Services that are technically internal but operationally independent

## Prefer real, controlled dependencies when practical

A real dependency you control usually beats a mock:

- Disposable test databases
- In-memory or ephemeral queues
- Local emulators
- Temporary directories
- Fake clocks
- Deterministic random sources
- Containerized dependencies

**Use the highest-fidelity dependency that gives meaningful confidence without making the test unacceptably slow, fragile, dangerous, or expensive.**

## Making boundaries substitutable

At a real boundary, pass the dependency in rather than constructing it inside, so a test can supply a controlled substitute. This is the injection rule from [interface-design.md](interface-design.md) - use it for meaningful boundaries, not every function.

**Prefer SDK-style interfaces over generic fetchers.** Specific functions per operation are easier to substitute than one generic function with conditional logic:

```typescript
// GOOD: each function substitutes to one specific shape
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: substituting requires conditional logic inside the fake
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

The SDK approach means each substitute returns one specific shape, no conditional logic in test setup, type safety per endpoint, and it's easy to see which endpoints a test exercises.
