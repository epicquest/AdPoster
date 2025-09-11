# Copilot Instructions

These are coding guidelines for GitHub Copilot suggestions in this repository. All generated code should follow these principles:

---

## ✅ KISS Principle (Keep It Simple, Stupid)
- Prefer simple, clear, and direct solutions over clever or over-engineered ones.
- Avoid unnecessary abstractions and premature optimizations.
- Write code that is easy to read and understand for future maintainers.
- **Example:** Prefer a simple `if/else` statement over a complex ternary operator for readability.

---

## ✅ SOLID Principles
Copilot suggestions should respect object-oriented design best practices:

1.  **Single Responsibility Principle**
    Each class or function should have one clear responsibility.
2.  **Open/Closed Principle**
    Code should be open for extension but closed for modification.
3.  **Liskov Substitution Principle**
    Subtypes must be substitutable for their base types without altering correctness.
4.  **Interface Segregation Principle**
    Prefer many small, specific interfaces over large, general-purpose ones.
5.  **Dependency Inversion Principle**
    Depend on abstractions, not on concrete implementations.

---

## 🚀 General Notes
- Favor readability and maintainability over brevity.
- Use meaningful names for variables, functions, and classes (e.g., `calculateTotalPrice` instead of `calc_tp`).
- Follow project-specific style conventions if they exist.

---

## 🛡️ Security
Copilot should prioritize secure coding practices.

- **Sanitize and Validate:** Always validate and sanitize user inputs to prevent injection attacks (SQL, XSS, etc.).
- **Avoid Hardcoding Secrets:** Never hardcode API keys, passwords, or other secrets. Use environment variables or a secure vault.
- **Principle of Least Privilege:** When generating code for permissions, adhere to the principle of least privilege.

---

## 🧪 Testing
All generated code should be easily testable and accompanied by a plan for testing.

- **Testability:** Write functions and components that are isolated and have predictable outputs for given inputs.
- **Pattern:** Follow the **Arrange-Act-Assert (AAA)** pattern for unit tests.
- **Mocks:** When mocking external dependencies, use a clear mocking library and ensure the mock correctly simulates the external behavior.
- **Example:** For a function `add(a, b)`, generate a test case that checks for correct addition, zero values, and negative numbers.

---

## 🐞 Error Handling & Observability
Ensure code is resilient and provides useful feedback for debugging.

- **Structured Handling:** Use `try...catch` blocks or language-specific error handling mechanisms.
- **Clear Messages:** Provide clear, actionable, and user-friendly error messages. Avoid exposing technical details in public-facing errors.
- **Logging:** When an error is caught, log it with sufficient context (stack trace, input values, etc.) to aid in debugging. Use appropriate log levels (e.g., `info`, `warn`, `error`).
- **Graceful Failure