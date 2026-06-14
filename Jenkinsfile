pipeline {
    agent any

    options {
        timeout(time: 1, unit: 'HOURS')
        ansiColor('xterm')
        disableConcurrentBuilds()
    }

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        ECR_REGISTRY       = '099720109477.dkr.ecr.us-east-1.amazonaws.com'
        APP_NAME           = 'sre-ai-agent'
        IMAGE_TAG          = "${env.BUILD_NUMBER}"
        KUBECONFIG_CRED    = credentials('aws-eks-kubeconfig')
        SMTP_RECEIVER      = 'admin@example.com'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/mymtg/ai-self-healing-k8s.git'
            }
        }

        stage('Static Lint Checks') {
            steps {
                echo 'Running Python & Terraform syntax linting check...'
                sh 'python3 -m py_compile ai-agent/*.py'
                sh 'terraform -cwd terraform/ validate'
            }
        }

        stage('Docker Build & ECR Push') {
            steps {
                script {
                    echo "Logging into AWS ECR..."
                    sh "aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}"
                    
                    echo "Building Docker image..."
                    sh "docker build -t ${ECR_REGISTRY}/${APP_NAME}:${IMAGE_TAG} -t ${ECR_REGISTRY}/${APP_NAME}:latest ."
                    
                    echo "Pushing Image to AWS ECR..."
                    sh "docker push ${ECR_REGISTRY}/${APP_NAME}:${IMAGE_TAG}"
                    sh "docker push ${ECR_REGISTRY}/${APP_NAME}:latest"
                }
            }
        }

        stage('Infrastructure Sync (Terraform)') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-credentials']]) {
                    sh '''
                        cd terraform/
                        terraform init
                        terraform apply -auto-approve
                    '''
                }
            }
        }

        stage('Deploy to EKS Cluster') {
            steps {
                script {
                    // Inject Kubeconfig from credentials
                    sh "mkdir -p ~/.kube && cp ${KUBECONFIG_CRED} ~/.kube/config"
                    
                    echo "Updating sre-ai-agent Kubernetes deployment..."
                    sh "kubectl apply -f kubernetes/namespace.yaml"
                    sh "kubectl apply -f kubernetes/configmap.yaml"
                    sh "kubectl apply -f kubernetes/secret.yaml"
                    
                    // Replace ECR image tag placeholder dynamically
                    sh "sed -i 's/:latest/:${IMAGE_TAG}/g' kubernetes/deployment.yaml"
                    sh "kubectl apply -f kubernetes/deployment.yaml"
                    
                    sh "kubectl apply -f kubernetes/service.yaml"
                    sh "kubectl apply -f kubernetes/hpa.yaml"
                    sh "kubectl apply -f kubernetes/ingress.yaml"
                }
            }
        }

        stage('Deployment Health Verification') {
            steps {
                script {
                    echo "Verifying application rollout status..."
                    try {
                        sh "kubectl rollout status deployment/${APP_NAME} -n production --timeout=120s"
                        echo "Deployment successfully verified!"
                    } catch (Exception e) {
                        echo "Deployment health check failed. Initiating automated rolling rollback..."
                        sh "kubectl rollout undo deployment/${APP_NAME} -n production"
                        error("Build failed and was automatically rolled back: ${e.message}")
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            mail to: "${SMTP_RECEIVER}",
                 subject: "SUCCESS: Jenkins Pipeline Build #${env.BUILD_NUMBER}",
                 body: "Great news! Jenkins Build #${env.BUILD_NUMBER} completed successfully.\nCode has been built, tested, and deployed to EKS cluster."
        }
        failure {
            mail to: "${SMTP_RECEIVER}",
                 subject: "FAILURE: Jenkins Pipeline Build #${env.BUILD_NUMBER}",
                 body: "Attention: Jenkins Build #${env.BUILD_NUMBER} has failed.\nPlease review Jenkins console output to diagnose and fix errors."
        }
    }
}
