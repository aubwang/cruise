# Deep Modules

From "A Philosophy of Software Design":

**Deep module** = small interface + substantial useful complexity hidden behind it.

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple params
├─────────────────────┤
│                     │
│  Deep Implementation│  ← Complex logic hidden
│                     │
└─────────────────────┘
```

**Shallow module** = large interface + little implementation (avoid).

```
┌─────────────────────────────────┐
│       Large Interface           │  ← Many methods, complex params
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through
└─────────────────────────────────┘
```

A deep module must still represent **one coherent concept**. A one-method module that secretly performs many unrelated business operations is not good merely because its interface is small.

Depth means:

- High capability relative to interface complexity
- Strong information hiding
- Stable concepts
- Safe, useful defaults
- Complexity absorbed behind the boundary

Depth does **not** mean:

- Hidden global state
- Surprising side effects
- A god object
- One generic method that accepts a huge configuration object
- Unrelated responsibilities combined merely to reduce method count

When designing an interface, ask:

- Does it expose a coherent domain concept?
- Does the module hide complexity callers shouldn't need to understand?
- Are the defaults safe and unsurprising?
- Would splitting it reveal genuinely independent responsibilities?
- Is the interface small because the abstraction is good, or because complexity was hidden in an unstructured options object?
