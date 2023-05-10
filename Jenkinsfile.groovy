pipeline {
  agent any
  
  stages {
    stage('Install dependencies') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }
    
    stage('Run tests') {
      steps {
        sh 'python manage.py test'
      }
    }
    
    stage('Deploy') {
      steps {
        sh 'python manage.py migrate'
        sh 'python manage.py collectstatic --no-input'
      }
    }
  }
}