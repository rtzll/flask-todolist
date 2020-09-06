pipeline {
    agent any

    stages {
        stage('Build') {
            when {
                branch 'dev'
            }    
            steps {
                sh label: '', script: '''OLD="$(sudo docker ps --all --quiet --filter=name="$CONTAINER_NAME")"
if [ -n "$OLD" ]; then
  sudo docker stop $OLD && sudo docker rm $OLD
fi
CONTAINER_NAME1="todolist"
OLD="$(sudo docker ps --all --quiet --filter=name="$CONTAINER_NAME1")"
if [ -n "$OLD" ]; then
  sudo docker stop $OLD && sudo docker rm $OLD
fi
echo "Building the code"
sudo docker build -t todolist:app .
echo "Testing"
sudo docker images '''
         
            }
       
         }
         stage("Starting and tesing app on dev branch") {
             when {
                 branch 'dev'
             }    
             steps {
                 sh label: '', script: ''' sudo docker-compose build
 sudo docker-compose up -d
 sudo docker-compose ps '''
             }    
             post {
                 success {
                     echo "App started successfully:)"
                 }
                 failure {
                          echo "App failed :("
                 }
             }
         }
         stage("Run Unit tests on stage branch ") {
             when {
                 branch 'stage'
             }    
            steps {
                sh label: '', script: '''git checkout stage
git merge dev'''
                sh label: '', script: 'sudo docker-compose ps'
            }
         }  
         stage("Stopping app") {
             when {
                 branch 'stage'
             }    
            steps {
                sh label: '', script: '''sudo docker-compose down
'''
            }
         }   
                     
                     
    }
}
