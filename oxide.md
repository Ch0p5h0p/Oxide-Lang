# Oxide Language — Detailed Design Notes

## 1️⃣ Core Philosophy

* **Compiled language** designed to produce raw assembly output for **maximum performance**.
* **Zero runtime**: no garbage collection, no virtual machine, no runtime type checking.
* Compiler handles all checks at **compile-time**, including type safety, parameter validation, and memory management decisions.
* **Optional manual memory control** for advanced users; otherwise, compiler manages temporary allocations efficiently.
* **Strong typing at compile-time**: types exist to ensure safety, but are **discarded in the compiled binary**, ensuring zero runtime type overhead.
* **Performance first**: design decisions favor CPU efficiency and cache-friendly memory layouts.

---

## 2️⃣ `df` — Unified Variables and Functions

* Every declaration uses the `df` keyword, unifying variables and functions. This simplifies compiler logic and reduces unnecessary distinctions between types of declarations.

```oxide
df x = 12563;          // simple variable
df f = (params){...};  // parametric expression (function)
```

### Parametric Expressions

* Curly braces `{}` indicate a **parametric expression** (similar to a function).
* Parameters are explicitly declared in parentheses before the `{}`.
* Inside the curly braces, **no access to outer-scope variables** by default — full isolation ensures predictable compilation and enables inlining.

**Example**

```oxide
df x = 2;
df f = (a,b,x){ a + b + x };
f(1,2,x);  // fully explicit parameter passing
```

### Key Design Points

* **Isolation**: expressions cannot “reach out” to outer variables unless passed as explicit parameters.
* **Explicit parameter passing** was chosen over optional capture (`!x`) for **maximal speed and inlining**.
* Optional captures were considered but rejected because they introduce **runtime dependency on outer variables**, which breaks the ability to safely inline and replace variables with registers at compile time.

---

## 3️⃣ Scope Rules

* **Each parametric expression has its own scope**.
* Only the declared parameters and any locally defined variables within the expression are accessible.
* Outer variables cannot be referenced unless explicitly passed in as parameters.
* This guarantees:

  1. Predictable memory layout
  2. Safe register allocation
  3. Full inlining without worrying about hidden dependencies

**Trade-Offs**

* Slightly more verbose for the user, because every value from an outer scope must be passed manually.
* Eliminates the need for closure support or runtime context capturing.

---

## 4️⃣ Speed-Oriented Design Strategies

### 4.1 Inlining

* Because parametric expressions only depend on explicit parameters, the compiler can safely **inline them**.
* Eliminates function call overhead entirely.

### 4.2 Compile-Time Evaluation

* Constant expressions and literal parameters are **precomputed at compile-time**.
* Example:

```oxide
df sum = (a,b){ a + b };
df y = sum(10,5);  // compiler computes 15 at compile-time
```

### 4.3 Dead Code Elimination

* Any unreachable code or unused expressions are **removed at compile-time**, reducing binary size and memory use.

### 4.4 Loop Unrolling

* Small loops with fixed iteration counts can be **fully unrolled**, reducing branch and jump overhead.

### 4.5 Register Allocation

* Hot variables and frequently used parameters are **kept in CPU registers**.
* Locals and temporaries that don’t fit in registers spill to **expression-specific arenas or the stack**.

### 4.6 Tail-Call Optimization

* Recursive parametric expressions can be transformed into loops, eliminating stack growth.

### 4.7 Direct-to-Assembly

* Compiler generates raw assembly instructions directly.
* Full control over register usage, instruction selection, and memory layout.

---

## 5️⃣ Memory Management

### 5.1 Original Idea: Giant Stack Frames

* Allocate a **large contiguous block of memory** for the entire program.
* Subframes for expressions/functions live inside this block.
* Pros:

  * Predictable memory layout
  * Cache-friendly sequential access
* Cons:

  * Can waste memory if the block is overestimated
  * Difficult to dynamically adapt for large or variable-sized allocations

