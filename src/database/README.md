# Database Package

This package contains all database-related functionality for the Google News Scraper.

## Directory Structure

```
database/
├── __init__.py              # Package initialization
├── config.py                # Database configuration
├── models/                  # Database models
│   ├── __init__.py
│   ├── article.py           # Article model (future)
│   ├── search_history.py    # Search history model (future)
│   └── user.py              # User model (future)
├── migrations/              # Database migrations
│   ├── __init__.py
│   ├── alembic.ini          # Alembic configuration (future)
│   └── versions/            # Migration files (future)
├── repositories/            # Repository pattern
│   ├── __init__.py
│   ├── base.py              # Base repository (future)
│   ├── article_repository.py # Article repository (future)
│   └── search_repository.py  # Search repository (future)
└── connections/             # Connection management
    ├── __init__.py
    ├── connection.py        # Database connection (future)
    ├── session.py           # Session management (future)
    └── health.py            # Database health checks (future)
```

## Future Implementation Plan

### Phase 1: Basic Database Setup
- [ ] SQLAlchemy integration
- [ ] Database connection management
- [ ] Basic Article model

### Phase 2: Repository Pattern
- [ ] Base repository class
- [ ] Article repository implementation
- [ ] Search history tracking

### Phase 3: Advanced Features
- [ ] Database migrations with Alembic
- [ ] Connection pooling
- [ ] Database health monitoring
- [ ] Caching layer

### Phase 4: Analytics & Reporting
- [ ] Analytics models
- [ ] Reporting queries
- [ ] Data aggregation

## Current Status

Currently using file-based storage (JSON/CSV files in artifacts directory).
Database integration is prepared but not yet implemented.

## Configuration

Database configuration can be set via environment variables:

```bash
DB_TYPE=sqlite                    # Database type
DB_HOST=localhost                 # Database host
DB_PORT=5432                      # Database port
DB_USERNAME=user                  # Database username
DB_PASSWORD=password              # Database password
DB_NAME=news_scraper.db           # Database name
DB_POOL_SIZE=5                    # Connection pool size
DB_ECHO=false                     # SQLAlchemy echo mode
```
