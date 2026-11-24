pipeline {
    agent any

    environment {
        APP_NAME    = "aceest-fitness"
        APP_VERSION = "v4.0.0"
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Checking out ${APP_NAME} (${APP_VERSION})"
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Setting up virtual environment and installing dependencies'
                sh '''
                    python3 -m venv .venv
                    .venv/bin/pip install --upgrade pip
                    .venv/bin/pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running Pytest unit tests and generating coverage reports'
                sh '''
                    export PYTHONPATH=.
                    .venv/bin/pytest -v --junitxml=test-results.xml --cov=ACEest_Fitness --cov-report=xml:coverage.xml
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('Package Build Artifact') {
            steps {
                echo "Packaging versioned artifact for ${APP_VERSION} (Build #${BUILD_NUMBER})"
                sh '''
                    mkdir -p dist
                    SHORT_SHA=$(git rev-parse --short HEAD || echo "local")
                    ARTIFACT="dist/${APP_NAME}-${APP_VERSION}-build-${BUILD_NUMBER}-${SHORT_SHA}.tar.gz"
                    tar -czf "${ARTIFACT}" ACEest_Fitness.py app.py requirements.txt Dockerfile tests/
                    ls -lh dist/
                '''
                archiveArtifacts artifacts: 'dist/*.tar.gz', fingerprint: true
            }
        }

        stage('Code Inspection') {
            steps {
                echo 'Running SonarQube static analysis and coverage inspection'
                sh '''
                    if command -v docker >/dev/null 2>&1 && [ -n "${SONAR_HOST_URL}" ] && [ -n "${SONAR_TOKEN}" ]; then
                        docker run --rm \
                          --add-host=host.docker.internal:host-gateway \
                          -e SONAR_HOST_URL="${SONAR_HOST_URL}" \
                          -e SONAR_TOKEN="${SONAR_TOKEN}" \
                          -v "${WORKSPACE}:/usr/src" \
                          sonarsource/sonar-scanner-cli
                    else
                        echo "SONAR_HOST_URL or SONAR_TOKEN not set; running syntax check"
                        .venv/bin/python -m py_compile ACEest_Fitness.py app.py
                    fi
                '''
            }
        }

        stage('Deploy Staging Smoke Check') {
            steps {
                echo 'Running staging smoke verification for ACEest Fitness'
                sh '''
                    mkdir -p /tmp/aceest-fitness-staging
                    cp ACEest_Fitness.py app.py requirements.txt /tmp/aceest-fitness-staging/
                    cd /tmp/aceest-fitness-staging
                    python3 -m venv .venv
                    .venv/bin/pip install -q -r requirements.txt
                    if [ -f app.pid ]; then
                        kill $(cat app.pid) 2>/dev/null || true
                    fi
                    nohup .venv/bin/gunicorn -b 0.0.0.0:5050 ACEest_Fitness:app > app.log 2>&1 &
                    echo $! > app.pid
                    sleep 2
                    curl -f -s http://127.0.0.1:5050/health
                '''
            }
        }
    }

    post {
        success {
            echo "CI pipeline succeeded for ${APP_NAME} ${APP_VERSION}"
        }
        failure {
            echo "Pipeline failed — check test or build logs"
        }
    }
}