**Verdict**: dropped in favor of a more adaptive, memory-efficient approach.

---

### 5.2 Positional Arenas (Current Idea)

* Two registers are used to define the **current active memory segment**:

  * `r14` → start of segment
  * `r15` → end of segment

#### How it Works

1. **Enter Expression**

   * Push the current `r14`/`r15` onto a small register stack.
   * Move `r14`/`r15` to define a new segment for this expression.

2. **Allocate Memory**

   * Every allocation inside the expression simply **increments `r14`**:

   ```asm
   mov rax, r14
   add r14, object_size
   ```

   * No heap or malloc required.

3. **Exit Expression**

   * Restore previous `r14`/`r15` from the stack.
   * Optional: zero out the memory segment to prevent accidental reuse.

**Advantages**

* Allocation = pointer increment → O(1)
* Deallocation = restore registers → O(1)
* Memory is **fully isolated per expression**, eliminating cross-expression interference
* Cache-friendly, contiguous memory layout
* Supports recursion naturally; each recursive call gets its own segment

#### Pseudocode

```asm
; enter expression
push r14
push r15
mov r14, expr_start
mov r15, expr_end

; allocate 16 bytes
mov rax, r14
add r14, 16

; exit expression
pop r15
pop r14
```

---

### 5.3 Optional Optimizations

1. **Register + Stack Hybrid**

   * Keep small locals in registers
   * Spill larger locals/subframe variables to the stack if necessary

2. **Mini-Arenas / Pools**

   * For larger or short-lived allocations, allocate small reusable arenas
   * Reset or reuse arenas after expression exits

3. **Parameter Passing**

   * Small primitives: by value
   * Large structs/arrays: by reference to reduce copy overhead

4. **Compile-Time Size Analysis**

   * Compiler can calculate max subframe/arena size → allocate exact memory, no wasted space

---

## 6️⃣ Memory vs Speed Trade-Off

| Approach                    | Speed    | Memory Efficiency | Notes                                                  |
| --------------------------- | -------- | ----------------- | ------------------------------------------------------ |
| Giant frame + subframes     | 🔥🔥🔥   | Medium            | predictable but can waste memory                       |
| Classic stack frames        | 🔥🔥     | High              | standard call frames                                   |
| Arena / pool allocations    | 🔥🔥🔥   | High              | per-expression arenas                                  |
| Register + stack hybrid     | 🔥🔥🔥🔥 | High              | minimal overhead, compiler-intensive                   |
| Positional arenas (current) | 🔥🔥🔥🔥 | High              | isolated, cache-friendly, fast allocation/deallocation |

---

## 7️⃣ Summary of Design Decisions

### Language Design

* Unified `df` for variables/functions
* Explicit parameter passing → fully isolated expressions
* Types exist at compile-time only
* Zero runtime overhead

### Memory Design

* **Positional arenas** per expression:

  * Two registers define start/end of segment
  * Linear allocation inside expression
  * Reset on exit
* No heap fragmentation, no runtime allocation overhead
* Supports recursion and nesting naturally
* Optional memory zeroing for safety/debug

### Performance Strategies

* Aggressive inlining of parametric expressions
* Compile-time constant folding
* Dead code elimination
* Loop unrolling
* Tail-call optimization
* Register-heavy variable allocation
* Direct assembly generation

---

## 8️⃣ Optional Enhancements / Ideas for Later

* Arena zeroing can be skipped in release builds for speed
* Compile-time analysis to precompute segment sizes for nested expressions
* Optional “overflow” mini-arenas if an expression exceeds its allocated segment
* Consider compiler warnings for very large parameter lists to avoid excessive copies

---

✅ **Bottom Line**

* Oxide is designed to be **fast, lean, and predictable**.
* Explicit parameters, isolated scopes, and positional arenas ensure:

  * Maximal CPU speed
  * Tight, cache-friendly memory usage
  * Predictable behavior
* No heap, no runtime, no GC — just **raw assembly control over everything**.


