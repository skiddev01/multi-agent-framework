# Multi-Agent Framework

A comprehensive, production-ready framework for building multi-agent AI systems based on the four-level design methodology (Conceptual, Functional, Behavioral, Technical).

## Gridfinity Assistant

A worked example app built on this framework. Upload a photo of the things you
want to store, tell it how big your grid is, and it groups similar objects,
sizes the right [Gridfinity](https://gridfinity.xyz) bins, and finds printable
models to make.

**Pipeline (three coordinated agents):**

1. **Vision agent** — Claude analyzes the photo, identifies objects, estimates
   their real-world size (mm), and groups similar items.
2. **Recommender** — deterministic Gridfinity spec math (42 mm cells, 7 mm
   heights) picks the smallest standard bin that fits each group, then packs
   the bins onto your baseplate.
3. **Research agent** — Claude's web search finds real printable models
   (Printables / MakerWorld / Thingiverse / gridfinity.xyz) per group.

**Run it:**

```bash
pip install -e .
export ANTHROPIC_API_KEY=sk-ant-...   # optional — omit for offline demo mode
gridfinity-web                        # serves http://127.0.0.1:8000
```

Then open the page, drop in a photo, set your grid size (e.g. `5 x 4` cells),
and hit **Analyze**. Without an API key the app runs in **demo mode**: the
Gridfinity math and grid-packing are fully live, and container links fall back
to search/generator URLs.

Configuration via env vars: `ANTHROPIC_API_KEY`, `GRIDFINITY_VISION_MODEL`,
`GRIDFINITY_RESEARCH_MODEL`, `GRIDFINITY_HOST`, `GRIDFINITY_PORT`.

The core (`src/gridfinity/spec.py`, `recommender.py`) is offline and fully unit
tested: `pytest tests/unit/test_gridfinity_*.py`.


## Quick Start

1. **Clone and Setup**
   ```bash
   git clone https://github.com/yourusername/multi-agent-framework.git
   cd multi-agent-framework
   ./scripts/setup.sh
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run Example**
   ```bash
   python -m src.examples.simple_research_crew
   ```

## Documentation

- [Architecture Overview](docs/architecture/README.md)
- [Agent Development Guide](docs/agent_specs/README.md)
- [Deployment Guide](docs/runbooks/deployment.md)

## Framework Features

### Core Capabilities
- **Four-Level Design Methodology**: Systematic approach from concept to implementation
- **Multiple Framework Support**: CrewAI, LangGraph, AutoGen integration
- **Production Ready**: Monitoring, testing, CI/CD included
- **Modular Architecture**: Loosely coupled, highly cohesive components

### Agent Types
- **Research Agents**: Web search, document analysis, data gathering
- **Content Agents**: Writing, summarization, formatting
- **Coordinator Agents**: Task orchestration, workflow management
- **Specialist Agents**: Domain-specific expertise modules

### Monitoring & Observability
- **AgentOps Integration**: Session replay, cost tracking
- **LangSmith Tracing**: End-to-end execution monitoring
- **Custom Metrics**: Performance and quality measurement
- **Error Tracking**: Automated error detection and alerting

## Development

### Prerequisites
- Python 3.9+
- Git
- Docker (optional)

### Setup Development Environment
```bash
# Install dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Testing Strategy
- **Unit Tests**: Individual agent behavior validation
- **Integration Tests**: Multi-agent coordination verification
- **Behavioral Tests**: End-to-end scenario validation
- **Performance Tests**: Load and scalability testing

## Project Structure

```
multi-agent-framework/
├── src/                    # Source code
│   ├── agents/            # Agent implementations
│   ├── config/            # Configuration management
│   ├── tools/             # Shared tools and utilities
│   ├── workflows/         # Multi-agent workflows
│   └── shared/            # Common utilities
├── tests/                 # Testing infrastructure
├── docs/                  # Documentation
├── infrastructure/        # Deployment configurations
├── monitoring/           # Observability configs
└── scripts/              # Automation scripts
```

## Deployment

### Local Development
```bash
docker-compose up -d
```

### Production Deployment
```bash
# Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Or using scripts
./scripts/deploy.sh production
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Based on research from:
- Microsoft's Multi-Agent System Design Guide
- CrewAI Framework Documentation
- LangGraph Architecture Patterns
- Academic research on agent design patterns
