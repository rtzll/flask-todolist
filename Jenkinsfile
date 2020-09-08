pipeline {
    agent any

    stages {
        stage('Build ') {
           options {
                timeout(time: 5, unit: "MINUTES")
            }

              
            steps {
              // sh label: '', script: '''git checkout origin/dev

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
         stage("Starting app") {
            options {
                timeout(time: 5, unit: "MINUTES")
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
         stage("Test") {
            options {
                timeout(time: 5, unit: "MINUTES")
            }

          
            steps {
                sh label: '', script: './tests/test.sh'
            }
         }  
         stage("Stopping app") {
           
            steps {
                sh label: '', script: '''sudo docker-compose down
'''
            }
         }   
         stage("Deploy") {
           
            steps {
                sh label: '', script: '''sudo docker login --username usama911 --password 722e8d94-09f8-41d6-b719-b8d6055807e3
'''
                sh label: '', script: 'sudo docker tag todolist:app usama911/todolist:app'
                sh label: '', script: 'sudo docker push usama911/todolist:app'
            }
         }  
                     
                     
    }
}
