pipeline {
    agent any

    environment {
        ENVIRONMENT = 'testing'
        CI = 'true'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out code...'
                checkout scm
            }
        }

        stage('Set Up Environment') {
            steps {
                echo '🐍 Setting up Python environment...'
                sh '''
                    python3 -m venv venv || true
                    source venv/bin/activate
                    pip install --upgrade pip
                    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
                    if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt || true; fi
                    pip install ruff mypy pre-commit yamllint
                '''
            }
        }

        stage('Prepare Environment') {
            steps {
                echo '⚙️ Preparing environment...'
                sh 'cp .env.example .env || true'
            }
        }

        stage('Code Quality Checks') {
            steps {
                echo '🧼 Running code quality checks...'
                sh '''
                    source venv/bin/activate
                    echo "Running Ruff and Mypy checks..."
                    ruff check .
                    ruff format --check .
                    echo "Running MyPy type checking on app/ directory with pyproject.toml configuration..."
                    mypy app/
                    echo "Running codespell checks..."
                    codespell -q 2 -I .codespell-ignore-words.txt app README.md docs/
                    echo "✅ Code Quality stage completed."
                '''
            }
        }

        stage('Pre-commit Hooks') {
            steps {
                echo '🧩 Running pre-commit hooks...'
                sh '''
                    source venv/bin/activate
                    pre-commit run --all-files || true
                '''
            }
        }

        stage('Security Scan') {
            steps {
                echo '🔒 Running security scan...'
                sh 'echo "Security scanning skipped in Jenkins (configure Trivy if needed)"'
            }
        }

        stage('Database Migrations') {
            environment {
                DATABASE_URL = 'sqlite+aiosqlite:///./test.db'
            }
            steps {
                echo '🧱 Running Alembic migrations...'
                sh '''
                    source venv/bin/activate
                    alembic upgrade head || true
                '''
            }
        }

        stage('Run Tests') {
            environment {
                DATABASE_URL = 'sqlite+aiosqlite:///./test.db'
                PYTEST_ADDOPTS = '-q'
            }
            steps {
                echo '🧪 Running tests...'
                sh '''
                    source venv/bin/activate
                    pytest --maxfail=1 --disable-warnings -q
                '''
            }
        }
    }

    post {
        always {
            echo '📝 Generating reports...'
            sh '''
                source venv/bin/activate
                ruff check app/ --output-format json > ruff.json || echo "[]" > ruff.json
            '''
            archiveArtifacts artifacts: 'ruff.json', fingerprint: true
        }
        success {
            echo '✅ Pipeline completed successfully'
        }
        failure {
            echo '❌ Pipeline failed'
        }
        cleanup {
            sh 'rm -rf venv || true'
        }
    }
}
