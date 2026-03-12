properties([disableConcurrentBuilds()])

node {

    def commitSha = ''
    def commitMessage = ''
    def pipelineId = env.BUILD_ID
    def skipCI = false
    def dockerImage = ''
    def dockerRegistry = 'registry.digitalocean.com/vpnn-infra'
    def dockerRegistryCreds = '300304c6-69d3-446c-9ad3-b2ea416fbc7b'
    def branchName = gitRef.split('/')[2]
    def appName = 'mattermost-coffeebot'

    env.SOPS_AGE_KEY_FILE = '/var/lib/jenkins/.age-keys/age-keys.txt'

    withCredentials([
        string(credentialsId: 'ci_telegram_bot_token', variable: 'CI_TELEGRAM_BOT_TOKEN'),
    ]) {
        env.CI_TELEGRAM_BOT_TOKEN = CI_TELEGRAM_BOT_TOKEN
    }

    withCredentials([
        string(credentialsId: 'ci_telegram_chan_id', variable: 'CI_TELEGRAM_CHAN_ID'),
    ]) {
        env.CI_TELEGRAM_CHAN_ID = CI_TELEGRAM_CHAN_ID
    }

    if (!branchName.startsWith('test') && branchName != 'main') {
        echo "Skipping build for branch: ${branchName}"
        return
    }

    if (newRevisionId == '0000000000000000000000000000000000000000') {
        echo "someone deleted branch from Github UI. Skip build"
        return
    }

    try {
        stage('Checkout') {
            checkout scm
            echo "Enforced checkout to remotes/origin/${branchName} from hook"
            sh "git checkout remotes/origin/${branchName}"
            commitSha = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
            echo "Commit SHA: ${commitSha}"
            commitMessage = sh(script: "git log -1 --pretty=%B", returnStdout: true).trim()
            echo "Commit message: ${commitMessage}"
            if (commitMessage.contains('[skip-ci]')) {
                echo "Found [skip-ci]. Skipping pipeline"
                currentBuild.result = 'SUCCESS'
                skipCI = true
            }

        }

        if (!skipCI) {

            def imageTag = "${pipelineId}-${branchName}-${commitSha}"
            env.HELM_IMAGE_TAG = "${imageTag}"

            currentBuild.displayName = "${pipelineId}-${appName}-${branchName}"
            currentBuild.description = "Build and deploy to ${branchName}: ${appName}:${imageTag}"

            stage("Build Docker Image ${appName}") {
                sshagent(['service-user-key']) {
                  withEnv(['DOCKER_BUILDKIT=1']) {
                    sh "docker build --no-cache --ssh default --target prod  -f ./Dockerfile -t ${dockerRegistry}/${appName}:${imageTag} ."
                  }
                }
                echo "Docker Image: ${dockerRegistry}/${appName}:${imageTag}"
            }
            stage("Push Docker Image ${appName}") {
                sh """
                    echo "Pushing Docker image..."
                    docker push ${dockerRegistry}/${appName}:${imageTag}
                """
            }
            stage("Local Cleanup ${appName}") {
                sh "echo 'Очищаем локальные ресурсы'"
                sh "docker rmi ${dockerRegistry}/${appName}:${imageTag}"
            }

            dir("helm/${branchName}"){
                stage("Deploy to k8s") {
                    withKubeConfig([credentialsId: '9feec3fe-ca5d-494f-8a41-27c0479d9d74']) {
                        try {
                            sh "helmwave up --build --kubedog --show-secret=false"
                        } catch (Exception e) {
                            echo "Deploy ${appName}/${branchName} failed. Performing rollback."
                            sh "helmwave rollback"
                            throw e
                        }
                    }
                }
            }

        }
    } catch (Exception e) {
        if (branchName == 'master') {
            sh """ curl --data "parse_mode=HTML" --data "chat_id=${CI_TELEGRAM_CHAN_ID}" --data "text=<b>${JOB_NAME}-${branchName}</b>%0Adeploy failed! (╯°□°)╯︵┻━┻ %0A${BUILD_URL}" -X POST https://api.telegram.org/$CI_TELEGRAM_BOT_TOKEN/sendMessage """
        echo "Pipeline failed: ${e.getMessage()}"
        }
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        if (!skipCI && branchName == 'master' && currentBuild.result != 'FAILURE') {
            sh """ curl --data "parse_mode=HTML" --data "chat_id=${CI_TELEGRAM_CHAN_ID}" --data "text=<b>${JOB_NAME}-${branchName}</b>%0Adeploy done%0A${BUILD_URL}" -X POST https://api.telegram.org/$CI_TELEGRAM_BOT_TOKEN/sendMessage """
        }
        echo "Pipeline result: ${currentBuild.result == 'FAILURE' ? 'FAILURE' : 'SUCCESS'}"
    }
}
