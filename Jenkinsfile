pipeline {
    agent any

    stages {
        stage('Build and test on dev') {
            
              
            steps {
                sh label: '', script: '''git checkout origin/dev
'''
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
         stage("Run Functional tests on stage branch ") {
          
            steps {
                sh label: '', script: '''git checkout origin/stage
'''   
                sh label: '', script: '''git config --global user.email "usamazahid0123@gmail.com"
git config --global user.name "Usama42"'''
                sh label: '', script: 'git merge origin/dev'
                sh label: '', script: '''git branch 
'''
                sh label: '', script: 'sudo docker-compose ps'
            }
         }  
         stage("Stopping app") {
           
            steps {
                sh label: '', script: '''git branch 
'''
                sh label: '', script: '''sudo docker-compose down
'''
            }
         }   
         stage("Deploy to prod") {
           
            steps {
                sh label: '', script: '''git checkout origin/prod                
'''
                sh label: '', script: '''git config --global user.email "usamazahid0123@gmail.com"
git config --global user.name "Usama42"'''
                sh label: '', script: 'git merge origin/stage'
                sh label: '', script: '''sudo docker-compose ps
'''
            }
         }  
                     
                     
    }
}
