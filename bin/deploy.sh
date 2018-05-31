#!/usr/bin/env bash
set -e

dt=$(date '+%y-%m-%d-%H-%M-%S');
echo "$dt"


set_env(){
    export $(cat ./env/.env | grep -v ^# | xargs)
}


show_group_info () {
    gcloud compute instance-groups managed list $1 --zones ${ZONE} --quiet
}

create_instance_group(){
    gcloud compute instance-groups managed create ${SERVER_PREFIX}-${dt} \
        --zone ${ZONE} \
        --template ${TEMPLATE_NAME} \
        --size 1
}

set_named_port(){
    gcloud compute instance-groups managed set-named-ports $1 \
          --named-ports="api:80,api:8080" \
          --zone ${ZONE}
}

get_named_port(){
    gcloud compute instance-groups get-named-ports $1 --zone ${ZONE}

}


set_env

#### get existing instance group name
ACTIVE_INSTNCE_GROUP=$(basename `gcloud compute backend-services get-health ${ACTIVE_BACKEND_NAME} \
    --global | grep backend: | awk '{print $2}'`)

### Create Process
STANDBY_INSTANCE_GROUP=`create_instance_group | awk 'NR==2 {print $1}'`
set_named_port $STANDBY_INSTANCE_GROUP

sleep 30

# add to backend
gcloud compute backend-services add-backend ${ACTIVE_BACKEND_NAME} \
    --instance-group=${STANDBY_INSTANCE_GROUP} \
    --global \
    --instance-group-zone=${ZONE} \
    --project ${PROJECT_ID} \
    --quiet

sleep 30

## Delete Process
gcloud compute backend-services remove-backend ${ACTIVE_BACKEND_NAME} \
    --instance-group=${ACTIVE_INSTNCE_GROUP} \
    --global \
    --instance-group-zone=${ZONE} \
    --project ${PROJECT_ID} \
    --quiet

sleep 30

gcloud compute instance-groups managed delete ${ACTIVE_INSTNCE_GROUP} \
    --zone ${ZONE} \
    --quiet
