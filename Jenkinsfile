pipeline {
  agent any

  stages {

    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/Baribrahim/OneSky.git'
      }
    }

    stage('Inject .env files') {
      steps {
        withCredentials([
          file(credentialsId: 'team1-backend-env', variable: 'ENV_FILE'),
          file(credentialsId: 'team1-frontend-env', variable: 'FRONTEND_ENV')
        ]) {
          sh '''
            set +x
            # Copy backend env file to repo root for docker-compose (similar pattern to Test stage)
            cp "$ENV_FILE" ./backend/functionality/.env
            chmod 600 ./backend/functionality/.env
            
            # Copy frontend env file
            cp "$FRONTEND_ENV" ./frontend/.env
            chmod 600 ./frontend/.env
          '''
        }
      }
    }

    stage('Build & Start Docker Containers') {
      steps {
        sh '''
          # Source .env file to make variables available for docker-compose substitution
          set -a
          . ./backend/functionality/.env
          set +a
          docker compose down
          docker compose up --build -d
        '''
      }
    }

    stage('Debug Backend and DB') {
      steps {
        sh '''
          echo "==== Backend Logs (last 50 lines) ===="
          docker compose logs backend --tail=50 || true

          echo ""
          echo "==== DB Logs (last 50 lines) ===="
          docker compose logs db --tail=50 || true
        '''
      }
    }

  }
}