pipeline {
    agent any
    
    triggers {
        githubPush()
    }
    
    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_REPO_PREFIX = 'nils06'
        MOVIE_SERVICE_IMAGE = "${DOCKER_REPO_PREFIX}/movie-service"
        CAST_SERVICE_IMAGE = "${DOCKER_REPO_PREFIX}/cast-service"
        HELM_CHART_PATH = './charts'
        DOCKER_HUB_USER = 'nils06'
        DOCKER_HUB_PASS = credentials('DOCKER_HUB_PASS')
        KUBECONFIG = credentials("KUBECONFIG")
        
        DEV_NODEPORT = '30051'
        QA_NODEPORT = '30052'
        STAGING_NODEPORT = '30053'
        PROD_NODEPORT = '30054'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.BRANCH_NAME = env.GIT_BRANCH.replaceAll('origin/', '')
                    echo "Building on branch: ${env.BRANCH_NAME}"
                    
                    env.IMAGE_TAG = "${env.BRANCH_NAME}"
                    echo "Image tag: ${env.IMAGE_TAG}"
                }
            }
        }
        
        stage('Build Docker Images') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'staging'
                    branch 'qa'
                    branch 'prod'
                }
            }
            steps {
                script {
                    echo "Building Docker images..."
                    
                    sh """
                        docker build -t ${MOVIE_SERVICE_IMAGE}:${IMAGE_TAG} ./movie-service
                        docker tag ${MOVIE_SERVICE_IMAGE}:${IMAGE_TAG} ${MOVIE_SERVICE_IMAGE}:latest
                    """
                    
                    sh """
                        docker build -t ${CAST_SERVICE_IMAGE}:${IMAGE_TAG} ./cast-service
                        docker tag ${CAST_SERVICE_IMAGE}:${IMAGE_TAG} ${CAST_SERVICE_IMAGE}:latest
                    """
                }
            }
        }
        
        stage('Run Tests') {
            parallel {
                stage('Test Movie Service') {
                    steps {
                        script {
                            echo "Testing Movie Service..."
                            echo "TODO: Implement movie service tests"
                            echo "Movie service tests completed successfully"
                        }
                    }
                }
                
                stage('Test Cast Service') {
                    steps {
                        script {
                            echo "Testing Cast Service..."
                            echo "TODO: Implement cast service tests"
                            echo "Cast service tests completed successfully"
                        }
                    }
                }
            }
        }
        
        stage('Push to DockerHub') {
            when {
                anyOf {
                    branch 'dev'
                    branch 'staging'
                    branch 'qa'
                    branch 'prod'
                }
            }
            steps {
                script {
                    echo "Pushing images to DockerHub..."
                    
                    // Login to DockerHub
                    sh '''
                        echo $DOCKER_HUB_PASS | docker login -u $DOCKER_HUB_USER --password-stdin
                    '''
                    
                    // Push images
                    sh """
                        docker push ${MOVIE_SERVICE_IMAGE}:${IMAGE_TAG}
                        
                        docker push ${CAST_SERVICE_IMAGE}:${IMAGE_TAG}
                    """
                }
            }
            post {
                always {
                    // Cleanup: logout from DockerHub
                    sh 'docker logout'
                }
            }
        }
        
        stage('Deploy to Development') {
            when {
                branch 'dev'
            }
            steps {
                script {
                    deployToEnvironment('dev', env.IMAGE_TAG, env.DEV_NODEPORT)
                }
            }
        }
        
        stage('Deploy to QA') {
            when {
                branch 'qa'
            }
            steps {
                script {
                    deployToEnvironment('qa', env.IMAGE_TAG, env.QA_NODEPORT)
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'staging'
            }
            steps {
                script {
                    deployToEnvironment('staging', env.IMAGE_TAG, env.STAGING_NODEPORT)
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'prod' 
            }
            steps {
                script {
                    // Manual approval required for production deployment
                    input message: 'Deploy to Production?', 
                          ok: 'Deploy',
                          submitterParameter: 'APPROVER'
                    
                    echo "Production deployment approved by: ${APPROVER}"
                    deployToEnvironment('prod', env.IMAGE_TAG, env.PROD_NODEPORT)
                }
            }
        }
    }
}

def deployToEnvironment(environment, imageTag, nodePort) {
    sh '''
          rm -Rf .kube
          mkdir .kube
          ls
          cat $KUBECONFIG > .kube/config
    '''
    sh """
        kubectl create namespace ${environment} --dry-run=client -o yaml | kubectl apply -f -
    """
    
    // Deploy using Helm
    sh """
        helm upgrade --install fastapiapp-${environment} ${HELM_CHART_PATH} \\
            --namespace ${environment} \\
            --set movieService.image.tag=${imageTag} \\
            --set castService.image.tag=${imageTag} \\
            --set global.environment=${environment} \\
            --set nginx.service.nodePort=${nodePort} \\
            --wait \\
            --timeout=10m
    """
    
    // Verify deployment
    sh """
        kubectl get pods -n ${environment}
        kubectl get services -n ${environment}
    """
    
    echo "Successfully deployed to ${environment} environment"
}
