pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Test') {
      steps {
        sh 'poetry install'
        sh 'poetry run pytest --cov=app --cov-report=xml'
      }
    }
    stage('SonarQube') {
      environment {
        SONAR_TOKEN = credentials('sonar-token')
      }
      steps {
        sh "sonar-scanner -Dsonar.projectKey=neurobank \
                           -Dsonar.python.coverage.reportPaths=coverage.xml"
      }
    }
    stage('Build & Push') {
      steps {
        sh 'docker build -t myrepo/neurobank:${BUILD_NUMBER} .'
        sh 'docker push myrepo/neurobank:${BUILD_NUMBER}'
      }
    }
    stage('Deploy AppRunner') {
      steps {
        // AWS CLI / CDK / Terraform script here
        script {
          sh '''
            aws apprunner update-service \
              --service-arn ${APP_RUNNER_SERVICE_ARN} \
              --source-configuration '{
                "ImageRepository": {
                  "ImageIdentifier": "myrepo/neurobank:${BUILD_NUMBER}",
                  "ImageConfiguration": {
                    "Port": "8000"
                  }
                }
              }'
          '''
        }
      }
    }
  }
}
