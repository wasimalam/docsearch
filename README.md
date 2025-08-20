# Document Search Engine

This project is a document search engine that uses Elasticsearch, MySQL, and a Python backend.

## Services

The `docker-compose.yml` file defines the following services:

*   **db**: A MySQL database instance.
*   **phpmyadmin**: A web interface for managing the MySQL database.
*   **elasticsearch**: An Elasticsearch instance for indexing and searching documents.
*   **searchapi**: A Python-based API for interacting with the search engine.

## Getting Started

To get started with this project, you will need to have Docker and Docker Compose installed. Once you have them installed, you can run the following command to start the services:

```bash
docker-compose up -d
```

This will start all of the services in the background. You can then access the services at the following URLs:

*   **phpmyadmin**: http://localhost:8080
*   **elasticsearch**: http://localhost:9200
*   **searchapi**: http://localhost:5000
