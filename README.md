# ground

**The Foundation of TickShock.**

`ground` is the core library for the TickShock algorithmic trading stack. It serves as the "single source of truth" for the entire ecosystem, ensuring type safety and architectural consistency across all microservices.

---

### 📦 Key Components

* **Shared Type Definitions:** Universal models ensuring data integrity from **[flux](https://github.com/TickShock/flux)** ingestion to **[arc](https://github.com/TickShock/arc)** execution.
* **Architectural Constants:** Centralized "source of truth" for system identifiers and configurations used by the **[relay](https://github.com/TickShock/relay)** API layer.
* **Data Lake Schemas:** Standardized validation for market data stored in **[battery](https://github.com/TickShock/battery)**, ensuring compatibility with **[spark](https://github.com/TickShock/spark)** research.
* **Telemetry Protocols:** Unified logging and status formats for consistent visualization in **[meter](https://github.com/TickShock/meter)** and **[gauge](https://github.com/TickShock/gauge)**.

### 🚀 Usage

As this is a foundational dependency, all other TickShock repositories should have `ground` as a poetry dependency:

```bash
[tool.poetry.dependencies]
ground = { git = "https://github.com/TickShock/ground", tag = "v0.1.0" }
```

Reference ground content:

```
from tickshock.ground.types import Candle
```
