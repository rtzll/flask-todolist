pipeline {
    agent any

    stages {
        stage('dev') {
            steps {
                sh label: '', script: CONTAINER_NAME="migration"

                sh label: '', script: '''OLD="$(sudo docker ps --all --quiet --filter=name="$CONTAINER_NAME")"
'''
                sh label: '', script: ''' if [ -n "$OLD" ]; then
  sudo docker stop $OLD && sudo docker rm $OLD
fi'''
               
                sh label: '', script: CONTAINER_NAME1="todolist"

                sh label: '', script: '''OLD="$(sudo docker ps --all --quiet --filter=name="$CONTAINER_NAME1")"
'''                
                sh label: '', script: ''' if [ -n "$OLD" ]; then
  sudo docker stop $OLD && sudo docker rm $OLD
fi'''
                sh label: '', script: 'CONTAINER_NAME1="todolist"'
                sh label: '', script: 'OLD="$(sudo docker ps --all --quiet --filter=name="$CONTAINER_NAME1")"'
                sh label: '', script: '''if [ -n "$OLD" ]; then
  sudo docker stop $OLD && sudo docker rm $OLD
fi'''
                sh label: '', script: 'echo "Building the code"'
                sh label: '', script: 'sudo docker build -t todolist:app .'
                sh label: '', script: 'echo "Testing"'
                sh label: '', script: 'sudo docker images'
            }
       
         }
    }
}
