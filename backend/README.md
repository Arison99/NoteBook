# NoteBook Backend

A professional GraphQL learning application with distributed CouchDB replication.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run the application
python main.py
```

## Project Structure

- **`src/notebook/`** - Main application package
- **`config/`** - Configuration and settings
- **`tests/`** - Test suite with unit and integration tests
- **`scripts/`** - Utility scripts
- **`docs/`** - Documentation

## Key Features

✅ **GraphQL API** with Ariadne  
✅ **Distributed Replication** with CouchDB  
✅ **Professional Structure** with layered architecture  
✅ **Comprehensive Testing** with pytest  
✅ **Docker Support** for containerization  
✅ **Load Balancing** with HAProxy  
✅ **Monitoring & Health checks**  

## Documentation

- [Architecture Guide](docs/architecture.md)
- [Testing Guide](docs/testing.md)
- [Replication Guide](REPLICATION_GUIDE.md)

## Testing

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run only unit tests
python run_tests.py --unit
```

## Docker Deployment

```bash
# Single container
docker build -t notebook-backend .
docker run -p 5000:5000 notebook-backend

# Full distributed setup
docker-compose up -d
```

Built with ❤️ for learning GraphQL and distributed systems.