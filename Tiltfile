docker_build('daemon-chore-speech-nandy-io', './daemon')

k8s_yaml(kustomize('.'))

k8s_resource('daemon', port_forwards=['26751:5678'])