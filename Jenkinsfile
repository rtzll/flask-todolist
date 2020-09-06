pipeline {
    agent any

    stages {
        stage('dev') {
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
         stage("Start test app") {
             steps {
                 sh label: '', script: ''' sudo docker-compose build
 sudo docker-compose up -d
 sudo ./scripts/test_cont.ps1'''
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
         stage("Run tests") {
            steps {
                sh label: '', script: '  pytest  ./tests/test_basics.py'
            }
         }  
         stage("Stop test app") {
            steps {
                sh label: '', script: '''sudo docker-compose down
'''
            }
         }   
                     
                     
    }
}
