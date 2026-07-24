# Good and Bad Tests

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```typescript
// GOOD: Tests observable behavior
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

Characteristics:

- Tests behavior users/callers care about
- Uses the public interface for its scope
- Survives internal refactors
- Describes WHAT, not HOW
- Verifies one coherent behavior

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```typescript
// BAD: Tests implementation details
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on internal call counts/order that aren't part of a public contract
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT

## One Logical Assertion, Not One Matcher

"One assertion per test" means one coherent behavior with one principal reason to fail - **not** literally one `expect`. Multiple assertions are appropriate when they jointly establish one observable outcome.

```typescript
// GOOD: three assertions, one behavior - "successful checkout completes atomically"
test("successful checkout completes atomically", async () => {
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");          // checkout confirmed
  expect((await getOrder(result.orderId)).paid).toBe(true); // order marked paid
  expect(await countPayments(result.orderId)).toBe(1);      // exactly one payment record
});
```

Don't mechanically split every matcher into its own test. Do split when a test tries to verify unrelated behaviors - e.g. one test that asserts checkout succeeds _and_ an email is sent _and_ taxes are calculated _and_ retries fire _and_ admin reporting updates. That's five behaviors with five reasons to fail; give each its own test.

## What "Public Interface" Means

The public interface is the intended contract for the test's scope, not always the end-user UI:

- **Package** → the exported API
- **Service** → HTTP, RPC, messages, or commands
- **CLI** → exit status, output, filesystem effects
- **Migration** → the resulting schema and data
- **Database module** → persisted state and transaction semantics
- **Internal subsystem** → a stable module boundary, even if end users never call it directly

**Test through the narrowest stable interface that fully expresses the behavior being protected.** Don't route every test through the whole UI when a narrower stable boundary gives better isolation and equally meaningful confidence.

## Verifying Durable State

Prefer verifying application behavior through the public interface. Inspect a database, filesystem, queue, event stream, or cache directly when that system's state is _itself_ the contract under test.

```typescript
// BAD: bypasses the interface to assert an incidental detail
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD: verifies the behavior through the interface
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  expect((await getUser(user.id)).name).toBe("Alice");
});

// ALSO GOOD: the durable side effect IS the contract
test("createUser writes an audit record", async () => {
  await createUser({ name: "Alice" });
  const [latest] = await db.query("SELECT type FROM audit_log ORDER BY id DESC LIMIT 1");
  expect(latest.type).toBe("user.created");
});
```

Direct inspection is the right tool when the behavior lives at the boundary: migrations; unique, foreign-key, and check constraints; transactional rollback; isolation and concurrency; exact persistence formats; outbox events; audit records; queue publication; idempotency records; files on disk; cache invalidation; schema compatibility; and index or query-plan requirements when performance is part of the contract.

The line:

- **Bad** - bypassing the public interface solely to assert an incidental implementation detail.
- **Good** - inspecting a boundary because the durable state or side effect there _is_ the required behavior.

## Test Volume (AI-specific)

You can generate a huge test matrix in seconds. Don't do it by default.

- Start with the highest-value representative cases.
- Add a case only when it exposes a distinct behavior, boundary, invariant, or known failure mode.
- Don't write a separate test per trivial permutation unless the domain demands exhaustive coverage.
- Prefer table-driven tests when many examples exercise one coherent rule.
- Reach for property-based tests when broad input coverage protects a meaningful invariant.
- Use snapshot tests carefully and review them semantically. Don't accept a large snapshot just because it's easy to update.
- Coverage percentage is a diagnostic, not the goal. Don't write tests solely to raise it.
