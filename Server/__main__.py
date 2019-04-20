import boto3

def get_instances():
    instances = boto3.client('ec2').describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'running',
                'pending'
            ]
        },
    ],
    )
    return instances
print("Looking for an existing instance")
instances = get_instances()

instance_num = len(instances['Reservations'])

if instance_num == 0:
    instance = boto3.resource('ec2').create_instances(
        ImageId='ami-0080e4c5bc078760e',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='snu-amc'
    )[0]
    instance.wait_until_running()
    # Reload instance info
    instance.load()
    print("Launched instance public dns : ",instance.public_dns_name)
#else:
    # TODO : print public dns from instances
    
# TODO :Need a logic to launch AMI / launch python cserver

