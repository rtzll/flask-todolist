pipeline {
    agent any

    stages {
        stage('dev') {
            steps {
                sh label: '', script: 'ls -l'
                sh label: '', script: 'docker --version'
                sh label: '', script: 'sudo docker build -t todolist:app .'
                sh label: '', script: 'sudo docker images ls'
               
            }
        stage('Verify branch') {
            steps {
                echo "$GIT_BRANCH"
               
            }
        }    
        }
    }
}
