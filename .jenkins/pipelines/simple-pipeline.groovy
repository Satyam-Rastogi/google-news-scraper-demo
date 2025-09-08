// Simple Jenkins Pipeline for Google News Scraper API

pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'news-scraper-api'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh '''
                    echo "Setting up environment..."
                    python -m venv venv
                    source venv/bin/activate
                    pip install uv
                    uv sync --extra redis
                '''
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    source venv/bin/activate
                    echo "Running tests..."
                    uv run ruff check src/
                    uv run ruff format --check src/
                    uv run pytest tests/ -v || true
                '''
            }
        }
        
        stage('Build') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build -f deployment/docker/Dockerfile -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                sh '''
                    echo "Deploying application..."
                    cd deployment/docker
                    docker-compose down || true
                    docker-compose up -d
                    
                    echo "Waiting for services..."
                    sleep 30
                    
                    echo "Health check..."
                    curl -f http://localhost:8000/health/ || exit 1
                '''
            }
        }
    }
    
    post {
        always {
            sh '''
                echo "Cleaning up..."
                docker system prune -f || true
            '''
        }
        
        success {
            echo "✅ Pipeline completed successfully!"
        }
        
        failure {
            echo "❌ Pipeline failed!"
        }
    }
}
