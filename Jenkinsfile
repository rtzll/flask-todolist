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
         
            }
       
         }
    }
}
